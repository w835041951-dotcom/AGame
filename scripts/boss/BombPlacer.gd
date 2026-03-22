## 放置阶段状态机 - AutoLoad

extends Node

enum Phase { IDLE, PLACING, DETONATING, DONE }

var phase: Phase = Phase.IDLE
var placed_bombs: Dictionary = {}  # Vector2i(放置区世界坐标) -> bomb_type String
var selected_type: String = "cross"

signal bomb_placed(pos: Vector2i, bomb_type: String)
signal bomb_removed(pos: Vector2i)
signal detonation_started
signal detonation_done(total_damage: int)

func reset():
	placed_bombs.clear()
	phase = Phase.PLACING

func on_cell_clicked(x: int, y: int):
	if phase != Phase.PLACING:
		return
	var pos = Vector2i(x, y)

	if pos in placed_bombs:
		# 取消放置，归还库存
		var old_type = placed_bombs[pos]
		placed_bombs.erase(pos)
		GameManager.add_bomb(old_type)
		bomb_removed.emit(pos)
	else:
		# 检查库存
		if not GameManager.use_bomb(selected_type):
			return
		placed_bombs[pos] = selected_type
		bomb_placed.emit(pos, selected_type)

func detonate() -> int:
	if phase != Phase.PLACING:
		return 0
	phase = Phase.DETONATING
	detonation_started.emit()
	var total = await ExplosionCalc.resolve_all(placed_bombs)
	placed_bombs.clear()
	detonation_done.emit(total)
	phase = Phase.DONE
	return total

func can_detonate() -> bool:
	return phase == Phase.PLACING

func set_selected_type(type_id: String):
	selected_type = type_id
