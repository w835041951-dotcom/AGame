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

# ---- 探索次数 ----
var current_clicks: int = 7
var max_clicks: int = 7

# ---- 炸弹库存 ----
var bomb_inventory: Dictionary = {}  # bomb_type -> count

# ---- 倒计时 ----
var turn_timer: float = 45.0
var turn_duration: float = 45.0
var timer_running: bool = false

# ---- 临时升级阈值 ----
var combat_upgrade_thresholds: Array = [80, 50, 25]
var triggered_thresholds: Array = []

func _process(delta):
	if timer_running:
		turn_timer -= delta
		if turn_timer <= 0.0:
			turn_timer = 0.0
			timer_running = false  # 先停止，防止重复触发
			turn_ended.emit()

func end_turn():
	# 玩家主动结束回合
	if not timer_running:
		return
	timer_running = false
	turn_ended.emit()

signal clicks_exhausted

# ---- 探索点击 ----
func use_click() -> bool:
	if current_clicks <= 0:
		return false
	current_clicks -= 1
	if current_clicks == 0:
		clicks_exhausted.emit()
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
	_check_no_bomb_no_mine()
	return true

func _check_no_bomb_no_mine():
	check_no_bomb_no_mine()

func check_no_bomb_no_mine():
	# 如果炸弹用完（含放置区）且探索区没有未翻开格，判断为无路可走
	if total_bombs() > 0:
		return
	if not BombPlacer.placed_bombs.is_empty():
		return  # 放置区还有炸弹，可以引爆
	if not timer_running:
		return
	# 检查探索区是否还有 HIDDEN 格
	for y in range(GridManager.rows):
		for x in range(GridManager.cols):
			var cell = GridManager.get_cell(x, y)
			if cell.get("state") == GridManager.CellState.HIDDEN:
				return
	game_over.emit()

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
	if boss_hp <= 0:
		boss_hp = 0
		timer_running = false
		boss_defeated.emit()
		return
	_check_combat_threshold()

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
	# bomb_inventory 保留，炸弹可以带入下一关
	max_clicks = LevelData.get_max_clicks(floor_number)
	turn_duration = LevelData.get_turn_duration(floor_number)
	GridManager.reset_for_new_floor()
	# boss_hp 由 BossGrid.setup() 后 sync_boss_hp() 设置

# ---- 初始化Boss总HP ----
func init_boss_hp():
	boss_max_hp = BossGrid.get_total_max_hp()
	boss_hp = BossGrid.get_total_hp()

# ---- 玩家回血（升级用）----
func heal(amount: int):
	player_hp = min(player_hp + amount, player_max_hp)

# ---- 横扫减益：下回合点击次数-2 ----
var _swipe_debuff: int = 0

func apply_swipe_debuff():
	_swipe_debuff += 2

func start_turn():
	current_clicks = max(1, max_clicks - _swipe_debuff)
	_swipe_debuff = 0
	turn_timer = turn_duration
	timer_running = true
	turn_started.emit()
