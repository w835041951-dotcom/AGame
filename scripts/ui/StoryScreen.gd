## 故事过场动画 - 8bit 序列帧 + 打字机效果
## 播放完后自动切换到主游戏或由回调触发

extends Control

signal story_finished

# 每帧数据：图片路径 + 对白文本 + 显示时长
const STORY_FRAMES = [
	{
		"image":    "res://assets/sprites/story/story_01_kingdom.png",
		"lines":    ["从前，有一个宁静的王国……", "国王与公主居住在古老的城堡之中。"],
		"duration": 4.0,
		"sfx":      "mine_reveal",
	},
	{
		"image":    "res://assets/sprites/story/story_02_kidnap.png",
		"lines":    ["直到某一天——", "魔王统领军队，降临王国！", "公主被掳走关入了最深的地牢……"],
		"duration": 4.5,
		"sfx":      "boss_hit",
	},
	{
		"image":    "res://assets/sprites/story/story_02b_bombs_stolen.png",
		"lines":    ["魔王夺走了所有的炸弹！", "王国陷入了无力反抗的绝望……"],
		"duration": 4.0,
		"sfx":      "mine_bomb",
	},
	{
		"image":    "res://assets/sprites/story/story_03_hero.png",
		"lines":    ["此时，一位奇特的英雄挺身而出。", "他是炸弹人——炸弹领域的绝世高手。", "「我来救出公主！」"],
		"duration": 4.5,
		"sfx":      "bomb_place",
	},
	{
		"image":    "res://assets/sprites/story/story_04_dungeon.png",
		"lines":    ["地牢深处，暗雷遍布……", "翻开地块，找到炸弹，", "一层又一层，向魔王杀去！"],
		"duration": 4.5,
		"sfx":      "mine_bomb",
	},
	{
		"image":    "res://assets/sprites/story/story_05_victory.png",
		"lines":    ["也许有一天……", "炸弹和勇气能拯救一切。", "勇敢的冒险者，出发吧！"],
		"duration": 4.0,
		"sfx":      "upgrade_pick",
	},
]

const CHAR_DELAY  = 0.04   # 打字机每字间隔
const LINE_DELAY  = 0.6    # 两行之间停顿

var _frame_idx:   int   = 0
var _skip_pressed: bool = false

@onready var bg_rect:    TextureRect = $BG
@onready var text_box:   Panel       = $TextBox
@onready var text_label: Label       = $TextBox/Label
@onready var skip_label: Label       = $SkipLabel
@onready var frame_num:  Label       = $FrameNum

func _ready():
	_setup_ui()
	_play_frame(0)

func _setup_ui():
	set_anchors_preset(Control.PRESET_FULL_RECT)
	# 全屏黑底
	var bg_fill = ColorRect.new()
	bg_fill.color = Color(0, 0, 0, 1)
	bg_fill.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg_fill)
	move_child(bg_fill, 0)

func _input(event):
	if event is InputEventKey and event.pressed and not event.echo:
		_on_skip()
	if event is InputEventMouseButton and event.pressed:
		_on_skip()

func _on_skip():
	# 如果正在打字，先跳到文字末尾；否则跳到下一帧
	if _typing:
		_skip_typing = true
	else:
		_advance_frame()

# ─── 帧播放 ───────────────────────────────────────────────────

var _typing:      bool = false
var _skip_typing: bool = false

func _play_frame(idx: int):
	if idx >= STORY_FRAMES.size():
		_finish()
		return

	_frame_idx = idx
	var data    = STORY_FRAMES[idx]

	# 图片切换（淡入）
	bg_rect.modulate = Color(0, 0, 0, 0)
	if ResourceLoader.exists(data["image"]):
		bg_rect.texture = load(data["image"])
	var tw = create_tween()
	tw.tween_property(bg_rect, "modulate", Color.WHITE, 0.4)
	await tw.finished

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
	tw.tween_property(bg_rect, "modulate", Color(0, 0, 0, 0), 0.3)
	await tw.finished
	_play_frame(_frame_idx + 1)

func _typewrite_lines(lines: Array):
	text_label.text = ""
	_typing = true
	_skip_typing = false
	var full_text = ""

	for i in range(lines.size()):
		var line = lines[i]
		if i > 0:
			full_text += "\n"
			if not _skip_typing:
				await get_tree().create_timer(LINE_DELAY).timeout

		for ch in line:
			if _skip_typing:
				break
			full_text += ch
			text_label.text = full_text
			await get_tree().create_timer(CHAR_DELAY).timeout

		if _skip_typing:
			break

	# 跳过时直接显示全部
	if _skip_typing:
		text_label.text = "\n".join(lines)

	_typing = false
	_skip_typing = false

func _finish():
	var tw = create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.5)
	await tw.finished
	story_finished.emit()
	get_tree().change_scene_to_file("res://scenes/ui/TitleScreen.tscn")
