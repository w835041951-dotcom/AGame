## 成就系统 - AutoLoad
## 追踪玩家统计数据和成就解锁

extends Node

signal achievement_unlocked(id: String, title: String)

# ---- 持久化统计 ----
var stats: Dictionary = {
	"total_runs": 0,
	"total_damage": 0,
	"max_chain": 0,
	"max_floor": 0,
	"bosses_killed": 0,
	"bombs_used": 0,
	"total_crits": 0,
	"perfect_turns": 0,  # 一回合不受伤
}

# ---- 成就定义 ----
const ACHIEVEMENTS = {
	"first_blood":    { "title": "初战告捷",     "desc": "击败第一个Boss",         "icon": "⚔",  "check": "bosses_killed >= 1" },
	"explorer":       { "title": "探索者",       "desc": "通过10层",              "icon": "🗺",  "check": "max_floor >= 10" },
	"veteran":        { "title": "老练冒险家",    "desc": "通过30层",              "icon": "🏅",  "check": "max_floor >= 30" },
	"legend":         { "title": "传奇勇者",     "desc": "通过50层",              "icon": "🏆",  "check": "max_floor >= 50" },
	"champion":       { "title": "十境征服者",    "desc": "通关全部100层",          "icon": "👑",  "check": "max_floor >= 100" },
	"combo_starter":  { "title": "连锁入门",     "desc": "达成3连锁",             "icon": "🔗",  "check": "max_chain >= 3" },
	"combo_master":   { "title": "连锁大师",     "desc": "达成8连锁",             "icon": "⛓",  "check": "max_chain >= 8" },
	"demolisher":     { "title": "爆破专家",     "desc": "累计造成10000伤害",      "icon": "💥",  "check": "total_damage >= 10000" },
	"destroyer":      { "title": "毁灭者",       "desc": "累计造成100000伤害",     "icon": "☄",  "check": "total_damage >= 100000" },
	"bomber":         { "title": "炸弹达人",     "desc": "累计使用500个炸弹",      "icon": "💣",  "check": "bombs_used >= 500" },
	"persistence":    { "title": "百折不挠",     "desc": "游玩10局",              "icon": "🔁",  "check": "total_runs >= 10" },
	"flawless_flow":  { "title": "无伤节奏",     "desc": "累计达成20次无伤回合",    "icon": "🛡",  "check": "perfect_turns >= 20" },
	"critical_eye":   { "title": "暴击之眼",     "desc": "触发50次暴击",           "icon": "👁",  "check": "total_crits >= 50" },
}

var unlocked: Dictionary = {}  # id -> true
var _took_damage_this_turn: bool = false

const SAVE_PATH = "user://achievements.json"

func _ready():
	_load()
	# Wire signals
	GameManager.boss_defeated.connect(_on_boss_defeated)
	GameManager.turn_started.connect(_on_turn_started)
	GameManager.turn_ended.connect(_on_turn_ended)
	GameManager.player_damaged.connect(_on_player_damaged)
	ExplosionCalc.critical_hit.connect(func(_c, _d): _inc("total_crits", 1))

func _on_turn_started():
	_took_damage_this_turn = false

func _on_player_damaged(_amount: int):
	_took_damage_this_turn = true

func _on_turn_ended():
	if not _took_damage_this_turn and GameManager.player_hp > 0:
		_inc("perfect_turns", 1)

func _on_boss_defeated():
	_inc("bosses_killed", 1)

func end_run():
	stats["total_runs"] += 1
	stats["total_damage"] += GameManager.stat_total_damage
	stats["bombs_used"] += GameManager.stat_bombs_used
	if GameManager.stat_max_chain > stats["max_chain"]:
		stats["max_chain"] = GameManager.stat_max_chain
	if GameManager.stat_floors_cleared > stats["max_floor"]:
		stats["max_floor"] = GameManager.stat_floors_cleared
	_check_all()
	_save()

func _inc(key: String, amount: int):
	stats[key] = stats.get(key, 0) + amount

func _check_all():
	for id in ACHIEVEMENTS:
		if unlocked.has(id):
			continue
		var ach = ACHIEVEMENTS[id]
		if _evaluate(ach["check"]):
			unlocked[id] = true
			achievement_unlocked.emit(id, ach["title"])

func _evaluate(expr: String) -> bool:
	# Simple "stat_key >= value" evaluator
	var parts = expr.split(" ")
	if parts.size() != 3:
		return false
	var key = parts[0]
	var val = stats.get(key, 0)
	var threshold = int(parts[2])
	match parts[1]:
		">=": return val >= threshold
		">":  return val > threshold
		"==": return val == threshold
	return false

func get_progress(id: String) -> float:
	if unlocked.has(id):
		return 1.0
	var ach = ACHIEVEMENTS.get(id, {})
	var expr = ach.get("check", "")
	var parts = expr.split(" ")
	if parts.size() != 3:
		return 0.0
	var key = parts[0]
	var val = float(stats.get(key, 0))
	var threshold = float(parts[2])
	if threshold <= 0:
		return 0.0
	return clampf(val / threshold, 0.0, 1.0)

func get_unlocked_count() -> int:
	return unlocked.size()

func get_total_count() -> int:
	return ACHIEVEMENTS.size()

func _save():
	var data = { "stats": stats, "unlocked": unlocked }
	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))

func _load():
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return
	var json = JSON.new()
	if json.parse(file.get_as_text()) != OK:
		return
	var data = json.data
	if data is Dictionary:
		if data.has("stats") and data["stats"] is Dictionary:
			for k in data["stats"]:
				stats[k] = int(data["stats"][k])
		if data.has("unlocked") and data["unlocked"] is Dictionary:
			unlocked = data["unlocked"]
