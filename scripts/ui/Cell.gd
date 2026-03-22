## 单个格子节点 - 支持放置区和扫雷区两种模式

extends Button

enum Mode { PLACEMENT, MINE }
enum DisplayState { EMPTY, BOMB_PLACED, BLOCKED, BOSS_NORMAL, BOSS_WEAK, BOSS_ARMOR, BOSS_ABSORB, BOSS_DEAD, EXPLODING, MINE_HIDDEN, MINE_REVEALED, MINE_BOMB }

const SIZE = 56

var mode: Mode = Mode.PLACEMENT
var grid_x: int
var grid_y: int

# 各状态颜色
const C_EMPTY        = Color(0.25, 0.25, 0.30)
const C_BOSS_NORMAL  = Color(0.45, 0.12, 0.12)
const C_BOSS_WEAK    = Color(0.20, 0.18, 0.05)
const C_BOSS_ARMOR   = Color(0.18, 0.22, 0.35)
const C_BOSS_ABSORB  = Color(0.10, 0.30, 0.15)
const C_BOSS_DEAD    = Color(0.08, 0.08, 0.08)
const C_MINE_HIDDEN  = Color(0.30, 0.30, 0.35)
const C_MINE_REVEAL  = Color(0.78, 0.75, 0.68)
const C_EXPLODING    = Color(1.0,  0.45, 0.05)

const NUMBER_COLORS = [
	Color.WHITE,
	Color(0.3, 0.5, 1.0), Color(0.2, 0.75, 0.3), Color(0.9, 0.25, 0.25),
	Color(0.2, 0.2, 0.8), Color(0.75, 0.15, 0.15), Color(0.15, 0.65, 0.65),
	Color(0.15, 0.15, 0.15), Color(0.55, 0.55, 0.55),
]

func setup(x: int, y: int, m: Mode):
	grid_x = x
	grid_y = y
	mode = m
	custom_minimum_size = Vector2(SIZE, SIZE)
	size = Vector2(SIZE, SIZE)
	text = ""
	add_theme_font_size_override("font_size", 18)
	set_display_state(DisplayState.MINE_HIDDEN if mode == Mode.MINE else DisplayState.EMPTY)
	pressed.connect(_on_pressed)

func _on_pressed():
	if mode == Mode.PLACEMENT:
		BombPlacer.on_cell_clicked(grid_x, grid_y)
	else:
		GridManager.reveal_cell(grid_x, grid_y)

func set_display_state(state: DisplayState, extra: Dictionary = {}):
	text = ""
	disabled = false
	var bg = C_EMPTY
	var border = Color(0.5, 0.5, 0.55)
	var border_w = 1

	match state:
		DisplayState.EMPTY:
			bg = C_EMPTY
		DisplayState.BOMB_PLACED:
			var info = BombRegistry.get_bomb_info(extra.get("bomb_type", "cross"))
			bg = info.get("color", Color.RED).darkened(0.4)
			border = info.get("color", Color.RED)
			border_w = 2
			text = _bomb_icon(extra.get("bomb_type", "cross"))
			add_theme_color_override("font_color", info.get("color", Color.RED))
		DisplayState.BLOCKED:
			bg = Color(0.3, 0.05, 0.05)
			text = "X"
			add_theme_color_override("font_color", Color(0.8, 0.2, 0.2))
			disabled = true
		DisplayState.BOSS_NORMAL:
			bg = C_BOSS_NORMAL
			border = Color(0.8, 0.2, 0.2)
			border_w = 2
			_show_boss_info(extra)
		DisplayState.BOSS_WEAK:
			bg = C_BOSS_WEAK
			border = Color(1.0, 0.9, 0.1)
			border_w = 3
			_show_boss_info(extra)
		DisplayState.BOSS_ARMOR:
			bg = C_BOSS_ARMOR
			border = Color(0.5, 0.6, 0.9)
			border_w = 3
			_show_boss_info(extra)
		DisplayState.BOSS_ABSORB:
			bg = C_BOSS_ABSORB
			border = Color(0.2, 0.9, 0.4)
			border_w = 2
			_show_boss_info(extra)
		DisplayState.BOSS_DEAD:
			bg = C_BOSS_DEAD
			text = "✕"
			add_theme_color_override("font_color", Color(0.4, 0.4, 0.4))
			disabled = true
		DisplayState.EXPLODING:
			bg = C_EXPLODING
			border = Color(1.0, 0.7, 0.0)
			border_w = 3
			_flash_explode()
		DisplayState.MINE_HIDDEN:
			bg = C_MINE_HIDDEN
			border = Color(0.5, 0.5, 0.55)
		DisplayState.MINE_REVEALED:
			bg = C_MINE_REVEAL
			border = Color(0.55, 0.52, 0.46)
			disabled = true
			var adj = extra.get("adjacent", 0)
			if adj > 0:
				text = str(adj)
				var nc = NUMBER_COLORS[adj] if adj < NUMBER_COLORS.size() else Color.WHITE
				add_theme_color_override("font_color", nc)
		DisplayState.MINE_BOMB:
			bg = BombRegistry.get_bomb_info(extra.get("bomb_type","cross")).get("color", Color.RED).darkened(0.3)
			border = BombRegistry.get_bomb_info(extra.get("bomb_type","cross")).get("color", Color.RED)
			border_w = 2
			text = _bomb_icon(extra.get("bomb_type", "cross"))
			add_theme_color_override("font_color", Color.WHITE)
			disabled = true

	_apply_style(bg, border, border_w)

func _show_boss_info(extra: Dictionary):
	var part = extra.get("part", BossGrid.BodyPart.NONE)
	match part:
		BossGrid.BodyPart.HEAD: text = "H"
		BossGrid.BodyPart.LEG:  text = "L"
		BossGrid.BodyPart.CORE: text = "C"
	if text != "":
		add_theme_color_override("font_color", Color(1.0, 1.0, 0.6))

func _flash_explode():
	var tween = create_tween()
	tween.tween_method(func(c): _apply_style(c, Color.YELLOW, 3),
		C_EXPLODING, C_EMPTY, 0.5)

func _bomb_icon(bomb_type: String) -> String:
	match bomb_type:
		"cross":   return "+"
		"scatter": return "*"
		"bounce":  return "~"
		"pierce":  return "|"
		"area":    return "#"
		_:         return "!"

func _apply_style(bg: Color, border: Color, border_w: int):
	var s = StyleBoxFlat.new()
	s.bg_color = bg
	s.border_width_left = border_w
	s.border_width_right = border_w
	s.border_width_top = border_w
	s.border_width_bottom = border_w
	s.border_color = border
	s.corner_radius_top_left = 4
	s.corner_radius_top_right = 4
	s.corner_radius_bottom_left = 4
	s.corner_radius_bottom_right = 4
	add_theme_stylebox_override("normal", s)
	var h = s.duplicate()
	h.bg_color = bg.lightened(0.1)
	add_theme_stylebox_override("hover", h)
	add_theme_stylebox_override("pressed", s)
	add_theme_stylebox_override("disabled", s)
