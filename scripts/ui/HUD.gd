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
	floor_label.add_theme_font_size_override("font_size", 17)
	timer_label.add_theme_font_size_override("font_size", 20)
	clicks_label.add_theme_font_size_override("font_size", 16)
	player_hp_label.add_theme_font_size_override("font_size", 16)
	player_hp_label.add_theme_color_override("font_color", Color(0.4, 1.0, 0.4))
	boss_hp_label.add_theme_font_size_override("font_size", 15)

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
		Color(1.0, 0.25, 0.25) if warn else Color(1.0, 1.0, 1.0))

	# 倒计时最后10秒每秒beep
	var t_int = int(t)
	if warn and t_int != _last_timer_int:
		_last_timer_int = t_int
		AudioManager.play_sfx("timer_warn")

func _flash_hp_label():
	var tween = create_tween()
	tween.tween_property(player_hp_label, "modulate", Color(2.0, 0.3, 0.3), 0.08)
	tween.tween_property(player_hp_label, "modulate", Color.WHITE, 0.4)
