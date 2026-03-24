## 标题界面 - 新游戏/继续/设置/退出
## 包含背景动画、菜单选项、视觉主题选择

extends Control

signal start_new_game
signal continue_game

const TITLE_BG = "res://assets/sprites/ui/title_bg.png"

var _menu_items: Array = []
var _selected:   int   = 0
var _can_input:  bool  = false
var _has_save:   bool  = false
var _theme_btns: Array = []
var _floor_picker: OptionButton = null
var _selected_floor: int = 1
var _settings_panel: Control = null
var _title_lbl: Label = null
var _sub_lbl: Label = null
var _overlay: ColorRect = null
var _menu_vbox: VBoxContainer = null
var _ver_lbl: Label = null
var _hint_lbl: Label = null
var _press_any_key: bool = true
var _press_overlay: Control = null
var _press_pulse_tween: Tween = null
var _settings_hint_lbl: Label = null

func _ready():
	_setup_scene()
	_show_press_any_key()

func _show_press_any_key():
	modulate = Color(1, 1, 1, 0)
	AudioManager.play_bgm("battle", false)
	# 隐藏菜单，只显示标题+按任意键
	if _menu_vbox:
		_menu_vbox.modulate = Color(1, 1, 1, 0)
	if _hint_lbl:
		_hint_lbl.modulate = Color(1, 1, 1, 0)
	if _ver_lbl:
		_ver_lbl.modulate = Color(1, 1, 1, 0)
	# 按任意键阶段：让背景图更亮
	if _overlay:
		_overlay.color.a = 0.45

	_press_overlay = Label.new()
	_press_overlay.text = "—  按任意键 / 手柄A键继续  —"
	_press_overlay.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_press_overlay.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_press_overlay.position = Vector2(0, 680)
	_press_overlay.size = Vector2(1920, 50)
	_press_overlay.add_theme_font_size_override("font_size", 28)
	_press_overlay.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	add_child(_press_overlay)

	# 闪烁动画
	_press_pulse_tween = create_tween().set_loops()
	_press_pulse_tween.tween_property(_press_overlay, "modulate:a", 0.3, 1.0)
	_press_pulse_tween.tween_property(_press_overlay, "modulate:a", 1.0, 1.0)

	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.8)

func _animate_in():
	_press_any_key = false
	if _press_pulse_tween and _press_pulse_tween.is_valid():
		_press_pulse_tween.kill()
		_press_pulse_tween = null
	if _press_overlay:
		_press_overlay.queue_free()
		_press_overlay = null
	# 恢复遮罩浓度
	if _overlay:
		var target_a = (UIThemeManager.color("intro_overlay") as Color).a
		var tw_ov = create_tween()
		tw_ov.tween_property(_overlay, "color:a", target_a, 0.4)
	# 显示菜单等元素
	if _menu_vbox:
		var tw1 = create_tween()
		tw1.tween_property(_menu_vbox, "modulate:a", 1.0, 0.4)
	if _hint_lbl:
		var tw2 = create_tween()
		tw2.tween_property(_hint_lbl, "modulate:a", 1.0, 0.4)
	if _ver_lbl:
		var tw3 = create_tween()
		tw3.tween_property(_ver_lbl, "modulate:a", 1.0, 0.3)
	_can_input = true
	await get_tree().create_timer(0.4).timeout

# ─── 场景构建 ────────────────────────────────────────────────

func _setup_scene():
	set_anchors_preset(Control.PRESET_FULL_RECT)

	# ── 背景图 ──
	var bg = TextureRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	if ResourceLoader.exists(TITLE_BG):
		bg.texture = load(TITLE_BG)
	bg.modulate = Color(0.85, 0.80, 0.75)
	add_child(bg)

	# ── 暗色遮罩 ──
	_overlay = ColorRect.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.color = UIThemeManager.color("intro_overlay")
	add_child(_overlay)

	# ── 标题文字 ──
	_title_lbl = Label.new()
	_title_lbl.text = "炸弹人勇闯地牢"
	_title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_title_lbl.position = Vector2(0, 100)
	_title_lbl.size = Vector2(1920, 130)
	_title_lbl.add_theme_font_size_override("font_size", 82)
	_title_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_accent"))
	_title_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	_title_lbl.add_theme_constant_override("shadow_offset_x", 5)
	_title_lbl.add_theme_constant_override("shadow_offset_y", 5)
	add_child(_title_lbl)

	_sub_lbl = Label.new()
	_sub_lbl.text = "BOMBER DUNGEON  100 FLOORS"
	_sub_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_sub_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_sub_lbl.position = Vector2(0, 218)
	_sub_lbl.size = Vector2(1920, 44)
	_sub_lbl.add_theme_font_size_override("font_size", 26)
	_sub_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	_sub_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	_sub_lbl.add_theme_constant_override("shadow_offset_x", 2)
	_sub_lbl.add_theme_constant_override("shadow_offset_y", 2)
	add_child(_sub_lbl)

	# ── 最佳记录 ──
	var best_floor = AchievementManager.stats.get("max_floor", 0)
	var total_runs = AchievementManager.stats.get("total_runs", 0)
	var unlocked = 0
	for aid in AchievementManager.ACHIEVEMENTS:
		if AchievementManager.unlocked.has(aid):
			unlocked += 1
	if total_runs > 0:
		var records_lbl = Label.new()
		records_lbl.text = "🏆 最高层: %d  |  🎮 游玩次数: %d  |  ⭐ 成就: %d/%d" % [best_floor, total_runs, unlocked, AchievementManager.ACHIEVEMENTS.size()]
		records_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		records_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
		records_lbl.position = Vector2(0, 268)
		records_lbl.size = Vector2(1920, 36)
		records_lbl.add_theme_font_size_override("font_size", 18)
		records_lbl.add_theme_color_override("font_color", Color(0.85, 0.78, 0.55, 0.8))
		records_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
		records_lbl.add_theme_constant_override("shadow_offset_x", 1)
		records_lbl.add_theme_constant_override("shadow_offset_y", 1)
		add_child(records_lbl)

	# ── 菜单容器 ──
	_menu_vbox = VBoxContainer.new()
	_menu_vbox.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_menu_vbox.position = Vector2(1920 / 2.0 - 200, 320)
	_menu_vbox.size = Vector2(400, 400)
	_menu_vbox.add_theme_constant_override("separation", 18)
	add_child(_menu_vbox)

	var items_def = [
		{"id": "story",    "label": "▶  观看故事",  "enabled": true},
		{"id": "new_game", "label": "⚔  新游戏",    "enabled": true},
		{"id": "continue", "label": "◎  继续游戏" if _has_save else "◎  继续游戏 (无存档)",  "enabled": _has_save},
		{"id": "settings", "label": "⚙  设置",      "enabled": true},
		{"id": "quit",     "label": "✕  退出",      "enabled": true},
	]

	_menu_items.clear()
	for item_def in items_def:
		var btn = _make_menu_btn(item_def["label"])
		btn.disabled = not item_def["enabled"]
		btn.set_meta("item_id", item_def["id"])
		btn.pressed.connect(func(): _on_menu_selected(btn.get_meta("item_id")))
		_menu_vbox.add_child(btn)
		_menu_items.append(btn)

	_update_selection(_default_menu_index())

	# ── 版权/版本 ──
	_ver_lbl = Label.new()
	_ver_lbl.text = "v0.1  --  MADE WITH GODOT 4"
	_ver_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_ver_lbl.position = Vector2(0, 1080 - 36)
	_ver_lbl.size = Vector2(1920, 28)
	_ver_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_ver_lbl.add_theme_font_size_override("font_size", 14)
	_ver_lbl.add_theme_color_override("font_color", (UIThemeManager.color("text_secondary") as Color).darkened(0.4))
	add_child(_ver_lbl)

	# ── 操作提示 ──
	_hint_lbl = Label.new()
	_hint_lbl.text = "↑↓ 选择  ENTER确认  ESC退出  手柄: ↑↓/A/B"
	_hint_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_hint_lbl.position = Vector2(0, 1080 - 68)
	_hint_lbl.size = Vector2(1920, 28)
	_hint_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint_lbl.add_theme_font_size_override("font_size", 18)
	_hint_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	_hint_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	_hint_lbl.add_theme_constant_override("shadow_offset_x", 1)
	_hint_lbl.add_theme_constant_override("shadow_offset_y", 1)
	add_child(_hint_lbl)

	_start_bg_animation(_title_lbl)

	UIThemeManager.theme_changed.connect(func(_n): _apply_theme())

func _default_menu_index() -> int:
	for i in range(_menu_items.size()):
		if _menu_items[i].get_meta("item_id") == "new_game" and not _menu_items[i].disabled:
			return i
	for i in range(_menu_items.size()):
		if not _menu_items[i].disabled:
			return i
	return 0

# ─── 主题实时刷新 ────────────────────────────────────────────

func _apply_theme():
	var tm = UIThemeManager
	if _title_lbl:
		_title_lbl.add_theme_color_override("font_color", tm.color("text_accent"))
	if _sub_lbl:
		_sub_lbl.add_theme_color_override("font_color", tm.color("text_secondary"))
	if _overlay:
		_overlay.color = tm.color("intro_overlay")
	if _ver_lbl:
		_ver_lbl.add_theme_color_override("font_color", (tm.color("text_secondary") as Color).darkened(0.4))
	if _hint_lbl:
		_hint_lbl.add_theme_color_override("font_color", tm.color("text_secondary"))
	# 刷新菜单按钮颜色
	for i in range(_menu_items.size()):
		var btn = _menu_items[i]
		var sn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
		btn.add_theme_stylebox_override("normal", sn)
		btn.add_theme_stylebox_override("disabled", sn)
		btn.add_theme_color_override("font_color", tm.color("text_primary"))
		btn.add_theme_color_override("font_disabled_color", (tm.color("text_secondary") as Color).darkened(0.4))
		var sh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong")
		btn.add_theme_stylebox_override("hover", sh)
		btn.add_theme_stylebox_override("pressed", sh)
	_update_selection(_selected)

# ─── 设置面板 ────────────────────────────────────────────────
const THEME_DEFS = [
	{
		"id": UIThemeManager.ThemeStyle.SAKURA,
		"name": "樱花幻境",
		"desc": "花瓣飘落 · 梦幻迷境",
		"accent": Color(1.0, 0.60, 0.78),
		"bg":     Color(0.09, 0.06, 0.12),
		"brd":    Color(0.50, 0.30, 0.45),
	},
	{
		"id": UIThemeManager.ThemeStyle.STEAM,
		"name": "蒸汽朋克",
		"desc": "齿轮咆哮 · 铜色帝国",
		"accent": Color(0.90, 0.70, 0.25),
		"bg":     Color(0.12, 0.09, 0.06),
		"brd":    Color(0.45, 0.35, 0.18),
	},
	{
		"id": UIThemeManager.ThemeStyle.NEON,
		"name": "霓虹都市",
		"desc": "电光幻影 · 赛博夜色",
		"accent": Color(1.0, 0.20, 0.80),
		"bg":     Color(0.04, 0.03, 0.10),
		"brd":    Color(0.20, 0.10, 0.40),
	},
]
func _open_settings():
	if _settings_panel:
		return
	_can_input = false

	_settings_panel = Control.new()
	_settings_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_settings_panel)

	# 遮罩
	var dim = ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.7)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			_close_settings()
	)
	_settings_panel.add_child(dim)

	# 主面板
	var panel = Control.new()
	panel.position = Vector2(220, 70)
	panel.size = Vector2(1480, 940)
	var ps = UIThemeManager.make_themed_stylebox("panel_bg", "hud_bg", "border_strong")
	var panel_bg = Panel.new()
	panel_bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel_bg.add_theme_stylebox_override("panel", ps)
	panel.add_child(panel_bg)
	_settings_panel.add_child(panel)

	# 标题区
	var stitle = Label.new()
	stitle.text = "⚙ 开始界面设置"
	stitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	stitle.position = Vector2(0, 18)
	stitle.size = Vector2(1480, 56)
	stitle.add_theme_font_size_override("font_size", 44)
	stitle.add_theme_color_override("font_color", UIThemeManager.color("text_accent"))
	stitle.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	stitle.add_theme_constant_override("shadow_offset_x", 2)
	stitle.add_theme_constant_override("shadow_offset_y", 2)
	panel.add_child(stitle)

	var ssub = Label.new()
	ssub.text = "在进入游戏前统一调整视觉、玩法、显示与音频"
	ssub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ssub.position = Vector2(0, 70)
	ssub.size = Vector2(1480, 30)
	ssub.add_theme_font_size_override("font_size", 18)
	ssub.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	panel.add_child(ssub)

	# 左右列卡片
	var left_card = Panel.new()
	left_card.position = Vector2(36, 112)
	left_card.size = Vector2(700, 740)
	left_card.add_theme_stylebox_override("panel", UIThemeManager.make_themed_stylebox("panel_bg", "btn_normal_bg", "btn_normal_brd"))
	panel.add_child(left_card)

	var right_card = Panel.new()
	right_card.position = Vector2(744, 112)
	right_card.size = Vector2(700, 740)
	right_card.add_theme_stylebox_override("panel", UIThemeManager.make_themed_stylebox("panel_bg", "btn_normal_bg", "btn_normal_brd"))
	panel.add_child(right_card)

	# 右上角关闭
	var close_btn = Button.new()
	close_btn.text = "✕"
	close_btn.position = Vector2(1418, 16)
	close_btn.size = Vector2(44, 38)
	close_btn.add_theme_font_size_override("font_size", 22)
	close_btn.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd"))
	close_btn.add_theme_stylebox_override("hover", UIThemeManager.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong"))
	close_btn.add_theme_stylebox_override("pressed", UIThemeManager.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong"))
	close_btn.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	close_btn.pressed.connect(_close_settings)
	panel.add_child(close_btn)

	# 左列：视觉风格
	var style_lbl = Label.new()
	style_lbl.text = "视觉风格"
	style_lbl.position = Vector2(20, 18)
	style_lbl.size = Vector2(220, 32)
	style_lbl.add_theme_font_size_override("font_size", 26)
	style_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	left_card.add_child(style_lbl)

	var card_w = 210
	var card_h = 118
	var gap = 14
	var start_x = 22
	var card_y = 62
	_theme_btns.clear()
	for i in range(THEME_DEFS.size()):
		var tdef = THEME_DEFS[i]
		var btn = _make_theme_card(tdef, card_w, card_h, tdef["id"] == UIThemeManager.current_theme)
		btn.position = Vector2(start_x + i * (card_w + gap), card_y)
		btn.set_meta("theme_id", tdef["id"])
		var cap_btn = btn
		btn.pressed.connect(func():
			UIThemeManager.set_theme(cap_btn.get_meta("theme_id"))
			_close_settings()
			_open_settings()
		)
		left_card.add_child(btn)
		_theme_btns.append(btn)

	# 左列：显示设置
	var display_lbl = Label.new()
	display_lbl.text = "显示设置"
	display_lbl.position = Vector2(20, 220)
	display_lbl.size = Vector2(220, 32)
	display_lbl.add_theme_font_size_override("font_size", 26)
	display_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	left_card.add_child(display_lbl)

	var res_lbl = Label.new()
	res_lbl.text = "分辨率"
	res_lbl.position = Vector2(24, 266)
	res_lbl.size = Vector2(100, 30)
	res_lbl.add_theme_font_size_override("font_size", 18)
	res_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(res_lbl)

	var res_picker = OptionButton.new()
	res_picker.position = Vector2(130, 264)
	res_picker.size = Vector2(220, 36)
	res_picker.add_theme_font_size_override("font_size", 16)
	res_picker.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd"))
	res_picker.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	for i in range(GameSettings.RESOLUTION_LABELS.size()):
		res_picker.add_item(GameSettings.RESOLUTION_LABELS[i], i)
	res_picker.selected = GameSettings.resolution_index
	res_picker.item_selected.connect(func(idx): GameSettings.set_resolution(idx))
	left_card.add_child(res_picker)

	var fs_check = CheckButton.new()
	fs_check.text = "全屏"
	fs_check.position = Vector2(372, 264)
	fs_check.size = Vector2(120, 36)
	fs_check.button_pressed = GameSettings.fullscreen
	fs_check.add_theme_font_size_override("font_size", 18)
	fs_check.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	fs_check.toggled.connect(func(on): GameSettings.set_fullscreen(on))
	left_card.add_child(fs_check)

	var fps_lbl = Label.new()
	fps_lbl.text = "帧率"
	fps_lbl.position = Vector2(24, 314)
	fps_lbl.size = Vector2(100, 30)
	fps_lbl.add_theme_font_size_override("font_size", 18)
	fps_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(fps_lbl)

	var fps_picker = OptionButton.new()
	fps_picker.position = Vector2(130, 312)
	fps_picker.size = Vector2(170, 36)
	fps_picker.add_theme_font_size_override("font_size", 16)
	fps_picker.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd"))
	fps_picker.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	for i in range(GameSettings.FPS_LABELS.size()):
		fps_picker.add_item(GameSettings.FPS_LABELS[i], i)
	fps_picker.selected = GameSettings.fps_index
	fps_picker.item_selected.connect(func(idx): GameSettings.set_fps(idx))
	left_card.add_child(fps_picker)

	var vs_check = CheckButton.new()
	vs_check.text = "垂直同步"
	vs_check.position = Vector2(318, 312)
	vs_check.size = Vector2(170, 36)
	vs_check.button_pressed = GameSettings.vsync_on
	vs_check.add_theme_font_size_override("font_size", 18)
	vs_check.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	vs_check.toggled.connect(func(on): GameSettings.set_vsync(on))
	left_card.add_child(vs_check)

	# 左列：音量设置
	var audio_lbl = Label.new()
	audio_lbl.text = "音量设置"
	audio_lbl.position = Vector2(20, 384)
	audio_lbl.size = Vector2(220, 32)
	audio_lbl.add_theme_font_size_override("font_size", 26)
	audio_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	left_card.add_child(audio_lbl)

	var mus_lbl = Label.new()
	mus_lbl.text = "音乐"
	mus_lbl.position = Vector2(24, 432)
	mus_lbl.size = Vector2(70, 30)
	mus_lbl.add_theme_font_size_override("font_size", 18)
	mus_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(mus_lbl)

	var mus_slider = HSlider.new()
	mus_slider.position = Vector2(98, 434)
	mus_slider.size = Vector2(430, 28)
	mus_slider.min_value = 0.0
	mus_slider.max_value = 1.0
	mus_slider.step = 0.05
	mus_slider.value = GameSettings.music_volume
	mus_slider.value_changed.connect(func(val): GameSettings.set_music_volume(val))
	left_card.add_child(mus_slider)

	var mus_val = Label.new()
	mus_val.text = "%d%%" % int(GameSettings.music_volume * 100)
	mus_val.position = Vector2(540, 430)
	mus_val.size = Vector2(64, 30)
	mus_val.add_theme_font_size_override("font_size", 16)
	mus_val.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(mus_val)
	mus_slider.value_changed.connect(func(val): mus_val.text = "%d%%" % int(val * 100))

	var sfx_lbl = Label.new()
	sfx_lbl.text = "音效"
	sfx_lbl.position = Vector2(24, 474)
	sfx_lbl.size = Vector2(70, 30)
	sfx_lbl.add_theme_font_size_override("font_size", 18)
	sfx_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(sfx_lbl)

	var sfx_slider = HSlider.new()
	sfx_slider.position = Vector2(98, 476)
	sfx_slider.size = Vector2(430, 28)
	sfx_slider.min_value = 0.0
	sfx_slider.max_value = 1.0
	sfx_slider.step = 0.05
	sfx_slider.value = GameSettings.sfx_volume
	sfx_slider.value_changed.connect(func(val): GameSettings.set_sfx_volume(val))
	left_card.add_child(sfx_slider)

	var sfx_val = Label.new()
	sfx_val.text = "%d%%" % int(GameSettings.sfx_volume * 100)
	sfx_val.position = Vector2(540, 472)
	sfx_val.size = Vector2(64, 30)
	sfx_val.add_theme_font_size_override("font_size", 16)
	sfx_val.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	left_card.add_child(sfx_val)
	sfx_slider.value_changed.connect(func(val): sfx_val.text = "%d%%" % int(val * 100))

	# 右列：玩法设置
	var game_lbl = Label.new()
	game_lbl.text = "玩法设置"
	game_lbl.position = Vector2(20, 18)
	game_lbl.size = Vector2(220, 32)
	game_lbl.add_theme_font_size_override("font_size", 26)
	game_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	right_card.add_child(game_lbl)

	var floor_lbl = Label.new()
	floor_lbl.text = "起始关卡"
	floor_lbl.position = Vector2(24, 66)
	floor_lbl.size = Vector2(140, 30)
	floor_lbl.add_theme_font_size_override("font_size", 20)
	floor_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	right_card.add_child(floor_lbl)

	_floor_picker = OptionButton.new()
	_floor_picker.position = Vector2(170, 62)
	_floor_picker.size = Vector2(500, 38)
	_floor_picker.add_theme_font_size_override("font_size", 18)
	_floor_picker.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd"))
	_floor_picker.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	for i in range(1, 301):
		var level = LevelData.get_level(i)
		var cycle = LevelData.get_cycle(i)
		var cycle_str = "" if cycle == 0 else " [%d周目]" % (cycle + 1)
		_floor_picker.add_item("%d层 - %s%s" % [i, level["name"], cycle_str], i)
	_floor_picker.selected = _selected_floor - 1
	_floor_picker.item_selected.connect(func(idx): _selected_floor = _floor_picker.get_item_id(idx))
	right_card.add_child(_floor_picker)

	var diff_lbl = Label.new()
	diff_lbl.text = "预设难度"
	diff_lbl.position = Vector2(24, 122)
	diff_lbl.size = Vector2(140, 30)
	diff_lbl.add_theme_font_size_override("font_size", 20)
	diff_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	right_card.add_child(diff_lbl)

	var preset_colors = [Color(0.3, 0.8, 0.4), Color(0.9, 0.8, 0.3), Color(0.9, 0.3, 0.3)]
	for di in range(GameSettings.DIFFICULTY_LABELS.size()):
		var dbtn = Button.new()
		var is_sel = (di == GameSettings.difficulty)
		dbtn.text = GameSettings.DIFFICULTY_LABELS[di]
		dbtn.position = Vector2(170 + di * 166, 118)
		dbtn.size = Vector2(150, 34)
		dbtn.add_theme_font_size_override("font_size", 17)
		var ds = StyleBoxFlat.new()
		ds.set_corner_radius_all(8)
		ds.set_border_width_all(2 if not is_sel else 3)
		ds.bg_color = preset_colors[di].darkened(0.5) if is_sel else UIThemeManager.color("btn_normal_bg")
		ds.border_color = preset_colors[di] if is_sel else UIThemeManager.color("btn_normal_brd")
		dbtn.add_theme_stylebox_override("normal", ds)
		var dsh = ds.duplicate()
		dsh.border_color = preset_colors[di]
		dsh.set_border_width_all(3)
		dbtn.add_theme_stylebox_override("hover", dsh)
		dbtn.add_theme_stylebox_override("pressed", dsh)
		dbtn.add_theme_color_override("font_color", preset_colors[di] if is_sel else UIThemeManager.color("text_primary"))
		var cap_di = di
		dbtn.pressed.connect(func():
			GameSettings.set_difficulty(cap_di)
			_close_settings()
			_open_settings()
		)
		right_card.add_child(dbtn)

	var mine_lbl = Label.new()
	mine_lbl.text = "扫雷难度"
	mine_lbl.position = Vector2(24, 182)
	mine_lbl.size = Vector2(140, 28)
	mine_lbl.add_theme_font_size_override("font_size", 18)
	mine_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	right_card.add_child(mine_lbl)

	var mine_slider = HSlider.new()
	mine_slider.position = Vector2(170, 186)
	mine_slider.size = Vector2(420, 24)
	mine_slider.min_value = 0.3
	mine_slider.max_value = 3.0
	mine_slider.step = 0.1
	mine_slider.value = GameSettings.mine_difficulty
	right_card.add_child(mine_slider)

	var mine_val = Label.new()
	mine_val.text = "×%.1f" % GameSettings.mine_difficulty
	mine_val.position = Vector2(600, 182)
	mine_val.size = Vector2(74, 28)
	mine_val.add_theme_font_size_override("font_size", 18)
	mine_val.add_theme_color_override("font_color", _diff_color(GameSettings.mine_difficulty, 1.0))
	right_card.add_child(mine_val)

	var boss_lbl = Label.new()
	boss_lbl.text = "Boss血量"
	boss_lbl.position = Vector2(24, 226)
	boss_lbl.size = Vector2(140, 28)
	boss_lbl.add_theme_font_size_override("font_size", 18)
	boss_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	right_card.add_child(boss_lbl)

	var boss_slider = HSlider.new()
	boss_slider.position = Vector2(170, 230)
	boss_slider.size = Vector2(420, 24)
	boss_slider.min_value = 0.3
	boss_slider.max_value = 5.0
	boss_slider.step = 0.1
	boss_slider.value = GameSettings.boss_hp_mult
	right_card.add_child(boss_slider)

	var boss_val = Label.new()
	boss_val.text = "×%.1f" % GameSettings.boss_hp_mult
	boss_val.position = Vector2(600, 226)
	boss_val.size = Vector2(74, 28)
	boss_val.add_theme_font_size_override("font_size", 18)
	boss_val.add_theme_color_override("font_color", _diff_color(GameSettings.boss_hp_mult, 1.0))
	right_card.add_child(boss_val)

	mine_slider.value_changed.connect(func(val):
		GameSettings.set_mine_difficulty(val)
		mine_val.text = "×%.1f" % val
		mine_val.add_theme_color_override("font_color", _diff_color(val, 1.0))
	)
	boss_slider.value_changed.connect(func(val):
		GameSettings.set_boss_hp_mult(val)
		boss_val.text = "×%.1f" % val
		boss_val.add_theme_color_override("font_color", _diff_color(val, 1.0))
	)

	# 右列：实时预估
	var preview_lbl = Label.new()
	preview_lbl.text = "当前配置预估"
	preview_lbl.position = Vector2(24, 292)
	preview_lbl.size = Vector2(200, 30)
	preview_lbl.add_theme_font_size_override("font_size", 22)
	preview_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	right_card.add_child(preview_lbl)

	var preview_box = RichTextLabel.new()
	preview_box.position = Vector2(24, 330)
	preview_box.size = Vector2(650, 300)
	preview_box.bbcode_enabled = true
	preview_box.fit_content = false
	preview_box.scroll_active = false
	preview_box.add_theme_font_size_override("normal_font_size", 17)
	preview_box.add_theme_color_override("default_color", UIThemeManager.color("text_secondary"))
	right_card.add_child(preview_box)

	var refresh_preview = func():
		var f = _selected_floor
		var bomb_n = LevelData.get_bomb_count(f)
		var clicks = LevelData.get_max_clicks(f)
		var t = LevelData.get_turn_duration(f)
		var atk = LevelData.get_boss_attack(f)
		preview_box.clear()
		preview_box.append_text("[color=#ffd98a]关卡[/color]  第%d层\n" % f)
		preview_box.append_text("[color=#ffd98a]探索[/color]  炸弹数 %d, 点击 %d\n" % [bomb_n, clicks])
		preview_box.append_text("[color=#ffd98a]战斗[/color]  回合时长 %.1fs, Boss攻击 %d\n" % [t, atk])
		preview_box.append_text("[color=#ffd98a]自定义[/color]  扫雷 x%.1f, Boss血量 x%.1f\n" % [GameSettings.mine_difficulty, GameSettings.boss_hp_mult])
		preview_box.append_text("[color=#ffd98a]难度预设[/color]  %s" % GameSettings.get_difficulty_label())

	refresh_preview.call()
	_floor_picker.item_selected.connect(func(_idx): refresh_preview.call())
	mine_slider.value_changed.connect(func(_v): refresh_preview.call())
	boss_slider.value_changed.connect(func(_v): refresh_preview.call())

	# 底部按钮区
	var reset_btn = Button.new()
	reset_btn.text = "重置为标准"
	reset_btn.position = Vector2(36, 868)
	reset_btn.size = Vector2(230, 50)
	reset_btn.add_theme_font_size_override("font_size", 22)
	reset_btn.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd"))
	reset_btn.add_theme_stylebox_override("hover", UIThemeManager.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong"))
	reset_btn.add_theme_stylebox_override("pressed", UIThemeManager.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong"))
	reset_btn.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	reset_btn.pressed.connect(func():
		GameSettings.set_resolution(2)
		GameSettings.set_fullscreen(false)
		GameSettings.set_fps(1)
		GameSettings.set_vsync(true)
		GameSettings.set_difficulty(1)
		GameSettings.set_music_volume(0.7)
		GameSettings.set_sfx_volume(1.0)
		_selected_floor = 1
		_close_settings()
		_open_settings()
	)
	panel.add_child(reset_btn)

	var back_btn = Button.new()
	back_btn.text = "← 返回"
	back_btn.position = Vector2(1160, 864)
	back_btn.size = Vector2(284, 56)
	back_btn.add_theme_font_size_override("font_size", 30)
	back_btn.add_theme_stylebox_override("normal", UIThemeManager.make_themed_stylebox("btn_end_normal", "btn_end_bg", "btn_end_brd"))
	back_btn.add_theme_stylebox_override("hover", UIThemeManager.make_themed_stylebox("btn_end_hover", "btn_end_hover", "btn_end_hbrd"))
	back_btn.add_theme_stylebox_override("pressed", UIThemeManager.make_themed_stylebox("btn_end_hover", "btn_end_hover", "btn_end_hbrd"))
	back_btn.add_theme_color_override("font_color", UIThemeManager.color("btn_end_text"))
	back_btn.pressed.connect(_close_settings)
	panel.add_child(back_btn)

	_settings_hint_lbl = Label.new()
	_settings_hint_lbl.text = "ESC / 手柄B / 点击遮罩 关闭"
	_settings_hint_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_settings_hint_lbl.position = Vector2(820, 872)
	_settings_hint_lbl.size = Vector2(320, 36)
	_settings_hint_lbl.add_theme_font_size_override("font_size", 16)
	_settings_hint_lbl.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	panel.add_child(_settings_hint_lbl)

	# 淡入
	_settings_panel.modulate = Color(1, 1, 1, 0)
	var tw = create_tween()
	tw.tween_property(_settings_panel, "modulate:a", 1.0, 0.25)

func _close_settings():
	if not _settings_panel:
		return
	_settings_hint_lbl = null
	_settings_panel.queue_free()
	_settings_panel = null
	_can_input = true

func _diff_color(val: float, center: float) -> Color:
	if val < center * 0.8:
		return Color(0.3, 0.85, 0.4)
	elif val > center * 1.3:
		return Color(0.95, 0.3, 0.2)
	return Color(0.9, 0.8, 0.3)

func _make_theme_card(tdef: Dictionary, w: int, h: int, selected: bool) -> Button:
	var btn = Button.new()
	btn.custom_minimum_size = Vector2(w, h)
	btn.size = Vector2(w, h)

	var s = StyleBoxFlat.new()
	s.bg_color = tdef["bg"]
	s.border_color = tdef["brd"] if not selected else tdef["accent"]
	s.set_border_width_all(4 if selected else 2)
	s.set_corner_radius_all(8)
	s.shadow_color = (tdef["accent"] as Color).darkened(0.2)
	s.shadow_size = 8 if selected else 2
	btn.add_theme_stylebox_override("normal", s)
	var h_style = s.duplicate()
	h_style.border_color = tdef["accent"]
	h_style.set_border_width_all(4)
	h_style.shadow_size = 6
	btn.add_theme_stylebox_override("hover", h_style)
	btn.add_theme_stylebox_override("pressed", h_style)

	# 名字
	var name_lbl = Label.new()
	name_lbl.text = tdef["name"]
	name_lbl.position = Vector2(12, 10)
	name_lbl.size = Vector2(w - 24, 34)
	name_lbl.add_theme_font_size_override("font_size", 22)
	name_lbl.add_theme_color_override("font_color", tdef["accent"])
	name_lbl.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	name_lbl.add_theme_constant_override("shadow_offset_x", 1)
	name_lbl.add_theme_constant_override("shadow_offset_y", 1)
	btn.add_child(name_lbl)

	# 描述
	var desc_lbl = Label.new()
	desc_lbl.text = tdef["desc"]
	desc_lbl.position = Vector2(12, 46)
	desc_lbl.size = Vector2(w - 24, 44)
	desc_lbl.add_theme_font_size_override("font_size", 15)
	desc_lbl.add_theme_color_override("font_color", (tdef["accent"] as Color).darkened(0.1))
	btn.add_child(desc_lbl)

	# 选中指示点
	if selected:
		var dot = Label.new()
		dot.text = "●"
		dot.position = Vector2(w - 30, 8)
		dot.size = Vector2(22, 22)
		dot.add_theme_font_size_override("font_size", 16)
		dot.add_theme_color_override("font_color", tdef["accent"])
		btn.add_child(dot)

	return btn

# ─── 菜单按钮 ────────────────────────────────────────────────

func _make_menu_btn(label_text: String) -> Button:
	var tm = UIThemeManager
	var btn = Button.new()
	btn.text = label_text
	btn.custom_minimum_size = Vector2(400, 62)
	btn.add_theme_font_size_override("font_size", 32)

	var sn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
	btn.add_theme_stylebox_override("normal",   sn)
	btn.add_theme_stylebox_override("disabled", sn)
	btn.add_theme_color_override("font_color",          tm.color("text_primary"))
	btn.add_theme_color_override("font_disabled_color", (tm.color("text_secondary") as Color).darkened(0.4))
	btn.add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
	btn.add_theme_constant_override("shadow_offset_x", 2)
	btn.add_theme_constant_override("shadow_offset_y", 2)

	var sh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong")
	btn.add_theme_stylebox_override("hover",   sh)
	btn.add_theme_stylebox_override("pressed", sh)

	btn.mouse_entered.connect(func():
		var idx = _menu_items.find(btn)
		if idx >= 0:
			_update_selection(idx)
			AudioManager.play_sfx("ui_click")
	)
	return btn

func _update_selection(idx: int):
	var tm = UIThemeManager
	_selected = idx
	for i in range(_menu_items.size()):
		var btn = _menu_items[i]
		if i == _selected and not btn.disabled:
			var sh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong")
			btn.add_theme_stylebox_override("normal", sh)
		else:
			var sn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
			btn.add_theme_stylebox_override("normal", sn)

func _start_bg_animation(title_lbl: Label):
	var pulse = create_tween().set_loops()
	pulse.tween_property(title_lbl, "modulate:v", 0.85, 1.4)
	pulse.tween_property(title_lbl, "modulate:v", 1.0,  1.4)

# ─── 键盘导航 ────────────────────────────────────────────────

func _input(event):
	# 按任意键阶段
	if _press_any_key:
		if (event is InputEventKey or event is InputEventMouseButton or event is InputEventJoypadButton) and event.pressed:
			_animate_in()
		return
	# 设置面板打开时，ESC关闭它
	if _settings_panel:
		if event is InputEventJoypadButton and event.pressed and event.button_index == JOY_BUTTON_B:
			_close_settings()
			return
		if event is InputEventKey and event.pressed and not event.echo:
			if event.keycode == KEY_ESCAPE:
				_close_settings()
		return
	if not _can_input:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_UP, KEY_W:
				_move_selection(-1)
			KEY_DOWN, KEY_S:
				_move_selection(1)
			KEY_ENTER, KEY_KP_ENTER, KEY_SPACE:
				_activate_selected()
			KEY_ESCAPE:
				_on_menu_selected("quit")
	if event is InputEventJoypadButton and event.pressed:
		match event.button_index:
			JOY_BUTTON_DPAD_UP:
				_move_selection(-1)
			JOY_BUTTON_DPAD_DOWN:
				_move_selection(1)
			JOY_BUTTON_A:
				_activate_selected()
			JOY_BUTTON_B:
				_on_menu_selected("quit")

func _move_selection(dir: int):
	AudioManager.play_sfx("ui_click")
	var attempts = 0
	var new_sel = _selected
	while attempts < _menu_items.size():
		new_sel = (new_sel + dir + _menu_items.size()) % _menu_items.size()
		if not _menu_items[new_sel].disabled:
			break
		attempts += 1
	_update_selection(new_sel)

func _activate_selected():
	var btn = _menu_items[_selected]
	if not btn.disabled:
		_on_menu_selected(btn.get_meta("item_id"))

func _on_menu_selected(item_id: String):
	AudioManager.play_sfx("upgrade_pick")
	match item_id:
		"story":
			_transition_to_story()
		"new_game":
			_transition_to_game(false)
		"continue":
			_transition_to_game(true)
		"settings":
			_open_settings()
		"quit":
			get_tree().quit()

# ─── 场景切换 ────────────────────────────────────────────────

func _transition_to_story():
	_can_input = false
	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.4)
	await tw.finished
	get_tree().change_scene_to_file("res://scenes/ui/StoryScreen.tscn")

func _transition_to_game(is_continue: bool):
	_can_input = false
	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.4)
	await tw.finished
	if not is_continue:
		_reset_game_state()
	get_tree().change_scene_to_file("res://scenes/game/Main.tscn")

func _reset_game_state():
	GameManager.player_hp       = GameManager.player_max_hp
	var start_floor = _selected_floor
	GameManager.floor_number    = start_floor
	GameManager.bomb_inventory.clear()
	GameManager.bomb_inventory_changed.emit()
	GameManager.triggered_thresholds.clear()
	GameManager.max_clicks      = LevelData.get_max_clicks(start_floor)
	GameManager.turn_duration   = LevelData.get_turn_duration(start_floor)
	GridManager.reset_for_new_floor()
	UpgradeManager.clear_combat_effects()
	BombRegistry.reset_to_defaults()
