## 扫雷区逻辑 - AutoLoad
## 翻到炸弹 = 加入库存，不再直接触发攻击

extends Node

signal grid_revealed(x: int, y: int, cell_data: Dictionary)
signal bomb_found(x: int, y: int, bomb_type: String)

const COLS = 10
const ROWS = 5
const BOMB_COUNT = 12

var grid: Array = []

enum CellState { HIDDEN, REVEALED }

func generate_grid():
	grid.clear()
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
				grid[y][x]["adjacent"] = _count_adjacent(x, y)

func reveal_cell(x: int, y: int):
	var cell = grid[y][x]
	if cell["state"] != CellState.HIDDEN:
		return
	if not GameManager.use_click():
		return
	cell["state"] = CellState.REVEALED

	if cell["is_bomb"]:
		# 找到炸弹 = 加入库存
		GameManager.add_bomb(cell["bomb_type"])
		bomb_found.emit(x, y, cell["bomb_type"])
		grid_revealed.emit(x, y, cell)
	else:
		grid_revealed.emit(x, y, cell)
		if cell["adjacent"] == 0:
			_auto_reveal(x, y)

func _auto_reveal(start_x: int, start_y: int):
	var queue = [Vector2i(start_x, start_y)]
	while queue.size() > 0:
		var pos = queue.pop_front()
		for dy in range(-1, 2):
			for dx in range(-1, 2):
				if dx == 0 and dy == 0:
					continue
				var nx = pos.x + dx
				var ny = pos.y + dy
				if nx >= 0 and nx < COLS and ny >= 0 and ny < ROWS:
					var nb = grid[ny][nx]
					if nb["state"] == CellState.HIDDEN and not nb["is_bomb"]:
						nb["state"] = CellState.REVEALED
						grid_revealed.emit(nx, ny, nb)
						if nb["adjacent"] == 0:
							queue.append(Vector2i(nx, ny))

func _count_adjacent(x: int, y: int) -> int:
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

func get_cell(x: int, y: int) -> Dictionary:
	if x < 0 or x >= COLS or y < 0 or y >= ROWS:
		return {}
	return grid[y][x]
