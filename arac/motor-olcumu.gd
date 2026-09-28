extends SceneTree
## Zipla hissini GERCEK motorda olcer.
##
## `arac/zipla-egrisi.py`, `oyuncu.gd`'nin `_physics_process` govdesinin
## Python'a tasinmis bir kopyasi. Bu betik ayni senaryolari Godot'un kendisinde,
## `yandan-gorunum/scenes/oyuncu.tscn` sahnesini hic degistirmeden, gercek
## `move_and_slide()` ve gercek `Input` eylemleriyle kosturur. `arac/motor-karsilastir.py`
## iki sonucu yan yana koyar: Python kopyasi motordan ayrisirsa CI kirmizi yanar.
##
##   godot --headless --path yandan-gorunum --import
##   godot --headless --path yandan-gorunum --script "$PWD/arac/motor-olcumu.gd"
##
## Cikti, tek satir: `MOTOR_OLCUM {json}`. Senaryolar zipla-egrisi.py'deki
## ile ayni: tam ziplama, 0,10 s'de birakilan ziplama, kenardan 0,10 / 0,15 s
## sonra basilan tus (kojot), inise 0,08 / 0,20 s kala basilan tus (tampon).
## Butun zamanlar fizik adimi cinsinden, projenin kendi tick ayarindan.

const ZEMIN_GENISLIK := 4000.0
const ZEMIN_KALINLIK := 40.0
const DUSUS_YUKSEKLIK := 45.0

var _oyuncu: CharacterBody2D
var _zemin: StaticBody2D
var _tick: int
var _adim: int = 0
var _senaryolar: Array = []
var _sonuc := {}


func _initialize() -> void:
    _tick = int(ProjectSettings.get_setting("physics/common/physics_ticks_per_second", 60))

    _zemin = StaticBody2D.new()
    var sekil := CollisionShape2D.new()
    var dikdortgen := RectangleShape2D.new()
    dikdortgen.size = Vector2(ZEMIN_GENISLIK, ZEMIN_KALINLIK)
    sekil.shape = dikdortgen
    _zemin.add_child(sekil)
    # Zeminin ust yuzeyi y = 0.
    _zemin.position = Vector2(0.0, ZEMIN_KALINLIK / 2.0)
    root.add_child(_zemin)

    var sahne: PackedScene = load("res://scenes/oyuncu.tscn")
    if sahne == null:
        _bitir_hatayla("res://scenes/oyuncu.tscn yuklenemedi")
        return
    _oyuncu = sahne.instantiate()
    _oyuncu.position = Vector2(0.0, -40.0)
    root.add_child(_oyuncu)

    _senaryolar = [
        _tam_zipla(),
        _erken_birak(),
        _kojot(_saniye(0.10), "kojot_010"),
        _kojot(_saniye(0.15), "kojot_015"),
        _dusus_suresi(),
    ]


func _saniye(s: float) -> int:
    return int(round(s * _tick))


# ---------------------------------------------------------------------------
# Senaryolar coroutine degil, adim adim ilerleyen durum makineleri: her fizik
# adiminda `_physics_process` bir kez cagrilir ve oyuncunun kendi
# `_physics_process`'inden ONCE calisir, yani burada basilan tus oyuncunun o
# adimdaki `is_action_just_pressed` sorgusunda gorunur.
# ---------------------------------------------------------------------------

func _physics_process(_delta: float) -> bool:
    if _senaryolar.is_empty():
        return true
    var s: Dictionary = _senaryolar[0]
    var bitti: bool = s.adim.call(s)
    if bitti:
        _senaryolar.pop_front()
        if _senaryolar.is_empty():
            _rapor()
            return true
    _adim += 1
    if _adim > _tick * 60:
        _bitir_hatayla("olcum 60 saniyede bitmedi")
        return true
    return false


func _yerlestir() -> void:
    _oyuncu.position = Vector2(0.0, -40.0)
    _oyuncu.velocity = Vector2.ZERO
    _zemin.position = Vector2(0.0, ZEMIN_KALINLIK / 2.0)


## Oyuncu yere oturana ve orada birkac adim kalana kadar bekler.
func _oturdu_mu(s: Dictionary) -> bool:
    if _oyuncu.is_on_floor() and absf(_oyuncu.velocity.y) < 0.001:
        s.yerde = s.get("yerde", 0) + 1
    else:
        s.yerde = 0
    return s.yerde >= 10


func _tam_zipla() -> Dictionary:
    return {"ad": "tam", "faz": 0, "adim": _zipla_adimi, "birak": -1}


func _erken_birak() -> Dictionary:
    return {"ad": "erken", "faz": 0, "adim": _zipla_adimi, "birak": _saniye(0.10)}


func _zipla_adimi(s: Dictionary) -> bool:
    match s.faz:
        0:
            _yerlestir()
            s.faz = 1
        1:
            if _oturdu_mu(s):
                s.taban = _oyuncu.position.y
                s.tepe = _oyuncu.position.y
                s.k = 0
                Input.action_press("zipla")
                s.faz = 2
        2:
            s.k += 1
            s.tepe = minf(s.tepe, _oyuncu.position.y)
            if s.k == s.birak:
                Input.action_release("zipla")
            if s.k > _tick and _oyuncu.is_on_floor():
                Input.action_release("zipla")
                _sonuc[s.ad] = s.taban - s.tepe
                return true
    return false


## Oyuncu yerde dururken zemin ayaginin altindan cekilir (kenardan dusmenin
## esdegeri), `gecikme` adim sonra tusa basilir. Ziplayip ziplamadigi olculur.
func _kojot(gecikme: int, ad: String) -> Dictionary:
    return {"ad": ad, "faz": 0, "adim": _kojot_adimi, "gecikme": gecikme}


func _kojot_adimi(s: Dictionary) -> bool:
    match s.faz:
        0:
            _yerlestir()
            s.faz = 1
        1:
            if _oturdu_mu(s):
                _zemin.position = Vector2(0.0, 100000.0)
                s.k = 0
                s.zipladi = false
                s.faz = 2
        2:
            s.k += 1
            if s.k == s.gecikme:
                Input.action_press("zipla")
            if s.k > s.gecikme and _oyuncu.velocity.y < 0.0:
                s.zipladi = true
            if s.k == s.gecikme + 3:
                Input.action_release("zipla")
                _sonuc[s.ad] = s.zipladi
                return true
    return false


## Tampon senaryosunun ilk yarisi: 45 px yukseklikten birakilan oyuncu kac
## adimda yere iniyor. Iki tampon senaryosu bu sayiya gore kurulur.
func _dusus_suresi() -> Dictionary:
    return {"ad": "dusus", "faz": 0, "adim": _dusus_adimi}


func _dusus_adimi(s: Dictionary) -> bool:
    match s.faz:
        0:
            _yerlestir()
            s.faz = 1
        1:
            if _oturdu_mu(s):
                s.taban = _oyuncu.position.y
                _oyuncu.position.y = s.taban - DUSUS_YUKSEKLIK
                _oyuncu.velocity = Vector2.ZERO
                s.k = 0
                s.faz = 2
        2:
            s.k += 1
            if _oyuncu.is_on_floor():
                _sonuc["dusus_adim"] = s.k
                _senaryolar.append(_tampon(_saniye(0.08), "tampon_008", s.k))
                _senaryolar.append(_tampon(_saniye(0.20), "tampon_020", s.k))
                return true
    return false


func _tampon(onceden: int, ad: String, inis: int) -> Dictionary:
    return {"ad": ad, "faz": 0, "adim": _tampon_adimi, "bas": inis - onceden, "inis": inis}


func _tampon_adimi(s: Dictionary) -> bool:
    match s.faz:
        0:
            _yerlestir()
            s.faz = 1
        1:
            if _oturdu_mu(s):
                s.taban = _oyuncu.position.y
                _oyuncu.position.y = s.taban - DUSUS_YUKSEKLIK
                _oyuncu.velocity = Vector2.ZERO
                s.k = 0
                s.zipladi = false
                s.faz = 2
        2:
            s.k += 1
            if s.k == s.bas:
                Input.action_press("zipla")
            elif s.k == s.bas + 1:
                Input.action_release("zipla")
            if s.k > s.inis and _oyuncu.velocity.y < 0.0:
                s.zipladi = true
            if s.k >= s.inis + _saniye(0.25):
                _sonuc[s.ad] = s.zipladi
                return true
    return false


func _rapor() -> void:
    _sonuc["tick"] = _tick
    _sonuc["godot"] = Engine.get_version_info().string
    print("MOTOR_OLCUM " + JSON.stringify(_sonuc))
    quit(0)


func _bitir_hatayla(neden: String) -> void:
    printerr("MOTOR_OLCUM_HATA " + neden)
    quit(1)
