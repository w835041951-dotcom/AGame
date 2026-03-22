## 永久升级面板（整局有效）

extends Control

@onready var title_label: Label = $TitleLabel
@onready var choice_container: HBoxContainer = $ChoiceContainer

func _ready():
	visible = false

func show_choices(upgrades: Array):
	visible = true
	title_label.text = "【永久强化】选择（整局有效）"
	for child in choice_container.get_children():
		child.queue_free()
	for upgrade in upgrades:
		choice_container.add_child(_make_btn(upgrade))

func _make_btn(upgrade: Dictionary) -> Button:
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(260, 110)
	btn.text = "%s\n\n%s" % [upgrade["name"], upgrade["description"]]
	btn.add_theme_font_size_override("font_size", 15)
	var col = _rarity_color(upgrade.get("rarity", "common"))
	btn.add_theme_color_override("font_color", col)
	btn.pressed.connect(func(): _on_chosen(upgrade))
	return btn

func _on_chosen(upgrade: Dictionary):
	UpgradeManager.apply_permanent(upgrade)
	visible = false
	get_parent().on_permanent_upgrade_chosen()

func _rarity_color(rarity: String) -> Color:
	match rarity:
		"rare": return Color(0.35, 0.55, 1.0)
		"epic": return Color(0.75, 0.30, 1.0)
		_:      return Color(0.75, 0.75, 0.75)
