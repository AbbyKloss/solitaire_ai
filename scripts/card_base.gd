extends MarginContainer
signal clicked

#@onready var card_db = get_node("res://card_info.gd")
@export var suit = "spade"
@export var rank = 1
@export var flipped = false
@export var card_back = "back27.png"

#@onready var card_texture = get_node("CardTexture")

const card_base_sprite_loc = "res://card_sprites"

const valid_suits = ["spade", "heart", "diamond", "club"]
const valid_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

#func _init(): # this was for testing
	#rank = valid_ranks.pick_random()
	#suit = valid_suits.pick_random()
	#
	#var rng = RandomNumberGenerator.new()
	#flipped = rng.randi() % 2

func get_flipped_sprite() -> String:
	var texture_loc = card_base_sprite_loc.path_join("backs").path_join(card_back)
	
	return texture_loc

func sprite_lookup() -> String:
	if (suit not in valid_suits) or (rank not in valid_ranks):
		suit = valid_suits[0]
		rank = valid_ranks[0]
		
	if flipped:
		return get_flipped_sprite()
		
	var filename = suit + str(rank) + ".png"
	var texture_loc = card_base_sprite_loc.path_join(suit).path_join(filename)
	
	return texture_loc

func change_texture() -> void:
	var texture = sprite_lookup()
	$CardTexture.texture = load(texture)
	

func flip_card():
	flipped = !flipped
	change_texture()

func _ready() -> void:
	change_texture()


func _on_input_event(event):
	print(event)
	if event is InputEventMouseButton:
		print(event)
