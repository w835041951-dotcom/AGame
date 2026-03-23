"""
主题UI素材批量生成器 v2 — 高品质版
为三套主题 (樱花幻境/蒸汽朋克/霓虹都市) 生成完整的UI组件纹理

所有素材使用渐变、纹理填充、发光、内阴影等效果
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "ui", "themed")
random.seed(2026)

def save(img, *path_parts):
    p = os.path.join(ROOT, *path_parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print("  saved", os.path.relpath(p, ROOT))

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def shift(color, amt):
    return tuple(clamp(c + amt) for c in color)

def alpha(color, a):
    return color[:3] + (a,)

# ═══════════════════════════════════════════════════════════════
# 主题色板
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "sakura": {
        "bg":           (18, 10, 22),
        "bg_light":     (35, 22, 42),
        "border":       (140, 90, 130),
        "border_hi":    (255, 150, 200),
        "accent":       (255, 170, 200),
        "accent2":      (200, 120, 255),
        "text":         (255, 235, 245),
        "danger":       (255, 60, 80),
        "heal":         (100, 255, 160),
        "mana":         (150, 120, 255),
        "stone":        (30, 18, 35),
        "stone_hi":     (52, 35, 58),
        "mortar":       (20, 12, 25),
        "metal":        (130, 110, 140),
        "rust":         (180, 120, 150),
        "common":       (45, 35, 50),
        "rare":         (50, 40, 100),
        "epic":         (110, 40, 120),
        "noise_density": 0.2,
        "style":        "sakura",
    },
    "steam": {
        "bg":           (22, 16, 10),
        "bg_light":     (42, 30, 18),
        "border":       (120, 85, 45),
        "border_hi":    (210, 165, 60),
        "accent":       (230, 180, 55),
        "accent2":      (185, 95, 30),
        "text":         (240, 225, 190),
        "danger":       (210, 55, 30),
        "heal":         (60, 200, 90),
        "mana":         (70, 130, 210),
        "stone":        (38, 28, 18),
        "stone_hi":     (60, 45, 28),
        "mortar":       (25, 18, 12),
        "metal":        (110, 100, 85),
        "rust":         (155, 95, 45),
        "common":       (50, 40, 28),
        "rare":         (40, 50, 85),
        "epic":         (85, 35, 80),
        "noise_density": 0.25,
        "style":        "gear",
    },
    "neon": {
        "bg":           (8, 5, 18),
        "bg_light":     (18, 10, 38),
        "border":       (50, 20, 90),
        "border_hi":    (255, 50, 200),
        "accent":       (255, 60, 210),
        "accent2":      (0, 230, 255),
        "text":         (240, 220, 255),
        "danger":       (255, 40, 80),
        "heal":         (0, 255, 170),
        "mana":         (100, 50, 255),
        "stone":        (14, 8, 28),
        "stone_hi":     (28, 16, 50),
        "mortar":       (6, 3, 14),
        "metal":        (70, 45, 110),
        "rust":         (200, 50, 180),
        "common":       (22, 14, 40),
        "rare":         (30, 15, 70),
        "epic":         (90, 15, 70),
        "noise_density": 0.15,
        "style":        "neon",
    },
}

# ═══════════════════════════════════════════════════════════════
# 纹理填充器
# ═══════════════════════════════════════════════════════════════

def fill_stone(dr, x0, y0, x1, y1, t):
    """蒸汽朋克风 — 金属齿轮纹理"""
    base = t["stone"]
    dr.rectangle([x0, y0, x1, y1], fill=base)
    mortar = t["mortar"]
    # 铆钉行
    bh = max(8, (y1 - y0) // 4)
    for row_y in range(y0 + bh, y1, bh):
        dr.line([(x0, row_y), (x1, row_y)], fill=alpha(mortar, 120), width=1)
    bw = max(12, (x1 - x0) // 5)
    row = 0
    for row_y in range(y0, y1, bh):
        offset = bw // 2 if row % 2 else 0
        for col_x in range(x0 + offset, x1, bw):
            dr.line([(col_x, row_y), (col_x, min(row_y + bh, y1))], fill=alpha(mortar, 80), width=1)
        row += 1
    # 铆钉
    rivet_c = t["metal"]
    for ry in range(y0 + bh, y1, bh):
        for rx in range(x0 + bw // 2, x1, bw):
            dr.ellipse([rx - 1, ry - 1, rx + 1, ry + 1], fill=alpha(rivet_c, 90))
    # 噪点
    for _ in range(int((x1 - x0) * (y1 - y0) * t["noise_density"] * 0.01)):
        nx = random.randint(x0, x1)
        ny = random.randint(y0, y1)
        ns = random.randint(-20, 20)
        c = shift(base, ns) + (50,)
        dr.point((nx, ny), fill=c)

def fill_sakura(dr, x0, y0, x1, y1, t):
    """樱花幻境风 — 花瓣柔和纹理"""
    base = t["stone"]
    dr.rectangle([x0, y0, x1, y1], fill=base)
    # 柔和花瓣暗纹
    petal_c = t["accent"]
    for _ in range(max(3, (x1 - x0) // 15)):
        px = random.randint(x0 + 4, x1 - 4)
        py = random.randint(y0 + 4, y1 - 4)
        size = random.randint(3, 8)
        dr.ellipse([px - size, py - size // 2, px + size, py + size // 2],
                   fill=alpha(petal_c, 18))
    # 淡樱色噪点
    for _ in range(int((x1 - x0) * (y1 - y0) * t["noise_density"] * 0.01)):
        nx = random.randint(x0, x1)
        ny = random.randint(y0, y1)
        c = alpha(petal_c, random.randint(8, 25))
        dr.point((nx, ny), fill=c)

def fill_circuit(dr, x0, y0, x1, y1, t):
    """霓虹都市风 — 电路板纹理"""
    base = t["stone"]
    dr.rectangle([x0, y0, x1, y1], fill=base)
    acc = t["accent"]
    # 网格线
    gap = max(8, (x1 - x0) // 10)
    for gx in range(x0, x1, gap):
        dr.line([(gx, y0), (gx, y1)], fill=alpha(acc, 15), width=1)
    for gy in range(y0, y1, gap):
        dr.line([(x0, gy), (x1, gy)], fill=alpha(acc, 15), width=1)
    # 随机电路线
    for _ in range(max(3, (x1 - x0) // 20)):
        sx = random.randint(x0 + 4, x1 - 4)
        sy = random.randint(y0 + 4, y1 - 4)
        length = random.randint(8, min(40, (x1 - x0) // 2))
        if random.random() < 0.5:
            dr.line([(sx, sy), (sx + length, sy)], fill=alpha(acc, 35), width=1)
            # 转角
            dy = random.choice([-1, 1]) * random.randint(4, 15)
            dr.line([(sx + length, sy), (sx + length, sy + dy)], fill=alpha(acc, 35), width=1)
        else:
            dr.line([(sx, sy), (sx, sy + length)], fill=alpha(acc, 35), width=1)
    # 节点亮点
    for _ in range(max(2, (x1 - x0) // 30)):
        px_ = random.randint(x0 + 4, x1 - 4)
        py_ = random.randint(y0 + 4, y1 - 4)
        dr.ellipse([px_ - 1, py_ - 1, px_ + 1, py_ + 1], fill=alpha(acc, 60))

def fill_pixel8(dr, x0, y0, x1, y1, t):
    """霓虹网格纹理"""
    base = t["stone"]
    hi = t["stone_hi"]
    dr.rectangle([x0, y0, x1, y1], fill=base)
    # 霓虹网格线
    gap = max(6, (x1 - x0) // 8)
    acc = t["accent"]
    for gx in range(x0, x1, gap):
        dr.line([(gx, y0), (gx, y1)], fill=alpha(acc, 12), width=1)
    for gy in range(y0, y1, gap):
        dr.line([(x0, gy), (x1, gy)], fill=alpha(acc, 12), width=1)
    # 散落亮点
    for _ in range(max(2, (x1 - x0) // 20)):
        bx = random.randint(x0 + 2, x1 - 2)
        by = random.randint(y0 + 2, y1 - 2)
        dr.ellipse([bx - 1, by - 1, bx + 1, by + 1], fill=alpha(acc, 35))

def fill_bg(dr, x0, y0, x1, y1, t):
    style = t["style"]
    if style == "gear":
        fill_stone(dr, x0, y0, x1, y1, t)
    elif style == "neon":
        fill_circuit(dr, x0, y0, x1, y1, t)
        fill_pixel8(dr, x0, y0, x1, y1, t)
    elif style == "sakura":
        fill_sakura(dr, x0, y0, x1, y1, t)
    else:
        fill_stone(dr, x0, y0, x1, y1, t)

def draw_border(dr, w, h, t, bw=2, color_key="border"):
    c = t[color_key]
    for i in range(bw):
        dr.rectangle([i, i, w - 1 - i, h - 1 - i], outline=c + (200 - i * 30,))

def draw_glow_border(dr, w, h, t, bw=2):
    """赛博朋克发光边框"""
    c = t["accent"]
    for i in range(bw):
        a = 180 - i * 40
        dr.rectangle([i, i, w - 1 - i, h - 1 - i], outline=alpha(c, a))
    # 外发光
    c2 = t["accent2"]
    dr.rectangle([0, 0, w - 1, h - 1], outline=alpha(c2, 40))

def draw_pixel_border(dr, w, h, t, bw=2):
    """霓虹发光尖角边框"""
    c = t["border_hi"]
    c2 = t["accent2"]
    for i in range(bw):
        a = 200 - i * 50
        dr.rectangle([i, i, w - 1 - i, h - 1 - i], outline=alpha(c, a))
    # 角落亮点
    dr.rectangle([0, 0, 3, 3], fill=alpha(c2, 120))
    dr.rectangle([w - 4, 0, w - 1, 3], fill=alpha(c2, 120))
    dr.rectangle([0, h - 4, 3, h - 1], fill=alpha(c2, 120))
    dr.rectangle([w - 4, h - 4, w - 1, h - 1], fill=alpha(c2, 120))

def draw_sakura_border(dr, w, h, t, bw=2):
    """樱花柔和圆角边框"""
    c = t["border"]
    for i in range(bw):
        a = 160 - i * 30
        dr.rectangle([i, i, w - 1 - i, h - 1 - i], outline=alpha(c, a))

def auto_border(dr, w, h, t, bw=2):
    if t["style"] == "neon":
        draw_glow_border(dr, w, h, t, bw)
    elif t["style"] == "sakura":
        draw_sakura_border(dr, w, h, t, bw)
    else:
        draw_border(dr, w, h, t, bw)

def add_3d_edge(dr, w, h, t):
    hi = shift(t["bg_light"], 25)
    lo = shift(t["bg_light"], -25)
    dr.line([(2, 1), (w - 3, 1)], fill=alpha(hi, 120), width=1)
    dr.line([(1, 2), (1, h - 3)], fill=alpha(hi, 80), width=1)
    dr.line([(2, h - 2), (w - 3, h - 2)], fill=alpha(lo, 120), width=1)
    dr.line([(w - 2, 2), (w - 2, h - 3)], fill=alpha(lo, 80), width=1)

def add_inner_shadow(img, depth=3, opacity=60):
    """添加内阴影效果"""
    w, h = img.size
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(depth):
        a = opacity - i * (opacity // depth)
        sd.rectangle([i, i, w - 1 - i, h - 1 - i], outline=(0, 0, 0, a))
    return Image.alpha_composite(img, shadow)

def add_outer_glow(img, color, radius=4, intensity=80):
    """添加外发光效果"""
    w, h = img.size
    glow = Image.new("RGBA", (w + radius * 2, h + radius * 2), (0, 0, 0, 0))
    glow_dr = ImageDraw.Draw(glow)
    # 绘制边缘发光
    for i in range(radius, 0, -1):
        a = int(intensity * (1 - i / radius))
        glow_dr.rounded_rectangle([radius - i, radius - i, w + radius + i - 1, h + radius + i - 1],
                                   radius=6, outline=color[:3] + (a,))
    glow.paste(img, (radius, radius))
    # 裁剪回原始尺寸
    return glow.crop((radius, radius, w + radius, h + radius))

def vgradient(dr, x0, y0, x1, y1, c_top, c_bot, alpha_val=255):
    """垂直渐变填充"""
    h = y1 - y0
    for y in range(h):
        ratio = y / max(h - 1, 1)
        r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
        g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
        b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
        dr.line([(x0, y0 + y), (x1, y0 + y)], fill=(clamp(r), clamp(g), clamp(b), alpha_val))

# ═══════════════════════════════════════════════════════════════
# 按钮生成
# ═══════════════════════════════════════════════════════════════
def gen_buttons(theme_name, t):
    W, H = 200, 56
    for state in ["normal", "hover", "pressed"]:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        if state == "normal":
            bg_top = shift(t["bg_light"], 12)
            bg_bot = shift(t["bg_light"], -8)
        elif state == "hover":
            bg_top = shift(t["bg_light"], 28)
            bg_bot = shift(t["bg_light"], 8)
        else:
            bg_top = shift(t["bg_light"], -12)
            bg_bot = shift(t["bg_light"], 4)
        # 渐变背景
        dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=6, fill=bg_top)
        vgradient(dr, 3, 3, W - 3, H - 3, bg_top, bg_bot)
        fill_bg(dr, 4, 4, W - 4, H - 4, t)
        if state == "pressed":
            dr.line([(4, 3), (W - 4, 3)], fill=alpha(shift(bg_top, -35), 160), width=2)
        else:
            add_3d_edge(dr, W, H, t)
        auto_border(dr, W, H, t, 2)
        img = add_inner_shadow(img, 2, 40)
        save(img, theme_name, "btn_%s.png" % state)

    W2 = 220
    for state in ["normal", "hover"]:
        img = Image.new("RGBA", (W2, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        if state == "normal":
            bg_top = shift(t["accent2"], -15)
            bg_bot = shift(t["accent2"], -45)
        else:
            bg_top = shift(t["accent2"], 10)
            bg_bot = shift(t["accent2"], -20)
        dr.rounded_rectangle([0, 0, W2 - 1, H - 1], radius=6, fill=bg_top)
        vgradient(dr, 3, 3, W2 - 3, H - 3, bg_top, bg_bot)
        fill_bg(dr, 4, 4, W2 - 4, H - 4, t)
        add_3d_edge(dr, W2, H, t)
        auto_border(dr, W2, H, t, 2)
        # 强调色高光线
        dr.line([(8, 2), (W2 - 8, 2)], fill=alpha(t["accent"], 120), width=1)
        img = add_inner_shadow(img, 2, 35)
        save(img, theme_name, "btn_end_%s.png" % state)

# ═══════════════════════════════════════════════════════════════
# 面板背景
# ═══════════════════════════════════════════════════════════════
def gen_panel(theme_name, t):
    W, H = 400, 300
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # 渐变底色
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=10, fill=t["bg"])
    vgradient(dr, 4, 4, W - 4, H - 4, shift(t["bg"], 8), shift(t["bg"], -4))
    fill_bg(dr, 6, 6, W - 6, H - 6, t)
    auto_border(dr, W, H, t, 3)
    # 顶部金色装饰线
    acc = t["accent"]
    dr.line([(12, 3), (W - 12, 3)], fill=alpha(acc, 140), width=2)
    dr.line([(12, 5), (W - 12, 5)], fill=alpha(acc, 50), width=1)
    # 底部微光线
    dr.line([(12, H - 4), (W - 12, H - 4)], fill=alpha(acc, 60), width=1)
    img = add_inner_shadow(img, 3, 50)
    save(img, theme_name, "panel_bg.png")

# ═══════════════════════════════════════════════════════════════
# 升级卡片 (common/rare/epic)
# ═══════════════════════════════════════════════════════════════
def gen_cards(theme_name, t):
    W, H = 280, 180
    rarities = {
        "common": (t["common"], t["border"], t["text"], 0),
        "rare":   (t["rare"],   t["mana"],  (180, 210, 255), 3),
        "epic":   (t["epic"],   t["accent2"], (255, 190, 255), 5),
    }
    for rarity, (bg, brd, _glow, glow_r) in rarities.items():
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        # 渐变背景
        bg_top = shift(bg, 12)
        bg_bot = shift(bg, -8)
        dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=8, fill=bg_top)
        vgradient(dr, 4, 4, W - 4, H - 4, bg_top, bg_bot)
        fill_bg(dr, 5, 5, W - 5, H - 5, t)
        # 稀有度边框 (多层)
        for i in range(3):
            a = 220 - i * 55
            dr.rounded_rectangle([i, i, W - 1 - i, H - 1 - i], radius=8, outline=alpha(brd, a))
        # 顶部高光条
        dr.line([(10, 3), (W - 10, 3)], fill=alpha(brd, 180), width=2)
        # 中部分割线
        dr.line([(15, H // 3), (W - 15, H // 3)], fill=alpha(brd, 50), width=1)
        # 底部暗线
        dr.line([(10, H - 4), (W - 10, H - 4)], fill=alpha(shift(bg, -35), 120), width=2)
        img = add_inner_shadow(img, 2, 35)
        if rarity == "epic":
            for cx, cy in [(10, 10), (W - 10, 10), (10, H - 10), (W - 10, H - 10)]:
                dr = ImageDraw.Draw(img)
                dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=alpha(brd, 140))
        if glow_r > 0:
            img = add_outer_glow(img, brd, glow_r, 60)
        save(img, theme_name, "card_%s.png" % rarity)

# ═══════════════════════════════════════════════════════════════
# HUD状态栏底板
# ═══════════════════════════════════════════════════════════════
def gen_hud_bar(theme_name, t):
    W, H = 1920, 64
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # 三段渐变: 顶部亮 → 中间暗 → 底部略亮
    for y in range(H):
        ratio = y / H
        if ratio < 0.15:
            mix = ratio / 0.15
            r = clamp(t["bg_light"][0] * (1.0 - mix * 0.5))
            g = clamp(t["bg_light"][1] * (1.0 - mix * 0.5))
            b = clamp(t["bg_light"][2] * (1.0 - mix * 0.5))
        elif ratio < 0.85:
            r, g, b = t["bg"][0], t["bg"][1], t["bg"][2]
        else:
            mix = (ratio - 0.85) / 0.15
            r = clamp(t["bg"][0] + mix * 10)
            g = clamp(t["bg"][1] + mix * 8)
            b = clamp(t["bg"][2] + mix * 6)
        dr.line([(0, y), (W, y)], fill=(r, g, b, 245))
    fill_bg(dr, 0, 4, W, H - 4, t)
    # 顶部高光线
    dr.line([(0, 0), (W, 0)], fill=alpha(shift(t["bg_light"], 30), 100), width=1)
    # 底部强调线 (双线)
    acc = t["accent"]
    dr.line([(0, H - 3), (W, H - 3)], fill=alpha(acc, 100), width=2)
    dr.line([(0, H - 1), (W, H - 1)], fill=alpha(shift(t["bg"], -15), 220), width=1)
    save(img, theme_name, "hud_bar_bg.png")

# ═══════════════════════════════════════════════════════════════
# 格子纹理 64x64 — 主题化
# ═══════════════════════════════════════════════════════════════
def gen_cells(theme_name, t):
    S = 64
    # ── blocked ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    bg = shift(t["danger"], -60)
    dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=bg)
    fill_bg(dr, 3, 3, S - 3, S - 3, t)
    # X标记
    dr.line([(10, 10), (S - 10, S - 10)], fill=alpha(t["danger"], 200), width=3)
    dr.line([(S - 10, 10), (10, S - 10)], fill=alpha(t["danger"], 200), width=3)
    auto_border(dr, S, S, t, 2)
    save(img, theme_name, "cell_blocked.png")

    # ── exploding ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=(60, 30, 10))
    # 爆炸光芒
    cx, cy = S // 2, S // 2
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int(math.cos(rad) * 28)
        ey = cy + int(math.sin(rad) * 28)
        dr.line([(cx, cy), (ex, ey)], fill=(255, 200, 50, 180), width=2)
    dr.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 220, 100, 220))
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 200, 250))
    auto_border(dr, S, S, t, 2)
    save(img, theme_name, "cell_exploding.png")

    # ── bomb_placed ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=shift(t["accent2"], -40))
    fill_bg(dr, 3, 3, S - 3, S - 3, t)
    # 放置标记圆环
    dr.ellipse([14, 14, S - 14, S - 14], outline=alpha(t["accent"], 150), width=2)
    auto_border(dr, S, S, t, 2)
    save(img, theme_name, "cell_bomb_placed.png")

    # ── minion ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=shift(t["heal"], -60))
    fill_bg(dr, 3, 3, S - 3, S - 3, t)
    # 小怪轮廓
    dr.ellipse([16, 12, S - 16, S - 16], fill=alpha(t["heal"], 80))
    # 眼睛
    dr.ellipse([22, 22, 28, 28], fill=(255, 50, 50, 200))
    dr.ellipse([36, 22, 42, 28], fill=(255, 50, 50, 200))
    auto_border(dr, S, S, t, 2)
    save(img, theme_name, "cell_minion.png")

# ═══════════════════════════════════════════════════════════════
# 分割线
# ═══════════════════════════════════════════════════════════════
def gen_separator(theme_name, t):
    W, H = 512, 8
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    acc = t["accent"]
    # 中间亮两侧暗渐变
    for x in range(W):
        ratio = 1.0 - abs(x - W / 2) / (W / 2)
        a = int(ratio * 160)
        dr.line([(x, 2), (x, 5)], fill=alpha(acc, a))
    # 中心高亮线
    dr.line([(W // 4, 3), (W * 3 // 4, 3)], fill=alpha(acc, 200), width=1)
    save(img, theme_name, "separator_h.png")

# ═══════════════════════════════════════════════════════════════
# 面板四角装饰
# ═══════════════════════════════════════════════════════════════
def gen_corners(theme_name, t):
    S = 32
    acc = t["accent"]
    brd = t["border_hi"]
    for suffix, flip_x, flip_y in [("tl", False, False), ("tr", True, False),
                                     ("bl", False, True), ("br", True, True)]:
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        # L形角
        dr.line([(2, 2), (S - 4, 2)], fill=alpha(brd, 200), width=2)
        dr.line([(2, 2), (2, S - 4)], fill=alpha(brd, 200), width=2)
        # 角点装饰
        dr.ellipse([0, 0, 6, 6], fill=alpha(acc, 220))
        # 短装饰线
        if t["style"] == "circuit":
            dr.line([(8, 6), (20, 6)], fill=alpha(acc, 80), width=1)
            dr.line([(6, 8), (6, 20)], fill=alpha(acc, 80), width=1)
        elif t["style"] == "pixel8":
            for i in range(3):
                dr.rectangle([8 + i * 6, 4, 12 + i * 6, 8], fill=alpha(brd, 120 - i * 30))
        else:
            # 卷草纹
            dr.arc([4, 4, 18, 18], 180, 270, fill=alpha(acc, 100), width=1)
        final = img
        if flip_x:
            final = final.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_y:
            final = final.transpose(Image.FLIP_TOP_BOTTOM)
        save(final, theme_name, "frame_corner_%s.png" % suffix)

# ═══════════════════════════════════════════════════════════════
# HUD小图标 24x24
# ═══════════════════════════════════════════════════════════════
def gen_icons(theme_name, t):
    S = 32
    acc = t["accent"]
    # ── HP心形 ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["danger"]
    # 更精细的心形
    dr.ellipse([3, 6, 16, 19], fill=alpha(c, 230))
    dr.ellipse([14, 6, 27, 19], fill=alpha(c, 230))
    dr.polygon([(3, 14), (15, 28), (27, 14)], fill=alpha(c, 230))
    # 高光 (左上圆弧)
    dr.ellipse([6, 8, 13, 15], fill=alpha(shift(c, 50), 100))
    dr.ellipse([8, 9, 11, 12], fill=alpha(shift(c, 80), 80))
    save(img, theme_name, "icon_hp.png")

    # ── 点击/手指 ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["text"]
    # 指尖圆圈
    dr.ellipse([9, 1, 21, 13], fill=alpha(c, 210))
    # 手掌
    dr.rounded_rectangle([10, 11, 20, 28], radius=3, fill=alpha(c, 210))
    # 拇指
    dr.rounded_rectangle([5, 14, 10, 24], radius=2, fill=alpha(c, 170))
    # 其他手指
    dr.rounded_rectangle([20, 14, 25, 22], radius=2, fill=alpha(c, 170))
    # 点击波纹
    dr.arc([4, 0, 26, 16], 200, 340, fill=alpha(acc, 80), width=1)
    save(img, theme_name, "icon_click.png")

    # ── 楼层/城堡塔 ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = acc
    # 主塔身
    dr.rectangle([8, 10, 24, 30], fill=alpha(c, 210))
    # 城垛 (更精细)
    for bx in [7, 12, 17, 22]:
        dr.rectangle([bx, 6, bx + 4, 10], fill=alpha(c, 210))
    # 小塔尖
    dr.polygon([(14, 2), (18, 2), (16, 6)], fill=alpha(shift(c, 20), 200))
    # 门
    dr.rounded_rectangle([12, 20, 20, 30], radius=3, fill=alpha(t["bg"], 220))
    # 窗户
    dr.rectangle([11, 13, 14, 16], fill=alpha(shift(c, 40), 150))
    dr.rectangle([18, 13, 21, 16], fill=alpha(shift(c, 40), 150))
    save(img, theme_name, "icon_floor.png")

    # ── 计时器/钟表 ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["text"]
    # 外圈
    dr.ellipse([2, 2, 30, 30], outline=alpha(c, 220), width=3)
    # 内圈装饰
    dr.ellipse([5, 5, 27, 27], outline=alpha(acc, 70), width=1)
    # 刻度
    cx, cy = 16, 16
    for angle in range(0, 360, 30):
        rad = math.radians(angle - 90)
        ix1 = cx + int(math.cos(rad) * 11)
        iy1 = cy + int(math.sin(rad) * 11)
        ix2 = cx + int(math.cos(rad) * 13)
        iy2 = cy + int(math.sin(rad) * 13)
        w = 2 if angle % 90 == 0 else 1
        dr.line([(ix1, iy1), (ix2, iy2)], fill=alpha(acc, 140), width=w)
    # 分针
    dr.line([(cx, cy), (cx, 5)], fill=alpha(c, 240), width=2)
    # 时针
    dr.line([(cx, cy), (cx + 6, cy + 3)], fill=alpha(c, 200), width=2)
    # 中心点
    dr.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=alpha(acc, 220))
    save(img, theme_name, "icon_timer.png")

    # ── 炸弹图标 ──
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["accent2"]
    # 球体 (渐变效果)
    dr.ellipse([5, 9, 25, 29], fill=alpha(c, 235))
    dr.ellipse([8, 12, 22, 26], fill=alpha(shift(c, 25), 140))
    dr.ellipse([10, 13, 16, 19], fill=alpha(shift(c, 50), 80))
    # 引线
    dr.line([(15, 9), (18, 4)], fill=alpha(t["text"], 220), width=2)
    dr.line([(18, 4), (20, 2)], fill=alpha(t["text"], 180), width=1)
    # 火花 (更大更亮)
    dr.ellipse([18, 0, 24, 6], fill=alpha(t["accent"], 220))
    dr.ellipse([19, 1, 23, 5], fill=alpha(shift(t["accent"], 30), 180))
    save(img, theme_name, "icon_bomb.png")

# ═══════════════════════════════════════════════════════════════
# 提示框背景
# ═══════════════════════════════════════════════════════════════
def gen_tooltip(theme_name, t):
    W, H = 300, 80
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    bg = shift(t["bg"], 10)
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=6, fill=alpha(bg, 230))
    auto_border(dr, W, H, t, 1)
    # 顶部装饰线
    dr.line([(4, 2), (W - 4, 2)], fill=alpha(t["accent"], 80), width=1)
    save(img, theme_name, "tooltip_bg.png")

# ═══════════════════════════════════════════════════════════════
# 滚动条
# ═══════════════════════════════════════════════════════════════
def gen_scrollbar(theme_name, t):
    # thumb
    img = Image.new("RGBA", (12, 48), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([1, 1, 10, 46], radius=4, fill=alpha(t["border_hi"], 160))
    dr.line([(4, 16), (8, 16)], fill=alpha(t["accent"], 100), width=1)
    dr.line([(4, 24), (8, 24)], fill=alpha(t["accent"], 100), width=1)
    dr.line([(4, 32), (8, 32)], fill=alpha(t["accent"], 100), width=1)
    save(img, theme_name, "scroll_thumb.png")

    # track
    img = Image.new("RGBA", (12, 200), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([2, 2, 9, 197], radius=3, fill=alpha(t["bg_light"], 100))
    save(img, theme_name, "scroll_track.png")

# ═══════════════════════════════════════════════════════════════
# 额外: 主题化cell (覆盖通用cell)
# ═══════════════════════════════════════════════════════════════
def gen_themed_cells(theme_name, t):
    S = 64
    cells = {
        "cell_empty": t["stone"],
        "cell_mine_hidden": shift(t["stone"], 8),
        "cell_mine_revealed": shift(t["stone_hi"], 15),
    }
    for name, bg in cells.items():
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=bg)
        fill_bg(dr, 3, 3, S - 3, S - 3, t)
        add_3d_edge(dr, S, S, t)
        auto_border(dr, S, S, t, 2)
        save(img, theme_name, "%s.png" % name)

    # boss状态格(带主题纹理)
    boss_cells = {
        "cell_boss_normal": (t["accent2"],    t["border"]),
        "cell_boss_weak":   ((200, 180, 30),  (220, 200, 40)),
        "cell_boss_armor":  (t["metal"],      t["mana"]),
        "cell_boss_absorb": (shift(t["heal"], -30), t["heal"]),
        "cell_boss_dead":   ((25, 25, 28),    (55, 55, 60)),
    }
    for name, (bg, brd) in boss_cells.items():
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=4, fill=bg)
        fill_bg(dr, 3, 3, S - 3, S - 3, t)
        for i in range(2):
            dr.rounded_rectangle([i, i, S - 1 - i, S - 1 - i], radius=4, outline=alpha(brd, 200 - i * 60))
        if "dead" in name:
            dr.line([(10, 10), (S - 10, S - 10)], fill=(80, 80, 85, 150), width=2)
            dr.line([(S - 10, 10), (10, S - 10)], fill=(80, 80, 85, 150), width=2)
        save(img, theme_name, "%s.png" % name)

# ═══════════════════════════════════════════════════════════════
# HP条纹理
# ═══════════════════════════════════════════════════════════════
def gen_bars(theme_name, t):
    # Boss HP bar bg
    W, H = 400, 28
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    bg_dark = shift(t["bg"], -8)
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=5, fill=bg_dark)
    vgradient(dr, 2, 2, W - 2, H - 2, shift(bg_dark, 8), shift(bg_dark, -5))
    auto_border(dr, W, H, t, 2)
    img = add_inner_shadow(img, 2, 50)
    save(img, theme_name, "boss_hp_bg.png")

    # Boss HP bar fill
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["danger"]
    c_top = shift(c, 30)
    c_bot = shift(c, -15)
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=5, fill=c)
    vgradient(dr, 1, 1, W - 1, H - 1, c_top, c_bot)
    # 斜线光泽
    for x in range(0, W, 10):
        dr.line([(x, 0), (x + 8, H)], fill=alpha(shift(c, 40), 45), width=3)
    # 顶部高光
    dr.line([(4, 2), (W - 4, 2)], fill=alpha(shift(c, 60), 80), width=1)
    save(img, theme_name, "boss_hp_fill.png")

    # Player HP bar
    for suffix, color in [("bg", shift(t["bg"], -8)), ("fill", t["heal"])]:
        img = Image.new("RGBA", (200, 14), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([0, 0, 199, 13], radius=4, fill=color)
        if suffix == "fill":
            vgradient(dr, 1, 1, 199, 13, shift(color, 25), shift(color, -10))
            for x in range(0, 200, 8):
                dr.line([(x, 0), (x + 5, 14)], fill=alpha(shift(color, 30), 40), width=2)
            dr.line([(3, 2), (197, 2)], fill=alpha(shift(color, 50), 60), width=1)
        else:
            img = add_inner_shadow(img, 2, 45)
        save(img, theme_name, "hp_bar_%s.png" % suffix)

# ═══════════════════════════════════════════════════════════════
# 标签背景 (floor_badge / bomb_counter / timer)
# ═══════════════════════════════════════════════════════════════
def gen_label_badges(theme_name, t):
    acc = t["accent"]
    brd = t["border_hi"]

    # floor badge
    W, H = 140, 40
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W - 1, H - 1], radius=8, fill=alpha(t["bg_light"], 210))
    vgradient(dr, 2, 2, W - 2, H - 2, alpha(shift(t["bg_light"], 10), 180), alpha(shift(t["bg_light"], -8), 180))
    fill_bg(dr, 3, 3, W - 3, H - 3, t)
    auto_border(dr, W, H, t, 2)
    dr.line([(8, 2), (W - 8, 2)], fill=alpha(acc, 180), width=1)
    img = add_inner_shadow(img, 2, 30)
    save(img, theme_name, "floor_badge.png")

    # bomb counter
    W2, H2 = 160, 40
    img = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W2 - 1, H2 - 1], radius=8, fill=alpha(t["bg_light"], 210))
    vgradient(dr, 2, 2, W2 - 2, H2 - 2, alpha(shift(t["bg_light"], 10), 180), alpha(shift(t["bg_light"], -8), 180))
    fill_bg(dr, 3, 3, W2 - 3, H2 - 3, t)
    auto_border(dr, W2, H2, t, 2)
    img = add_inner_shadow(img, 2, 30)
    save(img, theme_name, "bomb_counter_bg.png")
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W2 - 1, H2 - 1], radius=6, fill=alpha(t["bg_light"], 200))
    fill_bg(dr, 3, 3, W2 - 3, H2 - 3, t)
    auto_border(dr, W2, H2, t, 2)
    save(img, theme_name, "bomb_counter_bg.png")

    # timer bg (圆形表盘)
    S = 44
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.ellipse([0, 0, S - 1, S - 1], fill=alpha(t["bg_light"], 200))
    dr.ellipse([2, 2, S - 3, S - 3], outline=alpha(brd, 160), width=2)
    # 刻度
    cx, cy = S // 2, S // 2
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ix = cx + int(math.cos(rad) * (S // 2 - 6))
        iy = cy + int(math.sin(rad) * (S // 2 - 6))
        dr.ellipse([ix - 1, iy - 1, ix + 1, iy + 1], fill=alpha(acc, 120))
    save(img, theme_name, "timer_circle.png")

    # hp badge (血量标签背景)
    W3, H3 = 160, 40
    img = Image.new("RGBA", (W3, H3), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W3 - 1, H3 - 1], radius=8, fill=alpha(t["bg_light"], 210))
    vgradient(dr, 2, 2, W3 - 2, H3 - 2, alpha(shift(t["bg_light"], 10), 180), alpha(shift(t["bg_light"], -8), 180))
    fill_bg(dr, 3, 3, W3 - 3, H3 - 3, t)
    auto_border(dr, W3, H3, t, 2)
    # 红色顶线（代表血量）
    dr.line([(8, 2), (W3 - 8, 2)], fill=alpha(t["danger"], 160), width=1)
    img = add_inner_shadow(img, 2, 30)
    save(img, theme_name, "hp_badge.png")

    # timer badge (计时器标签背景)
    W4, H4 = 120, 40
    img = Image.new("RGBA", (W4, H4), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, W4 - 1, H4 - 1], radius=8, fill=alpha(t["bg_light"], 210))
    vgradient(dr, 2, 2, W4 - 2, H4 - 2, alpha(shift(t["bg_light"], 10), 180), alpha(shift(t["bg_light"], -8), 180))
    fill_bg(dr, 3, 3, W4 - 3, H4 - 3, t)
    auto_border(dr, W4, H4, t, 2)
    img = add_inner_shadow(img, 2, 30)
    save(img, theme_name, "timer_badge.png")

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════
def main():
    total = 0
    for theme_name, t in THEMES.items():
        print("\n=== %s ===" % theme_name.upper())
        gen_buttons(theme_name, t)      # 5 per theme
        gen_panel(theme_name, t)        # 1
        gen_cards(theme_name, t)        # 3
        gen_hud_bar(theme_name, t)      # 1
        gen_cells(theme_name, t)        # 4
        gen_themed_cells(theme_name, t) # 8
        gen_separator(theme_name, t)    # 1
        gen_corners(theme_name, t)      # 4
        gen_icons(theme_name, t)        # 5
        gen_tooltip(theme_name, t)      # 1
        gen_scrollbar(theme_name, t)    # 2
        gen_bars(theme_name, t)         # 4
        gen_label_badges(theme_name, t) # 3
        count = 5 + 1 + 3 + 1 + 4 + 8 + 1 + 4 + 5 + 1 + 2 + 4 + 3
        total += count
        print("  %d files for %s" % (count, theme_name))
    print("\n✅ Total: %d themed sprites generated" % total)

if __name__ == "__main__":
    main()
