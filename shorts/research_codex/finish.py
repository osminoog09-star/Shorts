from pathlib import Path
import subprocess,json,sys,hashlib
from PIL import Image,ImageOps,ImageDraw
from episodes import EPISODES
B=Path(__file__).resolve().parent;R=B.parents[1]
e=next(e for e in EPISODES if e['id']==sys.argv[1]);W=B/'work'/e['id'];out=R/'videos'/f'{e["id"]}_ru.mp4';out.parent.mkdir(exist_ok=True,parents=True)
# Exact approved visual, Liam and Laeko, requested explicitly by owner 25.10.
outro=R/'videos/m1lash_outro_short_ru.mp4';assert outro.exists()
cmd=['ffmpeg','-v','error','-y','-i',str(W/'silent.mp4'),'-i',str(W/'mix.m4a'),'-i',str(outro),'-filter_complex','[0:v]setsar=1,fps=30,format=yuv420p[v0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a0];[2:v]setsar=1,fps=30,format=yuv420p[v1];[2:a]aresample=48000,aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]','-map','[v]','-map','[a]','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True);subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));tl=json.loads((W/'timeline.json').read_text());body=tl[-1]['end'];dur=float(p['format']['duration']);times=[.1]+[s['start']+.55*(s['end']-s['start']) for s in tl]+[body-.08,body+.3,dur-.25]
qs=[]
for i,t in enumerate(times):
 f=W/f'qa_{i:02}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(max(0,t)),'-i',str(out),'-frames:v','1','-q:v','2',str(f)],check=True);qs.append(f)
thumbs=[]
for f in qs:
 im=Image.open(f).convert('RGB');im.thumbnail((270,480));thumbs.append(im)
sheet=Image.new('RGB',(270*5,510*2),'#eeeeee');d=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):x=(i%5)*270;y=(i//5)*510;sheet.paste(im,(x,y));d.text((x+6,y+482),f'{times[i]:.2f}s',fill='#222')
qdir=R/'shorts/research_codex/qa';qdir.mkdir(exist_ok=True);sheet.save(qdir/f'{e["id"]}_contact.jpg',quality=92)
meta={'id':e['id'],'title':e['title'],'style':e['style'],'duration':dur,'body_seconds':body,'file':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'probe':p,'full_decode':'passed','voice':'Dmitry body, approved existing Liam outro','lip_sync':'No visible speaker in body; approved original Rhubarb in outro','music':'Original procedural body and approved Laeko outro, explicit owner request; NCS restriction unresolved','human_continuous_watch':False,'human_continuous_listen':False,'publication_status':'not scheduled','sources':e['sources']}
(qdir/f'{e["id"]}_qa.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));(W/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps({k:meta[k] for k in ['id','duration','bytes','file']}))
