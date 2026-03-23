"""
全素材AI生成器 + 每小时自动调度
═══════════════════════════════════════════
三大主题: 樱花幻境(SAKURA) / 蒸汽朋克(STEAM) / 霓虹都市(NEON)
100个Boss (10区域×10Boss)
10张背景 + 6张故事CG + 17种炸弹 + 8种VFX + 3张底材纹理 + 1张标题背景

用法:
  set POLLINATIONS_API_KEY=sk_xxx
  python scripts/tools/gen_all_art.py                 # 全部生成(每小时重试)
  python scripts/tools/gen_all_art.py --category boss  # 只生成Boss
  python scripts/tools/gen_all_art.py --category bg    # 只生成背景
  python scripts/tools/gen_all_art.py --category story  # 只生成故事CG
  python scripts/tools/gen_all_art.py --category ui    # 只生成UI底材+合成
  python scripts/tools/gen_all_art.py --category bombs  # 只生成炸弹
  python scripts/tools/gen_all_art.py --category vfx   # 只生成VFX
  python scripts/tools/gen_all_art.py --category title  # 只生成标题
  python scripts/tools/gen_all_art.py --list            # 列出全部任务
  python scripts/tools/gen_all_art.py --dry-run         # 只打印prompt
  python scripts/tools/gen_all_art.py --no-loop         # 不循环, 跑一轮就停
  python scripts/tools/gen_all_art.py --wait 600        # 限流等待600秒(默认3600)
"""
import os, sys, math, random, hashlib, time, json, datetime, argparse
from pathlib import Path
from urllib.parse import quote

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
    import io, requests
except ImportError:
    print("请先安装: pip install pillow requests")
    sys.exit(1)

random.seed(2026)

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets" / "sprites"
THEMED_DIR = ASSETS / "ui" / "themed"
TEXTURE_DIR = ROOT / "scripts" / "tools" / ".ai_textures"
CACHE_FILE = ROOT / "scripts" / "tools" / ".ai_art_cache.json"

POLLINATIONS_BASE = "https://gen.pollinations.ai"
WAIT_SECONDS = 3600  # 默认1小时

# ═══════════════════════════════════════════════════════════════
#  三大UI主题色板 (与UIThemeManager.gd / gen_theme_sprites.py 同步)
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "sakura": {
        "bg": (18, 10, 22), "bg_light": (35, 22, 42),
        "border": (140, 90, 130), "border_hi": (255, 150, 200),
        "accent": (255, 170, 200), "accent2": (200, 120, 255),
        "text": (255, 235, 245), "danger": (255, 60, 80),
        "heal": (100, 255, 160), "mana": (150, 120, 255),
        "stone": (30, 18, 35), "stone_hi": (52, 35, 58),
        "mortar": (20, 12, 25), "metal": (130, 110, 140),
        "rust": (180, 120, 150),
        "common": (45, 35, 50), "rare": (50, 40, 100), "epic": (110, 40, 120),
        "noise_density": 0.2,
        "style": "sakura",
    },
    "steam": {
        "bg": (22, 16, 10), "bg_light": (42, 30, 18),
        "border": (120, 85, 45), "border_hi": (210, 165, 60),
        "accent": (230, 180, 55), "accent2": (185, 95, 30),
        "text": (240, 225, 190), "danger": (210, 55, 30),
        "heal": (60, 200, 90), "mana": (70, 130, 210),
        "stone": (38, 28, 18), "stone_hi": (60, 45, 28),
        "mortar": (25, 18, 12), "metal": (110, 100, 85),
        "rust": (155, 95, 45),
        "common": (50, 40, 28), "rare": (40, 50, 85), "epic": (85, 35, 80),
        "noise_density": 0.25,
        "style": "gear",
    },
    "neon": {
        "bg": (8, 5, 18), "bg_light": (18, 10, 38),
        "border": (50, 20, 90), "border_hi": (255, 50, 200),
        "accent": (255, 60, 210), "accent2": (0, 230, 255),
        "text": (240, 220, 255), "danger": (255, 40, 80),
        "heal": (0, 255, 170), "mana": (100, 50, 255),
        "stone": (14, 8, 28), "stone_hi": (28, 16, 50),
        "mortar": (6, 3, 14), "metal": (70, 45, 110),
        "rust": (200, 50, 180),
        "common": (22, 14, 40), "rare": (30, 15, 70), "epic": (90, 15, 70),
        "noise_density": 0.15,
        "style": "neon",
    },
}

# ═══════════════════════════════════════════════════════════════
#  UI底材Prompt (每主题1次API)
# ═══════════════════════════════════════════════════════════════
TEXTURE_PROMPTS = {
    "sakura": (
        "seamless tileable Japanese cherry blossom pattern texture, "
        "soft pink petals on dark purple-black background, "
        "delicate sakura flowers, gentle watercolor style, "
        "anime aesthetic, dreamy and ethereal, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
    "steam": (
        "seamless tileable steampunk brass gears and pipes texture, "
        "dark brown background with copper mechanical parts, "
        "cogs wheels rivets and steam vents, industrial Victorian, "
        "warm amber lighting, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
    "neon": (
        "seamless tileable synthwave neon grid texture, "
        "dark purple-black background with glowing hot pink and cyan lines, "
        "retro 80s wireframe grid, vaporwave aesthetic, "
        "neon glow effects, game texture, 512x512, "
        "no text, no watermark, flat top-down view"
    ),
}

# ═══════════════════════════════════════════════════════════════
#  100个Boss定义 (10区域 × 10Boss)
# ═══════════════════════════════════════════════════════════════

# 区域定义
ZONES = [
    {"id": "BAMBOO",  "name": "竹林秘境", "style": "Japanese bamboo forest, misty twilight, zen garden"},
    {"id": "GEAR",    "name": "齿轮要塞", "style": "steampunk factory, brass gears, steam and pipes, Victorian industrial"},
    {"id": "OCEAN",   "name": "深渊之海", "style": "deep ocean abyss, bioluminescent, dark underwater realm"},
    {"id": "LAVA",    "name": "熔岩地狱", "style": "volcanic hellscape, flowing magma, fire and brimstone"},
    {"id": "MOON",    "name": "月华殿堂", "style": "ethereal moonlit celestial palace, silver and crystal, divine light"},
    {"id": "ICE",     "name": "永冻冰原", "style": "frozen tundra, aurora borealis, ice crystals, blizzard"},
    {"id": "TOXIC",   "name": "瘴毒沼泽", "style": "poisonous swamp, glowing toxic plants, sickly green mist"},
    {"id": "GHOST",   "name": "幽灵古城", "style": "haunted ancient Japanese city, ghostly lanterns, spirit realm"},
    {"id": "CHAOS",   "name": "混沌裂隙", "style": "reality-warping dimensional rift, fractured space, impossible geometry"},
    {"id": "VOID",    "name": "虚空深渊", "style": "cosmic void, distant galaxies, eldritch cosmic horror, dark matter"},
]

# 每区域的Boss列表 [key_suffix, chinese_name, creature_desc, grid_w, grid_h]
ZONE_BOSSES = {
    "BAMBOO": [
        ("TANUKI",  "竹林狸猫", "chubby raccoon dog yokai with leaf on head", 3, 3),
        ("KITSUNE", "竹叶狐仙", "elegant nine-tailed fox spirit with sakura", 4, 3),
        ("TENGU",   "天狗",     "red-faced long-nosed tengu with fan", 3, 4),
        ("ONI",     "竹鬼",     "muscular green oni demon with iron club", 4, 4),
        ("JOROUGUMO","络新妇",  "beautiful spider woman yokai with web", 3, 3),
        ("HEBI",    "蛇姬",     "elegant snake princess with scales", 5, 3),
        ("TSURU",   "仙鹤",     "mystical crane with glowing wings", 5, 3),
        ("KUMA",    "墨熊",     "massive ink-black bear with kanji markings", 4, 4),
        ("ENMA",    "灵猿",     "wise spirit ape monk with staff", 3, 4),
        ("RYUU",    "竹龙",     "sinuous eastern dragon among bamboo", 6, 3),
    ],
    "GEAR": [
        ("AUTOMATON","蒸汽傀儡", "mechanical puppet automaton with gears", 3, 4),
        ("TANK",    "铁甲战车",  "armored steam-powered tank with cannons", 5, 3),
        ("ARACHNE", "机械蜘蛛",  "brass spider mech with steam legs", 4, 3),
        ("DRILL",   "钻地机",    "giant drill machine with spinning bit", 3, 4),
        ("CANNON",  "火炮台",    "multi-barrel cannon turret emplacement", 4, 3),
        ("HAWK",    "机械鹰",    "clockwork hawk with brass wings", 5, 3),
        ("BRONZE",  "铜人",      "giant bronze humanoid with furnace chest", 4, 5),
        ("WORM",    "齿轮蠕虫",  "segmented mechanical worm with gears", 6, 3),
        ("KNIGHT",  "蒸汽骑士",  "armored knight in steam-powered exosuit", 4, 5),
        ("COLOSSUS","齿轮巨人",  "colossal clockwork giant towering above", 5, 5),
    ],
    "OCEAN": [
        ("JELLY",   "水母女王",  "giant ethereal jellyfish queen glowing", 4, 4),
        ("SHARK",   "铁齿鲨",    "armored megalodon shark with metal teeth", 6, 3),
        ("KRAKEN",  "深海章鱼",  "massive kraken with swirling tentacles", 5, 5),
        ("SIREN",   "海妖",      "beautiful but deadly siren mermaid", 3, 4),
        ("CRAB",    "钢壳蟹",    "giant armored crab with crystal claws", 5, 3),
        ("SEASERPENT","海蛇",    "coiled sea serpent with water powers", 5, 3),
        ("ANGLER",  "灯笼鱼",    "deep sea anglerfish with bio-light lure", 4, 3),
        ("WHALE",   "幽灵鲸",    "ghostly whale with spiritual glow", 6, 3),
        ("CORAL",   "珊瑚魔",    "living coral reef creature with spines", 4, 4),
        ("LEVIATHAN","利维坦",   "massive leviathan sea monster primordial", 6, 4),
    ],
    "LAVA": [
        ("SALAMANDER","火蜥蜴", "fire salamander with molten skin", 4, 3),
        ("PHOENIX", "熔岩凤凰",  "lava phoenix with dripping magma wings", 5, 4),
        ("MAGMA",   "岩浆巨人",  "golem made of cooling magma and rock", 4, 5),
        ("FIREWORM","火焰虫",    "giant fire centipede with flaming segments", 6, 3),
        ("FIEND",   "烈焰魔",    "fire demon with flaming horns and whip", 4, 5),
        ("DRAKE",   "火龙",      "lava dragon breathing molten fire", 5, 4),
        ("ELEMENTAL","火元素",   "pure fire elemental being of living flame", 3, 4),
        ("CERBERUS","地狱犬",    "three-headed hellhound with fire manes", 5, 4),
        ("PYROHYDRA","熔岩九头蛇","multi-headed lava hydra spitting fire", 6, 4),
        ("IFRIT",   "伊芙利特",  "towering fire djinn lord with crown", 5, 5),
    ],
    "MOON": [
        ("RABBIT",  "玉兔",      "mystical jade rabbit with moon energy", 3, 3),
        ("FAIRY",   "月仙",      "ethereal moon fairy with silver wings", 3, 4),
        ("CRANE",   "月下白鹤",  "celestial crane with moonbeam feathers", 5, 3),
        ("SILVERFOX","银狐",     "silver fox spirit with moon blessing", 4, 3),
        ("MOTH",    "皇蛾",      "giant lunar moth with starlight wings", 5, 4),
        ("OWL",     "夜枭",      "wise great owl with glowing moon eyes", 4, 4),
        ("QILIN",   "麒麟",      "divine qilin unicorn beast with scales", 5, 4),
        ("MOONSPIRIT","月灵",    "pure lunar spirit entity glowing silver", 3, 4),
        ("GUARDIAN","月卫",      "celestial moon guardian in divine armor", 4, 5),
        ("EMPRESS", "月帝",      "beautiful moon empress on crystal throne", 5, 5),
    ],
    "ICE": [
        ("WOLF",    "冰狼",      "ice wolf with frost aura and blue eyes", 4, 3),
        ("BEAR",    "霜熊",      "massive frost bear covered in icicles", 4, 4),
        ("ICEGOLEM","冰巨人",    "towering ice golem with frozen core", 4, 5),
        ("WRAITH",  "寒魄",      "ice wraith spirit made of frost mist", 3, 4),
        ("YETI",    "雪人",      "abominable snowman yeti with ice claws", 4, 4),
        ("ICESPIDER","冰蛛",     "frozen spider with ice crystal web", 4, 3),
        ("ICEPYTHON","冰蟒",     "massive ice python with frozen scales", 6, 3),
        ("FROSTBIRD","冰凤",     "ice phoenix with crystalline feathers", 5, 4),
        ("MAMMOTH", "猛犸",      "ancient mammoth with frozen tusks", 5, 4),
        ("ICEQUEEN","冰后",      "beautiful ice queen with blizzard magic", 4, 5),
    ],
    "TOXIC": [
        ("MUSHROOM","毒菇王",    "giant toxic mushroom king with spores", 3, 4),
        ("TOAD",    "毒蟾",      "massive poison toad with warts", 4, 3),
        ("VINE",    "噬人藤",    "carnivorous plant vine with thorns", 3, 5),
        ("SLUG",    "酸液蛞蝓",  "giant acid slug leaving corrosive trail", 5, 3),
        ("SCORPION","剧毒蝎",    "giant venomous scorpion with glowing tail", 5, 3),
        ("BEETLE",  "腐蚀甲虫",  "armored beetle with acid spray", 4, 3),
        ("ORCHID",  "幽兰",      "deadly beautiful orchid flower monster", 3, 4),
        ("SWAMPTHING","沼泽怪",  "amorphous swamp creature of mud and toxin", 4, 4),
        ("TOXHYDRA","毒九头蛇",  "multi-headed poison hydra dripping venom", 6, 4),
        ("PLAGUELORD","瘟疫使",  "plague lord in tattered robes with miasma", 4, 5),
    ],
    "GHOST": [
        ("SAMURAI", "幽灵武士",  "spectral samurai ghost with katana", 3, 4),
        ("GEISHA",  "怨灵艺伎",  "ghostly geisha with pale face and rage", 3, 4),
        ("LANTERN", "灯笼鬼",    "floating lantern ghost with eerie glow", 3, 3),
        ("SKELETON","骸骨兵",    "animated skeleton warrior with sword", 3, 4),
        ("BANSHEE", "哭泣女",    "screaming banshee ghost with flowing hair", 3, 4),
        ("REAPER",  "死神",      "grim reaper with scythe and dark cloak", 4, 5),
        ("PUPPET",  "人偶师",    "puppet master ghost controlling marionettes", 4, 4),
        ("SHADOWGHOST","影鬼",   "shadow ghost that merges with darkness", 4, 4),
        ("WRAITHKING","怨灵王",  "wraith king with crown and ghostly army", 5, 5),
        ("LICH",    "巫妖",      "undead lich sorcerer with skull staff", 4, 5),
    ],
    "CHAOS": [
        ("MIMIC",   "混沌拟态",  "shapeshifting mimic creature of chaos", 3, 3),
        ("EYE",     "千眼",      "floating mass of hundreds of eyes", 4, 4),
        ("BLOB",    "混沌粘液",  "amorphous chaos blob absorbing reality", 4, 3),
        ("CHIMERA", "奇美拉",    "chimera beast with multiple animal heads", 5, 4),
        ("RIFTWORM","裂隙虫",    "reality-warping dimensional worm", 6, 3),
        ("CHAOSGARGOYLE","混沌石像","gargoyle with fractured reality aura", 4, 4),
        ("CHAOSGOLEM","混沌巨人","golem made of broken reality fragments", 5, 5),
        ("CHAOSWITCH","混沌巫师","chaos witch warping space around her", 4, 5),
        ("CHAOSDRAGON","混沌龙", "dragon of warped dimensions breathing chaos", 6, 4),
        ("CHAOSLORD","混沌主宰", "lord of chaos sitting on impossible throne", 5, 5),
    ],
    "VOID": [
        ("PHANTOM", "虚空幻影",  "ethereal void phantom flickering in and out", 3, 4),
        ("CRYSTAL", "虚空水晶",  "cosmic crystal entity with star core", 4, 4),
        ("VOIDSERPENT","虚空巨蟒","giant serpent of dark matter and starlight", 6, 3),
        ("VOIDTITAN","虚空泰坦", "colossal titan made of cosmic matter", 5, 5),
        ("VOIDREAPER","虚空收割者","void reaper harvesting cosmic energy", 4, 5),
        ("VOIDHYDRA","虚空九头蛇","hydra of the void with galaxy heads", 6, 4),
        ("VOIDPHOENIX","虚空凤凰","phoenix reborn from cosmic nebula", 5, 4),
        ("VOIDDEMON","虚空魔王", "demon lord of the void with dark galaxy wings", 5, 5),
        ("VOIDDRAGON","虚空巨龙","ultimate dragon of cosmic darkness", 6, 5),
        ("VOIDGOD", "虚空神",    "god-like entity of pure void energy, final boss", 6, 6),
    ],
}

# 区域色彩 (用于LevelData.gd的level color)
ZONE_COLORS = {
    "BAMBOO": (0.40, 0.70, 0.45),
    "GEAR":   (0.70, 0.55, 0.30),
    "OCEAN":  (0.25, 0.50, 0.80),
    "LAVA":   (0.90, 0.35, 0.15),
    "MOON":   (0.70, 0.65, 0.90),
    "ICE":    (0.50, 0.75, 0.95),
    "TOXIC":  (0.45, 0.75, 0.25),
    "GHOST":  (0.60, 0.50, 0.70),
    "CHAOS":  (0.80, 0.30, 0.60),
    "VOID":   (0.40, 0.25, 0.65),
}

# ═══════════════════════════════════════════════════════════════
#  背景场景 (10个, 每区域1张)
# ═══════════════════════════════════════════════════════════════
BG_SCENES = {
    "bg_bamboo_grove":   "mystical Japanese bamboo forest at twilight, mist between tall bamboo, stone lanterns, zen garden path",
    "bg_gear_fortress":  "steampunk factory interior, massive brass gears turning, steam vents, copper pipes, Victorian industrial hall",
    "bg_deep_ocean":     "deep underwater abyss realm, bioluminescent jellyfish, coral and ancient ruins, dark blue depths",
    "bg_lava_hellscape": "volcanic hellscape with flowing magma rivers, obsidian pillars, fire and brimstone, infernal glow",
    "bg_moon_palace":    "ethereal moonlit celestial palace, crystal pillars, floating platforms, silver moonbeams, divine clouds",
    "bg_frozen_tundra":  "frozen tundra landscape, aurora borealis, ice crystal formations, snowstorm, ancient frozen temple",
    "bg_toxic_swamp":    "poisonous swamp at night, glowing toxic mushrooms, bubbling green pools, dead twisted trees, mist",
    "bg_ghost_city":     "haunted ancient Japanese city at night, ghostly paper lanterns, fog, torii gates, spirit wisps",
    "bg_chaos_rift":     "dimensional rift in reality, fractured space, impossible geometry, warped colors, reality breaking apart",
    "bg_void_abyss":     "cosmic void with distant galaxies, dark matter clouds, stars and nebulae, cosmic horror atmosphere",
}

# ═══════════════════════════════════════════════════════════════
#  故事CG (6帧)
# ═══════════════════════════════════════════════════════════════
STORY_FRAMES = {
    "story_01_world":        "beautiful fantasy world with ten floating realms connected by bridges, wide panoramic view, peaceful sky",
    "story_02_invasion":     "dark portals opening across the sky, monsters pouring out, world in chaos, dramatic lightning",
    "story_03_hero":         "young bomber hero picking up glowing bomb in ruins, determined expression, dawn light behind",
    "story_04_journey":      "hero entering a mystical bamboo gate, ten realm towers visible in distance, epic adventure beginning",
    "story_05_victory":      "hero celebrating with explosion behind defeated boss, golden light rays, triumphant pose",
    "story_06_final":        "hero facing cosmic void god in epic final arena, all elements converging, ultimate showdown",
}

# ═══════════════════════════════════════════════════════════════
#  炸弹类型
# ═══════════════════════════════════════════════════════════════
BOMB_TYPES = {
    "pierce_h":  "horizontal piercing arrow bomb, blue energy trail",
    "pierce_v":  "vertical piercing arrow bomb, blue energy trail",
    "cross":     "cross-shaped holy bomb, golden sacred glow",
    "x_shot":    "X-shaped explosive, red diagonal energy lines",
    "bounce":    "bouncing rubber bomb, spring coils and rubber",
    "area":      "area-of-effect round bomb, shockwave energy rings",
    "cluster":   "cluster bomb splitting into small sub-munitions",
    "drill":     "drill bomb boring into ground, metal spiral bit",
    "flame":     "fire bomb with dancing flames, orange and red",
    "frost":     "ice bomb with frost crystals, blue and white",
    "poison":    "poison bomb with toxic green cloud",
    "thunder":   "lightning bomb with electric arcs, yellow sparks",
    "holy":      "holy bomb with divine golden cross light",
    "mega":      "massive oversized mega bomb, glowing with power",
    "nova":      "supernova bomb, radiant cosmic explosion energy",
    "scatter":   "scatter bomb with multiple fragments flying out",
    "void":      "void bomb with dark matter purple-black swirl",
}

# ═══════════════════════════════════════════════════════════════
#  VFX特效
# ═══════════════════════════════════════════════════════════════
VFX_EFFECTS = {
    "boss_hit_flash":     "bright white and yellow impact flash, radial burst",
    "chain_spark":        "electric chain lightning spark, blue-white arcs",
    "death_particles":    "explosion death particles, orange and red debris flying",
    "debuff_icon":        "skull debuff status icon, purple poison drip",
    "explosion_ring":     "expanding explosion shockwave ring, orange fiery glow",
    "floor_transition":   "magical portal swirl transition effect, blue-purple vortex",
    "upgrade_shine":      "golden upgrade sparkle shine effect, star glint burst",
    "weak_point_glow":    "pulsing red weak point indicator, target crosshair glow",
}

# ═══════════════════════════════════════════════════════════════
#  风格前缀
# ═══════════════════════════════════════════════════════════════
STYLE_BOSS = (
    "dark fantasy pixel art boss monster sprite, "
    "game asset on solid black background, "
    "top-down view, detailed shading, glowing eyes, "
    "menacing creature, dungeon crawler style, "
    "no text, no watermark, sharp edges"
)

STYLE_BG = (
    "wide landscape environment art, "
    "atmospheric lighting, detailed game background, "
    "16:9 aspect ratio, moody and immersive, "
    "no text, no characters, no watermark"
)

STYLE_STORY = (
    "cinematic illustration, dramatic scene, "
    "game cutscene art 16:9, dramatic lighting, "
    "painterly style with soft gradients, "
    "no text, no watermark, no UI elements"
)

STYLE_BOMB = (
    "pixel art game item icon, fantasy style, "
    "single bomb or explosive weapon on transparent background, "
    "clean sharp edges, top-down view, 64x64 game sprite, "
    "no text, no watermark"
)

STYLE_VFX = (
    "pixel art visual effect sprite, "
    "glowing magical effect on black background, "
    "game VFX asset, semi-transparent edges, "
    "no text, no watermark"
)

STYLE_TITLE = (
    "epic fantasy game title screen background, "
    "ten floating realms visible in cosmic sky, "
    "bomber hero silhouette at mystical gate, "
    "atmospheric fog, magical portals, wide 16:9, "
    "no text, no watermark"
)

BOMB_SHEET_PROMPT = (
    "sprite sheet grid of 20 pixel art bomb and explosive weapon icons, "
    "4 columns 5 rows on solid black background, fantasy game items, "
    "each icon 128x128 pixels with clear black separation lines, "
    "variety of magical bombs: arrow, cross, bouncing, area, cluster, "
    "drill, fire, ice, poison, lightning, holy, mega, nova, scatter, void, "
    "each with unique color and visual effect, pixel art style, "
    "clean sharp edges, no text, no watermark"
)

TITLE_PROMPT = (
    "epic fantasy game title screen background art, "
    "mystical gate between floating realms, "
    "silhouette of bomber hero standing at dimensional crossroads, "
    "ten different world portals visible in cosmic sky, "
    "atmospheric fog, magical energy, wide 16:9, "
    "no text, no watermark, cinematic composition"
)


# ═══════════════════════════════════════════════════════════════
#  辅助函数
# ═══════════════════════════════════════════════════════════════
def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def prompt_hash(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()[:12]

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def shift(color, amt):
    return tuple(clamp(c + amt) for c in color[:3])

def alpha_tuple(color, a):
    return color[:3] + (a,)

RESULT_OK = "ok"
RESULT_CACHED = "cached"
RESULT_RATE_LIMITED = "rate_limited"
RESULT_FAILED = "failed"


def generate_image(prompt, output_path, width=512, height=512, cache=None, dry_run=False):
    """调用 Pollinations.ai API 生成一张图"""
    ph = prompt_hash(prompt)
    if cache and ph in cache and output_path.exists():
        return RESULT_CACHED

    if dry_run:
        print(f"  [dry-run] {output_path.name}: {prompt[:100]}...")
        return RESULT_OK

    output_path.parent.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 100000
    encoded = quote(prompt, safe="")
    url = f"{POLLINATIONS_BASE}/image/{encoded}?width={width}&height={height}&model=flux&seed={seed}&nologo=true"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{now}] {output_path.name} ({width}x{height})...", end=" ", flush=True)

    for attempt in range(2):
        try:
            resp = requests.get(url, headers=headers, timeout=180)
            if resp.status_code == 402:
                print("⏳ 额度耗尽")
                return RESULT_RATE_LIMITED
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt < 1:
                time.sleep(5)
            else:
                print(f"✗ 失败: {e}")
                return RESULT_FAILED
    else:
        return RESULT_FAILED

    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    img.save(str(output_path))
    print("✓")

    if cache is not None:
        cache[ph] = str(output_path.name)
        save_cache(cache)

    time.sleep(1)
    return RESULT_OK


# ═══════════════════════════════════════════════════════════════
#  任务构建器
# ═══════════════════════════════════════════════════════════════
def build_boss_tasks():
    """构建100个Boss生成任务"""
    tasks = []
    for zone in ZONES:
        zone_id = zone["id"]
        zone_style = zone["style"]
        for suffix, cn_name, creature_desc, gw, gh in ZONE_BOSSES[zone_id]:
            key = f"{zone_id}_{suffix}"
            prompt = f"{STYLE_BOSS}, {zone_style}, {creature_desc}"
            path = ASSETS / "boss" / f"boss_{key.lower()}.png"
            tasks.append({"name": f"Boss: {cn_name}", "prompt": prompt,
                          "path": path, "w": 512, "h": 512})
    return tasks

def build_bg_tasks():
    """构建10张背景任务"""
    tasks = []
    for name, desc in BG_SCENES.items():
        prompt = f"{STYLE_BG}, {desc}"
        path = ASSETS / "bg" / f"{name}.png"
        tasks.append({"name": f"BG: {name}", "prompt": prompt,
                      "path": path, "w": 1920, "h": 1080})
    return tasks

def build_story_tasks():
    """构建6张故事CG任务"""
    tasks = []
    for name, desc in STORY_FRAMES.items():
        prompt = f"{STYLE_STORY}, {desc}"
        path = ASSETS / "story" / f"{name}.png"
        tasks.append({"name": f"Story: {name}", "prompt": prompt,
                      "path": path, "w": 1920, "h": 1080})
    return tasks

def build_bomb_tasks():
    """构建单张炸弹合集图 + 切割"""
    tasks = []
    path = ASSETS / "bombs" / "bomb_sheet.png"
    tasks.append({"name": "Bomb sheet", "prompt": BOMB_SHEET_PROMPT,
                  "path": path, "w": 512, "h": 640,
                  "post": "cut_bombs"})
    return tasks

def build_vfx_tasks():
    """构建8张VFX特效任务"""
    tasks = []
    for name, desc in VFX_EFFECTS.items():
        prompt = f"{STYLE_VFX}, {desc}"
        path = ASSETS / "vfx" / f"{name}.png"
        tasks.append({"name": f"VFX: {name}", "prompt": prompt,
                      "path": path, "w": 256, "h": 256})
    return tasks

def build_ui_texture_tasks():
    """构建3张UI底材纹理任务"""
    tasks = []
    for theme, prompt in TEXTURE_PROMPTS.items():
        path = TEXTURE_DIR / f"base_{theme}.png"
        tasks.append({"name": f"UI Texture: {theme}", "prompt": prompt,
                      "path": path, "w": 512, "h": 512,
                      "post": f"compose_{theme}"})
    return tasks

def build_title_task():
    """构建标题背景任务"""
    path = ASSETS / "ui" / "title_bg.png"
    return [{"name": "Title BG", "prompt": TITLE_PROMPT,
             "path": path, "w": 1920, "h": 1080}]


# ═══════════════════════════════════════════════════════════════
#  UI合成 (底材→44个UI组件)
# ═══════════════════════════════════════════════════════════════
UI_COMPONENTS = [
    # (文件名, 宽, 高, 用哪些颜色键)
    ("btn_normal",       220, 56,  "bg_light", "border"),
    ("btn_hover",        220, 56,  "stone_hi", "border_hi"),
    ("btn_end",          220, 56,  "accent2", "accent"),
    ("btn_end_hover",    220, 56,  "accent", "accent2"),
    ("panel_bg",         320, 240, "bg", "border"),
    ("panel_header",     320, 48,  "bg_light", "border_hi"),
    ("card_common",      180, 240, "common", "border"),
    ("card_rare",        180, 240, "rare", "border_hi"),
    ("card_epic",        180, 240, "epic", "accent2"),
    ("hud_bar",          400, 40,  "bg", "border"),
    ("hud_bg",           1920, 64, "bg", "border"),
    ("boss_bar_bg",      300, 24,  "bg", "border"),
    ("boss_bar_fill",    300, 24,  "danger", "accent2"),
    ("hp_bar_bg",        200, 16,  "bg", "border"),
    ("hp_bar_fill",      200, 16,  "heal", "border"),
    ("hp_bar_mid",       200, 16,  "accent", "border"),
    ("mine_hidden",      64, 64,   "stone", "border"),
    ("mine_reveal",      64, 64,   "mortar", "stone"),
    ("mine_bomb",        64, 64,   "danger", "accent2"),
    ("cell_empty",       64, 64,   "bg", "border"),
    ("cell_boss",        64, 64,   "bg_light", "border_hi"),
    ("cell_explode",     64, 64,   "accent2", "accent"),
    ("cell_blocked",     64, 64,   "danger", "border"),
    ("cell_dead",        64, 64,   "mortar", "stone"),
    ("overlay_dark",     320, 240, "bg", "border"),
    ("overlay_intro",    1920, 1080,"bg", "border"),
    ("tooltip_bg",       240, 120, "bg_light", "border"),
    ("selector_bg",      180, 48,  "bg", "border"),
    ("selector_active",  180, 48,  "bg_light", "accent"),
    ("tab_normal",       120, 40,  "bg", "border"),
    ("tab_active",       120, 40,  "bg_light", "accent"),
    ("progress_bg",      200, 12,  "bg", "border"),
    ("progress_fill",    200, 12,  "accent", "border_hi"),
    ("divider_h",        300, 4,   "border", "border"),
    ("divider_v",        4, 200,   "border", "border"),
    ("slot_empty",       64, 64,   "bg", "border"),
    ("slot_filled",      64, 64,   "bg_light", "border_hi"),
    ("popup_bg",         400, 300, "bg", "border_hi"),
    ("toast_bg",         300, 48,  "bg_light", "accent"),
    ("badge_bg",         32, 32,   "accent", "border_hi"),
    ("icon_frame",       48, 48,   "bg_light", "border"),
    ("section_header",   400, 36,  "bg_light", "border"),
    ("footer_bar",       1920, 32, "bg", "border"),
    ("dialog_bg",        480, 320, "bg", "border_hi"),
]

def tile_texture(tex, w, h):
    tw, th = tex.size
    result = Image.new("RGBA", (w, h))
    for y in range(0, h, th):
        for x in range(0, w, tw):
            result.paste(tex, (x, y))
    return result.crop((0, 0, w, h))

def blend_texture(base_img, texture, opacity=0.35):
    w, h = base_img.size
    tex_resized = tile_texture(texture, w, h)
    enhancer = ImageEnhance.Brightness(tex_resized)
    tex_resized = enhancer.enhance(0.6)
    return Image.blend(base_img, tex_resized, opacity)

def make_textured_rect(w, h, bg_color, brd_color, texture, brd_w=2):
    """创建带AI纹理的矩形UI组件"""
    base = Image.new("RGBA", (w, h), bg_color + (255,))
    if texture:
        base = blend_texture(base, texture, 0.30)
    draw = ImageDraw.Draw(base)
    # 边框
    for i in range(brd_w):
        draw.rectangle([i, i, w - 1 - i, h - 1 - i], outline=brd_color + (255,))
    return base

def compose_theme_ui(theme_name, cache=None):
    """用AI底材纹理合成该主题的全部UI组件"""
    tex_path = TEXTURE_DIR / f"base_{theme_name}.png"
    texture = None
    if tex_path.exists():
        texture = Image.open(str(tex_path)).convert("RGBA")

    t = THEMES[theme_name]
    out_dir = THEMED_DIR / theme_name
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for comp in UI_COMPONENTS:
        fname, w, h, bg_key, brd_key = comp[0], comp[1], comp[2], comp[3], comp[4]
        out = out_dir / f"{fname}.png"
        bg_c = t[bg_key]
        brd_c = t[brd_key]
        img = make_textured_rect(w, h, bg_c, brd_c, texture)
        img.save(str(out))
        count += 1

    print(f"  合成 {theme_name}: {count} 个UI组件")
    return count

def cut_bomb_sheet():
    """将炸弹合集图切割为单独图标"""
    sheet_path = ASSETS / "bombs" / "bomb_sheet.png"
    if not sheet_path.exists():
        print("  ✗ bomb_sheet.png 不存在")
        return 0
    sheet = Image.open(str(sheet_path)).convert("RGBA")
    cols, rows = 4, 5
    cw = sheet.width // cols
    ch = sheet.height // rows
    bomb_keys = list(BOMB_TYPES.keys())
    count = 0
    for idx, key in enumerate(bomb_keys):
        if idx >= cols * rows:
            break
        r, c = divmod(idx, cols)
        icon = sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
        icon = icon.resize((128, 128), Image.LANCZOS)
        out = ASSETS / "bombs" / f"bomb_{key}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        icon.save(str(out))
        count += 1
    print(f"  切割炸弹图标: {count} 个")
    return count


# ═══════════════════════════════════════════════════════════════
#  运行批次
# ═══════════════════════════════════════════════════════════════
def run_batch(tasks, cache, dry_run=False):
    """执行一批生成任务, 返回 (完成数, 缓存数, 限流?)"""
    done = 0
    cached = 0
    rate_limited = False
    for t in tasks:
        result = generate_image(t["prompt"], t["path"], t["w"], t["h"], cache, dry_run)
        if result == RESULT_OK:
            done += 1
            # 后处理
            post = t.get("post", "")
            if post == "cut_bombs":
                cut_bomb_sheet()
            elif post.startswith("compose_"):
                theme = post.replace("compose_", "")
                compose_theme_ui(theme, cache)
        elif result == RESULT_CACHED:
            cached += 1
            # 即使缓存也执行后处理
            post = t.get("post", "")
            if post == "cut_bombs":
                cut_bomb_sheet()
            elif post.startswith("compose_"):
                theme = post.replace("compose_", "")
                compose_theme_ui(theme, cache)
        elif result == RESULT_RATE_LIMITED:
            rate_limited = True
            break
        # RESULT_FAILED → 继续下一个
    return done, cached, rate_limited

def count_pending(tasks, cache):
    """统计未完成任务数"""
    pending = 0
    for t in tasks:
        ph = prompt_hash(t["prompt"])
        if ph not in cache:
            pending += 1
    return pending


# ═══════════════════════════════════════════════════════════════
#  列表模式
# ═══════════════════════════════════════════════════════════════
def list_all_tasks():
    """列出所有任务"""
    categories = [
        ("Boss (100)", build_boss_tasks()),
        ("Background (10)", build_bg_tasks()),
        ("Story (6)", build_story_tasks()),
        ("Bombs (1 sheet)", build_bomb_tasks()),
        ("VFX (8)", build_vfx_tasks()),
        ("UI Textures (3)", build_ui_texture_tasks()),
        ("Title (1)", build_title_task()),
    ]
    cache = load_cache()
    total = 0
    total_pending = 0
    for cat_name, tasks in categories:
        pending = count_pending(tasks, cache)
        total += len(tasks)
        total_pending += pending
        status = "✓ 已完成" if pending == 0 else f"⏳ {pending}/{len(tasks)} 待生成"
        print(f"  {cat_name}: {status}")
    print(f"\n  总计: {total} 任务, {total_pending} 待生成, {total - total_pending} 已缓存")


# ═══════════════════════════════════════════════════════════════
#  主循环
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="全素材AI生成器")
    parser.add_argument("--category", default="all",
                        choices=["all", "boss", "bg", "story", "bombs", "vfx", "ui", "title"])
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--dry-run", action="store_true", help="只打印prompt")
    parser.add_argument("--no-loop", action="store_true", help="不循环")
    parser.add_argument("--wait", type=int, default=WAIT_SECONDS, help="限流等待秒数")
    args = parser.parse_args()

    if args.list:
        print("\n═══ 全部生成任务 ═══")
        list_all_tasks()
        return

    # 构建任务列表
    all_tasks = []
    cat = args.category
    if cat in ("all", "ui"):
        all_tasks.extend(build_ui_texture_tasks())
    if cat in ("all", "title"):
        all_tasks.extend(build_title_task())
    if cat in ("all", "bombs"):
        all_tasks.extend(build_bomb_tasks())
    if cat in ("all", "boss"):
        all_tasks.extend(build_boss_tasks())
    if cat in ("all", "bg"):
        all_tasks.extend(build_bg_tasks())
    if cat in ("all", "story"):
        all_tasks.extend(build_story_tasks())
    if cat in ("all", "vfx"):
        all_tasks.extend(build_vfx_tasks())

    print(f"\n═══ 素材生成器 ({cat}) ═══")
    print(f"  任务数: {len(all_tasks)}")
    print(f"  限流等待: {args.wait}秒")
    print(f"  循环模式: {'否' if args.no_loop else '是'}")

    round_num = 0
    while True:
        round_num += 1
        cache = load_cache()
        pending = count_pending(all_tasks, cache)
        if pending == 0:
            print(f"\n🎉 全部 {len(all_tasks)} 个任务完成!")
            # 确保所有UI合成都已执行
            for theme in THEMES:
                compose_theme_ui(theme, cache)
            cut_bomb_sheet()
            break

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n── 第{round_num}轮 [{now}] 待生成: {pending}/{len(all_tasks)} ──")

        done, cached, rate_limited = run_batch(all_tasks, cache, args.dry_run)
        print(f"  本轮: 生成{done} 缓存{cached}", end="")
        if rate_limited:
            print(" 触发限流")
        else:
            print()

        if args.dry_run or args.no_loop:
            break

        if rate_limited:
            cache = load_cache()
            remaining = count_pending(all_tasks, cache)
            if remaining == 0:
                print(f"\n🎉 全部完成!")
                break
            next_time = (datetime.datetime.now() +
                         datetime.timedelta(seconds=args.wait)).strftime("%H:%M:%S")
            print(f"  ⏳ 等待{args.wait}秒后重试 (预计{next_time})...")
            print(f"     剩余: {remaining} 个任务")
            print(f"     按Ctrl+C可安全退出(进度已保存)")
            try:
                time.sleep(args.wait)
            except KeyboardInterrupt:
                print("\n\n⚡ 已安全退出, 进度已保存")
                return
        else:
            # 没有限流但可能有失败, 检查是否全部完成
            cache = load_cache()
            remaining = count_pending(all_tasks, cache)
            if remaining == 0:
                print(f"\n🎉 全部完成!")
                for theme in THEMES:
                    compose_theme_ui(theme, cache)
                break
            # 有失败的, 等一会儿重试
            print(f"  剩余{remaining}个, 30秒后重试...")
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n\n⚡ 已安全退出")
                return


if __name__ == "__main__":
    main()
