## 爆炸范围计算 + 伤害结算 - AutoLoad

extends Node

signal explosion_visual(bomb_positions: Array, blast_cells: Array)
signal damage_numbers(cell_damages: Dictionary)  # Vector2i(world) -> int 总伤害
signal chain_triggered(chained_positions: Array)  # 被连锁引爆的炸弹位置
signal critical_hit(cell: Vector2i, damage: int)  # 暴击通知

# ---- 爆炸范围计算 ----

func get_blast_cells(origin: Vector2i, bomb_type: String) -> Array:
	var lvl = BombRegistry.get_bomb_level(bomb_type)
	match bomb_type:
		"pierce_h": return _line_h(origin, 1 + lvl)
		"pierce_v": return _line_v(origin, 1 + lvl)
		"cross": return _cross(origin, 1 + lvl)
		"fan": return _fan(origin, 1 + lvl)
		"x_shot": return _x_diag(origin, 1 + lvl)
		"second_blast": return _cross(origin, 1 + lvl)
		"freeze_bomb": return _cross(origin, 1 + lvl)
		"magnetic": return _cross(origin, 1)
		"bounce": return _bounce(origin, lvl)
		"scatter": return _scatter(origin, 1 + lvl)
		"blackhole": return _cross(origin, 1 + lvl)
		"ultimate": return _ultimate(origin, 4 + lvl)
		_: return _cross(origin, 1 + lvl)

func _cross(origin: Vector2i, reach: int) -> Array:
	var cells = []
	for i in range(-reach, reach + 1):
		cells.append(Vector2i(origin.x + i, origin.y))
		if i != 0:
			cells.append(Vector2i(origin.x, origin.y + i))
	return cells

func _line_h(origin: Vector2i, reach: int) -> Array:
	var cells = []
	for i in range(-reach, reach + 1):
		cells.append(Vector2i(origin.x + i, origin.y))
	return cells

func _line_v(origin: Vector2i, reach: int) -> Array:
	var cells = []
	for i in range(-reach, reach + 1):
		cells.append(Vector2i(origin.x, origin.y + i))
	return cells

func _fan(origin: Vector2i, reach: int) -> Array:
	var cells = [origin]
	var dir = 1
	if origin.x > BossGrid.boss_origin.x:
		dir = -1
	for i in range(1, reach + 1):
		cells.append(origin + Vector2i(dir * i, 0))
		cells.append(origin + Vector2i(dir * i, 1))
		cells.append(origin + Vector2i(dir * i, -1))
	return cells

func _x_diag(origin: Vector2i, reach: int) -> Array:
	var cells = [origin]
	for i in range(1, reach + 1):
		cells.append(origin + Vector2i(i, i))
		cells.append(origin + Vector2i(i, -i))
		cells.append(origin + Vector2i(-i, i))
		cells.append(origin + Vector2i(-i, -i))
	return cells

func _bounce(origin: Vector2i, lvl: int = 1) -> Array:
	var cells = []
	var pos = origin
	var dir = Vector2i(1, 0)
	var bounces = 0
	var max_bounces = 1 + lvl
	var max_cells = 8 + 4 * lvl
	while cells.size() < max_cells and bounces < max_bounces:
		if not cells.has(pos):
			cells.append(pos)
		var next = pos + dir
		if next.x < 0 or next.x >= BossGrid.placement_cols:
			dir.x = -dir.x
			bounces += 1
		elif next.y < 0 or next.y >= BossGrid.placement_rows:
			dir.y = -dir.y
			bounces += 1
		else:
			pos = next
	return cells

func _scatter(origin: Vector2i, reach: int) -> Array:
	var cells = [origin]
	for i in range(1, reach + 1):
		cells.append(origin + Vector2i(i, 0))
		cells.append(origin + Vector2i(-i, 0))
		cells.append(origin + Vector2i(0, i))
		cells.append(origin + Vector2i(0, -i))
		cells.append(origin + Vector2i(i, i))
		cells.append(origin + Vector2i(-i, -i))
		cells.append(origin + Vector2i(i, -i))
		cells.append(origin + Vector2i(-i, i))
	return cells

func _ultimate(origin: Vector2i, reach: int) -> Array:
	var cells = _cross(origin, reach)
	for i in range(1, reach + 1):
		cells.append(origin + Vector2i(i, i))
		cells.append(origin + Vector2i(-i, -i))
		cells.append(origin + Vector2i(i, -i))
		cells.append(origin + Vector2i(-i, i))
	return cells

func _blackhole_area(origin: Vector2i, radius: int) -> Array:
	var cells = []
	for dy in range(-radius, radius + 1):
		for dx in range(-radius, radius + 1):
			cells.append(origin + Vector2i(dx, dy))
	return cells

func _apply_magnetic_shift(bombs: Dictionary) -> Dictionary:
	var shifted = bombs.duplicate(true)
	var magnets: Array = []
	for p in shifted.keys():
		if shifted[p] == "magnetic":
			magnets.append(p)
	if magnets.is_empty():
		return shifted

	for m in magnets:
		for p in shifted.keys().duplicate():
			if p == m:
				continue
			if shifted[p] == "magnetic":
				continue
			if abs(p.x - m.x) > 1 or abs(p.y - m.y) > 1:
				continue
			var dir = Vector2i(sign(m.x - p.x), sign(m.y - p.y))
			var np = p + dir
			if np == m:
				continue
			if np.x < 0 or np.x >= BossGrid.placement_cols or np.y < 0 or np.y >= BossGrid.placement_rows:
				continue
			if shifted.has(np):
				continue
			if BossGrid.is_boss_tile(np) or BossGrid.is_blocked_cell(np):
				continue
			var t = shifted[p]
			shifted.erase(p)
			shifted[np] = t
	return shifted

# ---- 完整伤害结算 ----

func resolve_all(placed_bombs: Dictionary) -> int:
	if placed_bombs.is_empty():
		return 0

	var active_bombs = _apply_magnetic_shift(placed_bombs)

	# 步骤1: 连锁传播（BFS，最多3层）
	var chain_per_level = UpgradeManager.get_chain_bonus_per_level()
	if GameManager.challenge_modifier == "连锁强化：连锁加成+20%，点击-1":
		chain_per_level += 0.2
	var chain_bonus: Dictionary = {}  # Vector2i -> float 额外倍率
	var to_process = active_bombs.keys().duplicate()
	var chained = {}
	for _depth in range(3):
		var next_wave = []
		for bomb_pos in to_process:
			var blast = get_blast_cells(bomb_pos, active_bombs[bomb_pos])
			for other_pos in active_bombs.keys():
				if other_pos != bomb_pos and blast.has(other_pos) and other_pos not in chained:
					chain_bonus[other_pos] = chain_bonus.get(other_pos, 0.0) + chain_per_level
					chained[other_pos] = true
					next_wave.append(other_pos)
		to_process = next_wave
		if to_process.is_empty():
			break

	if not chained.is_empty():
		chain_triggered.emit(chained.keys())

	var chain_count = chained.size()
	if chain_count > GameManager.stat_max_chain:
		GameManager.stat_max_chain = chain_count
	GameManager.stat_bombs_used += active_bombs.size()

	# 步骤2: 构建 hit_map
	var dmg_mult = UpgradeManager.get_combat_dmg_mult()
	var hit_map: Dictionary = {}  # cell -> [{dmg,type}]
	var all_blast_cells: Array = []
	var freeze_hit: bool = false
	var second_wave_bombs: Array = []
	var delayed_bombs: Array = []

	for bomb_pos in active_bombs:
		var bomb_type = active_bombs[bomb_pos]
		var base_dmg = float(BombRegistry.calculate_damage(bomb_type)) * dmg_mult
		if BossGrid.is_polluted_cell(bomb_pos):
			base_dmg *= 0.78
		if bomb_type == "ultimate":
			base_dmg *= 1.2
		if BombRegistry.has_affix(bomb_type, "ignite"):
			base_dmg *= 1.2

		if BombRegistry.has_affix(bomb_type, "link"):
			for ap in active_bombs.keys():
				if ap == bomb_pos:
					continue
				if abs(ap.x - bomb_pos.x) <= 1 and abs(ap.y - bomb_pos.y) <= 1:
					if BombRegistry.get_bomb_class(active_bombs[ap]) == BombRegistry.get_bomb_class(bomb_type):
						base_dmg *= 2.0
						break

		if BombRegistry.has_affix(bomb_type, "delay"):
			delayed_bombs.append(bomb_pos)
			base_dmg *= 0.8
		if GameManager.challenge_modifier == "冷却回路：过载效果伤害+20%" and BombRegistry.has_affix(bomb_type, "overload"):
			base_dmg *= 1.2

		var chain_mult = 1.0 + min(chain_bonus.get(bomb_pos, 0.0), 1.5)
		var blast = get_blast_cells(bomb_pos, bomb_type)
		for cell in blast:
			if cell not in all_blast_cells:
				all_blast_cells.append(cell)
			if BossGrid.is_boss_tile(cell):
				if cell not in hit_map:
					hit_map[cell] = []
				hit_map[cell].append({"dmg": base_dmg * chain_mult, "type": bomb_type})
				if bomb_type == "freeze_bomb":
					freeze_hit = true

		if bomb_type == "second_blast":
			second_wave_bombs.append(bomb_pos)

		if bomb_type == "blackhole":
			for pull_cell in _blackhole_area(bomb_pos, 2):
				if pull_cell not in all_blast_cells:
					all_blast_cells.append(pull_cell)
				if BossGrid.is_boss_tile(pull_cell):
					if pull_cell not in hit_map:
						hit_map[pull_cell] = []
					hit_map[pull_cell].append({"dmg": base_dmg * 0.5, "type": bomb_type})

	# 步骤3: 交叉加成（多炸弹命中同一格）
	for cell in hit_map:
		var hits: Array = hit_map[cell]
		if hits.size() > 1:
			var bonus_mult = 1.0 + (hits.size() - 1) * 0.3
			for h in hits:
				h["dmg"] *= bonus_mult

	# 步骤3.5: 小怪伤害
	var minion_damages: Dictionary = {}
	for cell in all_blast_cells:
		if MinionGrid.is_minion_tile(cell):
			var total_hit = 0.0
			for bomb_pos in active_bombs:
				var blast = get_blast_cells(bomb_pos, active_bombs[bomb_pos])
				if cell in blast:
					total_hit += float(BombRegistry.calculate_damage(active_bombs[bomb_pos])) * dmg_mult
			var minion_dmg = int(total_hit)
			if minion_dmg > 0:
				minion_damages[cell] = minion_dmg
				MinionGrid.apply_damage(cell, minion_dmg)

	# 步骤4: 写入Boss伤害
	var total_damage = 0
	var cell_damages: Dictionary = {}
	var crit_chance = 0.06 + min(active_bombs.size() * 0.03, 0.12)
	for cell in hit_map:
		var final_sum = 0.0
		for h in hit_map[cell]:
			var dmg = float(h["dmg"])
			var t = String(h["type"])
			var pierce = BombRegistry.is_piercing_type(t) or BombRegistry.has_affix(t, "pierce")
			if BossGrid.is_shielded_cell(cell) and not pierce:
				dmg *= 0.65
			final_sum += dmg
		var final_dmg = int(final_sum)
		if randf() < crit_chance:
			final_dmg = int(final_dmg * 1.5)
			critical_hit.emit(cell, final_dmg)
		total_damage += final_dmg
		cell_damages[cell] = final_dmg
		BossGrid.apply_damage_to_tile(cell, final_dmg)

	for cell in minion_damages:
		if not cell_damages.has(cell):
			cell_damages[cell] = minion_damages[cell]

	# 冻结效果
	if freeze_hit:
		UpgradeManager.active_combat["freeze_boss"] = true

	# 同步HP
	GameManager.sync_boss_hp()

	explosion_visual.emit(active_bombs.keys(), all_blast_cells)
	damage_numbers.emit(cell_damages)
	await get_tree().create_timer(0.6).timeout

	# 二次弹效果：仅二次弹执行额外波次，并封锁地块
	if not second_wave_bombs.is_empty():
		var second_local: Dictionary = {}
		for pos in second_wave_bombs:
			second_local[pos] = "second_blast"
		total_damage += await _second_wave(second_local, 0.55)
		for pos in second_wave_bombs:
			BossGrid.add_temporary_blocks(pos, 1)

	# 延时词条：追加延后结算
	if not delayed_bombs.is_empty():
		var delayed_local: Dictionary = {}
		for pos in delayed_bombs:
			delayed_local[pos] = active_bombs[pos]
		total_damage += await _second_wave(delayed_local, 0.50)

	# 升级二次引爆
	if UpgradeManager.is_double_detonate():
		UpgradeManager.consume_double_detonate()
		total_damage += await _second_wave(active_bombs, 0.55)

	# 过载词条：使用后进入冷却
	for p in active_bombs:
		var t = active_bombs[p]
		if BombRegistry.has_affix(t, "overload"):
			GameManager.apply_bomb_cooldown(t, 1)

	# 过载挑战：让最高伤害炸弹进入额外冷却
	if GameManager.challenge_modifier == "冷却回路：过载效果伤害+20%":
		var top_type = ""
		var top_dmg = -1
		for p in active_bombs:
			var t = active_bombs[p]
			var d = BombRegistry.calculate_damage(t)
			if d > top_dmg:
				top_dmg = d
				top_type = t
		if top_type != "":
			GameManager.apply_bomb_cooldown(top_type, 1)

	GameManager.stat_total_damage += total_damage
	return total_damage

func _second_wave(bombs: Dictionary, ratio: float) -> int:
	if bombs.is_empty():
		return 0
	var dmg_mult = UpgradeManager.get_combat_dmg_mult()
	var hit_map2: Dictionary = {}
	var blast_cells2: Array = []
	for bomb_pos in bombs:
		var bomb_type = bombs[bomb_pos]
		var base_dmg = float(BombRegistry.calculate_damage(bomb_type)) * dmg_mult * ratio
		var blast = get_blast_cells(bomb_pos, bomb_type)
		for cell in blast:
			if cell not in blast_cells2:
				blast_cells2.append(cell)
			if BossGrid.is_boss_tile(cell):
				if cell not in hit_map2:
					hit_map2[cell] = 0.0
				hit_map2[cell] += base_dmg
	explosion_visual.emit(bombs.keys(), blast_cells2)
	var total2 = 0
	for cell in hit_map2:
		var fd = int(hit_map2[cell])
		total2 += fd
		BossGrid.apply_damage_to_tile(cell, fd)
	GameManager.sync_boss_hp()
	await get_tree().create_timer(0.45).timeout
	return total2
