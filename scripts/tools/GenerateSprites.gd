## 占位精灵图生成器
## 在 Godot 编辑器中：Tools > Execute Script（或直接在场景里挂到节点上运行一次）
## 生成所有游戏所需的像素风占位图，保存到 assets/sprites/

@tool
extends EditorScript

func _run():
	var base = "res://assets/sprites/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(base + "bombs"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(base + "boss"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(base + "ui"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(base + "vfx"))

	_gen_bombs(base + "bombs/")
	_gen_boss_tiles(base + "boss/")
	_gen_ui(base + "ui/")
	_gen_explosion(base + "vfx/")

	print("=== Sprite generation complete ===")

# ---- 炸弹图标 32x32 ----
func _gen_bombs(dir: String):
	var defs = {
		"cross":   [Color(0.9, 0.15, 0.15), "+"],
		"scatter": [Color(1.0, 0.55, 0.05), "*"],
		"bounce":  [Color(0.1, 0.85, 0.85), "~"],
		"pierce":  [Color(1.0, 0.95, 0.1),  "|"],
		"area":    [Color(0.7, 0.1, 0.9),   "#"],
	}
	for bomb_type in defs:
		var col: Color = defs[bomb_type][0]
		var img = Image.create(32, 32, false, Image.FORMAT_RGBA8)
		img.fill(Color(0, 0, 0, 0))
		# 外圆
		_draw_circle(img, 16, 16, 12, col.darkened(0.3))
		# 内圆高亮
		_draw_circle(img, 15, 14, 8, col)
		# 高光点
		_draw_rect_img(img, 12, 10, 4, 3, col.lightened(0.5))
		# 引线
		_draw_rect_img(img, 21, 4, 2, 6, Color(0.8, 0.7, 0.2))
		_save(img, dir + bomb_type + ".png")
	print("Bombs generated")

# ---- Boss 格子 64x64 ----
func _gen_boss_tiles(dir: String):
	var tiles = {
		"normal":  [Color(0.45, 0.12, 0.12), Color(0.8, 0.2, 0.2), 2],
		"weak":    [Color(0.20, 0.18, 0.05), Color(1.0, 0.9, 0.1), 3],
		"armor":   [Color(0.18, 0.22, 0.35), Color(0.5, 0.6, 0.9), 3],
		"absorb":  [Color(0.10, 0.30, 0.15), Color(0.2, 0.9, 0.4), 2],
		"dead":    [Color(0.08, 0.08, 0.08), Color(0.3, 0.3, 0.3), 1],
	}
	for name in tiles:
		var bg: Color = tiles[name][0]
		var border: Color = tiles[name][1]
		var bw: int = tiles[name][2]
		var img = Image.create(64, 64, false, Image.FORMAT_RGBA8)
		img.fill(bg)
		_draw_border(img, border, bw)
		# dead 格子加 X
		if name == "dead":
			_draw_x(img, Color(0.4, 0.4, 0.4))
		# weak 格子加裂纹效果
		if name == "weak":
			_draw_cracks(img, Color(1.0, 0.7, 0.0, 0.6))
		# armor 格子加铆钉
		if name == "armor":
			for pos in [Vector2i(8,8), Vector2i(56,8), Vector2i(8,56), Vector2i(56,56)]:
				_draw_circle(img, pos.x, pos.y, 4, Color(0.6, 0.7, 1.0))
		_save(img, dir + "tile_" + name + ".png")

	# 关键部位图标 32x32
	_gen_part_icon(dir + "part_head.png", Color(0.9, 0.2, 0.2), "H")
	_gen_part_icon(dir + "part_leg.png",  Color(0.2, 0.5, 0.9), "L")
	_gen_part_icon(dir + "part_core.png", Color(0.9, 0.7, 0.1), "C")
	print("Boss tiles generated")

func _gen_part_icon(path: String, col: Color, _label: String):
	var img = Image.create(32, 32, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	_draw_circle(img, 16, 16, 12, col.darkened(0.3))
	_draw_circle(img, 16, 16, 8,  col)
	_draw_border(img, col.lightened(0.3), 2)
	_save(img, path)

# ---- UI 格子 32x32 ----
func _gen_ui(dir: String):
	var states = {
		"cell_empty":       [Color(0.25, 0.25, 0.30), Color(0.5, 0.5, 0.55)],
		"cell_mine_hidden": [Color(0.30, 0.30, 0.35), Color(0.5, 0.5, 0.55)],
		"cell_mine_reveal": [Color(0.78, 0.75, 0.68), Color(0.55, 0.52, 0.46)],
		"cell_exploding":   [Color(1.0,  0.45, 0.05), Color(1.0, 0.7, 0.0)],
	}
	for name in states:
		var bg: Color = states[name][0]
		var border: Color = states[name][1]
		var img = Image.create(32, 32, false, Image.FORMAT_RGBA8)
		img.fill(bg)
		_draw_border(img, border, 1)
		_save(img, dir + name + ".png")
	print("UI cells generated")

# ---- 爆炸特效 Spritesheet 256x32 (8帧) ----
func _gen_explosion(dir: String):
	var img = Image.create(256, 32, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for frame in range(8):
		var cx = frame * 32 + 16
		var cy = 16
		var progress = float(frame) / 7.0
		var radius = int(lerp(2.0, 14.0, progress))
		var alpha = 1.0 - progress * 0.6
		var col = Color(1.0, lerp(0.8, 0.1, progress), 0.0, alpha)
		_draw_circle_offset(img, cx, cy, radius, col)
		if radius > 4:
			_draw_circle_offset(img, cx, cy, radius - 3, Color(1.0, 1.0, 0.6, alpha))
	_save(img, dir + "explosion_strip8.png")
	print("VFX generated")

# ---- 底层绘图函数 ----

func _draw_circle(img: Image, cx: int, cy: int, r: int, col: Color):
	for y in range(cy - r, cy + r + 1):
		for x in range(cx - r, cx + r + 1):
			if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
				if x >= 0 and x < img.get_width() and y >= 0 and y < img.get_height():
					img.set_pixel(x, y, col)

func _draw_circle_offset(img: Image, cx: int, cy: int, r: int, col: Color):
	_draw_circle(img, cx, cy, r, col)

func _draw_rect_img(img: Image, x: int, y: int, w: int, h: int, col: Color):
	for py in range(y, y + h):
		for px in range(x, x + w):
			if px >= 0 and px < img.get_width() and py >= 0 and py < img.get_height():
				img.set_pixel(px, py, col)

func _draw_border(img: Image, col: Color, bw: int):
	var W = img.get_width()
	var H = img.get_height()
	for i in range(bw):
		for x in range(W):
			img.set_pixel(x, i, col)
			img.set_pixel(x, H - 1 - i, col)
		for y in range(H):
			img.set_pixel(i, y, col)
			img.set_pixel(W - 1 - i, y, col)

func _draw_x(img: Image, col: Color):
	var w = img.get_width()
	var h = img.get_height()
	for i in range(min(w, h)):
		var x1 = int(i * float(w) / h)
		var y1 = int(i * float(h) / w)
		for d in range(-2, 3):
			if x1 + d >= 0 and x1 + d < w:
				img.set_pixel(x1 + d, i, col)
			if w - 1 - x1 + d >= 0 and w - 1 - x1 + d < w:
				img.set_pixel(w - 1 - x1 + d, i, col)

func _draw_cracks(img: Image, col: Color):
	var w = img.get_width()
	var h = img.get_height()
	# 简单几条斜线模拟裂纹
	var cracks = [[10, 5, 25, 30], [35, 10, 50, 45], [20, 35, 40, 60]]
	for c in cracks:
		_draw_line_img(img, c[0], c[1], c[2], c[3], col)

func _draw_line_img(img: Image, x0: int, y0: int, x1: int, y1: int, col: Color):
	var dx = abs(x1 - x0)
	var dy = abs(y1 - y0)
	var sx = 1 if x0 < x1 else -1
	var sy = 1 if y0 < y1 else -1
	var err = dx - dy
	while true:
		if x0 >= 0 and x0 < img.get_width() and y0 >= 0 and y0 < img.get_height():
			img.set_pixel(x0, y0, col)
		if x0 == x1 and y0 == y1:
			break
		var e2 = 2 * err
		if e2 > -dy:
			err -= dy
			x0 += sx
		if e2 < dx:
			err += dx
			y0 += sy

func _save(img: Image, res_path: String):
	var abs_path = ProjectSettings.globalize_path(res_path)
	img.save_png(abs_path)
