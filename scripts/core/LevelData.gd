## 关卡数据 - AutoLoad
## 20个主题关卡 × 5周期 = 100层
## 每种Boss独立形状、配色、棋盘大小、探索区参数
## 周期递增：HP倍率、攻击力、移动速度、棋盘扩展

extends Node

# ============================================================
#  Boss 形状模板  (Vector2i 相对坐标, (0,0) = 左上角)
# ============================================================

# 1 - 石像鬼 (角+身+尾, 5×4, 9格)
const SHAPE_GARGOYLE = [
	               Vector2i(1,0),                Vector2i(3,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	                              Vector2i(2,3),
]

# 2 - 影蛛 (T形, 5×3, 11格)
const SHAPE_SPIDER = [
	               Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
]

# 3 - 熔岩巨蛇 (S形, 4×4, 10格)
const SHAPE_SERPENT = [
	Vector2i(0,0), Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	                                               Vector2i(3,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3),
]

# 4 - 骸骨巨人 (人形, 7×5, 19格)
const SHAPE_GIANT = [
	                              Vector2i(2,0), Vector2i(3,0), Vector2i(4,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
	Vector2i(0,3),                               Vector2i(3,3),                               Vector2i(6,3),
	               Vector2i(1,4),                Vector2i(3,4),                Vector2i(5,4),
]

# 5 - 深渊魔王 (双角+翼, 6×5, 20格)
const SHAPE_DEMON = [
	Vector2i(0,0),                                                              Vector2i(5,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	Vector2i(0,3), Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3), Vector2i(5,3),
	                              Vector2i(2,4), Vector2i(3,4),
]

# 6 - 冰霜女巫 (菱形, 5×5, 13格)
const SHAPE_WITCH = [
	                              Vector2i(2,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	                              Vector2i(2,4),
]

# 7 - 暗夜飞龙 (展翅, 7×3, 15格)
const SHAPE_WYVERN = [
	Vector2i(0,0),                Vector2i(3,0),                Vector2i(6,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1), Vector2i(6,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
]

# 8 - 深海巨怪 (触手散布, 5×4, 12格)
const SHAPE_KRAKEN = [
	Vector2i(0,0),                Vector2i(2,0),                Vector2i(4,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3),                Vector2i(2,3),                Vector2i(4,3),
]

# 9 - 铁甲傀儡 (H桥, 5×4, 14格)
const SHAPE_GOLEM = [
	Vector2i(0,0), Vector2i(1,0),                Vector2i(3,0), Vector2i(4,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3), Vector2i(1,3),                Vector2i(3,3), Vector2i(4,3),
]

# 10 - 血月狼王 (箭头, 6×5, 14格)
const SHAPE_WOLF = [
	                                             Vector2i(3,0),
	                              Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
	                              Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	                                             Vector2i(3,4),
]

# 11 - 雷霆泰坦 (蝶形, 7×5, 19格)
const SHAPE_TITAN = [
	Vector2i(0,0),                                                             Vector2i(6,0),
	Vector2i(0,1), Vector2i(1,1),                               Vector2i(5,1), Vector2i(6,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2), Vector2i(6,2),
	Vector2i(0,3), Vector2i(1,3),                               Vector2i(5,3), Vector2i(6,3),
	Vector2i(0,4),                                                             Vector2i(6,4),
]

# 12 - 毒雾蘑菇 (蘑菇形, 5×5, 15格)
const SHAPE_MUSHROOM = [
	               Vector2i(1,0), Vector2i(2,0), Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	                              Vector2i(2,3),
	               Vector2i(1,4), Vector2i(2,4), Vector2i(3,4),
]

# 13 - 水晶守卫 (菱刺, 5×5, 16格)
const SHAPE_CRYSTAL = [
	               Vector2i(1,0),                Vector2i(3,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3), Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	                              Vector2i(2,4),
]

# 14 - 暗影刺客 (沙漏, 5×5, 15格)
const SHAPE_ASSASSIN = [
	Vector2i(0,0),                                              Vector2i(4,0),
	Vector2i(0,1), Vector2i(1,1),               Vector2i(3,1), Vector2i(4,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2),
	Vector2i(0,3), Vector2i(1,3),               Vector2i(3,3), Vector2i(4,3),
	Vector2i(0,4),                                              Vector2i(4,4),
]

# 15 - 火焰凤凰 (V翼, 7×5, 15格)
const SHAPE_PHOENIX = [
	Vector2i(0,0),                                                             Vector2i(6,0),
	Vector2i(0,1), Vector2i(1,1),                               Vector2i(5,1), Vector2i(6,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2),
	                              Vector2i(2,3), Vector2i(3,3), Vector2i(4,3),
	                                             Vector2i(3,4),
]

# 16 - 死灵巫王 (叠层, 6×5, 16格)
const SHAPE_LICH = [
	               Vector2i(1,0), Vector2i(2,0), Vector2i(3,0), Vector2i(4,0),
	                              Vector2i(2,1), Vector2i(3,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	                              Vector2i(2,3), Vector2i(3,3),
	               Vector2i(1,4), Vector2i(2,4), Vector2i(3,4), Vector2i(4,4),
]

# 17 - 虚空行者 (星形, 5×5, 16格)
const SHAPE_VOID = [
	Vector2i(0,0),                Vector2i(2,0),                Vector2i(4,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1),
	Vector2i(0,2), Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3),
	Vector2i(0,4),                                              Vector2i(4,4),
]

# 18 - 风暴巨鹰 (宽翼, 8×4, 20格)
const SHAPE_EAGLE = [
	Vector2i(0,0),                Vector2i(3,0), Vector2i(4,0),                Vector2i(7,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1), Vector2i(6,1), Vector2i(7,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2), Vector2i(6,2),
	                                             Vector2i(3,3), Vector2i(4,3),
]

# 19 - 混沌领主 (堡垒, 7×5, 19格)
const SHAPE_CHAOS = [
	Vector2i(0,0),                Vector2i(3,0),                               Vector2i(6,0),
	               Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1),
	                              Vector2i(2,2), Vector2i(3,2), Vector2i(4,2),
	               Vector2i(1,3), Vector2i(2,3), Vector2i(3,3), Vector2i(4,3), Vector2i(5,3),
	Vector2i(0,4),                Vector2i(3,4),                               Vector2i(6,4),
]

# 20 - 终焉之龙 (古龙, 8×4, 22格)
const SHAPE_ENDDRAGON = [
	               Vector2i(1,0), Vector2i(2,0),                Vector2i(5,0), Vector2i(6,0),
	Vector2i(0,1), Vector2i(1,1), Vector2i(2,1), Vector2i(3,1), Vector2i(4,1), Vector2i(5,1), Vector2i(6,1), Vector2i(7,1),
	               Vector2i(1,2), Vector2i(2,2), Vector2i(3,2), Vector2i(4,2), Vector2i(5,2), Vector2i(6,2),
	                              Vector2i(2,3), Vector2i(3,3), Vector2i(4,3), Vector2i(5,3),
]

# ============================================================
#  20 关卡定义 — 每关独立配置
#  bomb_count  = 探索区地雷数量 (密度 15%-20%)
#  base_clicks = 基础探索点击次数 (周期再叠加)
# ============================================================
const LEVELS = [
	# ── 第一幕 · 阴暗地牢 (1-5) ──────────────────────
	{
		"id": 1, "name": "石牢",
		"boss_name": "石像鬼", "boss_shape": "GARGOYLE",
		"subtitle": "冰冷的石墙间回荡着低沉的呻吟…",
		"color": Color(0.60, 0.65, 0.70),
		"tile_weights": { "WEAK": 0.35, "ARMOR": 0.05, "ABSORB": 0.02, "NORMAL": 0.58 },
		"bomb_count": 6, "base_clicks": 8,
		"turn_duration": 50.0, "boss_attack": 3, "boss_move_interval": 70.0,
		"placement_cols": 8, "placement_rows": 5,
		"mine_cols": 8, "mine_rows": 4,
	},
	{
		"id": 2, "name": "暗影长廊",
		"boss_name": "影蛛", "boss_shape": "SPIDER",
		"subtitle": "影子在摇曳的火光中扭曲蠕动…",
		"color": Color(0.50, 0.35, 0.65),
		"tile_weights": { "WEAK": 0.30, "ARMOR": 0.10, "ABSORB": 0.05, "NORMAL": 0.55 },
		"bomb_count": 7, "base_clicks": 9,
		"turn_duration": 48.0, "boss_attack": 3, "boss_move_interval": 65.0,
		"placement_cols": 9, "placement_rows": 5,
		"mine_cols": 9, "mine_rows": 4,
	},
	{
		"id": 3, "name": "熔岩洞窟",
		"boss_name": "熔岩巨蛇", "boss_shape": "SERPENT",
		"subtitle": "脚下的岩浆发出炙热的光芒…",
		"color": Color(0.95, 0.45, 0.15),
		"tile_weights": { "WEAK": 0.28, "ARMOR": 0.12, "ABSORB": 0.05, "NORMAL": 0.55 },
		"bomb_count": 8, "base_clicks": 10,
		"turn_duration": 46.0, "boss_attack": 4, "boss_move_interval": 62.0,
		"placement_cols": 9, "placement_rows": 6,
		"mine_cols": 9, "mine_rows": 5,
	},
	{
		"id": 4, "name": "骸骨密室",
		"boss_name": "骸骨巨人", "boss_shape": "GIANT",
		"subtitle": "堆积如山的白骨中传来咔嚓声…",
		"color": Color(0.85, 0.82, 0.70),
		"tile_weights": { "WEAK": 0.25, "ARMOR": 0.15, "ABSORB": 0.05, "NORMAL": 0.55 },
		"bomb_count": 10, "base_clicks": 11,
		"turn_duration": 44.0, "boss_attack": 4, "boss_move_interval": 60.0,
		"placement_cols": 10, "placement_rows": 6,
		"mine_cols": 10, "mine_rows": 5,
	},
	{
		"id": 5, "name": "深渊王座",
		"boss_name": "深渊魔王", "boss_shape": "DEMON",
		"subtitle": "黑暗的尽头，一双猩红的眼睛注视着你…",
		"color": Color(0.90, 0.12, 0.08),
		"tile_weights": { "WEAK": 0.22, "ARMOR": 0.18, "ABSORB": 0.08, "NORMAL": 0.52 },
		"bomb_count": 10, "base_clicks": 12,
		"turn_duration": 42.0, "boss_attack": 5, "boss_move_interval": 58.0,
		"placement_cols": 11, "placement_rows": 6,
		"mine_cols": 11, "mine_rows": 5,
	},
	# ── 第二幕 · 异域荒原 (6-10) ─────────────────────
	{
		"id": 6, "name": "霜寒冰殿",
		"boss_name": "冰霜女巫", "boss_shape": "WITCH",
		"subtitle": "寒冷刺骨的冰晶在空气中飞舞…",
		"color": Color(0.65, 0.82, 0.95),
		"tile_weights": { "WEAK": 0.20, "ARMOR": 0.18, "ABSORB": 0.10, "NORMAL": 0.52 },
		"bomb_count": 10, "base_clicks": 12,
		"turn_duration": 40.0, "boss_attack": 5, "boss_move_interval": 55.0,
		"placement_cols": 11, "placement_rows": 7,
		"mine_cols": 11, "mine_rows": 5,
	},
	{
		"id": 7, "name": "风蚀峡谷",
		"boss_name": "暗夜飞龙", "boss_shape": "WYVERN",
		"subtitle": "峡谷中呼啸的狂风裹挟着龙的咆哮…",
		"color": Color(0.18, 0.45, 0.40),
		"tile_weights": { "WEAK": 0.18, "ARMOR": 0.20, "ABSORB": 0.10, "NORMAL": 0.52 },
		"bomb_count": 12, "base_clicks": 13,
		"turn_duration": 38.0, "boss_attack": 6, "boss_move_interval": 52.0,
		"placement_cols": 12, "placement_rows": 7,
		"mine_cols": 12, "mine_rows": 5,
	},
	{
		"id": 8, "name": "沉船墓地",
		"boss_name": "深海巨怪", "boss_shape": "KRAKEN",
		"subtitle": "锈蚀的船骸中传来深海的低语…",
		"color": Color(0.12, 0.25, 0.45),
		"tile_weights": { "WEAK": 0.18, "ARMOR": 0.15, "ABSORB": 0.15, "NORMAL": 0.52 },
		"bomb_count": 11, "base_clicks": 14,
		"turn_duration": 38.0, "boss_attack": 6, "boss_move_interval": 50.0,
		"placement_cols": 12, "placement_rows": 7,
		"mine_cols": 12, "mine_rows": 6,
	},
	{
		"id": 9, "name": "钢铁堡垒",
		"boss_name": "铁甲傀儡", "boss_shape": "GOLEM",
		"subtitle": "齿轮与蒸汽的轰鸣填满了整座堡垒…",
		"color": Color(0.55, 0.58, 0.62),
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.25, "ABSORB": 0.10, "NORMAL": 0.50 },
		"bomb_count": 13, "base_clicks": 15,
		"turn_duration": 36.0, "boss_attack": 7, "boss_move_interval": 48.0,
		"placement_cols": 13, "placement_rows": 7,
		"mine_cols": 13, "mine_rows": 6,
	},
	{
		"id": 10, "name": "血月荒野",
		"boss_name": "血月狼王", "boss_shape": "WOLF",
		"subtitle": "血色月光下，狼群的嚎叫此起彼伏…",
		"color": Color(0.55, 0.10, 0.12),
		"tile_weights": { "WEAK": 0.15, "ARMOR": 0.20, "ABSORB": 0.12, "NORMAL": 0.53 },
		"bomb_count": 14, "base_clicks": 16,
		"turn_duration": 35.0, "boss_attack": 7, "boss_move_interval": 45.0,
		"placement_cols": 13, "placement_rows": 7,
		"mine_cols": 13, "mine_rows": 6,
	},
	# ── 第三幕 · 魔域纵深 (11-15) ────────────────────
	{
		"id": 11, "name": "雷鸣峰顶",
		"boss_name": "雷霆泰坦", "boss_shape": "TITAN",
		"subtitle": "雷电劈裂山巅，巨影在云层中若隐若现…",
		"color": Color(0.35, 0.50, 0.75),
		"tile_weights": { "WEAK": 0.12, "ARMOR": 0.22, "ABSORB": 0.13, "NORMAL": 0.53 },
		"bomb_count": 15, "base_clicks": 17,
		"turn_duration": 34.0, "boss_attack": 8, "boss_move_interval": 42.0,
		"placement_cols": 14, "placement_rows": 8,
		"mine_cols": 14, "mine_rows": 6,
	},
	{
		"id": 12, "name": "毒雾森林",
		"boss_name": "毒雾蘑菇", "boss_shape": "MUSHROOM",
		"subtitle": "有毒的孢子弥漫在腐朽的林间…",
		"color": Color(0.40, 0.55, 0.20),
		"tile_weights": { "WEAK": 0.12, "ARMOR": 0.18, "ABSORB": 0.18, "NORMAL": 0.52 },
		"bomb_count": 14, "base_clicks": 17,
		"turn_duration": 34.0, "boss_attack": 8, "boss_move_interval": 42.0,
		"placement_cols": 14, "placement_rows": 8,
		"mine_cols": 14, "mine_rows": 6,
	},
	{
		"id": 13, "name": "水晶矿脉",
		"boss_name": "水晶守卫", "boss_shape": "CRYSTAL",
		"subtitle": "水晶折射的光芒令人目眩神迷…",
		"color": Color(0.20, 0.65, 0.70),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.28, "ABSORB": 0.12, "NORMAL": 0.50 },
		"bomb_count": 15, "base_clicks": 18,
		"turn_duration": 32.0, "boss_attack": 9, "boss_move_interval": 40.0,
		"placement_cols": 15, "placement_rows": 8,
		"mine_cols": 15, "mine_rows": 6,
	},
	{
		"id": 14, "name": "幽暗密道",
		"boss_name": "暗影刺客", "boss_shape": "ASSASSIN",
		"subtitle": "寂静的暗道中，只有匕首划过空气的风声…",
		"color": Color(0.28, 0.25, 0.30),
		"tile_weights": { "WEAK": 0.12, "ARMOR": 0.22, "ABSORB": 0.16, "NORMAL": 0.50 },
		"bomb_count": 16, "base_clicks": 19,
		"turn_duration": 30.0, "boss_attack": 9, "boss_move_interval": 38.0,
		"placement_cols": 15, "placement_rows": 8,
		"mine_cols": 15, "mine_rows": 7,
	},
	{
		"id": 15, "name": "烈焰神殿",
		"boss_name": "火焰凤凰", "boss_shape": "PHOENIX",
		"subtitle": "永不熄灭的烈焰中涅槃之鸟振翅高飞…",
		"color": Color(0.95, 0.70, 0.15),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.20, "ABSORB": 0.15, "NORMAL": 0.55 },
		"bomb_count": 17, "base_clicks": 20,
		"turn_duration": 30.0, "boss_attack": 10, "boss_move_interval": 36.0,
		"placement_cols": 16, "placement_rows": 8,
		"mine_cols": 16, "mine_rows": 7,
	},
	# ── 第四幕 · 死域深层 (16-20) ────────────────────
	{
		"id": 16, "name": "亡者陵墓",
		"boss_name": "死灵巫王", "boss_shape": "LICH",
		"subtitle": "亡灵的哀嚎从石棺的裂缝中渗出…",
		"color": Color(0.30, 0.45, 0.25),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.28, "ABSORB": 0.15, "NORMAL": 0.49 },
		"bomb_count": 17, "base_clicks": 21,
		"turn_duration": 28.0, "boss_attack": 10, "boss_move_interval": 34.0,
		"placement_cols": 16, "placement_rows": 9,
		"mine_cols": 16, "mine_rows": 7,
	},
	{
		"id": 17, "name": "虚空裂隙",
		"boss_name": "虚空行者", "boss_shape": "VOID",
		"subtitle": "现实的边界在这里崩塌，虚空蔓延…",
		"color": Color(0.35, 0.15, 0.50),
		"tile_weights": { "WEAK": 0.10, "ARMOR": 0.25, "ABSORB": 0.18, "NORMAL": 0.47 },
		"bomb_count": 18, "base_clicks": 22,
		"turn_duration": 28.0, "boss_attack": 11, "boss_move_interval": 32.0,
		"placement_cols": 17, "placement_rows": 9,
		"mine_cols": 17, "mine_rows": 7,
	},
	{
		"id": 18, "name": "风暴之巅",
		"boss_name": "风暴巨鹰", "boss_shape": "EAGLE",
		"subtitle": "暴风与雷霆在峰顶编织出死亡之翼…",
		"color": Color(0.50, 0.55, 0.65),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.25, "ABSORB": 0.15, "NORMAL": 0.52 },
		"bomb_count": 19, "base_clicks": 23,
		"turn_duration": 26.0, "boss_attack": 12, "boss_move_interval": 30.0,
		"placement_cols": 18, "placement_rows": 9,
		"mine_cols": 17, "mine_rows": 7,
	},
	{
		"id": 19, "name": "混沌深渊",
		"boss_name": "混沌领主", "boss_shape": "CHAOS",
		"subtitle": "混沌的力量扭曲了一切秩序与形态…",
		"color": Color(0.60, 0.08, 0.10),
		"tile_weights": { "WEAK": 0.08, "ARMOR": 0.30, "ABSORB": 0.15, "NORMAL": 0.47 },
		"bomb_count": 20, "base_clicks": 24,
		"turn_duration": 25.0, "boss_attack": 13, "boss_move_interval": 28.0,
		"placement_cols": 18, "placement_rows": 10,
		"mine_cols": 18, "mine_rows": 7,
	},
	{
		"id": 20, "name": "终焉之地",
		"boss_name": "终焉之龙", "boss_shape": "ENDDRAGON",
		"subtitle": "万物终结之处，古龙在此沉睡万年…",
		"color": Color(0.55, 0.45, 0.15),
		"tile_weights": { "WEAK": 0.06, "ARMOR": 0.30, "ABSORB": 0.18, "NORMAL": 0.46 },
		"bomb_count": 22, "base_clicks": 25,
		"turn_duration": 24.0, "boss_attack": 14, "boss_move_interval": 26.0,
		"placement_cols": 19, "placement_rows": 10,
		"mine_cols": 18, "mine_rows": 7,
	},
]

# ============================================================
#  映射表
# ============================================================
const SHAPE_MAP = {
	"GARGOYLE": SHAPE_GARGOYLE, "SPIDER": SHAPE_SPIDER,
	"SERPENT": SHAPE_SERPENT, "GIANT": SHAPE_GIANT, "DEMON": SHAPE_DEMON,
	"WITCH": SHAPE_WITCH, "WYVERN": SHAPE_WYVERN, "KRAKEN": SHAPE_KRAKEN,
	"GOLEM": SHAPE_GOLEM, "WOLF": SHAPE_WOLF, "TITAN": SHAPE_TITAN,
	"MUSHROOM": SHAPE_MUSHROOM, "CRYSTAL": SHAPE_CRYSTAL,
	"ASSASSIN": SHAPE_ASSASSIN, "PHOENIX": SHAPE_PHOENIX,
	"LICH": SHAPE_LICH, "VOID": SHAPE_VOID, "EAGLE": SHAPE_EAGLE,
	"CHAOS": SHAPE_CHAOS, "ENDDRAGON": SHAPE_ENDDRAGON,
}

const BOSS_TEXTURE_MAP = {
	"GARGOYLE":  "res://assets/sprites/boss/boss_gargoyle.png",
	"SPIDER":    "res://assets/sprites/boss/boss_spider.png",
	"SERPENT":   "res://assets/sprites/boss/boss_serpent.png",
	"GIANT":     "res://assets/sprites/boss/boss_giant.png",
	"DEMON":     "res://assets/sprites/boss/boss_demon.png",
	"WITCH":     "res://assets/sprites/boss/boss_witch.png",
	"WYVERN":    "res://assets/sprites/boss/boss_wyvern.png",
	"KRAKEN":    "res://assets/sprites/boss/boss_kraken.png",
	"GOLEM":     "res://assets/sprites/boss/boss_golem.png",
	"WOLF":      "res://assets/sprites/boss/boss_wolf.png",
	"TITAN":     "res://assets/sprites/boss/boss_titan.png",
	"MUSHROOM":  "res://assets/sprites/boss/boss_mushroom.png",
	"CRYSTAL":   "res://assets/sprites/boss/boss_crystal.png",
	"ASSASSIN":  "res://assets/sprites/boss/boss_assassin.png",
	"PHOENIX":   "res://assets/sprites/boss/boss_phoenix.png",
	"LICH":      "res://assets/sprites/boss/boss_lich.png",
	"VOID":      "res://assets/sprites/boss/boss_void.png",
	"EAGLE":     "res://assets/sprites/boss/boss_eagle.png",
	"CHAOS":     "res://assets/sprites/boss/boss_chaos.png",
	"ENDDRAGON": "res://assets/sprites/boss/boss_enddragon.png",
}

# ============================================================
#  查询接口  —  20关循环, 5周期 = 100层
# ============================================================

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

const BACKGROUND_PATHS: Array = [
	"res://assets/sprites/bg/bg_stone_prison.png",     # floor 1
	"res://assets/sprites/bg/bg_bone_chamber.png",     # floor 2
	"res://assets/sprites/bg/bg_lava_cave.png",        # floor 3
	"res://assets/sprites/bg/bg_ghost_wreck.png",      # floor 4
	"res://assets/sprites/bg/bg_crystal_cavern.png",   # floor 5
	"res://assets/sprites/bg/bg_ancient_ruins.png",    # floor 6
	"res://assets/sprites/bg/bg_shadow_hall.png",      # floor 7
	"res://assets/sprites/bg/bg_frost_altar.png",      # floor 8
	"res://assets/sprites/bg/bg_plague_swamp.png",     # floor 9
	"res://assets/sprites/bg/bg_mechanical_fort.png",  # floor 10
	"res://assets/sprites/bg/bg_nightmare_maze.png",   # floor 11
	"res://assets/sprites/bg/bg_corrupted_temple.png", # floor 12
	"res://assets/sprites/bg/bg_void_rift.png",        # floor 13
	"res://assets/sprites/bg/bg_thunder_peak.png",     # floor 14
	"res://assets/sprites/bg/bg_shadow_realm.png",     # floor 15
	"res://assets/sprites/bg/bg_chaos_forge.png",      # floor 16
	"res://assets/sprites/bg/bg_void_palace.png",      # floor 17
	"res://assets/sprites/bg/bg_divine_sanctum.png",   # floor 18
	"res://assets/sprites/bg/bg_abyss_throne.png",     # floor 19
	"res://assets/sprites/bg/bg_final_sanctum.png",    # floor 20
]

func get_background_texture_path(floor_number: int) -> String:
	var idx = ((floor_number - 1) % BACKGROUND_PATHS.size())
	return BACKGROUND_PATHS[idx]

func get_cell_size(floor_number: int) -> int:
	var p_cols = get_placement_cols(floor_number)
	var p_rows = get_placement_rows(floor_number)
	var m_cols = get_mine_cols(floor_number)
	var m_rows = get_mine_rows(floor_number)
	var max_cols = max(p_cols, m_cols)
	var size_by_w = int(1760.0 / max_cols)
	var size_by_h = int(880.0 / (p_rows + m_rows))
	return min(size_by_w, size_by_h)

# ── 难度参数（含周期递增）──

func get_bomb_count(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["bomb_count"] + cycle * 2

func get_turn_duration(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return maxf(level["turn_duration"] - cycle * 3.0, 15.0)

func get_boss_attack(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["boss_attack"] + cycle * 3

func get_boss_move_interval(floor_number: int) -> float:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return maxf(level["boss_move_interval"] - cycle * 5.0, 18.0)

func get_tile_weights(floor_number: int) -> Dictionary:
	return get_level(floor_number)["tile_weights"]

func get_hp_multiplier(floor_number: int) -> float:
	var cycle = get_cycle(floor_number)
	return 1.0 + cycle * 0.5

func get_max_clicks(floor_number: int) -> int:
	var level = get_level(floor_number)
	var cycle = get_cycle(floor_number)
	return level["base_clicks"] + cycle * 3
