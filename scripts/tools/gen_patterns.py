"""装饰线条 & 花纹纹路生成器 (三主题版)
每个主题生成独立配色:
  sakura/ — 粉紫/薰衣草, 配深紫红
  steam/  — 暖金/琥珀/铜, 配深棕
  neon/   — 霓虹粉/青, 配深紫蓝

每套包含:
  divider_ornate.png     华丽分割线
  divider_chain.png      锁链分割线
  divider_wave.png       波浪分割线
  corner_ornament.png    角落装饰 (4方向)
  corner_tl.png          左上角单独
  border_rune.png        符文边框 (九宫格)
  pattern_celtic.png     凯尔特结 (可平铺)
  pattern_diamond.png    菱形编织 (可平铺)
  pattern_vine.png       藤蔓花纹 (可平铺)
  pattern_scale.png      龙鳞纹路 (可平铺)
  pattern_zigzag.png     锯齿纹路 (可平铺)
  pattern_spiral.png     旋涡纹路
  pattern_greek_key.png  希腊回纹
  pattern_weave.png      编织纹路 (可平铺)
"""
import os, math, random
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "ui", "patterns")

# ─── 三套主题调色板 ───────────────────────────────
PALETTES = {
    "sakura": {
        "primary":     (255, 150, 200),   # 樱花粉
        "primary_hi":  (255, 200, 230),
        "primary_lo":  (180, 100, 140),
        "primary_dk":  (110, 60, 85),
        "secondary":   (180, 120, 220),   # 薰衣草
        "secondary_hi":(220, 170, 255),
        "secondary_lo":(120, 80, 150),
        "metal":       (180, 165, 190),   # 银紫
        "metal_hi":    (220, 210, 230),
        "metal_lo":    (120, 110, 135),
        "gem":         (200, 40, 80),     # 红宝石
        "gem_hi":      (240, 90, 120),
        "gem2":        (100, 200, 160),   # 翡翠
        "gem3":        (150, 120, 255),   # 紫宝石
        "vine_dk":     (80, 50, 90),
        "vine":        (120, 80, 130),
        "vine_hi":     (170, 120, 180),
        "flower":      (255, 130, 180),
        "scale_a":     ((80, 50, 70), (110, 70, 95), (140, 95, 120)),
        "scale_b":     ((70, 45, 80), (100, 65, 110), (130, 90, 140)),
    },
    "steam": {
        "primary":     (220, 180, 50),    # 金色
        "primary_hi":  (255, 225, 100),
        "primary_lo":  (160, 120, 30),
        "primary_dk":  (100, 75, 20),
        "secondary":   (170, 110, 55),    # 古铜
        "secondary_hi":(210, 155, 90),
        "secondary_lo":(110, 70, 30),
        "metal":       (180, 185, 195),   # 银
        "metal_hi":    (220, 225, 235),
        "metal_lo":    (120, 125, 135),
        "gem":         (200, 40, 50),     # 红宝石
        "gem_hi":      (240, 90, 100),
        "gem2":        (40, 180, 80),     # 翡翠
        "gem3":        (60, 200, 220),    # 青宝石
        "vine_dk":     (50, 100, 40),
        "vine":        (70, 140, 55),
        "vine_hi":     (100, 180, 80),
        "flower":      (200, 80, 120),
        "scale_a":     ((60, 90, 60), (80, 120, 80), (100, 150, 100)),
        "scale_b":     ((50, 80, 70), (70, 110, 90), (90, 140, 110)),
    },
    "neon": {
        "primary":     (255, 50, 200),    # 霓虹粉
        "primary_hi":  (255, 120, 230),
        "primary_lo":  (180, 20, 140),
        "primary_dk":  (100, 10, 80),
        "secondary":   (0, 220, 255),     # 电光青
        "secondary_hi":(100, 240, 255),
        "secondary_lo":(0, 140, 180),
        "metal":       (100, 80, 160),    # 紫钢
        "metal_hi":    (150, 130, 210),
        "metal_lo":    (50, 40, 100),
        "gem":         (255, 30, 120),    # 品红宝石
        "gem_hi":      (255, 90, 170),
        "gem2":        (0, 230, 200),     # 青绿
        "gem3":        (150, 50, 255),    # 紫电
        "vine_dk":     (30, 10, 60),      # 数据流
        "vine":        (60, 20, 120),
        "vine_hi":     (100, 40, 180),
        "flower":      (255, 50, 180),
        "scale_a":     ((20, 10, 50), (35, 20, 80), (50, 30, 110)),
        "scale_b":     ((35, 15, 60), (55, 25, 90), (75, 40, 130)),
    },
}

random.seed(2026)


def save(img, theme, name):
    d = os.path.join(ROOT, theme)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    img.save(path)
    print(f"  ✓ {theme}/{name} ({img.width}x{img.height})")


def col_a(c, a=255):
    return c + (a,)


# ═══════════════════════════════════════════════
# 1. 华丽分割线  256 x 24
# ═══════════════════════════════════════════════
def gen_divider_ornate(theme, p):
    W, H = 256, 24
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cy = H // 2

    dr.line([(8, cy - 1), (W - 9, cy - 1)], fill=col_a(p["primary_hi"], 200), width=1)
    dr.line([(8, cy),     (W - 9, cy)],     fill=col_a(p["primary"], 240),    width=2)
    dr.line([(8, cy + 2), (W - 9, cy + 2)], fill=col_a(p["primary_lo"], 180), width=1)

    for sx in [0, W]:
        d = 1 if sx == 0 else -1
        for i in range(6):
            angle = i * 0.5
            x = sx + d * (8 + int(math.cos(angle) * 5))
            y = cy + int(math.sin(angle) * (3 + i * 0.5))
            dr.rectangle([x, y, x + 1, y + 1], fill=col_a(p["primary"], 200 - i * 15))
        for i in range(8):
            t = i * 0.6
            x = sx + d * (4 + int(math.cos(t) * (3 - i * 0.3)))
            y = cy + int(math.sin(t) * (3 - i * 0.3))
            dr.point((x, y), fill=col_a(p["primary_hi"], 220 - i * 15))

    gem_r = 4
    dr.ellipse([W // 2 - gem_r, cy - gem_r, W // 2 + gem_r, cy + gem_r],
               fill=col_a(p["gem"], 255), outline=col_a(p["primary"], 255))
    dr.ellipse([W // 2 - 2, cy - 2, W // 2, cy], fill=col_a(p["gem_hi"], 180))

    for offset in [40, 80, 120]:
        for sign in [-1, 1]:
            x = W // 2 + sign * offset
            dr.polygon([(x, cy - 3), (x + 2, cy), (x, cy + 3), (x - 2, cy)],
                       fill=col_a(p["primary_hi"], 160))
            dr.point((x, cy - 2), fill=col_a(p["primary_hi"], 220))

    save(img, theme, "divider_ornate.png")


# ═══════════════════════════════════════════════
# 2. 锁链分割线  256 x 20
# ═══════════════════════════════════════════════
def gen_divider_chain(theme, p):
    W, H = 256, 20
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cy = H // 2
    link_w, link_h = 14, 10
    gap = 2

    x = 4
    idx = 0
    while x + link_w < W - 4:
        y0 = cy - link_h // 2 + (1 if idx % 2 else -1)
        dr.rounded_rectangle([x, y0, x + link_w, y0 + link_h],
                             radius=3, outline=col_a(p["metal"], 220), width=2)
        dr.line([(x + 2, y0 + 1), (x + link_w - 2, y0 + 1)],
                fill=col_a(p["metal_hi"], 140), width=1)
        dr.line([(x + 2, y0 + link_h - 1), (x + link_w - 2, y0 + link_h - 1)],
                fill=col_a(p["metal_lo"], 150), width=1)
        x += link_w - gap
        idx += 1

    save(img, theme, "divider_chain.png")


# ═══════════════════════════════════════════════
# 3. 波浪分割线  256 x 16
# ═══════════════════════════════════════════════
def gen_divider_wave(theme, p):
    W, H = 256, 16
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cy = H // 2

    for color, amp, phase, width in [
        (col_a(p["secondary_lo"], 160), 4, 0.3, 2),
        (col_a(p["secondary"], 220),    3, 0.0, 2),
        (col_a(p["secondary_hi"], 140), 3, -0.3, 1),
    ]:
        pts = [(x, cy + int(amp * math.sin(x * 0.08 + phase))) for x in range(W)]
        dr.line(pts, fill=color, width=width)

    for x in range(0, W, 40):
        y = cy + int(3 * math.sin(x * 0.08))
        dr.rectangle([x - 1, y - 1, x + 1, y], fill=col_a(p["secondary_hi"], 200))

    save(img, theme, "divider_wave.png")


# ═══════════════════════════════════════════════
# 4. 角落装饰  64 x 64 → 128x128 合并
# ═══════════════════════════════════════════════
def gen_corner_ornament(theme, p):
    SZ = 64
    corner = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(corner)

    dr.line([(2, 2), (SZ - 6, 2)], fill=col_a(p["primary"], 240), width=3)
    dr.line([(2, 2), (2, SZ - 6)], fill=col_a(p["primary"], 240), width=3)
    dr.line([(4, 1), (SZ - 8, 1)], fill=col_a(p["primary_hi"], 160), width=1)
    dr.line([(1, 4), (1, SZ - 8)], fill=col_a(p["primary_hi"], 160), width=1)

    dr.ellipse([0, 0, 8, 8], fill=col_a(p["gem2"], 255), outline=col_a(p["primary"], 255))
    dr.point((2, 2), fill=col_a(p["primary_hi"], 200))

    for i in range(3):
        bx = 16 + i * 14
        dr.polygon([(bx, 2), (bx + 5, 6), (bx + 10, 2), (bx + 5, -2)],
                   fill=col_a(p["primary_lo"], 140 - i * 20))
        dr.line([(bx + 2, 2), (bx + 8, 2)], fill=col_a(p["primary_hi"], 120), width=1)

    for i in range(3):
        by = 16 + i * 14
        dr.polygon([(2, by), (6, by + 5), (2, by + 10), (-2, by + 5)],
                   fill=col_a(p["primary_lo"], 140 - i * 20))
        dr.line([(2, by + 2), (2, by + 8)], fill=col_a(p["primary_hi"], 120), width=1)

    for t in range(20):
        angle = t * 0.25 + 0.5
        r = 6 + t * 0.6
        x = 4 + int(math.cos(angle) * r)
        y = 4 + int(math.sin(angle) * r)
        if 0 <= x < SZ and 0 <= y < SZ:
            dr.point((x, y), fill=col_a(p["primary"], max(40, 180 - t * 7)))

    out = Image.new("RGBA", (SZ * 2, SZ * 2), (0, 0, 0, 0))
    out.paste(corner, (0, 0))
    out.paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (SZ, 0))
    out.paste(corner.transpose(Image.FLIP_TOP_BOTTOM), (0, SZ))
    rot = corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    out.paste(rot, (SZ, SZ))

    save(out, theme, "corner_ornament.png")
    save(corner, theme, "corner_tl.png")


# ═══════════════════════════════════════════════
# 5. 符文边框 (九宫格)  48 x 48
# ═══════════════════════════════════════════════
def gen_border_rune(theme, p):
    SZ = 48
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = SZ // 2, SZ // 2

    dr.rectangle([0, 0, SZ - 1, SZ - 1], outline=col_a(p["primary_dk"], 200), width=2)
    dr.rectangle([3, 3, SZ - 4, SZ - 4], outline=col_a(p["primary"], 200), width=1)

    for mx, my in [(cx, 1), (cx, SZ - 2), (1, cy), (SZ - 2, cy)]:
        dr.rectangle([mx - 2, my - 1, mx + 2, my + 1], fill=col_a(p["gem3"], 180))
        dr.point((mx, my), fill=col_a(p["primary_hi"], 220))

    for cx2, cy2 in [(4, 4), (SZ - 5, 4), (4, SZ - 5), (SZ - 5, SZ - 5)]:
        dr.line([(cx2 - 2, cy2), (cx2 + 2, cy2)], fill=col_a(p["primary_hi"], 160), width=1)
        dr.line([(cx2, cy2 - 2), (cx2, cy2 + 2)], fill=col_a(p["primary_hi"], 160), width=1)

    for i in range(8, SZ - 8, 6):
        for pt in [(i, 2), (i, SZ - 3), (2, i), (SZ - 3, i)]:
            dr.point(pt, fill=col_a(p["primary"], 120))

    save(img, theme, "border_rune.png")


# ═══════════════════════════════════════════════
# 6. 凯尔特结  64 x 64
# ═══════════════════════════════════════════════
def gen_pattern_celtic(theme, p):
    SZ = 64
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = SZ // 2, SZ // 2
    r = 18

    arcs = [
        (cx - r // 2, cy - r // 2, 0, 90),
        (cx + r // 2, cy - r // 2, 90, 180),
        (cx + r // 2, cy + r // 2, 180, 270),
        (cx - r // 2, cy + r // 2, 270, 360),
    ]
    for ax, ay, a0, a1 in arcs:
        dr.arc([ax - r, ay - r, ax + r, ay + r], a0, a1,
               fill=col_a(p["primary_dk"], 200), width=5)
    for ax, ay, a0, a1 in arcs:
        dr.arc([ax - r, ay - r, ax + r, ay + r], a0, a1,
               fill=col_a(p["primary"], 230), width=3)
    for ax, ay, a0, a1 in arcs:
        dr.arc([ax - r + 1, ay - r + 1, ax + r - 1, ay + r - 1], a0, a0 + 30,
               fill=col_a(p["primary_hi"], 160), width=1)

    for kx, ky in [(cx, cy - r // 2 - 2), (cx, cy + r // 2 + 2),
                   (cx - r // 2 - 2, cy), (cx + r // 2 + 2, cy)]:
        dr.ellipse([kx - 2, ky - 2, kx + 2, ky + 2], fill=col_a(p["primary"], 200))
        dr.point((kx, ky - 1), fill=col_a(p["primary_hi"], 180))

    for cx2, cy2 in [(0, 0), (SZ - 1, 0), (0, SZ - 1), (SZ - 1, SZ - 1)]:
        dr.ellipse([cx2 - 2, cy2 - 2, cx2 + 2, cy2 + 2], fill=col_a(p["primary_lo"], 140))

    save(img, theme, "pattern_celtic.png")


# ═══════════════════════════════════════════════
# 7. 菱形编织  48 x 48
# ═══════════════════════════════════════════════
def gen_pattern_diamond(theme, p):
    SZ = 48
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = SZ // 2, SZ // 2

    dr.polygon([(cx, 4), (SZ - 4, cy), (cx, SZ - 4), (4, cy)],
               outline=col_a(p["metal"], 220))
    dr.polygon([(cx, 10), (SZ - 10, cy), (cx, SZ - 10), (10, cy)],
               outline=col_a(p["metal_hi"], 180))
    dr.line([(cx, 0), (cx, SZ)], fill=col_a(p["metal_lo"], 100), width=1)
    dr.line([(0, cy), (SZ, cy)], fill=col_a(p["metal_lo"], 100), width=1)
    dr.line([(0, 0), (SZ, SZ)], fill=col_a(p["metal_lo"], 80), width=1)
    dr.line([(SZ, 0), (0, SZ)], fill=col_a(p["metal_lo"], 80), width=1)
    dr.line([(cx - 6, cy - 6), (cx + 6, cy + 6)], fill=col_a(p["metal"], 160), width=2)
    dr.line([(cx + 6, cy - 6), (cx - 6, cy + 6)], fill=col_a(p["metal"], 160), width=2)
    dr.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=col_a(p["metal_hi"], 200))

    for ex, ey in [(cx, 0), (cx, SZ - 1), (0, cy), (SZ - 1, cy)]:
        dr.rectangle([ex - 1, ey - 1, ex + 1, ey + 1], fill=col_a(p["metal"], 160))

    save(img, theme, "pattern_diamond.png")


# ═══════════════════════════════════════════════
# 8. 藤蔓花纹  128 x 48
# ═══════════════════════════════════════════════
def gen_pattern_vine(theme, p):
    W, H = 128, 48
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cy = H // 2

    vine_pts = [(x, cy + int(8 * math.sin(x * 0.06))) for x in range(W)]
    dr.line(vine_pts, fill=col_a(p["vine_dk"], 220), width=4)
    dr.line(vine_pts, fill=col_a(p["vine"], 240), width=2)
    dr.line([(x, y - 1) for x, y in vine_pts], fill=col_a(p["vine_hi"], 120), width=1)

    for lx, direction in [(16, -1), (36, 1), (56, -1), (76, 1), (96, -1), (116, 1)]:
        ly = cy + int(8 * math.sin(lx * 0.06))
        tip_y = ly + direction * 12
        dr.polygon([(lx - 1, ly), (lx + direction * 4, ly + direction * 4),
                    (lx + direction * 2, tip_y), (lx - direction * 4, ly + direction * 6)],
                   fill=col_a(p["vine"], 180))
        dr.line([(lx, ly), (lx + direction, tip_y)], fill=col_a(p["vine_dk"], 160), width=1)
        dr.point((lx + direction * 2, tip_y - direction), fill=col_a(p["vine_hi"], 180))

    for tx in range(8, W, 24):
        ty = cy + int(8 * math.sin(tx * 0.06))
        side = 1 if (tx // 24) % 2 == 0 else -1
        tendril = []
        for t in range(12):
            angle = t * 0.4 + 1.0
            r = 3 + t * 0.3
            tendril.append((tx + int(math.cos(angle) * r) * side,
                           ty - int(math.sin(angle) * r)))
        if len(tendril) > 1:
            dr.line(tendril, fill=col_a(p["vine"], 80), width=1)

    for bx in [28, 68, 108]:
        by = cy + int(8 * math.sin(bx * 0.06)) - 6
        dr.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=col_a(p["flower"], 180))
        dr.point((bx - 1, by - 1), fill=col_a(p["secondary_hi"], 200))

    save(img, theme, "pattern_vine.png")


# ═══════════════════════════════════════════════
# 9. 龙鳞纹路  64 x 64
# ═══════════════════════════════════════════════
def gen_pattern_scale(theme, p):
    SZ = 64
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    scale_w, scale_h = 16, 12
    colors = [p["scale_a"], p["scale_b"]]

    for row in range(-1, SZ // scale_h + 2):
        offset = scale_w // 2 if row % 2 else 0
        for col in range(-1, SZ // scale_w + 2):
            x = col * scale_w + offset
            y = row * scale_h
            if x > SZ + scale_w or y > SZ + scale_h:
                continue
            dark, mid, light = colors[(row + col) % 2]
            dr.arc([x, y, x + scale_w, y + scale_h * 2], 200, 340,
                   fill=col_a(dark, 200), width=2)
            dr.arc([x + 2, y + 2, x + scale_w - 2, y + scale_h * 2 - 4], 210, 330,
                   fill=col_a(mid, 160), width=1)
            dr.arc([x + 3, y + 1, x + scale_w - 3, y + scale_h], 230, 310,
                   fill=col_a(light, 100), width=1)

    save(img, theme, "pattern_scale.png")


# ═══════════════════════════════════════════════
# 10. 锯齿纹路  64 x 32
# ═══════════════════════════════════════════════
def gen_pattern_zigzag(theme, p):
    W, H = 64, 32
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    tooth_w = 16

    for base_y, color, width in [
        (4,  p["primary_dk"],   3), (8,  p["primary"],     2), (12, p["primary_hi"],   1),
        (20, p["secondary_lo"], 3), (24, p["secondary"],    2), (28, p["secondary_hi"], 1),
    ]:
        pts, x, up = [], 0, True
        while x <= W:
            pts.append((x, base_y - 4 if up else base_y + 4))
            x += tooth_w // 2
            up = not up
        dr.line(pts, fill=col_a(color, 200), width=width)

    save(img, theme, "pattern_zigzag.png")


# ═══════════════════════════════════════════════
# 11. 旋涡纹路  64 x 64
# ═══════════════════════════════════════════════
def gen_pattern_spiral(theme, p):
    SZ = 64
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx, cy = SZ // 2, SZ // 2

    for spiral_idx in range(2):
        phase = spiral_idx * math.pi
        pts = []
        for i in range(80):
            t = i * 0.12
            r = 2 + t * 3.2
            pts.append((cx + int(math.cos(t + phase) * r),
                       cy + int(math.sin(t + phase) * r)))
        if len(pts) > 1:
            dr.line(pts, fill=col_a(p["secondary_lo"], 180), width=3)
            dr.line(pts, fill=col_a(p["secondary"], 220), width=2)
        if pts:
            ex, ey = pts[-1]
            dr.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=col_a(p["secondary_hi"], 200))

    dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=col_a(p["gem"], 220))
    dr.ellipse([cx - 1, cy - 2, cx + 1, cy], fill=col_a(p["gem_hi"], 160))

    save(img, theme, "pattern_spiral.png")


# ═══════════════════════════════════════════════
# 12. 希腊回纹  128 x 24
# ═══════════════════════════════════════════════
def gen_pattern_greek_key(theme, p):
    W, H = 128, 24
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    unit, lw = 6, 2

    dr.line([(0, 2), (W, 2)], fill=col_a(p["primary"], 220), width=lw)
    dr.line([(0, H - 3), (W, H - 3)], fill=col_a(p["primary"], 220), width=lw)

    x = 0
    while x < W:
        pts = [(x, 4), (x + unit * 3, 4), (x + unit * 3, H - 4),
               (x + unit, H - 4), (x + unit, 4 + unit),
               (x + unit * 2, 4 + unit), (x + unit * 2, H - 4 - unit)]
        dr.line(pts, fill=col_a(p["primary"], 200), width=lw)
        dr.line([(x + 1, 5), (x + unit * 3 - 1, 5)],
                fill=col_a(p["primary_hi"], 120), width=1)
        x += unit * 4

    save(img, theme, "pattern_greek_key.png")


# ═══════════════════════════════════════════════
# 13. 编织纹路  64 x 64
# ═══════════════════════════════════════════════
def gen_pattern_weave(theme, p):
    SZ = 64
    img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    band_w, gap = 8, 8
    period = band_w + gap

    for row in range(0, SZ, period):
        for seg in range(0, SZ, period * 2):
            dr.rectangle([seg, row, seg + period, row + band_w],
                         fill=col_a(p["secondary_lo"], 160))
            dr.rectangle([seg, row, seg + period, row + 2],
                         fill=col_a(p["secondary_hi"], 120))
            dr.rectangle([seg, row + band_w - 2, seg + period, row + band_w],
                         fill=col_a(p["secondary_lo"], 180))

    for col_x in range(0, SZ, period):
        for seg in range(0, SZ, period * 2):
            dr.rectangle([col_x, seg, col_x + band_w, seg + period],
                         fill=col_a(p["primary_lo"], 180))
            dr.rectangle([col_x, seg, col_x + 2, seg + period],
                         fill=col_a(p["primary_hi"], 120))
            dr.rectangle([col_x + band_w - 2, seg, col_x + band_w, seg + period],
                         fill=col_a(p["primary_dk"], 150))

    for row in range(0, SZ, period):
        for col_x in range(0, SZ, period):
            dr.rectangle([col_x + 1, row + 1, col_x + 3, row + 3],
                         fill=col_a(p["primary_hi"], 80))

    save(img, theme, "pattern_weave.png")


# ═══════════════════════════════════════════════
GENERATORS = [
    gen_divider_ornate, gen_divider_chain, gen_divider_wave,
    gen_corner_ornament, gen_border_rune,
    gen_pattern_celtic, gen_pattern_diamond, gen_pattern_vine,
    gen_pattern_scale, gen_pattern_zigzag, gen_pattern_spiral,
    gen_pattern_greek_key, gen_pattern_weave,
]

if __name__ == "__main__":
    total = 0
    for theme_name, palette in PALETTES.items():
        print(f"\n{'=' * 20} {theme_name.upper()} {'=' * 20}")
        for gen_fn in GENERATORS:
            gen_fn(theme_name, palette)
            total += 1
    print(f"\n=== 全部完成! 3 套主题 × 14 种纹路 (含 corner_tl) = {total + 3} 张图片 ===")
