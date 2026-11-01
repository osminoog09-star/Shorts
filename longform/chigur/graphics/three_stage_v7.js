// M1lash Chigur V7: purpose-built 3D prop storyboard, no PIL, no movie media.
const W=960,H=540,R=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,canvas:document.getElementById("scene")});
R.setSize(W,H,false);R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;
R.outputEncoding=THREE.sRGBEncoding;R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=.83;
const S=new THREE.Scene();S.background=new THREE.Color(0x060b12);
const C=new THREE.PerspectiveCamera(39,W/H,.1,70);
S.add(new THREE.HemisphereLight(0xc4d4f1,0x29211b,.42));
const K=new THREE.SpotLight(0xffd0a0,2.4,26,.7,.62,1);K.position.set(-3,6,5);K.castShadow=true;K.shadow.mapSize.set(1024,1024);S.add(K,K.target);
const B=new THREE.PointLight(0x5d9dd1,1.8,20);B.position.set(4,3,-2);S.add(B);
const M=(c,r=.5,m=.1)=>new THREE.MeshPhysicalMaterial({color:c,roughness:r,metalness:m,clearcoat:m>.5?.5:.1});
const gold=M(0xd1a669,.27,.86),brass=M(0x8e6d41,.36,.78),steel=M(0x555f66,.38,.72),
wood=M(0x33231b,.73,.04),wall=M(0x384149,.88),ink=M(0x141920,.66,.24),paper=M(0xc9c0a3,.92),
glass=M(0x19463c,.23,.27),rubber=M(0x0e1116,.9);
function add(g,geo,m,x=0,y=0,z=0){const o=new THREE.Mesh(geo,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;g.add(o);return o}
function box(g,x,y,z,w,h,d,m){return add(g,new THREE.BoxGeometry(w,h,d),m,x,y,z)}
function cy(g,x,y,z,r,h,m){return add(g,new THREE.CylinderGeometry(r,r,h,48),m,x,y,z)}
function ball(g,x,y,z,r,m){return add(g,new THREE.SphereGeometry(r,28,16),m,x,y,z)}
function ring(g,x,y,z,r,t,m){return add(g,new THREE.TorusGeometry(r,t,12,52),m,x,y,z)}
function grain(){const canvas=document.createElement("canvas");canvas.width=256;canvas.height=256;const x=canvas.getContext("2d");x.fillStyle="#473123";x.fillRect(0,0,256,256);for(let i=0;i<350;i++){x.strokeStyle=i%5?"#3a281f":"#694732";x.globalAlpha=.06;x.beginPath();let yy=(i*67)%256;x.moveTo(0,yy);x.bezierCurveTo(65,yy+2,182,yy-2,256,yy+1);x.stroke()}return new THREE.CanvasTexture(canvas)}
const timber=M(0xb3a192,.74);timber.map=grain();timber.map.wrapS=timber.map.wrapT=THREE.RepeatWrapping;
function table(g){box(g,0,-1.3,0,11,.26,8,timber);box(g,0,-1.48,0,11,.09,8,ink)}
function coin(g,r=.65){const q=new THREE.Group();g.add(q);cy(q,0,0,0,r,.095,gold);
 for(let side of [-1,1]){const r1=ring(q,0,side*.055,0,r*.85,.02,brass);r1.rotation.x=Math.PI/2;
 const r2=ring(q,0,side*.061,0,r*.60,.011,gold);r2.rotation.x=Math.PI/2}
 for(let i=0;i<60;i++){const a=i*Math.PI/30;const k=box(q,Math.cos(a)*r,0,Math.sin(a)*r,.02,.095,.01,brass);k.rotation.y=-a}
 const b=ball(q,0,.061,0,r*.22,gold);b.scale.set(.8,.12,1.05);return q}
function knob(g,x,y,z,r=.12){const k=cy(g,x,y,z,r,.08,ink);k.rotation.x=Math.PI/2;ring(g,x,y,z+.05,r*.65,.012,gold)}
const G=[],A=[];const stage=()=>{const g=new THREE.Group();G.push(g);S.add(g);return g};
// 1 Coin decision: physical small engraved coin on ledger, no disembodied person.
{const g=stage();table(g);const q=coin(g,.7);q.position.set(-.6,-1.10,.7);q.rotation.set(Math.PI/2-.3,.2,.13);
const book=box(g,1.2,-1.12,-.65,2.0,.12,2.6,M(0x3b2219,.75));book.rotation.y=-.12;
const leaf=box(g,1.2,-1.049,-.65,1.8,.016,2.35,paper);leaf.rotation.y=-.12;
for(let j=0;j<10;j++)box(g,1,-1.038,-1.6+j*.19,1.05,.002,.014,brass);
const mug=cy(g,-2.7,-.99,-1.0,.4,.55,steel);ring(g,-2.7,-.70,-1.0,.42,.04,gold).rotation.x=Math.PI/2;
for(let i=0;i<4;i++){let c=coin(g,.17);c.position.set(-1.85+i*.22,-1.12,1.8)}
A.push(t=>{q.rotation.z=.13+.1*Math.sin(t*1.4)});}
 // 2 Motel door: large architectural perspective, opening door and amber sidelight.
{const g=stage();box(g,0,-1.62,0,15,.10,17,wall);box(g,0,.5,-6.1,15,7,.3,wall);
for(let i=-2;i<=2;i++){let x=i*2.45;box(g,x,-.10,-5.88,1.75,3.1,.24,ink);box(g,x,-.1,-5.68,1.48,2.9,.08,timber);box(g,x,1.10,-5.61,.48,.21,.05,gold);
ball(g,x+.50,-.20,-5.59,.08,gold)}
for(let x of [-4.8,4.8])box(g,x,.4,-2.8,.17,4.0,6,wall);
const lamp=box(g,-3.0,1.0,-5.35,.55,.58,.22,gold);
const light=new THREE.PointLight(0xffad65,2.5,8);light.position.set(-3.0,1.1,-4.7);g.add(light);
A.push(t=>{light.intensity=2.5+.2*Math.sin(t)})}
 // 3 Analogue tracking detector with physical knobs and a moving green oscilloscope.
{const g=stage();table(g);const d=new THREE.Group();g.add(d);d.position.set(0,-.81,.15);d.rotation.y=-.13;
box(d,0,0,0,4.4,1.35,2.35,steel);box(d,0,.72,0,4.30,.12,2.27,ink);
box(d,-.72,.29,1.21,2.35,.82,.09,ink);box(d,-.72,.29,1.28,2.13,.65,.018,M(0x16392d,.24));
const wave=new THREE.MeshBasicMaterial({color:0x65e5aa});
const needle=box(d,-.79,.29,1.306,1.85,.012,.012,wave);
for(let i=0;i<6;i++)knob(d,1.15+(i%2)*.40,.48-Math.floor(i/2)*.3,1.27,.11);
for(let i=0;i<8;i++)box(d,1.0+i*.16,-.46,1.26,.08,.11,.04,ink);
for(let x of [-1.95,1.95])for(let y of [-.54,.53]){let k=cy(d,x,y,1.24,.052,.015,gold);k.rotation.x=Math.PI/2}
const aerial=cy(d,1.7,1.67,-.65,.024,2.15,gold);ball(d,1.7,2.78,-.65,.06,gold);
A.push(t=>{needle.rotation.z=.3*Math.sin(t*3)})}
 // 4 Refusal: a coin left behind, untouched, on a counter; no stick-figure metaphor.
{const g=stage();table(g);const q=coin(g,.52);q.position.set(-.5,-1.10,.3);q.rotation.x=Math.PI/2;
const card=box(g,1.05,-1.15,.85,1.9,.025,2.1,paper);card.rotation.y=.2;
for(let j=0;j<7;j++)box(g,.90,-1.129,.04+j*.22,1.18,.002,.011,brass);
const steelCup=cy(g,-2.25,-.89,1.35,.28,.57,steel);ring(g,-2.25,-.58,1.35,.29,.03,gold).rotation.x=Math.PI/2;
box(g,0,1.3,-4.3,12,4,.2,wall);
const cold=new THREE.PointLight(0x83bed3,1.2,12);cold.position.set(3,2,-1);g.add(cold);A.push(t=>{q.rotation.z=.02*Math.sin(t*.3)})}
 // 5 Briefcase: real open lid, cash edges, metal hardware, directed side light.
{const g=stage();table(g);const d=new THREE.Group();d.position.set(0,-.86,0);g.add(d);const lid=new THREE.Group();lid.position.set(0,.26,-1.32);d.add(lid);
box(d,0,0,0,4.1,.62,2.7,ink);box(lid,0,.08,1.31,4.08,.16,2.65,ink);
for(let i=0;i<6;i++){let x=-1.25+(i%3)*1.25,z=-.56+Math.floor(i/3)*1.04;for(let j=0;j<12;j++)box(d,x,.34+j*.012,z,.91,.009,.64,paper);
box(d,x,.52,z,.10,.024,.67,M(0x577560,.8))}
for(let x of [-1.24,1.24]){box(d,x,.06,1.36,.35,.26,.24,gold);let s=cy(d,x,.2,1.51,.04,.01,brass);s.rotation.x=Math.PI/2}
const h=ring(d,0,-.12,1.5,.43,.073,ink);h.rotation.x=Math.PI/2;
A.push(t=>{lid.rotation.x=-1.02+.08*Math.sin(t*.4)})}
 // 6 Night road: car approaching under one streetlight with three-dimensional beams.
{const g=stage();box(g,0,-1.55,0,28,.09,24,wall);for(let z=-11;z<11;z+=2.1)box(g,0,-1.495,z,.11,.008,1.03,paper);
const car=new THREE.Group();car.position.set(0,-.94,-2);g.add(car);box(car,0,0,0,2.3,.49,4.0,ink);box(car,0,.34,-.4,2.0,.7,2.15,steel);
for(let x of [-1.05,1.05])for(let z of [-1.25,1.25]){const w=cy(car,x,-.29,z,.32,.19,ink);w.rotation.z=Math.PI/2}
for(let x of [-.79,.79]){ball(car,x,-.02,2.06,.17,gold);const f=new THREE.SpotLight(0xffdfab,2.6,17,.22,.7);f.position.set(x,-.02,2.02);f.target.position.set(x*2,-1.3,11);car.add(f,f.target)}
const pole=cy(g,4.2,1.45,-1,.10,5.5,steel);box(g,3.45,4.15,-1,1.7,.14,.14,steel);
const yellow=new THREE.PointLight(0xffb879,1.9,16);yellow.position.set(2.75,3.8,-1);g.add(yellow);
for(let x of [-6,6])box(g,x,1.5,-9,4,4,.25,wall);
A.push(t=>{car.position.z=-2+t*.23})}
const poses=[[[1.4,1.6,6.8],[-.4,-1,0]],[[-2.7,1.25,7.5],[0,-.2,-4.0]],[[2.4,1.45,5.5],[0,-.4,.3]],[[1,1.4,6.1],[-.4,-1,0]],[[2.3,1.75,5.2],[0,-.3,0]],[[-3,1.25,6.0],[0,-1,-1.7]]];
window.frame=(T)=>{const i=Math.min(5,Math.floor(T/6)),t=T-i*6;G.forEach((g,j)=>g.visible=i===j);A[i](t);
const [xyz,target]=poses[i];C.position.set(xyz[0]+.06*Math.sin(t*.4),xyz[1],xyz[2]-.05*t);C.lookAt(...target);
S.fog=new THREE.FogExp2(i===1?0x273441:0x050911,i===1?.042:.012);
R.render(S,C);return R.domElement.toDataURL('image/png')};window.ready=true;window.frame(0);
