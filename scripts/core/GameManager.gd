## 游戏状态管理 - AutoLoad

extends Node

signal turn_started
signal turn_ended
signal game_over
signal boss_defeated
signal combat_upgrade_triggered
signal bomb_inventory_changed

# ---- 玩家状态 ----
var player_hp: int = 30
var player_max_hp: int = 30
var floor_number: int = 1

# ---- Boss状态 ----
var boss_hp: int = 0
var boss_max_hp: int = 0

# ---- 扫雷点击次数 ----
var current_clicks: int = 5
var max_clicks: int = 5

# ---- 炸弹库存 ----
var bomb_inventory: Dictionary = {}  # bomb_type -> count

# ---- 倒计时 ----
var turn_timer: float = 60.0
var turn_duration: float = 60.0
var timer_running: bool = false

# ---- 临时升级阈值 ----
var combat_upgrade_thresholds: Array = [75, 50, 25]
var triggered_thresholds: Array = []

func _process(delta):
	if timer_running:
		turn_timer -= delta
		if turn_timer <= 0.0:
			turn_timer = 0.0
			timer_running = false  # 先停止，防止重复触发
			turn_ended.emit()

func start_turn():
	current_clicks = max_clicks
	turn_timer = turn_duration
	timer_running = true
	turn_started.emit()

func end_turn():
	# 玩家主动结束回合
	if not timer_running:
		return
	timer_running = false
	turn_ended.emit()

# ---- 扫雷点击 ----
func use_click() -> bool:
	if current_clicks <= 0:
		return false
	current_clicks -= 1
	return true

# ---- 炸弹库存 ----
func add_bomb(type: String):
	bomb_inventory[type] = bomb_inventory.get(type, 0) + 1
	bomb_inventory_changed.emit()

func use_bomb(type: String) -> bool:
	if bomb_inventory.get(type, 0) <= 0:
		return false
	bomb_inventory[type] -= 1
	if bomb_inventory[type] == 0:
		bomb_inventory.erase(type)
	bomb_inventory_changed.emit()
	return true

func get_bomb_count(type: String) -> int:
	return bomb_inventory.get(type, 0)

func total_bombs() -> int:
	var total = 0
	for v in bomb_inventory.values():
		total += v
	return total

# ---- Boss伤害与HP同步 ----
func sync_boss_hp():
	boss_hp = BossGrid.get_total_hp()
	_check_combat_threshold()
	if boss_hp <= 0:
		boss_hp = 0
		timer_running = false
		boss_defeated.emit()

func _check_combat_threshold():
	if boss_max_hp <= 0:
		return
	var pct = int(boss_hp * 100.0 / boss_max_hp)
	for threshold in combat_upgrade_thresholds:
		if pct <= threshold and threshold not in triggered_thresholds:
			triggered_thresholds.append(threshold)
			timer_running = false  # 暂停倒计时
			combat_upgrade_triggered.emit()
			break

# ---- 玩家受伤 ----
func take_damage(amount: int):
	var real_amount = int(amount * BossGrid.boss_attack_multiplier)
	player_hp = max(0, player_hp - real_amount)
	if player_hp <= 0:
		game_over.emit()

# ---- 进入下一层 ----
func next_floor():
	floor_number += 1
	triggered_thresholds.clear()
	bomb_inventory.clear()
	bomb_inventory_changed.emit()
	max_clicks = 5 + floor_number
	turn_duration = min(turn_duration, 120.0)  # 最长2分钟
	# boss_hp 由 BossGrid.setup() 后 sync_boss_hp() 设置

# ---- 初始化Boss总HP ----
func init_boss_hp():
	boss_max_hp = BossGrid.get_total_max_hp()
	boss_hp = BossGrid.get_total_hp()

# ---- 玩家回血（升级用）----
func heal(amount: int):
	player_hp = min(player_hp + amount, player_max_hp)
