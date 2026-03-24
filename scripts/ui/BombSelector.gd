## 炸弹选择工具栏 + 结束回合按钮

extends Control

@onready var type_container: HBoxContainer = $TypeContainer
@onready var end_turn_btn: Button = $EndTurnBtn
@onready var reset_btn: Button = $ResetBtn
@onready var inventory_label: Label = $InventoryLabel

signal reset_board_pressed

func _ready():
	end_turn_btn.add_theme_font_size_override("font_size", 18)
	reset_btn.add_theme_font_size_override("font_size", 16)
	inventory_label.add_theme_font_size_override("font_size", 15)
	_apply_theme()
	UIThemeManager.theme_changed.connect(func(_n): _apply_theme(); _rebuild())
	GameManager.bomb_inventory_changed.connect(_refresh)
	GameManager.turn_started.connect(_rebuild)
	BombPlacer.bomb_placed.connect(func(_a,_b): _refresh())
	BombPlacer.bomb_removed.connect(func(_a): _refresh())
	end_turn_btn.pressed.connect(func(): GameManager.end_turn())
	reset_btn.pressed.connect(func(): reset_board_pressed.emit())
	_rebuild()

func _apply_theme():
	var tm = UIThemeManager
	inventory_label.add_theme_color_override("font_color", tm.color("text_secondary"))
	inventory_label.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	inventory_label.add_theme_constant_override("shadow_offset_x", 1)
	inventory_label.add_theme_constant_override("shadow_offset_y", 1)
	end_turn_btn.add_theme_color_override("font_color", tm.color("btn_end_text"))
	end_turn_btn.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	end_turn_btn.add_theme_constant_override("shadow_offset_x", 1)
	end_turn_btn.add_theme_constant_override("shadow_offset_y", 1)
	var sn = tm.make_themed_stylebox("btn_end_normal", "btn_end_bg", "btn_end_brd")
	end_turn_btn.add_theme_stylebox_override("normal", sn)
	var sh = tm.make_themed_stylebox("btn_end_hover", "btn_end_hover", "btn_end_hbrd")
	end_turn_btn.add_theme_stylebox_override("hover", sh)
	end_turn_btn.add_theme_stylebox_override("pressed", sh)
	# Reset button styling
	reset_btn.add_theme_color_override("font_color", tm.color("text_primary"))
	var rsn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
	reset_btn.add_theme_stylebox_override("normal", rsn)
	var rsh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong")
	reset_btn.add_theme_stylebox_override("hover", rsh)
	reset_btn.add_theme_stylebox_override("pressed", rsh)

func _rebuild(_n = null):
	for child in type_container.get_children():
		child.queue_free()
	for type_id in BombRegistry.get_available_types():
		var btn = _make_type_btn(type_id)
		type_container.add_child(btn)
	_refresh()

func _refresh(_n = null):
	for btn in type_container.get_children():
		var type_id = btn.get_meta("type_id", "")
		if type_id != "":
			var count = GameManager.get_bomb_count(type_id)
			var cd = GameManager.bomb_cooldowns.get(type_id, 0)
			var info = BombRegistry.get_bomb_info(type_id)
			var lvl = BombRegistry.get_bomb_level(type_id)
			var cd_text = "" if cd <= 0 else "\n冷却:%d" % cd
			btn.text = "%s Lv%d ×%d%s" % [info.get("name",""), lvl, count, cd_text]
			var aff = BombRegistry.get_affixes(type_id)
			var aff_text = "无" if aff.is_empty() else ",".join(aff)
			btn.tooltip_text = "%s  Lv.%d\n范围: %s\n词条: %s" % [info.get("name",""), lvl, BombRegistry.get_range_description(type_id), aff_text]
			btn.disabled = (count == 0 or cd > 0)
	inventory_label.text = "库存: %d" % GameManager.total_bombs()

func _make_type_btn(type_id: String) -> Button:
	var tm = UIThemeManager
	var info = BombRegistry.get_bomb_info(type_id)
	var btn = Button.new()
	btn.set_meta("type_id", type_id)
	btn.custom_minimum_size = Vector2(160, 72)
	btn.add_theme_font_size_override("font_size", 14)
	btn.toggle_mode = true
	btn.button_pressed = (type_id == BombPlacer.selected_type)
	btn.expand_icon = true
	btn.icon_alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.add_theme_constant_override("icon_max_width", 36)
	var col = info.get("color", Color.WHITE)
	btn.add_theme_color_override("font_color", col.lightened(0.3))
	btn.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	btn.add_theme_constant_override("shadow_offset_x", 1)
	btn.add_theme_constant_override("shadow_offset_y", 1)
	var sn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
	btn.add_theme_stylebox_override("normal", sn)
	var sh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "btn_normal_brd")
	btn.add_theme_stylebox_override("hover", sh)
	var sp = tm.make_themed_stylebox("btn_pressed", "btn_normal_bg", "btn_normal_brd")
	if sp:
		btn.add_theme_stylebox_override("pressed", sp)
	else:
		var sel = StyleBoxFlat.new()
		sel.bg_color = col.darkened(0.7)
		sel.border_color = col.darkened(0.2)
		sel.set_border_width_all(3)
		sel.set_corner_radius_all(int(tm.color("corner_radius")))
		btn.add_theme_stylebox_override("pressed", sel)
	var tex_path = "res://assets/sprites/bombs/%s.png" % type_id
	if ResourceLoader.exists(tex_path):
		btn.icon = load(tex_path)
	btn.pressed.connect(func():
		BombPlacer.set_selected_type(type_id)
		_update_selection()
	)
	return btn

func _update_selection():
	for btn in type_container.get_children():
		var type_id = btn.get_meta("type_id", "")
		btn.button_pressed = (type_id == BombPlacer.selected_type)

func _bomb_icon(type_id: String) -> String:
	match type_id:
		"pierce_h": return "↔"
		"pierce_v": return "↕"
		"cross": return "+"
		"fan": return "◢"
		"x_shot": return "╳"
		"second_blast": return "◎"
		"freeze_bomb": return "❄"
		"magnetic": return "🧲"
		"bounce": return "~"
		"blackhole": return "●"
		"ultimate": return "★"
		_: return "!"
