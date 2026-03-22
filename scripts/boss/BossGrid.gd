## Boss 区域数据管理 - AutoLoad

extends Node

enum TileType { NORMAL, WEAK, ARMOR, ABSORB }
enum BodyPart { NONE, HEAD, LEG, CORE }

const PLACEMENT_COLS = 10
const PLACEMENT_ROWS = 6
const BOSS_COLS = 4
const BOSS_ROWS = 3

# boss_origin: Boss左上角在放置区的世界坐标
var boss_origin: Vector2i = Vector2i(PLACEMENT_COLS - BOSS_COLS, 1)

# tiles: Vector2i(局部坐标) -> {type, part, hp, max_hp, alive}
var tiles: Dictionary = {}

var boss_attack_multiplier: float = 1.0
var move_interval: float = 60.0

signal boss_moved(new_origin: Vector2i)
signal tiles_refreshed
signal tile_destroyed(local_pos: Vector2i, part: BodyPart)
signal core_destroyed  # 由 Main 监听，决定是否弹出临时升级

func setup():
	boss_attack_multiplier = 1.0
	var floor_n = GameManager.floor_number
	move_interval = LevelData.get_boss_move_interval(floor_n)
	boss_origin = Vector2i(PLACEMENT_COLS - BOSS_COLS, 1)
	tiles.clear()

	var hp_mult = LevelData.get_hp_multiplier(floor_n)

	# 初始化所有格子（根据关卡数据）
	for y in range(BOSS_ROWS):
		for x in range(BOSS_COLS):
			var pos = Vector2i(x, y)
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

	# 随机分配关键部位（各一个）
	var positions = tiles.keys().duplicate()
	positions.shuffle()
	tiles[positions[0]]["part"] = BodyPart.HEAD
	tiles[positions[1]]["part"] = BodyPart.LEG
	tiles[positions[2]]["part"] = BodyPart.CORE

	tiles_refreshed.emit()

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
			# 吸收格：回血，不受伤
			GameManager.boss_hp = min(GameManager.boss_hp + 5, GameManager.boss_max_hp)
			return
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

signal boss_attacked  # Boss走出左边界，攻击玩家

func move_left():
	# Boss每回合向左移动一格；到左边界后停住并每回合持续扣血
	if boss_origin.x > 0:
		boss_origin.x -= 1
	else:
		boss_attacked.emit()
	boss_moved.emit(boss_origin)

func random_move():
	move_left()

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
