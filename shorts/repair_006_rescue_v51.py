#!/usr/bin/env python3
"""006 V51: real RU rescue scene, shot crops, official outro. PRIVATE QA only."""
import argparse,sys,subprocess,json,cv2
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import movie_short as s
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--title',required=True);ap.add_argument('--work',required=True);a=ap.parse_args()
w=Path(a.work);w.mkdir(parents=True,exist_ok=True);src=a.source
import shutil
if Path(a.title).resolve()!=(w/'title.wav').resolve():shutil.copyfile(a.title,w/'title.wav')
parts=[(150,168),(175.5,181.5),(186.5,196),(202,204.7),(207,211),(217,221)]
f=[]
for n,(a,b) in enumerate(parts):
 f.extend([f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[v{n}]',f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000[a{n}]'])
f.append(''.join(f'[v{n}][a{n}]' for n in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=1[v][a]')
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-filter_complex_threads','1','-filter_complex',';'.join(f),'-map','[v]','-map','[a]','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-c:a','aac','-b:a','256k',str(w/'sequence.mp4')],check=True)

cap=cv2.VideoCapture(str(w/'sequence.mp4'))
# Sequence-time crops at real shots; no interpolation through unrelated shots.
shots=[(0,.52),(1.5,.52),(3.1,.28),(4.7667,.74),(6.6333,.5),(8.1333,.44),(10.0333,.5),(11.3667,.5),(12.6333,.63),(15.4333,.48),(17.6,.5),(18,.64),(21.3333,.5),(23.2,.5),(24,.5),(24.5,.5),(25.8667,.5),(27.4333,.40),(29.7667,.45),(30.8,.5),(32.7,.5),(33.5,.5),(35.8667,.64),(36.2,.64),(38.2,.64),(39.8,.64),(40.2,.58),(41.4667,.48),(42.6667,.55)]
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18',str(w/'manual_picture.mp4')],stdin=subprocess.PIPE)
i=0
while True:
 ok,fr=cap.read()
 if not ok:break
 t=i/30;f=next(x for a,x in reversed(shots) if t>=a);h,width=fr.shape[:2];cw=round(h*9/16);x=round(width*f-cw/2);x=max(0,min(width-cw,x));p.stdin.write(cv2.resize(fr[:,x:x+cw],(1080,1920)).tobytes());i+=1
p.stdin.close();assert p.wait()==0

s.ass([],w/'subtitles.ass','ВОЛНА УЖЕ БЛИЗКО',2.6)
cues=[(1.05,2.8,r'ДОЙЛ, ВОЗВРАЩАЙТЕСЬ\NНА РЕЙНДЖЕР!'),(3.10,6.3,r'МЫ НИКУДА НЕ УЙДЁМ\NБЕЗ ЕЁ ДАННЫХ.'),(6.75,9.2,r'ВЕРНИТЕСЬ СЕЙЧАС ЖЕ!\NУ НАС НЕТ ВРЕМЕНИ.'),(10.3,11.65,r'НАДВИГАЕТСЯ\NВТОРАЯ ВОЛНА.'),(11.65,12.6,'ОНА СМОЕТ НАС.'),(13.5,15.1,'НЕТ. НАШЛА!'),(15.4,17.5,r'ТАЩИ СВОЮ ЗАДНИЦУ\NВ РЕЙНДЖЕР!'),(18.2,19.7,'УЛЕТАЙ, КУПЕР!'),(19.7,21.5,r'Я НЕ УСПЕЮ.\NУЛЕТАЙ!'),(22.1,23.6,'ДАВАЙ ЗА НЕЙ!'),(24.65,25.9,'ВСТАВАЙ, БРЭНД!'),(29.2,30.6,'Я НЕ УСПЕЮ!'),(30.6,31.7,'НЕТ, УСПЕЕШЬ!'),(31.8,32.8,'ТЫ УСПЕЕШЬ!'),(33.6,34.4,'БЫСТРЕЕ!'),(36.3,37.3,'ДАВАЙ!')]
with (w/'subtitles.ass').open('a') as out:
 for a,b,txt in cues:out.write(f'Dialogue: 0,{s.ass_time(a)},{s.ass_time(b)},Sub,,0,0,0,,{txt}\n')

subprocess.run(['ffmpeg','-v','error','-y','-i',str(w/'manual_picture.mp4'),'-i',str(w/'sequence.mp4'),'-map','0:v','-map','1:a','-vf',f"subtitles='{w/'subtitles.ass'}'",'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-c:a','aac','-b:a','256k',str(w/'body.mp4')],check=True)
subprocess.run(['python',str(ROOT/'tools/assemble_with_outro.py'),str(w/'body.mp4'),'-o',str(w/'kino_006_v51.mp4'),'--title',str(w/'title.wav'),'--audio-bitrate','256k','--preset','veryfast'],check=True)

subprocess.run([sys.executable,str(ROOT/'skills/ext/ffmpeg-skill/scripts/check.py'),str(w/'kino_006_v51.mp4'),'--platform','shorts','--json'],check=True)
subprocess.run([sys.executable,str(ROOT/'skills/ext/ffmpeg-skill/scripts/look.py'),str(w/'kino_006_v51.mp4'),'--tiles','4x3','--overwrite','-o',str(w/'final_look.jpg')],check=True)
