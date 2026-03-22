## 游戏事件 → 音效触发的连接脚本
## 挂载到 Main 节点，统一管理所有音效触发

extends Node

func _ready():
	# Boss战音效
	BombPlacer.bomb_placed.connect(func(_p, _t): AudioManager.play_sfx("bomb_place"))
	BombPlacer.bomb_removed.connect(func(_p): AudioManager.play_sfx("bomb_remove"))
	BombPlacer.detonation_started.connect(func(): AudioManager.play_sfx("detonate"))
	ExplosionCalc.explosion_visual.connect(func(_p, _t): AudioManager.play_sfx("explosion"))

	# Boss格子
	BossGrid.tile_destroyed.connect(func(_lp, _part): AudioManager.play_sfx("tile_break"))
	BossGrid.boss_moved.connect(func(_o): AudioManager.play_sfx("boss_move"))

	# 探索区
	GridManager.grid_revealed.connect(func(_x, _y, _d): AudioManager.play_sfx("mine_reveal"))
	GridManager.bomb_found.connect(func(_x, _y, _t): AudioManager.play_sfx("mine_bomb"))

	# 玩家受伤
	GameManager.game_over.connect(func():
		AudioManager.stop_bgm()
		AudioManager.play_bgm("gameover", false)
	)

	# 升级
	GameManager.combat_upgrade_triggered.connect(func():
		AudioManager.play_sfx("upgrade_pick")
	)
	GameManager.boss_defeated.connect(func():
		AudioManager.play_sfx("upgrade_pick")
	)

	# BGM：战斗开始
	GameManager.turn_started.connect(func():
		AudioManager.play_bgm("battle")
	)

	# 倒计时警告音（每秒一次，当剩余<10s）
	# 由 HUD 的 _process 触发，见 HUD.gd
