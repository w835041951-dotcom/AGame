## HUD - 顶部状态栏

extends Control

@onready var timer_label: Label = $TimerLabel
@onready var player_hp_label: Label = $PlayerHPLabel
@onready var boss_hp_bar: ProgressBar = $BossHPBar
@onready var boss_hp_label: Label = $BossHPLabel
@onready var floor_label: Label = $FloorLabel
@onready var clicks_label: Label = $ClicksLabel

var _last_timer_int: int = -1

func _process(_delta):
	floor_label.text     = "第 %d 层" % GameManager.floor_number
	player_hp_label.text = "HP: %d/%d" % [GameManager.player_hp, GameManager.player_max_hp]
	clicks_label.text    = "扫雷: %d" % GameManager.current_clicks
	boss_hp_bar.max_value = max(GameManager.boss_max_hp, 1)
	boss_hp_bar.value    = GameManager.boss_hp
	boss_hp_label.text   = "Boss: %d/%d" % [GameManager.boss_hp, GameManager.boss_max_hp]

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
