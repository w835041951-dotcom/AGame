## 主场景控制器

extends Node2D

@onready var placement_view = $PlacementView
@onready var mine_view = $MineView
@onready var hud = $HUD
@onready var bomb_selector = $BombSelector
@onready var combat_upgrade_panel = $CombatUpgradePanel
@onready var permanent_upgrade_panel = $PermanentUpgradePanel

func _ready():
	GameManager.boss_defeated.connect(_on_boss_defeated)
	GameManager.game_over.connect(_on_game_over)
	GameManager.turn_ended.connect(_on_turn_ended)
	GameManager.combat_upgrade_triggered.connect(_on_combat_upgrade)
	BossGrid.core_destroyed.connect(_on_combat_upgrade)
	BossGrid.boss_attacked.connect(_on_boss_attacked)

	combat_upgrade_panel.visible = false
	permanent_upgrade_panel.visible = false

	_start_new_floor()

func _start_new_floor():
	BossGrid.setup()
	GameManager.init_boss_hp()
	UpgradeManager.clear_combat_effects()
	BombPlacer.reset()
	GameManager.start_turn()

func _on_turn_ended():
	var total_damage := 0
	if BombPlacer.phase == BombPlacer.Phase.PLACING:
		total_damage = await BombPlacer.detonate()
	_after_detonation(total_damage)

func _after_detonation(_total_damage: int):
	if GameManager.boss_hp <= 0:
		return
	# Boss向左移动一格（到左边界时自动触发boss_attacked扣血）
	await get_tree().create_timer(0.4).timeout
	BossGrid.move_left()
	await get_tree().create_timer(0.2).timeout
	if GameManager.player_hp <= 0:
		return
	BombPlacer.reset()
	GameManager.start_turn()

func _on_boss_attacked():
	GameManager.take_damage(5)
	_screen_shake()

func _screen_shake(intensity: float = 10.0, duration: float = 0.3):
	var tween = create_tween()
	var steps = 6
	var step_dur = duration / (steps + 1)
	for i in range(steps):
		var offset = Vector2(randf_range(-intensity, intensity), randf_range(-intensity, intensity))
		tween.tween_property(self, "position", offset, step_dur)
		intensity *= 0.7
	tween.tween_property(self, "position", Vector2.ZERO, step_dur)

func _on_combat_upgrade():
	# 暂停，显示临时升级
	combat_upgrade_panel.show_choices(UpgradeManager.get_combat_choices(3))
	_animate_panel_in(combat_upgrade_panel)

func _on_boss_defeated():
	await get_tree().create_timer(0.5).timeout
	permanent_upgrade_panel.show_choices(UpgradeManager.get_permanent_choices(3))
	_animate_panel_in(permanent_upgrade_panel)

func _animate_panel_in(panel: Control):
	panel.modulate = Color(1, 1, 1, 0)
	var tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tween.tween_property(panel, "modulate:a", 1.0, 0.3)

func _on_game_over():
	# TODO: 显示游戏结束画面
	print("GAME OVER — floor %d" % GameManager.floor_number)

# 升级选完后继续（由 UpgradePanel 回调）
func on_combat_upgrade_chosen():
	combat_upgrade_panel.visible = false
	GameManager.timer_running = true  # 恢复倒计时

func on_permanent_upgrade_chosen():
	permanent_upgrade_panel.visible = false
	GameManager.next_floor()
	_start_new_floor()
