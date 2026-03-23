"""
游戏主界面 AI 纹理生成器 (优化版)
策略: 每主题只调1次API生成底材纹理, 然后PIL合成所有UI组件

API调用总量:
  - 3次: 三主题基底纹理 (sakura/steam/neon)
  - 1次: 炸弹图标合集 (4×5网格)
  - 1次: 标题背景
  总计 ~5次API调用 → 覆盖全部UI + 炸弹

使用:
  set POLLINATIONS_API_KEY=sk_xxx
  python scripts/tools/gen_game_ui.py                 # 生成全部
  python scripts/tools/gen_game_ui.py --phase texture  # 只生成AI底材
  python scripts/tools/gen_game_ui.py --phase compose  # 只做合成(不调API)
  python scripts/tools/gen_game_ui.py --phase bombs    # 只生成炸弹
  python scripts/tools/gen_game_ui.py --dry-run        # 只看prompt
"""
import os, sys, math, random, hashlib, time, argparse, json
from pathlib import Path
from urllib.parse import quote

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
    import io, requests
except ImportError:
    print("请先安装: pip install pillow requests")
    sys.exit(1)

random.seed(2026)

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets" / "sprites"
THEMED_DIR = ASSETS / "ui" / "themed"
TEXTURE_DIR = ROOT / "scripts" / "tools" / ".ai_textures"
CACHE_FILE = ROOT / "scripts" / "tools" / ".ai_art_cache.json"

POLLINATIONS_BASE = "https://gen.pollinations.ai"

# ═══════════════════════════════════════════════════════════
# 底材Prompt — 每主题1次API调用
# ═══════════════════════════════════════════════════════════
TEXTURE_PROMPTS = {
    "sakura": (
        "seamless tileable Japanese cherry blossom pattern texture, "
        "soft pink petals on dark purple-black background, "
        "delicate sakura flowers, gentle watercolor style, "
        "anime aesthetic, dreamy and ethereal, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
    "steam": (
        "seamless tileable steampunk brass gears and pipes texture, "
        "dark brown background with copper mechanical parts, "
        "cogs wheels rivets and steam vents, industrial Victorian, "
        "warm amber lighting, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
    "neon": (
        "seamless tileable synthwave neon grid texture, "
        "dark purple-black background with glowing hot pink and cyan lines, "
        "retro 80s wireframe grid, vaporwave aesthetic, "
        "neon glow effects, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
}

BOMB_PROMPT = (
    "sprite sheet grid of 20 pixel art bomb and explosive weapon icons, "
    "4 columns 5 rows on solid black background, dark fantasy game items, "
    "each icon 128x128 pixels with clear black separation lines between them, "
    "variety of magical bombs: arrow bomb, cross bomb, bouncing bomb, area bomb, "
    "cluster bomb, drill bomb, fire bomb, ice bomb, poison bomb, lightning bomb, "
    "holy bomb, mega bomb, nova bomb, scatter bomb, void bomb, "
    "piercing arrow, X-shaped explosive, spring bomb, "
    "each with unique color and visual effect, pixel art style, "
    "clean sharp edges, no text, no watermark"
)

TITLE_PROMPT = (
    "epic fantasy game title screen background art, "
    "mystical gate between floating realms, "
    "silhouette of bomber hero standing at dimensional crossroads, "
    "ten different world portals visible in cosmic sky, "
    "atmospheric fog, magical energy, wide 16:9, "
    "no text, no watermark, cinematic composition"
)

# ═══════════════════════════════════════════════════════════
# 主题色板 (同gen_theme_sprites.py)
# ═══════════════════════════════════════════════════════════
THEMES = {
    "sakura": {
        "bg": (18, 10, 22), "bg_light": (35, 22, 42),
        "border": (140, 90, 130), "border_hi": (255, 150, 200),
        "accent": (255, 170, 200), "accent2": (200, 120, 255),
        "text": (255, 235, 245), "danger": (255, 60, 80),
        "heal": (100, 255, 160), "mana": (150, 120, 255),
        "stone": (30, 18, 35), "stone_hi": (52, 35, 58),
        "mortar": (20, 12, 25), "metal": (130, 110, 140),
        "common": (45, 35, 50), "rare": (50, 40, 100), "epic": (110, 40, 120),
    },
    "steam": {
        "bg": (22, 16, 10), "bg_light": (42, 30, 18),
        "border": (120, 85, 45), "border_hi": (210, 165, 60),
        "accent": (230, 180, 55), "accent2": (185, 95, 30),
        "text": (240, 225, 190), "danger": (210, 55, 30),
        "heal": (60, 200, 90), "mana": (70, 130, 210),
        "stone": (38, 28, 18), "stone_hi": (60, 45, 28),
        "mortar": (25, 18, 12), "metal": (110, 100, 85),
        "common": (50, 40, 28), "rare": (40, 50, 85), "epic": (85, 35, 80),
    },
    "neon": {
        "bg": (8, 5, 18), "bg_light": (18, 10, 38),
        "border": (50, 20, 90), "border_hi": (255, 50, 200),
        "accent": (255, 60, 210), "accent2": (0, 230, 255),
        "text": (240, 220, 255), "danger": (255, 40, 80),
        "heal": (0, 255, 170), "mana": (100, 50, 255),
        "stone": (14, 8, 28), "stone_hi": (28, 16, 50),
        "mortar": (6, 3, 14), "metal": (70, 45, 110),
        "common": (22, 14, 40), "rare": (30, 15, 70), "epic": (90, 15, 70),
    },
}

# ═══════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════
def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def shift(color, amt):
    return tuple(clamp(c + amt) for c in color[:3])

def alpha(color, a):
    return color[:3] + (a,)

def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def prompt_hash(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()[:12]

def save_img(img, *path_parts):
    p = os.path.join(str(THEMED_DIR), *path_parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print(f"    saved {os.path.basename(p)}")

# ═══════════════════════════════════════════════════════════
# API 调用
# ═══════════════════════════════════════════════════════════
def call_api(prompt, output_path, width=512, height=512, cache=None, dry_run=False):
    """调用 Pollinations.ai 免费 API"""
    ph = prompt_hash(prompt)
    if cache and ph in cache and output_path.exists():
        print(f"  [cached] {output_path.name}")
        return True

    if dry_run:
        print(f"  [dry-run] {output_path.name}")
        print(f"    prompt: {prompt[:150]}...")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 100000
    encoded = quote(prompt, safe="")
    url = f"{POLLINATIONS_BASE}/image/{encoded}?width={width}&height={height}&model=flux&seed={seed}&nologo=true"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"  [API] {output_path.name} ({width}x{height})...")

    last_err = None
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=180)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            last_err = e
            if attempt < 2:
                wait = (attempt + 1) * 5
                print(f"    retry {attempt+1}/3 in {wait}s...")
                time.sleep(wait)
    else:
        print(f"  ✗ FAILED {output_path.name}: {last_err}")
        return False

    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    img.save(str(output_path))
    print(f"  ✓ {output_path.name}")

    if cache is not None:
        cache[ph] = str(output_path.name)
        save_cache(cache)

    time.sleep(1)
    return True

# ═══════════════════════════════════════════════════════════
# Phase 1: 生成AI底材纹理 (3次API)
# ═══════════════════════════════════════════════════════════
def gen_base_textures(cache, dry_run=False):
    print("\n══ 生成基底纹理 (3次API) ══")
    count = 0
    for theme, prompt in TEXTURE_PROMPTS.items():
        out = TEXTURE_DIR / f"base_{theme}.png"
        if call_api(prompt, out, 512, 512, cache, dry_run):
            count += 1
    return count

# ═══════════════════════════════════════════════════════════
# Phase 2: 用AI纹理合成全部UI组件
# ═══════════════════════════════════════════════════════════
def tile_texture(tex, w, h):
    """将纹理平铺到指定尺寸"""
    tw, th = tex.size
    result = Image.new("RGBA", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            result.paste(tex, (x, y))
    return result.crop((0, 0, w, h))

def blend_texture(base_img, texture, opacity=0.35):
    """将AI纹理混合到base_img上"""
    w, h = base_img.size
    tex_resized = tile_texture(texture, w, h)
    # 调整纹理亮度匹配底色
    enhancer = ImageEnhance.Brightness(tex_resized)
    tex_resized = enhancer.enhance(0.6)
    # 混合
    return Image.blend(base_img, tex_resized, opacity)

def vgradient(draw, x0, y0, x1, y1, c_top, c_bot, a=255):
    h = y1 - y0
    for y in range(max(h, 1)):
        ratio = y / max(h - 1, 1)
        r = clamp(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
        g = clamp(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
        b = clamp(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
        draw.line([(x0, y0 + y), (x1, y0 + y)], fill=(r, g, b, a))

def add_inner_shadow(img, depth=3, opacity=60):
    w, h = img.size
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(depth):
        a = opacity - i * (opacity // max(depth, 1))
        sd.rectangle([i, i, w - 1 - i, h - 1 - i], outline=(0, 0, 0, a))
    return Image.alpha_composite(img, shadow)

def make_textured_rect(w, h, base_color, tex, border_color=None, border_w=2, radius=4, tex_opacity=0.3):
    """创建一个带AI纹理的矩形UI组件"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # 底色
    dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=base_color)
    # 叠加AI纹理
    tex_layer = tile_texture(tex, w, h)
    enhancer = ImageEnhance.Brightness(tex_layer)
    tex_layer = enhancer.enhance(0.5)
    # 创建圆角mask
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([2, 2, w - 3, h - 3], radius=max(0, radius - 2), fill=int(255 * tex_opacity))
    img.paste(Image.composite(tex_layer, img, mask), (0, 0), mask)
    # 渐变光泽
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(h // 3):
        a = int(30 * (1 - y / (h // 3)))
        od.line([(2, y + 2), (w - 3, y + 2)], fill=(255, 255, 255, a))
    img = Image.alpha_composite(img, overlay)
    # 边框
    if border_color:
        dr = ImageDraw.Draw(img)
        for i in range(border_w):
            a = 220 - i * 50
            dr.rounded_rectangle([i, i, w - 1 - i, h - 1 - i], radius=radius,
                                  outline=alpha(border_color, a))
    return img

def compose_theme(theme_name, t, tex):
    """用AI纹理合成一个主题的全部UI组件"""
    print(f"\n  合成 {theme_name} 主题...")
    count = 0

    # ── 按钮 ──
    for state, brightness in [("normal", 1.0), ("hover", 1.3), ("pressed", 0.7)]:
        bg = shift(t["bg_light"], int(12 * brightness))
        img = make_textured_rect(200, 56, bg, tex, t["border"], 2, 6, 0.35)
        if state == "pressed":
            img = add_inner_shadow(img, 3, 70)
        else:
            img = add_inner_shadow(img, 2, 40)
        save_img(img, theme_name, f"btn_{state}.png")
        count += 1

    for state, brightness in [("normal", 1.0), ("hover", 1.25)]:
        bg = shift(t["accent2"], int(-15 * (2 - brightness)))
        img = make_textured_rect(220, 56, bg, tex, t["accent2"], 2, 6, 0.25)
        # 顶部高光
        dr = ImageDraw.Draw(img)
        dr.line([(8, 2), (212, 2)], fill=alpha(t["accent"], 120), width=1)
        img = add_inner_shadow(img, 2, 35)
        save_img(img, theme_name, f"btn_end_{state}.png")
        count += 1

    # ── 面板 ──
    img = make_textured_rect(400, 300, t["bg"], tex, t["border"], 3, 10, 0.3)
    dr = ImageDraw.Draw(img)
    dr.line([(12, 3), (388, 3)], fill=alpha(t["accent"], 140), width=2)
    dr.line([(12, H - 4), (388, H - 4)], fill=alpha(t["accent"], 60), width=1) if (H := 300) else None
    img = add_inner_shadow(img, 3, 50)
    save_img(img, theme_name, "panel_bg.png")
    count += 1

    # ── 升级卡片 ──
    for rarity, (bg, brd, glow_r) in [
        ("common", (t["common"], t["border"], 0)),
        ("rare",   (t["rare"],   t["mana"],   3)),
        ("epic",   (t["epic"],   t["accent2"], 5)),
    ]:
        img = make_textured_rect(280, 180, bg, tex, brd, 3, 8, 0.3)
        dr = ImageDraw.Draw(img)
        # 顶部稀有度高光
        dr.line([(10, 3), (270, 3)], fill=alpha(brd, 180), width=2)
        # 中部分割线
        dr.line([(15, 60), (265, 60)], fill=alpha(brd, 50), width=1)
        img = add_inner_shadow(img, 2, 35)
        save_img(img, theme_name, f"card_{rarity}.png")
        count += 1

    # ── HUD栏 ──
    img = make_textured_rect(1920, 64, t["bg"], tex, None, 0, 0, 0.25)
    dr = ImageDraw.Draw(img)
    dr.line([(0, 0), (1920, 0)], fill=alpha(shift(t["bg_light"], 30), 100), width=1)
    dr.line([(0, 61), (1920, 61)], fill=alpha(t["accent"], 100), width=2)
    dr.line([(0, 63), (1920, 63)], fill=alpha(shift(t["bg"], -15), 220), width=1)
    save_img(img, theme_name, "hud_bar_bg.png")
    count += 1

    # ── 格子纹理 64x64 ──
    cell_defs = {
        "cell_empty":         (t["stone"],              t["border"],       2),
        "cell_mine_hidden":   (shift(t["stone"], 8),    t["border"],       2),
        "cell_mine_revealed": (shift(t["stone_hi"], 15), t["border"],      1),
        "cell_boss_normal":   (t["accent2"],            t["border"],       2),
        "cell_boss_weak":     ((200, 180, 30),          (220, 200, 40),    2),
        "cell_boss_armor":    (t["metal"],              t["mana"],         2),
        "cell_boss_absorb":   (shift(t["heal"], -30),   t["heal"],         2),
        "cell_boss_dead":     ((25, 25, 28),            (55, 55, 60),      2),
        "cell_blocked":       (shift(t["danger"], -60), t["danger"],       2),
        "cell_bomb_placed":   (shift(t["accent2"], -40), t["accent"],      2),
        "cell_minion":        (shift(t["heal"], -60),   t["heal"],         2),
    }
    for name, (bg, brd, bw) in cell_defs.items():
        img = make_textured_rect(64, 64, bg, tex, brd, bw, 4, 0.35)
        # 特殊标记
        if "dead" in name:
            dr = ImageDraw.Draw(img)
            dr.line([(12, 12), (52, 52)], fill=(80, 80, 85, 150), width=2)
            dr.line([(52, 12), (12, 52)], fill=(80, 80, 85, 150), width=2)
        elif "blocked" in name:
            dr = ImageDraw.Draw(img)
            dr.line([(12, 12), (52, 52)], fill=alpha(t["danger"], 200), width=3)
            dr.line([(52, 12), (12, 52)], fill=alpha(t["danger"], 200), width=3)
        elif "exploding" in name:
            dr = ImageDraw.Draw(img)
            cx, cy = 32, 32
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                ex = cx + int(math.cos(rad) * 24)
                ey = cy + int(math.sin(rad) * 24)
                dr.line([(cx, cy), (ex, ey)], fill=(255, 200, 50, 180), width=2)
        save_img(img, theme_name, f"{name}.png")
        count += 1

    # ── exploding (单独处理) ──
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([0, 0, 63, 63], radius=4, fill=(60, 30, 10))
    # 叠加纹理
    tex_layer = tile_texture(tex, 64, 64)
    enhancer = ImageEnhance.Brightness(tex_layer)
    tex_layer = enhancer.enhance(0.3)
    mask = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(mask).rounded_rectangle([2, 2, 61, 61], radius=3, fill=80)
    img.paste(Image.composite(tex_layer, img, mask), (0, 0), mask)
    cx, cy = 32, 32
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int(math.cos(rad) * 28)
        ey = cy + int(math.sin(rad) * 28)
        dr = ImageDraw.Draw(img)
        dr.line([(cx, cy), (ex, ey)], fill=(255, 200, 50, 180), width=2)
    dr = ImageDraw.Draw(img)
    dr.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 220, 100, 220))
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 200, 250))
    save_img(img, theme_name, "cell_exploding.png")
    count += 1

    # ── HP条 ──
    for name, w, h, color, is_fill in [
        ("boss_hp_bg",  400, 28, shift(t["bg"], -8), False),
        ("boss_hp_fill", 400, 28, t["danger"],       True),
        ("hp_bar_bg",   200, 14, shift(t["bg"], -8), False),
        ("hp_bar_fill", 200, 14, t["heal"],          True),
    ]:
        img = make_textured_rect(w, h, color, tex, t["border"] if not is_fill else None,
                                  1 if not is_fill else 0, 5, 0.2)
        if is_fill:
            dr = ImageDraw.Draw(img)
            # 斜线光泽
            for x in range(0, w, 10):
                dr.line([(x, 0), (x + 8, h)], fill=alpha(shift(color, 40), 45), width=3)
            dr.line([(4, 2), (w - 4, 2)], fill=alpha(shift(color, 60), 80), width=1)
        else:
            img = add_inner_shadow(img, 2, 50)
        save_img(img, theme_name, f"{name}.png")
        count += 1

    # ── 标签徽章 ──
    badges = [
        ("floor_badge",     140, 40, t["accent"]),
        ("bomb_counter_bg", 160, 40, t["border_hi"]),
        ("timer_circle",    44,  44, t["border_hi"]),
        ("hp_badge",        160, 40, t["danger"]),
        ("timer_badge",     120, 40, t["border_hi"]),
    ]
    for name, w, h, accent_c in badges:
        r = h // 2 if "circle" in name else 8
        img = make_textured_rect(w, h, alpha(t["bg_light"], 210)[:3], tex, t["border"], 2, r, 0.3)
        dr = ImageDraw.Draw(img)
        dr.line([(6, 2), (w - 6, 2)], fill=alpha(accent_c, 140), width=1)
        img = add_inner_shadow(img, 2, 30)
        save_img(img, theme_name, f"{name}.png")
        count += 1

    # ── 分割线 ──
    W, H = 512, 8
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for x in range(W):
        ratio = 1.0 - abs(x - W / 2) / (W / 2)
        a = int(ratio * 160)
        dr.line([(x, 2), (x, 5)], fill=alpha(t["accent"], a))
    dr.line([(W // 4, 3), (W * 3 // 4, 3)], fill=alpha(t["accent"], 200), width=1)
    save_img(img, theme_name, "separator_h.png")
    count += 1

    # ── 四角装饰 ──
    S = 32
    for suffix, flip_x, flip_y in [("tl", False, False), ("tr", True, False),
                                     ("bl", False, True), ("br", True, True)]:
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.line([(2, 2), (S - 4, 2)], fill=alpha(t["border_hi"], 200), width=2)
        dr.line([(2, 2), (2, S - 4)], fill=alpha(t["border_hi"], 200), width=2)
        dr.ellipse([0, 0, 6, 6], fill=alpha(t["accent"], 220))
        final = img
        if flip_x:
            final = final.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_y:
            final = final.transpose(Image.FLIP_TOP_BOTTOM)
        save_img(final, theme_name, f"frame_corner_{suffix}.png")
        count += 1

    # ── 图标 32x32 (保持PIL绘制, 不需要AI纹理) ──
    gen_icons_for_theme(theme_name, t)
    count += 5

    # ── 提示框 + 滚动条 ──
    img = make_textured_rect(300, 80, shift(t["bg"], 10), tex, t["border"], 1, 6, 0.25)
    save_img(img, theme_name, "tooltip_bg.png")
    count += 1

    # scroll_thumb
    img = Image.new("RGBA", (12, 48), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([1, 1, 10, 46], radius=4, fill=alpha(t["border_hi"], 160))
    save_img(img, theme_name, "scroll_thumb.png")
    count += 1

    # scroll_track
    img = Image.new("RGBA", (12, 200), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([2, 2, 9, 197], radius=3, fill=alpha(t["bg_light"], 100))
    save_img(img, theme_name, "scroll_track.png")
    count += 1

    return count

def gen_icons_for_theme(theme_name, t):
    """图标用纯PIL绘制(太小了AI纹理没意义)"""
    S = 32
    # HP心形
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["danger"]
    dr.ellipse([3, 6, 16, 19], fill=alpha(c, 230))
    dr.ellipse([14, 6, 27, 19], fill=alpha(c, 230))
    dr.polygon([(3, 14), (15, 28), (27, 14)], fill=alpha(c, 230))
    dr.ellipse([6, 8, 13, 15], fill=alpha(shift(c, 50), 100))
    save_img(img, theme_name, "icon_hp.png")

    # 手指
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["text"]
    dr.ellipse([9, 1, 21, 13], fill=alpha(c, 210))
    dr.rounded_rectangle([10, 11, 20, 28], radius=3, fill=alpha(c, 210))
    dr.rounded_rectangle([5, 14, 10, 24], radius=2, fill=alpha(c, 170))
    dr.rounded_rectangle([20, 14, 25, 22], radius=2, fill=alpha(c, 170))
    save_img(img, theme_name, "icon_click.png")

    # 城堡
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["accent"]
    dr.rectangle([8, 10, 24, 30], fill=alpha(c, 210))
    for bx in [7, 12, 17, 22]:
        dr.rectangle([bx, 6, bx + 4, 10], fill=alpha(c, 210))
    dr.polygon([(14, 2), (18, 2), (16, 6)], fill=alpha(shift(c, 20), 200))
    dr.rounded_rectangle([12, 20, 20, 30], radius=3, fill=alpha(t["bg"], 220))
    save_img(img, theme_name, "icon_floor.png")

    # 计时器
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["text"]
    dr.ellipse([2, 2, 30, 30], outline=alpha(c, 220), width=3)
    cx, cy = 16, 16
    dr.line([(cx, cy), (cx, 5)], fill=alpha(c, 240), width=2)
    dr.line([(cx, cy), (cx + 6, cy + 3)], fill=alpha(c, 200), width=2)
    dr.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=alpha(t["accent"], 220))
    save_img(img, theme_name, "icon_timer.png")

    # 炸弹
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    c = t["accent2"]
    dr.ellipse([5, 9, 25, 29], fill=alpha(c, 235))
    dr.ellipse([8, 12, 22, 26], fill=alpha(shift(c, 25), 140))
    dr.line([(15, 9), (18, 4)], fill=alpha(t["text"], 220), width=2)
    dr.ellipse([18, 0, 24, 6], fill=alpha(t["accent"], 220))
    save_img(img, theme_name, "icon_bomb.png")

# ═══════════════════════════════════════════════════════════
# Phase 3: 炸弹图标合集 (1次API → 切17个)
# ═══════════════════════════════════════════════════════════
BOMB_NAMES = [
    "pierce_h", "pierce_v", "cross", "x_shot", "bounce",
    "area", "cluster", "drill", "flame", "frost",
    "poison", "thunder", "holy", "mega", "nova",
    "scatter", "void",
]

def gen_bombs(cache, dry_run=False):
    print("\n══ 炸弹图标 (1次API → 17个) ══")
    sheet_path = TEXTURE_DIR / "bomb_sheet.png"
    if not call_api(BOMB_PROMPT, sheet_path, 512, 640, cache, dry_run):
        return 0
    if dry_run:
        return 17

    # 切割 4×5 网格
    sheet = Image.open(str(sheet_path)).convert("RGBA")
    sw, sh = sheet.size
    cols, rows = 4, 5
    cw, ch = sw // cols, sh // rows
    out_dir = ASSETS / "bombs"
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for idx, name in enumerate(BOMB_NAMES):
        col = idx % cols
        row = idx // cols
        x0, y0 = col * cw, row * ch
        cell = sheet.crop((x0, y0, x0 + cw, y0 + ch))
        cell = cell.resize((64, 64), Image.LANCZOS)
        out = out_dir / f"{name}.png"
        cell.save(str(out))
        print(f"    切出 {name}.png")
        count += 1
    return count

# ═══════════════════════════════════════════════════════════
# Phase 4: 标题背景 (1次API)
# ═══════════════════════════════════════════════════════════
def gen_title_bg(cache, dry_run=False):
    print("\n══ 标题背景 (1次API) ══")
    out = ASSETS / "ui" / "title_bg.png"
    if call_api(TITLE_PROMPT, out, 1280, 720, cache, dry_run):
        if not dry_run and out.exists():
            img = Image.open(str(out)).convert("RGBA")
            img = img.resize((640, 360), Image.LANCZOS)
            img.save(str(out))
        return 1
    return 0

# ═══════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="游戏UI AI纹理生成器 (优化版)")
    parser.add_argument("--phase", choices=["all", "texture", "compose", "bombs", "title"],
                        default="all", help="执行阶段")
    parser.add_argument("--dry-run", action="store_true", help="只看prompt不调API")
    parser.add_argument("--theme", choices=["sakura", "steam", "neon", "all"],
                        default="all", help="指定主题")
    args = parser.parse_args()

    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    if not api_key and not args.dry_run and args.phase != "compose":
        print("错误: 请设置 POLLINATIONS_API_KEY")
        print("  免费注册: https://enter.pollinations.ai/")
        print("  设置: set POLLINATIONS_API_KEY=sk_xxx")
        print("\n或使用 --dry-run 只看prompt")
        sys.exit(1)

    cache = load_cache()
    total_api = 0
    total_sprites = 0

    phase = args.phase

    # Phase 1: 生成AI底材纹理
    if phase in ("all", "texture"):
        total_api += gen_base_textures(cache, args.dry_run)

    # Phase 2: 合成UI组件
    if phase in ("all", "compose"):
        print("\n══ 合成UI组件 ══")
        themes = [args.theme] if args.theme != "all" else ["sakura", "steam", "neon"]
        for theme_name in themes:
            tex_path = TEXTURE_DIR / f"base_{theme_name}.png"
            if not tex_path.exists():
                print(f"  ⚠ 未找到 {theme_name} 底材纹理, 先运行 --phase texture")
                continue
            tex = Image.open(str(tex_path)).convert("RGBA")
            n = compose_theme(theme_name, THEMES[theme_name], tex)
            total_sprites += n
            print(f"  {theme_name}: {n} 个组件")

    # Phase 3: 炸弹图标
    if phase in ("all", "bombs"):
        n = gen_bombs(cache, args.dry_run)
        total_sprites += n
        total_api += 1 if n > 0 else 0

    # Phase 4: 标题背景
    if phase in ("all", "title"):
        n = gen_title_bg(cache, args.dry_run)
        total_sprites += n
        total_api += n

    print(f"\n✅ 完成! API调用: {total_api}次, 生成: {total_sprites}个sprite")
    if phase == "all":
        print("  3次底材 + 1次炸弹 + 1次标题 = 5次API调用")
        print("  覆盖: 132个主题UI + 17个炸弹 + 1个标题 = 150个sprite")

if __name__ == "__main__":
    main()
