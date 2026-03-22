## 爆炸范围计算 + 伤害结算 - AutoLoad

extends Node

signal explosion_visual(bomb_positions: Array, blast_cells: Array)

# ---- 爆炸范围计算 ----

func get_blast_cells(origin: Vector2i, bomb_type: String) -> Array:
	match bomb_type:
		"cross":   return _cross(origin, 3)
		"scatter": return _rect(origin, 1)
		"area":    return _rect(origin, 2)
		"pierce":  return _pierce(origin)
		"bounce":  return _bounce(origin)
		_:         return _cross(origin, 2)

func _cross(origin: Vector2i, reach: int) -> Array:
	var cells = []
	for i in range(-reach, reach + 1):
		cells.append(Vector2i(origin.x + i, origin.y))
		if i != 0:
			cells.append(Vector2i(origin.x, origin.y + i))
	return cells

func _rect(origin: Vector2i, half: int) -> Array:
	var cells = []
	for dy in range(-half, half + 1):
		for dx in range(-half, half + 1):
			cells.append(origin + Vector2i(dx, dy))
	return cells

func _pierce(origin: Vector2i) -> Array:
	var cells = []
	for x in range(BossGrid.PLACEMENT_COLS):
		cells.append(Vector2i(x, origin.y))
	return cells

func _bounce(origin: Vector2i) -> Array:
	var cells = []
	var pos = origin
	var dir = Vector2i(1, 0)
	var bounces = 0
	while cells.size() < 20 and bounces < 4:
		if not cells.has(pos):
			cells.append(pos)
		var next = pos + dir
		if next.x < 0 or next.x >= BossGrid.PLACEMENT_COLS:
			dir.x = -dir.x
			bounces += 1
		elif next.y < 0 or next.y >= BossGrid.PLACEMENT_ROWS:
			dir.y = -dir.y
			bounces += 1
		else:
			pos = next
	return cells

# ---- 完整伤害结算 ----

func resolve_all(placed_bombs: Dictionary) -> int:
	if placed_bombs.is_empty():
		return 0

	# 步骤1: 连锁传播（BFS，最多3层）
	var chain_per_level = UpgradeManager.get_chain_bonus_per_level()
	var chain_bonus: Dictionary = {}  # Vector2i -> float 额外倍率
	var to_process = placed_bombs.keys().duplicate()
	var chained = {}
	for depth in range(3):
		var next_wave = []
		for bomb_pos in to_process:
			var blast = get_blast_cells(bomb_pos, placed_bombs[bomb_pos])
			for other_pos in placed_bombs.keys():
				if other_pos != bomb_pos and blast.has(other_pos) and other_pos not in chained:
					chain_bonus[other_pos] = chain_bonus.get(other_pos, 0.0) + chain_per_level
					chained[other_pos] = true
					next_wave.append(other_pos)
		to_process = next_wave
		if to_process.is_empty():
			break

	# 步骤2: 构建 hit_map
	var dmg_mult = UpgradeManager.get_combat_dmg_mult()
	var hit_map: Dictionary = {}
	var all_blast_cells: Array = []  # 所有爆炸范围格子（去重）
	for bomb_pos in placed_bombs:
		var bomb_type = placed_bombs[bomb_pos]
		var base_dmg = float(BombRegistry.calculate_damage(bomb_type)) * dmg_mult
		var chain_mult = 1.0 + chain_bonus.get(bomb_pos, 0.0)
		var blast = get_blast_cells(bomb_pos, bomb_type)
		for cell in blast:
			if cell not in all_blast_cells:
				all_blast_cells.append(cell)
			if BossGrid.is_boss_tile(cell):
				if cell not in hit_map:
					hit_map[cell] = []
				hit_map[cell].append(base_dmg * chain_mult)

	# 步骤3: 交叉加成（多炸弹命中同一格，每额外一颗+50%）
	for cell in hit_map:
		var hits: Array = hit_map[cell]
		if hits.size() > 1:
			var bonus_mult = 1.0 + (hits.size() - 1) * 0.5
			for i in range(hits.size()):
				hits[i] *= bonus_mult

	# 步骤4: 逐格写入伤害（类型修正在 BossGrid 内部处理）
	var total_damage = 0
	for cell in hit_map:
		var sum = 0.0
		for v in hit_map[cell]:
			sum += v
		var final_dmg = int(sum)
		total_damage += final_dmg
		BossGrid.apply_damage_to_tile(cell, final_dmg)

	# 步骤5: 同步总HP + 检查升级阈值
	GameManager.sync_boss_hp()

	# 爆炸视觉信号（供 PlacementView 播放动画）
	explosion_visual.emit(placed_bombs.keys(), all_blast_cells)

	await get_tree().create_timer(0.6).timeout
	return total_damage
