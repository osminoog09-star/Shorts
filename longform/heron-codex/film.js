import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {createExhibit} from './models_v2.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const clip=new URLSearchParams(location.search).get('clip');
const portrait=clip&&clip!=='ending';
const timeline=await (await fetch(clip?`./timeline-${clip}.json`:'./timeline.json')).json();
export const duration=timeline.reduce((a,s)=>a+s.dur,0);
const W=portrait?1080:1920,H=portrait?1920:1080, TAU=Math.PI*2;
document.getElementById('stage').style.cssText=`width:${W}px;height:${H}px;position:relative;overflow:hidden`;
const overlayCanvas=document.getElementById('overlay');overlayCanvas.width=W;overlayCanvas.height=H;
const renderer=new T.WebGLRenderer({canvas:document.getElementById('gl'),antialias:true,preserveDrawingBuffer:true});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.VSMShadowMap;renderer.shadowMap.autoUpdate=false;
const pmrem=new T.PMREMGenerator(renderer),env=pmrem.fromScene(new RoomEnvironment(),.04).texture;
const scene=new T.Scene();scene.background=new T.Color(0xe8e1d5);scene.environment=env;scene.environmentIntensity=.65;
scene.add(new T.HemisphereLight(0xe9f0f5,0x65564b,.45));
const sun=new T.DirectionalLight(0xffedd5,3.3);sun.position.set(-4,9,6);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-14;sun.shadow.camera.right=14;sun.shadow.camera.top=12;sun.shadow.camera.bottom=-10;sun.shadow.camera.near=.5;sun.shadow.camera.far=35;sun.shadow.bias=-.0003;sun.shadow.normalBias=.025;sun.shadow.radius=3;sun.shadow.blurSamples=4;scene.add(sun);
const fill=new T.DirectionalLight(0xbccfdf,.85);fill.position.set(6,3,-4);scene.add(fill);
const rim=new T.DirectionalLight(0xffd5a0,1.3);rim.position.set(-3,6,-6);scene.add(rim);
const cam=new T.PerspectiveCamera(34,W/H,.1,100);
const {models}=createExhibit(scene);
let shadowScene='';
const rt=new T.WebGLRenderTarget(W,H,{depthTexture:new T.DepthTexture(W,H,T.UnsignedShortType)});
const post=new T.Scene(),postCam=new T.OrthographicCamera(-1,1,1,-1,0,1);
const focusMaterial=new T.ShaderMaterial({uniforms:{image:{value:rt.texture},depth:{value:rt.depthTexture},focus:{value:15}},vertexShader:`varying vec2 uv0;void main(){uv0=uv;gl_Position=vec4(position.xy,0.,1.);}`,fragmentShader:`uniform sampler2D image;uniform sampler2D depth;uniform float focus;varying vec2 uv0;
void main(){float d=texture2D(depth,uv0).x;float z=.1*100./(100.-d*(100.-.1));float coc=clamp(abs(z-focus)*.0015,0.,.003);vec2 e=vec2(coc,coc*${W/H});gl_FragColor=texture2D(image,uv0)*.4+(texture2D(image,uv0+vec2(e.x,0.))+texture2D(image,uv0-vec2(e.x,0.))+texture2D(image,uv0+vec2(0.,e.y))+texture2D(image,uv0-vec2(0.,e.y)))*.15;
#include <tonemapping_fragment>
#include <colorspace_fragment>
}`});post.add(new T.Mesh(new T.PlaneGeometry(2,2),focusMaterial));
const ov=document.getElementById('overlay'),ctx=ov.getContext('2d');
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
function wrap(text,max,font){ctx.font=font;let out=[],line='';for(const word of text.split(' ')){if(ctx.measureText(line+word).width>max&&line){out.push(line.trim());line='';}line+=word+' ';}if(line)out.push(line.trim());return out;}
function roundRect(x,y,w,h,r,c){ctx.fillStyle=c;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
function text(s,x,y,size=30,color='#26363a',weight=600){ctx.font=`${weight} ${size}px DejaVu Sans`;ctx.fillStyle=color;ctx.fillText(s,x,y);}
function overlay(s,t,total){ctx.clearRect(0,0,W,H);ctx.fillStyle='#eee9e1';ctx.fillRect(0,0,W,portrait?435:265);ctx.fillRect(0,H-70,W,70);
 if(portrait){
  text('M1LASH / ИНЖЕНЕРИЯ ДРЕВНОСТИ',70,94,25,'#53656a',700);
  wrap(s.title,940,'700 62px DejaVu Sans').forEach((l,i)=>text(l,70,194+i*72,62,'#26363a',700));
  wrap(s.key,940,'600 35px DejaVu Sans').forEach((l,i)=>text(l,70,365+i*43,35,'#586f78',600));
  roundRect(55,1480,970,250,30,'rgba(255,253,247,.96)');
  const cue=s.cues?.find(c=>t>=c.start+.15&&t<c.end+.3);
  wrap(cue?.text||'',870,'600 43px DejaVu Sans').slice(0,4).forEach((l,i)=>text(l,100,1545+i*49,43,'#26363a',600));
  text('ПОЛНАЯ ИСТОРИЯ — НА КАНАЛЕ',70,1800,30,'#53656a',700);
  text('Учебная 3D-реконструкция · размеры условны',70,1852,22,'#607078');
  ctx.fillStyle='#8db8b0';ctx.fillRect(0,H-5,W*total/duration,5);
  let fade=Math.max(1-t/.3,1-(s.dur-t)/.3,0);if(fade>0){ctx.fillStyle=`rgba(238,233,225,${Math.min(1,fade)})`;ctx.fillRect(0,0,W,H);}
  return;
 }
 text('M1LASH / ИНЖЕНЕРИЯ ДРЕВНОСТИ',90,68,22,'#53656a',700);text(String(s.index+1).padStart(2,'0')+' / '+timeline.length,1710,68,22,'#53656a');
 const titleLines=wrap(s.title,1470,'700 48px DejaVu Sans');titleLines.forEach((l,i)=>text(l,90,140+i*55,48,'#26363a',700));
 const lines=wrap(s.key,1350,'600 33px DejaVu Sans');lines.forEach((l,i)=>text(l,92,218+i*40,33,'#586f78',600));
 roundRect(90,890,1740,115,24,'rgba(255,253,247,.94)');
 const parts=s.text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[s.text];let n=s.text.length,p=Math.min(.999,t/Math.max(1,s.speech))*n,a=0,sub=parts.at(-1);for(const part of parts){a+=part.length;if(p<a){sub=part.trim();break;}}
 if(s.cues?.length){const cue=s.cues.find(c=>t>=c.start+.15&&t<c.end+.35);sub=cue?.text||'';}
 const subtitle=wrap(sub,1630,'600 30px DejaVu Sans');subtitle.slice(0,3).forEach((l,i)=>text(l,125,932+i*33,30,'#26363a',600));
 text('УЧЕБНАЯ 3D-РЕКОНСТРУКЦИЯ · МАСШТАБЫ УСЛОВНЫ',90,1044,17,'#607078');text(s.source,1300,1044,17,'#607078');
 ctx.fillStyle='#8db8b0';ctx.fillRect(0,H-5,W*total/duration,5);
 // Full-scene cuts use a short cream dip instead of overlapping labels.
 let fade=Math.max(1-t/.45,1-(s.dur-t)/.45,0);if(fade>0){ctx.fillStyle=`rgba(238,233,225,${Math.min(1,fade)})`;ctx.fillRect(0,0,W,H);}
}
export function renderAt(time){time=Math.max(0,Math.min(duration-.001,time));const s=timeline.find(s=>time<s.start+s.dur)||timeline.at(-1),t=time-s.start;
 Object.values(models).forEach(o=>o.g.visible=false);
 const focus=s.focus;
 if(s.model==='all'){
  for(const [j,k]of ['coin','door','steam'].entries()){const o=models[k];o.g.visible=true;o.g.scale.setScalar(.56);o.g.position.set((j-1)*4.4,-1.05,0);o.update(t+j*1.7,focus);}
 }else{const o=models[s.model];o.g.visible=true;o.g.scale.setScalar(1);o.g.position.set(0,0,0);o.update(t,focus);}
 const cut=Math.floor(t/8),v=(t%8)/8;let az=-.55+(cut%3)*.28+.16*smooth(v),el=.24;
 let r=portrait?(s.model==='coin'?27:23):(s.model==='all'?19:s.model==='archive'?15:s.model==='door'?20:16);
 const target=new T.Vector3(0,s.model==='door'?.85:s.model==='archive'?-1.1:.05,0);if(s.model==='archive'){el=.75;az=-.25+.15*smooth(v);}
 if(!portrait&&s.model==='coin'){
  if(focus==='lever'){target.set(-.6,.55,.1);r=11.5;el=.34;az=-.22+.16*smooth(v);}
  if(focus==='valve'){target.set(.8,-.65,.65);r=11.8;az=.16+.16*smooth(v);}
  if(focus==='reset'){target.set(-.65,.15,.25);r=13;el=.33;}
  if(focus==='explode'){target.y=.55;r=18;el=.4;}
 }
 if(!portrait&&s.model==='door'){
  if(focus==='heat'){target.set(-1.7,-.2,.45);r=15.5;az=-.55+.18*smooth(v);}
  if(focus==='bucket'){target.set(.65,-.4,.4);r=14.5;az=.20+.16*smooth(v);}
 }
 if(!portrait&&s.model==='steam'){
  if(focus==='jets'){target.set(0,1.3,0);r=11;el=.16;az=.2+.18*smooth(v);}
  if(focus==='detail'){target.set(1.1,-.25,.2);r=18;el=.33;}
 }
 r*=1-.025*smooth(v);el+=.02*Math.sin(t*.15);
 cam.position.set(Math.sin(az)*Math.cos(el)*r,target.y+Math.sin(el)*r,Math.cos(az)*Math.cos(el)*r);cam.lookAt(target);cam.updateMatrixWorld();
 const sk=`${s.model}/${s.index}`;if(sk!==shadowScene){renderer.shadowMap.needsUpdate=true;shadowScene=sk;}
 if(['lever','valve','jets','detail','bucket'].includes(focus)){focusMaterial.uniforms.focus.value=r;renderer.setRenderTarget(rt);renderer.render(scene,cam);renderer.setRenderTarget(null);renderer.render(post,postCam);}else renderer.render(scene,cam);overlay(s,t,time);
}
