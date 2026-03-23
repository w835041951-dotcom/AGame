## 故事过场动画 - 8bit 序列帧 + 打字机效果 + 动态特效
## 播放完后自动切换到主游戏或由回调触发

extends Control

signal story_finished

# 每帧数据：图片路径 + 对白文本 + 显示时长 + 特效
const STORY_FRAMES = [
	{
		"image":    "res://assets/sprites/story/story_01_world.png",
		"lines":    [
			"传说，世界由十座浮空之境相连。",
			"竹林、齿轮、深海、熔岩、月华……",
			"万物在此共生，岁月静好。",
		],
		"duration": 3.5,
		"sfx":      "mine_reveal",
		"effect":   "pan_right",
		"particles": "firefly",
	},
	{
		"image":    "res://assets/sprites/story/story_02_invasion.png",
		"lines":    [
			"直到——裂缝出现。",
			"虚空的力量渗入每一座境界。",
			"怪物从裂隙中涌出，十境陷入混乱。",
		],
		"duration": 4.0,
		"sfx":      "boss_hit",
		"effect":   "shake",
		"particles": "ember",
		"flash":    true,
	},
	{
		"image":    "res://assets/sprites/story/story_03_hero.png",
		"lines":    [
			"废墟之中，一个身影站了起来。",
			"炸弹人——唯一能引爆封印之力的人。",
			"",
			"「……交给我。」",
		],
		"duration": 4.0,
		"sfx":      "bomb_place",
		"effect":   "zoom_out",
		"particles": "dust",
	},
	{
		"image":    "res://assets/sprites/story/story_04_journey.png",
		"lines":    [
			"从竹林秘境出发，穿越十座境界。",
			"每一层，都有沉睡的炸弹和觉醒的守卫。",
			"探索、收集、引爆——",
			"这就是前进的唯一方式。",
		],
		"duration": 4.0,
		"sfx":      "mine_bomb",
		"effect":   "pan_down",
		"particles": "dust",
	},
	{
		"image":    "res://assets/sprites/story/story_05_victory.png",
		"lines":    [
			"每击败一个守卫，封印便松动一分。",
			"力量在积累，希望在生长。",
		],
		"duration": 3.5,
		"sfx":      "upgrade_pick",
		"effect":   "zoom_in",
		"particles": "sparkle",
	},
	{
		"image":    "res://assets/sprites/story/story_06_final.png",
		"lines":    [
			"当十境之门全部打开——",
			"虚空深渊的虚空神将在终焉等待。",
			"",
			"无论结局如何，",
			"踏出这一步的人——不需要理由。",
		],
		"duration": 4.5,
		"sfx":      "upgrade_pick",
		"effect":   "zoom_in",
		"particles": "sparkle",
		"flash":    true,
	},
]

const CHAR_DELAY       = 0.04
const CHAR_DELAY_WHISPER = 0.07
const LINE_DELAY       = 0.6

var _frame_idx:   int   = 0
var _skip_pressed: bool = false

@onready var bg_rect:    TextureRect    = $BG
@onready var text_box:   Panel          = $TextBox
@onready var text_label: RichTextLabel  = $TextBox/Label
@onready var skip_label: Label          = $SkipLabel
@onready var frame_num:  Label          = $FrameNum

# ── 动态特效状态 ──
var _effect_type: String = ""
var _effect_time: float = 0.0
var _particles: Array = []  # [{pos, vel, life, max_life, color, size}]
var _particle_type: String = ""
var _flash_rect: ColorRect = null
var _vignette_rect: ColorRect = null

func _ready():
	_setup_ui()
	_play_frame(0)

func _setup_ui():
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg_fill = ColorRect.new()
	bg_fill.color = Color(0, 0, 0, 1)
	bg_fill.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg_fill)
	move_child(bg_fill, 0)

	# 闪白层
	_flash_rect = ColorRect.new()
	_flash_rect.color = Color(1, 1, 1, 0)
	_flash_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_flash_rect)

	# 暗角层
	_vignette_rect = ColorRect.new()
	_vignette_rect.color = Color(0, 0, 0, 0)
	_vignette_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_vignette_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_vignette_rect.material = _create_vignette_material()
	add_child(_vignette_rect)

func _create_vignette_material() -> ShaderMaterial:
	var shader = Shader.new()
	shader.code = """
shader_type canvas_item;
void fragment() {
	vec2 uv = UV - vec2(0.5);
	float d = length(uv) * 1.6;
	float vig = smoothstep(0.3, 1.2, d);
	COLOR = vec4(0.0, 0.0, 0.0, vig * 0.65);
}
"""
	var mat = ShaderMaterial.new()
	mat.shader = shader
	return mat

func _input(event):
	if event is InputEventKey and event.pressed and not event.echo:
		_on_skip()
	if event is InputEventMouseButton and event.pressed:
		_on_skip()

func _on_skip():
	if _typing:
		_skip_typing = true
	else:
		_advance_frame()

# ── 粒子系统 ─────────────────────────────────────────────────

func _spawn_particles(type: String):
	_particle_type = type
	_particles.clear()
	for i in range(40):
		_particles.append(_new_particle(type, true))

func _new_particle(type: String, random_life: bool = false) -> Dictionary:
	var p = {
		"pos": Vector2(randf_range(0, 1920), randf_range(0, 1080)),
		"vel": Vector2.ZERO,
		"life": 0.0,
		"max_life": randf_range(2.0, 5.0),
		"color": Color.WHITE,
		"size": 3.0,
	}
	match type:
		"firefly":
			p["pos"] = Vector2(randf_range(0, 1920), randf_range(500, 1000))
			p["vel"] = Vector2(randf_range(-15, 15), randf_range(-25, -5))
			p["color"] = Color(0.7, 1.0, 0.4, 0.0)
			p["size"] = randf_range(2, 5)
			p["max_life"] = randf_range(3.0, 6.0)
		"ember":
			p["pos"] = Vector2(randf_range(0, 1920), randf_range(700, 1080))
			p["vel"] = Vector2(randf_range(-30, 30), randf_range(-80, -30))
			p["color"] = Color(1.0, randf_range(0.3, 0.7), 0.1, 0.0)
			p["size"] = randf_range(2, 4)
			p["max_life"] = randf_range(1.5, 3.5)
		"dark_ash":
			p["pos"] = Vector2(randf_range(0, 1920), randf_range(-50, 0))
			p["vel"] = Vector2(randf_range(-10, 10), randf_range(15, 40))
			p["color"] = Color(0.25, 0.18, 0.3, 0.0)
			p["size"] = randf_range(3, 7)
			p["max_life"] = randf_range(3.0, 6.0)
		"dust":
			p["pos"] = Vector2(randf_range(0, 1920), randf_range(0, 1080))
			p["vel"] = Vector2(randf_range(-5, 5), randf_range(-3, 3))
			p["color"] = Color(0.8, 0.75, 0.65, 0.0)
			p["size"] = randf_range(1, 3)
			p["max_life"] = randf_range(3.0, 7.0)
		"sparkle":
			p["pos"] = Vector2(randf_range(100, 1820), randf_range(100, 800))
			p["vel"] = Vector2(randf_range(-8, 8), randf_range(-20, -5))
			var gold = randf_range(0.0, 1.0)
			p["color"] = Color(1.0, 0.85 + gold * 0.15, 0.2 + gold * 0.3, 0.0)
			p["size"] = randf_range(2, 5)
			p["max_life"] = randf_range(1.0, 3.0)
	if random_life:
		p["life"] = randf_range(0, p["max_life"] * 0.8)
	return p

func _process(delta):
	_effect_time += delta
	# 镜头动态
	_apply_camera_effect(delta)
	# 粒子更新
	_update_particles(delta)
	queue_redraw()

func _apply_camera_effect(_delta: float):
	var t = _effect_time
	match _effect_type:
		"pan_right":
			bg_rect.position.x = -t * 8.0  # 缓慢右移
		"pan_down":
			bg_rect.position.y = -t * 6.0
		"zoom_in":
			var s = 1.0 + t * 0.012
			bg_rect.scale = Vector2(s, s)
			bg_rect.position = Vector2(-960 * (s - 1), -540 * (s - 1))
		"zoom_out":
			var s = 1.08 - t * 0.01
			s = max(s, 1.0)
			bg_rect.scale = Vector2(s, s)
			bg_rect.position = Vector2(-960 * (s - 1), -540 * (s - 1))
		"shake":
			if t < 1.5:
				var intensity = max(0, 12.0 - t * 8.0)
				bg_rect.position = Vector2(
					randf_range(-intensity, intensity),
					randf_range(-intensity, intensity)
				)
			else:
				bg_rect.position = Vector2.ZERO

func _update_particles(delta: float):
	var to_remove = []
	for i in range(_particles.size()):
		var p = _particles[i]
		p["life"] += delta
		p["pos"] += p["vel"] * delta
		# 萤火虫飘动
		if _particle_type == "firefly":
			p["vel"].x += randf_range(-20, 20) * delta
			p["vel"].y += randf_range(-10, 10) * delta
		# 淡入淡出
		var t = p["life"] / p["max_life"]
		if t < 0.2:
			p["color"].a = t / 0.2
		elif t > 0.7:
			p["color"].a = (1.0 - t) / 0.3
		else:
			p["color"].a = 1.0
		if p["life"] >= p["max_life"]:
			to_remove.append(i)
	# 重生粒子
	for i in range(to_remove.size() - 1, -1, -1):
		_particles[to_remove[i]] = _new_particle(_particle_type)

func _draw():
	for p in _particles:
		if p["color"].a > 0.01:
			var r = p["size"]
			draw_circle(p["pos"], r, p["color"])
			# 发光效果
			if _particle_type in ["firefly", "ember", "sparkle"]:
				var glow_col = Color(p["color"].r, p["color"].g, p["color"].b, p["color"].a * 0.3)
				draw_circle(p["pos"], r * 2.5, glow_col)

# ── 帧播放 ───────────────────────────────────────────────────

var _typing:      bool = false
var _skip_typing: bool = false

func _play_frame(idx: int):
	if idx >= STORY_FRAMES.size():
		_finish()
		return

	_frame_idx = idx
	var data = STORY_FRAMES[idx]

	# 重置镜头
	bg_rect.position = Vector2.ZERO
	bg_rect.scale = Vector2.ONE
	_effect_type = data.get("effect", "")
	_effect_time = 0.0

	# 图片切换（淡入）
	bg_rect.modulate = Color(0, 0, 0, 0)
	if ResourceLoader.exists(data["image"]):
		bg_rect.texture = load(data["image"])
	var tw = create_tween()
	tw.tween_property(bg_rect, "modulate", Color.WHITE, 0.5)

	# 闪白效果
	if data.get("flash", false):
		_flash_rect.color = Color(1, 1, 1, 0.7)
		var flash_tw = create_tween()
		flash_tw.tween_property(_flash_rect, "color:a", 0.0, 0.6)

	await tw.finished

	# 启动粒子
	var pt = data.get("particles", "")
	if pt != "":
		_spawn_particles(pt)
	else:
		_particles.clear()

	# 帧序号
	frame_num.text = "%d / %d" % [idx + 1, STORY_FRAMES.size()]

	# 音效
	if data.get("sfx", "") != "":
		AudioManager.play_sfx(data["sfx"])

	# 逐行打字
	await _typewrite_lines(data["lines"])

	# 停留后自动跳下一帧
	await get_tree().create_timer(data["duration"]).timeout
	_advance_frame()

func _advance_frame():
	if _frame_idx + 1 >= STORY_FRAMES.size():
		_finish()
		return
	var tw = create_tween()
	tw.tween_property(bg_rect, "modulate", Color(0, 0, 0, 0), 0.35)
	await tw.finished
	_play_frame(_frame_idx + 1)

func _typewrite_lines(lines: Array):
	text_label.text = ""
	_typing = true
	_skip_typing = false
	var bbcode = ""

	for i in range(lines.size()):
		var line = lines[i]
		if i > 0:
			bbcode += "\n"
			if not _skip_typing:
				await get_tree().create_timer(LINE_DELAY).timeout

		var is_whisper = _is_whisper_line(line)
		var delay = CHAR_DELAY_WHISPER if is_whisper else CHAR_DELAY
		var prefix = "[color=#6a5a8a][i]" if is_whisper else ""
		var suffix = "[/i][/color]" if is_whisper else ""

		if is_whisper:
			bbcode += prefix

		for ch in line:
			if _skip_typing:
				break
			bbcode += ch
			text_label.text = bbcode + (suffix if is_whisper else "")
			await get_tree().create_timer(delay).timeout

		if _skip_typing:
			break

		if is_whisper:
			bbcode += suffix

	# 跳过时直接显示全部
	if _skip_typing:
		text_label.text = _build_full_bbcode(lines)

	_typing = false
	_skip_typing = false

func _build_full_bbcode(lines: Array) -> String:
	var result = ""
	for i in range(lines.size()):
		if i > 0:
			result += "\n"
		var line = lines[i]
		if _is_whisper_line(line):
			result += "[color=#6a5a8a][i]" + line + "[/i][/color]"
		else:
			result += line
	return result

func _is_whisper_line(line: String) -> bool:
	return line.begins_with("\u2026") and line.length() > 1 and line.find("'") >= 0

func _finish():
	_particles.clear()
	_effect_type = ""
	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.5)
	await tw.finished
	story_finished.emit()
	get_tree().change_scene_to_file("res://scenes/ui/TitleScreen.tscn")
