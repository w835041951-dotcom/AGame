## 小怪系统 - AutoLoad
## 某些关卡中，先清小怪，再让Boss入场
## 小怪占据放置区左侧格子，死亡后掉落炸弹

extends Node

signal minions_refreshed
signal minion_defeated(world_pos: Vector2i, drop_type: String)
signal all_minions_cleared  # 全部小怪消灭，Boss入场

# minion_tiles: Vector2i(world坐标) -> { hp, max_hp, alive, drop_type, label }
var minion_tiles: Dictionary = {}

var phase: int = 0  # 0 = 无小怪, 1 = 小怪阶段, 2 = Boss阶段
const PHASE_NONE = 0
const PHASE_MINIONS = 1
const PHASE_BOSS = 2

# 小怪预设类型
const MINION_TYPES = {
	"grunt":    { "hp": 8,  "drop": "pierce_h", "label": "史莱姆",  "color": Color(0.4, 0.9, 0.3) },
	"brute":    { "hp": 15, "drop": "cross",    "label": "骷髅兵",  "color": Color(0.85, 0.82, 0.70) },
	"shield":   { "hp": 20, "drop": "bounce",   "label": "盾卫",    "color": Color(0.55, 0.58, 0.62) },
	"volatile": { "hp": 6,  "drop": "scatter",  "label": "爆炸蜘蛛","color": Color(0.95, 0.45, 0.15) },
	"reflect":  { "hp": 12, "drop": "pierce_v", "label": "镜魔",    "color": Color(0.6, 0.3, 0.95) },
	"healer":   { "hp": 10, "drop": "cross",    "label": "祭司",    "color": Color(0.3, 0.95, 0.7) },
}

func setup():
	minion_tiles.clear()
	phase = PHASE_NONE

	var floor_n = GameManager.floor_number
	var level = LevelData.get_level(floor_n)
	if level.is_empty() or not level.has("minions"):
		phase = PHASE_BOSS  # 无小怪，直接Boss阶段
		return

	var minion_list: Array = level["minions"]
	if minion_list.is_empty():
		phase = PHASE_BOSS
		return

	# 按配置生成小怪格子
	for entry in minion_list:
		var world_pos = Vector2i(entry["x"], entry["y"])
		var mtype = entry.get("type", "grunt")
		var def = MINION_TYPES.get(mtype, MINION_TYPES["grunt"])
		var hp_mult = LevelData.get_hp_multiplier(floor_n)
		var hp = max(1, int(def["hp"] * hp_mult))
		minion_tiles[world_pos] = {
			"hp": hp,
			"max_hp": hp,
			"alive": true,
			"drop_type": def["drop"],
			"label": def["label"],
			"color": def["color"],
			"mtype": mtype,
		}

	phase = PHASE_MINIONS
	minions_refreshed.emit()

func is_minion_tile(world_pos: Vector2i) -> bool:
	return minion_tiles.has(world_pos) and minion_tiles[world_pos]["alive"]

func get_tile(world_pos: Vector2i) -> Dictionary:
	return minion_tiles.get(world_pos, {})

# 对某世界坐标的小怪施加伤害，返回实际造成的伤害
func apply_damage(world_pos: Vector2i, amount: int) -> int:
	if not minion_tiles.has(world_pos):
		return 0
	var tile = minion_tiles[world_pos]
	if not tile["alive"]:
		return 0
	# 镜魔：反射30%伤害给玩家
	if tile["mtype"] == "reflect":
		var reflected = max(1, int(amount * 0.3))
		GameManager.take_damage(reflected)
	var actual = min(amount, tile["hp"])
	tile["hp"] -= actual
	if tile["hp"] <= 0:
		tile["alive"] = false
		# 祭司：死亡时回复Boss 5% HP
		if tile["mtype"] == "healer":
			var heal_amt = max(1, int(GameManager.boss_max_hp * 0.05))
			GameManager.boss_hp = min(GameManager.boss_hp + heal_amt, GameManager.boss_max_hp)
		var drop = tile["drop_type"]
		minion_defeated.emit(world_pos, drop)
		_check_all_cleared()
	return actual

func _check_all_cleared():
	for pos in minion_tiles:
		if minion_tiles[pos]["alive"]:
			return
	# 全部清除
	phase = PHASE_BOSS
	all_minions_cleared.emit()

func alive_count() -> int:
	var n = 0
	for pos in minion_tiles:
		if minion_tiles[pos]["alive"]:
			n += 1
	return n

func has_minions() -> bool:
	return phase == PHASE_MINIONS and alive_count() > 0

func spawn_random_minion(count: int = 1):
	var spawn_candidates: Array = []
	for y in range(BossGrid.placement_rows):
		for x in range(max(1, int(BossGrid.placement_cols * 0.35))):
			var p = Vector2i(x, y)
			if minion_tiles.has(p) and minion_tiles[p]["alive"]:
				continue
			if BossGrid.is_boss_tile(p):
				continue
			spawn_candidates.append(p)
	if spawn_candidates.is_empty():
		return

	phase = PHASE_MINIONS
	spawn_candidates.shuffle()
	for i in range(min(count, spawn_candidates.size())):
		var world_pos = spawn_candidates[i]
		var type_pool = ["grunt", "shield", "volatile"]
		if BossGrid.current_phase >= 2:
			type_pool.append("reflect")
		if BossGrid.current_phase >= 3:
			type_pool.append("healer")
		var mtype = type_pool[randi() % type_pool.size()]
		var def = MINION_TYPES.get(mtype, MINION_TYPES["grunt"])
		var hp_mult = LevelData.get_hp_multiplier(GameManager.floor_number)
		var hp = max(1, int(def["hp"] * hp_mult * 0.7))
		minion_tiles[world_pos] = {
			"hp": hp,
			"max_hp": hp,
			"alive": true,
			"drop_type": def["drop"],
			"label": def["label"],
			"color": def["color"],
			"mtype": mtype,
		}
	minions_refreshed.emit()
