"""
generate_boss_sprites.py  — AGame floors 6-20 boss sprite sheets
Rules:
  • ALL face features (eyes, mouth, teeth) are placed INSIDE the body bounds
  • Body fills most of the canvas — large imposing presence
  • Bodies are organic, irregular shapes — NOT rectangular blocks
  • Each boss: unique silhouette, 2-3 color palette, pixel-art style
  • 64px per grid cell, RGBA PNG
"""

import os, math, random
from PIL import Image, ImageDraw

CELL = 64
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites", "boss")
os.makedirs(OUT_DIR, exist_ok=True)
rng = random.Random(42)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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

def grid(img, wc, hc):
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
        tx = x0 + i * gap + gap//4
        if pointy:
            draw.polygon([(tx, y0), (tx+tw, y0), (tx+tw//2, y0+th)], fill=col)
        else:
            draw.rectangle([tx, y0, tx+tw, y0+th], fill=col)

def blob(draw, cx, cy, rx, ry, col, bumps=8, bump_size=0.18):
    """Draw an irregular organic blob shape."""
    pts = []
    for i in range(36):
        a = math.radians(i * 10)
        noise_r = 1.0 + bump_size * math.sin(a * bumps + rng.uniform(0, math.pi))
        px = cx + int(math.cos(a) * rx * noise_r)
        py = cy + int(math.sin(a) * ry * noise_r)
        pts.append((px, py))
    draw.polygon(pts, fill=col)

def save(img, wc, hc, path):
    grid(img, wc, hc)
    noise(img)
    img.save(path)
    print(f"  saved: {path}")

# ---------------------------------------------------------------------------
# Boss generators
# ---------------------------------------------------------------------------

def gen_lich(path):
    """4×4 — purple/bone undead lich."""
    W, H = 4, 4
    img = canvas(W, H, (6, 3, 14, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, cy, 120, 40, (20,0,50,0), (80,30,160,180))

    # Flowing robe — wide organic trapezoid shape
    robe_pts = [
        (cx-int(W_px*0.44), int(H_px*0.90)),
        (cx+int(W_px*0.44), int(H_px*0.90)),
        (cx+int(W_px*0.30), int(H_px*0.55)),
        (cx+int(W_px*0.22), int(H_px*0.22)),
        (cx-int(W_px*0.22), int(H_px*0.22)),
        (cx-int(W_px*0.30), int(H_px*0.55)),
    ]
    d.polygon(robe_pts, fill=(55, 22, 105, 245))
    # Inner robe highlight — organic oval
    blob(d, cx, int(H_px*0.58), int(W_px*0.24), int(H_px*0.28),
         (72, 32, 138, 248), bumps=5, bump_size=0.08)

    # Skull head — organic oval, not circle
    head_cx = cx
    head_cy = int(H_px * 0.16)
    head_rx = int(W_px * 0.22)
    head_ry = int(H_px * 0.17)
    ht = max(2, head_cy - head_ry)
    hb = head_cy + head_ry
    hl = head_cx - head_rx
    hr = head_cx + head_rx
    blob(d, head_cx, head_cy, head_rx, head_ry, (195, 188, 208, 245), bumps=6, bump_size=0.06)
    # Jaw lower portion
    blob(d, head_cx, head_cy + int(head_ry*0.35), int(head_rx*0.80), int(head_ry*0.42),
         (175, 168, 188, 238), bumps=4, bump_size=0.05)

    # Crown spikes — clamped to canvas top
    crown_col = (230, 218, 245, 255)
    for ox, spike_h in [(-int(head_rx*0.6), 18), (-int(head_rx*0.25), 26),
                         (0, 32), (int(head_rx*0.25), 26), (int(head_rx*0.6), 18)]:
        bx = head_cx + ox
        tip_y = max(2, ht - spike_h)
        d.polygon([(bx-5, ht+4),(bx+5, ht+4),(bx, tip_y)], fill=crown_col)

    # Eyes inside skull
    eye_y = max(ht+7, head_cy - int(head_ry*0.05))
    eye_y = min(hb - int(head_ry*0.45), eye_y)
    eye_r = max(4, int(head_rx*0.22))
    eye(d, head_cx-int(head_rx*0.38), eye_y, eye_r, (55,140,255,255), (130,210,255,255))
    eye(d, head_cx+int(head_rx*0.38), eye_y, eye_r, (55,140,255,255), (130,210,255,255))

    # Mouth crack inside jaw
    jaw_center_y = head_cy + int(head_ry*0.65)
    jaw_center_y = min(hb-4, jaw_center_y)
    d.line([(head_cx-int(head_rx*0.35), jaw_center_y),
            (head_cx+int(head_rx*0.35), jaw_center_y)], fill=(30,15,60,220), width=3)

    # Soul orb in chest
    orb_cy = int(H_px*0.50)
    blob(d, cx, orb_cy, 16, 16, (95,55,195,200), bumps=8, bump_size=0.15)
    blob(d, cx, orb_cy, 9, 9, (175,135,255,230), bumps=4, bump_size=0.1)

    # Bony arms — organic extensions from robe
    arm_col = (185,178,200,228)
    for side in [-1, 1]:
        ax0 = cx + side*int(W_px*0.27)
        ay0 = int(H_px*0.42)
        ax1 = max(2, min(W_px-2, cx + side*int(W_px*0.46)))
        ay1 = int(H_px*0.60)
        d.line([(ax0,ay0),(ax1,ay1)], fill=arm_col, width=6)
        blob(d, ax1, ay1+8, 10, 8, arm_col, bumps=5, bump_size=0.2)

    save(img, W, H, path)


def gen_dragon(path):
    """6×5 — crimson/gold dragon, massive organic body."""
    W, H = 6, 5
    img = canvas(W, H, (14, 4, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, cy, 200, 60, (70,8,0,0), (190,55,8,170))

    # Dragon body — large organic blob
    blob(d, cx, int(H_px*0.62), int(W_px*0.42), int(H_px*0.28),
         (155, 22, 12, 252), bumps=7, bump_size=0.12)
    # Belly lighter
    blob(d, cx, int(H_px*0.66), int(W_px*0.28), int(H_px*0.18),
         (175, 38, 20, 220), bumps=5, bump_size=0.06)

    # Neck — tapered polygon
    neck_pts = [
        (cx-int(W_px*0.10), int(H_px*0.42)),
        (cx+int(W_px*0.10), int(H_px*0.42)),
        (cx+int(W_px*0.07), int(H_px*0.22)),
        (cx-int(W_px*0.07), int(H_px*0.22)),
    ]
    d.polygon(neck_pts, fill=(138,18,10,248))

    # Head — organic oval
    head_cx = cx
    head_cy = int(H_px*0.14)
    head_rx = int(W_px*0.17)
    head_ry = int(H_px*0.14)
    ht = max(2, head_cy-head_ry)
    hb = head_cy+head_ry
    hl = head_cx-head_rx
    hr = head_cx+head_rx
    blob(d, head_cx, head_cy, head_rx, head_ry, (168,28,15,252), bumps=6, bump_size=0.08)
    # Snout protrusion — lower half
    snout_y = head_cy + int(head_ry*0.1)
    blob(d, head_cx, (snout_y+hb)//2, int(head_rx*0.78), int((hb-snout_y)//2)+2,
         (182,32,18,250), bumps=4, bump_size=0.06)

    # Horns — clamped above head
    horn_col = (200,155,18,255)
    for hx_off, lean in [(-int(head_rx*0.65),-18),(int(head_rx*0.65),18)]:
        bx = head_cx+hx_off
        tip_x = bx+int(math.sin(math.radians(lean))*28)
        tip_y = max(2, ht-30)
        d.polygon([(bx-6, ht+4),(bx+6, ht+4),(tip_x, tip_y)], fill=horn_col)

    # Eyes inside head — above snout
    eye_y = max(ht+8, head_cy - int(head_ry*0.15))
    eye_y = min(snout_y - 8, eye_y)
    eye_r = max(5, int(head_rx*0.25))
    eye(d, head_cx-int(head_rx*0.42), eye_y, eye_r, (218,155,18,255),(55,18,0,255))
    eye(d, head_cx+int(head_rx*0.42), eye_y, eye_r, (218,155,18,255),(55,18,0,255))

    # Mouth & teeth inside snout
    mouth_y = snout_y + int((hb-snout_y)*0.5)
    mouth_y = min(hb-6, mouth_y)
    d.line([(hl+14,mouth_y),(hr-14,mouth_y)], fill=(30,8,4,220), width=4)
    teeth_row(d, hl+16, mouth_y-8, hr-16, 5, 8, 8, (230,210,190,240), pointy=True)

    # Wings — organic membrane shape
    for side in [-1, 1]:
        wing_pts = [
            (cx+side*int(W_px*0.35), int(H_px*0.48)),
            (cx+side*int(W_px*0.49), int(H_px*0.18)),
            (cx+side*int(W_px*0.49), int(H_px*0.68)),
            (cx+side*int(W_px*0.28), int(H_px*0.62)),
        ]
        d.polygon(wing_pts, fill=(118,15,8,205))
        # Wing ribs
        for k in range(1,4):
            t = k/4
            wx = int(wing_pts[0][0]+(wing_pts[1][0]-wing_pts[0][0])*t)
            wy = int(wing_pts[0][1]+(wing_pts[1][1]-wing_pts[0][1])*t)
            d.line([(wing_pts[0][0],wing_pts[0][1]),(wx,wy)],
                   fill=(155,20,10,160), width=2)

    # Scales
    for _ in range(55):
        sx = int(W_px*0.14)+rng.randint(0,int(W_px*0.72))
        sy = int(H_px*0.42)+rng.randint(0,int(H_px*0.44))
        r2 = rng.randint(4,8)
        d.arc([sx-r2,sy-r2//2,sx+r2,sy+r2//2],180,360,fill=(195,45,18,110),width=2)

    # Fire breath from mouth
    fire_y0 = mouth_y
    fire_y1 = min(H_px-2, int(H_px*0.38))
    if fire_y0 > fire_y1:
        fire_pts = [(head_cx-14,fire_y0),(head_cx+14,fire_y0),
                    (head_cx+22,fire_y1+6),(head_cx,fire_y1),(head_cx-22,fire_y1+6)]
        d.polygon(fire_pts, fill=(255,135,18,195))
        inner_pts = [(head_cx-8,fire_y0),(head_cx+8,fire_y0),
                     (head_cx+10,fire_y1+8),(head_cx,fire_y1+2),(head_cx-10,fire_y1+8)]
        d.polygon(inner_pts, fill=(255,218,75,195))

    save(img, W, H, path)


def gen_colossus(path):
    """5×5 — massive organic stone giant, mossy, no rectangular body."""
    W, H = 5, 5
    img = canvas(W, H, (8, 10, 8, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.6), 160, 50, (0,30,0,0),(20,80,20,140))

    body_col   = (95, 100, 90, 252)
    dark_col   = (65,  72, 60, 245)
    moss_col   = (40, 110, 45, 200)
    crack_col  = (30,  35, 28, 220)

    # Body — not a rectangle, but a massive organic boulder-shape
    # Lower body blob
    blob(d, cx, int(H_px*0.68), int(W_px*0.42), int(H_px*0.28),
         body_col, bumps=7, bump_size=0.14)
    # Upper torso — slightly narrower
    blob(d, cx, int(H_px*0.44), int(W_px*0.36), int(H_px*0.22),
         dark_col, bumps=6, bump_size=0.12)
    # Shoulders — two side blobs
    for side in [-1, 1]:
        blob(d, cx+side*int(W_px*0.32), int(H_px*0.36), int(W_px*0.14), int(H_px*0.12),
             body_col, bumps=5, bump_size=0.18)

    # Head — organic boulder shaped
    head_cx = cx
    head_cy = int(H_px*0.17)
    head_rx = int(W_px*0.22)
    head_ry = int(H_px*0.17)
    ht = max(2, head_cy-head_ry)
    hb = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, body_col, bumps=7, bump_size=0.14)

    # Rocky brow ridges above eyes
    brow_y = head_cy - int(head_ry*0.22)
    for side in [-1, 1]:
        bx = head_cx + side*int(head_rx*0.38)
        d.polygon([(bx-14, brow_y+6),(bx+14, brow_y+6),
                   (bx+side*4, brow_y-8),(bx-side*4, brow_y-4)], fill=dark_col)

    # Eyes inside head, below brow ridges
    ey = max(ht+8, brow_y+4)
    ey = min(hb-int(head_ry*0.4), ey)
    ew = int(head_rx*0.30)
    eye(d, head_cx-int(head_rx*0.38), ey, 9, (40,180,40,255),(10,80,10,255))
    eye(d, head_cx+int(head_rx*0.38), ey, 9, (40,180,40,255),(10,80,10,255))

    # Rocky mouth — jagged crack inside lower head
    mouth_y = hb - int(head_ry*0.28)
    mouth_y = min(hb-4, max(ey+14, mouth_y))
    mouth_pts = []
    mw = int(head_rx*0.56)
    for i in range(8):
        t = i/7
        mx = head_cx-mw + int(2*mw*t)
        my = mouth_y + (4 if i%2==0 else -4)
        mouth_pts.append((mx, my))
    for i in range(len(mouth_pts)-1):
        d.line([mouth_pts[i], mouth_pts[i+1]], fill=crack_col, width=3)

    # Fist — organic rock blob at end of arms
    for side in [-1, 1]:
        arm_tip_x = cx + side*int(W_px*0.42)
        arm_tip_y = int(H_px*0.66)
        blob(d, arm_tip_x, arm_tip_y, int(W_px*0.10), int(H_px*0.09),
             body_col, bumps=6, bump_size=0.20)

    # Tree/vine legs organic shapes
    for side in [-1, 1]:
        lx = cx + side*int(W_px*0.22)
        blob(d, lx, int(H_px*0.87), int(W_px*0.09), int(H_px*0.11),
             dark_col, bumps=5, bump_size=0.16)

    # Cracks + moss
    for _ in range(10):
        crx = rng.randint(int(W_px*0.14), int(W_px*0.86))
        cry = rng.randint(int(H_px*0.24), int(H_px*0.88))
        d.line([(crx,cry),(crx+rng.randint(-18,18), cry+rng.randint(8,22))],
               fill=crack_col, width=2)
        # Moss patch
        mx = rng.randint(int(W_px*0.16), int(W_px*0.84))
        my = rng.randint(int(H_px*0.26), int(H_px*0.86))
        blob(d, mx, my, rng.randint(5,10), rng.randint(4,8), moss_col)

    save(img, W, H, path)


def gen_hydra(path):
    """7×4 — teal/green hydra with 3 organic serpentine necks."""
    W, H = 7, 4
    img = canvas(W, H, (4, 12, 10, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.7), 180, 50, (0,50,40,0),(15,120,90,150))

    body_col  = (25, 100, 75, 250)
    dark_col  = (15,  68, 50, 245)
    scale_col = (35, 130, 95, 130)

    # Main body — large organic coiled mass
    blob(d, cx, int(H_px*0.72), int(W_px*0.42), int(H_px*0.24),
         body_col, bumps=8, bump_size=0.12)
    blob(d, cx, int(H_px*0.60), int(W_px*0.34), int(H_px*0.18),
         dark_col, bumps=6, bump_size=0.10)

    # Three serpentine necks and heads
    heads = [
        (int(W_px*0.20), int(H_px*0.10), int(W_px*0.25), int(H_px*0.48)),
        (int(W_px*0.50), int(H_px*0.06), int(W_px*0.50), int(H_px*0.45)),
        (int(W_px*0.80), int(H_px*0.10), int(W_px*0.75), int(H_px*0.48)),
    ]
    head_rx = int(W_px*0.10)
    head_ry = int(H_px*0.14)

    for (hcxh, hcyh, nbx, nby) in heads:
        # neck as thick tapered poly
        nw_top = 16; nw_bot = 24
        d.polygon([
            (nbx-nw_bot//2, nby), (nbx+nw_bot//2, nby),
            (hcxh+nw_top//2, hcyh+head_ry),
            (hcxh-nw_top//2, hcyh+head_ry)
        ], fill=dark_col)

        # Head blob
        ht = max(2, hcyh-head_ry)
        hb = hcyh+head_ry
        blob(d, hcxh, hcyh, head_rx, head_ry, body_col, bumps=5, bump_size=0.10)
        # Snout protrusion lower half
        snout_y = hcyh + int(head_ry*0.08)
        blob(d, hcxh, (snout_y+hb)//2, int(head_rx*0.76), (hb-snout_y)//2+2,
             (30,115,85,250), bumps=4, bump_size=0.06)

        # Eyes inside upper head
        ey2 = max(ht+6, hcyh - int(head_ry*0.18))
        ey2 = min(snout_y-6, ey2)
        er2 = max(4, int(head_rx*0.30))
        eye(d, hcxh-int(head_rx*0.40), ey2, er2, (255,200,0,255),(60,40,0,255))
        eye(d, hcxh+int(head_rx*0.40), ey2, er2, (255,200,0,255),(60,40,0,255))

        # Mouth inside lower snout
        my2 = snout_y + int((hb-snout_y)*0.5)
        my2 = min(hb-4, my2)
        d.line([(hcxh-int(head_rx*0.65),my2),(hcxh+int(head_rx*0.65),my2)],
               fill=(8,35,25,220), width=3)
        teeth_row(d, hcxh-int(head_rx*0.60), my2-6, hcxh+int(head_rx*0.60),
                  3, 6, 6, (230,225,215,240), pointy=True)

    # Scales
    for _ in range(50):
        sx = int(W_px*0.14)+rng.randint(0,int(W_px*0.72))
        sy = int(H_px*0.50)+rng.randint(0,int(H_px*0.44))
        r2 = rng.randint(3,7)
        d.arc([sx-r2,sy-r2//2,sx+r2,sy+r2//2],180,360,fill=scale_col,width=2)

    save(img, W, H, path)


def gen_phoenix(path):
    """5×6 — orange/gold phoenix, spread wings, face inside flame-crown head."""
    W, H = 5, 6
    img = canvas(W, H, (16, 6, 2, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 190, 50, (80,15,0,0),(220,100,10,170))

    body_col    = (210, 80, 10, 250)
    wing_col    = (190, 55,  5, 215)
    feather_col = (240,160, 20, 220)
    tail_col    = (255,200, 30, 210)

    # Body — elongated organic teardrop
    blob(d, cx, int(H_px*0.54), int(W_px*0.22), int(H_px*0.22),
         body_col, bumps=6, bump_size=0.10)

    # Wings — organic swept shapes
    for side in [-1, 1]:
        wing_pts = [
            (cx+side*int(W_px*0.18), int(H_px*0.42)),
            (cx+side*int(W_px*0.49), int(H_px*0.06)),
            (cx+side*int(W_px*0.49), int(H_px*0.55)),
            (cx+side*int(W_px*0.26), int(H_px*0.64)),
        ]
        d.polygon(wing_pts, fill=wing_col)
        # Feather tips
        for k in range(4):
            t = (k+1)/5
            fx = int(wing_pts[1][0]+(wing_pts[2][0]-wing_pts[1][0])*t)
            fy = int(wing_pts[1][1]+(wing_pts[2][1]-wing_pts[1][1])*t)
            tip_x = max(2, min(W_px-2, fx+side*16))
            tip_y = max(2, min(H_px-2, fy-12))
            d.polygon([(fx-5,fy),(fx+5,fy),(tip_x,tip_y)], fill=feather_col)

    # Tail feathers at bottom
    tail_y0 = int(H_px*0.73)
    tail_y1 = min(H_px-2, int(H_px*0.97))
    for i in range(5):
        tx = cx+(i-2)*int(W_px*0.07)
        d.polygon([(tx-7,tail_y0),(tx+7,tail_y0),(tx,tail_y1)], fill=tail_col)

    # Head — organic flame-teardrop
    head_cx = cx
    head_cy = int(H_px*0.24)
    head_rx = int(W_px*0.13)
    head_ry = int(H_px*0.12)
    ht = max(2, head_cy-head_ry)
    hb = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, body_col, bumps=5, bump_size=0.10)

    # Flame crest — inside canvas, starting from ht
    for i, (ox, ch) in enumerate([(-int(head_rx*0.5),18),(0,25),(int(head_rx*0.5),18)]):
        bx = head_cx+ox
        d.polygon([(bx-5,ht+4),(bx+5,ht+4),(bx,max(2,ht+4-ch))], fill=feather_col)

    # Eyes inside head
    ey3 = max(ht+6, head_cy-int(head_ry*0.18))
    ey3 = min(hb-12, ey3)
    er3 = max(3, int(head_rx*0.28))
    eye(d, head_cx-int(head_rx*0.40), ey3, er3, (255,230,50,255),(80,30,0,255))
    eye(d, head_cx+int(head_rx*0.40), ey3, er3, (255,230,50,255),(80,30,0,255))

    # Beak — lower head, inside bounds
    beak_y0 = head_cy+int(head_ry*0.1)
    beak_y1 = min(hb-2, beak_y0+int(head_ry*0.55))
    d.polygon([(head_cx-int(head_rx*0.28),beak_y0),
               (head_cx+int(head_rx*0.28),beak_y0),
               (head_cx,beak_y1)], fill=(230,170,20,250))

    save(img, W, H, path)


def gen_lich_king(path):
    """6×6 — black/silver ice lich king, organic flowing robes."""
    W, H = 6, 6
    img = canvas(W, H, (5, 5, 14, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 230, 60, (0,0,40,0),(50,60,180,160))

    robe_col   = (28, 28, 65, 250)
    silver_col = (148,158,175, 248)
    ice_col    = (160,210,255, 230)
    orb_col    = (80, 100,220, 210)

    # Flowing robe — organic shape with wide hem
    robe_pts = [
        (cx-int(W_px*0.48), int(H_px*0.96)),
        (cx+int(W_px*0.48), int(H_px*0.96)),
        (cx+int(W_px*0.35), int(H_px*0.65)),
        (cx+int(W_px*0.26), int(H_px*0.28)),
        (cx-int(W_px*0.26), int(H_px*0.28)),
        (cx-int(W_px*0.35), int(H_px*0.65)),
    ]
    d.polygon(robe_pts, fill=robe_col)
    blob(d, cx, int(H_px*0.58), int(W_px*0.24), int(H_px*0.24), (38,38,80,240))

    # Shoulder pauldrons — organic rounded
    for side in [-1, 1]:
        sx = cx+side*int(W_px*0.34)
        sy = int(H_px*0.30)
        blob(d, sx, sy, int(W_px*0.10), int(H_px*0.08), silver_col, bumps=5, bump_size=0.14)
        blob(d, sx, sy+int(H_px*0.05), int(W_px*0.07), int(H_px*0.05),
             (180,192,210,240))

    # Head — organic skull
    head_cx = cx
    head_cy = int(H_px*0.18)
    head_rx = int(W_px*0.17)
    head_ry = int(H_px*0.14)
    ht = max(2, head_cy-head_ry)
    hb = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, (28,28,65,250), bumps=5, bump_size=0.07)

    # Ice crown spikes — clamped
    crown_pts = [(-int(head_rx*0.6),14),(-int(head_rx*0.25),22),
                 (0,28),(int(head_rx*0.25),22),(int(head_rx*0.6),14)]
    for ox, sh in crown_pts:
        bx = head_cx+ox
        d.polygon([(bx-5,ht+3),(bx+5,ht+3),(bx,max(2,ht-sh))], fill=ice_col)

    # Visor
    visor_y0 = head_cy-int(head_ry*0.10)
    visor_y1 = hb-2
    blob(d, head_cx, (visor_y0+visor_y1)//2, int(head_rx*0.84), (visor_y1-visor_y0)//2,
         (40,42,88,248))

    # Eyes inside upper face
    ey4 = max(ht+8, head_cy-int(head_ry*0.30))
    ey4 = min(visor_y0-6, ey4)
    er4 = max(4, int(head_rx*0.24))
    eye(d, head_cx-int(head_rx*0.40), ey4, er4, (100,180,255,255),(200,230,255,255))
    eye(d, head_cx+int(head_rx*0.40), ey4, er4, (100,180,255,255),(200,230,255,255))

    # Orb in chest — held between wrapped hands
    orb_cy = int(H_px*0.54)
    blob(d, cx, orb_cy, 20, 20, orb_col, bumps=8, bump_size=0.12)
    blob(d, cx, orb_cy, 12, 12, (130,160,255,240), bumps=4, bump_size=0.08)
    d.ellipse([cx-5, orb_cy-14, cx+2, orb_cy-7], fill=(220,235,255,180))

    # Rune trim along robe bottom
    for i in range(6):
        rx2 = cx-int(W_px*0.40)+i*int(W_px*0.135)
        ry2 = int(H_px*0.86)
        blob(d, rx2+6, ry2+8, 7, 9, (60,70,160,200))
        blob(d, rx2+6, ry2+8, 4, 5, (100,120,220,200))

    save(img, W, H, path)


def gen_void(path):
    """7×5 — deep void eater, tentacles from organic mass, eyes inside."""
    W, H = 7, 5
    img = canvas(W, H, (4, 2, 8, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 220, 60, (10,0,30,0),(70,20,150,180))

    void_col  = (28, 10, 60, 252)
    mid_col   = (60, 20,120, 248)
    eye_col   = (160,80,255, 255)
    tent_col  = (50, 15,100, 235)

    # Central void mass — fully organic
    blob(d, cx, int(H_px*0.50), int(W_px*0.30), int(H_px*0.34),
         void_col, bumps=9, bump_size=0.18)
    blob(d, cx, int(H_px*0.48), int(W_px*0.22), int(H_px*0.26),
         mid_col, bumps=7, bump_size=0.14)

    # Inner eye bounds
    ibx0 = cx-int(W_px*0.18); ibx1 = cx+int(W_px*0.18)
    iby0 = int(H_px*0.22);    iby1 = int(H_px*0.74)

    eye_positions = [
        (cx,           int(H_px*0.38), 14),
        (cx-int(W_px*0.11), int(H_px*0.33), 10),
        (cx+int(W_px*0.11), int(H_px*0.33), 10),
        (cx-int(W_px*0.08), int(H_px*0.55), 8),
        (cx+int(W_px*0.08), int(H_px*0.55), 8),
        (cx,           int(H_px*0.63), 7),
    ]
    for (ex, ey5, er5) in eye_positions:
        ex  = max(ibx0+er5+2, min(ibx1-er5-2, ex))
        ey5 = max(iby0+er5+2, min(iby1-er5-2, ey5))
        eye(d, ex, ey5, er5, eye_col, (230,160,255,255))

    # Tentacles from body edge — clamped
    for i in range(10):
        ang = 180 + i*19
        rad = math.radians(ang)
        sr = int(min(W_px,H_px)*0.25)
        er2 = int(min(W_px,H_px)*0.455)
        sx2 = cx+int(math.cos(rad)*sr)
        sy2 = int(H_px*0.50)+int(math.sin(rad)*sr)
        ex2 = max(2,min(W_px-2,cx+int(math.cos(rad)*er2)))
        ey2 = max(2,min(H_px-2,int(H_px*0.50)+int(math.sin(rad)*er2)))
        pts2 = []
        for j in range(8):
            t = j/7
            px2 = sx2+(ex2-sx2)*t; py2 = sy2+(ey2-sy2)*t
            perp_x = -(ey2-sy2); perp_y = ex2-sx2
            ln2 = math.hypot(perp_x,perp_y) or 1
            wave = math.sin(t*math.pi*2.5)*10*(1-t)
            pts2.append((px2+perp_x/ln2*wave, py2+perp_y/ln2*wave))
        for j in range(len(pts2)-1):
            w2 = max(1, int(6*(1-j/len(pts2))))
            d.line([pts2[j],pts2[j+1]], fill=tent_col, width=w2)

    save(img, W, H, path)


def gen_golem(path):
    """5×5 — obsidian lava golem, organic rock construction."""
    W, H = 5, 5
    img = canvas(W, H, (10, 5, 2, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.6), 170, 50, (50,8,0,0),(180,60,5,150))

    obsidian = (22, 15, 10, 252)
    lava     = (230, 90, 10, 240)
    bright   = (255,180, 30, 230)

    # Body — not rectangular: wide lower mass + narrower torso
    blob(d, cx, int(H_px*0.72), int(W_px*0.38), int(H_px*0.22),
         obsidian, bumps=7, bump_size=0.15)
    blob(d, cx, int(H_px*0.50), int(W_px*0.30), int(H_px*0.22),
         (30,20,14,252), bumps=6, bump_size=0.12)

    # Lava chest gem
    blob(d, cx, int(H_px*0.50), 24, 22, lava, bumps=6, bump_size=0.15)
    blob(d, cx, int(H_px*0.50), 14, 13, bright, bumps=4, bump_size=0.10)

    # Organic boulder arms
    for side in [-1, 1]:
        blob(d, cx+side*int(W_px*0.40), int(H_px*0.50), int(W_px*0.12), int(H_px*0.22),
             obsidian, bumps=6, bump_size=0.18)
        # Lava knuckle fist
        blob(d, cx+side*int(W_px*0.40), int(H_px*0.65), 14, 12, lava, bumps=5, bump_size=0.18)

    # Head — lumpy rock boulder
    head_cx = cx
    head_cy = int(H_px*0.17)
    head_rx = int(W_px*0.21)
    head_ry = int(H_px*0.16)
    ht = max(2, head_cy-head_ry)
    hb = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, obsidian, bumps=8, bump_size=0.16)

    # Rocky brow shelf
    brow_y = head_cy-int(head_ry*0.18)
    d.polygon([
        (head_cx-int(head_rx*0.65), brow_y),
        (head_cx+int(head_rx*0.65), brow_y),
        (head_cx+int(head_rx*0.50), brow_y-10),
        (head_cx-int(head_rx*0.50), brow_y-10),
    ], fill=(35,25,16,252))

    # Eyes — lava glow under brow, inside head
    ey6 = max(ht+8, brow_y+4)
    ey6 = min(hb-int(head_ry*0.4), ey6)
    ew6 = int(head_rx*0.32)
    eye(d, head_cx-ew6, ey6, 10, lava, bright)
    eye(d, head_cx+ew6, ey6, 10, lava, bright)

    # Mouth — lava crack inside lower head
    mouth_y6 = hb-int(head_ry*0.28)
    mouth_y6 = min(hb-4, max(ey6+14, mouth_y6))
    pts6 = [(head_cx-int(head_rx*0.52), mouth_y6)]
    for i in range(1,7):
        t = i/6
        pts6.append((head_cx-int(head_rx*0.52)+int(head_rx*1.04*t),
                     mouth_y6 + (5 if i%2==0 else -5)))
    pts6.append((head_cx+int(head_rx*0.52), mouth_y6))
    for i in range(len(pts6)-1):
        d.line([pts6[i],pts6[i+1]], fill=lava, width=3)

    # Lava cracks on body
    for _ in range(12):
        crx = rng.randint(int(W_px*0.12), int(W_px*0.88))
        cry = rng.randint(int(H_px*0.30), int(H_px*0.88))
        d.line([(crx,cry),(crx+rng.randint(-14,14), cry+rng.randint(6,18))],
               fill=lava, width=2)

    save(img, W, H, path)


def gen_kraken(path):
    """8×5 — navy/teal kraken, organic mantle, 8 tentacles from base."""
    W, H = 8, 5
    img = canvas(W, H, (3, 6, 14, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 230, 60, (0,15,50,0),(10,60,130,160))

    body_col = (18, 45, 85, 252)
    dark_col = (12, 30, 60, 248)
    sucker   = (30, 80,120, 200)

    # Head mantle — organic pointed top, wide base
    mantle_pts = [
        (cx, max(2, int(H_px*0.04))),
        (cx+int(W_px*0.24), int(H_px*0.18)),
        (cx+int(W_px*0.26), int(H_px*0.56)),
        (cx-int(W_px*0.26), int(H_px*0.56)),
        (cx-int(W_px*0.24), int(H_px*0.18)),
    ]
    d.polygon(mantle_pts, fill=body_col)
    # Inner mantle
    inner_pts = [
        (cx, max(2, int(H_px*0.07))),
        (cx+int(W_px*0.18), int(H_px*0.20)),
        (cx+int(W_px*0.20), int(H_px*0.52)),
        (cx-int(W_px*0.20), int(H_px*0.52)),
        (cx-int(W_px*0.18), int(H_px*0.20)),
    ]
    d.polygon(inner_pts, fill=(24,55,100,248))

    # Eyes inside mantle
    eye_bd_x0 = cx-int(W_px*0.20); eye_bd_x1 = cx+int(W_px*0.20)
    eye_bd_y0 = int(H_px*0.10);    eye_bd_y1 = int(H_px*0.50)
    ey7  = (eye_bd_y0+eye_bd_y1)//2 - int(H_px*0.06)
    er7  = max(7, int(W_px*0.038))
    ex7l = max(eye_bd_x0+er7+2, cx-int(W_px*0.12))
    ex7r = min(eye_bd_x1-er7-2, cx+int(W_px*0.12))
    eye(d, ex7l, ey7, er7, (0,210,180,255),(0,80,60,255))
    eye(d, ex7r, ey7, er7, (0,210,180,255),(0,80,60,255))

    # Mouth arc inside lower mantle
    mouth_y7 = int(H_px*0.46)
    mouth_y7 = min(eye_bd_y1-6, mouth_y7)
    d.arc([cx-int(W_px*0.14), mouth_y7-12, cx+int(W_px*0.14), mouth_y7+12],
          0,180, fill=(5,18,40,220), width=4)

    # 8 tentacles fanning downward
    base_y = int(H_px*0.56)
    for i in range(8):
        ang3 = 195+i*21
        rad3 = math.radians(ang3)
        length = int(min(W_px,H_px)*0.42)
        ex3 = max(2,min(W_px-2, cx+int(math.cos(rad3)*length)))
        ey3 = max(base_y,min(H_px-2, base_y+int(abs(math.sin(rad3))*length)))
        pts3 = []
        for j in range(9):
            t = j/8
            px3 = cx+(ex3-cx)*t; py3 = base_y+(ey3-base_y)*t
            perp_x = -(ey3-base_y); perp_y = ex3-cx
            ln3 = math.hypot(perp_x,perp_y) or 1
            wave = math.sin(t*math.pi*2.5)*12*(1-t)*(1 if i%2==0 else -1)
            pts3.append((px3+perp_x/ln3*wave, py3+perp_y/ln3*wave))
        for j in range(len(pts3)-1):
            w3 = max(1, int(8*(1-j/len(pts3))))
            d.line([pts3[j],pts3[j+1]], fill=body_col, width=w3)
            if j%2==0:
                mid_x = int((pts3[j][0]+pts3[j+1][0])/2)
                mid_y = int((pts3[j][1]+pts3[j+1][1])/2)
                sr = max(2, w3//2)
                d.ellipse([mid_x-sr,mid_y-sr,mid_x+sr,mid_y+sr], fill=sucker)

    save(img, W, H, path)


def gen_nightmare(path):
    """6×5 — magenta nightmare lord, fluid shifting mass."""
    W, H = 6, 5
    img = canvas(W, H, (12, 4, 12, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 210, 55, (40,0,50,0),(160,20,180,165))

    body_col = (110, 15, 115, 250)
    dark_col = ( 75,  8,  80, 245)
    wisp_col = (220, 90, 240, 180)

    # Fluid distorted body — very organic asymmetric blobs
    blob(d, cx, int(H_px*0.60), int(W_px*0.42), int(H_px*0.30),
         body_col, bumps=11, bump_size=0.22)
    blob(d, cx, int(H_px*0.52), int(W_px*0.32), int(H_px*0.22),
         dark_col, bumps=9, bump_size=0.18)

    # Head — distorted organic mass
    head_cx = cx
    head_cy = int(H_px*0.20)
    head_rx = int(W_px*0.22)
    head_ry = int(H_px*0.17)
    ht8 = max(2, head_cy-head_ry)
    hb8 = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, body_col, bumps=10, bump_size=0.20)
    # Side distortion growths — inside head width + a bit
    for side in [-1, 1]:
        lx = head_cx+side*int(head_rx*0.68)
        ly = head_cy+int(head_ry*0.10)
        blob(d, lx, ly, int(head_rx*0.32), int(head_ry*0.28), dark_col)

    # Eyes inside head
    ey8 = max(ht8+7, head_cy-int(head_ry*0.22))
    ey8 = min(hb8-int(head_ry*0.45), ey8)
    er8 = max(5, int(head_rx*0.26))
    eye(d, head_cx-int(head_rx*0.42), ey8, er8, (255,100,255,255),(200,20,220,255))
    eye(d, head_cx+int(head_rx*0.42), ey8, er8, (255,100,255,255),(200,20,220,255))

    # Warped mouth inside lower head
    mouth_y8 = hb8-int(head_ry*0.30)
    mouth_y8 = min(hb8-4, max(ey8+er8+6, mouth_y8))
    pts8 = []
    mw8 = int(head_rx*0.58)
    for i in range(12):
        t = i/11
        pts8.append((head_cx-mw8+int(2*mw8*t),
                     mouth_y8+int(math.sin(t*math.pi*3)*5)))
    for i in range(len(pts8)-1):
        d.line([pts8[i],pts8[i+1]], fill=(20,5,25,230), width=3)

    # Dream wisps floating in canvas
    for _ in range(12):
        wx = rng.randint(8, W_px-8)
        wy = rng.randint(8, H_px-8)
        wr = rng.randint(4, 14)
        blob(d, wx, wy, wr, int(wr*0.7), wisp_col, bumps=5, bump_size=0.25)

    save(img, W, H, path)


def gen_frost_titan(path):
    """7×6 — ice blue titan, crystal organic armor, no rectangular body."""
    W, H = 7, 6
    img = canvas(W, H, (5, 10, 20, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 250, 65, (0,20,60,0),(30,100,200,150))

    ice_col  = (100, 180, 240, 250)
    dark_ice = ( 55, 120, 180, 245)
    crystal  = (190, 230, 255, 220)
    deep_b   = ( 20,  55, 110, 248)

    # Massive lower body — ice boulder
    blob(d, cx, int(H_px*0.74), int(W_px*0.40), int(H_px*0.22),
         dark_ice, bumps=7, bump_size=0.12)
    # Upper torso — slightly smaller organic shape
    blob(d, cx, int(H_px*0.52), int(W_px*0.34), int(H_px*0.24),
         ice_col, bumps=6, bump_size=0.10)
    # Inner torso darker
    blob(d, cx, int(H_px*0.52), int(W_px*0.24), int(H_px*0.18),
         dark_ice, bumps=5, bump_size=0.08)

    # Crystal cluster chest
    for i in range(5):
        crx = cx+(i-2)*int(W_px*0.060)
        cry = int(H_px*0.51)
        crh = int(H_px*0.13)+(i%2)*int(H_px*0.04)
        d.polygon([(crx-7,cry),(crx+7,cry),(crx,cry-crh)], fill=crystal)

    # Organic ice arms
    for side in [-1, 1]:
        blob(d, cx+side*int(W_px*0.42), int(H_px*0.52), int(W_px*0.09), int(H_px*0.22),
             dark_ice, bumps=6, bump_size=0.14)
        # Ice fist
        blob(d, cx+side*int(W_px*0.42), int(H_px*0.72), int(W_px*0.10), int(H_px*0.08),
             ice_col, bumps=6, bump_size=0.20)

    # Head — organic ice helm shape
    head_cx = cx
    head_cy = int(H_px*0.18)
    head_rx = int(W_px*0.18)
    head_ry = int(H_px*0.16)
    ht9 = max(2, head_cy-head_ry)
    hb9 = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, ice_col, bumps=6, bump_size=0.10)
    blob(d, head_cx, head_cy+int(head_ry*0.20), int(head_rx*0.80), int(head_ry*0.72),
         dark_ice, bumps=5, bump_size=0.08)

    # Crystal horns — from head top, clamped
    for ox, ch in [(-int(head_rx*0.50),26),(0,36),(int(head_rx*0.50),26)]:
        bx = head_cx+ox
        d.polygon([(bx-5,ht9+2),(bx+5,ht9+2),(bx,max(2,ht9-ch))], fill=crystal)

    # Visor eyes inside helmet
    ey9 = head_cy-int(head_ry*0.12)
    ey9 = max(ht9+8, min(hb9-int(head_ry*0.55), ey9))
    ew9 = int(head_rx*0.34)
    d.ellipse([head_cx-ew9-6, ey9-6, head_cx+ew9+6, ey9+6], fill=deep_b)
    eye(d, head_cx-ew9, ey9, 7, (160,230,255,255),(20,80,160,255))
    eye(d, head_cx+ew9, ey9, 7, (160,230,255,255),(20,80,160,255))

    # Grill at mouth — inside head lower area
    grill_y = hb9-int(head_ry*0.32)
    grill_y = min(hb9-6, max(ey9+12, grill_y))
    for k in range(2):
        d.line([(head_cx-int(head_rx*0.52), grill_y+k*7),
                (head_cx+int(head_rx*0.52), grill_y+k*7)],
               fill=deep_b, width=4)

    save(img, W, H, path)


def gen_plague(path):
    """6×5 — sickly green bloated plague lord."""
    W, H = 6, 5
    img = canvas(W, H, (6, 10, 4, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.55), 200, 55, (10,40,0,0),(50,160,20,155))

    green  = ( 60, 130, 25, 250)
    yellow = (175, 185, 20, 240)
    dark_g = ( 35,  80, 12, 248)
    pus    = (215, 200, 40, 230)

    # Bloated organic body — very round and lumpy
    blob(d, cx, int(H_px*0.62), int(W_px*0.44), int(H_px*0.30),
         green, bumps=9, bump_size=0.20)
    blob(d, cx, int(H_px*0.56), int(W_px*0.34), int(H_px*0.22),
         dark_g, bumps=7, bump_size=0.16)

    # Bloated head
    head_cx = cx
    head_cy = int(H_px*0.22)
    head_rx = int(W_px*0.24)
    head_ry = int(H_px*0.19)
    ht10 = max(2, head_cy-head_ry)
    hb10 = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, green, bumps=8, bump_size=0.18)
    blob(d, head_cx, head_cy+int(head_ry*0.1), int(head_rx*0.86), int(head_ry*0.82),
         dark_g, bumps=6, bump_size=0.12)

    # Eyes inside head
    ey10 = max(ht10+8, head_cy-int(head_ry*0.30))
    ey10 = min(hb10-int(head_ry*0.45), ey10)
    er10 = max(5, int(head_rx*0.24))
    eye(d, head_cx-int(head_rx*0.38), ey10, er10, yellow,(80,90,5,255))
    eye(d, head_cx+int(head_rx*0.38), ey10, er10, yellow,(80,90,5,255))

    # Plague grin inside head lower area
    mouth_y10 = hb10-int(head_ry*0.34)
    mouth_y10 = min(hb10-4, max(ey10+er10+6, mouth_y10))
    d.arc([head_cx-int(head_rx*0.55), mouth_y10-14,
           head_cx+int(head_rx*0.55), mouth_y10+14],
          0, 180, fill=yellow, width=4)
    teeth_row(d, head_cx-int(head_rx*0.45), mouth_y10-8,
              head_cx+int(head_rx*0.45), 4, 8, 8, (200,200,160,235), pointy=True)

    # Pustules on body
    for _ in range(22):
        px10 = rng.randint(int(W_px*0.12), int(W_px*0.88))
        py10 = rng.randint(int(H_px*0.28), int(H_px*0.92))
        pr10 = rng.randint(5, 15)
        blob(d, px10, py10, pr10, int(pr10*0.75), yellow, bumps=5, bump_size=0.20)
        blob(d, px10-pr10//3, py10-pr10//3, pr10//3, pr10//3, pus)

    save(img, W, H, path)


def gen_thunder(path):
    """6×6 — electric blue war god, massive organic armored form."""
    W, H = 6, 6
    img = canvas(W, H, (4, 4, 16, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 240, 60, (0,0,60,0),(40,80,255,165))

    armor_col  = ( 40,  50, 130, 252)
    bright_col = (130, 180, 255, 248)
    elec_col   = (200, 230, 255, 230)
    dark_col   = ( 18,  22,  65, 250)

    # Massive armored torso — organic rounded
    blob(d, cx, int(H_px*0.60), int(W_px*0.40), int(H_px*0.28),
         armor_col, bumps=6, bump_size=0.10)
    blob(d, cx, int(H_px*0.54), int(W_px*0.30), int(H_px*0.20),
         dark_col, bumps=5, bump_size=0.08)

    # Energy core in chest
    blob(d, cx, int(H_px*0.52), 22, 22, bright_col, bumps=7, bump_size=0.15)
    blob(d, cx, int(H_px*0.52), 12, 12, elec_col, bumps=4, bump_size=0.10)

    # Organic legs
    for side in [-1, 1]:
        blob(d, cx+side*int(W_px*0.22), int(H_px*0.82), int(W_px*0.10), int(H_px*0.13),
             armor_col, bumps=5, bump_size=0.12)

    # Arms with organic pauldrons
    for side in [-1, 1]:
        # Shoulder blob
        blob(d, cx+side*int(W_px*0.33), int(H_px*0.36), int(W_px*0.11), int(H_px*0.10),
             bright_col, bumps=6, bump_size=0.14)
        # Arm
        blob(d, cx+side*int(W_px*0.42), int(H_px*0.54), int(W_px*0.09), int(H_px*0.22),
             dark_col, bumps=5, bump_size=0.10)
        # Gauntlet
        blob(d, cx+side*int(W_px*0.42), int(H_px*0.70), 16, 14, armor_col, bumps=6, bump_size=0.18)
        # Lightning arcs from gauntlet — clamped
        for k in range(3):
            lx2 = cx+side*int(W_px*0.42)+side*(k-1)*5
            ly0 = int(H_px*0.74)
            ly1 = min(H_px-2, ly0+rng.randint(14,28))
            d.line([(lx2,ly0),(lx2+side*rng.randint(5,12),ly1)], fill=elec_col, width=2)

    # Head — large organic helm
    head_cx = cx
    head_cy = int(H_px*0.18)
    head_rx = int(W_px*0.19)
    head_ry = int(H_px*0.16)
    ht11 = max(2, head_cy-head_ry)
    hb11 = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, armor_col, bumps=6, bump_size=0.10)
    blob(d, head_cx, head_cy+int(head_ry*0.18), int(head_rx*0.80), int(head_ry*0.72),
         dark_col, bumps=5, bump_size=0.08)

    # Lightning horns — clamped
    for hx_off, tilt in [(-int(head_rx*0.50),-14),(int(head_rx*0.50),14)]:
        bx = head_cx+hx_off
        tip_x = bx+int(math.sin(math.radians(tilt))*24)
        tip_y = max(2, ht11-28)
        d.polygon([(bx-5,ht11+2),(bx+5,ht11+2),(tip_x,tip_y)], fill=elec_col)

    # Visor slit inside helm
    ey11 = head_cy-int(head_ry*0.12)
    ey11 = max(ht11+8, min(hb11-int(head_ry*0.55), ey11))
    d.ellipse([head_cx-int(head_rx*0.52), ey11-5,
               head_cx+int(head_rx*0.52), ey11+5], fill=bright_col)
    ew11 = int(head_rx*0.32)
    eye(d, head_cx-ew11, ey11, 5, elec_col, (255,255,255,255))
    eye(d, head_cx+ew11, ey11, 5, elec_col, (255,255,255,255))

    # Lightning arcs on body
    for _ in range(10):
        lx3 = rng.randint(int(W_px*0.18), int(W_px*0.82))
        ly3 = rng.randint(int(H_px*0.32), int(H_px*0.76))
        for _ in range(4):
            d.line([(lx3,ly3),(lx3+rng.randint(-22,22),ly3+rng.randint(-14,14))],
                   fill=elec_col, width=1)

    save(img, W, H, path)


def gen_shadow(path):
    """8×6 — black shadow king, massive fluid dark mass."""
    W, H = 8, 6
    img = canvas(W, H, (2, 2, 6, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 280, 70, (5,0,15,0),(40,10,80,170))

    shadow_col = (15, 10, 30, 252)
    mid_col    = (35, 20, 65, 248)
    eye_col    = (200,150,255, 255)
    tendril_col= (25, 12, 50, 240)

    # Main shadow mass — very large organic
    blob(d, cx, int(H_px*0.55), int(W_px*0.38), int(H_px*0.38),
         shadow_col, bumps=12, bump_size=0.22)
    blob(d, cx, int(H_px*0.50), int(W_px*0.28), int(H_px*0.28),
         mid_col, bumps=9, bump_size=0.18)

    # Shadow crown spikes around top — clamped
    for i in range(7):
        ang_s = -55+i*18
        rad_s = math.radians(ang_s-90)
        spike_len = 28+(i%3)*16
        bx_s = cx+int(math.cos(math.radians(ang_s))*int(W_px*0.25))
        by_s = int(H_px*0.22)+int(math.sin(math.radians(ang_s))*int(H_px*0.11))
        tip_x = max(2,min(W_px-2, bx_s+int(math.cos(rad_s)*spike_len)))
        tip_y = max(2,min(H_px-2, by_s+int(math.sin(rad_s)*spike_len)))
        d.polygon([(bx_s-5,by_s),(bx_s+5,by_s),(tip_x,tip_y)], fill=shadow_col)

    # Inner eye bounds
    ibx0 = cx-int(W_px*0.22); ibx1 = cx+int(W_px*0.22)
    iby0 = int(H_px*0.22);    iby1 = int(H_px*0.78)

    eye_positions12 = [
        (cx-int(W_px*0.12), int(H_px*0.42), 11),
        (cx+int(W_px*0.12), int(H_px*0.42), 11),
        (cx,                int(H_px*0.58), 8),
    ]
    for (ex12, ey12, er12) in eye_positions12:
        ex12 = max(ibx0+er12+2, min(ibx1-er12-2, ex12))
        ey12 = max(iby0+er12+2, min(iby1-er12-2, ey12))
        eye(d, ex12, ey12, er12, eye_col, (230,190,255,255))

    # Shadow mouth
    mouth_y12 = int(H_px*0.68)
    mouth_y12 = min(iby1-8, max(eye_positions12[-1][1]+eye_positions12[-1][2]+6, mouth_y12))
    pts12 = []
    mw12 = int(W_px*0.22)
    for i in range(14):
        t = i/13
        pts12.append((cx-mw12+int(2*mw12*t), mouth_y12+int(math.sin(t*math.pi*4)*7)))
    for i in range(len(pts12)-1):
        d.line([pts12[i],pts12[i+1]], fill=(5,2,12,235), width=3)

    # Shadow tendrils — clamped
    body_cx2 = cx; body_cy2 = int(H_px*0.52)
    for i in range(12):
        ang12 = i*30
        rad12 = math.radians(ang12)
        sr12 = int(min(W_px,H_px)*0.28)
        er12 = int(min(W_px,H_px)*0.47)
        sx12 = max(2,min(W_px-2, body_cx2+int(math.cos(rad12)*sr12)))
        sy12 = max(2,min(H_px-2, body_cy2+int(math.sin(rad12)*sr12)))
        ex13 = max(2,min(W_px-2, body_cx2+int(math.cos(rad12)*er12)))
        ey13 = max(2,min(H_px-2, body_cy2+int(math.sin(rad12)*er12)))
        pts13 = []
        for j in range(7):
            t = j/6
            px13 = sx12+(ex13-sx12)*t; py13 = sy12+(ey13-sy12)*t
            perp_x = -(ey13-sy12); perp_y = ex13-sx12
            ln13 = math.hypot(perp_x,perp_y) or 1
            wave = math.sin(t*math.pi*2)*9*(1-t)
            pts13.append((px13+perp_x/ln13*wave, py13+perp_y/ln13*wave))
        for j in range(len(pts13)-1):
            w13 = max(1, int(5*(1-j/len(pts13))))
            d.line([pts13[j],pts13[j+1]], fill=tendril_col, width=w13)

    save(img, W, H, path)


def gen_ancient(path):
    """8×7 — gold/white ancient god, many arms, organic divine form."""
    W, H = 8, 7
    img = canvas(W, H, (14, 12, 5, 255))
    d = ImageDraw.Draw(img)
    cx, cy = cxy(img)
    W_px, H_px = W*CELL, H*CELL

    glow(img, cx, int(H_px*0.5), 300, 70, (60,50,0,0),(220,190,30,170))

    gold_col  = (210,175, 20, 252)
    pale_col  = (240,225,160, 245)
    dark_gold = (140,110, 10, 248)
    white_col = (245,245,235, 240)

    # Central torso — organic divine form
    blob(d, cx, int(H_px*0.58), int(W_px*0.28), int(H_px*0.24),
         gold_col, bumps=7, bump_size=0.12)
    blob(d, cx, int(H_px*0.54), int(W_px*0.20), int(H_px*0.18),
         dark_gold, bumps=5, bump_size=0.08)

    # 6 arms radiating — organic and clamped
    for i in range(6):
        ang_a = -55+i*42
        rad_a = math.radians(ang_a)
        sr_a = int(W_px*0.20)
        er_a = int(W_px*0.44)
        ax0 = cx+int(math.cos(rad_a)*sr_a)
        ay0 = int(H_px*0.57)+int(math.sin(rad_a)*sr_a)
        ax1 = max(2,min(W_px-2, cx+int(math.cos(rad_a)*er_a)))
        ay1 = max(2,min(H_px-2, int(H_px*0.57)+int(math.sin(rad_a)*er_a)))
        d.line([(ax0,ay0),(ax1,ay1)], fill=gold_col, width=10)
        blob(d, ax1, ay1, 11, 11, pale_col, bumps=5, bump_size=0.18)

    # Head — organic divine oval
    head_cx = cx
    head_cy = int(H_px*0.18)
    head_rx = int(W_px*0.16)
    head_ry = int(H_px*0.14)
    ht14 = max(2, head_cy-head_ry)
    hb14 = head_cy+head_ry
    blob(d, head_cx, head_cy, head_rx, head_ry, pale_col, bumps=5, bump_size=0.08)

    # Halo — ring above head, clamped
    halo_r = int(head_rx*1.4)
    halo_cy = max(2+halo_r, ht14-8)
    d.ellipse([head_cx-halo_r, halo_cy-halo_r//2,
               head_cx+halo_r, halo_cy+halo_r//2], outline=gold_col, width=5)

    # Eyes inside head
    ey14 = max(ht14+7, head_cy-int(head_ry*0.22))
    ey14 = min(hb14-int(head_ry*0.44), ey14)
    er14 = max(4, int(head_rx*0.26))
    eye(d, head_cx-int(head_rx*0.40), ey14, er14, white_col,(50,40,0,255))
    eye(d, head_cx+int(head_rx*0.40), ey14, er14, white_col,(50,40,0,255))

    # Serene mouth inside lower head
    mouth_y14 = hb14-int(head_ry*0.30)
    mouth_y14 = min(hb14-4, max(ey14+er14+5, mouth_y14))
    d.arc([head_cx-int(head_rx*0.42), mouth_y14-9,
           head_cx+int(head_rx*0.42), mouth_y14+9], 0,180, fill=gold_col, width=3)

    # Divine runes on body
    for i in range(8):
        rx14 = cx-int(W_px*0.22)+i*int(W_px*0.066)
        ry14 = int(H_px*0.56)+(i%3)*14
        blob(d, rx14+5, ry14+7, 6, 8, dark_gold)
        blob(d, rx14+5, ry14+7, 3, 4, gold_col)

    save(img, W, H, path)


# ---------------------------------------------------------------------------
BOSSES = [
    ("boss_lich.png",       gen_lich),
    ("boss_dragon.png",     gen_dragon),
    ("boss_colossus.png",   gen_colossus),
    ("boss_hydra.png",      gen_hydra),
    ("boss_phoenix.png",    gen_phoenix),
    ("boss_lich_king.png",  gen_lich_king),
    ("boss_void.png",       gen_void),
    ("boss_golem.png",      gen_golem),
    ("boss_kraken.png",     gen_kraken),
    ("boss_nightmare.png",  gen_nightmare),
    ("boss_frost_titan.png",gen_frost_titan),
    ("boss_plague.png",     gen_plague),
    ("boss_thunder.png",    gen_thunder),
    ("boss_shadow.png",     gen_shadow),
    ("boss_ancient.png",    gen_ancient),
]

if __name__ == "__main__":
    print("Generating boss sprites...")
    for filename, func in BOSSES:
        func(os.path.join(OUT_DIR, filename))
    print(f"Done! {len(BOSSES)} bosses generated.")
