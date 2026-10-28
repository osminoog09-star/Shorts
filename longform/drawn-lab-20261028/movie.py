from pathlib import Path
import json,subprocess,urllib.request,hashlib
R=Path(__file__).resolve().parent;B=R/'build';B.mkdir(exist_ok=True)
URL='https://upload.wikimedia.org/wikipedia/commons/transcoded/6/6d/Le_Voyage_dans_la_Lune_%281902%29.webm/Le_Voyage_dans_la_Lune_%281902%29.webm.1080p.vp9.webm'
def run(*a):subprocess.run([str(x)for x in a],check=True)
source=B/'movie_source.webm'
if not source.exists():
 req=urllib.request.Request(URL,headers={'User-Agent':'M1lashFilmResearch/1.0'})
 with urllib.request.urlopen(req,timeout=90)as src,source.open('wb')as dst:
  import shutil
  shutil.copyfileobj(src,dst)
s=json.loads((B/'short_92_timeline.json').read_text())['scenes'][0];D=s['duration']+.18
def when(w):return next(x['offset']/1e7 for x in s['words']if x['text'].lower()==w.lower())
# Actual silent source shots were checked on a whole-film contact sheet.
cuts=[(0,320,620), (when('Сначала'),65,510),(when('потом'),195,710),(when('внутрь'),280,920),(when('запуск'),320,600),(when('посадка'),354,720),(when('встреча'),509,730),(when('Это'),454,510),(when('Попробуй'),550,720),(when('Сейчас'),666,760),(when('Подпишись'),703,720)]
cuts.sort();parts=B/'movie_parts';parts.mkdir(exist_ok=True);paths=[];shotlog=[]
for i,(at,start,cx)in enumerate(cuts):
 end=cuts[i+1][0]if i+1<len(cuts)else D;dur=end-at
 if dur<=0:continue
 p=parts/f'{i:02d}.mp4';paths.append(p)
 vf=f"crop=608:1080:x='max(0,min(iw-ow,{cx}-ow/2+22*sin(t*0.7)))':y=0,scale=1080:1920:flags=lanczos,fps=30,setsar=1"
 run('ffmpeg','-nostdin','-v','error','-y','-ss',str(start),'-i',source,'-t',str(dur),'-vf',vf,'-an','-map_metadata','-1','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',p)
 shotlog.append(dict(target_start=at,target_end=end,source_start=start,crop_center=cx))
cat=parts/'list.txt';cat.write_text('\n'.join("file '"+str(p.resolve())+"'"for p in paths))
run('ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',cat,'-c','copy','-an','-map_metadata','-1','-movflags','+faststart',B/'movie_base.mp4')
(B/'movie_shots_private.json').write_text(json.dumps(dict(source=URL,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),duration=D,shots=shotlog),indent=2))
print('Movie source muted; full-bleed timed edit complete',D)
