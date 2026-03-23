"""
Boss 像素艺术生成器 v5 — 20种Boss独立纹理
每个Boss一张atlas贴图，Cell.gd按local坐标裁切
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "boss")
os.makedirs(OUT, exist_ok=True)

SCALE = 6
CELL_PX = 64  # 每格最终像素

random.seed(42)

# ── 20种Boss的配色方案 ──
BOSS_CONFIGS = {
    # --- 第一幕 (1-5) ---
    "gargoyle": {
        "cols": 5, "rows": 4,
        "shape": [(1,0),(3,0),(1,1),(2,1),(3,1),(1,2),(2,2),(3,2),(2,3)],
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
        "cols": 7, "rows": 5,
        "shape": [(2,0),(3,0),(4,0),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(5,2),
                  (0,3),(3,3),(6,3),(1,4),(3,4),(5,4)],
        "body":  (85, 82, 70),    # 骨白色
        "dark":  (42, 40, 35),
        "crack": (50, 48, 42),
        "glow":  (220, 200, 120), # 骨黄光
        "eye":   (240, 220, 140),
        "rune":  (200, 180, 100),
        "accent":(160, 140, 80),
    },
    "demon": {
        "cols": 6, "rows": 5,
        "shape": [(0,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),
                  (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(2,4),(3,4)],
        "body":  (80, 25, 20),    # 深渊暗红
        "dark":  (40, 10, 8),
        "crack": (50, 15, 12),
        "glow":  (255, 40, 30),   # 血红光
        "eye":   (255, 60, 40),
        "rune":  (220, 30, 20),
        "accent":(180, 20, 15),
    },
    # --- 第二幕 (6-10) ---
    "witch": {
        "cols": 5, "rows": 5,
        "shape": [(2,0),(1,1),(2,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),
                  (1,3),(2,3),(3,3),(2,4)],
        "body":  (160, 200, 230),  # 冰蓝色
        "dark":  (60, 80, 110),
        "crack": (80, 100, 130),
        "glow":  (100, 200, 255),  # 冰霜光
        "eye":   (140, 220, 255),
        "rune":  (80, 180, 240),
        "accent":(60, 150, 220),
    },
    "wyvern": {
        "cols": 7, "rows": 3,
        "shape": [(0,0),(3,0),(6,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
                  (1,2),(2,2),(3,2),(4,2),(5,2)],
        "body":  (35, 80, 65),    # 暗翠绿
        "dark":  (15, 40, 30),
        "crack": (25, 50, 40),
        "glow":  (0, 255, 180),   # 翠光
        "eye":   (40, 255, 200),
        "rune":  (0, 220, 150),
        "accent":(0, 180, 120),
    },
    "kraken": {
        "cols": 5, "rows": 4,
        "shape": [(0,0),(2,0),(4,0),(1,1),(2,1),(3,1),
                  (1,2),(2,2),(3,2),(0,3),(2,3),(4,3)],
        "body":  (25, 40, 70),    # 深海蓝
        "dark":  (10, 18, 35),
        "crack": (15, 25, 45),
        "glow":  (0, 150, 255),   # 深海光
        "eye":   (40, 180, 255),
        "rune":  (0, 120, 220),
        "accent":(0, 100, 190),
    },
    "golem": {
        "cols": 5, "rows": 4,
        "shape": [(0,0),(1,0),(3,0),(4,0),(1,1),(2,1),(3,1),
                  (1,2),(2,2),(3,2),(0,3),(1,3),(3,3),(4,3)],
        "body":  (110, 115, 120),  # 钢铁灰
        "dark":  (50, 52, 55),
        "crack": (60, 62, 65),
        "glow":  (255, 200, 80),   # 熔铁金
        "eye":   (255, 220, 100),
        "rune":  (230, 180, 60),
        "accent":(200, 150, 40),
    },
    "wolf": {
        "cols": 6, "rows": 5,
        "shape": [(3,0),(2,1),(3,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),
                  (2,3),(3,3),(4,3),(3,4)],
        "body":  (80, 25, 25),    # 暗血红
        "dark":  (40, 10, 10),
        "crack": (50, 15, 15),
        "glow":  (255, 50, 50),   # 血光
        "eye":   (255, 80, 60),
        "rune":  (220, 40, 40),
        "accent":(180, 30, 30),
    },
    # --- 第三幕 (11-15) ---
    "titan": {
        "cols": 7, "rows": 5,
        "shape": [(0,0),(6,0),(0,1),(1,1),(5,1),(6,1),
                  (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
                  (0,3),(1,3),(5,3),(6,3),(0,4),(6,4)],
        "body":  (70, 80, 110),    # 雷暴蓝灰
        "dark":  (30, 35, 55),
        "crack": (40, 45, 65),
        "glow":  (80, 180, 255),   # 电光蓝
        "eye":   (120, 200, 255),
        "rune":  (60, 160, 240),
        "accent":(40, 140, 220),
    },
    "mushroom": {
        "cols": 5, "rows": 5,
        "shape": [(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),
                  (1,2),(2,2),(3,2),(2,3),(1,4),(2,4),(3,4)],
        "body":  (60, 75, 35),    # 毒绿褐
        "dark":  (28, 38, 15),
        "crack": (35, 45, 20),
        "glow":  (120, 255, 40),  # 毒光绿
        "eye":   (150, 255, 60),
        "rune":  (100, 220, 30),
        "accent":(80, 190, 20),
    },
    "crystal": {
        "cols": 5, "rows": 5,
        "shape": [(1,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(3,2),
                  (0,3),(1,3),(2,3),(3,3),(4,3),(2,4)],
        "body":  (40, 100, 110),   # 水晶青
        "dark":  (15, 45, 50),
        "crack": (25, 60, 65),
        "glow":  (0, 255, 220),    # 水晶光
        "eye":   (60, 255, 240),
        "rune":  (0, 220, 190),
        "accent":(0, 190, 160),
    },
    "assassin": {
        "cols": 5, "rows": 5,
        "shape": [(0,0),(4,0),(0,1),(1,1),(3,1),(4,1),
                  (1,2),(2,2),(3,2),(0,3),(1,3),(3,3),(4,3),(0,4),(4,4)],
        "body":  (40, 40, 45),    # 暗影灰
        "dark":  (18, 18, 22),
        "crack": (28, 28, 32),
        "glow":  (200, 50, 255),  # 暗影紫
        "eye":   (230, 80, 255),
        "rune":  (180, 40, 230),
        "accent":(150, 30, 200),
    },
    "phoenix": {
        "cols": 7, "rows": 5,
        "shape": [(0,0),(6,0),(0,1),(1,1),(5,1),(6,1),
                  (1,2),(2,2),(3,2),(4,2),(5,2),(2,3),(3,3),(4,3),(3,4)],
        "body":  (120, 80, 20),    # 火焰金棕
        "dark":  (60, 35, 8),
        "crack": (70, 45, 12),
        "glow":  (255, 200, 40),   # 烈焰金
        "eye":   (255, 220, 80),
        "rune":  (255, 180, 30),
        "accent":(230, 150, 20),
    },
    # --- 第四幕 (16-20) ---
    "lich": {
        "cols": 6, "rows": 5,
        "shape": [(1,0),(2,0),(3,0),(4,0),(2,1),(3,1),
                  (1,2),(2,2),(3,2),(4,2),(2,3),(3,3),
                  (1,4),(2,4),(3,4),(4,4)],
        "body":  (40, 60, 35),    # 亡灵绿
        "dark":  (18, 30, 15),
        "crack": (25, 38, 20),
        "glow":  (100, 255, 80),  # 魂火绿
        "eye":   (130, 255, 100),
        "rune":  (80, 230, 60),
        "accent":(60, 200, 40),
    },
    "void": {
        "cols": 5, "rows": 5,
        "shape": [(0,0),(2,0),(4,0),(1,1),(2,1),(3,1),
                  (0,2),(1,2),(2,2),(3,2),(4,2),(1,3),(2,3),(3,3),
                  (0,4),(4,4)],
        "body":  (50, 20, 70),    # 虚空紫
        "dark":  (22, 8, 30),
        "crack": (30, 12, 40),
        "glow":  (180, 80, 255),  # 虚空光
        "eye":   (210, 110, 255),
        "rune":  (160, 60, 230),
        "accent":(130, 40, 200),
    },
    "eagle": {
        "cols": 8, "rows": 4,
        "shape": [(0,0),(3,0),(4,0),(7,0),
                  (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),
                  (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(3,3),(4,3)],
        "body":  (90, 95, 105),    # 暴风灰白
        "dark":  (40, 42, 48),
        "crack": (50, 52, 58),
        "glow":  (200, 220, 255),  # 风暴白光
        "eye":   (220, 235, 255),
        "rune":  (180, 200, 240),
        "accent":(150, 170, 220),
    },
    "chaos": {
        "cols": 7, "rows": 5,
        "shape": [(0,0),(3,0),(6,0),(1,1),(2,1),(3,1),(4,1),(5,1),
                  (2,2),(3,2),(4,2),(1,3),(2,3),(3,3),(4,3),(5,3),
                  (0,4),(3,4),(6,4)],
        "body":  (65, 15, 15),    # 混沌暗赤
        "dark":  (30, 5, 5),
        "crack": (40, 8, 8),
        "glow":  (255, 40, 60),   # 混沌赤光
        "eye":   (255, 70, 80),
        "rune":  (230, 30, 50),
        "accent":(200, 20, 40),
    },
    "enddragon": {
        "cols": 8, "rows": 4,
        "shape": [(1,0),(2,0),(5,0),(6,0),
                  (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),
                  (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
                  (2,3),(3,3),(4,3),(5,3)],
        "body":  (85, 70, 30),    # 古龙暗金
        "dark":  (40, 32, 12),
        "crack": (50, 40, 16),
        "glow":  (255, 220, 100),  # 古龙金光
        "eye":   (255, 240, 130),
        "rune":  (230, 200, 80),
        "accent":(200, 170, 60),
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

def _row_spans(shape_list):
    rows = {}
    for x, y in shape_list:
        rows.setdefault(y, []).append(x)
    spans = []
    for y, xs in rows.items():
        xs = sorted(xs)
        start = xs[0]
        prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            spans.append({"y": y, "start": start, "end": prev, "width": prev - start + 1})
            start = x
            prev = x
        spans.append({"y": y, "start": start, "end": prev, "width": prev - start + 1})
    return spans

def _choose_face_span(shape_list, min_y):
    """Pick best row for face — prefer upper body, wide spans."""
    max_y = max(p[1] for p in shape_list)
    height = max_y - min_y + 1
    spans = _row_spans(shape_list)
    for min_w in [3, 2]:
        for ratio in [0.35, 0.55, 0.75, 1.0]:
            cutoff = min_y + max(1, int(height * ratio))
            cands = [s for s in spans if s["y"] <= cutoff and s["width"] >= min_w]
            if cands:
                cands.sort(key=lambda s: (s["y"], -s["width"]))
                return cands[0]
    spans.sort(key=lambda s: (-s["width"], s["y"]))
    return spans[0]

def _choose_mouth_span(shape_list, face_span):
    spans = _row_spans(shape_list)
    candidates = []
    for span in spans:
        if span["y"] < face_span["y"]:
            continue
        overlap_start = max(span["start"], face_span["start"])
        overlap_end = min(span["end"], face_span["end"])
        overlap = overlap_end - overlap_start + 1
        if overlap > 0:
            candidates.append({
                "y": span["y"],
                "start": overlap_start,
                "end": overlap_end,
                "width": overlap,
            })
    if not candidates:
        return {"y": face_span["y"], "start": face_span["start"], "end": face_span["end"], "width": face_span["width"]}
    candidates.sort(key=lambda s: (0 if s["y"] == face_span["y"] + 1 else 1, -s["width"], s["y"]))
    return candidates[0]

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
    """Draw face (eyes + mouth) strictly clipped to body cells."""
    glow_c = cfg["glow"]
    eye_c = cfg["eye"]
    body = cfg["body"]

    # ── Build body mask for clipping ──
    body_mask = Image.new("L", img.size, 0)
    bm_dr = ImageDraw.Draw(body_mask)
    for (cx, cy) in shape:
        x0, y0 = px(cx * cell), px(cy * cell)
        x1, y1 = px((cx + 1) * cell), px((cy + 1) * cell)
        bm_dr.rectangle([x0, y0, x1, y1], fill=255)

    # ── Face layer (all face features drawn here, clipped later) ──
    face = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(face)

    min_y = min(p[1] for p in shape_list)
    face_span = _choose_face_span(shape_list, min_y)
    face_cells = [(x, face_span["y"]) for x in range(face_span["start"], face_span["end"] + 1)]

    # ── Eye cell selection ──
    if len(face_cells) >= 5:
        eye_left = face_cells[1]
        eye_right = face_cells[-2]
    elif len(face_cells) >= 3:
        eye_left = face_cells[0]
        eye_right = face_cells[-1]
    elif len(face_cells) == 2:
        eye_left = face_cells[0]
        eye_right = face_cells[1]
    else:
        eye_left = face_cells[0]
        eye_right = face_cells[0]

    eye_inset = 0.34 if len(face_cells) <= 2 else 0.5
    if eye_left == eye_right:
        eye_positions = [
            ((eye_left[0] + 0.35) * cell, (eye_left[1] + 0.46) * cell),
            ((eye_right[0] + 0.65) * cell, (eye_right[1] + 0.46) * cell),
        ]
    else:
        eye_positions = [
            ((eye_left[0] + eye_inset) * cell, (eye_left[1] + 0.46) * cell),
            ((eye_right[0] + (1.0 - eye_inset)) * cell, (eye_right[1] + 0.46) * cell),
        ]

    # ── Draw eyes on face layer ──
    eye_socket_w = min(14, max(9, int(cell * 0.13)))
    eye_socket_h = min(10, max(7, int(cell * 0.09)))
    eye_outer_r = min(7, max(5, int(cell * 0.11)))
    eye_inner_r = max(3, eye_outer_r - 3)
    eye_highlight_r = max(1.5, eye_inner_r * 0.4)

    for ex, ey in eye_positions:
        bg_c = tuple(max(0, c - 15) for c in body)
        rect(dr, ex - eye_socket_w, ey - eye_socket_h,
             ex + eye_socket_w, ey + eye_socket_h, fill=bg_c + (255,), radius=8)
        rect(dr, ex - eye_socket_w + 2, ey - eye_socket_h + 2,
             ex + eye_socket_w - 2, ey + eye_socket_h - 2, fill=(8, 8, 12, 255), radius=7)
        face = add_glow(face, px(ex), px(ey), px(10), glow_c + (140,))
        dr = ImageDraw.Draw(face)
        circle(dr, ex, ey, eye_outer_r, eye_c + (255,))
        bright = (min(255, eye_c[0]+100), min(255, eye_c[1]+100), min(255, eye_c[2]+100))
        circle(dr, ex, ey, eye_inner_r, bright + (255,))
        circle(dr, ex - eye_outer_r * 0.35, ey - eye_outer_r * 0.35,
               eye_highlight_r, (255, 255, 255, 220))

    # ── Mouth on face layer ──
    mouth_span = _choose_mouth_span(shape_list, face_span)
    mouth_cells = [(x, mouth_span["y"]) for x in range(mouth_span["start"], mouth_span["end"] + 1)]

    if mouth_cells:
        max_cells = 3 if len(mouth_cells) >= 3 else len(mouth_cells)
        mouth_mid = len(mouth_cells) // 2
        mouth_start = max(0, mouth_mid - (max_cells // 2))
        mouth_end = mouth_start + max_cells
        mouth_cells = mouth_cells[mouth_start:mouth_end]

        mx_left = (mouth_cells[0][0] + 0.24) * cell
        mx_right = (mouth_cells[-1][0] + 0.76) * cell
        my = (mouth_cells[0][1] + 0.68) * cell
        mouth_h = min(12, max(8, int(cell * 0.18)))

        bg_c = tuple(max(0, c - 15) for c in body)
        rect(dr, mx_left - 3, my - mouth_h * 0.5 - 2, mx_right + 3, my + mouth_h * 0.5 + 2,
             fill=bg_c + (255,), radius=4)
        rect(dr, mx_left, my - mouth_h * 0.5, mx_right, my + mouth_h * 0.5,
             fill=(12, 8, 14, 255), radius=4)
        rect(dr, mx_left + 3, my - mouth_h * 0.25, mx_right - 3, my + mouth_h * 0.25,
             fill=(60, 10, 10, 200), radius=2)

        tooth_w = min(7, max(5, int(cell * 0.1)))
        n_teeth = max(2, int((mx_right - mx_left) / (tooth_w + 4)))
        spacing = (mx_right - mx_left) / n_teeth
        for i in range(n_teeth):
            tx = mx_left + i * spacing + spacing * 0.22
            poly(dr, [(tx, my - mouth_h * 0.5),
                      (tx + tooth_w * 0.5, my - mouth_h * 0.5 + 7),
                      (tx + tooth_w, my - mouth_h * 0.5)],
                 fill=(210, 210, 195, 255))
            poly(dr, [(tx + spacing * 0.08, my + mouth_h * 0.5),
                      (tx + tooth_w * 0.5, my + mouth_h * 0.5 - 6),
                      (tx + tooth_w - spacing * 0.08, my + mouth_h * 0.5)],
                 fill=(190, 190, 175, 255))

    # ── Clip face layer to body mask, composite ──
    face_a = face.split()[3]
    clipped_a = ImageChops.multiply(face_a, body_mask)
    face.putalpha(clipped_a)
    return Image.alpha_composite(img, face)

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
