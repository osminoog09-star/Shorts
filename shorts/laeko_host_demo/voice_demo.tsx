import React from 'react';
import {createRoot} from 'react-dom/client';
import {HostCard} from './HostCard';
import {NPose} from './Narrator2';
const root=createRoot(document.getElementById('root')!);
const cue=[1.5,2.87,1.77,6.05];
import LS from './liam_lipsync_source.json';
const VIS:Record<string,number>={A:0,B:.3,C:.55,D:.95,E:.65,F:.35,G:.25,H:.55,X:0};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
function pop(t:number,at:number){const d=t-at;return d<0?0:1-Math.exp(-d*13)*Math.cos(d*16)}
function Demo({t}:{t:number}){
 const p=pop(t,1.5);
 const pose:NPose=t<2.65?'point':t<6.05?'talk':'laugh';
 const previous:NPose=t<2.65?'rest':t<6.05?'point':'talk';
 const at=t<2.65?1.5:t<6.05?2.65:6.05;
 const sourceFrame=Math.round((20+t-1.5)*30);
 const v=(i:number)=>t>=1.5&&t<6.05?(VIS[LS.visemes[i]||'X']??0):0;
 const mouth=(v(sourceFrame-1)+2*v(sourceFrame)+v(sourceFrame+1))/4;
 const beat=Math.exp(-Math.max(0,t-cue[2])%0.423*14);
 const title=t<1.5?'ДОСМОТРЕЛ?':t<2.87?'ПОДПИШИСЬ!':'СПАСИБО ЗА ПРОСМОТР!';
 const a=t<1.5?0:t<2.87?1.5:2.87;
 return <div style={{width:1080,height:1920,overflow:'hidden',position:'relative',fontFamily:'DejaVu Sans, sans-serif',color:'#fff',background:'radial-gradient(ellipse at 25% 60%,#293865 0%,#10152a 42%,#070912 90%)'}}>
 <div style={{position:'absolute',inset:-200,opacity:0.4,transform:`perspective(1100px) rotateX(65deg) rotateZ(${-12+Math.sin(t*.2)*3}deg) translateY(500px)`,backgroundImage:'linear-gradient(#52638a55 2px,transparent 2px),linear-gradient(90deg,#52638a55 2px,transparent 2px)',backgroundSize:'110px 110px'}}/>
 {[0,1,2,3,4,5].map(i=><div key={i} style={{position:'absolute',width:160+i*27,height:160+i*27,borderRadius:'50%',border:'2px solid '+(i%2?'#ff73bb':'#76dbff'),opacity:.07,left:40+i*155+Math.sin(t*.45+i)*30,top:260+i*180+Math.cos(t*.3+i)*30,filter:'blur(2px)'}}/>)}
 <div style={{position:'absolute',left:76,top:160,fontSize:33,fontWeight:800,letterSpacing:10,color:'#98b3de'}}>M1LASH</div>
 <div style={{position:'absolute',left:76,top:225,width:80,height:6,borderRadius:4,background:'#73d5ff'}}/>
 <div style={{position:'absolute',left:65,right:80,top:365,fontSize:t<2.87?96:74,lineHeight:1.1,fontWeight:900,letterSpacing:-3,transform:`translateY(${(1-clamp(pop(t,a)))*35}px) scale(${.96+.04*pop(t,a)})`,transformOrigin:'left top'}}>{title}</div>
 <div style={{position:'absolute',left:65,top:650,fontSize:35,color:'#aebedc',opacity:t<cue[0]?1:0}}>Тот самый финал — теперь с голосом</div>
 <div style={{position:'absolute',left:65,top:910,width:380,height:450,opacity:clamp(p),transform:`translateY(${(1-p)*130}px) scale(${1.4*p}) rotate(${Math.sin(t*1.5)*.7}deg)`,transformOrigin:'left bottom'}}><HostCard f={Math.round(t*30)} pose={pose} prev={previous} k={clamp((t-at)/.35)} mouth={mouth}/></div>
 <div style={{position:'absolute',left:65,top:620,opacity:clamp(pop(t,cue[2])),transform:`scale(${pop(t,cue[2])})`,transformOrigin:'left center',padding:'24px 38px',borderRadius:22,fontSize:44,fontWeight:900,background:'linear-gradient(140deg,#ff4969,#d52246)',boxShadow:`0 10px 50px #ff4969${Math.round(25+beat*30).toString(16)}`}}>ПОДПИСЫВАЙСЯ</div>
 <div style={{position:'absolute',left:655,top:1040,width:280,opacity:clamp(pop(t,4.6)),transform:`translateY(${(1-pop(t,4.6))*25}px)`,fontSize:44,fontWeight:800,lineHeight:1.25,color:'#ffdf91'}}>И за<br/>твой лайк!</div>
 <div style={{position:'absolute',left:65,top:1510,fontSize:34,color:'#abc0df',opacity:clamp(pop(t,cue[3]+.4))}}>Как тебе такая концовка?</div>
 <div style={{position:'absolute',left:65,top:1700,fontSize:22,color:'#7886a2',lineHeight:1.5}}>Laeko — DON'T WANNA KNOW!!!<br/>Music provided by NoCopyrightSounds · ncs.io/dontwannaknow</div>
 <div style={{position:'absolute',inset:0,background:'#070912',opacity:clamp((t-11.6)/.4),pointerEvents:'none'}}/>
 </div>
}
(window as any).renderFrame=(f:number)=>root.render(<Demo t={f/30}/>);
(window as any).renderFrame(0);
