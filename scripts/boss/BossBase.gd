## Boss 基础类

extends Node

@export var boss_name: String = "Boss"
@export var max_hp: int = 100
@export var attack_damage: int = 5

var current_hp: int

signal hp_changed(current: int, maximum: int)
signal boss_attacking(damage: int)

func _ready():
	current_hp = max_hp

func take_damage(amount: int):
	current_hp = max(0, current_hp - amount)
	hp_changed.emit(current_hp, max_hp)
	if current_hp <= 0:
		die()

func perform_attack():
	# 每回合结束Boss攻击玩家
	boss_attacking.emit(attack_damage)
	GameManager.take_damage(attack_damage)

func die():
	pass # 由子类或GameManager处理
