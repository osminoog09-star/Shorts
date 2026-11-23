"""Скан ленты наград (справа вверху, под счётчиком денег) по ключевым кадрам (каждые 2 с) во ВСЕХ записях Wardogs.
-> killscan/<stem>.tsv: локальная_секунда<TAB>текст строки (OCR Windows, ru)."""
import subprocess, sys, shutil
from pathlib import Path
W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
REC = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings\Вардокс")
SKIP = {"Game_2026-11-22_01-47-53", "Game_2026-11-22_15-25-58", "Game_2026-11-22_17-18-19", "Game_2026-11-22_20-14-07"}  # CS2 / пустые
H, N, KEY = 180, 24, 2.0
files = [p for p in sorted(REC.glob("Game_*.mkv")) if p.stem not in SKIP]
_names = [a for a in sys.argv[1:] if not a.startswith("--")]
if _names: files = [p for p in files if p.stem in _names]
for f in files:
    tsv = W / "killscan" / f"{f.stem}.tsv"
    if tsv.exists() and "--force" not in sys.argv: print("skip", f.stem); continue
    out = W / "killscan" / f.stem
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-skip_frame", "nokey", "-i", str(f), "-vf", f"crop=600:{H}:1960:66,tile=1x{N}",
                    "-fps_mode", "vfr", "-start_number", "0", str(out / "tile_%04d.png")], check=True)
    tiles = sorted(out.glob("tile_*.png"))
    rows = []
    for k in range(0, len(tiles), 40):
        chunk = tiles[k:k + 40]
        res = subprocess.run(["powershell", "-NoProfile", "-Command", "[Console]::OutputEncoding=[Text.Encoding]::UTF8; & '" + str(W / "ocr.ps1") +
                              "' -Paths " + ",".join("'" + str(t) + "'" for t in chunk)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in res.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 3: continue
            ti = int(Path(parts[0]).stem.split("_")[1]); y = int(parts[1])
            rows.append(((ti * N + y // H) * KEY, parts[2].strip()))
    with open(tsv, "w", encoding="utf-8") as o:
        for sec, t in sorted(rows): o.write(f"{sec:.0f}\t{t}\n")
    print(f.stem, "tiles", len(tiles), "lines", len(rows), flush=True)
