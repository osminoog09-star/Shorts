"""Sample the actual decoded shot midpoints in chronological order."""
from pathlib import Path
import json,sys,subprocess
from PIL import Image,ImageDraw
OUT=Path(r'C:\M1lash\Работа\bot_audit_20261112')
def main():
    video=Path(sys.argv[1]); label=sys.argv[2]
    tl=json.loads((OUT/'timeline.json').read_text('utf-8'))
    fps=tl['fps'];shots=tl['scenes']; work=OUT/('qa_'+label);work.mkdir(exist_ok=True)
    terms=[f'eq(n,{round((s["start"]+s["end"])*fps/2)})' for s in shots]
    def balanced(xs):
        if len(xs)==1:return xs[0]
        mid=len(xs)//2
        return '('+balanced(xs[:mid])+'+'+balanced(xs[mid:])+')'
    selected=balanced(terms)
    filt=f"select='{selected}',scale=256:144"
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-an','-vf',filt,'-fps_mode','vfr','-q:v','3',str(work/'shot_%04d.jpg')],check=True)
    assert len(list(work.glob('shot_*.jpg')))==len(shots)
    for ch in range(1,9):
        rows=[(n,s) for n,s in enumerate(shots,1) if s['chapter']==ch]
        tilew,tileh=256,161
        out=Image.new('RGB',(tilew*5,tileh*((len(rows)+4)//5)),(26,30,42))
        draw=ImageDraw.Draw(out)
        for i,(n,s) in enumerate(rows):
            x=i%5*tilew;y=i//5*tileh
            with Image.open(work/f'shot_{n:04d}.jpg') as im:out.paste(im,(x,y))
            draw.text((x+4,y+145),f'{s["id"]} {s["start"]:.1f}s {s["location"]}/{s["mode"]}',fill='white')
        out.save(work/f'chapter_{ch:02d}.jpg',quality=89)
    print('DECODED_SHOT_COVERAGE',label,len(shots),flush=True)
if __name__=='__main__':main()
