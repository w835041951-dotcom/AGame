## 主场景控制器

extends Node2D

@onready var placement_view = $PlacementView
@onready var mine_view = $MineView
@onready var hud = $HUD
@onready var bomb_selector = $BombSelector
@onready var combat_upgrade_panel = $CombatUpgradePanel
@onready var permanent_upgrade_panel = $PermanentUpgradePanel
@onready var background_rect = $Background

const DEFAULT_BACKGROUND_PATH = "res://assets/sprites/ui/background.png"
const PauseMenuScript = preload("res://scripts/ui/PauseMenu.gd")

var _background_cache: Dictionary = {}
var _pause_menu: Node = null

func _ready():
	GameManager.boss_defeated.connect(_on_boss_defeated)
	GameManager.game_over.connect(_on_game_over)
	GameManager.turn_ended.connect(_on_turn_ended)
	GameManager.combat_upgrade_triggered.connect(_on_combat_upgrade)
	BossGrid.core_destroyed.connect(_on_combat_upgrade)
	BossGrid.boss_attacked.connect(_on_boss_attacked)
	BossGrid.ranged_attack.connect(_on_boss_ranged_attack)
	BossGrid.phase_changed.connect(_on_boss_phase_changed)
	ExplosionCalc.damage_numbers.connect(_on_damage_numbers)
	ExplosionCalc.critical_hit.connect(_on_critical_hit)
	ExplosionCalc.chain_triggered.connect(_on_chain_triggered)
	MinionGrid.all_minions_cleared.connect(_on_all_minions_cleared)
	hud.reset_board_pressed.connect(_on_reset_board)
	bomb_selector.reset_board_pressed.connect(_on_reset_board)
	GameManager.lucky_find.connect(_on_lucky_find)
	GameManager.streak_bonus.connect(_on_streak_bonus)

	combat_upgrade_panel.visible = false
	permanent_upgrade_panel.visible = false

	# 暂停菜单
	_pause_menu = CanvasLayer.new()
	_pause_menu.set_script(PauseMenuScript)
	add_child(_pause_menu)
	_pause_menu.restart_requested.connect(_on_restart)
	_pause_menu.quit_to_title_requested.connect(_on_quit_to_title)

	# 成就通知
	AchievementManager.achievement_unlocked.connect(_on_achievement_unlocked)

	# 给玩家初始炸弹，第一回合有足够弹药
	GameManager.add_bomb("pierce_h")
	GameManager.add_bomb("pierce_h")
	GameManager.add_bomb("pierce_v")
	GameManager.add_bomb("pierce_v")

	# 新手引导
	if GameManager.floor_number == 1:
		TutorialManager.try_show("welcome", self)

	_start_new_floor()

func _start_new_floor():
	_apply_floor_background()
	# 显示剧情卡片（如有）
	await _show_story_card_if_needed()
	# 显示关卡标题
	await _show_level_intro()
	MinionGrid.setup()
	BossGrid.setup()
	_layout_views()
	GameManager.init_boss_hp()
	UpgradeManager.clear_combat_effects()
	BombPlacer.reset()
	GameManager.start_turn()

var _section_labels: Array = []  # 区域标签引用

func _layout_views():
	# 清除旧区域标签
	for lbl in _section_labels:
		if is_instance_valid(lbl):
			lbl.queue_free()
	_section_labels.clear()

	# 根据当前层的棋盘大小动态计算布局
	var floor_n = GameManager.floor_number
	var cs = LevelData.get_cell_size(floor_n)
	var p_cols = BossGrid.placement_cols
	var p_rows = BossGrid.placement_rows
	var m_cols = LevelData.get_mine_cols(floor_n)
	var m_rows = LevelData.get_mine_rows(floor_n)
	var p_width = p_cols * cs
	var p_height = p_rows * cs
	var m_width = m_cols * cs
	var m_height = m_rows * cs

	# 两个棋盘取最大宽度，统一居中对齐
	var max_width = max(p_width, m_width)
	var center_x = (1920 - max_width) / 2

	# 放置区居中
	var hud_h = 68
	var sel_h = 64
	var gap = 4
	var label_h = 24
	var total_h = label_h + p_height + sel_h + label_h + m_height + gap * 4
	var start_y = hud_h + max(0, (1080 - hud_h - total_h) / 2)

	# Boss区域标签
	var boss_label = _create_section_label("⚔ Boss 战场", center_x, start_y, max_width)
	_section_labels.append(boss_label)

	placement_view.position = Vector2(center_x + (max_width - p_width) / 2, start_y + label_h + gap)
	bomb_selector.position.y = start_y + label_h + gap + p_height + gap
	bomb_selector.size.x = 1920

	var mine_top = start_y + label_h + gap + p_height + sel_h + gap * 2
	# 探索区域标签
	var mine_label = _create_section_label("🔍 探索区", center_x, mine_top, max_width)
	_section_labels.append(mine_label)
	mine_view.position = Vector2(center_x + (max_width - m_width) / 2, mine_top + label_h + gap)

func _create_section_label(text_str: String, x: float, y: float, width: float) -> Label:
	var lbl = Label.new()
	lbl.text = text_str
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	lbl.position = Vector2(x, y)
	lbl.size = Vector2(width, 24)
	lbl.add_theme_font_size_override("font_size", 14)
	var tint = LevelData.get_level_color(GameManager.floor_number)
	lbl.add_theme_color_override("font_color", tint.lerp(Color(0.78, 0.74, 0.68, 1.0), 0.45))
	add_child(lbl)
	return lbl

func _get_cached_texture(path: String) -> Texture2D:
	if path.is_empty():
		path = DEFAULT_BACKGROUND_PATH
	if _background_cache.has(path):
		return _background_cache[path]
	if not ResourceLoader.exists(path):
		path = DEFAULT_BACKGROUND_PATH
	if not ResourceLoader.exists(path):
		return null
	var texture = load(path) as Texture2D
	if texture != null:
		_background_cache[path] = texture
	return texture

func _apply_floor_background():
	var floor_n = GameManager.floor_number
	var path = LevelData.get_background_texture_path(floor_n)
	var texture = _get_cached_texture(path)
	if texture != null:
		background_rect.texture = texture
		background_rect.modulate = Color(0.82, 0.82, 0.86, 1.0)
	_spawn_ambient_particles(floor_n)

func _show_story_card_if_needed():
	var floor_n = GameManager.floor_number
	if not LevelData.should_show_story_card(floor_n):
		return

	var canvas = CanvasLayer.new()
	canvas.layer = 88
	add_child(canvas)

	var overlay = ColorRect.new()
	overlay.color = Color(0.01, 0.01, 0.02, 0.0)
	overlay.size = Vector2(1920, 1080)
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(overlay)

	var panel = PanelContainer.new()
	panel.position = Vector2(180, 110)
	panel.size = Vector2(1560, 860)
	panel.modulate = Color(1, 1, 1, 0)
	canvas.add_child(panel)

	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = UIThemeManager.color("hud_bg")
	panel_style.border_color = LevelData.get_level_color(floor_n).lerp(Color(1, 1, 1, 1), 0.2)
	panel_style.set_border_width_all(3)
	panel_style.set_corner_radius_all(18)
	panel.add_theme_stylebox_override("panel", panel_style)

	var art = TextureRect.new()
	art.position = Vector2(24, 24)
	art.size = Vector2(960, 812)
	art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	var story_texture = _get_cached_texture(LevelData.get_story_art_path(floor_n))
	if story_texture != null:
		art.texture = story_texture
	panel.add_child(art)

	var title = Label.new()
	title.text = LevelData.get_story_title(floor_n)
	title.position = Vector2(1020, 86)
	title.size = Vector2(470, 80)
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title.add_theme_font_size_override("font_size", 42)
	title.add_theme_color_override("font_color", LevelData.get_level_color(floor_n))
	panel.add_child(title)

	var body = Label.new()
	body.text = LevelData.get_story_text(floor_n)
	body.position = Vector2(1020, 220)
	body.size = Vector2(470, 320)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 26)
	body.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	panel.add_child(body)

	var hint = Label.new()
	hint.text = "战区档案已更新"
	hint.position = Vector2(1020, 720)
	hint.size = Vector2(420, 40)
	hint.add_theme_font_size_override("font_size", 20)
	hint.add_theme_color_override("font_color", (UIThemeManager.color("text_secondary") as Color).darkened(0.2))
	panel.add_child(hint)

	var tw = create_tween()
	tw.tween_property(overlay, "color:a", 0.86, 0.25)
	tw.parallel().tween_property(panel, "modulate:a", 1.0, 0.25)
	tw.tween_interval(1.9)
	tw.tween_property(panel, "modulate:a", 0.0, 0.28)
	tw.parallel().tween_property(overlay, "color:a", 0.0, 0.28)
	tw.tween_callback(canvas.queue_free)
	await tw.finished

func _show_level_intro():
	var floor_n = GameManager.floor_number
	var boss_name = LevelData.get_boss_name(floor_n)
	var level_color = LevelData.get_level_color(floor_n)

	var canvas = CanvasLayer.new()
	canvas.layer = 90
	add_child(canvas)

	var bg = ColorRect.new()
	bg.color = UIThemeManager.color("intro_overlay")
	bg.size = Vector2(1920, 1080)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(bg)

	# 「第 X 层  Boss名」 一行搞定
	var title = Label.new()
	title.text = "第 %d 层 — %s" % [floor_n, boss_name]
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.position = Vector2(0, 440)
	title.size = Vector2(1920, 100)
	title.add_theme_font_size_override("font_size", 64)
	title.add_theme_color_override("font_color", level_color)
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	title.add_theme_constant_override("shadow_offset_x", 3)
	title.add_theme_constant_override("shadow_offset_y", 3)
	title.modulate = Color(1, 1, 1, 0)
	title.pivot_offset = Vector2(960, 50)
	bg.add_child(title)

	var tw = create_tween()
	tw.tween_property(title, "modulate:a", 1.0, 0.3)
	tw.tween_property(title, "scale", Vector2(1.05, 1.05), 0.15).set_trans(Tween.TRANS_BACK)
	tw.tween_property(title, "scale", Vector2.ONE, 0.1)
	tw.tween_interval(0.8)
	tw.tween_property(bg, "modulate:a", 0.0, 0.35)
	tw.tween_callback(canvas.queue_free)
	await tw.finished

func _on_turn_ended():
	if BombPlacer.phase == BombPlacer.Phase.PLACING:
		var dmg = await BombPlacer.detonate()
		# 等爆炸动画播完再显示伤害统计
		await get_tree().create_timer(0.3).timeout
		if dmg > 0:
			_show_damage_summary(dmg)
			await get_tree().create_timer(0.8).timeout  # 让统计弹窗显示一会儿
	# 等待临时升级面板（如有）关闭后再继续
	await _wait_for_combat_upgrade()
	_after_detonation()

func _wait_for_combat_upgrade():
	while combat_upgrade_panel.visible:
		await get_tree().process_frame

func _after_detonation():
	if GameManager.boss_hp <= 0:
		return
	await get_tree().create_timer(0.5).timeout
	# 小怪阶段时Boss不移动
	if not MinionGrid.has_minions():
		if UpgradeManager.is_boss_frozen():
			UpgradeManager.consume_freeze_boss()
		else:
			BossGrid.random_move()
			await get_tree().create_timer(0.6).timeout  # Boss移动/攻击动画时间
	await get_tree().create_timer(0.4).timeout
	if GameManager.player_hp <= 0:
		return
	BombPlacer.reset()
	GameManager.start_turn()

func _on_reset_board():
	# 重置扫雷区并立即进入下一回合
	if BombPlacer.phase != BombPlacer.Phase.PLACING:
		return
	GridManager.reset_for_new_floor()
	GridManager.generate_grid()
	mine_view._build_grid()
	GameManager.end_turn()

func _on_boss_attacked(attack_type: int):
	TutorialManager.try_show("first_boss_attack", self)
	var raw_atk = LevelData.get_boss_attack(GameManager.floor_number)
	var hp_ratio = float(GameManager.boss_hp) / max(GameManager.boss_max_hp, 1)
	var alive_ratio = BossGrid.alive_ratio()
	var base_atk = max(1, int(raw_atk * hp_ratio * alive_ratio))
	match attack_type:
		BossGrid.AttackType.SLAM:
			# 重击：双倍伤害 + 强烈震屏
			GameManager.take_damage(int(base_atk * 2.0))
			_screen_shake(22.0, 0.45)
			_flash_screen(Color(1.0, 0.1, 0.0, 0.35), 0.12)
			_show_attack_label("重 击！", Color(0.98, 0.18, 0.05))
		BossGrid.AttackType.CHARGE:
			# 突进：1.5x 伤害 + 中等震屏
			GameManager.take_damage(int(base_atk * 1.5))
			_screen_shake(16.0, 0.38)
			_flash_screen(Color(1.0, 0.3, 0.0, 0.25), 0.1)
			_show_attack_label("突 进！", Color(0.95, 0.55, 0.05))
		BossGrid.AttackType.WIDE_SWIPE:
			# 横扫：1.2x 伤害 + 减少玩家下一回合点击数
			GameManager.take_damage(int(base_atk * 1.2))
			GameManager.apply_swipe_debuff()
			_screen_shake(14.0, 0.5)
			_show_attack_label("横 扫！", Color(0.7, 0.2, 0.95))
		BossGrid.AttackType.STRAFE:
			# 侧移：1.3x 伤害 + 大面积封锁区
			GameManager.take_damage(int(base_atk * 1.3))
			_screen_shake(12.0, 0.35)
			_flash_screen(Color(1.0, 0.2, 0.2, 0.25), 0.1)
			_show_attack_label("侧 移！", Color(0.3, 0.7, 0.95))
		BossGrid.AttackType.BURROW:
			# 潜地：0.6x 伤害 + 大面积封锁
			GameManager.take_damage(int(base_atk * 0.6))
			_screen_shake(10.0, 0.3)
			_flash_screen(Color(0.8, 0.3, 0.1, 0.2), 0.12)
			_show_attack_label("潜 地！", Color(0.5, 0.35, 0.2))
		_:
			# 普通攻击
			GameManager.take_damage(base_atk)
			_screen_shake()
			_flash_screen(Color(1.0, 0.15, 0.1, 0.2), 0.1)
			_show_attack_label("攻 击！", Color(0.95, 0.55, 0.45))

func _on_boss_ranged_attack(attack_type: int):
	# 远程轰炸：Boss不在左边界也能发动，造成伤害+封锁
	var raw_atk = LevelData.get_boss_attack(GameManager.floor_number)
	var hp_ratio = float(GameManager.boss_hp) / max(GameManager.boss_max_hp, 1)
	var base_atk = max(1, int(raw_atk * hp_ratio * 0.5))
	GameManager.take_damage(base_atk)
	_screen_shake(10.0, 0.3)
	_flash_screen(Color(1.0, 0.1, 0.0, 0.3), 0.12)
	_show_attack_label("远程轰炸！", Color(1.0, 0.4, 0.15))
	# 在玩家区域产生封锁
	BossGrid.add_temporary_blocks(Vector2i(randi_range(0, 3), randi_range(0, BossGrid.placement_rows - 1)), 2)

func _show_attack_label(text: String, color: Color):
	var canvas = CanvasLayer.new()
	canvas.layer = 85
	add_child(canvas)
	var lbl = Label.new()
	lbl.text = text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 460)
	lbl.size = Vector2(1920, 120)
	lbl.add_theme_font_size_override("font_size", 88)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	lbl.add_theme_constant_override("shadow_offset_x", 4)
	lbl.add_theme_constant_override("shadow_offset_y", 4)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 60)  # 相对于label自身的中心点
	canvas.add_child(lbl)
	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.12)
	tw.tween_property(lbl, "scale", Vector2(1.08, 1.08), 0.12).set_trans(Tween.TRANS_BACK)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.1)
	tw.tween_interval(0.4)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.25)
	tw.tween_callback(canvas.queue_free)

func _screen_shake(intensity: float = 10.0, duration: float = 0.3):
	if not GameSettings.screen_shake_enabled:
		return
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
	# 关掉可能还在等待的临时升级面板，避免 _wait_for_combat_upgrade 死锁
	combat_upgrade_panel.visible = false
	# Boss死亡序列：震屏 + 逐格爆碎 + 闪光
	await get_tree().create_timer(0.3).timeout  # 让最后一击伤害数字先显示
	_screen_shake(18.0, 0.6)
	_show_boss_death_flash()
	await placement_view.play_boss_death_sequence()
	await get_tree().create_timer(0.3).timeout  # 爆碎完喘息一下
	_show_boss_defeated_label()
	await get_tree().create_timer(0.8).timeout  # 让"Boss击破"标签充分展示
	# 结算正确标记回血
	var correct = mine_view.count_correct_marks()
	if correct > 0:
		await _show_mark_heal_animation(correct)
		await get_tree().create_timer(0.3).timeout
	# 再显示永久升级面板
	await get_tree().create_timer(0.4).timeout
	permanent_upgrade_panel.show_choices(UpgradeManager.get_permanent_choices(3))
	TutorialManager.try_show("first_upgrade", self)
	_animate_panel_in(permanent_upgrade_panel)

func _show_boss_death_flash():
	var canvas = CanvasLayer.new()
	canvas.layer = 75
	add_child(canvas)
	var flash = ColorRect.new()
	flash.color = Color(1.0, 0.9, 0.6, 0.0)
	flash.size = Vector2(1920, 1080)
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(flash)
	var tw = create_tween()
	tw.tween_property(flash, "color:a", 0.7, 0.1)
	tw.tween_property(flash, "color:a", 0.0, 0.8).set_trans(Tween.TRANS_EXPO)
	tw.tween_callback(canvas.queue_free)

func _show_boss_defeated_label():
	var canvas = CanvasLayer.new()
	canvas.layer = 85
	add_child(canvas)
	var lbl = Label.new()
	lbl.text = "Boss 击破！"
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 420)
	lbl.size = Vector2(1920, 120)
	lbl.add_theme_font_size_override("font_size", 88)
	lbl.add_theme_color_override("font_color", Color(1.0, 0.85, 0.2))
	lbl.add_theme_color_override("font_shadow_color", Color(0.6, 0.15, 0.0, 0.9))
	lbl.add_theme_constant_override("shadow_offset_x", 4)
	lbl.add_theme_constant_override("shadow_offset_y", 4)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 60)
	canvas.add_child(lbl)
	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.12)
	tw.tween_property(lbl, "scale", Vector2(1.12, 1.12), 0.15).set_trans(Tween.TRANS_BACK)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.12)
	tw.tween_interval(0.8)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.4)
	tw.tween_callback(canvas.queue_free)

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
		lbl.add_theme_color_override("font_color", UIThemeManager.color("text_heal"))
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

func _on_damage_numbers(cell_damages: Dictionary):
	if cell_damages.is_empty():
		return
	var canvas = CanvasLayer.new()
	canvas.layer = 70
	add_child(canvas)
	var cs = LevelData.get_cell_size(GameManager.floor_number)
	var view_pos = placement_view.global_position
	var total_dmg = 0
	for cell in cell_damages:
		var dmg: int = cell_damages[cell]
		if dmg <= 0:
			continue
		total_dmg += dmg
		var lbl = Label.new()
		lbl.text = "-%d" % dmg
		var font_size = 28 if dmg < 30 else (38 if dmg < 60 else 50)
		lbl.add_theme_font_size_override("font_size", font_size)
		var col = UIThemeManager.color("dmg_lo") if dmg < 20 else (UIThemeManager.color("dmg_mid") if dmg < 50 else UIThemeManager.color("dmg_hi"))
		lbl.add_theme_color_override("font_color", col)
		lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
		lbl.add_theme_constant_override("shadow_offset_x", 2)
		lbl.add_theme_constant_override("shadow_offset_y", 2)
		var wx = view_pos.x + cell.x * cs + cs * 0.5 - 20 + randf_range(-8, 8)
		var wy = view_pos.y + cell.y * cs + cs * 0.1
		lbl.position = Vector2(wx, wy)
		lbl.modulate = Color(1, 1, 1, 0)
		lbl.pivot_offset = Vector2(20, 12)
		canvas.add_child(lbl)
		# Pop + float animation
		var tw = create_tween()
		tw.tween_property(lbl, "modulate:a", 1.0, 0.06)
		tw.parallel().tween_property(lbl, "scale", Vector2(1.25, 1.25), 0.06)
		tw.tween_property(lbl, "scale", Vector2.ONE, 0.1).set_trans(Tween.TRANS_BACK)
		tw.tween_property(lbl, "position:y", wy - 55, 0.55).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.25).set_delay(0.35)
	# 大量伤害时微震
	if total_dmg >= 40:
		_screen_shake(min(total_dmg * 0.15, 12.0), 0.15)
	await get_tree().create_timer(0.8).timeout
	canvas.queue_free()

func _animate_panel_in(panel: Control):
	panel.modulate = Color(1, 1, 1, 0)
	var tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tween.tween_property(panel, "modulate:a", 1.0, 0.3)

func _on_game_over():
	GameManager.timer_running = false
	AchievementManager.end_run()
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
	title.add_theme_color_override("font_color", UIThemeManager.color("text_danger"))
	title.add_theme_color_override("font_shadow_color", (UIThemeManager.color("text_danger") as Color).darkened(0.6))
	title.add_theme_constant_override("shadow_offset_x", 4)
	title.add_theme_constant_override("shadow_offset_y", 4)
	title.modulate = Color(1, 1, 1, 0)
	overlay.add_child(title)

	# ── 分隔线 ──
	var sep = Label.new()
	sep.text = "━━━━━━━━━━━━━━━━━━━━"
	sep.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sep.position = Vector2(0, 400)
	sep.size = Vector2(1920, 40)
	sep.add_theme_font_size_override("font_size", 24)
	sep.add_theme_color_override("font_color", (UIThemeManager.color("text_danger") as Color).darkened(0.3).lerp(Color.TRANSPARENT, 0.4))
	sep.modulate = Color(1, 1, 1, 0)
	overlay.add_child(sep)

	# ── 层数信息 ──
	var info = Label.new()
	info.text = "你倒在了第 %d 层" % GameManager.floor_number
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	info.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	info.position = Vector2(0, 480)
	info.size = Vector2(1920, 60)
	info.add_theme_font_size_override("font_size", 42)
	info.add_theme_color_override("font_color", UIThemeManager.color("text_accent"))
	info.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	info.add_theme_constant_override("shadow_offset_x", 2)
	info.add_theme_constant_override("shadow_offset_y", 2)
	info.modulate = Color(1, 1, 1, 0)
	overlay.add_child(info)

	# ── 战斗统计 ──
	var stats_lines = [
		"⚡ 总伤害: %d" % GameManager.stat_total_damage,
		"💣 炸弹使用: %d" % GameManager.stat_bombs_used,
		"🔗 最大连锁: %d" % GameManager.stat_max_chain,
		"🏆 通过层数: %d" % GameManager.stat_floors_cleared,
		"🎯 击杀Boss: %d" % AchievementManager.stats.get("bosses_killed", 0),
	]
	var stat_y = 545.0
	var stat_nodes: Array = []
	for line in stats_lines:
		var s = Label.new()
		s.text = line
		s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		s.position = Vector2(0, stat_y)
		s.size = Vector2(1920, 34)
		s.add_theme_font_size_override("font_size", 22)
		s.add_theme_color_override("font_color", Color(0.85, 0.78, 0.55))
		s.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
		s.add_theme_constant_override("shadow_offset_x", 1)
		s.add_theme_constant_override("shadow_offset_y", 1)
		s.modulate = Color(1, 1, 1, 0)
		overlay.add_child(s)
		stat_nodes.append(s)
		stat_y += 30.0

	# ── 评价 ──
	var rating_text = _get_run_rating()
	var rating = Label.new()
	rating.text = rating_text
	rating.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rating.position = Vector2(0, stat_y + 10)
	rating.size = Vector2(1920, 50)
	rating.add_theme_font_size_override("font_size", 30)
	rating.add_theme_color_override("font_color", Color(1.0, 0.85, 0.2))
	rating.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	rating.add_theme_constant_override("shadow_offset_x", 2)
	rating.add_theme_constant_override("shadow_offset_y", 2)
	rating.modulate = Color(1, 1, 1, 0)
	overlay.add_child(rating)

	# ── 操作按钮 ──
	var btn_box = HBoxContainer.new()
	btn_box.position = Vector2(560, stat_y + 70)
	btn_box.size = Vector2(800, 60)
	btn_box.add_theme_constant_override("separation", 40)
	btn_box.alignment = BoxContainer.ALIGNMENT_CENTER
	btn_box.modulate = Color(1, 1, 1, 0)
	overlay.add_child(btn_box)

	var retry_btn = Button.new()
	retry_btn.text = "🔄 重新开始"
	retry_btn.custom_minimum_size = Vector2(200, 56)
	retry_btn.add_theme_font_size_override("font_size", 28)
	retry_btn.add_theme_color_override("font_color", UIThemeManager.color("text_heal"))
	var rs = UIThemeManager.make_stylebox("btn_normal_bg", "btn_normal_brd")
	retry_btn.add_theme_stylebox_override("normal", rs)
	retry_btn.add_theme_stylebox_override("hover", UIThemeManager.make_stylebox("btn_hover_bg", "border_strong"))
	retry_btn.pressed.connect(_on_restart)
	btn_box.add_child(retry_btn)

	var title_btn = Button.new()
	title_btn.text = "🏠 返回标题"
	title_btn.custom_minimum_size = Vector2(200, 56)
	title_btn.add_theme_font_size_override("font_size", 28)
	title_btn.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	title_btn.add_theme_stylebox_override("normal", rs.duplicate())
	title_btn.add_theme_stylebox_override("hover", UIThemeManager.make_stylebox("btn_hover_bg", "border_strong"))
	title_btn.pressed.connect(_on_quit_to_title)
	btn_box.add_child(title_btn)

	# ═══ 动画序列 ═══
	# 1. 遮罩渐暗
	var tw_bg = create_tween()
	tw_bg.tween_property(overlay, "color", UIThemeManager.color("intro_overlay"), 1.2)

	# 2. 标题从上方滑入（带回弹）
	var tw_t1 = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw_t1.tween_interval(0.3)
	tw_t1.tween_property(title, "position:y", 280.0, 0.7)
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
	tw_i1.tween_property(info, "position:y", 440.0, 0.5)
	var tw_i2 = create_tween().set_ease(Tween.EASE_OUT)
	tw_i2.tween_interval(1.2)
	tw_i2.tween_property(info, "modulate:a", 1.0, 0.5)

	# 5. 统计数据逐行淡入
	var stat_base_delay = 1.8
	for si in range(stat_nodes.size()):
		var tw_sn = create_tween().set_ease(Tween.EASE_OUT)
		tw_sn.tween_interval(stat_base_delay + si * 0.15)
		tw_sn.tween_property(stat_nodes[si], "modulate:a", 1.0, 0.35)

	# 6. 评价淡入
	var tw_r = create_tween().set_ease(Tween.EASE_OUT)
	tw_r.tween_interval(stat_base_delay + stat_nodes.size() * 0.15 + 0.3)
	tw_r.tween_property(rating, "modulate:a", 1.0, 0.5)

	# 7. 按钮淡入
	var tw_h = create_tween()
	tw_h.tween_interval(stat_base_delay + stat_nodes.size() * 0.15 + 1.0)
	tw_h.tween_property(btn_box, "modulate:a", 1.0, 0.5)

# 升级选完后继续（由 UpgradePanel 回调）
func on_combat_upgrade_chosen():
	combat_upgrade_panel.visible = false
	_show_upgrade_flash("增益获得！", Color(0.3, 0.85, 1.0))

func on_permanent_upgrade_chosen():
	permanent_upgrade_panel.visible = false
	_show_upgrade_flash("强化完成！", Color(1.0, 0.85, 0.2))
	GameManager.next_floor()
	_start_new_floor()

func _show_upgrade_flash(text: String, color: Color):
	_flash_screen(color.lerp(Color.WHITE, 0.5), 0.06)
	var canvas = CanvasLayer.new()
	canvas.layer = 76
	add_child(canvas)
	var lbl = Label.new()
	lbl.text = text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 500)
	lbl.size = Vector2(1920, 60)
	lbl.add_theme_font_size_override("font_size", 36)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	lbl.add_theme_constant_override("shadow_offset_x", 2)
	lbl.add_theme_constant_override("shadow_offset_y", 2)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 30)
	canvas.add_child(lbl)
	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.08)
	tw.parallel().tween_property(lbl, "scale", Vector2(1.2, 1.2), 0.08)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.1).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.5)
	tw.tween_property(lbl, "position:y", 470.0, 0.25)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.25)
	tw.tween_callback(canvas.queue_free)

func _get_run_rating() -> String:
	var floor_n = GameManager.floor_number
	var dmg = GameManager.stat_total_damage
	if floor_n >= 50:
		return "🏆 传奇勇者！你的名字将被铭记！"
	elif floor_n >= 20:
		return "⭐ 精英冒险家！实力不俗！"
	elif floor_n >= 10:
		return "💪 初露锋芒！继续加油！"
	elif dmg >= 500:
		return "💥 爆破专家！虽败犹荣！"
	else:
		return "🌱 初出茅庐，下次会更好！"

func _on_all_minions_cleared():
	# 所有小怪已消灭，Boss入场
	_show_boss_enter_label(LevelData.get_boss_name(GameManager.floor_number))
	# 刷新放置区显示Boss格子
	placement_view._refresh_boss_tiles()

func _show_boss_enter_label(boss_name: String):
	var canvas = CanvasLayer.new()
	canvas.layer = 85
	add_child(canvas)
	var lbl = Label.new()
	lbl.text = boss_name + " 入场！"
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 440)
	lbl.size = Vector2(1920, 100)
	lbl.add_theme_font_size_override("font_size", 72)
	lbl.add_theme_color_override("font_color", Color(0.95, 0.25, 0.1))
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	lbl.add_theme_constant_override("shadow_offset_x", 4)
	lbl.add_theme_constant_override("shadow_offset_y", 4)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 50)
	canvas.add_child(lbl)
	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.15)
	tw.tween_property(lbl, "scale", Vector2(1.05, 1.05), 0.15).set_trans(Tween.TRANS_BACK)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.12)
	tw.tween_interval(0.6)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.3)
	tw.tween_callback(canvas.queue_free)

func _on_boss_phase_changed(phase: int):
	if phase <= 1:
		return
	var txt: String
	var color: Color
	var font_size: int
	if phase >= 3:
		txt = "最终阶段！"
		color = Color(1.0, 0.15, 0.1)
		font_size = 56
		_screen_shake(14.0, 0.5)
		_flash_screen(Color(1.0, 0.1, 0.0, 0.3), 0.15)
		AudioManager.play_sfx("boss_hit")
	else:
		txt = "Boss 狂暴化！"
		color = Color(1.0, 0.75, 0.15)
		font_size = 48
		_screen_shake(8.0, 0.3)
		_flash_screen(Color(1.0, 0.6, 0.0, 0.2), 0.1)
	_show_phase_banner(txt, color, font_size)
# ======== 趣味性系统 ========

# ---- Lucky Find 弹窗 ----
func _on_lucky_find(_reward_type: String, reward_text: String):
	_show_reward_popup(reward_text, Color(1.0, 0.85, 0.1), 32)

# ---- Streak Bonus 弹窗 ----
func _on_streak_bonus(streak: int, reward_text: String):
	var color = Color(0.2, 1.0, 0.3) if streak < 5 else Color(1.0, 0.5, 0.0) if streak < 7 else Color(1.0, 0.2, 0.8)
	_show_reward_popup(reward_text, color, 36)
	_screen_shake(4.0 + streak, 0.15)

# ---- 连锁触发反馈 ----
func _on_chain_triggered(chained_positions: Array):
	_show_chain_celebration(chained_positions.size())

# ---- Critical Hit 闪光 ----
func _on_critical_hit(cell: Vector2i, damage: int):
	var cs = LevelData.get_cell_size(GameManager.floor_number)
	var view_pos = placement_view.global_position
	var wx = view_pos.x + cell.x * cs + cs * 0.5
	var wy = view_pos.y + cell.y * cs

	# 暴击整屏微闪
	_flash_screen(Color(1.0, 0.9, 0.3, 0.15), 0.08)

	var canvas = CanvasLayer.new()
	canvas.layer = 72
	add_child(canvas)

	var lbl = Label.new()
	lbl.text = "暴击! -%d" % damage
	lbl.add_theme_font_size_override("font_size", 42)
	lbl.add_theme_color_override("font_color", Color(1.0, 0.15, 0.0))
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	lbl.add_theme_constant_override("shadow_offset_x", 3)
	lbl.add_theme_constant_override("shadow_offset_y", 3)
	lbl.position = Vector2(wx - 60, wy - 20)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(60, 20)
	canvas.add_child(lbl)

	var tw2 = create_tween()
	tw2.tween_property(lbl, "modulate:a", 1.0, 0.06)
	tw2.parallel().tween_property(lbl, "scale", Vector2(1.3, 1.3), 0.06)
	tw2.tween_property(lbl, "scale", Vector2.ONE, 0.1).set_trans(Tween.TRANS_BACK)
	tw2.tween_property(lbl, "position:y", wy - 90, 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw2.parallel().tween_property(lbl, "modulate:a", 0.0, 0.3).set_delay(0.3)
	tw2.tween_callback(canvas.queue_free)

	_screen_shake(6.0, 0.12)

# ---- 通用奖励弹窗（在探索区上方浮出） ----
func _show_reward_popup(text: String, color: Color, font_size: int = 32):
	var canvas = CanvasLayer.new()
	canvas.layer = 75
	add_child(canvas)

	var lbl = Label.new()
	lbl.text = "★ %s ★" % text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, mine_view.global_position.y - 50)
	lbl.size = Vector2(1920, 60)
	lbl.add_theme_font_size_override("font_size", font_size)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	lbl.add_theme_constant_override("shadow_offset_x", 2)
	lbl.add_theme_constant_override("shadow_offset_y", 2)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 30)
	canvas.add_child(lbl)

	var tw3 = create_tween()
	tw3.tween_property(lbl, "modulate:a", 1.0, 0.1)
	tw3.tween_property(lbl, "scale", Vector2(1.1, 1.1), 0.1).set_trans(Tween.TRANS_BACK)
	tw3.tween_property(lbl, "scale", Vector2.ONE, 0.08)
	tw3.tween_interval(0.7)
	tw3.tween_property(lbl, "position:y", lbl.position.y - 40, 0.35)
	tw3.parallel().tween_property(lbl, "modulate:a", 0.0, 0.35)
	tw3.tween_callback(canvas.queue_free)

# ---- 总伤害统计弹窗（引爆后显示） ----
func _show_damage_summary(total_damage: int):
	if total_damage <= 0:
		return
	var rating: String
	var rating_color: Color
	if total_damage >= GameManager.boss_max_hp * 0.5:
		rating = "毁灭打击！"
		rating_color = Color(1.0, 0.1, 0.0)
	elif total_damage >= GameManager.boss_max_hp * 0.25:
		rating = "强力一击！"
		rating_color = Color(1.0, 0.6, 0.0)
	elif total_damage >= GameManager.boss_max_hp * 0.1:
		rating = "不错！"
		rating_color = Color(0.3, 1.0, 0.4)
	else:
		return  # 小伤害不提示

	var canvas = CanvasLayer.new()
	canvas.layer = 71
	add_child(canvas)

	var lbl = Label.new()
	lbl.text = "%s  ⚡%d 伤害" % [rating, total_damage]
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 480)
	lbl.size = Vector2(1920, 80)
	lbl.add_theme_font_size_override("font_size", 48)
	lbl.add_theme_color_override("font_color", rating_color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	lbl.add_theme_constant_override("shadow_offset_x", 3)
	lbl.add_theme_constant_override("shadow_offset_y", 3)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 40)
	canvas.add_child(lbl)

	var tw4 = create_tween()
	tw4.tween_property(lbl, "modulate:a", 1.0, 0.12)
	tw4.tween_property(lbl, "scale", Vector2(1.15, 1.15), 0.1).set_trans(Tween.TRANS_BACK)
	tw4.tween_property(lbl, "scale", Vector2.ONE, 0.08)
	tw4.tween_interval(0.6)
	tw4.tween_property(lbl, "modulate:a", 0.0, 0.3)
	tw4.tween_callback(canvas.queue_free)

# ---- 暂停菜单回调 ----
func _on_restart():
	get_tree().paused = false
	get_tree().reload_current_scene()

func _on_quit_to_title():
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/ui/TitleScreen.tscn")

# ---- 成就解锁通知 ----
func _on_achievement_unlocked(id: String, title: String):
	var ach = AchievementManager.ACHIEVEMENTS.get(id, {})
	var icon = ach.get("icon", "🏆")
	var canvas = CanvasLayer.new()
	canvas.layer = 95
	add_child(canvas)
	var panel = PanelContainer.new()
	panel.position = Vector2(1440, -80)
	panel.size = Vector2(440, 70)
	var ps = StyleBoxFlat.new()
	ps.bg_color = Color(0.08, 0.06, 0.12, 0.92)
	ps.border_color = Color(1.0, 0.85, 0.2, 0.8)
	ps.set_border_width_all(2)
	ps.set_corner_radius_all(12)
	ps.shadow_color = Color(0, 0, 0, 0.4)
	ps.shadow_size = 6
	panel.add_theme_stylebox_override("panel", ps)
	canvas.add_child(panel)
	var lbl = Label.new()
	lbl.text = "%s 成就解锁: %s" % [icon, title]
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	lbl.add_theme_font_size_override("font_size", 22)
	lbl.add_theme_color_override("font_color", Color(1.0, 0.85, 0.2))
	panel.add_child(lbl)
	var tw = create_tween()
	tw.tween_property(panel, "position:y", 20.0, 0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_interval(2.5)
	tw.tween_property(panel, "position:y", -80.0, 0.3).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	tw.tween_callback(canvas.queue_free)

# ---- 连锁庆祝 ----
func _show_chain_celebration(chain_count: int):
	if chain_count < 2:
		return
	var text: String
	var color: Color
	var font_size: int
	if chain_count >= 8:
		text = "超 级 连 锁 ×%d！" % chain_count
		color = Color(1.0, 0.15, 0.85)
		font_size = 72
	elif chain_count >= 5:
		text = "连 锁 ×%d！" % chain_count
		color = Color(0.85, 0.3, 1.0)
		font_size = 60
	elif chain_count >= 3:
		text = "连锁 ×%d" % chain_count
		color = Color(1.0, 0.65, 0.1)
		font_size = 48
	else:
		text = "连锁 ×%d" % chain_count
		color = Color(0.4, 0.9, 1.0)
		font_size = 40

	var canvas = CanvasLayer.new()
	canvas.layer = 73
	add_child(canvas)

	var lbl = Label.new()
	lbl.text = text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 360)
	lbl.size = Vector2(1920, 100)
	lbl.add_theme_font_size_override("font_size", font_size)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	lbl.add_theme_constant_override("shadow_offset_x", 3)
	lbl.add_theme_constant_override("shadow_offset_y", 3)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 50)
	canvas.add_child(lbl)

	var tw = create_tween()
	tw.tween_property(lbl, "modulate:a", 1.0, 0.08)
	tw.parallel().tween_property(lbl, "scale", Vector2(1.3, 1.3), 0.08)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.6)
	tw.tween_property(lbl, "position:y", 320.0, 0.3)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.3)
	tw.tween_callback(canvas.queue_free)

	if chain_count >= 5:
		_screen_shake(3.0 + chain_count, 0.2)
	if chain_count >= 3:
		_flash_screen(color.lerp(Color.WHITE, 0.5), 0.06)

# ---- 整屏微闪（暴击/连锁/Boss死亡用） ----
func _flash_screen(color: Color, duration: float = 0.08):
	var canvas = CanvasLayer.new()
	canvas.layer = 74
	add_child(canvas)
	var flash = ColorRect.new()
	flash.color = color
	flash.size = Vector2(1920, 1080)
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(flash)
	var tw = create_tween()
	tw.tween_property(flash, "color:a", 0.0, duration * 4).set_trans(Tween.TRANS_EXPO)
	tw.tween_callback(canvas.queue_free)

# ---- Boss阶段转换横幅 ----
func _show_phase_banner(text: String, color: Color, font_size: int):
	var canvas = CanvasLayer.new()
	canvas.layer = 86
	add_child(canvas)

	# 横幅背景条
	var bar = ColorRect.new()
	bar.color = Color(0, 0, 0, 0.0)
	bar.size = Vector2(1920, 120)
	bar.position = Vector2(0, 480)
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(bar)

	var lbl = Label.new()
	lbl.text = text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	lbl.position = Vector2(0, 0)
	lbl.size = Vector2(1920, 120)
	lbl.add_theme_font_size_override("font_size", font_size)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	lbl.add_theme_constant_override("shadow_offset_x", 4)
	lbl.add_theme_constant_override("shadow_offset_y", 4)
	lbl.modulate = Color(1, 1, 1, 0)
	lbl.pivot_offset = Vector2(960, 60)
	bar.add_child(lbl)

	var tw = create_tween()
	# Bar slides in
	tw.tween_property(bar, "color:a", 0.75, 0.15)
	tw.parallel().tween_property(lbl, "modulate:a", 1.0, 0.1)
	tw.parallel().tween_property(lbl, "scale", Vector2(1.15, 1.15), 0.1)
	tw.tween_property(lbl, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.9)
	tw.tween_property(bar, "color:a", 0.0, 0.3)
	tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.3)
	tw.tween_callback(canvas.queue_free)

# ---- 环境粒子（浮尘/光点） ----
var _ambient_particles: Array = []

func _spawn_ambient_particles(floor_n: int):
	# 清除旧粒子
	for p in _ambient_particles:
		if is_instance_valid(p):
			p.queue_free()
	_ambient_particles.clear()

	var level_color = LevelData.get_level_color(floor_n)
	var particle_color = level_color.lerp(Color(1, 1, 1, 0.15), 0.6)

	for i in range(12):
		var dot = ColorRect.new()
		var sz = randf_range(2.0, 5.0)
		dot.size = Vector2(sz, sz)
		dot.color = particle_color
		dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
		dot.z_index = -1
		dot.position = Vector2(randf_range(0, 1920), randf_range(0, 1080))
		dot.modulate = Color(1, 1, 1, randf_range(0.1, 0.4))
		add_child(dot)
		_ambient_particles.append(dot)

		# Slow float + fade loop
		var dur = randf_range(6.0, 14.0)
		var tw_p = create_tween().set_loops()
		tw_p.tween_property(dot, "position:y", dot.position.y - randf_range(60, 180), dur).set_trans(Tween.TRANS_SINE)
		tw_p.parallel().tween_property(dot, "position:x", dot.position.x + randf_range(-40, 40), dur).set_trans(Tween.TRANS_SINE)
		tw_p.parallel().tween_property(dot, "modulate:a", randf_range(0.05, 0.2), dur * 0.5)
		tw_p.tween_property(dot, "position", Vector2(randf_range(0, 1920), randf_range(0, 1080)), 0.05)
		tw_p.tween_property(dot, "modulate:a", randf_range(0.15, 0.4), dur * 0.5)
