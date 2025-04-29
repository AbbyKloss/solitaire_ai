extends Sprite2D

var parent_node

func _ready():
	parent_node = get_parent()

func _input(event):
	if event.is_action_pressed("click") and is_pixel_opaque(get_local_mouse_position()):
		parent_node.flip_card()
