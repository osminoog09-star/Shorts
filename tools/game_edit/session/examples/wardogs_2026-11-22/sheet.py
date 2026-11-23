"""Контактный лист: sheet.py name 0:28:20 0:29:50 [step] -> sheets/name.jpg (кадры с подписью времени)."""
import subprocess, sys
from src import W, locate, hms
name, a, b = sys.argv[1], hms(sys.argv[2]), hms(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else max(2.0, (b - a) / 20)
f, la = locate(a)
n = int((b - a) / step) + 1
cols = 5; rows = (n + cols - 1) // cols
(W / "sheets").mkdir(exist_ok=True)
import shutil
if not (W / "arial.ttf").exists(): shutil.copy(r"C:\Windows\Fonts\arial.ttf", W / "arial.ttf")
vf = (f"fps=1/{step},scale=384:-1,drawtext=fontfile=arial.ttf:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6:"
      f"text='%{{pts\\:hms\\:{a}}}',tile={cols}x{rows}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{la:.2f}", "-t", f"{b-a:.2f}", "-i", f, "-frames:v", "1", "-vf", vf,
                "-q:v", "4", str(W / "sheets" / f"{name}.jpg")], check=True, cwd=W)
print(W / "sheets" / f"{name}.jpg")
