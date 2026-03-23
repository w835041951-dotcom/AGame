## 游戏设置管理器 - AutoLoad
## 管理分辨率、窗口模式、帧率、垂直同步、音量等设置

extends Node

signal settings_changed

const SAVE_PATH = "user://game_settings.cfg"

# ── 分辨率选项 ──
const RESOLUTIONS = [
	Vector2i(1280, 720),
	Vector2i(1600, 900),
	Vector2i(1920, 1080),
	Vector2i(2560, 1440),
]
const RESOLUTION_LABELS = ["1280×720", "1600×900", "1920×1080", "2560×1440"]

# ── 帧率选项 ──
const FPS_OPTIONS = [30, 60, 120, 0]  # 0 = 不限制
const FPS_LABELS  = ["30 FPS", "60 FPS", "120 FPS", "不限制"]

# ── 当前设置 ──
var resolution_index: int = 2      # 默认 1920×1080
var fullscreen: bool = false
var fps_index: int = 1             # 默认 60 FPS
var vsync_on: bool = true
var music_volume: float = 0.7      # 0.0 ~ 1.0
var sfx_volume: float = 1.0        # 0.0 ~ 1.0

# ── 难度选项 ──
const DIFFICULTY_LABELS = ["简单", "普通", "困难"]
var difficulty: int = 1            # 0=简单, 1=普通, 2=困难（旧系统保留兼容）

# ── 自定义难度滑块 ──
# mine_difficulty: 扫雷难度倍率 (0.5=超简单, 1.0=标准, 3.0=地狱)
#   影响：雷数、格子大小、点击次数
var mine_difficulty: float = 1.0
# boss_hp_mult: Boss血量倍率 (0.5=纸糊, 1.0=标准, 5.0=铁壁)
#   影响：每格血量
var boss_hp_mult: float = 1.0

func _ready():
	_load()
	_apply_all()

# ── 应用设置 ──

func _apply_all():
	_apply_window_mode()
	_apply_resolution()
	_apply_fps()
	_apply_vsync()
	_apply_audio()

func _apply_window_mode():
	if fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		_apply_resolution()

func _apply_resolution():
	if fullscreen:
		return
	var res = RESOLUTIONS[resolution_index]
	DisplayServer.window_set_size(res)
	# 居中窗口
	var screen_size = DisplayServer.screen_get_size()
	var pos = (screen_size - res) / 2
	DisplayServer.window_set_position(pos)

func _apply_fps():
	Engine.max_fps = FPS_OPTIONS[fps_index]

func _apply_vsync():
	DisplayServer.window_set_vsync_mode(
		DisplayServer.VSYNC_ENABLED if vsync_on else DisplayServer.VSYNC_DISABLED
	)

func _apply_audio():
	AudioManager.set_music_volume(music_volume)
	AudioManager.set_sfx_volume(sfx_volume)

# ── 设置修改接口 ──

func set_resolution(idx: int):
	resolution_index = clampi(idx, 0, RESOLUTIONS.size() - 1)
	_apply_resolution()
	_save()
	settings_changed.emit()

func set_fullscreen(on: bool):
	fullscreen = on
	_apply_window_mode()
	_save()
	settings_changed.emit()

func set_fps(idx: int):
	fps_index = clampi(idx, 0, FPS_OPTIONS.size() - 1)
	_apply_fps()
	_save()
	settings_changed.emit()

func set_vsync(on: bool):
	vsync_on = on
	_apply_vsync()
	_save()
	settings_changed.emit()

func set_music_volume(val: float):
	music_volume = clampf(val, 0.0, 1.0)
	_apply_audio()
	_save()

func set_sfx_volume(val: float):
	sfx_volume = clampf(val, 0.0, 1.0)
	_apply_audio()
	_save()

func set_difficulty(idx: int):
	difficulty = clampi(idx, 0, DIFFICULTY_LABELS.size() - 1)
	# 同步滑块到预设值
	match difficulty:
		0: mine_difficulty = 0.7; boss_hp_mult = 0.7
		1: mine_difficulty = 1.0; boss_hp_mult = 1.0
		2: mine_difficulty = 1.5; boss_hp_mult = 1.5
	_save()
	settings_changed.emit()

func set_mine_difficulty(val: float):
	mine_difficulty = clampf(val, 0.3, 3.0)
	difficulty = -1  # 自定义
	_save()
	settings_changed.emit()

func set_boss_hp_mult(val: float):
	boss_hp_mult = clampf(val, 0.3, 5.0)
	difficulty = -1  # 自定义
	_save()
	settings_changed.emit()

func get_difficulty_label() -> String:
	if difficulty >= 0 and difficulty < DIFFICULTY_LABELS.size():
		return DIFFICULTY_LABELS[difficulty]
	return "自定义"

# ── 持久化 ──

func _save():
	var cfg = ConfigFile.new()
	cfg.set_value("display", "resolution_index", resolution_index)
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.set_value("display", "fps_index", fps_index)
	cfg.set_value("display", "vsync", vsync_on)
	cfg.set_value("audio", "music_volume", music_volume)
	cfg.set_value("audio", "sfx_volume", sfx_volume)
	cfg.set_value("gameplay", "difficulty", difficulty)
	cfg.set_value("gameplay", "mine_difficulty", mine_difficulty)
	cfg.set_value("gameplay", "boss_hp_mult", boss_hp_mult)
	cfg.save(SAVE_PATH)

func _load():
	var cfg = ConfigFile.new()
	if cfg.load(SAVE_PATH) != OK:
		return
	resolution_index = cfg.get_value("display", "resolution_index", 2)
	fullscreen = cfg.get_value("display", "fullscreen", false)
	fps_index = cfg.get_value("display", "fps_index", 1)
	vsync_on = cfg.get_value("display", "vsync", true)
	music_volume = cfg.get_value("audio", "music_volume", 0.7)
	sfx_volume = cfg.get_value("audio", "sfx_volume", 1.0)
	difficulty = cfg.get_value("gameplay", "difficulty", 1)
	mine_difficulty = cfg.get_value("gameplay", "mine_difficulty", 1.0)
	boss_hp_mult = cfg.get_value("gameplay", "boss_hp_mult", 1.0)
