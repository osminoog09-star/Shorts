#!/usr/bin/env python3
"""Thin local wrapper for PySceneDetect: shot-boundary CSV is diagnostic evidence."""
import argparse,subprocess,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument("video");p.add_argument("--output",default="work/scene_audit");a=p.parse_args()
 path=Path(a.video).resolve()
 if not path.is_file() or path.suffix.lower() not in (".mp4",".mov",".mkv"):
  raise SystemExit("NO-GO: existing video required")
 out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
 cmd=[sys.executable,"-m","scenedetect","-i",str(path),"detect-content","list-scenes","-o",str(out)]
 print("Detecting shot changes; do not confuse cuts with artistic quality")
 subprocess.run(cmd,check=True,timeout=1200)
 print("Scene report directory:",out)
if __name__=="__main__":main()
