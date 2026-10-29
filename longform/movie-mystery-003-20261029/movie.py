from pathlib import Path
import json,subprocess,urllib.request,zipfile,hashlib,shutil
R=Path(__file__).resolve().parent;B=R/'build';B.mkdir(exist_ok=True)
URL='https://download.blender.org/demo/movies/ToS/ToS-4k-1920.mov.zip'
def run(*a):subprocess.run([str(x)for x in a],check=True)
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
source=B/'source.mov'
if not source.exists():
 z=B/'source.zip';urllib.request.urlretrieve(URL,z)
 with zipfile.ZipFile(z)as f:
  name=next(x for x in f.namelist()if x.endswith('.mov'))
  with f.open(name)as a,source.open('wb')as b:shutil.copyfileobj(a,b)
s=json.loads((B/'short_92_timeline.json').read_text())['scenes'][0];D=s['duration']+.18
norm=lambda x:x.lower().strip('«».,!?:;')
def when(w,n=1):return [x['offset']/1e7 for x in s['words']if norm(x['text'])==norm(w)][n-1]
# Each crop follows the actual principal face/hand, not a fixed central window.
shots=[(0,510,780),(1.25,30,1260),(when('роботизированной'),34,980),(when('Через'),50,960),(when('Через')+2.8,55,640),(when('Учёные'),50,960),(when('снова'),210,960),(when('встречу'),347,1090),(when('На'),358,780),(when('Но'),347,1090),(when('Я'),358,780),(when('Но',2),360,800),(when('повод'),347,1090),(when('железная'),389,740),(when('Пока'),480,1000),(when('ему'),510,780),(when('Угадал'),530,960),(when('Угадал')+2,436,1000),(when('Подпишись'),210,960)]
shots.sort();O=B/'movie_parts';O.mkdir(exist_ok=True);ps=[];log=[]
for i,(at,st,cx)in enumerate(shots):
 end=shots[i+1][0]if i+1<len(shots)else D;d=end-at
 if d<=0:continue
 p=O/f'{i:02d}.mp4';ps.append(p)
 # Four-second decoder warm-up avoids open-GOP seek reference errors in the old MOV.
 warm=min(4,st);vf=f"crop=450:800:x='max(0,min(iw-ow,{cx}-ow/2+12*sin(t*.5)))':y=0,scale=1080:1920:flags=lanczos,fps=30,setsar=1"
 run('ffmpeg','-nostdin','-v','error','-y','-ss',str(st-warm),'-i',source,'-ss',str(warm),'-t',str(d),'-vf',vf,'-an','-map_metadata','-1','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',p)
 assert duration(p)>=d-.05,(i,duration(p),d)
 run('ffmpeg','-xerror','-v','error','-i',p,'-f','null','-')
 log.append(dict(at=at,end=end,source=st,center=cx))
cat=O/'list.txt';cat.write_text('\n'.join("file '"+str(p.resolve())+"'"for p in ps))
run('ffmpeg','-xerror','-v','error','-y','-f','concat','-safe','0','-i',cat,'-c','copy','-an','-map_metadata','-1','-movflags','+faststart',B/'movie_base.mp4')
assert duration(B/'movie_base.mp4')>=D-.05
(B/'shots_private.json').write_text(json.dumps(dict(source=URL,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),duration=D,shots=log),indent=2))
print('Real licensed modern footage edit complete',D)
