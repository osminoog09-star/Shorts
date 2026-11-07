"""Тепловая защита RTX на ноутбуке Дениса (Claude, 07.11.2026): решение Дениса — держать GPU до 75 °C.
Вызывать между тяжёлыми шагами (кадр SDXL, фраза TTS): если ≥ HOT — пауза, пока не остынет до COOL.
Ничего не меняет в системе: только читает nvidia-smi."""
import os, subprocess, time
from pathlib import Path

HOT = int(os.environ.get('M1LASH_GPU_HOT', 75)); COOL = int(os.environ.get('M1LASH_GPU_COOL', 68))
EXE = next((x for x in [r'C:\Windows\System32\nvidia-smi.exe', r'C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe'] if Path(x).exists()), 'nvidia-smi')


def temp():
    try:
        return round(float(subprocess.run([EXE, '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]))
    except Exception:
        return None


def guard(tag=''):
    t = temp()
    if t is None or t < HOT: return t
    print(f'THERMAL pause {tag}: GPU {t} °C ≥ {HOT} — жду до {COOL} °C', flush=True); t0 = time.time()
    while True:
        time.sleep(5); t = temp()
        if t is None or t <= COOL: break
        if time.time() - t0 > 900: print('THERMAL: 15 мин не остывает — продолжаю, проверь охлаждение', flush=True); break
    print(f'THERMAL resume {tag}: GPU {t} °C после {int(time.time() - t0)} с', flush=True); return t
