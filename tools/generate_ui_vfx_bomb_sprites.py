"""
generate_ui_vfx_bomb_sprites.py
Generates bomb sprites, VFX sprites, and UI sprites for AGame.
All pixel-art style, no anti-aliasing.
"""

import os
import math
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
BASE = "Q:/AGame/assets/sprites"
BOMBS_DIR = os.path.join(BASE, "bombs")
VFX_DIR   = os.path.join(BASE, "vfx")
UI_DIR    = os.path.join(BASE, "ui")

for d in (BOMBS_DIR, VFX_DIR, UI_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def new_img(w, h, bg=(0, 0, 0, 0)):
    img = Image.new("RGBA", (w, h), bg)
    return img, ImageDraw.Draw(img)

def save(img, path):
    img.save(path)
    print(f"  saved: {path}")

def circle_points(cx, cy, r, n=64):
    """Return list of integer (x,y) on a circle."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts

def draw_bomb_base(draw, cx, cy, r, body_color, shadow_color, shine_color):
    """Draw a round bomb body with shading."""
    # Shadow below-right
    draw.ellipse([cx - r + 2, cy - r + 2, cx + r + 2, cy + r + 2], fill=shadow_color)
    # Main body
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body_color)
    # Shine top-left
    sr = max(1, r // 3)
    draw.ellipse([cx - r + 2, cy - r + 2, cx - r + 2 + sr, cy - r + 2 + sr], fill=shine_color)

def draw_fuse(draw, cx, cy_top, color=(180, 140, 60)):
    """Draw a small fuse line + spark above the bomb."""
    # Fuse line
    draw.line([(cx, cy_top), (cx + 3, cy_top - 5), (cx + 2, cy_top - 9)], fill=color, width=1)
    # Spark
    draw.point((cx + 2, cy_top - 10), fill=(255, 255, 100))
    draw.point((cx + 3, cy_top - 11), fill=(255, 200, 50))
    draw.point((cx + 1, cy_top - 11), fill=(255, 255, 150))

def pixel_circle_fill(draw, cx, cy, r, color):
    """Fill pixels within radius r (pixel-art hard edges)."""
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                draw.point((cx + dx, cy + dy), fill=color)

def pixel_ring(draw, cx, cy, r_inner, r_outer, color):
    """Draw a pixel ring between two radii."""
    for dy in range(-r_outer, r_outer + 1):
        for dx in range(-r_outer, r_outer + 1):
            d2 = dx * dx + dy * dy
            if r_inner * r_inner <= d2 <= r_outer * r_outer:
                draw.point((cx + dx, cy + dy), fill=color)

def star_polygon(cx, cy, n, r_outer, r_inner, angle_offset=0):
    """Return polygon points for a star shape."""
    pts = []
    for i in range(n * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.pi * i / n + angle_offset
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

# ---------------------------------------------------------------------------
# ==================  BOMB SPRITES  ==================
# ---------------------------------------------------------------------------

def gen_nova():
    """nova.png — Star burst, yellow/white radial, 32×32"""
    img, draw = new_img(32, 32, (10, 8, 20, 255))
    cx, cy = 16, 16
    # Outer star rays
    for i in range(8):
        a = math.pi * i / 4
        x2 = int(cx + 14 * math.cos(a))
        y2 = int(cy + 14 * math.sin(a))
        draw.line([(cx, cy), (x2, y2)], fill=(255, 230, 80), width=2)
        # Secondary thin rays offset by 22.5 degrees
        a2 = a + math.pi / 8
        x3 = int(cx + 10 * math.cos(a2))
        y3 = int(cy + 10 * math.sin(a2))
        draw.line([(cx, cy), (x3, y3)], fill=(255, 255, 180), width=1)
    # Center orb
    pixel_circle_fill(draw, cx, cy, 5, (255, 200, 40))
    pixel_circle_fill(draw, cx, cy, 3, (255, 240, 120))
    pixel_circle_fill(draw, cx, cy, 1, (255, 255, 220))
    save(img, os.path.join(BOMBS_DIR, "nova.png"))


def gen_frost():
    """frost.png — Snowflake, cyan/white, 32×32"""
    img, draw = new_img(32, 32, (8, 12, 28, 255))
    cx, cy = 16, 16
    # 6 main arms
    for i in range(6):
        a = math.pi * i / 3
        x2 = int(cx + 13 * math.cos(a))
        y2 = int(cy + 13 * math.sin(a))
        draw.line([(cx, cy), (x2, y2)], fill=(160, 230, 255), width=2)
        # Branches at 60% and 80% of arm
        for frac in (0.5, 0.75):
            bx = int(cx + frac * 13 * math.cos(a))
            by = int(cy + frac * 13 * math.sin(a))
            for bdir in (+1, -1):
                ba = a + bdir * math.pi / 3
                ex = int(bx + 4 * math.cos(ba))
                ey = int(by + 4 * math.sin(ba))
                draw.line([(bx, by), (ex, ey)], fill=(200, 240, 255), width=1)
    # Center
    pixel_circle_fill(draw, cx, cy, 3, (200, 240, 255))
    pixel_circle_fill(draw, cx, cy, 1, (255, 255, 255))
    # Corner dots
    for i in range(6):
        a = math.pi * i / 3 + math.pi / 6
        dx = int(cx + 13 * math.cos(a))
        dy = int(cy + 13 * math.sin(a))
        draw.point((dx, dy), fill=(220, 245, 255))
    save(img, os.path.join(BOMBS_DIR, "frost.png"))


def gen_poison():
    """poison.png — Skull/cloud shape, green/purple, 32×32"""
    img, draw = new_img(32, 32, (8, 6, 18, 255))
    cx, cy = 16, 14
    # Purple cloud body
    pixel_circle_fill(draw, cx, cy, 9, (90, 40, 120))
    pixel_circle_fill(draw, cx - 5, cy + 2, 6, (90, 40, 120))
    pixel_circle_fill(draw, cx + 5, cy + 2, 6, (90, 40, 120))
    # Skull face outline
    pixel_circle_fill(draw, cx, cy - 1, 7, (160, 200, 80))
    # Eyes
    pixel_circle_fill(draw, cx - 2, cy - 2, 2, (30, 20, 60))
    pixel_circle_fill(draw, cx + 2, cy - 2, 2, (30, 20, 60))
    # Nose
    draw.point((cx, cy + 1), fill=(30, 20, 60))
    # Teeth
    for tx in (cx - 3, cx - 1, cx + 1, cx + 3):
        draw.rectangle([tx, cy + 3, tx + 1, cy + 5], fill=(30, 20, 60))
    draw.line([(cx - 4, cy + 3), (cx + 4, cy + 3)], fill=(30, 20, 60), width=1)
    # Green mist particles below
    for gx, gy in ((10, 25), (16, 27), (22, 25), (8, 28), (24, 28)):
        pixel_circle_fill(draw, gx, gy, 2, (80, 180, 60, 180))
    save(img, os.path.join(BOMBS_DIR, "poison.png"))


def gen_thunder():
    """thunder.png — Lightning bolt, electric blue/yellow, 32×32"""
    img, draw = new_img(32, 32, (10, 6, 22, 255))
    # Bolt silhouette: classic Z-shape lightning
    bolt = [
        (20, 2), (10, 15), (17, 15), (8, 30), (22, 14), (15, 14)
    ]
    draw.polygon(bolt, fill=(255, 230, 30))
    # Inner bright
    inner = [
        (19, 4), (12, 14), (17, 14), (11, 27), (20, 15), (15, 15)
    ]
    draw.polygon(inner, fill=(255, 255, 160))
    # Electric glow dots
    for ex, ey in ((6, 10), (26, 14), (5, 22), (27, 22)):
        draw.point((ex, ey), fill=(160, 200, 255))
        draw.point((ex + 1, ey), fill=(160, 200, 255))
        draw.point((ex, ey + 1), fill=(100, 160, 255))
    save(img, os.path.join(BOMBS_DIR, "thunder.png"))


def gen_mega():
    """mega.png — Large spiky bomb, red/orange, 32×32"""
    img, draw = new_img(32, 32, (12, 6, 6, 255))
    cx, cy = 16, 17
    # Spikes
    for i in range(8):
        a = math.pi * i / 4 - math.pi / 8
        x2 = int(cx + 14 * math.cos(a))
        y2 = int(cy + 14 * math.sin(a))
        # Triangle spike
        a_l = a - 0.2
        a_r = a + 0.2
        pts = [
            (cx + 8 * math.cos(a_l), cy + 8 * math.sin(a_l)),
            (x2, y2),
            (cx + 8 * math.cos(a_r), cy + 8 * math.sin(a_r))
        ]
        draw.polygon(pts, fill=(200, 60, 20))
    # Body
    pixel_circle_fill(draw, cx, cy, 9, (180, 50, 20))
    pixel_circle_fill(draw, cx, cy, 7, (220, 80, 30))
    # Band around middle
    pixel_ring(draw, cx, cy, 6, 8, (140, 30, 10))
    # Shine
    pixel_circle_fill(draw, cx - 3, cy - 3, 2, (255, 160, 80))
    # Fuse
    draw_fuse(draw, cx, cy - 9, (200, 150, 50))
    save(img, os.path.join(BOMBS_DIR, "mega.png"))


def gen_void():
    """void.png — Dark orb with purple ring, black/purple, 32×32"""
    img, draw = new_img(32, 32, (8, 4, 16, 255))
    cx, cy = 16, 16
    # Outer purple glow ring
    pixel_ring(draw, cx, cy, 11, 14, (80, 20, 140))
    pixel_ring(draw, cx, cy, 9, 11, (50, 10, 100))
    # Dark orb
    pixel_circle_fill(draw, cx, cy, 9, (20, 10, 40))
    # Void swirl — lighter arcs
    for i in range(3):
        a_start = i * 2 * math.pi / 3
        pts = []
        for j in range(20):
            a = a_start + j * math.pi / 20
            r = 6 - j * 0.1
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        if len(pts) >= 2:
            draw.line(pts, fill=(120, 60, 200), width=1)
    # Tiny purple gleam
    pixel_circle_fill(draw, cx - 2, cy - 3, 1, (160, 100, 255))
    draw_fuse(draw, cx, cy - 9, (100, 60, 160))
    save(img, os.path.join(BOMBS_DIR, "void.png"))


def gen_cluster():
    """cluster.png — Multiple small bombs, orange/red, 32×32"""
    img, draw = new_img(32, 32, (10, 6, 6, 255))
    # Main central bomb
    draw_bomb_base(draw, 16, 17, 7, (200, 80, 20), (100, 30, 10), (255, 160, 80))
    draw_fuse(draw, 16, 10, (180, 130, 40))
    # Smaller satellite bombs
    for angle, dist in [(45, 11), (135, 11), (225, 11), (315, 11)]:
        a = math.radians(angle)
        sx = int(16 + dist * math.cos(a))
        sy = int(17 + dist * math.sin(a))
        draw_bomb_base(draw, sx, sy, 4, (220, 100, 30), (120, 40, 10), (255, 180, 80))
    save(img, os.path.join(BOMBS_DIR, "cluster.png"))


def gen_drill():
    """drill.png — Arrow/drill tip, silver/grey, 32×32"""
    img, draw = new_img(32, 32, (8, 8, 12, 255))
    # Drill tip (pointing right)
    # Main arrowhead
    tip = [(30, 16), (14, 6), (14, 26)]
    draw.polygon(tip, fill=(180, 190, 200))
    # Bright edge
    draw.line([(30, 16), (14, 6)], fill=(240, 245, 255), width=1)
    # Shaft
    draw.rectangle([4, 13, 15, 19], fill=(140, 150, 160))
    # Shaft grooves
    for gx in range(6, 15, 3):
        draw.line([(gx, 13), (gx, 19)], fill=(100, 110, 120), width=1)
    # Top dark edge of shaft
    draw.line([(4, 13), (15, 13)], fill=(80, 90, 100), width=1)
    draw.line([(4, 19), (15, 19)], fill=(80, 90, 100), width=1)
    # Back cap
    draw.rectangle([2, 11, 5, 21], fill=(110, 115, 125))
    # Shine on arrowhead
    draw.line([(28, 15), (16, 8)], fill=(255, 255, 255), width=1)
    save(img, os.path.join(BOMBS_DIR, "drill.png"))


def gen_flame():
    """flame.png — Flame shape, orange/red, 32×32"""
    img, draw = new_img(32, 32, (10, 5, 5, 255))
    cx = 16
    # Outer flame (red-orange)
    outer_flame = [
        (16, 2), (22, 8), (26, 6), (24, 14),
        (28, 16), (24, 22), (26, 28), (22, 30),
        (16, 28), (10, 30), (6, 28), (8, 22),
        (4, 16), (8, 14), (6, 6), (10, 8)
    ]
    draw.polygon(outer_flame, fill=(200, 60, 10))
    # Mid flame
    mid_flame = [
        (16, 5), (20, 10), (23, 9), (21, 15),
        (24, 17), (21, 22), (22, 27), (19, 28),
        (16, 26), (13, 28), (10, 27), (11, 22),
        (8, 17), (11, 15), (9, 9), (12, 10)
    ]
    draw.polygon(mid_flame, fill=(230, 100, 20))
    # Inner flame (bright)
    inner_flame = [
        (16, 9), (19, 14), (21, 17), (19, 21),
        (16, 23), (13, 21), (11, 17), (13, 14)
    ]
    draw.polygon(inner_flame, fill=(255, 180, 30))
    # Core
    pixel_circle_fill(draw, 16, 18, 4, (255, 230, 80))
    pixel_circle_fill(draw, 16, 19, 2, (255, 255, 160))
    save(img, os.path.join(BOMBS_DIR, "flame.png"))


def gen_holy():
    """holy.png — Cross with glow, gold/white, 32×32"""
    img, draw = new_img(32, 32, (8, 6, 16, 255))
    cx, cy = 16, 16
    # Glow halo (large semi-transparent ring)
    pixel_ring(draw, cx, cy, 12, 15, (180, 150, 40, 180))
    pixel_ring(draw, cx, cy, 10, 12, (220, 190, 80, 140))
    # Cross shape
    draw.rectangle([cx - 3, cy - 13, cx + 3, cy + 13], fill=(220, 190, 60))
    draw.rectangle([cx - 13, cy - 3, cx + 13, cy + 3], fill=(220, 190, 60))
    # Cross bright inner strip
    draw.rectangle([cx - 1, cy - 13, cx + 1, cy + 13], fill=(255, 240, 140))
    draw.rectangle([cx - 13, cy - 1, cx + 13, cy + 1], fill=(255, 240, 140))
    # Center orb
    pixel_circle_fill(draw, cx, cy, 4, (255, 240, 100))
    pixel_circle_fill(draw, cx, cy, 2, (255, 255, 220))
    # Corner sparkles
    for sx, sy in ((4, 4), (28, 4), (4, 28), (28, 28)):
        draw.point((sx, sy), fill=(255, 255, 180))
        draw.point((sx + 1, sy), fill=(255, 240, 120))
        draw.point((sx, sy + 1), fill=(255, 240, 120))
    save(img, os.path.join(BOMBS_DIR, "holy.png"))


# ---------------------------------------------------------------------------
# ==================  VFX SPRITES  ==================
# ---------------------------------------------------------------------------

def gen_explosion_ring():
    """explosion_ring.png — 64×64, orange/red expanding ring"""
    img, draw = new_img(64, 64)
    cx, cy = 32, 32
    # Outer glow ring
    pixel_ring(draw, cx, cy, 26, 31, (120, 40, 10, 120))
    pixel_ring(draw, cx, cy, 22, 26, (200, 80, 20, 180))
    pixel_ring(draw, cx, cy, 18, 22, (240, 120, 30, 220))
    pixel_ring(draw, cx, cy, 15, 18, (255, 160, 60, 200))
    pixel_ring(draw, cx, cy, 12, 15, (255, 200, 80, 160))
    # Jagged edge (spikes on ring)
    for i in range(12):
        a = 2 * math.pi * i / 12
        x_in  = int(cx + 22 * math.cos(a))
        y_in  = int(cy + 22 * math.sin(a))
        x_out = int(cx + 30 * math.cos(a))
        y_out = int(cy + 30 * math.sin(a))
        draw.line([(x_in, y_in), (x_out, y_out)], fill=(255, 220, 60, 200), width=2)
    save(img, os.path.join(VFX_DIR, "explosion_ring.png"))


def gen_chain_spark():
    """chain_spark.png — 32×32, yellow electric spark"""
    img, draw = new_img(32, 32)
    cx, cy = 16, 16
    # Multiple jagged lines radiating out
    for i in range(8):
        a = math.pi * i / 4
        prev = (cx, cy)
        r_step = 4
        color = (255, 220, 40) if i % 2 == 0 else (180, 220, 255)
        for step in range(1, 4):
            r = r_step * step
            jitter_a = a + (0.3 if step % 2 == 0 else -0.3)
            nx = int(cx + r * math.cos(jitter_a))
            ny = int(cy + r * math.sin(jitter_a))
            draw.line([prev, (nx, ny)], fill=color, width=1)
            prev = (nx, ny)
    # Center dot
    pixel_circle_fill(draw, cx, cy, 3, (255, 255, 160))
    pixel_circle_fill(draw, cx, cy, 1, (255, 255, 255))
    save(img, os.path.join(VFX_DIR, "chain_spark.png"))


def gen_boss_hit_flash():
    """boss_hit_flash.png — 64×64, white flash with red edge"""
    img, draw = new_img(64, 64)
    cx, cy = 32, 32
    # Red outer glow
    pixel_ring(draw, cx, cy, 26, 31, (200, 20, 20, 180))
    pixel_ring(draw, cx, cy, 22, 26, (255, 60, 40, 200))
    # White inner flash fading to transparent
    pixel_ring(draw, cx, cy, 16, 22, (255, 200, 200, 180))
    pixel_ring(draw, cx, cy, 10, 16, (255, 230, 230, 220))
    pixel_ring(draw, cx, cy, 4, 10, (255, 255, 255, 200))
    pixel_circle_fill(draw, cx, cy, 4, (255, 255, 255, 160))
    save(img, os.path.join(VFX_DIR, "boss_hit_flash.png"))


def gen_weak_point_glow():
    """weak_point_glow.png — 32×32, yellow pulsing star"""
    img, draw = new_img(32, 32)
    cx, cy = 16, 16
    # Soft glow ring
    pixel_ring(draw, cx, cy, 13, 15, (200, 180, 20, 140))
    pixel_ring(draw, cx, cy, 10, 13, (230, 210, 40, 180))
    # 8-point star
    star_pts = star_polygon(cx, cy, 8, 12, 5, -math.pi / 2)
    draw.polygon(star_pts, fill=(255, 230, 60))
    # Inner star
    inner_star = star_polygon(cx, cy, 8, 7, 3, -math.pi / 2)
    draw.polygon(inner_star, fill=(255, 255, 160))
    # Center
    pixel_circle_fill(draw, cx, cy, 2, (255, 255, 220))
    save(img, os.path.join(VFX_DIR, "weak_point_glow.png"))


def gen_debuff_icon():
    """debuff_icon.png — 24×24, red downward arrow"""
    img, draw = new_img(24, 24)
    # Arrow head (pointed down)
    arrow = [(12, 22), (3, 10), (8, 10), (8, 2), (16, 2), (16, 10), (21, 10)]
    draw.polygon(arrow, fill=(200, 30, 30))
    # Bright edge
    draw.line([(12, 22), (3, 10)], fill=(255, 80, 80), width=1)
    draw.line([(12, 22), (21, 10)], fill=(255, 80, 80), width=1)
    # Dark outline
    draw.polygon(arrow, outline=(100, 10, 10))
    save(img, os.path.join(VFX_DIR, "debuff_icon.png"))


def gen_upgrade_shine():
    """upgrade_shine.png — 48×48, gold sparkle/star burst"""
    img, draw = new_img(48, 48)
    cx, cy = 24, 24
    # Big 4-point star
    big_star = star_polygon(cx, cy, 4, 22, 4, 0)
    draw.polygon(big_star, fill=(220, 180, 30, 220))
    # 8-point secondary star
    sec_star = star_polygon(cx, cy, 8, 14, 5, math.pi / 8)
    draw.polygon(sec_star, fill=(255, 220, 60, 200))
    # Glow ring
    pixel_ring(draw, cx, cy, 18, 22, (180, 140, 20, 100))
    # Center
    pixel_circle_fill(draw, cx, cy, 5, (255, 240, 120))
    pixel_circle_fill(draw, cx, cy, 3, (255, 255, 220))
    # Sparkle dots at corners
    for sx, sy in ((8, 8), (40, 8), (8, 40), (40, 40), (24, 4), (24, 44), (4, 24), (44, 24)):
        draw.point((sx, sy), fill=(255, 240, 100, 200))
        if sx > 1: draw.point((sx - 1, sy), fill=(220, 200, 60, 150))
    save(img, os.path.join(VFX_DIR, "upgrade_shine.png"))


def gen_floor_transition():
    """floor_transition.png — 128×128, dark vortex spiral"""
    img, draw = new_img(128, 128, (0, 0, 0, 255))
    cx, cy = 64, 64
    # Concentric rings in dark purple/indigo
    ring_colors = [
        (60, 0, 100), (80, 10, 130), (100, 20, 160),
        (60, 0, 100), (40, 0, 80), (20, 0, 50)
    ]
    for i, rc in enumerate(ring_colors):
        r_out = 60 - i * 8
        r_in  = max(0, r_out - 6)
        if r_out > 0:
            pixel_ring(draw, cx, cy, r_in, r_out, rc)
    # Spiral arms
    for arm in range(3):
        a0 = arm * 2 * math.pi / 3
        for t in range(80):
            frac = t / 80
            a = a0 + frac * 4 * math.pi  # 2 full rotations
            r = 60 * (1 - frac)
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            intensity = int(80 + 120 * frac)
            draw.point((x, y), fill=(intensity // 2, 0, intensity))
            if t > 0:
                a_prev = a0 + (t - 1) / 80 * 4 * math.pi
                r_prev = 60 * (1 - (t - 1) / 80)
                xp = int(cx + r_prev * math.cos(a_prev))
                yp = int(cy + r_prev * math.sin(a_prev))
                draw.line([(xp, yp), (x, y)], fill=(intensity // 2, 0, intensity), width=1)
    # Dark center
    pixel_circle_fill(draw, cx, cy, 8, (0, 0, 0, 255))
    # Star in center
    star_pts = star_polygon(cx, cy, 6, 6, 2, 0)
    draw.polygon(star_pts, fill=(160, 80, 255))
    save(img, os.path.join(VFX_DIR, "floor_transition.png"))


def gen_death_particles():
    """death_particles.png — 32×32, gray dust particles"""
    img, draw = new_img(32, 32)
    # Scattered dust particle clusters
    import random
    random.seed(42)
    for _ in range(40):
        px = random.randint(1, 30)
        py = random.randint(1, 30)
        sz = random.randint(1, 3)
        gray = random.randint(100, 180)
        alpha = random.randint(140, 220)
        pixel_circle_fill(draw, px, py, sz, (gray, gray, gray - 10, alpha))
    # A couple bigger ash chunks
    for px, py in ((8, 10), (22, 8), (14, 22), (25, 24)):
        pixel_circle_fill(draw, px, py, 3, (120, 120, 110, 200))
        pixel_circle_fill(draw, px, py, 1, (180, 175, 165, 220))
    save(img, os.path.join(VFX_DIR, "death_particles.png"))


# ---------------------------------------------------------------------------
# ==================  UI SPRITES  ==================
# ---------------------------------------------------------------------------

def gen_cell(filename, border_color, fill_color, inner_color,
             extra_fn=None, size=64):
    """Generic grid cell with border and fill."""
    img, draw = new_img(size, size, (0, 0, 0, 255))
    # Outer border
    draw.rectangle([0, 0, size - 1, size - 1], fill=border_color)
    # Inner fill
    draw.rectangle([2, 2, size - 3, size - 3], fill=fill_color)
    # Inner highlight
    draw.rectangle([3, 3, size - 4, size - 4], fill=inner_color)
    if extra_fn:
        extra_fn(draw, size)
    save(img, os.path.join(UI_DIR, filename))
    return img, draw


def gen_cell_empty():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(50, 50, 55))
    draw.rectangle([2, 2, 61, 61], fill=(35, 35, 40))
    draw.rectangle([3, 3, 60, 60], fill=(40, 40, 46))
    # Subtle grid corner marks
    for cx2, cy2 in ((3, 3), (60, 3), (3, 60), (60, 60)):
        draw.point((cx2, cy2), fill=(60, 60, 66))
    save(img, os.path.join(UI_DIR, "cell_empty.png"))


def gen_cell_boss_normal():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(80, 20, 20))
    draw.rectangle([2, 2, 61, 61], fill=(55, 15, 15))
    # Brick texture lines
    for row in range(4):
        y = 10 + row * 13
        draw.line([(3, y), (60, y)], fill=(70, 22, 22), width=1)
    for row in range(4):
        offset = 16 if row % 2 == 0 else 0
        for col in range(3):
            x = 3 + offset + col * 32
            y = 4 + row * 13
            draw.line([(x, y), (x, y + 12)], fill=(70, 22, 22), width=1)
    # Top-left shine
    draw.line([(2, 2), (61, 2)], fill=(100, 30, 30), width=1)
    draw.line([(2, 2), (2, 61)], fill=(100, 30, 30), width=1)
    save(img, os.path.join(UI_DIR, "cell_boss_normal.png"))


def gen_cell_boss_weak():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(180, 160, 20))
    draw.rectangle([2, 2, 61, 61], fill=(50, 40, 10))
    draw.rectangle([3, 3, 60, 60], fill=(55, 48, 12))
    # Glow inner border
    draw.rectangle([4, 4, 59, 59], outline=(200, 180, 40), width=2)
    # Corner glow points
    for cx2, cy2 in ((6, 6), (57, 6), (6, 57), (57, 57), (32, 4), (32, 59), (4, 32), (59, 32)):
        pixel_circle_fill(draw, cx2, cy2, 2, (220, 200, 60))
    save(img, os.path.join(UI_DIR, "cell_boss_weak.png"))


def gen_cell_boss_armor():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    # Heavy blue-grey border
    draw.rectangle([0, 0, 63, 63], fill=(60, 70, 90))
    draw.rectangle([3, 3, 60, 60], fill=(40, 48, 62))
    draw.rectangle([5, 5, 58, 58], fill=(46, 55, 70))
    # Rivet bolts at corners
    for cx2, cy2 in ((8, 8), (55, 8), (8, 55), (55, 55)):
        pixel_circle_fill(draw, cx2, cy2, 3, (80, 90, 110))
        pixel_circle_fill(draw, cx2, cy2, 1, (140, 150, 170))
    # Armor plate lines
    draw.line([(16, 5), (16, 58)], fill=(55, 64, 80), width=1)
    draw.line([(48, 5), (48, 58)], fill=(55, 64, 80), width=1)
    draw.line([(5, 16), (58, 16)], fill=(55, 64, 80), width=1)
    draw.line([(5, 48), (58, 48)], fill=(55, 64, 80), width=1)
    # Top highlight
    draw.line([(3, 3), (60, 3)], fill=(90, 100, 120), width=1)
    draw.line([(3, 3), (3, 60)], fill=(90, 100, 120), width=1)
    save(img, os.path.join(UI_DIR, "cell_boss_armor.png"))


def gen_cell_boss_absorb():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(20, 100, 40))
    draw.rectangle([2, 2, 61, 61], fill=(15, 60, 28))
    draw.rectangle([3, 3, 60, 60], fill=(18, 70, 32))
    # Shimmer diagonal lines
    for i in range(0, 64, 8):
        draw.line([(i, 3), (i + 58, 61)], fill=(30, 90, 48), width=1)
    # Border highlight
    draw.rectangle([4, 4, 59, 59], outline=(40, 140, 60), width=1)
    # Center orb
    pixel_circle_fill(draw, 32, 32, 8, (20, 100, 44))
    pixel_ring(draw, 32, 32, 5, 8, (30, 140, 55))
    pixel_circle_fill(draw, 32, 32, 4, (40, 160, 70))
    save(img, os.path.join(UI_DIR, "cell_boss_absorb.png"))


def gen_cell_boss_dead():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(15, 15, 15))
    draw.rectangle([2, 2, 61, 61], fill=(10, 10, 10))
    # X marks
    draw.line([(8, 8), (56, 56)], fill=(60, 20, 20, 180), width=3)
    draw.line([(56, 8), (8, 56)], fill=(60, 20, 20, 180), width=3)
    # Low opacity border
    draw.rectangle([2, 2, 61, 61], outline=(40, 40, 40), width=1)
    save(img, os.path.join(UI_DIR, "cell_boss_dead.png"))


def gen_cell_mine_hidden():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(55, 55, 60))
    draw.rectangle([3, 3, 60, 60], fill=(40, 40, 44))
    # Classic minesweeper raised look (top-left lighter, bottom-right darker)
    draw.line([(3, 3), (60, 3)], fill=(68, 68, 74), width=2)
    draw.line([(3, 3), (3, 60)], fill=(68, 68, 74), width=2)
    draw.line([(3, 60), (60, 60)], fill=(28, 28, 32), width=2)
    draw.line([(60, 3), (60, 60)], fill=(28, 28, 32), width=2)
    save(img, os.path.join(UI_DIR, "cell_mine_hidden.png"))


def gen_cell_mine_revealed():
    img, draw = new_img(64, 64, (0, 0, 0, 255))
    draw.rectangle([0, 0, 63, 63], fill=(70, 70, 76))
    draw.rectangle([3, 3, 60, 60], fill=(58, 58, 64))
    # Sunken look (opposite of raised)
    draw.line([(3, 3), (60, 3)], fill=(44, 44, 50), width=1)
    draw.line([(3, 3), (3, 60)], fill=(44, 44, 50), width=1)
    draw.line([(3, 60), (60, 60)], fill=(80, 80, 88), width=1)
    draw.line([(60, 3), (60, 60)], fill=(80, 80, 88), width=1)
    save(img, os.path.join(UI_DIR, "cell_mine_revealed.png"))


def gen_bomb_counter_bg():
    """bomb_counter_bg.png — 80×32, HUD bomb count background, dark pill"""
    img, draw = new_img(80, 32, (0, 0, 0, 0))
    r = 14
    # Fill pill shape with rounded ends
    draw.rectangle([r, 0, 80 - r, 31], fill=(30, 28, 40, 230))
    draw.ellipse([0, 0, r * 2, 31], fill=(30, 28, 40, 230))
    draw.ellipse([80 - r * 2, 0, 79, 31], fill=(30, 28, 40, 230))
    # Border
    draw.rectangle([r, 1, 80 - r, 30], outline=(80, 70, 110, 200))
    draw.arc([0, 0, r * 2, 31], 90, 270, fill=(80, 70, 110, 200))
    draw.arc([80 - r * 2, 0, 79, 31], 270, 90, fill=(80, 70, 110, 200))
    save(img, os.path.join(UI_DIR, "bomb_counter_bg.png"))


def gen_hp_bar_bg():
    """hp_bar_bg.png — 200×20, HP bar background dark red"""
    img, draw = new_img(200, 20, (0, 0, 0, 255))
    draw.rectangle([0, 0, 199, 19], fill=(40, 8, 8))
    draw.rectangle([1, 1, 198, 18], fill=(55, 12, 12))
    # Inner recessed
    draw.rectangle([2, 2, 197, 17], fill=(30, 6, 6))
    draw.line([(2, 2), (197, 2)], fill=(70, 16, 16), width=1)
    draw.line([(2, 2), (2, 17)], fill=(70, 16, 16), width=1)
    save(img, os.path.join(UI_DIR, "hp_bar_bg.png"))


def gen_hp_bar_fill():
    """hp_bar_fill.png — 200×20, HP fill green to red gradient"""
    img, draw = new_img(200, 20, (0, 0, 0, 0))
    for x in range(200):
        t = x / 199
        # Green (0,200,60) -> Yellow (220,200,0) -> Red (220,40,20)
        if t < 0.5:
            t2 = t * 2
            r = int(0 + 220 * t2)
            g = int(200 + 0 * t2)
            b = int(60 - 60 * t2)
        else:
            t2 = (t - 0.5) * 2
            r = 220
            g = int(200 - 160 * t2)
            b = int(0)
        col = (r, g, b, 255)
        # Add highlight strip
        for y in range(20):
            if y <= 3:
                factor = 1.2
                c = (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)), 255)
            elif y >= 17:
                factor = 0.7
                c = (int(r * factor), int(g * factor), int(b * factor), 255)
            else:
                c = col
            draw.point((x, y), fill=c)
    save(img, os.path.join(UI_DIR, "hp_bar_fill.png"))


def gen_boss_hp_bg():
    """boss_hp_bg.png — 300×20, Boss HP background"""
    img, draw = new_img(300, 20, (0, 0, 0, 255))
    draw.rectangle([0, 0, 299, 19], fill=(30, 6, 20))
    draw.rectangle([1, 1, 298, 18], fill=(44, 10, 28))
    draw.rectangle([2, 2, 297, 17], fill=(22, 4, 14))
    draw.line([(2, 2), (297, 2)], fill=(60, 14, 36), width=1)
    draw.line([(2, 2), (2, 17)], fill=(60, 14, 36), width=1)
    save(img, os.path.join(UI_DIR, "boss_hp_bg.png"))


def gen_boss_hp_fill():
    """boss_hp_fill.png — 300×20, Boss HP fill dark red to orange"""
    img, draw = new_img(300, 20, (0, 0, 0, 0))
    for x in range(300):
        t = x / 299
        r = int(160 + 95 * t)
        g = int(10 + 70 * t)
        b = 10
        for y in range(20):
            if y <= 3:
                factor = 1.3
                c = (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)), 255)
            elif y >= 17:
                factor = 0.65
                c = (int(r * factor), int(g * factor), int(b * factor), 255)
            else:
                c = (r, g, b, 255)
            draw.point((x, y), fill=c)
    save(img, os.path.join(UI_DIR, "boss_hp_fill.png"))


def gen_timer_circle():
    """timer_circle.png — 64×64, circular timer background"""
    img, draw = new_img(64, 64, (0, 0, 0, 0))
    cx, cy = 32, 32
    # Outer ring dark grey
    pixel_circle_fill(draw, cx, cy, 30, (40, 40, 50, 230))
    # Track ring
    pixel_ring(draw, cx, cy, 24, 30, (20, 20, 28, 240))
    # Inner face
    pixel_circle_fill(draw, cx, cy, 24, (28, 26, 38, 220))
    # Tick marks
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        x_in  = int(cx + 22 * math.cos(a))
        y_in  = int(cy + 22 * math.sin(a))
        x_out = int(cx + 29 * math.cos(a))
        y_out = int(cy + 29 * math.sin(a))
        tick_col = (140, 130, 160, 220) if i % 3 == 0 else (80, 75, 95, 180)
        draw.line([(x_in, y_in), (x_out, y_out)], fill=tick_col, width=1 if i % 3 != 0 else 2)
    # Center dot
    pixel_circle_fill(draw, cx, cy, 3, (160, 150, 200, 230))
    pixel_circle_fill(draw, cx, cy, 1, (220, 215, 240, 255))
    save(img, os.path.join(UI_DIR, "timer_circle.png"))


def gen_floor_badge():
    """floor_badge.png — 96×48, golden frame badge"""
    img, draw = new_img(96, 48, (0, 0, 0, 0))
    # Outer golden frame
    draw.rectangle([0, 0, 95, 47], fill=(100, 80, 10))
    draw.rectangle([2, 2, 93, 45], fill=(50, 35, 5))
    draw.rectangle([4, 4, 91, 43], fill=(60, 45, 8))
    # Corner ornaments
    for cx2, cy2 in ((6, 6), (89, 6), (6, 41), (89, 41)):
        pixel_circle_fill(draw, cx2, cy2, 3, (180, 150, 30))
        pixel_circle_fill(draw, cx2, cy2, 1, (240, 210, 80))
    # Top/bottom decorative lines
    draw.line([(10, 4), (85, 4)], fill=(180, 150, 30), width=1)
    draw.line([(10, 43), (85, 43)], fill=(180, 150, 30), width=1)
    # Left/right lines
    draw.line([(4, 10), (4, 37)], fill=(180, 150, 30), width=1)
    draw.line([(91, 10), (91, 37)], fill=(180, 150, 30), width=1)
    # Inner panel
    draw.rectangle([6, 6, 89, 41], fill=(35, 25, 5))
    # Double inner border
    draw.rectangle([7, 7, 88, 40], outline=(140, 110, 20), width=1)
    draw.rectangle([9, 9, 86, 38], outline=(80, 60, 10), width=1)
    save(img, os.path.join(UI_DIR, "floor_badge.png"))


# ---------------------------------------------------------------------------
# Run all generators
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Generating Bomb Sprites ===")
    gen_nova()
    gen_frost()
    gen_poison()
    gen_thunder()
    gen_mega()
    gen_void()
    gen_cluster()
    gen_drill()
    gen_flame()
    gen_holy()

    print("\n=== Generating VFX Sprites ===")
    gen_explosion_ring()
    gen_chain_spark()
    gen_boss_hit_flash()
    gen_weak_point_glow()
    gen_debuff_icon()
    gen_upgrade_shine()
    gen_floor_transition()
    gen_death_particles()

    print("\n=== Generating UI Sprites ===")
    gen_cell_empty()
    gen_cell_boss_normal()
    gen_cell_boss_weak()
    gen_cell_boss_armor()
    gen_cell_boss_absorb()
    gen_cell_boss_dead()
    gen_cell_mine_hidden()
    gen_cell_mine_revealed()
    gen_bomb_counter_bg()
    gen_hp_bar_bg()
    gen_hp_bar_fill()
    gen_boss_hp_bg()
    gen_boss_hp_fill()
    gen_timer_circle()
    gen_floor_badge()

    print("\nDone! All sprites generated.")
