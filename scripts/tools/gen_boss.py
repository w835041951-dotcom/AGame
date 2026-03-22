"""
Boss 像素艺术生成器 v3 — 地牢石像鬼(Gargoyle)风格
256x192px (4col x 3row, 64px/cell)
特点：石头质感 + 裂纹 + 发光符文 + 蝙蝠翼 — 经典地牢像素风
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

SCALE = 6
W, H = 256 * SCALE, 192 * SCALE
CELL = 64 * SCALE

random.seed(42)  # 可复现

def px(v):
    if isinstance(v, (list, tuple)) and len(v) > 0 and not isinstance(v[0], (int, float)):
        return [(int(x * SCALE), int(y * SCALE)) for x, y in v]
    if isinstance(v, (list, tuple)):
        return [int(x * SCALE) for x in v]
    return int(v * SCALE)

def circle(dr, cx, cy, r, fill, outline=None, ow=1):
    dr.ellipse([px(cx - r), px(cy - r), px(cx + r), px(cy + r)], fill=fill,
               outline=outline, width=px(ow) if outline else 0)

def rect(dr, x0, y0, x1, y1, fill=None, outline=None, ow=1, radius=0):
    dr.rounded_rectangle([px(x0), px(y0), px(x1), px(y1)],
                         radius=px(radius), fill=fill,
                         outline=outline, width=px(ow) if outline else 0)

def poly(dr, pts, fill, outline=None, ow=1):
    dr.polygon(px(pts), fill=fill, outline=outline, width=px(ow) if outline else 0)

def line(dr, x0, y0, x1, y1, fill, w=1):
    dr.line([px(x0), px(y0), px(x1), px(y1)], fill=fill, width=px(w))

def add_glow(img, cx, cy, r, color, steps=12):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdr = ImageDraw.Draw(glow)
    for i in range(steps, 0, -1):
        alpha = int(color[3] * (i / steps) ** 2)
        rad = int(r * i / steps)
        c = color[:3] + (alpha,)
        gdr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=c)
    return Image.alpha_composite(img, glow)

def stone_noise(dr, x0, y0, x1, y1, base_color, density=0.3):
    """在区域上绘制像素化石头噪点纹理"""
    for y in range(y0, y1, px(2)):
        for x in range(x0, x1, px(2)):
            if random.random() < density:
                shade = random.randint(-15, 15)
                c = tuple(max(0, min(255, base_color[i] + shade)) for i in range(3))
                dr.rectangle([x, y, x + px(2), y + px(2)], fill=c + (60,))

def gen_boss():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    # ── 石体底色：深灰-岩绿渐变 ──
    for y in range(H):
        t = y / H
        r = int(50 + 20 * t)
        g = int(55 + 15 * t)
        b = int(60 - 10 * t)
        dr.line([(px(6), y), (W - px(6), y)], fill=(r, g, b, 240))

    # ── 石像主体（多层岩石质感） ──
    rect(dr, 8, 10, 248, 182, fill=(35, 38, 42, 200), radius=12)
    rect(dr, 5, 7, 251, 185, fill=(60, 65, 72, 255), radius=10)
    rect(dr, 10, 12, 246, 180, fill=(72, 78, 85, 255), radius=8)

    # 岩石表面噪点
    stone_noise(dr, px(10), px(12), px(246), px(180), (72, 78, 85))

    # ── 岩石裂纹纹路 ──
    cracks = [
        [(22, 34), (46, 52), (64, 48), (82, 58)],
        [(168, 28), (186, 44), (204, 40), (224, 52)],
        [(28, 110), (52, 122), (72, 116), (96, 128)],
        [(158, 122), (182, 132), (200, 124), (232, 136)],
        [(58, 158), (90, 168), (114, 160)],
        [(140, 156), (170, 166), (194, 158)],
    ]
    for crack in cracks:
        for i in range(len(crack) - 1):
            line(dr, crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1],
                 (40, 42, 48, 180), 2)
            line(dr, crack[i][0] + 1, crack[i][1] + 1, crack[i + 1][0] + 1, crack[i + 1][1] + 1,
                 (90, 95, 100, 80), 1)

    # ── 蝙蝠翼（左） ──
    wing_l = [(8, 24), (0, 12), (0, 178), (8, 168), (34, 140), (30, 90), (36, 52), (34, 34)]
    poly(dr, wing_l, fill=(40, 44, 50, 255))
    for i in range(4):
        yt = 26 + i * 34
        yb = yt + 32
        poly(dr, [(8, yt), (30, yt - 4), (32, yb + 4), (8, yb)],
             fill=(55, 60, 68, 220))
        line(dr, 9, yt + 2, 28, yt - 2, (80, 85, 95, 160), 1)
    # 蝙蝠翼（右，镜像）
    wing_r = [(248, 24), (256, 12), (256, 178), (248, 168), (222, 140), (226, 90), (220, 52), (222, 34)]
    poly(dr, wing_r, fill=(40, 44, 50, 255))
    for i in range(4):
        yt = 26 + i * 34
        yb = yt + 32
        poly(dr, [(248, yt), (226, yt - 4), (224, yb + 4), (248, yb)],
             fill=(55, 60, 68, 220))
        line(dr, 247, yt + 2, 228, yt - 2, (80, 85, 95, 160), 1)

    # ── 石角（弯曲羊角造型） ──
    for t in range(8):
        frac = t / 7
        ax = 58 + int(18 * frac)
        ay = 12 - int(22 * math.sin(frac * math.pi * 0.6))
        r_size = 12 - int(8 * frac)
        shade = int(90 + 40 * frac)
        circle(dr, ax, ay, r_size, (shade, shade - 5, shade - 10, 255))
    for t in range(8):
        frac = t / 7
        ax = 198 - int(18 * frac)
        ay = 12 - int(22 * math.sin(frac * math.pi * 0.6))
        r_size = 12 - int(8 * frac)
        shade = int(90 + 40 * frac)
        circle(dr, ax, ay, r_size, (shade, shade - 5, shade - 10, 255))

    # ── 面部 ──
    rect(dr, 62, 4, 194, 62, fill=(58, 62, 70, 255), radius=14)
    rect(dr, 66, 8, 190, 60, fill=(70, 75, 82, 255), radius=12)
    stone_noise(dr, px(66), px(8), px(190), px(60), (70, 75, 82), 0.2)

    # 眉脊
    poly(dr, [(70, 22), (94, 14), (102, 22), (94, 26), (70, 28)], fill=(50, 54, 60, 255))
    poly(dr, [(186, 22), (162, 14), (154, 22), (162, 26), (186, 28)], fill=(50, 54, 60, 255))

    # 眼窝（深凹）
    poly(dr, [(74, 22), (100, 20), (102, 37), (74, 39)], fill=(10, 12, 15, 255))
    poly(dr, [(154, 20), (180, 22), (180, 39), (152, 37)], fill=(10, 12, 15, 255))

    # 眼睛发光（绿色地牢灵光）
    img = add_glow(img, px(88), px(30), px(14), (60, 255, 120, 140))
    img = add_glow(img, px(168), px(30), px(14), (60, 255, 120, 140))
    dr = ImageDraw.Draw(img)
    circle(dr, 88, 30, 6, (80, 255, 130, 255))
    circle(dr, 88, 30, 3, (200, 255, 220, 255))
    circle(dr, 168, 30, 6, (80, 255, 130, 255))
    circle(dr, 168, 30, 3, (200, 255, 220, 255))

    # 鼻部（扁平+两个鼻孔）
    poly(dr, [(120, 37), (128, 32), (136, 37), (134, 46), (122, 46)], fill=(55, 58, 65, 255))
    circle(dr, 124, 43, 3, (20, 22, 26, 255))
    circle(dr, 132, 43, 3, (20, 22, 26, 255))

    # 嘴部（石裂口+尖牙）
    poly(dr, [(78, 46), (178, 46), (174, 59), (82, 59)], fill=(15, 16, 20, 255))
    for tx in range(82, 173, 12):
        poly(dr, [(tx, 46), (tx + 6, 46), (tx + 3, 54)], fill=(190, 195, 180, 255))
    for tx in range(88, 172, 12):
        poly(dr, [(tx, 59), (tx + 6, 59), (tx + 3, 52)], fill=(180, 185, 170, 255))

    # ── 胸甲：发光符文圆盘 ──
    cx, cy = 128, 128
    circle(dr, cx, cy, 32, (45, 48, 55, 255))
    circle(dr, cx, cy, 27, (55, 58, 65, 255))
    stone_noise(dr, px(cx - 27), px(cy - 27), px(cx + 27), px(cy + 27), (55, 58, 65), 0.2)

    rune_pts = [
        [(cx, cy - 22), (cx + 14, cy - 7), (cx + 10, cy + 12), (cx, cy + 22),
         (cx - 10, cy + 12), (cx - 14, cy - 7), (cx, cy - 22)],
        [(cx - 7, cy - 12), (cx + 7, cy - 12)],
        [(cx - 10, cy + 5), (cx + 10, cy + 5)],
    ]
    for rune in rune_pts:
        for i in range(len(rune) - 1):
            line(dr, rune[i][0], rune[i][1], rune[i + 1][0], rune[i + 1][1],
                 (60, 220, 100, 255), 2)
    img = add_glow(img, px(cx), px(cy), px(22), (40, 255, 100, 130))
    img = add_glow(img, px(cx), px(cy), px(12), (120, 255, 160, 100))
    dr = ImageDraw.Draw(img)
    gem = [(cx, cy - 12), (cx + 8, cy - 6), (cx + 8, cy + 6), (cx, cy + 12),
           (cx - 8, cy + 6), (cx - 8, cy - 6)]
    poly(dr, gem, fill=(30, 180, 80, 255))
    poly(dr, [(cx, cy - 12), (cx + 8, cy - 6), (cx + 2, cy)], fill=(60, 230, 120, 220))
    poly(dr, [(cx, cy - 12), (cx - 8, cy - 6), (cx - 2, cy)], fill=(20, 140, 60, 200))
    circle(dr, cx - 2, cy - 7, 2.5, (180, 255, 200, 200))

    # ── 腹部石砖分节 ──
    for seg_y in [70, 86, 100, 114]:
        line(dr, 42, seg_y, 214, seg_y, (48, 50, 56, 180), 2)
        line(dr, 42, seg_y + 1, 214, seg_y + 1, (85, 90, 95, 60), 1)
        for sx in [60, 94, 128, 162, 196]:
            circle(dr, sx, seg_y, 2.5, (90, 95, 100, 150))

    # ── 石质手臂刻痕 ──
    for side, xb in [(-1, 42), (1, 214)]:
        for ay in range(72, 178, 17):
            line(dr, xb, ay, xb + side * 8, ay + 7, (55, 58, 65, 150), 2)
            line(dr, xb, ay + 1, xb + side * 8, ay + 8, (90, 95, 100, 60), 1)

    # ── 底部石爪 ──
    for cx2 in [56, 92, 128, 164, 200]:
        poly(dr, [(cx2 - 11, 174), (cx2, 168), (cx2 + 11, 174), (cx2 + 6, 192), (cx2 - 6, 192)],
             fill=(50, 54, 60, 255))
        poly(dr, [(cx2 - 7, 174), (cx2, 170), (cx2 + 7, 174), (cx2 + 4, 188), (cx2 - 4, 188)],
             fill=(68, 72, 80, 255))
        line(dr, cx2 - 7, 174, cx2 - 4, 188, (95, 100, 108, 180), 1)

    # ── 两侧符文标记（绿色小符号） ──
    for rx, ry in [(26, 78), (26, 134), (230, 78), (230, 134)]:
        circle(dr, rx, ry, 5, (40, 180, 80, 120))
        img = add_glow(img, px(rx), px(ry), px(7), (40, 220, 80, 60))
        dr = ImageDraw.Draw(img)

    # ── 外轮廓描边 ──
    rect(dr, 4, 6, 252, 186, outline=(70, 200, 110, 180), ow=2, radius=10)
    rect(dr, 6, 8, 250, 184, outline=(50, 55, 62, 120), ow=1, radius=8)

    # ── 缩小到最终尺寸 ──
    out_img = img.resize((256, 192), Image.LANCZOS)

    # ── 轻微格线（调试参考）──
    gdr = ImageDraw.Draw(out_img)
    for col in range(1, 4):
        gdr.line([(col * 64, 0), (col * 64, 192)], fill=(60, 180, 100, 30), width=1)
    for row in range(1, 3):
        gdr.line([(0, row * 64), (256, row * 64)], fill=(60, 180, 100, 30), width=1)

    path = os.path.join(OUT, "boss_full.png")
    out_img.save(path)
    print("saved", path)

    # ── 受击叠加层（绿色闪光） ──
    hit = Image.new("RGBA", (256, 192), (0, 0, 0, 0))
    hdr = ImageDraw.Draw(hit)
    hdr.rounded_rectangle([2, 4, 254, 188], radius=10, fill=(80, 255, 120, 90))
    hit.save(os.path.join(OUT, "boss_hit_overlay.png"))
    print("saved boss_hit_overlay.png")


def gen_bombs():
    """地牢像素风炸弹图标 32x32 — 圆形炸弹+不同符文标记"""
    bdir = os.path.join(OUT, "..", "bombs")
    os.makedirs(bdir, exist_ok=True)
    S = 6
    SZ = 32 * S

    configs = {
        "cross":   {"body": (55, 55, 60), "rune": (255, 60, 50),  "glow": (255, 80, 60, 120)},
        "scatter": {"body": (55, 55, 60), "rune": (255, 180, 40), "glow": (255, 200, 60, 120)},
        "bounce":  {"body": (55, 55, 60), "rune": (40, 220, 220), "glow": (60, 240, 240, 120)},
        "pierce":  {"body": (55, 55, 60), "rune": (240, 240, 60), "glow": (255, 255, 80, 120)},
        "area":    {"body": (55, 55, 60), "rune": (200, 60, 255), "glow": (220, 80, 255, 120)},
    }

    for name, cfg in configs.items():
        img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        cx = cy = SZ // 2
        r = SZ // 2 - 4 * S

        # 阴影
        dr.ellipse([cx - r + 2 * S, cy - r + 4 * S, cx + r + 2 * S, cy + r + 4 * S],
                   fill=(0, 0, 0, 60))
        # 深色外圈（铁壳）
        dark = tuple(max(0, c - 25) for c in cfg["body"])
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark + (255,))
        # 主体
        dr.ellipse([cx - r + S, cy - r + S, cx + r - S, cy + r - S], fill=cfg["body"] + (255,))
        # 噪点质感
        for _ in range(80):
            nx = random.randint(cx - r + 2 * S, cx + r - 2 * S)
            ny = random.randint(cy - r + 2 * S, cy + r - 2 * S)
            sh = random.randint(-10, 10)
            nc = tuple(max(0, min(255, cfg["body"][i] + sh)) for i in range(3))
            dr.rectangle([nx, ny, nx + S, ny + S], fill=nc + (50,))
        # 高光
        dr.ellipse([cx - r + 3 * S, cy - r + 2 * S, cx - r + 9 * S, cy - r + 7 * S],
                   fill=(255, 255, 255, 140))
        dr.ellipse([cx - r + 4 * S, cy - r + 3 * S, cx - r + 7 * S, cy - r + 5 * S],
                   fill=(255, 255, 255, 200))

        # 发光符文（每种炸弹不同）
        rc = cfg["rune"]
        img = add_glow(img, cx, cy, int(r * 0.6), cfg["glow"])
        dr = ImageDraw.Draw(img)

        if name == "cross":
            line(dr, cx // S - 6, cy // S, cx // S + 6, cy // S, rc + (255,), 2)
            line(dr, cx // S, cy // S - 6, cx // S, cy // S + 6, rc + (255,), 2)
        elif name == "scatter":
            for angle in range(0, 360, 60):
                a = math.radians(angle)
                ex = cx + int(r * 0.4 * math.cos(a))
                ey = cy + int(r * 0.4 * math.sin(a))
                dr.ellipse([ex - S, ey - S, ex + S, ey + S], fill=rc + (255,))
        elif name == "bounce":
            pts = []
            for i in range(5):
                a = math.radians(i * 72 - 90)
                pts.append((cx + int(r * 0.45 * math.cos(a)), cy + int(r * 0.45 * math.sin(a))))
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                dr.line([x0, y0, x1, y1], fill=rc + (255,), width=int(1.5 * S))
        elif name == "pierce":
            # 向上箭头
            poly(dr, [
                (cx // S, cy // S - 7),
                (cx // S + 5, cy // S),
                (cx // S + 2, cy // S),
                (cx // S + 2, cy // S + 6),
                (cx // S - 2, cy // S + 6),
                (cx // S - 2, cy // S),
                (cx // S - 5, cy // S),
            ], fill=rc + (255,))
        elif name == "area":
            rect(dr, cx // S - 5, cy // S - 5, cx // S + 5, cy // S + 5,
                 fill=None, outline=rc + (255,), ow=2, radius=1)
            rect(dr, cx // S - 3, cy // S - 3, cx // S + 3, cy // S + 3,
                 fill=rc + (200,), radius=0)

        # 引线
        fuse_pts = [
            (int(cx + r * 0.5), int(cy - r * 0.7)),
            (int(cx + r * 0.75), int(cy - r * 0.95)),
            (int(cx + r * 1.0), int(cy - r * 1.15)),
        ]
        dr.line(fuse_pts, fill=(120, 100, 50, 255), width=2 * S)
        dr.line(fuse_pts, fill=(180, 150, 70, 200), width=S)

        # 引线火花
        fsx, fsy = fuse_pts[-1]
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            length = S * (3 + (angle % 3))
            dr.line([fsx, fsy, int(fsx + length * math.cos(a)), int(fsy + length * math.sin(a))],
                    fill=(255, 220, 60, 200), width=S)
        dr.ellipse([fsx - 2 * S, fsy - 2 * S, fsx + 2 * S, fsy + 2 * S],
                   fill=(255, 250, 180, 255))

        out = img.resize((32, 32), Image.LANCZOS)
        path = os.path.join(bdir, name + ".png")
        out.save(path)
        print("saved", path)


if __name__ == "__main__":
    gen_boss()
    gen_bombs()
    print("All done!")
