## 探索区视图 - 下区

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
var cell_size: int = 64

var cells: Array = []

func _ready():
	GridManager.grid_revealed.connect(_on_revealed)
	GridManager.bomb_found.connect(_on_bomb_found)
	GameManager.turn_started.connect(_on_turn_started)
	GameManager.clicks_exhausted.connect(_on_clicks_exhausted)
	UpgradeManager.reveal_bombs_triggered.connect(_reveal_all_bombs)

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

func _on_bomb_found(x: int, y: int, bomb_type: String):
	cells[y][x].set_display_state(Cell.DisplayState.MINE_BOMB, {"bomb_type": bomb_type, "revealed": true})
	if GridManager.is_magic_reveal:
		cells[y][x].animate_magic_reveal()
	else:
		cells[y][x].animate_reveal()

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
