## 探索区视图 - 下区

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
var cell_size: int = 64

var cells: Array = []
var _reveal_combo: int = 0  # 连续翻开格子计数
var _combo_timer: float = 0.0  # 连击超时
var _combo_label: Label = null

func _ready():
	GridManager.grid_revealed.connect(_on_revealed)
	GridManager.bomb_found.connect(_on_bomb_found)
	GridManager.special_found.connect(_on_special_found)
	GameManager.turn_started.connect(_on_turn_started)
	GameManager.clicks_exhausted.connect(_on_clicks_exhausted)
	UpgradeManager.reveal_bombs_triggered.connect(_reveal_all_bombs)

func _process(delta):
	if _combo_timer > 0:
		_combo_timer -= delta
		if _combo_timer <= 0 and _reveal_combo >= 6:
			_show_combo_popup(_reveal_combo)
			_reveal_combo = 0

func _on_clicks_exhausted():
	for row in cells:
		for cell in row:
			if not cell.disabled:
				cell.disabled = true

func _on_turn_started():
	if GridManager.grid.is_empty():
		GridManager.generate_grid()
		_build_grid()
		if UpgradeManager.is_reveal_bombs():
			_reveal_all_bombs()
	else:
		# 探索图已存在，保留格子对象（右键标记保留），只重置可点击性
		_restore_clickable()
		if UpgradeManager.is_reveal_bombs():
			_reveal_all_bombs()

func _build_grid():
	cells.clear()
	for child in get_children():
		child.queue_free()

	cell_size = LevelData.get_cell_size(GameManager.floor_number)
	for y in range(GridManager.rows):
		var row = []
		for x in range(GridManager.cols):
			var cell = CellScene.instantiate()
			add_child(cell)
			cell.position = Vector2(x * cell_size, y * cell_size)
			cell.setup(x, y, Cell.Mode.MINE, cell_size)
			row.append(cell)
		cells.append(row)

func _restore_clickable():
	for y in range(GridManager.rows):
		for x in range(GridManager.cols):
			var data = GridManager.get_cell(x, y)
			if data.get("state") == GridManager.CellState.HIDDEN:
				cells[y][x].disabled = false

func _on_revealed(x: int, y: int, data: Dictionary):
	cells[y][x].set_display_state(Cell.DisplayState.MINE_REVEALED, {"adjacent": data["adjacent"]})
	if GridManager.is_magic_reveal:
		cells[y][x].animate_magic_reveal()
	else:
		cells[y][x].animate_reveal()
	_reveal_combo += 1
	_combo_timer = 0.15  # 150ms内连续翻开算combo
	var sp = data.get("special_type", "")
	if sp != "":
		_show_special_popup(cells[y][x].position, sp)

func _on_bomb_found(x: int, y: int, bomb_type: String):
	cells[y][x].set_display_state(Cell.DisplayState.MINE_BOMB, {"bomb_type": bomb_type, "revealed": true})
	if GridManager.is_magic_reveal:
		cells[y][x].animate_magic_reveal()
	else:
		cells[y][x].animate_reveal()
		_celebrate_bomb_found(x, y)
	# 稀有炸弹特殊视觉
	if _is_rare_bomb(bomb_type):
		_add_rare_bomb_glow(x, y, bomb_type)

func _reveal_all_bombs():
	for y in range(GridManager.rows):
		for x in range(GridManager.cols):
			var cell = GridManager.get_cell(x, y)
			if cell.get("is_bomb", false) and cell.get("state") == GridManager.CellState.HIDDEN:
				cells[y][x].set_display_state(Cell.DisplayState.MINE_BOMB, {"bomb_type": cell["bomb_type"]})
				cells[y][x].animate_magic_reveal()

func count_correct_marks() -> int:
	var count = 0
	for y in range(cells.size()):
		for x in range(cells[y].size()):
			if cells[y][x].is_marked():
				var data = GridManager.get_cell(x, y)
				if data.get("is_bomb", false):
					count += 1
	return count

# ---- 找到炸弹的庆祝效果 ----
func _celebrate_bomb_found(x: int, y: int):
	var cell_node = cells[y][x]
	# 脉冲放大 + 金色闪光
	cell_node.pivot_offset = cell_node.size / 2
	var tw = create_tween()
	tw.tween_property(cell_node, "modulate", UIThemeManager.color("text_accent").lightened(0.8), 0.08)
	tw.tween_property(cell_node, "scale", Vector2(1.3, 1.3), 0.08).set_trans(Tween.TRANS_BACK)
	tw.set_parallel(false)
	tw.tween_property(cell_node, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(cell_node, "modulate", Color.WHITE, 0.2)

	# 显示连击数（如果streak >= 2）
	if GameManager.bomb_streak >= 2:
		var streak_lbl = Label.new()
		streak_lbl.text = "×%d" % GameManager.bomb_streak
		streak_lbl.add_theme_font_size_override("font_size", 26)
		streak_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_accent") if GameManager.bomb_streak < 5 else UIThemeManager.color("text_danger"))
		streak_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
		streak_lbl.add_theme_constant_override("shadow_offset_x", 1)
		streak_lbl.add_theme_constant_override("shadow_offset_y", 1)
		streak_lbl.position = cell_node.position + Vector2(cell_size * 0.6, -10)
		streak_lbl.modulate = Color(1, 1, 1, 0)
		add_child(streak_lbl)
		var tw2 = create_tween()
		tw2.tween_property(streak_lbl, "modulate:a", 1.0, 0.08)
		tw2.tween_property(streak_lbl, "position:y", streak_lbl.position.y - 20, 0.4)
		tw2.parallel().tween_property(streak_lbl, "modulate:a", 0.0, 0.2).set_delay(0.25)
		tw2.tween_callback(streak_lbl.queue_free)

# ---- Combo 弹窗 ----
func _show_combo_popup(combo: int):
	var text: String
	var color: Color
	var tm = UIThemeManager
	if combo >= 20:
		text = "超级探索！×%d" % combo
		color = tm.color("rarity_epic")
	elif combo >= 12:
		text = "大范围探索！×%d" % combo
		color = tm.color("rarity_rare")
	else:
		text = "连锁探索 ×%d" % combo
		color = tm.color("text_accent")

	if _combo_label and is_instance_valid(_combo_label):
		_combo_label.queue_free()

	_combo_label = Label.new()
	_combo_label.text = text
	_combo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_combo_label.position = Vector2(0, -36)
	_combo_label.size = Vector2(size.x if size.x > 0 else 800, 48)
	_combo_label.add_theme_font_size_override("font_size", 32)
	_combo_label.add_theme_color_override("font_color", color)
	_combo_label.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	_combo_label.add_theme_constant_override("shadow_offset_x", 2)
	_combo_label.add_theme_constant_override("shadow_offset_y", 2)
	_combo_label.modulate = Color(1, 1, 1, 0)
	_combo_label.pivot_offset = Vector2(_combo_label.size.x / 2, 20)
	add_child(_combo_label)

	var tw = create_tween()
	tw.tween_property(_combo_label, "modulate:a", 1.0, 0.1)
	tw.tween_property(_combo_label, "scale", Vector2(1.15, 1.15), 0.1).set_trans(Tween.TRANS_BACK)
	tw.tween_property(_combo_label, "scale", Vector2.ONE, 0.08)
	tw.tween_interval(0.8)
	tw.tween_property(_combo_label, "modulate:a", 0.0, 0.3)
	tw.tween_callback(_combo_label.queue_free)

	# Combo奖励：大范围探索+1点击
	if combo >= 12:
		GameManager.current_clicks += 1

func _on_special_found(x: int, y: int, special_type: String):
	if y < 0 or y >= cells.size() or x < 0 or x >= cells[y].size():
		return
	_show_special_popup(cells[y][x].position, special_type)

func _show_special_popup(pos: Vector2, special_type: String):
	var text = ""
	var color = UIThemeManager.color("text_accent")
	match special_type:
		"supply":
			text = "补给箱"
			color = UIThemeManager.color("text_heal")
		"relic":
			text = "遗物"
			color = UIThemeManager.color("rarity_rare")
		"risk":
			text = "污染源"
			color = UIThemeManager.color("text_danger")
		_:
			return
	var lbl = Label.new()
	lbl.text = text
	lbl.add_theme_font_size_override("font_size", max(14, cell_size * 0.26))
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	lbl.add_theme_constant_override("shadow_offset_x", 1)
	lbl.add_theme_constant_override("shadow_offset_y", 1)
	lbl.position = pos + Vector2(4, 4)
	lbl.modulate = Color(1, 1, 1, 0)
	add_child(lbl)
	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.1)
	tw.tween_property(lbl, "position:y", lbl.position.y - 18, 0.45)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.25).set_delay(0.25)
	tw.tween_callback(lbl.queue_free)

# ---- 稀有炸弹视觉区分 ----
const RARE_BOMBS = ["cross", "x_shot", "bounce", "scatter"]

func _is_rare_bomb(bomb_type: String) -> bool:
	return bomb_type in RARE_BOMBS

func _add_rare_bomb_glow(x: int, y: int, bomb_type: String):
	var cell_node = cells[y][x]
	var info = BombRegistry.get_bomb_info(bomb_type)
	var bomb_color: Color = info.get("color", Color.WHITE)

	# 发光边框
	var glow = ColorRect.new()
	glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glow.size = Vector2(cell_size, cell_size)
	glow.position = cell_node.position
	glow.color = Color(bomb_color.r, bomb_color.g, bomb_color.b, 0.0)
	add_child(glow)

	# 呼吸脉冲动画（持续闪烁边框）
	var tw = create_tween().set_loops(6)
	tw.tween_property(glow, "color:a", 0.25, 0.4).set_trans(Tween.TRANS_SINE)
	tw.tween_property(glow, "color:a", 0.05, 0.4).set_trans(Tween.TRANS_SINE)
	tw.finished.connect(glow.queue_free)

	# 星星粒子效果
	for i in range(4):
		var star = Label.new()
		star.text = "✦"
		star.add_theme_font_size_override("font_size", randi_range(10, 16))
		star.add_theme_color_override("font_color", bomb_color.lightened(0.4))
		star.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var sx = cell_node.position.x + randf_range(2, cell_size - 10)
		var sy = cell_node.position.y + randf_range(2, cell_size - 10)
		star.position = Vector2(sx, sy)
		star.modulate = Color(1, 1, 1, 0)
		add_child(star)
		var tw2 = create_tween()
		tw2.tween_interval(i * 0.12)
		tw2.tween_property(star, "modulate:a", 1.0, 0.15)
		tw2.tween_property(star, "position:y", sy - 18, 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw2.parallel().tween_property(star, "modulate:a", 0.0, 0.25).set_delay(0.3)
		tw2.tween_callback(star.queue_free)

	# "稀有!" 文字提示
	var rarity_lbl = Label.new()
	var rarity_name = {"cross": "十字", "x_shot": "X弹", "bounce": "反弹", "scatter": "散射"}.get(bomb_type, "稀有")
	rarity_lbl.text = "★ %s" % rarity_name
	rarity_lbl.add_theme_font_size_override("font_size", 16)
	rarity_lbl.add_theme_color_override("font_color", bomb_color.lightened(0.5))
	rarity_lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	rarity_lbl.add_theme_constant_override("shadow_offset_x", 1)
	rarity_lbl.add_theme_constant_override("shadow_offset_y", 1)
	rarity_lbl.position = cell_node.position + Vector2(cell_size * 0.5 - 20, -18)
	rarity_lbl.modulate = Color(1, 1, 1, 0)
	rarity_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rarity_lbl)
	var tw3 = create_tween()
	tw3.tween_property(rarity_lbl, "modulate:a", 1.0, 0.12)
	tw3.tween_interval(1.0)
	tw3.tween_property(rarity_lbl, "modulate:a", 0.0, 0.3)
	tw3.tween_callback(rarity_lbl.queue_free)
