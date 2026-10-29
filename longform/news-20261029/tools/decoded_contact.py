from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parent.parent;v=r/'out/M1lash_News_V2_Quality_26m50.mp4';dest=r/'out/qa/decoded';dest.mkdir(exist_ok=True)
times=[.9,18,72,127,155,260,360,480,535,650,709,845,1068,1208,1405,1602]
def frame(pair):
 i,t=pair;p=dest/f'{i:02}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(v),'-vf','scale=480:270','-frames:v','1',str(p)],check=True);return p
with ThreadPoolExecutor(max_workers=4) as e:paths=list(e.map(frame,enumerate(times)))
out=Image.new('RGB',(1920,1200),'#102235');d=ImageDraw.Draw(out);f=ImageFont.truetype(str(r/'assets/DejaVuSans.ttf'),18)
for i,(p,t) in enumerate(zip(paths,times)):
 x=i%4*480;y=i//4*300;out.paste(Image.open(p),(x,y));d.text((x+8,y+275),f'{int(t//60):02}:{t%60:05.2f}',font=f,fill='#fff4df')
out.save(r/'out/qa/FINAL_DECODED_CONTACT.jpg',quality=92)
print('decoded frames',len(paths))
