"""Prepare two truly portrait scenes and a voiced closing from the shared TTS."""
import json,math,subprocess,wave
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;O=R/'out';O.mkdir(exist_ok=True);SR=44100
src=R.parents[1]/'media/tts/heron_finish';job=json.loads((R.parents[1]/'jobs/tts/heron_finish.json').read_text())
TEMPO=1.20
specs={
 'coin':('coin',['Автомат за монету','Вес запускает рычаг','Вода и автоматический сброс','Подпишись! Спасибо за просмотр и лайк'],['Почти 2000 лет назад','Монета — физический сигнал','Клапан закрывается сам','Доверил бы ему свою монету?'],['wide','lever','valve','reset']),
 'steam':('steam',['Паровой шар из древности','Почему он вращается','Опыт — ещё не завод','Подпишись! Спасибо за просмотр и лайк'],['Эолипил Герона','Реакция струй создаёт момент','Для полезной работы нужно больше','Как бы ты применил этот прибор?'],['wide','jets','detail','overview']),
 'ending':('all',['Спасибо, что досмотрел!'],['Подпишись · спасибо за лайк · что разобрать следующим?'],['final'])}
manifest=[]
for line in job['lines']:
 name=line['id'];meta=json.loads((src/f'{name}.json').read_text());assert meta['text']==line['text']
 tmp=O/f'speech_{name}.wav'
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(src/f'{name}.mp3'),'-af',f'aresample=44100,atempo={TEMPO},loudnorm=I=-17:TP=-3:LRA=9','-ar','44100','-ac','1',str(tmp)],check=True)
 with wave.open(str(tmp)) as w:a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
 speech=len(a)/SR;dur=math.ceil((speech+1.2)*30)/30
 if name!='ending':assert 30<=dur<=60,(name,dur)
 else:assert dur<25,(name,dur)
 x=np.zeros(round(dur*SR),np.float32);st=round(.15*SR);x[st:st+len(a)]=a
 t=np.arange(len(x),dtype=np.float32)/SR
 for j,hz in enumerate([130.8128,164.8138,195.9977]):
  beat=(t+j*.55)%8;env=np.exp(-beat*1.5)*np.minimum(beat/.03,1);x+=np.sin(2*np.pi*hz*t)*env*.006
 x*=np.minimum(1,t/.1)*np.minimum(1,np.maximum(0,(dur-t)/.7))
 dst=R/f'native_{name}.wav'
 with wave.open(str(dst),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-.9,.9)*32767).astype(np.int16).tobytes())
 words=meta['words'];cues=[]
 for i in range(0,len(words),8):
  row=words[i:i+8];cues.append({'start':row[0]['start']/TEMPO,'end':row[-1]['end']/TEMPO,'text':' '.join(z['w'] for z in row)})
 model,titles,keys,focus=specs[name]
 # Last scene begins on the spoken call to action, rather than an arbitrary silent title card.
 cta=next((w['start']/TEMPO for w in words if w['w'].lower().startswith('полная')),speech*.76)
 marks=[0,speech*.24,speech*.5,max(speech*.66,cta),dur] if name!='ending' else [0,dur]
 scenes=[]
 for i,(b,e) in enumerate(zip(marks,marks[1:])):
  scenes.append({'index':i,'model':model,'focus':focus[i],'title':titles[i],'key':keys[i],'source':'Герон · Пневматика','text':line['text'],'start':b,'dur':e-b,'speech':speech,'cues':[{'start':c['start']-b,'end':c['end']-b,'text':c['text']} for c in cues if c['end']>b-.15 and c['start']<e]})
 (R/f'timeline-{name}.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2))
 manifest.append({'name':name,'duration':dur,'frames':round(dur*30),'audio':dst.name,'width':1920 if name=='ending' else 1080,'height':1080 if name=='ending' else 1920})
(R/'native.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
tasks=[]
for m in manifest:
 n=2 if m['name']=='ending' else 4
 for i in range(n):tasks.append({'clip':m['name'],'part':i,'parts':n,'frames':m['frames']})
(R/'native_matrix.json').write_text(json.dumps({'include':tasks}));print(json.dumps(manifest))
