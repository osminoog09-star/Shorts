"""Глобальное время сессии (сек от 13:05:40) -> (файл, локальная секунда)."""
import json, os
from pathlib import Path
# рабочая папка сессии: set GAME_WORK=C:\M1lash\Работа\<игра>_<дата>
W = Path(os.environ.get("GAME_WORK", r"C:\M1lash\Работа\game_2026-11-17"))
IDX = json.load(open(W / "index.json", encoding="utf-8"))["files"]
DUR = {}

def _dur(f):
    if f not in DUR:
        import subprocess
        DUR[f] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                      capture_output=True, text=True).stdout)
    return DUR[f]

def locate(t):
    for x in reversed(IDX):
        if t >= x["off"]:
            loc = t - x["off"]
            if loc > _dur(x["file"]):
                raise ValueError(f"{t} попадает в разрыв записи")
            return x["file"], loc
    raise ValueError(t)

def hms(s):
    s = s.strip(); p = [float(x) for x in s.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]
