import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const timeline=await (await fetch('./timeline.json')).json();
export const duration=timeline.reduce((a,s)=>a+s.dur,0);
const W=1920,H=1080, TAU=Math.PI*2;
const C={cream:0xeee9e1,lav:0xcac5ef,mint:0x9ed6bf,blue:0x80bbdb,peach:0xe4b09b,gold:0xc9a467,ink:0x26363a,white:0xf9f6ed,water:0x399fcd};
const renderer=new T.WebGLRenderer({canvas:document.getElementById('gl'),antialias:true,preserveDrawingBuffer:true});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=.9;
const pmrem=new T.PMREMGenerator(renderer), env=pmrem.fromScene(new RoomEnvironment(),.05).texture;
const scene=new T.Scene();scene.background=new T.Color(C.cream);scene.environment=env;
scene.add(new T.HemisphereLight(0xffffff,0xc4bab4,1.05));const sun=new T.DirectionalLight(0xffffff,2.0);sun.position.set(4,8,6);scene.add(sun);
const fill=new T.DirectionalLight(0xc4ceff,.7);fill.position.set(-6,4,-3);scene.add(fill);
const cam=new T.PerspectiveCamera(32,W/H,.1,100);
const mat=(color,gloss=false)=>new T.MeshPhysicalMaterial({color,roughness:gloss?.22:.64,metalness:0,clearcoat:gloss?.65:0,envMapIntensity:.65});
const M={};for(const [k,c]of Object.entries(C))M[k]=mat(c,k==='water'||k==='gold');
M.gold=new T.MeshStandardMaterial({color:C.gold,metalness:.7,roughness:.3});
M.glass=new T.MeshPhysicalMaterial({color:0xb3d8df,transparent:true,opacity:.14,roughness:.3,depthWrite:false,side:T.DoubleSide});
function mesh(g,m,parent=scene){const o=new T.Mesh(g,typeof m==='string'?M[m]:m);parent.add(o);return o;}
function box(x,y,z,w,h,d,m,p){const o=mesh(new RoundedBoxGeometry(w,h,d,3,Math.min(w,h,d)*.13),m,p);o.position.set(x,y,z);return o;}
function cyl(x,y,z,r,h,m,p,r2=r){const o=mesh(new T.CylinderGeometry(r,r2,h,32),m,p);o.position.set(x,y,z);return o;}
function ball(x,y,z,r,m,p){const o=mesh(new T.SphereGeometry(r,32,20),m,p);o.position.set(x,y,z);return o;}
function pipe(points,r,m,p){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(q=>new T.Vector3(...q))),24,r,8,false),m,p);}
function shadow(x,z,rx,rz,p){const c=document.createElement('canvas');c.width=128;c.height=128;const q=c.getContext('2d'),g=q.createRadialGradient(64,64,3,64,64,60);g.addColorStop(0,'rgba(44,40,58,.22)');g.addColorStop(1,'rgba(44,40,58,0)');q.fillStyle=g;q.fillRect(0,0,128,128);const o=mesh(new T.PlaneGeometry(rx,rz),new T.MeshBasicMaterial({map:new T.CanvasTexture(c),transparent:true,depthWrite:false}),p);o.rotation.x=-Math.PI/2;o.position.set(x,-2.47,z);}
const floor=mesh(new T.PlaneGeometry(200,200),mat(C.cream));floor.rotation.x=-Math.PI/2;floor.position.y=-2.5;
function group(){const g=new T.Group();scene.add(g);return g;}
function slab(g,w=7,d=4){box(0,-2.28,0,w,.38,d,'white',g);shadow(0,0,w*1.5,d*1.7,g);}
// Original educational reconstruction of Pneumatics 21. Open front exposes mechanism.
function coinModel(){const g=group();slab(g);box(0,0,-.95,5,4.1,.28,'lav',g);// Left wall removed for the educational cutaway.
box(2.35,0,0,.3,4.1,2.2,'lav',g);
 const roof=box(0,2.1,0,5.1,.25,2.3,'mint',g);box(-1.2,2.24,.0,1.4,.08,.22,'ink',g);
 cyl(1.1,-.25,-.15,1,2.8,'glass',g);const water=cyl(1.1,-.6,-.15,.9,1.7,'water',g);cyl(1.1,-1.7,-.15,1.05,.18,'gold',g);
 cyl(-.4,-.6,0,.13,2.9,'gold',g);
 const lever=new T.Group();lever.position.set(-.4,.55,.05);g.add(lever);box(.05,0,0,3.25,.14,.22,'gold',lever);const pan=cyl(-1.25,.06,0,.45,.08,'peach',lever);
 const lid=cyl(1.07,-.2,0,.22,.15,'gold',g);const link=box(1.07,.15,0,.07,.7,.07,'gold',g);pipe([[1.1,-1.6,0],[1.1,-1.6,1.25],[1.1,-1.85,1.5]],.13,'gold',g);
 const cup=cyl(1.1,-2,1.55,.43,.35,'peach',g,.36);const cuplevel=cyl(1.1,-1.85,1.55,.34,.05,'water',g);
 const coin=cyl(-1.65,3.2,0,.25,.09,'gold',g);coin.rotation.x=Math.PI/2;
 const stream=cyl(1.1,-1.75,1.5,.065,.4,'water',g);
 const coins=[];for(let i=0;i<7;i++){const c=cyl(-1.8+i*.11,-2.01,.18+i*.03,.19,.05,'gold',g);coins.push(c);}
 return {g,update(t,focus){let u=(t%9)/9;const on=u>.2&&u<.64;lever.rotation.z=on?.16:0;coin.visible=u<.78;coin.rotation.x=u<.2?Math.PI*.5*(1-u/.2):0;coin.position.set(u<.64?-1.65: -1.65+(u-.64)*.7,u<.2?3.2-u*13.5:u<.64?.5:.5-(u-.64)*15,0);lid.position.y=-.2+(on?.35:0);link.position.y=.15+(on?.25:0);stream.visible=on;water.scale.y=1-(on?(u-.2)*.15:0);cuplevel.visible=u>.24;roof.position.y=focus==='explode'?3.0:2.1;}};}
// Pneumatics 37: heat -> displaced water -> bucket -> chains -> door pivots.
function doorModel(){const g=group();slab(g,8.5,4.2);box(0,-.3,-.2,5.4,.25,2.4,'lav',g);box(0,3.9,-.6,5.8,.35,1.3,'white',g);
 const a=new T.Group(),b=new T.Group();a.position.set(-1.6,1.6,-.65);b.position.set(1.6,1.6,-.65);g.add(a,b);box(.8,0,0,1.55,3.3,.2,'mint',a);box(-.8,0,0,1.55,3.3,.2,'mint',b);ball(1.35,0,.2,.1,'gold',a);ball(-1.35,0,.2,.1,'gold',b);
 for(const x of [-2.4,2.4])cyl(x,1.7,-.5,.23,4,'white',g);
 const reservoir=ball(-2.2,-.9,.2,.85,'glass',g);ball(-2.2,-1.15,.2,.66,'water',g);
 box(-3.25,.35,1,.95,.75,1.0,'peach',g);cyl(-3.25,.82,1,.52,.16,'gold',g);
 const flames=[];for(let i=0;i<4;i++){const o=mesh(new T.ConeGeometry(.12+.04*i,.55+.1*i,12),mat(0xef8d5d),g);o.position.set(-3.4+i*.12,1.15,1);flames.push(o);}
 pipe([[-3.25,.3,1],[-3.25,-.8,1],[-2.2,-.8,.2]],.065,'gold',g);pipe([[-2.2,-1,.2],[-1.7,.2,.4],[.5,.2,.4],[.5,-.8,.4]],.06,'gold',g);
 const bucket=cyl(.5,-1.3,.5,.45,.75,'peach',g,.36),bv=cyl(.5,-1.15,.5,.35,.06,'water',g);
 const pulley=cyl(.5,.8,.5,.28,.12,'gold',g);pulley.rotation.x=Math.PI/2;
 const chain=box(.5,-.15,.5,.045,1.7,.045,'gold',g);pipe([[.5,.8,.5],[-1.6,.8,-.65],[-1.6,1.6,-.65]],.035,'gold',g);pipe([[.5,.8,.5],[1.6,.8,-.65],[1.6,1.6,-.65]],.035,'gold',g);
 const weight=box(2.7,-1.1,.1,.55,.65,.55,'gold',g);pipe([[2.7,-.6,.1],[2.7,.9,.1],[1.6,.9,-.65]],.03,'gold',g);
 const dots=[];for(let i=0;i<8;i++)dots.push(ball(-2.2,-.6,.2,.07,'peach',g));
 return {g,update(t){const u=(t%14)/14,p=u<.6?Math.min(1,u/.5):Math.max(0,(1-u)/.4);a.rotation.y=-p*1.05;b.rotation.y=p*1.05;bucket.position.y=-.6-p*1;bv.position.y=bucket.position.y+.1;bv.scale.y=.2+p*2;weight.position.y=-1.3+p*.7;chain.scale.y=.6+p*.5;chain.position.y=.2-p*.5;flames.forEach((f,i)=>{f.visible=u<.65;f.scale.setScalar(.88+.12*Math.sin(t*5+i));});dots.forEach((d,i)=>{d.position.y=-.3+.23*Math.sin(t+i);d.position.x=-2.2+.3*Math.cos(t*.7+i);});}};}
// Pneumatics 50: steam jets tangent to a pivoted sphere.
function steamModel(){const g=group();slab(g,6,4);cyl(0,-1.6,0,1.3,.9,'gold',g);cyl(0,-1.12,0,1.4,.16,'peach',g);
 pipe([[-1.05,-1.1,0],[-1.3,0,0],[-1.25,1.4,0],[-.86,1.4,0]],.1,'gold',g);pipe([[1.05,-1.1,0],[1.3,0,0],[1.25,1.4,0],[.86,1.4,0]],.1,'gold',g);
 const rotor=new T.Group();rotor.position.y=1.4;g.add(rotor);ball(0,0,0,.9,'mint',rotor);pipe([[0,.7,.35],[0,1.0,.35],[0,1.0,.9]],.11,'gold',rotor);pipe([[0,-.7,-.35],[0,-1,-.35],[0,-1,-.9]],.11,'gold',rotor);
 const steam=[];for(const sign of [-1,1])for(let i=0;i<9;i++){const p=ball(0,sign,sign,.07,'white',rotor);p.material=M.white.clone();p.material.transparent=true;steam.push({p,i,sign});}
 const fire=[];for(let i=0;i<6;i++){const f=mesh(new T.ConeGeometry(.11,.5,12),mat(i%2?0xf1b265:0xe08c6e),g);f.position.set(Math.cos(i)*.6,-2.1,Math.sin(i)*.6);fire.push(f);}
 return {g,update(t){rotor.rotation.x=t*1.4;steam.forEach(({p,i,sign})=>{let v=((t*1.1+i/9)%1);p.position.set(.08*Math.sin(i+t),sign,sign*(1+v*1.8));p.scale.setScalar(1+v*1.5);p.material.opacity=1-v;});fire.forEach((f,i)=>f.scale.y=.8+.2*Math.sin(t*6+i));}};}
const models={coin:coinModel(),door:doorModel(),steam:steamModel()};
const rt=new T.WebGLRenderTarget(W,H,{depthTexture:new T.DepthTexture(W,H,T.UnsignedShortType)});
const post=new T.Scene(),postCam=new T.OrthographicCamera(-1,1,1,-1,0,1);
const focusMaterial=new T.ShaderMaterial({uniforms:{image:{value:rt.texture},depth:{value:rt.depthTexture},focus:{value:15}},vertexShader:`varying vec2 uv0;void main(){uv0=uv;gl_Position=vec4(position.xy,0.,1.);}`,fragmentShader:`uniform sampler2D image;uniform sampler2D depth;uniform float focus;varying vec2 uv0;
void main(){float d=texture2D(depth,uv0).x;float z=.1*100./(100.-d*(100.-.1));float coc=clamp(abs(z-focus)*.0015,0.,.003);vec2 e=vec2(coc,coc*1.7778);gl_FragColor=texture2D(image,uv0)*.4+(texture2D(image,uv0+vec2(e.x,0.))+texture2D(image,uv0-vec2(e.x,0.))+texture2D(image,uv0+vec2(0.,e.y))+texture2D(image,uv0-vec2(0.,e.y)))*.15;
#include <tonemapping_fragment>
#include <colorspace_fragment>
}`});post.add(new T.Mesh(new T.PlaneGeometry(2,2),focusMaterial));
const ov=document.getElementById('overlay'),ctx=ov.getContext('2d');
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
function wrap(text,max,font){ctx.font=font;let out=[],line='';for(const word of text.split(' ')){if(ctx.measureText(line+word).width>max&&line){out.push(line.trim());line='';}line+=word+' ';}if(line)out.push(line.trim());return out;}
function roundRect(x,y,w,h,r,c){ctx.fillStyle=c;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
function text(s,x,y,size=30,color='#26363a',weight=600){ctx.font=`${weight} ${size}px DejaVu Sans`;ctx.fillStyle=color;ctx.fillText(s,x,y);}
function overlay(s,t,total){ctx.clearRect(0,0,W,H);
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
  for(const [j,o]of Object.values(models).entries()){o.g.visible=true;o.g.scale.setScalar(.56);o.g.position.set((j-1)*4.4,-1.05,0);o.update(t+j*1.7,focus);}
 }else{const o=models[s.model];o.g.visible=true;o.g.scale.setScalar(1);o.g.position.set(0,0,0);o.update(t,focus);}
 const cut=Math.floor(t/9),v=(t%9)/9;let az=(-.28+cut*.3)%1.1-.35,el=.25;
 let r=s.model==='all'?21:s.model==='door'?19:15;
 if(['lever','valve','reset','jets','detail','bucket','heat'].includes(focus))r*=.8;
 az+=.18*smooth(v);el+=.03*Math.sin(t*.15);r*=1-.025*smooth(v);
 const target=new T.Vector3(0,s.model==='door'?.6:.1,0);cam.position.set(Math.sin(az)*Math.cos(el)*r,target.y+Math.sin(el)*r,Math.cos(az)*Math.cos(el)*r);cam.lookAt(target);cam.updateMatrixWorld();
 if(['lever','valve','jets','detail','bucket'].includes(focus)){focusMaterial.uniforms.focus.value=r;renderer.setRenderTarget(rt);renderer.render(scene,cam);renderer.setRenderTarget(null);renderer.render(post,postCam);}else renderer.render(scene,cam);overlay(s,t,time);
}
