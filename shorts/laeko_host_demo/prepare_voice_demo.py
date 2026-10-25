from pathlib import Path
import json
b=Path(__file__).resolve().parent
s=(b/'demo.tsx').read_text()
s=s.replace("const cue=[1.5,4.892,6.139,9.521];", "const cue=[1.5,2.87,1.77,6.05];\nimport LS from './liam_lipsync_source.json';\nconst VIS:Record<string,number>={A:0,B:.3,C:.55,D:.95,E:.65,F:.35,G:.25,H:.55,X:0};")
a=s.index(' const p=pop(');z=s.index(' const beat=',a)
s=s[:a]+''' const p=pop(t,1.5);
 const pose:NPose=t<2.65?'point':t<6.05?'talk':'laugh';
 const previous:NPose=t<2.65?'rest':t<6.05?'point':'talk';
 const at=t<2.65?1.5:t<6.05?2.65:6.05;
 const sourceFrame=Math.round((20+t-1.5)*30);
 const v=(i:number)=>t>=1.5&&t<6.05?(VIS[LS.visemes[i]||'X']??0):0;
 const mouth=(v(sourceFrame-1)+2*v(sourceFrame)+v(sourceFrame+1))/4;
'''+s[z:]
a=s.index(' const title=');z=s.index(' return <div',a)
s=s[:a]+''' const title=t<1.5?'ДОСМОТРЕЛ?':t<2.87?'ПОДПИШИСЬ!':'СПАСИБО ЗА ПРОСМОТР!';
 const a=t<1.5?0:t<2.87?1.5:2.87;
'''+s[z:]
s=s.replace('fontSize:t<cue[2]?96:79','fontSize:t<2.87?96:74')
s=s.replace('Сейчас появится знакомое лицо','Тот самый финал — теперь с голосом')
s=s.replace('mouth={0}','mouth={mouth}')
s=s.replace('opacity:clamp(pop(t,cue[3]))','opacity:clamp(pop(t,4.6))').replace('(1-pop(t,cue[3]))','(1-pop(t,4.6))')
s=s.replace('Спасибо<br/>за просмотр<br/>и лайк!','И за<br/>твой лайк!')
(b/'voice_demo.tsx').write_text(s)
(b/'voice.html').write_text((b/'index.html').read_text().replace('bundle.js','voice_bundle.js'))
s=(b/'render.cjs').read_text().replace("'index.html'","'voice.html'").replace("'silent.mp4'","'voice_silent.mp4'")
(b/'render_voice.cjs').write_text(s)
