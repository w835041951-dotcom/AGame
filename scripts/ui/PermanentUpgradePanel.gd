## 永久升级面板（整局有效）

extends Control

@onready var title_label: Label = $TitleLabel
@onready var choice_container: HBoxContainer = $ChoiceContainer

func _ready():
	visible = false

func show_choices(upgrades: Array):
	visible = true
	title_label.text = "🏆 永久强化"
	_style_title(title_label, Color(1.0, 0.75, 0.2))
	for child in choice_container.get_children():
		child.queue_free()
	for upgrade in upgrades:
		choice_container.add_child(_make_card(upgrade))

func _make_card(upgrade: Dictionary) -> Control:
	var rarity = upgrade.get("rarity", "common")
	var rarity_col = _rarity_color(rarity)
	var rarity_bg  = _rarity_bg(rarity)

	var card = Panel.new()
	card.custom_minimum_size = Vector2(300, 180)

	var style = StyleBoxFlat.new()
	style.bg_color = rarity_bg
	style.border_color = rarity_col
	style.border_width_left = 3
	style.border_width_right = 3
	style.border_width_top = 3
	style.border_width_bottom = 3
	style.corner_radius_top_left = 6
	style.corner_radius_top_right = 6
	style.corner_radius_bottom_left = 6
	style.corner_radius_bottom_right = 6
	style.shadow_color = Color(0, 0, 0, 0.5)
	style.shadow_size = 4
	card.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", 8)
	card.add_child(vbox)

	var rarity_lbl = Label.new()
	rarity_lbl.text = _rarity_text(rarity)
	rarity_lbl.add_theme_color_override("font_color", rarity_col)
	rarity_lbl.add_theme_font_size_override("font_size", 11)
	rarity_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rarity_lbl.add_theme_constant_override("margin_top", 12)
	vbox.add_child(rarity_lbl)

	var name_lbl = Label.new()
	name_lbl.text = upgrade["name"]
	name_lbl.add_theme_color_override("font_color", Color(0.95, 0.92, 0.85))
	name_lbl.add_theme_font_size_override("font_size", 22)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD
	vbox.add_child(name_lbl)

	var desc_lbl = Label.new()
	desc_lbl.text = upgrade["description"]
	desc_lbl.add_theme_color_override("font_color", Color(0.72, 0.70, 0.62))
	desc_lbl.add_theme_font_size_override("font_size", 14)
	desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD
	vbox.add_child(desc_lbl)

	var spacer = Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(spacer)

	var btn = Button.new()
	btn.text = "选择"
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", Color.WHITE)
	var btn_style = StyleBoxFlat.new()
	btn_style.bg_color = rarity_col.darkened(0.3)
	btn_style.corner_radius_top_left = 0
	btn_style.corner_radius_top_right = 0
	btn_style.corner_radius_bottom_left = 6
	btn_style.corner_radius_bottom_right = 6
	btn.add_theme_stylebox_override("normal", btn_style)
	var btn_hover = btn_style.duplicate()
	btn_hover.bg_color = rarity_col.darkened(0.1)
	btn.add_theme_stylebox_override("hover", btn_hover)
	btn.pressed.connect(func(): _on_chosen(upgrade))
	vbox.add_child(btn)

	return card

func _on_chosen(upgrade: Dictionary):
	UpgradeManager.apply_permanent(upgrade)
	visible = false
	get_parent().on_permanent_upgrade_chosen()

func _style_title(lbl: Label, col: Color):
	lbl.add_theme_color_override("font_color", col)
	lbl.add_theme_font_size_override("font_size", 28)
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

func _rarity_color(rarity: String) -> Color:
	match rarity:
		"rare":   return Color(0.35, 0.60, 0.95)
		"epic":   return Color(0.75, 0.30, 0.92)
		_:        return Color(0.65, 0.60, 0.50)

func _rarity_bg(rarity: String) -> Color:
	match rarity:
		"rare":   return Color(0.06, 0.10, 0.22)
		"epic":   return Color(0.12, 0.04, 0.20)
		_:        return Color(0.10, 0.09, 0.08)

func _rarity_text(rarity: String) -> String:
	match rarity:
		"rare":   return "★★ 稀有"
		"epic":   return "★★★ 史诗"
		_:        return "★ 普通"
