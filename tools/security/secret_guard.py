#!/usr/bin/env python3
"""Non-disclosing read-only heuristic over tracked text. NOT a full history scan."""
import json,re,subprocess
from pathlib import Path
PATTERNS={
  "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{55,})"),
  "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
  "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
  "private_key_header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
}
EXT={".py",".js",".ts",".tsx",".json",".md",".txt",".yml",".yaml",".env",".sh"}
def scan(text):
 return sorted(k for k,r in PATTERNS.items() if r.search(text))
def main():
 command=subprocess.run(["git","ls-files","-z"],capture_output=True,check=True)
 report=[];checked=0
 for rel in command.stdout.decode("utf-8","replace").split("\0"):
  if not rel:continue
  path=Path(rel)
  if path.suffix not in EXT or not path.is_file() or path.stat().st_size>1024*1024:continue
  checked+=1
  found=scan(path.read_text(encoding="utf-8",errors="ignore"))
  if found:report.append({"path":rel,"possible_rules":found})
 print(json.dumps({"mode":"advisory only; do not print candidate secret contents",
                   "tracked_text_files_scanned":checked,"possible_findings":report},indent=2))
 if "--strict" in __import__("sys").argv and report:raise SystemExit(2)
if __name__=="__main__":main()
