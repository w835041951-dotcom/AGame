## 升级系统 - AutoLoad
## 临时升级（当层有效）+ 永久升级（整局有效）

extends Node

# ---- 永久升级池（通关奖励 - 炸弹升级） ----
const PERMANENT_UPGRADES = [
	{ "id": "bomb_range_up",  "name": "范围扩展", "description": "所有炸弹攻击范围 +1",   "rarity": "rare"   },
	{ "id": "bomb_dmg_up",    "name": "火药加强", "description": "所有炸弹基础伤害 +3",   "rarity": "common" },
	{ "id": "unlock_cross",   "name": "十字炮",   "description": "解锁十字炮炸弹",          "rarity": "rare"   },
	{ "id": "unlock_fan",     "name": "扇形弹",   "description": "解锁扇形弹",              "rarity": "rare"   },
	{ "id": "unlock_x_shot",  "name": "X发射",    "description": "解锁X发射炸弹",            "rarity": "rare"   },
	{ "id": "unlock_second",  "name": "二次弹",   "description": "解锁二次引爆弹",          "rarity": "epic"   },
	{ "id": "unlock_freeze",  "name": "冰封弹",   "description": "解锁冰封弹",              "rarity": "epic"   },
	{ "id": "unlock_magnetic", "name": "磁暴弹",  "description": "解锁磁暴弹",             "rarity": "epic"   },
	{ "id": "unlock_bounce",  "name": "反弹炸弹", "description": "解锁反弹炸弹",            "rarity": "epic"   },
	{ "id": "unlock_blackhole", "name": "黑洞弹", "description": "解锁黑洞弹",              "rarity": "epic"   },
	{ "id": "unlock_ultimate", "name": "究极弹",  "description": "解锁局内唯一究极弹",      "rarity": "epic"   },
	{ "id": "chain_boost",    "name": "连锁大师", "description": "连锁加成从30%提升到60%","rarity": "epic"   },
]

# ---- 临时升级池（血量阶段奖励 - 棋盘效果） ----
const COMBAT_UPGRADES = [
	{ "id": "reveal_bombs",     "name": "全图透视", "description": "探索区所有炸弹位置显示",  "rarity": "rare"   },
	{ "id": "reveal_area",      "name": "局部透视", "description": "随机翻开探索区5×5区域",   "rarity": "common" },
	{ "id": "extra_weak",       "name": "暴露弱点", "description": "Boss新增1个弱点格",       "rarity": "rare"   },
	{ "id": "freeze_boss",      "name": "冻结Boss", "description": "本回合Boss不移动",         "rarity": "rare"   },
	{ "id": "heal_combat",      "name": "战场急救", "description": "立即回复 8 点HP",         "rarity": "common" },
	{ "id": "more_clicks",      "name": "额外点击", "description": "本层探索次数 +2",   "rarity": "common" },
	{ "id": "extra_bombs",      "name": "弹药补给", "description": "立即获得2个当前类型炸弹", "rarity": "common" },
	{ "id": "double_detonate",  "name": "二次引爆", "description": "下次引爆触发两次",         "rarity": "epic"   },
]

# ---- 临时效果状态 ----
var active_combat: Dictionary = {}  # effect_id -> bool or value

# ---- 永久效果状态 ----
var _chain_multiplier_perm: float = 0.3  # 默认值，chain_boost 升级后变 0.5

signal reveal_bombs_triggered

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
		"bomb_range_up":
			BombRegistry.upgrade_all_bomb_levels()
		"bomb_dmg_up":
			BombRegistry.bonus_damage += 3
		"unlock_cross":
			BombRegistry.unlock_type("cross")
		"unlock_fan":
			BombRegistry.unlock_type("fan")
		"unlock_x_shot":
			BombRegistry.unlock_type("x_shot")
		"unlock_second":
			BombRegistry.unlock_type("second_blast")
		"unlock_freeze":
			BombRegistry.unlock_type("freeze_bomb")
		"unlock_magnetic":
			BombRegistry.unlock_type("magnetic")
		"unlock_bounce":
			BombRegistry.unlock_type("bounce")
		"unlock_blackhole":
			BombRegistry.unlock_type("blackhole")
		"unlock_ultimate":
			BombRegistry.unlock_type("ultimate")
		"chain_boost":
			_chain_multiplier_perm = 0.6

func apply_combat(upgrade: Dictionary):
	match upgrade["id"]:
		"reveal_bombs":
			active_combat["reveal_bombs"] = true
			reveal_bombs_triggered.emit()
		"reveal_area":
			var cx = randi_range(2, max(2, GridManager.cols - 3))
			var cy = randi_range(2, max(2, GridManager.rows - 3))
			GridManager.reveal_area(cx, cy, 2)
		"extra_weak":
			BossGrid.refresh_weak_tiles()
		"freeze_boss":
			active_combat["freeze_boss"] = true
		"heal_combat":
			GameManager.heal(8)
		"more_clicks":
			GameManager.current_clicks += 2
		"extra_bombs":
			GameManager.add_bomb(BombPlacer.selected_type)
			GameManager.add_bomb(BombPlacer.selected_type)
		"double_detonate":
			active_combat["double_detonate"] = true

func clear_combat_effects():
	active_combat.clear()

func get_combat_dmg_mult() -> float:
	return active_combat.get("dmg_boost", 1.0)

func get_chain_bonus_per_level() -> float:
	return _chain_multiplier_perm

func is_double_detonate() -> bool:
	return active_combat.get("double_detonate", false)

func consume_double_detonate():
	active_combat.erase("double_detonate")

func is_reveal_bombs() -> bool:
	return active_combat.get("reveal_bombs", false)

func is_boss_frozen() -> bool:
	return active_combat.get("freeze_boss", false)

func consume_freeze_boss():
	active_combat.erase("freeze_boss")
