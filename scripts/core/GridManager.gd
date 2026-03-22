## 扫雷格子数据和逻辑

extends Node

signal grid_revealed(x: int, y: int, cell_data: Dictionary)
signal bomb_triggered(x: int, y: int, bomb_type: String)

const COLS = 10
const ROWS = 8
const BOMB_COUNT = 15

var grid: Array = []  # Array of Dictionaries

enum CellState { HIDDEN, REVEALED, FLAGGED }

func generate_grid():
	grid.clear()
	# 初始化所有格子
	for y in range(ROWS):
		var row = []
		for x in range(COLS):
			row.append({
				"state": CellState.HIDDEN,
				"is_bomb": false,
				"bomb_type": "",
				"adjacent": 0
			})
		grid.append(row)

	# 随机放置炸弹
	var positions = []
	for y in range(ROWS):
		for x in range(COLS):
			positions.append(Vector2i(x, y))
	positions.shuffle()

	var bomb_types = BombRegistry.get_available_types()
	for i in range(BOMB_COUNT):
		var pos = positions[i]
		grid[pos.y][pos.x]["is_bomb"] = true
		grid[pos.y][pos.x]["bomb_type"] = bomb_types[randi() % bomb_types.size()]

	# 计算相邻数字
	for y in range(ROWS):
		for x in range(COLS):
			if not grid[y][x]["is_bomb"]:
				grid[y][x]["adjacent"] = count_adjacent_bombs(x, y)

func count_adjacent_bombs(x: int, y: int) -> int:
	var count = 0
	for dy in range(-1, 2):
		for dx in range(-1, 2):
			if dx == 0 and dy == 0:
				continue
			var nx = x + dx
			var ny = y + dy
			if nx >= 0 and nx < COLS and ny >= 0 and ny < ROWS:
				if grid[ny][nx]["is_bomb"]:
					count += 1
	return count

func reveal_cell(x: int, y: int):
	if not GameManager.use_click():
		return

	var cell = grid[y][x]
	if cell["state"] != CellState.HIDDEN:
		return

	cell["state"] = CellState.REVEALED

	if cell["is_bomb"]:
		bomb_triggered.emit(x, y, cell["bomb_type"])
	else:
		grid_revealed.emit(x, y, cell)
		# 空白格自动翻开周围（不消耗点击次数）
		if cell["adjacent"] == 0:
			auto_reveal_adjacent(x, y)

func auto_reveal_adjacent(x: int, y: int):
	for dy in range(-1, 2):
		for dx in range(-1, 2):
			if dx == 0 and dy == 0:
				continue
			var nx = x + dx
			var ny = y + dy
			if nx >= 0 and nx < COLS and ny >= 0 and ny < ROWS:
				var neighbor = grid[ny][nx]
				if neighbor["state"] == CellState.HIDDEN and not neighbor["is_bomb"]:
					neighbor["state"] = CellState.REVEALED
					grid_revealed.emit(nx, ny, neighbor)
					if neighbor["adjacent"] == 0:
						auto_reveal_adjacent(nx, ny)

func get_cell(x: int, y: int) -> Dictionary:
	return grid[y][x]
