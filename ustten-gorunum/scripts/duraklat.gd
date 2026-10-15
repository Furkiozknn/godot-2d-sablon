extends CanvasLayer
## Duraklatma menusu: Esc (ui_cancel) acar ve kapatir. Oyunu duraklatir, her
## eylemin tusunu gosterir; bir tusa tiklayip yeni tusa basinca degisir ve
## GirdiAyarlari onu kaydeder. Autoload olarak kayitli (Duraklat), yani her
## sahnede calisir; arayuz koddan kuruluyor, sahne dosyasi yalnizca kok.

## Eylemlerin menudeki adlari. Listede olmayan eylem kendi adiyla gorunur.
const ETIKETLER := {
    &"move_left": "Sola",
    &"move_right": "Saga",
    &"move_up": "Yukari",
    &"move_down": "Asagi",
    &"zipla": "Zipla",
    &"asagi": "Asagi in",
    &"etkilesim": "Etkilesim",
}

## Testler kendi GirdiAyarlari ornegini verebilir; yoksa autoload kullanilir.
var girdi: Node

var _bekleyen: StringName = &""
var _kok: Control
var _liste: VBoxContainer
var _not: Label
var _devam: Button
var _butonlar := {}


func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    if girdi == null:
        girdi = get_node_or_null(^"/root/GirdiAyarlari")
    _kur()
    _kok.hide()


func acik() -> bool:
    return _kok.visible


func ac() -> void:
    _yenile()
    _not.text = ""
    _kok.show()
    get_tree().paused = true
    _devam.grab_focus()


func kapat() -> void:
    _bekleyen = &""
    _kok.hide()
    get_tree().paused = false


## Bir eylemin tus dugmesine tiklandi: siradaki tus o eyleme atanacak.
func tus_bekle(eylem: StringName) -> void:
    _bekleyen = eylem
    _yenile()
    if _butonlar.has(eylem):
        _butonlar[eylem].text = "Bir tusa basin..."
    _not.text = "Esc: vazgec"


func bekliyor() -> bool:
    return _bekleyen != &""


func _unhandled_input(olay: InputEvent) -> void:
    if bekliyor() or not olay.is_action_pressed("ui_cancel"):
        return
    if acik():
        kapat()
    else:
        ac()
    get_viewport().set_input_as_handled()


## Tus beklerken gelen ilk klavye basisi yeni tustur; Esc vazgecer.
func _input(olay: InputEvent) -> void:
    if not bekliyor():
        return
    var tus := olay as InputEventKey
    if tus == null or not tus.pressed or tus.echo:
        return
    get_viewport().set_input_as_handled()
    var kod: int = tus.physical_keycode if tus.physical_keycode != KEY_NONE else tus.keycode
    if kod == KEY_ESCAPE:
        _not.text = "Vazgecildi."
    elif girdi != null:
        girdi.tus_ata(_bekleyen, kod)
        girdi.kaydet()
        _not.text = "Kaydedildi."
    _bekleyen = &""
    _yenile()


func _kur() -> void:
    _kok = ColorRect.new()
    _kok.color = Color(0.0, 0.0, 0.0, 0.6)
    _kok.set_anchors_preset(Control.PRESET_FULL_RECT)
    add_child(_kok)

    var orta := CenterContainer.new()
    orta.set_anchors_preset(Control.PRESET_FULL_RECT)
    _kok.add_child(orta)

    var panel := PanelContainer.new()
    orta.add_child(panel)
    var kutu := VBoxContainer.new()
    kutu.add_theme_constant_override("separation", 6)
    panel.add_child(kutu)

    var baslik := Label.new()
    baslik.text = "DURAKLATILDI"
    baslik.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    kutu.add_child(baslik)

    _liste = VBoxContainer.new()
    kutu.add_child(_liste)

    _not = Label.new()
    _not.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    kutu.add_child(_not)

    var satir := HBoxContainer.new()
    satir.add_theme_constant_override("separation", 6)
    kutu.add_child(satir)
    _devam = _buton(satir, "Devam", kapat)
    _buton(satir, "Varsayilan tuslar", _varsayilana_don)
    _buton(satir, "Cik", func() -> void: get_tree().quit())


func _buton(ebeveyn: Node, yazi: String, tikla: Callable) -> Button:
    var b := Button.new()
    b.text = yazi
    b.pressed.connect(tikla)
    ebeveyn.add_child(b)
    return b


func _varsayilana_don() -> void:
    if girdi != null:
        girdi.sifirla()
    _not.text = "Varsayilan tuslar geri geldi."
    _yenile()


func _yenile() -> void:
    for cocuk in _liste.get_children():
        _liste.remove_child(cocuk)
        cocuk.queue_free()
    _butonlar.clear()
    if girdi == null:
        return
    for eylem in girdi.eylemler():
        var satir := HBoxContainer.new()
        var ad := Label.new()
        ad.text = ETIKETLER.get(eylem, String(eylem))
        ad.custom_minimum_size = Vector2(110, 0)
        satir.add_child(ad)
        var tus := Button.new()
        tus.text = girdi.tus_adi(eylem)
        tus.custom_minimum_size = Vector2(130, 0)
        tus.pressed.connect(tus_bekle.bind(eylem))
        satir.add_child(tus)
        _butonlar[eylem] = tus
        _liste.add_child(satir)
