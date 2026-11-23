"""1) добавляет записи 19–20.11 в index.json (смещение 200000 с + время от 19.11 21:32:17), 2) печатает события с глобальным временем,
3) мозаики кадров за 1,5 с до плашки награды: sheets/kills_XX.jpg (по 20 событий, подпись #номер тип время)."""
import json, subprocess, datetime as dt
from pathlib import Path
W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
REC = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings\Вардокс")
idx = json.load(open(W / "index.json", encoding="utf-8"))
have = {Path(x["file"]).stem for x in idx["files"]}
T19 = dt.datetime(2026, 11, 19, 21, 32, 17)
for p in sorted(REC.glob("Game_2026-11-19_*.mkv")) + sorted(REC.glob("Game_2026-11-20_*.mkv")):
    if p.stem in have: continue
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
    w = dt.datetime.strptime(p.stem[5:], "%Y-%m-%d_%H-%M-%S")
    idx["files"].append(dict(file=str(p), off=200000 + (w - T19).total_seconds(), dur=d, wall=str(w)))
idx["files"].sort(key=lambda x: x["off"])
json.dump(idx, open(W / "index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
off = {Path(x["file"]).stem: (x["off"], x["file"]) for x in idx["files"]}
def h(s): return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:04.1f}"
E = json.load(open(W / "events.json", encoding="utf-8"))["events"]
K = [e for e in E if e["type"] in ("kill", "headshot", "revenge", "vehicle", "teamkill")]
for i, e in enumerate(K):
    e["g"] = off[e["stem"]][0] + e["t"]; e["i"] = i
    print(f'#{i:02d} {e["type"]:8s} {h(e["g"])}  {e["stem"][5:]} {e["t"]:.0f}s  {e["text"][:40]}')
json.dump(K, open(W / "kills.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
(W / "sheets" / "k").mkdir(parents=True, exist_ok=True)
for e in K:
    p = W / "sheets" / "k" / f"k{e['i']:03d}.jpg"
    if p.exists(): continue
    lab = f"#{e['i']} {e['type']}".replace(":", "\\:")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, e['t'] - 1.5):.2f}", "-i", off[e["stem"]][1], "-frames:v", "1",
                    "-vf", f"crop=2304:1296:128:72,scale=384:216,drawtext=fontfile=arial.ttf:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7:x=4:y=4:text='{lab}'",
                    str(p)], check=True, cwd=W)
for k in range(0, len(K), 20):
    grp = K[k:k + 20]; ins = []
    for e in grp: ins += ["-i", str(W / "sheets" / "k" / f"k{e['i']:03d}.jpg")]
    n = len(grp); lay = "|".join(f"{(j % 5) * 384}_{(j // 5) * 216}" for j in range(n))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"xstack=inputs={n}:layout={lay}:fill=black", str(W / "sheets" / f"kills_{k // 20:02d}.jpg")], check=True)
print("mosaics", (len(K) + 19) // 20)
