$ErrorActionPreference = "Continue"
$wt = "C:\M1lash\Работа\shorts_pub_wt"
$R = "osminoog09-star/Shorts"
Set-Location $wt
git push -q origin HEAD:main
if ($LASTEXITCODE) { "PUSH FAIL"; exit 1 }
"PUSH OK"
$items = @{
  "wardogs_ep1" = "private-wardogs-ep1-ca1ee7f8";
  "wardogs_short_friendly_fire" = "private-wardogs-short-friendly-fire-eaa80ba9";
  "wardogs_short_give_me_driver" = "private-wardogs-short-give-me-driver-aa1e9601";
  "wardogs_short_heli_stump" = "private-wardogs-short-heli-stump-3076b1e7";
  "wardogs_short_alisa" = "private-wardogs-short-alisa-19ed3fb8";
  "wardogs_short_ural" = "private-wardogs-short-ural-9e4a1ecd"
}
foreach ($k in "wardogs_ep1","wardogs_short_friendly_fire","wardogs_short_give_me_driver","wardogs_short_heli_stump","wardogs_short_alisa","wardogs_short_ural") {
  "=== $k"
  $before = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId"
  gh workflow run youtube-direct.yml -R $R --ref main -f "manifest=publishing/queue/$k.json" -f execute=true -f mode=upload
  $rid = $before
  for ($i = 0; $i -lt 20 -and $rid -eq $before; $i++) { Start-Sleep 6; $rid = gh run list -R $R --workflow youtube-direct.yml --limit 1 --json databaseId -q ".[0].databaseId" }
  "run $rid"
  gh run watch $rid -R $R --interval 30 --exit-status | Out-Null
  $c = gh run view $rid -R $R --json conclusion -q .conclusion
  "conclusion $c"
  if ($c -eq "success") { gh release delete $items[$k] -R $R --yes; "draft deleted" }
}
git fetch -q origin
foreach ($k in $items.Keys) { $r = git show "origin/main:publishing/receipts/$k.json" 2>$null; if ($r) { "RECEIPT $k"; $r } }
