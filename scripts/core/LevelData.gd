## 关卡数据 - AutoLoad
## 5个主题关卡循环，随周期递增难度
## 每层独立的Boss形状、棋盘大小、探索区大小

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

# ---- 强化形状（关卡 6-10 循环，中大型 10-16 格）----

# 关卡6 - 巫妖（菱形脊骨，11格）
const SHAPE_LICH = [
	                   Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1),                    Vector2i(2,1),                Vector2i(4,1),
	                   Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	                                  Vector2i(2,3),
	                   Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
]

# 关卡7 - 海妖（弯钩形，12格）
const SHAPE_LEVIATHAN = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0), Vector2i(3,0), Vector2i(4,0),
	               Vector2i(1,1),                                Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	                                                              Vector2i(4,3),
	               Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
]

# 关卡8 - 地狱狗（宽爪形，13格）
const SHAPE_HELLHOUND = [
	Vector2i(0,0),                    Vector2i(2,0),                Vector2i(4,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	               Vector2i(1,3),                Vector2i(3,3),
	               Vector2i(1,4),                Vector2i(3,4),
]

# 关卡9 - 魂灵（虚空环形，14格）
const SHAPE_WRAITH = [
	                   Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1),                                                  Vector2i(4,1),
	Vector2i(0,2),                    Vector2i(2,2),                Vector2i(4,2),
	Vector2i(0,3),                                                  Vector2i(4,3),
	                   Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
]

# 关卡10 - 蝎王（宽尾蝎形，16格）
const SHAPE_SCORPION = [
	                   Vector2i(1,0),                Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	                               Vector2i(2,3),
	                               Vector2i(2,4), Vector2i(3,4), Vector2i(4,4),
]

# ---- 超级形状（关卡 11-15 循环，大型 15-22 格）----

# 关卡11 - 龙（S形躯干，18格）
const SHAPE_DRAGON = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	                               Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	                               Vector2i(2,2), Vector2i(3,2),
	                   Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	Vector2i(0,4), Vector2i(1,4), Vector2i(2,4),
	Vector2i(0,5), Vector2i(1,5),
]

# 关卡12 - 九头蛇（Y分叉形，19格）
const SHAPE_HYDRA = [
	Vector2i(0,0), Vector2i(1,0),                 Vector2i(3,0), Vector2i(4,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	                               Vector2i(2,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	               Vector2i(1,4),                Vector2i(3,4),
	               Vector2i(1,5), Vector2i(2,5), Vector2i(3,5),
	Vector2i(0,6),                                               Vector2i(4,6),
]

# 关卡13 - 不死鸟（展翼形，20格）
const SHAPE_PHOENIX = [
	Vector2i(0,0),                                               Vector2i(5,0),
	Vector2i(0,1), Vector2i(1,1),                 Vector2i(4,1), Vector2i(5,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	                               Vector2i(2,4), Vector2i(3,4),
	                               Vector2i(2,5), Vector2i(3,5),
]

# 关卡14 - 巨像（城堡形，21格）
const SHAPE_COLOSSUS = [
	Vector2i(0,0), Vector2i(1,0),                 Vector2i(3,0), Vector2i(4,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	               Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
	                               Vector2i(2,5),
]

# 关卡15 - 克苏鲁（触手扩散形，22格）
const SHAPE_CTHULHU = [
	Vector2i(0,0),                Vector2i(2,0),                Vector2i(4,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	Vector2i(0,4),                Vector2i(2,4),                Vector2i(4,4),
	Vector2i(0,5),                               Vector2i(3,5),
]

# ---- 神话形状（关卡 16-20 循环，超大型 20-30 格）----

# 关卡16 - 虚无领主（空心大方块，24格）
const SHAPE_VOID_LORD = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0), Vector2i(3,0), Vector2i(4,0), Vector2i(5,0),
	Vector2i(0,1),                                                               Vector2i(5,1),
	Vector2i(0,2),                Vector2i(2,2), Vector2i(3,2),                 Vector2i(5,2),
	Vector2i(0,3),                Vector2i(2,3), Vector2i(3,3),                 Vector2i(5,3),
	Vector2i(0,4),                                                               Vector2i(5,4),
	Vector2i(0,5), Vector2i(1,5), Vector2i(2,5), Vector2i(3,5), Vector2i(4,5), Vector2i(5,5),
]

# 关卡17 - 暗影帝皇（王座宽冠形，25格）
const SHAPE_SHADOW_EMPEROR = [
	Vector2i(0,0), Vector2i(1,0),                 Vector2i(3,0),                Vector2i(5,0), Vector2i(6,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1), Vector2i(6,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
	               Vector2i(1,3),                Vector2i(3,3),                Vector2i(5,3),
	                               Vector2i(2,4), Vector2i(3,4), Vector2i(4,4),
]

# 关卡18 - 混沌神（非对称混沌形，26格）
const SHAPE_CHAOS_GOD = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0),
	Vector2i(0,1),                Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2),                Vector2i(4,2), Vector2i(5,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3), Vector2i(5,3),
	Vector2i(0,4),                Vector2i(2,4),                Vector2i(4,4),
	Vector2i(0,5), Vector2i(1,5),                Vector2i(3,5), Vector2i(4,5), Vector2i(5,5),
]

# 关卡19 - 永恒巨兽（双十字叠加，28格）
const SHAPE_ETERNAL_BEAST = [
	                   Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	Vector2i(0,3), Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	               Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
	Vector2i(0,5), Vector2i(1,5), Vector2i(2,5), Vector2i(3,5), Vector2i(4,5),
	               Vector2i(1,6), Vector2i(2,6), Vector2i(3,6),
]

# 关卡20 - 宇宙终焉（满星云扩散形，30格）
const SHAPE_APOCALYPSE = [
	Vector2i(0,0),                Vector2i(2,0),                Vector2i(4,0),                Vector2i(6,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2), Vector2i(6,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3), Vector2i(5,3),
	Vector2i(0,4),                Vector2i(2,4),                Vector2i(4,4),                Vector2i(6,4),
	               Vector2i(1,5),                Vector2i(3,5),                Vector2i(5,5),
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
		"bomb_count": 9,
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
		"bomb_count": 13,
		"turn_duration": 40.0,
		"boss_attack": 5,
		"boss_move_interval": 55.0,
		"placement_cols": 13, "placement_rows": 7,
		"mine_cols": 13, "mine_rows": 6,
		"boss_shape": "SPIDER",
	},
	{
		"id": 3,
		"name": "熔岩洞窟",
		"boss_name": "熔岩巨蛇",
		"subtitle": "脚下的岩浆发出炙热的光芒…",
		"color": Color(0.95, 0.45, 0.15),
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.20, "ABSORB": 0.15, "NORMAL": 0.50 },
		"bomb_count": 16,
		"turn_duration": 36.0,
		"boss_attack": 6,
		"boss_move_interval": 50.0,
		"placement_cols": 15, "placement_rows": 8,
		"mine_cols": 14, "mine_rows": 6,
		"boss_shape": "SERPENT",
	},
	{
		"id": 4,
		"name": "骸骨密室",
		"boss_name": "骸骨巨人",
		"subtitle": "堆积如山的白骨中传来咔嚓声…",
		"color": Color(0.85, 0.82, 0.7),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.35, "ABSORB": 0.12, "NORMAL": 0.43 },
		"bomb_count": 19,
		"turn_duration": 36.0,
		"boss_attack": 7,
		"boss_move_interval": 45.0,
		"placement_cols": 17, "placement_rows": 9,
		"mine_cols": 16, "mine_rows": 7,
		"boss_shape": "GIANT",
	},
	{
		"id": 5,
		"name": "深渊王座",
		"boss_name": "深渊魔王",
		"subtitle": "黑暗的尽头，一双猩红的眼睛注视着你…",
		"color": Color(0.9, 0.12, 0.08),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.30, "ABSORB": 0.15, "NORMAL": 0.47 },
		"bomb_count": 22,
		"turn_duration": 32.0,
		"boss_attack": 9,
		"boss_move_interval": 40.0,
		"placement_cols": 19, "placement_rows": 10,
		"mine_cols": 18, "mine_rows": 7,
		"boss_shape": "DEMON",
	},
	# ---- 关卡 6-10：寒冰/暮色 主题 ----
	{
		"id": 6,
		"name": "冰霜祭坛",
		"boss_name": "巫妖祭司",
		"subtitle": "冻结的咒语封印着无数亡魂的怒火…",
		"color": Color(0.55, 0.82, 0.98),
		"tile_weights": { "WEAK": 0.20, "ARMOR": 0.20, "ABSORB": 0.12, "NORMAL": 0.48 },
		"bomb_count": 25,
		"turn_duration": 30.0,
		"boss_attack": 10,
		"boss_move_interval": 38.0,
		"placement_cols": 20, "placement_rows": 10,
		"mine_cols": 19, "mine_rows": 8,
		"boss_shape": "LICH",
	},
	{
		"id": 7,
		"name": "深海神殿",
		"boss_name": "海渊妖姬",
		"subtitle": "触碰圣坛的瞬间，海水倒灌而来…",
		"color": Color(0.10, 0.45, 0.75),
		"tile_weights": { "WEAK": 0.18, "ARMOR": 0.22, "ABSORB": 0.14, "NORMAL": 0.46 },
		"bomb_count": 27,
		"turn_duration": 29.0,
		"boss_attack": 11,
		"boss_move_interval": 36.0,
		"placement_cols": 21, "placement_rows": 10,
		"mine_cols": 20, "mine_rows": 8,
		"boss_shape": "LEVIATHAN",
	},
	{
		"id": 8,
		"name": "炼狱犬舍",
		"boss_name": "烈焰地狱犬",
		"subtitle": "三颗狗头同时发出令人窒息的嚎叫…",
		"color": Color(0.95, 0.55, 0.10),
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.28, "ABSORB": 0.14, "NORMAL": 0.43 },
		"bomb_count": 29,
		"turn_duration": 28.0,
		"boss_attack": 12,
		"boss_move_interval": 34.0,
		"placement_cols": 22, "placement_rows": 11,
		"mine_cols": 21, "mine_rows": 8,
		"boss_shape": "HELLHOUND",
	},
	{
		"id": 9,
		"name": "幽灵船骸",
		"boss_name": "缥缈魂灵",
		"subtitle": "腐烂的船板间飘荡着无声的哭泣…",
		"color": Color(0.70, 0.90, 0.80),
		"tile_weights": { "WEAK": 0.12, "ARMOR": 0.25, "ABSORB": 0.18, "NORMAL": 0.45 },
		"bomb_count": 31,
		"turn_duration": 27.0,
		"boss_attack": 13,
		"boss_move_interval": 32.0,
		"placement_cols": 23, "placement_rows": 11,
		"mine_cols": 22, "mine_rows": 9,
		"boss_shape": "WRAITH",
	},
	{
		"id": 10,
		"name": "毒刺沙漠",
		"boss_name": "沙漠蝎王",
		"subtitle": "炽热的沙尘暴掩盖了那柄致命的巨螫…",
		"color": Color(0.92, 0.80, 0.30),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.30, "ABSORB": 0.16, "NORMAL": 0.44 },
		"bomb_count": 33,
		"turn_duration": 26.0,
		"boss_attack": 14,
		"boss_move_interval": 30.0,
		"placement_cols": 24, "placement_rows": 12,
		"mine_cols": 23, "mine_rows": 9,
		"boss_shape": "SCORPION",
	},
	# ---- 关卡 11-15：龙焰/古神 主题 ----
	{
		"id": 11,
		"name": "龙渊熔炉",
		"boss_name": "永焰金龙",
		"subtitle": "古龙的咆哮震碎了洞窟千年的寂静…",
		"color": Color(0.98, 0.40, 0.12),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.32, "ABSORB": 0.18, "NORMAL": 0.42 },
		"bomb_count": 35,
		"turn_duration": 25.0,
		"boss_attack": 15,
		"boss_move_interval": 28.0,
		"placement_cols": 24, "placement_rows": 12,
		"mine_cols": 23, "mine_rows": 10,
		"boss_shape": "DRAGON",
	},
	{
		"id": 12,
		"name": "腐化神殿",
		"boss_name": "九头血蛇",
		"subtitle": "每割下一颗头颅，便生出两颗更邪恶的…",
		"color": Color(0.40, 0.75, 0.25),
		"tile_weights": { "WEAK": 0.07, "ARMOR": 0.33, "ABSORB": 0.20, "NORMAL": 0.40 },
		"bomb_count": 37,
		"turn_duration": 24.0,
		"boss_attack": 15,
		"boss_move_interval": 27.0,
		"placement_cols": 25, "placement_rows": 12,
		"mine_cols": 24, "mine_rows": 10,
		"boss_shape": "HYDRA",
	},
	{
		"id": 13,
		"name": "烬羽圣山",
		"boss_name": "涅槃不死鸟",
		"subtitle": "在灰烬中诞生的火焰永远无法被扑灭…",
		"color": Color(0.98, 0.70, 0.10),
		"tile_weights": { "WEAK": 0.06, "ARMOR": 0.34, "ABSORB": 0.20, "NORMAL": 0.40 },
		"bomb_count": 38,
		"turn_duration": 24.0,
		"boss_attack": 16,
		"boss_move_interval": 26.0,
		"placement_cols": 25, "placement_rows": 13,
		"mine_cols": 24, "mine_rows": 10,
		"boss_shape": "PHOENIX",
	},
	{
		"id": 14,
		"name": "巨神战场",
		"boss_name": "钢铁巨像",
		"subtitle": "大地在每一步伐下颤抖，天空因它而变色…",
		"color": Color(0.65, 0.68, 0.72),
		"tile_weights": { "WEAK": 0.05, "ARMOR": 0.40, "ABSORB": 0.18, "NORMAL": 0.37 },
		"bomb_count": 40,
		"turn_duration": 23.0,
		"boss_attack": 16,
		"boss_move_interval": 25.0,
		"placement_cols": 26, "placement_rows": 13,
		"mine_cols": 25, "mine_rows": 10,
		"boss_shape": "COLOSSUS",
	},
	{
		"id": 15,
		"name": "星渊禁地",
		"boss_name": "星海克苏鲁",
		"subtitle": "凝视深渊，深渊亦以无数触手凝视着你…",
		"color": Color(0.30, 0.15, 0.55),
		"tile_weights": { "WEAK": 0.05, "ARMOR": 0.38, "ABSORB": 0.22, "NORMAL": 0.35 },
		"bomb_count": 42,
		"turn_duration": 22.0,
		"boss_attack": 17,
		"boss_move_interval": 24.0,
		"placement_cols": 26, "placement_rows": 13,
		"mine_cols": 25, "mine_rows": 11,
		"boss_shape": "CTHULHU",
	},
	# ---- 关卡 16-20：虚空/终焉 主题 ----
	{
		"id": 16,
		"name": "虚空裂隙",
		"boss_name": "虚无领主",
		"subtitle": "裂缝的另一端是比死亡更彻底的虚无…",
		"color": Color(0.20, 0.05, 0.35),
		"tile_weights": { "WEAK": 0.04, "ARMOR": 0.38, "ABSORB": 0.24, "NORMAL": 0.34 },
		"bomb_count": 42,
		"turn_duration": 22.0,
		"boss_attack": 17,
		"boss_move_interval": 23.0,
		"placement_cols": 27, "placement_rows": 13,
		"mine_cols": 26, "mine_rows": 11,
		"boss_shape": "VOID_LORD",
	},
	{
		"id": 17,
		"name": "暗影皇宫",
		"boss_name": "暗影帝皇",
		"subtitle": "千万亡灵俯首，铸就了他不朽的王冠…",
		"color": Color(0.12, 0.08, 0.22),
		"tile_weights": { "WEAK": 0.04, "ARMOR": 0.40, "ABSORB": 0.24, "NORMAL": 0.32 },
		"bomb_count": 43,
		"turn_duration": 21.0,
		"boss_attack": 17,
		"boss_move_interval": 23.0,
		"placement_cols": 27, "placement_rows": 14,
		"mine_cols": 26, "mine_rows": 11,
		"boss_shape": "SHADOW_EMPEROR",
	},
	{
		"id": 18,
		"name": "混沌神域",
		"boss_name": "混沌化身",
		"subtitle": "秩序在此终结，唯有无尽的混乱延伸…",
		"color": Color(0.60, 0.10, 0.70),
		"tile_weights": { "WEAK": 0.04, "ARMOR": 0.38, "ABSORB": 0.26, "NORMAL": 0.32 },
		"bomb_count": 43,
		"turn_duration": 21.0,
		"boss_attack": 18,
		"boss_move_interval": 22.0,
		"placement_cols": 27, "placement_rows": 14,
		"mine_cols": 26, "mine_rows": 12,
		"boss_shape": "CHAOS_GOD",
	},
	{
		"id": 19,
		"name": "永恒冰牢",
		"boss_name": "永恒巨兽",
		"subtitle": "亿万年的沉眠之后，它再度睁开了那双眼…",
		"color": Color(0.80, 0.92, 1.00),
		"tile_weights": { "WEAK": 0.03, "ARMOR": 0.42, "ABSORB": 0.25, "NORMAL": 0.30 },
		"bomb_count": 44,
		"turn_duration": 20.0,
		"boss_attack": 18,
		"boss_move_interval": 22.0,
		"placement_cols": 28, "placement_rows": 14,
		"mine_cols": 27, "mine_rows": 12,
		"boss_shape": "ETERNAL_BEAST",
	},
	{
		"id": 20,
		"name": "末日星核",
		"boss_name": "宇宙终焉",
		"subtitle": "万物的终点已至——唯有爆炸能回应宇宙的沉默…",
		"color": Color(1.00, 0.98, 0.90),
		"tile_weights": { "WEAK": 0.02, "ARMOR": 0.43, "ABSORB": 0.25, "NORMAL": 0.30 },
		"bomb_count": 45,
		"turn_duration": 20.0,
		"boss_attack": 18,
		"boss_move_interval": 22.0,
		"placement_cols": 28, "placement_rows": 14,
		"mine_cols": 27, "mine_rows": 12,
		"boss_shape": "APOCALYPSE",
	},
]

const SHAPE_MAP = {
	"GARGOYLE": SHAPE_GARGOYLE,
	"SPIDER": SHAPE_SPIDER,
	"SERPENT": SHAPE_SERPENT,
	"GIANT": SHAPE_GIANT,
	"DEMON": SHAPE_DEMON,
	# 关卡 6-10
	"LICH": SHAPE_LICH,
	"LEVIATHAN": SHAPE_LEVIATHAN,
	"HELLHOUND": SHAPE_HELLHOUND,
	"WRAITH": SHAPE_WRAITH,
	"SCORPION": SHAPE_SCORPION,
	# 关卡 11-15
	"DRAGON": SHAPE_DRAGON,
	"HYDRA": SHAPE_HYDRA,
	"PHOENIX": SHAPE_PHOENIX,
	"COLOSSUS": SHAPE_COLOSSUS,
	"CTHULHU": SHAPE_CTHULHU,
	# 关卡 16-20
	"VOID_LORD": SHAPE_VOID_LORD,
	"SHADOW_EMPEROR": SHAPE_SHADOW_EMPEROR,
	"CHAOS_GOD": SHAPE_CHAOS_GOD,
	"ETERNAL_BEAST": SHAPE_ETERNAL_BEAST,
	"APOCALYPSE": SHAPE_APOCALYPSE,
}

const BOSS_TEXTURE_MAP = {
	"GARGOYLE": "res://assets/sprites/boss/boss_gargoyle.png",
	"SPIDER":   "res://assets/sprites/boss/boss_spider.png",
	"SERPENT":  "res://assets/sprites/boss/boss_serpent.png",
	"GIANT":    "res://assets/sprites/boss/boss_giant.png",
	"DEMON":    "res://assets/sprites/boss/boss_demon.png",
	# 关卡 6-10
	"LICH":          "res://assets/sprites/boss/boss_lich.png",
	"LEVIATHAN":     "res://assets/sprites/boss/boss_leviathan.png",
	"HELLHOUND":     "res://assets/sprites/boss/boss_hellhound.png",
	"WRAITH":        "res://assets/sprites/boss/boss_wraith.png",
	"SCORPION":      "res://assets/sprites/boss/boss_scorpion.png",
	# 关卡 11-15
	"DRAGON":        "res://assets/sprites/boss/boss_dragon.png",
	"HYDRA":         "res://assets/sprites/boss/boss_hydra.png",
	"PHOENIX":       "res://assets/sprites/boss/boss_phoenix.png",
	"COLOSSUS":      "res://assets/sprites/boss/boss_colossus.png",
	"CTHULHU":       "res://assets/sprites/boss/boss_cthulhu.png",
	# 关卡 16-20
	"VOID_LORD":        "res://assets/sprites/boss/boss_void_lord.png",
	"SHADOW_EMPEROR":   "res://assets/sprites/boss/boss_shadow_emperor.png",
	"CHAOS_GOD":        "res://assets/sprites/boss/boss_chaos_god.png",
	"ETERNAL_BEAST":    "res://assets/sprites/boss/boss_eternal_beast.png",
	"APOCALYPSE":       "res://assets/sprites/boss/boss_apocalypse.png",
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

func get_boss_texture_path(floor_number: int) -> String:
	var key = get_level(floor_number)["boss_shape"]
	return BOSS_TEXTURE_MAP[key]

# 根据棋盘大小自动计算格子像素大小，保证放置区+探索区不超过可用高度
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
	return 6 + floor_number + cycle * 2
