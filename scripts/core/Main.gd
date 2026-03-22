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
	await get_tree().create_timer(0.4).timeout
	if UpgradeManager.is_boss_frozen():
		UpgradeManager.consume_freeze_boss()
	else:
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
	GameManager.timer_running = false
	# 禁用所有游戏交互
	placement_view.process_mode = Node.PROCESS_MODE_DISABLED
	mine_view.process_mode = Node.PROCESS_MODE_DISABLED
	bomb_selector.process_mode = Node.PROCESS_MODE_DISABLED
	_screen_shake(15.0, 0.5)
	_show_game_over_screen()

func _show_game_over_screen():
	# CanvasLayer 保证覆盖在最上层，不受 screen shake 影响
	var canvas = CanvasLayer.new()
	canvas.layer = 100
	add_child(canvas)

	# 全屏遮罩
	var overlay = ColorRect.new()
	overlay.color = Color(0, 0, 0, 0)
	overlay.size = Vector2(1920, 1080)
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(overlay)

	# ── 标题 ──
	var title = Label.new()
	title.text = "游 戏 结 束"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.position = Vector2(0, 260)
	title.size = Vector2(1920, 120)
	title.add_theme_font_size_override("font_size", 96)
	title.add_theme_color_override("font_color", Color(0.95, 0.18, 0.08))
	title.add_theme_color_override("font_shadow_color", Color(0.4, 0.02, 0.0, 0.9))
	title.add_theme_constant_override("shadow_offset_x", 4)
	title.add_theme_constant_override("shadow_offset_y", 4)
	title.modulate = Color(1, 1, 1, 0)
	overlay.add_child(title)

	# ── 分隔线 ──
	var sep = Label.new()
	sep.text = "━━━━━━━━━━━━━━━━━━━━"
	sep.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sep.position = Vector2(0, 450)
	sep.size = Vector2(1920, 40)
	sep.add_theme_font_size_override("font_size", 24)
	sep.add_theme_color_override("font_color", Color(0.6, 0.25, 0.1, 0.6))
	sep.modulate = Color(1, 1, 1, 0)
	overlay.add_child(sep)

	# ── 层数信息 ──
	var info = Label.new()
	info.text = "你倒在了第 %d 层" % GameManager.floor_number
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	info.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	info.position = Vector2(0, 540)
	info.size = Vector2(1920, 60)
	info.add_theme_font_size_override("font_size", 42)
	info.add_theme_color_override("font_color", Color(0.9, 0.8, 0.55))
	info.add_theme_color_override("font_shadow_color", Color(0.3, 0.2, 0.05, 0.7))
	info.add_theme_constant_override("shadow_offset_x", 2)
	info.add_theme_constant_override("shadow_offset_y", 2)
	info.modulate = Color(1, 1, 1, 0)
	overlay.add_child(info)

	# ── 重启提示 ──
	var hint = Label.new()
	hint.text = "按 F5 重新开始"
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	hint.position = Vector2(0, 620)
	hint.size = Vector2(1920, 50)
	hint.add_theme_font_size_override("font_size", 28)
	hint.add_theme_color_override("font_color", Color(0.55, 0.5, 0.4))
	hint.modulate = Color(1, 1, 1, 0)
	overlay.add_child(hint)

	# ═══ 动画序列 ═══
	# 1. 遮罩渐暗
	var tw_bg = create_tween()
	tw_bg.tween_property(overlay, "color", Color(0.02, 0.01, 0.0, 0.9), 1.2)

	# 2. 标题从上方滑入（带回弹）
	var tw_t1 = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw_t1.tween_interval(0.3)
	tw_t1.tween_property(title, "position:y", 340.0, 0.7)
	var tw_t2 = create_tween().set_ease(Tween.EASE_OUT)
	tw_t2.tween_interval(0.3)
	tw_t2.tween_property(title, "modulate:a", 1.0, 0.5)

	# 3. 分隔线淡入
	var tw_sep = create_tween()
	tw_sep.tween_interval(0.8)
	tw_sep.tween_property(sep, "modulate:a", 1.0, 0.4)

	# 4. 层数信息从下方滑入
	var tw_i1 = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw_i1.tween_interval(1.2)
	tw_i1.tween_property(info, "position:y", 500.0, 0.5)
	var tw_i2 = create_tween().set_ease(Tween.EASE_OUT)
	tw_i2.tween_interval(1.2)
	tw_i2.tween_property(info, "modulate:a", 1.0, 0.5)

	# 5. 重启提示淡入 + 呼吸闪烁
	var tw_h = create_tween()
	tw_h.tween_interval(2.0)
	tw_h.tween_property(hint, "modulate:a", 1.0, 0.5)
	tw_h.tween_callback(func():
		var pulse = create_tween().set_loops()
		pulse.tween_property(hint, "modulate:a", 0.3, 1.2)
		pulse.tween_property(hint, "modulate:a", 1.0, 1.2)
	)

# 升级选完后继续（由 UpgradePanel 回调）
func on_combat_upgrade_chosen():
	combat_upgrade_panel.visible = false
	GameManager.timer_running = true  # 恢复倒计时

func on_permanent_upgrade_chosen():
	permanent_upgrade_panel.visible = false
	GameManager.next_floor()
	_start_new_floor()
