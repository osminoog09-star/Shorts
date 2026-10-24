// Движок «премиальный стилизованный 3D»: PBR-материалы, студийный свет из RoomEnvironment,
// мягкие контактные тени, глубина резкости (Bokeh), пастельная палитра. Детерминированный renderAt(t).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
export { THREE, RoundedBoxGeometry };

export const W = 1920, H = 1080;
// пастель
export const C = {
  cream: 0xf3e9dd, sand: 0xe9d6bf, lav: 0xb5a2ff, mint: 0x86dcbc, peach: 0xffb48a, pink: 0xff98b1, butter: 0xffdc7a,
  sky: 0x8cc8ff, sage: 0xc5dcb8, gold: 0xe9b97f, bronze: 0xd9a06b, patina: 0x9fd6c2, coral: 0xff8f87, ink: 0x2b2a3a,
  deep: 0x3d3a5c, white: 0xffffff, sea: 0x8fd0e6, night: 0x2c2f4f,
};
export const CSS = {
  cream: '#f6efe6', lav: '#c6b8ff', mint: '#a9e6cf', peach: '#ffc9a8', pink: '#ffaec0', butter: '#ffe7a3', sky: '#a9d6ff',
  gold: '#e9b97f', coral: '#ff8f87', ink: '#2b2a3a', deep: '#3d3a5c', white: '#ffffff', patina: '#9fd6c2',
};

// ───────── easing ─────────
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const smooth = (x) => x * x * (3 - 2 * x);
export const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
export const easeIO2 = (x) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
export const easeOut = (x) => 1 - Math.pow(1 - x, 3);
export const easeIn = (x) => x * x * x;
export const backOut = (x, s = 1.6) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
export const spring = (x, k = 9, d = 5) => (x <= 0 ? 0 : 1 - Math.exp(-d * x) * Math.cos(k * x));
export function pop(t, t0, dur = 0.6) { const x = (t - t0) / dur; if (x <= 0) return 0; return spring(x * 1.4, 8, 5.5); }
export function hash(n) { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); }
export function noise1(x) { const i = Math.floor(x), f = x - i; return lerp(hash(i), hash(i + 1), smooth(f)) * 2 - 1; }

// ───────── renderer ─────────
const canvas = document.getElementById('gl');
export const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
renderer.shadowMap.enabled = !(window.DBG || {}).noShadow;
renderer.shadowMap.type = THREE.VSMShadowMap;
renderer.localClippingEnabled = true;

const pmrem = new THREE.PMREMGenerator(renderer);
export const envMap = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const DBG = window.DBG || {};
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { samples: DBG.samples ?? 4, type: THREE.HalfFloatType }));
const renderPass = new RenderPass(new THREE.Scene(), new THREE.PerspectiveCamera());
const bokeh = new BokehPass(renderPass.scene, renderPass.camera, { focus: 10, aperture: 0.0008, maxblur: 0.008 });
const grade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, vig: { value: 0.22 }, flash: { value: 0 }, fade: { value: 0 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time, vig, flash, fade; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
    void main(){ vec4 c=texture2D(tDiffuse,vUv); vec2 d=vUv-.5; d.x*=1.6;
      c.rgb*=1.-vig*smoothstep(.35,1.05,length(d));
      c.rgb+=(h(vUv*vec2(1920.,1080.)+fract(time*7.))-.5)*.022;
      c.rgb=mix(c.rgb, vec3(1.), flash); c.rgb=mix(c.rgb, vec3(0.965,0.937,0.902), fade);
      gl_FragColor=c; }`,
});
composer.addPass(renderPass);
if (!DBG.noBokeh) composer.addPass(bokeh);
composer.addPass(new OutputPass());
composer.addPass(grade);

export function render(scene, camera, opts = {}) {
  renderPass.scene = scene; renderPass.camera = camera;
  bokeh.scene = scene; bokeh.camera = camera;
  const u = bokeh.uniforms;
  u.focus.value = opts.focus ?? 10;
  u.aperture.value = opts.aperture ?? 0.0006;
  u.maxblur.value = opts.maxblur ?? 0.008;
  u.nearClip.value = camera.near; u.farClip.value = camera.far; u.aspect.value = W / H;
  grade.uniforms.time.value = opts.time || 0;
  grade.uniforms.flash.value = opts.flash || 0;
  grade.uniforms.fade.value = opts.fade || 0;
  grade.uniforms.vig.value = opts.vig ?? 0.22;
  composer.render();
}

// ───────── материалы ─────────
export const matte = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.0, envMapIntensity: 0.6, ...extra });
export const gloss = (color, extra = {}) => new THREE.MeshPhysicalMaterial({ color, roughness: 0.28, metalness: 0.0, clearcoat: 0.8, clearcoatRoughness: 0.15, envMapIntensity: 0.7, ...extra });
export const metal = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.32, metalness: 0.75, envMapIntensity: 1.2, ...extra });

// Студийная сцена: фон-циклорама, мягкий ключ с тенью, заполняющий и контровой
export function studio(scene, { bg = C.cream, floor = true, floorY = -2, key = [4, 9, 6], shadowSize = 14, keyI = 2.9, fill = 0.32 } = {}) {
  scene.environment = envMap;
  scene.background = new THREE.Color(bg);
  scene.fog = new THREE.Fog(bg, 30, 70);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xd9cbbb, fill));
  const k = new THREE.DirectionalLight(0xfff4e8, keyI); k.position.set(...key); k.castShadow = true;
  k.shadow.mapSize.set(1024, 1024); k.shadow.radius = 9; k.shadow.blurSamples = 16; k.shadow.bias = -0.0004;
  const s = k.shadow.camera; s.left = -shadowSize; s.right = shadowSize; s.top = shadowSize; s.bottom = -shadowSize; s.near = 0.5; s.far = 40;
  scene.add(k); scene.add(k.target);
  const rim = new THREE.DirectionalLight(0xd8e4ff, 0.8); rim.position.set(-6, 4, -8); scene.add(rim);
  let ground = null;
  if (floor) {
    ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({ color: bg, roughness: 0.95 }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = floorY; ground.receiveShadow = true; scene.add(ground);
  }
  return { key: k, ground };
}
export function shadowAll(obj, cast = true, receive = true) { obj.traverse((o) => { if (o.isMesh) { o.castShadow = cast; o.receiveShadow = receive; } }); return obj; }

// ───────── шестерня со скруглёнными кромками ─────────
export function gearShape(teeth, r, { depth = 0.11, holeR = 0.18, spokes = 4, rimW = 0.17 } = {}) {
  const s = new THREE.Shape();
  const ro = r, ri = r * (1 - depth);
  const n = teeth * 4;
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * Math.PI * 2;
    const ph = i % 4;
    const rr = ph === 0 ? ri : ph === 2 ? ro : (ri + ro) / 2 + (ro - ri) * 0.25;
    const x = Math.cos(a) * rr, y = Math.sin(a) * rr;
    if (i === 0) s.moveTo(x, y); else s.lineTo(x, y);
  }
  if (holeR > 0) { const h = new THREE.Path(); h.absarc(0, 0, r * holeR * 0.45, 0, Math.PI * 2, true); s.holes.push(h); }
  if (spokes > 0) {
    const rIn = r * holeR + r * 0.08, rOut = ri - r * rimW;
    if (rOut > rIn + r * 0.06) for (let k = 0; k < spokes; k++) {
      const a0 = (k / spokes) * Math.PI * 2 + 0.26, a1 = ((k + 1) / spokes) * Math.PI * 2 - 0.26;
      const p = new THREE.Path(); p.absarc(0, 0, rOut, a0, a1, false); p.absarc(0, 0, rIn, a1, a0, true); s.holes.push(p);
    }
  }
  return s;
}
const gearCache = new Map();
export function gear(teeth, r, mat, opts = {}) {
  const th = opts.thick ?? 0.3;
  const key = JSON.stringify([teeth, r, th, opts.spokes, opts.holeR]);
  let g = gearCache.get(key);
  if (!g) {
    const bev = Math.min(0.06, th * 0.25);
    g = new THREE.ExtrudeGeometry(gearShape(teeth, r, opts), { depth: th - bev * 2, bevelEnabled: true, bevelThickness: bev, bevelSize: bev * 0.8, bevelSegments: 3, curveSegments: 28 });
    g.translate(0, 0, -(th - bev * 2) / 2);
    g.computeVertexNormals();
    gearCache.set(key, g);
  }
  const m = new THREE.Mesh(g, typeof mat === 'number' ? metal(mat) : mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

// ───────── 2D-слой: премиальные подписи ─────────
const oc = document.getElementById('ov');
export const ctx = oc.getContext('2d');
export function clear2d() { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); }
export function project(v, camera) { const p = v.clone().project(camera); return { x: (p.x * 0.5 + 0.5) * W, y: (-p.y * 0.5 + 0.5) * H, z: p.z }; }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }

// Крупный заголовок, слова выезжают снизу из маски с пружиной
export function title(text, x, y, t, t0, { size = 120, color = CSS.ink, weight = 900, align = 'center', stagger = 0.07, dur = 0.7, out = null, letter = -2, font = 'Rubik' } = {}) {
  if (t < t0) return;
  const words = text.split(' ');
  ctx.save(); ctx.font = `${weight} ${size}px "${font}"`; ctx.textBaseline = 'alphabetic';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${letter}px`;
  const sp = ctx.measureText(' ').width;
  const widths = words.map((w) => ctx.measureText(w).width);
  const total = widths.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  const fo = out != null ? easeIn(seg(t, out, out + 0.45)) : 0;
  words.forEach((w, i) => {
    const k = easeOut(seg(t, t0 + i * stagger, t0 + i * stagger + dur));
    const kk = spring(seg(t, t0 + i * stagger, t0 + i * stagger + dur * 1.6) * 1.2, 7, 5);
    ctx.save();
    ctx.beginPath(); ctx.rect(cx - 20, y - size * 1.05, widths[i] + 40, size * 1.35); ctx.clip();
    ctx.globalAlpha = clamp(k * 1.4) * (1 - fo);
    ctx.fillStyle = color;
    ctx.fillText(w, cx, y + (1 - kk) * size * 1.1 - fo * size * 0.6);
    ctx.restore();
    cx += widths[i] + sp;
  });
  ctx.restore();
}

// Плашка-пилюля
export function pill(text, x, y, t, t0, { size = 40, bg = CSS.white, color = CSS.ink, dot = null, out = null, align = 'center', weight = 700, padX = 34, padY = 18 } = {}) {
  if (t < t0) return;
  const k = spring(seg(t, t0, t0 + 0.9) * 1.25, 8, 6);
  const fo = out != null ? easeIn(seg(t, out, out + 0.4)) : 0;
  if (k <= 0.001 || fo >= 1) return;
  ctx.save(); ctx.font = `${weight} ${size}px "Rubik"`;
  const tw = ctx.measureText(text).width + (dot ? size * 0.9 : 0);
  const w = tw + padX * 2, h = size + padY * 2;
  const x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  ctx.globalAlpha = clamp(k) * (1 - fo);
  ctx.translate(x0 + w / 2, y); ctx.scale(lerp(0.85, 1, k), lerp(0.85, 1, k)); ctx.translate(-(x0 + w / 2), -y);
  ctx.shadowColor = 'rgba(60,40,80,0.18)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
  rr(x0, y - h / 2, w, h, h / 2); ctx.fillStyle = bg; ctx.fill();
  ctx.shadowColor = 'transparent';
  let tx = x0 + padX;
  if (dot) { ctx.beginPath(); ctx.arc(tx + size * 0.3, y, size * 0.26, 0, Math.PI * 2); ctx.fillStyle = dot; ctx.fill(); tx += size * 0.9; }
  ctx.fillStyle = color; ctx.textBaseline = 'middle'; ctx.fillText(text, tx, y + size * 0.04);
  ctx.restore();
}

export function counter(value, x, y, { size = 200, color = CSS.ink, alpha = 1, suffix = '', align = 'center', font = 'Rubik', weight = 900 } = {}) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.font = `${weight} ${size}px "${font}"`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
  if ('letterSpacing' in ctx) ctx.letterSpacing = '-4px';
  ctx.fillStyle = color; ctx.fillText(String(value) + suffix, x, y); ctx.restore();
}

export function leader(p, x, y, t, t0, { color = CSS.ink, width = 3 } = {}) {
  const k = easeOut(seg(t, t0, t0 + 0.6)); if (k <= 0) return;
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = width; ctx.globalAlpha = 0.85; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(lerp(p.x, x, k), lerp(p.y, y, k)); ctx.stroke();
  ctx.beginPath(); ctx.arc(p.x, p.y, 7, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill();
  ctx.restore();
}

// Субтитр закадра
export function subtitle(words, t, { y = 1000, size = 40 } = {}) {
  const cur = words.filter((w) => w.start <= t + 0.05);
  if (!cur.length) return;
  let i = cur.length - 1; const line = [cur[i]];
  while (i > 0 && cur[i].start - cur[i - 1].end < 0.35 && line.length < 9) { i--; line.unshift(cur[i]); }
  const last = line[line.length - 1];
  if (t > last.end + 0.6) return;
  const txt = line.map((w) => w.w).join(' ');
  ctx.save(); ctx.font = `600 ${size}px "Rubik"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(txt).width + 60;
  ctx.globalAlpha = clamp((last.end + 0.6 - t) / 0.3);
  rr(960 - w / 2, y - size * 0.85, w, size * 1.7, size * 0.85); ctx.fillStyle = 'rgba(43,42,58,0.62)'; ctx.fill();
  ctx.fillStyle = '#fff'; ctx.fillText(txt, 960, y + 2);
  ctx.restore();
}

// Переход: мягкий круг цвета фона
export function iris(p, x = 960, y = 540, color = CSS.cream) {
  if (p <= 0 || p >= 2) return;
  const R = Math.hypot(W, H);
  ctx.save(); ctx.fillStyle = color;
  if (p < 1) { const r = easeInOut(p) * R; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); }
  else { const r = easeInOut(p - 1) * R; ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.arc(x, y, r, 0, Math.PI * 2, true); ctx.fill('evenodd'); }
  ctx.restore();
}
