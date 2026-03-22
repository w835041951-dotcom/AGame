## 单个格子节点脚本

extends Button

const SIZE = 64  # 每个格子像素大小

var grid_x: int
var grid_y: int
var cell_data: Dictionary

# 颜色定义
const COLOR_HIDDEN = Color(0.3, 0.3, 0.35)
const COLOR_REVEALED = Color(0.85, 0.82, 0.75)
const COLOR_BOMB_FLASH = Color(1.0, 0.9, 0.0)
const NUMBER_COLORS = [
	Color.WHITE,
	Color(0.2, 0.4, 1.0),   # 1 蓝
	Color(0.1, 0.7, 0.2),   # 2 绿
	Color(0.9, 0.2, 0.2),   # 3 红
	Color(0.1, 0.1, 0.7),   # 4 深蓝
	Color(0.7, 0.1, 0.1),   # 5 深红
	Color(0.1, 0.6, 0.6),   # 6 青
	Color(0.1, 0.1, 0.1),   # 7 黑
	Color(0.5, 0.5, 0.5),   # 8 灰
]

func setup(x: int, y: int):
	grid_x = x
	grid_y = y
	custom_minimum_size = Vector2(SIZE, SIZE)
	size = Vector2(SIZE, SIZE)
	text = ""
	add_theme_color_override("font_color", Color.WHITE)
	add_theme_font_size_override("font_size", 20)
	_set_hidden_style()
	pressed.connect(_on_pressed)

func _on_pressed():
	if GameManager.current_clicks <= 0:
		return
	GridManager.reveal_cell(grid_x, grid_y)

func reveal(data: Dictionary):
	cell_data = data
	_set_revealed_style()
	if data["is_bomb"]:
		_show_bomb(data["bomb_type"])
	elif data["adjacent"] > 0:
		text = str(data["adjacent"])
		var color = NUMBER_COLORS[data["adjacent"]] if data["adjacent"] < NUMBER_COLORS.size() else Color.WHITE
		add_theme_color_override("font_color", color)
	else:
		text = ""

func flash_bomb():
	# 触发炸弹时闪烁动画
	var tween = create_tween()
	tween.tween_method(_set_color, COLOR_BOMB_FLASH, COLOR_REVEALED, 0.4)

func _show_bomb(bomb_type: String):
	var info = BombRegistry.get_bomb_info(bomb_type)
	text = _get_bomb_icon(bomb_type)
	if info.has("color"):
		add_theme_color_override("font_color", info["color"])
	_set_bomb_style(info.get("color", Color.RED))

func _get_bomb_icon(bomb_type: String) -> String:
	match bomb_type:
		"cross": return "+"
		"scatter": return "*"
		"bounce": return "~"
		"pierce": return "|"
		"area": return "#"
		_: return "!"

func _set_hidden_style():
	var style = StyleBoxFlat.new()
	style.bg_color = COLOR_HIDDEN
	style.border_width_all = 2
	style.border_color = Color(0.5, 0.5, 0.55)
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_left = 4
	style.corner_radius_bottom_right = 4
	add_theme_stylebox_override("normal", style)
	add_theme_stylebox_override("hover", _make_hover_style())

func _make_hover_style() -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.4, 0.4, 0.45)
	style.border_width_all = 2
	style.border_color = Color(0.7, 0.7, 0.75)
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_left = 4
	style.corner_radius_bottom_right = 4
	return style

func _set_revealed_style():
	var style = StyleBoxFlat.new()
	style.bg_color = COLOR_REVEALED
	style.border_width_all = 1
	style.border_color = Color(0.6, 0.58, 0.52)
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_left = 4
	style.corner_radius_bottom_right = 4
	add_theme_stylebox_override("normal", style)
	add_theme_stylebox_override("hover", style)
	add_theme_stylebox_override("pressed", style)
	disabled = true

func _set_bomb_style(color: Color):
	var style = StyleBoxFlat.new()
	style.bg_color = color.darkened(0.3)
	style.border_width_all = 2
	style.border_color = color
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_left = 4
	style.corner_radius_bottom_right = 4
	add_theme_stylebox_override("normal", style)
	add_theme_stylebox_override("hover", style)
	disabled = true

func _set_color(color: Color):
	var style = StyleBoxFlat.new()
	style.bg_color = color
	style.corner_radius_top_left = 4
	style.corner_radius_top_right = 4
	style.corner_radius_bottom_left = 4
	style.corner_radius_bottom_right = 4
	add_theme_stylebox_override("normal", style)
