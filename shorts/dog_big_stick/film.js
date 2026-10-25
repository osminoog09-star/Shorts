import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
export const duration=22;
const W=1080,H=1920,scene=new T.Scene();scene.background=new T.Color('#e6e3d8');scene.fog=new T.Fog('#e6e3d8',15,35);
const renderer=new T.WebGLRenderer({canvas:document.getElementById('gl'),antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
const pmrem=new T.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;scene.environmentIntensity=.38;
const camera=new T.PerspectiveCamera(34,W/H,.1,70);
scene.add(new T.HemisphereLight('#f7f5df','#7a8c78',2));
function light(col,power,pos){const l=new T.DirectionalLight(col,power);l.position.set(...pos);scene.add(l);return l;}
const sun=light('#fff0d0',3.2,[-3,7,5]);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-7,right:7,top:7,bottom:-7,near:.1,far:22});sun.shadow.bias=-.0003;sun.shadow.normalBias=.025;sun.shadow.radius=4;light('#d6e8ff',1,[5,4,-2]);
const mat=(c,r=.65,m=0)=>new T.MeshStandardMaterial({color:c,roughness:r,metalness:m});
const gold=mat('#ba7a35'),lightgold=mat('#d9a55a'),cream=mat('#f4ddaf'),dark=mat('#352b24'),black=mat('#141713',.22),pink=mat('#d48f86'),red=mat('#637f7b',.38),metal=mat('#c8a26a',.32,.7);
function mesh(g,m,parent=scene,pos=[0,0,0]){const x=new T.Mesh(g,m);x.position.set(...pos);x.castShadow=true;x.receiveShadow=true;parent.add(x);return x;}
function ball(parent,m,pos,scale){const x=mesh(new T.SphereGeometry(1,32,24),m,parent,pos);x.scale.set(...scale);return x;}
function box(parent,m,pos,size,r=.08){return mesh(new RoundedBoxGeometry(...size,3,r),m,parent,pos);}
function line(parent,points,m,r=.02){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),24,r,8,false),m,parent);}
function cylinder(parent,m,a,b,r1,r2=r1){const A=new T.Vector3(...a),B=new T.Vector3(...b),d=B.clone().sub(A);const x=mesh(new T.CylinderGeometry(r2,r1,d.length(),14),m,parent,A.clone().add(B).multiplyScalar(.5).toArray());x.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return x;}
// Original small-scale wood grain. No borrowed imagery.
function wood(c1,c2){const c=document.createElement('canvas');c.width=256;c.height=512;const q=c.getContext('2d');q.fillStyle=c1;q.fillRect(0,0,256,512);let seed=21;const rand=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);for(let i=0;i<190;i++){q.strokeStyle=c2;q.globalAlpha=.08+rand()*.2;q.lineWidth=.4+rand()*2;q.beginPath();let x=rand()*256;for(let y=0;y<=512;y+=8){q.lineTo(x+Math.sin(y*.02+i)*4,y);}q.stroke();}const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;return new T.MeshStandardMaterial({map:tx,roughness:.78,bumpMap:tx,bumpScale:.025});}
const oak=wood('#926040','#543a29'),bark=wood('#725039','#382e24'),plaster=mat('#e7d5be'),grass=mat('#7e9d85'),leaf=mat('#527c61');
box(scene,mat('#d9d4bd'),[0,-.16,0],[24,.3,24],.1);
// Yard behind the doorway: paving stones, fence, terracotta, plants.
for(let j=0;j<7;j++)for(let i=-2;i<3;i++)box(scene,mat((i+j)%2?'#b9bbb0':'#c4c5b9'),[i*.74,.013,-j*.72+2],[.70,.06,.67],.07);
for(const side of [-1,1]){
 const fence=new T.Group();scene.add(fence);for(let i=0;i<7;i++)box(fence,oak,[side*(1.65+i*.43),.75,-2.5],[.32,1.5,.12],.04);
 for(let y of [.4,1.05])box(fence,oak,[side*3.0,y,-2.6],[3.4,.16,.12],.02);
 const pot=mesh(new T.CylinderGeometry(.32,.23,.48,32),mat('#bc8f72'),scene,[side*2.15,.24,.7]);
 for(let i=0;i<9;i++){let a=i*2.399;const p=[side*2.15+Math.sin(a)*.30,.8+(i%3)*.14,.7+Math.cos(a)*.25];cylinder(scene,leaf,[side*2.15,.45,.7],p,.018);const l=ball(scene,leaf,p,[.08,.28,.06]);l.rotation.z=Math.sin(a)*.5;}
}
for(let i=0;i<8;i++){const x=(i%2?1:-1)*(3+i*.35),z=-5-(i%3);cylinder(scene,oak,[x,0,z],[x,2.5,z],.11,.08);for(let j=0;j<3;j++)ball(scene,mat(j%2?'#9db294':'#71977a'),[x+(j-1)*.3,2.4+j*.33,z],[.75,.75,.65]);}
const gate=new T.Group();scene.add(gate);const posts=[];
for(const sign of [-1,1]){const p=new T.Group();p.position.x=sign*1.23;gate.add(p);box(p,oak,[0,1.45,.82],[.24,2.9,.3],.035);box(p,plaster,[sign*.6,1.4,.8],[1.05,2.8,.24],.04);box(p,mat('#f1e6d4'),[0,2.95,.82],[.36,.14,.4],.03);for(let y of [.3,1.45,2.7])ball(p,metal,[0,y,1.0],[.026,.026,.012]);posts.push(p);}
const lintel=box(gate,oak,[0,2.82,.82],[2.7,.25,.34],.04);
// Original articulated puppy. Expressive eyes, pads, collar, whiskers, layered fur tufts.
const dog=new T.Group();scene.add(dog);
ball(dog,gold,[0,.76,-.15],[.48,.50,.79]);ball(dog,lightgold,[0,.92,.36],[.43,.48,.45]);ball(dog,cream,[0,.74,.66],[.26,.35,.10]);
const legs=[];
for(let z of [-.64,.44])for(let sign of [-1,1]){const g=new T.Group();g.position.set(sign*.32,.65,z);dog.add(g);ball(g,gold,[0,-.16,0],[.155,.35,.16]);ball(g,lightgold,[0,-.48,.06],[.20,.13,.25]);for(let k=-1;k<=1;k++)line(g,[[k*.085,-.42,.22],[k*.085,-.45,.28]],gold,.008);legs.push(g);}
const tail=new T.Group();tail.position.set(0,.94,-.88);dog.add(tail);line(tail,[[0,0,0],[0,.2,-.25],[0,.48,-.43],[0,.65,-.35]],gold,.115);ball(tail,lightgold,[0,.62,-.36],[.12,.18,.12]);
const neck=mesh(new T.TorusGeometry(.34,.065,12,48),red,dog,[0,1.23,.34]);neck.rotation.x=Math.PI/2;const tag=mesh(new T.CylinderGeometry(.085,.085,.025,28),metal,dog,[0,1.11,.72]);tag.rotation.x=Math.PI/2;
const head=new T.Group();head.position.set(0,1.37,.52);dog.add(head);ball(head,lightgold,[0,.13,0],[.52,.47,.43]);
const ears=[];for(const sign of [-1,1]){const ear=new T.Group();head.add(ear);ear.position.set(sign*.44,.24,-.04);ball(ear,gold,[sign*.02,-.20,0],[.19,.43,.17]);ball(ear,mat('#a86e46'),[sign*.02,-.21,.12],[.11,.28,.055]);ears.push(ear);}
for(const sign of [-1,1]){ball(head,cream,[sign*.22,.14,.33],[.23,.25,.15]);ball(head,mat('#fbf8ee',.26),[sign*.21,.17,.415],[.12,.15,.062]);ball(head,mat('#5a3a24',.3),[sign*.21,.17,.465],[.079,.1,.027]);ball(head,black,[sign*.21,.17,.486],[.047,.07,.018]);ball(head,mat('#ffffff',.05),[sign*.19,.205,.501],[.026,.032,.012]);const brow=ball(head,gold,[sign*.23,.38,.38],[.15,.055,.07]);brow.rotation.z=sign*-.12;}
ball(head,cream,[-.15,-.095,.48],[.23,.18,.20]);ball(head,cream,[.15,-.095,.48],[.23,.18,.20]);ball(head,black,[0,-.025,.66],[.14,.10,.08]);ball(head,mat('#504d43',.12),[-.04,.015,.72],[.042,.018,.008]);line(head,[[-.21,-.19,.57],[0,-.23,.6],[.21,-.19,.57]],dark,.016);
for(let sign of [-1,1])for(let i=0;i<3;i++)ball(head,dark,[sign*(.17+(i%2)*.06),-.10-(i/2)*.04,.655],[.009,.009,.006]);
// Fur silhouette: individual overlapping tapered tufts, not a smooth clay blob.
const furCanvas=document.createElement('canvas');furCanvas.width=512;furCanvas.height=512;const fq=furCanvas.getContext('2d');fq.fillStyle='#c79450';fq.fillRect(0,0,512,512);let fs=37;const fr=()=>((fs=(fs*1664525+1013904223)>>>0)/4294967296);for(let i=0;i<18000;i++){const x=fr()*512,y=fr()*512;fq.strokeStyle=i%2?'#e1b777':'#9f6d37';fq.globalAlpha=.08+fr()*.15;fq.lineWidth=.5+fr();fq.beginPath();fq.moveTo(x,y);fq.lineTo(x+(fr()-.5)*5,y+3+fr()*8);fq.stroke();}const furTex=new T.CanvasTexture(furCanvas);furTex.colorSpace=T.SRGBColorSpace;for(const m of [gold,lightgold]){m.bumpMap=furTex;m.bumpScale=.025;m.roughnessMap=furTex;m.roughness=.85;}
const stick=new T.Group();head.add(stick);stick.position.set(0,-.20,.72);cylinder(stick,bark,[-2.05,0,0],[2.05,.07,.03],.075,.065);
for(let i=0;i<7;i++){const x=-1.8+i*.57;ball(stick,bark,[x,.025,.015],[.11,.10,.10]);if(i%2===0)cylinder(stick,bark,[x,.02,0],[x+.16,.27,(i%3-1)*.17],.035,.012);}
const bot=new T.Group();scene.add(bot);box(bot,mat('#afc4bf',.34),[0,.80,0],[.6,.8,.48],.16);box(bot,mat('#223c43',.25),[0,1.24,.11],[.59,.31,.40],.10);for(let x of [-.15,.15])ball(bot,mat('#98f0d1',.2),[x,1.26,.315],[.07,.065,.015]);for(let x of [-.26,.26]){const w=mesh(new T.CylinderGeometry(.17,.17,.13,24),dark,bot,[x,.19,0]);w.rotation.z=Math.PI/2;}cylinder(bot,metal,[-.2,.83,.1],[-.52,.62,.2],.035);const tool=box(bot,mat('#f1b956',.35,.5),[-.52,.65,.28],[.13,.2,.22],.03);
const rubble=[];for(let i=0;i<9;i++){const r=box(scene,plaster,[0,-3,0],[.16+(i%3)*.06,.12,.19],.02);rubble.push(r);}
const ctx=document.getElementById('overlay').getContext('2d');
const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));const ease=v=>{v=clamp(v);return v*v*(3-2*v);};
function label(txt,y,size=55,color='#263d3c'){ctx.font=`900 ${size}px DejaVu Sans`;ctx.textAlign='center';ctx.fillStyle=color;ctx.fillText(txt,W/2,y);}
export function renderAt(t){
 dog.position.set(0,Math.sin(t*11)*.025*(t<2.8?1:0),-2.7+2.28*ease(t/2.8));
 const bonk=Math.sin(clamp((t-2.8)/.5)*Math.PI);if(t>=2.8&&t<3.3)dog.position.z-=.25*bonk;
 let walking=t<2.8||(t>13&&t<17);for(let i=0;i<legs.length;i++)legs[i].rotation.x=walking?Math.sin(t*10+i%2*Math.PI+(i>1?Math.PI:0))*.38:0;
 tail.rotation.z=Math.sin(t*(t<3?7:3))*.42;head.rotation.z=t>3&&t<6?-.18*Math.sin((t-3)*1.3):Math.sin(t*2)*.035;head.rotation.y=t>5&&t<9?.30*ease((t-5)/.7):0;
 for(let i=0;i<2;i++)ears[i].rotation.z=Math.sin(t*6+i)*.06+(i?1:-1)*bonk*.22;
 bot.position.set(4.3-2.65*ease((t-5)/2),Math.abs(Math.sin(t*9))*.018,1.3);bot.rotation.y=.15;tool.rotation.z=Math.sin(t*70)*(t>9&&t<12.4?.15:0);
 const expansion=ease((t-10)/2.4);posts[0].position.x=-1.23-expansion*1.3;posts[1].position.x=1.23+expansion*1.3;lintel.scale.x=1+expansion*.95;
 for(let i=0;i<rubble.length;i++){const dt=clamp(t-10-i*.07,0,3);const r=rubble[i];r.visible=t>10+i*.07;r.position.set((i%2?1:-1)*(1.2+dt*.22+(i%3)*.12),Math.max(.08,2.8-dt*dt*2.7),.82+dt*.1);r.rotation.set(dt*i,dt*.4,dt*.7);}
 if(t>13){dog.position.z+=ease((t-13)/4)*3.2;dog.rotation.y=-.12*ease((t-16)/1);}
 if(t>17)dog.position.z=3.05;
 const shot=t<5?0:t<10?1:t<15?2:3;
 let cp=shot===0?[.8,2.7,10.4]:shot===1?[1.9,2.6,9.0]:shot===2?[2.8,3.0,11.4]:[2.2,2.8,11.2];
 camera.position.set(cp[0]+Math.sin(t*.25)*.2,cp[1],cp[2]);camera.lookAt(0,1.15,t>15?1.7:.1);renderer.render(scene,camera);
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#243c39';ctx.font='700 27px DejaVu Sans';ctx.textAlign='left';ctx.fillText('M1LASH  /  ПЁС И ТЕХНОЛОГИИ',65,105);
 if(t<2.8){label('ПАЛКА ИЛИ ДВЕРЬ?',255,64);label('Когда позвал ИИ на помощь',320,34,'#56716a');}
 else if(t<5){label('НЕ ПРОХОДИТ.',255,68);if(t>3.6)label('Ну и кто тут неправ?',325,40,'#56716a');}
 else if(t<9){label('ИИ: «Я ПОМОГУ».',255,62);}
 else if(t<13){label('РАСШИРЯЕМ ДВЕРЬ.',255,57);label('Палку трогать нельзя.',320,38,'#56716a');}
 else if(t<18){label('ПАЛКА ПРОШЛА.',255,67);label('ДОМ НЕ ВЫДЕРЖАЛ.',325,55,'#ad674b');}
 else {label('ПОДПИШИСЬ!',235,72);label('Спасибо за просмотр и лайк',300,37);label('Твой тоже тащит брёвна?',365,39);}
}
