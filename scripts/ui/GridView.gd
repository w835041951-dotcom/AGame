## Grid 容器脚本 — 管理所有格子的生成和响应

extends Control

const CellScene = preload("res://scenes/game/Cell.tscn")

var cells: Array = []  # 2D array of Cell nodes

func _ready():
	GridManager.grid_revealed.connect(_on_cell_revealed)
	GridManager.bomb_triggered.connect(_on_bomb_triggered)
	GameManager.turn_started.connect(_on_turn_started)
	# 不在 _ready 里建格子，等 GameManager.start_turn() 触发 turn_started 信号再建

func _build_grid():
	cells.clear()
	# 清除旧节点
	for child in get_children():
		child.queue_free()

	for y in range(GridManager.ROWS):
		var row = []
		for x in range(GridManager.COLS):
			var cell = CellScene.instantiate()
			add_child(cell)
			cell.position = Vector2(x * 68, y * 68)  # 64px + 4px gap
			cell.setup(x, y)
			row.append(cell)
		cells.append(row)

	# 居中整个Grid
	var total_w = GridManager.COLS * 68
	var total_h = GridManager.ROWS * 68
	position = Vector2((1280 - total_w) / 2.0, (720 - total_h) / 2.0 + 40)

func _on_cell_revealed(x: int, y: int, data: Dictionary):
	cells[y][x].reveal(data)

func _on_bomb_triggered(x: int, y: int, bomb_type: String):
	cells[y][x].reveal({"is_bomb": true, "bomb_type": bomb_type, "adjacent": 0})
	cells[y][x].flash_bomb()
	BombEffect.trigger_bomb(x, y, bomb_type)

func _on_turn_started(_clicks: int):
	_build_grid()
	GridManager.generate_grid()
