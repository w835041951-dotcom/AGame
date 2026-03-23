"""
Boss 像素风精灵生成器 v6  —  20种Boss 大型有机轮廓风格
使用 blob / glow / 有机多边形 绘制, 不按格子独立绘制
每个Boss是一张大型 atlas 贴图, Cell.gd 按 local 坐标裁切
使用 UI patterns (sakura主题) 作为Boss身体纹理装饰
"""
import os, math, random
from PIL import Image, ImageDraw, ImageEnhance, ImageChops

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

CELL = 64
rng = random.Random(42)

# ── UI 主题纹路素材 ──────────────────────────────
PATTERN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "ui", "patterns", "sakura")
_pattern_cache = {}

def _load_pattern(name):
    """加载 sakura 主题的纹路 PNG 并缓存"""
    if name in _pattern_cache:
        return _pattern_cache[name]
    path = os.path.join(PATTERN_DIR, name)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        _pattern_cache[name] = img
        return img
    return None

def tile_pattern(pat, w, h):
    """将小纹路图平铺到 w×h 大小"""
    pw, ph = pat.size
    tiled = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for ty in range(0, h, ph):
        for tx in range(0, w, pw):
            tiled.paste(pat, (tx, ty))
    return tiled.crop((0, 0, w, h))

def tint_pattern(pat, color, alpha=80):
    """对纹路重新着色: 取纹路亮度作为蒙版, 用 color 着色并设透明度"""
    pat = pat.convert("RGBA")
    r, g, b = color[:3]
    w, h = pat.size
    px = pat.load()
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rpx = result.load()
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = px[x, y]
            if pa < 10:
                continue
            brightness = (pr + pg + pb) / (3 * 255.0)
            a = int(alpha * brightness * (pa / 255.0))
            rpx[x, y] = (r, g, b, min(255, a))
    return result

def overlay_pattern(img, pattern_name, cx, cy, rx, ry, color, alpha=70):
    """在 img 的椭圆区域(cx,cy,rx,ry)内叠加纹路装饰"""
    pat = _load_pattern(pattern_name)
    if pat is None:
        return
    region_w = rx * 2
    region_h = ry * 2
    if region_w < 8 or region_h < 8:
        return
    tiled = tile_pattern(pat, region_w, region_h)
    tinted = tint_pattern(tiled, color, alpha)
    # 用椭圆蒙版裁切
    mask = Image.new("L", (region_w, region_h), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, region_w - 1, region_h - 1], fill=255)
    tinted.putalpha(ImageChops.multiply(tinted.split()[3], mask))
    paste_x = cx - rx
    paste_y = cy - ry
    img.paste(Image.alpha_composite(
        img.crop((paste_x, paste_y, paste_x + region_w, paste_y + region_h)).convert("RGBA"),
        tinted
    ), (paste_x, paste_y))

def overlay_pattern_rect(img, pattern_name, x0, y0, w, h, color, alpha=60):
    """在矩形区域内叠加纹路装饰"""
    pat = _load_pattern(pattern_name)
    if pat is None:
        return
    if w < 8 or h < 8:
        return
    tiled = tile_pattern(pat, w, h)
    tinted = tint_pattern(tiled, color, alpha)
    region = img.crop((x0, y0, x0 + w, y0 + h)).convert("RGBA")
    composited = Image.alpha_composite(region, tinted)
    img.paste(composited, (x0, y0))

def overlay_border(img, border_name, x0, y0, w, h, alpha=50):
    """在区域边缘叠加边框纹路"""
    pat = _load_pattern(border_name)
    if pat is None:
        return
    pw, ph = pat.size
    # 上边
    for tx in range(x0, x0 + w, pw):
        rw = min(pw, x0 + w - tx)
        piece = pat.crop((0, 0, rw, ph)).copy()
        px_data = piece.load()
        for py in range(ph):
            for px_x in range(rw):
                r, g, b, a = px_data[px_x, py]
                px_data[px_x, py] = (r, g, b, min(255, int(a * alpha / 100)))
        img.paste(Image.alpha_composite(
            img.crop((tx, y0, tx + rw, y0 + ph)).convert("RGBA"),
            piece
        ), (tx, y0))

# ── 通用绘图工具 (与 generate_boss_sprites.py 一致) ──

def canvas(wc, hc, bg=(10, 6, 16, 255)):
    return Image.new("RGBA", (wc * CELL, hc * CELL), bg)

def cxy(img):
    w, h = img.size
    return w // 2, h // 2

def glow(img, cx, cy, r_out, r_in, col_out, col_in, steps=30):
    draw = ImageDraw.Draw(img)
    for i in range(steps, -1, -1):
        t = i / steps
        r = int(r_in + (r_out - r_in) * t)
        a_out = col_out[3] if len(col_out) > 3 else 255
        a_in  = col_in[3]  if len(col_in)  > 3 else 255
        a = int(a_out + (a_in - a_out) * (1 - t))
        c = tuple(int(col_out[k] + (col_in[k] - col_out[k]) * (1 - t)) for k in range(3)) + (a,)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)

def noise(img, intensity=15):
    px = img.load()
    w, h = img.size
    for _ in range(w * h // 8):
        x = rng.randint(0, w-1); y = rng.randint(0, h-1)
        r, g, b, a = px[x, y]
        if a < 40: continue
        d = rng.randint(-intensity, intensity)
        px[x, y] = (max(0,min(255,r+d)), max(0,min(255,g+d)), max(0,min(255,b+d)), a)

def grid_lines(img, wc, hc):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for c in range(1, wc):
        draw.line([(c*CELL,0),(c*CELL,h-1)], fill=(255,255,255,18))
    for r in range(1, hc):
        draw.line([(0,r*CELL),(w-1,r*CELL)], fill=(255,255,255,18))

def eye(draw, cx, cy, r, iris, pupil):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=iris)
    pr = max(2, r//2)
    draw.ellipse([cx-pr, cy-pr, cx+pr, cy+pr], fill=pupil)
    hl = max(1, pr//2)
    draw.ellipse([cx-r+2, cy-r+2, cx-r+2+hl, cy-r+2+hl], fill=(255,255,255,200))

def teeth_row(draw, x0, y0, x1, count, th, tw, col, pointy=True):
    gap = (x1 - x0) // max(1, count)
    for i in range(count):
        tx = x0 + i * gap + gap // 4
        if pointy:
            draw.polygon([(tx, y0), (tx + tw, y0), (tx + tw // 2, y0 + th)], fill=col)
        else:
            draw.rectangle([tx, y0, tx + tw, y0 + th], fill=col)

def blob(draw, cx, cy, rx, ry, col, bumps=8, bump_size=0.18):
    pts = []
    for i in range(36):
        a = math.radians(i * 10)
        noise_r = 1.0 + bump_size * math.sin(a * bumps + rng.uniform(0, math.pi))
        px = cx + int(math.cos(a) * rx * noise_r)
        py = cy + int(math.sin(a) * ry * noise_r)
        pts.append((px, py))
    draw.polygon(pts, fill=col)

def save(img, wc, hc, path):
    grid_lines(img, wc, hc)
    noise(img)
    img.save(path)
    name = os.path.basename(path)
    print(f"  saved {name}  ({img.size[0]}x{img.size[1]})")

# ── 20 个 Boss 生成器 ──────────────────────────────

def gen_gargoyle(path):
    """5x4 — 石像鬼: 蝙蝠翼石兽"""
    W, H = 5, 4
    img = canvas(W, H, (12, 14, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.55), 150, 40, (0,20,0,0), (30,80,50,150))
    d = ImageDraw.Draw(img)
    body = (72, 78, 85, 252)
    dark = (40, 44, 50, 248)
    wing = (55, 60, 68, 220)
    glow_c = (60, 255, 120, 255)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.12), int(Hp*0.35)),
               (cx+s*int(Wp*0.48), int(Hp*0.08)),
               (cx+s*int(Wp*0.48), int(Hp*0.55)),
               (cx+s*int(Wp*0.20), int(Hp*0.60))]
        d.polygon(pts, fill=wing)
        for k in range(1,4):
            t=k/4
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t)
            fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],( fx, fy)], fill=(50,55,62,180), width=2)
    # body
    blob(d, cx, int(Hp*0.55), int(Wp*0.28), int(Hp*0.28), body, bumps=7, bump_size=0.14)
    blob(d, cx, int(Hp*0.50), int(Wp*0.20), int(Hp*0.20), dark, bumps=5, bump_size=0.10)
    # head
    hcx, hcy = cx, int(Hp*0.22)
    hrx, hry = int(Wp*0.20), int(Hp*0.18)
    blob(d, hcx, hcy, hrx, hry, body, bumps=6, bump_size=0.12)
    # horns
    for ox in [-int(hrx*0.6), int(hrx*0.6)]:
        d.polygon([(hcx+ox-5,hcy-hry+6),(hcx+ox+5,hcy-hry+6),(hcx+ox,max(2,hcy-hry-18))], fill=dark)
    # eyes
    ey = hcy - int(hry*0.08)
    eye(d, hcx-int(hrx*0.38), ey, 8, glow_c, (20,80,40,255))
    eye(d, hcx+int(hrx*0.38), ey, 8, glow_c, (20,80,40,255))
    # mouth
    my = hcy + int(hry*0.45)
    d.arc([hcx-int(hrx*0.45),my-8,hcx+int(hrx*0.45),my+8], 0,180, fill=dark, width=3)
    teeth_row(d, hcx-int(hrx*0.35), my-6, hcx+int(hrx*0.35), 4, 6, 6, (180,185,190,240))
    # tail
    tail_pts = [(cx, int(Hp*0.78)), (cx-int(Wp*0.05), int(Hp*0.88)), (cx+int(Wp*0.02), int(Hp*0.95))]
    for i in range(len(tail_pts)-1):
        d.line([tail_pts[i], tail_pts[i+1]], fill=dark, width=4)
    # cracks
    for _ in range(8):
        crx=rng.randint(int(Wp*0.15),int(Wp*0.85)); cry=rng.randint(int(Hp*0.30),int(Hp*0.80))
        d.line([(crx,cry),(crx+rng.randint(-14,14),cry+rng.randint(6,16))], fill=(35,38,42,180), width=2)
    # UI纹路: 凯尔特结 — 石像鬼的古老石纹
    overlay_pattern(img, "pattern_celtic.png", cx, int(Hp*0.55), int(Wp*0.26), int(Hp*0.26), (72,78,85), alpha=55)
    overlay_pattern_rect(img, "border_rune.png", int(Wp*0.05), int(Hp*0.05), int(Wp*0.90), int(Hp*0.90), (60,255,120), alpha=30)
    save(img, W, H, path)


def gen_spider(path):
    """5x4 — 影蛛: 紫色蜘蛛形"""
    W, H = 5, 4
    img = canvas(W, H, (10, 6, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 140, 40, (20,0,30,0), (80,30,120,150))
    d = ImageDraw.Draw(img)
    body = (60, 45, 85, 252)
    dark = (35, 25, 50, 248)
    leg_c = (50, 35, 70, 230)
    eye_c = (220, 50, 255, 255)
    # 8 legs
    angles_l = [155,135,200,220]
    angles_r = [25,45,340,320]
    for ang in angles_l + angles_r:
        rad = math.radians(ang)
        sx = cx + int(math.cos(rad)*int(Wp*0.14))
        sy = int(Hp*0.48) + int(math.sin(rad)*int(Hp*0.10))
        mid_x = cx + int(math.cos(rad)*int(Wp*0.30))
        mid_y = int(Hp*0.48) + int(math.sin(rad)*int(Hp*0.22))
        ex = max(4,min(Wp-4, cx+int(math.cos(rad)*int(Wp*0.46))))
        ey2 = max(4,min(Hp-4, int(Hp*0.48)+int(math.sin(rad)*int(Hp*0.38))))
        d.line([(sx,sy),(mid_x,mid_y)], fill=leg_c, width=5)
        d.line([(mid_x,mid_y),(ex,ey2)], fill=leg_c, width=3)
    # abdomen
    blob(d, cx, int(Hp*0.62), int(Wp*0.26), int(Hp*0.22), body, bumps=8, bump_size=0.16)
    blob(d, cx, int(Hp*0.60), int(Wp*0.18), int(Hp*0.15), dark, bumps=6, bump_size=0.10)
    # cephalothorax
    blob(d, cx, int(Hp*0.35), int(Wp*0.20), int(Hp*0.18), body, bumps=6, bump_size=0.12)
    # 6 eyes (3 pairs)
    for i, (ox, oy, r) in enumerate([(-12,-6,7),(12,-6,7),(-8,4,5),(8,4,5),(-16,0,4),(16,0,4)]):
        eye(d, cx+ox, int(Hp*0.30)+oy, r, eye_c, (120,20,160,255))
    # fangs
    for s in [-1, 1]:
        fx = cx + s*int(Wp*0.06)
        d.polygon([(fx-3,int(Hp*0.42)),(fx+3,int(Hp*0.42)),(fx,int(Hp*0.52))], fill=(180,160,200,240))
    # abdomen pattern
    for i in range(4):
        py = int(Hp*0.55) + i*int(Hp*0.05)
        blob(d, cx, py, int(Wp*0.06)-i*2, 4, (80,50,110,120))
    # UI纹路: 编织纹 — 蜘蛛丝网感
    overlay_pattern(img, "pattern_weave.png", cx, int(Hp*0.62), int(Wp*0.24), int(Hp*0.20), (80,50,110), alpha=50)
    overlay_pattern(img, "pattern_spiral.png", cx, int(Hp*0.35), int(Wp*0.18), int(Hp*0.16), (220,50,255), alpha=35)
    save(img, W, H, path)


def gen_serpent(path):
    """6x4 — 熔岩巨蛇: S形蜿蜒"""
    W, H = 6, 4
    img = canvas(W, H, (16, 8, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 180, 50, (50,15,0,0), (160,60,8,155))
    d = ImageDraw.Draw(img)
    body = (120, 55, 20, 252)
    dark = (70, 30, 10, 248)
    lava = (255, 120, 20, 240)
    # S-curve body segments
    spine = [(int(Wp*0.82),int(Hp*0.15)), (int(Wp*0.65),int(Hp*0.25)),
             (int(Wp*0.45),int(Hp*0.35)), (int(Wp*0.30),int(Hp*0.50)),
             (int(Wp*0.20),int(Hp*0.65)), (int(Wp*0.35),int(Hp*0.78)),
             (int(Wp*0.55),int(Hp*0.85)), (int(Wp*0.70),int(Hp*0.90))]
    for i, (sx, sy) in enumerate(spine):
        r = max(12, 30 - i*2)
        blob(d, sx, sy, r+8, r, body, bumps=6, bump_size=0.12)
    for i, (sx, sy) in enumerate(spine):
        r = max(8, 22 - i*2)
        blob(d, sx, sy, r+4, r, dark, bumps=5, bump_size=0.08)
    # head
    hcx, hcy = int(Wp*0.82), int(Hp*0.15)
    hrx, hry = int(Wp*0.14), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, body, bumps=6, bump_size=0.10)
    # eyes
    eye(d, hcx-int(hrx*0.40), hcy-int(hry*0.15), 7, lava, (60,25,5,255))
    eye(d, hcx+int(hrx*0.40), hcy-int(hry*0.15), 7, lava, (60,25,5,255))
    # mouth
    my = hcy + int(hry*0.50)
    d.line([(hcx-int(hrx*0.55),my),(hcx+int(hrx*0.55),my)], fill=(40,15,5,220), width=3)
    teeth_row(d, hcx-int(hrx*0.45), my-6, hcx+int(hrx*0.45), 4, 6, 5, (220,200,180,240))
    # lava glow between segments
    for i in range(len(spine)-1):
        mx = (spine[i][0]+spine[i+1][0])//2
        my2 = (spine[i][1]+spine[i+1][1])//2
        blob(d, mx, my2, 8, 6, lava, bumps=4, bump_size=0.20)
    # tail tip
    tx, ty = spine[-1]
    d.polygon([(tx,ty-6),(tx+18,ty),(tx,ty+6)], fill=dark)
    # scales
    for _ in range(35):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90))
        sy=rng.randint(int(Hp*0.10),int(Hp*0.92))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=(160,70,20,110),width=2)
    # UI纹路: 龙鳞纹 — 蛇身鳞片
    overlay_pattern_rect(img, "pattern_scale.png", int(Wp*0.15), int(Hp*0.15), int(Wp*0.70), int(Hp*0.70), (160,70,20), alpha=50)
    save(img, W, H, path)


def gen_giant(path):
    """7x5 — 骸骨巨人: 巨大骷髅战士"""
    W, H = 7, 5
    img = canvas(W, H, (10, 10, 8, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 220, 60, (30,25,0,0), (100,90,40,150))
    d = ImageDraw.Draw(img)
    bone = (200, 195, 178, 252)
    dark = (85, 82, 70, 248)
    glow_c = (220, 200, 120, 255)
    # ribcage torso
    blob(d, cx, int(Hp*0.55), int(Wp*0.28), int(Hp*0.26), dark, bumps=7, bump_size=0.12)
    for i in range(5):
        ry = int(Hp*0.42) + i*int(Hp*0.06)
        rw = int(Wp*0.24) - abs(i-2)*int(Wp*0.03)
        d.arc([cx-rw,ry-6,cx+rw,ry+6], 0, 180, fill=bone, width=3)
    # shoulders
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.28), int(Hp*0.32), int(Wp*0.10), int(Hp*0.08), bone, bumps=5, bump_size=0.14)
    # arms
    for s in [-1, 1]:
        ax = cx+s*int(Wp*0.36)
        d.line([(cx+s*int(Wp*0.28),int(Hp*0.36)),(ax,int(Hp*0.62))], fill=bone, width=6)
        blob(d, ax, int(Hp*0.64), 12, 10, bone, bumps=5, bump_size=0.20)
    # pelvis + legs
    blob(d, cx, int(Hp*0.72), int(Wp*0.16), int(Hp*0.08), dark, bumps=5, bump_size=0.10)
    for s in [-1, 1]:
        lx = cx + s*int(Wp*0.12)
        d.line([(lx,int(Hp*0.76)),(lx+s*int(Wp*0.04),int(Hp*0.94))], fill=bone, width=5)
    # skull head
    hcx, hcy = cx, int(Hp*0.16)
    hrx, hry = int(Wp*0.16), int(Hp*0.15)
    blob(d, hcx, hcy, hrx, hry, bone, bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.25), int(hrx*0.75), int(hry*0.55), (170,165,150,240), bumps=4, bump_size=0.06)
    # eye sockets
    ey = hcy - int(hry*0.05)
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.35)
        d.ellipse([ex-8,ey-6,ex+8,ey+6], fill=(20,18,15,240))
        eye(d, ex, ey, 5, glow_c, (255,240,160,255))
    # jaw
    jy = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.45),jy),(hcx+int(hrx*0.45),jy)], fill=(30,28,22,220), width=3)
    teeth_row(d, hcx-int(hrx*0.38), jy-6, hcx+int(hrx*0.38), 5, 7, 6, bone)
    # UI纹路: 锯齿纹 — 骨骼战士粗犷纹路
    overlay_pattern(img, "pattern_zigzag.png", cx, int(Hp*0.50), int(Wp*0.25), int(Hp*0.24), (200,190,150), alpha=45)
    overlay_pattern_rect(img, "border_rune.png", int(Wp*0.08), int(Hp*0.08), int(Wp*0.84), int(Hp*0.84), (200,190,150), alpha=25)
    save(img, W, H, path)


def gen_demon(path):
    """6x5 — 深渊魔王: 带翼恶魔"""
    W, H = 6, 5
    img = canvas(W, H, (14, 4, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 200, 55, (50,5,0,0), (180,30,10,160))
    d = ImageDraw.Draw(img)
    body = (100, 25, 18, 252)
    dark = (50, 12, 8, 248)
    fire = (255, 60, 30, 240)
    # demon wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.18),int(Hp*0.35)),
               (cx+s*int(Wp*0.48),int(Hp*0.06)),
               (cx+s*int(Wp*0.48),int(Hp*0.58)),
               (cx+s*int(Wp*0.22),int(Hp*0.55))]
        d.polygon(pts, fill=(70,15,10,215))
        for k in range(1,4):
            t=k/4; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=(90,20,12,160), width=2)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.30), int(Hp*0.28), body, bumps=7, bump_size=0.14)
    blob(d, cx, int(Hp*0.54), int(Wp*0.22), int(Hp*0.20), dark, bumps=5, bump_size=0.10)
    # legs
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.16), int(Hp*0.84), int(Wp*0.08), int(Hp*0.12), dark, bumps=5, bump_size=0.14)
    # head
    hcx, hcy = cx, int(Hp*0.20)
    hrx, hry = int(Wp*0.18), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, body, bumps=6, bump_size=0.12)
    # horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.6)
        tip_x = bx + s*16
        d.polygon([(bx-5,hcy-hry+5),(bx+5,hcy-hry+5),(tip_x,max(2,hcy-hry-28))], fill=(60,15,8,255))
    # eyes
    ey = hcy - int(hry*0.05)
    eye(d, hcx-int(hrx*0.38), ey, 9, fire, (80,15,5,255))
    eye(d, hcx+int(hrx*0.38), ey, 9, fire, (80,15,5,255))
    # mouth
    my = hcy + int(hry*0.50)
    d.arc([hcx-int(hrx*0.50),my-10,hcx+int(hrx*0.50),my+10], 0,180, fill=(30,8,4,220), width=4)
    teeth_row(d, hcx-int(hrx*0.40), my-7, hcx+int(hrx*0.40), 5, 8, 7, (220,180,160,240))
    # fire aura
    for _ in range(15):
        fx=rng.randint(int(Wp*0.10),int(Wp*0.90)); fy=rng.randint(int(Hp*0.20),int(Hp*0.85))
        blob(d, fx, fy, rng.randint(4,10), rng.randint(3,8), (255,80,20,100))
    # UI纹路: 希腊回纹 — 恶魔仪式纹
    overlay_pattern(img, "pattern_greek_key.png", cx, int(Hp*0.58), int(Wp*0.28), int(Hp*0.22), (200,40,20), alpha=50)
    overlay_pattern_rect(img, "divider_chain.png", int(Wp*0.10), int(Hp*0.45), int(Wp*0.80), 20, (255,80,20), alpha=40)
    save(img, W, H, path)


def gen_witch(path):
    """5x5 — 冰霜女巫: 猫头鹰形冰法师"""
    W, H = 5, 5
    img = canvas(W, H, (6, 10, 18, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 170, 45, (0,15,40,0), (40,100,200,155))
    d = ImageDraw.Draw(img)
    robe = (90, 130, 180, 250)
    dark = (50, 70, 110, 248)
    ice  = (160, 220, 255, 235)
    # robe body
    robe_pts = [(cx-int(Wp*0.44),int(Hp*0.92)), (cx+int(Wp*0.44),int(Hp*0.92)),
                (cx+int(Wp*0.28),int(Hp*0.55)), (cx+int(Wp*0.18),int(Hp*0.28)),
                (cx-int(Wp*0.18),int(Hp*0.28)), (cx-int(Wp*0.28),int(Hp*0.55))]
    d.polygon(robe_pts, fill=dark)
    blob(d, cx, int(Hp*0.58), int(Wp*0.26), int(Hp*0.26), robe, bumps=6, bump_size=0.08)
    # owl-like head
    hcx, hcy = cx, int(Hp*0.18)
    hrx, hry = int(Wp*0.22), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, robe, bumps=6, bump_size=0.10)
    # ear tufts
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.55),hcy-hry+6),(hcx+s*int(hrx*0.70),hcy-hry+4),
                   (hcx+s*int(hrx*0.45),max(2,hcy-hry-22))], fill=dark)
    # large owl eyes
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.36)
        ey = hcy - int(hry*0.05)
        d.ellipse([ex-12,ey-10,ex+12,ey+10], fill=(30,45,70,255))
        eye(d, ex, ey, 9, ice, (40,80,140,255))
    # beak
    by = hcy + int(hry*0.40)
    d.polygon([(hcx-8,by-4),(hcx+8,by-4),(hcx,by+10)], fill=(140,170,200,245))
    # ice crystal staff
    sx = cx - int(Wp*0.30)
    d.line([(sx,int(Hp*0.30)),(sx,int(Hp*0.88))], fill=(120,150,190,230), width=4)
    for i in range(3):
        cy2 = int(Hp*0.30) - i*14
        d.polygon([(sx-6,cy2),(sx+6,cy2),(sx,max(2,cy2-16))], fill=ice)
    # frost particles
    for _ in range(12):
        fx=rng.randint(6,Wp-6); fy=rng.randint(6,Hp-6)
        blob(d, fx, fy, rng.randint(3,7), rng.randint(2,5), (180,220,255,80))
    # UI纹路: 菱形编织 — 冰晶结构纹
    overlay_pattern(img, "pattern_diamond.png", cx, int(Hp*0.52), int(Wp*0.22), int(Hp*0.24), (140,190,240), alpha=50)
    overlay_pattern_rect(img, "divider_wave.png", int(Wp*0.08), int(Hp*0.82), int(Wp*0.84), 16, (180,220,255), alpha=40)
    save(img, W, H, path)


def gen_wyvern(path):
    """7x4 — 暗夜飞龙: 展翅龙"""
    W, H = 7, 4
    img = canvas(W, H, (4, 12, 10, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 210, 55, (0,30,20,0), (10,100,70,155))
    d = ImageDraw.Draw(img)
    body = (30, 90, 70, 252)
    dark = (15, 55, 40, 248)
    glow_c = (40, 255, 180, 255)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.10),int(Hp*0.40)),
               (cx+s*int(Wp*0.48),int(Hp*0.05)),
               (cx+s*int(Wp*0.48),int(Hp*0.60)),
               (cx+s*int(Wp*0.16),int(Hp*0.56))]
        d.polygon(pts, fill=(20,65,48,215))
        for k in range(1,5):
            t=k/5; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=(25,75,55,160), width=2)
    # body
    blob(d, cx, int(Hp*0.52), int(Wp*0.18), int(Hp*0.25), body, bumps=6, bump_size=0.12)
    # neck
    d.polygon([(cx-int(Wp*0.05),int(Hp*0.35)),(cx+int(Wp*0.05),int(Hp*0.35)),
               (cx+int(Wp*0.04),int(Hp*0.18)),(cx-int(Wp*0.04),int(Hp*0.18))], fill=body)
    # head
    hcx, hcy = cx, int(Hp*0.12)
    hrx, hry = int(Wp*0.10), int(Hp*0.11)
    blob(d, hcx, hcy, hrx, hry, body, bumps=5, bump_size=0.10)
    # horns
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.55),hcy-hry+4),(hcx+s*int(hrx*0.65),hcy-hry+2),
                   (hcx+s*int(hrx*0.40)+s*10,max(2,hcy-hry-16))], fill=dark)
    eye(d, hcx-int(hrx*0.40), hcy, 5, glow_c, (10,60,40,255))
    eye(d, hcx+int(hrx*0.40), hcy, 5, glow_c, (10,60,40,255))
    # jaw
    my = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.50),my),(hcx+int(hrx*0.50),my)], fill=(8,30,22,220), width=2)
    teeth_row(d, hcx-int(hrx*0.40), my-5, hcx+int(hrx*0.40), 3, 5, 5, (200,210,200,240))
    # tail
    tail_pts = [(cx,int(Hp*0.72)),(cx-int(Wp*0.06),int(Hp*0.85)),(cx-int(Wp*0.10),int(Hp*0.94))]
    for i in range(len(tail_pts)-1):
        d.line([tail_pts[i],tail_pts[i+1]], fill=dark, width=max(2,5-i*2))
    # scales
    for _ in range(30):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.20),int(Hp*0.80))
        d.arc([sx-4,sy-2,sx+4,sy+2],180,360,fill=(45,120,90,110),width=2)
    # UI纹路: 龙鳞纹 — 飞龙鳞甲
    overlay_pattern(img, "pattern_scale.png", cx, int(Hp*0.48), int(Wp*0.22), int(Hp*0.22), (40,120,80), alpha=50)
    overlay_pattern_rect(img, "pattern_zigzag.png", int(Wp*0.08), int(Hp*0.06), int(Wp*0.84), int(Hp*0.15), (80,160,130), alpha=35)
    save(img, W, H, path)


def gen_kraken(path):
    """6x5 — 深海巨怪: 章鱼触手"""
    W, H = 6, 5
    img = canvas(W, H, (3, 6, 14, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.45), 200, 55, (0,10,40,0), (10,50,120,155))
    d = ImageDraw.Draw(img)
    body = (20, 50, 95, 252)
    dark = (12, 30, 60, 248)
    sucker = (35, 85, 130, 200)
    eye_c = (0, 210, 180, 255)
    # mantle head
    mantle_pts = [(cx,max(2,int(Hp*0.04))),
                  (cx+int(Wp*0.26),int(Hp*0.18)),
                  (cx+int(Wp*0.28),int(Hp*0.48)),
                  (cx-int(Wp*0.28),int(Hp*0.48)),
                  (cx-int(Wp*0.26),int(Hp*0.18))]
    d.polygon(mantle_pts, fill=body)
    d.polygon([(cx,max(2,int(Hp*0.07))),
               (cx+int(Wp*0.20),int(Hp*0.20)),
               (cx+int(Wp*0.22),int(Hp*0.44)),
               (cx-int(Wp*0.22),int(Hp*0.44)),
               (cx-int(Wp*0.20),int(Hp*0.20))], fill=(25,60,110,248))
    # eyes
    ey = int(Hp*0.28)
    eye(d, cx-int(Wp*0.12), ey, 10, eye_c, (0, 80, 60, 255))
    eye(d, cx+int(Wp*0.12), ey, 10, eye_c, (0, 80, 60, 255))
    # mouth
    d.arc([cx-int(Wp*0.12),int(Hp*0.38)-8,cx+int(Wp*0.12),int(Hp*0.38)+8], 0,180, fill=dark, width=3)
    # 8 tentacles
    base_y = int(Hp*0.50)
    for i in range(8):
        ang = 200 + i*20
        rad = math.radians(ang)
        length = int(min(Wp,Hp)*0.42)
        ex = max(4,min(Wp-4, cx+int(math.cos(rad)*length)))
        ey2 = max(base_y,min(Hp-4, base_y+int(abs(math.sin(rad))*length)))
        pts = []
        for j in range(9):
            t=j/8
            px2=cx+(ex-cx)*t; py2=base_y+(ey2-base_y)*t
            perp_x=-(ey2-base_y); perp_y=ex-cx
            ln=math.hypot(perp_x,perp_y) or 1
            wave=math.sin(t*math.pi*2.5)*12*(1-t)*(1 if i%2==0 else -1)
            pts.append((px2+perp_x/ln*wave, py2+perp_y/ln*wave))
        for j in range(len(pts)-1):
            w=max(1,int(7*(1-j/len(pts))))
            col_a = max(60, int(200*(1-j/len(pts))))
            d.line([pts[j],pts[j+1]], fill=(70,30,120,col_a), width=w)
            if j%2==0:
                mx=int((pts[j][0]+pts[j+1][0])/2); my2=int((pts[j][1]+pts[j+1][1])/2)
                sr=max(2,w//2)
                d.ellipse([mx-sr,my2-sr,mx+sr,my2+sr], fill=sucker)
    # UI纹路: 旋涡纹 — 深海漩涡
    overlay_pattern(img, "pattern_spiral.png", cx, int(Hp*0.32), int(Wp*0.24), int(Hp*0.20), (30,100,160), alpha=50)
    overlay_pattern_rect(img, "divider_wave.png", int(Wp*0.05), int(Hp*0.55), int(Wp*0.90), 16, (80,180,220), alpha=40)
    save(img, W, H, path)


def gen_golem(path):
    """5x5 — 铁甲傀儡: 石龟乌龟形"""
    W, H = 5, 5
    img = canvas(W, H, (10, 10, 8, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.55), 165, 45, (20,15,0,0), (100,80,20,145))
    d = ImageDraw.Draw(img)
    shell = (95, 100, 90, 252)
    dark = (55, 60, 50, 248)
    metal = (160, 155, 140, 240)
    lava = (255, 200, 80, 240)
    # shell dome
    blob(d, cx, int(Hp*0.55), int(Wp*0.40), int(Hp*0.30), shell, bumps=8, bump_size=0.14)
    blob(d, cx, int(Hp*0.52), int(Wp*0.30), int(Hp*0.22), dark, bumps=6, bump_size=0.10)
    # shell plates
    for i in range(4):
        a = math.radians(-30 + i*40)
        px2 = cx + int(math.cos(a)*int(Wp*0.22))
        py2 = int(Hp*0.52) + int(math.sin(a)*int(Hp*0.14))
        blob(d, px2, py2, 14, 12, metal, bumps=5, bump_size=0.12)
    # head
    hcx, hcy = cx, int(Hp*0.22)
    hrx, hry = int(Wp*0.18), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, shell, bumps=6, bump_size=0.12)
    # brow ridge
    d.polygon([(hcx-int(hrx*0.60),hcy-int(hry*0.15)),
               (hcx+int(hrx*0.60),hcy-int(hry*0.15)),
               (hcx+int(hrx*0.50),hcy-int(hry*0.40)),
               (hcx-int(hrx*0.50),hcy-int(hry*0.40))], fill=dark)
    # eyes
    ey = hcy + int(hry*0.05)
    eye(d, hcx-int(hrx*0.35), ey, 7, lava, (80,60,10,255))
    eye(d, hcx+int(hrx*0.35), ey, 7, lava, (80,60,10,255))
    # mouth
    my = hcy + int(hry*0.55)
    for i in range(6):
        t=i/5
        d.line([(hcx-int(hrx*0.45)+int(hrx*0.90*t),my+(4 if i%2==0 else -4)),
                (hcx-int(hrx*0.45)+int(hrx*0.90*(t+0.16)),my+(-4 if i%2==0 else 4))], fill=(30,32,28,220), width=2)
    # legs
    for s in [-1, 1]:
        for oy in [0, int(Hp*0.22)]:
            lx = cx + s*int(Wp*0.36)
            ly = int(Hp*0.50) + oy
            blob(d, lx, ly, int(Wp*0.08), int(Hp*0.08), shell, bumps=5, bump_size=0.16)
    # moss
    for _ in range(10):
        mx=rng.randint(int(Wp*0.12),int(Wp*0.88)); my2=rng.randint(int(Hp*0.30),int(Hp*0.80))
        blob(d, mx, my2, rng.randint(4,9), rng.randint(3,7), (40,110,45,130))
    # UI纹路: 凯尔特结 — 铁甲符文
    overlay_pattern(img, "pattern_celtic.png", cx, int(Hp*0.50), int(Wp*0.26), int(Hp*0.26), (160,140,80), alpha=50)
    overlay_pattern_rect(img, "border_rune.png", int(Wp*0.10), int(Hp*0.10), int(Wp*0.80), int(Hp*0.80), (180,150,50), alpha=30)
    save(img, W, H, path)


def gen_wolf(path):
    """6x5 — 血月狼王: 奔跑狼形"""
    W, H = 6, 5
    img = canvas(W, H, (14, 4, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 200, 55, (40,5,5,0), (140,20,20,155))
    d = ImageDraw.Draw(img)
    fur = (95, 25, 22, 252)
    dark = (50, 12, 10, 248)
    eye_c = (255, 50, 50, 255)
    # body - hunched wolf form
    blob(d, cx+int(Wp*0.05), int(Hp*0.50), int(Wp*0.32), int(Hp*0.22), fur, bumps=8, bump_size=0.14)
    blob(d, cx+int(Wp*0.05), int(Hp*0.48), int(Wp*0.24), int(Hp*0.16), dark, bumps=6, bump_size=0.10)
    # mane
    blob(d, cx-int(Wp*0.06), int(Hp*0.34), int(Wp*0.18), int(Hp*0.16), fur, bumps=9, bump_size=0.18)
    # head
    hcx = cx - int(Wp*0.14)
    hcy = int(Hp*0.22)
    hrx, hry = int(Wp*0.14), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, fur, bumps=6, bump_size=0.12)
    # snout
    snout_x = hcx - int(hrx*0.40)
    blob(d, snout_x, hcy+int(hry*0.20), int(hrx*0.50), int(hry*0.40), (110,30,25,250), bumps=4, bump_size=0.08)
    # ears
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.35),hcy-hry+4),
                   (hcx+s*int(hrx*0.55),max(2,hcy-hry-18)),
                   (hcx+s*int(hrx*0.20),hcy-hry+2)], fill=dark)
    # eyes
    eye(d, hcx-int(hrx*0.15), hcy-int(hry*0.10), 7, eye_c, (80,15,10,255))
    eye(d, hcx+int(hrx*0.25), hcy-int(hry*0.10), 7, eye_c, (80,15,10,255))
    # mouth
    my = hcy + int(hry*0.50)
    d.line([(snout_x-int(hrx*0.30),my),(hcx+int(hrx*0.10),my)], fill=(30,8,6,220), width=3)
    teeth_row(d, snout_x-int(hrx*0.20), my-5, hcx, 4, 6, 5, (210,190,180,240))
    # legs
    for i, (lx, ly) in enumerate([(cx-int(Wp*0.18),int(Hp*0.72)),
                                   (cx+int(Wp*0.08),int(Hp*0.74)),
                                   (cx+int(Wp*0.22),int(Hp*0.70)),
                                   (cx-int(Wp*0.08),int(Hp*0.78))]):
        d.line([(lx,ly),(lx+(4 if i<2 else -4),int(Hp*0.94))], fill=dark, width=4)
    # tail
    d.line([(cx+int(Wp*0.30),int(Hp*0.42)),(cx+int(Wp*0.42),int(Hp*0.28)),
            (cx+int(Wp*0.44),int(Hp*0.22))], fill=fur, width=5, joint="curve")
    # blood drip
    for _ in range(8):
        bx=rng.randint(int(Wp*0.10),int(Wp*0.90)); by=rng.randint(int(Hp*0.50),int(Hp*0.92))
        d.line([(bx,by),(bx,by+rng.randint(6,14))], fill=(200,20,20,120), width=2)
    # UI纹路: 藤蔓花纹 — 血月野性纹
    overlay_pattern(img, "pattern_vine.png", cx, int(Hp*0.50), int(Wp*0.28), int(Hp*0.22), (180,40,30), alpha=45)
    save(img, W, H, path)


def gen_titan(path):
    """7x5 — 雷霆泰坦: 螃蟹形电光巨人"""
    W, H = 7, 5
    img = canvas(W, H, (4, 4, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 230, 60, (0,0,50,0), (35,70,220,160))
    d = ImageDraw.Draw(img)
    armor = (40, 50, 130, 252)
    dark = (20, 25, 70, 248)
    elec = (200, 230, 255, 235)
    bright = (130, 180, 255, 248)
    # massive body
    blob(d, cx, int(Hp*0.58), int(Wp*0.36), int(Hp*0.28), armor, bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.54), int(Wp*0.26), int(Hp*0.20), dark, bumps=5, bump_size=0.08)
    # energy core
    blob(d, cx, int(Hp*0.52), 22, 22, bright, bumps=7, bump_size=0.15)
    blob(d, cx, int(Hp*0.52), 12, 12, elec, bumps=4, bump_size=0.10)
    # crab claws
    for s in [-1, 1]:
        ax = cx + s*int(Wp*0.32)
        blob(d, ax, int(Hp*0.40), int(Wp*0.10), int(Hp*0.12), armor, bumps=5, bump_size=0.12)
        claw_x = cx + s*int(Wp*0.44)
        d.polygon([(ax,int(Hp*0.36)),(claw_x,int(Hp*0.26)),(claw_x,int(Hp*0.40))], fill=bright)
        d.polygon([(ax,int(Hp*0.44)),(claw_x,int(Hp*0.48)),(claw_x,int(Hp*0.38))], fill=armor)
    # legs
    for s in [-1, 1]:
        for i in range(2):
            lx = cx + s*int(Wp*0.18) + s*i*int(Wp*0.10)
            blob(d, lx, int(Hp*0.84), int(Wp*0.06), int(Hp*0.10), dark, bumps=4, bump_size=0.12)
    # head
    hcx, hcy = cx, int(Hp*0.20)
    hrx, hry = int(Wp*0.16), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, armor, bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.18), int(hrx*0.78), int(hry*0.68), dark, bumps=5, bump_size=0.08)
    # lightning horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.50)
        d.polygon([(bx-4,hcy-hry+3),(bx+4,hcy-hry+3),(bx+s*12,max(2,hcy-hry-26))], fill=elec)
    # visor eyes
    ey = hcy - int(hry*0.08)
    d.ellipse([hcx-int(hrx*0.50),ey-5,hcx+int(hrx*0.50),ey+5], fill=bright)
    eye(d, hcx-int(hrx*0.30), ey, 5, elec, (255,255,255,255))
    eye(d, hcx+int(hrx*0.30), ey, 5, elec, (255,255,255,255))
    # lightning arcs
    for _ in range(12):
        lx=rng.randint(int(Wp*0.12),int(Wp*0.88)); ly=rng.randint(int(Hp*0.25),int(Hp*0.80))
        for _ in range(3):
            d.line([(lx,ly),(lx+rng.randint(-18,18),ly+rng.randint(-12,12))], fill=elec, width=1)
    # UI纹路: 锯齿纹 — 电弧闪电纹
    overlay_pattern(img, "pattern_zigzag.png", cx, int(Hp*0.52), int(Wp*0.30), int(Hp*0.24), (60,180,255), alpha=45)
    overlay_pattern_rect(img, "divider_chain.png", int(Wp*0.08), int(Hp*0.78), int(Wp*0.84), 20, (80,200,255), alpha=35)
    save(img, W, H, path)


def gen_mushroom(path):
    """5x5 — 毒雾蘑菇: 巨大蘑菇怪"""
    W, H = 5, 5
    img = canvas(W, H, (8, 12, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 165, 45, (10,30,0,0), (45,130,15,150))
    d = ImageDraw.Draw(img)
    cap = (75, 120, 35, 252)
    stem = (140, 135, 100, 248)
    spot = (190, 200, 50, 230)
    dark = (40, 65, 18, 248)
    # stem
    d.polygon([(cx-int(Wp*0.12),int(Hp*0.40)),(cx+int(Wp*0.12),int(Hp*0.40)),
               (cx+int(Wp*0.16),int(Hp*0.88)),(cx-int(Wp*0.16),int(Hp*0.88))], fill=stem)
    blob(d, cx, int(Hp*0.88), int(Wp*0.20), int(Hp*0.08), (120,115,80,240), bumps=6, bump_size=0.12)
    # mushroom cap - big dome
    blob(d, cx, int(Hp*0.28), int(Wp*0.42), int(Hp*0.24), cap, bumps=8, bump_size=0.16)
    blob(d, cx, int(Hp*0.26), int(Wp*0.34), int(Hp*0.18), dark, bumps=6, bump_size=0.12)
    # spots on cap
    for _ in range(8):
        sx=cx+rng.randint(-int(Wp*0.30),int(Wp*0.30))
        sy=int(Hp*0.20)+rng.randint(-int(Hp*0.12),int(Hp*0.12))
        sr=rng.randint(6,14)
        blob(d, sx, sy, sr, int(sr*0.8), spot, bumps=4, bump_size=0.15)
    # face on stem
    ey = int(Hp*0.50)
    eye(d, cx-int(Wp*0.06), ey, 7, spot, (50,65,15,255))
    eye(d, cx+int(Wp*0.06), ey, 7, spot, (50,65,15,255))
    my = int(Hp*0.62)
    d.arc([cx-int(Wp*0.08),my-8,cx+int(Wp*0.08),my+8], 0,180, fill=dark, width=3)
    # spore particles
    for _ in range(18):
        fx=rng.randint(6,Wp-6); fy=rng.randint(6,Hp-6)
        blob(d, fx, fy, rng.randint(2,6), rng.randint(2,4), (160,180,40,90))
    # UI纹路: 旋涡纹 — 蘑菇孢子旋涡
    overlay_pattern(img, "pattern_spiral.png", cx, int(Hp*0.30), int(Wp*0.24), int(Hp*0.18), (140,160,40), alpha=45)
    overlay_pattern(img, "pattern_vine.png", cx, int(Hp*0.65), int(Wp*0.18), int(Hp*0.16), (80,120,30), alpha=40)
    save(img, W, H, path)


def gen_crystal(path):
    """5x5 — 水晶守卫: 海星形水晶体"""
    W, H = 5, 5
    img = canvas(W, H, (4, 14, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 165, 45, (0,20,25,0), (10,100,110,155))
    d = ImageDraw.Draw(img)
    crystal = (50, 130, 140, 252)
    bright = (160, 230, 245, 235)
    dark = (25, 70, 80, 248)
    core = (0, 255, 220, 240)
    # crystal spikes radiating from center (star/starfish)
    for i in range(5):
        ang = math.radians(-90 + i*72)
        tip_x = cx + int(math.cos(ang)*int(Wp*0.44))
        tip_y = int(Hp*0.48) + int(math.sin(ang)*int(Hp*0.42))
        tip_x = max(4,min(Wp-4,tip_x))
        tip_y = max(4,min(Hp-4,tip_y))
        base_w = int(Wp*0.08)
        perp = ang + math.pi/2
        bx1 = cx+int(math.cos(perp)*base_w)
        by1 = int(Hp*0.48)+int(math.sin(perp)*base_w)
        bx2 = cx-int(math.cos(perp)*base_w)
        by2 = int(Hp*0.48)-int(math.sin(perp)*base_w)
        d.polygon([(bx1,by1),(tip_x,tip_y),(bx2,by2)], fill=crystal)
        d.line([(cx,int(Hp*0.48)),(tip_x,tip_y)], fill=bright, width=2)
    # core body
    blob(d, cx, int(Hp*0.48), int(Wp*0.18), int(Hp*0.18), dark, bumps=6, bump_size=0.10)
    blob(d, cx, int(Hp*0.48), int(Wp*0.12), int(Hp*0.12), crystal, bumps=5, bump_size=0.08)
    # central eye
    eye(d, cx, int(Hp*0.46), 12, core, (0,120,100,255))
    # smaller eyes on tips
    for i in range(5):
        ang = math.radians(-90 + i*72)
        tx = cx + int(math.cos(ang)*int(Wp*0.32))
        ty = int(Hp*0.48) + int(math.sin(ang)*int(Hp*0.30))
        tx = max(8,min(Wp-8,tx)); ty = max(8,min(Hp-8,ty))
        eye(d, tx, ty, 4, core, (0,80,70,255))
    # crystal shards floating
    for _ in range(8):
        sx=rng.randint(8,Wp-8); sy=rng.randint(8,Hp-8)
        sh=rng.randint(8,16)
        d.polygon([(sx-3,sy),(sx,sy-sh),(sx+3,sy)], fill=bright)
    # UI纹路: 菱形编织 — 水晶棱面纹
    overlay_pattern(img, "pattern_diamond.png", cx, int(Hp*0.50), int(Wp*0.22), int(Hp*0.22), (80,220,210), alpha=50)
    save(img, W, H, path)


def gen_assassin(path):
    """5x5 — 暗影刺客: 蝎子形"""
    W, H = 5, 5
    img = canvas(W, H, (8, 6, 10, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.55), 165, 45, (15,0,20,0), (80,20,100,150))
    d = ImageDraw.Draw(img)
    body = (45, 42, 52, 252)
    dark = (22, 20, 28, 248)
    purple = (200, 50, 255, 240)
    # scorpion body
    blob(d, cx, int(Hp*0.58), int(Wp*0.28), int(Hp*0.18), body, bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.56), int(Wp*0.20), int(Hp*0.12), dark, bumps=5, bump_size=0.08)
    # tail curling up and over
    tail_pts = [(cx,int(Hp*0.44)),(cx+int(Wp*0.05),int(Hp*0.32)),
                (cx+int(Wp*0.02),int(Hp*0.18)),(cx-int(Wp*0.06),int(Hp*0.10)),
                (cx-int(Wp*0.10),int(Hp*0.06))]
    for i in range(len(tail_pts)-1):
        w = max(2, 8-i*2)
        d.line([tail_pts[i],tail_pts[i+1]], fill=body, width=w)
    # stinger
    sx, sy = tail_pts[-1]
    d.polygon([(sx-4,sy+2),(sx+4,sy+2),(sx,max(2,sy-12))], fill=purple)
    # claws
    for s in [-1, 1]:
        ax = cx + s*int(Wp*0.30)
        ay = int(Hp*0.45)
        d.line([(cx+s*int(Wp*0.18),int(Hp*0.52)),(ax,ay)], fill=body, width=5)
        d.polygon([(ax,ay-6),(ax+s*14,ay-10),(ax+s*8,ay)], fill=dark)
        d.polygon([(ax,ay+6),(ax+s*14,ay+10),(ax+s*8,ay)], fill=dark)
    # legs
    for s in [-1, 1]:
        for i in range(3):
            lx = cx + s*int(Wp*0.16) + s*i*int(Wp*0.06)
            ly = int(Hp*0.62) + i*int(Hp*0.06)
            d.line([(lx,ly),(lx+s*int(Wp*0.12),ly+int(Hp*0.14))], fill=dark, width=3)
    # head
    hcx, hcy = cx, int(Hp*0.52)
    blob(d, hcx, hcy, int(Wp*0.12), int(Hp*0.08), body, bumps=5, bump_size=0.10)
    eye(d, hcx-8, hcy-2, 5, purple, (120,20,160,255))
    eye(d, hcx+8, hcy-2, 5, purple, (120,20,160,255))
    # shadow wisps
    for _ in range(10):
        wx=rng.randint(8,Wp-8); wy=rng.randint(8,Hp-8)
        blob(d, wx, wy, rng.randint(4,10), rng.randint(3,7), (80,40,120,70))
    # UI纹路: 编织纹 — 暗影蝎甲
    overlay_pattern(img, "pattern_weave.png", cx, int(Hp*0.68), int(Wp*0.22), int(Hp*0.20), (60,30,90), alpha=45)
    overlay_pattern(img, "pattern_greek_key.png", cx, int(Hp*0.52), int(Wp*0.10), int(Hp*0.06), (120,60,180), alpha=40)
    save(img, W, H, path)


def gen_phoenix(path):
    """7x5 — 火焰凤凰: 金红展翅"""
    W, H = 7, 5
    img = canvas(W, H, (16, 6, 2, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 220, 55, (60,12,0,0), (200,80,8,165))
    d = ImageDraw.Draw(img)
    body = (210, 80, 10, 250)
    wing = (190, 55, 5, 218)
    feather = (240, 160, 20, 225)
    tail = (255, 200, 30, 215)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.14),int(Hp*0.42)),
               (cx+s*int(Wp*0.48),int(Hp*0.06)),
               (cx+s*int(Wp*0.48),int(Hp*0.55)),
               (cx+s*int(Wp*0.22),int(Hp*0.58))]
        d.polygon(pts, fill=wing)
        for k in range(4):
            t=(k+1)/5
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t)
            fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            tip_x=max(2,min(Wp-2,fx+s*16)); tip_y=max(2,min(Hp-2,fy-12))
            d.polygon([(fx-5,fy),(fx+5,fy),(tip_x,tip_y)], fill=feather)
    # body
    blob(d, cx, int(Hp*0.54), int(Wp*0.16), int(Hp*0.22), body, bumps=6, bump_size=0.10)
    # tail
    for i in range(5):
        tx = cx + (i-2)*int(Wp*0.06)
        d.polygon([(tx-6,int(Hp*0.73)),(tx+6,int(Hp*0.73)),(tx,min(Hp-2,int(Hp*0.95)))], fill=tail)
    # head
    hcx, hcy = cx, int(Hp*0.24)
    hrx, hry = int(Wp*0.10), int(Hp*0.12)
    blob(d, hcx, hcy, hrx, hry, body, bumps=5, bump_size=0.10)
    # flame crest
    for ox, ch in [(-int(hrx*0.50),18),(0,26),(int(hrx*0.50),18)]:
        d.polygon([(hcx+ox-4,hcy-hry+4),(hcx+ox+4,hcy-hry+4),(hcx+ox,max(2,hcy-hry-ch))], fill=feather)
    # eyes
    eye(d, hcx-int(hrx*0.40), hcy, 5, (255,230,50,255), (80,30,0,255))
    eye(d, hcx+int(hrx*0.40), hcy, 5, (255,230,50,255), (80,30,0,255))
    # beak
    by = hcy + int(hry*0.35)
    d.polygon([(hcx-int(hrx*0.28),by),(hcx+int(hrx*0.28),by),(hcx,by+int(hry*0.50))], fill=(230,170,20,250))
    # flame particles
    for _ in range(16):
        fx=rng.randint(8,Wp-8); fy=rng.randint(8,Hp-8)
        blob(d, fx, fy, rng.randint(3,8), rng.randint(2,6), (255,140,30,80))
    # UI纹路: 龙鳞纹 — 凤凰羽鳞
    overlay_pattern(img, "pattern_scale.png", cx, int(Hp*0.50), int(Wp*0.26), int(Hp*0.22), (255,160,30), alpha=45)
    overlay_pattern_rect(img, "divider_ornate.png", int(Wp*0.10), int(Hp*0.42), int(Wp*0.80), 24, (255,200,60), alpha=35)
    save(img, W, H, path)


def gen_lich(path):
    """6x5 — 死灵巫王: 骷髅法师"""
    W, H = 6, 5
    img = canvas(W, H, (6, 10, 6, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 200, 55, (10,25,0,0), (40,120,30,155))
    d = ImageDraw.Draw(img)
    robe = (35, 55, 30, 250)
    dark = (18, 30, 15, 248)
    soul = (100, 255, 80, 240)
    bone = (195, 188, 170, 245)
    # robe
    robe_pts = [(cx-int(Wp*0.44),int(Hp*0.94)),(cx+int(Wp*0.44),int(Hp*0.94)),
                (cx+int(Wp*0.30),int(Hp*0.58)),(cx+int(Wp*0.20),int(Hp*0.26)),
                (cx-int(Wp*0.20),int(Hp*0.26)),(cx-int(Wp*0.30),int(Hp*0.58))]
    d.polygon(robe_pts, fill=dark)
    blob(d, cx, int(Hp*0.58), int(Wp*0.24), int(Hp*0.24), robe, bumps=6, bump_size=0.08)
    # skull head
    hcx, hcy = cx, int(Hp*0.16)
    hrx, hry = int(Wp*0.16), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, bone, bumps=6, bump_size=0.08)
    blob(d, hcx, hcy+int(hry*0.30), int(hrx*0.72), int(hry*0.48), (170,162,148,240), bumps=4, bump_size=0.06)
    # crown
    for ox, sh in [(-int(hrx*0.50),14),(-int(hrx*0.20),20),(0,26),(int(hrx*0.20),20),(int(hrx*0.50),14)]:
        d.polygon([(hcx+ox-4,hcy-hry+4),(hcx+ox+4,hcy-hry+4),(hcx+ox,max(2,hcy-hry-sh))], fill=soul)
    # eye sockets
    ey = hcy - int(hry*0.05)
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.36)
        d.ellipse([ex-7,ey-5,ex+7,ey+5], fill=(15,20,12,240))
        eye(d, ex, ey, 5, soul, (160,255,120,255))
    # jaw
    jy = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.40),jy),(hcx+int(hrx*0.40),jy)], fill=(12,18,10,220), width=3)
    # soul orb chest
    orb_cy = int(Hp*0.48)
    blob(d, cx, orb_cy, 18, 18, (60,180,50,200), bumps=8, bump_size=0.15)
    blob(d, cx, orb_cy, 10, 10, soul, bumps=4, bump_size=0.10)
    # bony hands
    for s in [-1, 1]:
        hx = cx + s*int(Wp*0.26)
        hy = int(Hp*0.52)
        blob(d, hx, hy, 10, 8, bone, bumps=5, bump_size=0.20)
    # soul wisps
    for _ in range(10):
        wx=rng.randint(8,Wp-8); wy=rng.randint(8,Hp-8)
        blob(d, wx, wy, rng.randint(3,8), rng.randint(2,6), (80,200,60,70))
    # UI纹路: 符文边框 + 希腊回纹 — 死灵法阵
    overlay_pattern(img, "pattern_greek_key.png", cx, int(Hp*0.48), int(Wp*0.24), int(Hp*0.10), (80,200,60), alpha=50)
    overlay_pattern_rect(img, "border_rune.png", int(Wp*0.10), int(Hp*0.10), int(Wp*0.80), int(Hp*0.80), (100,220,80), alpha=30)
    save(img, W, H, path)


def gen_void(path):
    """5x5 — 虚空行者: 水母形"""
    W, H = 5, 5
    img = canvas(W, H, (6, 3, 12, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.45), 170, 45, (10,0,30,0), (60,18,130,160))
    d = ImageDraw.Draw(img)
    body = (55, 20, 100, 252)
    dark = (30, 10, 60, 248)
    glow_c = (180, 80, 255, 250)
    # bell dome (jellyfish cap)
    blob(d, cx, int(Hp*0.28), int(Wp*0.38), int(Hp*0.24), body, bumps=8, bump_size=0.14)
    blob(d, cx, int(Hp*0.26), int(Wp*0.28), int(Hp*0.18), dark, bumps=6, bump_size=0.10)
    # face on bell
    eye(d, cx-int(Wp*0.10), int(Hp*0.24), 8, glow_c, (100,40,180,255))
    eye(d, cx+int(Wp*0.10), int(Hp*0.24), 8, glow_c, (100,40,180,255))
    # inner mouth glow
    blob(d, cx, int(Hp*0.34), int(Wp*0.08), int(Hp*0.04), (80,30,140,200))
    # trailing tentacles
    for i in range(7):
        start_x = cx - int(Wp*0.28) + i*int(Wp*0.095)
        pts = []
        for j in range(10):
            t = j/9
            px2 = start_x + math.sin(t*math.pi*3 + i*0.5) * 12
            py2 = int(Hp*0.46) + t*int(Hp*0.48)
            py2 = min(Hp-2, py2)
            pts.append((px2, py2))
        for j in range(len(pts)-1):
            w = max(1, int(4*(1-j/len(pts))))
            col_a = max(60, int(200*(1-j/len(pts))))
            d.line([pts[j],pts[j+1]], fill=(70,30,120,col_a), width=w)
    # bioluminescent dots
    for _ in range(14):
        fx=rng.randint(8,Wp-8); fy=rng.randint(int(Hp*0.15),Hp-8)
        r2=rng.randint(2,5)
        d.ellipse([fx-r2,fy-r2,fx+r2,fy+r2], fill=(160,80,240,120))
    # UI纹路: 旋涡纹 — 虚空次元裂痕
    overlay_pattern(img, "pattern_spiral.png", cx, int(Hp*0.28), int(Wp*0.22), int(Hp*0.18), (120,60,200), alpha=50)
    overlay_pattern_rect(img, "divider_wave.png", int(Wp*0.06), int(Hp*0.50), int(Wp*0.88), 16, (160,80,240), alpha=40)
    save(img, W, H, path)


def gen_eagle(path):
    """8x4 — 风暴巨鹰: 展翅猛禽"""
    W, H = 8, 4
    img = canvas(W, H, (6, 8, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 240, 55, (10,12,25,0), (80,90,160,150))
    d = ImageDraw.Draw(img)
    body = (100, 105, 118, 252)
    dark = (55, 58, 68, 248)
    white = (210, 220, 235, 245)
    storm = (200, 220, 255, 235)
    # massive wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.10),int(Hp*0.42)),
               (cx+s*int(Wp*0.49),int(Hp*0.04)),
               (cx+s*int(Wp*0.49),int(Hp*0.55)),
               (cx+s*int(Wp*0.18),int(Hp*0.60))]
        d.polygon(pts, fill=dark)
        for k in range(5):
            t=(k+1)/6
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t)
            fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            tip_x=max(2,min(Wp-2,fx+s*14)); tip_y=max(2,fy-10)
            d.polygon([(fx-4,fy),(fx+4,fy),(tip_x,tip_y)], fill=body)
    # body
    blob(d, cx, int(Hp*0.52), int(Wp*0.14), int(Hp*0.25), body, bumps=6, bump_size=0.10)
    blob(d, cx, int(Hp*0.48), int(Wp*0.10), int(Hp*0.18), dark, bumps=5, bump_size=0.08)
    # white chest
    blob(d, cx, int(Hp*0.55), int(Wp*0.08), int(Hp*0.12), white, bumps=4, bump_size=0.08)
    # head
    hcx, hcy = cx, int(Hp*0.22)
    hrx, hry = int(Wp*0.08), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, white, bumps=5, bump_size=0.10)
    # fierce brow
    d.polygon([(hcx-int(hrx*0.80),hcy-int(hry*0.25)),
               (hcx+int(hrx*0.80),hcy-int(hry*0.25)),
               (hcx+int(hrx*0.55),hcy-int(hry*0.50)),
               (hcx-int(hrx*0.55),hcy-int(hry*0.50))], fill=dark)
    # eyes
    ey = hcy - int(hry*0.05)
    eye(d, hcx-int(hrx*0.40), ey, 5, storm, (30,35,60,255))
    eye(d, hcx+int(hrx*0.40), ey, 5, storm, (30,35,60,255))
    # hooked beak
    by = hcy + int(hry*0.25)
    d.polygon([(hcx-int(hrx*0.30),by),(hcx+int(hrx*0.30),by),
               (hcx,by+int(hry*0.55))], fill=(180,160,60,250))
    # tail
    for i in range(4):
        tx = cx + (i-1.5)*int(Wp*0.03)
        d.polygon([(int(tx)-4,int(Hp*0.72)),(int(tx)+4,int(Hp*0.72)),(int(tx),min(Hp-2,int(Hp*0.94)))], fill=dark)
    # storm lightning
    for _ in range(8):
        lx=rng.randint(int(Wp*0.08),int(Wp*0.92)); ly=rng.randint(int(Hp*0.15),int(Hp*0.85))
        for _ in range(2):
            d.line([(lx,ly),(lx+rng.randint(-16,16),ly+rng.randint(-10,10))], fill=storm, width=1)
    # UI纹路: 藤蔓花纹 — 风暴羽翼纹
    overlay_pattern(img, "pattern_vine.png", cx, int(Hp*0.42), int(Wp*0.30), int(Hp*0.18), (100,140,180), alpha=40)
    overlay_pattern_rect(img, "pattern_zigzag.png", int(Wp*0.06), int(Hp*0.65), int(Wp*0.88), 32, (140,180,220), alpha=35)
    save(img, W, H, path)


def gen_chaos(path):
    """7x5 — 混沌领主: 三头蛇形"""
    W, H = 7, 5
    img = canvas(W, H, (14, 4, 6, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.6), 220, 55, (40,5,5,0), (160,20,30,160))
    d = ImageDraw.Draw(img)
    body = (80, 18, 22, 252)
    dark = (40, 8, 10, 248)
    fire = (255, 40, 60, 240)
    scale = (100, 25, 30, 130)
    # coiled body mass
    blob(d, cx, int(Hp*0.70), int(Wp*0.38), int(Hp*0.22), body, bumps=9, bump_size=0.16)
    blob(d, cx, int(Hp*0.66), int(Wp*0.28), int(Hp*0.16), dark, bumps=7, bump_size=0.12)
    # three necks + heads
    heads = [(int(Wp*0.20),int(Hp*0.12), int(Wp*0.25),int(Hp*0.45)),
             (int(Wp*0.50),int(Hp*0.08), int(Wp*0.50),int(Hp*0.42)),
             (int(Wp*0.80),int(Hp*0.12), int(Wp*0.75),int(Hp*0.45))]
    head_r = int(Wp*0.08)
    for (hx, hy, nx, ny) in heads:
        d.polygon([(nx-12,ny),(nx+12,ny),(hx+8,hy+head_r),(hx-8,hy+head_r)], fill=dark)
        blob(d, hx, hy, head_r, int(Hp*0.10), body, bumps=5, bump_size=0.10)
        blob(d, hx, hy+int(Hp*0.05), int(head_r*0.75), int(Hp*0.06), (95,22,26,250), bumps=4, bump_size=0.06)
        eye(d, hx-int(head_r*0.40), hy-int(Hp*0.02), 5, fire, (80,12,15,255))
        eye(d, hx+int(head_r*0.40), hy-int(Hp*0.02), 5, fire, (80,12,15,255))
        my = hy + int(Hp*0.08)
        d.line([(hx-int(head_r*0.55),my),(hx+int(head_r*0.55),my)], fill=(25,5,6,220), width=2)
        teeth_row(d, hx-int(head_r*0.45), my-4, hx+int(head_r*0.45), 3, 5, 4, (210,180,170,240))
    # legs/tail
    for s in [-1, 1]:
        lx = cx + s*int(Wp*0.30)
        blob(d, lx, int(Hp*0.88), int(Wp*0.06), int(Hp*0.08), dark, bumps=4, bump_size=0.14)
    # scales
    for _ in range(35):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.40),int(Hp*0.88))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=scale,width=2)
    # chaos fire
    for _ in range(12):
        fx=rng.randint(8,Wp-8); fy=rng.randint(8,Hp-8)
        blob(d, fx, fy, rng.randint(3,8), rng.randint(2,6), (255,60,40,70))
    # UI纹路: 龙鳞纹 + 凯尔特结 — 混沌纹
    overlay_pattern(img, "pattern_scale.png", cx, int(Hp*0.70), int(Wp*0.36), int(Hp*0.20), (100,25,30), alpha=45)
    overlay_pattern(img, "pattern_celtic.png", int(Wp*0.50), int(Hp*0.30), int(Wp*0.12), int(Hp*0.10), (255,40,60), alpha=40)
    save(img, W, H, path)


def gen_enddragon(path):
    """8x5 — 终焉之龙: 古龙完全体"""
    W, H = 8, 5
    img = canvas(W, H, (14, 10, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    Wp, Hp = W*CELL, H*CELL
    glow(img, cx, int(Hp*0.5), 260, 65, (50,35,0,0), (180,140,20,165))
    d = ImageDraw.Draw(img)
    body = (120, 90, 25, 252)
    dark = (65, 48, 12, 248)
    gold = (255, 220, 100, 240)
    fire = (255, 160, 30, 220)
    # massive wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.16),int(Hp*0.38)),
               (cx+s*int(Wp*0.49),int(Hp*0.04)),
               (cx+s*int(Wp*0.49),int(Hp*0.60)),
               (cx+s*int(Wp*0.22),int(Hp*0.58))]
        d.polygon(pts, fill=(90,65,15,218))
        for k in range(5):
            t=(k+1)/6
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t)
            fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=(110,80,20,160), width=2)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.24), int(Hp*0.26), body, bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.56), int(Wp*0.18), int(Hp*0.18), dark, bumps=5, bump_size=0.08)
    # belly
    blob(d, cx, int(Hp*0.62), int(Wp*0.14), int(Hp*0.14), (140,105,30,220), bumps=4, bump_size=0.06)
    # neck
    d.polygon([(cx-int(Wp*0.05),int(Hp*0.38)),(cx+int(Wp*0.05),int(Hp*0.38)),
               (cx+int(Wp*0.04),int(Hp*0.18)),(cx-int(Wp*0.04),int(Hp*0.18))], fill=body)
    # head
    hcx, hcy = cx, int(Hp*0.12)
    hrx, hry = int(Wp*0.10), int(Hp*0.12)
    blob(d, hcx, hcy, hrx, hry, body, bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.15), int(hrx*0.75), int(hry*0.45), (140,105,30,250), bumps=4, bump_size=0.06)
    # crown horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.58)
        tip_x = bx + s*18
        d.polygon([(bx-5,hcy-hry+4),(bx+5,hcy-hry+4),(tip_x,max(2,hcy-hry-30))], fill=gold)
    d.polygon([(hcx-4,hcy-hry+2),(hcx+4,hcy-hry+2),(hcx,max(2,hcy-hry-20))], fill=gold)
    # eyes
    ey = hcy - int(hry*0.10)
    eye(d, hcx-int(hrx*0.40), ey, 7, gold, (50,35,5,255))
    eye(d, hcx+int(hrx*0.40), ey, 7, gold, (50,35,5,255))
    # mouth + teeth
    my = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.55),my),(hcx+int(hrx*0.55),my)], fill=(35,22,5,220), width=3)
    teeth_row(d, hcx-int(hrx*0.45), my-6, hcx+int(hrx*0.45), 5, 7, 6, (230,215,180,240))
    # fire breath
    fire_y0 = my + 4
    fire_y1 = int(Hp*0.35)
    if fire_y0 < fire_y1:
        d.polygon([(hcx-12,fire_y0),(hcx+12,fire_y0),(hcx+20,fire_y1),(hcx,fire_y1-6),(hcx-20,fire_y1)],
                  fill=(255,130,15,195))
        d.polygon([(hcx-6,fire_y0),(hcx+6,fire_y0),(hcx+10,fire_y1-2),(hcx,fire_y1-8),(hcx-10,fire_y1-2)],
                  fill=(255,210,60,195))
    # legs
    for s in [-1, 1]:
        lx = cx + s*int(Wp*0.16)
        d.line([(lx,int(Hp*0.76)),(lx+s*int(Wp*0.04),int(Hp*0.94))], fill=dark, width=5)
        blob(d, lx+s*int(Wp*0.04), int(Hp*0.94), 10, 6, body, bumps=4, bump_size=0.18)
    # tail
    d.line([(cx,int(Hp*0.78)),(cx-int(Wp*0.08),int(Hp*0.88)),
            (cx-int(Wp*0.14),int(Hp*0.94))], fill=dark, width=5, joint="curve")
    # scales
    for _ in range(50):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.20),int(Hp*0.85))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=(160,120,30,100),width=2)
    # UI纹路: 龙鳞纹 + 符文边框 + 华丽分割线 — 终焉古龙全套装饰
    overlay_pattern(img, "pattern_scale.png", cx, int(Hp*0.58), int(Wp*0.22), int(Hp*0.24), (180,140,30), alpha=50)
    overlay_pattern_rect(img, "border_rune.png", int(Wp*0.06), int(Hp*0.06), int(Wp*0.88), int(Hp*0.88), (255,220,100), alpha=30)
    overlay_pattern_rect(img, "divider_ornate.png", int(Wp*0.12), int(Hp*0.38), int(Wp*0.76), 24, (255,200,60), alpha=35)
    save(img, W, H, path)


# ── 生成主函数 ───────────────────────────────────

BOSSES = {
    "gargoyle": (gen_gargoyle, 5, 4),
    "spider":   (gen_spider,   5, 4),
    "serpent":  (gen_serpent,   6, 4),
    "giant":    (gen_giant,     7, 5),
    "demon":    (gen_demon,     6, 5),
    "witch":    (gen_witch,     5, 5),
    "wyvern":   (gen_wyvern,    7, 4),
    "kraken":   (gen_kraken,    6, 5),
    "golem":    (gen_golem,     5, 5),
    "wolf":     (gen_wolf,      6, 5),
    "titan":    (gen_titan,     7, 5),
    "mushroom": (gen_mushroom,  5, 5),
    "crystal":  (gen_crystal,   5, 5),
    "assassin": (gen_assassin,  5, 5),
    "phoenix":  (gen_phoenix,   7, 5),
    "lich":     (gen_lich,      6, 5),
    "void":     (gen_void,      5, 5),
    "eagle":    (gen_eagle,     8, 4),
    "chaos":    (gen_chaos,     7, 5),
    "enddragon":(gen_enddragon, 8, 5),
}

def gen_boss():
    print("Generating 20 boss sprites (organic silhouette style)...")
    for name, (func, cols, rows) in BOSSES.items():
        path = os.path.join(OUT, f"boss_{name}.png")
        func(path)
    print(f"Done! {len(BOSSES)} bosses generated.")

if __name__ == "__main__":
    gen_boss()
