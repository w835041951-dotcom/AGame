## 新手引导系统 - AutoLoad
## 首次游玩时在关键时刻显示提示气泡

extends Node

const SAVE_PATH = "user://tutorial.json"

var shown_tips: Dictionary = {}  # tip_id -> true
var _loaded: bool = false

# 所有提示定义
const TIPS = {
	"welcome": {
		"text": "欢迎来到炸弹人勇闯地牢！\n\n🔍 点击下方探索区翻格子找炸弹\n💣 将炸弹拖到上方战场攻击Boss\n⏱ 注意倒计时，时间到自动引爆！",
		"y": 320,
		"delay": 0.5,
	},
	"first_bomb": {
		"text": "💣 获得炸弹！\n从下方栏选择炸弹，点击战场放置\n不同炸弹有不同爆炸范围",
		"y": 500,
		"delay": 0.2,
	},
	"first_boss_attack": {
		"text": "⚠ Boss到达左边界会攻击你！\n尽快用炸弹消灭Boss格子\n关注HUD上的攻击预告",
		"y": 400,
		"delay": 0.1,
	},
	"first_upgrade": {
		"text": "🏆 击败Boss后可选择永久强化！\n强化效果整局有效，慎重选择",
		"y": 280,
		"delay": 0.3,
	},
	"chain_hint": {
		"text": "🔗 炸弹可以引爆其他炸弹形成连锁！\n尝试把炸弹放在彼此范围内",
		"y": 420,
		"delay": 0.2,
	},
}

func _ready():
	_load()

func has_shown(tip_id: String) -> bool:
	return shown_tips.has(tip_id)

func try_show(tip_id: String, parent: Node) -> bool:
	if has_shown(tip_id):
		return false
	if not TIPS.has(tip_id):
		return false
	shown_tips[tip_id] = true
	_save()
	var tip = TIPS[tip_id]
	_display_tip(tip["text"], tip["y"], tip.get("delay", 0.3), parent)
	return true

func _display_tip(text: String, y_pos: float, delay: float, parent: Node):
	var canvas = CanvasLayer.new()
	canvas.layer = 92
	parent.add_child(canvas)

	var overlay = ColorRect.new()
	overlay.color = Color(0, 0, 0, 0.0)
	overlay.size = Vector2(1920, 1080)
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.add_child(overlay)

	var panel = PanelContainer.new()
	panel.position = Vector2(460, y_pos)
	panel.size = Vector2(1000, 0)
	panel.modulate = Color(1, 1, 1, 0)
	canvas.add_child(panel)

	var ps = StyleBoxFlat.new()
	ps.bg_color = Color(0.06, 0.05, 0.1, 0.95)
	ps.border_color = Color(0.4, 0.75, 1.0, 0.9)
	ps.set_border_width_all(2)
	ps.set_corner_radius_all(16)
	ps.shadow_color = Color(0, 0, 0, 0.5)
	ps.shadow_size = 8
	ps.content_margin_left = 24
	ps.content_margin_right = 24
	ps.content_margin_top = 20
	ps.content_margin_bottom = 20
	panel.add_theme_stylebox_override("panel", ps)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 12)
	panel.add_child(vbox)

	var lbl = Label.new()
	lbl.text = text
	lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl.add_theme_font_size_override("font_size", 24)
	lbl.add_theme_color_override("font_color", Color(0.9, 0.92, 1.0))
	vbox.add_child(lbl)

	var btn = Button.new()
	btn.text = "知道了"
	btn.custom_minimum_size = Vector2(140, 42)
	btn.add_theme_font_size_override("font_size", 20)
	btn.add_theme_color_override("font_color", Color(0.3, 0.85, 1.0))
	btn.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vbox.add_child(btn)

	var tw = create_tween()
	tw.tween_interval(delay)
	tw.tween_property(overlay, "color:a", 0.5, 0.2)
	tw.parallel().tween_property(panel, "modulate:a", 1.0, 0.25)

	btn.pressed.connect(func():
		var tw2 = panel.create_tween()
		tw2.tween_property(overlay, "color:a", 0.0, 0.15)
		tw2.parallel().tween_property(panel, "modulate:a", 0.0, 0.15)
		tw2.tween_callback(canvas.queue_free)
	)

func reset_all():
	shown_tips.clear()
	_save()

func _save():
	var f = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(shown_tips))

func _load():
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var f = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not f:
		return
	var data = JSON.parse_string(f.get_as_text())
	if data is Dictionary:
		shown_tips = data
	_loaded = true
