"""
generate_story_art.py
Generates 16 mid-game and endgame story screen PNGs for "炸弹人勇闯地牢".
Output: q:/AGame/assets/sprites/story/  (640x360 px, RGB PNG, pixel-art style)
"""

from PIL import Image, ImageDraw
import math
import os
import sys

OUT_DIR = r"Q:\AGame\assets\sprites\story"
W, H = 640, 360

os.makedirs(OUT_DIR, exist_ok=True)


# ── palette helpers ──────────────────────────────────────────────────────────

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def blend(c1, c2, t):
    return tuple(clamp(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def fill_gradient_v(img, top_color, bot_color):
    """Vertical gradient fill."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = blend(top_color, bot_color, t)
        draw.line([(0, y), (W - 1, y)], fill=c)


def fill_gradient_h(img, left_color, right_color):
    draw = ImageDraw.Draw(img)
    for x in range(W):
        t = x / (W - 1)
        c = blend(left_color, right_color, t)
        draw.line([(x, 0), (x, H - 1)], fill=c)


def radial_glow(img, cx, cy, radius, color, intensity=0.7):
    """Add a radial glow on top of existing pixels."""
    pixels = img.load()
    for y in range(max(0, cy - radius), min(H, cy + radius)):
        for x in range(max(0, cx - radius), min(W, cx + radius)):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist < radius:
                t = (1 - dist / radius) * intensity
                r, g, b = pixels[x, y]
                pixels[x, y] = (
                    clamp(r + color[0] * t),
                    clamp(g + color[1] * t),
                    clamp(b + color[2] * t),
                )


def vignette(img, strength=0.7):
    """Darken edges."""
    pixels = img.load()
    cx, cy = W / 2, H / 2
    max_d = math.sqrt(cx ** 2 + cy ** 2)
    for y in range(H):
        for x in range(W):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_d
            factor = max(0.0, 1.0 - d * strength)
            r, g, b = pixels[x, y]
            pixels[x, y] = (clamp(r * factor), clamp(g * factor), clamp(b * factor))


def draw_rect(draw, x, y, w, h, color):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def draw_hero(draw, x, y, color=(220, 180, 120)):
    """Simple ~20px humanoid pixel silhouette at (x,y) = feet position."""
    # head (4x4)
    draw_rect(draw, x - 2, y - 20, 4, 4, color)
    # body (4x7)
    draw_rect(draw, x - 2, y - 16, 4, 7, color)
    # legs
    draw_rect(draw, x - 2, y - 9, 2, 9, color)
    draw_rect(draw, x, y - 9, 2, 9, color)
    # arms
    draw_rect(draw, x - 4, y - 15, 2, 5, color)
    draw_rect(draw, x + 2, y - 15, 2, 5, color)


def draw_torch(draw, img, x, y, flame_color=(255, 160, 40)):
    """Small wall torch at pixel (x,y) + glow."""
    draw_rect(draw, x - 1, y, 2, 6, (100, 70, 30))
    draw_rect(draw, x - 2, y - 4, 4, 4, flame_color)
    radial_glow(img, x, y - 2, 60, flame_color, 0.4)


def draw_stairs(draw, sx, sy, steps=8, step_w=40, step_h=10, color=(60, 60, 80)):
    """Descending staircase going right and down."""
    for i in range(steps):
        x = sx + i * (step_w // 2)
        y = sy + i * step_h
        draw_rect(draw, x, y, step_w, step_h, color)
        draw_rect(draw, x, y, step_w, 2, (80, 80, 100))  # highlight


def draw_door(draw, x, y, w, h, wall_color=(40, 30, 50), door_color=(20, 15, 30)):
    draw_rect(draw, x - 8, y - 8, w + 16, h + 16, wall_color)
    draw_rect(draw, x, y, w, h, door_color)
    # arch
    for ix in range(w):
        arch_y = y - int(math.sqrt(max(0, (w / 2) ** 2 - (ix - w / 2) ** 2)) * 0.4)
        draw_rect(draw, x + ix, arch_y, 1, y - arch_y + 1, wall_color)


def draw_window_bars(draw, x, y, cell_w=24, cell_h=28):
    """Barred prison cell opening."""
    draw_rect(draw, x, y, cell_w, cell_h, (15, 10, 20))
    for bx in range(3):
        draw_rect(draw, x + bx * 8 + 4, y, 2, cell_h, (60, 55, 65))
    draw_rect(draw, x, y + cell_h // 2, cell_w, 2, (60, 55, 65))


def save(img, name):
    path = os.path.join(OUT_DIR, name)
    img.save(path)
    print(f"  saved {path}")


# ── individual scenes ────────────────────────────────────────────────────────

def story_06_deeper():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (5, 10, 40), (0, 0, 10))
    draw = ImageDraw.Draw(img)

    # spiral staircase suggestion: concentric arcs + steps
    for ring in range(6, 0, -1):
        r = ring * 28
        cx, cy = W // 2, H // 2 + 40
        c_val = clamp(20 + ring * 8)
        draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 180, 360, fill=(c_val, c_val, c_val + 20))

    draw_stairs(draw, W // 2 - 80, H // 2 - 40, steps=7, step_w=36, step_h=12, color=(30, 35, 70))

    # torch on wall
    draw_torch(draw, img, W // 2 + 100, H // 2 - 60)

    # hero descending
    draw_hero(draw, W // 2 - 30, H // 2 + 30, color=(180, 150, 100))

    # darkness below
    draw_rect(draw, 0, H - 80, W, 80, (0, 0, 5))
    for fade_y in range(40):
        alpha = int(fade_y / 40 * 180)
        color = (0, 0, clamp(5 - fade_y // 8))
        draw.line([(0, H - 80 + fade_y), (W - 1, H - 80 + fade_y)], fill=color)

    vignette(img, 0.8)
    save(img, "story_06_deeper.png")


def story_07_guardian():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (15, 5, 30), (5, 0, 15))
    draw = ImageDraw.Draw(img)

    # temple pillars
    for px in [80, 200, 440, 560]:
        draw_rect(draw, px, 60, 28, H - 60, (40, 35, 55))
        draw_rect(draw, px, 60, 28, 12, (60, 55, 75))  # capital

    # Guardian body (large stone figure, ~120px tall)
    gx, gy = W // 2, H - 60
    stone = (70, 65, 85)
    stone_dark = (45, 42, 58)
    # legs
    draw_rect(draw, gx - 20, gy - 60, 16, 60, stone_dark)
    draw_rect(draw, gx + 4, gy - 60, 16, 60, stone_dark)
    # body
    draw_rect(draw, gx - 28, gy - 110, 56, 50, stone)
    # shoulders
    draw_rect(draw, gx - 44, gy - 115, 20, 14, stone)
    draw_rect(draw, gx + 24, gy - 115, 20, 14, stone)
    # arms
    draw_rect(draw, gx - 46, gy - 101, 14, 50, stone_dark)
    draw_rect(draw, gx + 32, gy - 101, 14, 50, stone_dark)
    # head
    draw_rect(draw, gx - 18, gy - 135, 36, 30, stone)
    # glowing eyes
    eye_color = (160, 80, 255)
    draw_rect(draw, gx - 12, gy - 125, 8, 6, eye_color)
    draw_rect(draw, gx + 4, gy - 125, 8, 6, eye_color)
    radial_glow(img, gx - 8, gy - 122, 35, (120, 40, 200), 0.6)
    radial_glow(img, gx + 8, gy - 122, 35, (120, 40, 200), 0.6)

    # hero (small, in awe)
    draw_hero(draw, W // 2 - 90, H - 60, color=(180, 150, 100))

    vignette(img, 0.85)
    save(img, "story_07_guardian.png")


def story_08_revelation():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (50, 30, 10), (20, 12, 5))
    draw = ImageDraw.Draw(img)

    # amber ambient
    radial_glow(img, W // 2, H // 2, 220, (255, 160, 40), 0.35)

    # ruined walls
    for bx in range(0, W, 20):
        bh = 30 + (bx * 7 + 13) % 40
        draw_rect(draw, bx, H - bh - 20, 18, bh, (60, 40, 20))
    for bx in range(0, W, 20):
        bh = 20 + (bx * 5 + 7) % 30
        draw_rect(draw, bx, 0, 18, bh, (55, 38, 18))

    # workbench
    draw_rect(draw, W // 2 - 100, H // 2 + 20, 200, 12, (80, 55, 25))
    draw_rect(draw, W // 2 - 95, H // 2 + 0, 190, 22, (70, 48, 20))

    # blueprints on bench
    draw_rect(draw, W // 2 - 80, H // 2 - 5, 60, 22, (180, 160, 100))
    for line_y in range(3):
        draw_rect(draw, W // 2 - 75, H // 2 - 2 + line_y * 7, 50, 2, (100, 90, 60))
    draw_rect(draw, W // 2 + 10, H // 2 - 5, 40, 22, (170, 150, 90))

    # bomb parts on bench
    draw_rect(draw, W // 2 + 60, H // 2 + 2, 14, 14, (40, 40, 40))
    draw_rect(draw, W // 2 + 66, H // 2 - 2, 4, 6, (80, 70, 30))

    # wall cracks with writing
    draw_rect(draw, 60, 80, 80, 100, (45, 30, 15))
    for cy in range(5):
        draw_rect(draw, 68, 90 + cy * 16, 64, 2, (100, 80, 40))

    # hero studying blueprints
    draw_hero(draw, W // 2 - 10, H - 60, color=(180, 150, 100))

    vignette(img, 0.75)
    save(img, "story_08_revelation.png")


def story_09_merchant():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (10, 5, 0), (5, 3, 0))
    draw = ImageDraw.Draw(img)

    # cave chamber walls
    draw_rect(draw, 0, 0, W, 60, (25, 18, 10))
    draw_rect(draw, 0, H - 50, W, 50, (20, 15, 8))
    draw_rect(draw, 0, 0, 40, H, (20, 14, 8))
    draw_rect(draw, W - 40, 0, 40, H, (20, 14, 8))

    # candles on table
    table_x = W // 2 - 60
    draw_rect(draw, table_x, H // 2 + 30, 120, 10, (50, 35, 15))
    for cx in [table_x + 20, table_x + 60, table_x + 100]:
        draw_rect(draw, cx, H // 2 + 22, 4, 10, (200, 190, 160))
        draw_rect(draw, cx, H // 2 + 18, 6, 6, (255, 220, 80))
        radial_glow(img, cx + 2, H // 2 + 20, 45, (255, 160, 40), 0.45)

    # merchant silhouette (hooded, taller)
    mx, my = W // 2 + 50, H - 50
    hood = (30, 20, 10)
    robe = (25, 18, 8)
    # robe body
    draw_rect(draw, mx - 18, my - 80, 36, 80, robe)
    draw_rect(draw, mx - 22, my - 60, 44, 60, robe)
    # hood
    draw_rect(draw, mx - 14, my - 96, 28, 20, hood)
    draw_rect(draw, mx - 18, my - 90, 36, 16, hood)
    # face in shadow
    draw_rect(draw, mx - 10, my - 88, 20, 14, (10, 8, 5))
    # glowing eyes hint
    draw_rect(draw, mx - 7, my - 84, 4, 3, (200, 150, 60))
    draw_rect(draw, mx + 3, my - 84, 4, 3, (200, 150, 60))

    # hero (smaller, left side)
    draw_hero(draw, W // 2 - 60, H - 50, color=(180, 150, 100))

    # goods on table
    draw_rect(draw, table_x + 5, H // 2 + 10, 10, 14, (80, 60, 40))  # potion
    draw_rect(draw, table_x + 20, H // 2 + 12, 12, 12, (40, 40, 40))  # bomb
    draw_rect(draw, table_x + 40, H // 2 + 8, 16, 18, (120, 100, 60))  # box

    vignette(img, 0.9)
    save(img, "story_09_merchant.png")


def story_10_halfway():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (30, 0, 0), (10, 0, 5))
    draw = ImageDraw.Draw(img)

    # grand central chamber columns
    for i, px in enumerate([30, 130, W - 130 - 28, W - 30 - 28]):
        draw_rect(draw, px, 20, 28, H - 20, (50, 10, 10))
        draw_rect(draw, px - 8, 20, 44, 16, (65, 15, 15))

    # ceiling details
    for tx in range(0, W, 32):
        draw_rect(draw, tx, 0, 28, 20, (40, 8, 8))

    # 5 doorways at the bottom
    door_colors = [
        (40, 5, 5), (35, 5, 20), (20, 5, 40), (35, 20, 5), (40, 5, 5)
    ]
    for i in range(5):
        dx = 60 + i * 112
        dy = H - 90
        draw_rect(draw, dx - 8, dy - 8, 56, 90 + 8, (50, 12, 12))
        draw_rect(draw, dx, dy, 40, 82, door_colors[i])
        # rune above door
        draw_rect(draw, dx + 14, dy - 20, 12, 10, (180, 40, 40))

    # central glowing sigil on floor
    radial_glow(img, W // 2, H - 20, 100, (180, 30, 30), 0.5)
    draw_rect(draw, W // 2 - 20, H - 30, 40, 4, (200, 50, 50))
    draw_rect(draw, W // 2 - 4, H - 46, 8, 36, (200, 50, 50))

    # hero small in center
    draw_hero(draw, W // 2, H - 50, color=(180, 150, 100))

    vignette(img, 0.85)
    save(img, "story_10_halfway.png")


def story_11_cursed():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (0, 0, 0), (10, 0, 20))
    draw = ImageDraw.Draw(img)

    # dark energy tendrils spreading from center
    cx, cy = W // 2, H // 2
    for angle_deg in range(0, 360, 15):
        angle = math.radians(angle_deg)
        for r in range(0, 180, 3):
            tx = int(cx + math.cos(angle) * r)
            ty = int(cy + math.sin(angle) * r)
            if 0 <= tx < W and 0 <= ty < H:
                fade = 1 - r / 180
                c = (clamp(60 * fade), 0, clamp(80 * fade))
                draw.point((tx, ty), fill=c)

    # shadow spreading effect
    for ring in range(5):
        r = 30 + ring * 20
        alpha_val = clamp(120 - ring * 20)
        for angle_deg in range(0, 360, 2):
            angle = math.radians(angle_deg)
            px = int(cx + math.cos(angle) * r)
            py = int(cy + math.sin(angle) * r)
            if 0 <= px < W and 0 <= py < H:
                draw.point((px, py), fill=(alpha_val // 4, 0, alpha_val // 2))

    # hero at center
    draw_hero(draw, cx, cy + 10, color=(100, 50, 150))

    # dark aura around hero
    radial_glow(img, cx, cy, 80, (80, 0, 120), 0.6)

    # glowing purple eyes
    draw_rect(draw, cx - 3, cy - 18, 3, 3, (200, 100, 255))
    draw_rect(draw, cx + 1, cy - 18, 3, 3, (200, 100, 255))

    vignette(img, 0.9)
    save(img, "story_11_cursed.png")


def story_12_allies():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (20, 20, 25), (10, 10, 15))
    draw = ImageDraw.Draw(img)

    # stone walls
    for bx in range(0, W, 32):
        for by in range(0, H, 16):
            offset = 16 if (by // 16) % 2 == 1 else 0
            c = 35 if (bx + by) % 64 < 32 else 30
            draw_rect(draw, bx + offset - 32, by, 30, 14, (c, c, c + 5))

    # prison cells (left and right)
    for cell_x in [40, 140]:
        draw_rect(draw, cell_x, H // 2 - 50, 80, 100, (12, 10, 18))
        for bar in range(4):
            draw_rect(draw, cell_x + bar * 18 + 8, H // 2 - 50, 4, 100, (55, 50, 60))
        draw_rect(draw, cell_x, H // 2 - 50, 80, 4, (55, 50, 60))
        draw_rect(draw, cell_x, H // 2 + 46, 80, 4, (55, 50, 60))
        # prisoner arm reaching out
        draw_rect(draw, cell_x + 30, H // 2 - 10, 4, 28, (140, 110, 80))
        draw_rect(draw, cell_x + 34, H // 2 + 14, 12, 4, (140, 110, 80))

    for cell_x in [W - 120, W - 220]:
        draw_rect(draw, cell_x, H // 2 - 50, 80, 100, (12, 10, 18))
        for bar in range(4):
            draw_rect(draw, cell_x + bar * 18 + 8, H // 2 - 50, 4, 100, (55, 50, 60))
        draw_rect(draw, cell_x, H // 2 - 50, 80, 4, (55, 50, 60))
        draw_rect(draw, cell_x, H // 2 + 46, 80, 4, (55, 50, 60))
        draw_rect(draw, cell_x + 30, H // 2 - 10, 4, 28, (140, 110, 80))
        draw_rect(draw, cell_x + 18, H // 2 + 14, 12, 4, (140, 110, 80))

    # hero in corridor
    draw_hero(draw, W // 2, H - 60, color=(180, 150, 100))
    draw_torch(draw, img, W // 2 + 5, H // 2 - 80)

    vignette(img, 0.85)
    save(img, "story_12_allies.png")


def story_13_forge():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (15, 5, 0), (5, 2, 0))
    draw = ImageDraw.Draw(img)

    # forge glow (central)
    radial_glow(img, W // 2, H - 40, 200, (255, 120, 20), 0.6)
    radial_glow(img, W // 2, H - 40, 100, (255, 200, 60), 0.5)

    # forge structure
    forge_x = W // 2 - 50
    draw_rect(draw, forge_x, H - 80, 100, 80, (50, 30, 10))
    draw_rect(draw, forge_x - 10, H - 90, 120, 20, (60, 40, 15))
    # fire inside
    for fy in range(20):
        fc = clamp(200 + fy * 2)
        fg = clamp(80 + fy * 6)
        draw.line([(forge_x + 10, H - 80 + fy), (forge_x + 90, H - 80 + fy)],
                  fill=(fc, fg, 0))

    # sparks
    import random
    random.seed(42)
    for _ in range(30):
        sx = W // 2 + random.randint(-60, 60)
        sy = H - 80 - random.randint(0, 80)
        spark_c = random.choice([(255, 200, 50), (255, 150, 20), (255, 255, 100)])
        draw_rect(draw, sx, sy, 2, 2, spark_c)

    # hero at forge (crafting stance)
    draw_hero(draw, W // 2 - 20, H - 60, color=(180, 150, 100))
    # arm extended toward forge
    draw_rect(draw, W // 2 - 18, H - 74, 20, 4, (180, 150, 100))

    # walls (stone, dark)
    draw_rect(draw, 0, 0, 40, H, (20, 12, 5))
    draw_rect(draw, W - 40, 0, 40, H, (20, 12, 5))
    draw_rect(draw, 0, 0, W, 40, (18, 10, 4))

    # hanging chains
    for cx in [100, 200, W - 200, W - 100]:
        for link in range(0, 60, 8):
            draw_rect(draw, cx - 1, link, 3, 5, (50, 45, 40))

    vignette(img, 0.8)
    save(img, "story_13_forge.png")


def story_14_boss_lair():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (20, 0, 0), (5, 0, 0))
    draw = ImageDraw.Draw(img)

    # ominous red glow from door
    radial_glow(img, W // 2, H // 2 - 10, 160, (180, 20, 20), 0.45)

    # massive door
    door_w, door_h = 160, 220
    dx = W // 2 - door_w // 2
    dy = H // 2 - door_h // 2 - 20
    # door frame
    draw_rect(draw, dx - 16, dy - 16, door_w + 32, door_h + 16, (40, 5, 5))
    # door panels
    draw_rect(draw, dx, dy, door_w, door_h, (20, 2, 2))
    draw_rect(draw, dx + 8, dy + 8, door_w // 2 - 12, door_h - 16, (25, 4, 4))
    draw_rect(draw, dx + door_w // 2 + 4, dy + 8, door_w // 2 - 12, door_h - 16, (25, 4, 4))

    # evil runes on door
    rune_color = (200, 40, 40)
    rune_positions = [
        (dx + 20, dy + 30), (dx + 60, dy + 20), (dx + 100, dy + 30),
        (dx + 20, dy + 80), (dx + 70, dy + 70), (dx + 110, dy + 85),
        (dx + 40, dy + 130), (dx + 90, dy + 120),
    ]
    for rx, ry in rune_positions:
        draw_rect(draw, rx, ry, 8, 12, rune_color)
        draw_rect(draw, rx - 4, ry + 4, 16, 4, rune_color)
        radial_glow(img, rx + 4, ry + 6, 15, (220, 50, 50), 0.3)

    # door knockers / boss symbol
    draw_rect(draw, dx + door_w // 2 - 6, dy + door_h // 2 - 6, 12, 12, (120, 20, 20))

    # floor skulls
    for sx_pos in [W // 2 - 100, W // 2 + 80]:
        draw_rect(draw, sx_pos, H - 70, 14, 12, (80, 75, 70))
        draw_rect(draw, sx_pos + 2, H - 70, 4, 4, (10, 8, 8))
        draw_rect(draw, sx_pos + 8, H - 70, 4, 4, (10, 8, 8))

    # hero (small, at bottom)
    draw_hero(draw, W // 2, H - 50, color=(180, 150, 100))

    vignette(img, 0.9)
    save(img, "story_14_boss_lair.png")


def story_15_sacrifice():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (2, 5, 15), (0, 2, 8))
    draw = ImageDraw.Draw(img)

    # cold blue ambient
    radial_glow(img, W // 2, H // 2, 180, (20, 40, 120), 0.4)

    # stone floor
    for bx in range(0, W, 40):
        draw_rect(draw, bx, H - 40, 38, 40, (25, 28, 35))
        draw_rect(draw, bx, H - 42, 38, 3, (35, 38, 48))

    # skeleton lying on ground
    sx = W // 2 - 40
    sy = H - 60
    bone = (180, 175, 165)
    # skull
    draw_rect(draw, sx, sy - 14, 16, 14, bone)
    draw_rect(draw, sx + 3, sy - 3, 4, 4, (10, 12, 16))
    draw_rect(draw, sx + 9, sy - 3, 4, 4, (10, 12, 16))
    # ribcage
    draw_rect(draw, sx + 4, sy, 14, 20, bone)
    for rib in range(4):
        draw_rect(draw, sx + 2, sy + rib * 5 + 1, 18, 2, (160, 155, 145))
    # arm bones spread
    draw_rect(draw, sx - 20, sy + 4, 22, 4, bone)
    draw_rect(draw, sx + 18, sy + 4, 22, 4, bone)
    # leg bones
    draw_rect(draw, sx + 6, sy + 20, 6, 26, bone)
    draw_rect(draw, sx + 14, sy + 20, 6, 26, bone)

    # note on ground near skeleton
    note_x = sx + 50
    draw_rect(draw, note_x, sy - 4, 36, 28, (160, 145, 100))
    for line in range(4):
        draw_rect(draw, note_x + 4, sy + line * 6, 28, 2, (100, 90, 60))
    # fold corner
    draw_rect(draw, note_x + 28, sy - 4, 8, 8, (130, 118, 80))

    # hero (alive, finding skeleton)
    draw_hero(draw, W // 2 + 80, H - 50, color=(180, 150, 100))

    # torch dim blue-ish light
    draw_torch(draw, img, W // 2 + 80, H // 2 - 40, flame_color=(60, 100, 200))

    vignette(img, 0.85)
    save(img, "story_15_sacrifice.png")


def story_16_power():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (10, 8, 0), (20, 15, 0))
    draw = ImageDraw.Draw(img)

    # gold/white power aura
    for ring in range(8, 0, -1):
        r = ring * 25
        intensity = (9 - ring) / 8 * 0.4
        radial_glow(img, W // 2, H // 2 - 10, r, (255, 220, 80), intensity)

    # outer rays
    cx, cy = W // 2, H // 2 - 10
    for angle_deg in range(0, 360, 12):
        angle = math.radians(angle_deg)
        for r in range(60, 200, 4):
            fade = 1 - (r - 60) / 140
            px2 = int(cx + math.cos(angle) * r)
            py2 = int(cy + math.sin(angle) * r)
            if 0 <= px2 < W and 0 <= py2 < H:
                c = (clamp(255 * fade * 0.6), clamp(200 * fade * 0.6), 0)
                draw.point((px2, py2), fill=c)

    # bomb energy orbs orbiting hero
    for i, angle_deg in enumerate(range(0, 360, 45)):
        angle = math.radians(angle_deg)
        ox = int(cx + math.cos(angle) * 55)
        oy = int(cy + math.sin(angle) * 55)
        orb_color = [(255, 200, 0), (255, 150, 0), (255, 255, 100), (200, 240, 0)][i % 4]
        draw_rect(draw, ox - 5, oy - 5, 10, 10, orb_color)
        radial_glow(img, ox, oy, 20, orb_color, 0.5)

    # hero (empowered, bright)
    draw_hero(draw, cx, cy + 60, color=(255, 240, 160))
    # power corona around hero
    radial_glow(img, cx, cy + 40, 40, (255, 255, 120), 0.7)

    # ground glow
    radial_glow(img, cx, H - 20, 120, (200, 160, 20), 0.3)

    vignette(img, 0.6)
    save(img, "story_16_power.png")


def story_17_final_door():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (0, 0, 0), (5, 4, 0))
    draw = ImageDraw.Draw(img)

    # light leaking from behind door
    radial_glow(img, W // 2, H // 3, 200, (255, 200, 50), 0.35)

    # enormous obsidian gate
    gate_w, gate_h = 240, 300
    gx = W // 2 - gate_w // 2
    gy = H // 2 - gate_h // 2 - 30

    # gate frame (thick)
    draw_rect(draw, gx - 24, gy - 24, gate_w + 48, gate_h + 24, (10, 8, 0))
    obsidian = (15, 12, 5)
    draw_rect(draw, gx, gy, gate_w, gate_h, obsidian)

    # gold trim on gate
    gold = (180, 140, 20)
    draw_rect(draw, gx, gy, gate_w, 6, gold)
    draw_rect(draw, gx, gy + gate_h - 6, gate_w, 6, gold)
    draw_rect(draw, gx, gy, 6, gate_h, gold)
    draw_rect(draw, gx + gate_w - 6, gy, 6, gate_h, gold)

    # gold center divider
    draw_rect(draw, W // 2 - 3, gy, 6, gate_h, gold)

    # gold runes / symbols
    rune_positions_g = [
        (gx + 30, gy + 40), (gx + 90, gy + 30), (gx + 150, gy + 40),
        (gx + 30, gy + 100), (gx + 150, gy + 100),
        (gx + 60, gy + 160), (gx + 130, gy + 160),
    ]
    for rx, ry in rune_positions_g:
        draw_rect(draw, rx, ry, 10, 16, gold)
        draw_rect(draw, rx - 4, ry + 6, 18, 4, gold)
        radial_glow(img, rx + 5, ry + 8, 18, (220, 180, 40), 0.35)

    # light crack between gate doors
    for ly in range(gate_h):
        brightness = int(200 * (1 - abs(ly - gate_h // 2) / (gate_h // 2)) * 0.8)
        draw.point((W // 2, gy + ly), fill=(brightness, clamp(brightness * 0.8), 0))

    # hero tiny at bottom
    draw_hero(draw, W // 2, H - 40, color=(180, 150, 100))

    vignette(img, 0.9)
    save(img, "story_17_final_door.png")


def story_18_truth():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (5, 0, 20), (15, 0, 40))
    draw = ImageDraw.Draw(img)

    # divine light from above
    for ly in range(H // 2):
        t = 1 - ly / (H // 2)
        c = (clamp(40 * t), 0, clamp(80 * t))
        draw.line([(0, ly), (W - 1, ly)], fill=c)

    # divine beam
    radial_glow(img, W // 2, 0, 300, (180, 50, 255), 0.5)
    radial_glow(img, W // 2, H // 4, 150, (255, 200, 255), 0.4)

    # ancient god figure (massive, top-center)
    gx, gy = W // 2, 20
    divine = (200, 150, 255)
    divine_glow = (255, 200, 255)
    # outer cloak/wings
    for wing in range(-3, 4):
        w_x = gx + wing * 40
        w_y = gy + abs(wing) * 20
        draw_rect(draw, w_x - 12, w_y, 24, 120, (clamp(60 + abs(wing) * 10), 0, clamp(100 + abs(wing) * 15)))
    # body
    draw_rect(draw, gx - 24, gy, 48, 100, divine)
    # head (large, imposing)
    draw_rect(draw, gx - 20, gy - 30, 40, 32, divine)
    # crown/halo
    draw_rect(draw, gx - 30, gy - 36, 60, 8, divine_glow)
    for spike in range(5):
        draw_rect(draw, gx - 28 + spike * 14, gy - 50, 6, 16, divine_glow)
    # glowing eyes
    draw_rect(draw, gx - 12, gy - 22, 8, 6, (255, 255, 255))
    draw_rect(draw, gx + 4, gy - 22, 8, 6, (255, 255, 255))
    radial_glow(img, gx - 8, gy - 19, 30, (200, 150, 255), 0.7)
    radial_glow(img, gx + 8, gy - 19, 30, (200, 150, 255), 0.7)

    # hero tiny at bottom
    draw_hero(draw, W // 2, H - 40, color=(180, 150, 100))

    # divine rays
    for angle_deg in range(0, 360, 20):
        angle = math.radians(angle_deg)
        for r in range(40, 260, 6):
            fade = 1 - r / 260
            px2 = int(W // 2 + math.cos(angle) * r)
            py2 = int(20 + math.sin(angle) * r)
            if 0 <= px2 < W and 0 <= py2 < H:
                c = (clamp(120 * fade * 0.5), 0, clamp(200 * fade * 0.5))
                draw.point((px2, py2), fill=c)

    vignette(img, 0.75)
    save(img, "story_18_truth.png")


def story_19_last_stand():
    img = Image.new("RGB", (W, H))
    # Pure black base
    img.paste((0, 0, 0), [0, 0, W, H])
    draw = ImageDraw.Draw(img)

    # single small light source (hero's lantern / torch)
    lx, ly = W // 2, H // 2 + 20
    radial_glow(img, lx, ly, 120, (200, 160, 60), 0.55)
    radial_glow(img, lx, ly, 60, (255, 200, 80), 0.4)

    # hero (lit from below)
    draw_hero(draw, lx, ly + 50, color=(220, 180, 120))

    # tiny light in hero's hand (torch/bomb)
    draw_rect(draw, lx + 3, ly + 20, 6, 6, (255, 220, 80))
    radial_glow(img, lx + 6, ly + 23, 30, (255, 180, 40), 0.6)

    # vast darkness with hints of shapes
    for eye_pair in [(lx - 120, ly - 30), (lx + 100, ly - 20), (lx - 60, ly + 60),
                     (lx + 140, ly + 40), (lx - 180, ly + 10), (lx + 60, ly - 60)]:
        ex, ey = eye_pair
        if 0 <= ex < W - 12 and 0 <= ey < H - 6:
            draw_rect(draw, ex, ey, 5, 3, (80, 0, 0))
            draw_rect(draw, ex + 8, ey, 5, 3, (80, 0, 0))

    # ground line
    draw_rect(draw, 0, H - 40, W, 40, (5, 4, 3))
    draw_rect(draw, 0, H - 42, W, 3, (20, 16, 10))

    vignette(img, 0.95)
    save(img, "story_19_last_stand.png")


def story_20_ending_bad():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (0, 0, 0), (5, 0, 5))
    draw = ImageDraw.Draw(img)

    # darkness consuming everything
    # shadowy tendrils from edges
    for angle_deg in range(0, 360, 8):
        angle = math.radians(angle_deg)
        ex = int(W // 2 + math.cos(angle) * W)
        ey = int(H // 2 + math.sin(angle) * H)
        # tendrils toward center
        for r in range(0, 150, 4):
            px2 = int(ex + (W // 2 - ex) * r / 150)
            py2 = int(ey + (H // 2 - ey) * r / 150)
            if 0 <= px2 < W and 0 <= py2 < H:
                fade = r / 150
                c = (0, 0, clamp(20 * fade))
                draw.point((px2, py2), fill=c)

    # center darkness vortex
    cx, cy = W // 2, H // 2
    for ring in range(10):
        r = ring * 18
        c = clamp(ring * 5)
        draw.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], outline=(c, 0, c + 5))

    # hero silhouette being consumed
    # only a faint outline remains
    draw_hero(draw, cx, cy + 30, color=(15, 0, 25))
    # shadow eating the hero
    radial_glow(img, cx, cy + 10, 60, (30, 0, 50), 0.5)

    # desperate glint of light (almost gone)
    draw_rect(draw, cx - 2, cy + 5, 4, 4, (60, 40, 20))
    radial_glow(img, cx, cy + 7, 15, (100, 60, 20), 0.3)

    vignette(img, 1.0)
    save(img, "story_20_ending_bad.png")


def story_20_ending_good():
    img = Image.new("RGB", (W, H))
    fill_gradient_v(img, (20, 10, 0), (60, 30, 5))
    draw = ImageDraw.Draw(img)

    # dawn sky gradient (bottom of sky = lighter/warmer)
    for y in range(H // 2):
        t = y / (H // 2)
        c = blend((30, 15, 0), (180, 100, 20), t)
        draw.line([(0, y), (W - 1, y)], fill=c)

    # golden sunrise
    radial_glow(img, W // 2, H // 3, 200, (255, 180, 40), 0.65)
    radial_glow(img, W // 2, H // 3, 100, (255, 220, 80), 0.5)

    # sun disc
    sun_x, sun_y = W // 2, H // 3
    draw_rect(draw, sun_x - 20, sun_y - 20, 40, 40, (255, 240, 120))
    radial_glow(img, sun_x, sun_y, 50, (255, 255, 200), 0.6)

    # rays
    for angle_deg in range(0, 360, 22):
        angle = math.radians(angle_deg)
        for r in range(30, 130, 4):
            fade = 1 - (r - 30) / 100
            px2 = int(sun_x + math.cos(angle) * r)
            py2 = int(sun_y + math.sin(angle) * r)
            if 0 <= px2 < W and 0 <= py2 < H:
                c = (clamp(255 * fade * 0.7), clamp(200 * fade * 0.7), 0)
                draw.point((px2, py2), fill=c)

    # dungeon exit (dark opening at bottom center)
    exit_x = W // 2 - 40
    draw_rect(draw, exit_x - 8, H - 100, 96, 110, (40, 30, 15))
    draw_rect(draw, exit_x, H - 90, 80, 100, (10, 5, 0))

    # ground / hillside
    draw_rect(draw, 0, H - 60, W, 60, (30, 50, 10))
    draw_rect(draw, 0, H - 62, W, 4, (50, 70, 15))
    for tx in range(0, W, 16):
        h_tree = 20 + (tx * 7) % 30
        draw_rect(draw, tx + 4, H - 62 - h_tree, 8, h_tree, (20, 40, 8))
        draw_rect(draw, tx, H - 62 - h_tree - 10, 16, 12, (30, 60, 10))

    # hero exiting into light (triumphant pose)
    hero_color_hero = (220, 190, 140)
    draw_hero(draw, W // 2, H - 60, color=hero_color_hero)
    # arms raised
    draw_rect(draw, W // 2 - 12, H - 80, 4, 12, hero_color_hero)
    draw_rect(draw, W // 2 + 8, H - 80, 4, 12, hero_color_hero)
    # glow around hero
    radial_glow(img, W // 2, H - 70, 40, (255, 200, 80), 0.45)

    vignette(img, 0.5)
    save(img, "story_20_ending_good.png")


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}")
    print("Generating story screens...")

    story_06_deeper()
    story_07_guardian()
    story_08_revelation()
    story_09_merchant()
    story_10_halfway()
    story_11_cursed()
    story_12_allies()
    story_13_forge()
    story_14_boss_lair()
    story_15_sacrifice()
    story_16_power()
    story_17_final_door()
    story_18_truth()
    story_19_last_stand()
    story_20_ending_bad()
    story_20_ending_good()

    print("Done! 16 images generated.")
