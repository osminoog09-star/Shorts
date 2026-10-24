import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

// Original exhibit models. All maps are procedurally drawn; no borrowed images.
function texture(kind,size=256){
 const c=document.createElement('canvas');c.width=c.height=size;const q=c.getContext('2d');
 q.fillStyle=kind==='wood'?'#806044':kind==='stone'?'#c9bd9f':'#b6a080';q.fillRect(0,0,size,size);
 const rnd=i=>{const x=Math.sin(i*127.1+18.7)*43758.5453;return x-Math.floor(x);};
 if(kind==='wood'){
  for(let i=0;i<190;i++){const x=i/190*size;q.strokeStyle=`rgba(25,13,7,${.07+rnd(i)*.22})`;q.lineWidth=.5+rnd(i+6)*1.5;q.beginPath();for(let y=0;y<=size;y+=8){const xx=x+Math.sin(y*.026+i*.7)*3+Math.sin(y*.08+i)*.8;y?q.lineTo(xx,y):q.moveTo(xx,y);}q.stroke();}
  for(let i=0;i<4;i++){q.strokeStyle='rgba(35,19,11,.22)';q.beginPath();q.ellipse(rnd(i+20)*size,rnd(i+25)*size,3,16,0,0,Math.PI*2);q.stroke();}
 }else{
  for(let i=0;i<4200;i++){const v=rnd(i);q.fillStyle=`rgba(${v>.5?'255,247,226':'36,47,42'},${kind==='stone'?.04+v*.12:.025+v*.09})`;q.fillRect(rnd(i+1)*size,rnd(i+2)*size,kind==='stone'?1+v*4:1,1+v*3);}
  if(kind==='metal')for(let i=0;i<170;i++){q.strokeStyle='rgba(33,45,40,.18)';q.lineWidth=.5;q.beginPath();const x=rnd(i+90)*size,y=rnd(i+190)*size;q.moveTo(x,y);q.lineTo(x+4+rnd(i+39)*22,y+1);q.stroke();}
 }
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(kind==='wood'?2:3,kind==='wood'?1:3);return t;
}
const woodMap=texture('wood'),stoneMap=texture('stone'),metalMap=texture('metal');
const metal=new T.MeshStandardMaterial({color:0x9c723e,metalness:.84,roughness:.29,map:metalMap,bumpMap:metalMap,bumpScale:.012});
const bronze=new T.MeshStandardMaterial({color:0x927a4f,metalness:.78,roughness:.4,map:metalMap,bumpMap:metalMap,bumpScale:.018});
const copper=new T.MeshStandardMaterial({color:0xb65c3a,metalness:.9,roughness:.28,map:metalMap,bumpMap:metalMap,bumpScale:.012});
const iron=new T.MeshStandardMaterial({color:0x343d3d,metalness:.76,roughness:.4});
const wood=new T.MeshStandardMaterial({color:0xaf8058,roughness:.66,map:woodMap,bumpMap:woodMap,bumpScale:.038});
const stone=new T.MeshStandardMaterial({color:0xe3d4b8,roughness:.86,map:stoneMap,bumpMap:stoneMap,bumpScale:.045});
const ceramic=new T.MeshPhysicalMaterial({color:0xc69b7a,roughness:.38,clearcoat:.25});
const water=new T.MeshPhysicalMaterial({color:0x4098ac,metalness:.05,roughness:.10,clearcoat:1,transparent:true,opacity:.72,depthWrite:false});
const ink=new T.MeshStandardMaterial({color:0x243a3c,roughness:.75});
const paper=new T.MeshStandardMaterial({color:0xe5d3aa,roughness:.92});
const mats={metal,bronze,copper,iron,wood,stone,ceramic,water,ink,paper};
function mesh(geo,mat,p,shadow=true){const o=new T.Mesh(geo,typeof mat==='string'?mats[mat]:mat);p.add(o);o.castShadow=shadow;o.receiveShadow=true;return o;}
function box(p,x,y,z,w,h,d,mat='metal',bevel=.04){const o=mesh(new RoundedBoxGeometry(w,h,d,2,Math.min(bevel,w*.12,h*.12,d*.12)),mat,p);o.position.set(x,y,z);return o;}
function cyl(p,x,y,z,r,h,mat='metal',r2=r,n=40){const o=mesh(new T.CylinderGeometry(r,r2,h,n),mat,p);o.position.set(x,y,z);return o;}
function sphere(p,x,y,z,r,mat='metal'){const o=mesh(new T.SphereGeometry(r,40,28),mat,p);o.position.set(x,y,z);return o;}
function torus(p,x,y,z,r,t=.03,mat='metal',axis='z'){const o=mesh(new T.TorusGeometry(r,t,8,48),mat,p);o.position.set(x,y,z);if(axis==='y')o.rotation.x=Math.PI/2;if(axis==='x')o.rotation.y=Math.PI/2;return o;}
function tube(p,pts,r=.06,mat='metal'){const o=mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts.map(v=>new T.Vector3(...v))),32,r,8,false),mat,p);return o;}
function bolt(p,x,y,z,r=.055,axis='z'){
 const o=cyl(p,x,y,z,r,.055,'iron',r,6);if(axis==='z')o.rotation.x=Math.PI/2;if(axis==='x')o.rotation.z=Math.PI/2;
 const washer=torus(p,x,y,z+.004,r*1.28,.012,'bronze',axis);return o;
}
function band(p,y,r,mat='iron'){torus(p,0,y,0,r,.045,mat,'y');}
function dynamic(g){g.traverse(o=>{if(o.isMesh)o.castShadow=false;});return g;}
function plaque(p,text,x,y,z,w=1.7,h=.3){
 const c=document.createElement('canvas');c.width=768;c.height=128;const q=c.getContext('2d');q.fillStyle='#b59a66';q.fillRect(0,0,768,128);q.strokeStyle='#534b36';q.lineWidth=5;q.strokeRect(10,10,748,108);q.fillStyle='#343a30';q.textAlign='center';q.font='bold 49px DejaVu Sans';q.fillText(text,384,83);
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;const m=new T.MeshStandardMaterial({map:t,metalness:.55,roughness:.4});const o=mesh(new T.PlaneGeometry(w,h),m,p,false);o.position.set(x,y,z);return o;
}
function pedestal(p,w=7,d=4){
 box(p,0,-2.38,0,w,.28,d,'stone',.05);box(p,0,-2.18,0,w-.2,.12,d-.2,'wood',.025);
 for(const x of [-w*.43,w*.43])for(const z of [-d*.4,d*.4])bolt(p,x,-2.10,z,.06,'y');
 plaque(p,'M1LASH · RECONSTRUCTION',0,-2.34,d/2+.009,2.4,.14);
}
function gear(p,x,y,z,r=.45){
 const g=new T.Group();p.add(g);g.position.set(x,y,z);const disk=cyl(g,0,0,0,r,.075,'bronze');disk.rotation.x=Math.PI/2;
 torus(g,0,0,.05,r*.68,.035,'metal');torus(g,0,0,.05,.1,.04,'iron');
 for(let i=0;i<16;i++){const a=i*Math.PI/8;const b=box(g,Math.cos(a)*r,Math.sin(a)*r,.0,.1,.13,.1,'bronze',.015);b.rotation.z=a;}
 return g;
}
function props(p,side=1){
 // Calipers, a mallet, parchment and spare parts on the exhibit's rear corners.
 const g=new T.Group();p.add(g);g.position.set(side*2.5,-2.02,-1.1);g.scale.setScalar(.65);
 const roll=cyl(g,0,.13,0,.13,1.35,'paper');roll.rotation.z=Math.PI/2;torus(g,.55,.13,0,.13,.018,'wood','x');
 box(g,-.4,.07,.55,1.1,.05,.65,'paper',.01);
 for(let i=0;i<4;i++)box(g,-.4,.1,.4+i*.1,.75,.005,.008,'wood',.001);
 const hammer=new T.Group();g.add(hammer);hammer.position.set(.65,.06,.45);hammer.rotation.y=-.55;box(hammer,0,0,0,.08,.08,.9,'wood',.015);box(hammer,0,.09,.35,.45,.23,.19,'iron',.025);
 const a=box(g,-.7,.12,.8,.035,.04,.85,'metal',.01);a.rotation.y=.2;const b=box(g,-.5,.12,.8,.035,.04,.85,'metal',.01);b.rotation.y=-.2;
 gear(g,.55,.24,-.35,.28).rotation.x=-Math.PI/2;
}
function coinMachine(scene){
 const g=new T.Group();scene.add(g);pedestal(g);props(g);
 // Wood frame with stone back, bronze panel seams and functional openings.
 box(g,0,0,-.94,4.9,4.1,.18,'wood');
 for(let i=-2;i<=2;i++)box(g,i*.91,0,-.82,.018,4.05,.025,'iron',.005);
 for(const x of [-2.42,2.42]){box(g,x,0,-.67,.16,4.3,.2,'bronze');for(const y of [-1.7,-.8,.1,1,1.8])bolt(g,x,y,-.54);}
 const roof=new T.Group();g.add(roof);box(roof,0,2.12,-.1,5.1,.22,2.1,'wood');box(roof,0,2.27,-.1,5,.07,2,'bronze',.02);box(roof,-1.35,2.32,.02,.95,.07,.20,'iron',.01);
 for(let i=0;i<8;i++)bolt(roof,-2.1+i*.60,2.3,.75,.05,'y');dynamic(roof);
 // Cut-away bronze reservoir. A half shell and rims make the section explicit.
 const shellMat=copper.clone();shellMat.side=T.DoubleSide;
 const shell=mesh(new T.CylinderGeometry(1,1,2.7,48,1,true,Math.PI*.12,Math.PI*1.2),shellMat,g);shell.position.set(1.1,-.2,-.1);
 cyl(g,1.1,-1.62,-.1,1.02,.12,'bronze');cyl(g,1.1,1.18,-.1,1.02,.10,'bronze');
 for(const y of [-1.5,.7]){const o=torus(g,1.1,y,-.1,1.015,.035,'iron','y');}
 for(let i=0;i<10;i++){const a=i*Math.PI*2/10;bolt(g,1.1+Math.cos(a)*1.01,.68,-.1+Math.sin(a)*1.01,.045,'y');}
 const level=cyl(g,1.1,-.55,-.1,.88,1.72,'water');level.castShadow=false;
 for(const r of [.25,.50,.76]){const o=torus(level,0,.865,0,r,.009,new T.MeshBasicMaterial({color:0xa7e0df,transparent:true,opacity:.4}),'y');o.castShadow=false;}
 cyl(g,-.42,-.6,.02,.13,2.95,'iron');cyl(g,-.42,-1.95,.02,.34,.16,'bronze');
 const pivot=cyl(g,-.42,.55,.02,.22,.36,'bronze');pivot.rotation.x=Math.PI/2;bolt(g,-.42,.55,.25,.11);
 const lever=new T.Group();g.add(lever);lever.position.set(-.42,.55,.06);box(lever,.06,0,0,3.25,.13,.20,'metal',.02);cyl(lever,-1.25,.07,0,.42,.06,'bronze');torus(lever,-1.25,.10,0,.4,.025,'metal','y');dynamic(lever);
 const lid=cyl(g,1.07,-.2,.05,.21,.14,'bronze');const link=box(g,1.07,.15,.05,.065,.75,.065,'iron',.01);lid.castShadow=link.castShadow=false;
 tube(g,[[1.1,-1.55,0],[1.1,-1.55,1.1],[1.1,-1.8,1.48]],.115,'copper');torus(g,1.1,-1.55,.35,.14,.035,'bronze');torus(g,1.1,-1.55,.8,.14,.035,'bronze');
 cyl(g,1.1,-1.97,1.5,.43,.27,'ceramic',.33);torus(g,1.1,-1.82,1.5,.42,.035,'ceramic','y');const cup=cyl(g,1.1,-1.84,1.5,.33,.025,'water');cup.castShadow=false;
 const coin=cyl(g,-1.65,3.1,0,.24,.075,'metal');coin.castShadow=false;torus(coin,0,.044,0,.205,.013,'bronze','y');
 for(let i=0;i<20;i++){const a=i*Math.PI/10;box(coin,Math.cos(a)*.225,0,Math.sin(a)*.225,.016,.084,.016,'bronze',.002).castShadow=false;}
 dynamic(coin);
 const weightArrow=new T.ArrowHelper(new T.Vector3(0,-1,0),new T.Vector3(-1.65,1.55,.25),.65,0x4e9298,.15,.08);g.add(weightArrow);
 for(let i=0;i<6;i++)cyl(g,-1.85+i*.14,-2.01,.18+i*.07,.18,.045,'bronze');
 const stream=cyl(g,1.1,-1.7,1.48,.037,.37,'water');stream.castShadow=false;
 const drips=[];for(let i=0;i<7;i++){const o=sphere(g,1.1,-1.65,1.48,.03,'water');o.castShadow=false;drips.push(o);}
 plaque(g,'PNEUMATICA · XXI',-.6,-1.56,-.80,1.7,.25);
 return {g,update(t,focus){const u=(t%10)/10;const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};const op=ease((u-.18)/.055)*(1-ease((u-.66)/.055));const on=op>.25;
 lever.rotation.z=op*.16;coin.visible=u<.8;coin.rotation.x=u<.18?Math.PI*.5*(1-u/.18):0;
 const cy=.55-1.25*Math.sin(op*.16)+.17*Math.cos(op*.16);
 coin.position.set(u<.66?-1.65:-1.65+(u-.66)*.7,u<.18?3.1-u*(2.38/.18):u<.66?cy:cy-(u-.66)*14,0);
 lid.position.y=-.2+op*.32;link.position.y=.15+op*.23;level.scale.y=1-(on?(u-.18)*.12:0);stream.visible=on;cup.visible=u>.24;roof.position.y=focus==='explode'?Math.min(1.1,t*.25):0;weightArrow.visible=focus==='lever';drips.forEach((o,i)=>{o.visible=on;o.position.y=-1.60-((t*1.9+i/7)%1)*.25;});}};
}
function chain(p,a,b,count=16){
 const links=[];for(let i=0;i<count;i++){const o=torus(p,0,0,0,.055,.013,'iron');o.castShadow=false;links.push(o);}
 return (aa=a,bb=b)=>{const u=new T.Vector3(...aa),v=new T.Vector3(...bb);links.forEach((o,i)=>{o.position.copy(u).lerp(v,i/(count-1));o.rotation.y=i%2?Math.PI/2:0;});};
}
function temple(scene){
 const g=new T.Group();scene.add(g);pedestal(g,8.4,4.5);
 // Architecture reads as a small stone temple, rather than a modern cupboard.
 for(let i=0;i<6;i++)box(g,-2.5+i, -.32,-.1,.97,.32,2.8,'stone',.025);
 for(const x of [-2.4,2.4]){
  cyl(g,x,-.05,-.65,.37,.22,'stone');cyl(g,x,1.80,-.65,.27,3.5,'stone',.32);
  for(let j=0;j<12;j++){const a=j*Math.PI/6;const o=cyl(g,x+Math.cos(a)*.268,1.8,-.65+Math.sin(a)*.268,.035,3.25,'stone');o.scale.z=.7;}
  cyl(g,x,3.6,-.65,.41,.20,'stone');box(g,x,3.78,-.65,.85,.18,.85,'stone');
 }
 box(g,0,4,-.65,5.8,.32,1.1,'stone');
 for(let i=0;i<14;i++)box(g,-2.6+i*.4,4.18,-.07,.20,.16,.22,'stone',.015);
 const tri=new T.Shape();tri.moveTo(-2.8,0);tri.lineTo(2.8,0);tri.lineTo(0,.85);tri.closePath();const ped=mesh(new T.ExtrudeGeometry(tri,{depth:.5,bevelEnabled:true,bevelSize:.035,bevelThickness:.035,bevelSegments:2,steps:1}),'stone',g);ped.position.set(0,4.25,-.9);
 const doors=[];for(const sign of [-1,1]){
  const d=new T.Group();g.add(d);d.position.set(sign*1.6,1.6,-.6);const dx=-sign*.8;box(d,dx,0,0,1.55,3.3,.16,'wood',.035);
  for(const yy of [-.95,.8]){box(d,dx,yy,.13,1.48,.10,.07,'iron',.01);for(const xx of [-.5,.0,.5])bolt(d,dx+xx,yy,.19,.05);}
  box(d,dx,0,.12,1.20,2.9,.08,'wood',.025);for(const yy of [-.7,.7])box(d,dx,yy,.18,.98,1.1,.06,'wood',.02);
  torus(d,-sign*1.28,.1,.24,.12,.025,'bronze');bolt(d,-sign*1.28,.25,.22,.065);dynamic(d);doors.push(d);
 }
 const furnace=cyl(g,-3.15,.12,.8,.44,.7,'ceramic',.37);torus(g,-3.15,.49,.8,.43,.055,'bronze','y');
 const flames=[];for(let i=0;i<5;i++){const m=new T.MeshStandardMaterial({color:i%2?0xf7b85d:0xe47a31,emissive:0xd13a0c,emissiveIntensity:.5,transparent:true,opacity:.88,roughness:.7});const o=mesh(new T.ConeGeometry(.09,.55+i*.045,10),m,g,false);o.position.set(-3.35+i*.10,.8,.8);flames.push(o);}
 // A bronze half-shell and blue section make pressure transfer legible.
 const rmat=bronze.clone();rmat.side=T.DoubleSide;const globe=mesh(new T.SphereGeometry(.78,40,24,Math.PI,Math.PI),rmat,g);globe.position.set(-2.1,-1.1,.25);sphere(g,-2.1,-1.24,.25,.62,'water');torus(g,-2.1,-1.1,.25,.79,.035,'iron');
 tube(g,[[-3.15,.12,.8],[-3.15,-.85,.8],[-2.1,-.85,.25]],.065,'copper');tube(g,[[-2.1,-1.2,.25],[-1.5,.1,.4],[.6,.1,.4],[.6,-.6,.4]],.06,'copper');
 const bucket=new T.Group();g.add(bucket);cyl(bucket,0,0,0,.4,.7,'copper',.30);torus(bucket,0,.35,0,.4,.04,'bronze','y');const bv=cyl(bucket,0,.25,0,.31,.03,'water');dynamic(bucket);
 const pulley=cyl(g,.6,.8,.5,.28,.12,'bronze');pulley.rotation.x=Math.PI/2;torus(g,.6,.8,.57,.22,.03,'iron');bolt(g,.6,.8,.6,.07);
 const drop=chain(g,[.6,.8,.5],[.6,-.9,.5],19);const left=chain(g,[.6,.8,.5],[-1.6,.8,-.6],24);const right=chain(g,[.6,.8,.5],[1.6,.8,-.6],20);
 const weight=box(g,2.7,-1.1,.1,.5,.65,.5,'iron',.025);weight.castShadow=false;const wc=chain(g,[2.7,.9,.1],[2.7,-.7,.1],18);
 tube(g,[[2.7,.9,.1],[1.6,.9,-.6]],.035,'iron');
 const air=[];const airM=new T.MeshBasicMaterial({color:0xe46b3f,transparent:true,opacity:.72});for(let i=0;i<8;i++)air.push(mesh(new T.SphereGeometry(.045,10,8),airM,g,false));
 plaque(g,'PNEUMATICA · XXXVII',0,3.99,-.07,2.25,.20);
 props(g,-1);
 return {g,update(t){const u=(t%16)/16,p=u<.6?Math.min(1,u/.5):Math.max(0,(1-u)/.4);doors[0].rotation.y=-p*1.07;doors[1].rotation.y=p*1.07;bucket.position.set(.6,-.65-p*.85,.5);bv.scale.y=.25+p*1.8;weight.position.y=-1.3+p*.7;drop([.6,.8,.5],[.6,bucket.position.y+.35,.5]);left();right();wc([2.7,.9,.1],[2.7,weight.position.y+.3,.1]);flames.forEach((f,i)=>{f.visible=u<.65;f.scale.y=.8+.2*Math.sin(t*5+i);});air.forEach((f,i)=>{f.position.set(-2.1+.35*Math.sin(t+i),-1.0+.3*Math.cos(t*.8+i),.4);});}};
}
function steamTexture(){const c=document.createElement('canvas');c.width=c.height=64;const q=c.getContext('2d');const r=q.createRadialGradient(32,32,2,32,32,31);r.addColorStop(0,'rgba(255,255,247,.55)');r.addColorStop(1,'rgba(255,255,247,0)');q.fillStyle=r;q.fillRect(0,0,64,64);return new T.CanvasTexture(c);}
function aeolipile(scene){
 const g=new T.Group();scene.add(g);pedestal(g,6,4);props(g,-1);
 const boiler=cyl(g,0,-1.56,0,1.25,.92,'copper');cyl(g,0,-1.08,0,1.32,.12,'bronze');
 for(const y of [-1.9,-1.25])band(g,y,1.255);
 for(let i=0;i<18;i++){const a=i*Math.PI/9;bolt(g,Math.cos(a)*1.26,-1.3,Math.sin(a)*1.26,.045,'y');}
 for(const x of [-.85,.85]){box(g,x,-2.02,.0,.28,.20,1.3,'iron');bolt(g,x,-1.9,.45,.07,'y');}
 for(const x of [-1,1]){
  tube(g,[[x,-1.08,0],[x*1.3,-.4,0],[x*1.25,1.4,0],[x*.86,1.4,0]],.095,'bronze');
  const sleeve=cyl(g,x*.94,1.4,0,.16,.35,'iron');sleeve.rotation.z=Math.PI/2;
  bolt(g,x*1.18,-.8,.1,.055);
 }
 const rotor=new T.Group();g.add(rotor);rotor.position.y=1.4;sphere(rotor,0,0,0,.89,'copper');torus(rotor,0,0,0,.9,.018,'bronze','x');
 for(let i=0;i<12;i++){const a=i*Math.PI/6;const o=sphere(rotor,0,Math.cos(a)*.9,Math.sin(a)*.9,.033,'bronze');o.castShadow=false;}
 tube(rotor,[[0,.70,.34],[0,1.0,.34],[0,1.0,.88]],.087,'bronze');tube(rotor,[[0,-.70,-.34],[0,-1,-.34],[0,-1,-.88]],.087,'bronze');dynamic(rotor);
 const smoke=[];const tex=steamTexture();for(const sign of [-1,1])for(let i=0;i<12;i++){const o=new T.Sprite(new T.SpriteMaterial({map:tex,transparent:true,opacity:.25,depthWrite:false,color:0xf5f4e8}));rotor.add(o);smoke.push({o,i,sign});}
 const hot=new T.MeshStandardMaterial({color:0xe58b3e,emissive:0xbb4209,emissiveIntensity:.45,roughness:.7});
 const fire=[];for(let i=0;i<5;i++){const o=mesh(new T.ConeGeometry(.10,.38,9),hot,g,false);o.position.set((i-2)*.16,-2.05,.85);fire.push(o);}
 const load=new T.Group();g.add(load);load.position.set(3.1,-1.3,0);
 for(const x of [-.7,.7]){box(load,x,-.1,0,.16,1.6,.6,'wood');bolt(load,x,.55,.32,.07);}
 const axle=cyl(load,0,.5,0,.08,1.9,'iron');axle.rotation.z=Math.PI/2;const drum=cyl(load,0,.5,0,.3,.8,'wood');drum.rotation.z=Math.PI/2;
 for(let i=0;i<6;i++)torus(load,-.3+i*.12,.5,0,.31,.025,'bronze','x');
 tube(load,[[.25,.5,.3],[.25,-.3,.3],[.25,-.7,.3]],.025,'wood');box(load,.25,-.9,.3,.45,.45,.45,'iron');plaque(load,'НАГРУЗКА · СХЕМА',0,-1.04,.62,1.8,.20);
 const arrows=[];for(const sign of [-1,1]){const o=new T.ArrowHelper(new T.Vector3(0,0,sign),new T.Vector3(0,sign,sign*.9),.72,0x4f99a6,.16,.08);rotor.add(o);arrows.push(o);}
 plaque(g,'PNEUMATICA · L',0,-1.59,1.24,1.65,.23);
 return {g,update(t,focus){load.visible=focus==='detail';arrows.forEach(o=>o.visible=focus==='jets');rotor.rotation.x=t*1.0;smoke.forEach(({o,i,sign})=>{const u=(t*.7+i/12)%1;o.position.set(.07*Math.sin(i+t),sign*(1+u*.13),sign*(.88+u*1.75));o.scale.setScalar(.13+u*.48);o.material.opacity=.32*(1-u);});fire.forEach((o,i)=>o.scale.y=.8+.2*Math.sin(t*5+i));}};
}

function sourceBook(scene){
 const g=new T.Group();scene.add(g);pedestal(g,7,4.6);
 box(g,0,-1.86,0,5.7,.28,3.7,'wood',.06);box(g,0,-1.68,0,5.4,.1,3.5,'paper',.025);
 const spine=cyl(g,0,-1.61,0,.13,3.4,'bronze');spine.rotation.x=Math.PI/2;
 for(const side of [-1,1]){
  const leaf=new T.Group();g.add(leaf);leaf.position.set(side*1.30,-1.59,0);leaf.rotation.z=-side*.055;
  for(let i=0;i<8;i++)box(leaf,0,i*.012,0,2.5,.013,3.32,'paper',.006);
  const c=document.createElement('canvas');c.width=768;c.height=1024;const q=c.getContext('2d');q.fillStyle='#e8d8b4';q.fillRect(0,0,768,1024);q.strokeStyle='#584d39';q.lineWidth=3;q.strokeRect(40,40,688,944);q.fillStyle='#453f31';q.textAlign='center';q.font='bold 52px DejaVu Sans';q.fillText('PNEUMATICA',384,130);q.font='29px DejaVu Sans';q.fillText(side<0?'XXI · COIN AND LEVER':'XXXVII · HEAT AND DOORS',384,195);
  q.lineWidth=7;q.beginPath();
  if(side<0){q.strokeRect(410,350,170,310);q.moveTo(170,430);q.lineTo(550,370);q.moveTo(340,395);q.lineTo(340,720);q.moveTo(550,370);q.lineTo(550,600);q.moveTo(520,650);q.lineTo(620,650);q.lineTo(620,720);q.moveTo(210,420);q.arc(200,320,42,0,Math.PI*2);}
  else {q.strokeRect(340,300,180,270);q.moveTo(170,450);q.lineTo(170,650);q.lineTo(340,650);q.lineTo(610,650);q.lineTo(610,720);q.moveTo(500,470);q.lineTo(610,550);q.lineTo(610,650);q.moveTo(250,650);q.arc(210,650,90,0,Math.PI*2);}
  q.stroke();q.font='22px DejaVu Sans';q.fillText('B. WOODCROFT · LONDON · 1851',384,870);q.font='20px DejaVu Sans';q.fillText('EDUCATIONAL DIAGRAM · NOT A FACSIMILE',384,925);
  const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;const page=mesh(new T.PlaneGeometry(2.5,3.3),new T.MeshStandardMaterial({map:tex,roughness:.85}),leaf,false);page.rotation.x=-Math.PI/2;page.position.y=.105;
 }
 const inkwell=cyl(g,2.8,-1.98,-1,.22,.28,'iron');const pen=box(g,2.65,-1.90,.5,.045,.045,1.2,'wood',.01);pen.rotation.y=.35;
 plaque(g,'ГЕРОН · ТЕКСТ И РЕКОНСТРУКЦИЯ',0,-1.82,1.86,3.8,.2);
 return {g,update(){g.rotation.y=0;}};
}

export function createExhibit(scene){
 const floor=mesh(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:0xe6dfd1,roughness:.93}),scene,false);floor.rotation.x=-Math.PI/2;floor.position.y=-2.55;
 const models={coin:coinMachine(scene),door:temple(scene),steam:aeolipile(scene),archive:sourceBook(scene)};
 return {models};
}
