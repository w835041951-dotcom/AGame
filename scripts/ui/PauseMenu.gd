## 暂停菜单 - ESC键暂停/继续
## 提供继续、音量调节、重新开始、返回标题功能

extends CanvasLayer

signal resume_requested
signal restart_requested
signal quit_to_title_requested

var _panel: PanelContainer
var _overlay: ColorRect
var _music_slider: HSlider
var _sfx_slider: HSlider
var _is_paused: bool = false

func _ready():
	layer = 110
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()

func _unhandled_input(event: InputEvent):
	if event.is_action_pressed("ui_cancel"):
		if _is_paused:
			unpause()
		else:
			pause()
		get_viewport().set_input_as_handled()

func pause():
	if _is_paused:
		return
	_is_paused = true
	visible = true
	get_tree().paused = true
	_animate_in()

func unpause():
	if not _is_paused:
		return
	_is_paused = false
	get_tree().paused = false
	_animate_out()

func _animate_in():
	_overlay.color.a = 0.0
	_panel.modulate.a = 0.0
	_panel.scale = Vector2(0.9, 0.9)
	var tw = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.set_parallel(true)
	tw.tween_property(_overlay, "color:a", 0.7, 0.2)
	tw.tween_property(_panel, "modulate:a", 1.0, 0.2)
	tw.tween_property(_panel, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK)

func _animate_out():
	var tw = create_tween().set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_CUBIC)
	tw.set_parallel(true)
	tw.tween_property(_overlay, "color:a", 0.0, 0.15)
	tw.tween_property(_panel, "modulate:a", 0.0, 0.15)
	tw.tween_property(_panel, "scale", Vector2(0.95, 0.95), 0.15)
	tw.chain().tween_callback(func(): visible = false)

func _build_ui():
	# Full-screen darken overlay
	_overlay = ColorRect.new()
	_overlay.color = Color(0.0, 0.0, 0.02, 0.7)
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_overlay)

	# Center panel
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.size = Vector2(480, 460)
	_panel.position = Vector2(720, 310)
	_panel.pivot_offset = Vector2(240, 230)
	var ps = StyleBoxFlat.new()
	ps.bg_color = UIThemeManager.color("hud_bg")
	ps.border_color = UIThemeManager.color("border_strong")
	ps.set_border_width_all(3)
	ps.set_corner_radius_all(16)
	ps.shadow_color = Color(0, 0, 0, 0.5)
	ps.shadow_size = 12
	_panel.add_theme_stylebox_override("panel", ps)
	add_child(_panel)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 16)
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left = 40
	vbox.offset_right = -40
	vbox.offset_top = 30
	vbox.offset_bottom = -30
	_panel.add_child(vbox)

	# Title
	var title = Label.new()
	title.text = "暂 停"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 48)
	title.add_theme_color_override("font_color", UIThemeManager.color("text_accent"))
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	title.add_theme_constant_override("shadow_offset_x", 2)
	title.add_theme_constant_override("shadow_offset_y", 2)
	vbox.add_child(title)

	# Separator
	var sep = HSeparator.new()
	vbox.add_child(sep)

	# Music volume
	var music_row = _make_slider_row("🎵 音乐", AudioManager.music_volume)
	_music_slider = music_row[1]
	_music_slider.value_changed.connect(func(v): AudioManager.set_music_volume(v))
	vbox.add_child(music_row[0])

	# SFX volume
	var sfx_row = _make_slider_row("🔊 音效", AudioManager.sfx_volume)
	_sfx_slider = sfx_row[1]
	_sfx_slider.value_changed.connect(func(v): AudioManager.set_sfx_volume(v))
	vbox.add_child(sfx_row[0])

	# Spacer
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 8)
	vbox.add_child(spacer)

	# Resume button
	var resume_btn = _make_button("继续游戏", UIThemeManager.color("text_heal"))
	resume_btn.pressed.connect(unpause)
	vbox.add_child(resume_btn)

	# Restart button
	var restart_btn = _make_button("重新开始", UIThemeManager.color("text_accent"))
	restart_btn.pressed.connect(func():
		unpause()
		restart_requested.emit()
	)
	vbox.add_child(restart_btn)

	# Quit button
	var quit_btn = _make_button("返回标题", UIThemeManager.color("text_danger"))
	quit_btn.pressed.connect(func():
		unpause()
		quit_to_title_requested.emit()
	)
	vbox.add_child(quit_btn)

func _make_slider_row(label_text: String, initial: float) -> Array:
	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 12)
	var lbl = Label.new()
	lbl.text = label_text
	lbl.custom_minimum_size = Vector2(100, 0)
	lbl.add_theme_font_size_override("font_size", 22)
	lbl.add_theme_color_override("font_color", UIThemeManager.color("text_primary"))
	hbox.add_child(lbl)
	var slider = HSlider.new()
	slider.min_value = 0.0
	slider.max_value = 1.0
	slider.step = 0.05
	slider.value = initial
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.custom_minimum_size = Vector2(200, 0)
	hbox.add_child(slider)
	return [hbox, slider]

func _make_button(text: String, color: Color) -> Button:
	var btn = Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(0, 48)
	btn.add_theme_font_size_override("font_size", 26)
	btn.add_theme_color_override("font_color", color)
	btn.add_theme_color_override("font_hover_color", color.lightened(0.2))
	var s = UIThemeManager.make_stylebox("btn_normal_bg", "btn_normal_brd")
	btn.add_theme_stylebox_override("normal", s)
	var h = UIThemeManager.make_stylebox("btn_hover_bg", "border_strong")
	btn.add_theme_stylebox_override("hover", h)
	var p = UIThemeManager.make_stylebox("btn_hover_bg", "border_strong")
	btn.add_theme_stylebox_override("pressed", p)
	return btn
