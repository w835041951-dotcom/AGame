"""
Boss 像素艺术生成器 v2 — 魔王骑士风格
208x156px (4col x 3row, 52px/cell)
特点：盔甲骑士 + 恶魔之翼 + 核心宝石 + 更多细节
"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

SCALE = 6   # 更高倍率 → 更清晰的像素细节
W, H   = 208 * SCALE, 156 * SCALE
CELL   = 52 * SCALE

def px(v):
    if isinstance(v, (list, tuple)) and len(v) > 0 and not isinstance(v[0], (int, float)):
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

def poly(dr, pts, fill, outline=None, ow=1):
    dr.polygon(px(pts), fill=fill, outline=outline, width=px(ow) if outline else 0)

def line(dr, x0, y0, x1, y1, fill, w=1):
    dr.line([px(x0), px(y0), px(x1), px(y1)], fill=fill, width=px(w))

def add_glow(img, cx, cy, r, color, steps=10):
    glow = Image.new("RGBA", img.size, (0,0,0,0))
    gdr  = ImageDraw.Draw(glow)
    for i in range(steps, 0, -1):
        alpha = int(color[3] * (i / steps) ** 2)
        rad   = int(r * i / steps)
        c     = color[:3] + (alpha,)
        gdr.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=c)
    return Image.alpha_composite(img, glow)

def gen_boss():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr  = ImageDraw.Draw(img)

    # ── 身体底色：深紫-黑渐变 ──
    for y in range(H):
        t = y / H
        r = int(35 + 25 * t)
        g = int(5  + 5  * t)
        b = int(55 - 20 * t)
        dr.line([(px(6), y), (W - px(6), y)], fill=(r, g, b, 240))

    # ── 盔甲主体（多层）──
    # 最外层阴影
    rect(dr, 8, 10, 200, 146, fill=(15, 5, 25, 200), radius=18)
    # 主甲板
    rect(dr, 5, 7, 203, 149, fill=(60, 18, 80, 255), radius=16)
    # 内衬（稍亮）
    rect(dr, 10, 12, 198, 144, fill=(75, 22, 95, 255), radius=13)

    # ── 鳞甲纹路（六边形网格感）──
    for row in range(20):
        for col in range(15):
            hx = col * px(12) + (px(6) if row % 2 else 0)
            hy = row * px(8) + px(8)
            if px(8) < hx < W - px(8) and px(10) < hy < H - px(10):
                dr.ellipse([hx-px(3), hy-px(2), hx+px(3), hy+px(2)],
                           fill=(90, 28, 115, 140))

    # ── 左右恶魔翼板 ──
    # 左翼骨架
    wing_pts_l = [(5,15),(0,8),(0,148),(5,142),(30,120),(28,80),(32,50),(30,28)]
    poly(dr, wing_pts_l, fill=(25, 8, 40, 255))
    # 左翼膜（深紫半透明）
    for i in range(4):
        y_top = 20 + i * 30
        y_bot = y_top + 28
        poly(dr, [(5, y_top),(28, y_top-5),(30, y_bot+5),(5, y_bot)],
             fill=(55, 15, 85, 200))
        line(dr, 7, y_top, 27, y_top-3, (130, 60, 180, 160), 1)
    # 右翼（镜像）
    wing_pts_r = [(203,15),(208,8),(208,148),(203,142),(178,120),(180,80),(176,50),(178,28)]
    poly(dr, wing_pts_r, fill=(25, 8, 40, 255))
    for i in range(4):
        y_top = 20 + i * 30
        y_bot = y_top + 28
        poly(dr, [(203, y_top),(180, y_top-5),(178, y_bot+5),(203, y_bot)],
             fill=(55, 15, 85, 200))
        line(dr, 201, y_top, 181, y_top-3, (130, 60, 180, 160), 1)

    # ── 肩甲（尖刺） ──
    # 左肩
    for i, (sx, ang) in enumerate([(18, -30), (24, -10), (30, 10)]):
        a = math.radians(ang - 90)
        tip_x = sx + int(16 * math.cos(a))
        tip_y = 10 + int(16 * math.sin(a))
        poly(dr, [(sx-5, 18),(sx+5, 18),(tip_x, tip_y)],
             fill=(120, 130, 170, 255))
        poly(dr, [(sx-3, 18),(sx+3, 18),(tip_x, tip_y)],
             fill=(200, 210, 255, 220))
    # 右肩
    for i, (sx, ang) in enumerate([(190, -150), (184, -170), (178, 170)]):
        a = math.radians(ang - 90)
        tip_x = sx + int(16 * math.cos(a))
        tip_y = 10 + int(16 * math.sin(a))
        poly(dr, [(sx-5, 18),(sx+5, 18),(tip_x, tip_y)],
             fill=(120, 130, 170, 255))
        poly(dr, [(sx-3, 18),(sx+3, 18),(tip_x, tip_y)],
             fill=(200, 210, 255, 220))

    # ── 铆钉/装饰钉 ──
    for y_r in [20, 40, 68, 95, 122, 142]:
        for x_r in [8, 20, 188, 200]:
            circle(dr, x_r, y_r, 3.5, (180, 190, 220, 255))
            circle(dr, x_r+0.8, y_r+0.8, 1.5, (80, 85, 110, 255))

    # ── 头盔 ──
    # 头盔主体
    rect(dr, 50, 2, 158, 56, fill=(50, 15, 70, 255), radius=20)
    rect(dr, 52, 4, 156, 54, fill=(70, 22, 95, 255), radius=18)
    # 头盔分缝
    line(dr, 104, 2, 104, 35, (40, 10, 60, 200), 2)
    # 头盔脊（顶部）
    poly(dr, [(90,4),(104,0),(118,4),(114,14),(94,14)], fill=(100,110,145,255))
    poly(dr, [(96,3),(104,0),(112,3),(109,11),(99,11)], fill=(200,210,240,255))
    # 两侧尖角（恶魔角）
    poly(dr, [(55,10),(62,2),(68,12),(64,20),(58,18)], fill=(80,90,130,255))
    poly(dr, [(153,10),(146,2),(140,12),(144,20),(150,18)], fill=(80,90,130,255))
    # 角高光
    poly(dr, [(57,10),(62,3),(67,12),(63,18),(59,17)], fill=(160,170,200,180))
    poly(dr, [(151,10),(146,3),(141,12),(145,18),(149,17)], fill=(160,170,200,180))

    # ── 面罩（中央 T 形开口）──
    # 眼缝
    poly(dr, [(60,20),(82,18),(84,28),(60,30)], fill=(5,2,8,255))
    poly(dr, [(124,18),(146,20),(148,30),(124,28)], fill=(5,2,8,255))
    # 眼睛发光
    img = add_glow(img, px(71), px(24), px(10), (180, 80, 255, 120))
    img = add_glow(img, px(135), px(24), px(10), (180, 80, 255, 120))
    dr = ImageDraw.Draw(img)
    # 瞳孔
    circle(dr, 71, 24, 6, (220, 120, 255, 255))
    circle(dr, 71, 24, 3, (80, 10, 120, 255))
    circle(dr, 135, 24, 6, (220, 120, 255, 255))
    circle(dr, 135, 24, 3, (80, 10, 120, 255))
    # 眼睛高光
    circle(dr, 68, 21, 2, (255, 240, 255, 220))
    circle(dr, 132, 21, 2, (255, 240, 255, 220))
    # 鼻/面罩中缝
    rect(dr, 100, 22, 108, 40, fill=(10, 3, 15, 220), radius=2)
    # 口缝（齿状）
    for tx in range(58, 150, 8):
        poly(dr, [(tx, 40),(tx+4, 40),(tx+3, 46),(tx+1, 46)], fill=(5, 2, 8, 200))

    # ── 胸甲中央纹章 ──
    cx, cy = 104, 106
    # 六角盾牌底
    hex6 = [(cx, cy-28),(cx+24,cy-14),(cx+24,cy+14),(cx,cy+28),(cx-24,cy+14),(cx-24,cy-14)]
    poly(dr, hex6, fill=(35, 10, 50, 255))
    dr.polygon(px(hex6), outline=(160, 80, 200, 255), width=px(2))
    # 内层六角
    hex6b = [(cx, cy-20),(cx+17,cy-10),(cx+17,cy+10),(cx,cy+20),(cx-17,cy+10),(cx-17,cy-10)]
    poly(dr, hex6b, fill=(55, 15, 78, 255))

    # ── CORE 发光水晶 ──
    img = add_glow(img, px(cx), px(cy), px(22), (200, 50, 255, 150))
    img = add_glow(img, px(cx), px(cy), px(14), (255, 150, 255, 100))
    dr = ImageDraw.Draw(img)
    # 水晶主体（菱形）
    poly(dr, [(cx,cy-16),(cx+10,cy),(cx,cy+16),(cx-10,cy)], fill=(180, 40, 220, 255))
    # 水晶面
    poly(dr, [(cx,cy-16),(cx+10,cy),(cx+2,cy)], fill=(230, 120, 255, 220))
    poly(dr, [(cx,cy-16),(cx-10,cy),(cx-2,cy)], fill=(140, 20, 180, 200))
    poly(dr, [(cx,cy+16),(cx+10,cy),(cx+2,cy)], fill=(120, 10, 160, 200))
    # 水晶高光
    poly(dr, [(cx-4,cy-14),(cx,cy-16),(cx+4,cy-10)], fill=(255, 220, 255, 200))
    circle(dr, cx-3, cy-10, 2, (255, 255, 255, 180))

    # ── 腹甲分节 ──
    for seg_y in [58, 70, 82, 92]:
        line(dr, 35, seg_y, 173, seg_y, (45, 12, 65, 180), 2)
        # 节间铆钉
        for sx in [50, 78, 104, 130, 158]:
            circle(dr, sx, seg_y, 2.5, (130, 80, 160, 180))

    # ── 手臂装甲痕迹（两侧弧线） ──
    for side, xb in [(-1, 36), (1, 172)]:
        for ay in range(60, 145, 12):
            line(dr, xb, ay, xb + side * 8, ay+5, (100, 40, 130, 150), 2)

    # ── 底部爪子 ──
    for cx2 in [46, 76, 104, 132, 162]:
        # 爪底
        poly(dr, [(cx2-10,144),(cx2,140),(cx2+10,144),(cx2+6,156),(cx2-6,156)],
             fill=(40, 10, 58, 255))
        # 爪面
        poly(dr, [(cx2-7,144),(cx2,141),(cx2+7,144),(cx2+4,154),(cx2-4,154)],
             fill=(75, 22, 100, 255))
        # 爪尖亮
        line(dr, cx2-7, 144, cx2-4, 154, (160, 100, 200, 180), 1)
        line(dr, cx2+7, 144, cx2+4, 154, (160, 100, 200, 180), 1)

    # ── 外轮廓描边 ──
    rect(dr, 4, 6, 204, 150, outline=(200, 100, 255, 220), ow=2, radius=16)
    rect(dr, 6, 8, 202, 148, outline=(120, 50, 160, 120), ow=1, radius=14)

    # ── 缩小 ──
    out_img = img.resize((208, 156), Image.LANCZOS)

    # ── 调试格线（淡） ──
    gdr = ImageDraw.Draw(out_img)
    for col in range(1, 4):
        gdr.line([(col*52, 0),(col*52, 156)], fill=(120,60,180,40), width=1)
    for row in range(1, 3):
        gdr.line([(0, row*52),(208, row*52)], fill=(120,60,180,40), width=1)

    path = os.path.join(OUT, "boss_full.png")
    out_img.save(path)
    print("saved", path)

    # ── 受击叠加层 ──
    hit = Image.new("RGBA", (208,156), (0,0,0,0))
    hdr = ImageDraw.Draw(hit)
    hdr.rounded_rectangle([2,4,206,152], radius=14, fill=(220,100,255,100))
    hit.save(os.path.join(OUT, "boss_hit_overlay.png"))
    print("saved boss_hit_overlay.png")

def gen_bombs():
    bdir = os.path.join(OUT, "..", "bombs")
    os.makedirs(bdir, exist_ok=True)
    S = 6
    SZ = 32 * S

    configs = {
        "cross":   ((220,  40,  40), "+",  (255, 80, 80)),
        "scatter": ((255, 140,  13), "✦",  (255,200, 60)),
        "bounce":  (( 30, 210, 210), "~",  (100,255,255)),
        "pierce":  ((240, 230,  30), "↑",  (255,255,120)),
        "area":    ((180,  30, 220), "◼",  (220,100,255)),
    }

    for name, (col, sym, highlight) in configs.items():
        img = Image.new("RGBA", (SZ, SZ), (0,0,0,0))
        dr  = ImageDraw.Draw(img)
        cx = cy = SZ // 2
        r = SZ // 2 - 5*S

        # 阴影
        dr.ellipse([cx-r+2*S, cy-r+4*S, cx+r+2*S, cy+r+4*S], fill=(0,0,0,80))
        # 深色外圈
        dark = tuple(max(0,c-60) for c in col)
        dr.ellipse([cx-r, cy-r, cx+r, cy+r], fill=dark+(255,))
        # 主色
        dr.ellipse([cx-r+S, cy-r+S, cx+r-S, cy+r-S], fill=col+(255,))
        # 中等亮面
        mid = tuple(min(255, c+40) for c in col)
        dr.ellipse([cx-r+2*S, cy-r+2*S, cx+r-2*S, cy+r-2*S], fill=mid+(200,))
        # 高光
        dr.ellipse([cx-r+3*S, cy-r+2*S, cx-r+9*S, cy-r+7*S],
                   fill=(255,255,255,200))
        dr.ellipse([cx-r+4*S, cy-r+3*S, cx-r+7*S, cy-r+6*S],
                   fill=(255,255,255,240))

        # 引线（粗，有弯曲感）
        fuse_pts = [
            (int(cx + r*0.55), int(cy - r*0.75)),
            (int(cx + r*0.80), int(cy - r*1.0)),
            (int(cx + r*1.1 + 2*S), int(cy - r*1.25 - 2*S)),
        ]
        dr.line(fuse_pts, fill=(180,150,30,255), width=3*S)
        dr.line(fuse_pts, fill=(220,190,50,200), width=S)

        # 引线火花
        fsx, fsy = fuse_pts[-1]
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            length = S * (4 + (angle % 3))
            dr.line([fsx, fsy, int(fsx+length*math.cos(a)), int(fsy+length*math.sin(a))],
                    fill=(255,230,60,220), width=S)
        # 火花中心点
        dr.ellipse([fsx-2*S, fsy-2*S, fsx+2*S, fsy+2*S], fill=(255,255,180,255))

        out = img.resize((32,32), Image.LANCZOS)
        path = os.path.join(bdir, name+".png")
        out.save(path)
        print("saved", path)

if __name__ == "__main__":
    gen_boss()
    gen_bombs()
    print("All done!")
