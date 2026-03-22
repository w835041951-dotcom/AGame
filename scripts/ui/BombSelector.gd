## 炸弹选择工具栏 + 结束回合按钮

extends Control

@onready var type_container: HBoxContainer = $TypeContainer
@onready var end_turn_btn: Button = $EndTurnBtn
@onready var inventory_label: Label = $InventoryLabel

func _ready():
	GameManager.bomb_inventory_changed.connect(_refresh)
	GameManager.turn_started.connect(_rebuild)
	BombPlacer.bomb_placed.connect(func(_a,_b): _refresh())
	BombPlacer.bomb_removed.connect(func(_a): _refresh())
	end_turn_btn.pressed.connect(func(): GameManager.end_turn())
	_rebuild()

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
	btn.custom_minimum_size = Vector2(90, 52)
	btn.add_theme_font_size_override("font_size", 13)
	btn.toggle_mode = true
	btn.button_pressed = (type_id == BombPlacer.selected_type)
	var col = info.get("color", Color.WHITE)
	btn.add_theme_color_override("font_color", col)
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
