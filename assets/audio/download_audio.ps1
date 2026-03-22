# 下载并整理 Kenney + Juhani Junkala 音频资源
# 在 assets/audio/ 目录下运行: powershell -ExecutionPolicy Bypass -File download_audio.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Download-Zip($url, $dest) {
    Write-Host "  Downloading $url ..."
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}

function Unzip($zipPath, $destDir) {
    Expand-Archive -Path $zipPath -DestinationPath $destDir -Force
}

# ---- 1. Kenney Digital Audio ----
$kenney_digital_zip = "$ScriptDir\tmp_kenney_digital.zip"
Download-Zip "https://kenney.nl/content/assets/kenney_digital-audio.zip" $kenney_digital_zip
$kenney_digital_dir = "$ScriptDir\tmp_kenney_digital"
Unzip $kenney_digital_zip $kenney_digital_dir

# 查找实际的 audio 子目录（Kenney zip 结构有时有一层嵌套）
$kdBase = (Get-ChildItem -Path $kenney_digital_dir -Recurse -Filter "*.ogg" | Select-Object -First 1).DirectoryName

# 映射: 目标文件名 -> Kenney Digital Audio 原始文件名
$sfx_kenney_digital = @{
    "bomb_place.wav"   = "click1.ogg"
    "bomb_remove.wav"  = "click2.ogg"
    "detonate.wav"     = "confirmation.ogg"
    "explosion.wav"    = "explosion.ogg"
    "tile_break.wav"   = "drop.ogg"
    "boss_hit.wav"     = "hit.ogg"
    "weak_hit.wav"     = "hitHurt.ogg"
    "chain.wav"        = "laser.ogg"
    "mine_bomb.wav"    = "powerUp.ogg"
    "boss_move.wav"    = "move.ogg"
    "player_hit.wav"   = "hitHurt.ogg"
    "timer_warn.wav"   = "tone.ogg"
}

foreach ($entry in $sfx_kenney_digital.GetEnumerator()) {
    $src = Join-Path $kdBase $entry.Value
    $dst = "$ScriptDir\sfx\$($entry.Key)"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  [OK] $($entry.Value) -> sfx/$($entry.Key)"
    } else {
        Write-Warning "  [MISSING] $($entry.Value) not found in Kenney Digital Audio"
    }
}

# ---- 2. Kenney Interface Sounds ----
$kenney_iface_zip = "$ScriptDir\tmp_kenney_iface.zip"
Download-Zip "https://kenney.nl/content/assets/kenney_interface-sounds.zip" $kenney_iface_zip
$kenney_iface_dir = "$ScriptDir\tmp_kenney_iface"
Unzip $kenney_iface_zip $kenney_iface_dir

$kiBase = (Get-ChildItem -Path $kenney_iface_dir -Recurse -Filter "*.ogg" | Select-Object -First 1).DirectoryName

$sfx_kenney_iface = @{
    "mine_reveal.wav"  = "click_003.ogg"
    "upgrade_pick.wav" = "confirmation_001.ogg"
    "ui_click.wav"     = "click_001.ogg"
}

foreach ($entry in $sfx_kenney_iface.GetEnumerator()) {
    $src = Join-Path $kiBase $entry.Value
    $dst = "$ScriptDir\sfx\$($entry.Key)"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  [OK] $($entry.Value) -> sfx/$($entry.Key)"
    } else {
        Write-Warning "  [MISSING] $($entry.Value) not found in Kenney Interface Sounds"
    }
}

# ---- 3. Juhani Junkala 5 Chiptunes (CC0 BGM) ----
# 直接下载 OpenGameArt zip
$jj_zip = "$ScriptDir\tmp_juhani.zip"
Download-Zip "https://opengameart.org/sites/default/files/5ChiptunesAction.zip" $jj_zip
$jj_dir = "$ScriptDir\tmp_juhani"
Unzip $jj_zip $jj_dir

# Juhani 的文件名（zip 里的实际名称）
$bgm_juhani = @{
    "battle.ogg"   = "Juhani Junkala [Chiptune Adventures] 1.ogg"
    "gameover.ogg" = "Juhani Junkala [Chiptune Adventures] 4.ogg"
    "boss.ogg"     = "Juhani Junkala [Chiptune Adventures] 3.ogg"
    "upgrade.ogg"  = "Juhani Junkala [Chiptune Adventures] 5.ogg"
}

$jjBase = (Get-ChildItem -Path $jj_dir -Recurse -Filter "*.ogg" | Select-Object -First 1).DirectoryName

foreach ($entry in $bgm_juhani.GetEnumerator()) {
    $src = Join-Path $jjBase $entry.Value
    $dst = "$ScriptDir\bgm\$($entry.Key)"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  [OK] BGM -> bgm/$($entry.Key)"
    } else {
        # 尝试按编号匹配
        $idx = switch ($entry.Key) {
            "battle.ogg"   { "1" }
            "boss.ogg"     { "3" }
            "gameover.ogg" { "4" }
            "upgrade.ogg"  { "5" }
        }
        $fallback = Get-ChildItem -Path $jjBase -Filter "*$idx*" | Select-Object -First 1
        if ($fallback) {
            Copy-Item $fallback.FullName $dst -Force
            Write-Host "  [OK-fallback] $($fallback.Name) -> bgm/$($entry.Key)"
        } else {
            Write-Warning "  [MISSING] BGM $($entry.Key) not found"
        }
    }
}

# ---- 清理临时文件 ----
Remove-Item $kenney_digital_zip, $kenney_iface_zip, $jj_zip -ErrorAction SilentlyContinue
Remove-Item $kenney_digital_dir, $kenney_iface_dir, $jj_dir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== 完成 ==="
Write-Host "BGM 文件: $(Get-ChildItem $ScriptDir\bgm | Measure-Object | Select-Object -ExpandProperty Count) 个"
Write-Host "SFX 文件: $(Get-ChildItem $ScriptDir\sfx | Measure-Object | Select-Object -ExpandProperty Count) 个"
Write-Host ""
Write-Host "接下来在 Godot 编辑器中:"
Write-Host "  1. Project > Audio Buses > Add Bus 'Music', Add Bus 'SFX'"
Write-Host "  2. F5 运行游戏"
