## 音频管理器 - AutoLoad
## 管理 BGM 和音效的播放、音量、切换

extends Node

# ---- 音频总线 ----
# 使用 Godot 默认的 Master/Music/SFX 总线
# 需要在 Project > Audio Buses 里创建 Music 和 SFX 两条总线

@onready var bgm_player: AudioStreamPlayer = $BGMPlayer
@onready var sfx_player: AudioStreamPlayer = $SFXPlayer

# 音量（0.0 ~ 1.0）
var music_volume: float = 0.7
var sfx_volume: float = 1.0

# BGM 文件路径映射
const BGM_TRACKS = {
	"battle":   "res://assets/audio/bgm/battle.wav",
	"boss":     "res://assets/audio/bgm/boss.wav",
	"upgrade":  "res://assets/audio/bgm/upgrade.wav",
	"gameover": "res://assets/audio/bgm/gameover.wav",
}

# 音效文件路径映射
const SFX_FILES = {
	"bomb_place":    "res://assets/audio/sfx/bomb_place.ogg",
	"bomb_remove":   "res://assets/audio/sfx/bomb_remove.ogg",
	"detonate":      "res://assets/audio/sfx/detonate.ogg",
	"explosion":     "res://assets/audio/sfx/explosion.ogg",
	"tile_break":    "res://assets/audio/sfx/tile_break.ogg",
	"boss_hit":      "res://assets/audio/sfx/boss_hit.ogg",
	"weak_hit":      "res://assets/audio/sfx/weak_hit.ogg",
	"chain":         "res://assets/audio/sfx/chain.ogg",
	"mine_reveal":   "res://assets/audio/sfx/mine_reveal.ogg",
	"mine_bomb":     "res://assets/audio/sfx/mine_bomb.ogg",
	"upgrade_pick":  "res://assets/audio/sfx/upgrade_pick.ogg",
	"boss_move":     "res://assets/audio/sfx/boss_move.ogg",
	"player_hit":    "res://assets/audio/sfx/player_hit.ogg",
	"ui_click":      "res://assets/audio/sfx/ui_click.ogg",
	"timer_warn":    "res://assets/audio/sfx/timer_warn.ogg",
}

var _current_bgm: String = ""
var _sfx_cache: Dictionary = {}  # 缓存已加载的音效

func _ready():
	_ensure_bus("Music")
	_ensure_bus("SFX")
	bgm_player.bus = "Music"
	sfx_player.bus = "SFX"
	_set_bus_volume("Music", music_volume)
	_set_bus_volume("SFX", sfx_volume)
	bgm_player.finished.connect(_on_bgm_finished)

func _ensure_bus(bus_name: String):
	if AudioServer.get_bus_index(bus_name) == -1:
		AudioServer.add_bus()
		var idx = AudioServer.bus_count - 1
		AudioServer.set_bus_name(idx, bus_name)
		AudioServer.set_bus_send(idx, "Master")

# ---- BGM ----

func play_bgm(track_name: String, crossfade: bool = true):
	if _current_bgm == track_name:
		return
	_current_bgm = track_name
	var path = BGM_TRACKS.get(track_name, "")
	if path == "" or not ResourceLoader.exists(path):
		return
	var stream = load(path)
	# 确保BGM循环播放
	if stream is AudioStreamWAV:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	elif stream is AudioStreamOggVorbis:
		stream.loop = true
	if crossfade and bgm_player.playing:
		await _fade_out(bgm_player, 0.5)
	bgm_player.stream = stream
	bgm_player.play()
	if crossfade:
		await _fade_in(bgm_player, 0.5)

func stop_bgm(fade: bool = true):
	if fade:
		await _fade_out(bgm_player, 0.5)
	bgm_player.stop()
	_current_bgm = ""

func _on_bgm_finished():
	# 如果BGM意外结束（流未循环），自动重播
	if _current_bgm != "" and bgm_player.stream:
		bgm_player.play()

# ---- 音效 ----

const MAX_SFX_POLYPHONY: int = 6  # 最多同时播放音效数

func play_sfx(sfx_name: String):
	var path = SFX_FILES.get(sfx_name, "")
	if path == "" or not ResourceLoader.exists(path):
		return
	if sfx_name not in _sfx_cache:
		_sfx_cache[sfx_name] = load(path)
	# 限制同时播放的音效数量，防止爆音/杂音
	var active_sfx := 0
	var oldest: AudioStreamPlayer = null
	for child in get_children():
		if child is AudioStreamPlayer and child != bgm_player and child != sfx_player:
			active_sfx += 1
			if oldest == null:
				oldest = child
	if active_sfx >= MAX_SFX_POLYPHONY:
		if oldest:
			oldest.stop()
			oldest.queue_free()
	var player = AudioStreamPlayer.new()
	player.bus = "SFX"
	player.stream = _sfx_cache[sfx_name]
	player.volume_db = linear_to_db(sfx_volume)
	add_child(player)
	player.play()
	player.finished.connect(player.queue_free)
	# 安全保底：3秒后强制清理（防止finished信号未触发）
	get_tree().create_timer(3.0).timeout.connect(func():
		if is_instance_valid(player) and player.is_inside_tree():
			player.queue_free()
	)

# ---- 音量控制 ----

func set_music_volume(val: float):
	music_volume = clamp(val, 0.0, 1.0)
	_set_bus_volume("Music", music_volume)

func set_sfx_volume(val: float):
	sfx_volume = clamp(val, 0.0, 1.0)
	_set_bus_volume("SFX", sfx_volume)

func _set_bus_volume(bus_name: String, linear: float):
	var idx = AudioServer.get_bus_index(bus_name)
	if idx >= 0:
		AudioServer.set_bus_volume_db(idx, linear_to_db(linear))

# ---- 淡入/淡出 ----

func _fade_out(player: AudioStreamPlayer, duration: float):
	var tween = create_tween()
	tween.tween_property(player, "volume_db", -80.0, duration)
	await tween.finished

func _fade_in(player: AudioStreamPlayer, duration: float):
	player.volume_db = -80.0
	var tween = create_tween()
	tween.tween_property(player, "volume_db", 0.0, duration)
	await tween.finished
