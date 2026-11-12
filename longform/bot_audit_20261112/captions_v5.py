from pathlib import Path
import re,sys
sys.path.insert(0,str(Path(__file__).parent))
from tighten_v5 import CUTS,FPS,remap

def parse(stamp):
    h,m,s=stamp.split(":")
    return 3600*int(h)+60*int(m)+float(s.replace(",","."))

def fmt(s):
    t=round(s*1000)
    return f"{t//3600000:02}:{t//60000%60:02}:{t//1000%60:02},{t%1000:03}"

def captions(source):
    out=[]
    skipped=0
    for block in re.split(r"\n\s*\n",source.read_text("utf-8-sig").strip()):
        _,span,*body=block.splitlines()
        start,end=map(parse,span.split(" --> "))
        if any(start>=a/FPS and end<=b/FPS for a,b in CUTS):
            skipped+=1
            continue
        assert not any(start<b/FPS and end>a/FPS for a,b in CUTS),(start,end,body)
        out.append((remap(start),remap(end),"\n".join(body)))
    assert all(a[1]<=b[0] for a,b in zip(out,out[1:]))
    return "\n\n".join(f"{n}\n{fmt(a)} --> {fmt(b)}\n{body}" for n,(a,b,body) in enumerate(out,1))+"\n",len(out),skipped

if __name__=="__main__":
    s,n,removed=captions(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(s,encoding="utf-8")
    print(n,removed)
