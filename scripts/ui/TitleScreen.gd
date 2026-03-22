## 标题界面 - 新游戏/继续/设置/退出
## 包含背景动画、菜单选项

extends Control

signal start_new_game
signal continue_game

const TITLE_BG = "res://assets/sprites/ui/title_bg.png"

var _menu_items: Array = []
var _selected:   int   = 0
var _can_input:  bool  = false
var _has_save:   bool  = false  # 是否有存档（目前简化为false）

func _ready():
	_setup_scene()
	_animate_in()

func _animate_in():
	modulate = Color(1, 1, 1, 0)
	AudioManager.play_bgm("battle", false)
	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.8)
	tw.tween_callback(func(): _can_input = true)
	await tw.finished

# ─── 场景构建（在 _ready 调用）───────────────────────────────

func _setup_scene():
	set_anchors_preset(Control.PRESET_FULL_RECT)

	# ── 背景图 ──
	var bg = TextureRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	if ResourceLoader.exists(TITLE_BG):
		bg.texture = load(TITLE_BG)
	bg.modulate = Color(0.6, 0.55, 0.5)  # 稍微压暗让文字清晰
	add_child(bg)

	# ── 像素风暗色遮罩 ──
	var overlay = ColorRect.new()
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	overlay.color = Color(0.0, 0.0, 0.02, 0.55)
	add_child(overlay)

	# ── 扫描线效果 ──
	var scanlines = ColorRect.new()
	scanlines.set_anchors_preset(Control.PRESET_FULL_RECT)
	scanlines.color = Color(0, 0, 0, 0)  # 实际扫描线用 shader 更好，这里跳过
	add_child(scanlines)

	# ── 标题文字 ──
	var title_lbl = Label.new()
	title_lbl.text = "炸弹人勇闯地牢"
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	title_lbl.position = Vector2(0, 80)
	title_lbl.size = Vector2(1920, 120)
	title_lbl.add_theme_font_size_override("font_size", 72)
	title_lbl.add_theme_color_override("font_color", Color(0.95, 0.80, 0.20))
	title_lbl.add_theme_color_override("font_shadow_color", Color(0.5, 0.15, 0.0, 0.9))
	title_lbl.add_theme_constant_override("shadow_offset_x", 4)
	title_lbl.add_theme_constant_override("shadow_offset_y", 4)
	add_child(title_lbl)

	var sub_lbl = Label.new()
	sub_lbl.text = "BOMBER DUNGEON  100 FLOORS"
	sub_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	sub_lbl.position = Vector2(0, 168)
	sub_lbl.size = Vector2(1920, 40)
	sub_lbl.add_theme_font_size_override("font_size", 22)
	sub_lbl.add_theme_color_override("font_color", Color(0.65, 0.55, 0.35))
	add_child(sub_lbl)

	# ── 菜单容器 ──
	var menu_vbox = VBoxContainer.new()
	menu_vbox.set_anchors_preset(Control.PRESET_TOP_LEFT)
	menu_vbox.position = Vector2(1920 / 2.0 - 180, 340)
	menu_vbox.size = Vector2(360, 280)
	menu_vbox.add_theme_constant_override("separation", 16)
	add_child(menu_vbox)

	# 菜单项定义
	var items_def = [
		{"id": "story",    "label": "▶  观看故事",  "enabled": true},
		{"id": "new_game", "label": "⚔  新游戏",    "enabled": true},
		{"id": "continue", "label": "◎  继续游戏",  "enabled": _has_save},
		{"id": "quit",     "label": "✕  退出",      "enabled": true},
	]

	_menu_items.clear()
	for item_def in items_def:
		var btn = _make_menu_btn(item_def["label"])
		btn.disabled = not item_def["enabled"]
		btn.set_meta("item_id", item_def["id"])
		btn.pressed.connect(func(): _on_menu_selected(btn.get_meta("item_id")))
		menu_vbox.add_child(btn)
		_menu_items.append(btn)

	_update_selection(0)

	# ── 版权/版本 ──
	var ver_lbl = Label.new()
	ver_lbl.text = "v0.1  --  MADE WITH GODOT 4"
	ver_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	ver_lbl.position = Vector2(0, 1080 - 36)
	ver_lbl.size = Vector2(1920, 28)
	ver_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ver_lbl.add_theme_font_size_override("font_size", 14)
	ver_lbl.add_theme_color_override("font_color", Color(0.35, 0.32, 0.28))
	add_child(ver_lbl)

	# ── 操作提示 ──
	var hint_lbl = Label.new()
	hint_lbl.text = "↑↓ 选择    ENTER / 点击 确认"
	hint_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hint_lbl.position = Vector2(0, 1080 - 68)
	hint_lbl.size = Vector2(1920, 28)
	hint_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint_lbl.add_theme_font_size_override("font_size", 16)
	hint_lbl.add_theme_color_override("font_color", Color(0.55, 0.50, 0.40))
	add_child(hint_lbl)

	# ── 背景粒子（简单跳动的炸弹符号）──
	_start_bg_animation(title_lbl)

func _make_menu_btn(label_text: String) -> Button:
	var btn = Button.new()
	btn.text = label_text
	btn.custom_minimum_size = Vector2(360, 56)
	btn.add_theme_font_size_override("font_size", 28)

	var s_normal = StyleBoxFlat.new()
	s_normal.bg_color      = Color(0.08, 0.06, 0.04, 0.85)
	s_normal.border_color  = Color(0.35, 0.28, 0.18)
	s_normal.set_border_width_all(2)
	s_normal.set_corner_radius_all(4)
	btn.add_theme_stylebox_override("normal",   s_normal)
	btn.add_theme_stylebox_override("disabled", s_normal)
	btn.add_theme_color_override("font_color",          Color(0.85, 0.80, 0.65))
	btn.add_theme_color_override("font_disabled_color", Color(0.35, 0.32, 0.28))

	var s_hover = s_normal.duplicate()
	s_hover.bg_color    = Color(0.18, 0.14, 0.08, 0.95)
	s_hover.border_color = Color(0.75, 0.60, 0.25)
	s_hover.set_border_width_all(3)
	btn.add_theme_stylebox_override("hover",   s_hover)
	btn.add_theme_stylebox_override("pressed", s_hover)

	btn.mouse_entered.connect(func():
		var idx = _menu_items.find(btn)
		if idx >= 0:
			_update_selection(idx)
			AudioManager.play_sfx("ui_click")
	)
	return btn

func _update_selection(idx: int):
	_selected = idx
	for i in range(_menu_items.size()):
		var btn = _menu_items[i]
		var s = StyleBoxFlat.new()
		if i == _selected and not btn.disabled:
			s.bg_color     = Color(0.22, 0.16, 0.06, 0.95)
			s.border_color = Color(0.95, 0.75, 0.20)
			s.set_border_width_all(3)
		else:
			s.bg_color     = Color(0.08, 0.06, 0.04, 0.85)
			s.border_color = Color(0.35, 0.28, 0.18)
			s.set_border_width_all(2)
		s.set_corner_radius_all(4)
		btn.add_theme_stylebox_override("normal", s)

func _start_bg_animation(title_lbl: Label):
	# 标题脉冲
	var pulse = create_tween().set_loops()
	pulse.tween_property(title_lbl, "modulate:v", 0.85, 1.4)
	pulse.tween_property(title_lbl, "modulate:v", 1.0,  1.4)

# ─── 键盘导航 ────────────────────────────────────────────────

func _input(event):
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
	GameManager.floor_number    = 1
	GameManager.bomb_inventory.clear()
	GameManager.bomb_inventory_changed.emit()
	GameManager.triggered_thresholds.clear()
	GameManager.max_clicks      = LevelData.get_max_clicks(1)
	GameManager.turn_duration   = LevelData.get_turn_duration(1)
	GridManager.reset_for_new_floor()
	UpgradeManager.clear_combat_effects()
	BombRegistry.reset_to_defaults()
