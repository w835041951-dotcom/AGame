## 升级系统 - AutoLoad
## 临时升级（当层有效）+ 永久升级（整局有效）

extends Node

# ---- 永久升级池 ----
const PERMANENT_UPGRADES = [
	{ "id": "more_clicks",    "name": "专注",     "description": "扫雷点击次数 +1",       "rarity": "common" },
	{ "id": "bomb_dmg_up",    "name": "火药加强", "description": "所有炸弹基础伤害 +3",   "rarity": "common" },
	{ "id": "unlock_bounce",  "name": "反弹炸弹", "description": "解锁反弹炸弹",          "rarity": "rare"   },
	{ "id": "unlock_pierce",  "name": "穿透炸弹", "description": "解锁穿透炸弹",          "rarity": "rare"   },
	{ "id": "unlock_area",    "name": "爆炸半径", "description": "解锁爆炸炸弹(5x5)",     "rarity": "epic"   },
	{ "id": "max_hp_up",      "name": "强化体魄", "description": "最大HP +5，立即回复",   "rarity": "common" },
	{ "id": "more_time",      "name": "时间掌控", "description": "每回合时间 +10秒",      "rarity": "rare"   },
	{ "id": "chain_boost",    "name": "连锁大师", "description": "连锁加成从30%提升到50%","rarity": "epic"   },
]

# ---- 临时升级池 ----
const COMBAT_UPGRADES = [
	{ "id": "extra_bombs",      "name": "弹药补给", "description": "立即获得2个当前类型炸弹", "rarity": "common" },
	{ "id": "dmg_boost_turn",   "name": "烈性炸药", "description": "本层所有炸弹伤害 ×1.5",  "rarity": "rare"   },
	{ "id": "extra_weak",       "name": "暴露弱点", "description": "Boss新增1个弱点格",       "rarity": "rare"   },
	{ "id": "double_detonate",  "name": "二次引爆", "description": "下次引爆触发两次",         "rarity": "epic"   },
	{ "id": "reveal_bombs",     "name": "透视",     "description": "扫雷区所有炸弹位置显示",  "rarity": "rare"   },
	{ "id": "heal_combat",      "name": "战场急救", "description": "立即回复 8 点HP",         "rarity": "common" },
]

# ---- 临时效果状态 ----
var active_combat: Dictionary = {}  # effect_id -> bool or value

# ---- 永久效果状态 ----
var _chain_multiplier_perm: float = 0.3  # 默认值，chain_boost 升级后变 0.5

func get_permanent_choices(count: int = 3) -> Array:
	var pool = PERMANENT_UPGRADES.duplicate()
	pool.shuffle()
	return pool.slice(0, min(count, pool.size()))

func get_combat_choices(count: int = 3) -> Array:
	var pool = COMBAT_UPGRADES.duplicate()
	pool.shuffle()
	return pool.slice(0, min(count, pool.size()))

func apply_permanent(upgrade: Dictionary):
	match upgrade["id"]:
		"more_clicks":
			GameManager.max_clicks += 1
		"bomb_dmg_up":
			for key in BombRegistry.BOMB_TYPES:
				BombRegistry.BOMB_TYPES[key]["damage"] += 3
		"unlock_bounce":
			BombRegistry.unlock_type("bounce")
		"unlock_pierce":
			BombRegistry.unlock_type("pierce")
		"unlock_area":
			BombRegistry.unlock_type("area")
		"max_hp_up":
			GameManager.player_max_hp += 5
			GameManager.heal(5)
		"more_time":
			GameManager.turn_duration += 10.0
		"chain_boost":
			_chain_multiplier_perm = 0.5

func apply_combat(upgrade: Dictionary):
	match upgrade["id"]:
		"extra_bombs":
			GameManager.add_bomb(BombPlacer.selected_type)
			GameManager.add_bomb(BombPlacer.selected_type)
		"dmg_boost_turn":
			active_combat["dmg_boost"] = 1.5
		"extra_weak":
			BossGrid.refresh_weak_tiles()
		"double_detonate":
			active_combat["double_detonate"] = true
		"reveal_bombs":
			active_combat["reveal_bombs"] = true
		"heal_combat":
			GameManager.heal(8)

func clear_combat_effects():
	active_combat.clear()

func get_combat_dmg_mult() -> float:
	return active_combat.get("dmg_boost", 1.0)

func get_chain_bonus_per_level() -> float:
	# 临时效果可以叠加在永久基础上
	return active_combat.get("chain_multiplier", _chain_multiplier_perm)

func is_double_detonate() -> bool:
	return active_combat.get("double_detonate", false)

func consume_double_detonate():
	active_combat.erase("double_detonate")

func is_reveal_bombs() -> bool:
	return active_combat.get("reveal_bombs", false)
