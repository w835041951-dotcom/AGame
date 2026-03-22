"""
生成游戏所有剩余美术资源
- 扫雷格子（隐藏/翻开/数字）
- UI元素（HP条、倒计时框、边框）
- 爆炸特效 spritesheet
- 背景纹理
"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites")
S = 4  # 像素艺术缩放倍数

def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("saved", path)

def px(v):
    return int(v * S)

# ═══════════════════════════════════════
# 扫雷格子 52x52
# ═══════════════════════════════════════
def gen_mine_cells():
    SZ = 52 * S

    # ── 隐藏格（凸起立体感）──
    img = Image.new("RGBA", (SZ, SZ), (0,0,0,0))
    dr  = ImageDraw.Draw(img)
    # 底色
    dr.rounded_rectangle([0,0,SZ-1,SZ-1], radius=px(5), fill=(72,75,90,255))
    # 亮面（左上）
    dr.rounded_rectangle([0,0,SZ-1,SZ-1], radius=px(5), outline=(110,115,135,255), width=px(2))
    # 暗面（右下）
    dr.line([(px(2),SZ-px(2)),(SZ-px(2),SZ-px(2))], fill=(45,47,58,255), width=px(2))
    dr.line([(SZ-px(2),px(2)),(SZ-px(2),SZ-px(2))], fill=(45,47,58,255), width=px(2))
    # 表面纹理：细微噪点感
    for y in range(0, SZ, px(8)):
        for x in range(0, SZ, px(8)):
            if (x//px(8) + y//px(8)) % 2 == 0:
                dr.rectangle([x+px(1),y+px(1),x+px(3),y+px(3)], fill=(80,83,98,100))
    # 中央小图案
    cx = cy = SZ//2
    dr.line([(cx-px(8),cy),(cx+px(8),cy)], fill=(90,93,110,180), width=px(2))
    dr.line([(cx,cy-px(8)),(cx,cy+px(8))], fill=(90,93,110,180), width=px(2))
    out = img.resize((52,52), Image.LANCZOS)
    save(out, "ui", "cell_hidden.png")

    # ── 翻开格（凹陷感）──
    img = Image.new("RGBA", (SZ, SZ), (0,0,0,0))
    dr  = ImageDraw.Draw(img)
    dr.rounded_rectangle([0,0,SZ-1,SZ-1], radius=px(5), fill=(195,188,170,255))
    # 凹陷边框
    dr.rounded_rectangle([0,0,SZ-1,SZ-1], radius=px(5), outline=(155,148,130,255), width=px(2))
    dr.line([(px(2),SZ-px(2)),(SZ-px(2),SZ-px(2))], fill=(215,208,192,255), width=px(2))
    dr.line([(SZ-px(2),px(2)),(SZ-px(2),SZ-px(2))], fill=(215,208,192,255), width=px(2))
    # 细纹
    for y in range(0, SZ, px(6)):
        dr.line([(px(3),y),(SZ-px(3),y)], fill=(180,173,155,60), width=px(1))
    out = img.resize((52,52), Image.LANCZOS)
    save(out, "ui", "cell_revealed.png")

    # ── 爆炸格 ──
    img = Image.new("RGBA", (SZ, SZ), (0,0,0,0))
    dr  = ImageDraw.Draw(img)
    # 多层橙红渐变
    for r, col in [
        (SZ//2, (180,60,0,200)),
        (int(SZ*0.42), (220,90,0,220)),
        (int(SZ*0.34), (255,130,0,240)),
        (int(SZ*0.22), (255,200,50,255)),
        (int(SZ*0.12), (255,240,180,255)),
    ]:
        cx = cy = SZ//2
        dr.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)
    # 火焰锯齿
    for angle in range(0, 360, 30):
        a = math.radians(angle)
        r1, r2 = SZ*0.38, SZ*0.48
        x1 = cx + int(r1*math.cos(a)); y1 = cy + int(r1*math.sin(a))
        x2 = cx + int(r2*math.cos(a+math.radians(15))); y2 = cy + int(r2*math.sin(a+math.radians(15)))
        x3 = cx + int(r1*math.cos(a+math.radians(30))); y3 = cy + int(r1*math.sin(a+math.radians(30)))
        dr.polygon([(x1,y1),(x2,y2),(x3,y3)], fill=(255,180,20,200))
    out = img.resize((52,52), Image.LANCZOS)
    save(out, "ui", "cell_exploding.png")

# ═══════════════════════════════════════
# 爆炸特效 Spritesheet 416x52 (8帧×52px)
# ═══════════════════════════════════════
def gen_explosion_sheet():
    FRAMES = 8
    FW = 52 * S
    img = Image.new("RGBA", (FW * FRAMES, FW), (0,0,0,0))

    for f in range(FRAMES):
        t = f / (FRAMES - 1)
        frame = Image.new("RGBA", (FW, FW), (0,0,0,0))
        dr = ImageDraw.Draw(frame)
        cx = cy = FW // 2

        # 爆炸从小到大，透明度从高到低
        max_r = int(FW * 0.45 * (0.3 + 0.7 * t))
        alpha_base = int(255 * (1 - t * 0.8))

        # 外圈烟雾
        if t > 0.3:
            smoke_r = int(FW * 0.48 * t)
            smoke_a = int(100 * (1 - t))
            dr.ellipse([cx-smoke_r,cy-smoke_r,cx+smoke_r,cy+smoke_r],
                       fill=(80,60,50,smoke_a))

        # 火焰层
        layers = [
            (1.0,   (200, 60,  0)),
            (0.75,  (240,110,  0)),
            (0.55,  (255,170, 20)),
            (0.30,  (255,230,100)),
            (0.12,  (255,255,220)),
        ]
        for scale, color in layers:
            r = int(max_r * scale)
            a = min(255, int(alpha_base * 1.2))
            dr.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color+(a,))

        # 火花粒子
        if t < 0.7:
            for i in range(8):
                angle = math.radians(i * 45 + f * 20)
                dist  = int(FW * 0.35 * t)
                sx = cx + int(dist * math.cos(angle))
                sy = cy + int(dist * math.sin(angle))
                spark_r = max(1, int(FW * 0.04 * (1-t)))
                dr.ellipse([sx-spark_r,sy-spark_r,sx+spark_r,sy+spark_r],
                           fill=(255,240,100,alpha_base))

        frame_small = frame.resize((52, 52), Image.LANCZOS)
        img.paste(frame_small, (f * 52, 0), frame_small)

    save(img.resize((52*FRAMES, 52), Image.LANCZOS), "vfx", "explosion_strip8.png")

# ═══════════════════════════════════════
# 背景纹理 1280x720
# ═══════════════════════════════════════
def gen_background():
    W, H = 1280, 720
    img = Image.new("RGBA", (W, H), (0,0,0,255))
    dr  = ImageDraw.Draw(img)

    # 深色地牢砖块纹理
    brick_w, brick_h = 64, 32
    for row in range(H // brick_h + 1):
        for col in range(W // brick_w + 1):
            offset = (brick_w // 2) if row % 2 == 1 else 0
            x = col * brick_w - offset
            y = row * brick_h
            # 砖块颜色轻微随机
            shade = 14 + (row * 7 + col * 3) % 8
            dr.rectangle([x+1, y+1, x+brick_w-2, y+brick_h-2],
                         fill=(shade, shade-2, shade+2, 255))
            dr.rectangle([x, y, x+brick_w-1, y+brick_h-1],
                         outline=(10, 10, 12, 255), width=1)

    # 四周暗角渐变
    vignette = Image.new("RGBA", (W, H), (0,0,0,0))
    vdr = ImageDraw.Draw(vignette)
    for i in range(200):
        alpha = int(180 * (1 - i/200) ** 2)
        vdr.rectangle([i, i, W-i, H-i], outline=(0,0,0,alpha), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), vignette)

    save(img, "ui", "background.png")

# ═══════════════════════════════════════
# HUD 元素
# ═══════════════════════════════════════
def gen_hud():
    # HP心形图标 20x20
    s = 4
    sz = 20 * s
    img = Image.new("RGBA", (sz, sz), (0,0,0,0))
    dr  = ImageDraw.Draw(img)
    cx  = sz // 2
    # 心形两个圆 + 三角
    dr.ellipse([cx-sz//3-s, sz//5, cx-s, sz//5+sz//3], fill=(220,40,60,255))
    dr.ellipse([cx+s, sz//5, cx+sz//3+s, sz//5+sz//3], fill=(220,40,60,255))
    dr.polygon([(sz//8, sz//3),(sz*7//8, sz//3),(cx, sz-sz//8)], fill=(220,40,60,255))
    # 高光
    dr.ellipse([cx-sz//3+s, sz//5+s, cx-sz//8, sz//5+sz//6], fill=(255,120,140,180))
    out = img.resize((20,20), Image.LANCZOS)
    save(out, "ui", "icon_hp.png")

    # 炸弹库存图标 20x20
    img = Image.new("RGBA", (sz, sz), (0,0,0,0))
    dr  = ImageDraw.Draw(img)
    r   = sz//2 - 3*s
    dr.ellipse([sz//2-r, sz//2-r+2*s, sz//2+r, sz//2+r+2*s], fill=(30,30,30,255))
    dr.ellipse([sz//2-r, sz//2-r, sz//2+r, sz//2+r], fill=(50,50,55,255))
    dr.ellipse([sz//2-r+s, sz//2-r, sz//2+r-s, sz//2+r-s], fill=(80,80,85,200))
    dr.line([sz//2+int(r*0.5), sz//2-int(r*0.7), sz//2+r+2*s, sz//2-r-s],
            fill=(180,155,30,255), width=2*s)
    out = img.resize((20,20), Image.LANCZOS)
    save(out, "ui", "icon_bomb.png")

if __name__ == "__main__":
    gen_mine_cells()
    gen_explosion_sheet()
    gen_background()
    gen_hud()
    print("=== All assets generated ===")
