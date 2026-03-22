## 关卡数据 - AutoLoad
## 5个主题关卡循环，随周期递增难度
## 每层独立的Boss形状、棋盘大小、扫雷大小

extends Node

# ---- Boss 形状模板 ----
# 每个形状是一组 Vector2i 相对坐标，表示 Boss 占据的格子
# (0,0) 为左上角参考点

# 关卡1 - 石像鬼（3x3 方块）
const SHAPE_GARGOYLE = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2),
]

# 关卡2 - 影蛛（T形，5格宽）
const SHAPE_SPIDER = [
	                   Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	                   Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
]

# 关卡3 - 熔岩巨蛇（L形蜿蜒，4x4）
const SHAPE_SERPENT = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	                                               Vector2i(3,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3),
]

# 关卡4 - 骸骨巨人（十字形，5x5）
const SHAPE_GIANT = [
	                   Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	                   Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3), Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	                   Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
]

# 关卡5 - 深渊魔王（大U形，6x4）
const SHAPE_DEMON = [
	Vector2i(0,0), Vector2i(1,0),                                 Vector2i(4,0), Vector2i(5,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
]

# ---- 关卡定义 ----
const LEVELS = [
	{
		"id": 1,
		"name": "石牢",
		"boss_name": "石像鬼",
		"subtitle": "冰冷的石墙间回荡着低沉的呻吟…",
		"color": Color(0.6, 0.65, 0.7),
		"tile_weights": { "WEAK": 0.30, "ARMOR": 0.10, "ABSORB": 0.05, "NORMAL": 0.55 },
		"bomb_count": 6,
		"turn_duration": 45.0,
		"boss_attack": 4,
		"boss_move_interval": 60.0,
		"placement_cols": 10, "placement_rows": 6,
		"mine_cols": 10, "mine_rows": 5,
		"boss_shape": "GARGOYLE",
	},
	{
		"id": 2,
		"name": "暗影长廊",
		"boss_name": "影蛛",
		"subtitle": "影子在摇曳的火光中扭曲蠕动…",
		"color": Color(0.5, 0.35, 0.65),
		"tile_weights": { "WEAK": 0.20, "ARMOR": 0.20, "ABSORB": 0.10, "NORMAL": 0.50 },
		"bomb_count": 8,
		"turn_duration": 40.0,
		"boss_attack": 5,
		"boss_move_interval": 55.0,
		"placement_cols": 11, "placement_rows": 6,
		"mine_cols": 11, "mine_rows": 5,
		"boss_shape": "SPIDER",
	},
	{
		"id": 3,
		"name": "熔岩洞窟",
		"boss_name": "熔岩巨蛇",
		"subtitle": "脚下的岩浆发出炙热的光芒…",
		"color": Color(0.95, 0.45, 0.15),
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.20, "ABSORB": 0.20, "NORMAL": 0.45 },
		"bomb_count": 9,
		"turn_duration": 35.0,
		"boss_attack": 6,
		"boss_move_interval": 50.0,
		"placement_cols": 12, "placement_rows": 7,
		"mine_cols": 12, "mine_rows": 5,
		"boss_shape": "SERPENT",
	},
	{
		"id": 4,
		"name": "骸骨密室",
		"boss_name": "骸骨巨人",
		"subtitle": "堆积如山的白骨中传来咔嚓声…",
		"color": Color(0.85, 0.82, 0.7),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.35, "ABSORB": 0.15, "NORMAL": 0.40 },
		"bomb_count": 10,
		"turn_duration": 32.0,
		"boss_attack": 7,
		"boss_move_interval": 45.0,
		"placement_cols": 13, "placement_rows": 8,
		"mine_cols": 12, "mine_rows": 6,
		"boss_shape": "GIANT",
	},
	{
		"id": 5,
		"name": "深渊王座",
		"boss_name": "深渊魔王",
		"subtitle": "黑暗的尽头，一双猩红的眼睛注视着你…",
		"color": Color(0.9, 0.12, 0.08),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.30, "ABSORB": 0.22, "NORMAL": 0.40 },
		"bomb_count": 12,
		"turn_duration": 28.0,
		"boss_attack": 9,
		"boss_move_interval": 40.0,
		"placement_cols": 14, "placement_rows": 8,
		"mine_cols": 14, "mine_rows": 6,
		"boss_shape": "DEMON",
	},
]

const SHAPE_MAP = {
	"GARGOYLE": SHAPE_GARGOYLE,
	"SPIDER": SHAPE_SPIDER,
	"SERPENT": SHAPE_SERPENT,
	"GIANT": SHAPE_GIANT,
	"DEMON": SHAPE_DEMON,
}

# ── 查询接口 ──

func get_level(floor_number: int) -> Dictionary:
	var idx = (floor_number - 1) % LEVELS.size()
	return LEVELS[idx]

func get_cycle(floor_number: int) -> int:
	return (floor_number - 1) / LEVELS.size()

func get_level_name(floor_number: int) -> String:
	return get_level(floor_number)["name"]

func get_boss_name(floor_number: int) -> String:
	return get_level(floor_number)["boss_name"]

func get_level_subtitle(floor_number: int) -> String:
	return get_level(floor_number)["subtitle"]

func get_level_color(floor_number: int) -> Color:
	return get_level(floor_number)["color"]

# ── 棋盘大小 ──

func get_placement_cols(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["placement_cols"] + cycle
	
func get_placement_rows(floor_number: int) -> int:
	return get_level(floor_number)["placement_rows"]

func get_mine_cols(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["mine_cols"] + cycle

func get_mine_rows(floor_number: int) -> int:
	return get_level(floor_number)["mine_rows"]

func get_boss_shape(floor_number: int) -> Array:
	var key = get_level(floor_number)["boss_shape"]
	return SHAPE_MAP[key]

# 根据棋盘大小自动计算格子像素大小，保证放置区+扫雷区不超过可用高度
func get_cell_size(floor_number: int) -> int:
	var p_cols = get_placement_cols(floor_number)
	var p_rows = get_placement_rows(floor_number)
	var m_cols = get_mine_cols(floor_number)
	var m_rows = get_mine_rows(floor_number)
	var max_cols = max(p_cols, m_cols)
	# 可用宽度 1760px（左右各 80 留白），可用高度 880px（顶68 HUD + 64 selector + 留白）
	var size_by_w = int(1760.0 / max_cols)
	var size_by_h = int(880.0 / (p_rows + m_rows))
	return min(size_by_w, size_by_h)

# ── 难度参数（含周期递增）──

func get_bomb_count(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["bomb_count"] + cycle

func get_turn_duration(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return maxf(level["turn_duration"] - cycle * 2.0, 15.0)

func get_boss_attack(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["boss_attack"] + cycle * 2

func get_boss_move_interval(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return maxf(level["boss_move_interval"] - cycle * 5.0, 20.0)

func get_tile_weights(floor_number: int) -> Dictionary:
	return get_level(floor_number)["tile_weights"]

func get_hp_multiplier(floor_number: int) -> float:
	var cycle = get_cycle(floor_number)
	return 1.0 + cycle * 0.3

func get_max_clicks(floor_number: int) -> int:
	var cycle = get_cycle(floor_number)
	return 5 + floor_number + cycle
