"""
AI 美术素材批量生成器
使用 Pollinations.ai 免费 API 批量生成游戏美术素材
支持: Boss精灵、背景图、故事CG、炸弹图标、VFX特效

免费! 只需注册获取API Key: https://enter.pollinations.ai/

使用前:
  pip install pillow requests
  set POLLINATIONS_API_KEY=pk_xxxxxxxx

用法:
  python scripts/tools/gen_ai_art.py --category boss     # 只生成Boss
  python scripts/tools/gen_ai_art.py --category bg        # 只生成背景
  python scripts/tools/gen_ai_art.py --category story     # 只生成故事CG
  python scripts/tools/gen_ai_art.py --category bombs     # 只生成炸弹图标
  python scripts/tools/gen_ai_art.py --category vfx       # 只生成VFX
  python scripts/tools/gen_ai_art.py --category title     # 只生成标题背景
  python scripts/tools/gen_ai_art.py --category all       # 全部生成
  python scripts/tools/gen_ai_art.py --list               # 列出所有任务不生成
  python scripts/tools/gen_ai_art.py --dry-run            # 只打印prompt不调API
"""
import os, sys, argparse, time, json, hashlib
from pathlib import Path
from urllib.parse import quote

try:
    from PIL import Image
    import io, requests
except ImportError:
    print("请先安装: pip install pillow requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets" / "sprites"
CACHE_FILE = ROOT / "scripts" / "tools" / ".ai_art_cache.json"

# ═══════════════════════════════════════════════════════════
# Pollinations.ai 配置 (免费注册)
# ═══════════════════════════════════════════════════════════
POLLINATIONS_BASE = "https://gen.pollinations.ai"
DEFAULT_MODEL = "flux"  # 可选: flux, turbo
_config = {"model": "flux"}

# ═══════════════════════════════════════════════════════════
# 风格前缀 (统一游戏视觉风格)
# ═══════════════════════════════════════════════════════════
STYLE_BOSS = (
    "dark fantasy pixel art boss monster sprite, "
    "game asset on solid black background, "
    "top-down view, detailed shading, glowing eyes, "
    "menacing organic creature, dungeon crawler style, "
    "no text, no watermark, sharp pixel edges"
)

STYLE_BG = (
    "dark fantasy dungeon environment, wide landscape, "
    "atmospheric lighting, detailed pixel art background, "
    "game background art 16:9 aspect ratio, "
    "moody and immersive, no text, no characters, no watermark"
)

STYLE_STORY = (
    "dark fantasy illustration, cinematic scene, "
    "pixel art style with soft gradients, "
    "game cutscene art 16:9, dramatic lighting, "
    "no text, no watermark, no UI elements"
)

STYLE_BOMB = (
    "pixel art game item icon, dark fantasy style, "
    "single bomb/explosive weapon on transparent background, "
    "clean sharp edges, top-down view, 64x64 game sprite, "
    "no text, no watermark"
)

STYLE_VFX = (
    "pixel art visual effect sprite sheet, "
    "glowing magical effect on black background, "
    "game VFX asset, transparent edges, "
    "no text, no watermark"
)

STYLE_TITLE = (
    "dark fantasy pixel art game title screen background, "
    "epic dungeon entrance with bomber hero silhouette, "
    "atmospheric fog, torchlight, castle in distance, "
    "wide 16:9 composition, no text, no watermark"
)

# ═══════════════════════════════════════════════════════════
# 素材定义
# ═══════════════════════════════════════════════════════════

BOSS_THEMES = [
    "ancient", "abyss", "blood", "celestial", "chaos",
    "dark", "doom", "forest", "frost", "inferno",
    "iron", "plague", "shadow", "thunder", "void"
]

BOSS_CREATURES = [
    "assassin", "crystal", "demon", "dragon", "eagle",
    "gargoyle", "ghost", "giant", "golem", "hydra",
    "kraken", "lich", "mushroom", "phoenix", "serpent",
    "spider", "titan", "witch", "wolf", "wyvern"
]

BOSS_CREATURE_DESC = {
    "assassin":  "shadowy rogue figure with daggers and cloak",
    "crystal":   "crystalline golem made of glowing gemstones",
    "demon":     "horned demon lord with fire and dark wings",
    "dragon":    "massive dragon with scales and flame breath",
    "eagle":     "giant eagle with lightning feathers",
    "gargoyle":  "stone gargoyle awakened with glowing cracks",
    "ghost":     "ethereal spirit with chains and spectral glow",
    "giant":     "towering humanoid brute with armor",
    "golem":     "stone golem with runes and mossy surface",
    "hydra":     "multi-headed serpent beast",
    "kraken":    "tentacled sea beast with bioluminescence",
    "lich":      "undead sorcerer with skull face and magic staff",
    "mushroom":  "giant poisonous mushroom creature with spores",
    "phoenix":   "blazing fire bird with radiant feathers",
    "serpent":   "massive coiled snake with venomous fangs",
    "spider":    "giant armored spider with glowing web",
    "titan":     "colossal armored warrior with great weapon",
    "witch":     "dark sorceress with cauldron and magic runes",
    "wolf":      "dire wolf with shadow aura and red eyes",
    "wyvern":    "winged lizard beast with barbed tail",
}

BOSS_THEME_DESC = {
    "ancient":    "ancient stone ruins theme, moss and carved runes",
    "abyss":      "deep ocean abyss theme, dark blue bioluminescent",
    "blood":      "blood-soaked crimson theme, veins and gore",
    "celestial":  "heavenly golden theme, halos and divine light",
    "chaos":      "chaotic warped theme, reality-bending distortion",
    "dark":       "pure darkness theme, shadow and void",
    "doom":       "apocalyptic theme, fire and destruction",
    "forest":     "overgrown forest theme, vines and nature",
    "frost":      "frozen ice theme, icicles and snowflakes",
    "inferno":    "hellfire theme, lava and flames",
    "iron":       "industrial metal theme, rust and gears",
    "plague":     "pestilence theme, sickly green poison",
    "shadow":     "shadow realm theme, dark purple mist",
    "thunder":    "storm theme, lightning and thunder clouds",
    "void":       "cosmic void theme, stars and dark matter",
}

# Boss 尺寸 (宽cells × 高cells)
BOSS_SIZES = {
    "assassin": (5, 5), "crystal": (5, 5), "demon": (6, 5),
    "dragon": (8, 5),   "eagle": (6, 4),   "gargoyle": (5, 4),
    "ghost": (4, 5),    "giant": (5, 6),   "golem": (6, 5),
    "hydra": (7, 4),    "kraken": (7, 5),  "lich": (4, 5),
    "mushroom": (4, 4), "phoenix": (7, 5), "serpent": (6, 3),
    "spider": (5, 4),   "titan": (6, 6),   "witch": (4, 5),
    "wolf": (6, 4),     "wyvern": (7, 5),
}

BG_SCENES = {
    "bg_stone_prison":     "underground stone prison dungeon, iron bars, torchlight",
    "bg_bone_chamber":     "chamber made of bones and skulls, eerie green glow",
    "bg_lava_cave":        "volcanic lava cave with flowing magma rivers",
    "bg_ghost_wreck":      "haunted shipwreck interior, ghostly blue light",
    "bg_crystal_cavern":   "vast crystal cavern with purple and blue gemstones",
    "bg_ancient_ruins":    "crumbling ancient temple ruins with overgrown vines",
    "bg_shadow_hall":      "dark shadowy great hall, floating candles",
    "bg_shadow_realm":     "shadow dimension, distorted reality, purple mist",
    "bg_frost_altar":      "frozen altar chamber, ice crystals, blue light",
    "bg_plague_swamp":     "toxic swamp with bubbling green pools and dead trees",
    "bg_mechanical_fort":  "steampunk mechanical fortress, gears and pipes",
    "bg_nightmare_maze":   "surreal nightmare labyrinth, impossible geometry",
    "bg_corrupted_temple": "corrupted holy temple, dark energy corruption",
    "bg_void_rift":        "tear in reality showing cosmic void, stars visible",
    "bg_void_palace":      "palace floating in the void of space",
    "bg_thunder_peak":     "mountain peak during lightning storm",
    "bg_chaos_forge":      "chaotic forge with warped metal and wild flames",
    "bg_abyss_throne":     "underwater abyss throne room, bioluminescent",
    "bg_divine_sanctum":   "golden divine sanctuary with holy light beams",
    "bg_final_sanctum":    "epic final arena, all elements converging",
}

STORY_FRAMES = {
    "story_00_title":           "bomber hero standing before massive dungeon gate, epic title card composition",
    "story_01_kingdom":         "peaceful pixel art kingdom with castle, blue sky, villagers below",
    "story_02_kidnap":          "dark shadow snatching princess from castle tower at night",
    "story_02b_bombs_stolen":   "villain stealing glowing bombs from royal armory",
    "story_03_hero":            "young bomber hero picking up first bomb, determined pose",
    "story_04_dungeon":         "hero entering dark dungeon entrance, light fading behind",
    "story_05_victory":         "hero celebrating with explosion behind defeated boss",
    "story_06_deeper":          "hero descending deeper stairs into darker dungeon",
    "story_10_midpoint":        "hero resting at campfire in dungeon, halfway point",
    "story_15_dark_turn":       "dungeon becoming corrupted, dark energy everywhere",
    "story_19_last_stand":      "hero facing final massive boss in epic arena",
    "story_20_ending_good":     "hero saving princess, sunlight breaking through dungeon",
    "story_20_ending_bad":      "hero fallen in dark dungeon, game over scene",
}

BOMB_TYPES = {
    "pierce_h":  "horizontal piercing arrow bomb, blue trail",
    "pierce_v":  "vertical piercing arrow bomb, blue trail",
    "cross":     "cross-shaped holy bomb, golden glow",
    "x_shot":    "X-shaped explosive, red diagonal lines",
    "bounce":    "bouncing rubber bomb, spring coils",
    "area":      "area-of-effect round bomb, shockwave rings",
    "cluster":   "cluster bomb splitting into mini bombs",
    "drill":     "drill bomb boring into ground, metal spiral",
    "flame":     "fire bomb with flames, orange and red",
    "frost":     "ice bomb with frost crystals, blue and white",
    "poison":    "poison bomb with toxic cloud, sickly green",
    "thunder":   "lightning bomb with electric sparks, yellow",
    "holy":      "holy bomb with divine light, golden cross",
    "mega":      "massive mega bomb, oversized and glowing",
    "nova":      "supernova bomb, radiant explosion energy",
    "scatter":   "scatter bomb with multiple fragments flying",
    "void":      "void bomb with dark matter swirl, purple black",
}

VFX_EFFECTS = {
    "boss_hit_flash":     "bright white and yellow impact flash, radial burst",
    "chain_spark":        "electric chain lightning spark, blue-white",
    "death_particles":    "explosion death particles, orange and red debris",
    "debuff_icon":        "skull debuff status icon, purple poison drip",
    "explosion_ring":     "expanding explosion shockwave ring, orange glow",
    "floor_transition":   "magical portal swirl transition effect, blue-purple",
    "upgrade_shine":      "golden upgrade sparkle shine effect, star glint",
    "weak_point_glow":    "pulsing red weak point indicator, target glow",
}


# ═══════════════════════════════════════════════════════════
# 生成逻辑
# ═══════════════════════════════════════════════════════════

def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def prompt_hash(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()[:12]

def generate_image(prompt, output_path, width=1024, height=1024, model=None, cache=None, dry_run=False):
    """调用 Pollinations.ai 免费 API 生成图片并保存"""
    if model is None:
        model = _config["model"]
    ph = prompt_hash(prompt)
    if cache and ph in cache:
        print(f"  [cached] {output_path.name}")
        return True

    if dry_run:
        print(f"  [dry-run] {output_path.name}")
        print(f"    prompt: {prompt[:120]}...")
        print(f"    size: {width}x{height}")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 100000
        api_key = os.environ.get("POLLINATIONS_API_KEY", "")
        encoded_prompt = quote(prompt, safe="")
        url = f"{POLLINATIONS_BASE}/image/{encoded_prompt}?width={width}&height={height}&model={model}&seed={seed}&nologo=true"
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        print(f"  generating {output_path.name} ({width}x{height})...")

        # 最多重试3次
        last_err = None
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=120)
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                last_err = e
                if attempt < 2:
                    wait = (attempt + 1) * 5
                    print(f"    retry {attempt+1}/3 in {wait}s...")
                    time.sleep(wait)
        else:
            raise last_err

        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")

        # 缩放到目标尺寸
        if img.size != (width, height):
            img = img.resize((width, height), Image.LANCZOS)

        img.save(str(output_path))
        print(f"  ✓ saved {output_path.name}")

        if cache is not None:
            cache[ph] = str(output_path.name)
            save_cache(cache)

        # Pollinations 有速率限制，间隔1秒
        time.sleep(1)
        return True

    except Exception as e:
        print(f"  ✗ FAILED {output_path.name}: {e}")
        return False


def gen_bosses(cache, dry_run=False, limit=0):
    """生成Boss精灵图"""
    print("\n══ BOSS SPRITES ══")
    count = 0
    cell = 64
    for theme in BOSS_THEMES:
        for creature in BOSS_CREATURES:
            if limit and count >= limit:
                return count
            fname = f"boss_{theme}_{creature}.png"
            out = ASSETS / "boss" / fname
            cols, rows = BOSS_SIZES.get(creature, (5, 4))
            w, h = cols * cell, rows * cell

            creature_desc = BOSS_CREATURE_DESC.get(creature, creature)
            theme_desc = BOSS_THEME_DESC.get(theme, theme)

            prompt = (
                f"{STYLE_BOSS}, "
                f"{creature_desc}, "
                f"{theme_desc}, "
                f"fitting in {cols}x{rows} grid cells"
            )

            # Flux 只支持特定尺寸，生成大图后缩放
            gen_w = max(512, min(1024, w))
            gen_h = max(512, min(1024, h))
            # 保持宽高比
            ratio = w / h
            if ratio > 1:
                gen_w = 1024
                gen_h = max(512, int(1024 / ratio))
            else:
                gen_h = 1024
                gen_w = max(512, int(1024 * ratio))

            if generate_image(prompt, out, gen_w, gen_h, cache=cache, dry_run=dry_run):
                # 后处理：缩放到实际游戏尺寸
                if not dry_run and out.exists():
                    img = Image.open(str(out)).convert("RGBA")
                    if img.size != (w, h):
                        img = img.resize((w, h), Image.LANCZOS)
                        img.save(str(out))
                count += 1
    return count


def gen_backgrounds(cache, dry_run=False):
    """生成背景图"""
    print("\n══ BACKGROUNDS ══")
    count = 0
    for name, desc in BG_SCENES.items():
        out = ASSETS / "bg" / f"{name}.png"
        prompt = f"{STYLE_BG}, {desc}"
        if generate_image(prompt, out, 1920, 1080, cache=cache, dry_run=dry_run):
            count += 1
    return count


def gen_story(cache, dry_run=False):
    """生成故事CG"""
    print("\n══ STORY ART ══")
    count = 0
    for name, desc in STORY_FRAMES.items():
        out = ASSETS / "story" / f"{name}.png"
        prompt = f"{STYLE_STORY}, {desc}"
        # 故事CG 用640x360然后放大
        if generate_image(prompt, out, 1280, 720, cache=cache, dry_run=dry_run):
            if not dry_run and out.exists():
                img = Image.open(str(out)).convert("RGBA")
                img = img.resize((640, 360), Image.LANCZOS)
                img.save(str(out))
            count += 1
    return count


def gen_bombs(cache, dry_run=False):
    """生成炸弹图标"""
    print("\n══ BOMB SPRITES ══")
    count = 0
    for name, desc in BOMB_TYPES.items():
        out = ASSETS / "bombs" / f"{name}.png"
        prompt = f"{STYLE_BOMB}, {desc}"
        if generate_image(prompt, out, 512, 512, cache=cache, dry_run=dry_run):
            if not dry_run and out.exists():
                img = Image.open(str(out)).convert("RGBA")
                img = img.resize((64, 64), Image.LANCZOS)
                img.save(str(out))
            count += 1
    return count


def gen_vfx(cache, dry_run=False):
    """生成VFX特效"""
    print("\n══ VFX EFFECTS ══")
    count = 0
    for name, desc in VFX_EFFECTS.items():
        out = ASSETS / "vfx" / f"{name}.png"
        prompt = f"{STYLE_VFX}, {desc}"
        if generate_image(prompt, out, 512, 512, cache=cache, dry_run=dry_run):
            if not dry_run and out.exists():
                img = Image.open(str(out)).convert("RGBA")
                img = img.resize((128, 128), Image.LANCZOS)
                img.save(str(out))
            count += 1
    return count


def gen_title(cache, dry_run=False):
    """生成标题背景"""
    print("\n══ TITLE BACKGROUND ══")
    out = ASSETS / "ui" / "title_bg.png"
    prompt = STYLE_TITLE
    if generate_image(prompt, out, 1280, 720, cache=cache, dry_run=dry_run):
        if not dry_run and out.exists():
            img = Image.open(str(out)).convert("RGBA")
            img = img.resize((640, 360), Image.LANCZOS)
            img.save(str(out))
        return 1
    return 0


def list_tasks():
    """列出所有生成任务"""
    print("═══ 所有生成任务 ═══\n")

    print(f"Boss 精灵: {len(BOSS_THEMES)} 主题 × {len(BOSS_CREATURES)} 生物 = {len(BOSS_THEMES) * len(BOSS_CREATURES)} 张")
    for t in BOSS_THEMES:
        print(f"  {t}: {', '.join(BOSS_CREATURES)}")

    print(f"\n背景图: {len(BG_SCENES)} 张")
    for name in BG_SCENES:
        print(f"  {name}.png")

    print(f"\n故事CG: {len(STORY_FRAMES)} 张")
    for name in STORY_FRAMES:
        print(f"  {name}.png")

    print(f"\n炸弹图标: {len(BOMB_TYPES)} 张")
    for name in BOMB_TYPES:
        print(f"  {name}.png")

    print(f"\nVFX特效: {len(VFX_EFFECTS)} 张")
    for name in VFX_EFFECTS:
        print(f"  {name}.png")

    print(f"\n标题背景: 1 张")

    total = (len(BOSS_THEMES) * len(BOSS_CREATURES) +
             len(BG_SCENES) + len(STORY_FRAMES) +
             len(BOMB_TYPES) + len(VFX_EFFECTS) + 1)
    print(f"\n总计: {total} 张")
    print(f"使用 Pollinations.ai 免费生成!")
    print(f"注册获取Key: https://enter.pollinations.ai/")


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="AI 美术素材批量生成器")
    parser.add_argument("--category", choices=["boss", "bg", "story", "bombs", "vfx", "title", "all"],
                        default="all", help="生成类别")
    parser.add_argument("--list", action="store_true", help="只列出任务不生成")
    parser.add_argument("--dry-run", action="store_true", help="只打印prompt不调API")
    parser.add_argument("--limit", type=int, default=0, help="Boss最多生成N张(测试用)")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=["flux", "turbo"],
                        help="Pollinations模型 (默认flux)")

    args = parser.parse_args()

    if args.list:
        list_tasks()
        return

    # 检查 API Key
    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    if not api_key and not args.dry_run:
        print("提示: 未设置 POLLINATIONS_API_KEY")
        print("  免费注册: https://enter.pollinations.ai/")
        print("  设置: set POLLINATIONS_API_KEY=pk_xxxxxxxx")
        print("\n或使用 --dry-run 只查看prompt")
        sys.exit(1)

    _config["model"] = args.model

    cache = load_cache()
    total = 0

    cat = args.category
    if cat in ("boss", "all"):
        total += gen_bosses(cache, args.dry_run, args.limit)
    if cat in ("bg", "all"):
        total += gen_backgrounds(cache, args.dry_run)
    if cat in ("story", "all"):
        total += gen_story(cache, args.dry_run)
    if cat in ("bombs", "all"):
        total += gen_bombs(cache, args.dry_run)
    if cat in ("vfx", "all"):
        total += gen_vfx(cache, args.dry_run)
    if cat in ("title", "all"):
        total += gen_title(cache, args.dry_run)

    print(f"\n✅ 完成! 共生成 {total} 张素材")


if __name__ == "__main__":
    main()
