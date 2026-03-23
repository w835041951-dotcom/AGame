## 放置区视图 - 上区（Boss + 炸弹放置）

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
var cell_size: int = 64

var cells: Array = []  # cells[y][x]
var _preview_cells: Array = []  # 当前高亮预览的格子坐标

func _ready():
	BombPlacer.bomb_placed.connect(_on_bomb_placed)
	BombPlacer.bomb_removed.connect(_on_bomb_removed)
	BossGrid.boss_moved.connect(_on_boss_moved)
	BossGrid.tiles_refreshed.connect(_refresh_boss_tiles)
	BossGrid.tile_destroyed.connect(_on_tile_destroyed)
	GameManager.turn_started.connect(_on_turn_started)
	ExplosionCalc.explosion_visual.connect(_on_explosion_visual)
	ExplosionCalc.chain_triggered.connect(_on_chain_triggered)
	MinionGrid.minions_refreshed.connect(_refresh_minion_tiles)
	MinionGrid.minion_defeated.connect(_on_minion_defeated)

func _on_turn_started():
	_build_grid()
	_refresh_boss_tiles()

func _build_grid():
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
	# 先把所有格子设回 EMPTY
	for y in range(BossGrid.placement_rows):
		for x in range(BossGrid.placement_cols):
			var world = Vector2i(x, y)
			if BombPlacer.placed_bombs.has(world):
				continue  # 已放炸弹的格子不覆盖
			cells[y][x].set_display_state(Cell.DisplayState.EMPTY)

	# 渲染小怪格子（优先级高于Boss）
	_refresh_minion_tiles()

	# 渲染 Boss 格子（若在小怪阶段，Boss格子不可见——Boss未入场）
	if MinionGrid.has_minions():
		return
	for local_pos in BossGrid.tiles:
		var tile = BossGrid.tiles[local_pos]
		var world = BossGrid.local_to_world(local_pos)
		if world.x < 0 or world.x >= BossGrid.placement_cols:
			continue
		if world.y < 0 or world.y >= BossGrid.placement_rows:
			continue
		if BombPlacer.placed_bombs.has(world):
			continue
		var state = _tile_state(tile)
		cells[world.y][world.x].set_display_state(state, {
			"hp": tile["hp"], "max_hp": tile["max_hp"], "part": tile["part"],
			"local_pos": local_pos
		})

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
	# 只在可放置的空格/死亡格上显示预览
	if BossGrid.is_boss_tile(pos) or pos in BombPlacer.placed_bombs:
		_clear_preview()
		return

	var blast = ExplosionCalc.get_blast_cells(pos, BombPlacer.selected_type)
	# 检查预览是否变化
	if blast == _preview_cells:
		return
	_clear_preview()
	_preview_cells = blast
	for cell_pos in blast:
		if cell_pos.y >= 0 and cell_pos.y < cells.size() and cell_pos.x >= 0 and cell_pos.x < cells[cell_pos.y].size():
			var c = cells[cell_pos.y][cell_pos.x]
			if c._current_state != Cell.DisplayState.BOMB_PLACED \
					and c._current_state != Cell.DisplayState.EXPLODING \
					and c._current_state != Cell.DisplayState.BOSS_DEAD:
				c.modulate = Color(1.3, 1.1, 0.7, 0.85)

func _clear_preview():
	for cell_pos in _preview_cells:
		if cell_pos.y >= 0 and cell_pos.y < cells.size() and cell_pos.x >= 0 and cell_pos.x < cells[cell_pos.y].size():
			var c = cells[cell_pos.y][cell_pos.x]
			if c._current_state == Cell.DisplayState.BOSS_DEAD:
				c.modulate = Color(0.35, 0.3, 0.3, 0.5)
			elif c._current_state != Cell.DisplayState.EXPLODING:
				c.modulate = Color.WHITE
	_preview_cells.clear()
