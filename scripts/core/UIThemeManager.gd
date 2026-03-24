## UI主题管理器 - AutoLoad
## 三套风格：樱花幻境 / 蒸汽朋克 / 霓虹都市
## 所有UI颜色/样式通过此单例获取，保存到用户数据

extends Node

signal theme_changed(new_theme: String)

enum ThemeStyle { SAKURA, STEAM, NEON }

const THEME_NAMES = {
	ThemeStyle.SAKURA: "樱花幻境",
	ThemeStyle.STEAM:   "蒸汽朋克",
	ThemeStyle.NEON:    "霓虹都市",
}

const SAVE_PATH = "user://ui_theme.cfg"

var current_theme: int = ThemeStyle.SAKURA

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
	ThemeStyle.SAKURA: {
		"bg_empty":        Color(0.09, 0.06, 0.12),
		"bg_secondary":    Color(0.16, 0.11, 0.20),
		"bg_void":         Color(0.03, 0.02, 0.04),
		"border_default":  Color(0.50, 0.30, 0.45),
		"border_strong":   Color(1.0, 0.60, 0.78),
		"text_primary":    Color(1.0, 0.94, 0.96),
		"text_secondary":  Color(0.85, 0.70, 0.80),
		"text_accent":     Color(1.0, 0.70, 0.85),
		"text_danger":     Color(1.0, 0.30, 0.35),
		"text_heal":       Color(0.40, 1.0, 0.65),
		"hud_bg":          Color(0.06, 0.04, 0.08, 0.96),
		"boss_bar_bg":     Color(0.08, 0.05, 0.10),
		"boss_bar_fill":   Color(0.95, 0.30, 0.50),
		"boss_bar_brd":    Color(1.0, 0.60, 0.78),
		"boss_hp_text":    Color(1.0, 0.92, 0.95),
		"player_hp_text":  Color(0.40, 1.0, 0.60),
		"btn_normal_bg":   Color(0.12, 0.08, 0.15),
		"btn_normal_brd":  Color(0.50, 0.30, 0.45),
		"btn_hover_bg":    Color(0.22, 0.15, 0.28),
		"btn_end_bg":      Color(0.18, 0.10, 0.22),
		"btn_end_brd":     Color(1.0, 0.60, 0.78),
		"btn_end_hover":   Color(0.28, 0.18, 0.35),
		"btn_end_hbrd":    Color(1.0, 0.75, 0.88),
		"btn_end_text":    Color(1.0, 0.80, 0.90),
		"explode_bg":      Color(1.0, 0.50, 0.65),
		"explode_brd":     Color(1.0, 0.75, 0.85),
		"mine_hidden":     Color(0.30, 0.20, 0.38),
		"mine_hidden_brd": Color(0.55, 0.35, 0.60),
		"mine_reveal":     Color(0.06, 0.04, 0.08),
		"mine_reveal_brd": Color(0.12, 0.08, 0.14),
		"boss_weak_brd":   Color(1.0, 0.85, 0.40),
		"boss_armor_brd":  Color(0.50, 0.55, 1.0),
		"boss_absorb_brd": Color(0.40, 0.90, 0.60),
		"intro_overlay":   Color(0.02, 0.01, 0.03, 0.85),
		"whisper_text":    Color(0.70, 0.45, 0.65, 0.75),
		"floor_text":      Color(0.95, 0.70, 0.82),
		"boss_label":      Color(1.0, 0.40, 0.55),
		"section_label":   Color(0.75, 0.55, 0.68, 0.85),
		"dmg_lo":          Color(1.0, 0.80, 0.85),
		"dmg_mid":         Color(1.0, 0.50, 0.60),
		"dmg_hi":          Color(1.0, 0.20, 0.30),
		"chain_flash":     Color(1.0, 0.6, 2.0),
		"boss_pulse":      Color(1.2, 1.0, 1.1),
		"blocked_bg":      Color(0.30, 0.06, 0.10),
		"boss_dead_tint":  Color(0.25, 0.20, 0.28, 0.45),
		"hp_bar_bg":       Color(0.04, 0.03, 0.05, 0.90),
		"hp_bar_mid":      Color(1.0, 0.70, 0.80),
		"preview_highlight": Color(1.2, 0.8, 1.0, 0.75),
		"shadow_color":    Color(0.05, 0, 0.05, 0.65),
		"card_shadow":     Color(0.05, 0, 0.05, 0.55),
		"rarity_common":   Color(0.75, 0.65, 0.72),
		"rarity_common_bg": Color(0.12, 0.08, 0.14),
		"rarity_rare":     Color(0.60, 0.40, 1.0),
		"rarity_rare_bg":  Color(0.10, 0.06, 0.22),
		"rarity_epic":     Color(1.0, 0.40, 0.70),
		"rarity_epic_bg":  Color(0.20, 0.06, 0.15),
		"card_name_text":  Color(1.0, 0.95, 0.97),
		"card_desc_text":  Color(0.85, 0.70, 0.80),
		"corner_radius":   8,
		"border_width":    2,
	},
	ThemeStyle.STEAM: {
		"bg_empty":        Color(0.12, 0.09, 0.06),
		"bg_secondary":    Color(0.20, 0.15, 0.10),
		"bg_void":         Color(0.04, 0.03, 0.02),
		"border_default":  Color(0.45, 0.35, 0.18),
		"border_strong":   Color(0.90, 0.70, 0.25),
		"text_primary":    Color(0.96, 0.92, 0.82),
		"text_secondary":  Color(0.78, 0.68, 0.50),
		"text_accent":     Color(1.0, 0.80, 0.28),
		"text_danger":     Color(0.95, 0.30, 0.15),
		"text_heal":       Color(0.30, 0.90, 0.45),
		"hud_bg":          Color(0.07, 0.05, 0.03, 0.96),
		"boss_bar_bg":     Color(0.10, 0.07, 0.04),
		"boss_bar_fill":   Color(0.85, 0.35, 0.10),
		"boss_bar_brd":    Color(0.80, 0.60, 0.22),
		"boss_hp_text":    Color(0.96, 0.88, 0.72),
		"player_hp_text":  Color(0.35, 0.90, 0.40),
		"btn_normal_bg":   Color(0.14, 0.10, 0.06),
		"btn_normal_brd":  Color(0.45, 0.35, 0.18),
		"btn_hover_bg":    Color(0.25, 0.18, 0.10),
		"btn_end_bg":      Color(0.20, 0.14, 0.06),
		"btn_end_brd":     Color(0.90, 0.70, 0.25),
		"btn_end_hover":   Color(0.30, 0.22, 0.10),
		"btn_end_hbrd":    Color(1.0, 0.82, 0.35),
		"btn_end_text":    Color(1.0, 0.85, 0.40),
		"explode_bg":      Color(1.0, 0.55, 0.15),
		"explode_brd":     Color(1.0, 0.78, 0.25),
		"mine_hidden":     Color(0.32, 0.25, 0.14),
		"mine_hidden_brd": Color(0.55, 0.42, 0.22),
		"mine_reveal":     Color(0.06, 0.05, 0.03),
		"mine_reveal_brd": Color(0.14, 0.11, 0.06),
		"boss_weak_brd":   Color(1.0, 0.88, 0.25),
		"boss_armor_brd":  Color(0.45, 0.55, 0.90),
		"boss_absorb_brd": Color(0.30, 0.85, 0.40),
		"intro_overlay":   Color(0.02, 0.01, 0.01, 0.85),
		"whisper_text":    Color(0.60, 0.48, 0.30, 0.75),
		"floor_text":      Color(0.90, 0.72, 0.40),
		"boss_label":      Color(0.95, 0.45, 0.15),
		"section_label":   Color(0.70, 0.55, 0.32, 0.85),
		"dmg_lo":          Color(1.0, 0.88, 0.30),
		"dmg_mid":         Color(1.0, 0.55, 0.15),
		"dmg_hi":          Color(1.0, 0.22, 0.08),
		"chain_flash":     Color(0.8, 0.9, 2.0),
		"boss_pulse":      Color(1.3, 1.15, 1.0),
		"blocked_bg":      Color(0.30, 0.08, 0.04),
		"boss_dead_tint":  Color(0.30, 0.25, 0.20, 0.45),
		"hp_bar_bg":       Color(0.05, 0.04, 0.02, 0.90),
		"hp_bar_mid":      Color(1.0, 0.80, 0.20),
		"preview_highlight": Color(1.2, 1.0, 0.6, 0.75),
		"shadow_color":    Color(0, 0, 0, 0.60),
		"card_shadow":     Color(0, 0, 0, 0.50),
		"rarity_common":   Color(0.72, 0.65, 0.50),
		"rarity_common_bg": Color(0.12, 0.10, 0.06),
		"rarity_rare":     Color(0.35, 0.60, 0.95),
		"rarity_rare_bg":  Color(0.08, 0.10, 0.22),
		"rarity_epic":     Color(0.90, 0.40, 0.20),
		"rarity_epic_bg":  Color(0.20, 0.08, 0.04),
		"card_name_text":  Color(0.96, 0.92, 0.82),
		"card_desc_text":  Color(0.78, 0.68, 0.50),
		"corner_radius":   4,
		"border_width":    2,
	},
	ThemeStyle.NEON: {
		"bg_empty":        Color(0.04, 0.03, 0.10),
		"bg_secondary":    Color(0.08, 0.05, 0.18),
		"bg_void":         Color(0.02, 0.01, 0.05),
		"border_default":  Color(0.20, 0.10, 0.40),
		"border_strong":   Color(1.0, 0.20, 0.80),
		"text_primary":    Color(0.95, 0.90, 1.0),
		"text_secondary":  Color(0.70, 0.55, 0.90),
		"text_accent":     Color(1.0, 0.25, 0.85),
		"text_danger":     Color(1.0, 0.20, 0.40),
		"text_heal":       Color(0.0, 1.0, 0.65),
		"hud_bg":          Color(0.03, 0.02, 0.08, 0.96),
		"boss_bar_bg":     Color(0.04, 0.02, 0.10),
		"boss_bar_fill":   Color(1.0, 0.15, 0.65),
		"boss_bar_brd":    Color(0.0, 0.90, 1.0),
		"boss_hp_text":    Color(0.90, 0.85, 1.0),
		"player_hp_text":  Color(0.0, 1.0, 0.70),
		"btn_normal_bg":   Color(0.06, 0.04, 0.14),
		"btn_normal_brd":  Color(0.25, 0.12, 0.50),
		"btn_hover_bg":    Color(0.12, 0.08, 0.28),
		"btn_end_bg":      Color(0.08, 0.04, 0.18),
		"btn_end_brd":     Color(1.0, 0.20, 0.80),
		"btn_end_hover":   Color(0.14, 0.08, 0.32),
		"btn_end_hbrd":    Color(0.0, 1.0, 1.0),
		"btn_end_text":    Color(0.0, 1.0, 0.90),
		"explode_bg":      Color(1.0, 0.15, 0.60),
		"explode_brd":     Color(0.0, 1.0, 1.0),
		"mine_hidden":     Color(0.16, 0.10, 0.35),
		"mine_hidden_brd": Color(0.35, 0.20, 0.65),
		"mine_reveal":     Color(0.03, 0.02, 0.06),
		"mine_reveal_brd": Color(0.08, 0.04, 0.12),
		"boss_weak_brd":   Color(0.0, 1.0, 0.85),
		"boss_armor_brd":  Color(0.40, 0.30, 1.0),
		"boss_absorb_brd": Color(1.0, 0.15, 0.60),
		"intro_overlay":   Color(0.02, 0.01, 0.06, 0.88),
		"whisper_text":    Color(0.50, 0.30, 0.90, 0.75),
		"floor_text":      Color(0.70, 0.40, 1.0),
		"boss_label":      Color(1.0, 0.20, 0.65),
		"section_label":   Color(0.0, 0.85, 0.95, 0.85),
		"dmg_lo":          Color(0.0, 1.0, 0.85),
		"dmg_mid":         Color(1.0, 0.20, 0.65),
		"dmg_hi":          Color(1.0, 0.40, 0.90),
		"chain_flash":     Color(0.5, 1.0, 2.5),
		"boss_pulse":      Color(1.2, 1.0, 1.4),
		"blocked_bg":      Color(0.20, 0.04, 0.12),
		"boss_dead_tint":  Color(0.15, 0.10, 0.25, 0.45),
		"hp_bar_bg":       Color(0.03, 0.02, 0.06, 0.90),
		"hp_bar_mid":      Color(0.0, 0.95, 0.90),
		"preview_highlight": Color(0.8, 1.2, 1.5, 0.80),
		"shadow_color":    Color(0, 0, 0.05, 0.70),
		"card_shadow":     Color(0, 0.02, 0.10, 0.65),
		"rarity_common":   Color(0.60, 0.50, 0.80),
		"rarity_common_bg": Color(0.06, 0.04, 0.14),
		"rarity_rare":     Color(0.0, 0.90, 1.0),
		"rarity_rare_bg":  Color(0.04, 0.08, 0.20),
		"rarity_epic":     Color(1.0, 0.15, 0.65),
		"rarity_epic_bg":  Color(0.20, 0.04, 0.15),
		"card_name_text":  Color(0.95, 0.90, 1.0),
		"card_desc_text":  Color(0.70, 0.55, 0.90),
		"corner_radius":   0,
		"border_width":    2,
	},
}

# ── 数字颜色（扫雷1-8）也按主题分套 ───────────────────────────

const NUMBER_COLORS_BY_THEME = {
	ThemeStyle.SAKURA: [
		Color(0,0,0), Color(0.60,0.40,1.0), Color(0.40,0.80,0.50),
		Color(1.0,0.30,0.45), Color(0.70,0.35,0.90), Color(0.90,0.25,0.35),
		Color(0.50,0.70,0.90), Color(1.0,0.70,0.80), Color(0.80,0.50,0.65),
	],
	ThemeStyle.STEAM: [
		Color(0,0,0), Color(0.35,0.55,0.95), Color(0.25,0.75,0.35),
		Color(0.95,0.30,0.15), Color(0.55,0.35,0.85), Color(0.85,0.22,0.15),
		Color(0.25,0.70,0.75), Color(1.0,0.80,0.25), Color(0.75,0.50,0.20),
	],
	ThemeStyle.NEON: [
		Color(0,0,0), Color(0.0,0.90,1.0), Color(0.0,1.0,0.60),
		Color(1.0,0.15,0.55), Color(0.75,0.30,1.0), Color(1.0,0.35,0.75),
		Color(0.0,0.80,0.90), Color(1.0,0.90,0.15), Color(0.90,0.50,0.0),
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

# ── 主题纹理 (patterns) ──

const THEME_FOLDER = {
	ThemeStyle.SAKURA: "sakura",
	ThemeStyle.STEAM:  "steam",
	ThemeStyle.NEON:   "neon",
}
var _pattern_cache: Dictionary = {}

func get_pattern(pat_name: String) -> Texture2D:
	var folder = THEME_FOLDER[current_theme]
	var key = "%s/%s" % [folder, pat_name]
	if _pattern_cache.has(key):
		return _pattern_cache[key]
	var path = "res://assets/sprites/ui/patterns/%s/%s.png" % [folder, pat_name]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		tex = load(path) as Texture2D
	_pattern_cache[key] = tex
	return tex

# ── 主题素材 (themed sprites) ──
var _themed_cache: Dictionary = {}

func get_themed(tex_name: String) -> Texture2D:
	var folder = THEME_FOLDER[current_theme]
	var key = "%s/%s" % [folder, tex_name]
	if _themed_cache.has(key):
		return _themed_cache[key]
	var path = "res://assets/sprites/ui/themed/%s/%s.png" % [folder, tex_name]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		tex = load(path) as Texture2D
	_themed_cache[key] = tex  # get_themed
	return tex

func make_themed_stylebox(style_name: String, fallback_bg: String = "", fallback_brd: String = "") -> StyleBox:
	var tex = get_themed(style_name)
	if tex:
		var s = StyleBoxTexture.new()
		s.texture = tex
		return s
	if fallback_bg != "":
		return make_stylebox(fallback_bg, fallback_brd)
	return null

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
		current_theme = cfg.get_value("ui", "theme", ThemeStyle.SAKURA)
