## 临时升级面板（本层有效）

extends Control

@onready var title_label: Label = $TitleLabel
@onready var choice_container: HBoxContainer = $ChoiceContainer

func _ready():
	visible = false

func show_choices(upgrades: Array):
	visible = true
	title_label.text = "⚡ 棋盘增益"
	_style_title(title_label, UIThemeManager.color("text_accent"))
	for child in choice_container.get_children():
		child.queue_free()
	var idx = 0
	for upgrade in upgrades:
		var card = _make_card(upgrade)
		choice_container.add_child(card)
		# 卡片入场动画：延迟滑入 + 淡入
		card.modulate = Color(1, 1, 1, 0)
		card.position.y += 30
		var tw = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
		tw.tween_interval(idx * 0.12)
		tw.tween_property(card, "modulate:a", 1.0, 0.3)
		tw.parallel().tween_property(card, "position:y", card.position.y - 30, 0.3)
		idx += 1

func _make_card(upgrade: Dictionary) -> Control:
	var rarity = upgrade.get("rarity", "common")
	var rarity_col = _rarity_color(rarity)
	var rarity_bg  = _rarity_bg(rarity)
	var tm = UIThemeManager

	var card = Panel.new()
	card.custom_minimum_size = Vector2(320, 240)

	# 尝试主题纹理卡片
	var card_tex_name = "card_" + rarity
	var card_sb = tm.make_themed_stylebox(card_tex_name, "", "")
	if card_sb:
		card.add_theme_stylebox_override("panel", card_sb)
	else:
		var style = StyleBoxFlat.new()
		style.bg_color = rarity_bg
		style.border_color = rarity_col
		style.set_border_width_all(3)
		style.set_corner_radius_all(int(tm.color("corner_radius")))
		style.shadow_color = tm.color("card_shadow")
		style.shadow_size = 6
		card.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", 10)
	card.add_child(vbox)

	# 稀有度标签
	var rarity_lbl = Label.new()
	rarity_lbl.text = _rarity_text(rarity)
	rarity_lbl.add_theme_color_override("font_color", rarity_col)
	rarity_lbl.add_theme_font_size_override("font_size", 13)
	rarity_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rarity_lbl.add_theme_constant_override("margin_top", 16)
	vbox.add_child(rarity_lbl)

	# 升级名称
	var name_lbl = Label.new()
	name_lbl.text = upgrade["name"]
	name_lbl.add_theme_color_override("font_color", UIThemeManager.color("card_name_text"))
	name_lbl.add_theme_font_size_override("font_size", 26)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD
	name_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	name_lbl.add_theme_constant_override("shadow_offset_x", 1)
	name_lbl.add_theme_constant_override("shadow_offset_y", 1)
	vbox.add_child(name_lbl)

	# 描述
	var desc_lbl = Label.new()
	desc_lbl.text = upgrade["description"]
	desc_lbl.add_theme_color_override("font_color", UIThemeManager.color("card_desc_text"))
	desc_lbl.add_theme_font_size_override("font_size", 16)
	desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD
	vbox.add_child(desc_lbl)

	# 选择按钮
	var spacer = Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(spacer)

	var btn = Button.new()
	btn.text = "选择"
	btn.custom_minimum_size = Vector2(0, 44)
	btn.add_theme_font_size_override("font_size", 20)
	btn.add_theme_color_override("font_color", Color.WHITE)
	btn.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	btn.add_theme_constant_override("shadow_offset_x", 1)
	btn.add_theme_constant_override("shadow_offset_y", 1)
	var btn_sb = tm.make_themed_stylebox("btn_normal", "", "")
	if btn_sb:
		btn.add_theme_stylebox_override("normal", btn_sb)
		var btn_hsb = tm.make_themed_stylebox("btn_hover", "", "")
		if btn_hsb:
			btn.add_theme_stylebox_override("hover", btn_hsb)
	else:
		var btn_style = StyleBoxFlat.new()
		btn_style.bg_color = rarity_col.darkened(0.3)
		btn_style.set_corner_radius_all(int(tm.color("corner_radius")))
		btn.add_theme_stylebox_override("normal", btn_style)
		var btn_hover = btn_style.duplicate()
		btn_hover.bg_color = rarity_col.darkened(0.1)
		btn.add_theme_stylebox_override("hover", btn_hover)
	btn.pressed.connect(func(): _on_chosen(upgrade))
	vbox.add_child(btn)

	return card

func _on_chosen(upgrade: Dictionary):
	UpgradeManager.apply_combat(upgrade)
	visible = false
	get_parent().on_combat_upgrade_chosen()

func _style_title(lbl: Label, col: Color):
	lbl.add_theme_color_override("font_color", col)
	lbl.add_theme_font_size_override("font_size", 32)
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	lbl.add_theme_constant_override("shadow_offset_x", 2)
	lbl.add_theme_constant_override("shadow_offset_y", 2)

func _rarity_color(rarity: String) -> Color:
	var tm = UIThemeManager
	match rarity:
		"rare":   return tm.color("rarity_rare")
		"epic":   return tm.color("rarity_epic")
		_:        return tm.color("rarity_common")

func _rarity_bg(rarity: String) -> Color:
	var tm = UIThemeManager
	match rarity:
		"rare":   return tm.color("rarity_rare_bg")
		"epic":   return tm.color("rarity_epic_bg")
		_:        return tm.color("rarity_common_bg")

func _rarity_text(rarity: String) -> String:
	match rarity:
		"rare":   return "★★ 稀有"
		"epic":   return "★★★ 史诗"
		_:        return "★ 普通"
