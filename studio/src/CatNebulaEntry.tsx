/** M1lash S7-D25; original HostCard and Rhubarb phonetic visemes.
 * Full-bleed ESA/Hubble CC BY 4.0 photographs, visible source credit.
 */
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, spring} from 'remotion';
import {HostCard} from './EditOutro';
import D from './cat_nebula_timeline.json';
const data=D as any;
const W=1080,H=1920,FPS=30;
const cyan='#55e7fa',amber='#ffc978';
const clips=['nircam.jpg','nircam.jpg','collage.jpg','nircam.jpg','miri.jpg','nircam.jpg','nircam.jpg'];
const titles=['КОСМИЧЕСКИЙ КОТ?!','7500 СВЕТОВЫХ ЛЕТ','ХАББЛ / УЭББ','ГЛАЗ — МОЛОДАЯ ЗВЕЗДА?','УЛЬТРАФИОЛЕТ + ВЕТЕР','КИС-КИС','ГДЕ ТЫ ВИДИШЬ ГЛАЗ?'];
const credit='NASA, ESA, CSA, STScI. Image Processing: J. DePasquale (STScI).';
const V:Record<string,number>={A:0,B:.3,C:.55,D:.95,E:.65,F:.35,G:.25,H:.55,X:0};
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
function chunks(text:string){const words=text.split(/\s+/),out:string[]=[];for(let i=0;i<words.length;i+=5)out.push(words.slice(i,i+5).join(' '));return out;}
const Shot:React.FC=()=>{
 const f=useCurrentFrame(),t=f/FPS;
 const segs=(data.segments||[]) as any[];
 let idx=segs.findIndex(s=>t>=s.start&&t<s.end);
 if(idx<0)idx=segs.length?Math.min(segs.length-1,segs.findIndex(s=>t<s.start)>=0?segs.findIndex(s=>t<s.start):segs.length-1):0;
 const seg=segs[idx]||{start:0,end:10,text:'',kind:'fact'};
 const local=Math.max(0,t-seg.start),dur=Math.max(.5,seg.end-seg.start),progress=clamp(local/dur);
 const img=clips[idx]||'nircam.jpg',scale=1.08+progress*.13;
 const moveX=Math.sin((t+idx)*.32)*24,moveY=(progress-.5)*36;
 const fade=clamp(local/.23)*clamp((dur-local)/.18);
 const host=idx===0||idx===5||idx===6,hostOpacity=host?clamp(local/.35):0;
 const pose=idx===0?'point':idx===5?'laugh':'talk';
 const mouth=V[(data.visemes||[])[f]||'X']||0;
 const parts=chunks(seg.text||''),k=Math.min(parts.length-1,Math.floor(progress*parts.length));
 const subtitle=parts[Math.max(0,k)]||'';
 const headScale=1+.08*spring({frame:f-Math.round(seg.start*FPS),fps:FPS,config:{damping:15}});
 const headline=titles[idx]||'';
 return <AbsoluteFill style={{background:'#070c1c',overflow:'hidden',fontFamily:'Arial, sans-serif',color:'#fff'}}>
  <Audio src={staticFile('cat_nebula/mix.wav')}/>
  {idx===2?
   <div style={{position:'absolute',inset:0,display:'flex'}}>
    <Img src={staticFile('cat_nebula/hubble.jpg')} style={{width:540,height:H,objectFit:'cover',objectPosition:'center'}}/>
    <Img src={staticFile('cat_nebula/nircam.jpg')} style={{width:540,height:H,objectFit:'cover',objectPosition:'center'}}/>
    <div style={{position:'absolute',top:1050,left:90,fontSize:30,fontWeight:900,color:cyan}}>ХАББЛ</div>
    <div style={{position:'absolute',top:1050,right:90,fontSize:30,fontWeight:900,color:amber}}>УЭББ</div>
   </div>:
   <Img src={staticFile('cat_nebula/'+img)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover',objectPosition:'center',transform:`translate(${moveX}px,${moveY}px) scale(${scale})`,filter:'contrast(1.06) saturate(1.12)'}}/>}
  <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(5,9,24,.60) 0%,transparent 28%,transparent 61%,rgba(5,9,24,.82) 92%)'}}/>
  <div style={{position:'absolute',top:105,left:62,right:50,display:'flex',justifyContent:'space-between',fontWeight:900,fontSize:30,letterSpacing:3,color:cyan}}><span>M1LASH / КОСМОС</span><span>29.10.2026</span></div>
  <div style={{position:'absolute',top:250,left:64,right:64,fontSize:64,fontWeight:900,lineHeight:1.04,letterSpacing:-2,textShadow:'0 8px 25px #000',color:idx===3?amber:'#fff',transform:`scale(${headScale})`,transformOrigin:'left center',opacity:fade}}>{headline}</div>
  {idx===3&&<div style={{position:'absolute',top:390,left:70,fontSize:27,fontWeight:800,color:amber,background:'rgba(0,0,0,.55)',padding:'12px 20px',borderRadius:10}}>ГИПОТЕЗА, НЕ ДОКАЗАНО</div>}
  {idx===4&&<div style={{position:'absolute',top:395,left:65,fontSize:25,fontWeight:800,color:cyan}}>СХЕМА / РЕКОНСТРУКЦИЯ</div>}
  {idx===4&&<svg style={{position:'absolute',left:0,top:500,width:W,height:700,opacity:.75}} viewBox="0 0 1080 700">{[0,1,2,3,4].map(i=><path key={i} d={`M${-100+progress*350} ${50+i*135} Q540 ${80+i*135} 1150 ${50+i*135}`} fill="none" stroke={i%2?amber:cyan} strokeWidth={3} strokeDasharray="18 22"/>)}</svg>}
  {host&&<div style={{position:'absolute',left:45,top:1060,width:380,height:450,opacity:hostOpacity,transform:`scale(${.94+.06*hostOpacity})`,transformOrigin:'bottom left'}}><HostCard f={f} pose={pose as any} prev={'talk'} k={.8} mouth={mouth}/></div>}
  <div style={{position:'absolute',left:host?450:80,right:70,top:host?1260:1390,minHeight:150,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',fontSize:host?44:57,fontWeight:900,lineHeight:1.14,textShadow:'2px 3px 4px #000, 0 0 16px #000',opacity:fade}}>{subtitle}</div>
  <div style={{position:'absolute',left:60,right:60,bottom:165,fontSize:18,lineHeight:1.22,opacity:.93,textAlign:'center',textShadow:'0 2px 8px #000'}}>{idx===2?'NASA, ESA, STScI. Image Processing: J. DePasquale (STScI). / '+credit:credit}<br/>ESA/Hubble CC BY 4.0 · адаптация M1lash</div>
  <div style={{position:'absolute',left:65,right:65,bottom:140,height:3,background:'rgba(255,255,255,.25)'}}><div style={{height:3,width:`${Math.min(100,100*f/Math.max(1,data.totalFrames))}%`,background:cyan}}/></div>
 </AbsoluteFill>;
};
const Root:React.FC=()=> <Composition id="cat-nebula-ru" component={Shot} durationInFrames={Math.max(30,data.totalFrames||30)} fps={FPS} width={W} height={H}/>;
registerRoot(Root);
