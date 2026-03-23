## 放置区视图 - 上区（Boss + 炸弹放置）

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
var cell_size: int = 64

var cells: Array = []  # cells[y][x]
var _preview_cells: Array = []  # 当前高亮预览的格子坐标
var _preview_overlays: Array = []  # 预览覆盖层节点
var _preview_labels: Array = []  # 预览伤害数字

func _ready():
	BombPlacer.bomb_placed.connect(_on_bomb_placed)
	BombPlacer.bomb_removed.connect(_on_bomb_removed)
	BossGrid.boss_moved.connect(_on_boss_moved)
	BossGrid.tiles_refreshed.connect(_refresh_boss_tiles)
	BossGrid.field_changed.connect(_refresh_boss_tiles)
	BossGrid.phase_changed.connect(func(_p): _refresh_boss_tiles())
	BossGrid.tile_destroyed.connect(_on_tile_destroyed)
	GameManager.turn_started.connect(_on_turn_started)
	ExplosionCalc.explosion_visual.connect(_on_explosion_visual)
	ExplosionCalc.chain_triggered.connect(_on_chain_triggered)
	MinionGrid.minions_refreshed.connect(_refresh_minion_tiles)
	MinionGrid.minion_defeated.connect(_on_minion_defeated)
	ExplosionCalc.damage_numbers.connect(_on_damage_dealt)

func _on_turn_started():
	_build_grid()
	_refresh_boss_tiles()
	_update_danger_zone()
	_update_boss_dying()

func _build_grid():
	# 先停止所有持续动画
	_stop_boss_dying()
	_hide_danger_overlay()
	_clear_preview()

	cells.clear()
	for child in get_children():
		child.queue_free()

	cell_size = LevelData.get_cell_size(GameManager.floor_number)
	for y in range(BossGrid.placement_rows):
		var row = []
		for x in range(BossGrid.placement_cols):
			var cell = CellScene.instantiate()
			add_child(cell)
			cell.position = Vector2(x * cell_size, y * cell_size)
			cell.setup(x, y, Cell.Mode.PLACEMENT, cell_size)
			row.append(cell)
		cells.append(row)

func _refresh_boss_tiles():
	if cells.is_empty():
		return
	var rows = cells.size()
	var cols = cells[0].size()
	# 先把所有格子设回 EMPTY
	for y in range(rows):
		for x in range(cols):
			var world = Vector2i(x, y)
			if BombPlacer.placed_bombs.has(world):
				continue  # 已放炸弹的格子不覆盖
			if BossGrid.is_blocked_cell(world):
				cells[y][x].set_display_state(Cell.DisplayState.BLOCKED)
			else:
				cells[y][x].set_display_state(Cell.DisplayState.EMPTY)

	# 渲染小怪格子（优先级高于Boss）
	_refresh_minion_tiles()

	# 渲染 Boss 格子（若在小怪阶段，Boss格子不可见——Boss未入场）
	if MinionGrid.has_minions():
		return
	for local_pos in BossGrid.tiles:
		var tile = BossGrid.tiles[local_pos]
		var world = BossGrid.local_to_world(local_pos)
		if world.x < 0 or world.x >= cols:
			continue
		if world.y < 0 or world.y >= rows:
			continue
		if BombPlacer.placed_bombs.has(world):
			continue
		var state = _tile_state(tile)
		cells[world.y][world.x].set_display_state(state, {
			"hp": tile["hp"], "max_hp": tile["max_hp"], "part": tile["part"],
			"local_pos": local_pos
		})

	# 污染地块视觉提示
	for y in range(rows):
		for x in range(cols):
			var w = Vector2i(x, y)
			if BossGrid.is_shielded_cell(w):
				var c2 = cells[y][x]
				if c2._current_state != Cell.DisplayState.BOMB_PLACED and c2._current_state != Cell.DisplayState.BOSS_DEAD:
					c2.modulate = Color(0.75, 0.86, 1.0, 1.0)
			if BossGrid.is_polluted_cell(w):
				var c = cells[y][x]
				if c._current_state == Cell.DisplayState.EMPTY or c._current_state == Cell.DisplayState.BLOCKED:
					c.modulate = Color(0.75, 1.0, 0.75, 1.0)

func _refresh_minion_tiles():
	if cells.is_empty():
		return
	for world_pos in MinionGrid.minion_tiles:
		var tile = MinionGrid.minion_tiles[world_pos]
		if not tile["alive"]:
			continue
		if world_pos.y < 0 or world_pos.y >= cells.size():
			continue
		if world_pos.x < 0 or world_pos.x >= cells[world_pos.y].size():
			continue
		if BombPlacer.placed_bombs.has(world_pos):
			continue
		cells[world_pos.y][world_pos.x].set_display_state(Cell.DisplayState.MINION, {
			"hp": tile["hp"], "max_hp": tile["max_hp"],
			"label": tile["label"], "color": tile["color"]
		})

func _on_minion_defeated(world_pos: Vector2i, _drop_type: String):
	if world_pos.y >= 0 and world_pos.y < cells.size() and world_pos.x >= 0 and world_pos.x < cells[world_pos.y].size():
		cells[world_pos.y][world_pos.x].animate_destruction()
		await get_tree().create_timer(0.25).timeout
		if world_pos.y < cells.size() and world_pos.x < cells[world_pos.y].size():
			cells[world_pos.y][world_pos.x].set_display_state(Cell.DisplayState.EMPTY)

func _tile_state(tile: Dictionary) -> Cell.DisplayState:
	if not tile["alive"]:
		return Cell.DisplayState.BOSS_DEAD  # 死亡格子保留轮廓，可放炸弹
	match tile["type"]:
		BossGrid.TileType.WEAK:   return Cell.DisplayState.BOSS_WEAK
		BossGrid.TileType.ARMOR:  return Cell.DisplayState.BOSS_ARMOR
		BossGrid.TileType.ABSORB: return Cell.DisplayState.BOSS_ABSORB
		_:                        return Cell.DisplayState.BOSS_NORMAL

func _on_bomb_placed(pos: Vector2i, bomb_type: String):
	if pos.y >= 0 and pos.x >= 0 and pos.y < cells.size() and pos.x < cells[pos.y].size():
		cells[pos.y][pos.x].set_display_state(Cell.DisplayState.BOMB_PLACED, {"bomb_type": bomb_type})
		cells[pos.y][pos.x].animate_placement()

func _on_bomb_removed(pos: Vector2i):
	if pos.y < 0 or pos.y >= cells.size() or pos.x < 0 or pos.x >= cells[pos.y].size():
		return
	var tile = BossGrid.get_tile(pos)
	if not tile.is_empty():
		var local_pos = BossGrid.world_to_local(pos)
		cells[pos.y][pos.x].set_display_state(_tile_state(tile), {
			"hp": tile["hp"], "max_hp": tile["max_hp"], "part": tile["part"],
			"local_pos": local_pos
		})
	else:
		cells[pos.y][pos.x].set_display_state(Cell.DisplayState.EMPTY)

func _on_boss_moved(_new_origin: Vector2i):
	_refresh_boss_tiles()
	_update_boss_dying()
	_update_danger_zone()
	# Boss格子移动脉冲动画
	for local_pos in BossGrid.tiles:
		if not BossGrid.tiles[local_pos]["alive"]:
			continue
		var world = BossGrid.local_to_world(local_pos)
		if world.x >= 0 and world.x < BossGrid.placement_cols and world.y >= 0 and world.y < BossGrid.placement_rows:
			cells[world.y][world.x].animate_boss_pulse()

func _on_tile_destroyed(local_pos: Vector2i, _part):
	var world = BossGrid.local_to_world(local_pos)
	if world.x < 0 or world.y < 0 or world.y >= cells.size() or world.x >= cells[world.y].size():
		return
	cells[world.y][world.x].animate_destruction()
	await get_tree().create_timer(0.3).timeout
	if world.y < cells.size() and world.x < cells[world.y].size():
		cells[world.y][world.x].set_display_state(Cell.DisplayState.BOSS_DEAD, {
			"local_pos": local_pos
		})

func play_boss_death_sequence():
	_stop_boss_dying()
	# 从中心向外逐格爆碎
	var center = Vector2(BossGrid.boss_width * 0.5, BossGrid.boss_height * 0.5)
	var tile_delays: Array = []
	var max_dist: float = 0.0
	for local_pos in BossGrid.tiles:
		var dx = local_pos.x + 0.5 - center.x
		var dy = local_pos.y + 0.5 - center.y
		var dist = sqrt(dx * dx + dy * dy)
		max_dist = max(max_dist, dist)
		tile_delays.append({"local": local_pos, "dist": dist})
	tile_delays.sort_custom(func(a, b): return a["dist"] < b["dist"])
	var total_time: float = 0.8
	for entry in tile_delays:
		var world = BossGrid.local_to_world(entry["local"])
		if world.y < 0 or world.y >= cells.size() or world.x < 0 or world.x >= cells[world.y].size():
			continue
		var delay = (entry["dist"] / max(max_dist, 1.0)) * total_time
		cells[world.y][world.x].animate_boss_death(delay)
	await get_tree().create_timer(total_time + 0.4).timeout

func _on_explosion_visual(bomb_positions: Array, blast_cells: Array):
	# 炸弹原点闪光
	for pos in bomb_positions:
		if pos.y >= 0 and pos.y < cells.size() and pos.x >= 0 and pos.x < cells[pos.y].size():
			cells[pos.y][pos.x].set_display_state(Cell.DisplayState.EXPLODING)
	# 爆炸范围闪光（带微小延迟）
	for pos in blast_cells:
		if pos in bomb_positions:
			continue
		if pos.y >= 0 and pos.y < cells.size() and pos.x >= 0 and pos.x < cells[pos.y].size():
			cells[pos.y][pos.x].animate_explosion_hit(0.05)

func _on_chain_triggered(chained_positions: Array):
	for pos in chained_positions:
		if pos.y >= 0 and pos.y < cells.size() and pos.x >= 0 and pos.x < cells[pos.y].size():
			cells[pos.y][pos.x].animate_chain()

# ---- 炸弹范围预览 ----

func _process(_delta):
	if BombPlacer.phase != BombPlacer.Phase.PLACING:
		_clear_preview()
		return
	if cells.is_empty():
		return

	var mouse = get_local_mouse_position()
	var gx = int(mouse.x / cell_size)
	var gy = int(mouse.y / cell_size)

	if gx < 0 or gx >= BossGrid.placement_cols or gy < 0 or gy >= BossGrid.placement_rows:
		_clear_preview()
		return

	var pos = Vector2i(gx, gy)
	# 已放炸弹的格子不预览；活Boss格只允许虚体炸弹预览
	if pos in BombPlacer.placed_bombs:
		_clear_preview()
		return
	if BossGrid.is_blocked_cell(pos):
		_clear_preview()
		return
	if BossGrid.is_boss_tile(pos) and not BombRegistry.is_ethereal(BombPlacer.selected_type):
		_clear_preview()
		return

	var blast = ExplosionCalc.get_blast_cells(pos, BombPlacer.selected_type)
	# 检查预览是否变化
	if blast == _preview_cells:
		return
	_clear_preview()
	_preview_cells = blast

	# 计算基础伤害
	var bomb_type = BombPlacer.selected_type
	var base_dmg = BombRegistry.calculate_damage(bomb_type)

	for cell_pos in blast:
		if cell_pos.y < 0 or cell_pos.y >= cells.size() or cell_pos.x < 0 or cell_pos.x >= cells[cell_pos.y].size():
			continue
		var c = cells[cell_pos.y][cell_pos.x]
		if c._current_state == Cell.DisplayState.BOMB_PLACED \
				or c._current_state == Cell.DisplayState.EXPLODING \
				or c._current_state == Cell.DisplayState.BOSS_DEAD:
			continue

		# 创建半透明覆盖层
		var overlay = ColorRect.new()
		overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
		overlay.size = Vector2(cell_size, cell_size)
		overlay.position = Vector2(cell_pos.x * cell_size, cell_pos.y * cell_size)

		var is_boss = BossGrid.is_boss_tile(cell_pos)
		var is_origin = (cell_pos == pos)

		if is_origin:
			overlay.color = Color(1.0, 1.0, 0.3, 0.25)  # 放置点：亮黄
		elif is_boss:
			overlay.color = Color(1.0, 0.3, 0.1, 0.22)  # 命中Boss：红橙
		else:
			overlay.color = Color(1.0, 0.8, 0.2, 0.12)  # 空白范围：淡黄

		add_child(overlay)
		_preview_overlays.append(overlay)

		# 在Boss格子上显示预估伤害数字
		if is_boss and not is_origin:
			var lbl = Label.new()
			lbl.text = "-%d" % base_dmg
			lbl.add_theme_font_size_override("font_size", max(12, cell_size * 0.22))
			lbl.add_theme_color_override("font_color", Color(1.0, 0.4, 0.2, 0.85))
			lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
			lbl.add_theme_constant_override("shadow_offset_x", 1)
			lbl.add_theme_constant_override("shadow_offset_y", 1)
			lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			lbl.vertical_alignment = VERTICAL_ALIGNMENT_TOP
			lbl.position = Vector2(cell_pos.x * cell_size, cell_pos.y * cell_size + 1)
			lbl.size = Vector2(cell_size, cell_size * 0.4)
			lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
			add_child(lbl)
			_preview_labels.append(lbl)

func _clear_preview():
	for ov in _preview_overlays:
		if is_instance_valid(ov):
			ov.queue_free()
	_preview_overlays.clear()
	for lbl in _preview_labels:
		if is_instance_valid(lbl):
			lbl.queue_free()
	_preview_labels.clear()
	_preview_cells.clear()



func _on_damage_dealt(_cell_damages: Dictionary):
	# 伤害后检查Boss是否濒死
	_update_boss_dying()

# ---- 危险区警告 ----
var _danger_overlay: ColorRect = null
var _danger_tween: Tween = null
var _boss_dying_tween: Tween = null  # Boss濒死抖动/闪烁

func _update_danger_zone():
	# 计算Boss最近存活格子到左边界的距离
	var min_dist = 999
	for pos in BossGrid.tiles:
		if BossGrid.tiles[pos]["alive"]:
			var world_x = pos.x + BossGrid.boss_origin.x
			min_dist = min(min_dist, world_x)

	if min_dist <= 3:
		_show_danger_overlay(min_dist)
	else:
		_hide_danger_overlay()

func _show_danger_overlay(dist: int):
	if not _danger_overlay:
		_danger_overlay = ColorRect.new()
		_danger_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_danger_overlay.size = Vector2(BossGrid.placement_cols * cell_size, BossGrid.placement_rows * cell_size)
		add_child(_danger_overlay)
	# 越近越红越不透明
	var intensity = (4.0 - dist) / 4.0  # 0.25 ~ 1.0
	_danger_overlay.color = Color(1.0, 0.0, 0.0, 0.03 + intensity * 0.08)

	if _danger_tween and _danger_tween.is_valid():
		return  # 已在脉冲中
	_danger_tween = create_tween().set_loops()
	var base_a = _danger_overlay.color.a
	_danger_tween.tween_property(_danger_overlay, "color:a", base_a + 0.06, 0.6)
	_danger_tween.tween_property(_danger_overlay, "color:a", base_a, 0.6)

func _hide_danger_overlay():
	if _danger_tween and _danger_tween.is_valid():
		_danger_tween.kill()
		_danger_tween = null
	if _danger_overlay:
		_danger_overlay.queue_free()
		_danger_overlay = null

# ---- Boss濒死反应 (HP<25%) ----
func _update_boss_dying():
	if GameManager.boss_max_hp <= 0:
		_stop_boss_dying()
		return
	var hp_pct = float(GameManager.boss_hp) / GameManager.boss_max_hp
	if hp_pct > 0.0 and hp_pct <= 0.25:
		_start_boss_dying(hp_pct)
	else:
		_stop_boss_dying()

func _start_boss_dying(hp_pct: float):
	if _boss_dying_tween and _boss_dying_tween.is_valid():
		return  # 已经在闪烁中
	# 越低HP闪烁越快
	var speed = lerpf(0.5, 0.2, 1.0 - hp_pct / 0.25)
	_boss_dying_tween = create_tween().set_loops()

	# 闪烁：所有存活Boss格子 红色闪烁 + 微抖
	_boss_dying_tween.tween_callback(_boss_dying_flash.bind(true, speed))
	_boss_dying_tween.tween_interval(speed)
	_boss_dying_tween.tween_callback(_boss_dying_flash.bind(false, speed))
	_boss_dying_tween.tween_interval(speed)

func _boss_dying_flash(flash_on: bool, _speed: float):
	for local_pos in BossGrid.tiles:
		if not BossGrid.tiles[local_pos]["alive"]:
			continue
		var world = BossGrid.local_to_world(local_pos)
		if world.y < 0 or world.y >= cells.size() or world.x < 0 or world.x >= cells[world.y].size():
			continue
		var c = cells[world.y][world.x]
		if c._current_state == Cell.DisplayState.BOMB_PLACED:
			continue
		if flash_on:
			c.modulate = Color(1.5, 0.4, 0.3, 1.0)
			# 微抖动
			c.position = Vector2(world.x * cell_size + randf_range(-2, 2), world.y * cell_size + randf_range(-2, 2))
		else:
			c.modulate = Color.WHITE
			c.position = Vector2(world.x * cell_size, world.y * cell_size)

func _stop_boss_dying():
	if _boss_dying_tween and _boss_dying_tween.is_valid():
		_boss_dying_tween.kill()
		_boss_dying_tween = null
		# 恢复所有Boss格子
		for local_pos in BossGrid.tiles:
			if not BossGrid.tiles[local_pos]["alive"]:
				continue
			var world = BossGrid.local_to_world(local_pos)
			if world.y < 0 or world.y >= cells.size() or world.x < 0 or world.x >= cells[world.y].size():
				continue
			var c = cells[world.y][world.x]
			if c._current_state != Cell.DisplayState.BOMB_PLACED:
				c.modulate = Color.WHITE
				c.position = Vector2(world.x * cell_size, world.y * cell_size)
