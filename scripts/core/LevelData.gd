## 关卡数据 - AutoLoad
## 5个主题关卡循环，随周期递增难度

extends Node

# ---- 关卡定义 ----
# 每5层为一个周期，周期越高难度越大
const LEVELS = [
	{
		"id": 1,
		"name": "石牢",
		"subtitle": "冰冷的石墙间回荡着低沉的呻吟…",
		"color": Color(0.6, 0.65, 0.7),        # 灰蓝石头色
		"tile_weights": { "WEAK": 0.30, "ARMOR": 0.10, "ABSORB": 0.05, "NORMAL": 0.55 },
		"bomb_count": 6,
		"turn_duration": 45.0,
		"boss_attack": 4,
		"boss_move_interval": 60.0,
	},
	{
		"id": 2,
		"name": "暗影长廊",
		"subtitle": "影子在摇曳的火光中扭曲蠕动…",
		"color": Color(0.5, 0.35, 0.65),        # 暗紫色
		"tile_weights": { "WEAK": 0.20, "ARMOR": 0.20, "ABSORB": 0.10, "NORMAL": 0.50 },
		"bomb_count": 8,
		"turn_duration": 40.0,
		"boss_attack": 5,
		"boss_move_interval": 55.0,
	},
	{
		"id": 3,
		"name": "熔岩洞窟",
		"subtitle": "脚下的岩浆发出炙热的光芒…",
		"color": Color(0.95, 0.45, 0.15),       # 熔岩橙
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.20, "ABSORB": 0.20, "NORMAL": 0.45 },
		"bomb_count": 9,
		"turn_duration": 35.0,
		"boss_attack": 6,
		"boss_move_interval": 50.0,
	},
	{
		"id": 4,
		"name": "骸骨密室",
		"subtitle": "堆积如山的白骨中传来咔嚓声…",
		"color": Color(0.85, 0.82, 0.7),        # 骨白色
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.35, "ABSORB": 0.15, "NORMAL": 0.40 },
		"bomb_count": 10,
		"turn_duration": 32.0,
		"boss_attack": 7,
		"boss_move_interval": 45.0,
	},
	{
		"id": 5,
		"name": "深渊王座",
		"subtitle": "黑暗的尽头，一双猩红的眼睛注视着你…",
		"color": Color(0.9, 0.12, 0.08),        # 深渊红
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.30, "ABSORB": 0.22, "NORMAL": 0.40 },
		"bomb_count": 12,
		"turn_duration": 28.0,
		"boss_attack": 9,
		"boss_move_interval": 40.0,
	},
]

# ── 查询接口 ──

func get_level(floor_number: int) -> Dictionary:
	var idx = (floor_number - 1) % LEVELS.size()
	return LEVELS[idx]

func get_cycle(floor_number: int) -> int:
	# 第几轮循环（从0开始），用于叠加难度
	return (floor_number - 1) / LEVELS.size()

func get_level_name(floor_number: int) -> String:
	return get_level(floor_number)["name"]

func get_level_subtitle(floor_number: int) -> String:
	return get_level(floor_number)["subtitle"]

func get_level_color(floor_number: int) -> Color:
	return get_level(floor_number)["color"]

# ── 难度参数（含周期递增）──

func get_bomb_count(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	# 每周期多1个雷
	return level["bomb_count"] + cycle

func get_turn_duration(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	# 每周期少2秒，最低15秒
	return maxf(level["turn_duration"] - cycle * 2.0, 15.0)

func get_boss_attack(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	# 每周期+2攻击
	return level["boss_attack"] + cycle * 2

func get_boss_move_interval(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	# 每周期快5秒，最低20秒
	return maxf(level["boss_move_interval"] - cycle * 5.0, 20.0)

func get_tile_weights(floor_number: int) -> Dictionary:
	return get_level(floor_number)["tile_weights"]

func get_hp_multiplier(floor_number: int) -> float:
	var cycle = get_cycle(floor_number)
	# 每周期Boss血量+30%
	return 1.0 + cycle * 0.3

func get_max_clicks(floor_number: int) -> int:
	# 基础5 + 每层+1，每周期额外+1
	var cycle = get_cycle(floor_number)
	return 5 + floor_number + cycle
