// Живой 3D-космос студии M1lash (Claude, 06.11.2026). Three.js r170, WebGL, без внешних запросов.
// Сцена: звёздное поле (3 слоя, мерцание), туманность (fbm-шейдер в цветах бренда), чёрная дыра с аккреционным
// диском и гравитационной линзой (пост-проход по экрану), объёмные планеты с атмосферой, планета с кольцом, кометы.
// Параллакс от мыши / наклона телефона. Пауза в фоне вкладки, prefers-reduced-motion → почти статично.
// Нет WebGL → подключается 2D-версия space_bg.js.
import * as THREE from './vendor/three.module.min.js';

const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvas = document.createElement('canvas');
canvas.id = 'space'; canvas.setAttribute('aria-hidden', 'true');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
} catch (e) { renderer = null; }
if (!renderer || !renderer.getContext()) {
  const s = document.createElement('script'); s.src = 'space_bg.js?v=20261106'; document.head.appendChild(s);
} else {
  document.body.prepend(canvas);
  start();
}

function start() {
  let DPR = Math.min(devicePixelRatio || 1, innerWidth < 700 ? 1.25 : 1.25);
  const LOW = innerWidth < 700 || (navigator.hardwareConcurrency || 8) <= 4;
  renderer.setPixelRatio(DPR);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, 1, .1, 2000);
  camera.position.set(0, 0, 30);
  const U = { uT: { value: 0 } };

  // ---------- туманность: большая сфера с fbm ----------
  const NOISE = `
    float h(vec3 p){p=fract(p*.3183099+.1);p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
    float n(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);
      return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),
                 mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z);}
    float fbm(vec3 p){float a=.5,s=0.;for(int i=0;i<5;i++){s+=a*n(p);p*=2.03;a*=.5;}return s;}`;
  const neb = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 32), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, uniforms: U,
    vertexShader: `varying vec3 vP;void main(){vP=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `uniform float uT;varying vec3 vP;${NOISE}
      void main(){vec3 p=vP*2.2+vec3(uT*.004,0.,uT*.003);
        float a=fbm(p), b=fbm(p*1.7+5.), c=fbm(p*.8-3.);
        vec3 deep=vec3(.012,.01,.035);
        vec3 col=deep+vec3(.23,.48,1.)*pow(a,3.)*.55+vec3(.55,.36,.98)*pow(b,3.2)*.6+vec3(.94,.28,.6)*pow(c,3.5)*.45;
        col+=vec3(1.,.55,.3)*pow(max(0.,fbm(p*3.+9.)-.55),2.)*.35;
        gl_FragColor=vec4(col,1.);}`
  }));
  scene.add(neb);

  // ---------- звёзды: 3 слоя с мерцанием ----------
  function stars(count, rMin, rMax, size) {
    const g = new THREE.BufferGeometry(), P = new Float32Array(count * 3), C = new Float32Array(count * 3), S = new Float32Array(count), Ph = new Float32Array(count);
    const pal = [[.75, .85, 1], [1, 1, 1], [1, .85, .7], [.85, .75, 1], [1, .75, .85]];
    for (let i = 0; i < count; i++) {
      const u = Math.random() * 2 - 1, th = Math.random() * 6.283, r = rMin + Math.random() * (rMax - rMin), q = Math.sqrt(1 - u * u);
      P.set([r * q * Math.cos(th), r * u, r * q * Math.sin(th) - 200], i * 3);
      C.set(pal[i % 5], i * 3); S[i] = size * (.4 + Math.random() ** 3 * 1.8); Ph[i] = Math.random() * 6.283;
    }
    g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('color', new THREE.BufferAttribute(C, 3));
    g.setAttribute('size', new THREE.BufferAttribute(S, 1)); g.setAttribute('ph', new THREE.BufferAttribute(Ph, 1));
    return new THREE.Points(g, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uT: U.uT, uPR: { value: DPR } }, vertexColors: true,
      vertexShader: `attribute float size;attribute float ph;varying vec3 vC;varying float vA;uniform float uT;uniform float uPR;
        void main(){vC=color;vA=.55+.45*sin(uT*(1.+ph*.4)+ph*7.);vec4 mv=modelViewMatrix*vec4(position,1.);
        gl_PointSize=size*uPR*(300./-mv.z);gl_Position=projectionMatrix*mv;}`,
      fragmentShader: `varying vec3 vC;varying float vA;void main(){vec2 d=gl_PointCoord-.5;float r=length(d);
        float core=smoothstep(.5,0.,r);float spike=max(0.,1.-abs(d.x)*14.)*max(0.,1.-abs(d.y)*2.)+max(0.,1.-abs(d.y)*14.)*max(0.,1.-abs(d.x)*2.);
        gl_FragColor=vec4(vC,(pow(core,2.2)+spike*.25*core)*vA);}`
    }));
  }
  const far = stars(3500, 400, 800, 5), mid = stars(1200, 150, 380, 6), near = stars(240, 60, 140, 5);
  scene.add(far, mid, near);

  // ---------- планеты ----------
  const sunDir = new THREE.Vector3(-1, .35, .6).normalize();
  function planet(r, c1, c2, c3, seed, bands) {
    return new THREE.Mesh(new THREE.SphereGeometry(r, 96, 64), new THREE.ShaderMaterial({
      uniforms: { uT: U.uT, uSun: { value: sunDir }, c1: { value: new THREE.Color(c1) }, c2: { value: new THREE.Color(c2) }, c3: { value: new THREE.Color(c3) }, uSeed: { value: seed }, uBands: { value: bands } },
      vertexShader: `varying vec3 vN;varying vec3 vP;varying vec3 vW;void main(){vN=normalize(normalMatrix*normal);vP=position;
        vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
      fragmentShader: `uniform float uT;uniform vec3 uSun;uniform vec3 c1;uniform vec3 c2;uniform vec3 c3;uniform float uSeed;uniform float uBands;
        varying vec3 vN;varying vec3 vP;varying vec3 vW;${NOISE}
        void main(){vec3 p=normalize(vP);float lat=p.y;
          float sw=fbm(p*3.+vec3(uSeed+uT*.01,0.,0.));
          float band=sin(lat*uBands+sw*4.)*.5+.5;
          vec3 base=mix(c1,c2,band);base=mix(base,c3,smoothstep(.62,.9,fbm(p*6.+uSeed)));
          vec3 N=normalize(vN);vec3 V=normalize(cameraPosition-vW);
          float dif=max(dot(N,normalize((viewMatrix*vec4(uSun,0.)).xyz)),0.);
          float term=smoothstep(-.05,.35,dif);
          float rim=pow(1.-max(dot(N,V),0.),3.);
          vec3 col=base*(.04+term*1.05)+c1*rim*(.25+term*.9)*1.2;
          gl_FragColor=vec4(col,1.);}`
    }));
  }
  const gas = planet(5.2, '#ffb36b', '#c2410c', '#fde3c4', 2.1, 14.);
  gas.position.set(19, 9, -18); scene.add(gas);
  const ice = planet(2.6, '#8bd0ff', '#1e3a8a', '#e0f2ff', 7.3, 9.);
  ice.position.set(-24, -12, -8); scene.add(ice);
  const moon = planet(1.1, '#e9d5ff', '#6d28d9', '#faf5ff', 4.4, 6.);
  moon.position.set(9, -15, 4); scene.add(moon);
  // кольцо газового гиганта
  const ring = new THREE.Mesh(new THREE.RingGeometry(6.6, 11.5, 160, 1), new THREE.ShaderMaterial({
    side: THREE.DoubleSide, transparent: true, depthWrite: false, uniforms: { uSun: { value: sunDir } },
    vertexShader: `varying vec2 vU;varying vec3 vW;void main(){vU=uv;vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader: `varying vec2 vU;varying vec3 vW;void main(){float r=length(vW.xy-vec2(0.));
      float t=fract(vU.x);float b=.55+.45*sin(t*90.)*sin(t*31.+1.)+.2*sin(t*230.);
      float a=smoothstep(0.,.06,t)*smoothstep(1.,.85,t)*b*.75;gl_FragColor=vec4(vec3(1.,.86,.7)*(.6+.4*b),a);}`
  }));
  // RingGeometry uv.x не радиальный → считаем радиус через атрибут
  { const pos = ring.geometry.attributes.position, uv = ring.geometry.attributes.uv;
    for (let i = 0; i < pos.count; i++) { const r = Math.hypot(pos.getX(i), pos.getY(i)); uv.setX(i, (r - 6.6) / (11.5 - 6.6)); } uv.needsUpdate = true; }
  ring.rotation.set(1.25, .25, -.35); gas.add(ring);

  // ---------- чёрная дыра ----------
  const hole = new THREE.Group(); hole.position.set(-15, 8, -6); scene.add(hole);
  const R0 = 2.2;
  const disk = new THREE.Mesh(new THREE.RingGeometry(R0 * 1.35, R0 * 4.2, 220, 1), new THREE.ShaderMaterial({
    side: THREE.DoubleSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uT: U.uT },
    vertexShader: `varying vec2 vQ;void main(){vQ=position.xy;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `uniform float uT;varying vec2 vQ;${NOISE}
      void main(){float r=length(vQ)/${(R0).toFixed(2)};float a=atan(vQ.y,vQ.x);
        float spin=a+uT*1.2/(r*r)*2.;
        float s=fbm(vec3(cos(spin)*r*1.6,sin(spin)*r*1.6,r*.8));
        float heat=clamp(1.-(r-1.35)/2.85,0.,1.);
        vec3 hot=mix(vec3(1.,.35,.08),vec3(1.,.93,.78),pow(heat,1.6));
        float dopp=.55+.45*sin(a+1.2);
        float edge=smoothstep(1.35,1.6,r)*smoothstep(4.2,3.,r);
        float i=edge*(.25+s*1.4)*(.4+heat*1.4)*(.45+dopp);
        gl_FragColor=vec4(hot*i*1.6,i);}`
  }));
  disk.rotation.x = -1.18; disk.rotation.y = .18; hole.add(disk);
  // линзированная «задняя» часть диска: тонкая дуга над горизонтом, а не толстое кольцо-«глаз»
  const haloMat = disk.material.clone(); haloMat.uniforms = { uT: U.uT };
  haloMat.fragmentShader = haloMat.fragmentShader.replace('gl_FragColor=vec4(hot*i*1.6,i);', 'float arc=smoothstep(.15,.95,vQ.y/length(vQ));gl_FragColor=vec4(hot*i*.9*arc,i*.5*arc);');
  const halo = new THREE.Mesh(new THREE.RingGeometry(R0 * 1.25, R0 * 2.0, 160, 1), haloMat);
  halo.rotation.x = .12; hole.add(halo);
  const horizon = new THREE.Mesh(new THREE.SphereGeometry(R0, 64, 48), new THREE.MeshBasicMaterial({ color: 0x000000 }));
  hole.add(horizon);
  const photon = new THREE.Mesh(new THREE.RingGeometry(R0 * 1.02, R0 * 1.12, 128), new THREE.MeshBasicMaterial({ color: 0xffd9b0, transparent: true, opacity: .1, blending: THREE.AdditiveBlending, depthWrite: false }));
  hole.add(photon);

  // ---------- кометы ----------
  const comets = [];
  const cometMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `varying vec2 vU;void main(){vU=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `varying vec2 vU;void main(){float x=vU.x;float y=abs(vU.y-.5)*2.;
      float w=mix(.04,1.,pow(x,3.));float a=smoothstep(w,0.,y)*pow(x,1.6);
      vec3 c=mix(vec3(.3,.6,1.),vec3(1.),pow(x,6.));gl_FragColor=vec4(c*a*1.6,a);}`
  });
  function spawnComet() {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(14, .7), cometMat);
    const left = Math.random() < .5, y = 6 + Math.random() * 16, z = -10 - Math.random() * 30;
    m.position.set(left ? -60 : 60, y, z);
    const v = new THREE.Vector3(left ? 1 : -1, -.25 - Math.random() * .25, 0).normalize().multiplyScalar(9 + Math.random() * 6);
    m.rotation.z = Math.atan2(v.y, v.x); m.userData = { v, life: 0 };
    const head = new THREE.Mesh(new THREE.SphereGeometry(.16, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    head.position.x = 7; m.add(head);
    scene.add(m); comets.push(m);
  }

  // ---------- пост-проход: линза + мягкое свечение ----------
  const rt = new THREE.WebGLRenderTarget(2, 2, { type: THREE.HalfFloatType });
  const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
    uniforms: { tD: { value: rt.texture }, uH: { value: new THREE.Vector2(.3, .7) }, uR: { value: .05 }, uRh: { value: .02 }, uAsp: { value: 1 }, uRes: { value: new THREE.Vector2(1, 1) } },
    vertexShader: `varying vec2 vU;void main(){vU=uv;gl_Position=vec4(position.xy,0.,1.);}`,
    fragmentShader: `uniform sampler2D tD;uniform vec2 uH;uniform float uR;uniform float uRh;uniform float uAsp;uniform vec2 uRes;varying vec2 vU;
      void main(){vec2 d=vU-uH;d.x*=uAsp;float r=length(d);
        float k=min(uR*uR/max(r*r,1e-4)*.35,uR*.4);vec2 off=normalize(d+1e-6)*k;off.x/=uAsp;
        vec2 uv=vU-off*step(uR*.98,r);
        vec3 c=texture2D(tD,uv).rgb;
        vec3 g=vec3(0.);vec2 px=1./uRes;
        for(int i=-1;i<=1;i++)for(int j=-1;j<=1;j++){vec3 s=texture2D(tD,uv+vec2(i,j)*px*9.).rgb;g+=max(s-.7,0.);}
        c+=g/9.*1.2;
        c*=smoothstep(uRh*.92,uRh*1.08,r);
        float vig=smoothstep(1.25,.35,length((vU-.5)*vec2(uAsp,1.)));c*=mix(.55,1.,vig);
        gl_FragColor=vec4(c,1.);}`
  }));
  const postScene = new THREE.Scene(), postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1); postScene.add(post);

  // ---------- размеры / ввод ----------
  function size() {
    const w = innerWidth, h = innerHeight;
    renderer.setSize(w, h, false); canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    camera.aspect = w / h; camera.fov = w < h ? 70 : 55; camera.updateProjectionMatrix();
    rt.setSize(w * DPR, h * DPR); post.material.uniforms.uAsp.value = w / h; post.material.uniforms.uRes.value.set(w * DPR, h * DPR);
    const mob = w < 700;
    hole.position.set(mob ? 14 : -40, mob ? 38 : 30, -60); gas.position.set(mob ? 10 : 30, mob ? -22 : 2, -30); ice.position.set(mob ? -10 : -27, mob ? -30 : -15, -12);
  }
  addEventListener('resize', size); size();
  let tx = 0, ty = 0, px = 0, py = 0;
  addEventListener('pointermove', e => { tx = e.clientX / innerWidth - .5; ty = e.clientY / innerHeight - .5; }, { passive: true });
  addEventListener('deviceorientation', e => { if (e.gamma != null) { tx = Math.max(-.5, Math.min(.5, e.gamma / 70)); ty = Math.max(-.5, Math.min(.5, (e.beta - 45) / 100)); } }, { passive: true });
  let scrollY0 = 0; addEventListener('scroll', () => { scrollY0 = scrollY; }, { passive: true });

  // ---------- цикл ----------
  const clock = new THREE.Clock(); let raf = 0, nextComet = 1.5, slow = 0, last = performance.now();
  const hv = new THREE.Vector3();
  function frame(now) {
    raf = requestAnimationFrame(frame);
    // 30 кадров/с на слабых устройствах: космос медленный, разницы не видно, батарея целее
    const el = now - last; if (LOW && el < 30) return; last = now;
    if (el > (LOW ? 45 : 26) && el < 200) { if (++slow > 40 && DPR > .7) { DPR = Math.max(.7, DPR - .2); renderer.setPixelRatio(DPR); size(); slow = 0; } } else { slow = Math.max(0, slow - 1); }
    const dt = Math.min(clock.getDelta(), .05), t = clock.elapsedTime * (RM ? .05 : 1);
    U.uT.value = t;
    px += (tx - px) * .035; py += (ty - py) * .035;
    const sc = Math.min(scrollY0, 3000);
    camera.position.set(px * 6, -py * 4 - sc * .003, 30 - sc * .006);
    camera.lookAt(px * 2, -py * 1.5 - sc * .003, -20);
    camera.rotation.z = px * .03;
    far.rotation.y = t * .004; mid.rotation.y = t * .007; near.rotation.y = t * .012;
    gas.rotation.y = t * .05; ice.rotation.y = t * .08; moon.rotation.y = t * .12;
    moon.position.x = (innerWidth < 700 ? 5 : 9) + Math.cos(t * .05) * 3; moon.position.z = 4 + Math.sin(t * .05) * 3;
    hole.lookAt(camera.position); disk.rotation.z = 0; photon.lookAt(camera.position);
    if (RM) { /* статичный кадр раз в 2 с достаточно */ }
    if (!RM && (nextComet -= dt) <= 0) { spawnComet(); nextComet = 6 + Math.random() * 7; }
    for (let i = comets.length - 1; i >= 0; i--) { const c = comets[i]; c.position.addScaledVector(c.userData.v, dt); c.userData.life += dt; if (c.userData.life > 14) { scene.remove(c); c.geometry.dispose(); comets.splice(i, 1); } }
    // экранная позиция дыры для линзы
    hv.copy(hole.position).project(camera);
    post.material.uniforms.uH.value.set(hv.x * .5 + .5, hv.y * .5 + .5);
    const edge = hole.position.clone().add(new THREE.Vector3(R0 * 2.2, 0, 0)).project(camera);
    post.material.uniforms.uR.value = Math.abs(edge.x - hv.x) * .5 * (innerWidth / innerHeight) * .9;
    const he = hole.position.clone().add(new THREE.Vector3(R0, 0, 0)).project(camera);
    post.material.uniforms.uRh.value = Math.abs(he.x - hv.x) * .5 * (innerWidth / innerHeight);
    renderer.setRenderTarget(rt); renderer.render(scene, camera);
    renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancelAnimationFrame(raf); else { clock.getDelta(); last = performance.now(); raf = requestAnimationFrame(frame); } });
  window.__space3d = { renderer, scene, camera };
  raf = requestAnimationFrame(frame);
}
