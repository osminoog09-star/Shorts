#!/usr/bin/env python3
"""Самопроверка ПК: ffmpeg, видеокарта для whisper, Ollama, git/gh, папки. Печатает PASS/FAIL по пунктам."""
import os, shutil, subprocess, sys, json, urllib.request
from pathlib import Path

ok = True
def check(name, fn):
    global ok
    try:
        r = fn(); print(f"PASS  {name}" + (f" — {r}" if r else ""))
    except Exception as e:  # noqa: BLE001
        ok = False; print(f"FAIL  {name} — {e}")

def need(cmd):
    if not shutil.which(cmd): raise RuntimeError(f"{cmd} не найден в PATH")
    return subprocess.run([cmd, "--version"], capture_output=True, text=True).stdout.splitlines()[0][:60]

check("ffmpeg", lambda: need("ffmpeg"))
check("git", lambda: need("git"))
check("gh (вход в GitHub)", lambda: subprocess.run(["gh", "auth", "status"], check=True, capture_output=True) and "вошёл")
def cuda():
    import ctranslate2
    n = ctranslate2.get_cuda_device_count()
    if n < 1: raise RuntimeError("CUDA не видна — whisper пойдёт на CPU (медленно)")
    return f"{n} GPU"
check("CUDA для whisper", cuda)
def ollama():
    tags = json.load(urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5))
    names = [m["name"] for m in tags.get("models", [])]
    if not any(n.startswith("gemma4") for n in names): raise RuntimeError(f"нет gemma4, есть: {names}")
    return ", ".join(names)
check("Ollama + Gemma 4", ollama)
root = Path(os.environ.get("M1LASH_ROOT", r"C:\M1lash"))
check("папки", lambda: all((root / d).is_dir() for d in ["Входящие", "Работа", "Готово"]) and str(root) or (_ for _ in ()).throw(RuntimeError("нет папок")))
print("\nИТОГ:", "ВСЁ ГОТОВО" if ok else "есть проблемы — см. FAIL выше")
sys.exit(0 if ok else 1)
