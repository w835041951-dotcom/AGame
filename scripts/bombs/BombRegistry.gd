## 炸弹类型注册表 - 单例
## 管理所有炸弹效果

extends Node

## 炸弹类型定义
const BOMB_TYPES = {
	"cross": {
		"name": "十字炮",
		"description": "横竖方向各攻击一排",
		"damage": 10,
		"color": Color.RED
	},
	"scatter": {
		"name": "散射",
		"description": "8个方向各发射一发",
		"damage": 6,
		"color": Color.ORANGE
	},
	"bounce": {
		"name": "反弹",
		"description": "发射后遇墙反弹，最多3次",
		"damage": 8,
		"color": Color.CYAN
	},
	"pierce": {
		"name": "穿透",
		"description": "直线穿透，伤害递减",
		"damage": 15,
		"color": Color.YELLOW
	},
	"area": {
		"name": "爆炸",
		"description": "3x3范围伤害",
		"damage": 12,
		"color": Color.FIREBRICK
	}
}

## 玩家当前解锁的炸弹类型（肉鸽升级后扩展）
var unlocked_types: Array = ["cross", "scatter"]

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
