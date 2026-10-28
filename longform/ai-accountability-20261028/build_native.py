"""Native huashu-motion chapter sources; no artificial narration or duration.
Each chapter is a local, editable HTML/GSAP composition, then masters are joined.
"""
from pathlib import Path
import json,os,re,shutil
R=Path(__file__).resolve().parent;B=R/'build';UP=Path(os.environ['HUASHU_ROOT'])
JS=r'''
const S=__SCENE__,L=__LIP__,CAPS=__CAPS__,P=__PORTRAIT__;
const W=P?1080:1920,H=P?1920:1080,D=S.duration+.18;
const beatTimes=[0];for(const c of CAPS)if(c.start-beatTimes.at(-1)>=5)beatTimes.push(c.start);
const C=document.querySelector('canvas'),g=C.getContext('2d');C.width=W;C.height=H;
const words=OM.words();const tl=gsap.timeline({paused:true});window.__timelines={film:tl};
beatTimes.forEach((t,i)=>tl.addLabel('scene:beat-'+i,t));
const blue='#58c8ff',orange='#efae70',pink='#ee87c4',green='#72c7aa';
const host=document.querySelector('#host'),cap=document.querySelector('#caption');
const preload=[];for(const pose of ['point','talk'])for(const v of 'ABCDEFGHX'){let im=new Image();im.src=`assets/host/${pose}_${v}.png`;preload.push(im)}
const lerp=(a,b,t)=>a+(b-a)*t;let angle,scale,cx,cy,faces,tags;
function pr(p){let[x,y,z]=p,a=angle;let xx=x*Math.cos(a)-z*Math.sin(a),zz=x*Math.sin(a)+z*Math.cos(a),dep=1/(1-zz*.025);return[cx+xx*scale*dep,cy+(zz*.36-y)*scale*dep]}
function path(pts,color,width=2,fill){g.beginPath();pts.forEach((p,i)=>{let q=pr(p);i?g.lineTo(...q):g.moveTo(...q)});if(fill){g.closePath();g.fillStyle=fill;g.fill()}g.strokeStyle=color;g.lineWidth=width;g.stroke()}
function label(p,s,c='#e8f4ff',size=P?28:25){let q=pr(p);g.font=`700 ${size}px M1`;g.fillStyle=c;g.textAlign='center';g.fillText(s,q[0],q[1])}
function box(p,sz,c,tag=''){let[x,y,z]=p,[dx,dy,dz]=sz.map(x=>x/2),v=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(a=>[x+a[0]*dx,y+a[1]*dy,z+a[2]*dz]);let f=[[[4,5,6,7],.82],[angle>=0?[1,5,6,2]:[0,3,7,4],.63],[[3,2,6,7],1.12]];let rgb=[1,3,5].map(i=>parseInt(c.slice(i,i+2),16));for(let[ids,m]of f){let pts=ids.map(i=>v[i]);faces.push({depth:pts.reduce((a,p)=>a+p[0]*Math.sin(angle)+p[2]*Math.cos(angle),0)/4,pts,c:`rgb(${rgb.map(x=>Math.min(255,Math.round(x*m))).join(',')})`})}if(tag)tags.push([[x,y+dy+.4,z],tag,c])}
function route(a,b,t,c=blue,n=3){path([a,b],'#416782',4);for(let i=0;i<n;i++){let u=(t*.24+i/n)%1,q=pr(a.map((x,j)=>lerp(x,b[j],u)));g.fillStyle=c;g.beginPath();g.arc(...q,5,0,7);g.fill()}}
function machine(x,z,c,title){box([x,0,z],[1.3,1.8,1.1],c,title);for(let y of[-.4,0,.4])box([x,y,z-.57],[.85,.07,.05],'#ccdfed');box([x,-.98,z],[1.6,.12,1.3],'#35506b');for(let a of[-.55,.55])box([x+a,-.65,z-.6],[.07,.07,.05],'#839db3')}
function laptop(x,z,c=blue){box([x,-.6,z],[2.7,.16,1.8],'#91a9c0');box([x,.45,z+.75],[2.7,1.9,.14],c);box([x,.45,z+.64],[2.4,1.55,.06],'#19334a');for(let i=0;i<4;i++)box([x-.22,.85-i*.26,z+.59],[1.45-i*.15,.05,.03],green);for(let i=0;i<7;i++)box([x-1+i*.32,-.48,z],[.19,.03,.5],'#3a526b')}
function doc(x,z,c,title){box([x,0,z],[1.8,2,.16],c,title);for(let j=0;j<4;j++)box([x,.55-j*.3,z-.1],[1.15-j*.08,.07,.04],'#dfebf1')}
function world(t){let shot=Math.max(0,beatTimes.filter(x=>x<=t).length-1),stage=shot%6,pres=[[-.34,1],[.22,1.12],[-.55,1.3],[.40,1.1],[-.12,1.4],[.12,1]];angle=pres[stage][0]+.12*Math.sin(t*.23);scale=(P?85:128)*pres[stage][1];cx=P?540:910;cy=P?800:570;faces=[];tags=[];
for(let i=-7;i<=7;i++)path([[i,-1.1,-3],[i,-1.1,4]],'#29445b',1);for(let j=-3;j<=4;j++)path([[-7,-1.1,j],[7,-1.1,j]],'#29445b',1);
let mode=S.visual;
if(['factory','meter','tokens','ledger'].includes(mode)){
 if(mode==='ledger'){for(let i=0;i<3;i++){let h=.8+(i+1)*.37+Math.max(0,Math.sin(t*.45+i))*.4;box([-3+i*3,-.8+h/2,0],[1.6,h,1.4],[blue,pink,orange][i],['ГЕНЕРАЦИЯ','ПРОВЕРКА','ИСПРАВЛЕНИЯ'][i])}}
 else{[-4,0,4].forEach((x,i)=>machine(x,0,[blue,pink,green][i],['ЗАДАЧА','ОБРАБОТКА','РЕЗУЛЬТАТ'][i]));route([-3,0,0],[-1,0,0],t);route([1,0,0],[3,0,0],t,pink);for(let j=0;j<6;j++)box([-4.5+(t*.9+j*1.7)%9,-.55,2],[.5,.3,.55],mode==='tokens'?green:orange);if(stage===3)box([2.8,0,2],[.12,1.6,1.2],orange,'ПРОВЕРКА')}
}else if(['cache','leak'].includes(mode)){
 for(let side of[-1,1]){let c=side<0?blue:orange;for(let i=0;i<6;i++)box([side*3+(i%3-1)*.75,-.5,Math.floor(i/3)],[.65,.42,.8],c);tags.push([[side*3,1.5,0],side<0?'КОНТЕКСТ А':'КОНТЕКСТ Б',c])}box([0,-.85,0],[.13,.5,3],'#95adc3','ГРАНИЦА');if(stage%2===0){let u=(t-beatTimes[shot])/((beatTimes[shot+1]||D)-beatTimes[shot]);box([3-6*u,.6+Math.sin(u*Math.PI)*.5,0],[.65,.42,.8],orange)}else{route([-3,.5,0],[-3,.5,2],t,blue);route([3,.5,0],[3,.5,2],t,orange)}
}else if(mode==='handoff'){
 [-4,0,4].forEach((x,i)=>machine(x,0,[blue,orange,pink][i],['ВХОД','ДОПУСК','ВЫХОД'][i]));route([-3,0,0],[-1,0,0],t);if(stage%2===0)route([1,0,0],[3,0,0],t,orange);else box([1.8,.1,0],[.18,2.5,2],'#d78d8d','СТОП')
}else if(['permissions','office'].includes(mode)){
 laptop(-4,0);machine(0,0,pink,'ПОМОЩНИК');route([-2.7,0,0],[-1,0,0],t);['ЧИТАТЬ','ЧЕРНОВИК','ОТПРАВИТЬ'].forEach((s,i)=>{let z=-2+i*2,c=[green,blue,orange][i];box([4,0,z],[.18,1.8,1.3],c,s);if(stage%3===i)route([1,0,0],[3.8,0,z],t,c)})
}else if(['laptop','browser'].includes(mode)){
 laptop(0,0);machine(-4,1,blue,'УСТРОЙСТВО');machine(4,1,pink,'ОБЛАКО');stage%2?route([1,0,0],[3,0,1],t,pink):route([-3,0,1],[-1,0,0],t,blue);for(let i=0;i<3;i++)box([-1.5+i*1.4,-.8,-2],[1,.12,.7],[blue,green,orange][i]);
}else if(['tickets','detective'].includes(mode)){
 [-3,0,3].forEach((x,i)=>doc(x,0,[blue,orange,green][i],['ОБРАЩЕНИЕ','ПРОВЕРКА','РЕШЕНИЕ'][i]));route([-1.9,0,0],[-1.1,0,0],t);route([1.1,0,0],[1.9,0,0],t,green);
}else{laptop(-3,0);laptop(3,0,pink);box([0,-.9,0],[.12,.25,4],'#9bb3c8');tags.push([[-3,2,0],'ЗАДАЧА',blue],[[3,2,0],'РЕЗУЛЬТАТ',pink])}
faces.sort((a,b)=>a.depth-b.depth).forEach(f=>path(f.pts,'#3b5971',1.4,f.c));tags.forEach(a=>label(...a));
}
let lastHost='';function draw(t){g.clearRect(0,0,W,H);world(t);let txt=CAPS.find(x=>x.start-.03<=t&&x.end+.1>=t)?.text||'';cap.textContent=txt;cap.style.opacity=txt?1:0;let cue=L.find(c=>c.start<=t&&c.end>=t)?.value||'X',pose=t<2?'point':'talk';let name=`assets/host/${pose}_${cue}.png`;if(name!==lastHost){host.src=name;lastHost=name}host.style.opacity=P||t<5||Math.floor(t/6)%4===2||S.cta?1:0}
OM.clock(tl,draw,D);OM.region('illustrated-process',()=>[30,P?480:310,W-60,P?650:470],'Условная схема процесса');
OM.music({product:'explainer',brand:'M1lash',bpm:102,energy:{'beat-0':.32,'beat-1':.22,'beat-2':.4,'beat-3':.3},ending:'button'});
OM.sfx('paper',.15,{gain:.15});draw(0);
'''
def groups(scene):
 words=scene['words'];out=[];idx=0
 for phrase in re.split(r'(?<=[,.!?;:])\s+',scene['text']):
  n=len(phrase.split());part=words[idx:idx+n];idx+=n
  if part:out.append(dict(text=phrase,start=part[0]['offset']/1e7,end=(part[-1]['offset']+part[-1]['duration'])/1e7))
 # merge single word tails into preceding clause, not arbitrary N-word cards
 for i in range(len(out)-1,0,-1):
  if len(out[i]['text'].split())==1:out[i-1]['text']+=' '+out[i]['text'];out[i-1]['end']=out[i]['end'];out.pop(i)
 return out

def make(s,portrait=False):
 folder=B/'native'/('short' if portrait else f"chapter_{s['id']:02d}");folder.mkdir(parents=True,exist_ok=True)
 for n in ['vendor','assets']:(folder/n).mkdir(exist_ok=True)
 for name,p in [('gsap.min.js',UP/'templates/blank/vendor/gsap.min.js'),('om.js',UP/'runtime/om.js')]:shutil.copy2(p,folder/'vendor'/name)
 for n in ['DejaVuSans.ttf','DejaVuSans-Bold.ttf']:shutil.copy2('/usr/share/fonts/truetype/dejavu/'+n,folder/'assets'/n)
 shutil.copy2(B/s['audio'],folder/'assets/voice.mp3');shutil.copytree(B/'host',folder/'assets/host',dirs_exist_ok=True)
 lip=json.loads((B/f"voice_{s['id']:02d}.rhubarb.json").read_text())['mouthCues'];w,h=(1080,1920) if portrait else (1920,1080)
 meta={'fact':'НОВОСТЬ · ИСТОЧНИКИ ПРОВЕРЕНЫ','example':'УСЛОВНЫЙ ПРИМЕР · НЕ РЕАЛЬНЫЙ ОФИС','analysis':'РАЗБОР M1LASH · ВЫВОДЫ АВТОРА'}[s['kind']]
 sources='Amazon / The Next Web · 27–28.10' if s['id']==2 else 'Cloudflare / Knostic / SGLang · 26–27.10' if s['kind']=='fact' and s['visual'] in ['leak','detective','handoff'] else 'Opera / TechRepublic · 27–28.10' if s['kind']=='fact' else 'Стилизованная кодовая реконструкция'
 wc=[dict(word=x['text'],start=x['offset']/1e7,end=(x['offset']+x['duration'])/1e7)for x in s['words']]
 js=JS.replace('__SCENE__',json.dumps(s,ensure_ascii=False)).replace('__LIP__',json.dumps(lip)).replace('__CAPS__',json.dumps(groups(s),ensure_ascii=False)).replace('__PORTRAIT__',str(portrait).lower())
 title=s['title'].replace('&','&amp;').replace('<','&lt;');hostcss='left:60px;top:995px;width:335px;height:397px' if portrait else 'right:55px;bottom:95px;width:228px;height:270px'
 capcss='left:65px;top:1420px;width:800px;font-size:39px' if portrait else 'left:65px;top:855px;width:1250px;font-size:36px'
 html=f'''<!doctype html><html lang="ru" data-composition-variables='[{{"id":"title","type":"string","label":"Заголовок","default":{json.dumps(s['title'],ensure_ascii=False)}}}]'><head><meta charset="utf-8"><title>M1lash · {title}</title><script src="vendor/gsap.min.js"></script><script src="vendor/om.js"></script><style>
@font-face{{font-family:M1;src:url(assets/DejaVuSans.ttf)}}@font-face{{font-family:M1;src:url(assets/DejaVuSans-Bold.ttf);font-weight:700}}html,body{{margin:0;overflow:hidden;background:#102036}}#film{{width:{w}px;height:{h}px;position:relative;overflow:hidden;font-family:M1;color:#eaf3ff;background:radial-gradient(ellipse at 50% 70%,#233c53,#0e192a 90%)}}canvas{{position:absolute;inset:0}}#brand{{position:absolute;left:65px;top:50px;font-size:27px;font-weight:700;color:#58c8ff}}#title{{position:absolute;left:65px;top:130px;max-width:{w-140}px;font-weight:700;font-size:{48 if portrait else 53}px;line-height:1.18}}#kind{{position:absolute;left:65px;top:{315 if portrait else 225}px;font-size:21px;color:#b9cbdc;max-width:{w-150}px}}#source{{position:absolute;left:65px;top:{370 if portrait else 1010}px;max-width:{w-150}px;font-size:20px;color:#9fb7cb}}#caption{{position:absolute;{capcss};padding:13px 22px;box-sizing:border-box;border-radius:14px;background:#071322ef;font-weight:700;line-height:1.27}}#host{{position:absolute;{hostcss}}}
</style></head><body><div id="film" data-composition-id="film" data-width="{w}" data-height="{h}" data-duration="{s['duration']+.18}"><canvas data-om-id="process"></canvas><div id="brand" data-om-id="brand">M1LASH · НОВОСТИ ИИ · 28.10.2026</div><div id="title" data-om-id="title" data-var-text="title">{title}</div><div id="kind" data-om-id="kind">{meta}</div><div id="source" data-om-id="source">{sources}</div><div id="caption" data-om-id="captions"></div><img id="host" data-om-id="host" src="assets/host/talk_X.png" alt="Ведущий M1lash за столом"><audio id="om-voice" src="assets/voice.mp3" data-start="0" data-duration="{s['duration']}" data-track-index="9" data-volume="1"></audio></div><script type="application/json" id="om-cues">{json.dumps(dict(words=wc),ensure_ascii=False)}</script><script>{js}</script></body></html>'''
 (folder/'materials.md').write_text('M1lash original coded explanatory geometry; these are illustrative diagrams, not proprietary product interfaces. Host art: approved studio/src/Narrator2.tsx and HostCorner framing. Narration: exact Edge ru-RU-DmitryNeural with recorded WordBoundary; actual Rhubarb phonetic cues. Music/SFX: original procedural huashu-motion output. Fonts: DejaVu Sans, native package license. Sources and factual boundaries: ../../../../RESEARCH.md. All library notices retained under vendor.\n')
 (folder/'index.html').write_text(html)
 return str(folder)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--ids');ap.add_argument('--short',action='store_true');a=ap.parse_args()
 scenes=json.loads((B/('short_timeline.json' if a.short else 'timeline.json')).read_text())['scenes']
 if a.ids:wanted={int(x)for x in a.ids.split(',')};scenes=[s for s in scenes if s['id'] in wanted]
 if not a.short:scenes[-1]['cta']=scenes[-1]['id']==37
 for s in scenes:print(make(s,a.short))
