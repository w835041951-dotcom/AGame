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

signal boss_moved(new_origin: Vector2i)
signal tiles_refreshed
signal tile_destroyed(local_pos: Vector2i, part: BodyPart)
signal core_destroyed

func setup():
	boss_attack_multiplier = 1.0
	var floor_n = GameManager.floor_number
	move_interval = LevelData.get_boss_move_interval(floor_n)

	# 从 LevelData 读取动态棋盘大小
	placement_cols = LevelData.get_placement_cols(floor_n)
	placement_rows = LevelData.get_placement_rows(floor_n)

	# 获取 Boss 形状
	var shape = LevelData.get_boss_shape(floor_n)
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

	# 随机分配关键部位
	var positions = tiles.keys().duplicate()
	positions.shuffle()
	tiles[positions[0]]["part"] = BodyPart.HEAD
	tiles[positions[1]]["part"] = BodyPart.LEG
	tiles[positions[2]]["part"] = BodyPart.CORE

	tiles_refreshed.emit()

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

	match tile["type"]:
		TileType.ABSORB:
			# 吸收格：回血3点，但仍受25%伤害
			GameManager.boss_hp = min(GameManager.boss_hp + 3, GameManager.boss_max_hp)
			amount = int(amount * 0.25)
		TileType.ARMOR:
			amount = int(amount * 0.5)
		TileType.WEAK:
			amount = int(amount * 2.0)

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

func move_left():
	# Boss每回合向左移动一格；到左边界后停住并每回合持续扣血
	if boss_origin.x > 0:
		boss_origin.x -= 1
	else:
		var atk = _choose_attack()
		boss_attacked.emit(atk)
	boss_moved.emit(boss_origin)

func random_move():
	# 高层有概率触发特殊移动
	var floor_n = GameManager.floor_number
	var charge_chance = min(0.05 * floor_n, 0.35)  # 每层+5%，最高35%
	if boss_origin.x > 1 and randf() < charge_chance:
		# 突进：移动2格
		boss_origin.x -= 2
		boss_moved.emit(boss_origin)
		# 突进后如果到了边界就立即攻击
		if boss_origin.x <= 0:
			boss_origin.x = 0
			boss_attacked.emit(AttackType.CHARGE)
	else:
		move_left()

func _choose_attack() -> AttackType:
	var floor_n = GameManager.floor_number
	# 高层Boss有更强攻击模式
	var roll = randf()
	if floor_n >= 5 and roll < 0.25:
		return AttackType.WIDE_SWIPE   # 横扫：对玩家造成AOE伤害
	elif floor_n >= 3 and roll < 0.45:
		return AttackType.SLAM         # 重击：造成双倍伤害
	elif floor_n >= 2 and roll < 0.60:
		return AttackType.CHARGE       # 突进：造成1.5x伤害
	return AttackType.NORMAL

func _random_type() -> TileType:
	var weights = LevelData.get_tile_weights(GameManager.floor_number)
	var roll = randf()
	var acc = 0.0
	acc += weights.get("WEAK", 0.15)
	if roll < acc: return TileType.WEAK
	acc += weights.get("ARMOR", 0.15)
	if roll < acc: return TileType.ARMOR
	acc += weights.get("ABSORB", 0.10)
	if roll < acc: return TileType.ABSORB
	return TileType.NORMAL

func _max_hp_for_type(type: TileType) -> int:
	match type:
		TileType.WEAK:   return 5
		TileType.ARMOR:  return 15
		TileType.ABSORB: return 8
		_:               return 10
