extends Node2D

const valid_suits = ["spade", "heart", "diamond", "club"]
const valid_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

@export var card_scene: PackedScene
@export var card_back = ""

var cards = []

func _init():
	if card_back == "":
		pick_random_card_back()
	
	generate_deck()

func _ready():
	var card_base_sprite_loc = "res://card_sprites"
	var texture = card_base_sprite_loc.path_join("backs").path_join(card_back)
	$DeckTop.texture = load(texture)
	print(cards)

func generate_deck():
	for suit in valid_suits:
		for rank in valid_ranks:
			var card_data = {
				"rank": rank,
				"suit": suit,
				"flipped": true,
				"card_back": card_back
			}
			cards.append(card_data)
	cards.shuffle()

func pick_random_card_back():
	var dir_name = "res://card_sprites/backs/"
	var dir = DirAccess.open(dir_name)
	var card_back_files = dir.get_files()
	var new_card_back_files = []
	for file in card_back_files:
		if "import" not in file:
			new_card_back_files.append(file)
	
	card_back = new_card_back_files.pick_random()

func create_card_instance(rank, suit, flipped=true, card_back=card_back):
	var card_instance = card_scene.instantiate()
	card_instance.rank = rank
	card_instance.suit = suit
	card_instance.flipped = true
	card_instance.card_back = card_back
	card_instance.set_name("%s%s" % [suit, rank])
	return card_instance
	
func get_top_card():
	return cards[0]
