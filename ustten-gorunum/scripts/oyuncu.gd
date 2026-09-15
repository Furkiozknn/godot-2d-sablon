extends CharacterBody2D
## Ustten gorunum (top-down) oyuncu hareketi - 8 yonlu, ivmeli.

@export var hiz: float = 120.0
@export var ivme: float = 900.0
@export var surtunme: float = 1200.0

func _physics_process(delta: float) -> void:
    var yon: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
    if yon != Vector2.ZERO:
        velocity = velocity.move_toward(yon * hiz, ivme * delta)
    else:
        velocity = velocity.move_toward(Vector2.ZERO, surtunme * delta)
    move_and_slide()
