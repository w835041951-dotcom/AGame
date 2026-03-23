"""
Generate an isolated late-game level pack for floors 201-300.

Outputs:
- scripts/core/LevelPack201_300.gd
- assets/sprites/boss/boss_pack_201_<name>.png
- assets/sprites/boss/boss_pack_201_300_preview.png

This keeps the 201-300 content separate from the base 1-200 setup so it can
coexist with other work in progress.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

import gen_boss as base_boss


ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PACK_PATH = os.path.join(ROOT, "scripts", "core", "LevelPack201_300.gd")
BOSS_DIR = os.path.join(ROOT, "assets", "sprites", "boss")
BG_DIR = os.path.join(ROOT, "assets", "sprites", "bg")
STORY_DIR = os.path.join(ROOT, "assets", "sprites", "story")
PREVIEW_PATH = os.path.join(BOSS_DIR, "boss_pack_201_300_preview.png")


Shape = Sequence[Tuple[int, int]]


@dataclass(frozen=True)
class Theme:
    code: str
    zone: str
    intro: str
    outro: str
    story_line: str
    color: Tuple[int, int, int]


@dataclass(frozen=True)
class BossSpec:
    code: str
    boss_name: str
    arena_name: str
    hint: str
    style: str
    body: Tuple[int, int, int]
    dark: Tuple[int, int, int]
    crack: Tuple[int, int, int]
    glow: Tuple[int, int, int]
    eye: Tuple[int, int, int]
    rune: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    shape: Shape


@dataclass(frozen=True)
class BossVariant:
    code: str
    act_index: int
    source: BossSpec
    shape: Shape


THEMES: List[Theme] = [
    Theme("embers", "余烬前哨", "炽灰顺着墙缝呼吸，", "你必须在火势合围前拆开节奏。", "残火沿着旧城骨架蔓延，晚到一步，整条推进线都会被烧穿。", (214, 104, 54)),
    Theme("frost", "霜蚀回廊", "霜纹把每一步都冻成回声，", "稍慢半拍，整块战线就会塌陷。", "霜蚀在高墙与地砖之间结出断层，任何迟疑都会让安全区瞬间碎掉。", (112, 188, 228)),
    Theme("tide", "潮墓祭港", "潮水敲击墓碑般的船壳，", "局面会在涨落之间突然翻面。", "涨潮时连墓碑都像在移动，只有提前算好的爆破顺序才压得住浪。", (58, 132, 166)),
    Theme("brass", "黄铜天阙", "齿轮与钟摆在高空啮合，", "任何贪刀都会被机关放大成失误。", "黄铜机关把每一次多余点击都翻译成惩罚，这一幕只奖励极干净的节奏。", (202, 164, 82)),
    Theme("starvoid", "终焉星渊", "星尘像余火一样坠落，", "这里只奖励最干净的推演与爆破。", "星渊没有真正的地平线，所有判断都要在坠落之前完成。", (176, 128, 222)),
]


BOSSES: List[BossSpec] = [
    BossSpec(
        "OBSIDIAN_SENTINEL", "黑曜哨兵", "裂火观测井", "厚甲很多，但中心链路一旦打开就会连续崩落。", "tank",
        (66, 72, 84), (24, 26, 34), (34, 38, 44), (255, 108, 64), (255, 180, 98), (215, 92, 48), (255, 140, 86),
        [(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(2,4)],
    ),
    BossSpec(
        "LANTERN_EEL", "灯笼深鳗", "流焰输水脉", "它善于把弱点藏在弯折处，横向爆破比正面硬推更值。", "rush",
        (54, 82, 98), (18, 28, 36), (34, 48, 56), (72, 220, 255), (152, 250, 255), (50, 188, 210), (116, 236, 255),
        [(0,0),(1,0),(2,0),(3,0),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(1,3),(4,3),(0,4),(1,4),(2,4),(3,4)],
    ),
    BossSpec(
        "THORN_RELIQUARY", "荆棘圣龛", "灰枝圣坛", "外圈脆，内圈硬，分段拆比集中一波更稳。", "balanced",
        (74, 92, 60), (24, 30, 20), (38, 48, 30), (122, 238, 110), (198, 255, 168), (96, 216, 84), (168, 242, 132),
        [(1,0),(3,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(3,2),(5,2),(1,3),(2,3),(3,3),(4,3),(2,4),(3,4)],
    ),
    BossSpec(
        "FURNACE_RAM", "熔炉攻城兽", "煤渣冲角廊", "前额最硬，但冲角后的躯干是典型的连爆走廊。", "tank",
        (102, 66, 38), (38, 18, 10), (58, 30, 16), (255, 138, 36), (255, 205, 104), (230, 102, 26), (255, 162, 58),
        [(0,0),(1,0),(4,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(2,3),(3,3),(4,3)],
    ),
    BossSpec(
        "MIRROR_MOTH", "镜翅蛾后", "折光礼拜堂", "翅面格子多但不耐久，适合从两侧同步削。", "artillery",
        (108, 92, 132), (34, 24, 42), (56, 42, 70), (224, 164, 255), (255, 214, 255), (198, 128, 240), (244, 194, 255),
        [(0,0),(5,0),(0,1),(1,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(4,3),(2,4),(3,4)],
    ),
    BossSpec(
        "PLAGUE_ORRERY", "疫蚀星仪", "腐蚀测天环", "会拖长战线，优先切掉中心齿轮能减少翻车点。", "leech",
        (92, 114, 72), (28, 36, 24), (46, 58, 36), (184, 255, 104), (228, 255, 170), (148, 228, 78), (210, 255, 126),
        [(1,0),(2,0),(3,0),(4,0),(0,1),(5,1),(0,2),(2,2),(3,2),(5,2),(0,3),(2,3),(3,3),(5,3),(0,4),(5,4),(1,5),(2,5),(3,5),(4,5)],
    ),
    BossSpec(
        "TIDE_JUDGE", "潮审判官", "沉碑系泊区", "头重脚轻，先拆两翼能让后续落点更宽。", "balanced",
        (70, 96, 112), (22, 30, 38), (38, 52, 64), (90, 214, 255), (170, 242, 255), (76, 182, 230), (124, 230, 255),
        [(2,0),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),(2,3),(1,4),(2,4),(3,4),(0,5),(4,5)],
    ),
    BossSpec(
        "BRASS_SCORCHER", "黄铜灼炮", "回火炮闸", "四角会卡手，提前把角位清成回弹通道很关键。", "artillery",
        (122, 94, 48), (46, 30, 12), (70, 48, 22), (255, 196, 72), (255, 232, 146), (224, 172, 58), (255, 214, 102),
        [(0,0),(1,0),(2,0),(3,0),(0,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(1,3),(4,3),(0,4),(1,4),(4,4),(5,4)],
    ),
    BossSpec(
        "VEIN_GOLEM", "血脉石魔", "温层心室", "血管状连接很多，链爆收益高，但别让吸收格拖住。", "leech",
        (126, 64, 72), (42, 18, 24), (62, 30, 38), (255, 92, 122), (255, 162, 182), (228, 74, 108), (255, 128, 154),
        [(0,0),(1,0),(3,0),(4,0),(0,1),(1,1),(2,1),(3,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(1,4),(3,4)],
    ),
    BossSpec(
        "SHRINE_DEVOURER", "祭坛吞噬者", "空槽祷室", "嘴部两侧薄，打穿后中心会很快失衡。", "rush",
        (88, 78, 52), (28, 22, 14), (44, 36, 22), (248, 214, 92), (255, 246, 162), (220, 184, 76), (255, 226, 122),
        [(1,0),(2,0),(3,0),(4,0),(0,1),(1,1),(4,1),(5,1),(0,2),(2,2),(3,2),(5,2),(1,3),(2,3),(3,3),(4,3),(1,4),(4,4)],
    ),
    BossSpec(
        "GLACIER_BELL", "冰川钟躯", "断霜鸣廊", "下盘稳定但腿位很薄，破腿后节奏会突然轻很多。", "tank",
        (146, 180, 198), (44, 58, 68), (78, 94, 106), (168, 242, 255), (224, 255, 255), (126, 220, 250), (194, 252, 255),
        [(2,0),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(1,4),(2,4),(3,4),(1,5),(3,5)],
    ),
    BossSpec(
        "CROWN_WRAITH", "冠冕幽魂", "暮冕议事厅", "冠尖是假压迫，真正的危险在中段吸收链。", "leech",
        (82, 70, 112), (24, 20, 34), (40, 34, 54), (186, 122, 255), (234, 190, 255), (160, 92, 234), (210, 154, 255),
        [(0,0),(2,0),(3,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(4,2),(1,3),(2,3),(3,3),(4,3),(2,4),(3,4)],
    ),
    BossSpec(
        "ROOT_COLOSSUS", "根须巨像", "盘根温床", "它的边角像假目标，优先打断中央主根更划算。", "balanced",
        (92, 86, 58), (28, 24, 14), (44, 38, 22), (194, 238, 96), (234, 255, 170), (160, 214, 76), (218, 248, 120),
        [(0,0),(2,0),(3,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(0,3),(2,3),(3,3),(5,3),(0,4),(1,4),(4,4),(5,4),(1,5),(2,5),(3,5),(4,5)],
    ),
    BossSpec(
        "COMET_STAG", "彗角天鹿", "落星折返庭", "上角华丽但脆，炸出缺口后请立刻转火躯干。", "artillery",
        (112, 120, 144), (32, 38, 50), (52, 60, 76), (255, 228, 104), (255, 255, 174), (236, 202, 74), (255, 242, 136),
        [(1,0),(4,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(2,3),(3,3),(1,4),(2,4),(3,4),(4,4),(0,5),(5,5)],
    ),
    BossSpec(
        "MAW_ENGINE", "巨颚机骸", "废压传送井", "左右咬合槽很适合散射与十字覆盖。", "rush",
        (104, 112, 118), (30, 34, 40), (46, 52, 60), (255, 150, 96), (255, 212, 156), (232, 124, 72), (255, 176, 126),
        [(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(5,1),(6,1),(0,2),(2,2),(3,2),(4,2),(6,2),(1,3),(2,3),(3,3),(4,3),(5,3),(2,4),(4,4)],
    ),
    BossSpec(
        "HARBOR_HYDRA", "港湾九首", "潮鸣锚场", "头很多但颈部都细，别被表面血量骗到。", "balanced",
        (58, 104, 126), (18, 32, 42), (30, 48, 60), (102, 236, 255), (186, 250, 255), (80, 198, 222), (134, 244, 255),
        [(0,0),(2,0),(4,0),(6,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(1,2),(3,2),(5,2),(1,3),(2,3),(3,3),(4,3),(5,3),(2,4),(3,4),(4,4),(1,5),(5,5)],
    ),
    BossSpec(
        "SHARD_SERAPH", "裂片炽天", "玻璃风暴中庭", "翅尖弱、核心硬，最怕你把连锁走廊先铺出来。", "artillery",
        (180, 106, 124), (46, 24, 34), (70, 40, 52), (255, 182, 214), (255, 228, 242), (242, 144, 182), (255, 196, 226),
        [(0,0),(6,0),(0,1),(1,1),(5,1),(6,1),(1,2),(2,2),(3,2),(4,2),(5,2),(2,3),(3,3),(4,3),(1,4),(2,4),(4,4),(5,4),(2,5),(3,5),(4,5)],
    ),
    BossSpec(
        "DUSK_TORTOISE", "昏潮巨龟", "暮潮浮堤", "甲壳很厚，但四肢与尾部一断就会失去压迫线。", "tank",
        (88, 108, 92), (24, 34, 28), (40, 54, 44), (182, 246, 132), (228, 255, 194), (150, 218, 102), (212, 255, 154),
        [(1,0),(2,0),(3,0),(4,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(1,3),(2,3),(3,3),(4,3),(1,4),(4,4),(0,5),(5,5)],
    ),
    BossSpec(
        "ASTER_TITAN", "星棘泰坦", "穹棘断桥", "中心列几乎决定整场节奏，敢切中轴就能拿到先手。", "balanced",
        (112, 92, 144), (30, 22, 42), (52, 38, 66), (214, 156, 255), (248, 212, 255), (188, 120, 244), (228, 176, 255),
        [(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(0,2),(2,2),(3,2),(4,2),(6,2),(1,3),(2,3),(3,3),(4,3),(5,3),(1,4),(3,4),(5,4),(2,5),(3,5),(4,5)],
    ),
    BossSpec(
        "VOID_KRAKEN", "虚潮海妖", "坠星黑潮口", "外圈触腕负责乱局，真正的命门永远在中央深处。", "leech",
        (74, 62, 118), (18, 14, 30), (34, 28, 48), (134, 110, 255), (198, 190, 255), (112, 94, 232), (166, 150, 255),
        [(3,0),(2,1),(3,1),(4,1),(1,2),(2,2),(3,2),(4,2),(5,2),(0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(1,4),(2,4),(3,4),(4,4),(5,4),(0,5),(2,5),(4,5),(6,5),(1,6),(5,6)],
    ),
]


def _boss_dims(shape: Shape) -> Tuple[int, int]:
    width = max(x for x, _ in shape) + 1
    height = max(y for _, y in shape) + 1
    return width, height


def _normalize_shape(shape: Shape) -> List[Tuple[int, int]]:
    points = sorted(set(shape), key=lambda item: (item[1], item[0]))
    min_x = min(x for x, _ in points)
    min_y = min(y for _, y in points)
    return [(x - min_x, y - min_y) for x, y in points]


def _row_spans(shape: Shape) -> Dict[int, Tuple[int, int]]:
    rows: Dict[int, List[int]] = {}
    for x, y in shape:
        rows.setdefault(y, []).append(x)
    return {y: (min(xs), max(xs)) for y, xs in rows.items()}


def _variant_suffix(act_index: int) -> str:
    if act_index == 3:
        return "COLOSSUS"
    if act_index >= 4:
        return "ABYSS"
    return ""


def _build_super_shape(boss: BossSpec, act_index: int, slot: int) -> Shape:
    if act_index < 3:
        return list(boss.shape)

    cells = set(boss.shape)
    rows = _row_spans(cells)
    min_y = min(rows)
    max_y = max(rows)
    center_x = round(sum(x for x, _ in cells) / len(cells))
    lean = -1 if (slot + act_index) % 2 == 0 else 1
    upper_y = min_y + 1 if (min_y + 1) in rows else min_y
    mid_y = min_y + (max_y - min_y) // 2
    lower_y = max_y - 1 if (max_y - 1) in rows else max_y

    def add_points(points: List[Tuple[int, int]]) -> None:
        for point in points:
            cells.add(point)

    if boss.style == "tank":
        left, right = rows.get(upper_y, rows[min_y])
        add_points([
            (left - 1, upper_y),
            (right + 1, upper_y),
            (center_x - 1, max_y + 1),
            (center_x, max_y + 1),
            (center_x + 1, max_y + 1),
            (center_x - lean, min_y - 1),
            (center_x - 2 * lean, min_y),
        ])
    elif boss.style == "rush":
        left, right = rows.get(mid_y, rows[upper_y])
        add_points([
            (right + 1, mid_y - 1),
            (right + 2, mid_y),
            (right + 3, mid_y + 1),
            (left - 1, lower_y),
            (left - 2, max_y),
            (left - 3, max_y + 1),
            (center_x + lean, min_y - 1),
        ])
    elif boss.style == "artillery":
        left, right = rows.get(mid_y, rows[upper_y])
        add_points([
            (left - 1, mid_y - 1),
            (left - 2, mid_y - 1),
            (right + 1, mid_y),
            (right + 2, mid_y),
            (center_x, min_y - 1),
            (center_x + lean, min_y - 2),
            (center_x - lean, max_y + 1),
        ])
    elif boss.style == "leech":
        left, right = rows.get(lower_y, rows[max_y])
        add_points([
            (left - 1, mid_y),
            (right + 1, mid_y - 1),
            (center_x - 1, max_y + 1),
            (center_x + 1, max_y + 1),
            (center_x - 2, max_y + 2),
            (center_x + 2, max_y + 2),
            (center_x + lean, min_y - 1),
        ])
    else:
        left, right = rows.get(mid_y, rows[upper_y])
        add_points([
            (left - 1, mid_y),
            (right + 1, mid_y),
            (center_x, min_y - 1),
            (center_x - lean, max_y + 1),
            (center_x + lean, max_y + 1),
        ])

    if act_index >= 4:
        rows = _row_spans(cells)
        min_y = min(rows)
        max_y = max(rows)
        center_x = round(sum(x for x, _ in cells) / len(cells))
        mid_y = min_y + (max_y - min_y) // 2
        left, right = rows.get(mid_y, rows[min_y])
        add_points([
            (left - 2, mid_y - 1),
            (left - 3, mid_y),
            (right + 2, mid_y),
            (right + 3, mid_y + 1),
            (center_x - lean, min_y - 2),
            (center_x, max_y + 2),
            (center_x + lean, max_y + 3),
        ])

    return _normalize_shape(cells)


def _get_boss_variant(boss: BossSpec, act_index: int, slot: int) -> BossVariant:
    suffix = _variant_suffix(act_index)
    code = boss.code if not suffix else f"{boss.code}_{suffix}"
    shape = _build_super_shape(boss, act_index, slot)
    return BossVariant(code, act_index, boss, shape)


def _collect_variants() -> List[BossVariant]:
    variants: Dict[str, BossVariant] = {}
    for act_index, _theme in enumerate(THEMES):
        for slot, boss in enumerate(BOSSES):
            variant = _get_boss_variant(boss, act_index, slot)
            variants.setdefault(variant.code, variant)
    return list(variants.values())


def _style_weights(style: str, act_index: int) -> Dict[str, float]:
    base_weights = {
        "tank": {"WEAK": 0.12, "ARMOR": 0.30, "ABSORB": 0.10},
        "rush": {"WEAK": 0.18, "ARMOR": 0.18, "ABSORB": 0.12},
        "artillery": {"WEAK": 0.20, "ARMOR": 0.15, "ABSORB": 0.10},
        "leech": {"WEAK": 0.14, "ARMOR": 0.18, "ABSORB": 0.18},
        "balanced": {"WEAK": 0.16, "ARMOR": 0.20, "ABSORB": 0.12},
    }[style].copy()
    base_weights["ARMOR"] = min(0.40, base_weights["ARMOR"] + act_index * 0.02)
    base_weights["ABSORB"] = min(0.24, base_weights["ABSORB"] + act_index * 0.015)
    if style in {"rush", "artillery"}:
        base_weights["WEAK"] = min(0.24, base_weights["WEAK"] + act_index * 0.01)
    normal = max(0.24, 1.0 - base_weights["WEAK"] - base_weights["ARMOR"] - base_weights["ABSORB"])
    total = base_weights["WEAK"] + base_weights["ARMOR"] + base_weights["ABSORB"] + normal
    return {
        "WEAK": round(base_weights["WEAK"] / total, 2),
        "ARMOR": round(base_weights["ARMOR"] / total, 2),
        "ABSORB": round(base_weights["ABSORB"] / total, 2),
        "NORMAL": round(normal / total, 2),
    }


def _blend_color(left: Tuple[int, int, int], right: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    return tuple(int(left[i] * (1.0 - ratio) + right[i] * ratio) for i in range(3))


def _color_text(rgb: Tuple[int, int, int]) -> str:
    return "Color(%.3f, %.3f, %.3f)" % (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def _gd_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _shape_text(shape: Shape) -> str:
    return "\n".join(f"\tVector2i({x},{y})," for x, y in shape)


def _dict_text(data: Dict[str, float]) -> str:
    order = ["WEAK", "ARMOR", "ABSORB", "NORMAL"]
    parts = [f'"{key}": {data[key]:.2f}' for key in order]
    return "{ " + ", ".join(parts) + " }"


def _vertical_gradient(width: int, height: int, top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height), top + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = _blend_color(top, bottom, ratio)
        draw.line([(0, y), (width, y)], fill=color + (255,))
    return image


def _add_glow(image: Image.Image, center: Tuple[int, int], radius: int, color: Tuple[int, int, int], alpha: int) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    for step in range(radius, 0, -8):
        ratio = step / float(radius)
        fill_alpha = int(alpha * (1.0 - ratio) ** 0.65)
        if fill_alpha <= 0:
            continue
        draw.ellipse(
            [center[0] - step, center[1] - step, center[0] + step, center[1] + step],
            fill=color + (fill_alpha,),
        )


def _draw_starfield(image: Image.Image, seed: int, color: Tuple[int, int, int], count: int) -> None:
    rng = __import__("random").Random(seed)
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    for _ in range(count):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        size = 2 if rng.random() > 0.82 else 1
        alpha = rng.randint(120, 240)
        draw.rectangle([x, y, x + size, y + size], fill=color + (alpha,))


def _draw_late_background(theme: Theme, act_index: int) -> Image.Image:
    width = 1920
    height = 1080
    top = _blend_color(theme.color, (10, 10, 16), 0.72)
    bottom = _blend_color(theme.color, (0, 0, 0), 0.82)
    image = _vertical_gradient(width, height, top, bottom)
    draw = ImageDraw.Draw(image, "RGBA")
    horizon = int(height * 0.58)
    accent = _blend_color(theme.color, (240, 220, 190), 0.35)

    if theme.code == "embers":
        _add_glow(image, (width // 2, horizon + 140), 420, theme.color, 120)
        for x in range(0, width, 180):
            tower_h = 180 + (x // 2) % 160
            draw.rectangle([x, horizon - tower_h, x + 110, horizon + 160], fill=(20, 14, 14, 255))
            draw.rectangle([x + 24, horizon - tower_h - 30, x + 82, horizon - tower_h], fill=(26, 18, 18, 255))
        for ember in range(120):
            px = (ember * 163) % width
            py = horizon - (ember * 37) % 520
            size = 2 + ember % 3
            draw.ellipse([px, py, px + size, py + size], fill=(255, 168, 96, 170))
    elif theme.code == "frost":
        _add_glow(image, (width // 2, horizon - 120), 360, accent, 110)
        for x in range(80, width, 220):
            arch_h = 260 + (x // 4) % 120
            draw.rectangle([x, horizon - arch_h, x + 44, horizon + 170], fill=(24, 36, 50, 255))
            draw.rectangle([x + 124, horizon - arch_h, x + 168, horizon + 170], fill=(24, 36, 50, 255))
            draw.arc([x - 20, horizon - arch_h - 20, x + 188, horizon - arch_h + 120], 180, 360, fill=(120, 180, 220, 160), width=8)
        for shard in range(40):
            px = 60 + shard * 46
            py = horizon + 100 + (shard % 4) * 30
            draw.polygon([(px, py), (px + 18, py - 70), (px + 32, py)], fill=(150, 210, 255, 120))
    elif theme.code == "tide":
        _add_glow(image, (width // 2, 180), (280), accent, 90)
        draw.rectangle([0, horizon + 70, width, height], fill=(12, 26, 36, 255))
        for x in range(100, width, 230):
            mast_h = 210 + (x // 5) % 140
            draw.line([(x, horizon - mast_h), (x, horizon + 120)], fill=(18, 24, 28, 255), width=8)
            draw.polygon([(x, horizon - mast_h + 20), (x + 90, horizon - mast_h + 70), (x, horizon - mast_h + 120)], fill=(24, 36, 42, 220))
        for wave in range(8):
            y = horizon + 80 + wave * 26
            draw.arc([-120, y - 20, width + 120, y + 80], 0, 180, fill=(90, 180, 210, 90), width=6)
    elif theme.code == "brass":
        _add_glow(image, (width // 2, 240), 320, accent, 100)
        for x in range(120, width, 260):
            tower_h = 240 + (x // 9) % 180
            draw.rectangle([x, horizon - tower_h, x + 84, horizon + 140], fill=(26, 20, 12, 255))
            draw.rectangle([x + 24, horizon - tower_h - 70, x + 60, horizon - tower_h], fill=(34, 24, 12, 255))
            gear_y = horizon - tower_h // 2
            draw.ellipse([x - 44, gear_y - 44, x + 44, gear_y + 44], outline=(220, 180, 100, 120), width=8)
            draw.ellipse([x + 50, gear_y + 40, x + 122, gear_y + 112], outline=(220, 180, 100, 100), width=6)
    else:
        _draw_starfield(image, 2200 + act_index, (230, 220, 255), 180)
        _add_glow(image, (width // 2, horizon - 160), 420, theme.color, 115)
        for x in range(0, width, 240):
            draw.polygon(
                [(x + 60, horizon + 120), (x + 120, horizon - 180), (x + 180, horizon + 120)],
                fill=(18, 12, 26, 255),
            )
        for arc in range(4):
            radius = 220 + arc * 90
            draw.arc([width // 2 - radius, 60, width // 2 + radius, 60 + radius], 200, 340, fill=(160, 120, 220, 90), width=5)

    draw.rectangle([0, horizon + 120, width, height], fill=(8, 8, 12, 150))
    return image


def _draw_story_scene(theme: Theme, act_index: int) -> Image.Image:
    width = 1600
    height = 900
    image = _vertical_gradient(width, height, _blend_color(theme.color, (12, 12, 16), 0.75), _blend_color(theme.color, (0, 0, 0), 0.88))
    draw = ImageDraw.Draw(image, "RGBA")
    center = (width // 2, height // 2 + 40)
    accent = _blend_color(theme.color, (255, 236, 210), 0.4)
    _add_glow(image, (center[0], center[1] - 120), 260, accent, 110)

    draw.rectangle([center[0] - 260, center[1] + 120, center[0] + 260, height], fill=(12, 12, 16, 220))

    if theme.code == "embers":
        draw.polygon([(center[0] - 220, center[1] + 140), (center[0] - 80, center[1] - 180), (center[0] + 10, center[1] + 140)], fill=(28, 20, 18, 255))
        draw.polygon([(center[0] + 40, center[1] + 140), (center[0] + 160, center[1] - 220), (center[0] + 260, center[1] + 140)], fill=(28, 20, 18, 255))
        for ember in range(80):
            px = 260 + (ember * 67) % 1080
            py = 120 + (ember * 43) % 520
            draw.ellipse([px, py, px + 4, py + 4], fill=(255, 186, 110, 160))
    elif theme.code == "frost":
        for pillar_x in [center[0] - 210, center[0] - 70, center[0] + 70, center[0] + 210]:
            draw.rectangle([pillar_x - 26, center[1] - 220, pillar_x + 26, center[1] + 140], fill=(26, 40, 54, 255))
            draw.polygon([(pillar_x - 30, center[1] + 140), (pillar_x, center[1] - 260), (pillar_x + 30, center[1] + 140)], fill=(158, 220, 255, 120))
    elif theme.code == "tide":
        for mast_x in [center[0] - 220, center[0] - 60, center[0] + 100]:
            draw.line([(mast_x, center[1] - 220), (mast_x, center[1] + 120)], fill=(20, 26, 30, 255), width=10)
            draw.polygon([(mast_x, center[1] - 200), (mast_x + 120, center[1] - 150), (mast_x, center[1] - 80)], fill=(24, 40, 48, 220))
        for wave in range(6):
            y = center[1] + 80 + wave * 22
            draw.arc([180, y - 40, width - 180, y + 70], 0, 180, fill=(100, 200, 220, 90), width=6)
    elif theme.code == "brass":
        for tower_x in [center[0] - 220, center[0], center[0] + 220]:
            draw.rectangle([tower_x - 44, center[1] - 260, tower_x + 44, center[1] + 120], fill=(30, 22, 12, 255))
            draw.ellipse([tower_x - 70, center[1] - 70, tower_x + 70, center[1] + 70], outline=(220, 180, 104, 120), width=10)
            draw.ellipse([tower_x - 24, center[1] - 24, tower_x + 24, center[1] + 24], fill=(100, 72, 30, 220))
    else:
        _draw_starfield(image, 3100 + act_index, (240, 230, 255), 220)
        for shard_x in [center[0] - 240, center[0] - 80, center[0] + 60, center[0] + 240]:
            draw.polygon([(shard_x, center[1] + 140), (shard_x + 40, center[1] - 180), (shard_x + 90, center[1] + 140)], fill=(24, 16, 36, 240))
        for ring in range(3):
            radius = 160 + ring * 70
            draw.arc([center[0] - radius, center[1] - 340, center[0] + radius, center[1] - 40], 205, 335, fill=(190, 160, 255, 90), width=8)

    hero_x = center[0] - 28
    hero_y = center[1] + 120
    draw.rectangle([hero_x - 16, hero_y - 110, hero_x + 16, hero_y - 70], fill=(214, 180, 126, 255))
    draw.rectangle([hero_x - 22, hero_y - 70, hero_x + 22, hero_y + 10], fill=(168, 106, 54, 255))
    draw.rectangle([hero_x - 12, hero_y + 10, hero_x - 2, hero_y + 78], fill=(110, 76, 42, 255))
    draw.rectangle([hero_x + 2, hero_y + 10, hero_x + 12, hero_y + 78], fill=(110, 76, 42, 255))
    draw.rectangle([hero_x - 30, hero_y - 60, hero_x - 18, hero_y + 6], fill=(168, 106, 54, 255))
    draw.rectangle([hero_x + 18, hero_y - 60, hero_x + 30, hero_y + 6], fill=(168, 106, 54, 255))
    draw.rectangle([hero_x + 30, hero_y - 48, hero_x + 58, hero_y - 20], fill=(46, 44, 44, 255))
    draw.rectangle([hero_x + 44, hero_y - 66, hero_x + 52, hero_y - 48], fill=(148, 112, 54, 255))
    _add_glow(image, (hero_x + 52, hero_y - 66), 44, accent, 80)
    return image


def _generate_background_assets() -> None:
    for act_index, theme in enumerate(THEMES):
        path = os.path.join(BG_DIR, f"bg_pack_201_{theme.code}.png")
        _draw_late_background(theme, act_index).save(path)
        print(f"saved {path}")


def _generate_story_assets() -> None:
    for act_index, theme in enumerate(THEMES):
        path = os.path.join(STORY_DIR, f"story_pack_201_{theme.code}.png")
        _draw_story_scene(theme, act_index).save(path)
        print(f"saved {path}")


def _build_levels() -> Dict[int, Dict[str, object]]:
    levels: Dict[int, Dict[str, object]] = {}
    for act_index, theme in enumerate(THEMES):
        for slot, boss in enumerate(BOSSES):
            variant = _get_boss_variant(boss, act_index, slot)
            floor = 201 + act_index * len(BOSSES) + slot
            width, height = _boss_dims(variant.shape)
            mass = len(variant.shape)
            mine_cols = 15 + (slot % 5) + act_index
            mine_rows = 8 + (slot // 5) + (1 if act_index >= 3 else 0)
            density = 0.17 + act_index * 0.01 + (slot % 4) * 0.006
            bomb_count = int(round(mine_cols * mine_rows * density))
            placement_cols = width + 8 + act_index + (2 if act_index >= 3 else 0)
            placement_rows = max(height + 3, 9 + act_index // 2 + (1 if act_index >= 3 else 0))
            role_bonus = {"tank": 2, "rush": 1, "artillery": 0, "leech": 1, "balanced": 1}[boss.style]
            attack = 11 + act_index * 2 + slot // 4 + role_bonus
            move_interval = max(14.0, 24.0 - act_index * 1.3 - slot * 0.18 - (1.0 if boss.style == "rush" else 0.0))
            turn_duration = max(16.0, 28.0 - act_index * 1.4 - slot * 0.22)
            hp_multiplier = round(2.05 + act_index * 0.35 + mass * 0.045 + (0.18 if act_index >= 3 else 0.0) + (0.12 if boss.style == "tank" else 0.0), 2)
            max_clicks = min(14, 9 + act_index + (1 if boss.style in {"artillery", "rush"} else 0) + (1 if mass >= 22 else 0))
            level_color = _blend_color(theme.color, boss.accent, 0.45)
            background_path = f"res://assets/sprites/bg/bg_pack_201_{theme.code}.png"
            story_art_path = f"res://assets/sprites/story/story_pack_201_{theme.code}.png"

            levels[floor] = {
                "id": floor,
                "name": f"{theme.zone}·{boss.arena_name}",
                "boss_name": boss.boss_name,
                "subtitle": f"{theme.intro}{boss.hint}{theme.outro}",
                "story_title": f"第{act_index + 1}幕·{theme.zone}",
                "story_text": theme.story_line,
                "show_story_card": slot == 0,
                "background_path": background_path,
                "story_art_path": story_art_path,
                "color": level_color,
                "tile_weights": _style_weights(boss.style, act_index),
                "bomb_count": bomb_count,
                "turn_duration": round(turn_duration, 1),
                "boss_attack": attack,
                "boss_move_interval": round(move_interval, 1),
                "placement_cols": placement_cols,
                "placement_rows": placement_rows,
                "mine_cols": mine_cols,
                "mine_rows": mine_rows,
                "boss_shape": variant.code,
                "hp_multiplier": hp_multiplier,
                "max_clicks": max_clicks,
            }
    return levels


def _generate_pack_gd(levels: Dict[int, Dict[str, object]]) -> str:
    variants = _collect_variants()
    shape_consts: List[str] = []
    for variant in variants:
        shape_consts.append(
            "const SHAPE_%s = [\n%s\n]\n" % (variant.code, _shape_text(variant.shape))
        )

    shape_map_lines = [f'\t"{variant.code}": SHAPE_{variant.code},' for variant in variants]
    texture_map_lines = [
        f'\t"{variant.code}": "res://assets/sprites/boss/boss_pack_201_{variant.code.lower()}.png",'
        for variant in variants
    ]

    level_lines: List[str] = []
    for floor in sorted(levels):
        level = levels[floor]
        level_lines.append(
            "\t%d: {\n"
            "\t\t\"id\": %d,\n"
            "\t\t\"name\": \"%s\",\n"
            "\t\t\"boss_name\": \"%s\",\n"
            "\t\t\"subtitle\": \"%s\",\n"
            "\t\t\"story_title\": \"%s\",\n"
            "\t\t\"story_text\": \"%s\",\n"
            "\t\t\"show_story_card\": %s,\n"
            "\t\t\"background_path\": \"%s\",\n"
            "\t\t\"story_art_path\": \"%s\",\n"
            "\t\t\"color\": %s,\n"
            "\t\t\"tile_weights\": %s,\n"
            "\t\t\"bomb_count\": %d,\n"
            "\t\t\"turn_duration\": %.1f,\n"
            "\t\t\"boss_attack\": %d,\n"
            "\t\t\"boss_move_interval\": %.1f,\n"
            "\t\t\"placement_cols\": %d,\n"
            "\t\t\"placement_rows\": %d,\n"
            "\t\t\"mine_cols\": %d,\n"
            "\t\t\"mine_rows\": %d,\n"
            "\t\t\"boss_shape\": \"%s\",\n"
            "\t\t\"hp_multiplier\": %.2f,\n"
            "\t\t\"max_clicks\": %d,\n"
            "\t},\n"
            % (
                floor,
                level["id"],
                _gd_string(level["name"]),
                _gd_string(level["boss_name"]),
                _gd_string(level["subtitle"]),
                _gd_string(level["story_title"]),
                _gd_string(level["story_text"]),
                "true" if level["show_story_card"] else "false",
                level["background_path"],
                level["story_art_path"],
                _color_text(level["color"]),
                _dict_text(level["tile_weights"]),
                level["bomb_count"],
                level["turn_duration"],
                level["boss_attack"],
                level["boss_move_interval"],
                level["placement_cols"],
                level["placement_rows"],
                level["mine_cols"],
                level["mine_rows"],
                level["boss_shape"],
                level["hp_multiplier"],
                level["max_clicks"],
            )
        )

    return (
        "## Floors 201-300 isolated content pack.\n"
        "## Generated by scripts/tools/gen_pack_201_300.py\n\n"
        "extends RefCounted\n\n"
        "const FLOOR_START = 201\n"
        "const FLOOR_END = 300\n\n"
        + "\n".join(shape_consts)
        + "\nconst SHAPE_MAP = {\n"
        + "\n".join(shape_map_lines)
        + "\n}\n\n"
        + "const BOSS_TEXTURE_MAP = {\n"
        + "\n".join(texture_map_lines)
        + "\n}\n\n"
        + "const LEVELS = {\n"
        + "".join(level_lines)
        + "}\n\n"
        + "static func has_floor(floor_number: int) -> bool:\n"
        + "\treturn floor_number >= FLOOR_START and floor_number <= FLOOR_END\n\n"
        + "static func get_cycle(_floor_number: int) -> int:\n"
        + "\treturn 0\n\n"
        + "static func get_level(floor_number: int) -> Dictionary:\n"
        + "\treturn LEVELS.get(floor_number, {})\n\n"
        + "static func get_shape_map() -> Dictionary:\n"
        + "\treturn SHAPE_MAP\n\n"
        + "static func get_texture_map() -> Dictionary:\n"
        + "\treturn BOSS_TEXTURE_MAP\n"
    )


def _generate_boss_assets() -> None:
    variants = _collect_variants()
    preview_items: List[Tuple[str, str]] = []
    latest_preview: Dict[str, Tuple[str, str]] = {}
    for variant in variants:
        boss = variant.source
        width, height = _boss_dims(variant.shape)
        cfg = {
            "cols": width,
            "rows": height,
            "shape": list(variant.shape),
            "body": boss.body,
            "dark": boss.dark,
            "crack": boss.crack,
            "glow": boss.glow,
            "eye": boss.eye,
            "rune": boss.rune,
            "accent": boss.accent,
        }
        filename = f"pack_201_{variant.code.lower()}"
        base_boss.gen_boss_sheet(filename, cfg)
        latest_preview[boss.code] = (boss.boss_name, os.path.join(BOSS_DIR, f"boss_{filename}.png"))

    preview_items = [latest_preview[boss.code] for boss in BOSSES if boss.code in latest_preview]

    thumb_w = 168
    thumb_h = 168
    cols = 4
    rows = math.ceil(len(preview_items) / cols)
    canvas = Image.new("RGBA", (cols * 212, rows * 224), (10, 10, 14, 255))
    draw = ImageDraw.Draw(canvas)

    for index, (name, path) in enumerate(preview_items):
        if not os.path.exists(path):
            continue
        img = Image.open(path).convert("RGBA")
        img.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        col = index % cols
        row = index // cols
        x = col * 212 + (212 - img.width) // 2
        y = row * 224 + 16
        panel = [col * 212 + 8, row * 224 + 8, col * 212 + 204, row * 224 + 214]
        draw.rounded_rectangle(panel, radius=12, fill=(20, 20, 28, 255), outline=(72, 72, 96, 255), width=2)
        canvas.alpha_composite(img, (x, y))
        draw.text((col * 212 + 18, row * 224 + 186), name, fill=(232, 226, 210, 255))

    canvas.save(PREVIEW_PATH)
    print(f"saved {PREVIEW_PATH}")


def main() -> None:
    os.makedirs(BOSS_DIR, exist_ok=True)
    os.makedirs(BG_DIR, exist_ok=True)
    os.makedirs(STORY_DIR, exist_ok=True)
    levels = _build_levels()
    pack_text = _generate_pack_gd(levels)
    with open(PACK_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(pack_text)
    print(f"saved {PACK_PATH}")
    _generate_boss_assets()
    _generate_background_assets()
    _generate_story_assets()
    print("late pack 201-300 generated")


if __name__ == "__main__":
    main()