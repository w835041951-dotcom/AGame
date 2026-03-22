# AI美术提示词清单 — 像素风扫雷+炸弹人 Roguelite

---

## 一、Boss 精灵图

### Boss 整体（4x3格子区域）

**推荐尺寸：** `256x192` px（单帧），Spritesheet `512x384` px

**中文说明：** 科幻地牢Boss，机械生物风格，身体分区可见，暗色调霓虹轮廓

```
pixel art boss monster, 16-bit style, sci-fi dungeon mechanized beast,
segmented body with glowing grid zones, dark color palette, neon cyan and
red accents, menacing front-facing pose, visible body parts HEAD LEGS CORE,
metallic carapace texture, pixelated sprite sheet, transparent background,
dark fantasy roguelite aesthetic, no anti-aliasing, crisp pixel edges
--ar 4:3 --style raw
```

---

### Boss 关键部位 — HEAD（头部）

**推荐尺寸：** `64x64` px

```
pixel art boss head segment, 16-bit, glowing red eye visor,
mechanical skull, dark metal plating, neon red highlight,
weak point indicator glow, dungeon roguelite style,
transparent background, no anti-aliasing
```

---

### Boss 关键部位 — CORE（核心）

**推荐尺寸：** `64x64` px

```
pixel art boss core reactor segment, 16-bit, pulsing energy crystal,
cyan and orange glow, exposed mechanical heart, dungeon sci-fi,
critical hit zone visual, dark background, crisp pixels
```

---

### Boss 关键部位 — LEG（腿部）

**推荐尺寸：** `64x96` px（宽x高）

```
pixel art boss mechanical leg segment pair, 16-bit,
armored hydraulic limbs, dark steel with neon blue joints,
dungeon mech aesthetic, front view, transparent background,
roguelite pixel sprite
```

---

### Boss 格子状态 Overlay（叠加层）

**推荐尺寸：** 每格 `64x64` px，4种状态

| 状态 | 中文 | 提示词 |
|------|------|--------|
| Normal | 普通格子 | `pixel art boss tile normal state, 16-bit, dark gray cell with faint grid line, subtle blue tint, dungeon UI tile, no glow, crisp pixel edges, transparent bg` |
| Weak | 弱点格子 | `pixel art boss tile weak point, 16-bit, glowing orange cracked cell, pulsing light effect, dungeon roguelite, warning indicator, crisp pixels, transparent bg` |
| Armor | 护甲格子 | `pixel art boss tile armored, 16-bit, metallic steel plate cell, riveted dark iron texture, blue-gray hue, blocked indicator, crisp pixel art, transparent bg` |
| Absorb | 吸收格子 | `pixel art boss tile absorbing, 16-bit, dark purple void cell, energy absorption swirl effect, neon violet glow, dungeon sci-fi, crisp pixels, transparent bg` |

---

## 二、炸弹类型

**推荐尺寸：** `32x32` px 每种（Spritesheet `128x64` px）

### 1. 十字炸弹 Cross Bomb

```
pixel art cross bomb, 16-bit, classic minesweeper style bomb with cross
blast indicator, dark metal sphere, red fuse, white cross pattern glow,
dungeon roguelite item, transparent background, crisp pixel edges,
sci-fi icon style
```

### 2. 散射炸弹 Scatter Bomb

```
pixel art scatter bomb, 16-bit, cluster grenade with multiple mini bombs
orbiting, dark gray casing, yellow neon scatter arrows radiating outward,
dungeon roguelite icon, transparent background, crisp pixels
```

### 3. 反弹炸弹 Bounce Bomb

```
pixel art bounce bomb, 16-bit, rubber-cased bouncing bomb with curved
arrow indicators, teal and white color, motion trail pixels, dungeon
roguelite item icon, transparent background, crisp pixel art
```

### 4. 穿透炸弹 Pierce Bomb

```
pixel art pierce bomb, 16-bit, elongated bullet-shaped bomb with drill tip,
dark steel body, sharp cyan penetration arrow, dungeon sci-fi weapon icon,
roguelite style, transparent background, no anti-aliasing
```

### 5. 爆炸范围炸弹 Area Bomb

```
pixel art area explosion bomb, 16-bit, large round bomb with circular
blast radius ring indicator, dark purple body, fiery orange ring glow,
dungeon roguelite icon, transparent background, crisp pixel edges
```

---

## 三、格子 UI

**推荐尺寸：** 每格 `32x32` px，Spritesheet `256x64` px

### 放置区格子（Placement Zone）

| 状态 | 中文说明 | 提示词 |
|------|---------|--------|
| Empty | 空格/可放置 | `pixel art grid cell empty placement zone, 16-bit, dark charcoal background, subtle cyan border, faint grid line, dungeon UI, clean, no glow, transparent bg` |
| Hover | 悬停高亮 | `pixel art grid cell hover state, 16-bit, highlighted cyan border glow, slightly lighter fill, dungeon roguelite UI, selection indicator, crisp pixels` |
| Occupied | 已放置炸弹 | `pixel art grid cell occupied, 16-bit, glowing bomb silhouette inside dark cell, orange border, dungeon sci-fi UI, crisp pixel edges` |
| Locked | 锁定/不可用 | `pixel art grid cell locked, 16-bit, dark cell with red X cross overlay, padlock icon pixel, dungeon minesweeper UI, crisp pixels, muted colors` |

---

### 扫雷区格子（Minesweeper Zone）

| 状态 | 中文说明 | 提示词 |
|------|---------|--------|
| Unrevealed | 未揭开 | `pixel art minesweeper cell unrevealed, 16-bit, dark raised tile, slight bevel edge, no number, dungeon stone texture, roguelite UI, crisp pixel art` |
| Revealed | 已揭开 | `pixel art minesweeper cell revealed, 16-bit, dark sunken tile, recessed appearance, dungeon floor texture, clean empty cell, pixel art UI` |
| Numbered 1-8 | 数字格 | `pixel art minesweeper numbered cell, 16-bit, revealed dark tile with bold neon number, each number unique color (1=cyan 2=green 3=red 4=purple), dungeon roguelite font, crisp pixels` |
| Mine | 地雷 | `pixel art minesweeper mine cell, 16-bit, dark tile with skull bomb icon, red glow explosion effect, dungeon roguelite, danger indicator, crisp pixel art` |

---

## 四、HUD 界面元素

### 血条 Health Bar — `256x24` px

```
pixel art health bar, 16-bit, segmented hp bar with individual blocks,
dark dungeon UI, crimson red fill gradient, dark gray empty segments,
skull end cap icon, neon red border glow, roguelite game interface,
horizontal layout, crisp pixel art, no anti-aliasing
```

### 倒计时 Timer — `128x48` px

```
pixel art countdown timer UI, 16-bit, digital clock display,
dark panel with neon cyan numbers, colon separator,
dungeon sci-fi interface, glowing digit pixels, warning pulse effect
when low, roguelite HUD element, crisp pixel art font
```

### 库存显示 Inventory Slots — 单槽 `48x48` px

```
pixel art inventory slot bar, 16-bit, 5 dark item slots in a row,
each with subtle grid border, active slot cyan highlighted,
bomb count badge pixel number, dungeon sci-fi UI,
roguelite game HUD, dark transparent panel background,
crisp pixel edges
```

### HUD 整体框架 — `512x128` px

```
pixel art HUD bottom bar, 16-bit, dark semi-transparent dungeon panel,
health segment bar on left, bomb inventory slots center,
countdown timer right, neon cyan accent lines,
sci-fi dungeon roguelite game interface, industrial riveted border,
crisp pixel art, no anti-aliasing
```

---

## 五、游戏主背景

### 对战界面主背景 — `512x512` px（可平铺）

```
pixel art dungeon background, 16-bit, dark stone floor with glowing grid
overlay, subtle hex pattern, neon cyan and dark teal ambient lighting,
sci-fi dungeon aesthetic, ominous atmosphere, tileable texture,
depth fog at edges, roguelite game environment, dark color palette
80% black and dark gray, accent neon lines, crisp pixel art
```

### 地牢侧墙装饰 — `128x512` px

```
pixel art dungeon side wall panel, 16-bit, dark stone bricks with tech
circuitry inlay, faint neon blue circuit lines, wall-mounted dim lights,
sci-fi dungeon vertical banner, roguelite side decoration,
dark atmospheric background element, crisp pixel art
```

---

## 六、升级卡片 — `160x224` px

### 临时升级卡片

```
pixel art roguelite upgrade card frame, 16-bit, temporary buff card,
dark charcoal card border, SILVER and blue neon trim,
hourglass pixel icon in corner, inner dark panel for art display,
bottom text area with dark background, glowing silver edge highlight,
dungeon sci-fi card UI, crisp pixel art, no anti-aliasing
```

### 永久升级卡片

```
pixel art roguelite upgrade card frame, 16-bit, permanent upgrade card,
dark obsidian border, GOLD and orange neon trim, diamond gem pixel icon
corner badge, inner dark art panel, ornate pixel border decoration,
glowing golden edge aura, dungeon sci-fi card UI, premium feel,
crisp pixel art, no anti-aliasing
```

---

## 七、特效 SpriteSheet

### 爆炸特效 — `32x32` px × 8帧（`256x32` px）

```
pixel art explosion animation spritesheet, 16-bit, 8 frames,
dungeon bomb blast, orange and white pixel burst,
smoke cloud fade, crisp pixel edges, dark background,
roguelite effect sprite, horizontal frame layout
```

### 格子揭开特效 — `32x32` px × 4帧

```
pixel art tile reveal animation, 16-bit, 4 frame spritesheet,
minesweeper cell flip open effect, dark to revealed tile,
subtle dust pixel particles, dungeon roguelite, horizontal layout
```

### 伤害数字字体 — `16x16` px 字符集

```
pixel art damage number font sheet, 16-bit, bold chunky digits 0-9,
neon red critical hit style, dark outline, dungeon roguelite game font,
each digit on transparent background, crisp pixel art bitmap font
```

---

## 八、尺寸汇总

| 元素 | 尺寸 (px) | 备注 |
|------|----------|------|
| Boss 整体 | `256x192` | 4x3格对应 |
| Boss 关键部位 HEAD/CORE | `64x64` | — |
| Boss LEG | `64x96` | — |
| 炸弹图标 | `32x32` | 5种各一张 |
| 格子（放置区/扫雷区） | `32x32` | — |
| Boss格子Overlay | `64x64` | — |
| 血条整体 | `256x24` | — |
| 倒计时 | `128x48` | — |
| 库存槽单槽 | `48x48` | — |
| HUD条 | `512x128` | — |
| 主背景 | `512x512` (tile) | — |
| 升级卡片 | `160x224` | — |
| 爆炸特效帧 | `32x32` ×8帧 | `256x32` spritesheet |

---

## 推荐工具

- **Leonardo.ai** — 免费每日token，支持 pixel art 模型（Phoenix / Alchemy V2）
- **Midjourney** — 质量最高，需订阅
- **Aseprite** — 后期修改/动画，强烈推荐（$20 一次性买断）
- **Piskel** — 免费在线像素画工具
