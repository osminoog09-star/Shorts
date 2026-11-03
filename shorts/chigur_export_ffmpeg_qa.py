#!/usr/bin/env python3
"""Export unmodified ffmpeg-skill QA tools from approved GitHub repository checkout.

Private handoff artifact for final Chigur QA; does NOT render or publish content.
"""
from pathlib import Path
from shutil import copytree
import hashlib,json,os
root=Path(__file__).resolve().parents[1]
src=root/"skills/ext/ffmpeg-skill/scripts"
dst=root/"motion-output"
if not (src/"check.py").is_file() or not (src/"look.py").is_file():
    raise RuntimeError("Official ffmpeg-skill QA tools missing in checkout")
copytree(src,dst/"official_ffmpeg_qa",dirs_exist_ok=True)
files=sorted(p for p in (dst/"official_ffmpeg_qa").rglob("*.py"))
(dst/"ffmpeg_qa_export_manifest.json").write_text(json.dumps({
    "root":"skills/ext/ffmpeg-skill/scripts",
    "github_run_id":os.getenv("GITHUB_RUN_ID","unknown"),
    "files_exported":len(files),
    "scripts_sha256":{p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("OFFICIAL_QA_TOOLS_EXPORT",len(files),flush=True)
