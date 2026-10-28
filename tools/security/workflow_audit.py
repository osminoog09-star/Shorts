#!/usr/bin/env python3
"""Read-only GitHub workflow security heuristic; prints rule names, never secrets."""
import json,re,sys
from pathlib import Path
RULES={
 "critical_pull_request_target":r"(?m)^\s*pull_request_target\s*:",
 "critical_shell_pipe":r"(?i)(curl|wget)[^\n]*\|\s*(?:ba)?sh\b",
 "write_all_permissions":r"(?im)^\s*permissions\s*:\s*write-all\b",
 "unpinned_action":r"(?m)^\s*-\s*uses:\s*[^@ \n]+@(?![0-9a-f]{40}(?:\s|$))\S+"
}
def scan(text):
 return {rule:len(re.findall(pattern,text)) for rule,pattern in RULES.items() if re.search(pattern,text)}
def main():
 out={};root=Path(".github/workflows")
 for file in sorted(root.glob("*.yml")):
  found=scan(file.read_text(encoding="utf-8"))
  if found:out[str(file)]=found
 print(json.dumps({"mode":"advisory; existing workflow debt, not comprehensive exploit proof","files":out},indent=2))
 if "--strict" in sys.argv and any(any(k.startswith("critical") for k in group) for group in out.values()):
  raise SystemExit(2)
if __name__=="__main__":main()
