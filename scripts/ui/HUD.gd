## HUD — 顶部状态栏：点击次数 + HP

extends Control

@onready var clicks_label: Label = $ClicksLabel
@onready var player_hp_label: Label = $PlayerHPLabel
@onready var boss_hp_bar: ProgressBar = $BossHPBar
@onready var boss_hp_label: Label = $BossHPLabel
@onready var floor_label: Label = $FloorLabel
@onready var damage_label: Label = $DamageLabel

func _ready():
	GameManager.turn_started.connect(_on_turn_started)
	GameManager.boss_defeated.connect(_on_boss_defeated)
	GameManager.game_over.connect(_on_game_over)
	BombEffect.attack_dealt.connect(_on_damage_dealt)
	_refresh()

func _process(_delta):
	clicks_label.text = "点击: %d / %d" % [GameManager.current_clicks, GameManager.max_clicks]
	player_hp_label.text = "HP: %d" % GameManager.player_hp
	boss_hp_bar.max_value = GameManager.boss_max_hp
	boss_hp_bar.value = GameManager.boss_hp
	boss_hp_label.text = "Boss HP: %d / %d" % [GameManager.boss_hp, GameManager.boss_max_hp]
	floor_label.text = "第 %d 层" % GameManager.floor_number

func _refresh():
	damage_label.visible = false

func _on_turn_started(_clicks: int):
	pass

func _on_damage_dealt(damage: int):
	damage_label.text = "-%d" % damage
	damage_label.visible = true
	var tween = create_tween()
	tween.tween_property(damage_label, "modulate:a", 0.0, 0.8)
	tween.tween_callback(func(): damage_label.visible = false; damage_label.modulate.a = 1.0)

func _on_boss_defeated():
	# 触发升级界面（由Main场景处理）
	pass

func _on_game_over():
	pass
