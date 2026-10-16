extends Node
## Tus atamalari: oyuncunun degistirdigi tuslari user:// altina kaydeder ve
## oyun her acildiginda geri yukler. Autoload olarak kayitli: GirdiAyarlari.
##
## Yalnizca klavye olaylari (InputEventKey) degisir; ayni eylemdeki gamepad
## ve fare olaylari oldugu gibi kalir. Kayit fiziksel tus kodudur, yani klavye
## duzeni (Q, F, AZERTY) degisse de tus klavyede ayni yerde kalir.
##
## Dosyaya yalnizca proje ayarindan FARKLI olan eylemler yazilir: sablonun
## varsayilan tuslarini sonradan degistirirseniz, oyuncunun dokunmadigi
## eylemler yeni varsayilani alir.

signal degisti(eylem: StringName)

const DOSYA := "user://girdi.cfg"
const BOLUM := "tuslar"

## Testler kendi dosyalarini kullanabilsin diye degistirilebilir.
var dosya: String = DOSYA


func _ready() -> void:
    yukle()


## Oyuncunun degistirebilecegi eylemler, project.godot'taki sirayla; ui_* haric.
func eylemler() -> Array[StringName]:
    var sonuc: Array[StringName] = []
    for ozellik in ProjectSettings.get_property_list():
        var ad: String = ozellik.name
        if not ad.begins_with("input/") or ad.begins_with("input/ui_"):
            continue
        var eylem := StringName(ad.substr(6))
        if InputMap.has_action(eylem) and not sonuc.has(eylem):
            sonuc.append(eylem)
    return sonuc


## Eylemin su anki klavye tuslari (fiziksel kod).
func tuslar(eylem: StringName) -> Array[int]:
    var sonuc: Array[int] = []
    if not InputMap.has_action(eylem):
        return sonuc
    for olay in InputMap.action_get_events(eylem):
        if olay is InputEventKey:
            sonuc.append(_kod(olay))
    return sonuc


## project.godot'taki klavye tuslari.
func varsayilan_tuslar(eylem: StringName) -> Array[int]:
    var sonuc: Array[int] = []
    var ayar: Variant = ProjectSettings.get_setting("input/" + String(eylem))
    if ayar is Dictionary:
        for olay in ayar.get("events", []):
            if olay is InputEventKey:
                sonuc.append(_kod(olay))
    return sonuc


## Eylemin klavye tuslarini tek bir tusla degistirir.
func tus_ata(eylem: StringName, fiziksel: int) -> void:
    if InputMap.has_action(eylem) and fiziksel > 0:
        _klavyeyi_yaz(eylem, [fiziksel])
        degisti.emit(eylem)


## Ekranda gosterilecek ad: "Space", "W / Up".
func tus_adi(eylem: StringName) -> String:
    var adlar := PackedStringArray()
    for kod in tuslar(eylem):
        var tus := kod as Key
        # Klavye duzenine gore ad (Q/F'de ayni yerdeki harf); headless'ta yok.
        if DisplayServer.get_name() != "headless":
            var yerel := DisplayServer.keyboard_get_keycode_from_physical(tus)
            if yerel != KEY_NONE:
                tus = yerel
        adlar.append(OS.get_keycode_string(tus))
    return " / ".join(adlar) if not adlar.is_empty() else "-"


func kaydet() -> Error:
    var cfg := ConfigFile.new()
    for eylem in eylemler():
        var simdiki := tuslar(eylem)
        if simdiki != varsayilan_tuslar(eylem):
            cfg.set_value(BOLUM, String(eylem), simdiki)
    return cfg.save(dosya)


## Kayitli tuslari uygular. Dosya yoksa, bozuksa ya da artik projede olmayan
## bir eylemi aniyorsa o kisim sessizce atlanir: oyun acilmali.
func yukle() -> void:
    var cfg := ConfigFile.new()
    if cfg.load(dosya) != OK or not cfg.has_section(BOLUM):
        return
    for anahtar in cfg.get_section_keys(BOLUM):
        var eylem := StringName(anahtar)
        if not InputMap.has_action(eylem):
            continue
        var kodlar: Variant = cfg.get_value(BOLUM, anahtar, [])
        if not (kodlar is Array):
            continue
        var gecerli: Array[int] = []
        for kod in kodlar:
            if typeof(kod) == TYPE_INT and kod > 0:
                gecerli.append(kod)
        if not gecerli.is_empty():
            _klavyeyi_yaz(eylem, gecerli)


## Butun tuslari project.godot'taki haline dondurur ve kaydi siler.
func sifirla() -> void:
    InputMap.load_from_project_settings()
    if FileAccess.file_exists(dosya):
        DirAccess.remove_absolute(dosya)
    for eylem in eylemler():
        degisti.emit(eylem)


func _klavyeyi_yaz(eylem: StringName, kodlar: Array[int]) -> void:
    for olay in InputMap.action_get_events(eylem):
        if olay is InputEventKey:
            InputMap.action_erase_event(eylem, olay)
    for kod in kodlar:
        var yeni := InputEventKey.new()
        yeni.physical_keycode = kod as Key
        InputMap.action_add_event(eylem, yeni)


func _kod(olay: InputEventKey) -> int:
    return olay.physical_keycode if olay.physical_keycode != KEY_NONE else olay.keycode
