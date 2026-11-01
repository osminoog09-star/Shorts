// Three.js preflight, private movie review only.
const R=new THREE.WebGLRenderer({canvas:document.getElementById('scene'),antialias:true,preserveDrawingBuffer:true});
R.setSize(960,540,false);R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;R.outputEncoding=THREE.sRGBEncoding;R.toneMapping=THREE.ACESFilmicToneMapping;
const S=new THREE.Scene();S.background=new THREE.Color(0x0a0e17);
const C=new THREE.PerspectiveCamera(35,960/540,.1,100);C.position.set(0,.8,8.5);
S.add(new THREE.HemisphereLight(0xdcefff,0x29182a,.7));
const L=new THREE.DirectionalLight(0xffd5a6,1.5);L.position.set(-3,8,6);L.castShadow=true;S.add(L);
const K=new THREE.PointLight(0x538de6,2,12);K.position.set(3,3,-2);S.add(K);
const mat=(c,r=.45,m=.25)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m});
const gold=mat(0xc9a06a,.25,.85),wood=mat(0x513526,.65,.05),wall=mat(0x4b5562,.84),dark=mat(0x171f2a,.5,.65),light=mat(0x50dca5,.2,.4);
function box(g,x,y,z,w,h,d,m){const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;g.add(o);return o}
function sphere(g,x,y,z,r,m){const o=new THREE.Mesh(new THREE.SphereGeometry(r,28,20),m);o.position.set(x,y,z);g.add(o);return o}
const G=[],A=[];
for(let i=0;i<6;i++){
 const g=new THREE.Group();S.add(g);G.push(g);box(g,0,-2.2,-.5,6,.25,7,wood);
 if(i===0){
  const coin=new THREE.Group();coin.position.y=-.95;g.add(coin);
  coin.add(new THREE.Mesh(new THREE.CylinderGeometry(.92,.92,.14,64),gold));
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.78,.043,8,64),gold);
  ring.rotation.x=Math.PI/2;coin.add(ring);
  A.push(t=>{coin.rotation.x=Math.PI/2+.3*Math.sin(t);coin.rotation.y=t*3;coin.position.y=-.8+.1*Math.sin(t*2)});
 }
 else if(i===1){
  box(g,0,.2,-2,5.5,6.2,.5,wall);
  const pivot=new THREE.Group();pivot.position.set(-1.2,.1,-1.5);g.add(pivot);
  box(pivot,1.15,0,0,2.3,4.5,.18,wood);
  sphere(pivot,2.08,0,.14,.08,gold);
  A.push(t=>{pivot.rotation.y=-1.1*Math.min(1,t/4)});
 }else if(i===2){
  box(g,0,-.8,.1,3.5,1.75,2,dark);
  box(g,-.7,-.72,1.16,1.65,1.05,.09,mat(0x194c40,.32));
  const needle=box(g,-.7,-.7,1.24,1.45,.035,.035,light);
  sphere(g,1,-.4,1.17,.12,gold);
  A.push(t=>{needle.rotation.z=t*3});
 }
 else if(i===3){
  box(g,0,-1.6,0,5.1,.22,3.3,wood);
  const coin=new THREE.Group();g.add(coin);coin.position.set(-.8,-1.34,.5);
  coin.add(new THREE.Mesh(new THREE.CylinderGeometry(.55,.55,.09,48),gold));
  A.push(t=>{coin.position.x=-.8+1.8*Math.min(1,t/4);coin.rotation.y=t*.8});
 }
 else if(i===4){
  box(g,0,-1.3,0,3.15,.5,2.15,dark);
  const lid=new THREE.Group();lid.position.set(0,-1.1,-1.1);g.add(lid);
  box(lid,0,0,1,3.2,.19,2.2,dark);
  for(let n=0;n<4;n++)box(g,-.85+(n%2)*1.7,-.98,-.5+Math.floor(n/2)*.9,.9,.05,.58,mat(0x73927d,.7));
  A.push(t=>{lid.rotation.x=-1.2*(1-Math.min(1,t/4))});
 }
 else{
  box(g,0,-1.94,0,5,.08,5,mat(0x202327,.95));
  const car=new THREE.Group();g.add(car);
  box(car,0,-1.4,0,2.6,.55,1.2,dark);
  box(car,-.2,-1.02,-.1,1.45,.52,1,mat(0x264d62,.2,.65));
  for(const x of [-.8,.8])sphere(car,x,-1.35,.61,.13,gold);
  A.push(t=>{car.position.z=3-t*.65});
 }
}
// Additional cinematic prop detailing. All geometry is real Three.js; no PIL art.
const brass=new THREE.MeshPhysicalMaterial({color:0xdaa75d,metalness:.91,roughness:.26,clearcoat:.7});
const ebony=new THREE.MeshPhysicalMaterial({color:0x141922,metalness:.35,roughness:.35,clearcoat:.45});
const paint=new THREE.MeshStandardMaterial({color:0x5d3829,roughness:.58});
const paper=new THREE.MeshStandardMaterial({color:0xe6dcb7,roughness:.84});
const glass=new THREE.MeshPhysicalMaterial({color:0x32615e,metalness:.48,roughness:.22,clearcoat:1});
const crimson=new THREE.MeshStandardMaterial({color:0x9b331e,metalness:.08,roughness:.58});
function cy(g,x,y,z,r,h,m,axis='y'){const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,40),m);o.position.set(x,y,z);if(axis==='z')o.rotation.x=Math.PI/2;o.castShadow=true;g.add(o);return o}
function bolt(g,x,y,z,r=.045){const o=sphere(g,x,y,z,r,brass);o.scale.set(1,1,.42);return o}
function beam(g,x,y,z,l,rot,m){const o=box(g,x,y,z,l,.035,.035,m);o.rotation.z=rot;return o}
const overhead=new THREE.PointLight(0xffcb92,1.8,14);overhead.position.set(-2,3,4);S.add(overhead);
const fill=new THREE.PointLight(0x9bbaff,1.1,12);fill.position.set(3,.8,4);S.add(fill);
for(const g of G){
  for(let i=-3;i<=3;i++){const plank=box(g,i*.85,-2.046,0,.015,.009,6,mat(0x6c4634,.86));plank.castShadow=false;}
  for(let i=0;i<8;i++){const screw=cy(g,-2.45+i*.7,-1.968,2.0,.022,.012,brass);screw.castShadow=false;}
}
{
 const g=G[0],main=g.children.find(o=>o.type==='Group');
 // Coin detail: engraved face, knurled edge and embossed laurel ticks.
 if(main){
  const front=cy(main,0,-.075,0,.81,.008,brass);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.72,.022,8,64),brass);ring.rotation.x=Math.PI/2;ring.position.y=-.084;main.add(ring);
  for(let j=0;j<48;j++){
   const a=j*Math.PI/24;
   const o=box(main,Math.sin(a)*.895,0,Math.cos(a)*.895,.045,.15,.016,brass);o.rotation.y=a;
  }
  for(let j=0;j<12;j++){let a=j*Math.PI/6;const o=box(main,Math.sin(a)*.57,-.085,Math.cos(a)*.57,.045,.012,.17,brass);o.rotation.y=a;}
 }
 // Register counter props and metallic frame
 const tray=box(g,-1.7,-1.88,-.4,1.4,.08,.9,ebony);tray.rotation.y=-.17;
 for(let n=0;n<4;n++)cy(g,-2.1+n*.24,-1.8,-.4,.11,.04,brass);
 for(let n=0;n<5;n++){const sl=box(g,.6+n*.31,-2.05,1.35,.26,.015,.035,paint);sl.castShadow=false;}
}
{
 const g=G[1];
 // Motel: moulded door surround, room number plate, hinges and corridor lights.
 for(const x of [-1.28,1.24]){
   box(g,x,.07,-1.15,.10,4.9,.36,ebony);
   for(const y of [-1.65,1.65]){const hinge=box(g,x,y,-1.08,.10,.23,.11,brass);hinge.castShadow=true;}
 }
 box(g,0,2.48,-1.22,2.58,.13,.38,ebony);
 box(g,.7,1.67,-1.18,.42,.24,.036,brass);
 for(let j=0;j<3;j++)box(g,.55+j*.14,1.67,-1.15,.035,.10,.016,ebony);
 const sconce=box(g,-2.1,1.18,-1.1,.27,.6,.3,brass);
 const shade=box(g,-2.1,1.45,-1.1,.55,.22,.46,paper);
 const lamp=new THREE.PointLight(0xffc28a,1.1,5);lamp.position.set(-2.1,1.42,-.9);g.add(lamp);
 for(let n=-2;n<=2;n++)box(g,n*1.1,-1.97,1.6,.015,.015,3.0,ebony);
}
{
 const g=G[2]; // transmitter/electronics: switches, metal screws, vents, radar dials
 for(let j=0;j<9;j++){box(g,1.1,-1.3+j*.16,1.08,.4,.025,.04,brass);}
 for(let j=0;j<4;j++){let x=.9+(j%2)*.42,y=-.4+Math.floor(j/2)*.39;cy(g,x,y,1.21,.14,.07,ebony,'z');bolt(g,x,y,1.27,.05);}
 for(let j=0;j<6;j++){let x=-1.36+j*.27;box(g,x,-1.5,1.12,.12,.045,.05,brass);}
 for(let j=0;j<4;j++){const screw=bolt(g,-1.43+(j%2)*2.85,-1.35+Math.floor(j/2)*1.55,1.13,.06);}
 box(g,1.27,1,-1.1,.05,2.3,.05,brass);
 sphere(g,1.27,2.16,-1.1,.085,brass);
 const cable=new THREE.Mesh(new THREE.TorusGeometry(.58,.055,10,36,Math.PI*1.55),ebony);cable.position.set(-.15,-2.0,1.1);cable.rotation.y=.6;g.add(cable);
}
window.frame=(T)=>{
 const i=Math.min(5,Math.floor(T/6)),t=T-i*6;
 G.forEach((g,j)=>g.visible=i===j);A[i](t);
 C.position.set(.3+.2*Math.sin(t*.4),.6+.08*Math.sin(t*.3),9-t*.1);
 C.lookAt(0,-.6,0);R.render(S,C);
 return R.domElement.toDataURL('image/png');
};
window.ready=Promise.resolve(true);window.frame(0);
