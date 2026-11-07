"""Reproducible three-film private edit; media stays outside public Git."""
import argparse,json,subprocess,math
from pathlib import Path
ROOT=Path(r'C:\M1lash\Работа\kino_new_20261107')
REPO=Path(__file__).resolve().parents[2]
PROJECTS={
 'kino009':{
  'title':'Она попросила обычный бургер — и всё изменилось 🍔 #shorts',
  'segments':[
   ['kino009_window2',20.65,6.45,354,1088,[[20.65,1490],[22.9,1050],[24.1,1660]]],
   ['kino009_window2',33.35,21.8,354,1088,[[33.35,1050],[35.933333,1660],[42.133333,1050],[45.233333,1660],[47.233333,1050],[53.866667,1660]]],
   ['kino009_window1',44.9,1.9,354,1088,[[44.9,1480]]],
  ],'hook':'ОБЫЧНЫЙ БУРГЕР?',
 },
 'kino010':{
  'title':'Тело дерётся само. А он просит не вставать 🤖 #shorts',
  'segments':[['kino010_window1',18.3,30.1,362,1072,[[18.3,1430],[19.633333,1270],[21.366667,1710],[23.9,1450],[24.766667,1450],[25.766667,1050],[26.966667,1710],[29.266667,1710],[31.0,1480],[32.566667,1530],[33.1,2250],[34.133333,1560],[41.466667,1300],[42.366667,1100],[43.333333,1300],[44.266667,1570],[44.933333,1230],[46.5,1150],[46.866667,1390]]]],
  'hook':'ТЕЛО ДЕРЁТСЯ САМО',
 },
 'kino011':{
  'title':'Все смотрели на фокус. Ребёнок заметил другое 🎩 #shorts',
  'segments':[['kino011_window1',14.5,41.1,352,1092,[[14.5,1240],[17.3,1390],[19.0,1240],[21.0,1300],[23.0,1030],[25.0,1450],[27.0,1300],[29.0,1180],[31.0,1050],[33.0,1350],[35.0,1450],[37.0,1300],[41.0,1370],[43.0,1650],[45.0,1770],[47.0,1400],[49.0,1350],[51.0,1320],[53.0,900]]]],
  'hook':'КУДА ДЕЛАСЬ ПТИЦА?',
  'editorial':[[4.0,5.8,'КЛЕТКА ИСЧЕЗЛА'],[11.6,13.6,'ПТИЦА ВЕРНУЛАСЬ'],[20.0,22.2,'НО МАЛЬЧИК ПЛАЧЕТ']],
 }
}

def cmd(args):
 p=subprocess.run([str(x) for x in args],capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace')[-2500:])
 return p.stdout

def ts(t):
 t=round(t*100);return f'{t//360000}:{t//6000%60:02d}:{t//100%60:02d}.{t%100:02d}'

def caption_words(name,start,dur,offset):
 rows=json.loads((ROOT/name/'transcript.json').read_text(encoding='utf8'))
 result=[];chunk=[]
 def flush():
  nonlocal chunk
  if chunk:
   text=' '.join(w['text'].strip() for w in chunk)
   text=text.replace('Стэм','СТЭМ').replace('Стем','СТЭМ')
   # The uncertain insult before the clear knife warning is left unsubtitled.
   if not any(bad in text for bad in ['Варан','убёртый','Чистем']):
    result.append([max(0,chunk[0]['start']-start)+offset,min(dur,chunk[-1]['end']-start)+offset,text])
   chunk=[]
 for row in rows:
  for w in row.get('words',[]):
   if w['start']<start-.03 or w['end']>start+dur+.03:continue
   if chunk and (len(' '.join(x['text'].strip() for x in chunk))+len(w['text'])>25 or len(chunk)>=4):flush()
   chunk.append(w)
  flush()
 return result

def write_ass(path,captions,hook,editorial=()):
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Arial,84,&H00FFFFFF,&H0000D8FF,&H00201810,&H90000000,-1,0,0,0,100,100,0,0,1,4,1,2,90,150,420,1
Style: Hook,Arial,62,&H0000DAFF,&H0000DAFF,&H00201810,&H90000000,-1,0,0,0,100,100,1,0,1,3,1,8,80,120,210,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 lines=[f'Dialogue: 1,0:00:00.00,0:00:01.85,Hook,,0,0,0,,{{\\fad(50,140)}}{hook}']
 for st,en,text in editorial:
  lines.append(f'Dialogue: 1,{ts(st)},{ts(en)},Hook,,0,0,0,,{{\\fad(80,120)}}{text}')
 for st,en,text in captions:
  if en-st<.10:continue
  style='{\\fscx108\\fscy108\\t(0,100,\\fscx100\\fscy100)\\fad(35,65)}'
  if 'чизбургер' in text.casefold() or 'нож' in text.casefold() or 'братик' in text.casefold():style=style[:-1]+'\\c&H00DAFF&}'
  lines.append(f'Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{style}{text}')
 path.write_text(header+'\n'.join(lines)+'\n',encoding='utf8')

def render(key):
 p=PROJECTS[key];out=ROOT/key;out.mkdir(exist_ok=True);parts=[];caps=[];offset=0
 for idx,(name,start,dur,y,h,focus) in enumerate(p['segments']):
  w=round(h*9/16/2)*2
  centers=focus
  xexpr=str(max(0,min(2560-w,centers[-1][1]-w/2)))
  for i in range(len(centers)-2,-1,-1):
   x=max(0,min(2560-w,centers[i][1]-w/2));boundary=centers[i+1][0]-start
   xexpr=f'if(lt(t,{boundary:.3f}),{x:.0f},{xexpr})'
  vf=f"crop={w}:{h}:'{xexpr}':{y},scale=1080:1920:flags=lanczos:in_color_matrix=bt601:out_color_matrix=bt709,setsar=1,fps=30,format=yuv420p"
  f=out/f'part{idx}.mp4'
  cmd(['ffmpeg','-v','error','-y','-ss',start,'-i',ROOT/(name+'.mp4'),'-t',dur,'-vf',vf,'-c:v','h264_nvenc','-preset','p4','-cq','18','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-ar','48000','-ac','2','-b:a','192k',f])
  parts.append(f);caps+=caption_words(name,start,dur,offset);offset+=dur
 concat=out/'concat.txt';concat.write_text(''.join("file '"+f.as_posix()+"'\n" for f in parts),encoding='utf8')
 raw=out/'body_clean.mp4'
 cmd(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',concat,'-c','copy','-movflags','+faststart',raw])
 write_ass(out/'captions.ass',caps,p['hook'],p.get('editorial',[]))
 # Render from this directory so the ASS filename contains no Windows drive colon.
 prev=Path.cwd()
 import os
 os.chdir(out)
 try:
  cmd(['ffmpeg','-v','error','-y','-i','body_clean.mp4','-vf',"ass=captions.ass",'-c:v','h264_nvenc','-preset','p4','-cq','18','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','copy','-movflags','+faststart','body.mp4'])
 finally:os.chdir(prev)
 manifest={'id':key,'public_title':p['title'],'body_seconds_planned':offset,'segments':p['segments'],'captions':caps,'status':'private_body_qa_pending','source_rights':'unverified; no public upload','source_max_quality':{'kino009':'4K 3840x1632','kino010':'1080p Ultra 1920x804','kino011':'1080p Ultra 1920x818'}[key]}
 (out/'edit.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 print('BODY_RENDERED',key,round(offset,3),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('project',choices=PROJECTS);a=p.parse_args();render(a.project)
