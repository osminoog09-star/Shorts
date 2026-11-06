# M1lash Studio — установка конвейера на ПК Дениса (Windows 10/11, NVIDIA 12 ГБ, 32 ГБ RAM).
# Запуск: PowerShell от администратора →  Set-ExecutionPolicy -Scope Process Bypass; .\setup.ps1
# Повторный запуск безопасен: уже установленное пропускается.
$ErrorActionPreference = "Continue"  # Stop в PS 5.1 роняет скрипт на любом stderr от gh/git/ollama
$Root = "C:\M1lash"
function Step($t) { Write-Host "`n== $t" -ForegroundColor Cyan }

Step "Проверка железа"
if (-not (Get-Command nvidia-smi -ea 0)) { Write-Warning "nvidia-smi не найден — поставь свежий драйвер NVIDIA (Studio) и запусти снова"; exit 1 }
try { nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv } catch { Write-Warning "nvidia-smi не найден — поставь свежий драйвер NVIDIA (Studio) и запусти снова"; exit 1 }
$free = [math]::Round((Get-PSDrive C).Free / 1GB)
Write-Host "Свободно на C: $free ГБ"; if ($free -lt 150) { Write-Warning "Нужно ~150–200 ГБ (модели + фильмы). Освободи место или поменяй `$Root на другой диск." }

Step "Программы (winget)"
$pkgs = "Git.Git","GitHub.cli","Python.Python.3.11","Gyan.FFmpeg","OpenJS.NodeJS.LTS","Ollama.Ollama"
foreach ($p in $pkgs) { winget list --id $p -e *> $null; if ($LASTEXITCODE -ne 0) { winget install --id $p -e --accept-source-agreements --accept-package-agreements } else { Write-Host "есть: $p" } }
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")

Step "Папки"
foreach ($d in "Входящие","Работа","Готово","Архив","Игры") { New-Item -ItemType Directory -Force -Path "$Root\$d" | Out-Null }

Step "Репозиторий"
gh auth status *> $null; if ($LASTEXITCODE -ne 0) { gh auth login -w -p https }
gh auth setup-git
if (-not (Test-Path "$Root\Shorts\.git")) { gh repo clone osminoog09-star/Shorts "$Root\Shorts" } else { git -C "$Root\Shorts" pull --rebase }

Step "Python-библиотеки (CUDA)"
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install playwright obsws-python faster-whisper edge-tts opencv-python numpy gdown nvidia-cublas-cu12 nvidia-cudnn-cu12

Step "Рендер и голос на видеокарте ПК (решение Дениса 06.11)"
py -3.11 -m pip install --index-url https://download.pytorch.org/whl/cu128 torch torchaudio
py -3.11 -m pip install qwen-tts==0.1.1 transformers==4.57.3 accelerate==1.12.0 soundfile huggingface-hub
New-Item -ItemType Directory -Force -Path "$Root\private\voice_ref" | Out-Null
Write-Host "Личный образец голоса положи в $Root\private\voice_ref (или он заберётся из приватного Drive). В Git он не попадает." -ForegroundColor Yellow

Step "Локальная LLM (решение Дениса 31.10: Ollama + Gemma 4 12B)"
ollama pull gemma4:12b

Step "Настройки конвейера"
[Environment]::SetEnvironmentVariable("M1LASH_WHISPER","large-v3","User")
[Environment]::SetEnvironmentVariable("M1LASH_DEVICE","cuda","User")
[Environment]::SetEnvironmentVariable("M1LASH_ROOT",$Root,"User")

Step "Автозапуск слежки за папкой «Входящие»"
$py = (py -3.11 -c "import sys;print(sys.executable)")
$act = New-ScheduledTaskAction -Execute $py -Argument "`"$Root\Shorts\scripts\pc\inbox_watch.py`"" -WorkingDirectory "$Root\Shorts"
$trg = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "M1lash Inbox" -Action $act -Trigger $trg -Description "M1lash: фильмы из Входящие → кино-Shorts" -Force | Out-Null

Step "Агенты студии (решение Дениса 06.11: автономная студия на ПК)"
npm install -g @anthropic-ai/claude-code
Write-Host "Войди в Claude Code своей подпиской (откроется браузер), потом закрой окно: claude"
claude --version
py -3.11 "$Root\Shorts\scripts\pc\local_llm_bench.py" --pull
$act2 = New-ScheduledTaskAction -Execute $py -Argument "`"$Root\Shorts\scripts\pc\agent_bridge.py`"" -WorkingDirectory "$Root\Shorts"
$trg2 = New-ScheduledTaskTrigger -AtLogOn
$set2 = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName "M1lash Studio Agents" -Action $act2 -Trigger $trg2 -Settings $set2 -Description "M1lash: директор студии + чат сайта (agent_bridge.py)" -Force | Out-Null
Start-ScheduledTask -TaskName "M1lash Studio Agents"
$act3 = New-ScheduledTaskAction -Execute $py -Argument "`"$Root\Shorts\scripts\pc\game_watch.py`"" -WorkingDirectory "$Root\Shorts"
Register-ScheduledTask -TaskName "M1lash Games" -Action $act3 -Trigger $trg2 -Settings $set2 -Description "M1lash: записи OBS из $Root\Игры → игровой отдел" -Force | Out-Null
Start-ScheduledTask -TaskName "M1lash Games"
Write-Host "OBS: Настройки → Вывод → Путь записи = $Root\Игры (формат mkv). Дальше игровой отдел всё делает сам." -ForegroundColor Yellow

Write-Host "OBS для записи фрагментов: Инструменты → Настройки сервера WebSocket → включить; пароль запиши в переменную OBS_WS_PASSWORD (setx OBS_WS_PASSWORD ...)." -ForegroundColor Yellow

Step "Ярлык «Панель M1lash» на рабочем столе (вкл/выкл студии, игровой режим, сайт)"
$pyw = $py -replace 'python\.exe$','pythonw.exe'
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\Панель M1lash.lnk")
$lnk.TargetPath = $pyw; $lnk.Arguments = "`"$Root\Shorts\scripts\pc\studio_panel.pyw`""; $lnk.WorkingDirectory = "$Root\Shorts"
$lnk.IconLocation = "$env:SystemRoot\System32\imageres.dll,109"; $lnk.Save()

Step "Самопроверка"
py -3.11 "$Root\Shorts\scripts\pc\selfcheck.py"
Write-Host "`nГотово. Кидай файлы фильмов в $Root\Входящие — дальше всё само." -ForegroundColor Green
