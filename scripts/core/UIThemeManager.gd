## UI主题管理器 - AutoLoad
## 三套风格：暗黑地牢 / 赛博朋克 / 像素复古
## 所有UI颜色/样式通过此单例获取，保存到用户数据

extends Node

signal theme_changed(new_theme: String)

enum ThemeStyle { DUNGEON, CYBER, PIXEL }

const THEME_NAMES = {
	ThemeStyle.DUNGEON: "暗黑地牢",
	ThemeStyle.CYBER:   "赛博朋克",
	ThemeStyle.PIXEL:   "像素复古",
}

const SAVE_PATH = "user://ui_theme.cfg"

var current_theme: int = ThemeStyle.DUNGEON

# ── 每套主题的色板 ─────────────────────────────────────────────
#
# 命名约定:
#   bg_primary      主背景/格子基础色
#   bg_secondary    次背景/已翻格
#   bg_empty        放置区空格
#   bg_void         Boss已死格
#   border_default  默认边框
#   border_strong   高亮/选中边框
#   text_primary    主文字（HUD标题/计时器）
#   text_secondary  次级文字（副标题/点击数）
#   text_accent     强调文字（层数/金色高亮）
#   text_danger     危险/警告（受伤/计时警告）
#   text_heal       回血/增益
#   hud_bg          HUD背景条颜色
#   boss_bar_bg     Boss血条背景
#   boss_bar_fill   Boss血条填充
#   boss_hp_text    Boss血量文字
#   btn_normal_bg   按钮普通背景
#   btn_normal_brd  按钮普通边框
#   btn_hover_bg    按钮悬停背景
#   btn_hover_brd   按钮悬停边框
#   btn_end_text    结束按钮文字
#   explode_bg      爆炸格背景
#   explode_brd     爆炸格边框
#   mine_hidden     扫雷隐藏格
#   mine_hidden_brd 扫雷隐藏边框
#   mine_reveal     扫雷翻开格
#   mine_reveal_brd 扫雷翻开边框
#   boss_weak_brd   Boss弱点边框
#   boss_armor_brd  Boss护甲边框
#   boss_absorb_brd Boss吸收边框
#   intro_overlay   关卡介绍背景遮罩
#   whisper_text    古语低语颜色
#   section_label   区域标签
#   dmg_lo / dmg_mid / dmg_hi  三档伤害数字

const PALETTES = {
	ThemeStyle.DUNGEON: {
		"bg_empty":        Color(0.18, 0.17, 0.20),
		"bg_secondary":    Color(0.25, 0.26, 0.30),
		"bg_void":         Color(0.06, 0.06, 0.07),
		"border_default":  Color(0.28, 0.26, 0.24),
		"border_strong":   Color(0.55, 0.45, 0.25),
		"text_primary":    Color(0.92, 0.90, 0.82),
		"text_secondary":  Color(0.72, 0.68, 0.58),
		"text_accent":     Color(0.95, 0.82, 0.45),
		"text_danger":     Color(1.0, 0.25, 0.15),
		"text_heal":       Color(0.35, 0.95, 0.45),
		"hud_bg":          Color(0.10, 0.09, 0.08, 0.92),
		"boss_bar_bg":     Color(0.10, 0.08, 0.06),
		"boss_bar_fill":   Color(0.72, 0.15, 0.10),
		"boss_bar_brd":    Color(0.40, 0.32, 0.22),
		"boss_hp_text":    Color(0.90, 0.85, 0.75),
		"player_hp_text":  Color(0.35, 0.85, 0.35),
		"btn_normal_bg":   Color(0.14, 0.13, 0.11),
		"btn_normal_brd":  Color(0.32, 0.28, 0.22),
		"btn_hover_bg":    Color(0.22, 0.19, 0.15),
		"btn_end_bg":      Color(0.18, 0.15, 0.12),
		"btn_end_brd":     Color(0.55, 0.45, 0.25),
		"btn_end_hover":   Color(0.25, 0.20, 0.15),
		"btn_end_hbrd":    Color(0.70, 0.58, 0.30),
		"btn_end_text":    Color(0.95, 0.85, 0.45),
		"explode_bg":      Color(0.90, 0.35, 0.05),
		"explode_brd":     Color(1.0, 0.65, 0.0),
		"mine_hidden":     Color(0.25, 0.26, 0.30),
		"mine_hidden_brd": Color(0.33, 0.35, 0.40),
		"mine_reveal":     Color(0.58, 0.54, 0.44),
		"mine_reveal_brd": Color(0.48, 0.44, 0.36),
		"boss_weak_brd":   Color(0.95, 0.80, 0.15),
		"boss_armor_brd":  Color(0.45, 0.55, 0.85),
		"boss_absorb_brd": Color(0.20, 0.75, 0.35),
		"intro_overlay":   Color(0.02, 0.01, 0.0, 0.85),
		"whisper_text":    Color(0.45, 0.38, 0.58, 0.7),
		"floor_text":      Color(0.65, 0.6, 0.5),
		"boss_label":      Color(0.85, 0.35, 0.25),
		"section_label":   Color(0.55, 0.50, 0.40, 0.8),
		"dmg_lo":          Color(1.0, 0.85, 0.2),
		"dmg_mid":         Color(1.0, 0.45, 0.1),
		"dmg_hi":          Color(1.0, 0.15, 0.05),
		"chain_flash":     Color(0.5, 0.8, 2.5),
		"boss_pulse":      Color(1.3, 1.1, 1.0),
		"corner_radius":   4,
		"border_width":    2,
	},
	ThemeStyle.CYBER: {
		"bg_empty":        Color(0.04, 0.06, 0.12),
		"bg_secondary":    Color(0.06, 0.04, 0.14),
		"bg_void":         Color(0.02, 0.02, 0.05),
		"border_default":  Color(0.15, 0.20, 0.35),
		"border_strong":   Color(0.0, 0.85, 0.95),
		"text_primary":    Color(0.85, 0.95, 1.0),
		"text_secondary":  Color(0.45, 0.75, 0.90),
		"text_accent":     Color(0.0, 0.95, 0.85),
		"text_danger":     Color(1.0, 0.15, 0.45),
		"text_heal":       Color(0.15, 0.95, 0.55),
		"hud_bg":          Color(0.04, 0.05, 0.12, 0.95),
		"boss_bar_bg":     Color(0.04, 0.04, 0.10),
		"boss_bar_fill":   Color(0.9, 0.05, 0.4),
		"boss_bar_brd":    Color(0.0, 0.85, 0.95),
		"boss_hp_text":    Color(0.75, 0.90, 1.0),
		"player_hp_text":  Color(0.15, 0.95, 0.65),
		"btn_normal_bg":   Color(0.05, 0.06, 0.14),
		"btn_normal_brd":  Color(0.10, 0.35, 0.55),
		"btn_hover_bg":    Color(0.08, 0.12, 0.22),
		"btn_end_bg":      Color(0.06, 0.08, 0.18),
		"btn_end_brd":     Color(0.0, 0.80, 0.90),
		"btn_end_hover":   Color(0.10, 0.15, 0.28),
		"btn_end_hbrd":    Color(0.3, 1.0, 1.0),
		"btn_end_text":    Color(0.0, 0.95, 0.90),
		"explode_bg":      Color(0.9, 0.05, 0.5),
		"explode_brd":     Color(1.0, 0.3, 0.8),
		"mine_hidden":     Color(0.05, 0.07, 0.16),
		"mine_hidden_brd": Color(0.12, 0.22, 0.40),
		"mine_reveal":     Color(0.08, 0.14, 0.25),
		"mine_reveal_brd": Color(0.0, 0.65, 0.80),
		"boss_weak_brd":   Color(0.0, 0.95, 0.85),
		"boss_armor_brd":  Color(0.3, 0.4, 1.0),
		"boss_absorb_brd": Color(0.9, 0.05, 0.5),
		"intro_overlay":   Color(0.0, 0.02, 0.08, 0.88),
		"whisper_text":    Color(0.3, 0.65, 0.95, 0.7),
		"floor_text":      Color(0.45, 0.85, 1.0),
		"boss_label":      Color(1.0, 0.15, 0.5),
		"section_label":   Color(0.0, 0.75, 0.85, 0.8),
		"dmg_lo":          Color(0.0, 0.95, 0.85),
		"dmg_mid":         Color(0.9, 0.05, 0.5),
		"dmg_hi":          Color(1.0, 0.3, 0.8),
		"chain_flash":     Color(0.3, 1.0, 2.5),
		"boss_pulse":      Color(1.0, 1.3, 1.5),
		"corner_radius":   1,
		"border_width":    2,
	},
	ThemeStyle.PIXEL: {
		"bg_empty":        Color(0.12, 0.14, 0.10),
		"bg_secondary":    Color(0.22, 0.24, 0.18),
		"bg_void":         Color(0.05, 0.06, 0.04),
		"border_default":  Color(0.30, 0.30, 0.22),
		"border_strong":   Color(0.85, 0.75, 0.10),
		"text_primary":    Color(0.88, 0.92, 0.70),
		"text_secondary":  Color(0.65, 0.68, 0.48),
		"text_accent":     Color(0.95, 0.88, 0.25),
		"text_danger":     Color(0.95, 0.18, 0.10),
		"text_heal":       Color(0.30, 0.90, 0.30),
		"hud_bg":          Color(0.10, 0.11, 0.08, 0.95),
		"boss_bar_bg":     Color(0.08, 0.08, 0.06),
		"boss_bar_fill":   Color(0.75, 0.20, 0.05),
		"boss_bar_brd":    Color(0.50, 0.45, 0.20),
		"boss_hp_text":    Color(0.88, 0.85, 0.65),
		"player_hp_text":  Color(0.30, 0.85, 0.25),
		"btn_normal_bg":   Color(0.14, 0.15, 0.10),
		"btn_normal_brd":  Color(0.38, 0.35, 0.22),
		"btn_hover_bg":    Color(0.22, 0.24, 0.16),
		"btn_end_bg":      Color(0.16, 0.17, 0.11),
		"btn_end_brd":     Color(0.70, 0.60, 0.15),
		"btn_end_hover":   Color(0.24, 0.26, 0.16),
		"btn_end_hbrd":    Color(0.92, 0.80, 0.25),
		"btn_end_text":    Color(0.95, 0.88, 0.35),
		"explode_bg":      Color(0.95, 0.50, 0.05),
		"explode_brd":     Color(1.0, 0.80, 0.0),
		"mine_hidden":     Color(0.18, 0.20, 0.14),
		"mine_hidden_brd": Color(0.32, 0.34, 0.24),
		"mine_reveal":     Color(0.48, 0.50, 0.34),
		"mine_reveal_brd": Color(0.38, 0.40, 0.28),
		"boss_weak_brd":   Color(0.95, 0.85, 0.10),
		"boss_armor_brd":  Color(0.40, 0.55, 0.30),
		"boss_absorb_brd": Color(0.25, 0.70, 0.30),
		"intro_overlay":   Color(0.04, 0.04, 0.02, 0.88),
		"whisper_text":    Color(0.50, 0.55, 0.35, 0.7),
		"floor_text":      Color(0.75, 0.72, 0.48),
		"boss_label":      Color(0.95, 0.30, 0.15),
		"section_label":   Color(0.60, 0.58, 0.38, 0.8),
		"dmg_lo":          Color(0.95, 0.88, 0.20),
		"dmg_mid":         Color(0.95, 0.55, 0.10),
		"dmg_hi":          Color(0.95, 0.20, 0.05),
		"chain_flash":     Color(0.6, 0.9, 2.0),
		"boss_pulse":      Color(1.2, 1.15, 1.0),
		"corner_radius":   0,
		"border_width":    3,
	},
}

# ── 数字颜色（扫雷1-8）也按主题分套 ───────────────────────────

const NUMBER_COLORS_BY_THEME = {
	ThemeStyle.DUNGEON: [
		Color(0,0,0), Color(0.15,0.35,0.80), Color(0.12,0.55,0.22),
		Color(0.80,0.15,0.12), Color(0.22,0.15,0.62), Color(0.62,0.12,0.12),
		Color(0.12,0.50,0.55), Color(0.88,0.72,0.18), Color(0.55,0.38,0.18),
	],
	ThemeStyle.CYBER: [
		Color(0,0,0), Color(0.0,0.85,0.95), Color(0.0,0.95,0.5),
		Color(0.95,0.05,0.45), Color(0.6,0.2,1.0), Color(0.95,0.3,0.65),
		Color(0.0,0.7,0.9), Color(0.95,0.85,0.0), Color(0.8,0.5,0.0),
	],
	ThemeStyle.PIXEL: [
		Color(0,0,0), Color(0.25,0.50,0.95), Color(0.18,0.72,0.25),
		Color(0.92,0.18,0.10), Color(0.55,0.18,0.85), Color(0.80,0.14,0.14),
		Color(0.15,0.65,0.70), Color(0.95,0.78,0.10), Color(0.65,0.40,0.14),
	],
}

# ── API ───────────────────────────────────────────────────────

func _ready():
	_load()

func color(key: String) -> Variant:
	return PALETTES[current_theme][key]

func get_number_color(n: int) -> Color:
	var arr = NUMBER_COLORS_BY_THEME[current_theme]
	return arr[n] if n < arr.size() else Color(0.1, 0.1, 0.1)

func set_theme(t: int):
	current_theme = t
	_save()
	theme_changed.emit(THEME_NAMES[t])

func theme_name() -> String:
	return THEME_NAMES[current_theme]

func make_stylebox(key_bg: String, key_brd: String, border_w: int = -1, corner_r: int = -1) -> StyleBoxFlat:
	var s = StyleBoxFlat.new()
	s.bg_color = color(key_bg)
	s.border_color = color(key_brd)
	var bw = border_w if border_w >= 0 else color("border_width")
	var cr = corner_r if corner_r >= 0 else color("corner_radius")
	s.set_border_width_all(bw)
	s.set_corner_radius_all(cr)
	return s

# ── 持久化 ────────────────────────────────────────────────────

func _save():
	var cfg = ConfigFile.new()
	cfg.set_value("ui", "theme", current_theme)
	cfg.save(SAVE_PATH)

func _load():
	var cfg = ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		current_theme = cfg.get_value("ui", "theme", ThemeStyle.DUNGEON)
