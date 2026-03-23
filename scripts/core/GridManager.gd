## 探索区逻辑 - AutoLoad
## 翻到炸弹 = 加入库存，不再直接触发攻击
## 每层只生成一次探索图，多回合共享同一张图

extends Node

signal grid_revealed(x: int, y: int, cell_data: Dictionary)
signal bomb_found(x: int, y: int, bomb_type: String)
signal special_found(x: int, y: int, special_type: String)

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

	# 从 LevelData 读取当前层的探索区大小
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
				"adjacent": 0,
				"special_type": ""
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

	_assign_special_cells(positions.slice(bomb_count, positions.size()))

	for y in range(rows):
		for x in range(cols):
			if not grid[y][x]["is_bomb"]:
				grid[y][x]["adjacent"] = _count_adjacent(x, y)

func reveal_cell(x: int, y: int, use_intel_scan: bool = false):
	var cell = grid[y][x]
	if cell["state"] != CellState.HIDDEN:
		return
	if use_intel_scan:
		if not GameManager.use_intel(1):
			return
	else:
		if not GameManager.use_click():
			return
	cell["state"] = CellState.REVEALED

	if cell["is_bomb"]:
		# 找到炸弹 = 加入库存，只发 bomb_found（不发 grid_revealed 避免覆盖显示）
		GameManager.add_bomb(cell["bomb_type"])
		bomb_found.emit(x, y, cell["bomb_type"])
		GameManager.total_bombs_found += 1
		GameManager.bomb_streak += 1
		_try_lucky_find()
		_try_streak_bonus()
		_check_all_bombs_found()
	else:
		GameManager.bomb_streak = 0  # 非炸弹中断连击
		_handle_special_cell(x, y, cell)
		grid_revealed.emit(x, y, cell)
		if cell["adjacent"] == 0:
			_auto_reveal(x, y)
	# 检查是否无路可走（在 _auto_reveal 完成后再检查，避免漏检）
	GameManager.check_no_bomb_no_mine()

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
			else:
				_handle_special_cell(nx, ny, cell)
				grid_revealed.emit(nx, ny, cell)
	is_magic_reveal = false

func _assign_special_cells(available_positions: Array):
	if available_positions.is_empty():
		return
	available_positions.shuffle()
	var total = available_positions.size()
	var supply_n = max(1, int(total * 0.09))
	var relic_n = max(1, int(total * 0.04))
	var risk_n = max(1, int(total * 0.04))

	var idx = 0
	for _i in range(supply_n):
		if idx >= available_positions.size():
			break
		var p = available_positions[idx]
		grid[p.y][p.x]["special_type"] = "supply"
		idx += 1
	for _i in range(relic_n):
		if idx >= available_positions.size():
			break
		var p = available_positions[idx]
		grid[p.y][p.x]["special_type"] = "relic"
		idx += 1
	for _i in range(risk_n):
		if idx >= available_positions.size():
			break
		var p = available_positions[idx]
		grid[p.y][p.x]["special_type"] = "risk"
		idx += 1

func _handle_special_cell(x: int, y: int, cell: Dictionary):
	var sp = cell.get("special_type", "")
	if sp == "":
		return
	special_found.emit(x, y, sp)
	match sp:
		"supply":
			GameManager.current_clicks += 1
			GameManager.add_intel(1)
			GameManager.lucky_find.emit("supply", "补给箱：+1点击 +1情报")
		"relic":
			GameManager.add_intel(2)
			GameManager.add_reroll_token(1)
			var available = BombRegistry.get_available_types()
			if not available.is_empty() and randf() < 0.55:
				var target = available[randi() % available.size()]
				BombRegistry.add_random_affix(target)
			if randf() < 0.35:
				var t = BombRegistry.get_available_types()
				if not t.is_empty():
					var bonus = t[randi() % t.size()]
					GameManager.add_bomb(bonus)
			GameManager.lucky_find.emit("relic", "遗物：+2情报 +1重铸")
		"risk":
			GameManager.current_clicks = max(0, GameManager.current_clicks - 1)
			GameManager.add_intel(1)
			GameManager.lucky_find.emit("risk", "污染源：-1点击 +1情报")
	cell["special_type"] = ""

# ---- Lucky Find: 找到炸弹时有概率触发额外奖励 ----
func _try_lucky_find():
	var roll = randf()
	if roll < 0.10:
		# 10%: 额外获得1次点击
		GameManager.current_clicks += 1
		GameManager.lucky_find.emit("click", "+1 点击！")
	elif roll < 0.15:
		# 5%: 额外获得一个随机炸弹
		var types = BombRegistry.get_available_types()
		var bonus_type = types[randi() % types.size()]
		GameManager.add_bomb(bonus_type)
		var info = BombRegistry.get_bomb_info(bonus_type)
		GameManager.lucky_find.emit("bomb", "幸运！+1 %s" % info.get("name", "炸弹"))
	elif roll < 0.18:
		# 3%: 回复少量生命
		if GameManager.player_hp < GameManager.player_max_hp:
			GameManager.heal(3)
			GameManager.lucky_find.emit("heal", "幸运回复 +3 HP")

# ---- Streak: 连续找到炸弹的递增奖励 ----
func _try_streak_bonus():
	var streak = GameManager.bomb_streak
	if streak == 3:
		GameManager.current_clicks += 1
		GameManager.streak_bonus.emit(3, "三连！+1 点击")
	elif streak == 5:
		var types = BombRegistry.get_available_types()
		var bonus_type = types[randi() % types.size()]
		GameManager.add_bomb(bonus_type)
		GameManager.streak_bonus.emit(5, "五连！+1 炸弹")
	elif streak >= 7 and streak % 3 == 1:
		GameManager.heal(1)
		GameManager.current_clicks += 1
		GameManager.streak_bonus.emit(streak, "%d连！+1点击 +1HP" % streak)

# ---- Discovery Bonus: 找到所有炸弹时的额外奖励 ----
func _check_all_bombs_found():
	if GameManager.total_bombs_found >= bomb_count:
		# 全部找到! 奖励额外点击和回复
		GameManager.current_clicks += 2
		GameManager.heal(5)
		GameManager.lucky_find.emit("discovery", "全部发现！+2点击 +5HP")
