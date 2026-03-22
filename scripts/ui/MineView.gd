## 扫雷区视图 - 下区

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")
const Cell = preload("res://scripts/ui/Cell.gd")
const CELL_SIZE = 58

var cells: Array = []

func _ready():
	GridManager.grid_revealed.connect(_on_revealed)
	GridManager.bomb_found.connect(_on_bomb_found)
	GameManager.turn_started.connect(_on_turn_started)

func _on_turn_started():
	_build_grid()
	GridManager.generate_grid()
	if UpgradeManager.is_reveal_bombs():
		_reveal_all_bombs()

func _build_grid():
	cells.clear()
	for child in get_children():
		child.queue_free()

	for y in range(GridManager.ROWS):
		var row = []
		for x in range(GridManager.COLS):
			var cell = CellScene.instantiate()
			add_child(cell)
			cell.position = Vector2(x * CELL_SIZE, y * CELL_SIZE)
			cell.setup(x, y, Cell.Mode.MINE)
			row.append(cell)
		cells.append(row)

func _on_revealed(x: int, y: int, data: Dictionary):
	cells[y][x].set_display_state(Cell.DisplayState.MINE_REVEALED, {"adjacent": data["adjacent"]})

func _on_bomb_found(x: int, y: int, bomb_type: String):
	cells[y][x].set_display_state(Cell.DisplayState.MINE_BOMB, {"bomb_type": bomb_type})

func _reveal_all_bombs():
	for y in range(GridManager.ROWS):
		for x in range(GridManager.COLS):
			var cell = GridManager.get_cell(x, y)
			if cell.get("is_bomb", false) and cell.get("state") == GridManager.CellState.HIDDEN:
				cells[y][x].set_display_state(Cell.DisplayState.MINE_BOMB, {"bomb_type": cell["bomb_type"]})
