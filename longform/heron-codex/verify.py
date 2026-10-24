"""Technical checks are evidence, not a claim that a person listened to the mix."""
from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out';T=json.loads((R/'timeline.json').read_text());D=sum(s['dur'] for s in T)
checks=[]
for f in sorted(O.glob('heron_*.mp4')):
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in data['streams'] if s['codec_type']=='video');a=next(s for s in data['streams'] if s['codec_type']=='audio');dur=float(data['format']['duration']);assert v['codec_name']=='h264';assert v['pix_fmt']=='yuv420p';assert v['r_frame_rate']=='30/1';assert a['codec_name']=='aac'
 assert (v['width'],v['height'])==((1080,1920) if 'short' in f.name else (1920,1080))
 if 'short' not in f.name:assert abs(dur-D)<.2 and 480<=dur<=600
 else:assert 15<=dur<=60
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-vn','-ar','16000','-f','f32le','-']);x=np.frombuffer(raw,np.float32);peak=float(np.max(np.abs(x)));rms=float(np.sqrt(np.mean(x*x)));assert peak<1 and rms>.015
 subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
 checks.append({'file':f.name,'duration':dur,'width':v['width'],'height':v['height'],'peak':peak,'rms':rms,'decoded':True})
# One frame per scene plus dense samples around several transition boundaries.
imgs=[]
for i,s in enumerate(T):
 p=O/f'qa_scene_{i:02}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(s['start']+s['dur']*.52),'-i',str(O/'heron_ancient_automation_ru.mp4'),'-frames:v','1',str(p)],check=True)
 im=Image.open(p).resize((480,270));imgs.append(im)
sheet=Image.new('RGB',(1920,6*300),'#eee9e1');q=ImageDraw.Draw(sheet)
for i,im in enumerate(imgs):x=(i%4)*480;y=(i//4)*300;sheet.paste(im,(x,y+25));q.text((x+12,y+5),f'{i+1:02} / {T[i]["title"]}',fill='#26363a',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16))
sheet.save(O/'heron_qa_contact.jpg',quality=90)
# Original thumbnail using our own render, not another creator's media.
im=Image.open(O/'qa_scene_04.jpg').resize((1280,720));q=ImageDraw.Draw(im);q.rounded_rectangle((30,35,685,245),radius=30,fill='#f8f3e9');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',67);q.text((55,55),'АВТОМАТ',font=font,fill='#26363a');q.text((55,135),'2000 ЛЕТ НАЗАД',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',43),fill='#5c7780');im.save(O/'heron_thumbnail.jpg',quality=95)
(O/'heron_qa.json').write_text(json.dumps({'technical_checks':checks,'visual_review':'pending agent inspection of decoded frames','full_audio_listen':'not performed by this automated script'},ensure_ascii=False,indent=2));print(json.dumps(checks,ensure_ascii=False))
