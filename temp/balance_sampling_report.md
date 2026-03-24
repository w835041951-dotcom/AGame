# 平衡采样报告（10局）

## 总体
- 局数: 10
- 平均通关层数: 62.20（范围 6 ~ 200，σ=57.61）
- 层数四分位: P25=16.2  P50=60.5  P75=78.2
- 平均总回合数: 177.30
- 平均单回合伤害: 57.50
- 平均点击盈亏/回合: -7.039
- 平均情报盈亏/回合: 0.541
- 平均剩余HP: 0.9
- 通关局数: 1/10

## 层数分布
-      0-5 层:  (0局)
-     6-20 层: ████ (4局)
-    21-50 层:  (0局)
-   51-100 层: █████ (5局)
-     101+ 层: █ (1局)

## 死亡原因
- hp_depleted: 9局
- win: 1局

## 分局明细
- Run 01 | seed=20260324 | floors=15 | turns=83 | avg_dmg=29.07 | click_delta=-4.867 | intel_delta=0.831 | hp=0 | end=hp_depleted
- Run 02 | seed=20260421 | floors=6 | turns=52 | avg_dmg=19.29 | click_delta=-4.519 | intel_delta=0.288 | hp=0 | end=hp_depleted
- Run 03 | seed=20260518 | floors=73 | turns=220 | avg_dmg=58.77 | click_delta=-7.691 | intel_delta=0.618 | hp=0 | end=hp_depleted
- Run 04 | seed=20260615 | floors=14 | turns=78 | avg_dmg=26.00 | click_delta=-6.577 | intel_delta=0.179 | hp=0 | end=hp_depleted
- Run 05 | seed=20260712 | floors=60 | turns=192 | avg_dmg=58.67 | click_delta=-7.479 | intel_delta=0.464 | hp=0 | end=hp_depleted
- Run 06 | seed=20260809 | floors=93 | turns=227 | avg_dmg=82.94 | click_delta=-8.048 | intel_delta=0.612 | hp=0 | end=hp_depleted
- Run 07 | seed=20260906 | floors=80 | turns=227 | avg_dmg=69.58 | click_delta=-7.859 | intel_delta=0.656 | hp=0 | end=hp_depleted
- Run 08 | seed=20261003 | floors=61 | turns=202 | avg_dmg=53.99 | click_delta=-7.312 | intel_delta=0.426 | hp=0 | end=hp_depleted
- Run 09 | seed=20261100 | floors=200 | turns=398 | avg_dmg=144.60 | click_delta=-9.399 | intel_delta=0.769 | hp=9 | end=win
- Run 10 | seed=20261197 | floors=20 | turns=94 | avg_dmg=32.06 | click_delta=-6.638 | intel_delta=0.564 | hp=0 | end=hp_depleted

## 说明
- 本结果为基于当前脚本公式的蒙特卡洛采样，适合做相对比较与版本回归。
- 若需引擎内逐帧真回放，请在本机安装 Godot CLI 后切换 headless 采样流程。
