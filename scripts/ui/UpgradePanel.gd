## 升级选择面板

extends Control

signal upgrade_chosen(upgrade: Dictionary)

@onready var choice_container = $ChoiceContainer
@onready var title_label = $TitleLabel

var choices: Array = []

func _ready():
	upgrade_chosen.connect(_on_upgrade_chosen)

func show_choices(upgrades: Array):
	choices = upgrades
	visible = true
	for child in choice_container.get_children():
		child.queue_free()

	for upgrade in upgrades:
		var btn = _make_upgrade_button(upgrade)
		choice_container.add_child(btn)

func _make_upgrade_button(upgrade: Dictionary) -> Button:
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(280, 100)
	btn.text = "%s\n%s" % [upgrade["name"], upgrade["description"]]
	btn.add_theme_font_size_override("font_size", 16)

	var rarity_color = Color.WHITE
	match upgrade.get("rarity", "common"):
		"common": rarity_color = Color(0.7, 0.7, 0.7)
		"rare": rarity_color = Color(0.3, 0.5, 1.0)
		"epic": rarity_color = Color(0.7, 0.3, 1.0)
	btn.add_theme_color_override("font_color", rarity_color)

	btn.pressed.connect(func(): upgrade_chosen.emit(upgrade))
	return btn

func _on_upgrade_chosen(upgrade: Dictionary):
	UpgradeManager.apply_upgrade(upgrade)
	visible = false
	GameManager.next_floor()
	GameManager.start_turn()
