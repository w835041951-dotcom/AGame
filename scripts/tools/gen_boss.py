"""
Boss 像素艺术生成器 — 4x scale trick for clean pixel art
208x156px (4col x 3row, 52px/cell)
"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

# 先在4倍大小上绘制，再缩小得到清晰像素风
SCALE = 4
W, H   = 208 * SCALE, 156 * SCALE
CELL   = 52 * SCALE

def px(v):
    if isinstance(v, (list, tuple)) and not isinstance(v[0], int):
        return [(int(x*SCALE), int(y*SCALE)) for x,y in v]
    if isinstance(v, (list, tuple)):
        return [int(x * SCALE) for x in v]
    return int(v * SCALE)

def circle(dr, cx, cy, r, fill, outline=None, ow=1):
    dr.ellipse([px(cx-r), px(cy-r), px(cx+r), px(cy+r)], fill=fill,
               outline=outline, width=px(ow) if outline else 0)

def rect(dr, x0, y0, x1, y1, fill=None, outline=None, ow=1, radius=0):
    dr.rounded_rectangle([px(x0), px(y0), px(x1), px(y1)],
                         radius=px(radius), fill=fill,
                         outline=outline, width=px(ow) if outline else 0)

def poly(dr, pts, fill):
    dr.polygon(px(pts), fill=fill)

def line(dr, x0, y0, x1, y1, fill, w=1):
    dr.line([px(x0), px(y0), px(x1), px(y1)], fill=fill, width=px(w))

# ═══════════════════════════════════════════════
# 辅助：在图上叠加径向发光
def add_glow(img, cx, cy, r, color, steps=8):
    glow = Image.new("RGBA", img.size, (0,0,0,0))
    gdr  = ImageDraw.Draw(glow)
    for i in range(steps, 0, -1):
        alpha = int(color[3] * (i / steps) ** 1.5)
        rad   = int(r * i / steps)
        c     = color[:3] + (alpha,)
        gdr.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c)
    return Image.alpha_composite(img, glow)

# ═══════════════════════════════════════════════
def gen_boss():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr  = ImageDraw.Draw(img)

    # ── 背景渐变体（深紫-暗红） ──
    for y in range(H):
        t = y / H
        r = int(80  + 60  * t)
        g = int(5   + 8   * t)
        b = int(15  + 10  * (1-t))
        dr.line([(px(4), y), (W - px(4), y)], fill=(r, g, b, 255))

    # ── 身体轮廓（圆角矩形，多层描边产生厚重感）──
    for offset, col in [(6,(40,0,0,255)),(4,(80,10,10,255)),(2,(140,20,20,255)),(0,(180,30,30,255))]:
        rect(dr, 4+offset, 6+offset, 204-offset, 150-offset,
             outline=col, ow=2, radius=16)

    # ── 身体主色块 ──
    rect(dr, 6, 8, 202, 148, fill=(90, 12, 12, 255), radius=14)

    # ── 鳞甲纹路（斜线网格） ──
    for i in range(-H, W+H, px(12)):
        dr.line([(i, 0), (i+H, H)], fill=(110,15,15,120), width=px(1))
    for i in range(-H, W+H, px(12)):
        dr.line([(i+H, 0), (i, H)], fill=(70, 8, 8, 80), width=px(1))

    # ── 左右装甲翼板 ──
    # 左翼
    poly(dr, [(4,20),(36,12),(36,144),(4,136)], fill=(50,55,80,255))
    for i in range(3):
        y0 = 20 + i*40
        poly(dr, [(4,y0),(36,y0-6),(36,y0+26),(4,y0+28)], fill=(65,70,100,255))
        line(dr, 6, y0+2, 34, y0-3, (140,150,200,200), 1)
    # 右翼
    poly(dr, [(204,20),(172,12),(172,144),(204,136)], fill=(50,55,80,255))
    for i in range(3):
        y0 = 20 + i*40
        poly(dr, [(204,y0),(172,y0-6),(172,y0+26),(204,y0+28)], fill=(65,70,100,255))
        line(dr, 202, y0+2, 174, y0-3, (140,150,200,200), 1)

    # ── 铆钉 ──
    rivet = (200,210,240,255)
    rivet_dark = (100,105,130,255)
    for yp in [18,42,66,92,118,140]:
        for xp, side in [(8, 1), (24, 1), (184, -1), (200, -1)]:
            circle(dr, xp, yp, 4, rivet)
            circle(dr, xp+1, yp+1, 2, rivet_dark)

    # ── 眼睛（第一行，y≈10~52）──
    for ex, flip in [(68, 1), (140, -1)]:
        # 眼眶
        circle(dr, ex, 32, 18, (30,5,5,255))
        circle(dr, ex, 32, 14, (200,30,30,255))
        # 虹膜
        circle(dr, ex, 32, 10, (240,80,20,255))
        # 瞳孔
        circle(dr, ex, 32,  6, (20,5,5,255))
        # 高光
        circle(dr, ex-4*flip, 28, 3, (255,240,200,230))
        # 外发光
        img = add_glow(img, px(ex), px(32), px(20), (255,60,0,60))

    # 眉骨/眉毛（尖刺状）
    poly(dr, [(52,18),(62,10),(72,20),(62,16)], fill=(60,8,8,255))
    poly(dr, [(156,18),(146,10),(136,20),(146,16)], fill=(60,8,8,255))

    # ── 鼻（中央脊骨）──
    poly(dr, [(100,42),(108,42),(110,62),(104,66),(98,62)], fill=(70,10,10,255))
    line(dr, 104, 44, 104, 64, (130,20,20,200), 2)

    # ── 嘴（第二行，y≈62~104）──
    mouth_pts = [
        (48,78),(52,72),(60,80),(68,68),(80,76),(104,70),(128,76),(140,68),(148,80),(156,72),(160,78),
        (160,92),(48,92)
    ]
    poly(dr, mouth_pts, fill=(15,3,3,255))
    # 牙齿
    tooth_col  = (230,225,210,255)
    fang_col   = (255,240,220,255)
    for tx in range(52, 158, 13):
        poly(dr, [(tx,73),(tx+6,73),(tx+3,86)], fill=tooth_col)
    # 獠牙
    poly(dr, [(62,73),(70,73),(66,96),(63,90)], fill=fang_col)
    poly(dr, [(138,73),(146,73),(141,96),(145,90)], fill=fang_col)
    # 嘴唇描边
    line(dr, 48,78, 160,78, (200,20,20,180), 1)

    # ── 胸甲中央纹章 ──
    cx, cy = 104, 118
    # 六边形底
    hex_pts = [(cx, cy-22),(cx+19,cy-11),(cx+19,cy+11),(cx,cy+22),(cx-19,cy+11),(cx-19,cy-11)]
    poly(dr, hex_pts, fill=(45,8,8,255))
    poly(dr, hex_pts, fill=None)
    dr.polygon(px(hex_pts), outline=(180,30,30,255), width=px(2))

    # ── CORE 发光水晶（中央） ──
    img = add_glow(img, px(cx), px(cy), px(18), (255,150,0,100))
    for r2, c2 in [(16,(255,200,50,80)),(12,(255,160,20,140)),(8,(255,220,80,200)),(4,(255,255,180,255))]:
        circle(dr, cx, cy, r2, c2)
    # 水晶高光
    poly(dr, [(cx-3,cy-10),(cx+3,cy-10),(cx+6,cy-2),(cx,cy+2),(cx-6,cy-2)], fill=(255,255,230,200))

    # ── 腹部装甲分节 ──
    for seg_y in [104, 115, 126]:
        line(dr, 36, seg_y, 172, seg_y, (60,8,8,160), 2)
        for sx in range(44, 172, 16):
            circle(dr, sx, seg_y, 3, (100,15,15,200))

    # ── 顶部尖角/头冠 ──
    poly(dr, [(88,8),(104,0),(120,8),(112,18),(96,18)], fill=(50,50,75,255))
    poly(dr, [(96,6),(104,0),(112,6),(108,14),(100,14)], fill=(140,150,190,255))

    # ── 底部爪子提示 ──
    for cx2 in [52, 88, 120, 156]:
        poly(dr, [(cx2-8,146),(cx2,143),(cx2+8,146),(cx2+4,156),(cx2-4,156)], fill=(60,8,8,255))
        poly(dr, [(cx2-4,147),(cx2,144),(cx2+4,147),(cx2+2,154),(cx2-2,154)], fill=(100,15,15,255))

    # ── 整体描边 ──
    rect(dr, 4, 6, 204, 150, outline=(220,50,50,255), ow=2, radius=16)

    # ── 缩小到目标尺寸 ──
    out_img = img.resize((208, 156), Image.LANCZOS)

    # ── 叠加半透明格子线（方便调试，可关闭）──
    gdr = ImageDraw.Draw(out_img)
    for col in range(1, 4):
        gdr.line([(col*52, 0),(col*52, 156)], fill=(0,0,0,50), width=1)
    for row in range(1, 3):
        gdr.line([(0, row*52),(208, row*52)], fill=(0,0,0,50), width=1)

    path = os.path.join(OUT, "boss_full.png")
    out_img.save(path)
    print("saved", path)

    # ── 受击叠加层 ──
    hit = Image.new("RGBA", (208,156), (0,0,0,0))
    hdr = ImageDraw.Draw(hit)
    hdr.rounded_rectangle([2,4,206,152], radius=14, fill=(255,50,50,90))
    hit.save(os.path.join(OUT, "boss_hit_overlay.png"))
    print("saved boss_hit_overlay.png")

# ═══════════════════════════════════════════════
# 炸弹图标 32x32（也重新生成，更精致）
def gen_bombs():
    bdir = os.path.join(OUT, "..", "bombs")
    os.makedirs(bdir, exist_ok=True)
    S = 4  # scale
    SZ = 32 * S

    configs = {
        "cross":   ((220, 40,  40), "+",  "十字"),
        "scatter": ((255,140,  13), "✦",  "散弹"),
        "bounce":  (( 30,210, 210), "~",  "反弹"),
        "pierce":  ((240,230,  30), "↑",  "穿透"),
        "area":    ((180, 30, 220), "◼",  "爆炸"),
    }

    for name, (col, sym, label) in configs.items():
        img = Image.new("RGBA", (SZ, SZ), (0,0,0,0))
        dr  = ImageDraw.Draw(img)
        cx = cy = SZ // 2
        r = SZ // 2 - 4*S

        # 阴影
        dr.ellipse([cx-r+2*S, cy-r+3*S, cx+r+2*S, cy+r+3*S], fill=(0,0,0,80))
        # 主体
        dark = tuple(max(0,c-80) for c in col) + (255,)
        dr.ellipse([cx-r, cy-r, cx+r, cy+r], fill=dark)
        dr.ellipse([cx-r+S, cy-r+S, cx+r-S, cy+r-S], fill=col+(255,))
        # 高光
        dr.ellipse([cx-r+3*S, cy-r+2*S, cx-r+8*S, cy-r+6*S], fill=(255,255,255,180))
        # 引线
        dr.line([cx+int(r*0.6), cy-int(r*0.8), cx+r+3*S, cy-r-3*S],
                fill=(200,170,40,255), width=2*S)
        # 引线火花
        fsx = cx+r+3*S; fsy = cy-r-3*S
        for angle in range(0, 360, 60):
            a = math.radians(angle)
            dr.line([fsx, fsy, int(fsx+5*S*math.cos(a)), int(fsy+5*S*math.sin(a))],
                    fill=(255,220,50,200), width=S)

        out = img.resize((32,32), Image.LANCZOS)
        path = os.path.join(bdir, name+".png")
        out.save(path)
        print("saved", path)

if __name__ == "__main__":
    gen_boss()
    gen_bombs()
    print("All done!")
