"""
generate_backgrounds.py
Generates all dungeon background sprites for AGame floors 1-20 plus
special screens. Output: 640x360 PNG files in assets/sprites/bg/
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = r"Q:\AGame\assets\sprites\bg"
W, H = 640, 360

os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(42)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def lerp_color(c1, c2, t):
    return tuple(clamp(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def make_gradient(img, top_color, bot_color):
    """Fill image with vertical gradient."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = lerp_color(top_color, bot_color, t)
        draw.line([(0, y), (W, y)], fill=c)


def add_noise(img, intensity=12, color_shift=(0, 0, 0)):
    """Add subtle pixel noise for stone texture."""
    px = img.load()
    for y in range(H):
        for x in range(W):
            if random.random() < 0.15:
                d = random.randint(-intensity, intensity)
                r, g, b = px[x, y]
                px[x, y] = (
                    clamp(r + d + color_shift[0]),
                    clamp(g + d + color_shift[1]),
                    clamp(b + d + color_shift[2]),
                )


def draw_stones(draw, base_color, highlight, shadow, rows=6, cols=8, offset_y=60):
    """Draw brick/stone grid with offset rows."""
    bw = W // cols
    bh = (H - offset_y) // rows
    for row in range(rows + 1):
        for col in range(cols + 1):
            ox = (bw // 2) if row % 2 == 1 else 0
            x = col * bw - ox
            y = offset_y + row * bh
            # stone fill with slight variation
            shade = random.randint(-10, 10)
            c = tuple(clamp(base_color[i] + shade) for i in range(3))
            draw.rectangle([x + 1, y + 1, x + bw - 2, y + bh - 2], fill=c)
            # mortar shadow lines
            draw.line([(x, y), (x + bw, y)], fill=shadow)
            draw.line([(x, y), (x, y + bh)], fill=shadow)
            # highlight top-left edge
            draw.line([(x + 1, y + 1), (x + bw - 2, y + 1)], fill=highlight)


def draw_arch(draw, cx, cy, w, h, color, thickness=4):
    """Draw a simple stone arch (semi-ellipse outline)."""
    bbox = [cx - w // 2, cy - h, cx + w // 2, cy]
    draw.arc(bbox, 180, 0, fill=color, width=thickness)
    draw.line([(cx - w // 2, cy - h // 4), (cx - w // 2, cy)], fill=color, width=thickness)
    draw.line([(cx + w // 2, cy - h // 4), (cx + w // 2, cy)], fill=color, width=thickness)


def draw_pillar(draw, x, y, pw, ph, light, dark, mid):
    """Draw a simple rectangular pillar with shading."""
    draw.rectangle([x, y, x + pw, y + ph], fill=mid)
    draw.rectangle([x, y, x + pw // 4, y + ph], fill=light)
    draw.rectangle([x + pw * 3 // 4, y, x + pw, y + ph], fill=dark)


def add_glow_spot(img, cx, cy, radius, color, alpha_max=80):
    """Add a radial glow using a separate RGBA layer merged in."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    steps = 12
    for s in range(steps, 0, -1):
        r = int(radius * s / steps)
        a = int(alpha_max * (1 - s / steps) ** 0.7)
        odraw.ellipse([cx - r, cy - r, cx + r, cy + r],
                      fill=(color[0], color[1], color[2], a))
    base = img.convert("RGBA")
    base = Image.alpha_composite(base, overlay)
    return base.convert("RGB")


def add_particles(img, count, color_range, size=2):
    """Scatter small glowing motes."""
    draw = ImageDraw.Draw(img)
    for _ in range(count):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        lum = random.randint(color_range[0], color_range[1])
        c = (lum, lum, lum)
        draw.ellipse([x, y, x + size, y + size], fill=c)


def draw_floor_line(draw, y, color, thickness=3):
    """Draw a horizontal floor separation line."""
    draw.line([(0, y), (W, y)], fill=color, width=thickness)


def add_vignette(img, strength=100):
    """Darken edges."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    cx, cy = W // 2, H // 2
    for s in range(20, 0, -1):
        rw = W * s // 20
        rh = H * s // 20
        a = int(strength * (1 - (s / 20) ** 1.5))
        odraw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                      fill=(0, 0, 0, a))
    base = img.convert("RGBA")
    base = Image.alpha_composite(base, overlay)
    return base.convert("RGB")


def save(img, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path)
    print(f"  Saved: {filename}")


# ---------------------------------------------------------------------------
# Floor generators
# ---------------------------------------------------------------------------

def gen_stone_prison():
    """Floor 1 – 石牢: Cool grey, dim blue torchlight"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (28, 32, 40), (14, 18, 24))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (52, 58, 66), (72, 78, 88), (18, 22, 28))
    # ceiling stones
    draw_stones(draw, (42, 48, 56), (62, 68, 76), (15, 18, 22), rows=2, cols=10, offset_y=0)
    # arches
    for cx in [160, 480]:
        draw_arch(draw, cx, H - 40, 120, 100, (35, 42, 52), thickness=5)
    # torch glows
    for gx in [80, 320, 560]:
        gy = 80
        img = add_glow_spot(img, gx, gy, 60, (80, 100, 160), 90)
        draw = ImageDraw.Draw(img)
        # torch bracket
        draw.rectangle([gx - 3, gy - 10, gx + 3, gy + 10], fill=(90, 70, 40))
        draw.ellipse([gx - 5, gy - 15, gx + 5, gy - 5], fill=(220, 160, 60))
    # bars/grate top-right corner
    for bx in range(490, 600, 14):
        draw.line([(bx, 20), (bx, 70)], fill=(30, 35, 42), width=2)
    draw.rectangle([490, 20, 600, 25], fill=(30, 35, 42))
    draw.rectangle([490, 68, 600, 73], fill=(30, 35, 42))
    add_noise(img, 10, (2, 3, 5))
    img = add_vignette(img, 80)
    save(img, "bg_stone_prison.png")


def gen_shadow_hall():
    """Floor 2 – 暗影长廊: Dark purple, flickering shadows"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (18, 10, 28), (8, 5, 15))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (32, 18, 45), (45, 25, 60), (12, 8, 18))
    # perspective corridor lines
    for i in range(5):
        x_l = 60 - i * 8
        x_r = W - 60 + i * 8
        y1 = 40 + i * 20
        y2 = H - 30 - i * 20
        draw.line([(x_l, y1), (W // 2, H // 2)], fill=(50, 28, 70), width=1)
        draw.line([(x_r, y1), (W // 2, H // 2)], fill=(50, 28, 70), width=1)
    # pillars
    for px in [40, 200, 440, 600]:
        draw_pillar(draw, px, 60, 24, H - 100, (40, 22, 55), (20, 10, 30), (30, 16, 42))
    # shadow wisps
    for _ in range(8):
        sx = random.randint(50, W - 50)
        sy = random.randint(80, H - 80)
        img = add_glow_spot(img, sx, sy, random.randint(20, 50), (60, 20, 100), 40)
        draw = ImageDraw.Draw(img)
    # torch glows purple
    for gx in [160, 480]:
        img = add_glow_spot(img, gx, 70, 55, (100, 40, 160), 70)
        draw = ImageDraw.Draw(img)
        draw.ellipse([gx - 4, 60, gx + 4, 72], fill=(180, 80, 255))
    add_noise(img, 8, (5, 2, 8))
    img = add_vignette(img, 110)
    save(img, "bg_shadow_hall.png")


def gen_lava_cave():
    """Floor 3 – 熔岩洞窟: Deep orange, red glow, black rocks"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (15, 8, 5), (30, 12, 5))
    draw = ImageDraw.Draw(img)
    # rocky ceiling/floor silhouette
    pts_top = [(0, 0)]
    for x in range(0, W + 40, 40):
        pts_top.append((x, random.randint(30, 80)))
    pts_top.extend([(W, 0)])
    draw.polygon(pts_top, fill=(12, 6, 4))
    pts_bot = [(0, H)]
    for x in range(0, W + 40, 40):
        pts_bot.append((x, H - random.randint(20, 60)))
    pts_bot.extend([(W, H)])
    draw.polygon(pts_bot, fill=(12, 6, 4))
    # lava cracks / streams
    for _ in range(5):
        lx = random.randint(20, W - 20)
        ly_start = H - 60
        for seg in range(8):
            lx2 = lx + random.randint(-20, 20)
            ly2 = ly_start - seg * 20 + random.randint(-5, 5)
            col = random.choice([(200, 60, 10), (220, 100, 20), (180, 40, 5)])
            draw.line([(lx, ly_start), (lx2, ly2)], fill=col, width=random.randint(2, 4))
            lx, ly_start = lx2, ly2
    # large lava glow pools at bottom
    for gx in [100, 320, 540]:
        img = add_glow_spot(img, gx, H - 30, 90, (220, 80, 10), 120)
        draw = ImageDraw.Draw(img)
    # rock columns (black silhouettes)
    for rx in [60, 200, 400, 580]:
        rh = random.randint(60, 140)
        draw.rectangle([rx, H - rh, rx + 22, H], fill=(10, 5, 3))
    # ember particles
    add_particles(img, 60, (180, 255), 2)
    add_noise(img, 12, (8, 3, 0))
    img = add_vignette(img, 70)
    save(img, "bg_lava_cave.png")


def gen_bone_chamber():
    """Floor 4 – 骸骨密室: Bone white, brown stone, green mold"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (35, 28, 22), (22, 18, 14))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (55, 45, 32), (70, 58, 44), (22, 18, 14))
    # piled bones along floor
    for bx in range(0, W, 30):
        by = H - random.randint(10, 30)
        draw.ellipse([bx, by, bx + 20, by + 16], fill=(200, 192, 170))
        draw.line([(bx + 5, by + 8), (bx + 25, by + 5)], fill=(210, 200, 178), width=2)
    # skulls (simple circles with eye holes)
    for sx in [80, 240, 400, 560]:
        sy = H - random.randint(40, 60)
        draw.ellipse([sx, sy, sx + 24, sy + 20], fill=(205, 196, 172))
        draw.ellipse([sx + 4, sy + 4, sx + 10, sy + 10], fill=(22, 18, 14))
        draw.ellipse([sx + 14, sy + 4, sx + 20, sy + 10], fill=(22, 18, 14))
    # green mold patches
    for _ in range(12):
        mx = random.randint(0, W)
        my = random.randint(H // 2, H)
        img = add_glow_spot(img, mx, my, random.randint(15, 35), (40, 100, 30), 50)
        draw = ImageDraw.Draw(img)
    # torches dim yellow
    for gx in [100, 320, 540]:
        img = add_glow_spot(img, gx, 80, 50, (160, 140, 60), 60)
        draw = ImageDraw.Draw(img)
    add_noise(img, 10, (4, 3, 1))
    img = add_vignette(img, 90)
    save(img, "bg_bone_chamber.png")


def gen_abyss_throne():
    """Floor 5 – 深渊王座: Black, deep crimson, silver trim"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (5, 3, 3), (10, 5, 5))
    draw = ImageDraw.Draw(img)
    # throne platform
    draw.rectangle([W // 2 - 80, H - 80, W // 2 + 80, H - 50], fill=(18, 8, 8))
    draw.rectangle([W // 2 - 60, H - 120, W // 2 + 60, H - 80], fill=(14, 6, 6))
    draw.rectangle([W // 2 - 40, H - 180, W // 2 + 40, H - 120], fill=(12, 5, 5))
    # silver trim on throne
    for y_t in [H - 80, H - 120, H - 180]:
        draw.line([(W // 2 - 80, y_t), (W // 2 + 80, y_t)], fill=(140, 140, 160), width=2)
    # large crimson glow
    img = add_glow_spot(img, W // 2, H - 140, 160, (160, 10, 10), 100)
    draw = ImageDraw.Draw(img)
    # pillars with silver caps
    for px in [60, 160, W - 160, W - 60]:
        draw_pillar(draw, px, 30, 20, H - 80, (30, 20, 20), (10, 5, 5), (20, 12, 12))
        draw.rectangle([px - 2, 28, px + 22, 35], fill=(120, 120, 140))
    # crimson floor glow strips
    for gy in [H - 45, H - 25]:
        img = add_glow_spot(img, W // 2, gy, 280, (120, 8, 8), 60)
        draw = ImageDraw.Draw(img)
    # silver star motes
    add_particles(img, 30, (120, 180), 1)
    add_noise(img, 8, (5, 0, 0))
    img = add_vignette(img, 120)
    save(img, "bg_abyss_throne.png")


def gen_frost_altar():
    """Floor 6 – 冰霜祭坛: Ice blue, white crystals, cold mist"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (20, 35, 55), (10, 20, 38))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (40, 65, 95), (60, 90, 125), (18, 30, 50))
    # ice crystals
    def draw_crystal(cx, cy, size, col):
        pts = [
            (cx, cy - size),
            (cx + size // 3, cy - size // 3),
            (cx + size // 5, cy + size // 2),
            (cx - size // 5, cy + size // 2),
            (cx - size // 3, cy - size // 3),
        ]
        draw.polygon(pts, fill=col)
        draw.polygon(pts, outline=(180, 220, 255))

    for _ in range(12):
        cx = random.randint(20, W - 20)
        cy = random.randint(H // 2, H - 20)
        sz = random.randint(12, 35)
        col = random.choice([(80, 160, 220), (120, 190, 240), (150, 210, 255)])
        draw_crystal(cx, cy, sz, col)
        img = add_glow_spot(img, cx, cy, sz + 10, (100, 180, 255), 50)
        draw = ImageDraw.Draw(img)
    # altar top center
    draw.rectangle([W // 2 - 60, H // 2 - 20, W // 2 + 60, H // 2 + 10], fill=(50, 90, 130))
    draw.rectangle([W // 2 - 80, H // 2 + 10, W // 2 + 80, H // 2 + 20], fill=(40, 75, 110))
    img = add_glow_spot(img, W // 2, H // 2 - 10, 80, (140, 200, 255), 90)
    draw = ImageDraw.Draw(img)
    # mist particles
    add_particles(img, 80, (140, 200), 1)
    add_noise(img, 8, (2, 5, 10))
    img = add_vignette(img, 80)
    save(img, "bg_frost_altar.png")


def gen_corrupted_temple():
    """Floor 7 – 腐化神殿: Sickly green, dark stone, vines"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (12, 22, 10), (8, 16, 6))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (25, 40, 20), (35, 55, 28), (10, 18, 8))
    # pillar ruins
    for px in [80, 240, 400, 560]:
        ph = random.randint(80, H - 60)
        draw_pillar(draw, px, H - ph, 28, ph, (32, 52, 26), (14, 24, 10), (22, 38, 18))
        # broken top
        for _ in range(4):
            fx = px + random.randint(-8, 36)
            fy = H - ph - random.randint(5, 20)
            draw.rectangle([fx, fy, fx + random.randint(4, 12), fy + random.randint(4, 12)],
                           fill=(28, 44, 22))
    # vine tendrils
    for _ in range(15):
        vx = random.randint(0, W)
        vy_top = 0
        segs = random.randint(5, 14)
        cx, cy = vx, vy_top
        for _ in range(segs):
            nx = cx + random.randint(-15, 15)
            ny = cy + random.randint(10, 28)
            col = random.choice([(30, 80, 20), (40, 100, 25), (20, 60, 15)])
            draw.line([(cx, cy), (nx, ny)], fill=col, width=2)
            cx, cy = nx, ny
    # sickly green glows
    for gx in [100, 320, 540]:
        img = add_glow_spot(img, gx, random.randint(60, H - 60), 60, (40, 140, 20), 70)
        draw = ImageDraw.Draw(img)
    add_particles(img, 40, (80, 150), 1)
    add_noise(img, 9, (2, 6, 1))
    img = add_vignette(img, 100)
    save(img, "bg_corrupted_temple.png")


def gen_ghost_wreck():
    """Floor 8 – 幽灵船骸: Dark navy, ghost blue, wood planks"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (8, 12, 28), (5, 8, 18))
    draw = ImageDraw.Draw(img)
    # wood planks (horizontal)
    plank_y = 60
    while plank_y < H:
        gap = random.choice([0, random.randint(1, 3)])
        col = random.choice([(42, 28, 16), (52, 34, 20), (35, 22, 12)])
        draw.rectangle([0, plank_y, W, plank_y + 14 - gap], fill=col)
        # grain lines
        for _ in range(8):
            gx = random.randint(0, W)
            draw.line([(gx, plank_y + 2), (gx + random.randint(20, 80), plank_y + 2)],
                      fill=(28, 18, 10), width=1)
        plank_y += 15
    # ship ribs (vertical curved beams)
    for rx in [60, 200, 380, 540]:
        for seg in range(12):
            sx = rx + int(8 * math.sin(seg * 0.5))
            sy = seg * 30
            draw.rectangle([sx, sy, sx + 10, sy + 30], fill=(30, 20, 12))
    # ghost wisps
    for _ in range(10):
        gx = random.randint(50, W - 50)
        gy = random.randint(30, H - 30)
        img = add_glow_spot(img, gx, gy, random.randint(20, 55), (80, 130, 220), 55)
        draw = ImageDraw.Draw(img)
    # porthole windows
    for px in [120, 360, 520]:
        draw.ellipse([px - 20, 60, px + 20, 100], outline=(60, 50, 30), width=4)
        img = add_glow_spot(img, px, 80, 18, (100, 160, 255), 60)
        draw = ImageDraw.Draw(img)
    add_particles(img, 50, (100, 180), 1)
    add_noise(img, 9, (2, 3, 6))
    img = add_vignette(img, 90)
    save(img, "bg_ghost_wreck.png")


def gen_mechanical_fort():
    """Floor 9 – 机械要塞: Steel grey, orange gears, sparks"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (20, 22, 25), (12, 13, 16))
    draw = ImageDraw.Draw(img)
    # metal panel grid
    for row in range(0, H, 40):
        for col in range(0, W, 50):
            shade = random.randint(-8, 8)
            c = clamp(38 + shade)
            draw.rectangle([col + 1, row + 1, col + 49, row + 39],
                           fill=(c, c + 1, c + 2))
            draw.line([(col, row), (col + 50, row)], fill=(25, 26, 28), width=1)
            draw.line([(col, row), (col, row + 40)], fill=(25, 26, 28), width=1)
            draw.line([(col + 1, row + 1), (col + 49, row + 1)], fill=(55, 57, 60), width=1)
    # gears (circles with teeth)
    def draw_gear(cx, cy, r, col):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col,
                     outline=(80, 82, 85))
        draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                     fill=(30, 31, 33))
        teeth = 8
        for t in range(teeth):
            angle = t * 2 * math.pi / teeth
            tx = cx + int((r + 6) * math.cos(angle))
            ty = cy + int((r + 6) * math.sin(angle))
            draw.rectangle([tx - 4, ty - 4, tx + 4, ty + 4], fill=col)

    draw_gear(W // 4, H // 3, 45, (160, 100, 30))
    draw_gear(W * 3 // 4, H // 2, 35, (140, 88, 25))
    draw_gear(W // 2, H * 2 // 3, 55, (170, 110, 35))
    # pipes
    for py in [80, 160, 250]:
        draw.rectangle([0, py, W, py + 12], fill=(45, 46, 50))
        draw.line([(0, py), (W, py)], fill=(60, 62, 65), width=1)
        draw.line([(0, py + 12), (W, py + 12)], fill=(20, 21, 23), width=1)
    # orange glow / furnace
    img = add_glow_spot(img, W // 2, H - 40, 120, (200, 100, 20), 100)
    draw = ImageDraw.Draw(img)
    # sparks
    for _ in range(60):
        sx = random.randint(0, W)
        sy = random.randint(H // 2, H)
        bc = random.choice([(255, 200, 60), (255, 150, 40), (255, 255, 100)])
        draw.point((sx, sy), fill=bc)
    add_noise(img, 6, (3, 3, 3))
    img = add_vignette(img, 85)
    save(img, "bg_mechanical_fort.png")


def gen_void_rift():
    """Floor 10 – 虚空裂隙: Deep purple, void black, star motes"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (5, 3, 15), (2, 1, 8))
    draw = ImageDraw.Draw(img)
    # void rift crack in center
    cx, cy = W // 2, H // 2
    rift_pts = [(cx, cy - 120)]
    for i in range(20):
        rx = cx + random.randint(-60, 60)
        ry = (cy - 120) + i * 12
        rift_pts.append((rx, ry))
    rift_pts.append((cx, cy + 120))
    for i in range(len(rift_pts) - 1):
        draw.line([rift_pts[i], rift_pts[i + 1]], fill=(80, 20, 160), width=6)
        draw.line([rift_pts[i], rift_pts[i + 1]], fill=(140, 60, 220), width=2)
    # rift glow
    img = add_glow_spot(img, cx, cy, 140, (100, 20, 200), 110)
    draw = ImageDraw.Draw(img)
    # reality fragments (polygons)
    for _ in range(8):
        fx = random.randint(60, W - 60)
        fy = random.randint(60, H - 60)
        sz = random.randint(15, 40)
        pts = [(fx + random.randint(-sz, sz), fy + random.randint(-sz, sz)) for _ in range(5)]
        col = random.choice([(40, 10, 80), (60, 15, 110), (30, 5, 60)])
        draw.polygon(pts, fill=col, outline=(100, 30, 180))
    # star motes
    for _ in range(120):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        br = random.randint(100, 255)
        sz = random.choice([1, 1, 1, 2])
        draw.ellipse([sx, sy, sx + sz, sy + sz], fill=(br, br // 2, br))
    add_noise(img, 6, (4, 1, 8))
    img = add_vignette(img, 90)
    save(img, "bg_void_rift.png")


def gen_crystal_cavern():
    """Floor 11 – 水晶洞窟: Cyan, light blue, crystal reflections"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (10, 28, 38), (5, 15, 22))
    draw = ImageDraw.Draw(img)
    # crystal clusters
    def draw_crystal_cluster(cx, cy):
        for _ in range(random.randint(3, 7)):
            ox = random.randint(-20, 20)
            oy = random.randint(-5, 5)
            sz = random.randint(10, 40)
            col = random.choice([
                (80, 200, 220), (100, 220, 240), (60, 180, 210),
                (120, 230, 255), (40, 160, 200)
            ])
            pts = [
                (cx + ox, cy + oy - sz),
                (cx + ox + sz // 4, cy + oy - sz // 3),
                (cx + ox + sz // 6, cy + oy + sz // 2),
                (cx + ox - sz // 6, cy + oy + sz // 2),
                (cx + ox - sz // 4, cy + oy - sz // 3),
            ]
            draw.polygon(pts, fill=col)

    for clx in [60, 180, 320, 460, 590]:
        cly = H - random.randint(20, 60)
        draw_crystal_cluster(clx, cly)
        img = add_glow_spot(img, clx, cly, 50, (80, 200, 220), 60)
        draw = ImageDraw.Draw(img)

    # ceiling crystals pointing down
    for clx in range(40, W, 80):
        cly = random.randint(10, 40)
        sz = random.randint(8, 25)
        col = random.choice([(60, 170, 200), (80, 190, 220)])
        draw.polygon([
            (clx, cly + sz),
            (clx + sz // 3, cly + sz // 3),
            (clx + sz // 5, cly),
            (clx - sz // 5, cly),
            (clx - sz // 3, cly + sz // 3),
        ], fill=col)

    # reflection pools on floor
    img = add_glow_spot(img, W // 2, H - 15, 200, (60, 180, 220), 70)
    draw = ImageDraw.Draw(img)
    add_particles(img, 80, (150, 230), 1)
    add_noise(img, 7, (2, 8, 10))
    img = add_vignette(img, 75)
    save(img, "bg_crystal_cavern.png")


def gen_plague_swamp():
    """Floor 12 – 瘟疫沼泽: Toxic green, brown mud, dead trees"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (10, 18, 8), (18, 28, 10))
    draw = ImageDraw.Draw(img)
    # muddy floor
    for y in range(H * 2 // 3, H, 3):
        for x in range(0, W, 3):
            mud = random.choice([(35, 22, 10), (42, 28, 14), (30, 20, 8), (28, 18, 9)])
            draw.rectangle([x, y, x + 2, y + 2], fill=mud)
    # dead trees
    def draw_dead_tree(tx, ty):
        draw.rectangle([tx - 4, ty - 80, tx + 4, ty], fill=(28, 18, 10))
        for b in range(4):
            blen = random.randint(20, 55)
            bdir = random.choice([-1, 1])
            by = ty - 20 - b * 15
            draw.line([(tx, by), (tx + bdir * blen, by - random.randint(5, 20))],
                      fill=(24, 16, 8), width=3)
            draw.line([(tx + bdir * blen, by - random.randint(5, 20)),
                       (tx + bdir * blen + bdir * random.randint(5, 20),
                        by - random.randint(10, 30))],
                      fill=(22, 14, 7), width=1)

    for tx in [60, 170, 310, 450, 580]:
        draw_dead_tree(tx, H - 20)
    # toxic bubbles / pools
    for _ in range(8):
        px = random.randint(30, W - 30)
        py = random.randint(H * 2 // 3, H - 20)
        r = random.randint(10, 30)
        img = add_glow_spot(img, px, py, r + 10, (60, 160, 20), 70)
        draw = ImageDraw.Draw(img)
        draw.ellipse([px - r, py - r // 2, px + r, py + r // 2],
                     outline=(80, 180, 30), width=2)
    # miasma glow
    for gx in [80, 320, 560]:
        img = add_glow_spot(img, gx, H // 2, 70, (50, 140, 20), 60)
        draw = ImageDraw.Draw(img)
    add_particles(img, 40, (60, 130), 2)
    add_noise(img, 11, (3, 6, 1))
    img = add_vignette(img, 95)
    save(img, "bg_plague_swamp.png")


def gen_thunder_peak():
    """Floor 13 – 雷霆峰顶: Electric blue, dark cloud, stone"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (8, 12, 22), (20, 28, 45))
    draw = ImageDraw.Draw(img)
    # storm clouds at top
    for _ in range(15):
        cx = random.randint(0, W)
        cy = random.randint(0, H // 3)
        r = random.randint(25, 70)
        shade = random.randint(18, 35)
        draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2],
                     fill=(shade, shade + 5, shade + 12))
    # stone floor/ground
    draw_stones(draw, (38, 42, 50), (52, 58, 68), (22, 26, 32), rows=3, cols=10, offset_y=H * 2 // 3)
    # lightning bolts
    def draw_lightning(sx, sy):
        cx, cy = sx, sy
        for _ in range(8):
            nx = cx + random.randint(-15, 15)
            ny = cy + random.randint(15, 35)
            draw.line([(cx, cy), (nx, ny)], fill=(180, 200, 255), width=2)
            draw.line([(cx, cy), (nx, ny)], fill=(240, 248, 255), width=1)
            cx, cy = nx, ny

    for lx in [80, 200, 360, 520, 600]:
        draw_lightning(lx, 0)
        img = add_glow_spot(img, lx, 80, 50, (100, 140, 255), 70)
        draw = ImageDraw.Draw(img)
    # electric motes
    for _ in range(80):
        px = random.randint(0, W)
        py = random.randint(0, H // 2)
        br = random.randint(150, 255)
        draw.point((px, py), fill=(br // 2, br // 2, br))
    add_noise(img, 8, (2, 3, 7))
    img = add_vignette(img, 80)
    save(img, "bg_thunder_peak.png")


def gen_shadow_realm():
    """Floor 14 – 暗影领域: Black, dark grey, shadow wisps"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (4, 4, 5), (2, 2, 3))
    draw = ImageDraw.Draw(img)
    # subtle geometric grid (darker)
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(10, 10, 12), width=1)
    for y in range(0, H, 45):
        draw.line([(0, y), (W, y)], fill=(10, 10, 12), width=1)
    # shadow wisps
    for _ in range(18):
        wx = random.randint(0, W)
        wy = random.randint(0, H)
        img = add_glow_spot(img, wx, wy, random.randint(25, 80), (25, 20, 35), 55)
        draw = ImageDraw.Draw(img)
    # faint silhouette shapes
    for _ in range(5):
        fx = random.randint(50, W - 50)
        fy = random.randint(40, H - 40)
        sz = random.randint(20, 60)
        pts = [(fx + random.randint(-sz, sz), fy + random.randint(-sz, sz)) for _ in range(6)]
        draw.polygon(pts, fill=(12, 10, 16))
    # ghostly eye pairs
    for _ in range(5):
        ex = random.randint(50, W - 80)
        ey = random.randint(60, H - 60)
        img = add_glow_spot(img, ex, ey, 8, (150, 0, 0), 80)
        img = add_glow_spot(img, ex + 20, ey, 8, (150, 0, 0), 80)
        draw = ImageDraw.Draw(img)
    add_noise(img, 5, (1, 1, 2))
    img = add_vignette(img, 130)
    save(img, "bg_shadow_realm.png")


def gen_divine_sanctum():
    """Floor 15 – 神圣圣所: Gold, white marble, divine light"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (40, 35, 20), (55, 48, 28))
    draw = ImageDraw.Draw(img)
    # white marble tiles
    tile = 50
    for row in range(0, H, tile):
        for col in range(0, W, tile):
            vein = random.randint(-8, 8)
            c = clamp(200 + vein)
            draw.rectangle([col + 1, row + 1, col + tile - 1, row + tile - 1],
                           fill=(c, c - 2, c - 8))
            draw.line([(col, row), (col + tile, row)], fill=(160, 152, 112), width=1)
            draw.line([(col, row), (col, row + tile)], fill=(160, 152, 112), width=1)
    # gold pillars
    for px in [40, 160, W - 160, W - 40]:
        draw_pillar(draw, px, 20, 22, H - 60, (230, 180, 60), (160, 120, 30), (200, 156, 48))
        # pillar capital (top decoration)
        draw.rectangle([px - 5, 18, px + 27, 26], fill=(240, 195, 70))
    # divine light rays from top center
    img = add_glow_spot(img, W // 2, 0, 250, (255, 240, 160), 130)
    draw = ImageDraw.Draw(img)
    # ray lines
    for angle in range(-60, 61, 15):
        rad = math.radians(angle)
        ex = W // 2 + int(300 * math.sin(rad))
        ey = int(300 * math.cos(rad))
        draw.line([(W // 2, 0), (ex, ey)], fill=(255, 240, 140), width=1)
    # golden altar
    draw.rectangle([W // 2 - 50, H - 80, W // 2 + 50, H - 50], fill=(200, 155, 40))
    draw.rectangle([W // 2 - 35, H - 110, W // 2 + 35, H - 80], fill=(215, 170, 50))
    img = add_glow_spot(img, W // 2, H - 90, 70, (255, 220, 80), 90)
    draw = ImageDraw.Draw(img)
    add_particles(img, 60, (200, 255), 1)
    add_noise(img, 6, (5, 4, 1))
    img = add_vignette(img, 60)
    save(img, "bg_divine_sanctum.png")


def gen_chaos_forge():
    """Floor 16 – 混沌熔炉: Orange fire, black smoke, runes"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (12, 6, 2), (22, 10, 4))
    draw = ImageDraw.Draw(img)
    draw_stones(draw, (25, 12, 5), (35, 18, 8), (12, 6, 2))
    # forge pit
    draw.rectangle([W // 2 - 80, H - 80, W // 2 + 80, H], fill=(18, 8, 3))
    img = add_glow_spot(img, W // 2, H - 40, 130, (220, 100, 10), 130)
    draw = ImageDraw.Draw(img)
    # flame shapes
    for fx in range(W // 2 - 70, W // 2 + 80, 20):
        fh = random.randint(30, 80)
        col = random.choice([(240, 120, 20), (255, 80, 10), (255, 160, 30)])
        draw.polygon([
            (fx, H - 80),
            (fx + 8, H - 80 - fh),
            (fx + 16, H - 80),
        ], fill=col)
    # smoke at top
    for _ in range(12):
        sx = random.randint(W // 2 - 100, W // 2 + 100)
        sy = random.randint(0, H // 3)
        r = random.randint(20, 55)
        shade = random.randint(12, 25)
        draw.ellipse([sx - r, sy - r // 2, sx + r, sy + r // 2],
                     fill=(shade, shade - 2, shade - 3))
    # rune symbols (simple cross/diamond shapes)
    def draw_rune(rx, ry, size, col):
        draw.line([(rx - size, ry), (rx + size, ry)], fill=col, width=2)
        draw.line([(rx, ry - size), (rx, ry + size)], fill=col, width=2)
        draw.rectangle([rx - size // 2, ry - size // 2, rx + size // 2, ry + size // 2],
                       outline=col)

    for _ in range(8):
        run_x = random.randint(30, W - 30)
        run_y = random.randint(40, H // 2)
        draw_rune(run_x, run_y, random.randint(6, 14),
                  random.choice([(180, 80, 20), (220, 120, 30)]))
    add_particles(img, 70, (180, 255), 1)
    add_noise(img, 10, (8, 3, 0))
    img = add_vignette(img, 90)
    save(img, "bg_chaos_forge.png")


def gen_nightmare_maze():
    """Floor 17 – 梦魇迷宫: Dark magenta, twisted geometry"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (15, 5, 15), (25, 8, 25))
    draw = ImageDraw.Draw(img)
    # distorted grid maze walls
    for row in range(0, H, 40):
        for col in range(0, W, 40):
            if random.random() < 0.4:
                ox = random.randint(-5, 5)
                oy = random.randint(-5, 5)
                c = random.choice([(55, 15, 55), (70, 22, 70), (40, 12, 40)])
                draw.rectangle([col + ox, row + oy, col + 38 + ox, row + 38 + oy],
                               fill=c, outline=(90, 30, 90))
    # impossible perspective lines
    for _ in range(6):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        x2 = random.randint(0, W)
        y2 = random.randint(0, H)
        draw.line([(x1, y1), (x2, y2)], fill=(120, 30, 120), width=2)
    # warped doorframes
    for dx in [120, 360, 520]:
        pts = [
            (dx + random.randint(-5, 5), 50),
            (dx + 60 + random.randint(-5, 5), 50),
            (dx + 65 + random.randint(-5, 5), H - 50),
            (dx - 5 + random.randint(-5, 5), H - 50),
        ]
        draw.polygon(pts, outline=(180, 50, 180), fill=None)
    # eye symbols
    for _ in range(5):
        ex = random.randint(40, W - 40)
        ey = random.randint(40, H - 40)
        size = random.randint(8, 20)
        draw.ellipse([ex - size, ey - size // 2, ex + size, ey + size // 2],
                     outline=(200, 60, 200), width=2)
        draw.ellipse([ex - size // 4, ey - size // 4, ex + size // 4, ey + size // 4],
                     fill=(200, 60, 200))
        img = add_glow_spot(img, ex, ey, size + 8, (160, 40, 160), 60)
        draw = ImageDraw.Draw(img)
    add_particles(img, 50, (90, 180), 1)
    add_noise(img, 9, (7, 2, 7))
    img = add_vignette(img, 100)
    save(img, "bg_nightmare_maze.png")


def gen_ancient_ruins():
    """Floor 18 – 远古遗迹: Sand/gold, carved stone, blue sky"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (80, 120, 180), (50, 90, 150))  # sky top
    draw = ImageDraw.Draw(img)
    # sandy ground
    for y in range(H * 2 // 3, H):
        for x in range(0, W, 2):
            v = random.randint(-8, 8)
            base = 180 + v
            draw.point((x, y), fill=(base, base - 20, base - 60))
    # carved stone columns (ruin style - partial)
    for cx in [60, 200, 440, 580]:
        ph = random.randint(H // 3, H * 2 // 3)
        col_y = H * 2 // 3 - ph
        draw_pillar(draw, cx, col_y, 30, ph, (200, 175, 110), (140, 118, 72), (170, 146, 90))
        # hieroglyph-like markings
        for mark_y in range(col_y + 10, col_y + ph, 25):
            draw.rectangle([cx + 8, mark_y, cx + 22, mark_y + 8], fill=(130, 105, 60))
        # broken top
        for _ in range(3):
            bx = cx + random.randint(-5, 35)
            by = col_y - random.randint(5, 20)
            draw.rectangle([bx, by, bx + random.randint(8, 18), by + random.randint(8, 18)],
                           fill=(160, 136, 82))
    # sun glow
    img = add_glow_spot(img, W - 80, 50, 80, (255, 230, 120), 100)
    draw = ImageDraw.Draw(img)
    draw.ellipse([W - 100, 30, W - 60, 70], fill=(255, 240, 160))
    # sand particles / dust
    add_particles(img, 50, (160, 210), 1)
    add_noise(img, 8, (6, 4, 0))
    img = add_vignette(img, 60)
    save(img, "bg_ancient_ruins.png")


def gen_void_palace():
    """Floor 19 – 虚空宫殿: Deep space, galaxy colors, pillars"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (5, 2, 18), (2, 5, 15))
    draw = ImageDraw.Draw(img)
    # starfield
    for _ in range(200):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        br = random.randint(80, 255)
        col = random.choice([
            (br, br, br),
            (br, br // 2, br),
            (br // 2, br // 2, br),
            (br, br, br // 2),
        ])
        draw.point((sx, sy), fill=col)
    # nebula clouds
    for _ in range(6):
        nx = random.randint(0, W)
        ny = random.randint(0, H)
        nc = random.choice([
            (60, 10, 120), (10, 40, 120), (80, 20, 80), (20, 60, 100)
        ])
        img = add_glow_spot(img, nx, ny, random.randint(50, 100), nc, 60)
        draw = ImageDraw.Draw(img)
    # cosmic pillars (semi-transparent look via blending)
    for px in [40, 160, W - 160, W - 40]:
        draw_pillar(draw, px, 20, 22, H - 50, (60, 30, 100), (20, 10, 50), (40, 20, 75))
        # glowing tops
        img = add_glow_spot(img, px + 11, 20, 25, (120, 60, 200), 80)
        draw = ImageDraw.Draw(img)
    # galaxy spiral hint
    for angle in range(0, 720, 8):
        rad = math.radians(angle)
        r = angle * 0.15
        gx = W // 2 + int(r * math.cos(rad))
        gy = H // 2 + int(r * 0.5 * math.sin(rad))
        if 0 <= gx < W and 0 <= gy < H:
            col_choice = angle % 360
            c = (
                clamp(60 + int(80 * math.sin(math.radians(col_choice)))),
                clamp(30 + int(60 * math.sin(math.radians(col_choice + 120)))),
                clamp(100 + int(80 * math.sin(math.radians(col_choice + 240)))),
            )
            draw.point((gx, gy), fill=c)
    add_noise(img, 5, (3, 2, 6))
    img = add_vignette(img, 70)
    save(img, "bg_void_palace.png")


def gen_final_sanctum():
    """Floor 20 – 最终圣殿: Pure black, golden divine rays"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (3, 2, 1), (6, 4, 2))
    draw = ImageDraw.Draw(img)
    # divine ray burst from center top
    cx = W // 2
    for angle in range(-80, 81, 5):
        rad = math.radians(angle - 90)
        length = random.randint(200, 350)
        ex = cx + int(length * math.cos(rad))
        ey = int(length * math.sin(rad))
        alpha = random.randint(40, 90)
        # Use glow spot trick along ray
        steps = 8
        for s in range(steps):
            t = s / steps
            rx = cx + int(t * (ex - cx))
            ry = int(t * ey)
            img = add_glow_spot(img, rx, ry, 12, (200, 160, 40), alpha // steps)
            draw = ImageDraw.Draw(img)
        draw.line([(cx, 0), (ex, ey)], fill=(120, 95, 20), width=1)

    # central divine glow
    img = add_glow_spot(img, cx, 0, 180, (255, 210, 60), 140)
    draw = ImageDraw.Draw(img)
    # void floor
    draw_stones(draw, (12, 9, 3), (18, 14, 5), (5, 4, 1), rows=4, cols=10, offset_y=H * 2 // 3)
    # altar of final boss
    draw.rectangle([cx - 70, H - 80, cx + 70, H - 55], fill=(25, 20, 5))
    draw.rectangle([cx - 50, H - 110, cx + 50, H - 80], fill=(20, 16, 4))
    img = add_glow_spot(img, cx, H - 90, 90, (200, 160, 30), 100)
    draw = ImageDraw.Draw(img)
    # rune ring
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        rx = cx + int(55 * math.cos(rad))
        ry = (H - 90) + int(20 * math.sin(rad))
        draw.rectangle([rx - 2, ry - 2, rx + 2, ry + 2], fill=(200, 160, 30))
    add_particles(img, 60, (150, 220), 1)
    add_noise(img, 7, (5, 4, 1))
    img = add_vignette(img, 80)
    save(img, "bg_final_sanctum.png")


# ---------------------------------------------------------------------------
# Special screens
# ---------------------------------------------------------------------------

def gen_game_over():
    """bg_game_over.png – dark red, skull atmosphere"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (8, 2, 2), (18, 5, 5))
    draw = ImageDraw.Draw(img)
    # blood cracks
    for _ in range(8):
        cx = random.randint(0, W)
        cy = random.randint(0, H)
        segs = random.randint(4, 10)
        x, y = cx, cy
        for _ in range(segs):
            nx = x + random.randint(-40, 40)
            ny = y + random.randint(-30, 30)
            draw.line([(x, y), (nx, ny)], fill=(80, 10, 10), width=2)
            x, y = nx, ny
    # large skull (center)
    scx, scy = W // 2, H // 2 - 20
    # cranium
    draw.ellipse([scx - 60, scy - 70, scx + 60, scy + 20], fill=(140, 128, 110))
    # jaw
    draw.rectangle([scx - 45, scy + 10, scx + 45, scy + 45], fill=(130, 118, 100))
    # teeth
    for tx in range(scx - 35, scx + 40, 14):
        draw.rectangle([tx, scy + 22, tx + 10, scy + 42], fill=(205, 195, 175))
        draw.rectangle([tx + 1, scy + 23, tx + 9, scy + 41], fill=(215, 205, 185))
    # eye sockets
    for ex in [scx - 28, scx + 10]:
        draw.ellipse([ex, scy - 35, ex + 32, scy - 5], fill=(15, 5, 5))
        img = add_glow_spot(img, ex + 16, scy - 20, 18, (150, 20, 20), 80)
        draw = ImageDraw.Draw(img)
    # nose hole
    draw.polygon([
        (scx - 8, scy - 5), (scx + 8, scy - 5),
        (scx + 5, scy + 8), (scx - 5, scy + 8)
    ], fill=(15, 5, 5))
    # dark red glow
    img = add_glow_spot(img, W // 2, H // 2, 180, (120, 10, 10), 90)
    draw = ImageDraw.Draw(img)
    # "YOU DIED" vibe — subtle text-like marks at bottom
    for _ in range(4):
        bx = W // 2 - 80 + random.randint(0, 160)
        by = H - 60
        draw.rectangle([bx, by, bx + random.randint(20, 60), by + 8], fill=(60, 10, 10))
    add_noise(img, 10, (8, 1, 1))
    img = add_vignette(img, 130)
    save(img, "bg_game_over.png")


def gen_victory():
    """bg_victory.png – golden light rays, triumphant"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (20, 16, 5), (35, 28, 8))
    draw = ImageDraw.Draw(img)
    # radiant burst from center
    cx, cy = W // 2, H // 2
    for angle in range(0, 360, 6):
        rad = math.radians(angle)
        length = random.randint(180, 320)
        ex = cx + int(length * math.cos(rad))
        ey = cy + int(length * math.sin(rad))
        draw.line([(cx, cy), (ex, ey)], fill=(120, 100, 30), width=1)
    # central glow
    img = add_glow_spot(img, cx, cy, 220, (255, 220, 80), 150)
    draw = ImageDraw.Draw(img)
    img = add_glow_spot(img, cx, cy, 80, (255, 250, 200), 200)
    draw = ImageDraw.Draw(img)
    # sparkling stars scattered around
    for _ in range(120):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        br = random.randint(140, 255)
        draw.point((sx, sy), fill=(br, int(br * 0.9), int(br * 0.4)))
        if random.random() < 0.2:
            draw.line([(sx - 3, sy), (sx + 3, sy)], fill=(br, br, br // 2), width=1)
            draw.line([(sx, sy - 3), (sx, sy + 3)], fill=(br, br, br // 2), width=1)
    # trophy silhouette hint
    draw.rectangle([cx - 20, cy + 40, cx + 20, cy + 80], fill=(100, 80, 20))
    draw.ellipse([cx - 30, cy, cx + 30, cy + 55], fill=(130, 105, 28))
    draw.rectangle([cx - 8, cy + 80, cx + 8, cy + 95], fill=(90, 72, 18))
    draw.rectangle([cx - 25, cy + 92, cx + 25, cy + 100], fill=(100, 80, 20))
    add_noise(img, 6, (6, 5, 1))
    img = add_vignette(img, 50)
    save(img, "bg_victory.png")


def gen_upgrade_panel():
    """bg_upgrade_panel.png – dark mystical runes border"""
    img = Image.new("RGB", (W, H))
    make_gradient(img, (8, 6, 20), (14, 10, 30))
    draw = ImageDraw.Draw(img)
    # dark center panel area
    draw.rectangle([40, 30, W - 40, H - 30], fill=(12, 9, 28), outline=(60, 40, 120), width=2)
    # rune border decorations
    def draw_border_rune(rx, ry):
        draw.ellipse([rx - 8, ry - 8, rx + 8, ry + 8], outline=(100, 60, 180), width=1)
        draw.line([(rx - 5, ry), (rx + 5, ry)], fill=(120, 80, 200), width=1)
        draw.line([(rx, ry - 5), (rx, ry + 5)], fill=(120, 80, 200), width=1)
        draw.rectangle([rx - 3, ry - 3, rx + 3, ry + 3], outline=(140, 100, 220))

    # top border runes
    for bx in range(80, W - 40, 60):
        draw_border_rune(bx, 30)
    # bottom border runes
    for bx in range(80, W - 40, 60):
        draw_border_rune(bx, H - 30)
    # side runes
    for by in range(70, H - 30, 60):
        draw_border_rune(40, by)
        draw_border_rune(W - 40, by)
    # corner ornaments
    for corner in [(40, 30), (W - 40, 30), (40, H - 30), (W - 40, H - 30)]:
        draw.ellipse([corner[0] - 12, corner[1] - 12, corner[0] + 12, corner[1] + 12],
                     outline=(160, 100, 255), width=2)
        draw.ellipse([corner[0] - 4, corner[1] - 4, corner[0] + 4, corner[1] + 4],
                     fill=(160, 100, 255))
    # mystical glow at center top
    img = add_glow_spot(img, W // 2, 30, 80, (80, 40, 180), 80)
    draw = ImageDraw.Draw(img)
    # scattered arcane symbols
    for _ in range(10):
        ax = random.randint(80, W - 80)
        ay = random.randint(60, H - 60)
        col = (random.randint(60, 120), random.randint(30, 80), random.randint(150, 220))
        draw.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], outline=col)
        draw.line([(ax - 6, ay), (ax + 6, ay)], fill=col, width=1)
        draw.line([(ax, ay - 6), (ax, ay + 6)], fill=col, width=1)
    add_particles(img, 40, (80, 150), 1)
    add_noise(img, 6, (3, 2, 7))
    img = add_vignette(img, 80)
    save(img, "bg_upgrade_panel.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Generating backgrounds to: {OUTPUT_DIR}")

    generators = [
        ("bg_stone_prison.png",     gen_stone_prison),
        ("bg_shadow_hall.png",      gen_shadow_hall),
        ("bg_lava_cave.png",        gen_lava_cave),
        ("bg_bone_chamber.png",     gen_bone_chamber),
        ("bg_abyss_throne.png",     gen_abyss_throne),
        ("bg_frost_altar.png",      gen_frost_altar),
        ("bg_corrupted_temple.png", gen_corrupted_temple),
        ("bg_ghost_wreck.png",      gen_ghost_wreck),
        ("bg_mechanical_fort.png",  gen_mechanical_fort),
        ("bg_void_rift.png",        gen_void_rift),
        ("bg_crystal_cavern.png",   gen_crystal_cavern),
        ("bg_plague_swamp.png",     gen_plague_swamp),
        ("bg_thunder_peak.png",     gen_thunder_peak),
        ("bg_shadow_realm.png",     gen_shadow_realm),
        ("bg_divine_sanctum.png",   gen_divine_sanctum),
        ("bg_chaos_forge.png",      gen_chaos_forge),
        ("bg_nightmare_maze.png",   gen_nightmare_maze),
        ("bg_ancient_ruins.png",    gen_ancient_ruins),
        ("bg_void_palace.png",      gen_void_palace),
        ("bg_final_sanctum.png",    gen_final_sanctum),
        ("bg_game_over.png",        gen_game_over),
        ("bg_victory.png",          gen_victory),
        ("bg_upgrade_panel.png",    gen_upgrade_panel),
    ]

    for name, fn in generators:
        print(f"  Generating {name} ...", end=" ", flush=True)
        fn()

    print(f"\nDone! {len(generators)} backgrounds generated.")


if __name__ == "__main__":
    main()
