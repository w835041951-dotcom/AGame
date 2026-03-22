## 炸弹选择工具栏 + 结束回合按钮

extends Control

@onready var type_container: HBoxContainer = $TypeContainer
@onready var end_turn_btn: Button = $EndTurnBtn
@onready var inventory_label: Label = $InventoryLabel

func _ready():
	end_turn_btn.add_theme_font_size_override("font_size", 15)
	inventory_label.add_theme_font_size_override("font_size", 14)
	inventory_label.add_theme_color_override("font_color", Color(0.72, 0.68, 0.58))
	_style_end_turn_btn()
	GameManager.bomb_inventory_changed.connect(_refresh)
	GameManager.turn_started.connect(_rebuild)
	BombPlacer.bomb_placed.connect(func(_a,_b): _refresh())
	BombPlacer.bomb_removed.connect(func(_a): _refresh())
	end_turn_btn.pressed.connect(func(): GameManager.end_turn())
	_rebuild()

func _style_end_turn_btn():
	end_turn_btn.add_theme_color_override("font_color", Color(0.95, 0.85, 0.45))
	var s = StyleBoxFlat.new()
	s.bg_color = Color(0.18, 0.15, 0.12)
	s.border_color = Color(0.55, 0.45, 0.25)
	s.set_border_width_all(2)
	s.set_corner_radius_all(4)
	s.shadow_color = Color(0, 0, 0, 0.4)
	s.shadow_size = 2
	end_turn_btn.add_theme_stylebox_override("normal", s)
	var h = s.duplicate()
	h.bg_color = Color(0.25, 0.20, 0.15)
	h.border_color = Color(0.70, 0.58, 0.30)
	end_turn_btn.add_theme_stylebox_override("hover", h)
	var p = s.duplicate()
	p.bg_color = Color(0.12, 0.10, 0.08)
	end_turn_btn.add_theme_stylebox_override("pressed", p)

func _rebuild(_n = null):
	for child in type_container.get_children():
		child.queue_free()
	for type_id in BombRegistry.get_available_types():
		var btn = _make_type_btn(type_id)
		type_container.add_child(btn)
	_refresh()

func _refresh(_n = null):
	# 更新每个按钮上的库存数字
	for btn in type_container.get_children():
		var type_id = btn.get_meta("type_id", "")
		if type_id != "":
			var count = GameManager.get_bomb_count(type_id)
			var info = BombRegistry.get_bomb_info(type_id)
			btn.text = "%s %s\n[%d]" % [_bomb_icon(type_id), info.get("name",""), count]
			btn.disabled = (count == 0)
	# 总库存
	inventory_label.text = "库存: %d" % GameManager.total_bombs()

func _make_type_btn(type_id: String) -> Button:
	var info = BombRegistry.get_bomb_info(type_id)
	var btn = Button.new()
	btn.set_meta("type_id", type_id)
	btn.custom_minimum_size = Vector2(100, 52)
	btn.add_theme_font_size_override("font_size", 12)
	btn.toggle_mode = true
	btn.button_pressed = (type_id == BombPlacer.selected_type)
	var col = info.get("color", Color.WHITE)
	btn.add_theme_color_override("font_color", col.lightened(0.2))
	# 地牢石按钮样式
	var s = StyleBoxFlat.new()
	s.bg_color = Color(0.14, 0.13, 0.11)
	s.border_color = Color(0.32, 0.28, 0.22)
	s.set_border_width_all(2)
	s.set_corner_radius_all(4)
	s.shadow_color = Color(0, 0, 0, 0.3)
	s.shadow_size = 1
	btn.add_theme_stylebox_override("normal", s)
	var hv = s.duplicate()
	hv.bg_color = Color(0.22, 0.19, 0.15)
	hv.border_color = col.darkened(0.3)
	btn.add_theme_stylebox_override("hover", hv)
	var sel = s.duplicate()
	sel.bg_color = col.darkened(0.7)
	sel.border_color = col.darkened(0.2)
	sel.set_border_width_all(3)
	btn.add_theme_stylebox_override("pressed", sel)
	# 加载炸弹图标
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
		"cross": return "+"
		"scatter": return "*"
		"bounce": return "~"
		"pierce": return "|"
		"area": return "#"
		_: return "!"
