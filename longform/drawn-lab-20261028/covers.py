"""Code-native packaging from the actual approved drawings and final footage."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,subprocess
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--preflight',type=Path,required=True);ap.add_argument('--release',type=Path,required=True);a=ap.parse_args();O=a.release;O.mkdir(exist_ok=True)
PAPER='#f8f1df';INK='#303b46';BLUE='#287a9e';PINK='#b85179'
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def sheet(size):
 im=Image.new('RGB',size,PAPER);d=ImageDraw.Draw(im)
 for x in range(0,size[0],32):d.line((x,0,x,size[1]),fill='#eee7d5')
 for y in range(0,size[1],32):d.line((0,y,size[0],y),fill='#eee7d5')
 return im
def text(im,xy,s,n,c=INK):ImageDraw.Draw(im).text(xy,s,font=font(n),fill=c,stroke_width=0)
def host(im,xy,size):
 p=Image.open(a.preflight/'scene_00/assets/host/point_X.png').convert('RGBA');p.thumbnail(size);im.paste(p,xy,p)
frame=Image.open(a.preflight/'scene_00/index-0.40s.png').convert('RGB');phones=frame.crop((440,310,1230,711));phones.thumbnail((860,440))
for variant in [1,2]:
 im=sheet((1280,720));text(im,(55,30),'M1LASH · РИСУЕМ И РАЗБИРАЕМ',22,BLUE)
 if variant==1:
  text(im,(50,88),'КТО СЪЕЛ',88);text(im,(50,183),'ЗАРЯД?',104,PINK)
  im.paste(phones.resize((790,401)),(35,310));host(im,(915,237),(305,420))
 else:
  text(im,(50,90),'ЭКРАН СПИТ.',78);text(im,(50,180),'ЗАРЯД УХОДИТ?',78,PINK)
  im.paste(phones.resize((790,401)),(35,310));host(im,(915,237),(305,420))
 im.save(O/f'Battery_Cover_{variant}.png')
# Native portrait science cover frames, preserving original diagrams and host.
for n,name,label,large in [(90,'Plane_Cover','БЕЗ ДВИГАТЕЛЯ','ПАДЕНИЕ?'),(91,'Venus_Cover','СУТКИ ДЛИННЕЕ','ГОДА?')]:
 im=sheet((1080,1920));text(im,(65,65),'M1LASH · РИСУЕМ И РАЗБИРАЕМ',27,BLUE);text(im,(65,180),label,57);text(im,(65,255),large,95,PINK)
 fr=Image.open(a.preflight/f'scene_{n}/index-30.00s.png').convert('RGB')
 crop=fr.crop((80,470,990,900))
 if n==90:
  crop=crop.crop((90,60,870,390));crop=crop.resize((1014,429));im.paste(crop,(33,500))
 else:im.paste(crop,(80,470))
 host(im,(65,1100),(350,430));text(im,(65,1610),'ОДИН РИСУНОК —',48,BLUE);text(im,(65,1675),'ПОНЯТНЫЙ ОТВЕТ',48,BLUE)
 im.save(O/(name+'.png'))
movie=O/'m1lash_movie_mystery_002_ru.mp4'
if movie.exists():
 target=O/'Movie_Mystery_Cover.png';subprocess.run(['ffmpeg','-xerror','-v','error','-y','-ss','0.4','-i',str(movie),'-frames:v','1',str(target)],check=True)
 print(target)
print('Two landscape alternatives and three native portrait covers; no movie title text.')
