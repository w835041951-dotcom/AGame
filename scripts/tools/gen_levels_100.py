"""
生成100关LevelData.gd (10区域×10Boss)
输出: scripts/core/LevelData.gd

用法: python scripts/tools/gen_levels_100.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gen_all_art import ZONES, ZONE_BOSSES, ZONE_COLORS, BG_SCENES

# 区域中文子地点名
ZONE_SUBNAMES = {
    "BAMBOO": ["入口", "竹径", "石桥", "溪谷", "古祠", "密林", "瀑布", "山腰", "云端", "竹顶"],
    "GEAR":   ["大门", "齿轮厅", "蒸汽廊", "熔炉", "管道", "钟楼", "铸造间", "指挥室", "通风井", "核心"],
    "OCEAN":  ["浅滩", "珊瑚礁", "暗流", "沉船", "深沟", "洞穴", "水母群", "黑域", "神殿", "深渊"],
    "LAVA":   ["火口", "岩桥", "熔岩河", "硫磺洞", "黑曜石", "火焰柱", "灰烬路", "炼狱", "地核", "火神殿"],
    "MOON":   ["月门", "星阶", "银池", "云台", "月桂园", "仙阁", "水镜", "光廊", "月坛", "月宫"],
    "ICE":    ["冰原", "雪谷", "冰洞", "霜桥", "极光", "冻湖", "冰塔", "暴风", "冰窟", "冰王座"],
    "TOXIC":  ["沼泽边", "毒雾", "枯林", "酸池", "孢子园", "蘑菇洞", "瘴气路", "淤泥坑", "毒泉", "瘟疫殿"],
    "GHOST":  ["城门", "幽巷", "灯笼街", "枯井", "茶馆", "戏楼", "坟场", "钟声", "鬼王路", "地府"],
    "CHAOS":  ["裂口", "碎空", "扭曲路", "镜之廊", "逆时钟", "虚像", "混沌海", "断层", "终焉", "混沌核心"],
    "VOID":   ["虚空门", "暗星", "星尘", "黑洞边", "时空裂", "银河", "湮灭", "奇点", "终极", "虚空神座"],
}

# 区域副标题模板
ZONE_SUBTITLES = {
    "BAMBOO": "竹影婆娑间隐约传来低吟…",
    "GEAR":   "齿轮咬合的轰鸣声震耳欲聋…",
    "OCEAN":  "深海中回荡着未知生物的呼唤…",
    "LAVA":   "空气灼热得几乎无法呼吸…",
    "MOON":   "银色月光下一切如梦如幻…",
    "ICE":    "寒风刺骨,冰晶在空中闪烁…",
    "TOXIC":  "毒雾弥漫,每一步都暗藏危机…",
    "GHOST":  "鬼火飘摇,亡灵在暗处窥视…",
    "CHAOS":  "现实在此扭曲崩塌…",
    "VOID":   "虚空中只有无尽的沉默…",
}


def generate():
    lines = []
    lines.append('## 关卡数据 - AutoLoad')
    lines.append('## 100个主题关卡 (10区域 × 10Boss)')
    lines.append('## 每种Boss独立形状、配色、棋盘大小、探索区参数')
    lines.append('')
    lines.append('extends Node')
    lines.append('')

    # BOSS_GRID_SIZE
    lines.append('const BOSS_GRID_SIZE = {')
    for zone in ZONES:
        zid = zone["id"]
        for suffix, cn, desc, gw, gh in ZONE_BOSSES[zid]:
            key = f"{zid}_{suffix}"
            lines.append(f'\t"{key}": Vector2i({gw}, {gh}),')
    lines.append('}')
    lines.append('')

    # LEVELS array
    lines.append('const LEVELS = [')
    floor_num = 0
    for zi, zone in enumerate(ZONES):
        zid = zone["id"]
        zname = zone["name"]
        color = ZONE_COLORS[zid]
        subtitle = ZONE_SUBTITLES[zid]
        sub_names = ZONE_SUBNAMES[zid]
        bosses = ZONE_BOSSES[zid]

        for bi, (suffix, cn_name, desc, gw, gh) in enumerate(bosses):
            floor_num += 1
            key = f"{zid}_{suffix}"
            level_name = f"{zname}·{sub_names[bi]}"

            # 难度渐进
            progress = floor_num / 100.0  # 0.01 ~ 1.0
            # tile weights: 弱点减少, 护甲/吸收增加
            weak = max(0.10, 0.40 - progress * 0.30)
            armor = min(0.25, 0.03 + progress * 0.22)
            absorb = min(0.15, 0.01 + progress * 0.14)
            normal = round(1.0 - weak - armor - absorb, 2)

            bomb_count = 5 + int(progress * 6)           # 5→11
            base_clicks = 7 + int(progress * 5)           # 7→12
            turn_dur = round(50.0 - progress * 25.0, 1)   # 50→25
            boss_atk = 3 + int(progress * 12)              # 3→15
            move_int = round(70.0 - progress * 45.0, 1)    # 70→25
            p_cols = 9 + int(progress * 3)                 # 9→12
            p_rows = 6 + int(progress * 2)                 # 6→8
            m_cols = 9 + int(progress * 3)                 # 9→12
            m_rows = 5 + int(progress * 3)                 # 5→8

            lines.append('\t{')
            lines.append(f'\t\t"id": {floor_num}, "name": "{level_name}",')
            lines.append(f'\t\t"boss_name": "{cn_name}", "boss_shape": "{key}",')
            lines.append(f'\t\t"subtitle": "{subtitle}",')
            lines.append(f'\t\t"color": Color({color[0]:.2f},{color[1]:.2f},{color[2]:.2f}),')
            lines.append(f'\t\t"tile_weights": {{ "WEAK": {weak:.2f}, "ARMOR": {armor:.2f}, "ABSORB": {absorb:.2f}, "NORMAL": {normal:.2f} }},')
            lines.append(f'\t\t"bomb_count": {bomb_count}, "base_clicks": {base_clicks},')
            lines.append(f'\t\t"turn_duration": {turn_dur}, "boss_attack": {boss_atk}, "boss_move_interval": {move_int},')
            lines.append(f'\t\t"placement_cols": {p_cols}, "placement_rows": {p_rows},')
            lines.append(f'\t\t"mine_cols": {m_cols}, "mine_rows": {m_rows},')
            lines.append('\t},')
    lines.append(']')
    lines.append('')

    # BOSS_TEXTURE_MAP
    lines.append('const BOSS_TEXTURE_MAP = {')
    for zone in ZONES:
        zid = zone["id"]
        for suffix, cn, desc, gw, gh in ZONE_BOSSES[zid]:
            key = f"{zid}_{suffix}"
            lines.append(f'\t"{key}": "res://assets/sprites/boss/boss_{key.lower()}.png",')
    lines.append('}')
    lines.append('')

    # 查询接口
    lines.append('# ============================================================')
    lines.append('#  查询接口  —  100关唯一对应')
    lines.append('# ============================================================')
    lines.append('')
    lines.append('func get_level(floor_number: int) -> Dictionary:')
    lines.append('\tvar idx = (floor_number - 1) % LEVELS.size()')
    lines.append('\treturn LEVELS[idx]')
    lines.append('')
    lines.append('func get_cycle(floor_number: int) -> int:')
    lines.append('\treturn (floor_number - 1) / LEVELS.size()')
    lines.append('')
    lines.append('func get_level_name(floor_number: int) -> String:')
    lines.append('\treturn get_level(floor_number)["name"]')
    lines.append('')
    lines.append('func get_boss_name(floor_number: int) -> String:')
    lines.append('\treturn get_level(floor_number)["boss_name"]')
    lines.append('')
    lines.append('func get_level_subtitle(floor_number: int) -> String:')
    lines.append('\treturn get_level(floor_number)["subtitle"]')
    lines.append('')
    lines.append('func get_level_color(floor_number: int) -> Color:')
    lines.append('\treturn get_level(floor_number)["color"]')
    lines.append('')
    lines.append('# -- 棋盘大小 --')
    lines.append('')
    lines.append('func get_placement_cols(floor_number: int) -> int:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\treturn level["placement_cols"] + cycle')
    lines.append('')
    lines.append('func get_placement_rows(floor_number: int) -> int:')
    lines.append('\treturn get_level(floor_number)["placement_rows"]')
    lines.append('')
    lines.append('func get_mine_cols(floor_number: int) -> int:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\tvar base = level["mine_cols"] + cycle')
    lines.append('\tvar extra = roundi((GameSettings.mine_difficulty - 1.0) * 3.0)')
    lines.append('\treturn maxi(base + extra, 6)')
    lines.append('')
    lines.append('func get_mine_rows(floor_number: int) -> int:')
    lines.append('\tvar base = get_level(floor_number)["mine_rows"]')
    lines.append('\tvar extra = roundi((GameSettings.mine_difficulty - 1.0) * 1.5)')
    lines.append('\treturn maxi(base + extra, 3)')
    lines.append('')
    lines.append('func get_boss_shape(floor_number: int) -> Array:')
    lines.append('\tvar key = get_level(floor_number)["boss_shape"]')
    lines.append('\tvar sz = BOSS_GRID_SIZE[key]')
    lines.append('\tvar arr = []')
    lines.append('\tfor y in range(sz.y):')
    lines.append('\t\tfor x in range(sz.x):')
    lines.append('\t\t\tarr.append(Vector2i(x, y))')
    lines.append('\treturn arr')
    lines.append('')
    lines.append('func get_boss_grid_size(floor_number: int) -> Vector2i:')
    lines.append('\tvar key = get_level(floor_number)["boss_shape"]')
    lines.append('\treturn BOSS_GRID_SIZE[key]')
    lines.append('')
    lines.append('func get_boss_texture_path(floor_number: int) -> String:')
    lines.append('\tvar key = get_level(floor_number)["boss_shape"]')
    lines.append('\treturn BOSS_TEXTURE_MAP[key]')
    lines.append('')

    # BACKGROUND_PATHS - 10 backgrounds (1 per zone)
    bg_keys = list(BG_SCENES.keys())
    lines.append('const BACKGROUND_PATHS: Array = [')
    for k in bg_keys:
        lines.append(f'\t"res://assets/sprites/bg/{k}.png",')
    lines.append(']')
    lines.append('')
    lines.append('func get_background_texture_path(floor_number: int) -> String:')
    lines.append('\tvar idx = ((floor_number - 1) / 10) % BACKGROUND_PATHS.size()')
    lines.append('\treturn BACKGROUND_PATHS[idx]')
    lines.append('')
    lines.append('func get_cell_size(floor_number: int) -> int:')
    lines.append('\tvar p_cols = get_placement_cols(floor_number)')
    lines.append('\tvar p_rows = get_placement_rows(floor_number)')
    lines.append('\tvar m_cols = get_mine_cols(floor_number)')
    lines.append('\tvar m_rows = get_mine_rows(floor_number)')
    lines.append('\tvar max_cols = max(p_cols, m_cols)')
    lines.append('\tvar size_by_w = int(1760.0 / max_cols)')
    lines.append('\tvar size_by_h = int(880.0 / (p_rows + m_rows))')
    lines.append('\treturn min(size_by_w, size_by_h)')
    lines.append('')
    lines.append('# -- 难度参数（含周期递增）--')
    lines.append('')
    lines.append('func get_bomb_count(floor_number: int) -> int:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\tvar base = level["bomb_count"] + cycle * 2')
    lines.append('\tvar d = GameSettings.mine_difficulty')
    lines.append('\tif is_equal_approx(d, 1.0):')
    lines.append('\t\treturn base')
    lines.append('\tvar cols = get_mine_cols(floor_number)')
    lines.append('\tvar rows = get_mine_rows(floor_number)')
    lines.append('\tvar base_cols = level["mine_cols"] + cycle')
    lines.append('\tvar base_rows = level["mine_rows"]')
    lines.append('\tvar base_density = float(base) / float(base_cols * base_rows)')
    lines.append('\tvar density_mult = 0.7 + 0.3 * d')
    lines.append('\treturn maxi(roundi(cols * rows * base_density * density_mult), 2)')
    lines.append('')
    lines.append('func get_turn_duration(floor_number: int) -> float:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\treturn maxf(level["turn_duration"] - cycle * 3.0, 15.0)')
    lines.append('')
    lines.append('func get_boss_attack(floor_number: int) -> int:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\treturn level["boss_attack"] + cycle * 3')
    lines.append('')
    lines.append('func get_boss_move_interval(floor_number: int) -> float:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\treturn maxf(level["boss_move_interval"] - cycle * 5.0, 18.0)')
    lines.append('')
    lines.append('func get_tile_weights(floor_number: int) -> Dictionary:')
    lines.append('\treturn get_level(floor_number)["tile_weights"]')
    lines.append('')
    lines.append('func get_hp_multiplier(floor_number: int) -> float:')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\tvar base = 1.0 + cycle * 0.5')
    lines.append('\treturn base * GameSettings.boss_hp_mult')
    lines.append('')
    lines.append('func get_max_clicks(floor_number: int) -> int:')
    lines.append('\tvar level = get_level(floor_number)')
    lines.append('\tvar cycle = get_cycle(floor_number)')
    lines.append('\treturn level["base_clicks"] + cycle * 3')
    lines.append('')

    return '\n'.join(lines) + '\n'


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "..", "core", "LevelData.gd")
    content = generate()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已生成 LevelData.gd: 100关, {os.path.getsize(out_path)} bytes")
