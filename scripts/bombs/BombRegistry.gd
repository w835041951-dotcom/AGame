## 炸弹类型注册表 - 单例
## 管理所有炸弹效果

extends Node

## 炸弹类型定义
const BOMB_TYPES = {
	"pierce_h": {
		"name": "横穿透",
		"description": "横向光束穿透整行",
		"damage": 15,
		"class": "line",
		"rarity": "common",
		"delay_stage": 0,
		"tags": ["stable"],
		"color": Color.YELLOW,
	},
	"pierce_v": {
		"name": "竖穿透",
		"description": "纵向光束穿透整列",
		"damage": 15,
		"class": "line",
		"rarity": "common",
		"delay_stage": 0,
		"tags": ["stable"],
		"color": Color.GREEN_YELLOW,
	},
	"cross": {
		"name": "十字炮",
		"description": "横竖十字范围爆破",
		"damage": 12,
		"class": "zone",
		"rarity": "rare",
		"delay_stage": 0,
		"tags": ["control"],
		"color": Color.RED,
	},
	"fan": {
		"name": "扇形弹",
		"description": "朝Boss方向扇形喷发",
		"damage": 11,
		"class": "zone",
		"rarity": "rare",
		"delay_stage": 0,
		"tags": ["control"],
		"color": Color(1.0, 0.55, 0.2),
	},
	"x_shot": {
		"name": "X弹",
		"description": "对角线四方向射击",
		"damage": 12,
		"class": "zone",
		"rarity": "rare",
		"delay_stage": 0,
		"tags": ["control"],
		"color": Color.ORANGE,
	},
	"second_blast": {
		"name": "二次弹",
		"description": "主爆后追加二段爆炸，并短暂封锁地块",
		"damage": 10,
		"class": "chain",
		"rarity": "epic",
		"delay_stage": 1,
		"tags": ["double", "block"],
		"color": Color(0.95, 0.7, 0.15),
	},
	"freeze_bomb": {
		"name": "冰封弹",
		"description": "冻结Boss位移1回合，低伤害",
		"damage": 9,
		"class": "utility",
		"rarity": "epic",
		"delay_stage": 0,
		"tags": ["freeze"],
		"color": Color(0.55, 0.85, 1.0),
	},
	"magnetic": {
		"name": "磁暴弹",
		"description": "拉拢周围炸弹1格，重排阵型",
		"damage": 8,
		"class": "utility",
		"rarity": "epic",
		"delay_stage": 0,
		"tags": ["magnetic"],
		"color": Color(0.45, 0.95, 0.95),
	},
	"bounce": {
		"name": "反弹弹",
		"description": "弹道遇墙反弹继续",
		"damage": 9,
		"class": "utility",
		"rarity": "rare",
		"delay_stage": 0,
		"tags": ["trajectory"],
		"color": Color.CYAN,
	},
	"scatter": {
		"name": "散射弹",
		"description": "八方向同时发射",
		"damage": 7,
		"class": "utility",
		"rarity": "rare",
		"delay_stage": 0,
		"tags": ["trajectory"],
		"color": Color.MAGENTA
	},
	"blackhole": {
		"name": "黑洞弹",
		"description": "吸附范围内目标到中心后引爆",
		"damage": 17,
		"class": "rare",
		"rarity": "legendary",
		"delay_stage": 1,
		"tags": ["pull", "burst"],
		"color": Color(0.35, 0.2, 0.65),
	},
	"ultimate": {
		"name": "究极弹",
		"description": "局内唯一超大范围聚爆",
		"damage": 34,
		"class": "ultimate",
		"rarity": "mythic",
		"delay_stage": 0,
		"tags": ["unique", "burst"],
		"color": Color.MAGENTA,
	}
}

## 玩家当前解锁的炸弹类型（肉鸽升级后扩展）
var unlocked_types: Array = ["pierce_h", "pierce_v"]

## 炸弹等级（影响攻击范围）
var bomb_levels: Dictionary = {}  # type_id -> int, 默认1
var bonus_damage: int = 0  # 全局额外伤害加成
var bomb_affixes: Dictionary = {}  # type_id -> Array[String]

const AFFIX_POOL = ["ignite", "delay", "link", "pierce", "overload"]

func get_available_types() -> Array:
	return unlocked_types

func unlock_type(type_id: String):
	if type_id in BOMB_TYPES and not type_id in unlocked_types:
		unlocked_types.append(type_id)

func get_bomb_info(type_id: String) -> Dictionary:
	return BOMB_TYPES.get(type_id, {})

func is_ethereal(_type_id: String) -> bool:
	return false

func is_unique(type_id: String) -> bool:
	return get_bomb_info(type_id).get("class", "") == "ultimate"

func is_piercing_type(type_id: String) -> bool:
	return type_id in ["pierce_h", "pierce_v", "ultimate"]

func get_delay_stage(type_id: String) -> int:
	return get_bomb_info(type_id).get("delay_stage", 0)

func get_bomb_class(type_id: String) -> String:
	return get_bomb_info(type_id).get("class", "line")

func get_affixes(type_id: String) -> Array:
	return bomb_affixes.get(type_id, [])

func has_affix(type_id: String, affix_id: String) -> bool:
	return affix_id in get_affixes(type_id)

func add_random_affix(type_id: String):
	if not BOMB_TYPES.has(type_id):
		return
	var affixes = get_affixes(type_id).duplicate()
	var candidates: Array = []
	for a in AFFIX_POOL:
		if a not in affixes:
			candidates.append(a)
	if candidates.is_empty():
		return
	affixes.append(candidates[randi() % candidates.size()])
	bomb_affixes[type_id] = affixes

func reroll_random_affix(type_id: String):
	if not BOMB_TYPES.has(type_id):
		return
	var affixes = get_affixes(type_id).duplicate()
	if affixes.is_empty():
		add_random_affix(type_id)
		return
	affixes[randi() % affixes.size()] = AFFIX_POOL[randi() % AFFIX_POOL.size()]
	bomb_affixes[type_id] = affixes

func calculate_damage(type_id: String) -> int:
	var info = get_bomb_info(type_id)
	var dmg = info.get("damage", 5) + bonus_damage
	if has_affix(type_id, "overload"):
		dmg = int(dmg * 1.6)
	elif has_affix(type_id, "delay"):
		dmg = int(dmg * 1.2)
	return dmg

func get_bomb_level(type_id: String) -> int:
	return bomb_levels.get(type_id, 1)

func upgrade_bomb_level(type_id: String):
	bomb_levels[type_id] = get_bomb_level(type_id) + 1

func upgrade_all_bomb_levels():
	for type_id in BOMB_TYPES:
		bomb_levels[type_id] = get_bomb_level(type_id) + 1

func get_range_description(type_id: String) -> String:
	var lvl = get_bomb_level(type_id)
	match type_id:
		"pierce_h":
			var reach = 1 + lvl
			return "横 ±%d 格" % reach
		"pierce_v":
			var reach = 1 + lvl
			return "竖 ±%d 格" % reach
		"cross":
			var reach = 1 + lvl
			return "十字 ±%d 格" % reach
		"fan":
			var reach = 1 + lvl
			return "扇形 %d 格" % reach
		"x_shot":
			var reach = 1 + lvl
			return "X形 ±%d 格" % reach
		"second_blast":
			var reach = 1 + lvl
			return "十字二段 ±%d 格" % reach
		"freeze_bomb":
			var reach = 1 + lvl
			return "冻结十字 ±%d 格" % reach
		"magnetic":
			return "磁吸半径 1"
		"bounce":
			var bounces = 1 + lvl
			return "反弹 %d 次" % bounces
		"scatter":
			var reach = 1 + lvl
			return "八方 %d 格" % reach
		"blackhole":
			var reach = 1 + lvl
			return "吸附半径 %d" % reach
		"ultimate":
			var reach = 4 + lvl
			return "究极范围 %d" % reach
		_:
			return ""

func reset_levels():
	bomb_levels.clear()

func reset_to_defaults():
	bomb_levels.clear()
	bomb_affixes.clear()
	unlocked_types = ["pierce_h", "pierce_v"]
