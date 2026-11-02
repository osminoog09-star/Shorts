#!/usr/bin/env python3
"""003 only: source-timed framing, restore chair action, official final assembler."""
import argparse, json, subprocess, sys, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import movie_short as studio
# Absolute source seconds. Cut changes snap; never interpolate between unrelated shots.
SHOTS=[(114,.31),(119.7523,.27),(124.6905,.31),(126.3589,.31),
 (127.5601,.31),(132.9321,.30),(137.3365,.42),(140.2394,.47),
 (143.7763,.15),(144.7773,.52),(145.7449,.53),(146.6792,.42),
 (151,.48),(151.3839,.39),(157.0228,.58),(159.7589,.39),
 (160.7933,.50),(162.0946,.39),(163.9631,.58),(167.39,.33)]
PARTS=[(120.5,147),(151,168)]
def focus(t):
 x=next(x for st,x in reversed(SHOTS) if t>=st)
 # Follow Fletcher's move toward the chair inside this continuous shot.
 if 140.2394<=t<143.7763: x=.51-min(1,(t-140.2394)/1.3)*.12
 if 143.7763<=t<144.7773: x=.15+max(0,min(1,(t-144.3)/.4773))*.17
 if 135.8<=t<137.3365: x=.33+min(1,(t-135.8)/1.4)*.19
 if 163.9631<=t<167.39: x=.58+min(1,(t-164.5)/2.3)*.15
 return x

def frame_at(src,t):
 import cv2
 c=cv2.VideoCapture(str(src)); c.set(cv2.CAP_PROP_POS_MSEC,t*1000)
 ok,fr=c.read(); c.release()
 if not ok: raise RuntimeError('No source frame')
 return crop(fr,t)

def crop(fr,t):
 import cv2
 # Source letterbox measured 1920x800 at y=140. Stable box, not dark-scene cropdetect.
 fr=fr[140:940,:]
 x=round(focus(t)*1920-225); x=max(0,min(1470,x))
 return cv2.resize(fr[:,x:x+450],(1080,1920),interpolation=cv2.INTER_LANCZOS4)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--master',required=True); ap.add_argument('--work',required=True); ap.add_argument('--preflight',action='store_true'); ap.add_argument('--resume',action='store_true'); a=ap.parse_args()
 src=Path(a.source); work=Path(a.work);work.mkdir(parents=True,exist_ok=True)
 if a.preflight:
  import cv2
  for t in [114.5,120.5,127,133.5,142.5,145.3,151.8,158]:
   cv2.imwrite(str(work/f'frame_{t}.jpg'),frame_at(src,t))
  return
 import cv2
 raw=work/'picture.mp4'
 if not a.resume:
  proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(raw)],stdin=subprocess.PIPE)
  for start,end in PARTS:
   cap=cv2.VideoCapture(str(src)); cap.set(cv2.CAP_PROP_POS_MSEC,start*1000)
   for n in range(round((end-start)*30)):
    t=start+n/30
    while True:
     ok,fr=cap.read()
     if not ok:raise RuntimeError('Early EOF')
     if cap.get(cv2.CAP_PROP_POS_MSEC)/1000>=t:break
    proc.stdin.write(crop(fr,t).tobytes())
   cap.release()
  proc.stdin.close()
  if proc.wait():raise RuntimeError('Video render failed')
 wav=work/'body.wav'
 studio.ff('-i',str(src),'-filter_complex','[0:a]atrim=120.5:147,asetpts=PTS-STARTPTS[a];[0:a]atrim=151:168,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]','-map','[out]','-ar','48000','-ac','2',str(wav))
 os.environ['M1LASH_WHISPER']='medium'
 raw_words=studio.transcribe(wav,'ru') if not (work/'asr_raw.json').exists() else json.loads((work/'asr_raw.json').read_text())
 (work/'asr_raw.json').write_text(json.dumps(raw_words,ensure_ascii=False,indent=2))
 words=json.loads((ROOT/'shorts/003_reviewed_words.json').read_text())['words']
 (work/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2))
 studio.ass(words,work/'subtitles.ass','ОН СОРВАЛ\\NРЕПЕТИЦИЮ',2.6)
 subs=work/'subtitles.ass';subs.write_text(subs.read_text().replace('8,80,80,220,1','8,80,80,1100,1').replace('Style: Top,DejaVu Sans,62,','Style: Top,DejaVu Sans,68,'))
 # Phrase-level captions grounded in source ASR; readable holds, no orphan syllables.
 cues=[(1.28,2.2,'СПЕШИШЬ.'),(3.5,4.7,'5 — 6 — И.'),(6.66,7.5,'ТЯНЕШЬ.'),(7.84,9.05,'5 — 6 — И.'),
 (30.07,31.0,'КАК ДУМАЕШЬ,'),(31.01,33.2,'ПОЧЕМУ Я ШВЫРНУЛ\\NВ ТЕБЯ СТУЛ?'),
 (34.43,35.42,'Я НЕ ЗНАЮ.'),(35.53,36.43,'ЗНАЕШЬ.'),(36.67,37.52,'ИЗ-ЗА ТЕМПА?'),
 (37.85,40.1,'ТЫ ТЯНУЛ\\NИЛИ ТОРОПИЛСЯ?'),(42.02,43.3,'Я НЕ ЗНАЮ.')]
 old=subs.read_text(); head=old.split('Dialogue:')[0]; hook=[x for x in old.splitlines() if x.startswith('Dialogue: 1,')]
 lines=[]
 for st,en,txt in cues:
  pos=r'\an8\pos(540,190)' if st in (34.43,36.67,42.02) else ''
  lines.append(f'Dialogue: 0,{studio.ass_time(st)},{studio.ass_time(en)},Sub,,0,0,0,,{{{pos}\\fad(50,60)}}{txt}')
 subs.write_text(head+'\n'.join(lines+hook)+'\n')
 (work/'cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2))
 body=work/'body.mp4'
 studio.ff('-i',str(raw),'-i',str(wav),'-vf',f"subtitles={work/'subtitles.ass'}",'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-c:a','aac','-b:a','256k','-t','43.5',str(body))
 # Reuse exactly the previously generated Dima title, never change voices.
 title=work/'title.wav'
 studio.ff('-ss','47','-t','2.146','-i',a.master,'-vn','-ar','48000','-ac','2',str(title))
 final=work/'kino_003_v54.mp4'
 subprocess.run([sys.executable,str(ROOT/'tools/assemble_with_outro.py'),str(body),'-o',str(final),'--title',str(title),'--audio-bitrate','256k','--preset','fast'],check=True)
 for tool,extra in [('check',['--platform','shorts']),('look',['--overwrite','--tiles','3x2','--safe','shorts','-o',str(work/'final_look.jpg')])]:
  r=subprocess.run([sys.executable,str(ROOT/f'skills/ext/ffmpeg-skill/scripts/{tool}.py'),str(final),*extra],text=True,capture_output=True)
  (work/f'{tool}.log').write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(tool+' failed')
if __name__=='__main__':main()
