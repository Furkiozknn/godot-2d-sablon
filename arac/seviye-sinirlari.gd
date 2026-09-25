extends SceneTree
## Ornek seviyeden dusulebiliyor mu?
##
## Sablonu ilk kez acan kisi once saga sola kosar. Kenardan bosluga dusup
## sonsuza kadar dusen bir karakter, "calismiyor" demenin en kisa yolu.
## Bu betik projenin kendi ana sahnesini yukler, oyuncuyu once saga sonra
## sola `ADIM_SANIYE` boyunca kosturur (arada ziplatarak) ve seviyenin
## disina cikip cikmadigina bakar.
##
##   godot --headless --fixed-fps 60 --path yandan-gorunum --script "$PWD/arac/seviye-sinirlari.gd"
##   godot --headless --fixed-fps 60 --path ustten-gorunum --script "$PWD/arac/seviye-sinirlari.gd"
##
## `--fixed-fps 60` gercek zamani beklemeden, projenin fizik adimiyla kosturur.
## Cikis kodu 0 = oyuncu seviyenin icinde kaldi. Sinir, ana sahnedeki
## gorunur alandan (Arkaplan ya da TileMapLayer) okunur; burada elle yazilmaz.

const ADIM_SANIYE := 10.0

var _oyuncu: CharacterBody2D
var _sinir: Rect2
var _tick: int
var _k := 0
var _en_uzak := Vector2.ZERO
var _eylemler: Array = []


func _initialize() -> void:
    _tick = int(ProjectSettings.get_setting("physics/common/physics_ticks_per_second", 60))
    var yol: String = ProjectSettings.get_setting("application/run/main_scene", "")
    var sahne: PackedScene = load(yol)
    if sahne == null:
        _bitir(false, "ana sahne yuklenemedi: " + yol)
        return
    var seviye: Node = sahne.instantiate()
    root.add_child(seviye)
    _oyuncu = seviye.get_node_or_null("Oyuncu")
    if _oyuncu == null:
        _bitir(false, "ana sahnede 'Oyuncu' dugumu yok")
        return
    _sinir = _seviye_siniri(seviye)
    _en_uzak = _oyuncu.global_position
    if _sinir.size == Vector2.ZERO:
        _bitir(false, "seviyenin gorunur alani bulunamadi (Arkaplan/TileMapLayer)")
        return

    # Proje hangi eylemleri tanimliyorsa onlar kullanilir: iki sablonun
    # girdi haritasi farkli (yandan: zipla; ustten: move_up/move_down).
    for yon in ["move_right", "move_left", "move_down", "move_up"]:
        if InputMap.has_action(yon):
            _eylemler.append(yon)


func _seviye_siniri(seviye: Node) -> Rect2:
    var arka := seviye.get_node_or_null("Arkaplan") as Polygon2D
    if arka != null:
        var r := Rect2(arka.polygon[0], Vector2.ZERO)
        for p in arka.polygon:
            r = r.expand(p)
        return Rect2(arka.to_global(r.position), r.size)
    var harita := seviye.get_node_or_null("TileMapLayer") as TileMapLayer
    if harita != null:
        var hucre := harita.get_used_rect()
        var boyut := Vector2(harita.tile_set.tile_size)
        return Rect2(harita.to_global(Vector2(hucre.position) * boyut), Vector2(hucre.size) * boyut)
    return Rect2()


func _physics_process(_delta: float) -> bool:
    if _oyuncu == null:
        return true
    var adim_basina := int(ADIM_SANIYE * _tick)
    var sira := _k / adim_basina
    if sira >= _eylemler.size():
        for e in _eylemler:
            Input.action_release(e)
        if InputMap.has_action("zipla"):
            Input.action_release("zipla")
        _bitir(true, "")
        return true

    for i in _eylemler.size():
        if i == sira:
            Input.action_press(_eylemler[i])
        else:
            Input.action_release(_eylemler[i])
    if InputMap.has_action("zipla"):
        # Yarim saniyede bir zipla: platformlarin ustune de cikabilsin.
        if _k % (_tick / 2) == 0:
            Input.action_press("zipla")
        elif _k % (_tick / 2) == 10:
            Input.action_release("zipla")

    var p := _oyuncu.global_position
    if absf(p.x - _sinir.get_center().x) > absf(_en_uzak.x - _sinir.get_center().x):
        _en_uzak = p
    if not _sinir.has_point(p):
        _bitir(false, "oyuncu seviyenin disina cikti: %s, seviye %s" % [p, _sinir])
        return true
    _k += 1
    return false


func _bitir(tamam: bool, neden: String) -> void:
    if tamam:
        print("SEVIYE_TAMAM oyuncu %d adim boyunca seviyenin icinde kaldi (en uzak nokta %s, seviye %s)"
            % [_k, _en_uzak, _sinir])
        quit(0)
    else:
        printerr("SEVIYE_HATA " + neden)
        quit(1)
