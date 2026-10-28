from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True)
base=Image.open(src).convert('RGB').resize((1280,720))
ft='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for n,(a,b,c)in enumerate([('ЧУЖОЙ','ОТВЕТ','#f2b473'),('КТО','ОТВЕТИТ?','#67cbfa'),('ИИ НА','РАБОТЕ','#ee8cc7')],1):
 im=base.copy();d=ImageDraw.Draw(im);d.rectangle((0,0,1280,275),fill='#102036');d.rectangle((0,560,1280,720),fill='#102036')
 d.text((48,28),'M1LASH  ·  НОВОСТИ ИИ',font=ImageFont.truetype(ft,25),fill='#62c8f8')
 d.text((45,72),a,font=ImageFont.truetype(ft,91),fill='#f3f7fc');d.text((45,170),b,font=ImageFont.truetype(ft,91),fill=c)
 d.rounded_rectangle((919,44,1225,98),radius=14,fill='#29465c');d.text((947,54),'28 ОКТЯБРЯ',font=ImageFont.truetype(ft,26),fill='#d8e8f1')
 d.line([(880,390),(700,350),(430,390)],fill='#f4b673',width=13,joint='curve');d.polygon([(430,390),(470,360),(475,402)],fill='#f4b673')
 d.rounded_rectangle((1010,466,1218,540),radius=15,fill='#efae70');d.text((1025,470),'155',font=ImageFont.truetype(ft,39),fill='#102036');d.text((1028,516),'ОТВЕТОВ',font=ImageFont.truetype(ft,18),fill='#102036')
 d.text((48,648),'Amazon  ·  Cloudflare  ·  Opera',font=ImageFont.truetype(ft,31),fill='#e5eff5')
 im.save(out/f'M1lash_Thumbnail_{n}.png')
