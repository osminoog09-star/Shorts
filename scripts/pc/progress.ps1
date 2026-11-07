# Живой прогресс сборки ролика «Живая картина» (Claude, 07.11.2026).
# Запуск: powershell -ExecutionPolicy Bypass -File scripts\pc\progress.ps1 -Project longform\oumuamua -Work C:\M1lash\Работа\oumuamua
param(
  [string]$Project = 'C:\M1lash\Shorts\longform\oumuamua',
  [string]$Work = 'C:\M1lash\Работа\oumuamua',
  [string]$Final = 'C:\M1lash\Готово\oumuamua_film.mp4',
  [int]$Every = 2
)
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$start = Get-Date; $hist = @{}

function Bar([string]$name, [double]$done, [double]$total, [string]$extra = '') {
  $w = 40; $p = 0; if ($total -gt 0) { $p = [math]::Min(1.0, [double]$done / [double]$total) }
  $n = [int]([math]::Round($p * $w)); $bar = ('█' * $n) + ('░' * ($w - $n))
  $col = 'DarkGray'; if ($p -ge 1) { $col = 'Green' } elseif ($done -gt 0) { $col = 'Yellow' }
  # ETA by the rate seen since this stage started moving
  $eta = ''
  if ($p -gt 0 -and $p -lt 1) {
    if (-not $hist.ContainsKey($name)) { $hist[$name] = @{ t = Get-Date; d = $done } }
    $h = $hist[$name]; $dt = ((Get-Date) - $h.t).TotalSeconds; $dd = $done - $h.d
    if ($dd -gt 0 -and $dt -gt 5) { $left = ($total - $done) / ($dd / $dt); $eta = '  ~' + [TimeSpan]::FromSeconds([int]$left).ToString('mm\:ss') + ' осталось' }
  }
  Write-Host ('{0,-10}' -f $name) -NoNewline; Write-Host $bar -ForegroundColor $col -NoNewline
  Write-Host (' {0,3}%  {1}/{2}{3}{4}' -f [int]($p * 100), [int]$done, [int]$total, $extra, $eta)
}

while ($true) {
  $shots = 0; $beats = 0; $voice = 0
  foreach ($f in Get-ChildItem "$Project\levels\*.json") {
    $j = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    $shots += @($j.shots).Count; $beats += @($j.beats).Count
    foreach ($b in $j.beats) { if (Test-Path "$Work\voice\$($j.id)\$($b.id).wav") { $voice++ } }
  }
  $png = @(Get-ChildItem "$Project\assets\*.png" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch '_depth' }).Count
  $dep = @(Get-ChildItem "$Project\assets\*_depth.png" -ErrorAction SilentlyContinue).Count
  # render: workers print "wN done/total"
  $rd = 0; $rt = 0; $log = "$Work\render_full.log"
  if ((Test-Path $log) -and (Get-Item $log).LastWriteTime -gt $start) {
    $last = @{}
    foreach ($l in (Get-Content $log -Tail 400 -ErrorAction SilentlyContinue)) { if ($l -match '^(w\d+)\s+(\d+)/(\d+)') { $last[$matches[1]] = @([int]$matches[2], [int]$matches[3]) } elseif ($l -match '^done ') { $last['done'] = 1 } }
    foreach ($k in $last.Keys) { if ($k -ne 'done') { $rd += $last[$k][0]; $rt += $last[$k][1] } }
    if ($last.ContainsKey('done') -and $rt -gt 0) { $rd = $rt }
  }
  $fin = 0; if ((Test-Path $Final) -and (Get-Item $Final).LastWriteTime -gt $start) { $fin = 1 }

  Clear-Host
  Write-Host '  M1lash · сборка фильма' -ForegroundColor Cyan -NoNewline
  Write-Host ('   прошло {0}   {1}' -f ((Get-Date) - $start).ToString('hh\:mm\:ss'), (Get-Date).ToString('HH:mm:ss')) -ForegroundColor DarkGray
  Write-Host ''
  Bar 'Голос' $voice $beats ' фраз'
  Bar 'Кадры' $png $shots ' картин'
  Bar 'Глубина' $dep $shots ' карт'
  if ($rt -gt 0) { Bar 'Рендер' $rd $rt ' кадров видео' } else { Bar 'Рендер' 0 1 ' (ещё не начат)' }
  Bar 'Финал' $fin 1 ' концовка v7 + проверки'
  Write-Host ''
  $all = ($voice / [math]::Max(1, $beats)) * .25 + ($png / [math]::Max(1, $shots)) * .25 + ($dep / [math]::Max(1, $shots)) * .05
  if ($rt -gt 0) { $all += ($rd / $rt) * .35 }; $all += $fin * .10
  Bar 'ВСЕГО' ([math]::Round($all * 100)) 100
  Write-Host ''; Write-Host '  Обновляется каждые 2 с · Ctrl+C — закрыть (сборку не останавливает)' -ForegroundColor DarkGray
  Start-Sleep -Seconds $Every
}
