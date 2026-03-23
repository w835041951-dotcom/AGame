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

var _background_cache: Dictionary = {}

func _ready():
	GameManager.boss_defeated.connect(_on_boss_defeated)
	GameManager.game_over.connect(_on_game_over)
	GameManager.turn_ended.connect(_on_turn_ended)
	GameManager.combat_upgrade_triggered.connect(_on_combat_upgrade)
	BossGrid.core_destroyed.connect(_on_combat_upgrade)
	BossGrid.boss_attacked.connect(_on_boss_attacked)
	ExplosionCalc.damage_numbers.connect(_on_damage_numbers)
	MinionGrid.all_minions_cleared.connect(_on_all_minions_cleared)

	combat_upgrade_panel.visible = false
	permanent_upgrade_panel.visible = false

	# 给玩家初始炸弹，避免第一回合无弹可用
	GameManager.add_bomb("pierce_h")
	GameManager.add_bomb("pierce_h")
	GameManager.add_bomb("pierce_v")

	_start_new_floor()

func _start_new_floor():
	_apply_floor_background()
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
	var label_h = 24
	var total_h = label_h + p_height + sel_h + label_h + m_height + gap * 4
	var start_y = hud_h + max(0, (1080 - hud_h - total_h) / 2)

	# Boss区域标签
	var boss_label = _create_section_label("⚔ Boss 战场", (1920 - p_width) / 2, start_y, p_width)
	_section_labels.append(boss_label)

	placement_view.position = Vector2((1920 - p_width) / 2, start_y + label_h + gap)
	bomb_selector.position.y = start_y + label_h + gap + p_height + gap
	bomb_selector.size.x = 1920

	var mine_top = start_y + label_h + gap + p_height + sel_h + gap * 2
	# 探索区域标签
	var mine_label = _create_section_label("🔍 探索区", (1920 - m_width) / 2, mine_top, m_width)
	_section_labels.append(mine_label)
	mine_view.position = Vector2((1920 - m_width) / 2, mine_top + label_h + gap)

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
	panel_style.bg_color = Color(0.05, 0.04, 0.05, 0.94)
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
	body.add_theme_color_override("font_color", Color(0.84, 0.82, 0.78))
	panel.add_child(body)

	var hint = Label.new()
	hint.text = "战区档案已更新"
	hint.position = Vector2(1020, 720)
	hint.size = Vector2(420, 40)
	hint.add_theme_font_size_override("font_size", 20)
	hint.add_theme_color_override("font_color", Color(0.65, 0.62, 0.58, 0.85))
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
	bg.color = UIThemeManager.color("intro_overlay")
	bg.size = Vector2(1920, 1080)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(bg)

	# 古语旁白（神秘低语）
	var whisper = Label.new()
	whisper.text = _get_level_whisper(floor_n)
	whisper.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	whisper.position = Vector2(0, 300)
	whisper.size = Vector2(1920, 40)
	whisper.add_theme_font_size_override("font_size", 18)
	whisper.add_theme_color_override("font_color", UIThemeManager.color("whisper_text"))
	whisper.modulate = Color(1, 1, 1, 0)
	bg.add_child(whisper)

	# 层数
	var floor_label = Label.new()
	floor_label.text = "第 %d 层" % floor_n
	floor_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	floor_label.position = Vector2(0, 340)
	floor_label.size = Vector2(1920, 50)
	floor_label.add_theme_font_size_override("font_size", 32)
	floor_label.add_theme_color_override("font_color", UIThemeManager.color("floor_text"))
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
	boss_label.add_theme_color_override("font_color", UIThemeManager.color("boss_label"))
	boss_label.modulate = Color(1, 1, 1, 0)
	bg.add_child(boss_label)

	# 副标题
	var sub = Label.new()
	sub.text = subtitle
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.position = Vector2(0, 550)
	sub.size = Vector2(1920, 50)
	sub.add_theme_font_size_override("font_size", 26)
	sub.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	sub.modulate = Color(1, 1, 1, 0)
	bg.add_child(sub)

	# ── 动画 ──
	var tw = create_tween()
	tw.tween_property(whisper, "modulate:a", 0.7, 0.5)
	tw.tween_interval(0.3)
	tw.tween_property(floor_label, "modulate:a", 1.0, 0.3)
	tw.tween_property(title, "modulate:a", 1.0, 0.4)
	tw.tween_property(boss_label, "modulate:a", 1.0, 0.3)
	tw.tween_property(sub, "modulate:a", 1.0, 0.4)
	tw.tween_interval(1.2)
	tw.tween_property(bg, "modulate:a", 0.0, 0.5)
	tw.tween_callback(canvas.queue_free)

	# 等动画结束
	await tw.finished

const LEVEL_WHISPERS = [
	["Kha'lithë… vorn amethaal…", "Duur okh… shtaan reeve…", "Mogh'raal vaan ethith…"],
	["Zhe'kuur… arraas thol…", "Vor'itha… mal'kaan dul…", "Sht'maas okh reethaal…"],
	["Ighn'raal… vhoum tesh'kaa…", "Bharr okh'muul dhaan…", "Zaan'veth uur tholiim…"],
	["Keth'uur… shaal marr'goth…", "Dhuum vaan… reth'aal kine…", "Okh'shaal muur taan'gal…"],
	["Maal'veth… orn gha'tuum…", "Zur'aan eth… kethaal ruum…", "Ghaal'ith vhoum daan'sheth…"],
]

func _get_level_whisper(floor_n: int) -> String:
	var idx = (floor_n - 1) % LEVEL_WHISPERS.size()
	var whispers = LEVEL_WHISPERS[idx]
	return whispers[randi() % whispers.size()]

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
	# 小怪阶段时Boss不移动
	if not MinionGrid.has_minions():
		if UpgradeManager.is_boss_frozen():
			UpgradeManager.consume_freeze_boss()
		else:
			BossGrid.random_move()
	await get_tree().create_timer(0.2).timeout
	if GameManager.player_hp <= 0:
		return
	BombPlacer.reset()
	GameManager.start_turn()

func _on_boss_attacked(attack_type: int):
	var base_atk = LevelData.get_boss_attack(GameManager.floor_number)
	match attack_type:
		BossGrid.AttackType.SLAM:
			# 重击：双倍伤害 + 强烈震屏
			GameManager.take_damage(int(base_atk * 2.0))
			_screen_shake(22.0, 0.45)
			_show_attack_label("重 击！", Color(0.98, 0.18, 0.05))
		BossGrid.AttackType.CHARGE:
			# 突进：1.5x 伤害 + 中等震屏
			GameManager.take_damage(int(base_atk * 1.5))
			_screen_shake(16.0, 0.38)
			_show_attack_label("突 进！", Color(0.95, 0.55, 0.05))
		BossGrid.AttackType.WIDE_SWIPE:
			# 横扫：1.2x 伤害 + 减少玩家下一回合点击数
			GameManager.take_damage(int(base_atk * 1.2))
			GameManager.apply_swipe_debuff()
			_screen_shake(14.0, 0.5)
			_show_attack_label("横 扫！", Color(0.7, 0.2, 0.95))
		_:
			# 普通攻击
			GameManager.take_damage(base_atk)
			_screen_shake()

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
	for cell in cell_damages:
		var dmg: int = cell_damages[cell]
		if dmg <= 0:
			continue
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
		canvas.add_child(lbl)
		var tw = create_tween()
		tw.tween_property(lbl, "modulate:a", 1.0, 0.1)
		tw.tween_property(lbl, "position:y", wy - 55, 0.55).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(lbl, "modulate:a", 0.0, 0.25).set_delay(0.35)
	await get_tree().create_timer(0.8).timeout
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
	sep.position = Vector2(0, 450)
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
	info.position = Vector2(0, 540)
	info.size = Vector2(1920, 60)
	info.add_theme_font_size_override("font_size", 42)
	info.add_theme_color_override("font_color", UIThemeManager.color("text_accent"))
	info.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
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
	hint.add_theme_color_override("font_color", UIThemeManager.color("text_secondary"))
	hint.modulate = Color(1, 1, 1, 0)
	overlay.add_child(hint)

	# ═══ 动画序列 ═══
	# 1. 遮罩渐暗
	var tw_bg = create_tween()
	tw_bg.tween_property(overlay, "color", UIThemeManager.color("intro_overlay"), 1.2)

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
