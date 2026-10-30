#!/usr/bin/env python3
"""M1lash Cat Nebula: strict Dmitry voice, ESA CC BY 4.0 photos, Rhubarb phonetic cues.
Never publish without human review of the finished video.
"""
import asyncio, json, math, subprocess, wave
from pathlib import Path
import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / 'studio/public/cat_nebula'
TIMELINE = ROOT / 'studio/src/cat_nebula_timeline.json'
PUBLIC.mkdir(parents=True, exist_ok=True)
VOICE, RATE, FPS, SR, GAP = 'ru-RU-DmitryNeural', '+0%', 30, 48000, 0.18
LINES = [
 ('fact_hook', 'Космос показал кота. И это не фотошоп!'),
 ('fact', 'Двадцать девятого октября NASA опубликовало новые снимки туманности «Кошачья голова» — примерно в семи с половиной тысячах световых лет от Земли.'),
 ('fact', '«Хаббл» видит тёмный столб пыли и красный глаз. А «Джеймс Уэбб» заглянул внутрь в инфракрасном свете.'),
 ('fact_caveat', 'Там проявились скрытые звёзды и тонкие нити газа. Сам «глаз» может быть молодой звездой — но это ещё не доказано.'),
 ('fact', 'Кота вылепили не инопланетяне: газ и пыль разрушают ультрафиолет и ветры соседних гигантских звёзд.'),
 ('joke', 'Похоже, космос просто ждал, когда мы скажем «кис-кис».'),
 ('cta', 'Увидел кота? Напиши, где глаз! Подпишись! И спасибо всем, кто досмотрел и поставил лайк.'),
]
IMAGES = {
 'collage.jpg': ('heic2614a', 'NASA & ESA'),
 'hubble.jpg': ('heic2614b', 'NASA, ESA, STScI. Image Processing: J. DePasquale (STScI).'),
 'nircam.jpg': ('heic2614f', 'NASA, ESA, CSA, STScI. Image Processing: J. DePasquale (STScI).'),
 'miri.jpg': ('heic2614d', 'NASA, ESA, CSA, STScI. Image Processing: J. DePasquale (STScI).'),
}
def run(*args):
 subprocess.run(args, check=True, stdout=subprocess.DEVNULL)
def get_images():
 for name,(ident,credit) in IMAGES.items():
  dst=PUBLIC/name
  if not dst.exists():
   last=None
   for url in [f'https://cdn.esahubble.org/archives/images/large/{ident}.jpg', f'https://cdn.esahubble.org/archives/images/screen/{ident}.jpg']:
    try:
     r=requests.get(url,timeout=50,headers={'User-Agent':'M1lash/1.0 (news editorial)'})
     r.raise_for_status(); dst.write_bytes(r.content)
     with Image.open(dst) as im: im.verify()
     break
    except Exception as exc:
     last=exc; dst.unlink(missing_ok=True)
   else: raise RuntimeError(f'Cannot fetch ESA photo {ident}: {last}')
  with Image.open(dst) as im:
   assert min(im.size)>=750, f'{name}: insufficient resolution {im.size}'
  print('PHOTO OK',name,dst.stat().st_size,credit)
async def synth_one(text, mp3, attempts=6):
 import edge_tts
 for attempt in range(1,attempts+1):
  try:
   await edge_tts.Communicate(text,VOICE,rate=RATE).save(str(mp3))
   if mp3.stat().st_size<1000: raise RuntimeError('Empty speech')
   return
  except Exception as exc:
   mp3.unlink(missing_ok=True)
   if attempt==attempts: raise RuntimeError(f'Dmitry TTS failed after {attempts}: {exc}') from exc
   await asyncio.sleep(2.0+attempt*.65)
async def get_voice():
 import re
 for i,(_,sentence) in enumerate(LINES):
  mp3=PUBLIC/f'dima_{i:02}.mp3'
  if not (mp3.exists() and mp3.stat().st_size>1000):
   try:
    await synth_one(sentence,mp3,attempts=5)
   except Exception:
    # Same verified Dmitry voice, same rate, shorter speech chunks; NO voice fallback.
    parts=re.split(r'(?<=[.!?])\s+',sentence)
    if len(parts)<2:
     words=sentence.split()
     parts=[' '.join(words[:len(words)//2]),' '.join(words[len(words)//2:])]
    files=[]
    for j,part in enumerate(parts):
     dest=PUBLIC/f'dima_{i:02}_part{j}.mp3'
     await synth_one(part,dest,attempts=12)
     files.append(dest)
    cmd=['ffmpeg','-y','-v','error']
    for f in files: cmd+=['-i',str(f)]
    cmd+=['-filter_complex',''.join(f'[{j}:a]' for j in range(len(files)))+f'concat=n={len(files)}:v=0:a=1[out]','-map','[out]','-c:a','libmp3lame','-q:a','2',str(mp3)]
    run(*cmd)
  run('ffmpeg','-y','-v','error','-i',str(mp3),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(PUBLIC/f'dima_{i:02}.wav'))
def join_audio():
 chunks=[]; timeline=[]; pos=0
 for i,(kind,words) in enumerate(LINES):
  with wave.open(str(PUBLIC/f'dima_{i:02}.wav'),'rb') as f:
   assert f.getnchannels()==1 and f.getframerate()==SR and f.getsampwidth()==2
   samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').copy()
  st=pos/SR; chunks.append(samples); pos+=len(samples); en=pos/SR
  timeline.append({'id':i,'kind':kind,'text':words,'start':round(st,4),'end':round(en,4),
                   'speaker':'dima','voice_id':VOICE,'engine':'edge-tts','rate':RATE,
                   'source_file':f'cat_nebula/dima_{i:02}.mp3'})
  if i<len(LINES)-1:
   gap=np.zeros(round(GAP*SR),dtype=np.int16); chunks.append(gap);pos+=len(gap)
 voice=np.concatenate(chunks)
 with wave.open(str(PUBLIC/'voice.wav'),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(voice.tobytes())
 t=np.arange(len(voice),dtype=np.float64)/SR
 bed=sum(np.sin(2*math.pi*hz*t+.13*np.sin(2*math.pi*.08*t)) for hz in [110.,164.81,220.])/3
 envelope=.5-.5*np.cos(2*math.pi*np.minimum(t/1.4,1))
 mixed=np.clip(voice.astype(np.float64)+bed*350*envelope,-32768,32767).astype('<i2')
 with wave.open(str(PUBLIC/'mix.wav'),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(mixed.tobytes())
 return timeline,len(voice)/SR
def lip_sync(seconds):
 import shutil
 if not shutil.which('rhubarb'): raise RuntimeError('Rhubarb unavailable; no fake lipsync')
 run('rhubarb','-r','phonetic','-f','json','-o',str(PUBLIC/'mouth.json'),str(PUBLIC/'voice.wav'))
 cues=json.loads((PUBLIC/'mouth.json').read_text())['mouthCues']
 if len(cues)<20: raise RuntimeError('Insufficient Rhubarb mouth cues')
 vis=[]
 for f in range(math.ceil(seconds*FPS)):
  t=(f+.5)/FPS
  v=next((c['value'] for c in cues if c['start']<=t<c['end']),'X')
  vis.append(v if v in 'ABCDEFGHX' else 'X')
 if len(set(vis)-{'X'})<3: raise RuntimeError('Rhubarb visemes not plausible')
 return vis,len(cues)
def main():
 get_images();asyncio.run(get_voice())
 segs,duration=join_audio();vis,cues=lip_sync(duration)
 data={'date':'2026-10-30','voice_id':VOICE,'engine':'edge-tts','rate':RATE,
       'fps':FPS,'totalFrames':len(vis),'totalSeconds':round(duration,4),
       'segments':segs,'visemes':vis,'rhubarb_cues':cues,
       'images':{n:{'id':ident,'credit':credit,'source':f'https://esahubble.org/images/{ident}/','license':'CC BY 4.0'} for n,(ident,credit) in IMAGES.items()},
       'music':{'source':'original-procedural','third_party':False,'generator':'build.py'},
       'release_ready':False}
 TIMELINE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 (PUBLIC/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('TTS PASS',VOICE,'duration',duration,'cues',cues,'frames',len(vis))
if __name__=='__main__': main()
