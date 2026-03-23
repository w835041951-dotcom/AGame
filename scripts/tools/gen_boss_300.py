"""
Boss 像素风精灵生成器 v7  —  300种Boss (20模板 × 15色彩主题)
生成 300 个独特 Boss PNG + 更新 LevelData.gd
用法: python gen_boss_300.py
"""
import os, math, random
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
CORE_DIR = os.path.join(os.path.dirname(__file__), "..", "core")
os.makedirs(OUT, exist_ok=True)

CELL = 64
rng = random.Random(42)

# ════════════════════════════════════════════════════════════
#  通用绘图工具
# ════════════════════════════════════════════════════════════

def canvas(wc, hc, bg):
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

def _glow_r(Wp, Hp):
    m = max(Wp, Hp)
    return int(m * 0.48), int(m * 0.13)

def _ca(col, a):
    """Return color tuple with overridden alpha."""
    return (col[0], col[1], col[2], a)

def _bright(col, amt=30):
    """Return brighter version of color."""
    return (min(255, col[0]+amt), min(255, col[1]+amt), min(255, col[2]+amt), col[3] if len(col)>3 else 255)

# ════════════════════════════════════════════════════════════
#  20 个参数化 Boss 模板
#  pal keys: bg, glow_out, glow_in, body, dark, eye, pupil,
#            teeth, accent, feature
# ════════════════════════════════════════════════════════════

def gen_gargoyle(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.55), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.12),int(Hp*0.35)),(cx+s*int(Wp*0.48),int(Hp*0.08)),
               (cx+s*int(Wp*0.48),int(Hp*0.55)),(cx+s*int(Wp*0.20),int(Hp*0.60))]
        d.polygon(pts, fill=pal["accent"])
        for k in range(1,4):
            t=k/4; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=_ca(pal["accent"],180), width=2)
    # body
    blob(d, cx, int(Hp*0.55), int(Wp*0.28), int(Hp*0.28), pal["body"], bumps=7, bump_size=0.14)
    blob(d, cx, int(Hp*0.50), int(Wp*0.20), int(Hp*0.20), pal["dark"], bumps=5, bump_size=0.10)
    # head
    hcx, hcy = cx, int(Hp*0.22); hrx, hry = int(Wp*0.20), int(Hp*0.18)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.12)
    # horns
    for s in [-1,1]:
        ox = s*int(hrx*0.6)
        d.polygon([(hcx+ox-5,hcy-hry+6),(hcx+ox+5,hcy-hry+6),(hcx+ox,max(2,hcy-hry-18))], fill=pal["dark"])
    # eyes
    ey = hcy - int(hry*0.08)
    eye(d, hcx-int(hrx*0.38), ey, 8, pal["eye"], pal["pupil"])
    eye(d, hcx+int(hrx*0.38), ey, 8, pal["eye"], pal["pupil"])
    # mouth
    my = hcy + int(hry*0.45)
    d.arc([hcx-int(hrx*0.45),my-8,hcx+int(hrx*0.45),my+8], 0,180, fill=pal["dark"], width=3)
    teeth_row(d, hcx-int(hrx*0.35), my-6, hcx+int(hrx*0.35), 4, 6, 6, pal["teeth"])
    # tail
    tail_pts = [(cx,int(Hp*0.78)),(cx-int(Wp*0.05),int(Hp*0.88)),(cx+int(Wp*0.02),int(Hp*0.95))]
    for i in range(len(tail_pts)-1):
        d.line([tail_pts[i], tail_pts[i+1]], fill=pal["dark"], width=4)
    # cracks
    for _ in range(8):
        crx=rng.randint(int(Wp*0.15),int(Wp*0.85)); cry=rng.randint(int(Hp*0.30),int(Hp*0.80))
        d.line([(crx,cry),(crx+rng.randint(-14,14),cry+rng.randint(6,16))], fill=_ca(pal["dark"],180), width=2)
    save(img, W, H, path)


def gen_spider(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    leg_c = _ca(pal["body"], 230)
    # 8 legs
    for ang in [155,135,200,220,25,45,340,320]:
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
    blob(d, cx, int(Hp*0.62), int(Wp*0.26), int(Hp*0.22), pal["body"], bumps=8, bump_size=0.16)
    blob(d, cx, int(Hp*0.60), int(Wp*0.18), int(Hp*0.15), pal["dark"], bumps=6, bump_size=0.10)
    # cephalothorax
    blob(d, cx, int(Hp*0.35), int(Wp*0.20), int(Hp*0.18), pal["body"], bumps=6, bump_size=0.12)
    # 6 eyes
    for ox, oy, r in [(-12,-6,7),(12,-6,7),(-8,4,5),(8,4,5),(-16,0,4),(16,0,4)]:
        eye(d, cx+ox, int(Hp*0.30)+oy, r, pal["eye"], pal["pupil"])
    # fangs
    for s in [-1, 1]:
        fx = cx + s*int(Wp*0.06)
        d.polygon([(fx-3,int(Hp*0.42)),(fx+3,int(Hp*0.42)),(fx,int(Hp*0.52))], fill=pal["teeth"])
    # abdomen pattern
    for i in range(4):
        py = int(Hp*0.55) + i*int(Hp*0.05)
        blob(d, cx, py, int(Wp*0.06)-i*2, 4, _ca(pal["accent"],120))
    save(img, W, H, path)


def gen_serpent(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # S-curve body segments
    spine = [(int(Wp*0.82),int(Hp*0.15)),(int(Wp*0.65),int(Hp*0.25)),
             (int(Wp*0.45),int(Hp*0.35)),(int(Wp*0.30),int(Hp*0.50)),
             (int(Wp*0.20),int(Hp*0.65)),(int(Wp*0.35),int(Hp*0.78)),
             (int(Wp*0.55),int(Hp*0.85)),(int(Wp*0.70),int(Hp*0.90))]
    for i, (sx, sy) in enumerate(spine):
        r = max(12, 30 - i*2)
        blob(d, sx, sy, r+8, r, pal["body"], bumps=6, bump_size=0.12)
    for i, (sx, sy) in enumerate(spine):
        r = max(8, 22 - i*2)
        blob(d, sx, sy, r+4, r, pal["dark"], bumps=5, bump_size=0.08)
    # head
    hcx, hcy = int(Wp*0.82), int(Hp*0.15)
    hrx, hry = int(Wp*0.14), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.10)
    eye(d, hcx-int(hrx*0.40), hcy-int(hry*0.15), 7, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.40), hcy-int(hry*0.15), 7, pal["feature"], pal["pupil"])
    my = hcy + int(hry*0.50)
    d.line([(hcx-int(hrx*0.55),my),(hcx+int(hrx*0.55),my)], fill=_ca(pal["dark"],220), width=3)
    teeth_row(d, hcx-int(hrx*0.45), my-6, hcx+int(hrx*0.45), 4, 6, 5, pal["teeth"])
    # lava glow between segments
    for i in range(len(spine)-1):
        mx = (spine[i][0]+spine[i+1][0])//2; my2 = (spine[i][1]+spine[i+1][1])//2
        blob(d, mx, my2, 8, 6, pal["feature"], bumps=4, bump_size=0.20)
    # tail tip
    tx, ty = spine[-1]
    d.polygon([(tx,ty-6),(tx+18,ty),(tx,ty+6)], fill=pal["dark"])
    # scales
    for _ in range(35):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.10),int(Hp*0.92))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=_ca(pal["body"],110),width=2)
    save(img, W, H, path)


def gen_giant(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    bone = _bright(pal["body"], 40)
    # ribcage
    blob(d, cx, int(Hp*0.55), int(Wp*0.28), int(Hp*0.26), pal["dark"], bumps=7, bump_size=0.12)
    for i in range(5):
        ry = int(Hp*0.42) + i*int(Hp*0.06)
        rw = int(Wp*0.24) - abs(i-2)*int(Wp*0.03)
        d.arc([cx-rw,ry-6,cx+rw,ry+6], 0, 180, fill=bone, width=3)
    # shoulders + arms
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.28), int(Hp*0.32), int(Wp*0.10), int(Hp*0.08), bone, bumps=5, bump_size=0.14)
        ax = cx+s*int(Wp*0.36)
        d.line([(cx+s*int(Wp*0.28),int(Hp*0.36)),(ax,int(Hp*0.62))], fill=bone, width=6)
        blob(d, ax, int(Hp*0.64), 12, 10, bone, bumps=5, bump_size=0.20)
    # pelvis + legs
    blob(d, cx, int(Hp*0.72), int(Wp*0.16), int(Hp*0.08), pal["dark"], bumps=5, bump_size=0.10)
    for s in [-1, 1]:
        lx = cx + s*int(Wp*0.12)
        d.line([(lx,int(Hp*0.76)),(lx+s*int(Wp*0.04),int(Hp*0.94))], fill=bone, width=5)
    # skull
    hcx, hcy = cx, int(Hp*0.16); hrx, hry = int(Wp*0.16), int(Hp*0.15)
    blob(d, hcx, hcy, hrx, hry, bone, bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.25), int(hrx*0.75), int(hry*0.55), pal["dark"], bumps=4, bump_size=0.06)
    # eye sockets
    ey = hcy - int(hry*0.05)
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.35)
        d.ellipse([ex-8,ey-6,ex+8,ey+6], fill=_ca(pal["dark"],240))
        eye(d, ex, ey, 5, pal["eye"], pal["pupil"])
    # jaw
    jy = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.45),jy),(hcx+int(hrx*0.45),jy)], fill=_ca(pal["dark"],220), width=3)
    teeth_row(d, hcx-int(hrx*0.38), jy-6, hcx+int(hrx*0.38), 5, 7, 6, pal["teeth"])
    save(img, W, H, path)


def gen_demon(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.18),int(Hp*0.35)),(cx+s*int(Wp*0.48),int(Hp*0.06)),
               (cx+s*int(Wp*0.48),int(Hp*0.58)),(cx+s*int(Wp*0.22),int(Hp*0.55))]
        d.polygon(pts, fill=pal["accent"])
        for k in range(1,4):
            t=k/4; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=_ca(pal["accent"],160), width=2)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.30), int(Hp*0.28), pal["body"], bumps=7, bump_size=0.14)
    blob(d, cx, int(Hp*0.54), int(Wp*0.22), int(Hp*0.20), pal["dark"], bumps=5, bump_size=0.10)
    # legs
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.16), int(Hp*0.84), int(Wp*0.08), int(Hp*0.12), pal["dark"], bumps=5, bump_size=0.14)
    # head
    hcx, hcy = cx, int(Hp*0.20); hrx, hry = int(Wp*0.18), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.12)
    # horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.6); tip_x = bx + s*16
        d.polygon([(bx-5,hcy-hry+5),(bx+5,hcy-hry+5),(tip_x,max(2,hcy-hry-28))], fill=pal["dark"])
    # eyes
    ey = hcy - int(hry*0.05)
    eye(d, hcx-int(hrx*0.38), ey, 9, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.38), ey, 9, pal["feature"], pal["pupil"])
    # mouth
    my = hcy + int(hry*0.50)
    d.arc([hcx-int(hrx*0.50),my-10,hcx+int(hrx*0.50),my+10], 0,180, fill=_ca(pal["dark"],220), width=4)
    teeth_row(d, hcx-int(hrx*0.40), my-7, hcx+int(hrx*0.40), 5, 8, 7, pal["teeth"])
    # fire aura
    for _ in range(15):
        fx=rng.randint(int(Wp*0.10),int(Wp*0.90)); fy=rng.randint(int(Hp*0.20),int(Hp*0.85))
        blob(d, fx, fy, rng.randint(4,10), rng.randint(3,8), _ca(pal["feature"],100))
    save(img, W, H, path)


def gen_witch(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # robe
    robe_pts = [(cx-int(Wp*0.44),int(Hp*0.92)),(cx+int(Wp*0.44),int(Hp*0.92)),
                (cx+int(Wp*0.28),int(Hp*0.55)),(cx+int(Wp*0.18),int(Hp*0.28)),
                (cx-int(Wp*0.18),int(Hp*0.28)),(cx-int(Wp*0.28),int(Hp*0.55))]
    d.polygon(robe_pts, fill=pal["dark"])
    blob(d, cx, int(Hp*0.58), int(Wp*0.26), int(Hp*0.26), pal["body"], bumps=6, bump_size=0.08)
    # head
    hcx, hcy = cx, int(Hp*0.18); hrx, hry = int(Wp*0.22), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.10)
    # ear tufts
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.55),hcy-hry+6),(hcx+s*int(hrx*0.70),hcy-hry+4),
                   (hcx+s*int(hrx*0.45),max(2,hcy-hry-22))], fill=pal["dark"])
    # eyes
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.36); ey = hcy - int(hry*0.05)
        d.ellipse([ex-12,ey-10,ex+12,ey+10], fill=pal["dark"])
        eye(d, ex, ey, 9, pal["feature"], pal["pupil"])
    # beak
    by = hcy + int(hry*0.40)
    d.polygon([(hcx-8,by-4),(hcx+8,by-4),(hcx,by+10)], fill=_bright(pal["body"],20))
    # staff
    sx = cx - int(Wp*0.30)
    d.line([(sx,int(Hp*0.30)),(sx,int(Hp*0.88))], fill=_ca(pal["dark"],230), width=4)
    for i in range(3):
        cy2 = int(Hp*0.30) - i*14
        d.polygon([(sx-6,cy2),(sx+6,cy2),(sx,max(2,cy2-16))], fill=pal["feature"])
    # particles
    for _ in range(12):
        fx=rng.randint(6,Wp-6); fy=rng.randint(6,Hp-6)
        blob(d, fx, fy, rng.randint(3,7), rng.randint(2,5), _ca(pal["feature"],80))
    save(img, W, H, path)


def gen_wyvern(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.10),int(Hp*0.40)),(cx+s*int(Wp*0.48),int(Hp*0.05)),
               (cx+s*int(Wp*0.48),int(Hp*0.60)),(cx+s*int(Wp*0.16),int(Hp*0.56))]
        d.polygon(pts, fill=_ca(pal["dark"],215))
        for k in range(1,5):
            t=k/5; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=_ca(pal["dark"],160), width=2)
    # body
    blob(d, cx, int(Hp*0.52), int(Wp*0.18), int(Hp*0.25), pal["body"], bumps=6, bump_size=0.12)
    # neck
    d.polygon([(cx-int(Wp*0.05),int(Hp*0.35)),(cx+int(Wp*0.05),int(Hp*0.35)),
               (cx+int(Wp*0.04),int(Hp*0.18)),(cx-int(Wp*0.04),int(Hp*0.18))], fill=pal["body"])
    # head
    hcx, hcy = cx, int(Hp*0.12); hrx, hry = int(Wp*0.10), int(Hp*0.11)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=5, bump_size=0.10)
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.55),hcy-hry+4),(hcx+s*int(hrx*0.65),hcy-hry+2),
                   (hcx+s*int(hrx*0.40)+s*10,max(2,hcy-hry-16))], fill=pal["dark"])
    eye(d, hcx-int(hrx*0.40), hcy, 5, pal["eye"], pal["pupil"])
    eye(d, hcx+int(hrx*0.40), hcy, 5, pal["eye"], pal["pupil"])
    my = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.50),my),(hcx+int(hrx*0.50),my)], fill=_ca(pal["dark"],220), width=2)
    teeth_row(d, hcx-int(hrx*0.40), my-5, hcx+int(hrx*0.40), 3, 5, 5, pal["teeth"])
    # tail
    tail_pts = [(cx,int(Hp*0.72)),(cx-int(Wp*0.06),int(Hp*0.85)),(cx-int(Wp*0.10),int(Hp*0.94))]
    for i in range(len(tail_pts)-1):
        d.line([tail_pts[i],tail_pts[i+1]], fill=pal["dark"], width=max(2,5-i*2))
    # scales
    for _ in range(30):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.20),int(Hp*0.80))
        d.arc([sx-4,sy-2,sx+4,sy+2],180,360,fill=_ca(pal["body"],110),width=2)
    save(img, W, H, path)


def gen_kraken(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.45), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    inner = _bright(pal["body"], 15)
    # mantle
    mantle_pts = [(cx,max(2,int(Hp*0.04))),(cx+int(Wp*0.26),int(Hp*0.18)),
                  (cx+int(Wp*0.28),int(Hp*0.48)),(cx-int(Wp*0.28),int(Hp*0.48)),
                  (cx-int(Wp*0.26),int(Hp*0.18))]
    d.polygon(mantle_pts, fill=pal["body"])
    d.polygon([(cx,max(2,int(Hp*0.07))),(cx+int(Wp*0.20),int(Hp*0.20)),
               (cx+int(Wp*0.22),int(Hp*0.44)),(cx-int(Wp*0.22),int(Hp*0.44)),
               (cx-int(Wp*0.20),int(Hp*0.20))], fill=inner)
    # eyes
    ey = int(Hp*0.28)
    eye(d, cx-int(Wp*0.12), ey, 10, pal["eye"], pal["pupil"])
    eye(d, cx+int(Wp*0.12), ey, 10, pal["eye"], pal["pupil"])
    d.arc([cx-int(Wp*0.12),int(Hp*0.38)-8,cx+int(Wp*0.12),int(Hp*0.38)+8], 0,180, fill=pal["dark"], width=3)
    # tentacles
    base_y = int(Hp*0.50)
    for i in range(8):
        ang = 200 + i*20; rad = math.radians(ang)
        length = int(min(Wp,Hp)*0.42)
        ex = max(4,min(Wp-4, cx+int(math.cos(rad)*length)))
        ey2 = max(base_y,min(Hp-4, base_y+int(abs(math.sin(rad))*length)))
        pts = []
        for j in range(9):
            t=j/8; px2=cx+(ex-cx)*t; py2=base_y+(ey2-base_y)*t
            perp_x=-(ey2-base_y); perp_y=ex-cx; ln=math.hypot(perp_x,perp_y) or 1
            wave=math.sin(t*math.pi*2.5)*12*(1-t)*(1 if i%2==0 else -1)
            pts.append((px2+perp_x/ln*wave, py2+perp_y/ln*wave))
        for j in range(len(pts)-1):
            w=max(1,int(7*(1-j/len(pts))))
            col_a = max(60, int(200*(1-j/len(pts))))
            d.line([pts[j],pts[j+1]], fill=_ca(pal["accent"],col_a), width=w)
            if j%2==0:
                mx=int((pts[j][0]+pts[j+1][0])/2); my2=int((pts[j][1]+pts[j+1][1])/2)
                sr=max(2,w//2)
                d.ellipse([mx-sr,my2-sr,mx+sr,my2+sr], fill=pal["accent"])
    save(img, W, H, path)


def gen_golem(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.55), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # shell
    blob(d, cx, int(Hp*0.55), int(Wp*0.40), int(Hp*0.30), pal["body"], bumps=8, bump_size=0.14)
    blob(d, cx, int(Hp*0.52), int(Wp*0.30), int(Hp*0.22), pal["dark"], bumps=6, bump_size=0.10)
    # plates
    for i in range(4):
        a = math.radians(-30 + i*40)
        px2 = cx + int(math.cos(a)*int(Wp*0.22)); py2 = int(Hp*0.52) + int(math.sin(a)*int(Hp*0.14))
        blob(d, px2, py2, 14, 12, pal["accent"], bumps=5, bump_size=0.12)
    # head
    hcx, hcy = cx, int(Hp*0.22); hrx, hry = int(Wp*0.18), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.12)
    d.polygon([(hcx-int(hrx*0.60),hcy-int(hry*0.15)),(hcx+int(hrx*0.60),hcy-int(hry*0.15)),
               (hcx+int(hrx*0.50),hcy-int(hry*0.40)),(hcx-int(hrx*0.50),hcy-int(hry*0.40))], fill=pal["dark"])
    ey = hcy + int(hry*0.05)
    eye(d, hcx-int(hrx*0.35), ey, 7, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.35), ey, 7, pal["feature"], pal["pupil"])
    # zigzag mouth
    my = hcy + int(hry*0.55)
    for i in range(6):
        t=i/5
        d.line([(hcx-int(hrx*0.45)+int(hrx*0.90*t),my+(4 if i%2==0 else -4)),
                (hcx-int(hrx*0.45)+int(hrx*0.90*(t+0.16)),my+(-4 if i%2==0 else 4))], fill=_ca(pal["dark"],220), width=2)
    # legs
    for s in [-1, 1]:
        for oy in [0, int(Hp*0.22)]:
            lx = cx + s*int(Wp*0.36); ly = int(Hp*0.50) + oy
            blob(d, lx, ly, int(Wp*0.08), int(Hp*0.08), pal["body"], bumps=5, bump_size=0.16)
    # moss
    for _ in range(10):
        mx=rng.randint(int(Wp*0.12),int(Wp*0.88)); my2=rng.randint(int(Hp*0.30),int(Hp*0.80))
        blob(d, mx, my2, rng.randint(4,9), rng.randint(3,7), _ca(pal["feature"],130))
    save(img, W, H, path)


def gen_wolf(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # body
    blob(d, cx+int(Wp*0.05), int(Hp*0.50), int(Wp*0.32), int(Hp*0.22), pal["body"], bumps=8, bump_size=0.14)
    blob(d, cx+int(Wp*0.05), int(Hp*0.48), int(Wp*0.24), int(Hp*0.16), pal["dark"], bumps=6, bump_size=0.10)
    # mane
    blob(d, cx-int(Wp*0.06), int(Hp*0.34), int(Wp*0.18), int(Hp*0.16), pal["body"], bumps=9, bump_size=0.18)
    # head
    hcx = cx - int(Wp*0.14); hcy = int(Hp*0.22)
    hrx, hry = int(Wp*0.14), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.12)
    # snout
    snout_x = hcx - int(hrx*0.40)
    blob(d, snout_x, hcy+int(hry*0.20), int(hrx*0.50), int(hry*0.40), _bright(pal["body"],15), bumps=4, bump_size=0.08)
    # ears
    for s in [-1, 1]:
        d.polygon([(hcx+s*int(hrx*0.35),hcy-hry+4),
                   (hcx+s*int(hrx*0.55),max(2,hcy-hry-18)),
                   (hcx+s*int(hrx*0.20),hcy-hry+2)], fill=pal["dark"])
    # eyes
    eye(d, hcx-int(hrx*0.15), hcy-int(hry*0.10), 7, pal["eye"], pal["pupil"])
    eye(d, hcx+int(hrx*0.25), hcy-int(hry*0.10), 7, pal["eye"], pal["pupil"])
    # mouth
    my = hcy + int(hry*0.50)
    d.line([(snout_x-int(hrx*0.30),my),(hcx+int(hrx*0.10),my)], fill=_ca(pal["dark"],220), width=3)
    teeth_row(d, snout_x-int(hrx*0.20), my-5, hcx, 4, 6, 5, pal["teeth"])
    # legs
    for i, (lx, ly) in enumerate([(cx-int(Wp*0.18),int(Hp*0.72)),(cx+int(Wp*0.08),int(Hp*0.74)),
                                   (cx+int(Wp*0.22),int(Hp*0.70)),(cx-int(Wp*0.08),int(Hp*0.78))]):
        d.line([(lx,ly),(lx+(4 if i<2 else -4),int(Hp*0.94))], fill=pal["dark"], width=4)
    # tail
    d.line([(cx+int(Wp*0.30),int(Hp*0.42)),(cx+int(Wp*0.42),int(Hp*0.28)),
            (cx+int(Wp*0.44),int(Hp*0.22))], fill=pal["body"], width=5, joint="curve")
    # blood drip
    for _ in range(8):
        bx=rng.randint(int(Wp*0.10),int(Wp*0.90)); by=rng.randint(int(Hp*0.50),int(Hp*0.92))
        d.line([(bx,by),(bx,by+rng.randint(6,14))], fill=_ca(pal["feature"],120), width=2)
    save(img, W, H, path)


def gen_titan(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    bright = _bright(pal["accent"], 30)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.36), int(Hp*0.28), pal["body"], bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.54), int(Wp*0.26), int(Hp*0.20), pal["dark"], bumps=5, bump_size=0.08)
    # energy core
    blob(d, cx, int(Hp*0.52), 22, 22, bright, bumps=7, bump_size=0.15)
    blob(d, cx, int(Hp*0.52), 12, 12, pal["feature"], bumps=4, bump_size=0.10)
    # claws
    for s in [-1, 1]:
        ax = cx + s*int(Wp*0.32)
        blob(d, ax, int(Hp*0.40), int(Wp*0.10), int(Hp*0.12), pal["body"], bumps=5, bump_size=0.12)
        claw_x = cx + s*int(Wp*0.44)
        d.polygon([(ax,int(Hp*0.36)),(claw_x,int(Hp*0.26)),(claw_x,int(Hp*0.40))], fill=bright)
        d.polygon([(ax,int(Hp*0.44)),(claw_x,int(Hp*0.48)),(claw_x,int(Hp*0.38))], fill=pal["body"])
    # legs
    for s in [-1, 1]:
        for i in range(2):
            lx = cx + s*int(Wp*0.18) + s*i*int(Wp*0.10)
            blob(d, lx, int(Hp*0.84), int(Wp*0.06), int(Hp*0.10), pal["dark"], bumps=4, bump_size=0.12)
    # head
    hcx, hcy = cx, int(Hp*0.20); hrx, hry = int(Wp*0.16), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.18), int(hrx*0.78), int(hry*0.68), pal["dark"], bumps=5, bump_size=0.08)
    # horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.50)
        d.polygon([(bx-4,hcy-hry+3),(bx+4,hcy-hry+3),(bx+s*12,max(2,hcy-hry-26))], fill=pal["feature"])
    # visor
    ey = hcy - int(hry*0.08)
    d.ellipse([hcx-int(hrx*0.50),ey-5,hcx+int(hrx*0.50),ey+5], fill=bright)
    eye(d, hcx-int(hrx*0.30), ey, 5, pal["feature"], (255,255,255,255))
    eye(d, hcx+int(hrx*0.30), ey, 5, pal["feature"], (255,255,255,255))
    # lightning
    for _ in range(12):
        lx=rng.randint(int(Wp*0.12),int(Wp*0.88)); ly=rng.randint(int(Hp*0.25),int(Hp*0.80))
        for _ in range(3):
            d.line([(lx,ly),(lx+rng.randint(-18,18),ly+rng.randint(-12,12))], fill=pal["feature"], width=1)
    save(img, W, H, path)


def gen_mushroom(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    stem_c = _bright(pal["accent"], 40)
    # stem
    d.polygon([(cx-int(Wp*0.12),int(Hp*0.40)),(cx+int(Wp*0.12),int(Hp*0.40)),
               (cx+int(Wp*0.16),int(Hp*0.88)),(cx-int(Wp*0.16),int(Hp*0.88))], fill=stem_c)
    blob(d, cx, int(Hp*0.88), int(Wp*0.20), int(Hp*0.08), _bright(pal["accent"],20), bumps=6, bump_size=0.12)
    # cap
    blob(d, cx, int(Hp*0.28), int(Wp*0.42), int(Hp*0.24), pal["body"], bumps=8, bump_size=0.16)
    blob(d, cx, int(Hp*0.26), int(Wp*0.34), int(Hp*0.18), pal["dark"], bumps=6, bump_size=0.12)
    # spots
    for _ in range(8):
        sx=cx+rng.randint(-int(Wp*0.30),int(Wp*0.30))
        sy=int(Hp*0.20)+rng.randint(-int(Hp*0.12),int(Hp*0.12))
        sr=rng.randint(6,14)
        blob(d, sx, sy, sr, int(sr*0.8), pal["feature"], bumps=4, bump_size=0.15)
    # face
    ey = int(Hp*0.50)
    eye(d, cx-int(Wp*0.06), ey, 7, pal["feature"], pal["pupil"])
    eye(d, cx+int(Wp*0.06), ey, 7, pal["feature"], pal["pupil"])
    my = int(Hp*0.62)
    d.arc([cx-int(Wp*0.08),my-8,cx+int(Wp*0.08),my+8], 0,180, fill=pal["dark"], width=3)
    # spores
    for _ in range(18):
        fx=rng.randint(6,Wp-6); fy=rng.randint(6,Hp-6)
        blob(d, fx, fy, rng.randint(2,6), rng.randint(2,4), _ca(pal["feature"],90))
    save(img, W, H, path)


def gen_crystal(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # crystal spikes
    for i in range(5):
        ang = math.radians(-90 + i*72)
        tip_x = max(4,min(Wp-4, cx + int(math.cos(ang)*int(Wp*0.44))))
        tip_y = max(4,min(Hp-4, int(Hp*0.48) + int(math.sin(ang)*int(Hp*0.42))))
        base_w = int(Wp*0.08); perp = ang + math.pi/2
        bx1 = cx+int(math.cos(perp)*base_w); by1 = int(Hp*0.48)+int(math.sin(perp)*base_w)
        bx2 = cx-int(math.cos(perp)*base_w); by2 = int(Hp*0.48)-int(math.sin(perp)*base_w)
        d.polygon([(bx1,by1),(tip_x,tip_y),(bx2,by2)], fill=pal["body"])
        d.line([(cx,int(Hp*0.48)),(tip_x,tip_y)], fill=pal["accent"], width=2)
    # core
    blob(d, cx, int(Hp*0.48), int(Wp*0.18), int(Hp*0.18), pal["dark"], bumps=6, bump_size=0.10)
    blob(d, cx, int(Hp*0.48), int(Wp*0.12), int(Hp*0.12), pal["body"], bumps=5, bump_size=0.08)
    eye(d, cx, int(Hp*0.46), 12, pal["feature"], pal["pupil"])
    # tip eyes
    for i in range(5):
        ang = math.radians(-90 + i*72)
        tx = max(8,min(Wp-8, cx+int(math.cos(ang)*int(Wp*0.32))))
        ty = max(8,min(Hp-8, int(Hp*0.48)+int(math.sin(ang)*int(Hp*0.30))))
        eye(d, tx, ty, 4, pal["feature"], pal["pupil"])
    # shards
    for _ in range(8):
        sx=rng.randint(8,Wp-8); sy=rng.randint(8,Hp-8); sh=rng.randint(8,16)
        d.polygon([(sx-3,sy),(sx,sy-sh),(sx+3,sy)], fill=pal["accent"])
    save(img, W, H, path)


def gen_assassin(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.55), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.28), int(Hp*0.18), pal["body"], bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.56), int(Wp*0.20), int(Hp*0.12), pal["dark"], bumps=5, bump_size=0.08)
    # tail
    tail_pts = [(cx,int(Hp*0.44)),(cx+int(Wp*0.05),int(Hp*0.32)),
                (cx+int(Wp*0.02),int(Hp*0.18)),(cx-int(Wp*0.06),int(Hp*0.10)),
                (cx-int(Wp*0.10),int(Hp*0.06))]
    for i in range(len(tail_pts)-1):
        d.line([tail_pts[i],tail_pts[i+1]], fill=pal["body"], width=max(2,8-i*2))
    sx, sy = tail_pts[-1]
    d.polygon([(sx-4,sy+2),(sx+4,sy+2),(sx,max(2,sy-12))], fill=pal["feature"])
    # claws
    for s in [-1, 1]:
        ax = cx + s*int(Wp*0.30); ay = int(Hp*0.45)
        d.line([(cx+s*int(Wp*0.18),int(Hp*0.52)),(ax,ay)], fill=pal["body"], width=5)
        d.polygon([(ax,ay-6),(ax+s*14,ay-10),(ax+s*8,ay)], fill=pal["dark"])
        d.polygon([(ax,ay+6),(ax+s*14,ay+10),(ax+s*8,ay)], fill=pal["dark"])
    # legs
    for s in [-1, 1]:
        for i in range(3):
            lx = cx + s*int(Wp*0.16) + s*i*int(Wp*0.06)
            ly = int(Hp*0.62) + i*int(Hp*0.06)
            d.line([(lx,ly),(lx+s*int(Wp*0.12),ly+int(Hp*0.14))], fill=pal["dark"], width=3)
    # head
    hcx, hcy = cx, int(Hp*0.52)
    blob(d, hcx, hcy, int(Wp*0.12), int(Hp*0.08), pal["body"], bumps=5, bump_size=0.10)
    eye(d, hcx-8, hcy-2, 5, pal["feature"], pal["pupil"])
    eye(d, hcx+8, hcy-2, 5, pal["feature"], pal["pupil"])
    # wisps
    for _ in range(10):
        wx=rng.randint(8,Wp-8); wy=rng.randint(8,Hp-8)
        blob(d, wx, wy, rng.randint(4,10), rng.randint(3,7), _ca(pal["feature"],70))
    save(img, W, H, path)


def gen_phoenix(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    wing_c = _ca(pal["body"], 218)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.14),int(Hp*0.42)),(cx+s*int(Wp*0.48),int(Hp*0.06)),
               (cx+s*int(Wp*0.48),int(Hp*0.55)),(cx+s*int(Wp*0.22),int(Hp*0.58))]
        d.polygon(pts, fill=wing_c)
        for k in range(4):
            t=(k+1)/5
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            tip_x=max(2,min(Wp-2,fx+s*16)); tip_y=max(2,min(Hp-2,fy-12))
            d.polygon([(fx-5,fy),(fx+5,fy),(tip_x,tip_y)], fill=pal["feature"])
    # body
    blob(d, cx, int(Hp*0.54), int(Wp*0.16), int(Hp*0.22), pal["body"], bumps=6, bump_size=0.10)
    # tail
    for i in range(5):
        tx = cx + (i-2)*int(Wp*0.06)
        d.polygon([(tx-6,int(Hp*0.73)),(tx+6,int(Hp*0.73)),(tx,min(Hp-2,int(Hp*0.95)))], fill=pal["accent"])
    # head
    hcx, hcy = cx, int(Hp*0.24); hrx, hry = int(Wp*0.10), int(Hp*0.12)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=5, bump_size=0.10)
    # crest
    for ox, ch in [(-int(hrx*0.50),18),(0,26),(int(hrx*0.50),18)]:
        d.polygon([(hcx+ox-4,hcy-hry+4),(hcx+ox+4,hcy-hry+4),(hcx+ox,max(2,hcy-hry-ch))], fill=pal["feature"])
    eye(d, hcx-int(hrx*0.40), hcy, 5, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.40), hcy, 5, pal["feature"], pal["pupil"])
    # beak
    by = hcy + int(hry*0.35)
    d.polygon([(hcx-int(hrx*0.28),by),(hcx+int(hrx*0.28),by),(hcx,by+int(hry*0.50))], fill=pal["accent"])
    # flame particles
    for _ in range(16):
        fx=rng.randint(8,Wp-8); fy=rng.randint(8,Hp-8)
        blob(d, fx, fy, rng.randint(3,8), rng.randint(2,6), _ca(pal["feature"],80))
    save(img, W, H, path)


def gen_lich(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    bone = pal["teeth"]
    # robe
    robe_pts = [(cx-int(Wp*0.44),int(Hp*0.94)),(cx+int(Wp*0.44),int(Hp*0.94)),
                (cx+int(Wp*0.30),int(Hp*0.58)),(cx+int(Wp*0.20),int(Hp*0.26)),
                (cx-int(Wp*0.20),int(Hp*0.26)),(cx-int(Wp*0.30),int(Hp*0.58))]
    d.polygon(robe_pts, fill=pal["dark"])
    blob(d, cx, int(Hp*0.58), int(Wp*0.24), int(Hp*0.24), pal["body"], bumps=6, bump_size=0.08)
    # skull
    hcx, hcy = cx, int(Hp*0.16); hrx, hry = int(Wp*0.16), int(Hp*0.14)
    blob(d, hcx, hcy, hrx, hry, bone, bumps=6, bump_size=0.08)
    blob(d, hcx, hcy+int(hry*0.30), int(hrx*0.72), int(hry*0.48), pal["dark"], bumps=4, bump_size=0.06)
    # crown
    for ox, sh in [(-int(hrx*0.50),14),(-int(hrx*0.20),20),(0,26),(int(hrx*0.20),20),(int(hrx*0.50),14)]:
        d.polygon([(hcx+ox-4,hcy-hry+4),(hcx+ox+4,hcy-hry+4),(hcx+ox,max(2,hcy-hry-sh))], fill=pal["feature"])
    # eye sockets
    ey = hcy - int(hry*0.05)
    for s in [-1, 1]:
        ex = hcx + s*int(hrx*0.36)
        d.ellipse([ex-7,ey-5,ex+7,ey+5], fill=_ca(pal["dark"],240))
        eye(d, ex, ey, 5, pal["feature"], pal["pupil"])
    # jaw
    jy = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.40),jy),(hcx+int(hrx*0.40),jy)], fill=_ca(pal["dark"],220), width=3)
    # soul orb
    orb_cy = int(Hp*0.48)
    blob(d, cx, orb_cy, 18, 18, _ca(pal["feature"],200), bumps=8, bump_size=0.15)
    blob(d, cx, orb_cy, 10, 10, pal["feature"], bumps=4, bump_size=0.10)
    # hands
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.26), int(Hp*0.52), 10, 8, bone, bumps=5, bump_size=0.20)
    # wisps
    for _ in range(10):
        wx=rng.randint(8,Wp-8); wy=rng.randint(8,Hp-8)
        blob(d, wx, wy, rng.randint(3,8), rng.randint(2,6), _ca(pal["feature"],70))
    save(img, W, H, path)


def gen_void(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.45), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # bell dome
    blob(d, cx, int(Hp*0.28), int(Wp*0.38), int(Hp*0.24), pal["body"], bumps=8, bump_size=0.14)
    blob(d, cx, int(Hp*0.26), int(Wp*0.28), int(Hp*0.18), pal["dark"], bumps=6, bump_size=0.10)
    eye(d, cx-int(Wp*0.10), int(Hp*0.24), 8, pal["eye"], pal["pupil"])
    eye(d, cx+int(Wp*0.10), int(Hp*0.24), 8, pal["eye"], pal["pupil"])
    blob(d, cx, int(Hp*0.34), int(Wp*0.08), int(Hp*0.04), _ca(pal["dark"],200))
    # tentacles
    for i in range(7):
        start_x = cx - int(Wp*0.28) + i*int(Wp*0.095)
        pts = []
        for j in range(10):
            t = j/9
            px2 = start_x + math.sin(t*math.pi*3 + i*0.5) * 12
            py2 = min(Hp-2, int(Hp*0.46) + t*int(Hp*0.48))
            pts.append((px2, py2))
        for j in range(len(pts)-1):
            w = max(1, int(4*(1-j/len(pts))))
            col_a = max(60, int(200*(1-j/len(pts))))
            d.line([pts[j],pts[j+1]], fill=_ca(pal["accent"],col_a), width=w)
    # dots
    for _ in range(14):
        fx=rng.randint(8,Wp-8); fy=rng.randint(int(Hp*0.15),Hp-8)
        r2=rng.randint(2,5)
        d.ellipse([fx-r2,fy-r2,fx+r2,fy+r2], fill=_ca(pal["feature"],120))
    save(img, W, H, path)


def gen_eagle(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.10),int(Hp*0.42)),(cx+s*int(Wp*0.49),int(Hp*0.04)),
               (cx+s*int(Wp*0.49),int(Hp*0.55)),(cx+s*int(Wp*0.18),int(Hp*0.60))]
        d.polygon(pts, fill=pal["dark"])
        for k in range(5):
            t=(k+1)/6
            fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            tip_x=max(2,min(Wp-2,fx+s*14)); tip_y=max(2,fy-10)
            d.polygon([(fx-4,fy),(fx+4,fy),(tip_x,tip_y)], fill=pal["body"])
    # body
    blob(d, cx, int(Hp*0.52), int(Wp*0.14), int(Hp*0.25), pal["body"], bumps=6, bump_size=0.10)
    blob(d, cx, int(Hp*0.48), int(Wp*0.10), int(Hp*0.18), pal["dark"], bumps=5, bump_size=0.08)
    blob(d, cx, int(Hp*0.55), int(Wp*0.08), int(Hp*0.12), pal["accent"], bumps=4, bump_size=0.08)
    # head
    hcx, hcy = cx, int(Hp*0.22); hrx, hry = int(Wp*0.08), int(Hp*0.16)
    blob(d, hcx, hcy, hrx, hry, pal["accent"], bumps=5, bump_size=0.10)
    d.polygon([(hcx-int(hrx*0.80),hcy-int(hry*0.25)),(hcx+int(hrx*0.80),hcy-int(hry*0.25)),
               (hcx+int(hrx*0.55),hcy-int(hry*0.50)),(hcx-int(hrx*0.55),hcy-int(hry*0.50))], fill=pal["dark"])
    eye(d, hcx-int(hrx*0.40), hcy-int(hry*0.05), 5, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.40), hcy-int(hry*0.05), 5, pal["feature"], pal["pupil"])
    by = hcy + int(hry*0.25)
    d.polygon([(hcx-int(hrx*0.30),by),(hcx+int(hrx*0.30),by),(hcx,by+int(hry*0.55))], fill=pal["accent"])
    # tail
    for i in range(4):
        tx = cx + (i-1.5)*int(Wp*0.03)
        d.polygon([(int(tx)-4,int(Hp*0.72)),(int(tx)+4,int(Hp*0.72)),(int(tx),min(Hp-2,int(Hp*0.94)))], fill=pal["dark"])
    # lightning
    for _ in range(8):
        lx=rng.randint(int(Wp*0.08),int(Wp*0.92)); ly=rng.randint(int(Hp*0.15),int(Hp*0.85))
        for _ in range(2):
            d.line([(lx,ly),(lx+rng.randint(-16,16),ly+rng.randint(-10,10))], fill=pal["feature"], width=1)
    save(img, W, H, path)


def gen_chaos(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.6), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # coiled body
    blob(d, cx, int(Hp*0.70), int(Wp*0.38), int(Hp*0.22), pal["body"], bumps=9, bump_size=0.16)
    blob(d, cx, int(Hp*0.66), int(Wp*0.28), int(Hp*0.16), pal["dark"], bumps=7, bump_size=0.12)
    # three heads
    heads = [(int(Wp*0.20),int(Hp*0.12),int(Wp*0.25),int(Hp*0.45)),
             (int(Wp*0.50),int(Hp*0.08),int(Wp*0.50),int(Hp*0.42)),
             (int(Wp*0.80),int(Hp*0.12),int(Wp*0.75),int(Hp*0.45))]
    head_r = int(Wp*0.08)
    for (hx, hy, nx, ny) in heads:
        d.polygon([(nx-12,ny),(nx+12,ny),(hx+8,hy+head_r),(hx-8,hy+head_r)], fill=pal["dark"])
        blob(d, hx, hy, head_r, int(Hp*0.10), pal["body"], bumps=5, bump_size=0.10)
        blob(d, hx, hy+int(Hp*0.05), int(head_r*0.75), int(Hp*0.06), _bright(pal["body"],15), bumps=4, bump_size=0.06)
        eye(d, hx-int(head_r*0.40), hy-int(Hp*0.02), 5, pal["feature"], pal["pupil"])
        eye(d, hx+int(head_r*0.40), hy-int(Hp*0.02), 5, pal["feature"], pal["pupil"])
        my = hy + int(Hp*0.08)
        d.line([(hx-int(head_r*0.55),my),(hx+int(head_r*0.55),my)], fill=_ca(pal["dark"],220), width=2)
        teeth_row(d, hx-int(head_r*0.45), my-4, hx+int(head_r*0.45), 3, 5, 4, pal["teeth"])
    # legs
    for s in [-1, 1]:
        blob(d, cx+s*int(Wp*0.30), int(Hp*0.88), int(Wp*0.06), int(Hp*0.08), pal["dark"], bumps=4, bump_size=0.14)
    # scales
    for _ in range(35):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.40),int(Hp*0.88))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=_ca(pal["body"],130),width=2)
    # fire
    for _ in range(12):
        fx=rng.randint(8,Wp-8); fy=rng.randint(8,Hp-8)
        blob(d, fx, fy, rng.randint(3,8), rng.randint(2,6), _ca(pal["feature"],70))
    save(img, W, H, path)


def gen_enddragon(path, W, H, pal):
    img = canvas(W, H, pal["bg"]); d = ImageDraw.Draw(img)
    Wp, Hp = W*CELL, H*CELL; cx = Wp//2
    ro, ri = _glow_r(Wp, Hp)
    glow(img, cx, int(Hp*0.5), ro, ri, pal["glow_out"], pal["glow_in"])
    d = ImageDraw.Draw(img)
    # wings
    for s in [-1, 1]:
        pts = [(cx+s*int(Wp*0.16),int(Hp*0.38)),(cx+s*int(Wp*0.49),int(Hp*0.04)),
               (cx+s*int(Wp*0.49),int(Hp*0.60)),(cx+s*int(Wp*0.22),int(Hp*0.58))]
        d.polygon(pts, fill=_ca(pal["dark"],218))
        for k in range(5):
            t=(k+1)/6; fx=int(pts[1][0]+(pts[2][0]-pts[1][0])*t); fy=int(pts[1][1]+(pts[2][1]-pts[1][1])*t)
            d.line([pts[0],(fx,fy)], fill=_ca(pal["dark"],160), width=2)
    # body
    blob(d, cx, int(Hp*0.58), int(Wp*0.24), int(Hp*0.26), pal["body"], bumps=7, bump_size=0.12)
    blob(d, cx, int(Hp*0.56), int(Wp*0.18), int(Hp*0.18), pal["dark"], bumps=5, bump_size=0.08)
    blob(d, cx, int(Hp*0.62), int(Wp*0.14), int(Hp*0.14), _bright(pal["body"],20), bumps=4, bump_size=0.06)
    # neck
    d.polygon([(cx-int(Wp*0.05),int(Hp*0.38)),(cx+int(Wp*0.05),int(Hp*0.38)),
               (cx+int(Wp*0.04),int(Hp*0.18)),(cx-int(Wp*0.04),int(Hp*0.18))], fill=pal["body"])
    # head
    hcx, hcy = cx, int(Hp*0.12); hrx, hry = int(Wp*0.10), int(Hp*0.12)
    blob(d, hcx, hcy, hrx, hry, pal["body"], bumps=6, bump_size=0.10)
    blob(d, hcx, hcy+int(hry*0.15), int(hrx*0.75), int(hry*0.45), _bright(pal["body"],20), bumps=4, bump_size=0.06)
    # crown horns
    for s in [-1, 1]:
        bx = hcx + s*int(hrx*0.58); tip_x = bx + s*18
        d.polygon([(bx-5,hcy-hry+4),(bx+5,hcy-hry+4),(tip_x,max(2,hcy-hry-30))], fill=pal["feature"])
    d.polygon([(hcx-4,hcy-hry+2),(hcx+4,hcy-hry+2),(hcx,max(2,hcy-hry-20))], fill=pal["feature"])
    # eyes
    ey = hcy - int(hry*0.10)
    eye(d, hcx-int(hrx*0.40), ey, 7, pal["feature"], pal["pupil"])
    eye(d, hcx+int(hrx*0.40), ey, 7, pal["feature"], pal["pupil"])
    # mouth + teeth
    my = hcy + int(hry*0.55)
    d.line([(hcx-int(hrx*0.55),my),(hcx+int(hrx*0.55),my)], fill=_ca(pal["dark"],220), width=3)
    teeth_row(d, hcx-int(hrx*0.45), my-6, hcx+int(hrx*0.45), 5, 7, 6, pal["teeth"])
    # fire breath
    fire_y0 = my + 4; fire_y1 = int(Hp*0.35)
    if fire_y0 < fire_y1:
        d.polygon([(hcx-12,fire_y0),(hcx+12,fire_y0),(hcx+20,fire_y1),(hcx,fire_y1-6),(hcx-20,fire_y1)],
                  fill=_ca(pal["feature"],195))
        d.polygon([(hcx-6,fire_y0),(hcx+6,fire_y0),(hcx+10,fire_y1-2),(hcx,fire_y1-8),(hcx-10,fire_y1-2)],
                  fill=_ca(pal["accent"],195))
    # legs
    for s in [-1, 1]:
        lx = cx + s*int(Wp*0.16)
        d.line([(lx,int(Hp*0.76)),(lx+s*int(Wp*0.04),int(Hp*0.94))], fill=pal["dark"], width=5)
        blob(d, lx+s*int(Wp*0.04), int(Hp*0.94), 10, 6, pal["body"], bumps=4, bump_size=0.18)
    # tail
    d.line([(cx,int(Hp*0.78)),(cx-int(Wp*0.08),int(Hp*0.88)),
            (cx-int(Wp*0.14),int(Hp*0.94))], fill=pal["dark"], width=5, joint="curve")
    # scales
    for _ in range(50):
        sx=rng.randint(int(Wp*0.10),int(Wp*0.90)); sy=rng.randint(int(Hp*0.20),int(Hp*0.85))
        d.arc([sx-5,sy-3,sx+5,sy+3],180,360,fill=_ca(pal["body"],100),width=2)
    save(img, W, H, path)


# ════════════════════════════════════════════════════════════
#  15 色彩主题 + 20 生物模板 + 关卡数据
# ════════════════════════════════════════════════════════════

THEMES = [
    # 0: 暗牢 (stone/grey-green)
    {"key":"dark","cn":"幽暗","loc":"暗牢","sub":"阴冷的石墙间回荡着低沉的呻吟…",
     "color":"Color(0.45,0.50,0.55)",
     "bg":(12,14,16,255),"glow_out":(0,20,0,0),"glow_in":(30,80,50,150),
     "body":(72,78,85,252),"dark":(40,44,50,248),"eye":(60,255,120,255),"pupil":(20,80,40,255),
     "teeth":(180,185,190,240),"accent":(55,60,68,220),"feature":(60,255,120,240)},
    # 1: 冰原 (frost/ice blue)
    {"key":"frost","cn":"极寒","loc":"冰原","sub":"永冻的冰原上寒风呼啸不止…",
     "color":"Color(0.65,0.82,0.95)",
     "bg":(6,10,18,255),"glow_out":(0,15,40,0),"glow_in":(40,100,200,155),
     "body":(90,130,180,252),"dark":(50,70,110,248),"eye":(160,220,255,255),"pupil":(40,80,140,255),
     "teeth":(200,215,230,240),"accent":(70,100,150,220),"feature":(160,220,255,240)},
    # 2: 火域 (inferno/red-orange)
    {"key":"inferno","cn":"灼热","loc":"火域","sub":"脚下的岩浆发出灼热的红光…",
     "color":"Color(0.95,0.45,0.15)",
     "bg":(16,8,4,255),"glow_out":(50,15,0,0),"glow_in":(160,60,8,155),
     "body":(120,55,20,252),"dark":(70,30,10,248),"eye":(255,120,20,255),"pupil":(60,25,5,255),
     "teeth":(220,200,180,240),"accent":(90,35,12,220),"feature":(255,120,20,240)},
    # 3: 深渊 (abyss/dark blue-teal)
    {"key":"abyss","cn":"深渊","loc":"深渊","sub":"黑暗的深渊中传来不祥的低语…",
     "color":"Color(0.12,0.25,0.45)",
     "bg":(3,6,14,255),"glow_out":(0,10,40,0),"glow_in":(10,50,120,155),
     "body":(20,50,95,252),"dark":(12,30,60,248),"eye":(0,210,180,255),"pupil":(0,80,60,255),
     "teeth":(150,170,190,240),"accent":(35,85,130,220),"feature":(0,210,180,240)},
    # 4: 暗域 (shadow/purple-black)
    {"key":"shadow","cn":"暗影","loc":"暗域","sub":"影子在每一个角落蠕动伸展…",
     "color":"Color(0.35,0.15,0.50)",
     "bg":(10,6,16,255),"glow_out":(20,0,30,0),"glow_in":(80,30,120,150),
     "body":(60,45,85,252),"dark":(35,25,50,248),"eye":(200,50,255,255),"pupil":(120,20,160,255),
     "teeth":(180,170,200,240),"accent":(50,35,70,220),"feature":(200,80,255,240)},
    # 5: 密林 (forest/green-gold)
    {"key":"forest","cn":"翡翠","loc":"密林","sub":"翠绿的藤蔓间隐藏着致命危机…",
     "color":"Color(0.25,0.55,0.20)",
     "bg":(8,12,4,255),"glow_out":(10,30,0,0),"glow_in":(45,130,15,150),
     "body":(55,100,35,252),"dark":(30,55,18,248),"eye":(190,200,50,255),"pupil":(50,65,15,255),
     "teeth":(180,190,140,240),"accent":(40,80,25,220),"feature":(190,200,50,240)},
    # 6: 铁城 (iron/steel-electric)
    {"key":"iron","cn":"钢铁","loc":"铁城","sub":"齿轮与蒸汽构成的钢铁迷宫…",
     "color":"Color(0.55,0.58,0.62)",
     "bg":(10,10,12,255),"glow_out":(10,10,20,0),"glow_in":(60,70,120,145),
     "body":(90,95,110,252),"dark":(50,55,65,248),"eye":(130,180,255,255),"pupil":(40,60,120,255),
     "teeth":(190,195,205,240),"accent":(70,75,88,220),"feature":(130,180,255,240)},
    # 7: 天殿 (celestial/white-gold)
    {"key":"celestial","cn":"神圣","loc":"天殿","sub":"圣光普照的殿堂已被黑暗侵蚀…",
     "color":"Color(0.85,0.80,0.55)",
     "bg":(14,12,8,255),"glow_out":(40,35,10,0),"glow_in":(160,140,50,155),
     "body":(180,170,120,252),"dark":(110,100,65,248),"eye":(255,230,100,255),"pupil":(100,85,25,255),
     "teeth":(225,220,200,240),"accent":(140,130,85,220),"feature":(255,230,100,240)},
    # 8: 乱界 (chaos/dark crimson)
    {"key":"chaos","cn":"混沌","loc":"乱界","sub":"混沌的力量扭曲了一切秩序…",
     "color":"Color(0.60,0.08,0.10)",
     "bg":(14,4,6,255),"glow_out":(40,5,5,0),"glow_in":(160,20,30,160),
     "body":(80,18,22,252),"dark":(40,8,10,248),"eye":(255,40,60,255),"pupil":(80,12,15,255),
     "teeth":(210,180,170,240),"accent":(60,12,16,220),"feature":(255,60,30,240)},
    # 9: 遗迹 (ancient/brown-amber)
    {"key":"ancient","cn":"远古","loc":"遗迹","sub":"远古文明的废墟中回荡着亡灵的哀叹…",
     "color":"Color(0.65,0.55,0.30)",
     "bg":(12,10,6,255),"glow_out":(30,20,5,0),"glow_in":(120,90,30,150),
     "body":(110,85,45,252),"dark":(65,50,25,248),"eye":(220,180,60,255),"pupil":(80,60,15,255),
     "teeth":(200,190,160,240),"accent":(85,65,35,220),"feature":(220,180,60,240)},
    # 10: 瘟沼 (plague/sick green)
    {"key":"plague","cn":"瘟疫","loc":"瘟沼","sub":"有毒的瘴气弥漫在腐朽的沼泽…",
     "color":"Color(0.40,0.55,0.15)",
     "bg":(8,10,4,255),"glow_out":(15,25,0,0),"glow_in":(60,100,10,150),
     "body":(80,105,30,252),"dark":(45,60,15,248),"eye":(180,220,40,255),"pupil":(60,80,10,255),
     "teeth":(170,185,120,240),"accent":(60,82,22,220),"feature":(180,220,40,240)},
    # 11: 雷峰 (thunder/blue-electric)
    {"key":"thunder","cn":"雷霆","loc":"雷峰","sub":"雷电劈裂山巅震耳欲聋…",
     "color":"Color(0.35,0.50,0.75)",
     "bg":(4,4,16,255),"glow_out":(0,0,50,0),"glow_in":(35,70,220,160),
     "body":(40,50,130,252),"dark":(20,25,70,248),"eye":(200,230,255,255),"pupil":(60,80,180,255),
     "teeth":(180,190,220,240),"accent":(30,40,100,220),"feature":(200,230,255,240)},
    # 12: 血原 (blood/dark crimson)
    {"key":"blood","cn":"血月","loc":"血原","sub":"血色月光下弥漫着死亡的气息…",
     "color":"Color(0.55,0.10,0.12)",
     "bg":(14,4,4,255),"glow_out":(40,5,5,0),"glow_in":(140,20,20,155),
     "body":(95,25,22,252),"dark":(50,12,10,248),"eye":(255,50,50,255),"pupil":(80,15,10,255),
     "teeth":(210,190,180,240),"accent":(70,18,16,220),"feature":(255,80,50,240)},
    # 13: 虚隙 (void/black-purple-neon)
    {"key":"void","cn":"虚无","loc":"虚隙","sub":"现实的边界在这里崩塌瓦解…",
     "color":"Color(0.28,0.10,0.35)",
     "bg":(6,3,12,255),"glow_out":(10,0,30,0),"glow_in":(60,18,130,160),
     "body":(55,20,100,252),"dark":(30,10,60,248),"eye":(180,80,255,255),"pupil":(100,40,180,255),
     "teeth":(170,150,200,240),"accent":(42,15,75,220),"feature":(180,80,255,240)},
    # 14: 终焉 (doom/bronze-gold)
    {"key":"doom","cn":"终焉","loc":"终焉","sub":"万物终结之处最终的审判将至…",
     "color":"Color(0.55,0.45,0.15)",
     "bg":(14,10,4,255),"glow_out":(50,35,0,0),"glow_in":(180,140,20,165),
     "body":(120,90,25,252),"dark":(65,48,12,248),"eye":(255,220,100,255),"pupil":(50,35,5,255),
     "teeth":(230,215,180,240),"accent":(90,65,15,220),"feature":(255,200,60,240)},
]

CREATURES = [
    {"key":"gargoyle","cn":"石像鬼","draw":gen_gargoyle,"bw":5,"bh":4},
    {"key":"spider",  "cn":"影蛛",  "draw":gen_spider,  "bw":5,"bh":4},
    {"key":"serpent", "cn":"巨蛇",  "draw":gen_serpent, "bw":6,"bh":4},
    {"key":"giant",   "cn":"骸巨人","draw":gen_giant,   "bw":7,"bh":5},
    {"key":"demon",   "cn":"魔王",  "draw":gen_demon,   "bw":6,"bh":5},
    {"key":"witch",   "cn":"巫师",  "draw":gen_witch,   "bw":5,"bh":5},
    {"key":"wyvern",  "cn":"飞龙",  "draw":gen_wyvern,  "bw":7,"bh":4},
    {"key":"kraken",  "cn":"海魔",  "draw":gen_kraken,  "bw":6,"bh":5},
    {"key":"golem",   "cn":"岩傀",  "draw":gen_golem,   "bw":5,"bh":5},
    {"key":"wolf",    "cn":"狼王",  "draw":gen_wolf,    "bw":6,"bh":5},
    {"key":"titan",   "cn":"泰坦",  "draw":gen_titan,   "bw":7,"bh":5},
    {"key":"mushroom","cn":"菌王",  "draw":gen_mushroom,"bw":5,"bh":5},
    {"key":"crystal", "cn":"晶体",  "draw":gen_crystal, "bw":5,"bh":5},
    {"key":"assassin","cn":"毒蝎",  "draw":gen_assassin,"bw":5,"bh":5},
    {"key":"phoenix", "cn":"凤凰",  "draw":gen_phoenix, "bw":7,"bh":5},
    {"key":"lich",    "cn":"巫妖",  "draw":gen_lich,    "bw":6,"bh":5},
    {"key":"ghost",   "cn":"幽灵",  "draw":gen_void,    "bw":5,"bh":5},
    {"key":"eagle",   "cn":"巨鹰",  "draw":gen_eagle,   "bw":8,"bh":4},
    {"key":"hydra",   "cn":"多头蛇","draw":gen_chaos,   "bw":7,"bh":5},
    {"key":"dragon",  "cn":"古龙",  "draw":gen_enddragon,"bw":8,"bh":5},
]

AREAS = [
    "入口","走廊","密室","祭坛","陵墓",
    "废墟","地窖","深处","圣殿","广场",
    "高塔","迷宫","桥梁","花园","王座",
    "矿道","峡谷","湖畔","洞窟","深渊",
]

# ════════════════════════════════════════════════════════════
#  LevelData.gd 生成
# ════════════════════════════════════════════════════════════

def _lerp(a, b, t):
    return a + (b - a) * t

def write_level_data(bosses):
    lines = []
    lines.append("## 关卡数据 - AutoLoad")
    lines.append("## 300个主题关卡 (15主题 × 20Boss)")
    lines.append("## 每种Boss独立形状、配色、棋盘大小、探索区参数")
    lines.append("")
    lines.append("extends Node")
    lines.append("")
    # BOSS_GRID_SIZE
    lines.append("const BOSS_GRID_SIZE = {")
    for b in bosses:
        lines.append('\t"%s": Vector2i(%d, %d),' % (b["key"], b["cols"], b["rows"]))
    lines.append("}")
    lines.append("")
    # LEVELS
    lines.append("const LEVELS = [")
    for i, b in enumerate(bosses):
        t = i / 299.0
        pcols = round(_lerp(9, 19, t))
        prows = round(_lerp(6, 10, t))
        mcols = round(_lerp(9, 18, t))
        mrows = round(_lerp(5, 7, t))
        bomb  = round(_lerp(6, 22, t))
        clicks= round(_lerp(8, 25, t))
        turn  = round(_lerp(50, 24, t), 1)
        atk   = round(_lerp(3, 14, t))
        move  = round(_lerp(70, 26, t), 1)
        weak  = max(0.05, round(0.35 - 0.30 * t, 2))
        armor = round(0.05 + 0.25 * t, 2)
        absorb= round(0.02 + 0.16 * t, 2)
        normal= round(max(0.01, 1.0 - weak - armor - absorb), 2)
        lines.append("\t{")
        lines.append('\t\t"id": %d, "name": "%s",' % (b["floor"], b["level_name"]))
        lines.append('\t\t"boss_name": "%s", "boss_shape": "%s",' % (b["boss_name"], b["key"]))
        lines.append('\t\t"subtitle": "%s",' % b["subtitle"])
        lines.append('\t\t"color": %s,' % b["color"])
        lines.append('\t\t"tile_weights": { "WEAK": %.2f, "ARMOR": %.2f, "ABSORB": %.2f, "NORMAL": %.2f },' % (weak, armor, absorb, normal))
        lines.append('\t\t"bomb_count": %d, "base_clicks": %d,' % (bomb, clicks))
        lines.append('\t\t"turn_duration": %.1f, "boss_attack": %d, "boss_move_interval": %.1f,' % (turn, atk, move))
        lines.append('\t\t"placement_cols": %d, "placement_rows": %d,' % (pcols, prows))
        lines.append('\t\t"mine_cols": %d, "mine_rows": %d,' % (mcols, mrows))
        lines.append("\t},")
    lines.append("]")
    lines.append("")
    # BOSS_TEXTURE_MAP
    lines.append("const BOSS_TEXTURE_MAP = {")
    for b in bosses:
        lines.append('\t"%s": "%s",' % (b["key"], b["texture"]))
    lines.append("}")
    lines.append("")
    # Query functions
    lines.append("""# ============================================================
#  查询接口  —  300关唯一对应
# ============================================================

func get_level(floor_number: int) -> Dictionary:
\tvar idx = (floor_number - 1) % LEVELS.size()
\treturn LEVELS[idx]

func get_cycle(floor_number: int) -> int:
\treturn (floor_number - 1) / LEVELS.size()

func get_level_name(floor_number: int) -> String:
\treturn get_level(floor_number)["name"]

func get_boss_name(floor_number: int) -> String:
\treturn get_level(floor_number)["boss_name"]

func get_level_subtitle(floor_number: int) -> String:
\treturn get_level(floor_number)["subtitle"]

func get_level_color(floor_number: int) -> Color:
\treturn get_level(floor_number)["color"]

# -- 棋盘大小 --

func get_placement_cols(floor_number: int) -> int:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn level["placement_cols"] + cycle

func get_placement_rows(floor_number: int) -> int:
\treturn get_level(floor_number)["placement_rows"]

func get_mine_cols(floor_number: int) -> int:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn level["mine_cols"] + cycle

func get_mine_rows(floor_number: int) -> int:
\treturn get_level(floor_number)["mine_rows"]

func get_boss_shape(floor_number: int) -> Array:
\tvar key = get_level(floor_number)["boss_shape"]
\tvar sz = BOSS_GRID_SIZE[key]
\tvar arr = []
\tfor y in range(sz.y):
\t\tfor x in range(sz.x):
\t\t\tarr.append(Vector2i(x, y))
\treturn arr

func get_boss_grid_size(floor_number: int) -> Vector2i:
\tvar key = get_level(floor_number)["boss_shape"]
\treturn BOSS_GRID_SIZE[key]

func get_boss_texture_path(floor_number: int) -> String:
\tvar key = get_level(floor_number)["boss_shape"]
\treturn BOSS_TEXTURE_MAP[key]

const BACKGROUND_PATHS: Array = [
\t"res://assets/sprites/bg/bg_stone_prison.png",
\t"res://assets/sprites/bg/bg_bone_chamber.png",
\t"res://assets/sprites/bg/bg_lava_cave.png",
\t"res://assets/sprites/bg/bg_ghost_wreck.png",
\t"res://assets/sprites/bg/bg_crystal_cavern.png",
\t"res://assets/sprites/bg/bg_ancient_ruins.png",
\t"res://assets/sprites/bg/bg_shadow_hall.png",
\t"res://assets/sprites/bg/bg_frost_altar.png",
\t"res://assets/sprites/bg/bg_plague_swamp.png",
\t"res://assets/sprites/bg/bg_mechanical_fort.png",
\t"res://assets/sprites/bg/bg_nightmare_maze.png",
\t"res://assets/sprites/bg/bg_corrupted_temple.png",
\t"res://assets/sprites/bg/bg_void_rift.png",
\t"res://assets/sprites/bg/bg_thunder_peak.png",
\t"res://assets/sprites/bg/bg_shadow_realm.png",
\t"res://assets/sprites/bg/bg_chaos_forge.png",
\t"res://assets/sprites/bg/bg_void_palace.png",
\t"res://assets/sprites/bg/bg_divine_sanctum.png",
\t"res://assets/sprites/bg/bg_abyss_throne.png",
\t"res://assets/sprites/bg/bg_final_sanctum.png",
]

func get_background_texture_path(floor_number: int) -> String:
\tvar idx = ((floor_number - 1) % BACKGROUND_PATHS.size())
\treturn BACKGROUND_PATHS[idx]

func get_cell_size(floor_number: int) -> int:
\tvar p_cols = get_placement_cols(floor_number)
\tvar p_rows = get_placement_rows(floor_number)
\tvar m_cols = get_mine_cols(floor_number)
\tvar m_rows = get_mine_rows(floor_number)
\tvar max_cols = max(p_cols, m_cols)
\tvar size_by_w = int(1760.0 / max_cols)
\tvar size_by_h = int(880.0 / (p_rows + m_rows))
\treturn min(size_by_w, size_by_h)

# -- 难度参数（含周期递增）--

func get_bomb_count(floor_number: int) -> int:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn level["bomb_count"] + cycle * 2

func get_turn_duration(floor_number: int) -> float:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn maxf(level["turn_duration"] - cycle * 3.0, 15.0)

func get_boss_attack(floor_number: int) -> int:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn level["boss_attack"] + cycle * 3

func get_boss_move_interval(floor_number: int) -> float:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn maxf(level["boss_move_interval"] - cycle * 5.0, 18.0)

func get_tile_weights(floor_number: int) -> Dictionary:
\treturn get_level(floor_number)["tile_weights"]

func get_hp_multiplier(floor_number: int) -> float:
\tvar cycle = get_cycle(floor_number)
\treturn 1.0 + cycle * 0.5

func get_max_clicks(floor_number: int) -> int:
\tvar level = get_level(floor_number)
\tvar cycle = get_cycle(floor_number)
\treturn level["base_clicks"] + cycle * 3

func get_level_raw(floor_number: int) -> Dictionary:
\treturn get_level(floor_number)

# -- 故事卡片 --
const STORY_FLOORS: Array = [1, 6, 11, 16, 20]
""")
    path = os.path.join(CORE_DIR, "LevelData.gd")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  wrote LevelData.gd ({len(bosses)} levels)")


# ════════════════════════════════════════════════════════════
#  主生成函数
# ════════════════════════════════════════════════════════════

def gen_all():
    print("Generating 300 boss sprites (20 templates x 15 themes)...")
    bosses = []

    for theme_idx, theme in enumerate(THEMES):
        for creature_idx, creature in enumerate(CREATURES):
            floor_num = theme_idx * 20 + creature_idx + 1

            # Size scaling per theme tier — early themes: smaller, late themes: bigger
            # theme 0-2: -2w -1h, theme 3-4: -1w 0h, theme 5-9: base, theme 10-12: +1w, theme 13-14: +1w +1h
            if theme_idx <= 2:
                dw, dh = -2, -1
            elif theme_idx <= 4:
                dw, dh = -1, 0
            elif theme_idx <= 9:
                dw, dh = 0, 0
            elif theme_idx <= 12:
                dw, dh = 1, 0
            else:
                dw, dh = 1, 1
            bw = max(3, creature["bw"] + dw)
            bh = max(3, creature["bh"] + dh)

            boss_key = "%s_%s" % (theme["key"].upper(), creature["key"].upper())
            fname = "boss_%s_%s.png" % (theme["key"], creature["key"])
            fpath = os.path.join(OUT, fname)

            # Unique seed per boss for variety
            rng.seed(42 + floor_num)
            creature["draw"](fpath, bw, bh, theme)

            bosses.append({
                "floor": floor_num,
                "key": boss_key,
                "cols": bw,
                "rows": bh,
                "boss_name": theme["cn"] + creature["cn"],
                "level_name": theme["loc"] + "\u00b7" + AREAS[creature_idx],
                "subtitle": theme["sub"],
                "color": theme["color"],
                "texture": "res://assets/sprites/boss/" + fname,
            })

    print(f"  Generated {len(bosses)} boss PNGs.")
    write_level_data(bosses)
    print("Done!")


if __name__ == "__main__":
    gen_all()
