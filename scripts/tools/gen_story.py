"""
生成游戏开始界面和故事过场的 8-bit 风格图片
输出到 assets/sprites/story/ 和 assets/sprites/ui/
高质量像素画 — 多层大气效果 + 细节丰富
"""

from PIL import Image, ImageDraw, ImageFilter
import os, math, random

OUT_STORY = "assets/sprites/story"
OUT_UI    = "assets/sprites/ui"
os.makedirs(OUT_STORY, exist_ok=True)
os.makedirs(OUT_UI,    exist_ok=True)

W, H = 640, 360   # 16:9，像素风分辨率

# ── 调色板 ────────────────────────────────────────────────────
BG_DEEP   = (8,   6,  14)
BG_DARK   = (18,  14,  28)
STONE     = (52,  48,  64)
STONE_LT  = (82,  76,  96)
STONE_DK  = (36,  32,  48)
GOLD      = (242, 196,  60)
GOLD_DK   = (160, 120,  20)
RED       = (210,  48,  48)
RED_LT    = (240,  90,  80)
RED_DK    = (120,  25,  20)
GREEN     = (60,  200,  80)
GREEN_DK  = (30,  120,  40)
GREEN_VDK = (18,  60,   28)
BLUE      = (60,  120, 220)
BLUE_LT   = (100, 180, 255)
BLUE_DK   = (20,   40, 100)
PURPLE    = (140,  60, 200)
PURPLE_LT = (200, 120, 255)
PURPLE_DK = (60,   25,  90)
WHITE     = (240, 235, 220)
GRAY      = (140, 134, 150)
GRAY_DK   = (80,  74,  90)
ORANGE    = (230, 140,  40)
ORANGE_LT = (255, 190,  80)
PINK      = (240, 140, 180)
CYAN      = (60,  210, 210)
BLACK     = (0,    0,    0)
SKIN      = (230, 180, 140)
SKIN_DK   = (190, 140, 100)

def new_img(bg=BG_DEEP):
    img = Image.new("RGBA", (W, H), bg + (255,))
    return img, ImageDraw.Draw(img)

def px(d, x, y, col, s=2):
    d.rectangle([x*s, y*s, x*s+s-1, y*s+s-1], fill=col)

def rect(d, x1, y1, x2, y2, col):
    d.rectangle([x1, y1, x2, y2], fill=col)

# ── 大气效果 ──────────────────────────────────────────────────

def draw_gradient(d, y1, y2, col_top, col_bot):
    for y in range(y1, y2):
        t = (y - y1) / max(1, y2 - y1)
        r = int(col_top[0] + (col_bot[0] - col_top[0]) * t)
        g = int(col_top[1] + (col_bot[1] - col_top[1]) * t)
        b = int(col_top[2] + (col_bot[2] - col_top[2]) * t)
        d.line([(0, y), (W-1, y)], fill=(r, g, b, 255))

def draw_stars(d, seed=42, count=80, y_max=None):
    rng = random.Random(seed)
    ym = y_max or (H // 2)
    for _ in range(count):
        sx, sy = rng.randint(0, W-1), rng.randint(0, ym)
        br = rng.randint(140, 255)
        size = rng.choice([1, 1, 1, 2])
        twinkle = rng.random()
        if twinkle > 0.85:
            # 十字星
            d.point((sx, sy), fill=(br, br, br - 20, 255))
            for off in range(1, size + 1):
                dim = max(60, br - off * 50)
                for dx2, dy2 in [(off, 0), (-off, 0), (0, off), (0, -off)]:
                    nx, ny = sx + dx2, sy + dy2
                    if 0 <= nx < W and 0 <= ny < H:
                        d.point((nx, ny), fill=(dim, dim, dim - 10, 200))
        else:
            d.point((sx, sy), fill=(br, br, br - 20, 255))
            if size == 2:
                d.point((sx + 1, sy), fill=(br - 30, br - 30, br - 40, 200))

def draw_fog(d, y_base, thickness=40, col=(60, 55, 80), alpha=50, seed=10):
    rng = random.Random(seed)
    for _ in range(thickness * 3):
        fx = rng.randint(0, W - 1)
        fy = y_base + rng.randint(-thickness, thickness)
        fw = rng.randint(20, 80)
        fh = rng.randint(4, 12)
        fa = max(5, alpha - abs(fy - y_base))
        d.ellipse([fx, fy, fx + fw, fy + fh], fill=col + (fa,))

def draw_particles(d, x1, y1, x2, y2, col, count=20, seed=0, size_range=(1, 3)):
    rng = random.Random(seed)
    for _ in range(count):
        px2 = rng.randint(x1, x2)
        py2 = rng.randint(y1, y2)
        ps = rng.randint(size_range[0], size_range[1])
        pa = rng.randint(80, 220)
        d.ellipse([px2, py2, px2 + ps, py2 + ps], fill=col[:3] + (pa,))

def draw_light_rays(d, cx, cy, count=8, length=120, col=(255, 240, 180), seed=77):
    rng = random.Random(seed)
    for i in range(count):
        angle = (i / count) * math.pi * 2 + rng.uniform(-0.2, 0.2)
        ln = length + rng.randint(-30, 30)
        ex = int(cx + math.cos(angle) * ln)
        ey = int(cy + math.sin(angle) * ln)
        for w in range(3, 0, -1):
            a = 15 + (3 - w) * 8
            d.line([(cx, cy), (ex, ey)], fill=col + (a,), width=w)

def draw_vignette(img, strength=0.6):
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    cx, cy = W // 2, H // 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)
    for ring in range(0, int(max_dist), 3):
        t = ring / max_dist
        a = int(255 * strength * (t ** 2))
        a = min(255, a)
        vd.ellipse([cx - ring, cy - ring, cx + ring, cy + ring], outline=(0, 0, 0, a), width=3)
    img.paste(Image.alpha_composite(img, vig))

# ── 精灵绘制 ─────────────────────────────────────────────────

def draw_sprite(d, ox, oy, data, palette, s=3):
    for row, line in enumerate(data):
        for col, ch in enumerate(line):
            c = palette.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + row) * s,
                             (ox + col) * s + s - 1, (oy + row) * s + s - 1], fill=c)

def draw_bomber(d, ox, oy, s=4, facing=1):
    head = [
        "..HHHH..",
        ".HHGGHH.",
        ".HGWWGH.",
        "HHFFF.HH",
        ".HHHHH..",
    ]
    body = [
        "..OOOO..",
        ".OOOOOO.",
        ".OOBBOOO",
        ".OOOOOO.",
        "..OOOO..",
        ".O.OO.O.",
        "SS.SS.SS",
        "SS..SS..",
    ]
    pal_h = {'.': None, 'H': (50, 165, 60), 'G': (35, 130, 45), 'W': WHITE, 'F': SKIN}
    pal_b = {'.': None, 'O': ORANGE, 'B': (180, 80, 20), 'S': (70, 45, 25)}
    for row, line in enumerate(head):
        for col, ch in enumerate(line):
            c = pal_h.get(ch)
            if c:
                bx = ox + (col if facing == 1 else (len(line) - 1 - col))
                d.rectangle([bx * s, (oy + row) * s, bx * s + s - 1, (oy + row) * s + s - 1], fill=c)
    for row, line in enumerate(body):
        for col, ch in enumerate(line):
            c = pal_b.get(ch)
            if c:
                bx = ox + (col if facing == 1 else (len(line) - 1 - col))
                d.rectangle([bx * s, (oy + 5 + row) * s, bx * s + s - 1, (oy + 5 + row) * s + s - 1], fill=c)

def draw_princess(d, ox, oy, s=3):
    crown = [
        "..G.G.G..",
        "..GGGGG..",
        "..GRGEG..",
    ]
    head = [
        ".MMMMM.",
        "MMMWWMM",
        "M.FWFM.",
        ".FFFFF.",
        "..FMF..",
    ]
    body = [
        "..PPP..",
        ".PPPPP.",
        "PPPPPPP",
        "PPPPPPP",
        ".PPPPP.",
        ".PP.PP.",
    ]
    pal_c = {'.': None, 'G': GOLD, 'R': RED, 'E': (60, 200, 220)}
    pal_h = {'.': None, 'M': (180, 50, 140), 'W': WHITE, 'F': SKIN}
    pal_b = {'.': None, 'P': PINK}
    for row, line in enumerate(crown):
        for col, ch in enumerate(line):
            c = pal_c.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + row) * s,
                             (ox + col) * s + s - 1, (oy + row) * s + s - 1], fill=c)
    for row, line in enumerate(head):
        for col, ch in enumerate(line):
            c = pal_h.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + 3 + row) * s,
                             (ox + col) * s + s - 1, (oy + 3 + row) * s + s - 1], fill=c)
    for row, line in enumerate(body):
        for col, ch in enumerate(line):
            c = pal_b.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + 8 + row) * s,
                             (ox + col) * s + s - 1, (oy + 8 + row) * s + s - 1], fill=c)

def draw_demon(d, ox, oy, s=4):
    horns = [
        "P..........P",
        ".P........P.",
        "..PP....PP..",
    ]
    head = [
        "..PPPPPP..",
        ".PPPPPPPP.",
        "PPRRPPRRPP",
        "PP.RPP.RPP",
        "PPPPPPPPPP",
        ".PPMMMPP.",
        "..PPPPPP..",
    ]
    body = [
        "..DDDDDD..",
        ".DDDDDDDD.",
        "DDDDDDDDDD",
        "DDDDDDDDDD",
        ".DDD..DDD.",
        "DDD....DDD",
    ]
    pal_horn = {'.': None, 'P': PURPLE_LT}
    pal_head = {'.': None, 'P': PURPLE, 'R': RED, 'M': (100, 30, 30)}
    pal_body = {'.': None, 'D': PURPLE_DK}
    for row, line in enumerate(horns):
        for col, ch in enumerate(line):
            c = pal_horn.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + row) * s,
                             (ox + col) * s + s - 1, (oy + row) * s + s - 1], fill=c)
    for row, line in enumerate(head):
        for col, ch in enumerate(line):
            c = pal_head.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + 3 + row) * s,
                             (ox + col) * s + s - 1, (oy + 3 + row) * s + s - 1], fill=c)
    for row, line in enumerate(body):
        for col, ch in enumerate(line):
            c = pal_body.get(ch)
            if c:
                d.rectangle([(ox + col) * s, (oy + 10 + row) * s,
                             (ox + col) * s + s - 1, (oy + 10 + row) * s + s - 1], fill=c)
    # 眼睛发光
    eye_cx1, eye_cx2 = (ox + 3) * s + s // 2, (ox + 7) * s + s // 2
    eye_cy = (oy + 5) * s + s // 2
    for r in range(s * 2, 0, -1):
        a = 40 + (s * 2 - r) * 20
        d.ellipse([eye_cx1 - r, eye_cy - r, eye_cx1 + r, eye_cy + r], fill=(255, 50, 30, min(255, a)))
        d.ellipse([eye_cx2 - r, eye_cy - r, eye_cx2 + r, eye_cy + r], fill=(255, 50, 30, min(255, a)))

def draw_bomb_item(d, cx, cy, s=8):
    # 圆形炸弹
    r = s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 30, 30, 255))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=(50, 50, 50, 255))
    # 高光
    d.ellipse([cx - r + 3, cy - r + 3, cx - r + 5, cy - r + 5], fill=(100, 100, 100, 180))
    # 引信
    d.line([(cx, cy - r), (cx + 3, cy - r - 5)], fill=ORANGE, width=2)
    d.ellipse([cx + 1, cy - r - 8, cx + 5, cy - r - 4], fill=GOLD)

def draw_castle(d, ox, oy, s=2):
    # 主体
    rect(d, ox * s, (oy + 12) * s, (ox + 40) * s, (oy + 45) * s, STONE)
    # 塔楼
    rect(d, ox * s, (oy + 2) * s, (ox + 10) * s, (oy + 20) * s, STONE_LT)
    rect(d, (ox + 30) * s, (oy + 2) * s, (ox + 40) * s, (oy + 20) * s, STONE_LT)
    # 中央高塔
    rect(d, (ox + 14) * s, (oy) * s, (ox + 26) * s, (oy + 15) * s, STONE)
    # 城垛
    for base_x in [ox, ox + 30]:
        for i in range(0, 10, 3):
            rect(d, (base_x + i) * s, (oy) * s, (base_x + i + 1) * s + 1, (oy + 2) * s, STONE_LT)
    for i in range(14, 26, 3):
        rect(d, (ox + i) * s, (oy - 2) * s, (ox + i + 1) * s + 1, (oy) * s, STONE_LT)
    # 城门
    d.ellipse([(ox + 15) * s, (oy + 26) * s, (ox + 25) * s, (oy + 34) * s], fill=BG_DEEP)
    rect(d, (ox + 15) * s, (oy + 30) * s, (ox + 25) * s, (oy + 45) * s, BG_DEEP)
    # 窗户（发光）
    for wx in [ox + 4, ox + 34]:
        rect(d, wx * s, (oy + 6) * s, (wx + 3) * s, (oy + 10) * s, GOLD)
        rect(d, (wx + 1) * s, (oy + 7) * s, (wx + 2) * s, (oy + 9) * s, (255, 240, 180, 255))
    # 中央大窗
    rect(d, (ox + 18) * s, (oy + 4) * s, (ox + 22) * s, (oy + 10) * s, GOLD)
    draw_light_rays(d, (ox + 20) * s, (oy + 7) * s, count=6, length=20, col=(255, 240, 160))
    # 旗帜
    flag_x = (ox + 20) * s
    flag_y = (oy - 2) * s
    d.line([(flag_x, flag_y), (flag_x, flag_y - 16)], fill=GRAY, width=2)
    d.polygon([(flag_x, flag_y - 16), (flag_x + 12, flag_y - 12), (flag_x, flag_y - 8)], fill=RED)

def draw_dungeon_grid(d, y_start, cell_size=22, seed=42):
    rng = random.Random(seed)
    for gy in range(y_start, H - 10, cell_size):
        for gx in range(10, W - 10, cell_size):
            shade = rng.randint(40, 60)
            d.rectangle([gx, gy, gx + cell_size - 2, gy + cell_size - 2],
                        fill=(shade, shade - 5, shade + 10, 255))
            # 石缝
            d.rectangle([gx, gy, gx + cell_size - 2, gy + 1], fill=(shade + 15, shade + 10, shade + 20, 255))
            d.rectangle([gx, gy, gx + 1, gy + cell_size - 2], fill=(shade + 10, shade + 8, shade + 15, 255))

def draw_lightning(d, start_x, start_y, end_y, seed=55, width=3, col=GOLD):
    rng = random.Random(seed)
    x = start_x
    pts = [(x, start_y)]
    y = start_y
    while y < end_y:
        y += rng.randint(8, 20)
        x += rng.randint(-15, 15)
        pts.append((x, min(y, end_y)))
    # 外光晕
    d.line(pts, fill=col + (80,), width=width + 4)
    d.line(pts, fill=col + (160,), width=width + 2)
    d.line(pts, fill=(255, 255, 240, 255), width=width)

# ═══════════════════════════════════════════════════════════════
# 故事帧
# ═══════════════════════════════════════════════════════════════

def save_frame(img, filename):
    out = img.convert("RGB")
    out.save(f"{OUT_STORY}/{filename}")
    print(f"  [story] {filename}")


# ── 帧 1：王国平和 ───────────────────────────────────────────

def frame1():
    img, d = new_img()
    # 夜空渐变
    draw_gradient(d, 0, H // 2, (8, 10, 35), (18, 25, 55))
    draw_stars(d, seed=1, count=100, y_max=H // 2)
    # 远景山脉
    for mx in range(0, W + 40, 3):
        my = int(H * 0.42 + math.sin(mx * 0.012) * 30 + math.sin(mx * 0.003) * 50)
        d.line([(mx, my), (mx, H // 2 + 40)], fill=(15, 18, 35, 255))
    # 草地
    draw_gradient(d, H // 2, H, GREEN_VDK, (12, 40, 18))
    rng = random.Random(11)
    for gx in range(0, W, 5):
        gh = rng.randint(2, 8)
        shade = rng.randint(0, 20)
        d.line([(gx, H // 2 - gh), (gx, H // 2 + 2)],
               fill=(40 + shade, 140 + shade, 50 + shade, 255), width=2)
    # 城堡
    draw_castle(d, 110, 30, s=3)
    # 月亮 + 光晕
    moon_x, moon_y = 520, 50
    for r in range(40, 0, -2):
        a = int(15 + (40 - r) * 2)
        d.ellipse([moon_x - r, moon_y - r, moon_x + r, moon_y + r],
                  fill=(200, 195, 160, a))
    d.ellipse([moon_x - 18, moon_y - 18, moon_x + 18, moon_y + 18], fill=(230, 225, 195, 255))
    d.ellipse([moon_x - 10, moon_y - 20, moon_x + 16, moon_y + 8], fill=(8, 10, 35, 255))
    # 萤火虫
    draw_particles(d, 40, H // 2 - 30, W - 40, H - 20, (180, 255, 100, 200), count=15, seed=33, size_range=(1, 3))
    # 雾气
    draw_fog(d, H // 2, thickness=30, col=(60, 80, 70), alpha=35, seed=22)
    draw_vignette(img, strength=0.5)
    save_frame(img, "story_01_kingdom.png")


# ── 帧 2：魔王降临，公主被抓 ─────────────────────────────────

def frame2():
    img, d = new_img()
    # 血色天空
    draw_gradient(d, 0, H // 2, (40, 5, 10), (80, 15, 15))
    draw_gradient(d, H // 2, H, (25, 10, 18), (10, 5, 8))
    draw_stars(d, seed=2, count=30, y_max=H // 3)
    # 闪电裂缝
    draw_lightning(d, 160, 0, 200, seed=55, width=2)
    draw_lightning(d, 450, 0, 180, seed=66, width=2)
    draw_lightning(d, 300, 0, 150, seed=77, width=3, col=(255, 180, 100))
    # 魔王（大，居中偏左）
    draw_demon(d, 20, 15, s=5)
    # 魔法漩涡（魔王周围）
    cx_v, cy_v = 170, 140
    for r in range(80, 10, -5):
        a = int(20 + (80 - r) * 0.8)
        d.ellipse([cx_v - r, cy_v - r, cx_v + r, cy_v + r],
                  outline=PURPLE + (a,), width=2)
    # 公主被困（右侧，笼子）
    cage_x, cage_y = 430, 130
    rect(d, cage_x, cage_y, cage_x + 70, cage_y + 100, (20, 15, 30, 180))
    for bar_x in range(cage_x, cage_x + 72, 8):
        d.line([(bar_x, cage_y), (bar_x, cage_y + 100)], fill=GRAY + (200,), width=2)
    d.line([(cage_x, cage_y), (cage_x + 70, cage_y)], fill=GRAY + (200,), width=2)
    draw_princess(d, (cage_x + 20) // 3, (cage_y + 20) // 3, s=3)
    # 红色粒子
    draw_particles(d, 0, 0, W, H // 2, (255, 60, 30, 255), count=40, seed=44, size_range=(1, 3))
    # 地面裂缝
    rng = random.Random(88)
    for _ in range(8):
        cx = rng.randint(50, W - 50)
        cy = rng.randint(H * 2 // 3, H - 20)
        d.line([(cx, cy), (cx + rng.randint(-20, 20), cy + rng.randint(5, 15))],
               fill=(180, 40, 20, 200), width=2)
    draw_fog(d, H * 2 // 3, thickness=40, col=(80, 20, 20), alpha=40, seed=33)
    draw_vignette(img, strength=0.7)
    save_frame(img, "story_02_kidnap.png")


# ── 帧 2b：炸弹被夺走 ───────────────────────────────────────

def frame2b():
    img, d = new_img()
    # 暗紫天空
    draw_gradient(d, 0, H, (30, 10, 40), (10, 5, 15))
    # 魔王（右侧，拖着炸弹）
    draw_demon(d, 90, 20, s=4)
    # 紫色吸收光环
    cx_a, cy_a = 320, 200
    for r in range(70, 5, -3):
        a = int(15 + (70 - r) * 0.7)
        angle_off = r * 0.1
        d.ellipse([cx_a - r, cy_a - int(r * 0.6), cx_a + r, cy_a + int(r * 0.6)],
                  outline=PURPLE_LT + (a,), width=2)
    # 被吸走的炸弹（环绕光环）
    bomb_pts = [(280, 170), (320, 155), (360, 168), (340, 200), (290, 210), (310, 230)]
    for bx, by in bomb_pts:
        draw_bomb_item(d, bx, by, s=6)
    # 左侧：失去武器的炸弹人（跪地）
    draw_bomber(d, 10, 50, s=4, facing=1)
    # 绝望的气氛 - 黑色粒子下落
    draw_particles(d, 0, 0, W, H, (20, 10, 30, 255), count=30, seed=99, size_range=(2, 5))
    # 地面废墟碎石
    rng = random.Random(55)
    for _ in range(15):
        rx = rng.randint(20, 250)
        ry = rng.randint(H * 3 // 4, H - 5)
        rs = rng.randint(3, 8)
        d.rectangle([rx, ry, rx + rs, ry + rs // 2], fill=STONE_DK)
    draw_fog(d, H * 3 // 4, thickness=30, col=(40, 20, 50), alpha=45, seed=11)
    draw_vignette(img, strength=0.65)
    save_frame(img, "story_02b_bombs_stolen.png")


# ── 帧 3：英雄站起来 ────────────────────────────────────────

def frame3():
    img, d = new_img()
    # 地牢内部背景
    draw_gradient(d, 0, H, (12, 10, 20), (8, 6, 14))
    # 石墙纹理
    rng = random.Random(33)
    for ty in range(0, H, 16):
        offset = 8 if (ty // 16) % 2 else 0
        for tx in range(0 - offset, W + 16, 32):
            shade = rng.randint(35, 55)
            d.rectangle([tx, ty, tx + 30, ty + 14], fill=(shade, shade - 3, shade + 8, 255))
            d.rectangle([tx + 1, ty + 1, tx + 29, ty + 1], fill=(shade + 12, shade + 8, shade + 15, 255))
    # 中央光源（炸弹人背后的光）
    cx_l, cy_l = W // 2, H // 2 - 20
    for r in range(140, 0, -2):
        a = int(6 + (140 - r) * 0.15)
        d.ellipse([cx_l - r, cy_l - r, cx_l + r, cy_l + r], fill=(255, 200, 80, a))
    # 炸弹人（居中，大，英雄姿态）
    draw_bomber(d, W // (4 * 2) - 4, H // (4 * 2) - 8, s=5, facing=1)
    # 火把（左右）
    for tx in [30, W - 50]:
        d.rectangle([tx, 60, tx + 8, 160], fill=(80, 55, 20, 255))
        for fr in range(16, 0, -2):
            a = int(60 + (16 - fr) * 12)
            d.ellipse([tx - fr + 4, 40 - fr, tx + fr + 4, 50 + fr // 2],
                      fill=(255, min(255, 120 + fr * 8), 20, min(255, a)))
    # 散落的零星炸弹（预示着希望）
    for bx, by in [(380, 250), (420, 240), (460, 260)]:
        draw_bomb_item(d, bx, by, s=7)
    # 灰尘粒子
    draw_particles(d, 0, 0, W, H, (200, 190, 160, 255), count=25, seed=44, size_range=(1, 2))
    draw_vignette(img, strength=0.55)
    save_frame(img, "story_03_hero.png")


# ── 帧 4：进入地牢探索 ──────────────────────────────────────

def frame4():
    img, d = new_img()
    draw_gradient(d, 0, H, (10, 8, 18), (6, 4, 10))
    # 地牢网格（扫雷区暗示）
    draw_dungeon_grid(d, 160, cell_size=24, seed=42)
    # 部分格子发红光（隐藏炸弹暗示）
    rng = random.Random(77)
    glow_cells = [(68, 184), (164, 208), (260, 160), (356, 184), (452, 208), (116, 232)]
    for gx, gy in glow_cells:
        for r in range(14, 0, -2):
            a = int(15 + (14 - r) * 4)
            d.ellipse([gx + 11 - r, gy + 11 - r, gx + 11 + r, gy + 11 + r],
                      fill=(200, 50, 30, a))
        d.rectangle([gx + 6, gy + 6, gx + 16, gy + 16], fill=RED)
    # 问号方块（顶部）
    for qx in range(200, 480, 60):
        d.rectangle([qx, 80, qx + 36, 116], fill=STONE_LT)
        d.rectangle([qx + 2, 82, qx + 34, 114], fill=STONE)
        # 金色问号
        pts = [(qx + 12, 88), (qx + 18, 86), (qx + 22, 90), (qx + 18, 96), (qx + 16, 100)]
        d.line(pts, fill=GOLD, width=2)
        d.rectangle([qx + 15, 104, qx + 18, 107], fill=GOLD)
    # 炸弹人（左上角，小，进入地牢）
    draw_bomber(d, 10, 30, s=3, facing=1)
    # 蓝色手电光线（炸弹人发出）
    d.polygon([(60, 120), (200, 130), (200, 170), (60, 150)], fill=(80, 140, 220, 30))
    d.polygon([(60, 128), (160, 138), (160, 158), (60, 142)], fill=(100, 180, 255, 20))
    # 暗雾
    draw_fog(d, 150, thickness=25, col=(30, 25, 50), alpha=50, seed=55)
    draw_fog(d, H - 30, thickness=20, col=(20, 15, 35), alpha=60, seed=66)
    draw_vignette(img, strength=0.7)
    save_frame(img, "story_04_dungeon.png")


# ── 帧 5：出发！爆炸胜利 ────────────────────────────────────

def frame5():
    img, d = new_img()
    # 爆炸背景渐变
    draw_gradient(d, 0, H, (60, 20, 8), (30, 8, 4))
    # 中央大爆炸
    cx_e, cy_e = W // 2, H // 2
    for r in range(180, 0, -3):
        t = (180 - r) / 180
        er = int(200 + t * 55)
        eg = int(80 + t * 160)
        eb = int(10 + t * 40)
        a = int(40 + t * 200)
        d.ellipse([cx_e - r, cy_e - r, cx_e + r, cy_e + r], fill=(min(255, er), min(255, eg), eb, min(255, a)))
    # 爆炸光线
    draw_light_rays(d, cx_e, cy_e, count=16, length=200, col=(255, 220, 100))
    # Boss碎片飞散
    offsets = [(-100, -70), (100, -80), (-90, 70), (110, 60)]
    for ox2, oy2 in offsets:
        fx, fy = cx_e + ox2, cy_e + oy2
        draw_demon(d, fx // 4 - 4, fy // 4, s=2)
    # 炸弹人胜利姿态（上方）
    draw_bomber(d, W // (5 * 2) - 2, 10, s=5, facing=1)
    # 公主（远处，自由了）
    draw_princess(d, W // (3 * 2) + 20, 15, s=3)
    # 星星爆炸粒子
    draw_particles(d, 30, 30, W - 30, H - 30, GOLD, count=50, seed=55, size_range=(2, 5))
    draw_particles(d, 50, 50, W - 50, H - 50, WHITE, count=30, seed=66, size_range=(1, 3))
    draw_particles(d, 0, 0, W, H, ORANGE_LT, count=20, seed=77, size_range=(3, 6))
    draw_vignette(img, strength=0.35)
    save_frame(img, "story_05_victory.png")


# ── 标题画面背景 ──────────────────────────────────────────────

def gen_title_bg():
    img, d = new_img()
    # 深邃地牢天空
    draw_gradient(d, 0, H, (8, 6, 18), (18, 14, 30))
    draw_stars(d, seed=99, count=60)
    # 远处城堡剪影
    rng = random.Random(42)
    for tx in range(0, W, 100):
        h2 = rng.randint(80, 150)
        d.rectangle([tx, H - h2, tx + 70, H], fill=(20, 16, 28, 255))
        for tip_x in [tx + 5, tx + 30, tx + 55]:
            d.polygon([(tip_x, H - h2 - 15), (tip_x + 8, H - h2), (tip_x + 16, H - h2)],
                      fill=(16, 12, 24, 255))
    # 地牢墙壁
    for ty in range(H - 60, H, 14):
        for tx2 in range(0, W, 50):
            d.rectangle([tx2, ty, tx2 + 46, ty + 12], fill=STONE + (255,))
    # 炸弹人
    draw_bomber(d, 55, 45, s=5, facing=1)
    # 公主
    draw_princess(d, 110, 40, s=4)
    # 炸弹
    for bx, by in [(40, 280), (70, 290), (520, 275), (550, 290), (580, 280)]:
        draw_bomb_item(d, bx, by, s=7)
    # 雾气
    draw_fog(d, H - 80, thickness=40, col=(40, 35, 55), alpha=40, seed=88)
    draw_vignette(img, strength=0.5)
    out = img.convert("RGB")
    out.save(f"{OUT_UI}/title_bg.png")
    print("  [ui] title_bg.png")


# ── 主程序 ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating story frames...")
    frame1()
    frame2()
    frame2b()
    frame3()
    frame4()
    frame5()
    gen_title_bg()
    print("Done!")
