## 扫雷区逻辑 - AutoLoad
## 翻到炸弹 = 加入库存，不再直接触发攻击
## 每层只生成一次扫雷图，多回合共享同一张图

extends Node

signal grid_revealed(x: int, y: int, cell_data: Dictionary)
signal bomb_found(x: int, y: int, bomb_type: String)

const COLS = 10
const ROWS = 5
var bomb_count: int = 8

var grid: Array = []
var _grid_generated: bool = false  # 本层是否已生成过扫雷图

enum CellState { HIDDEN, REVEALED }

func generate_grid():
	# 每层只生成一次，多回合共用同一张扫雷图
	if _grid_generated:
		return
	_grid_generated = true
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

	# 随机放置炸弹（数量由关卡决定）
	bomb_count = LevelData.get_bomb_count(GameManager.floor_number)
	var positions = []
	for y in range(ROWS):
		for x in range(COLS):
			positions.append(Vector2i(x, y))
	positions.shuffle()

	var bomb_types = BombRegistry.get_available_types()
	for i in range(bomb_count):
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
		# 找到炸弹 = 加入库存，只发 bomb_found（不发 grid_revealed 避免覆盖显示）
		GameManager.add_bomb(cell["bomb_type"])
		bomb_found.emit(x, y, cell["bomb_type"])
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

func reset_for_new_floor():
	grid.clear()
	_grid_generated = false

func reveal_area(cx: int, cy: int, radius: int = 1):
	# 透视：强制揭示以(cx,cy)为中心的radius格范围（不扣点击次数）
	for dy in range(-radius, radius + 1):
		for dx in range(-radius, radius + 1):
			var nx = cx + dx
			var ny = cy + dy
			if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
				continue
			var cell = grid[ny][nx]
			if cell["state"] != CellState.HIDDEN:
				continue
			cell["state"] = CellState.REVEALED
			if cell["is_bomb"]:
				GameManager.add_bomb(cell["bomb_type"])
				bomb_found.emit(nx, ny, cell["bomb_type"])
			grid_revealed.emit(nx, ny, cell)
