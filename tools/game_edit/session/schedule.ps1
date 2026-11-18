$ErrorActionPreference = "Continue"
$R = "osminoog09-star/Shorts"
$wt = "C:\M1lash\Работа\shorts_sched_wt"
Set-Location C:\M1lash\Shorts
git fetch -q origin
git worktree add -q --detach $wt origin/main
Set-Location $wt
$plan = [ordered]@{
  "wardogs_short_friendly_fire" = "2026-11-18T12:00:00+02:00";
  "wardogs_short_heli_stump"    = "2026-11-19T20:00:00+02:00";
  "wardogs_ep1"                 = "2026-11-18T17:00:00+02:00";
  "wardogs_short_give_me_driver"= "2026-11-18T20:00:00+02:00";
  "wardogs_short_alisa"         = "2026-11-20T20:00:00+02:00";
  "wardogs_short_ural"          = "2026-11-22T20:00:00+02:00"
}
foreach ($k in $plan.Keys) {
  $p = "publishing/queue/$k.json"
  $m = [IO.File]::ReadAllText((Join-Path $wt $p), [Text.Encoding]::UTF8)
  $m = $m -replace '"publish_at":\s*(null|"[^"]*")', ('"publish_at": "' + $plan[$k] + '"')
  [IO.File]::WriteAllText((Join-Path $wt $p), $m, (New-Object Text.UTF8Encoding $false))
}
foreach ($k in $plan.Keys) { python scripts/youtube_direct.py check --manifest "publishing/queue/$k.json" 2>&1 | Select-Object -Last 1 }
python -I tests/test_studio_review_queue.py 2>&1 | Select-Object -Last 1
git add publishing/queue
git commit -qm "schedule: Wardogs серия сегодня 17:00 + Shorts 18–22.11 (решение Дениса)"
git push -q origin HEAD:main
if ($LASTEXITCODE) { "PUSH FAIL"; exit 1 }
"PUSH OK"
foreach ($k in $plan.Keys) {
  "=== $k $($plan[$k])"
  $before = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId"
  gh workflow run youtube-direct.yml -R $R --ref main -f "manifest=publishing/queue/$k.json" -f execute=true -f mode=schedule -f "expected_publish_at=$($plan[$k])"
  $rid = $before
  for ($i = 0; $i -lt 20 -and $rid -eq $before; $i++) { Start-Sleep 6; $rid = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId" }
  gh run watch $rid -R $R --interval 20 --exit-status | Out-Null
  "run $rid " + (gh run view $rid -R $R --json conclusion -q .conclusion)
  gh run view $rid -R $R --log 2>$null | Select-String "YOUTUBE_SCHEDULE_OK|Error|failed" | Select-Object -First 2 | ForEach-Object { $_.Line }
}
Set-Location C:\M1lash\Shorts
git worktree remove --force $wt
