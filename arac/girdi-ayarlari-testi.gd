extends SceneTree
## Tus atama ve duraklatma menusu, gercek Godot'ta. Iki projede de ayni:
##
##   godot --headless --path yandan-gorunum --import
##   godot --headless --path yandan-gorunum --script "$PWD/arac/girdi-ayarlari-testi.gd"
##
## Cikti: `GIRDI_TAMAM <n> kontrol`; bir kontrol tutmazsa `GIRDI_HATA <ad>`
## satirlari ve cikis kodu 1. Gercek user://girdi.cfg'ye dokunmaz.

const DOSYA := "user://girdi-testi.cfg"

var _sayi := 0
var _basladi := false
var _hata := 0


func _kontrol(kosul: bool, ad: String) -> void:
    _sayi += 1
    if not kosul:
        _hata += 1
        printerr("GIRDI_HATA " + ad)


func _bas(kod: Key) -> InputEventKey:
    var olay := InputEventKey.new()
    olay.physical_keycode = kod
    olay.pressed = true
    return olay


# Dugumlerin _ready'si ilk karede calisir; testler o yuzden _initialize'da degil.
func _process(_delta: float) -> bool:
    if _basladi:
        return false
    _basladi = true
    _testler()
    return false


func _testler() -> void:
    if FileAccess.file_exists(DOSYA):
        DirAccess.remove_absolute(DOSYA)
    var g: Node = load("res://scripts/girdi_ayarlari.gd").new()
    g.dosya = DOSYA
    root.add_child(g)

    var eylemler: Array = g.eylemler()
    _kontrol(eylemler.size() >= 3, "proje eylemleri listeleniyor")
    _kontrol(eylemler.all(func(e): return not String(e).begins_with("ui_")), "ui_* listelenmiyor")
    var eylem: StringName = eylemler[0]
    var baska: StringName = eylemler[1]
    var varsayilan: Array = g.tuslar(eylem)
    _kontrol(not varsayilan.is_empty(), "eylemin varsayilan tusu var")
    _kontrol(varsayilan == g.varsayilan_tuslar(eylem), "baslangicta tuslar project.godot'taki gibi")
    _kontrol(g.tus_adi(eylem) != "-", "tus adi okunuyor")

    # Gamepad olayi tus atamasindan etkilenmemeli.
    var dugme := InputEventJoypadButton.new()
    dugme.button_index = JOY_BUTTON_A
    InputMap.action_add_event(eylem, dugme)

    g.tus_ata(eylem, KEY_K)
    _kontrol(g.tuslar(eylem) == [KEY_K], "tus_ata klavye tuslarini tek tusla degistiriyor")
    _kontrol(InputMap.event_is_action(_bas(KEY_K), eylem), "InputMap yeni tusu taniyor")
    _kontrol(InputMap.action_has_event(eylem, dugme), "gamepad olayi yerinde kaldi")
    _kontrol(g.tuslar(baska) == g.varsayilan_tuslar(baska), "baska eylem degismedi")

    _kontrol(g.kaydet() == OK, "kaydet")
    var cfg := ConfigFile.new()
    _kontrol(cfg.load(DOSYA) == OK, "kayit dosyasi okunuyor")
    _kontrol(cfg.get_section_keys("tuslar").size() == 1, "yalnizca degisen eylem kaydedildi")

    # Oyun yeniden acilmis gibi: InputMap proje ayarina doner, kayit yuklenir.
    InputMap.load_from_project_settings()
    _kontrol(g.tuslar(eylem) == varsayilan, "yeniden acilista once varsayilan")
    g.yukle()
    _kontrol(g.tuslar(eylem) == [KEY_K], "kayitli tus geri yuklendi")

    # Bozuk ya da eski kayit oyunu durdurmamali.
    cfg = ConfigFile.new()
    cfg.set_value("tuslar", "artik_olmayan_eylem", [KEY_L])
    cfg.set_value("tuslar", String(baska), "bozuk")
    cfg.save(DOSYA)
    InputMap.load_from_project_settings()
    g.yukle()
    _kontrol(g.tuslar(baska) == g.varsayilan_tuslar(baska), "bozuk deger atlandi")
    _kontrol(not InputMap.has_action(&"artik_olmayan_eylem"), "bilinmeyen eylem eklenmedi")

    g.tus_ata(eylem, KEY_K)
    g.kaydet()
    g.sifirla()
    _kontrol(g.tuslar(eylem) == varsayilan, "sifirla varsayilana donduruyor")
    _kontrol(not FileAccess.file_exists(DOSYA), "sifirla kaydi siliyor")

    # Duraklatma menusu: ac, bir tusa tikla, yeni tusa bas, kapat.
    var menu: CanvasLayer = load("res://scenes/duraklat.tscn").instantiate()
    menu.girdi = g
    root.add_child(menu)
    _kontrol(not menu.acik(), "menu kapali basliyor")
    menu.ac()
    _kontrol(menu.acik() and paused, "menu acilinca oyun duraklar")
    menu.tus_bekle(eylem)
    _kontrol(menu.bekliyor(), "tus bekleniyor")
    menu._input(_bas(KEY_ESCAPE))
    _kontrol(not menu.bekliyor() and g.tuslar(eylem) == varsayilan, "Esc vazgeciyor")
    menu.tus_bekle(eylem)
    menu._input(_bas(KEY_J))
    _kontrol(g.tuslar(eylem) == [KEY_J], "menuden atanan tus uygulaniyor")
    _kontrol(FileAccess.file_exists(DOSYA), "menuden atanan tus kaydediliyor")
    menu.kapat()
    _kontrol(not menu.acik() and not paused, "menu kapaninca oyun devam ediyor")

    g.sifirla()
    if _hata == 0:
        print("GIRDI_TAMAM %d kontrol" % _sayi)
    quit(1 if _hata > 0 else 0)
