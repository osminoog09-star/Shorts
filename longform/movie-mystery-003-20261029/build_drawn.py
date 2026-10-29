from pathlib import Path
import json,os,re,shutil,bisect,argparse
R=Path(__file__).resolve().parent;B=R/'build';UP=Path(os.environ['HUASHU_ROOT'])
def captions(s):
 text=s['text'];words=s['words'];norm=lambda v:re.sub(r'[^\w]','',v.lower())
 spoken=''.join(norm(w['text'])for w in words);original=''.join(norm(w)for w in text.split());assert spoken==original,(s['id'],'word timing alignment mismatch')
 ends=[];at=0
 for w in words:at+=len(norm(w['text']));ends.append(at)
 result=[];at=0
 for phrase in re.split(r'(?<=[,.!?;:])\s+|(?<=[.!?]»)\s+',text):
  n=len(norm(phrase));start=bisect.bisect_right(ends,at);at+=n;end=min(len(words)-1,bisect.bisect_left(ends,at))
  if start>=len(words):continue
  # The movie's spoken answer must never appear in the captions.
  if s['id']==92 and at>len(original)-len(norm('Слёзы стали.')):continue
  result.append(dict(text=phrase,start=words[start]['offset']/1e7,end=(words[end]['offset']+words[end]['duration'])/1e7))
 return result
def make(s):
 p=s['id']>=90;movie=s['id']==92;w,h=(1080,1920)if p else(1920,1080);D=s['duration']+.18
 f=B/'native'/f"scene_{s['id']:02d}";f.mkdir(parents=True,exist_ok=True)
 for n in ['assets','vendor']:(f/n).mkdir(exist_ok=True)
 for name,src in [('om.js',UP/'runtime/om.js'),('gsap.min.js',UP/'templates/blank/vendor/gsap.min.js')]:shutil.copy2(src,f/'vendor'/name)
 for n in ['DejaVuSans.ttf','DejaVuSans-Bold.ttf']:shutil.copy2('/usr/share/fonts/truetype/dejavu/'+n,f/'assets'/n)
 shutil.copytree(B/'host',f/'assets/host',dirs_exist_ok=True);shutil.copy2(B/s['audio'],f/'assets/voice.mp3')
 if movie:shutil.copy2(B/'movie_base.mp4',f/'assets/movie_base.mp4')
 lip=json.loads((B/f"voice_{s['id']:02d}.rhubarb.json").read_text())['mouthCues'];caps=captions(s)
 (f/'captions.json').write_text(json.dumps(caps,ensure_ascii=False))
 js=(R/'draw.js').read_text().replace('__SCENE__',json.dumps(s,ensure_ascii=False)).replace('__LIP__',json.dumps(lip)).replace('__CAPS__',json.dumps(caps,ensure_ascii=False)).replace('__PORTRAIT__',str(p).lower())
 wc=[dict(word=x['text'],start=x['offset']/1e7,end=(x['offset']+x['duration'])/1e7)for x in s['words']]
 if movie:wc=[x for x in wc if x['start']<next(x['start']for x in wc if x['word']=='Слёзы')]
 source='NASA / FAA · СХЕМА'if s['id']==90 else'NASA / ESA · СХЕМА'if s['id']==91 else'АВТОРСКИЙ РУССКИЙ ПЕРЕСКАЗ'if movie else'DOE / Apple / Google / Samsung · ИСТОЧНИКИ В ОПИСАНИИ'
 kind='УСЛОВНЫЙ ПРИМЕР'if s['kind']=='example'else'СХЕМА МЕХАНИЗМА · НЕ ЗАМЕР УСТРОЙСТВА'if s['id']<90 else'РАЗБОР M1LASH'
 hostcss='left:65px;top:990px;width:280px;height:332px'if p else'right:50px;bottom:95px;width:270px;height:320px'
 captioncss='left:65px;top:1360px;width:820px;font-size:40px'if p else'left:65px;top:850px;width:1360px;font-size:34px'
 rootbg='#080a0d'if movie else'#f8f1df';fg='#ffffff'if movie else'#303b46';capbg='#10151eea'if movie else'#fff9ecf5'
 variables=json.dumps([dict(id='title',type='string',label='Заголовок',default=s['title'])],ensure_ascii=False)
 video=f'<video id="footage" data-om-id="footage" src="assets/movie_base.mp4" muted playsinline data-start="0" data-duration="{D}"></video>'if movie else''
 html=f'''<!doctype html><html lang="ru" data-composition-variables='{variables}'><head><meta charset="utf-8"><title>M1lash drawn lab</title><script src="vendor/gsap.min.js"></script><script src="vendor/om.js"></script><style>
@font-face{{font-family:Ink;src:url(assets/DejaVuSans.ttf)}}@font-face{{font-family:Ink;src:url(assets/DejaVuSans-Bold.ttf);font-weight:700}}html,body{{margin:0;overflow:hidden;background:{rootbg}}}#film{{width:{w}px;height:{h}px;position:relative;overflow:hidden;font-family:Ink;color:{fg};background:{rootbg};background-image:{'none'if movie else'linear-gradient(#c4bca116 1px,transparent 1px),linear-gradient(90deg,#c4bca116 1px,transparent 1px)'};background-size:32px 32px}}canvas,#footage{{position:absolute;inset:0;width:100%;height:100%}}#footage{{object-fit:cover}}#brand{{position:absolute;left:65px;top:48px;font-size:25px;font-weight:700;color:{'#f8f1df'if movie else'#287a9e'}}}#title{{position:absolute;left:65px;top:125px;max-width:{w-140}px;font-size:{47 if p else 53}px;font-weight:700;line-height:1.18;text-shadow:{'0 2px 6px #000'if movie else'none'}}}#kind{{display:none;position:absolute;left:65px;top:{275 if p else 220}px;font-size:21px;color:{'#fff'if movie else'#6d7d87'}}}#source{{display:none;position:absolute;left:65px;top:{335 if p else 1035}px;font-size:{21 if p else 19}px;max-width:{w-150}px;color:{'#fff'if movie else'#6d7d87'}}}#caption{{position:absolute;{captioncss};box-sizing:border-box;padding:13px 22px;line-height:1.25;font-weight:700;border-radius:13px;background:{capbg};color:{fg};box-shadow:0 2px 0 #303b4620}}#host{{position:absolute;{hostcss}}}#pencil{{position:absolute;left:0;top:0;font-size:63px;color:#303b46;pointer-events:none}}#spot{{position:absolute;left:65px;top:450px}}
</style></head><body><div id="film" data-composition-id="film" data-width="{w}" data-height="{h}" data-duration="{D}">{video}<canvas data-om-id="drawing"></canvas><div id="brand" data-om-id="brand">M1LASH · {'КИНОЗАГАДКА'if movie else'РИСУЕМ И РАЗБИРАЕМ'}</div><div id="title" data-om-id="title" data-var-text="title">{s['title']}</div><div id="kind" data-om-id="kind">{kind}</div><div id="source" data-om-id="source">{source}</div><div id="pencil" data-om-id="pencil">✎</div><div id="spot" data-om-id="spot"></div><div id="caption" data-om-id="caption"></div><img id="host" data-om-id="host" src="assets/host/talk_X.png" alt="Нарисованный ведущий M1lash за столом"><audio id="om-voice" src="assets/voice.mp3" data-start="0" data-duration="{s['duration']}" data-volume="1"></audio></div><script type="application/json" id="om-cues">{json.dumps(dict(words=wc),ensure_ascii=False)}</script><script>{js}</script></body></html>'''
 (f/'index.html').write_text(html);(f/'materials.md').write_text('Original code drawings and approved Narrator2 art recoloured by code. Illustrative mechanisms, not measured device tests. Voice: exact Edge ru-RU-DmitryNeural +0%; Rhubarb phonetic. Fonts: DejaVu. Runtime: original huashu-motion 0.3.1. Sources: project RESEARCH.md. For movie: private rights/source manifest; CC BY3 film footage, no original soundtrack; authored Russian narration.');print(f)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ids',required=True);a=ap.parse_args();wanted={int(i)for i in a.ids.split(',')}
 scenes=json.loads((B/'timeline.json').read_text())['scenes']
 for i in [90,91,92]:
  f=B/f'short_{i}_timeline.json'
  if f.exists():scenes+=json.loads(f.read_text())['scenes']
 for s in scenes:
  if s['id']in wanted:make(s)
