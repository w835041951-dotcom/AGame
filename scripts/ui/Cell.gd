## 单个格子节点 - 支持放置区和扫雷区两种模式

extends Button

enum Mode { PLACEMENT, MINE }
enum DisplayState { EMPTY, BOMB_PLACED, BLOCKED, BOSS_NORMAL, BOSS_WEAK, BOSS_ARMOR, BOSS_ABSORB, BOSS_DEAD, EXPLODING, MINE_HIDDEN, MINE_REVEALED, MINE_BOMB }

const SIZE = 64  # 默认值，运行时由 setup() 覆盖
var cell_size: int = 64

var mode: Mode = Mode.PLACEMENT
var grid_x: int
var grid_y: int
var _current_state: DisplayState = DisplayState.EMPTY

const C_EMPTY       = Color(0.18, 0.17, 0.20)   # 暗黑地牢地板
const C_BOSS_DEAD   = Color(0.06, 0.06, 0.07)   # 虚空黑
const C_MINE_HIDDEN = Color(0.25, 0.26, 0.30)   # 神秘石砖
const C_MINE_REVEAL = Color(0.58, 0.54, 0.44)   # 温暖砂岩
const C_EXPLODING   = Color(0.90, 0.35, 0.05)   # 岩浆橙

# 数字颜色：在浅色翻开背景上清晰可读（用深色/饱和色）
const NUMBER_COLORS = [
	Color(0.2, 0.2, 0.2),       # 0 不显示
	Color(0.15, 0.35, 0.80),    # 1 蓝宝石
	Color(0.12, 0.55, 0.22),    # 2 翡翠绿
	Color(0.80, 0.15, 0.12),    # 3 红宝石
	Color(0.22, 0.15, 0.62),    # 4 紫水晶
	Color(0.62, 0.12, 0.12),    # 5 暗红宝石
	Color(0.12, 0.50, 0.55),    # 6 绿松石
	Color(0.88, 0.72, 0.18),    # 7 金色
	Color(0.55, 0.38, 0.18),    # 8 古铜色
]

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
		add_theme_color_override("font_color", Color(0.35, 0.90, 0.55))
	else:
		text = ""
		remove_theme_color_override("font_color")
		add_theme_font_size_override("font_size", 20)

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

	match state:
		DisplayState.EMPTY:
			_apply_style(C_EMPTY, Color(0.28, 0.26, 0.24), 1)

		DisplayState.BOMB_PLACED:
			var bomb_type = extra.get("bomb_type", "pierce_h")
			var info = BombRegistry.get_bomb_info(bomb_type)
			var col = info.get("color", Color.RED)
			_apply_style(col.darkened(0.5), col, 2)
			icon = _get_bomb_texture(bomb_type)
			expand_icon = true
			# 悬停提示：显示炸弹等级和范围
			var lvl = BombRegistry.get_bomb_level(bomb_type)
			var range_desc = BombRegistry.get_range_description(bomb_type)
			tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name", ""), lvl, range_desc]

		DisplayState.BLOCKED:
			_apply_style(Color(0.22, 0.05, 0.05), Color(0.65, 0.15, 0.15), 2)
			text = "✕"
			add_theme_color_override("font_color", Color(0.65, 0.15, 0.15))
			disabled = true

		DisplayState.BOSS_NORMAL, DisplayState.BOSS_WEAK, DisplayState.BOSS_ARMOR, DisplayState.BOSS_ABSORB:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			var border_col = Color(0.65, 0.18, 0.12)
			var border_w = 1
			match state:
				DisplayState.BOSS_WEAK:   border_col = Color(0.95, 0.80, 0.15); border_w = 3
				DisplayState.BOSS_ARMOR:  border_col = Color(0.45, 0.55, 0.85); border_w = 3
				DisplayState.BOSS_ABSORB: border_col = Color(0.20, 0.75, 0.35); border_w = 2
			_apply_style(Color(0,0,0,0), border_col, border_w)
			_show_boss_info(extra)

		DisplayState.BOSS_DEAD:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			_apply_style(C_BOSS_DEAD, Color(0.25, 0.22, 0.22), 1)
			modulate = Color(0.35, 0.3, 0.3, 0.5)

		DisplayState.EXPLODING:
			_apply_style(C_EXPLODING, Color(1.0, 0.65, 0.0), 3)
			_flash_explode()

		DisplayState.MINE_HIDDEN:
			_apply_style(C_MINE_HIDDEN, Color(0.33, 0.35, 0.40), 2)

		DisplayState.MINE_REVEALED:
			_apply_style(C_MINE_REVEAL, Color(0.48, 0.44, 0.36), 1)
			disabled = true
			var adj = extra.get("adjacent", 0)
			if adj > 0:
				text = str(adj)
				var nc = NUMBER_COLORS[adj] if adj < NUMBER_COLORS.size() else Color(0.1, 0.1, 0.1)
				add_theme_color_override("font_color", nc)
				add_theme_color_override("font_disabled_color", nc)
			else:
				# 空格，强制字色为透明（不显示任何字）
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
			# 悬停提示
			var mine_lvl = BombRegistry.get_bomb_level(bomb_type)
			var mine_range = BombRegistry.get_range_description(bomb_type)
			tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name", ""), mine_lvl, mine_range]
			if extra.get("revealed", false):
				disabled = true

	modulate = Color.WHITE

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
	# atlas 中每格固定 64px（PNG 的实际像素大小）
	var region = Rect2(local_pos.x * 64, local_pos.y * 64, 64, 64)
	# 安全检查：不超出贴图边界
	if region.position.x + 64 > tex.get_width() or region.position.y + 64 > tex.get_height():
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
		add_theme_color_override("font_color", Color(0.95, 0.88, 0.50))

func _bomb_symbol(bomb_type: String) -> String:
	match bomb_type:
		"pierce_h": return "↔"
		"pierce_v": return "↕"
		"cross":    return "+"
		"x_shot":   return "╳"
		"bounce":   return "~"
		_:           return "!"

func _flash_explode():
	var tween = create_tween()
	tween.tween_method(func(c): _apply_style(c, Color.YELLOW, 3), C_EXPLODING, C_EMPTY, 0.5)

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
	# 透视升级专用动画：紫色光晕 + 旋转缩放
	pivot_offset = size / 2
	scale = Vector2(0.0, 0.0)
	modulate = Color(0.6, 0.3, 1.0, 0.0)  # 紫色透明
	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate", Color(0.6, 0.3, 1.0, 1.0), 0.15)
	tween.tween_property(self, "rotation", TAU, 0.35).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await tween.finished
	rotation = 0.0
	# 从紫色过渡到正常白色
	var tw2 = create_tween()
	tw2.tween_property(self, "modulate", Color.WHITE, 0.3)

func animate_boss_pulse():
	var tween = create_tween()
	tween.tween_property(self, "modulate", Color(1.3, 1.1, 1.0), 0.05)
	tween.tween_property(self, "modulate", Color.WHITE, 0.25)

func _apply_style(bg: Color, border: Color, border_w: int):
	var s = StyleBoxFlat.new()
	s.bg_color = bg
	s.border_width_left = border_w
	s.border_width_right = border_w
	s.border_width_top = border_w
	s.border_width_bottom = border_w
	s.border_color = border
	s.corner_radius_top_left = 3
	s.corner_radius_top_right = 3
	s.corner_radius_bottom_left = 3
	s.corner_radius_bottom_right = 3
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
