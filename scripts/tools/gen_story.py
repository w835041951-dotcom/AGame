"""
生成游戏开始界面和故事过场的 8-bit 风格图片
输出到 assets/sprites/story/ 和 assets/sprites/ui/
"""

from PIL import Image, ImageDraw, ImageFont
import os, math, random

OUT_STORY = "assets/sprites/story"
OUT_UI    = "assets/sprites/ui"
os.makedirs(OUT_STORY, exist_ok=True)
os.makedirs(OUT_UI,    exist_ok=True)

W, H = 640, 360   # 16:9，像素风分辨率（Godot 缩放到 1920x1080）

# ── 调色板（深色地牢 8-bit）──────────────────────────────────
BG_DEEP   = (8,   6,  14)
BG_DARK   = (18,  14,  28)
STONE     = (52,  48,  64)
STONE_LT  = (82,  76,  96)
GOLD      = (242, 196,  60)
GOLD_DK   = (160, 120,  20)
RED       = (210,  48,  48)
RED_LT    = (240,  90,  80)
GREEN     = (60,  200,  80)
GREEN_DK  = (30,  120,  40)
BLUE      = (60,  120, 220)
BLUE_LT   = (100, 180, 255)
PURPLE    = (140,  60, 200)
PURPLE_LT = (200, 120, 255)
WHITE     = (240, 235, 220)
GRAY      = (140, 134, 150)
ORANGE    = (230, 140,  40)
PINK      = (240, 140, 180)
CYAN      = ( 60, 210, 210)
BLACK     = (  0,   0,   0)

# ── 像素画工具 ────────────────────────────────────────────────

def new_img():
    img = Image.new("RGB", (W, H), BG_DEEP)
    return img, ImageDraw.Draw(img)

def px(d, x, y, col, s=2):
    """画一个像素块（s=像素大小）"""
    d.rectangle([x*s, y*s, x*s+s-1, y*s+s-1], fill=col)

def rect(d, x1, y1, x2, y2, col, s=2):
    d.rectangle([x1*s, y1*s, x2*s+s-1, y2*s+s-1], fill=col)

def hline(d, x1, x2, y, col, s=2):
    rect(d, x1, y, x2, y, col, s)

def vline(d, x, y1, y2, col, s=2):
    rect(d, x, y1, x, y2, col, s)

def draw_text_8bit(d, text, x, y, col=WHITE, scale=1):
    """简单像素字体（5x7）"""
    FONT5 = {
        'A':[(1,0),(2,0),(0,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(3,3),(0,4),(3,4)],
        'B':[(0,0),(1,0),(2,0),(0,1),(3,1),(0,2),(1,2),(2,2),(0,3),(3,3),(0,4),(1,4),(2,4)],
        'C':[(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(1,4),(2,4),(3,4)],
        'D':[(0,0),(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(3,3),(0,4),(1,4),(2,4)],
        'E':[(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(0,3),(0,4),(1,4),(2,4),(3,4)],
        'F':[(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(0,3),(0,4)],
        'G':[(1,0),(2,0),(3,0),(0,1),(0,2),(2,2),(3,2),(0,3),(3,3),(1,4),(2,4),(3,4)],
        'H':[(0,0),(3,0),(0,1),(3,1),(0,2),(1,2),(2,2),(3,2),(0,3),(3,3),(0,4),(3,4)],
        'I':[(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
        'J':[(2,0),(3,0),(3,1),(3,2),(0,3),(3,3),(1,4),(2,4)],
        'K':[(0,0),(3,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(3,4)],
        'L':[(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4)],
        'M':[(0,0),(4,0),(0,1),(1,1),(3,1),(4,1),(0,2),(2,2),(4,2),(0,3),(4,3),(0,4),(4,4)],
        'N':[(0,0),(3,0),(0,1),(1,1),(3,1),(0,2),(2,2),(3,2),(0,3),(3,3),(0,4),(3,4)],
        'O':[(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(3,3),(1,4),(2,4)],
        'P':[(0,0),(1,0),(2,0),(0,1),(3,1),(0,2),(1,2),(2,2),(0,3),(0,4)],
        'Q':[(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(2,3),(3,3),(1,4),(2,4),(3,4)],
        'R':[(0,0),(1,0),(2,0),(0,1),(3,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(3,4)],
        'S':[(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(3,3),(0,4),(1,4),(2,4)],
        'T':[(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4)],
        'U':[(0,0),(3,0),(0,1),(3,1),(0,2),(3,2),(0,3),(3,3),(1,4),(2,4)],
        'V':[(0,0),(4,0),(0,1),(4,1),(1,2),(3,2),(1,3),(3,3),(2,4)],
        'W':[(0,0),(4,0),(0,1),(4,1),(0,2),(2,2),(4,2),(1,3),(3,3),(1,4),(3,4)],
        'X':[(0,0),(4,0),(1,1),(3,1),(2,2),(1,3),(3,3),(0,4),(4,4)],
        'Y':[(0,0),(4,0),(1,1),(3,1),(2,2),(2,3),(2,4)],
        'Z':[(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(1,3),(0,4),(1,4),(2,4),(3,4)],
        '0':[(1,0),(2,0),(0,1),(3,1),(0,2),(2,2),(3,2),(0,3),(3,3),(1,4),(2,4)],
        '1':[(1,0),(0,1),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
        '2':[(1,0),(2,0),(3,1),(2,2),(1,2),(0,3),(0,4),(1,4),(2,4),(3,4)],
        '3':[(0,0),(1,0),(2,0),(3,1),(1,2),(2,2),(3,3),(0,4),(1,4),(2,4)],
        '4':[(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(3,2),(2,3),(2,4)],
        '5':[(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(3,3),(0,4),(1,4),(2,4)],
        '6':[(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(0,3),(3,3),(1,4),(2,4)],
        '7':[(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(1,3),(1,4)],
        '8':[(1,0),(2,0),(0,1),(3,1),(1,2),(2,2),(0,3),(3,3),(1,4),(2,4)],
        '9':[(1,0),(2,0),(0,1),(3,1),(1,2),(2,2),(3,2),(3,3),(1,4),(2,4)],
        ' ':[], '!':[(1,0),(1,1),(1,2),(1,4)], '.':[(1,4)],
        ',':[(1,3),(0,4)], ':':[(1,1),(1,3)], '?':[(1,0),(2,0),(3,1),(2,2),(2,4)],
        '-':[(0,2),(1,2),(2,2),(3,2)], '/':[(3,0),(2,1),(2,2),(1,3),(0,4)],
        '~':[(0,1),(1,0),(2,1),(3,2),(4,1)],
    }
    cx = x
    for ch in text.upper():
        pts = FONT5.get(ch, [])
        for (fx, fy) in pts:
            d.rectangle(
                [(cx + fx*scale)*1, (y + fy*scale)*1,
                 (cx + fx*scale + scale - 1)*1, (y + fy*scale + scale - 1)*1],
                fill=col
            )
        cx += (5 + 1) * scale

# ── 绘制通用地牢背景 ─────────────────────────────────────────

def draw_dungeon_bg(d, dark=False):
    base = BG_DEEP if dark else BG_DARK
    d.rectangle([0, 0, W-1, H-1], fill=base)
    # 地板砖
    for ty in range(20, H//2, 20):
        for tx in range(0, W, 40):
            d.rectangle([tx, ty, tx+38, ty+18], fill=STONE)
            d.rectangle([tx+1, ty+1, tx+37, ty+17], fill=(STONE[0]+8, STONE[1]+8, STONE[2]+8))
    # 墙砖上半
    for ty in range(0, 22, 11):
        for tx in range(0 if ty%22==0 else 20, W, 40):
            d.rectangle([tx, ty, tx+38, ty+9], fill=(STONE[0]-10, STONE[1]-10, STONE[2]-5))
    # 顶部暗色
    d.rectangle([0, 0, W-1, 12], fill=(4, 3, 8))

def draw_stars(d, seed=42):
    rng = random.Random(seed)
    for _ in range(60):
        sx = rng.randint(0, W-1)
        sy = rng.randint(0, H//3)
        br = rng.randint(120, 240)
        d.point((sx, sy), fill=(br, br, br-20))

# ── 精灵：炸弹人（16x16 像素，居左上角参考） ─────────────────

def draw_bomber(d, ox, oy, s=3, facing=1):
    """facing: 1=右, -1=左"""
    # 身体（橙色工装）
    body = [
        "..OOOO..",
        ".OOOOOO.",
        ".OBBOOB.",  # B=按钮
        ".OOOOOO.",
        "..OOOO..",
        ".O.OO.O.",
        "#.####.#",
        "##.##.##",
    ]
    pal = {'.': None, 'O': ORANGE, 'B': (180,80,20), '#': (60,40,20)}
    # 头（肤色+头盔）
    head = [
        ".HHHH.",
        "HHWWHH",
        "H.WW.H",
        "HFFF.H",  # F=脸
        ".HHHH.",
    ]
    pal2 = {'.': None, 'H': (50,160,60), 'W': WHITE, 'F': (230,180,140)}
    for row, line in enumerate(head):
        for col, ch in enumerate(line):
            c = pal2.get(ch)
            if c:
                bx = ox + (col if facing==1 else (len(line)-1-col))
                d.rectangle([(bx)*s+1,(oy+row)*s+1,(bx)*s+s-1,(oy+row)*s+s-1], fill=c)
    for row, line in enumerate(body):
        for col, ch in enumerate(line):
            c = pal.get(ch)
            if c:
                bx = ox + (col if facing==1 else (len(line)-1-col))
                d.rectangle([(bx)*s+1,(oy+5+row)*s+1,(bx)*s+s-1,(oy+5+row)*s+s-1], fill=c)

def draw_bomb_item(d, ox, oy, s=3):
    b = [
        "..BBB..",
        ".BBBBB.",
        "BBBBBBB",
        "BBBBBBB",
        ".BBBBB.",
        "..BBB..",
    ]
    for row, line in enumerate(b):
        for col, ch in enumerate(line):
            if ch == 'B':
                shade = (20,20,20) if (row+col)%2==0 else (40,40,40)
                d.rectangle([(ox+col)*s,(oy+row)*s,(ox+col)*s+s-1,(oy+row)*s+s-1], fill=shade)
    # 引信
    d.rectangle([(ox+3)*s-1,(oy-1)*s,(ox+3)*s+1,(oy)*s], fill=ORANGE)
    d.rectangle([(ox+4)*s,(oy-2)*s,(ox+4)*s+s-1,(oy-1)*s], fill=GOLD)

def draw_princess(d, ox, oy, s=3):
    head = [
        ".CCCC.",
        "CCWWCC",  # C=crown/hair
        "C.WW.C",
        "CFFFC.",
        ".CCCC.",
    ]
    body = [
        ".PPPP.",
        "PPPPPP",
        "PPPPPP",
        ".P..P.",
        ".PP.PP",
    ]
    pal  = {'.': None, 'C': (200,60,160), 'W': WHITE, 'F': (235,185,145), 'P': PINK}
    for row, line in enumerate(head):
        for col, ch in enumerate(line):
            c = pal.get(ch)
            if c:
                d.rectangle([(ox+col)*s,(oy+row)*s,(ox+col)*s+s-1,(oy+row)*s+s-1], fill=c)
    for row, line in enumerate(body):
        for col, ch in enumerate(line):
            c = pal.get(ch)
            if c:
                d.rectangle([(ox+col)*s,(oy+5+row)*s,(ox+col)*s+s-1,(oy+5+row)*s+s-1], fill=c)
    # 皇冠
    crown = [(ox+1)*s, (oy-2)*s, GOLD]
    for cx in [ox+1, ox+2, ox+3, ox+4]:
        d.rectangle([(cx)*s,(oy-2)*s,(cx)*s+s-1,(oy-1)*s], fill=GOLD)
    d.point([(ox+1)*s, (oy-3)*s], fill=GOLD)
    d.point([(ox+2)*s+1, (oy-4)*s], fill=RED)
    d.point([(ox+4)*s, (oy-3)*s], fill=GOLD)

def draw_boss_demon(d, ox, oy, s=3):
    """简单像素魔王"""
    shape = [
        "..DDD..",
        ".DDDDD.",
        "DDRRRDD",
        "D.RRR.D",
        "DDDDDDD",
        ".DD.DD.",
        "DD...DD",
    ]
    pal = {'.': None, 'D': PURPLE, 'R': RED}
    for row, line in enumerate(shape):
        for col, ch in enumerate(line):
            c = pal.get(ch)
            if c:
                d.rectangle([(ox+col)*s,(oy+row)*s,(ox+col)*s+s-1,(oy+row)*s+s-1], fill=c)
    # 角
    for i in range(3):
        d.rectangle([(ox+i)*s,(oy-3+i)*s,(ox+i)*s+s-1,(oy-3+i)*s+s-1], fill=PURPLE_LT)
        d.rectangle([(ox+6-i)*s,(oy-3+i)*s,(ox+6-i)*s+s-1,(oy-3+i)*s+s-1], fill=PURPLE_LT)

def draw_castle(d, ox, oy, s=2):
    """城堡轮廓"""
    # 主体
    d.rectangle([ox*s, (oy+8)*s, (ox+30)*s, (oy+30)*s], fill=STONE)
    # 塔楼
    d.rectangle([ox*s, (oy+2)*s, (ox+8)*s, (oy+15)*s], fill=STONE)
    d.rectangle([(ox+22)*s, (oy+2)*s, (ox+30)*s, (oy+15)*s], fill=STONE)
    # 城垛（左塔）
    for i in [0, 2, 4]:
        d.rectangle([(ox+i)*s, (oy)*s, (ox+i+1)*s, (oy+2)*s], fill=STONE_LT)
    # 城垛（右塔）
    for i in [22, 24, 26, 28]:
        d.rectangle([(ox+i)*s, (oy)*s, (ox+i+1)*s, (oy+2)*s], fill=STONE_LT)
    # 城门
    d.rectangle([(ox+11)*s, (oy+18)*s, (ox+19)*s, (oy+30)*s], fill=BG_DEEP)
    d.ellipse([(ox+11)*s, (oy+15)*s, (ox+19)*s, (oy+21)*s], fill=BG_DEEP)
    # 窗（有光芒）
    d.rectangle([(ox+13)*s, (oy+5)*s, (ox+17)*s, (oy+11)*s], fill=GOLD)
    d.rectangle([(ox+14)*s, (oy+6)*s, (ox+16)*s, (oy+10)*s], fill=(255,240,180))

def draw_dungeon_entrance(d, ox, oy, s=2):
    """地牢入口（黑洞+石阶）"""
    # 石阶
    for step in range(5):
        sw = 20 - step*3
        d.rectangle([(ox - sw//2 + step)*s, (oy+step*2)*s,
                      (ox + sw//2 + 20 - step)*s, (oy+step*2+1)*s], fill=STONE_LT)
    # 地牢洞口
    d.ellipse([(ox-4)*s, (oy+8)*s, (ox+24)*s, (oy+18)*s], fill=BG_DEEP)
    # 阴影
    d.ellipse([(ox-2)*s, (oy+10)*s, (ox+22)*s, (oy+16)*s], fill=(4,3,8))

# ═══════════════════════════════════════════════════════════════
# 故事帧
# ═══════════════════════════════════════════════════════════════

def gen_story_frame(idx, draw_fn, filename):
    img, d = new_img()
    draw_fn(d)
    img.save(f"{OUT_STORY}/{filename}")
    print(f"  [story] {filename}")

# ── 帧 0：片名 ──────────────────────────────────────────────

def frame_title(d):
    draw_stars(d, seed=7)
    draw_dungeon_bg(d, dark=True)
    # 大标题（分行）
    texts = [
        (GOLD,    3, "BOMBER HERO",    80,  80),
        (WHITE,   2, "DUNGEON  RESCUE", 60, 120),
        (GRAY,    1, "A TALE OF BOMBS AND BRAVERY", 20, 155),
    ]
    for col, scale, txt, x, y in texts:
        draw_text_8bit(d, txt, x, y, col=col, scale=scale)
    # 炸弹人站在中央
    draw_bomber(d, 130, 185, s=4)
    # 公主在右边（窗中）
    d.rectangle([420, 150, 500, 240], fill=STONE)
    d.rectangle([435, 160, 485, 235], fill=BG_DEEP)
    draw_princess(d, 142, 60, s=2)
    draw_text_8bit(d, "PRESS ANY KEY", 170, 330, col=CYAN, scale=1)

# ── 帧 1：王国平和，公主在城堡 ────────────────────────────────

def frame1(d):
    draw_stars(d, seed=1)
    # 天空渐变
    for y in range(H//2):
        b = int(14 + y * 0.15)
        d.line([(0, y), (W-1, y)], fill=(8, 6, b))
    # 草地
    d.rectangle([0, H//2, W-1, H-1], fill=GREEN_DK)
    for gx in range(0, W, 8):
        gh = random.Random(gx).randint(0, 4)
        d.rectangle([gx, H//2 - gh, gx+3, H//2], fill=GREEN)
    # 城堡（居中）
    draw_castle(d, 145, 30, s=3)
    # 平和的月亮
    d.ellipse([520, 20, 580, 80], fill=(230,220,180))
    d.ellipse([530, 20, 580, 60], fill=BG_DEEP)  # 月牙
    # 文字
    draw_text_8bit(d, "ONCE UPON A TIME...", 10, 10, col=GOLD, scale=2)
    draw_text_8bit(d, "A KINGDOM LIVED IN PEACE", 60, 320, col=WHITE, scale=1)

# ── 帧 2：魔王带着军队出现，公主被抓 ─────────────────────────

def frame2(d):
    draw_dungeon_bg(d, dark=True)
    draw_stars(d, seed=2)
    # 红色天空（危险）
    for y in range(H//3):
        d.line([(0, y), (W-1, y)], fill=(int(20+y*0.3), 4, 8))
    # 魔王（大）
    draw_boss_demon(d, 240, 80, s=5)
    # 哭泣公主（被抓）
    d.rectangle([420, 200, 470, 280], fill=STONE)  # 笼子竖栏
    for bx in range(420, 475, 10):
        d.rectangle([bx, 200, bx+4, 280], fill=GRAY)
    draw_princess(d, 143, 72, s=2)
    # 闪电效果
    pts = [(490,30),(495,70),(485,70),(500,120),(480,120),(510,180)]
    d.line(pts, fill=GOLD, width=3)
    # 文字
    draw_text_8bit(d, "THE DEMON LORD", 20, 10, col=RED_LT, scale=2)
    draw_text_8bit(d, "KIDNAPPED THE PRINCESS!", 30, 40, col=RED, scale=1)
    draw_text_8bit(d, "THE KINGDOM FELL INTO DARKNESS...", 10, 330, col=GRAY, scale=1)

# ── 帧 2b：魔王夺走了炸弹！ ──────────────────────────────────

def frame2b(d):
    draw_dungeon_bg(d, dark=True)
    # 暗红天空
    for y in range(H // 3):
        d.line([(0, y), (W-1, y)], fill=(int(25 + y * 0.4), 4, 8))
    # 魔王（右侧，中等大小，爪子抓着炸弹）
    draw_boss_demon(d, 280, 80, s=4)
    # 魔王手持/抓取一堆炸弹（在魔王下方-右侧）
    bomb_positions = [
        (320, 200), (350, 215), (305, 220), (370, 200), (340, 235),
    ]
    for bx, by in bomb_positions:
        draw_bomb_item(d, bx // 3, by // 3, s=3)
    # 发光紫色魔法光环（炸弹被吸走的效果）
    for r2 in [55, 40, 25]:
        cx, cy = 350, 218
        col_r = min(255, 120 + r2)
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
                  outline=(col_r, 40, 200), width=2)
    # 左侧：惊慌的炸弹人（小，背对魔王）
    draw_bomber(d, 28, 60, s=3, facing=-1)
    # "空手" 效果 - 炸弹人手边没有炸弹，地面是空的
    draw_text_8bit(d, "THE BOMBS WERE STOLEN!", 20, 10, col=RED_LT, scale=2)
    draw_text_8bit(d, "THE DEMON LORD TOOK EVERY LAST ONE...", 8, 45, col=RED, scale=1)
    draw_text_8bit(d, "THE HERO STOOD POWERLESS... FOR NOW.", 8, 330, col=GRAY, scale=1)

# ── 帧 3：炸弹人英雄，接受任务 ───────────────────────────────

def frame3(d):
    draw_dungeon_bg(d)
    # 炸弹人站在地图前（中央，大）
    draw_bomber(d, 80, 130, s=5, facing=1)
    # 炸弹道具散落
    for bx, by in [(220,160),(250,200),(200,220),(270,170)]:
        draw_bomb_item(d, bx//3, by//3, s=3)
    # 火把
    for tx in [30, 580]:
        d.rectangle([tx, 60, tx+8, 140], fill=(80,60,20))
        d.ellipse([tx-4, 40, tx+12, 64], fill=ORANGE)
        d.ellipse([tx, 44, tx+8, 60], fill=GOLD)
    # 文字
    draw_text_8bit(d, "THEN A HERO APPEARED", 50, 20, col=GOLD, scale=2)
    draw_text_8bit(d, "BOMBER  -  MASTER OF EXPLOSIVES", 10, 60, col=ORANGE, scale=1)
    draw_text_8bit(d, '"I WILL RESCUE HER!"', 100, 320, col=WHITE, scale=1)

# ── 帧 4：进入地牢，扫雷 ─────────────────────────────────────

def frame4(d):
    draw_dungeon_bg(d, dark=True)
    # 地牢深处的网格（扫雷暗示）
    gs = 24
    for gy in range(180, H-20, gs):
        for gx in range(20, W-20, gs):
            d.rectangle([gx, gy, gx+gs-2, gy+gs-2], fill=STONE)
    # 隐藏炸弹发光
    for bx, by in [(68, 204), (164, 228), (260, 180), (356, 204), (452, 228), (116, 180)]:
        d.ellipse([bx-8, by-8, bx+8, by+8], fill=(60, 20, 20, 128))
        d.ellipse([bx-4, by-4, bx+4, by+4], fill=RED)
    # 炸弹人（左侧，小）
    draw_bomber(d, 18, 50, s=3, facing=1)
    # 问号方块（神秘）
    for qx in [300, 350, 400, 450]:
        d.rectangle([qx, 80, qx+28, 108], fill=STONE_LT)
        draw_text_8bit(d, "?", qx+8, 84, col=GOLD, scale=2)
    # 文字
    draw_text_8bit(d, "INTO THE DUNGEON...", 60, 20, col=CYAN, scale=2)
    draw_text_8bit(d, "FIND BOMBS HIDDEN IN THE DARK", 30, 60, col=GRAY, scale=1)
    draw_text_8bit(d, "AND BLAST THE BOSS TO PIECES!", 30, 330, col=RED_LT, scale=1)

# ── 帧 5：出发！炸弹爆炸 Boss ─────────────────────────────────

def frame5(d):
    # 爆炸背景
    for y in range(H):
        r = min(255, int(60 + y * 0.2))
        g = max(0,  int(30 - y * 0.05))
        d.line([(0, y), (W-1, y)], fill=(r, g, 4))
    # 爆炸圆圈
    for r2 in [160, 120, 80, 50]:
        alpha = 180 - r2
        cx, cy = W//2, H//2+20
        d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(min(255,200+r2//2), min(255,100+r2), 20))
    # Boss 碎裂（四片）
    for ox2, oy2 in [(-80,-60),(80,-60),(-80,60),(80,60)]:
        draw_boss_demon(d, (W//2+ox2)//3-5, (H//2+oy2)//3, s=2)
    # 炸弹人胜利
    draw_bomber(d, 125, 60, s=4, facing=1)
    # 星星爆炸效果
    rng = random.Random(55)
    for _ in range(30):
        sx = rng.randint(30, W-30)
        sy = rng.randint(30, H-80)
        sc = rng.choice([GOLD, WHITE, ORANGE, RED_LT])
        d.ellipse([sx-3, sy-3, sx+3, sy+3], fill=sc)
    draw_text_8bit(d, "VICTORY!", 200, 20, col=GOLD, scale=3)
    draw_text_8bit(d, "THE PRINCESS IS SAVED!", 80, 310, col=WHITE, scale=1)
    draw_text_8bit(d, "BUT MORE FLOORS AWAIT...", 90, 330, col=GRAY, scale=1)

# ── 标题画面背景 ──────────────────────────────────────────────

def gen_title_bg():
    img, d = new_img()
    draw_stars(d, seed=99)
    # 深邃地牢背景
    for y in range(H):
        mix = y / H
        r = int(8  + mix * 12)
        g = int(6  + mix * 8)
        b = int(14 + mix * 20)
        d.line([(0, y), (W-1, y)], fill=(r, g, b))
    # 远处城堡剪影（暗）
    for tx in range(0, W, 120):
        h2 = random.Random(tx*7).randint(60, 130)
        d.rectangle([tx, H-h2, tx+80, H-1], fill=(22,18,30))
        # 塔尖
        for tip_x in [tx+5, tx+35, tx+65]:
            tw2 = 10
            d.polygon([(tip_x, H-h2-20),(tip_x+tw2//2, H-h2),(tip_x+tw2, H-h2)], fill=(18,14,26))
    # 地牢墙壁
    for ty in range(H-50, H, 12):
        for tx2 in range(0, W, 50):
            d.rectangle([tx2, ty, tx2+46, ty+10], fill=STONE)
    # 炸弹人（中央大）
    draw_bomber(d, 160, 115, s=5, facing=1)
    # 公主（右侧）
    draw_princess(d, 290, 100, s=4)
    # 炸弹道具
    for bx2, by2 in [(40,200),(55,220),(70,200),(460,210),(480,225),(465,240)]:
        draw_bomb_item(d, bx2, by2, s=2)
    # 主标题
    draw_text_8bit(d, "BOMBER DUNGEON", 40, 24, col=GOLD, scale=3)
    draw_text_8bit(d, "100  FLOORS", 130, 68, col=ORANGE, scale=2)
    draw_text_8bit(d, "RESCUE THE PRINCESS!", 70, 108, col=WHITE, scale=1)
    img.save(f"{OUT_UI}/title_bg.png")
    print("  [ui] title_bg.png")

# ── 主程序 ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating story frames...")
    gen_story_frame(0, frame_title, "story_00_title.png")
    gen_story_frame(1, frame1,      "story_01_kingdom.png")
    gen_story_frame(2, frame2,      "story_02_kidnap.png")
    gen_story_frame(3, frame2b,     "story_02b_bombs_stolen.png")
    gen_story_frame(4, frame3,      "story_03_hero.png")
    gen_story_frame(5, frame4,      "story_04_dungeon.png")
    gen_story_frame(6, frame5,      "story_05_victory.png")
    gen_title_bg()
    print("Done!")
