"""Visual-only internal checks; never substitutes for a narrated pilot."""
import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
from render import frame
ROOT=Path(__file__).resolve().parent;B=ROOT/'build';B.mkdir(exist_ok=True)
scenes=[]
for i,b in enumerate((ROOT/'script.txt').read_text().strip().split('\n\n')):
 h,t=b.split('\n',1);chapter,kind,visual,title=h.split('|');scenes.append(dict(id=i,chapter=chapter,kind=kind,visual=visual,title=title,text=t,words=[],duration=50))
for portrait in [False,True]:
 selected=[0,2,3,6,9,10,12,16,18,21,23,27]
 tw,th=(384,216) if not portrait else (216,384)
 contact=Image.new('RGB',(tw*4,th*3),'#111827')
 for j,i in enumerate(selected):
  im=frame(scenes[i],9,portrait,visemes='B'*1600)
  im.save(B/f"design_{'p' if portrait else 'l'}_{i:02d}.jpg",quality=91)
  contact.paste(im.resize((tw,th)),((j%4)*tw,(j//4)*th))
 contact.save(B/f"design_contact_{'portrait' if portrait else 'landscape'}.jpg",quality=94)
# Short visual-only risk sample with several substantially different scene classes.
w,h=1920,1080;out=B/'VISUAL_ONLY_NOT_RELEASE.mp4'
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
for f in range(600):
 sec=f/30;i=[0,2,12,18][min(3,int(sec//5))];im=frame(scenes[i],sec%5,visemes=None);d=ImageDraw.Draw(im);d.rectangle((55,955,1300,1006),fill='#733446');d.text((75,965),'ВИЗУАЛЬНЫЙ ЧЕРНОВИК · БЕЗ ОЗВУЧКИ · НЕ РЕЛИЗ',font=__import__('render').font(24,True),fill='white');p.stdin.write(im.tobytes())
p.stdin.close()
if p.wait():raise RuntimeError('visual sample encode failed')
print(out)
