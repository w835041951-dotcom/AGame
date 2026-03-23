## 单个格子节点 - 支持放置区和探索区两种模式

extends Button

enum Mode { PLACEMENT, MINE }
enum DisplayState { EMPTY, BOMB_PLACED, BLOCKED, BOSS_NORMAL, BOSS_WEAK, BOSS_ARMOR, BOSS_ABSORB, BOSS_DEAD, EXPLODING, MINE_HIDDEN, MINE_REVEALED, MINE_BOMB, MINION }

const SIZE = 64  # 默认值，运行时由 setup() 覆盖
var cell_size: int = 64

var mode: Mode = Mode.PLACEMENT
var grid_x: int
var grid_y: int
var _current_state: DisplayState = DisplayState.EMPTY

static var _bomb_textures: Dictionary = {}
static var _boss_textures: Dictionary = {}  # path -> Texture2D

var _marked_safe: bool = false  # 右键标记为"安全/空"

func is_marked() -> bool:
	return _marked_safe

func setup(x: int, y: int, m: Mode, sz: int = 64):
	grid_x = x
	grid_y = y
	mode = m
	cell_size = sz
	custom_minimum_size = Vector2(cell_size, cell_size)
	size = Vector2(cell_size, cell_size)
	text = ""
	add_theme_font_size_override("font_size", max(12, cell_size / 3))
	set_display_state(DisplayState.MINE_HIDDEN if mode == Mode.MINE else DisplayState.EMPTY)
	pressed.connect(_on_pressed)

func _gui_input(event: InputEvent):
	if mode != Mode.MINE:
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
		if _current_state == DisplayState.MINE_HIDDEN:
			_marked_safe = !_marked_safe
			_update_mark_display()
			accept_event()

func _on_pressed():
	if mode == Mode.PLACEMENT:
		BombPlacer.on_cell_clicked(grid_x, grid_y)
	else:
		GridManager.reveal_cell(grid_x, grid_y)

func _update_mark_display():
	if _marked_safe:
		text = "○"
		add_theme_font_size_override("font_size", 24)
		add_theme_color_override("font_color", UIThemeManager.color("text_heal"))
	else:
		text = ""
		remove_theme_color_override("font_color")
		add_theme_font_size_override("font_size", 20)

var _hp_ratio: float = -1.0  # -1 = 不显示HP条

func set_display_state(state: DisplayState, extra: Dictionary = {}):
	_current_state = state
	_marked_safe = false  # 翻开/状态变化时清除标记
	text = ""
	icon = null
	disabled = false
	expand_icon = false
	tooltip_text = ""
	# 每次重置颜色和字号，防止上次状态残留
	remove_theme_color_override("font_color")
	remove_theme_color_override("font_disabled_color")
	add_theme_font_size_override("font_size", 20)

	var tm = UIThemeManager

	match state:
		DisplayState.EMPTY:
			_apply_style(tm.color("bg_empty"), tm.color("border_default"), 1)

		DisplayState.BOMB_PLACED:
			var bomb_type = extra.get("bomb_type", "pierce_h")
			var info = BombRegistry.get_bomb_info(bomb_type)
			var col = info.get("color", Color.RED)
			_apply_style(col.darkened(0.5), col, 2)
			icon = _get_bomb_texture(bomb_type)
			expand_icon = true
			var lvl = BombRegistry.get_bomb_level(bomb_type)
			var range_desc = BombRegistry.get_range_description(bomb_type)
			tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name", ""), lvl, range_desc]

		DisplayState.BLOCKED:
			_apply_style(Color(0.22, 0.05, 0.05), tm.color("text_danger").darkened(0.35), 2)
			text = "✕"
			add_theme_color_override("font_color", tm.color("text_danger"))
			disabled = true

		DisplayState.BOSS_NORMAL, DisplayState.BOSS_WEAK, DisplayState.BOSS_ARMOR, DisplayState.BOSS_ABSORB:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			var border_col = tm.color("text_danger").darkened(0.2)
			var border_w = 1
			match state:
				DisplayState.BOSS_WEAK:   border_col = tm.color("boss_weak_brd");   border_w = 3
				DisplayState.BOSS_ARMOR:  border_col = tm.color("boss_armor_brd");  border_w = 3
				DisplayState.BOSS_ABSORB: border_col = tm.color("boss_absorb_brd"); border_w = 2
			_apply_style(Color(0,0,0,0), border_col, border_w)
			_show_boss_info(extra)
			var hp = extra.get("hp", -1)
			var max_hp = extra.get("max_hp", 1)
			_hp_ratio = float(hp) / max(max_hp, 1) if hp >= 0 else -1.0
			queue_redraw()

		DisplayState.BOSS_DEAD:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			_apply_style(tm.color("bg_void"), tm.color("bg_secondary"), 1)
			modulate = Color(0.35, 0.3, 0.3, 0.5)
			_hp_ratio = -1.0
			queue_redraw()

		DisplayState.EXPLODING:
			_apply_style(tm.color("explode_bg"), tm.color("explode_brd"), 3)
			_flash_explode()

		DisplayState.MINE_HIDDEN:
			_apply_style(tm.color("mine_hidden"), tm.color("mine_hidden_brd"), 2)

		DisplayState.MINE_REVEALED:
			_apply_style(tm.color("mine_reveal"), tm.color("mine_reveal_brd"), 1)
			disabled = true
			var adj = extra.get("adjacent", 0)
			if adj > 0:
				text = str(adj)
				var nc = tm.get_number_color(adj)
				add_theme_color_override("font_color", nc)
				add_theme_color_override("font_disabled_color", nc)
			else:
				add_theme_color_override("font_color", Color(0,0,0,0))
				add_theme_color_override("font_disabled_color", Color(0,0,0,0))

		DisplayState.MINE_BOMB:
			var bomb_type = extra.get("bomb_type", "pierce_h")
			var info = BombRegistry.get_bomb_info(bomb_type)
			var col = info.get("color", Color.RED)
			_apply_style(col.darkened(0.35), col.lightened(0.1), 2)
			var tex = _get_bomb_texture(bomb_type)
			if tex != null:
				icon = tex
				expand_icon = true
			else:
				text = _bomb_symbol(bomb_type)
				var tc = col.lightened(0.5)
				add_theme_color_override("font_color", tc)
				add_theme_color_override("font_disabled_color", tc)
			var mine_lvl = BombRegistry.get_bomb_level(bomb_type)
			var mine_range = BombRegistry.get_range_description(bomb_type)
			tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name", ""), mine_lvl, mine_range]
			if extra.get("revealed", false):
				disabled = true

		DisplayState.MINION:
			var minion_color = extra.get("color", Color(0.4, 0.9, 0.3))
			var label_text = extra.get("label", "怪")
			_apply_style(minion_color.darkened(0.6), minion_color, 3)
			text = label_text.substr(0, 1)
			add_theme_font_size_override("font_size", max(14, cell_size / 3))
			add_theme_color_override("font_color", minion_color.lightened(0.6))
			var hp = extra.get("hp", -1)
			var max_hp = extra.get("max_hp", 1)
			_hp_ratio = float(hp) / max(max_hp, 1) if hp >= 0 else -1.0
			tooltip_text = "%s  HP: %d/%d" % [label_text, hp, max_hp]
			queue_redraw()

	modulate = Color.WHITE
	if _hp_ratio < 0.0:
		queue_redraw()

func _draw():
	if _hp_ratio < 0.0 or _hp_ratio > 1.0:
		return
	var bar_h = max(5, cell_size / 12)
	var bar_y = cell_size - bar_h
	draw_rect(Rect2(1, bar_y, cell_size - 2, bar_h), Color(0.05, 0.05, 0.05, 0.85))
	var bar_col: Color
	if _hp_ratio > 0.6:
		bar_col = UIThemeManager.color("text_heal")
	elif _hp_ratio > 0.3:
		bar_col = Color(0.95, 0.75, 0.1)
	else:
		bar_col = UIThemeManager.color("text_danger")
	var fill_w = int((cell_size - 2) * _hp_ratio)
	if fill_w > 0:
		draw_rect(Rect2(1, bar_y, fill_w, bar_h), bar_col)

func _get_bomb_texture(bomb_type: String) -> Texture2D:
	if bomb_type in _bomb_textures:
		return _bomb_textures[bomb_type]
	var path = "res://assets/sprites/bombs/%s.png" % bomb_type
	if ResourceLoader.exists(path):
		var tex = load(path) as Texture2D
		_bomb_textures[bomb_type] = tex
		return tex
	return null

func _get_boss_cell_texture(local_pos: Vector2i) -> AtlasTexture:
	var tex_path = LevelData.get_boss_texture_path(GameManager.floor_number)
	if not _boss_textures.has(tex_path):
		if ResourceLoader.exists(tex_path):
			_boss_textures[tex_path] = load(tex_path)
		else:
			return null
	var tex = _boss_textures[tex_path]
	if tex == null:
		return null
	if BossGrid.boss_width <= 0 or BossGrid.boss_height <= 0:
		return null
	var tile_w = int(tex.get_width()  / float(BossGrid.boss_width))
	var tile_h = int(tex.get_height() / float(BossGrid.boss_height))
	var region = Rect2(local_pos.x * tile_w, local_pos.y * tile_h, tile_w, tile_h)
	if region.position.x + tile_w > tex.get_width() or region.position.y + tile_h > tex.get_height():
		return null
	var atlas = AtlasTexture.new()
	atlas.atlas = tex
	atlas.region = region
	return atlas

func _show_boss_info(extra: Dictionary):
	var part = extra.get("part", BossGrid.BodyPart.NONE)
	match part:
		BossGrid.BodyPart.HEAD: text = "H"
		BossGrid.BodyPart.LEG:  text = "L"
		BossGrid.BodyPart.CORE: text = "C"
	if text != "":
		add_theme_color_override("font_color", UIThemeManager.color("text_accent"))

func _bomb_symbol(bomb_type: String) -> String:
	match bomb_type:
		"pierce_h": return "↔"
		"pierce_v": return "↕"
		"cross":    return "+"
		"x_shot":   return "╳"
		"bounce":   return "~"
		_:           return "!"

func _flash_explode():
	var c_start = UIThemeManager.color("explode_bg")
	var c_end   = UIThemeManager.color("bg_empty")
	var tween = create_tween()
	tween.tween_method(func(c): _apply_style(c, Color.YELLOW, 3), c_start, c_end, 0.5)

# ---- 动画方法 ----

func animate_explosion_hit(delay: float = 0.0):
	if _current_state == DisplayState.BOSS_DEAD:
		return
	var tween = create_tween()
	if delay > 0.0:
		tween.tween_interval(delay)
	tween.tween_property(self, "modulate", Color(3.0, 2.5, 0.5), 0.06)
	tween.tween_property(self, "modulate", Color.WHITE, 0.4)

func animate_placement():
	pivot_offset = size / 2
	scale = Vector2(0.5, 0.5)
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "scale", Vector2.ONE, 0.2)

func animate_destruction():
	pivot_offset = size / 2
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "scale", Vector2(0.6, 0.6), 0.3)

func animate_reveal():
	pivot_offset = size / 2
	scale = Vector2(0.0, 0.0)
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "scale", Vector2.ONE, 0.15)

func animate_magic_reveal():
	pivot_offset = size / 2
	scale = Vector2(0.0, 0.0)
	modulate = Color(0.6, 0.3, 1.0, 0.0)
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate", Color(0.6, 0.3, 1.0, 1.0), 0.15)
	tween.tween_property(self, "rotation", TAU, 0.35).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await tween.finished
	rotation = 0.0
	var tw2 = create_tween()
	tw2.tween_property(self, "modulate", Color.WHITE, 0.3)

func animate_boss_pulse():
	var c = UIThemeManager.color("boss_pulse")
	var tween = create_tween()
	tween.tween_property(self, "modulate", c, 0.05)
	tween.tween_property(self, "modulate", Color.WHITE, 0.25)

func animate_chain():
	var c = UIThemeManager.color("chain_flash")
	pivot_offset = size / 2
	var tween = create_tween().set_parallel(true)
	tween.tween_property(self, "modulate", c, 0.08)
	tween.tween_property(self, "scale", Vector2(1.25, 1.25), 0.08)
	var tw2 = create_tween().set_parallel(true)
	tw2.tween_interval(0.08)
	tw2.tween_property(self, "modulate", Color.WHITE, 0.35)
	tw2.tween_property(self, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

func _apply_style(bg: Color, border: Color, border_w: int):
	var cr = UIThemeManager.color("corner_radius") as int
	var s = StyleBoxFlat.new()
	s.bg_color = bg
	s.set_border_width_all(border_w)
	s.border_color = border
	s.set_corner_radius_all(cr)
	s.shadow_color = Color(0, 0, 0, 0.35)
	s.shadow_size = 2
	add_theme_stylebox_override("normal", s)
	var h = s.duplicate()
	h.bg_color = bg.lightened(0.10)
	h.border_color = border.lightened(0.15)
	add_theme_stylebox_override("hover", h)
	var p = s.duplicate()
	p.bg_color = bg.darkened(0.06)
	add_theme_stylebox_override("pressed", p)
	add_theme_stylebox_override("disabled", s)
