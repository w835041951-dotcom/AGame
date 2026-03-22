## 游戏状态管理 - 单例
## 挂载到 AutoLoad

extends Node

signal turn_started(clicks_remaining: int)
signal turn_ended
signal game_over
signal boss_defeated

var current_clicks: int = 5
var max_clicks: int = 5
var player_hp: int = 30
var player_max_hp: int = 30
var boss_hp: int = 100
var boss_max_hp: int = 100
var floor_number: int = 1

func start_turn():
	current_clicks = max_clicks
	turn_started.emit(current_clicks)

func use_click() -> bool:
	if current_clicks <= 0:
		return false
	current_clicks -= 1
	if current_clicks <= 0:
		turn_ended.emit()
	return true

func deal_damage_to_boss(amount: int):
	boss_hp -= amount
	if boss_hp <= 0:
		boss_hp = 0
		boss_defeated.emit()

func take_damage(amount: int):
	player_hp -= amount
	if player_hp <= 0:
		player_hp = 0
		game_over.emit()

func next_floor():
	floor_number += 1
	boss_max_hp = 100 + floor_number * 20
	boss_hp = boss_max_hp
	max_clicks = 5 + floor_number
