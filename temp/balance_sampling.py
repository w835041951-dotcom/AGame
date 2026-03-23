import json
import math
import random
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
LEVEL_DATA_PATH = ROOT / "scripts" / "core" / "LevelData.gd"
BOMB_REG_PATH = ROOT / "scripts" / "bombs" / "BombRegistry.gd"
GAME_MANAGER_PATH = ROOT / "scripts" / "core" / "GameManager.gd"
GRID_MANAGER_PATH = ROOT / "scripts" / "core" / "GridManager.gd"
BOSS_GRID_PATH = ROOT / "scripts" / "boss" / "BossGrid.gd"
EXP_CALC_PATH = ROOT / "scripts" / "boss" / "ExplosionCalc.gd"
UPGRADE_MANAGER_PATH = ROOT / "scripts" / "core" / "UpgradeManager.gd"


@dataclass
class RunResult:
    run_id: int
    seed: int
    floors_cleared: int
    turns: int
    total_damage: int
    avg_turn_damage: float
    avg_click_delta_per_turn: float
    avg_intel_delta_per_turn: float
    ending_hp: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_boss_grid_size(text: str) -> Dict[str, Tuple[int, int]]:
    out: Dict[str, Tuple[int, int]] = {}
    for m in re.finditer(r'"([A-Z0-9_]+)"\s*:\s*Vector2i\((\d+),\s*(\d+)\)', text):
        out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return out


def parse_level_blocks(level_data_text: str) -> List[Dict[str, int]]:
    anchor = "const LEVELS = ["
    start = level_data_text.find(anchor)
    if start < 0:
        raise RuntimeError("LEVELS section not found")
    i = start + len(anchor)
    depth = 1
    block = []
    blocks = []
    while i < len(level_data_text):
        ch = level_data_text[i]
        if ch == "{" and depth >= 1:
            depth += 1
            block.append(ch)
        elif ch == "}" and depth >= 2:
            block.append(ch)
            depth -= 1
            if depth == 1:
                blocks.append("".join(block))
                block = []
        elif depth >= 2:
            block.append(ch)
        elif ch == "]" and depth == 1:
            break
        i += 1

    levels: List[Dict[str, int]] = []
    keys_int = [
        "id",
        "bomb_count",
        "base_clicks",
        "boss_attack",
        "placement_cols",
        "placement_rows",
        "mine_cols",
        "mine_rows",
    ]
    keys_float = ["turn_duration", "boss_move_interval"]

    for b in blocks:
        entry: Dict[str, int] = {}
        for k in keys_int:
            m = re.search(rf'"{k}"\s*:\s*(-?\d+)', b)
            if not m:
                raise RuntimeError(f"key {k} missing in level block")
            entry[k] = int(m.group(1))
        for k in keys_float:
            m = re.search(rf'"{k}"\s*:\s*([0-9]+(?:\.[0-9]+)?)', b)
            if not m:
                raise RuntimeError(f"key {k} missing in level block")
            entry[k] = float(m.group(1))
        m = re.search(r'"boss_shape"\s*:\s*"([A-Z0-9_]+)"', b)
        if not m:
            raise RuntimeError("boss_shape missing")
        entry["boss_shape"] = m.group(1)
        levels.append(entry)
    return levels


def parse_bomb_damage_map(text: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for m in re.finditer(r'"([a-z_]+)"\s*:\s*\{[^\}]*?"damage"\s*:\s*(\d+),', text, flags=re.S):
        out[m.group(1)] = int(m.group(2))
    return out


def parse_balance_constants() -> Dict[str, float]:
    exp = read_text(EXP_CALC_PATH)
    game = read_text(GAME_MANAGER_PATH)
    grid = read_text(GRID_MANAGER_PATH)
    boss = read_text(BOSS_GRID_PATH)

    c = {}

    m = re.search(r'base_dmg \*=\s*([0-9.]+)\s*\n\t\tif bomb_type == "ultimate"', exp)
    c["pollution_factor"] = float(m.group(1)) if m else 0.78

    m = re.search(r'bonus_mult = 1.0 \+ \(hits\.size\(\) - 1\) \* ([0-9.]+)', exp)
    c["overlap_step"] = float(m.group(1)) if m else 0.3

    m = re.search(r'crit_chance = ([0-9.]+) \+ min\(active_bombs\.size\(\) \* ([0-9.]+), ([0-9.]+)\)', exp)
    c["crit_base"] = float(m.group(1)) if m else 0.06
    c["crit_per_bomb"] = float(m.group(2)) if m else 0.03
    c["crit_cap"] = float(m.group(3)) if m else 0.12

    m = re.search(r'dmg \*=\s*([0-9.]+)\s*\n\t\t\tfinal_sum \+= dmg', exp)
    c["shield_factor"] = float(m.group(1)) if m else 0.65

    m = re.search(r'_second_wave\(active_bombs,\s*([0-9.]+)\)', exp)
    c["double_detonate_ratio"] = float(m.group(1)) if m else 0.55

    m = re.search(r'if current_phase >= 2 and randf\(\) < \(([0-9.]+) if current_phase == 2 else ([0-9.]+)\)', boss)
    c["summon_p2"] = float(m.group(1)) if m else 0.16
    c["summon_p3"] = float(m.group(2)) if m else 0.28

    m = re.search(r'if roll < ([0-9.]+):\n\t\t# 10%: 额外获得1次点击', grid)
    c["lucky_click"] = float(m.group(1)) if m else 0.10
    m = re.search(r'elif roll < ([0-9.]+):\n\t\t# 5%: 额外获得一个随机炸弹', grid)
    c["lucky_bomb"] = float(m.group(1)) if m else 0.15
    m = re.search(r'elif roll < ([0-9.]+):\n\t\t# 3%: 回复少量生命', grid)
    c["lucky_heal"] = float(m.group(1)) if m else 0.18

    m = re.search(r'var supply_n = max\(1, int\(total \* ([0-9.]+)\)\)', grid)
    c["supply_rate"] = float(m.group(1)) if m else 0.09
    m = re.search(r'var relic_n = max\(1, int\(total \* ([0-9.]+)\)\)', grid)
    c["relic_rate"] = float(m.group(1)) if m else 0.04
    m = re.search(r'var risk_n = max\(1, int\(total \* ([0-9.]+)\)\)', grid)
    c["risk_rate"] = float(m.group(1)) if m else 0.04

    m = re.search(r'if not available\.is_empty\(\) and randf\(\) < ([0-9.]+)', grid)
    c["relic_affix_p"] = float(m.group(1)) if m else 0.55
    m = re.search(r'if randf\(\) < ([0-9.]+):\n\t\t\t\tvar t = BombRegistry.get_available_types\(\)', grid)
    c["relic_bonus_bomb_p"] = float(m.group(1)) if m else 0.35

    if "_chain_multiplier_perm = 0.6" in read_text(UPGRADE_MANAGER_PATH):
        c["chain_boost_value"] = 0.6
    else:
        c["chain_boost_value"] = 0.5

    # challenge strings fixed in GameManager
    c["challenge_chain"] = "连锁强化：连锁加成+20%，点击-1"
    c["challenge_shield"] = "护盾风暴：Boss护盾格+1"
    c["challenge_cooldown"] = "冷却回路：过载效果伤害+20%"
    c["challenge_intel"] = "情报富集：每回合+1情报"

    return c


def calc_damage(base: int, affixes: set) -> int:
    dmg = base
    if "overload" in affixes:
        dmg = int(dmg * 1.6)
    elif "delay" in affixes:
        dmg = int(dmg * 1.2)
    return dmg


def roll_challenge(rng: random.Random, floor_number: int, last: str, c: Dict[str, float]) -> str:
    weighted = [c["challenge_chain"], c["challenge_shield"], c["challenge_intel"]]
    if floor_number >= 5:
        weighted.append(c["challenge_cooldown"])
    if floor_number >= 12:
        weighted.append(c["challenge_cooldown"])
    if floor_number >= 20:
        weighted.append(c["challenge_shield"])
    picked = rng.choice(weighted)
    if len(weighted) > 1 and picked == last:
        picked = rng.choice(weighted)
    return picked


def run_once(
    run_id: int,
    seed: int,
    levels: List[Dict[str, int]],
    grid_sizes: Dict[str, Tuple[int, int]],
    bomb_damage: Dict[str, int],
    c: Dict[str, float],
) -> RunResult:
    rng = random.Random(seed)

    # progression state
    unlocked = ["pierce_h", "pierce_v"]
    affixes: Dict[str, set] = {k: set() for k in bomb_damage.keys()}
    inventory: Dict[str, int] = {}
    cooldowns: Dict[str, int] = {}
    chain_bonus_base = 0.3

    hp = 30
    floor = 1
    turns_total = 0
    dmg_total = 0
    clicks_delta_total = 0.0
    intel_delta_total = 0.0
    last_challenge = ""

    while hp > 0 and floor <= 200:
        level = levels[(floor - 1) % len(levels)]
        cycle = (floor - 1) // len(levels)

        hp_mult = (1.0 + cycle * 0.5)
        shape = level["boss_shape"]
        w, h = grid_sizes[shape]
        boss_hp = int(w * h * 10 * hp_mult)

        mine_cols = level["mine_cols"] + cycle
        mine_rows = level["mine_rows"]
        base_bomb = level["bomb_count"] + cycle * 2
        bomb_count = max(base_bomb, 2)
        total_cells = mine_cols * mine_rows
        bomb_hidden = min(bomb_count, total_cells - 1)
        nonbomb_hidden = total_cells - bomb_hidden

        max_clicks = level["base_clicks"] + cycle * 3
        boss_attack = level["boss_attack"] + cycle * 3

        # special pool counts
        supply_left = max(1, int(nonbomb_hidden * c["supply_rate"]))
        relic_left = max(1, int(nonbomb_hidden * c["relic_rate"]))
        risk_left = max(1, int(nonbomb_hidden * c["risk_rate"]))

        challenge = roll_challenge(rng, floor, last_challenge, c)
        last_challenge = challenge

        streak = 0
        floor_turns = 0
        floor_click_gain = 0
        floor_click_spend = 0
        floor_intel_gain = 0
        floor_intel_spend = 0

        while boss_hp > 0 and hp > 0 and floor_turns < 80:
            floor_turns += 1
            turns_total += 1

            # tick cooldowns
            for t in list(cooldowns.keys()):
                cooldowns[t] -= 1
                if cooldowns[t] <= 0:
                    del cooldowns[t]

            clicks = max_clicks
            if challenge == c["challenge_chain"]:
                clicks = max(1, clicks - 1)
            if challenge == c["challenge_intel"]:
                floor_intel_gain += 1

            # reveal loop
            i = 0
            while i < clicks and (bomb_hidden + nonbomb_hidden) > 0:
                i += 1
                floor_click_spend += 1
                hidden_total = bomb_hidden + nonbomb_hidden
                bomb_p = bomb_hidden / hidden_total
                if rng.random() < bomb_p:
                    bomb_hidden -= 1
                    btype = rng.choice(unlocked)
                    if btype != "ultimate" or inventory.get(btype, 0) == 0:
                        inventory[btype] = inventory.get(btype, 0) + 1
                    streak += 1

                    # lucky find
                    roll = rng.random()
                    if roll < c["lucky_click"]:
                        clicks += 1
                        floor_click_gain += 1
                    elif roll < c["lucky_bomb"]:
                        b2 = rng.choice(unlocked)
                        if b2 != "ultimate" or inventory.get(b2, 0) == 0:
                            inventory[b2] = inventory.get(b2, 0) + 1
                    elif roll < c["lucky_heal"]:
                        hp = min(30, hp + 3)

                    # streak rewards
                    if streak == 3:
                        clicks += 1
                        floor_click_gain += 1
                    elif streak == 5:
                        b3 = rng.choice(unlocked)
                        if b3 != "ultimate" or inventory.get(b3, 0) == 0:
                            inventory[b3] = inventory.get(b3, 0) + 1
                    elif streak >= 7 and streak % 3 == 1:
                        hp = min(30, hp + 1)
                        clicks += 1
                        floor_click_gain += 1
                else:
                    nonbomb_hidden -= 1
                    streak = 0
                    sp_total = supply_left + relic_left + risk_left
                    if sp_total > 0:
                        r = rng.randint(1, max(1, nonbomb_hidden + sp_total))
                        if r <= sp_total:
                            pick = rng.randint(1, sp_total)
                            if pick <= supply_left:
                                supply_left -= 1
                                clicks += 1
                                floor_click_gain += 1
                                floor_intel_gain += 1
                            elif pick <= supply_left + relic_left:
                                relic_left -= 1
                                floor_intel_gain += 2
                                # reroll token omitted from combat math, not direct DPS
                                if unlocked and rng.random() < c["relic_affix_p"]:
                                    target = rng.choice(unlocked)
                                    pool = ["ignite", "delay", "link", "pierce", "overload"]
                                    can = [a for a in pool if a not in affixes[target]]
                                    if can:
                                        affixes[target].add(rng.choice(can))
                                if rng.random() < c["relic_bonus_bomb_p"]:
                                    b4 = rng.choice(unlocked)
                                    if b4 != "ultimate" or inventory.get(b4, 0) == 0:
                                        inventory[b4] = inventory.get(b4, 0) + 1
                            else:
                                risk_left -= 1
                                clicks = max(i, clicks - 1)
                                floor_intel_gain += 1

            # choose bombs to use this turn (up to 7 practical placements)
            usable: List[str] = []
            for t, ct in inventory.items():
                if ct <= 0:
                    continue
                if cooldowns.get(t, 0) > 0:
                    continue
                usable.extend([t] * ct)

            if not usable:
                # no outgoing damage, player takes pressure damage
                incoming = max(1, int(boss_attack * (0.22 + 0.01 * floor_turns)))
                hp -= incoming
                continue

            # prioritize stronger bombs
            usable.sort(key=lambda t: calc_damage(bomb_damage[t], affixes[t]), reverse=True)
            used = usable[:7]
            used_counts: Dict[str, int] = {}
            for t in used:
                used_counts[t] = used_counts.get(t, 0) + 1
                inventory[t] -= 1
                if inventory[t] <= 0:
                    del inventory[t]

            n = len(used)
            chain_per = chain_bonus_base + (0.2 if challenge == c["challenge_chain"] else 0.0)
            chain_mult = 1.0 + min(chain_per * 0.35 * max(0, n - 1), 1.5)
            overlap_mult = 1.0 + c["overlap_step"] * max(0, n - 1) * 0.45
            crit = c["crit_base"] + min(n * c["crit_per_bomb"], c["crit_cap"])
            crit_expect = 1.0 + 0.5 * crit

            # approximate phase-dependent shield/pollution factors
            # phase thresholds 70% / 35%
            hp_ratio = boss_hp / max(1.0, float(int(w * h * 10 * hp_mult)))
            phase = 1
            if hp_ratio <= 0.35:
                phase = 3
            elif hp_ratio <= 0.70:
                phase = 2

            shield_extra = 1 if challenge == c["challenge_shield"] else 0
            shield_n = 0 if phase == 1 else (phase + shield_extra - 0)
            shield_ratio = min(0.85, shield_n / max(1, w * h))

            non_pierce_ratio = 1.0
            pierce_n = sum(1 for t in used if t in {"pierce_h", "pierce_v", "ultimate"} or "pierce" in affixes[t])
            non_pierce_ratio = max(0.0, 1.0 - pierce_n / max(1, n))
            shield_factor = 1.0 - shield_ratio * (1.0 - c["shield_factor"]) * non_pierce_ratio

            pollute_n = 0 if phase < 3 else 3
            placement_cells = (level["placement_cols"] + cycle) * level["placement_rows"]
            pollute_ratio = pollute_n / max(1, placement_cells)
            pollution_expect = 1.0 - pollute_ratio * (1.0 - c["pollution_factor"]) * 0.85

            base_sum = 0.0
            second_wave = 0.0
            delayed_wave = 0.0
            overload_types: List[str] = []

            for t in used:
                d = calc_damage(bomb_damage[t], affixes[t])
                if challenge == c["challenge_cooldown"] and "overload" in affixes[t]:
                    d = int(d * 1.2)
                if t == "ultimate":
                    d = int(d * 1.2)
                if "ignite" in affixes[t]:
                    d = int(d * 1.2)
                base_sum += d
                if t == "second_blast":
                    second_wave += d * 0.55
                if "delay" in affixes[t]:
                    delayed_wave += d * 0.5
                if "overload" in affixes[t]:
                    overload_types.append(t)

            total_turn_damage = base_sum * chain_mult * overlap_mult * crit_expect * shield_factor * pollution_expect
            total_turn_damage += second_wave + delayed_wave

            # occasional double detonate from combat thresholds approximated by low proc
            if rng.random() < 0.08:
                total_turn_damage += base_sum * c["double_detonate_ratio"] * 0.6

            turn_dmg_i = max(0, int(total_turn_damage))
            boss_hp -= turn_dmg_i
            dmg_total += turn_dmg_i

            # cooldown applies post-detonation
            for t in overload_types:
                cooldowns[t] = max(cooldowns.get(t, 0), 1)
            if challenge == c["challenge_cooldown"] and used:
                top_t = max(used, key=lambda x: calc_damage(bomb_damage[x], affixes[x]))
                cooldowns[top_t] = max(cooldowns.get(top_t, 0), 1)

            # incoming damage pressure this turn (reduced if freeze-like utility present)
            freeze_used = "freeze_bomb" in used
            pressure = 0.14 + 0.02 * max(0, phase - 1)
            if phase == 2 and rng.random() < c["summon_p2"]:
                pressure += 0.03
            if phase == 3 and rng.random() < c["summon_p3"]:
                pressure += 0.05
            if freeze_used:
                pressure *= 0.7
            incoming = max(1, int(boss_attack * pressure))
            hp -= incoming

        # floor end
        clicks_delta_total += (floor_click_gain - floor_click_spend)
        intel_delta_total += (floor_intel_gain - floor_intel_spend)

        if boss_hp <= 0 and hp > 0:
            # discovery bonus (all bombs found can happen before clear); simplified sustain
            hp = min(30, hp + 2)
            # emulate one permanent upgrade pick from random 3
            pool = [
                "bomb_range_up",
                "bomb_dmg_up",
                "unlock_cross",
                "unlock_fan",
                "unlock_x_shot",
                "unlock_second",
                "unlock_freeze",
                "unlock_magnetic",
                "unlock_bounce",
                "unlock_blackhole",
                "unlock_ultimate",
                "chain_boost",
            ]
            choices = rng.sample(pool, k=min(3, len(pool)))
            pick = rng.choice(choices)
            if pick == "bomb_dmg_up":
                for t in bomb_damage:
                    bomb_damage[t] += 1
            elif pick == "chain_boost":
                chain_bonus_base = c["chain_boost_value"]
            elif pick.startswith("unlock_"):
                mapping = {
                    "unlock_cross": "cross",
                    "unlock_fan": "fan",
                    "unlock_x_shot": "x_shot",
                    "unlock_second": "second_blast",
                    "unlock_freeze": "freeze_bomb",
                    "unlock_magnetic": "magnetic",
                    "unlock_bounce": "bounce",
                    "unlock_blackhole": "blackhole",
                    "unlock_ultimate": "ultimate",
                }
                u = mapping.get(pick)
                if u and u not in unlocked:
                    unlocked.append(u)
            floor += 1
        else:
            break

    floors_cleared = max(0, floor - 1)
    avg_turn_damage = (dmg_total / turns_total) if turns_total else 0.0
    avg_click_delta = (clicks_delta_total / turns_total) if turns_total else 0.0
    avg_intel_delta = (intel_delta_total / turns_total) if turns_total else 0.0

    return RunResult(
        run_id=run_id,
        seed=seed,
        floors_cleared=floors_cleared,
        turns=turns_total,
        total_damage=dmg_total,
        avg_turn_damage=avg_turn_damage,
        avg_click_delta_per_turn=avg_click_delta,
        avg_intel_delta_per_turn=avg_intel_delta,
        ending_hp=max(0, hp),
    )


def summarize(results: List[RunResult]) -> Dict[str, float]:
    n = len(results)
    def mean(vals: List[float]) -> float:
        return sum(vals) / n if n else 0.0

    floors = [r.floors_cleared for r in results]
    turns = [r.turns for r in results]
    dmg = [r.avg_turn_damage for r in results]
    click_delta = [r.avg_click_delta_per_turn for r in results]
    intel_delta = [r.avg_intel_delta_per_turn for r in results]

    return {
        "runs": n,
        "avg_floors_cleared": mean(floors),
        "min_floors_cleared": min(floors) if floors else 0,
        "max_floors_cleared": max(floors) if floors else 0,
        "avg_turns": mean(turns),
        "avg_turn_damage": mean(dmg),
        "avg_click_delta_per_turn": mean(click_delta),
        "avg_intel_delta_per_turn": mean(intel_delta),
    }


def main() -> None:
    level_text = read_text(LEVEL_DATA_PATH)
    bomb_text = read_text(BOMB_REG_PATH)

    grid_sizes = parse_boss_grid_size(level_text)
    levels = parse_level_blocks(level_text)
    base_bomb_damage = parse_bomb_damage_map(bomb_text)
    constants = parse_balance_constants()

    results: List[RunResult] = []
    for i in range(10):
        seed = 20260324 + i * 97
        # per-run bomb damage copy (includes run-local permanent upgrades)
        run_bomb_damage = dict(base_bomb_damage)
        r = run_once(i + 1, seed, levels, grid_sizes, run_bomb_damage, constants)
        results.append(r)

    summary = summarize(results)

    out_dir = ROOT / "temp"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "balance_sampling_results.json"
    md_path = out_dir / "balance_sampling_report.md"

    json_payload = {
        "summary": summary,
        "runs": [asdict(r) for r in results],
        "assumptions": {
            "engine_cli": "godot CLI unavailable in current environment; used formula-driven Monte Carlo simulation",
            "difficulty": "mine_difficulty=1.0, boss_hp_mult=1.0",
            "scope": "uses current script constants and helper formulas from LevelData/GameManager/GridManager/BossGrid/ExplosionCalc/BombRegistry",
        },
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# 平衡采样报告（10局）")
    lines.append("")
    lines.append("## 总体")
    lines.append(f"- 局数: {summary['runs']}")
    lines.append(f"- 平均通关层数: {summary['avg_floors_cleared']:.2f}（范围 {summary['min_floors_cleared']} ~ {summary['max_floors_cleared']}）")
    lines.append(f"- 平均总回合数: {summary['avg_turns']:.2f}")
    lines.append(f"- 平均单回合伤害: {summary['avg_turn_damage']:.2f}")
    lines.append(f"- 平均点击盈亏/回合: {summary['avg_click_delta_per_turn']:.3f}")
    lines.append(f"- 平均情报盈亏/回合: {summary['avg_intel_delta_per_turn']:.3f}")
    lines.append("")
    lines.append("## 分局明细")
    for r in results:
        lines.append(
            f"- Run {r.run_id:02d} | seed={r.seed} | floors={r.floors_cleared} | turns={r.turns} | avg_dmg={r.avg_turn_damage:.2f} | click_delta={r.avg_click_delta_per_turn:.3f} | intel_delta={r.avg_intel_delta_per_turn:.3f} | hp={r.ending_hp}"
        )
    lines.append("")
    lines.append("## 说明")
    lines.append("- 本结果为基于当前脚本公式的蒙特卡洛采样，适合做相对比较与版本回归。")
    lines.append("- 若需引擎内逐帧真回放，请在本机安装 Godot CLI 后切换 headless 采样流程。")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()
