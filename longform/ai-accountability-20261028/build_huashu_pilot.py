"""Build the opening as a native huashu-motion composition from accepted voice.
Source assets generated here are illustrative, never proprietary product interfaces.
"""
from pathlib import Path
import json,shutil,os,subprocess,re
ROOT=Path(__file__).resolve().parent;B=ROOT/'build';P=B/'huashu-pilot';P.mkdir(exist_ok=True)
UP=Path(os.environ.get('HUASHU_ROOT',str(ROOT.parents[1]/'skills/ext/huashu-motion')))
for name in ['assets','vendor']:(P/name).mkdir(exist_ok=True)
for name,src in [('gsap.min.js',UP/'templates/blank/vendor/gsap.min.js'),('om.js',UP/'runtime/om.js')]:shutil.copy2(src,P/'vendor'/name)
shutil.copy2(B/'voice_00.mp3',P/'assets/voice.mp3')
shutil.copy2('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',P/'assets/DejaVuSans.ttf')
shutil.copy2('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',P/'assets/DejaVuSans-Bold.ttf')
m=json.loads((B/'voice_00.json').read_text());words=[dict(word=w['text'],start=w['offset']/1e7,end=(w['offset']+w['duration'])/1e7) for w in m['words']]
groups=[];wi=0
for phrase in re.split(r'(?<=[,.!?;:])\s+',m['text']):
 n=len(phrase.split());part=words[wi:wi+n];wi+=n
 if part:groups.append(dict(text=phrase,start=part[0]['start'],end=part[-1]['end']))
D=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(B/'voice_00.mp3')]))
html='''<!doctype html>
<html lang="ru" data-composition-variables='[{"id":"accent","type":"color","label":"Акцент M1lash","default":"#58c8ff"},{"id":"question","type":"string","label":"Вопрос выпуска","default":"КТО ПРОВЕРЯЕТ РЕЗУЛЬТАТ?"}]'>
<head><meta charset="utf-8"><title>M1lash · opening pilot · huashu-motion</title>
<script src="vendor/gsap.min.js"></script><script src="vendor/om.js"></script>
<style>@font-face{font-family:M1;src:url(assets/DejaVuSans.ttf)}@font-face{font-family:M1;src:url(assets/DejaVuSans-Bold.ttf);font-weight:700}
html,body{margin:0;overflow:hidden;background:#0c1729}#film{position:relative;width:1920px;height:1080px;font-family:M1;color:#eaf3ff;overflow:hidden;background:radial-gradient(ellipse at 45% 70%,#24445d,#0c1729 80%)}
#brand{position:absolute;left:72px;top:50px;color:var(--accent);font-size:30px;font-weight:700;letter-spacing:2px}#date{position:absolute;right:75px;top:55px;font-size:25px;color:#a9bed0}#title{position:absolute;left:72px;top:124px;font-size:66px;font-weight:700;letter-spacing:-2px;max-width:1710px;line-height:1.14}#context{position:absolute;left:76px;top:224px;font-size:23px;color:#c3d4e3}
#space{position:absolute;left:100px;top:285px;width:1700px;height:530px;perspective:1600px}#world{position:absolute;inset:0;transform-style:preserve-3d}#floor{position:absolute;left:-400px;top:320px;width:2400px;height:900px;background:repeating-linear-gradient(0deg,transparent 0 74px,#68a9c518 75px 76px),repeating-linear-gradient(90deg,transparent 0 74px,#68a9c518 75px 76px);transform:rotateX(76deg);transform-origin:top;opacity:.8}
.node{position:absolute;top:60px;width:360px;height:280px;border:2px solid #5a8ba5;border-radius:28px;background:linear-gradient(145deg,#203a50,#122335);box-shadow:0 35px 70px #0007,inset 0 0 0 8px #ffffff04;transform-style:preserve-3d}.label{font-size:29px;letter-spacing:1px;font-weight:700;margin:30px 32px;color:var(--accent)}.detail{font-size:22px;line-height:1.5;margin:28px 32px;color:#aac2d3}.chip{display:flex;align-items:center;justify-content:center;margin:18px 32px;width:290px;height:110px;border-radius:14px;border:2px solid #58c8ff;background:#173b55;color:#e7f5ff;font-size:32px;font-weight:700;transform:translateZ(35px)}#request{left:0}#engine{left:660px;border-color:#a98bca}#answer{left:1320px;border-color:#f0ad6b}#answer .label{color:#f0ad6b}#answer .chip{border-color:#f0ad6b;background:#553e2b}#links{position:absolute;inset:0;width:1700px;height:530px}#packet{position:absolute;left:0;top:150px;width:90px;height:64px;border-radius:10px;background:#58c8ff;box-shadow:0 8px 30px #58c8ff66;border:3px solid #bdeaff;transform:translateZ(95px)}
#evidence{position:absolute;left:180px;top:335px;width:1480px;display:flex;gap:30px;transform-style:preserve-3d}.source{width:450px;height:280px;border-radius:24px;border:2px solid #718ba4;background:#112338;box-shadow:0 25px 50px #0006;display:flex;flex-direction:column;justify-content:center;padding:35px;box-sizing:border-box}.source b{font-size:45px;color:#eaf3ff}.source span{font-size:26px;line-height:1.4;margin-top:18px;color:#b6d0e3}.source em{font-size:20px;line-height:1.4;margin-top:15px;font-style:normal;color:#7cb1cc}
#question{position:absolute;left:160px;top:374px;width:1570px;font-size:100px;font-weight:700;line-height:1.1;color:#f5eee4;text-wrap:balance}#office{position:absolute;left:160px;top:580px;display:flex;gap:60px}.step{border:2px solid #58c8ff;border-radius:20px;background:#183147;font-size:30px;padding:30px 45px;box-shadow:0 25px 45px #0006}
#caption{position:absolute;left:80px;top:870px;max-width:1360px;min-height:52px;padding:15px 26px;background:#07111edb;border-radius:14px;font-size:36px;font-weight:700;line-height:1.3}#status{position:absolute;left:80px;bottom:46px;font-size:20px;color:#98aec3}#pilot{position:absolute;right:80px;bottom:50px;color:#ca9bb5;font-size:19px}
</style></head><body><div id="film" data-composition-id="film" data-width="1920" data-height="1080" data-duration="__D__">
<div id="brand" data-om-id="brand">M1LASH · НОВОСТИ ИИ</div><div id="date" data-om-id="date">28 октября 2026</div><div id="title" data-om-id="title">В ТВОЁМ ОТВЕТЕ — ЧУЖОЙ ДОКУМЕНТ</div><div id="context" data-om-id="context">Условная схема · не интерфейс сервиса</div>
<div id="space" data-om-id="diagram"><div id="world"><div id="floor"></div><svg id="links" viewBox="0 0 1700 530"><path d="M360 200H660M1020 200H1320" stroke="#4e809f" fill="none" stroke-width="6" stroke-dasharray="12 13"/></svg><div class="node" id="request" data-om-id="request"><div class="label">ТВОЙ ЗАПРОС</div><div class="chip">ДОКУМЕНТ А</div></div><div class="node" id="engine" data-om-id="engine"><div class="label">ОБРАБОТКА</div><div class="detail">Контекст запроса →<br>подготовка ответа</div></div><div class="node" id="answer" data-om-id="answer"><div class="label">ПОЛУЧЕННЫЙ ОТВЕТ</div><div class="chip">ФРАГМЕНТ Б</div></div><div id="packet" data-om-id="packet"></div></div></div>
<div id="evidence" data-om-id="sources"><div class="source" id="cloud"><b>Cloudflare</b><span>Граница между запросами</span><em>Раскрытие 26.10.2026<br>Инцидент исправлен в сентябре</em></div><div class="source" id="amazon"><b>Amazon</b><span>Счётчик ≠ полезная работа</span><em>Публикация 27.10.2026</em></div><div class="source" id="opera"><b>Opera</b><span>Часть работы — на устройстве</span><em>Анонс 27.10.2026 · early preview</em></div></div>
<div id="question" data-om-id="question" data-var-text="question">КТО ПРОВЕРЯЕТ РЕЗУЛЬТАТ?</div><div id="office" data-om-id="office"><div class="step">ЗАДАЧА</div><div class="step">ИСТОЧНИК</div><div class="step">ПРОВЕРКА</div><div class="step">ДЕЙСТВИЕ</div></div>
<div id="caption" data-om-id="captions"></div><div id="status">Кодовая реконструкция · источники и полный разбор — в основном выпуске</div><div id="pilot">ПИЛОТ ПОСТАНОВКИ · НЕ ПОЛНЫЙ ВЫПУСК</div>
<audio id="om-voice" src="assets/voice.mp3" data-start="0" data-duration="__D__" data-track-index="9" data-volume="1"></audio></div>
<script type="application/json" id="om-cues">__CUES__</script>
<script>
const captions=__CAPTIONS__;const tl=gsap.timeline({paused:true});window.__timelines={film:tl};const D=__D__,words=OM.words(),V=OM.vars();
const cue=(w)=>OM.cue(w), cloud=cue('Cloudflare'), amazon=cue('Amazon'), opera=cue('Opera'), question=cue('вопрос'),office=cue('офис');
tl.addLabel('scene:foreign-context',0).addLabel('scene:report',cloud).addLabel('scene:work-metrics',amazon).addLabel('scene:local-ai',opera).addLabel('scene:question',question).addLabel('scene:office',office);
const $=s=>document.querySelector(s),show=(id,o)=>$(id).style.opacity=o;
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
function draw(t){
const first=t<cloud,second=t>=cloud&&t<question,last=t>=question;
show('#space',first?1:0);show('#evidence',second?1:0);show('#question',last?1:0);show('#office',t>=office?1:0);
$('#world').style.transform=`rotateY(${-9+8*Math.sin(t*.23)}deg) rotateX(${3+Math.cos(t*.16)}deg) translateZ(${30+35*Math.sin(t*.18)}px)`;
const u=smooth((t-cue('документ'))/(cue('чужого')-cue('документ')));$('#packet').style.transform=`translate3d(${150+1300*u}px,${-100*Math.sin(u*Math.PI)}px,95px)`;$('#packet').style.background=u>.58?'#f0ad6b':'#58c8ff';
const stage=t<amazon?0:t<opera?1:2;
['#cloud','#amazon','#opera'].forEach((id,i)=>{$(id).style.transform=`translate3d(0,${i===stage?-35:20}px,${i===stage?80:0}px) rotateY(${i===stage?0:-5}deg)`;$(id).style.borderColor=i===stage?'#58c8ff':'#425a72';});
$('#title').textContent=first?'В ТВОЁМ ОТВЕТЕ — ЧУЖОЙ ДОКУМЕНТ':second?'ТРИ НОВОСТИ. ОДИН ВОПРОС.':'ИИ УЖЕ РАБОТАЕТ ЗА ТЕБЯ';
$('#question').style.transform=`translateY(${35*(1-smooth((t-question)/.7))}px)`;
$('#office').style.transform=`translateY(${40*(1-smooth((t-office)/.6))}px)`;
let cap=captions.find(c=>c.start-.04<=t&&c.end+.12>=t)?.text||'';$('#caption').textContent=cap;show('#caption',cap?1:0);
}
OM.clock(tl,draw,D);OM.music({product:'explainer',bpm:104,gain:.12});OM.sfx('thud',cue('чужого'),{gain:.3});OM.sfx('tick',amazon,{gain:.25});OM.sfx('whoosh',opera,{gain:.2});draw(0);
</script></body></html>'''
html=html.replace('__D__',str(D)).replace('__CUES__',json.dumps({'words':words},ensure_ascii=False)).replace('__CAPTIONS__',json.dumps(groups,ensure_ascii=False))
(P/'index.html').write_text(html)
print(P)
