## 放置区视图 - 上区（Boss + 炸弹放置）

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
const CELL_SIZE = 58  # 56px + 2px gap

var cells: Array = []  # cells[y][x]

func _ready():
	BombPlacer.bomb_placed.connect(_on_bomb_placed)
	BombPlacer.bomb_removed.connect(_on_bomb_removed)
	BossGrid.boss_moved.connect(_on_boss_moved)
	BossGrid.tiles_refreshed.connect(_refresh_boss_tiles)
	BossGrid.tile_destroyed.connect(_on_tile_destroyed)
	GameManager.turn_started.connect(_on_turn_started)

func _on_turn_started():
	_build_grid()
	_refresh_boss_tiles()

func _build_grid():
	cells.clear()
	for child in get_children():
		child.queue_free()

	for y in range(BossGrid.PLACEMENT_ROWS):
		var row = []
		for x in range(BossGrid.PLACEMENT_COLS):
			var cell = CellScene.instantiate()
			add_child(cell)
			cell.position = Vector2(x * CELL_SIZE, y * CELL_SIZE)
			cell.setup(x, y, Cell.Mode.PLACEMENT)
			row.append(cell)
		cells.append(row)

func _refresh_boss_tiles():
	if cells.is_empty():
		return
	# 先把所有格子设回 EMPTY
	for y in range(BossGrid.PLACEMENT_ROWS):
		for x in range(BossGrid.PLACEMENT_COLS):
			var world = Vector2i(x, y)
			if BombPlacer.placed_bombs.has(world):
				continue  # 已放炸弹的格子不覆盖
			cells[y][x].set_display_state(Cell.DisplayState.EMPTY)

	# 渲染 Boss 格子
	for local_pos in BossGrid.tiles:
		var tile = BossGrid.tiles[local_pos]
		var world = BossGrid.local_to_world(local_pos)
		if world.x < 0 or world.x >= BossGrid.PLACEMENT_COLS:
			continue
		if world.y < 0 or world.y >= BossGrid.PLACEMENT_ROWS:
			continue
		var state = _tile_state(tile)
		cells[world.y][world.x].set_display_state(state, {
			"hp": tile["hp"], "max_hp": tile["max_hp"], "part": tile["part"]
		})

func _tile_state(tile: Dictionary) -> Cell.DisplayState:
	if not tile["alive"]:
		return Cell.DisplayState.BOSS_DEAD
	match tile["type"]:
		BossGrid.TileType.WEAK:   return Cell.DisplayState.BOSS_WEAK
		BossGrid.TileType.ARMOR:  return Cell.DisplayState.BOSS_ARMOR
		BossGrid.TileType.ABSORB: return Cell.DisplayState.BOSS_ABSORB
		_:                        return Cell.DisplayState.BOSS_NORMAL

func _on_bomb_placed(pos: Vector2i, bomb_type: String):
	if pos.y >= 0 and pos.x >= 0 and pos.y < cells.size() and pos.x < cells[pos.y].size():
		cells[pos.y][pos.x].set_display_state(Cell.DisplayState.BOMB_PLACED, {"bomb_type": bomb_type})

func _on_bomb_removed(pos: Vector2i):
	if pos.y < 0 or pos.y >= cells.size() or pos.x < 0 or pos.x >= cells[pos.y].size():
		return
	if BossGrid.is_boss_tile(pos):
		var tile = BossGrid.get_tile(pos)
		if tile.is_empty():
			cells[pos.y][pos.x].set_display_state(Cell.DisplayState.EMPTY)
		else:
			cells[pos.y][pos.x].set_display_state(_tile_state(tile), {
				"hp": tile["hp"], "max_hp": tile["max_hp"], "part": tile["part"]
			})
	else:
		cells[pos.y][pos.x].set_display_state(Cell.DisplayState.EMPTY)

func _on_boss_moved(_new_origin: Vector2i):
	_refresh_boss_tiles()

func _on_tile_destroyed(local_pos: Vector2i, _part):
	var world = BossGrid.local_to_world(local_pos)
	if world.y < cells.size() and world.x < cells[world.y].size():
		cells[world.y][world.x].set_display_state(Cell.DisplayState.BOSS_DEAD)
