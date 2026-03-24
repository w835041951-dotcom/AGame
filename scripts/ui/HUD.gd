## HUD - 顶部状态栏

extends Control

signal reset_board_pressed

@onready var timer_label: Label = $TimerLabel
@onready var player_hp_label: Label = $PlayerHPLabel
@onready var boss_hp_bar: ProgressBar = $BossHPBar
@onready var boss_hp_label: Label = $BossHPLabel
@onready var floor_label: Label = $FloorLabel
@onready var clicks_label: Label = $ClicksLabel

var _intel_label: Label = null
var _challenge_label: Label = null
var _intent_label: Label = null

var _reset_btn: Button = null
var _last_timer_int: int = -1
var _display_boss_hp: float = 0.0
var _prev_player_hp: int = -1
var _hud_bar_bg: TextureRect = null
var _label_bg_nodes: Array = []
var _icon_nodes: Array = []
var _vignette: ColorRect = null
var _vignette_alpha: float = 0.0

func _ready():
	_create_reset_button()
	_create_runtime_labels()
	_create_vignette()
	_build_themed_visuals()
	_apply_theme()
	UIThemeManager.theme_changed.connect(func(_n):
		_rebuild_themed_visuals()
		_apply_theme()
	)

func _create_vignette():
	_vignette = ColorRect.new()
	_vignette.color = Color(0.8, 0.0, 0.0, 0.0)
	_vignette.size = Vector2(1920, 1080)
	_vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_vignette.z_index = 10
	add_child(_vignette)

func _build_themed_visuals():
	# HUD底板
	var bar_tex = UIThemeManager.get_themed("hud_bar_bg")
	if bar_tex:
		_hud_bar_bg = TextureRect.new()
		_hud_bar_bg.texture = bar_tex
		_hud_bar_bg.stretch_mode = TextureRect.STRETCH_SCALE
		_hud_bar_bg.set_anchors_preset(Control.PRESET_TOP_WIDE)
		_hud_bar_bg.size = Vector2(1920, 68)
		_hud_bar_bg.z_index = -2
		_hud_bar_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_hud_bar_bg)
	# 标签装饰底板
	_add_label_bg(floor_label,  "floor_badge",     Vector2(160, 42))
	_add_label_bg(clicks_label, "bomb_counter_bg", Vector2(170, 42))
	if _intel_label:
		_add_label_bg(_intel_label, "bomb_counter_bg", Vector2(170, 42))
	_add_label_bg(player_hp_label, "hp_badge",     Vector2(180, 42))
	_add_label_bg(timer_label,  "timer_badge",     Vector2(140, 42))
	# 分割线
	var sep_tex = UIThemeManager.get_themed("separator_h")
	if sep_tex:
		var sep = TextureRect.new()
		sep.texture = sep_tex
		sep.stretch_mode = TextureRect.STRETCH_SCALE
		sep.size = Vector2(1920, 6)
		sep.position = Vector2(0, 64)
		sep.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(sep)
		_icon_nodes.append(sep)
	# 四角装饰
	for corner in ["frame_corner_tl", "frame_corner_tr", "frame_corner_bl", "frame_corner_br"]:
		var ctex = UIThemeManager.get_themed(corner)
		if ctex:
			var cr = TextureRect.new()
			cr.texture = ctex
			cr.size = Vector2(32, 32)
			cr.mouse_filter = Control.MOUSE_FILTER_IGNORE
			match corner:
				"frame_corner_tl": cr.position = Vector2(0, 0)
				"frame_corner_tr": cr.position = Vector2(1888, 0)
				"frame_corner_bl": cr.position = Vector2(0, 36)
				"frame_corner_br": cr.position = Vector2(1888, 36)
			add_child(cr)
			_icon_nodes.append(cr)

func _add_label_bg(target: Control, tex_name: String, bg_size: Vector2):
	var tex = UIThemeManager.get_themed(tex_name)
	if tex == null:
		return
	var tr = TextureRect.new()
	tr.texture = tex
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.size = bg_size
	tr.position = target.position
	tr.z_index = -1
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(tr)
	_label_bg_nodes.append(tr)

func _add_themed_icon(target: Control, tex_name: String, offset: Vector2, sz: Vector2):
	var tex = UIThemeManager.get_themed(tex_name)
	if tex == null:
		return
	var tr = TextureRect.new()
	tr.texture = tex
	tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tr.size = sz
	tr.position = Vector2(target.position.x + offset.x, target.position.y + offset.y)
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(tr)
	_icon_nodes.append(tr)

func _rebuild_themed_visuals():
	# 清理旧节点
	for n in _label_bg_nodes + _icon_nodes:
		if is_instance_valid(n):
			n.queue_free()
	_label_bg_nodes.clear()
	_icon_nodes.clear()
	if _hud_bar_bg and is_instance_valid(_hud_bar_bg):
		_hud_bar_bg.queue_free()
		_hud_bar_bg = null
	_build_themed_visuals()

func _create_reset_button():
	pass  # Reset button moved to BombSelector

func _create_runtime_labels():
	_intel_label = Label.new()
	_intel_label.position = Vector2(368, 12)
	_intel_label.size = Vector2(170, 42)
	add_child(_intel_label)

	_challenge_label = Label.new()
	_challenge_label.position = Vector2(620, 16)
	_challenge_label.size = Vector2(560, 38)
	_challenge_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_challenge_label)

	_intent_label = Label.new()
	_intent_label.position = Vector2(1200, 16)
	_intent_label.size = Vector2(260, 38)
	_intent_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(_intent_label)

func _apply_theme():
	var tm = UIThemeManager
	floor_label.add_theme_font_size_override("font_size", 24)
	floor_label.add_theme_color_override("font_color", tm.color("text_accent"))
	floor_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
	floor_label.add_theme_constant_override("shadow_offset_x", 2)
	floor_label.add_theme_constant_override("shadow_offset_y", 2)
	timer_label.add_theme_font_size_override("font_size", 28)
	timer_label.add_theme_color_override("font_color", tm.color("text_primary"))
	timer_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
	timer_label.add_theme_constant_override("shadow_offset_x", 2)
	timer_label.add_theme_constant_override("shadow_offset_y", 2)
	clicks_label.add_theme_font_size_override("font_size", 20)
	clicks_label.add_theme_color_override("font_color", tm.color("text_secondary"))
	clicks_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
	clicks_label.add_theme_constant_override("shadow_offset_x", 1)
	clicks_label.add_theme_constant_override("shadow_offset_y", 1)
	if _intel_label:
		_intel_label.add_theme_font_size_override("font_size", 20)
		_intel_label.add_theme_color_override("font_color", tm.color("text_accent"))
		_intel_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
		_intel_label.add_theme_constant_override("shadow_offset_x", 1)
		_intel_label.add_theme_constant_override("shadow_offset_y", 1)
	if _challenge_label:
		_challenge_label.add_theme_font_size_override("font_size", 15)
		_challenge_label.add_theme_color_override("font_color", tm.color("text_secondary"))
		_challenge_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
		_challenge_label.add_theme_constant_override("shadow_offset_x", 1)
		_challenge_label.add_theme_constant_override("shadow_offset_y", 1)
	if _intent_label:
		_intent_label.add_theme_font_size_override("font_size", 16)
		_intent_label.add_theme_color_override("font_color", tm.color("text_danger"))
		_intent_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
		_intent_label.add_theme_constant_override("shadow_offset_x", 1)
		_intent_label.add_theme_constant_override("shadow_offset_y", 1)
	player_hp_label.add_theme_font_size_override("font_size", 22)
	player_hp_label.add_theme_color_override("font_color", tm.color("player_hp_text"))
	player_hp_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
	player_hp_label.add_theme_constant_override("shadow_offset_x", 2)
	player_hp_label.add_theme_constant_override("shadow_offset_y", 2)
	boss_hp_label.add_theme_font_size_override("font_size", 18)
	boss_hp_label.add_theme_color_override("font_color", tm.color("boss_hp_text"))
	boss_hp_label.add_theme_color_override("font_shadow_color", tm.color("shadow_color"))
	boss_hp_label.add_theme_constant_override("shadow_offset_x", 1)
	boss_hp_label.add_theme_constant_override("shadow_offset_y", 1)
	_style_boss_bar()
	_style_reset_btn()
	_apply_hud_pattern()

func _style_reset_btn():
	if not _reset_btn:
		return
	var tm = UIThemeManager
	var sn = tm.make_themed_stylebox("btn_normal", "btn_normal_bg", "btn_normal_brd")
	_reset_btn.add_theme_stylebox_override("normal", sn)
	var sh = tm.make_themed_stylebox("btn_hover", "btn_hover_bg", "border_strong")
	_reset_btn.add_theme_stylebox_override("hover", sh)
	var sp = tm.make_themed_stylebox("btn_pressed", "btn_hover_bg", "border_strong")
	_reset_btn.add_theme_stylebox_override("pressed", sp)
	_reset_btn.add_theme_color_override("font_color", tm.color("text_primary"))

func _style_boss_bar():
	var tm = UIThemeManager
	var bg_sb = tm.make_themed_stylebox("boss_hp_bg", "boss_bar_bg", "boss_bar_brd")
	boss_hp_bar.add_theme_stylebox_override("background", bg_sb)
	var fill_sb = tm.make_themed_stylebox("boss_hp_fill", "boss_bar_fill", "")
	boss_hp_bar.add_theme_stylebox_override("fill", fill_sb)

var _pattern_divider: TextureRect = null

func _apply_hud_pattern():
	# 添加主题分割线装饰
	if _pattern_divider:
		_pattern_divider.queue_free()
		_pattern_divider = null
	var divider_tex = UIThemeManager.get_pattern("divider_ornate")
	if divider_tex:
		_pattern_divider = TextureRect.new()
		_pattern_divider.texture = divider_tex
		_pattern_divider.position = Vector2(0, 56)
		_pattern_divider.size = Vector2(1920, 8)
		_pattern_divider.stretch_mode = TextureRect.STRETCH_TILE
		_pattern_divider.modulate = Color(1, 1, 1, 0.4)
		_pattern_divider.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_pattern_divider)

func _process(delta):
	floor_label.text     = "🏰 第 %d 层" % GameManager.floor_number
	clicks_label.text    = "👆 探索: %d" % GameManager.current_clicks
	clicks_label.add_theme_color_override(
		"font_color",
		UIThemeManager.color("text_danger") if GameManager.current_clicks <= 1 else UIThemeManager.color("text_secondary")
	)
	if _intel_label:
		_intel_label.text = "🧠 %d  🔁 %d" % [GameManager.intel_points, GameManager.reroll_tokens]
	if _challenge_label:
		var danger_msg = ""
		if BossGrid.has_alive_at_left_edge():
			danger_msg = "  |  危险：Boss已贴近"
		elif GameManager.turn_timer < 5.0 and GameManager.timer_running:
			danger_msg = "  |  危险：回合即将结束"
		_challenge_label.text = "挑战：%s%s" % [GameManager.challenge_modifier, danger_msg]
	if _intent_label:
		var intent = BossGrid.next_attack_intent
		var icon = BossGrid.attack_type_icon(intent)
		var name = BossGrid.attack_type_name(intent)
		_intent_label.text = "预告: %s %s" % [icon, name]
		_intent_label.add_theme_color_override("font_color", _intent_color(intent))

	boss_hp_bar.max_value = max(GameManager.boss_max_hp, 1)
	_display_boss_hp = lerp(_display_boss_hp, float(GameManager.boss_hp), delta * 8.0)
	boss_hp_bar.value = _display_boss_hp
	boss_hp_label.text   = "Boss: %d/%d" % [GameManager.boss_hp, GameManager.boss_max_hp]

	player_hp_label.text = "❤ HP: %d/%d" % [GameManager.player_hp, GameManager.player_max_hp]
	if _prev_player_hp >= 0 and GameManager.player_hp < _prev_player_hp:
		_flash_hp_label()
	_prev_player_hp = GameManager.player_hp

	var t = GameManager.turn_timer
	timer_label.text = "⏱ %.0f" % t
	var boss_close = BossGrid.has_alive_at_left_edge()
	var warn = (t < 10.0 or boss_close) and GameManager.timer_running
	if boss_close:
		# Boss在伤害位置：红色脉冲
		var pulse = 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.008)
		timer_label.add_theme_color_override("font_color", Color(1.0, pulse * 0.3, 0.0))
	else:
		timer_label.add_theme_color_override("font_color",
			UIThemeManager.color("text_danger") if warn else UIThemeManager.color("text_primary"))

	# 倒计时紧迫：最后5秒timer缩放脉冲
	if warn and t < 5.0 and GameManager.timer_running:
		var beat = 1.0 + 0.08 * abs(sin(Time.get_ticks_msec() * 0.012))
		timer_label.scale = Vector2(beat, beat)
		if _intent_label:
			_intent_label.text = "%s  ·  即将行动" % _intent_label.text
	else:
		timer_label.scale = Vector2.ONE

	var t_int = int(t)
	if warn and t_int != _last_timer_int:
		_last_timer_int = t_int
		AudioManager.play_sfx("timer_warn")

	# 低HP红色边缘渐变（血量<=30%时）
	var hp_ratio = float(GameManager.player_hp) / max(GameManager.player_max_hp, 1)
	if hp_ratio <= 0.3 and GameManager.player_hp > 0:
		var hp_pulse = 1.0 + 0.06 * abs(sin(Time.get_ticks_msec() * 0.01))
		player_hp_label.scale = Vector2(hp_pulse, hp_pulse)
	else:
		player_hp_label.scale = Vector2.ONE
	if hp_ratio <= 0.3 and GameManager.player_hp > 0:
		var intensity = (1.0 - hp_ratio / 0.3) * 0.15
		var flash = intensity * (0.7 + 0.3 * abs(sin(Time.get_ticks_msec() * 0.004)))
		_vignette_alpha = lerp(_vignette_alpha, flash, min(1.0, delta * 8.0))
		_vignette.color = Color(0.8, 0.0, 0.0, _vignette_alpha)
	else:
		_vignette_alpha = lerp(_vignette_alpha, 0.0, min(1.0, delta * 8.0))
		_vignette.color = Color(0.8, 0.0, 0.0, _vignette_alpha)

func _intent_color(intent: int) -> Color:
	match intent:
		BossGrid.AttackType.NORMAL:
			return UIThemeManager.color("text_secondary")
		BossGrid.AttackType.STRAFE:
			return Color(0.70, 0.85, 1.0)
		BossGrid.AttackType.BURROW:
			return Color(0.95, 0.75, 0.35)
		BossGrid.AttackType.SLAM, BossGrid.AttackType.CHARGE, BossGrid.AttackType.WIDE_SWIPE, BossGrid.AttackType.BOMBARD:
			return UIThemeManager.color("text_danger")
		_:
			return UIThemeManager.color("text_primary")

func _flash_hp_label():
	var tween = create_tween()
	tween.tween_property(player_hp_label, "modulate", Color(2.0, 0.3, 0.3), 0.08)
	tween.tween_property(player_hp_label, "modulate", Color.WHITE, 0.4)
