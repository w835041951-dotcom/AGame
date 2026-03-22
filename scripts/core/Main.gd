## 主场景控制器

extends Node2D

@onready var grid_view = $GridView
@onready var hud = $HUD
@onready var upgrade_panel = $UpgradePanel

func _ready():
	GameManager.boss_defeated.connect(_show_upgrade_panel)
	GameManager.game_over.connect(_show_game_over)
	GameManager.turn_ended.connect(_on_turn_ended)
	upgrade_panel.visible = false
	GameManager.start_turn()

func _on_turn_ended():
	# boss 已死时跳过，等升级界面处理
	if GameManager.boss_hp <= 0:
		return
	await get_tree().create_timer(0.5).timeout
	GameManager.take_damage(5)
	await get_tree().create_timer(0.3).timeout
	GameManager.start_turn()

func _show_upgrade_panel():
	upgrade_panel.visible = true
	upgrade_panel.show_choices(UpgradeManager.get_random_choices(3))

func _show_game_over():
	# TODO: 显示游戏结束界面
	print("Game Over!")
