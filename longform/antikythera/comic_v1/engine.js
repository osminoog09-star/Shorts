// Движок комикс-3D: toon-материалы, обводка, полутона, стикеры. Детерминированный renderAt(t).
import * as THREE from './node_modules/three/build/three.module.js';
export { THREE };
THREE.ColorManagement.enabled = false;

export const W = 1920, H = 1080;
export const C = {
  sea: 0x1fb5c9, sun: 0xffd23f, bronze: 0xf08a24, patina: 0x3fbf8f, red: 0xff4a3d,
  paper: 0xfff3d6, ink: 0x111111, blue: 0x2f6bff, pink: 0xff7eb6, purple: 0x8a5cff, white: 0xffffff,
};
export const CSS = {
  sea: '#1fb5c9', sun: '#ffd23f', bronze: '#f08a24', patina: '#3fbf8f', red: '#ff4a3d',
  paper: '#fff3d6', ink: '#111111', blue: '#2f6bff', pink: '#ff7eb6', purple: '#8a5cff', white: '#ffffff',
};

// ───────── easing / пружины ─────────
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const smooth = (x) => x * x * (3 - 2 * x);
export const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
export const easeOut = (x) => 1 - Math.pow(1 - x, 3);
export const backOut = (x, s = 2.2) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
// затухающая пружина: 0 → 1 с перелётом
export const spring = (x, k = 9, d = 4.5) => (x <= 0 ? 0 : 1 - Math.exp(-d * x) * Math.cos(k * x));
// упругий «поп» масштаба (squash/stretch) для момента появления
export function pop(t, t0, dur = 0.5) {
  const x = (t - t0) / dur;
  if (x <= 0) return { s: 0, sx: 0, sy: 0 };
  const s = spring(x * 1.6, 11, 5);
  const wob = Math.exp(-5 * x) * Math.sin(x * 14) * 0.18;
  return { s, sx: s * (1 + wob), sy: s * (1 - wob) };
}
// детерминированный шум
export function hash(n) { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); }
export function noise1(x) { const i = Math.floor(x), f = x - i; return lerp(hash(i), hash(i + 1), smooth(f)) * 2 - 1; }

// ───────── renderer + пост-проход ─────────
const canvas = document.getElementById('gl');
export const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;

const SS = 1.5; // суперсэмплинг цвета для гладких краёв
const colorRT = new THREE.WebGLRenderTarget(W * SS, H * SS, { samples: 0, type: THREE.UnsignedByteType });
const normalRT = new THREE.WebGLRenderTarget(W, H);
normalRT.depthTexture = new THREE.DepthTexture(W, H);
const normalMat = new THREE.MeshNormalMaterial();

const post = new THREE.ShaderMaterial({
  uniforms: {
    tColor: { value: colorRT.texture }, tNormal: { value: normalRT.texture }, tDepth: { value: normalRT.depthTexture },
    res: { value: new THREE.Vector2(W, H) }, near: { value: 0.1 }, far: { value: 200 },
    bgA: { value: new THREE.Color(C.sea) }, bgB: { value: new THREE.Color(C.paper) },
    bgMode: { value: 0 }, line: { value: 3.0 }, halftone: { value: 1.0 }, time: { value: 0 },
    flash: { value: 0 }, xray: { value: 0 }, dotScale: { value: 9.0 }, tint: { value: new THREE.Vector4(0, 0, 0, 0) },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `
    precision highp float;
    varying vec2 vUv;
    uniform sampler2D tColor, tNormal, tDepth;
    uniform vec2 res; uniform float near, far, line, halftone, time, flash, xray, dotScale;
    uniform vec3 bgA, bgB; uniform float bgMode; uniform vec4 tint;
    float lin(float d){ float z=d*2.-1.; return (2.*near*far)/(far+near-z*(far-near)); }
    float dep(vec2 uv){ return lin(texture2D(tDepth, uv).r); }
    vec3 nor(vec2 uv){ return texture2D(tNormal, uv).rgb*2.-1.; }
    float h21(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
    float dots(vec2 px, float amount, float ang, float sc){
      float c=cos(ang), s=sin(ang); vec2 q=mat2(c,-s,s,c)*px/sc; vec2 g=fract(q)-.5;
      float r=sqrt(clamp(amount,0.,1.))*.62; return 1.-smoothstep(r-.07, r+.07, length(g));
    }
    void main(){
      vec2 px=1./res; vec2 uv=vUv;
      float d0=texture2D(tDepth, uv).r; bool bg = d0>=0.99999;
      vec3 col = texture2D(tColor, uv).rgb;
      // обводка: разрывы глубины и нормалей по кругу радиуса line
      float e=0.; float z0=dep(uv); vec3 n0=nor(uv);
      for(int i=0;i<8;i++){
        float a=float(i)*0.785398; vec2 o=vec2(cos(a),sin(a))*line*px;
        float zd=texture2D(tDepth, uv+o).r; float z1=lin(zd);
        bool b1 = zd>=0.99999;
        if(bg != b1) e=1.;
        else if(!bg){
          float dz=abs(z1-z0)/max(z0,0.5); if(dz>0.045) e=1.;
          vec3 n1=nor(uv+o); if(dot(n0,n1)<0.72) e=max(e, 1.);
        }
      }
      if(bg){
        // фон: плоский цвет + радиальные полутона
        vec2 c=uv-.5; c.x*=res.x/res.y; float r=length(c);
        col = mix(bgA, bgA*0.82, smoothstep(.2,.95,r));
        float dd = dots(gl_FragCoord.xy, smoothstep(.25,1.1,r)*0.55*halftone, .785, dotScale*1.3);
        col = mix(col, col*0.62, dd);
        if(bgMode>0.5){ col = mix(bgB, bgB*0.9, smoothstep(.2,.95,r)); col=mix(col, bgA, dd*.5); }
      } else {
        // полутона в тени (по яркости тона)
        float lum=dot(col, vec3(.299,.587,.114));
        float sh = smoothstep(.62, .18, lum);
        float dd = dots(gl_FragCoord.xy, sh*0.7*halftone, .785, dotScale);
        col = mix(col, col*0.55, dd);
        // рентген
        if(xray>0.){ vec3 xr = vec3(.55,.95,1.)*(0.35+0.65*abs(n0.z)); col=mix(col, xr*vec3(.25,.75,.95), xray*.85); }
      }
      col = mix(col, tint.rgb, tint.a);
      col = mix(col, vec3(0.067), e);
      // бумажное зерно
      float g = h21(floor(gl_FragCoord.xy*.5)+floor(time*12.)) - .5;
      col += g*0.035;
      col = mix(col, vec3(1.), flash);
      gl_FragColor=vec4(col,1.);
    }`,
  depthTest: false, depthWrite: false,
});
const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post);
const postScene = new THREE.Scene(); postScene.add(quad);
const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

export function render(scene, camera, opts = {}) {
  post.uniforms.near.value = camera.near; post.uniforms.far.value = camera.far;
  post.uniforms.time.value = opts.time || 0;
  post.uniforms.bgA.value.set(opts.bg ?? C.sea);
  post.uniforms.bgB.value.set(opts.bg2 ?? C.paper);
  post.uniforms.bgMode.value = opts.bgMode || 0;
  post.uniforms.line.value = opts.line ?? 3.0;
  post.uniforms.halftone.value = opts.halftone ?? 1;
  post.uniforms.flash.value = opts.flash || 0;
  post.uniforms.xray.value = opts.xray || 0;
  const tn = opts.tint; post.uniforms.tint.value.set(tn ? tn[0] : 0, tn ? tn[1] : 0, tn ? tn[2] : 0, tn ? tn[3] : 0);
  scene.background = null;
  renderer.setRenderTarget(colorRT); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
  const om = scene.overrideMaterial; scene.overrideMaterial = normalMat;
  const hidden = [];
  scene.traverse((o) => { if (o.userData.noNormal && o.visible) { o.visible = false; hidden.push(o); } });
  renderer.setRenderTarget(normalRT); renderer.clear(); renderer.render(scene, camera);
  hidden.forEach((o) => { o.visible = true; });
  scene.overrideMaterial = om;
  post.uniforms.tDepth.value = normalRT.depthTexture;
  renderer.setRenderTarget(null); renderer.render(postScene, postCam);
}

// ───────── материалы ─────────
const gradTex = (() => {
  const d = new Uint8Array([90, 170, 255]);
  const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t;
})();
export const toon = (color, extra = {}) => new THREE.MeshToonMaterial({ color, gradientMap: gradTex, ...extra });

export function lights(scene, { key = [5, 8, 6], amb = 0.9 } = {}) {
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, amb));
  const d = new THREE.DirectionalLight(0xffffff, 2.2); d.position.set(...key); scene.add(d);
  return d;
}

// ───────── геометрия ─────────
export function gearShape(teeth, r, { depth = 0.12, holeR = 0.18, spokes = 4, rimW = 0.18, tri = 0.5 } = {}) {
  const s = new THREE.Shape();
  const ro = r, ri = r * (1 - depth);
  const n = teeth * 2;
  for (let i = 0; i <= n; i++) {
    const a0 = (i / n) * Math.PI * 2;
    const out = i % 2 === 0;
    // треугольные зубцы (как у механизма)
    const rr = out ? ro : ri;
    const a = a0 + (out ? 0 : 0);
    const x = Math.cos(a) * rr, y = Math.sin(a) * rr;
    if (i === 0) s.moveTo(x, y); else s.lineTo(x, y);
  }
  if (holeR > 0) {
    const h = new THREE.Path(); h.absarc(0, 0, r * holeR * 0.5, 0, Math.PI * 2, true); s.holes.push(h);
  }
  if (spokes > 0) {
    const rIn = r * holeR + r * 0.06, rOut = ri - r * rimW;
    if (rOut > rIn + r * 0.05) {
      for (let k = 0; k < spokes; k++) {
        const a0 = (k / spokes) * Math.PI * 2 + 0.22, a1 = ((k + 1) / spokes) * Math.PI * 2 - 0.22;
        const p = new THREE.Path();
        p.absarc(0, 0, rOut, a0, a1, false);
        p.absarc(0, 0, rIn, a1, a0, true);
        s.holes.push(p);
      }
    }
  }
  return s;
}
const gearCache = new Map();
export function gear(teeth, r, color = C.bronze, opts = {}) {
  const key = JSON.stringify([teeth, r, opts]);
  let g = gearCache.get(key);
  if (!g) {
    g = new THREE.ExtrudeGeometry(gearShape(teeth, r, opts), { depth: opts.thick ?? 0.12, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.015, bevelSegments: 1, curveSegments: 24 });
    g.translate(0, 0, -(opts.thick ?? 0.12) / 2);
    gearCache.set(key, g);
  }
  return new THREE.Mesh(g, toon(color));
}

// ───────── 2D-слой стикеров ─────────
const oc = document.getElementById('ov');
export const ctx = oc.getContext('2d');
export function clear2d() { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); }

export function project(v3, camera) {
  const v = v3.clone().project(camera);
  return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H, z: v.z };
}

// Стикер-текст: белая вырубка + чёрный контур + заливка + тень
export function sticker(text, x, y, { size = 90, font = 'Rubik', weight = 900, fill = CSS.sun, ink = CSS.ink, rot = 0, sx = 1, sy = 1, cut = 18, line = 7, shadow = 10, align = 'center', alpha = 1, upper = true, lh = 1.05 } = {}) {
  if (sx <= 0.001 || alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sx, sy);
  ctx.font = `${weight} ${size}px "${font}"`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round'; ctx.miterLimit = 2;
  const lines = String(upper ? text.toUpperCase() : text).split('\n');
  const yy = (i) => (i - (lines.length - 1) / 2) * size * lh;
  // тень
  ctx.save(); ctx.translate(shadow * 0.6, shadow);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = cut * 2 + line * 2;
  lines.forEach((l, i) => ctx.strokeText(l, 0, yy(i)));
  ctx.restore();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = cut * 2 + line * 2; lines.forEach((l, i) => ctx.strokeText(l, 0, yy(i)));
  ctx.strokeStyle = ink; ctx.lineWidth = line * 2; lines.forEach((l, i) => ctx.strokeText(l, 0, yy(i)));
  ctx.fillStyle = fill; lines.forEach((l, i) => ctx.fillText(l, 0, yy(i)));
  ctx.restore();
}

// Звуковая надпись во «взрыве»
export function burst(text, x, y, { r = 170, fill = CSS.sun, txt = CSS.red, rot = -0.12, s = 1, spikes = 14, size = 86, seed = 1 } = {}) {
  if (s <= 0.001) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  const path = new Path2D();
  for (let i = 0; i <= spikes * 2; i++) {
    const a = (i / (spikes * 2)) * Math.PI * 2;
    const rr = i % 2 === 0 ? r * (1 + 0.18 * hash(i + seed * 13)) : r * 0.68;
    const px = Math.cos(a) * rr * 1.25, py = Math.sin(a) * rr;
    i ? path.lineTo(px, py) : path.moveTo(px, py);
  }
  path.closePath();
  ctx.save(); ctx.translate(8, 12); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fill(path); ctx.restore();
  ctx.lineJoin = 'round';
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 34; ctx.stroke(path);
  ctx.strokeStyle = CSS.ink; ctx.lineWidth = 10; ctx.stroke(path);
  ctx.fillStyle = fill; ctx.fill(path);
  ctx.restore();
  sticker(text, x, y, { size, fill: txt, rot: rot + 0.05, sx: s, sy: s, cut: 0, line: 8, shadow: 0 });
}

// Линии действия/скорости вокруг точки
export function speedLines(x, y, { r0 = 220, r1 = 520, n = 26, alpha = 1, seed = 3, width = 7 } = {}) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = CSS.ink; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + hash(i + seed) * 0.2;
    const a0 = r0 * (0.9 + 0.3 * hash(i * 3 + seed)), a1 = r1 * (0.8 + 0.4 * hash(i * 7 + seed));
    ctx.lineWidth = width * (0.5 + hash(i * 11 + seed));
    ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * a0, y + Math.sin(a) * a0); ctx.lineTo(x + Math.cos(a) * a1, y + Math.sin(a) * a1); ctx.stroke();
  }
  ctx.restore();
}

// Комикс-плашка подписи (нарратив)
export function caption(text, x, y, { w = 720, size = 40, fill = CSS.sun, rot = -0.02, s = 1, align = 'left' } = {}) {
  if (s <= 0.001) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.font = `700 ${size}px "Rubik"`;
  const words = text.split(' '); const lines = []; let cur = '';
  for (const wd of words) { const tt = cur ? cur + ' ' + wd : wd; if (ctx.measureText(tt).width > w - 60 && cur) { lines.push(cur); cur = wd; } else cur = tt; }
  if (cur) lines.push(cur);
  const h = lines.length * size * 1.2 + 40;
  ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(10, 12, w, h);
  ctx.fillStyle = '#fff'; ctx.fillRect(-12, -12, w + 24, h + 24);
  ctx.fillStyle = fill; ctx.fillRect(0, 0, w, h);
  ctx.lineWidth = 7; ctx.strokeStyle = CSS.ink; ctx.strokeRect(0, 0, w, h);
  ctx.fillStyle = CSS.ink; ctx.textBaseline = 'top'; ctx.textAlign = 'left';
  lines.forEach((l, i) => ctx.fillText(l, 30, 22 + i * size * 1.2));
  ctx.restore();
}

// Иконка-стикер из Path2D-рисовалки (cb рисует в локальных координатах ~[-100,100])
export function iconSticker(draw, x, y, { s = 1, rot = 0, cut = 16 } = {}) {
  if (s <= 0.001) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  // три прохода: тень, белая вырубка, обычный
  for (const pass of ['shadow', 'cut', 'main']) {
    ctx.save();
    if (pass === 'shadow') ctx.translate(8, 11);
    draw(ctx, pass, cut);
    ctx.restore();
  }
  ctx.restore();
}

// Переход «полутоновая шторка»: закрывает кадр точками, растущими по диагонали
export function dotWipe(p, { color = CSS.ink, dir = 1, cell = 46 } = {}) {
  if (p <= 0 || p >= 2) return;
  ctx.save(); ctx.fillStyle = color;
  for (let y = -cell; y < H + cell; y += cell) {
    for (let x = -cell; x < W + cell; x += cell) {
      const xx = x + ((y / cell) % 2) * cell * 0.5;
      const k = (dir > 0 ? xx / W : 1 - xx / W) * 0.6 + (y / H) * 0.4; // 0..1
      const a = p < 1 ? clamp((p * 1.6 - k * 0.6) * 2.2) : clamp(((2 - p) * 1.6 - (1 - k) * 0.6) * 2.2);
      if (a <= 0) continue;
      ctx.beginPath(); ctx.arc(xx, y, a * cell * 0.78, 0, Math.PI * 2); ctx.fill();
    }
  }
  ctx.restore();
}
