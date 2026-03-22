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
	# 地牢风格 HUD
	floor_label.add_theme_font_size_override("font_size", 18)
	floor_label.add_theme_color_override("font_color", Color(0.95, 0.82, 0.45))
	timer_label.add_theme_font_size_override("font_size", 22)
	timer_label.add_theme_color_override("font_color", Color(0.92, 0.90, 0.82))
	clicks_label.add_theme_font_size_override("font_size", 16)
	clicks_label.add_theme_color_override("font_color", Color(0.72, 0.68, 0.58))
	player_hp_label.add_theme_font_size_override("font_size", 17)
	player_hp_label.add_theme_color_override("font_color", Color(0.35, 0.85, 0.35))
	boss_hp_label.add_theme_font_size_override("font_size", 15)
	boss_hp_label.add_theme_color_override("font_color", Color(0.90, 0.85, 0.75))
	_style_boss_bar()

func _style_boss_bar():
	var bg = StyleBoxFlat.new()
	bg.bg_color = Color(0.10, 0.08, 0.06)
	bg.border_color = Color(0.40, 0.32, 0.22)
	bg.set_border_width_all(2)
	bg.set_corner_radius_all(3)
	boss_hp_bar.add_theme_stylebox_override("background", bg)
	var fill = StyleBoxFlat.new()
	fill.bg_color = Color(0.72, 0.15, 0.10)
	fill.set_corner_radius_all(2)
	boss_hp_bar.add_theme_stylebox_override("fill", fill)

func _process(delta):
	floor_label.text     = "第 %d 层" % GameManager.floor_number
	clicks_label.text    = "扫雷: %d" % GameManager.current_clicks

	# Boss HP 平滑过渡
	boss_hp_bar.max_value = max(GameManager.boss_max_hp, 1)
	_display_boss_hp = lerp(_display_boss_hp, float(GameManager.boss_hp), delta * 8.0)
	boss_hp_bar.value = _display_boss_hp
	boss_hp_label.text   = "Boss: %d/%d" % [GameManager.boss_hp, GameManager.boss_max_hp]

	# 玩家 HP 受伤闪红
	player_hp_label.text = "HP: %d/%d" % [GameManager.player_hp, GameManager.player_max_hp]
	if _prev_player_hp >= 0 and GameManager.player_hp < _prev_player_hp:
		_flash_hp_label()
	_prev_player_hp = GameManager.player_hp

	var t = GameManager.turn_timer
	timer_label.text = "⏱ %.0f" % t
	var warn = t < 10.0 and GameManager.timer_running
	timer_label.add_theme_color_override("font_color",
		Color(1.0, 0.25, 0.15) if warn else Color(0.92, 0.90, 0.82))

	# 倒计时最后10秒每秒beep
	var t_int = int(t)
	if warn and t_int != _last_timer_int:
		_last_timer_int = t_int
		AudioManager.play_sfx("timer_warn")

func _flash_hp_label():
	var tween = create_tween()
	tween.tween_property(player_hp_label, "modulate", Color(2.0, 0.3, 0.3), 0.08)
	tween.tween_property(player_hp_label, "modulate", Color.WHITE, 0.4)
