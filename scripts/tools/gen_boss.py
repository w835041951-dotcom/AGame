"""
Boss 像素艺术生成器 v4 — 每种Boss独立纹理
按形状大小生成：石像鬼3x3, 影蛛5x3, 熔岩巨蛇4x4, 骸骨巨人5x5, 深渊魔王6x4
每个Boss一张atlas贴图，Cell.gd按local坐标裁切
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

SCALE = 6
CELL_PX = 64  # 每格最终像素

random.seed(42)

# ── 5种Boss的配色方案 ──
BOSS_CONFIGS = {
    "gargoyle": {
        "cols": 3, "rows": 3,
        "shape": [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(0,2),(1,2),(2,2)],
        "body":  (72, 78, 85),    # 灰石色
        "dark":  (35, 38, 42),
        "crack": (40, 42, 48),
        "glow":  (60, 255, 120),  # 绿色灵光
        "eye":   (80, 255, 130),
        "rune":  (60, 220, 100),
        "accent":(50, 180, 80),
    },
    "spider": {
        "cols": 5, "rows": 3,
        "shape": [(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(3,2)],
        "body":  (60, 45, 75),    # 暗紫色
        "dark":  (30, 22, 40),
        "crack": (40, 30, 50),
        "glow":  (180, 60, 255),  # 紫色毒光
        "eye":   (220, 50, 255),
        "rune":  (160, 40, 220),
        "accent":(120, 30, 180),
    },
    "serpent": {
        "cols": 4, "rows": 4,
        "shape": [(0,0),(1,0),(2,0),(3,0),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3)],
        "body":  (95, 55, 30),    # 熔岩橙棕
        "dark":  (50, 25, 12),
        "crack": (60, 30, 15),
        "glow":  (255, 120, 20),  # 熔岩橙
        "eye":   (255, 160, 40),
        "rune":  (255, 100, 10),
        "accent":(200, 80, 10),
    },
    "giant": {
        "cols": 5, "rows": 5,
        "shape": [(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(3,2),
                  (0,3),(1,3),(2,3),(3,3),(4,3),(1,4),(2,4),(3,4)],
        "body":  (85, 82, 70),    # 骨白色
        "dark":  (42, 40, 35),
        "crack": (50, 48, 42),
        "glow":  (220, 200, 120), # 骨黄光
        "eye":   (240, 220, 140),
        "rune":  (200, 180, 100),
        "accent":(160, 140, 80),
    },
    "demon": {
        "cols": 6, "rows": 4,
        "shape": [(0,0),(1,0),(4,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),
                  (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(1,3),(2,3),(3,3),(4,3)],
        "body":  (80, 25, 20),    # 深渊暗红
        "dark":  (40, 10, 8),
        "crack": (50, 15, 12),
        "glow":  (255, 40, 30),   # 血红光
        "eye":   (255, 60, 40),
        "rune":  (220, 30, 20),
        "accent":(180, 20, 15),
    },
}

def px(v):
    if isinstance(v, (list, tuple)) and len(v) > 0 and not isinstance(v[0], (int, float)):
        return [(int(x * SCALE), int(y * SCALE)) for x, y in v]
    if isinstance(v, (list, tuple)):
        return [int(x * SCALE) for x in v]
    return int(v * SCALE)

def circle(dr, cx, cy, r, fill, outline=None, ow=1):
    dr.ellipse([px(cx - r), px(cy - r), px(cx + r), px(cy + r)], fill=fill,
               outline=outline, width=px(ow) if outline else 0)

def rect(dr, x0, y0, x1, y1, fill=None, outline=None, ow=1, radius=0):
    dr.rounded_rectangle([px(x0), px(y0), px(x1), px(y1)],
                         radius=px(radius), fill=fill,
                         outline=outline, width=px(ow) if outline else 0)

def poly(dr, pts, fill, outline=None, ow=1):
    dr.polygon(px(pts), fill=fill, outline=outline, width=px(ow) if outline else 0)

def line(dr, x0, y0, x1, y1, fill, w=1):
    dr.line([px(x0), px(y0), px(x1), px(y1)], fill=fill, width=px(w))

def add_glow(img, cx, cy, r, color, steps=12):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdr = ImageDraw.Draw(glow)
    for i in range(steps, 0, -1):
        alpha = int(color[3] * (i / steps) ** 2)
        rad = int(r * i / steps)
        c = color[:3] + (alpha,)
        gdr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=c)
    return Image.alpha_composite(img, glow)

def stone_noise(dr, x0, y0, x1, y1, base_color, density=0.3):
    for y in range(y0, y1, px(2)):
        for x in range(x0, x1, px(2)):
            if random.random() < density:
                shade = random.randint(-15, 15)
                c = tuple(max(0, min(255, base_color[i] + shade)) for i in range(3))
                dr.rectangle([x, y, x + px(2), y + px(2)], fill=c + (60,))

def gen_boss_sheet(name, cfg):
    """生成单个Boss的atlas贴图"""
    cols, rows = cfg["cols"], cfg["rows"]
    shape = set(cfg["shape"])
    W = cols * CELL_PX * SCALE
    H = rows * CELL_PX * SCALE
    final_w = cols * CELL_PX
    final_h = rows * CELL_PX

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    body = cfg["body"]
    dark = cfg["dark"]
    crack_c = cfg["crack"]
    glow_c = cfg["glow"]
    eye_c = cfg["eye"]
    rune_c = cfg["rune"]
    accent = cfg["accent"]

    cell = CELL_PX  # 64

    # ── 填充每个形状格子 ──
    for (cx, cy) in shape:
        x0 = cx * cell
        y0 = cy * cell
        x1 = x0 + cell
        y1 = y0 + cell
        # 深色底
        rect(dr, x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=dark + (255,), radius=4)
        # 主体填色
        rect(dr, x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill=body + (255,), radius=3)
        # 石头噪点
        stone_noise(dr, px(x0 + 3), px(y0 + 3), px(x1 - 3), px(y1 - 3), body, 0.25)

    shape_list = list(shape)
    avg_x = sum(p[0] for p in shape_list) / len(shape_list)
    avg_y = sum(p[1] for p in shape_list) / len(shape_list)

    # ── 中心符文（画在身体中部，避开脸部） ──
    min_y = min(p[1] for p in shape_list)
    # 中心符文选在avg_y之下的格子
    body_cells = [p for p in shape_list if p[1] > min_y + 1]
    if not body_cells:
        body_cells = [p for p in shape_list if p[1] > min_y]
    if not body_cells:
        body_cells = shape_list
    center_cell = min(body_cells, key=lambda p: (p[0]+0.5-avg_x)**2 + (p[1]+0.5-avg_y)**2)
    rcx = (center_cell[0] + 0.5) * cell
    rcy = (center_cell[1] + 0.5) * cell
    rr = 18
    for i in range(6):
        a1 = math.radians(60 * i - 90)
        a2 = math.radians(60 * (i + 1) - 90)
        x1r = rcx + rr * math.cos(a1)
        y1r = rcy + rr * math.sin(a1)
        x2r = rcx + rr * math.cos(a2)
        y2r = rcy + rr * math.sin(a2)
        line(dr, x1r, y1r, x2r, y2r, rune_c + (255,), 2)
    img = add_glow(img, px(rcx), px(rcy), px(16), glow_c + (100,))
    dr = ImageDraw.Draw(img)
    circle(dr, rcx, rcy, 6, accent + (255,))
    circle(dr, rcx - 2, rcy - 2, 2.5, (min(255,accent[0]+80), min(255,accent[1]+80), min(255,accent[2]+80), 200))

    # ── 裂纹 ──
    random.seed(hash(name))
    for _ in range(len(shape_list) * 2):
        cell_pick = random.choice(shape_list)
        sx = (cell_pick[0] + random.uniform(0.15, 0.85)) * cell
        sy = (cell_pick[1] + random.uniform(0.15, 0.85)) * cell
        for seg in range(random.randint(2, 4)):
            ex = sx + random.uniform(-18, 18)
            ey = sy + random.uniform(-18, 18)
            line(dr, sx, sy, ex, ey, crack_c + (180,), 2)
            line(dr, sx + 0.8, sy + 0.8, ex + 0.8, ey + 0.8, (min(255,crack_c[0]+50), min(255,crack_c[1]+50), min(255,crack_c[2]+50), 60), 1)
            sx, sy = ex, ey

    # ── 边缘符文小点 ──
    edge_cells = []
    for p in shape_list:
        neighbors = [(p[0]+dx, p[1]+dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]
        if any(n not in shape for n in neighbors):
            edge_cells.append(p)
    for ec in edge_cells[::2]:
        rx = (ec[0] + 0.5) * cell
        ry = (ec[1] + 0.5) * cell
        circle(dr, rx, ry, 4, glow_c[:3] + (80,))
        img = add_glow(img, px(rx), px(ry), px(6), glow_c + (40,))
        dr = ImageDraw.Draw(img)

    # ── 脸部（最后画，覆盖裂纹） ──
    img = _draw_face(img, cfg, shape, shape_list, avg_x, avg_y, cell)
    dr = ImageDraw.Draw(img)

    # ── 轮廓描边 ──
    for (cx2, cy2) in shape:
        x0 = cx2 * cell
        y0 = cy2 * cell
        x1 = x0 + cell
        y1 = y0 + cell
        rect(dr, x0 + 1, y0 + 1, x1 - 1, y1 - 1, outline=glow_c[:3] + (100,), ow=1, radius=4)

    # ── 缩小到最终尺寸 ──
    out_img = img.resize((final_w, final_h), Image.LANCZOS)
    gdr = ImageDraw.Draw(out_img)
    for col in range(1, cols):
        gdr.line([(col * CELL_PX, 0), (col * CELL_PX, final_h)], fill=glow_c[:3] + (25,), width=1)
    for row in range(1, rows):
        gdr.line([(0, row * CELL_PX), (final_w, row * CELL_PX)], fill=glow_c[:3] + (25,), width=1)

    path = os.path.join(OUT, f"boss_{name}.png")
    out_img.save(path)
    print(f"saved boss_{name}.png  ({final_w}x{final_h})")


def _draw_face(img, cfg, shape, shape_list, avg_x, avg_y, cell):
    """在Boss贴图上画眼睛+嘴巴，返回新img（因为add_glow创建新Image）"""
    dr = ImageDraw.Draw(img)
    glow_c = cfg["glow"]
    eye_c = cfg["eye"]
    body = cfg["body"]

    min_y = min(p[1] for p in shape_list)
    top_row = sorted([p for p in shape_list if p[1] == min_y], key=lambda p: p[0])

    # ── 选眼睛位置：取上排靠中心的两格 ──
    if len(top_row) >= 3:
        mid = len(top_row) // 2
        eye_left = top_row[mid - 1]
        eye_right = top_row[mid + 1] if mid + 1 < len(top_row) else top_row[mid]
    elif len(top_row) >= 2:
        eye_left = top_row[0]
        eye_right = top_row[-1]
    else:
        eye_left = top_row[0]
        eye_right = top_row[0]

    # ── 画两只眼睛 ──
    for ec in [eye_left, eye_right]:
        ex = (ec[0] + 0.5) * cell
        ey = (ec[1] + 0.35) * cell
        # 眼窝背景（覆盖裂纹）
        bg_c = tuple(max(0, c - 15) for c in body)
        rect(dr, ex - 18, ey - 13, ex + 18, ey + 13, fill=bg_c + (255,), radius=10)
        # 眼窝深凹
        rect(dr, ex - 15, ey - 10, ex + 15, ey + 10, fill=(8, 8, 12, 255), radius=8)
        # 发光
        img = add_glow(img, px(ex), px(ey), px(14), glow_c + (160,))
        dr = ImageDraw.Draw(img)
        # 眼球
        circle(dr, ex, ey, 9, eye_c + (255,))
        # 内瞳
        bright = (min(255, eye_c[0]+100), min(255, eye_c[1]+100), min(255, eye_c[2]+100))
        circle(dr, ex, ey, 5, bright + (255,))
        # 高光点
        circle(dr, ex - 3, ey - 3, 2.5, (255, 255, 255, 220))

    # ── 选嘴巴位置：眼睛下方一行 ──
    mouth_y = min_y + 1
    mouth_row = sorted([p for p in shape_list if p[1] == mouth_y], key=lambda p: p[0])
    if not mouth_row:
        mouth_row = top_row
        mouth_y = min_y
        mouth_vert_offset = 0.78
    else:
        mouth_vert_offset = 0.35

    # 嘴巴横跨中间1~3格
    mid = len(mouth_row) // 2
    m_start = max(0, mid - 1)
    m_end = min(len(mouth_row), mid + 2)
    mouth_cells = mouth_row[m_start:m_end]

    if mouth_cells:
        mx_left = (mouth_cells[0][0] + 0.12) * cell
        mx_right = (mouth_cells[-1][0] + 0.88) * cell
        my = (mouth_cells[0][1] + mouth_vert_offset) * cell
        mouth_h = 16

        # 嘴巴背景（覆盖裂纹）
        bg_c = tuple(max(0, c - 15) for c in body)
        rect(dr, mx_left - 3, my - mouth_h * 0.5 - 3, mx_right + 3, my + mouth_h * 0.5 + 3,
             fill=bg_c + (255,), radius=4)
        # 嘴巴黑洞
        rect(dr, mx_left, my - mouth_h * 0.5, mx_right, my + mouth_h * 0.5,
             fill=(12, 8, 14, 255), radius=4)
        # 深红内腔
        rect(dr, mx_left + 4, my - mouth_h * 0.3, mx_right - 4, my + mouth_h * 0.3,
             fill=(60, 10, 10, 200), radius=2)

        # 上排尖牙
        tooth_w = 10
        n_teeth = max(3, int((mx_right - mx_left) / (tooth_w + 3)))
        spacing = (mx_right - mx_left) / n_teeth
        for i in range(n_teeth):
            tx = mx_left + i * spacing + spacing * 0.15
            poly(dr, [(tx, my - mouth_h * 0.5),
                      (tx + tooth_w * 0.5, my - mouth_h * 0.5 + 10),
                      (tx + tooth_w, my - mouth_h * 0.5)],
                 fill=(210, 210, 195, 255))
            poly(dr, [(tx + spacing * 0.08, my + mouth_h * 0.5),
                      (tx + tooth_w * 0.5, my + mouth_h * 0.5 - 8),
                      (tx + tooth_w - spacing * 0.08, my + mouth_h * 0.5)],
                 fill=(190, 190, 175, 255))

    return img

def gen_boss():
    """生成所有Boss贴图"""
    for name, cfg in BOSS_CONFIGS.items():
        gen_boss_sheet(name, cfg)
    # 通用受击叠加层（取最大尺寸）
    max_w = max(c["cols"] for c in BOSS_CONFIGS.values()) * CELL_PX
    max_h = max(c["rows"] for c in BOSS_CONFIGS.values()) * CELL_PX
    hit = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
    hdr = ImageDraw.Draw(hit)
    hdr.rounded_rectangle([2, 2, max_w-2, max_h-2], radius=10, fill=(255, 255, 255, 70))
    hit.save(os.path.join(OUT, "boss_hit_overlay.png"))
    print("saved boss_hit_overlay.png")
def gen_bombs():
    """地牢像素风炸弹图标 32x32 — 圆形炸弹+不同符文标记"""
    bdir = os.path.join(OUT, "..", "bombs")
    os.makedirs(bdir, exist_ok=True)
    S = 6
    SZ = 32 * S

    configs = {
        "cross":   {"body": (55, 55, 60), "rune": (255, 60, 50),  "glow": (255, 80, 60, 120)},
        "scatter": {"body": (55, 55, 60), "rune": (255, 180, 40), "glow": (255, 200, 60, 120)},
        "bounce":  {"body": (55, 55, 60), "rune": (40, 220, 220), "glow": (60, 240, 240, 120)},
        "pierce":  {"body": (55, 55, 60), "rune": (240, 240, 60), "glow": (255, 255, 80, 120)},
        "area":    {"body": (55, 55, 60), "rune": (200, 60, 255), "glow": (220, 80, 255, 120)},
    }

    for name, cfg in configs.items():
        img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        cx = cy = SZ // 2
        r = SZ // 2 - 4 * S

        # 阴影
        dr.ellipse([cx - r + 2 * S, cy - r + 4 * S, cx + r + 2 * S, cy + r + 4 * S],
                   fill=(0, 0, 0, 60))
        # 深色外圈（铁壳）
        dark = tuple(max(0, c - 25) for c in cfg["body"])
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark + (255,))
        # 主体
        dr.ellipse([cx - r + S, cy - r + S, cx + r - S, cy + r - S], fill=cfg["body"] + (255,))
        # 噪点质感
        for _ in range(80):
            nx = random.randint(cx - r + 2 * S, cx + r - 2 * S)
            ny = random.randint(cy - r + 2 * S, cy + r - 2 * S)
            sh = random.randint(-10, 10)
            nc = tuple(max(0, min(255, cfg["body"][i] + sh)) for i in range(3))
            dr.rectangle([nx, ny, nx + S, ny + S], fill=nc + (50,))
        # 高光
        dr.ellipse([cx - r + 3 * S, cy - r + 2 * S, cx - r + 9 * S, cy - r + 7 * S],
                   fill=(255, 255, 255, 140))
        dr.ellipse([cx - r + 4 * S, cy - r + 3 * S, cx - r + 7 * S, cy - r + 5 * S],
                   fill=(255, 255, 255, 200))

        # 发光符文（每种炸弹不同）
        rc = cfg["rune"]
        img = add_glow(img, cx, cy, int(r * 0.6), cfg["glow"])
        dr = ImageDraw.Draw(img)

        if name == "cross":
            line(dr, cx // S - 6, cy // S, cx // S + 6, cy // S, rc + (255,), 2)
            line(dr, cx // S, cy // S - 6, cx // S, cy // S + 6, rc + (255,), 2)
        elif name == "scatter":
            for angle in range(0, 360, 60):
                a = math.radians(angle)
                ex = cx + int(r * 0.4 * math.cos(a))
                ey = cy + int(r * 0.4 * math.sin(a))
                dr.ellipse([ex - S, ey - S, ex + S, ey + S], fill=rc + (255,))
        elif name == "bounce":
            pts = []
            for i in range(5):
                a = math.radians(i * 72 - 90)
                pts.append((cx + int(r * 0.45 * math.cos(a)), cy + int(r * 0.45 * math.sin(a))))
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                dr.line([x0, y0, x1, y1], fill=rc + (255,), width=int(1.5 * S))
        elif name == "pierce":
            # 向上箭头
            poly(dr, [
                (cx // S, cy // S - 7),
                (cx // S + 5, cy // S),
                (cx // S + 2, cy // S),
                (cx // S + 2, cy // S + 6),
                (cx // S - 2, cy // S + 6),
                (cx // S - 2, cy // S),
                (cx // S - 5, cy // S),
            ], fill=rc + (255,))
        elif name == "area":
            rect(dr, cx // S - 5, cy // S - 5, cx // S + 5, cy // S + 5,
                 fill=None, outline=rc + (255,), ow=2, radius=1)
            rect(dr, cx // S - 3, cy // S - 3, cx // S + 3, cy // S + 3,
                 fill=rc + (200,), radius=0)

        # 引线
        fuse_pts = [
            (int(cx + r * 0.5), int(cy - r * 0.7)),
            (int(cx + r * 0.75), int(cy - r * 0.95)),
            (int(cx + r * 1.0), int(cy - r * 1.15)),
        ]
        dr.line(fuse_pts, fill=(120, 100, 50, 255), width=2 * S)
        dr.line(fuse_pts, fill=(180, 150, 70, 200), width=S)

        # 引线火花
        fsx, fsy = fuse_pts[-1]
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            length = S * (3 + (angle % 3))
            dr.line([fsx, fsy, int(fsx + length * math.cos(a)), int(fsy + length * math.sin(a))],
                    fill=(255, 220, 60, 200), width=S)
        dr.ellipse([fsx - 2 * S, fsy - 2 * S, fsx + 2 * S, fsy + 2 * S],
                   fill=(255, 250, 180, 255))

        out = img.resize((32, 32), Image.LANCZOS)
        path = os.path.join(bdir, name + ".png")
        out.save(path)
        print("saved", path)


if __name__ == "__main__":
    gen_boss()
    gen_bombs()
    print("All done!")
