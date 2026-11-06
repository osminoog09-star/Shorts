# M1lash — рабочий набор на ПК Дениса (решение 06.11.2026, 18:28): БЕЗ агентов, Ollama, заданий и панели.
# Работу запускает Claude из чата (рендер, голос Дениса, whisper, сборка) на видеокарте ПК.
# Запуск: PowerShell от администратора → Set-ExecutionPolicy -Scope Process Bypass; .\setup_worker.ps1   (повторно — безопасно)
$ErrorActionPreference = "Continue"
$Root = "C:\M1lash"
function Step($t) { Write-Host "`n== $t" -ForegroundColor Cyan }

Step "Видеокарта"
if (-not (Get-Command nvidia-smi -ea 0)) { Write-Warning "nvidia-smi не найден — поставь драйвер NVIDIA"; exit 1 }
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv

Step "Программы (winget)"
foreach ($p in "Git.Git","GitHub.cli","Python.Python.3.11","Gyan.FFmpeg","OpenJS.NodeJS.LTS") {
  winget list --id $p -e *> $null; if ($LASTEXITCODE -ne 0) { winget install --id $p -e --accept-source-agreements --accept-package-agreements } else { Write-Host "есть: $p" } }
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")

Step "Папки"
foreach ($d in "Работа","Готово","private\voice_ref") { New-Item -ItemType Directory -Force -Path "$Root\$d" | Out-Null }

Step "Репозиторий"
gh auth status *> $null; if ($LASTEXITCODE -ne 0) { gh auth login -w -p https }
gh auth setup-git
if (-not (Test-Path "$Root\Shorts\scripts\pc\local_jobs.py")) { if (Test-Path "$Root\Shorts") { Rename-Item "$Root\Shorts" "Shorts_bad_$(Get-Date -f HHmmss)" }; git clone https://github.com/osminoog09-star/Shorts "$Root\Shorts" }
else { git -C "$Root\Shorts" pull --rebase --autostash }
git -C "$Root\Shorts" config --local credential.interactive never

Step "Python: рендер, голос (Qwen3-TTS), whisper — на CUDA"
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install --index-url https://download.pytorch.org/whl/cu128 torch torchaudio
py -3.11 -m pip install qwen-tts==0.1.1 transformers==4.57.3 accelerate==1.12.0 soundfile huggingface-hub faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12 playwright opencv-python numpy pillow gdown
py -3.11 -m playwright install chromium

Step "Настройки"
[Environment]::SetEnvironmentVariable("M1LASH_ROOT",$Root,"User")
[Environment]::SetEnvironmentVariable("M1LASH_DEVICE","cuda","User")
[Environment]::SetEnvironmentVariable("M1LASH_WHISPER","large-v3","User")
$env:M1LASH_ROOT = $Root

Step "Самопроверка"
py -3.11 "$Root\Shorts\scripts\pc\selfcheck.py"
Write-Host "`nОбразец голоса положи в $Root\private\voice_ref (в Git не попадает). Дальше задачи — через Claude в чате." -ForegroundColor Green
