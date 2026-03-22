# 音频资源清单

## 下载地址
- Kenney Digital Audio: https://kenney.nl/assets/digital-audio
- Kenney Interface Sounds: https://kenney.nl/assets/interface-sounds
- Juhani Junkala BGM (CC0): https://opengameart.org/content/5-chiptunes-action

---

## BGM（放到 assets/audio/bgm/）

| 文件名 | 说明 | 推荐来源 |
|--------|------|---------|
| battle.ogg | 战斗主循环BGM | Juhani Junkala - Action 1 或 2 |
| boss.ogg | Boss激烈阶段（可选） | Juhani Junkala - Action 3 |
| upgrade.ogg | 升级选择界面（可选） | Juhani Junkala - Action 5 |
| gameover.ogg | 游戏结束 | Juhani Junkala - Action 4 |

---

## 音效（放到 assets/audio/sfx/）

| 文件名 | 说明 | 推荐来源 |
|--------|------|---------|
| bomb_place.wav | 放置炸弹 | Kenney Digital Audio - click1.ogg |
| bomb_remove.wav | 取消炸弹 | Kenney Digital Audio - click2.ogg |
| detonate.wav | 按下引爆 | Kenney Digital Audio - confirmation.ogg |
| explosion.wav | 爆炸音效 | Kenney Digital Audio - explosion.ogg |
| tile_break.wav | Boss格子被摧毁 | Kenney Digital Audio - drop.ogg |
| boss_hit.wav | Boss受伤 | Kenney Digital Audio - hit.ogg |
| weak_hit.wav | 命中弱点（更响） | Kenney Digital Audio - hitHurt.ogg |
| chain.wav | 连锁爆炸 | Kenney Digital Audio - laser.ogg |
| mine_reveal.wav | 扫雷翻格 | Kenney Interface Sounds - click_003.ogg |
| mine_bomb.wav | 扫雷翻到炸弹 | Kenney Digital Audio - powerUp.ogg |
| upgrade_pick.wav | 选择升级 | Kenney Interface Sounds - confirmation_001.ogg |
| boss_move.wav | Boss移动 | Kenney Digital Audio - move.ogg |
| player_hit.wav | 玩家受伤 | Kenney Digital Audio - hitHurt.ogg |
| ui_click.wav | UI点击 | Kenney Interface Sounds - click_001.ogg |
| timer_warn.wav | 倒计时警告beep | Kenney Digital Audio - tone.ogg |

---

## 注意
- 所有 Kenney 素材均为 CC0，可直接商用，无需署名
- .ogg 格式在 Godot 里需要改扩展名或在代码里对应修改路径
- BGM 建议转为 .ogg（Godot 对 .ogg 流式播放更省内存）
- 音效建议用 .wav（低延迟）
