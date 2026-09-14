extends CharacterBody2D
## Yandan gorunum (side-scroller) oyuncu hareketi.
## Iceride uc "iyi hissettiren" teknik var:
##   kojot suresi  : platformdan dustukten sonra kisa sure daha ziplayabilme
##   zipla tamponu : yere inmeden hemen once basilan ziplamayi hatirlama
##   degisken yukseklik : tusu erken birakinca ziplama kisalir

@export var hiz: float = 130.0
@export var zipla_gucu: float = 330.0
@export var yercekimi: float = 980.0
@export var hava_kontrolu: float = 0.85
@export var kojot_suresi: float = 0.12
@export var zipla_tampon_suresi: float = 0.12

var _kojot: float = 0.0
var _tampon: float = 0.0
var _bakis_yonu: float = 1.0

@onready var _gorsel: AnimatedSprite2D = $Gorsel

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += yercekimi * delta
        _kojot -= delta
    else:
        _kojot = kojot_suresi

    if Input.is_action_just_pressed("zipla"):
        _tampon = zipla_tampon_suresi
    else:
        _tampon -= delta

    if _tampon > 0.0 and _kojot > 0.0:
        velocity.y = -zipla_gucu
        _tampon = 0.0
        _kojot = 0.0

    if Input.is_action_just_released("zipla") and velocity.y < 0.0:
        velocity.y *= 0.45

    var yon: float = Input.get_axis("move_left", "move_right")
    var carpan: float = 1.0 if is_on_floor() else hava_kontrolu
    if yon != 0.0:
        velocity.x = move_toward(velocity.x, yon * hiz, 1400.0 * delta * carpan)
    else:
        velocity.x = move_toward(velocity.x, 0.0, 1200.0 * delta * carpan)

    move_and_slide()

    if yon != 0.0:
        _bakis_yonu = yon
    _gorsel.flip_h = _bakis_yonu < 0.0

    var hedef_animasyon: StringName
    if is_on_floor():
        hedef_animasyon = &"idle" if abs(velocity.x) < 5.0 else &"yuru"
    else:
        hedef_animasyon = &"zipla" if velocity.y < 0.0 else &"dus"
    if _gorsel.animation != hedef_animasyon:
        _gorsel.play(hedef_animasyon)
