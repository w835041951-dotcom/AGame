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

# ── 格子状态纹理 ──
# 优先从主题目录加载，回退到通用目录
const CELL_TEX_NAMES = {
	"empty":        "cell_empty",
	"mine_hidden":  "cell_mine_hidden",
	"mine_reveal":  "cell_mine_revealed",
	"boss_normal":  "cell_boss_normal",
	"boss_weak":    "cell_boss_weak",
	"boss_armor":   "cell_boss_armor",
	"boss_absorb":  "cell_boss_absorb",
	"boss_dead":    "cell_boss_dead",
	"blocked":      "cell_blocked",
	"exploding":    "cell_exploding",
	"bomb_placed":  "cell_bomb_placed",
	"minion":       "cell_minion",
	"hp_bar_bg":    "hp_bar_bg",
	"hp_bar_fill":  "hp_bar_fill",
}
const CELL_TEX_FALLBACK = {
	"empty":       "res://assets/sprites/ui/cell_empty.png",
	"mine_hidden": "res://assets/sprites/ui/cell_mine_hidden.png",
	"mine_reveal": "res://assets/sprites/ui/cell_mine_revealed.png",
	"boss_normal": "res://assets/sprites/ui/cell_boss_normal.png",
	"boss_weak":   "res://assets/sprites/ui/cell_boss_weak.png",
	"boss_armor":  "res://assets/sprites/ui/cell_boss_armor.png",
	"boss_absorb": "res://assets/sprites/ui/cell_boss_absorb.png",
	"boss_dead":   "res://assets/sprites/ui/cell_boss_dead.png",
	"hp_bar_bg":   "res://assets/sprites/ui/hp_bar_bg.png",
	"hp_bar_fill": "res://assets/sprites/ui/hp_bar_fill.png",
}

static func _get_cell_tex(key: String) -> Texture2D:
	# 1) 尝试主题素材
	var themed_name = CELL_TEX_NAMES.get(key, "")
	if themed_name != "":
		var tex = UIThemeManager.get_themed(themed_name)
		if tex:
			return tex
	# 2) 回退到通用素材
	var path = CELL_TEX_FALLBACK.get(key, "")
	if path != "" and ResourceLoader.exists(path):
		return load(path) as Texture2D
	return null

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
	add_theme_font_size_override("font_size", max(14, cell_size * 0.38))
	set_display_state(DisplayState.MINE_HIDDEN if mode == Mode.MINE else DisplayState.EMPTY)
	pressed.connect(_on_pressed)
	mouse_entered.connect(_on_mouse_entered)
	mouse_exited.connect(_on_mouse_exited)

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
		GridManager.reveal_cell(grid_x, grid_y, Input.is_key_pressed(KEY_SHIFT))

func _on_mouse_entered():
	_hovered = true
	if _hp_ratio >= 0.0:
		queue_redraw()

func _on_mouse_exited():
	_hovered = false
	if _hp_ratio >= 0.0:
		queue_redraw()

func _update_mark_display():
	if _marked_safe:
		text = "○"
		add_theme_font_size_override("font_size", max(20, cell_size * 0.38))
		add_theme_color_override("font_color", UIThemeManager.color("text_heal"))
		add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
		add_theme_constant_override("shadow_offset_x", 1)
		add_theme_constant_override("shadow_offset_y", 1)
	else:
		text = ""
		remove_theme_color_override("font_color")
		remove_theme_color_override("font_shadow_color")
		add_theme_font_size_override("font_size", max(14, cell_size * 0.38))

var _hp_ratio: float = -1.0  # -1 = 不显示HP条
var _hovered: bool = false    # 鼠标悬停时才显示HP条

func set_display_state(state: DisplayState, extra: Dictionary = {}):
	_current_state = state
	_marked_safe = false  # 翻开/状态变化时清除标记
	text = ""
	icon = null
	disabled = false
	expand_icon = false
	tooltip_text = ""
	modulate = Color.WHITE
	# 每次重置颜色和字号，防止上次状态残留
	remove_theme_color_override("font_color")
	remove_theme_color_override("font_disabled_color")
	remove_theme_color_override("font_shadow_color")
	add_theme_font_size_override("font_size", max(16, cell_size * 0.35))

	var tm = UIThemeManager

	match state:
		DisplayState.EMPTY:
			_apply_tex_or_flat("empty", tm.color("bg_empty"), tm.color("border_default"), 0)

		DisplayState.BOMB_PLACED:
			var bomb_type = extra.get("bomb_type", "pierce_h")
			var info = BombRegistry.get_bomb_info(bomb_type)
			var col = info.get("color", Color.RED)
			_apply_tex_or_flat("bomb_placed", col.darkened(0.5), col, 1)
			icon = _get_bomb_texture(bomb_type)
			expand_icon = true
			var lvl = BombRegistry.get_bomb_level(bomb_type)
			var range_desc = BombRegistry.get_range_description(bomb_type)
			tooltip_text = "%s  Lv.%d\n范围: %s" % [info.get("name", ""), lvl, range_desc]

		DisplayState.BLOCKED:
			_apply_tex_or_flat("blocked", tm.color("blocked_bg"), (tm.color("text_danger") as Color).darkened(0.35), 1)
			text = "✕"
			add_theme_color_override("font_color", tm.color("text_danger"))
			disabled = true

		DisplayState.BOSS_NORMAL, DisplayState.BOSS_WEAK, DisplayState.BOSS_ARMOR, DisplayState.BOSS_ABSORB:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			# 透明背景，让Boss贴图完全显示
			_apply_style(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0)
			_show_boss_info(extra)
			var hp = extra.get("hp", -1)
			var max_hp = extra.get("max_hp", 1)
			_hp_ratio = float(hp) / max(max_hp, 1) if hp >= 0 else -1.0
			queue_redraw()

		DisplayState.BOSS_DEAD:
			var local = extra.get("local_pos", Vector2i(0, 0))
			icon = _get_boss_cell_texture(local)
			expand_icon = true
			_apply_tex_or_flat("boss_dead", tm.color("bg_void"), tm.color("bg_secondary"), 1)
			modulate = tm.color("boss_dead_tint")
			_hp_ratio = -1.0
			queue_redraw()

		DisplayState.EXPLODING:
			_apply_tex_or_flat("exploding", tm.color("explode_bg"), tm.color("explode_brd"), 2)
			_flash_explode()

		DisplayState.MINE_HIDDEN:
			_apply_tex_or_flat("mine_hidden", tm.color("mine_hidden"), tm.color("mine_hidden_brd"), 2)
			text = "?"
			add_theme_color_override("font_color", (tm.color("mine_hidden_brd") as Color).lightened(0.2))
			add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
			add_theme_constant_override("shadow_offset_x", 1)
			add_theme_constant_override("shadow_offset_y", 1)

		DisplayState.MINE_REVEALED:
			_apply_tex_or_flat("mine_reveal", tm.color("mine_reveal"), tm.color("mine_reveal_brd"), 0)
			disabled = true
			var adj = extra.get("adjacent", 0)
			if adj > 0:
				text = str(adj)
				add_theme_font_size_override("font_size", max(18, cell_size * 0.42))
				var nc = tm.get_number_color(adj)
				add_theme_color_override("font_color", nc)
				add_theme_color_override("font_disabled_color", nc)
				add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
				add_theme_constant_override("shadow_offset_x", 1)
				add_theme_constant_override("shadow_offset_y", 1)
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
			_apply_tex_or_flat("minion", minion_color.darkened(0.6), minion_color, 1)
			text = label_text.substr(0, 1)
			add_theme_font_size_override("font_size", max(16, cell_size * 0.38))
			add_theme_color_override("font_color", minion_color.lightened(0.6))
			add_theme_color_override("font_shadow_color", UIThemeManager.color("shadow_color"))
			add_theme_constant_override("shadow_offset_x", 1)
			add_theme_constant_override("shadow_offset_y", 1)
			var hp = extra.get("hp", -1)
			var max_hp = extra.get("max_hp", 1)
			_hp_ratio = float(hp) / max(max_hp, 1) if hp >= 0 else -1.0
			tooltip_text = "%s  HP: %d/%d" % [label_text, hp, max_hp]
			queue_redraw()

	if _hp_ratio < 0.0:
		queue_redraw()

func _draw():
	if not _hovered or _hp_ratio < 0.0 or _hp_ratio > 1.0:
		return
	var bar_h = max(8, cell_size / 7)
	var bar_y = cell_size - bar_h - 1
	# 背景纹理
	var bg_tex = _get_cell_tex("hp_bar_bg")
	if bg_tex:
		draw_texture_rect(bg_tex, Rect2(1, bar_y, cell_size - 2, bar_h), false)
	else:
		draw_rect(Rect2(1, bar_y, cell_size - 2, bar_h), UIThemeManager.color("hp_bar_bg"))
	# 填充
	var bar_col: Color
	if _hp_ratio > 0.6:
		bar_col = UIThemeManager.color("text_heal")
	elif _hp_ratio > 0.3:
		bar_col = UIThemeManager.color("hp_bar_mid")
	else:
		bar_col = UIThemeManager.color("text_danger")
	var fill_w = int((cell_size - 2) * _hp_ratio)
	if fill_w > 0:
		var fill_tex = _get_cell_tex("hp_bar_fill")
		if fill_tex:
			draw_texture_rect(fill_tex, Rect2(1, bar_y, fill_w, bar_h), false, bar_col)
		else:
			draw_rect(Rect2(1, bar_y, fill_w, bar_h), bar_col)
	# Slim outline for clarity
	draw_rect(Rect2(1, bar_y, cell_size - 2, bar_h), UIThemeManager.color("shadow_color"), false, 1.0)

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
	if BossGrid.atlas_cols <= 0 or BossGrid.atlas_rows <= 0:
		return null
	var tile_w = int(tex.get_width()  / float(BossGrid.atlas_cols))
	var tile_h = int(tex.get_height() / float(BossGrid.atlas_rows))
	var region = Rect2(local_pos.x * tile_w, local_pos.y * tile_h, tile_w, tile_h)
	if region.position.x + tile_w > tex.get_width() or region.position.y + tile_h > tex.get_height():
		return null
	var atlas = AtlasTexture.new()
	atlas.atlas = tex
	atlas.region = region
	return atlas

func _show_boss_info(extra: Dictionary):
	var part = extra.get("part", BossGrid.BodyPart.NONE)
	var hp = extra.get("hp", 0)
	var max_hp = extra.get("max_hp", 1)
	var part_name = ""
	match part:
		BossGrid.BodyPart.HEAD: part_name = "头部"
		BossGrid.BodyPart.LEG:  part_name = "腿部"
		BossGrid.BodyPart.CORE: part_name = "核心"
		_: part_name = "身体"
	tooltip_text = "%s  HP: %d/%d" % [part_name, hp, max_hp]

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
	pivot_offset = size / 2
	var tween = create_tween()
	if delay > 0.0:
		tween.tween_interval(delay)
	# Flash white-yellow then punch scale
	tween.tween_property(self, "modulate", Color(3.0, 2.5, 0.5), 0.04)
	tween.parallel().tween_property(self, "scale", Vector2(1.15, 1.15), 0.04)
	tween.tween_property(self, "scale", Vector2(0.92, 0.92), 0.06).set_trans(Tween.TRANS_CUBIC)
	tween.tween_property(self, "scale", Vector2.ONE, 0.15).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(self, "modulate", Color.WHITE, 0.35)

func animate_placement():
	pivot_offset = size / 2
	scale = Vector2(0.5, 0.5)
	modulate = Color(1.5, 1.5, 0.8)
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "scale", Vector2(1.08, 1.08), 0.12)
	tween.parallel().tween_property(self, "modulate", Color.WHITE, 0.15)
	tween.tween_property(self, "scale", Vector2.ONE, 0.08)

func animate_destruction():
	pivot_offset = size / 2
	var tween = create_tween()
	tween.tween_property(self, "modulate", Color(1.5, 0.5, 0.3), 0.06)
	tween.parallel().tween_property(self, "scale", Vector2(1.1, 1.1), 0.06)
	tween.tween_property(self, "scale", Vector2(0.5, 0.5), 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.parallel().tween_property(self, "modulate", Color(0.5, 0.2, 0.1, 0.5), 0.2)

func animate_boss_death(delay: float = 0.0):
	pivot_offset = size / 2
	var tween = create_tween()
	if delay > 0.0:
		tween.tween_interval(delay)
	# 先闪白
	tween.tween_property(self, "modulate", Color(4.0, 3.5, 1.5, 1.0), 0.06)
	# 膨胀
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2(1.3, 1.3), 0.12).set_trans(Tween.TRANS_BACK)
	tween.tween_property(self, "modulate", Color(1.5, 0.4, 0.1, 1.0), 0.12)
	tween.set_parallel(false)
	# 爆裂缩小 + 旋转
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2(0.0, 0.0), 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "modulate", Color(0.5, 0.1, 0.0, 0.0), 0.25)
	tween.tween_property(self, "rotation", randf_range(-0.5, 0.5), 0.25)
	await tween.finished

func animate_reveal():
	pivot_offset = size / 2
	scale = Vector2(0.0, 0.0)
	rotation = -0.15
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2.ONE, 0.2)
	tween.tween_property(self, "rotation", 0.0, 0.2)

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
	s.shadow_color = UIThemeManager.color("shadow_color")
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

func _apply_tex_or_flat(tex_key: String, fallback_bg: Color, border: Color, border_w: int):
	var tex = _get_cell_tex(tex_key)
	if tex == null:
		_apply_style(fallback_bg, border, border_w)
		return
	var s = StyleBoxTexture.new()
	s.texture = tex
	s.modulate_color = Color.WHITE
	add_theme_stylebox_override("normal", s)
	var h_box = StyleBoxTexture.new()
	h_box.texture = tex
	h_box.modulate_color = Color(1.25, 1.25, 1.25, 1.0)
	add_theme_stylebox_override("hover", h_box)
	var p_box = StyleBoxTexture.new()
	p_box.texture = tex
	p_box.modulate_color = Color(0.9, 0.9, 0.9, 1.0)
	add_theme_stylebox_override("pressed", p_box)
	add_theme_stylebox_override("disabled", s)
