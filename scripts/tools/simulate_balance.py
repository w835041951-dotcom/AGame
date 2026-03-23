"""
模拟每关的炸弹伤害量 vs Boss血量，帮助调整难度
"""

# ── Boss形状 → 格子数 ──
BOSS_GRID_SIZE = {
    "DARK_GARGOYLE": (3,3), "DARK_SPIDER": (3,3), "DARK_SERPENT": (4,3),
    "DARK_GIANT": (5,4), "DARK_DEMON": (4,4), "DARK_WITCH": (3,4),
    "DARK_WYVERN": (5,3), "DARK_KRAKEN": (4,4), "DARK_GOLEM": (3,4),
    "DARK_WOLF": (4,4), "DARK_TITAN": (5,4), "DARK_MUSHROOM": (3,4),
    "DARK_CRYSTAL": (3,4), "DARK_ASSASSIN": (3,4), "DARK_PHOENIX": (5,4),
    "DARK_LICH": (4,4), "DARK_GHOST": (3,4), "DARK_EAGLE": (6,3),
    "DARK_HYDRA": (5,4), "DARK_DRAGON": (6,4),
}

# ── 20关数据 ──
LEVELS = [
    {"id": 1,  "boss_shape": "DARK_GARGOYLE", "bomb_count": 6},
    {"id": 2,  "boss_shape": "DARK_SPIDER",   "bomb_count": 6},
    {"id": 3,  "boss_shape": "DARK_SERPENT",   "bomb_count": 6},
    {"id": 4,  "boss_shape": "DARK_GIANT",     "bomb_count": 6},
    {"id": 5,  "boss_shape": "DARK_DEMON",     "bomb_count": 6},
    {"id": 6,  "boss_shape": "DARK_WITCH",     "bomb_count": 6},
    {"id": 7,  "boss_shape": "DARK_WYVERN",    "bomb_count": 6},
    {"id": 8,  "boss_shape": "DARK_KRAKEN",    "bomb_count": 6},
    {"id": 9,  "boss_shape": "DARK_GOLEM",     "bomb_count": 6},
    {"id": 10, "boss_shape": "DARK_WOLF",      "bomb_count": 6},
    {"id": 11, "boss_shape": "DARK_TITAN",     "bomb_count": 7},
    {"id": 12, "boss_shape": "DARK_MUSHROOM",  "bomb_count": 7},
    {"id": 13, "boss_shape": "DARK_CRYSTAL",   "bomb_count": 7},
    {"id": 14, "boss_shape": "DARK_ASSASSIN",  "bomb_count": 7},
    {"id": 15, "boss_shape": "DARK_PHOENIX",   "bomb_count": 7},
    {"id": 16, "boss_shape": "DARK_LICH",      "bomb_count": 7},
    {"id": 17, "boss_shape": "DARK_GHOST",     "bomb_count": 7},
    {"id": 18, "boss_shape": "DARK_EAGLE",     "bomb_count": 7},
    {"id": 19, "boss_shape": "DARK_HYDRA",     "bomb_count": 7},
    {"id": 20, "boss_shape": "DARK_DRAGON",    "bomb_count": 7},
]

# ── 炸弹基础伤害 ──
BOMB_DAMAGE = {
    "pierce_h": 15, "pierce_v": 15,
    "cross": 12, "x_shot": 12,
    "bounce": 8, "scatter": 6,
}

HP_PER_TILE = 10


def get_tile_count(shape_key):
    w, h = BOSS_GRID_SIZE[shape_key]
    return w * h


def simulate():
    print("=" * 100)
    print(f"{'层':>4} {'Boss':^16} {'格子':>4} {'HP倍':>5} {'Boss总HP':>8} "
          f"{'炸弹数':>6} {'理论伤害':>8} {'覆盖率':>6} "
          f"{'需回合':>6} {'难度':>8}")
    print("-" * 100)

    for floor_n in range(1, 101):
        cycle = (floor_n - 1) // 20
        level_idx = (floor_n - 1) % 20
        level = LEVELS[level_idx]

        shape = level["boss_shape"]
        tile_count = get_tile_count(shape)
        hp_mult = 1.0 + cycle * 0.5
        boss_total_hp = int(HP_PER_TILE * hp_mult) * tile_count

        # 炸弹数 = 基础 + cycle*2（扫雷中能找到的）
        bomb_count = level["bomb_count"] + cycle * 2

        # ── 估算单回合最大伤害 ──
        # 假设：玩家翻到所有炸弹，合理放置
        # 平均炸弹伤害 ≈ 加权平均（多pierce/cross，少scatter）
        avg_bomb_dmg = 13.0  # pierce(15) 和 cross(12) 为主

        # 每颗炸弹平均命中boss格子数（取决于boss大小和炸弹类型）
        # pierce_h: 命中 boss_width 格 (3~6)
        # pierce_v: 命中 boss_height 格 (3~4)  
        # cross: 命中约 2*(reach)-1 格，但很多在boss外
        # 实际命中率：boss占放置区比例
        boss_w, boss_h = BOSS_GRID_SIZE[shape]
        placement_cols = level_idx // 10 * 1 + 8 + cycle  # 简化: 8~9 + cycle
        if level_idx >= 10:
            placement_cols = 9 + cycle
        else:
            placement_cols = 8 + cycle
        placement_rows = 5 if level_idx < 18 else 6

        # 单颗炸弹 平均命中boss格子数
        # pierce_h 穿整行 → 命中 min(boss_w, reach*2+1) 中在boss区域的格子
        # 简化估算：boss覆盖率
        boss_area_ratio = tile_count / (placement_cols * placement_rows)

        # 理想单次放置伤害（所有炸弹都放在最优位置）
        # 乐观估算：每炸弹平均命中2~3个boss格子
        avg_hit_tiles = min(3.0, boss_w * 0.6)  # pierce类更高
        single_bomb_dmg = avg_bomb_dmg * avg_hit_tiles

        # 单回合总伤害（无升级、无连锁）
        turn_damage_no_chain = int(single_bomb_dmg * bomb_count)

        # 加连锁估计（2~3颗炸弹互相连锁，+30%）
        chain_bonus = 1.15 if bomb_count >= 4 else 1.0
        turn_damage = int(turn_damage_no_chain * chain_bonus)

        # 需要几回合击杀
        turns_needed = boss_total_hp / max(turn_damage, 1)

        # 难度评级
        if turns_needed <= 1.5:
            diff = "🟢 简单"
        elif turns_needed <= 2.5:
            diff = "🟡 适中"
        elif turns_needed <= 4.0:
            diff = "🟠 困难"
        else:
            diff = "🔴 极难"

        prefix = ""
        if level_idx == 0:
            prefix = f"\n{'─'*100}\n  ◆ 周期 {cycle} (第{floor_n}-{floor_n+19}层) hp倍率={hp_mult:.1f}x\n{'─'*100}\n"

        if prefix:
            print(prefix, end="")

        print(f"{floor_n:>4} {shape:^16} {tile_count:>4} {hp_mult:>5.1f} {boss_total_hp:>8} "
              f"{bomb_count:>6} {turn_damage:>8} {boss_area_ratio:>5.0%} "
              f"{turns_needed:>6.1f} {diff:>8}")

    print("\n" + "=" * 100)
    print("\n📊 模拟参数说明:")
    print(f"  • 格子血量: {HP_PER_TILE}")
    print(f"  • 炸弹平均伤害: ~13 (pierce=15, cross=12)")
    print(f"  • 每炸弹平均命中Boss格子: ~2-3格")
    print(f"  • 连锁加成估算: ~15% (4+炸弹)")
    print(f"  • 无战斗升级加成")
    print(f"\n🎯 难度参考:")
    print(f"  🟢 ≤1.5回合  🟡 ≤2.5回合  🟠 ≤4回合  🔴 >4回合")


if __name__ == "__main__":
    simulate()
