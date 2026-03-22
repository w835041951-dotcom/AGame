## 升级选择面板 - 支持临时和永久两种模式

extends Control

signal chosen

@onready var title_label: Label = $TitleLabel
@onready var choice_container: HBoxContainer = $ChoiceContainer

var is_permanent: bool = false

func _ready():
	visible = false

func show_choices(upgrades: Array, permanent: bool):
	is_permanent = permanent
	visible = true
	title_label.text = "【永久升级】选择强化" if permanent else "【临时升级】选择增益（本层有效）"

	for child in choice_container.get_children():
		child.queue_free()

	for upgrade in upgrades:
		var btn = _make_btn(upgrade)
		choice_container.add_child(btn)

func _make_btn(upgrade: Dictionary) -> Button:
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(260, 110)
	btn.text = "%s\n\n%s" % [upgrade["name"], upgrade["description"]]
	btn.add_theme_font_size_override("font_size", 15)
	var col = Color.WHITE
	match upgrade.get("rarity", "common"):
		"common": col = Color(0.75, 0.75, 0.75)
		"rare":   col = Color(0.35, 0.55, 1.0)
		"epic":   col = Color(0.75, 0.30, 1.0)
	btn.add_theme_color_override("font_color", col)
	btn.pressed.connect(func(): _on_chosen(upgrade))
	return btn

func _on_chosen(upgrade: Dictionary):
	if is_permanent:
		UpgradeManager.apply_permanent(upgrade)
		get_parent().on_permanent_upgrade_chosen()
	else:
		UpgradeManager.apply_combat(upgrade)
		get_parent().on_combat_upgrade_chosen()
	chosen.emit()
