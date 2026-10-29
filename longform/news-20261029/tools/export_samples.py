from pathlib import Path
import json,subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent.parent;M=json.loads((R/'out/M1lash_News_20261029_Dima_Sveta_MIX_manifest.json').read_text());D=R/'out/decoded_checks';D.mkdir(exist_ok=True)
# Start/end plus deterministic samples at real speech and chapter transitions.
times=[0.1,1.0,5.5]+[max(.1,M['segments'][i]['start']+.25) for i in range(0,len(M['segments']),4)]+[M['duration']-1.0]
def one(t):
 p=D/(str(round(t,2))+'.jpg');subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(R/'out/M1lash_News_DIMA_SVETA_REVIEW.mp4'),'-frames:v','1','-q:v','3',str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True);return p
with ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(one,times))
cols=4;rows=(len(files)+cols-1)//cols;o=Image.new('RGB',(cols*480,rows*270),'#101d30');d=ImageDraw.Draw(o)
for i,p in enumerate(files):
 a=Image.open(p);a.thumbnail((480,270));o.paste(a,((i%cols)*480,(i//cols)*270));d.text(((i%cols)*480+6,(i//cols)*270+245),p.stem,fill='#e96853')
o.save(R/'out/DECODED_CONTACT.jpg');print('decoded samples',len(files))
