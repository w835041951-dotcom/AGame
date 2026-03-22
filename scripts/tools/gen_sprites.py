"""地牢像素风 Boss 格子 & 部位图标生成器
生成: tile_normal/weak/armor/absorb/dead.png + part_head/leg/core.png
（炸弹图标由 gen_boss.py 生成，扫雷格/爆炸由 gen_assets.py 生成）
"""
import os, math, random
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites")
S = 4  # 像素艺术放大倍数
random.seed(42)

def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("saved", path)

def px(v):
    return int(v * S)

def stone_noise(dr, x0, y0, x1, y1, base, density=0.25):
    for y in range(y0, y1, px(2)):
        for x in range(x0, x1, px(2)):
            if random.random() < density:
                sh = random.randint(-15, 15)
                c = tuple(max(0, min(255, base[i] + sh)) for i in range(3))
                dr.rectangle([x, y, x + px(2), y + px(2)], fill=c + (60,))

# ═══════════════════════════════════════
# Boss 格子 56x56 — 地牢石砖风格
# ═══════════════════════════════════════
def gen_boss_tiles():
    SZ = 56 * S

    tiles = {
        "normal": {
            "base": (85, 30, 28),
            "border": (160, 45, 40),
            "bw": 2,
            "accent": None,
        },
        "weak": {
            "base": (70, 65, 25),
            "border": (220, 195, 30),
            "bw": 3,
            "accent": "zigzag",
        },
        "armor": {
            "base": (40, 50, 80),
            "border": (100, 130, 200),
            "bw": 3,
            "accent": "rivets",
        },
        "absorb": {
            "base": (25, 65, 40),
            "border": (50, 190, 90),
            "bw": 2,
            "accent": "rune",
        },
        "dead": {
            "base": (18, 18, 20),
            "border": (55, 55, 60),
            "bw": 1,
            "accent": "crack",
        },
    }

    for name, cfg in tiles.items():
        img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        base = cfg["base"]
        border = cfg["border"]
        bw = cfg["bw"]

        # 石砖底色 + 圆角
        dr.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=px(3), fill=base + (255,))

        # 3D 边框（上亮下暗）
        hi = tuple(min(255, c + 20) for c in base)
        lo = tuple(max(0, c - 25) for c in base)
        dr.line([(px(2), px(1)), (SZ - px(3), px(1))], fill=hi + (200,), width=px(1))
        dr.line([(px(1), px(2)), (px(1), SZ - px(3))], fill=hi + (160,), width=px(1))
        dr.line([(px(2), SZ - px(2)), (SZ - px(3), SZ - px(2))], fill=lo + (200,), width=px(1))
        dr.line([(SZ - px(2), px(2)), (SZ - px(2), SZ - px(3))], fill=lo + (160,), width=px(1))

        # 石砖接缝
        dr.line([(px(4), SZ // 2), (SZ - px(4), SZ // 2)], fill=lo + (80,), width=px(1))
        dr.line([(SZ // 3, px(4)), (SZ // 3, SZ // 2 - px(2))], fill=lo + (60,), width=px(1))
        dr.line([(SZ * 2 // 3, SZ // 2 + px(2)), (SZ * 2 // 3, SZ - px(4))], fill=lo + (60,), width=px(1))

        # 噪点纹理
        stone_noise(dr, px(3), px(3), SZ - px(3), SZ - px(3), base)

        # 彩色边框
        for i in range(bw):
            off = px(1) * i
            dr.rounded_rectangle([off, off, SZ - 1 - off, SZ - 1 - off],
                                 radius=px(3), outline=border + (220,), width=px(1))

        # 独特装饰
        cx, cy = SZ // 2, SZ // 2
        accent = cfg["accent"]
        if accent == "zigzag":
            # 弱点闪电纹
            pts_l = [(px(6), px(5)), (px(10), SZ // 2), (px(7), SZ // 2), (px(11), SZ - px(5))]
            pts_r = [(SZ - px(6), px(5)), (SZ - px(10), SZ // 2), (SZ - px(7), SZ // 2), (SZ - px(11), SZ - px(5))]
            dr.line(pts_l, fill=(255, 200, 40, 160), width=px(1))
            dr.line(pts_r, fill=(255, 200, 40, 160), width=px(1))
        elif accent == "rivets":
            # 四角铆钉
            rivet_r = px(3)
            for rx, ry in [(px(5), px(5)), (SZ - px(5), px(5)),
                           (px(5), SZ - px(5)), (SZ - px(5), SZ - px(5))]:
                dr.ellipse([rx - rivet_r, ry - rivet_r, rx + rivet_r, ry + rivet_r],
                           fill=(140, 160, 220, 200))
                dr.ellipse([rx - rivet_r + px(1), ry - rivet_r + px(1),
                            rx + rivet_r - px(1), ry + rivet_r - px(1)],
                           fill=(170, 190, 240, 180))
        elif accent == "rune":
            # 吸收符文圈
            rr = int(SZ * 0.25)
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                       outline=(60, 220, 100, 140), width=px(1))
            dr.ellipse([cx - rr + px(3), cy - rr + px(3),
                        cx + rr - px(3), cy + rr - px(3)],
                       outline=(60, 220, 100, 100), width=px(1))
            # 十字符文
            dr.line([cx, cy - rr + px(2), cx, cy + rr - px(2)],
                    fill=(60, 220, 100, 120), width=px(1))
            dr.line([cx - rr + px(2), cy, cx + rr - px(2), cy],
                    fill=(60, 220, 100, 120), width=px(1))
        elif accent == "crack":
            # 死亡裂纹 X
            dr.line([px(6), px(6), SZ - px(6), SZ - px(6)],
                    fill=(80, 80, 85, 200), width=px(2))
            dr.line([SZ - px(6), px(6), px(6), SZ - px(6)],
                    fill=(80, 80, 85, 200), width=px(2))
            # 碎片散落
            for _ in range(5):
                fx = random.randint(px(6), SZ - px(6))
                fy = random.randint(px(6), SZ - px(6))
                dr.rectangle([fx, fy, fx + px(2), fy + px(2)], fill=(50, 50, 55, 100))

        out = img.resize((56, 56), Image.LANCZOS)
        save(out, "boss", "tile_" + name + ".png")

# ═══════════════════════════════════════
# Boss 部位图标 24x24 — 宝石地牢风
# ═══════════════════════════════════════
def gen_part_icons():
    SZ = 24 * S

    parts = {
        "head": {"base": (180, 45, 40), "gem": (230, 70, 60), "hi": (255, 140, 130)},
        "leg":  {"base": (40, 100, 190), "gem": (60, 140, 230), "hi": (140, 195, 255)},
        "core": {"base": (190, 150, 25), "gem": (230, 185, 40), "hi": (255, 230, 130)},
    }

    for name, cfg in parts.items():
        img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        cx, cy = SZ // 2, SZ // 2
        r = SZ // 2 - px(2)

        # 暗色外环
        dark = tuple(max(0, c - 40) for c in cfg["base"])
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark + (255,),
                   outline=cfg["base"] + (255,), width=px(2))
        # 宝石主色
        ir = r - px(3)
        dr.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=cfg["gem"] + (255,))
        # 高光
        hr = ir // 2
        dr.ellipse([cx - hr - px(1), cy - hr - px(2), cx + hr - px(2), cy],
                   fill=cfg["hi"] + (150,))
        # 底部暗影
        dr.arc([cx - ir, cy, cx + ir, cy + ir], 30, 150,
               fill=dark + (120,), width=px(1))

        out = img.resize((24, 24), Image.LANCZOS)
        save(out, "boss", "part_" + name + ".png")

if __name__ == "__main__":
    gen_boss_tiles()
    gen_part_icons()
    print("=== Boss tiles & parts generated ===")
