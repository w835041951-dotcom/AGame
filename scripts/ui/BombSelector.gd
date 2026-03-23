## 炸弹选择工具栏 + 结束回合按钮

extends Control

@onready var type_container: HBoxContainer = $TypeContainer
@onready var end_turn_btn: Button = $EndTurnBtn
@onready var inventory_label: Label = $InventoryLabel

func _ready():
	end_turn_btn.add_theme_font_size_override("font_size", 15)
	inventory_label.add_theme_font_size_override("font_size", 14)
	_apply_theme()
	UIThemeManager.theme_changed.connect(func(_n): _apply_theme(); _rebuild())
	GameManager.bomb_inventory_changed.connect(_refresh)
	GameManager.turn_started.connect(_rebuild)
	BombPlacer.bomb_placed.connect(func(_a,_b): _refresh())
	BombPlacer.bomb_removed.connect(func(_a): _refresh())
	end_turn_btn.pressed.connect(func(): GameManager.end_turn())
	_rebuild()

func _apply_theme():
	var tm = UIThemeManager
	inventory_label.add_theme_color_override("font_color", tm.color("text_secondary"))
	end_turn_btn.add_theme_color_override("font_color", tm.color("btn_end_text"))
	var cr = tm.color("corner_radius") as int
	var s = StyleBoxFlat.new()
	s.bg_color = tm.color("btn_end_bg")
	s.border_color = tm.color("btn_end_brd")
	s.set_border_width_all(2)
	s.set_corner_radius_all(cr)
	s.shadow_color = Color(0, 0, 0, 0.4)
	s.shadow_size = 2
	end_turn_btn.add_theme_stylebox_override("normal", s)
	var h = s.duplicate()
	h.bg_color = tm.color("btn_end_hover")
	h.border_color = tm.color("btn_end_hbrd")
	end_turn_btn.add_theme_stylebox_override("hover", h)
	var p = s.duplicate()
	p.bg_color = (tm.color("btn_end_bg") as Color).darkened(0.25)
	end_turn_btn.add_theme_stylebox_override("pressed", p)

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
			var info = BombRegistry.get_bomb_info(type_id)
			var lvl = BombRegistry.get_bomb_level(type_id)
			btn.text = "%s %s Lv.%d\n[%d]" % [_bomb_icon(type_id), info.get("name",""), lvl, count]
			btn.tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name",""), lvl, BombRegistry.get_range_description(type_id)]
			btn.disabled = (count == 0)
	inventory_label.text = "库存: %d" % GameManager.total_bombs()

func _make_type_btn(type_id: String) -> Button:
	var tm = UIThemeManager
	var info = BombRegistry.get_bomb_info(type_id)
	var btn = Button.new()
	btn.set_meta("type_id", type_id)
	btn.custom_minimum_size = Vector2(100, 52)
	btn.add_theme_font_size_override("font_size", 12)
	btn.toggle_mode = true
	btn.button_pressed = (type_id == BombPlacer.selected_type)
	var col = info.get("color", Color.WHITE)
	btn.add_theme_color_override("font_color", col.lightened(0.2))
	var cr = tm.color("corner_radius") as int
	var s = StyleBoxFlat.new()
	s.bg_color = tm.color("btn_normal_bg")
	s.border_color = tm.color("btn_normal_brd")
	s.set_border_width_all(2)
	s.set_corner_radius_all(cr)
	s.shadow_color = Color(0, 0, 0, 0.3)
	s.shadow_size = 1
	btn.add_theme_stylebox_override("normal", s)
	var hv = s.duplicate()
	hv.bg_color = tm.color("btn_hover_bg")
	hv.border_color = col.darkened(0.3)
	btn.add_theme_stylebox_override("hover", hv)
	var sel = s.duplicate()
	sel.bg_color = col.darkened(0.7)
	sel.border_color = col.darkened(0.2)
	sel.set_border_width_all(3)
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
		"x_shot": return "╳"
		"bounce": return "~"
		_: return "!"
