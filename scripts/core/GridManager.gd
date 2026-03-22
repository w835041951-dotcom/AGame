## 扫雷区逻辑 - AutoLoad
## 翻到炸弹 = 加入库存，不再直接触发攻击
## 每层只生成一次扫雷图，多回合共享同一张图

extends Node

signal grid_revealed(x: int, y: int, cell_data: Dictionary)
signal bomb_found(x: int, y: int, bomb_type: String)

# 动态尺寸，每层 setup 时从 LevelData 更新
var cols: int = 10
var rows: int = 5
var bomb_count: int = 8

var grid: Array = []
var _grid_generated: bool = false
var is_magic_reveal: bool = false  # 透视升级触发时为true，用于动画区分

enum CellState { HIDDEN, REVEALED }

func generate_grid():
	if _grid_generated:
		return
	_grid_generated = true

	# 从 LevelData 读取当前层的扫雷大小
	var floor_n = GameManager.floor_number
	cols = LevelData.get_mine_cols(floor_n)
	rows = LevelData.get_mine_rows(floor_n)
	bomb_count = LevelData.get_bomb_count(floor_n)

	grid.clear()
	for y in range(rows):
		var row = []
		for x in range(cols):
			row.append({
				"state": CellState.HIDDEN,
				"is_bomb": false,
				"bomb_type": "",
				"adjacent": 0
			})
		grid.append(row)

	var positions = []
	for y in range(rows):
		for x in range(cols):
			positions.append(Vector2i(x, y))
	positions.shuffle()

	var bomb_types = BombRegistry.get_available_types()
	for i in range(bomb_count):
		var pos = positions[i]
		grid[pos.y][pos.x]["is_bomb"] = true
		grid[pos.y][pos.x]["bomb_type"] = bomb_types[randi() % bomb_types.size()]

	for y in range(rows):
		for x in range(cols):
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
	GameManager._check_no_bomb_no_mine()

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
				if nx >= 0 and nx < cols and ny >= 0 and ny < rows:
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
			if nx >= 0 and nx < cols and ny >= 0 and ny < rows:
				if grid[ny][nx]["is_bomb"]:
					count += 1
	return count

func get_cell(x: int, y: int) -> Dictionary:
	if x < 0 or x >= cols or y < 0 or y >= rows:
		return {}
	return grid[y][x]

func reset_for_new_floor():
	grid.clear()
	_grid_generated = false

func reveal_area(cx: int, cy: int, radius: int = 1):
	# 透视：强制揭示以(cx,cy)为中心的radius格范围（不扣点击次数）
	is_magic_reveal = true
	for dy in range(-radius, radius + 1):
		for dx in range(-radius, radius + 1):
			var nx = cx + dx
			var ny = cy + dy
			if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
				continue
			var cell = grid[ny][nx]
			if cell["state"] != CellState.HIDDEN:
				continue
			cell["state"] = CellState.REVEALED
			if cell["is_bomb"]:
				GameManager.add_bomb(cell["bomb_type"])
				bomb_found.emit(nx, ny, cell["bomb_type"])
			grid_revealed.emit(nx, ny, cell)
	is_magic_reveal = false
