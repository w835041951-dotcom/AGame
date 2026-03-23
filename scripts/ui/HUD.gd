## HUD - 顶部状态栏

extends Control

@onready var timer_label: Label = $TimerLabel
@onready var player_hp_label: Label = $PlayerHPLabel
@onready var boss_hp_bar: ProgressBar = $BossHPBar
@onready var boss_hp_label: Label = $BossHPLabel
@onready var floor_label: Label = $FloorLabel
@onready var clicks_label: Label = $ClicksLabel

var _last_timer_int: int = -1
var _display_boss_hp: float = 0.0
var _prev_player_hp: int = -1

func _ready():
	_apply_theme()
	UIThemeManager.theme_changed.connect(func(_n): _apply_theme())

func _apply_theme():
	var tm = UIThemeManager
	floor_label.add_theme_font_size_override("font_size", 20)
	floor_label.add_theme_color_override("font_color", tm.get("text_accent"))
	floor_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	floor_label.add_theme_constant_override("shadow_offset_x", 1)
	floor_label.add_theme_constant_override("shadow_offset_y", 1)
	timer_label.add_theme_font_size_override("font_size", 24)
	timer_label.add_theme_color_override("font_color", tm.get("text_primary"))
	timer_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	timer_label.add_theme_constant_override("shadow_offset_x", 1)
	timer_label.add_theme_constant_override("shadow_offset_y", 1)
	clicks_label.add_theme_font_size_override("font_size", 17)
	clicks_label.add_theme_color_override("font_color", tm.get("text_secondary"))
	player_hp_label.add_theme_font_size_override("font_size", 19)
	player_hp_label.add_theme_color_override("font_color", tm.get("player_hp_text"))
	player_hp_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.5))
	player_hp_label.add_theme_constant_override("shadow_offset_x", 1)
	player_hp_label.add_theme_constant_override("shadow_offset_y", 1)
	boss_hp_label.add_theme_font_size_override("font_size", 16)
	boss_hp_label.add_theme_color_override("font_color", tm.get("boss_hp_text"))
	_style_boss_bar()

func _style_boss_bar():
	var tm = UIThemeManager
	var bg = StyleBoxFlat.new()
	bg.bg_color = tm.get("boss_bar_bg")
	bg.border_color = tm.get("boss_bar_brd")
	bg.set_border_width_all(2)
	bg.set_corner_radius_all(tm.get("corner_radius"))
	boss_hp_bar.add_theme_stylebox_override("background", bg)
	var fill = StyleBoxFlat.new()
	fill.bg_color = tm.get("boss_bar_fill")
	fill.set_corner_radius_all(tm.get("corner_radius"))
	boss_hp_bar.add_theme_stylebox_override("fill", fill)

func _process(delta):
	floor_label.text     = "🏰 第 %d 层" % GameManager.floor_number
	clicks_label.text    = "👆 探索: %d" % GameManager.current_clicks

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
	var warn = t < 10.0 and GameManager.timer_running
	timer_label.add_theme_color_override("font_color",
		UIThemeManager.get("text_danger") if warn else UIThemeManager.get("text_primary"))

	var t_int = int(t)
	if warn and t_int != _last_timer_int:
		_last_timer_int = t_int
		AudioManager.play_sfx("timer_warn")

func _flash_hp_label():
	var tween = create_tween()
	tween.tween_property(player_hp_label, "modulate", Color(2.0, 0.3, 0.3), 0.08)
	tween.tween_property(player_hp_label, "modulate", Color.WHITE, 0.4)
