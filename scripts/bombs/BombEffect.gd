## 炸弹触发效果处理

extends Node

signal attack_animation_started(type: String, origin: Vector2i)
signal attack_dealt(damage: int)

func trigger_bomb(x: int, y: int, bomb_type: String):
	var damage = BombRegistry.calculate_damage(bomb_type)
	attack_animation_started.emit(bomb_type, Vector2i(x, y))
	# 动画结束后造成伤害（由动画节点回调）
	await get_tree().create_timer(0.5).timeout
	GameManager.deal_damage_to_boss(damage)
	attack_dealt.emit(damage)
