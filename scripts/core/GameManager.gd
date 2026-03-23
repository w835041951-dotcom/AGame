## 游戏状态管理 - AutoLoad

extends Node

signal turn_started
signal turn_ended
signal game_over
signal boss_defeated
signal combat_upgrade_triggered
signal bomb_inventory_changed
signal lucky_find(reward_type: String, reward_text: String)
signal streak_bonus(streak: int, reward_text: String)
signal intel_changed(value: int)

# ---- 连续发现炸弹的连击系统 ----
var bomb_streak: int = 0  # 当前连续找到炸弹次数
var total_bombs_found: int = 0  # 本层找到的炸弹总数

# ---- 全局统计（游戏结束后展示） ----
var stat_total_damage: int = 0  # 本局总共造成伤害
var stat_max_chain: int = 0  # 本局最大连锁数
var stat_bombs_used: int = 0  # 本局使用炸弹总数
var stat_floors_cleared: int = 0  # 本局通过层数

# ---- 双资源：情报值 ----
var intel_points: int = 0
var reroll_tokens: int = 0

# ---- 炸弹冷却（过载等效果） ----
var bomb_cooldowns: Dictionary = {}  # type -> turns

# ---- 每局挑战词条 ----
var challenge_modifier: String = ""
var _last_challenge_modifier: String = ""

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
	if BombRegistry.is_unique(type) and bomb_inventory.get(type, 0) > 0:
		return
	bomb_inventory[type] = bomb_inventory.get(type, 0) + 1
	bomb_inventory_changed.emit()

func use_bomb(type: String) -> bool:
	if bomb_cooldowns.get(type, 0) > 0:
		return false
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
signal player_damaged(amount: int)

func take_damage(amount: int):
	var real_amount = int(amount * BossGrid.boss_attack_multiplier)
	if real_amount <= 0:
		return
	player_hp = max(0, player_hp - real_amount)
	player_damaged.emit(real_amount)
	if player_hp <= 0:
		game_over.emit()

# ---- 进入下一层 ----
func next_floor():
	floor_number += 1
	stat_floors_cleared += 1
	triggered_thresholds.clear()
	bomb_streak = 0
	total_bombs_found = 0
	intel_points = 0
	reroll_tokens = 0
	bomb_cooldowns.clear()
	_roll_challenge_modifier()
	# bomb_inventory 保留，炸弹可以带入下一关
	max_clicks = LevelData.get_max_clicks(floor_number)
	current_clicks = max_clicks  # 重置点击数，防止跨关残留
	turn_duration = LevelData.get_turn_duration(floor_number)
	GridManager.reset_for_new_floor()
	# boss_hp 由 BossGrid.setup() 后 sync_boss_hp() 设置

# ---- 初始化Boss总HP ----
func init_boss_hp():
	boss_max_hp = BossGrid.get_total_max_hp()
	boss_hp = BossGrid.get_total_hp()
	BossGrid.update_phase_by_hp(boss_hp, boss_max_hp)

# ---- 玩家回血（升级用）----
func heal(amount: int):
	player_hp = min(player_hp + amount, player_max_hp)

func add_intel(amount: int):
	if amount <= 0:
		return
	intel_points = max(0, intel_points + amount)
	intel_changed.emit(intel_points)

func add_reroll_token(amount: int = 1):
	reroll_tokens = max(0, reroll_tokens + amount)

func use_reroll_token() -> bool:
	if reroll_tokens <= 0:
		return false
	reroll_tokens -= 1
	return true

func use_intel(amount: int = 1) -> bool:
	if amount <= 0:
		return true
	if intel_points < amount:
		return false
	intel_points -= amount
	intel_changed.emit(intel_points)
	return true

func apply_bomb_cooldown(type: String, turns: int):
	if turns <= 0:
		return
	bomb_cooldowns[type] = max(bomb_cooldowns.get(type, 0), turns)

func _tick_bomb_cooldowns():
	for type in bomb_cooldowns.keys():
		bomb_cooldowns[type] -= 1
		if bomb_cooldowns[type] <= 0:
			bomb_cooldowns.erase(type)
	bomb_inventory_changed.emit()

func _roll_challenge_modifier():
	var weighted: Array = [
		"连锁强化：连锁加成+20%，点击-1",
		"护盾风暴：Boss护盾格+1",
		"情报富集：每回合+1情报"
	]
	# 冷却回路放到中后期更有意义，避免前期出现体感落差
	if floor_number >= 5:
		weighted.append("冷却回路：过载效果伤害+20%")
	if floor_number >= 12:
		weighted.append("冷却回路：过载效果伤害+20%")
	if floor_number >= 20:
		weighted.append("护盾风暴：Boss护盾格+1")

	var picked = weighted[randi() % weighted.size()]
	if weighted.size() > 1 and picked == _last_challenge_modifier:
		picked = weighted[randi() % weighted.size()]
	challenge_modifier = picked
	_last_challenge_modifier = challenge_modifier

# ---- 横扫减益：下回合点击次数-2 ----
var _swipe_debuff: int = 0

func apply_swipe_debuff():
	_swipe_debuff += 2

func start_turn():
	if challenge_modifier.is_empty():
		_roll_challenge_modifier()
	# 冷却应在每回合开始时递减，而非仅初始化时生效
	_tick_bomb_cooldowns()
	current_clicks = max(1, max_clicks - _swipe_debuff)
	_swipe_debuff = 0
	if challenge_modifier == "连锁强化：连锁加成+20%，点击-1":
		current_clicks = max(1, current_clicks - 1)
	if challenge_modifier == "情报富集：每回合+1情报":
		add_intel(1)
	BossGrid.on_new_turn()
	# Boss到达伤害位置时大幅缩短回合时间（紧迫感）
	if BossGrid.has_alive_at_left_edge():
		turn_timer = max(8.0, turn_duration * 0.4)
	else:
		turn_timer = turn_duration
	timer_running = true
	turn_started.emit()
