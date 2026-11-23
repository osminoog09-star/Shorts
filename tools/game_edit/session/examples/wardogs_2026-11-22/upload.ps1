$ErrorActionPreference = "Continue"
$R = "osminoog09-star/Shorts"; $G = "C:\M1lash\Готово\wardogs_2026-11-22"; $Wk = "C:\M1lash\Работа\wardogs_2026-11-22"
$wt = "C:\M1lash\Работа\shorts_pub_wt3"
$files = [ordered]@{ "wardogs3_ep" = "wardogs3_ep.mp4"; "wardogs3_short_headshots" = "short_headshots.mp4"; "wardogs3_short_emo" = "short_emo.mp4";
                     "wardogs3_short_nick" = "short_nick.mp4"; "wardogs3_short_pilot" = "short_pilot.mp4"; "wardogs3_short_learn" = "short_learn.mp4"; "wardogs3_short_kind" = "short_kind.mp4" }
Set-Location C:\M1lash\Shorts
git fetch -q origin
if (Test-Path $wt) { git worktree remove --force $wt }
git worktree add -q --detach $wt origin/main
python "$Wk\make_manifests.py" "$wt\publishing\queue"
$tags = @{}
foreach ($k in $files.Keys) {
  $mp4 = Join-Path $G $files[$k]
  $sha = (Get-FileHash $mp4 -Algorithm SHA256).Hash.ToLower()
  $tag = "private-" + $k.Replace("_", "-") + "-" + $sha.Substring(0, 8); $asset = "$k.mp4"
  $stage = Join-Path $env:TEMP "m1lash_$tag"; New-Item -ItemType Directory -Force $stage | Out-Null
  Copy-Item $mp4 (Join-Path $stage $asset) -Force
  gh release view $tag -R $R *> $null
  if ($LASTEXITCODE) { gh release create $tag (Join-Path $stage $asset) --draft --title "PRIVATE draft $k (auto-delete)" --notes "Owner-private upload source; draft = not public; deleted after YouTube upload." -R $R | Out-Null }
  "draft $tag"
  $mp = "$wt\publishing\queue\$k.json"
  $m = Get-Content $mp -Raw -Encoding utf8 | ConvertFrom-Json
  $m | Add-Member -NotePropertyName source -NotePropertyValue ([ordered]@{ type = "release"; tag = $tag; asset = $asset; sha256 = $sha }) -Force
  [IO.File]::WriteAllText($mp, ($m | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding $false))
  $tags[$k] = $tag
}
Set-Location $wt
foreach ($k in $files.Keys) { python scripts/youtube_direct.py check --manifest "publishing/queue/$k.json" 2>&1 | Select-Object -Last 1 }
git add publishing/queue
git commit -qm "publish: Wardogs-3 серия + 6 Shorts → private draft sources"
git push -q origin HEAD:main
if ($LASTEXITCODE) { "PUSH FAIL"; exit 1 }
"PUSH OK"
foreach ($k in $files.Keys) {
  "=== $k"
  $before = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId"
  gh workflow run youtube-direct.yml -R $R --ref main -f "manifest=publishing/queue/$k.json" -f execute=true -f mode=upload
  $rid = $before
  for ($i = 0; $i -lt 20 -and $rid -eq $before; $i++) { Start-Sleep 6; $rid = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId" }
  gh run watch $rid -R $R --interval 30 --exit-status | Out-Null
  $c = gh run view $rid -R $R --json conclusion -q .conclusion
  "run $rid $c"
  if ($c -eq "success") { gh release delete $tags[$k] -R $R --yes; "draft deleted" }
}
git fetch -q origin
foreach ($k in $files.Keys) { $r = git show "origin/main:publishing/receipts/$k.json" 2>$null | Out-String; if ($r) { "RECEIPT $k " + (($r | ConvertFrom-Json).video_url) } }
Set-Location C:\M1lash\Shorts
git worktree remove --force $wt
