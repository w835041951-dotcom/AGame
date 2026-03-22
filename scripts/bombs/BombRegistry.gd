## 炸弹类型注册表 - 单例
## 管理所有炸弹效果

extends Node

## 炸弹类型定义
const BOMB_TYPES = {
	"pierce_h": {
		"name": "横穿透",
		"description": "横向穿透，范围随等级增大",
		"damage": 12,
		"color": Color.YELLOW
	},
	"pierce_v": {
		"name": "竖穿透",
		"description": "纵向穿透，范围随等级增大",
		"damage": 12,
		"color": Color.GREEN_YELLOW
	},
	"cross": {
		"name": "十字炮",
		"description": "横竖方向各攻击一排",
		"damage": 10,
		"color": Color.RED
	},
	"x_shot": {
		"name": "X发射",
		"description": "对角线四方向发射",
		"damage": 10,
		"color": Color.ORANGE
	},
	"bounce": {
		"name": "反弹",
		"description": "发射后遇墙反弹",
		"damage": 10,
		"color": Color.CYAN
	}
}

## 玩家当前解锁的炸弹类型（肉鸽升级后扩展）
var unlocked_types: Array = ["pierce_h", "pierce_v"]

## 炸弹等级（影响攻击范围）
var bomb_levels: Dictionary = {}  # type_id -> int, 默认1

func get_available_types() -> Array:
	return unlocked_types

func unlock_type(type_id: String):
	if type_id in BOMB_TYPES and not type_id in unlocked_types:
		unlocked_types.append(type_id)

func get_bomb_info(type_id: String) -> Dictionary:
	return BOMB_TYPES.get(type_id, {})

func calculate_damage(type_id: String) -> int:
	var info = get_bomb_info(type_id)
	return info.get("damage", 5)

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
		"x_shot":
			var reach = 1 + lvl
			return "X形 ±%d 格" % reach
		"bounce":
			var bounces = 1 + lvl
			return "反弹 %d 次" % bounces
		_:
			return ""

func reset_levels():
	bomb_levels.clear()

func reset_to_defaults():
	bomb_levels.clear()
	unlocked_types = ["pierce_h", "pierce_v"]
