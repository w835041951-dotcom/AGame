## 肉鸽升级选项数据

extends Node

const UPGRADES = [
	{
		"id": "more_clicks",
		"name": "专注",
		"description": "每回合点击次数 +1",
		"rarity": "common",
	},
	{
		"id": "bomb_damage_up",
		"name": "火药加强",
		"description": "所有炸弹伤害 +3",
		"rarity": "common",
	},
	{
		"id": "unlock_bounce",
		"name": "反弹炸弹",
		"description": "解锁反弹炸弹，遇墙反弹3次",
		"rarity": "rare",
	},
	{
		"id": "unlock_pierce",
		"name": "穿透炸弹",
		"description": "解锁穿透炸弹，直线穿透伤害",
		"rarity": "rare",
	},
	{
		"id": "unlock_area",
		"name": "爆炸半径",
		"description": "解锁爆炸炸弹，3x3范围伤害",
		"rarity": "epic",
	},
	{
		"id": "heal",
		"name": "急救包",
		"description": "恢复 10 点生命值",
		"rarity": "common",
	},
]

func get_random_choices(count: int = 3) -> Array:
	var pool = UPGRADES.duplicate()
	pool.shuffle()
	return pool.slice(0, count)

func apply_upgrade(upgrade: Dictionary):
	match upgrade["id"]:
		"more_clicks":
			GameManager.max_clicks += 1
		"bomb_damage_up":
			for key in BombRegistry.BOMB_TYPES:
				BombRegistry.BOMB_TYPES[key]["damage"] += 3
		"unlock_bounce":
			BombRegistry.unlock_type("bounce")
		"unlock_pierce":
			BombRegistry.unlock_type("pierce")
		"unlock_area":
			BombRegistry.unlock_type("area")
		"heal":
			GameManager.player_hp = min(GameManager.player_hp + 10, GameManager.player_max_hp)
