#!/usr/bin/env python3
"""Inspect downloaded Python wheels before installation. NOT an antivirus scanner."""
import hashlib,json,os,stat,sys,zipfile
from pathlib import Path,PurePosixPath
def inspect(wheel):
    size=wheel.stat().st_size
    if not size or size>250*1024*1024:raise ValueError("wheel size out of bound")
    expanded=0;record=False;meta=False
    with zipfile.ZipFile(wheel) as z:
        for item in z.infolist():
            s=item.filename
            path=PurePosixPath(s)
            if s.startswith("/") or "\\" in s or ".." in path.parts or not s:
                raise ValueError("unsafe archive path")
            if stat.S_ISLNK((item.external_attr>>16)&0o170000):
                raise ValueError("symlink in wheel")
            if s.lower().endswith(".pth"):raise ValueError("executable .pth hook requires review")
            expanded+=item.file_size
            if expanded>1500*1024*1024:raise ValueError("unpacked wheel too large")
            if s.endswith(".dist-info/RECORD"):record=True
            if s.endswith(".dist-info/METADATA"):meta=True
        if not record or not meta:raise ValueError("missing wheel metadata")
    with wheel.open("rb") as f:sha=hashlib.file_digest(f,"sha256").hexdigest()
    return {"file":wheel.name,"size":size,"sha256":sha,"archive_integrity":"checked"}
if __name__=="__main__":
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path("wheelhouse")
    files=sorted(root.glob("*.whl"))
    if not files:raise SystemExit("NO-GO: no wheel files")
    results=[]
    for f in files:
        try:results.append(inspect(f))
        except Exception as exc:raise SystemExit("NO-GO: "+f.name+": "+str(exc))
    print(json.dumps({"scope":"archive hygiene only, NOT malware/CVE clearance","wheels":results},indent=2))
