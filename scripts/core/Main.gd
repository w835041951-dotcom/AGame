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
	# 显示关卡标题
	await _show_level_intro()
	BossGrid.setup()
	_layout_views()
	GameManager.init_boss_hp()
	UpgradeManager.clear_combat_effects()
	BombPlacer.reset()
	GameManager.start_turn()

func _layout_views():
	# 根据当前层的棋盘大小动态计算布局
	var floor_n = GameManager.floor_number
	var cs = LevelData.get_cell_size(floor_n)
	var p_cols = BossGrid.placement_cols
	var p_rows = BossGrid.placement_rows
	var m_cols = GridManager.cols if GridManager.cols > 1 else LevelData.get_mine_cols(floor_n)
	var m_rows = LevelData.get_mine_rows(floor_n)
	var p_width = p_cols * cs
	var p_height = p_rows * cs
	var m_width = m_cols * cs
	var m_height = m_rows * cs

	# 放置区居中
	var hud_h = 68
	var sel_h = 64
	var gap = 4
	var total_h = p_height + sel_h + m_height + gap * 2
	var start_y = hud_h + max(0, (1080 - hud_h - total_h) / 2)

	placement_view.position = Vector2((1920 - p_width) / 2, start_y)
	bomb_selector.position.y = start_y + p_height + gap
	bomb_selector.size.x = 1920
	mine_view.position = Vector2((1920 - m_width) / 2, start_y + p_height + sel_h + gap * 2)

func _show_level_intro():
	var floor_n = GameManager.floor_number
	var level_name = LevelData.get_level_name(floor_n)
	var boss_name = LevelData.get_boss_name(floor_n)
	var subtitle = LevelData.get_level_subtitle(floor_n)
	var level_color = LevelData.get_level_color(floor_n)
	var cycle = LevelData.get_cycle(floor_n)

	var canvas = CanvasLayer.new()
	canvas.layer = 90
	add_child(canvas)

	# 暗背景
	var bg = ColorRect.new()
	bg.color = Color(0.02, 0.01, 0.0, 0.85)
	bg.size = Vector2(1920, 1080)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(bg)

	# 层数
	var floor_label = Label.new()
	floor_label.text = "第 %d 层" % floor_n
	floor_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	floor_label.position = Vector2(0, 340)
	floor_label.size = Vector2(1920, 50)
	floor_label.add_theme_font_size_override("font_size", 32)
	floor_label.add_theme_color_override("font_color", Color(0.65, 0.6, 0.5))
	floor_label.modulate = Color(1, 1, 1, 0)
	bg.add_child(floor_label)

	# 关卡名
	var title = Label.new()
	var cycle_mark = "" if cycle == 0 else " · %d周目" % (cycle + 1)
	title.text = level_name + cycle_mark
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.position = Vector2(0, 380)
	title.size = Vector2(1920, 100)
	title.add_theme_font_size_override("font_size", 80)
	title.add_theme_color_override("font_color", level_color)
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	title.add_theme_constant_override("shadow_offset_x", 3)
	title.add_theme_constant_override("shadow_offset_y", 3)
	title.modulate = Color(1, 1, 1, 0)
	bg.add_child(title)

	# Boss名字
	var boss_label = Label.new()
	boss_label.text = "Boss: " + boss_name
	boss_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_label.position = Vector2(0, 490)
	boss_label.size = Vector2(1920, 50)
	boss_label.add_theme_font_size_override("font_size", 34)
	boss_label.add_theme_color_override("font_color", Color(0.85, 0.35, 0.25))
	boss_label.modulate = Color(1, 1, 1, 0)
	bg.add_child(boss_label)

	# 副标题
	var sub = Label.new()
	sub.text = subtitle
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.position = Vector2(0, 550)
	sub.size = Vector2(1920, 50)
	sub.add_theme_font_size_override("font_size", 26)
	sub.add_theme_color_override("font_color", Color(0.55, 0.5, 0.42))
	sub.modulate = Color(1, 1, 1, 0)
	bg.add_child(sub)

	# ── 动画 ──
	var tw = create_tween()
	tw.tween_property(floor_label, "modulate:a", 1.0, 0.3)
	tw.tween_property(title, "modulate:a", 1.0, 0.4)
	tw.tween_property(boss_label, "modulate:a", 1.0, 0.3)
	tw.tween_property(sub, "modulate:a", 1.0, 0.4)
	tw.tween_interval(1.2)
	tw.tween_property(bg, "modulate:a", 0.0, 0.5)
	tw.tween_callback(canvas.queue_free)

	# 等动画结束
	await tw.finished

func _on_turn_ended():
	if BombPlacer.phase == BombPlacer.Phase.PLACING:
		await BombPlacer.detonate()
	# 等待临时升级面板（如有）关闭后再继续
	await _wait_for_combat_upgrade()
	_after_detonation()

func _wait_for_combat_upgrade():
	while combat_upgrade_panel.visible:
		await get_tree().process_frame

func _after_detonation():
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
	var atk = LevelData.get_boss_attack(GameManager.floor_number)
	GameManager.take_damage(atk)
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
	# 先等爆炸动画看完
	await get_tree().create_timer(0.8).timeout
	# 结算正确标记回血
	var correct = mine_view.count_correct_marks()
	if correct > 0:
		await _show_mark_heal_animation(correct)
	# 再显示永久升级面板
	await get_tree().create_timer(0.3).timeout
	permanent_upgrade_panel.show_choices(UpgradeManager.get_permanent_choices(3))
	_animate_panel_in(permanent_upgrade_panel)

func _show_mark_heal_animation(count: int):
	AudioManager.play_sfx("upgrade_pick")
	var canvas = CanvasLayer.new()
	canvas.layer = 80
	add_child(canvas)
	for i in range(count):
		GameManager.heal(1)
		var lbl = Label.new()
		lbl.text = "+1 HP"
		lbl.add_theme_font_size_override("font_size", 36)
		lbl.add_theme_color_override("font_color", Color(0.35, 0.95, 0.45))
		lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
		lbl.add_theme_constant_override("shadow_offset_x", 2)
		lbl.add_theme_constant_override("shadow_offset_y", 2)
		lbl.position = Vector2(randf_range(700, 1100), randf_range(420, 580))
		lbl.modulate = Color(1, 1, 1, 0)
		canvas.add_child(lbl)
		var tw = create_tween()
		tw.tween_property(lbl, "modulate:a", 1.0, 0.15)
		tw.tween_property(lbl, "position:y", lbl.position.y - 60, 0.6).set_trans(Tween.TRANS_CUBIC)
		tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.3).set_delay(0.35)
		if i < count - 1:
			AudioManager.play_sfx("mine_reveal")
			await get_tree().create_timer(0.18).timeout
	await get_tree().create_timer(0.55).timeout
	canvas.queue_free()

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
	# 回合流程由 _wait_for_combat_upgrade() 继续，无需手动恢复计时器

func on_permanent_upgrade_chosen():
	permanent_upgrade_panel.visible = false
	GameManager.next_floor()
	_start_new_floor()
