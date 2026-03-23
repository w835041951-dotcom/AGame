"""
自动定时素材生成调度器
每小时自动调用 Pollinations API 生成素材，直到全部完成

用法:
  set POLLINATIONS_API_KEY=sk_xxx
  python scripts/tools/auto_gen.py              # 全部类别
  python scripts/tools/auto_gen.py --skip-ui     # 跳过UI(已完成)
  python scripts/tools/auto_gen.py --only boss   # 只跑boss
"""
import os, sys, time, json, hashlib, datetime
from pathlib import Path
from urllib.parse import quote

try:
    from PIL import Image
    import io, requests
except ImportError:
    print("请先安装: pip install pillow requests")
    sys.exit(1)

# 复用 gen_ai_art.py 的所有数据定义
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from gen_ai_art import (
    BOSS_THEMES, BOSS_CREATURES, BOSS_CREATURE_DESC, BOSS_THEME_DESC, BOSS_SIZES,
    STYLE_BOSS, STYLE_BG, STYLE_STORY, STYLE_BOMB, STYLE_VFX, STYLE_TITLE,
    BG_SCENES, STORY_FRAMES, BOMB_TYPES, VFX_EFFECTS,
    POLLINATIONS_BASE, CACHE_FILE, ASSETS,
)

WAIT_SECONDS = 3600  # 1小时

# ═══════════════════════════════════════════════════════════
# 缓存管理
# ═══════════════════════════════════════════════════════════
def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def prompt_hash(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()[:12]

# ═══════════════════════════════════════════════════════════
# 单次生成 (返回状态码区分成功/限流/失败)
# ═══════════════════════════════════════════════════════════
RESULT_OK = "ok"
RESULT_CACHED = "cached"
RESULT_RATE_LIMITED = "rate_limited"
RESULT_FAILED = "failed"

def generate_one(prompt, output_path, width, height, cache):
    """生成单张图片，返回结果状态"""
    ph = prompt_hash(prompt)
    if ph in cache:
        return RESULT_CACHED

    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 100000
    encoded = quote(prompt, safe="")
    url = f"{POLLINATIONS_BASE}/image/{encoded}?width={width}&height={height}&model=flux&seed={seed}&nologo=true"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{now}] {output_path.name} ({width}x{height})...", end=" ", flush=True)

    for attempt in range(2):
        try:
            resp = requests.get(url, headers=headers, timeout=180)
            if resp.status_code == 402:
                print("⏳ 额度耗尽")
                return RESULT_RATE_LIMITED
            resp.raise_for_status()

            img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
            if img.size != (width, height):
                img = img.resize((width, height), Image.LANCZOS)
            img.save(str(output_path))

            cache[ph] = output_path.name
            save_cache(cache)
            print("✓")
            time.sleep(1)
            return RESULT_OK

        except requests.RequestException as e:
            if attempt == 0:
                print(f"retry...", end=" ", flush=True)
                time.sleep(5)
            else:
                print(f"✗ {e}")
                return RESULT_FAILED

    return RESULT_FAILED

# ═══════════════════════════════════════════════════════════
# 任务列表构建
# ═══════════════════════════════════════════════════════════
def build_boss_tasks():
    tasks = []
    cell = 64
    for theme in BOSS_THEMES:
        for creature in BOSS_CREATURES:
            fname = f"boss_{theme}_{creature}.png"
            out = ASSETS / "boss" / fname
            cols, rows = BOSS_SIZES.get(creature, (5, 4))
            w, h = cols * cell, rows * cell
            creature_desc = BOSS_CREATURE_DESC.get(creature, creature)
            theme_desc = BOSS_THEME_DESC.get(theme, theme)
            prompt = (
                f"{STYLE_BOSS}, {creature_desc}, {theme_desc}, "
                f"fitting in {cols}x{rows} grid cells"
            )
            ratio = w / h
            if ratio > 1:
                gen_w, gen_h = 1024, max(512, int(1024 / ratio))
            else:
                gen_h, gen_w = 1024, max(512, int(1024 * ratio))
            tasks.append((prompt, out, gen_w, gen_h, w, h))
    return tasks

def build_bg_tasks():
    tasks = []
    for name, desc in BG_SCENES.items():
        out = ASSETS / "bg" / f"{name}.png"
        prompt = f"{STYLE_BG}, {desc}"
        tasks.append((prompt, out, 1920, 1080, 1920, 1080))
    return tasks

def build_story_tasks():
    tasks = []
    for name, desc in STORY_FRAMES.items():
        out = ASSETS / "story" / f"{name}.png"
        prompt = f"{STYLE_STORY}, {desc}"
        tasks.append((prompt, out, 1280, 720, 640, 360))
    return tasks

def build_bomb_tasks():
    tasks = []
    for name, desc in BOMB_TYPES.items():
        out = ASSETS / "bombs" / f"{name}.png"
        prompt = f"{STYLE_BOMB}, {desc}"
        tasks.append((prompt, out, 512, 512, 64, 64))
    return tasks

def build_vfx_tasks():
    tasks = []
    for name, desc in VFX_EFFECTS.items():
        out = ASSETS / "vfx" / f"{name}.png"
        prompt = f"{STYLE_VFX}, {desc}"
        tasks.append((prompt, out, 512, 512, 128, 128))
    return tasks

def build_title_task():
    out = ASSETS / "ui" / "title_bg.png"
    return [(STYLE_TITLE, out, 1280, 720, 640, 360)]

# ═══════════════════════════════════════════════════════════
# 主调度循环
# ═══════════════════════════════════════════════════════════
def run_batch(tasks, cache, label):
    """执行一批任务，遇到限流暂停，返回 (完成数, 跳过数, 是否被限流)"""
    done = 0
    skipped = 0
    for prompt, out, gen_w, gen_h, final_w, final_h in tasks:
        ph = prompt_hash(prompt)
        if ph in cache:
            skipped += 1
            continue

        result = generate_one(prompt, out, gen_w, gen_h, cache)

        if result == RESULT_OK:
            # 后处理: 缩放到最终尺寸
            if out.exists() and (gen_w != final_w or gen_h != final_h):
                img = Image.open(str(out)).convert("RGBA")
                img = img.resize((final_w, final_h), Image.LANCZOS)
                img.save(str(out))
            done += 1
        elif result == RESULT_RATE_LIMITED:
            return done, skipped, True
        # RESULT_FAILED: 跳过继续下一个

    return done, skipped, False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="定时素材生成调度器")
    parser.add_argument("--skip-ui", action="store_true", help="跳过UI纹理(已由gen_game_ui.py完成)")
    parser.add_argument("--only", choices=["boss", "bg", "story", "bombs", "vfx", "title"],
                        help="只跑指定类别")
    parser.add_argument("--wait", type=int, default=3600, help="限流后等待秒数(默认3600)")
    args = parser.parse_args()

    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    if not api_key:
        print("错误: 请设置 POLLINATIONS_API_KEY")
        print("  set POLLINATIONS_API_KEY=sk_xxx")
        sys.exit(1)

    wait_sec = args.wait

    # 构建任务列表
    categories = []
    if args.only:
        mapping = {
            "boss": ("Boss精灵", build_boss_tasks),
            "bg": ("背景图", build_bg_tasks),
            "story": ("故事CG", build_story_tasks),
            "bombs": ("炸弹图标", build_bomb_tasks),
            "vfx": ("VFX特效", build_vfx_tasks),
            "title": ("标题背景", build_title_task),
        }
        k = args.only
        categories.append((mapping[k][0], mapping[k][1]))
    else:
        categories = [
            ("Boss精灵", build_boss_tasks),
            ("背景图", build_bg_tasks),
            ("故事CG", build_story_tasks),
            ("炸弹图标", build_bomb_tasks),
            ("VFX特效", build_vfx_tasks),
            ("标题背景", build_title_task),
        ]

    round_num = 0
    while True:
        round_num += 1
        cache = load_cache()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"第 {round_num} 轮  {now}")
        print(f"{'='*60}")

        all_done = True
        hit_limit = False
        total_generated = 0
        total_cached = 0

        for label, builder in categories:
            tasks = builder()
            remaining = sum(1 for p, *_ in tasks if prompt_hash(p) not in cache)
            total = len(tasks)
            cached = total - remaining

            if remaining == 0:
                print(f"\n  ✅ {label}: 全部完成 ({total}/{total})")
                total_cached += cached
                continue

            all_done = False
            print(f"\n  🔄 {label}: {cached}/{total} 已完成, 还剩 {remaining}")

            done, skipped, rate_limited = run_batch(tasks, cache, label)
            total_generated += done
            total_cached += skipped

            if rate_limited:
                hit_limit = True
                print(f"\n  ⏳ {label}: 本轮生成 {done} 张后额度耗尽")
                break
            else:
                print(f"  ✅ {label}: 本轮生成 {done} 张")

        # 本轮总结
        cache = load_cache()
        print(f"\n{'─'*40}")
        print(f"本轮: 生成 {total_generated} 张")
        print(f"缓存总数: {len(cache)} 条")

        if all_done and not hit_limit:
            total_all = sum(len(b()) for _, b in categories)
            print(f"\n🎉🎉🎉 全部 {total_all} 张素材生成完毕!")
            break

        if hit_limit:
            wake_time = datetime.datetime.now() + datetime.timedelta(seconds=wait_sec)
            print(f"\n⏰ 等待额度恢复... {wait_sec//60} 分钟后继续")
            print(f"   下次运行: {wake_time.strftime('%H:%M:%S')}")
            print(f"   (按 Ctrl+C 随时停止，进度已保存)")
            try:
                time.sleep(wait_sec)
            except KeyboardInterrupt:
                print("\n\n⛔ 手动停止。已生成的素材已缓存，下次运行自动跳过。")
                sys.exit(0)
        else:
            # 没有限流但还有未完成的(可能是失败的)，等一会儿重试
            print(f"\n⏰ 部分失败，5分钟后重试...")
            try:
                time.sleep(300)
            except KeyboardInterrupt:
                print("\n\n⛔ 手动停止。")
                sys.exit(0)


if __name__ == "__main__":
    main()
