"""Export the exact already-approved vertical M1lash outro as a read-only artifact.

This job does not change any final YouTube video or copy film sources.
"""
from pathlib import Path
import shutil, subprocess, hashlib
p=Path("media/outro/m1lash_outro_v1_vertical.mp4")
if not p.is_file(): raise FileNotFoundError(p)
subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(p),"-f","null","-"],check=True)
out=Path("motion-output/approved_vertical_outro_exact.mp4")
out.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(p,out)
print("EXACT_APPROVED_OUTRO",out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest())
