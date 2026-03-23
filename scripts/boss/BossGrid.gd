## Boss 区域数据管理 - AutoLoad
## 支持动态棋盘大小和不规则Boss形状

extends Node

enum TileType { NORMAL, WEAK, ARMOR, ABSORB }
enum BodyPart { NONE, HEAD, LEG, CORE }

# 当前层动态尺寸（每层 setup() 时从 LevelData 读取）
var placement_cols: int = 10
var placement_rows: int = 6

# boss_origin: Boss左上角在放置区的世界坐标
var boss_origin: Vector2i = Vector2i(6, 1)

# tiles: Vector2i(局部坐标) -> {type, part, hp, max_hp, alive}
var tiles: Dictionary = {}

var boss_attack_multiplier: float = 1.0
var move_interval: float = 60.0

# Boss形状的包围盒（用于计算初始位置和移动边界）
var boss_width: int = 4
var boss_height: int = 3

# PNG 贴图的格子维度（用于 atlas 纹理裁切，与形状无关）
var atlas_cols: int = 5
var atlas_rows: int = 4

signal boss_moved(new_origin: Vector2i)
signal tiles_refreshed
signal tile_destroyed(local_pos: Vector2i, part: BodyPart)
signal core_destroyed
signal phase_changed(new_phase: int)
signal field_changed

var current_phase: int = 1
var _turn_count: int = 0
var shielded_cells: Array = []  # Array[Vector2i]
var polluted_cells: Array = []  # Array[Vector2i]
var blocked_ttl: Dictionary = {}  # Vector2i -> remaining turns

func setup():
	boss_attack_multiplier = 1.0
	current_phase = 1
	_turn_count = 0
	shielded_cells.clear()
	polluted_cells.clear()
	blocked_ttl.clear()
	var floor_n = GameManager.floor_number
	move_interval = LevelData.get_boss_move_interval(floor_n)

	# 从 LevelData 读取动态棋盘大小
	placement_cols = LevelData.get_placement_cols(floor_n)
	placement_rows = LevelData.get_placement_rows(floor_n)

	# 获取 Boss 形状和 PNG 格子维度
	var shape = LevelData.get_boss_shape(floor_n)
	var grid_sz = LevelData.get_boss_grid_size(floor_n)
	atlas_cols = grid_sz.x
	atlas_rows = grid_sz.y
	_calc_boss_bounds(shape)

	# Boss 初始位置：靠右，垂直居中
	boss_origin = Vector2i(placement_cols - boss_width, max(0, (placement_rows - boss_height) / 2))
	tiles.clear()

	var hp_mult = LevelData.get_hp_multiplier(floor_n)

	# 按形状生成格子
	for pos in shape:
		var type = _random_type()
		var base_hp = _max_hp_for_type(type)
		var scaled_hp = int(base_hp * hp_mult)
		tiles[pos] = {
			"type": type,
			"part": BodyPart.NONE,
			"hp": scaled_hp,
			"max_hp": scaled_hp,
			"alive": true
		}

	# 随机分配关键部位（至少需要3个格子）
	var positions = tiles.keys().duplicate()
	positions.shuffle()
	if positions.size() >= 1: tiles[positions[0]]["part"] = BodyPart.HEAD
	if positions.size() >= 2: tiles[positions[1]]["part"] = BodyPart.LEG
	if positions.size() >= 3: tiles[positions[2]]["part"] = BodyPart.CORE

	tiles_refreshed.emit()
	phase_changed.emit(current_phase)
	field_changed.emit()

func update_phase_by_hp(cur_hp: int, max_hp: int):
	if max_hp <= 0:
		return
	var ratio = float(cur_hp) / max_hp
	var next_phase = 1
	if ratio <= 0.35:
		next_phase = 3
	elif ratio <= 0.70:
		next_phase = 2
	if next_phase != current_phase:
		current_phase = next_phase
		phase_changed.emit(current_phase)

func on_new_turn():
	_turn_count += 1
	update_phase_by_hp(GameManager.boss_hp, max(GameManager.boss_max_hp, 1))
	_decay_blocks()
	_generate_field_mechanics()

func _decay_blocks():
	for pos in blocked_ttl.keys():
		blocked_ttl[pos] -= 1
		if blocked_ttl[pos] <= 0:
			blocked_ttl.erase(pos)

func _generate_field_mechanics():
	shielded_cells.clear()
	polluted_cells.clear()

	if current_phase >= 2:
		# 随机护盾格（优先Boss存活格）
		var alive_world: Array = []
		for local_pos in tiles:
			if tiles[local_pos]["alive"]:
				alive_world.append(local_to_world(local_pos))
		alive_world.shuffle()
		var shield_extra = 1 if GameManager.challenge_modifier == "护盾风暴：Boss护盾格+1" else 0
		var shield_n = min(1 + current_phase - 1 + shield_extra, alive_world.size())
		for i in range(shield_n):
			shielded_cells.append(alive_world[i])

		# 随机封锁格（不能布弹）
		var candidates: Array = []
		for y in range(placement_rows):
			for x in range(placement_cols):
				var w = Vector2i(x, y)
				if is_boss_tile(w):
					continue
				if MinionGrid.is_minion_tile(w):
					continue
				candidates.append(w)
		candidates.shuffle()
		var block_n = min(1 + (1 if current_phase >= 3 else 0), candidates.size())
		for i in range(block_n):
			blocked_ttl[candidates[i]] = max(blocked_ttl.get(candidates[i], 0), 1)

	if current_phase >= 3:
		# 污染地块：伤害衰减
		var pollute_n = min(3, placement_cols * placement_rows)
		for i in range(pollute_n):
			polluted_cells.append(Vector2i(randi_range(0, placement_cols - 1), randi_range(0, placement_rows - 1)))

	# 召唤机制
	if current_phase >= 2 and randf() < (0.16 if current_phase == 2 else 0.28):
		MinionGrid.spawn_random_minion(1 if current_phase == 2 else 2)

	field_changed.emit()

func is_blocked_cell(world_pos: Vector2i) -> bool:
	return blocked_ttl.get(world_pos, 0) > 0

func is_polluted_cell(world_pos: Vector2i) -> bool:
	return world_pos in polluted_cells

func is_shielded_cell(world_pos: Vector2i) -> bool:
	return world_pos in shielded_cells

func add_temporary_blocks(center: Vector2i, radius: int = 1):
	for dy in range(-radius, radius + 1):
		for dx in range(-radius, radius + 1):
			var p = center + Vector2i(dx, dy)
			if p.x < 0 or p.x >= placement_cols or p.y < 0 or p.y >= placement_rows:
				continue
			if is_boss_tile(p) or MinionGrid.is_minion_tile(p):
				continue
			blocked_ttl[p] = max(blocked_ttl.get(p, 0), 1)
	field_changed.emit()

func _calc_boss_bounds(shape: Array):
	var max_x = 0
	var max_y = 0
	for pos in shape:
		if pos.x > max_x: max_x = pos.x
		if pos.y > max_y: max_y = pos.y
	boss_width = max_x + 1
	boss_height = max_y + 1

func refresh_weak_tiles():
	# 每回合重新随机 2~3 个存活格为 WEAK
	var alive_positions = []
	for pos in tiles:
		if tiles[pos]["alive"]:
			alive_positions.append(pos)
	alive_positions.shuffle()
	var count = min(randi_range(2, 3), alive_positions.size())
	for i in range(count):
		var pos = alive_positions[i]
		if tiles[pos]["type"] != TileType.ARMOR:  # 护甲格不变弱点
			tiles[pos]["type"] = TileType.WEAK
			tiles[pos]["max_hp"] = 5
			tiles[pos]["hp"] = min(tiles[pos]["hp"], 5)
	tiles_refreshed.emit()

func get_total_hp() -> int:
	var total = 0
	for tile in tiles.values():
		if tile["alive"]:
			total += tile["hp"]
	return total

func get_total_max_hp() -> int:
	var total = 0
	for tile in tiles.values():
		total += tile["max_hp"]
	return total

func alive_ratio() -> float:
	if tiles.is_empty():
		return 0.0
	var alive_count = 0
	for t in tiles.values():
		if t["alive"]:
			alive_count += 1
	return float(alive_count) / tiles.size()

func is_boss_tile(world_pos: Vector2i) -> bool:
	var local = world_to_local(world_pos)
	return local in tiles and tiles[local]["alive"]

func get_tile(world_pos: Vector2i) -> Dictionary:
	var local = world_to_local(world_pos)
	return tiles.get(local, {})

func world_to_local(world_pos: Vector2i) -> Vector2i:
	return world_pos - boss_origin

func local_to_world(local_pos: Vector2i) -> Vector2i:
	return local_pos + boss_origin

func apply_damage_to_tile(world_pos: Vector2i, amount: int):
	var local = world_to_local(world_pos)
	if local not in tiles:
		return
	var tile = tiles[local]
	if not tile["alive"]:
		return

	# 暂时禁用类型伤害修正，所有格子受伤一致
	# --- 保留原逻辑 ---
	#match tile["type"]:
	#	TileType.ABSORB:
	#		GameManager.boss_hp = min(GameManager.boss_hp + 3, GameManager.boss_max_hp)
	#		amount = int(amount * 0.25)
	#	TileType.ARMOR:
	#		amount = int(amount * 0.5)
	#	TileType.WEAK:
	#		amount = int(amount * 2.0)

	tile["hp"] = max(0, tile["hp"] - amount)
	if tile["hp"] <= 0:
		tile["alive"] = false
		_on_tile_destroyed(local, tile)

func _on_tile_destroyed(local_pos: Vector2i, tile: Dictionary):
	tile_destroyed.emit(local_pos, tile["part"])
	match tile["part"]:
		BodyPart.HEAD:
			boss_attack_multiplier *= 0.5
		BodyPart.LEG:
			move_interval = 120.0
		BodyPart.CORE:
			core_destroyed.emit()

enum AttackType { NORMAL, CHARGE, SLAM, WIDE_SWIPE }

signal boss_attacked(attack_type: AttackType)  # Boss走出左边界，攻击玩家

func has_alive_at_left_edge() -> bool:
	for pos in tiles:
		if tiles[pos]["alive"] and pos.x + boss_origin.x <= 0:
			return true
	return false

func move_left():
	# 存活格子已经在左边界→停止移动，直接攻击
	if has_alive_at_left_edge():
		var atk = _choose_attack()
		boss_attacked.emit(atk)
		return
	boss_origin.x -= 1
	if has_alive_at_left_edge():
		var atk = _choose_attack()
		boss_attacked.emit(atk)
	boss_moved.emit(boss_origin)

func random_move():
	# 存活格子已在左边界→停止移动，直接攻击
	if has_alive_at_left_edge():
		var atk = _choose_attack()
		boss_attacked.emit(atk)
		return

	# P3 狂暴：有概率额外前压1格
	if current_phase >= 3 and boss_origin.x > 0 and randf() < 0.35:
		boss_origin.x -= 1
		boss_moved.emit(boss_origin)
		if has_alive_at_left_edge():
			boss_attacked.emit(AttackType.SLAM)
			return

	# 高层有概率触发特殊移动
	var floor_n = GameManager.floor_number
	var level_idx = LevelData.get_level(floor_n)["id"]
	var charge_chance = min(0.02 * level_idx, 0.35)  # 每关+2%，最高35%
	if boss_origin.x > 1 and randf() < charge_chance:
		# 突进：移动2格
		boss_origin.x -= 2
		boss_moved.emit(boss_origin)
		# 突进后如果存活格子碰到左边界就攻击
		if has_alive_at_left_edge():
			boss_attacked.emit(AttackType.CHARGE)
	else:
		move_left()

func _choose_attack() -> AttackType:
	var floor_n = GameManager.floor_number
	var level_idx = LevelData.get_level(floor_n)["id"]  # 1-20 within cycle
	# 高层Boss有更强攻击模式
	var roll = randf()
	if level_idx >= 15 and roll < 0.25:
		return AttackType.WIDE_SWIPE   # 横扫：对玩家造成AOE伤害
	elif level_idx >= 8 and roll < 0.45:
		return AttackType.SLAM         # 重击：造成双倍伤害
	elif level_idx >= 4 and roll < 0.60:
		return AttackType.CHARGE       # 突进：造成1.5x伤害
	return AttackType.NORMAL

func _random_type() -> TileType:
	# 暂时禁用类型差异，所有格子统一为NORMAL
	return TileType.NORMAL
	# --- 保留原逻辑 ---
	#var weights = LevelData.get_tile_weights(GameManager.floor_number)
	#var roll = randf()
	#var acc = 0.0
	#acc += weights.get("WEAK", 0.15)
	#if roll < acc: return TileType.WEAK
	#acc += weights.get("ARMOR", 0.15)
	#if roll < acc: return TileType.ARMOR
	#acc += weights.get("ABSORB", 0.10)
	#if roll < acc: return TileType.ABSORB
	#return TileType.NORMAL

func _max_hp_for_type(_type: TileType) -> int:
	# 暂时统一血量
	return 10
	# --- 保留原逻辑 ---
	#match type:
	#	TileType.WEAK:   return 5
	#	TileType.ARMOR:  return 15
	#	TileType.ABSORB: return 8
	#	_:               return 10
