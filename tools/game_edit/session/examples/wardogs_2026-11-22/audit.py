"""Аудит серии: по 3 кадра на сегмент (начало/середина/конец) с подписью #idx, kind, время источника.
Листы по 8 сегментов: sheets/audit_XX.jpg"""
import subprocess, sys
from ep1 import SEG
from edit import seg_dur, W
body = W / "ep1" / "body.mp4"
out = W / "sheets" / "audit"; out.mkdir(parents=True, exist_ok=True)
t = 0.0; rows = []
for i, s in enumerate(SEG):
    d = seg_dur(s)
    for j, f in enumerate((0.08, 0.5, 0.92)):
        p = out / f"s{i:03d}_{j}.png"
        lab = f"#{i} {s['k']}{'x'+str(s.get('sp')) if s.get('sp') else ''} {s.get('a','card')} ({d:.0f}s)" if j == 0 else ""
        lab = lab.replace(":", "\\:")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t + d*f:.2f}", "-i", str(body), "-frames:v", "1",
                        "-vf", f"scale=400:225,drawtext=fontfile=arial.ttf:fontsize=17:fontcolor=yellow:box=1:boxcolor=black@0.7:x=4:y=4:text='{lab}'",
                        str(p)], check=True, cwd=W)
    rows.append(i); t += d
for k in range(0, len(rows), 8):
    grp = rows[k:k+8]; ins = []
    for i in grp:
        for j in range(3): ins += ["-i", str(out / f"s{i:03d}_{j}.png")]
    n = len(grp)
    lay = "|".join(f"{c*400}_{r*225}" for r in range(n) for c in range(3))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"xstack=inputs={3*n}:layout={lay}",
                    str(W / "sheets" / f"audit_{k//8:02d}.jpg")], check=True)
print("ok", len(rows))
