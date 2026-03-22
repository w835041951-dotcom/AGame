"""
地牢像素风美术资源生成器
- 扫雷格子（石砖质感）
- 爆炸特效 spritesheet (火焰+碎石)
- 地牢背景（砖墙+火把光晕）
- HUD 图标
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites")
S = 4  # 像素艺术缩放倍数

random.seed(42)

def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("saved", path)

def px(v):
    return int(v * S)

def stone_noise(dr, x0, y0, x1, y1, base, density=0.3):
    for y in range(y0, y1, px(2)):
        for x in range(x0, x1, px(2)):
            if random.random() < density:
                sh = random.randint(-12, 12)
                c = tuple(max(0, min(255, base[i] + sh)) for i in range(3))
                dr.rectangle([x, y, x + px(2), y + px(2)], fill=c + (50,))

# ═══════════════════════════════════════
# 扫雷格子 52x52 — 石砖地牢风格
# ═══════════════════════════════════════
def gen_mine_cells():
    SZ = 52 * S

    # ── 隐藏格（石砖凸起） ──
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    base = (65, 68, 75)
    dr.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=px(4), fill=base + (255,))
    # 3D 凸起边框
    dr.line([(px(1), px(1)), (SZ - px(2), px(1))], fill=(95, 98, 105, 255), width=px(2))
    dr.line([(px(1), px(1)), (px(1), SZ - px(2))], fill=(90, 93, 100, 255), width=px(2))
    dr.line([(px(2), SZ - px(2)), (SZ - px(2), SZ - px(2))], fill=(40, 42, 50, 255), width=px(2))
    dr.line([(SZ - px(2), px(2)), (SZ - px(2), SZ - px(2))], fill=(42, 44, 52, 255), width=px(2))
    # 石砖接缝
    dr.line([(px(4), SZ // 2), (SZ - px(4), SZ // 2)], fill=(50, 52, 58, 100), width=px(1))
    dr.line([(SZ // 3, px(4)), (SZ // 3, SZ // 2 - px(2))], fill=(50, 52, 58, 80), width=px(1))
    dr.line([(SZ * 2 // 3, SZ // 2 + px(2)), (SZ * 2 // 3, SZ - px(4))], fill=(50, 52, 58, 80), width=px(1))
    # 噪点
    stone_noise(dr, px(3), px(3), SZ - px(3), SZ - px(3), base, 0.2)
    # 中心问号纹（暗示隐藏内容）
    cx = cy = SZ // 2
    dr.ellipse([cx - px(4), cy - px(6), cx + px(4), cy + px(1)], fill=(75, 78, 85, 120))
    dr.rectangle([cx - px(1), cy + px(2), cx + px(1), cy + px(4)], fill=(75, 78, 85, 120))
    out = img.resize((52, 52), Image.LANCZOS)
    save(out, "ui", "cell_hidden.png")
    save(out, "ui", "cell_mine_hidden.png")

    # ── 翻开格（凹陷地砖） ──
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    base_r = (170, 162, 145)
    dr.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=px(4), fill=base_r + (255,))
    # 凹陷效果（上暗下亮）
    dr.line([(px(1), px(1)), (SZ - px(2), px(1))], fill=(140, 132, 115, 255), width=px(2))
    dr.line([(px(1), px(1)), (px(1), SZ - px(2))], fill=(145, 137, 120, 255), width=px(2))
    dr.line([(px(2), SZ - px(2)), (SZ - px(2), SZ - px(2))], fill=(195, 188, 172, 255), width=px(2))
    dr.line([(SZ - px(2), px(2)), (SZ - px(2), SZ - px(2))], fill=(192, 185, 168, 255), width=px(2))
    # 砖缝纹理
    for y in range(0, SZ, px(6)):
        dr.line([(px(3), y), (SZ - px(3), y)], fill=(155, 148, 130, 50), width=px(1))
    stone_noise(dr, px(3), px(3), SZ - px(3), SZ - px(3), base_r, 0.15)
    out = img.resize((52, 52), Image.LANCZOS)
    save(out, "ui", "cell_revealed.png")
    save(out, "ui", "cell_mine_reveal.png")

    # ── 爆炸格（岩浆裂缝） ──
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = SZ // 2
    # 外层暗红
    dr.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=px(4), fill=(120, 40, 10, 255))
    # 内层火焰
    layers = [
        (int(SZ * 0.45), (180, 60, 0, 220)),
        (int(SZ * 0.38), (220, 100, 0, 240)),
        (int(SZ * 0.30), (255, 150, 20, 250)),
        (int(SZ * 0.20), (255, 210, 80, 255)),
        (int(SZ * 0.10), (255, 245, 180, 255)),
    ]
    for r, col in layers:
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # 岩浆裂缝线
    for angle in range(0, 360, 40):
        a = math.radians(angle + random.randint(-10, 10))
        r1, r2 = SZ * 0.25, SZ * 0.44
        x1 = cx + int(r1 * math.cos(a))
        y1 = cy + int(r1 * math.sin(a))
        x2 = cx + int(r2 * math.cos(a))
        y2 = cy + int(r2 * math.sin(a))
        dr.line([x1, y1, x2, y2], fill=(255, 200, 50, 200), width=px(1))
    out = img.resize((52, 52), Image.LANCZOS)
    save(out, "ui", "cell_exploding.png")

    # ── cell_empty (空地板) ──
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    base_e = (58, 60, 68)
    dr.rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=px(4), fill=base_e + (255,))
    dr.rounded_rectangle([px(2), px(2), SZ - px(3), SZ - px(3)], radius=px(3),
                         outline=(48, 50, 58, 255), width=px(1))
    stone_noise(dr, px(3), px(3), SZ - px(3), SZ - px(3), base_e, 0.15)
    out = img.resize((52, 52), Image.LANCZOS)
    save(out, "ui", "cell_empty.png")

# ═══════════════════════════════════════
# 爆炸特效 Spritesheet 416x52 (8帧×52px)
# 火焰 + 碎石粒子 地牢风
# ═══════════════════════════════════════
def gen_explosion_sheet():
    FRAMES = 8
    FW = 52 * S
    img = Image.new("RGBA", (FW * FRAMES, FW), (0, 0, 0, 0))

    for f in range(FRAMES):
        t = f / (FRAMES - 1)
        frame = Image.new("RGBA", (FW, FW), (0, 0, 0, 0))
        dr = ImageDraw.Draw(frame)
        cx = cy = FW // 2

        max_r = int(FW * 0.45 * (0.3 + 0.7 * t))
        alpha_base = int(255 * (1 - t * 0.8))

        # 烟雾（灰色）
        if t > 0.25:
            smoke_r = int(FW * 0.48 * t)
            smoke_a = int(80 * (1 - t))
            dr.ellipse([cx - smoke_r, cy - smoke_r, cx + smoke_r, cy + smoke_r],
                       fill=(60, 55, 50, smoke_a))

        # 火焰核心
        fire_layers = [
            (1.0, (160, 50, 0)),
            (0.75, (210, 90, 0)),
            (0.55, (240, 150, 10)),
            (0.35, (255, 210, 60)),
            (0.15, (255, 245, 180)),
        ]
        for scale, color in fire_layers:
            r = int(max_r * scale)
            a = min(255, int(alpha_base * 1.1))
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))

        # 碎石粒子
        if t < 0.8:
            for i in range(6):
                angle = math.radians(i * 60 + f * 25)
                dist = int(FW * 0.38 * t)
                sx = cx + int(dist * math.cos(angle))
                sy = cy + int(dist * math.sin(angle))
                ps = max(1, int(FW * 0.035 * (1 - t)))
                # 石头碎片（灰色）
                dr.rectangle([sx - ps, sy - ps, sx + ps, sy + ps],
                             fill=(100, 95, 85, alpha_base))

        # 火花
        if t < 0.6:
            for i in range(8):
                angle = math.radians(i * 45 + f * 15)
                dist = int(FW * 0.32 * t)
                sx = cx + int(dist * math.cos(angle))
                sy = cy + int(dist * math.sin(angle))
                spark_r = max(1, int(FW * 0.025 * (1 - t)))
                dr.ellipse([sx - spark_r, sy - spark_r, sx + spark_r, sy + spark_r],
                           fill=(255, 230, 80, alpha_base))

        frame_small = frame.resize((52, 52), Image.LANCZOS)
        img.paste(frame_small, (f * 52, 0), frame_small)

    save(img.resize((52 * FRAMES, 52), Image.LANCZOS), "vfx", "explosion_strip8.png")

# ═══════════════════════════════════════
# 背景 1280x720 — 地牢石砖 + 火把光晕
# ═══════════════════════════════════════
def gen_background():
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    dr = ImageDraw.Draw(img)

    # 石砖墙（交错砌法）
    brick_w, brick_h = 64, 32
    for row in range(H // brick_h + 1):
        for col in range(W // brick_w + 2):
            offset = (brick_w // 2) if row % 2 == 1 else 0
            x = col * brick_w - offset
            y = row * brick_h
            # 石砖颜色（深灰偏暖）
            shade = 18 + (row * 7 + col * 3) % 10
            r = shade + 2
            g = shade
            b = shade - 1
            dr.rectangle([x + 1, y + 1, x + brick_w - 2, y + brick_h - 2],
                         fill=(r, g, b, 255))
            dr.rectangle([x, y, x + brick_w - 1, y + brick_h - 1],
                         outline=(8, 8, 10, 255), width=1)
            # 偶尔有苔藓
            if (row * 13 + col * 7) % 11 == 0:
                mx = x + random.randint(5, brick_w - 10)
                my = y + brick_h - 6
                dr.rectangle([mx, my, mx + 4, my + 3], fill=(25, 40, 20, 80))

    # 火把光晕（左右各一个暖色光源）
    torch_positions = [(160, 240), (1120, 240), (640, 120)]
    for tx, ty in torch_positions:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdr = ImageDraw.Draw(glow)
        for i in range(120, 0, -2):
            alpha = int(25 * (i / 120) ** 2)
            gdr.ellipse([tx - i * 2, ty - i * 2, tx + i * 2, ty + i * 2],
                        fill=(180, 120, 40, alpha))
        img = Image.alpha_composite(img, glow)

    # 四周暗角
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vdr = ImageDraw.Draw(vignette)
    for i in range(250):
        alpha = int(200 * (1 - i / 250) ** 2.5)
        vdr.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, alpha), width=1)
    img = Image.alpha_composite(img, vignette)

    save(img, "ui", "background.png")

# ═══════════════════════════════════════
# HUD 图标 — 像素地牢风 (32x32 放大版)
# ═══════════════════════════════════════
def gen_hud():
    s = S
    sz = 32 * s

    # ── HP 心形图标 ──
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = sz // 2, sz // 2 + px(1)
    hr = sz // 5
    # 心形主体（深红宝石色）
    dr.ellipse([cx - hr * 2, cy - hr, cx, cy + hr], fill=(165, 28, 38, 255))
    dr.ellipse([cx, cy - hr, cx + hr * 2, cy + hr], fill=(165, 28, 38, 255))
    dr.polygon([(cx - hr * 2 + px(1), cy), (cx + hr * 2 - px(1), cy), (cx, cy + hr * 2 + px(2))],
               fill=(165, 28, 38, 255))
    # 外描边
    dr.ellipse([cx - hr * 2 - px(1), cy - hr - px(1), cx + px(1), cy + hr + px(1)],
               outline=(90, 12, 18, 200), width=px(1))
    dr.ellipse([cx - px(1), cy - hr - px(1), cx + hr * 2 + px(1), cy + hr + px(1)],
               outline=(90, 12, 18, 200), width=px(1))
    # 宝石高光
    dr.ellipse([cx - hr + px(1), cy - hr + px(1), cx - px(1), cy + px(1)],
               fill=(230, 100, 110, 150))
    dr.ellipse([cx - hr + px(2), cy - hr + px(2), cx - px(3), cy - px(1)],
               fill=(255, 180, 185, 120))
    out = img.resize((32, 32), Image.LANCZOS)
    save(out, "ui", "icon_hp.png")

    # ── 炸弹库存图标 ──
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = sz // 2
    r = sz // 2 - px(4)
    # 阴影
    dr.ellipse([cx - r + px(2), cy - r + px(3), cx + r + px(2), cy + r + px(3)],
               fill=(0, 0, 0, 50))
    # 铁球体
    dr.ellipse([cx - r, cy - r + px(1), cx + r, cy + r + px(1)],
               fill=(35, 38, 45, 255), outline=(55, 58, 65, 255), width=px(1))
    # 内环反光
    ir = r - px(2)
    dr.ellipse([cx - ir, cy - ir + px(1), cx + ir, cy + ir + px(1)],
               fill=(48, 52, 60, 255))
    # 高光
    dr.ellipse([cx - ir + px(1), cy - ir + px(1), cx - ir + px(5), cy - ir + px(5)],
               fill=(120, 125, 135, 180))
    # 引线
    fx1 = cx + int(r * 0.3)
    fy1 = cy - int(r * 0.7)
    fx2 = cx + r
    fy2 = cy - r - px(3)
    dr.line([fx1, fy1, fx2, fy2], fill=(150, 120, 45, 255), width=px(2))
    # 火花
    dr.ellipse([fx2 - px(3), fy2 - px(3), fx2 + px(3), fy2 + px(3)],
               fill=(255, 200, 50, 255))
    dr.ellipse([fx2 - px(1), fy2 - px(1), fx2 + px(1), fy2 + px(1)],
               fill=(255, 245, 190, 255))
    # 小火花射线
    for angle in [30, 90, 150, 210, 330]:
        a = math.radians(angle)
        sx = fx2 + int(px(4) * math.cos(a))
        sy = fy2 + int(px(4) * math.sin(a))
        dr.line([fx2, fy2, sx, sy], fill=(255, 220, 80, 180), width=px(1))
    out = img.resize((32, 32), Image.LANCZOS)
    save(out, "ui", "icon_bomb.png")

    # ── 计时器沙漏图标 ──
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = sz // 2
    # 上下框
    dr.rectangle([cx - px(5), px(2), cx + px(5), px(4)], fill=(160, 140, 90, 255))
    dr.rectangle([cx - px(5), sz - px(4), cx + px(5), sz - px(2)], fill=(160, 140, 90, 255))
    # 玻璃体
    pts_top = [(cx - px(4), px(4)), (cx + px(4), px(4)), (cx + px(1), sz // 2 - px(1)), (cx - px(1), sz // 2 - px(1))]
    pts_bot = [(cx - px(1), sz // 2 + px(1)), (cx + px(1), sz // 2 + px(1)), (cx + px(4), sz - px(4)), (cx - px(4), sz - px(4))]
    dr.polygon(pts_top, fill=(180, 170, 140, 100), outline=(140, 125, 80, 200))
    dr.polygon(pts_bot, fill=(180, 170, 140, 100), outline=(140, 125, 80, 200))
    # 沙子（上半）
    sand_h = int(sz * 0.15)
    for dy in range(sand_h):
        w = int(px(3) * (1 - dy / sand_h))
        if w < 1:
            break
        y = px(5) + dy
        dr.line([cx - w, y, cx + w, y], fill=(210, 180, 90, 200))
    # 沙子（下半）
    for dy in range(sand_h * 2):
        w = int(px(3.5) * (dy / (sand_h * 2)))
        y = sz - px(5) - dy
        dr.line([cx - w, y, cx + w, y], fill=(210, 180, 90, 220))
    # 流沙中线
    dr.line([cx, sz // 2 - px(2), cx, sz // 2 + px(2)], fill=(210, 180, 90, 160), width=px(1))
    out = img.resize((32, 32), Image.LANCZOS)
    save(out, "ui", "icon_timer.png")

    # ── 楼层阶梯图标 ──
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    stairs = [
        (px(2), sz - px(4), px(8), sz - px(2)),
        (px(6), sz - px(8), px(12), sz - px(4)),
        (px(10), sz - px(12), px(16), sz - px(8)),
        (px(14), sz - px(16), px(20), sz - px(12)),
    ]
    for x1, y1, x2, y2 in stairs:
        dr.rectangle([x1, y1, x2, y2], fill=(100, 90, 70, 255), outline=(65, 58, 45, 255), width=px(1))
        dr.line([(x1 + px(1), y1 + px(1)), (x2 - px(1), y1 + px(1))],
                fill=(130, 120, 95, 150), width=px(1))
    # 向上箭头
    ax = px(18)
    dr.polygon([(ax, px(3)), (ax - px(3), px(8)), (ax + px(3), px(8))],
               fill=(200, 175, 100, 220))
    dr.rectangle([ax - px(1), px(8), ax + px(1), px(13)], fill=(200, 175, 100, 220))
    out = img.resize((32, 32), Image.LANCZOS)
    save(out, "ui", "icon_floor.png")

    # ── 扫雷点击图标（十字准星） ──
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = sz // 2
    r_out = px(6)
    r_in = px(2)
    col = (180, 170, 140, 220)
    dr.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], outline=col, width=px(1))
    dr.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=col)
    dr.line([cx, cy - r_out - px(2), cx, cy - r_out + px(1)], fill=col, width=px(1))
    dr.line([cx, cy + r_out - px(1), cx, cy + r_out + px(2)], fill=col, width=px(1))
    dr.line([cx - r_out - px(2), cy, cx - r_out + px(1), cy], fill=col, width=px(1))
    dr.line([cx + r_out - px(1), cy, cx + r_out + px(2), cy], fill=col, width=px(1))
    out = img.resize((32, 32), Image.LANCZOS)
    save(out, "ui", "icon_click.png")

if __name__ == "__main__":
    gen_mine_cells()
    gen_explosion_sheet()
    gen_background()
    gen_hud()
    print("=== All assets generated ===")
