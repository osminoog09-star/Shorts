# M1lash Studio — установка конвейера на ПК Дениса (Windows 10/11, NVIDIA 12 ГБ, 32 ГБ RAM).
# Запуск: PowerShell от администратора →  Set-ExecutionPolicy -Scope Process Bypass; .\setup.ps1
# Повторный запуск безопасен: уже установленное пропускается.
$ErrorActionPreference = "Stop"
$Root = "C:\M1lash"
function Step($t) { Write-Host "`n== $t" -ForegroundColor Cyan }

Step "Проверка железа"
try { nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv } catch { Write-Warning "nvidia-smi не найден — поставь свежий драйвер NVIDIA (Studio) и запусти снова"; exit 1 }
$free = [math]::Round((Get-PSDrive C).Free / 1GB)
Write-Host "Свободно на C: $free ГБ"; if ($free -lt 150) { Write-Warning "Нужно ~150–200 ГБ (модели + фильмы). Освободи место или поменяй `$Root на другой диск." }

Step "Программы (winget)"
$pkgs = "Git.Git","GitHub.cli","Python.Python.3.11","Gyan.FFmpeg","OpenJS.NodeJS.LTS","Ollama.Ollama"
foreach ($p in $pkgs) { winget list --id $p -e *> $null; if ($LASTEXITCODE -ne 0) { winget install --id $p -e --accept-source-agreements --accept-package-agreements } else { Write-Host "есть: $p" } }
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")

Step "Папки"
foreach ($d in "Входящие","Работа","Готово","Архив") { New-Item -ItemType Directory -Force -Path "$Root\$d" | Out-Null }

Step "Репозиторий"
if (-not (Test-Path "$Root\Shorts\.git")) { gh auth status *> $null; if ($LASTEXITCODE -ne 0) { gh auth login -w }; gh repo clone osminoog09-star/Shorts "$Root\Shorts" } else { git -C "$Root\Shorts" pull --rebase }

Step "Python-библиотеки (CUDA)"
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install faster-whisper edge-tts opencv-python numpy gdown nvidia-cublas-cu12 nvidia-cudnn-cu12

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

Step "Самопроверка"
py -3.11 "$Root\Shorts\scripts\pc\selfcheck.py"
Write-Host "`nГотово. Кидай файлы фильмов в $Root\Входящие — дальше всё само." -ForegroundColor Green
