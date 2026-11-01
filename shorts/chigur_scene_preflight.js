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
