// Three.js preflight, private movie review only.
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 768/1366, 0.1, 100);
const R=new THREE.WebGLRenderer({canvas:document.getElementById('scene'),antialias:true,preserveDrawingBuffer:true});
R.setSize(768,1366,false);R.shadowMap.enabled=true;
const S=new THREE.Scene();S.background=new THREE.Color(0x0a0e17);
const C=new THREE.PerspectiveCamera(36,768/1366,.1,100);C.position.set(0,1,12);
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
