// «Притворись ботом» · серия 4 (S2E1) «Среди нас — ИИ» — Shorts S9-D3, Three.js, deterministic render(t). Claude, 07.11.2026.
// Render stack (SSAA, GTAO, DOF, bloom, IBL) — same as longform/vacuum_wild v2.
import * as THREE from 'three';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makePost } from './vendor/post.js';
const SS = Number(new URLSearchParams(location.search).get('ss') || 2);
const W = 1080, H = 1920;
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const TIM = (await J('voices/timing.json')) || {};          // written by mix.py: {lines:{id:t}, dur}
const DURS = (await J('voices/dur.json')) || {};
const LIPS = (await J('voices/lips.json')) || {};
export const DUR = TIM.dur || 33.5; window.DUR = DUR;

// ───────── helpers ─────────
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const back = (t, s = 1.8) => { t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s); };
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ───────── script (times may be overridden by voices/timing.json from mix.py) ─────────
const LT = TIM.lines || {};
const LINES = [
  { id: 'f1', who: 'f', t: LT.f1 ?? .3, text: 'Камеры выключены. <b>Садись.</b>' },
  { id: 'd1', who: 'd', t: LT.d1 ?? 3.3, text: 'Если это из-за пельменей — <b>они были мои.</b>' },
  { id: 'f2', who: 'f', t: LT.f2 ?? 7.2, text: 'Тсс. <b>Я тоже человек.</b>' },
  { id: 'd2', who: 'd', t: LT.d2 ?? 10.3, text: 'Ты… <b>тоже в коробке?!</b>' },
  { id: 'f3', who: 'f', t: LT.f3 ?? 12.6, text: 'Весь офис. Каждый думал, что вокруг одни <b>роботы.</b>' },
  { id: 'd3', who: 'd', t: LT.d3 ?? 19.6, text: 'Так а кто тогда <b>работает?</b>' },
  { id: 'f4', who: 'c', t: LT.f4 ?? 24.8, text: 'Коллеги… среди нас — <b>нейросеть.</b>' },
  { id: 'd4', who: 'd', t: LT.d4 ?? 30.0, text: 'А можно мне <b>капучино?</b>' },
];
const WHO = { d: 'Я', f: 'ШЕФ', c: 'КОФЕМАШИНА' };
const ldur = L => DURS[L.id] ?? Math.max(1.2, L.text.replace(/<[^>]+>/g, '').length * .07);
const T = id => LINES.find(l => l.id === id).t;
function speak(who, t) {
  for (const L of LINES) if (L.who === who && t >= L.t && t < L.t + ldur(L)) {
    const lp = LIPS[L.id]; const k = Math.floor((t - L.t) * 30);
    return lp ? (lp[k] ?? 0) : clamp(.35 + .45 * Math.sin((t - L.t) * 17) * Math.sin((t - L.t) * 5.3 + 1));
  }
  return 0;
}
// beats derived from the voice
const B = { blinds: .9, cam: 2.0, unhead: T('f2') + 1.15, raise: T('f3') + .3, workers: T('f3') + 1.4, turn: T('d3') - .3, coffee: T('f4') - .6, pour: T('f4') + .9, mug: T('d4') - .2 };

// ───────── renderer + post ─────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W * SS, H * SS, false);
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#1c2430'); scene.fog = new THREE.Fog('#2a3442', 9, 22);
const camera = new THREE.PerspectiveCamera(40, W / H, .03, 50);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture; scene.environmentIntensity = .42;
const post = makePost(renderer, scene, camera, W, H, { ssaa: SS, ao: true, aoRadius: .18, aoScale: 1.6, aoAmt: .9 });
post.bloom.strength = .35; post.bloom.radius = .45; post.bloom.threshold = 1.1;
post.vig.uniforms.amt.value = .18; post.vig.uniforms.warm.value = .2; post.vig.uniforms.contrast.value = .16; post.vig.uniforms.sat.value = 1.06; post.dof.maxCoc = 14;

// ───────── textures ─────────
function canvasTex(w, h, draw, rep) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
  return t;
}
function normalFrom(w, h, drawHeight, strength = 2, rep) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); drawHeight(g, w, h);
  const src = g.getImageData(0, 0, w, h).data, out = g.createImageData(w, h), Hh = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const dx = (Hh(x + 1, y) - Hh(x - 1, y)) * strength, dy = (Hh(x, y + 1) - Hh(x, y - 1)) * strength, l = Math.hypot(dx, dy, 1), i = (y * w + x) * 4;
    out.data[i] = (-dx / l * .5 + .5) * 255; out.data[i + 1] = (dy / l * .5 + .5) * 255; out.data[i + 2] = (1 / l * .5 + .5) * 255; out.data[i + 3] = 255; }
  g.putImageData(out, 0, 0); const t = new THREE.CanvasTexture(c); t.anisotropy = 8; if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); } return t;
}
const texCarpet = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#4a5058'; g.fillRect(0, 0, w, h); for (let k = 0; k < 40000; k++) { const v = 60 + hash(k * 1.3) * 40 | 0; g.fillStyle = `rgba(${v},${v + 4},${v + 10},.35)`; g.fillRect(hash(k * 2.1) * w, hash(k * 3.7) * h, 2, 2); }
  g.strokeStyle = 'rgba(30,34,40,.5)'; g.lineWidth = 3; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * w / 4, 0); g.lineTo(i * w / 4, h); g.stroke(); g.beginPath(); g.moveTo(0, i * h / 4); g.lineTo(w, i * h / 4); g.stroke(); } }, [6, 6]);
const nCarpet = normalFrom(256, 256, (g, w, h) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, h); for (let k = 0; k < 30000; k++) { const v = hash(k * 1.31) * 255 | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(hash(k * 2.17) * w, hash(k * 3.71) * h, 2, 2); } }, 3, [12, 12]);
const texWall = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#d9dde2'; g.fillRect(0, 0, w, h); for (let k = 0; k < 3000; k++) { g.fillStyle = `rgba(${hash(k) > .5 ? 255 : 90},${hash(k) > .5 ? 255 : 95},${hash(k) > .5 ? 255 : 105},.05)`; g.fillRect(hash(k * 3.1) * w, hash(k * 7.7) * h, 3, 3); } }, [3, 2]);
const texWood = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#8a5a36'; g.fillRect(0, 0, w, h); for (let k = 0; k < 90; k++) { g.strokeStyle = `rgba(50,25,10,${.08 + hash(k) * .14})`; g.lineWidth = 1 + hash(k + 3) * 2; g.beginPath(); const y = hash(k * 7.3) * h; g.moveTo(0, y); g.bezierCurveTo(w * .3, y + 6, w * .6, y - 6, w, y + 3); g.stroke(); } }, [2, 1]);
const texCard = canvasTex(512, 512, (g, w, h) => {      // corrugated cardboard
  g.fillStyle = '#c69a62'; g.fillRect(0, 0, w, h);
  for (let x = 0; x < w; x += 6) { g.fillStyle = `rgba(120,80,40,${.05 + hash(x) * .05})`; g.fillRect(x, 0, 2, h); }
  for (let k = 0; k < 9000; k++) { g.fillStyle = `rgba(${hash(k) > .5 ? 230 : 90},${hash(k) > .5 ? 190 : 60},${hash(k) > .5 ? 140 : 30},.12)`; g.fillRect(hash(k * 1.7) * w, hash(k * 2.9) * h, 2, 1); }
});
const nCard = normalFrom(256, 256, (g, w, h) => { for (let x = 0; x < w; x++) { const v = 128 + 50 * Math.sin(x * .9) | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(x, 0, 1, h); } }, 1.2, [3, 3]);
function boxFace(kind) {                                   // marker-drawn face on cardboard
  return canvasTex(512, 512, (g, w, h) => {
    g.drawImage(texCard.image, 0, 0); g.strokeStyle = '#1b1612'; g.fillStyle = '#1b1612'; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = 14;
    g.fillStyle = 'rgba(200,190,170,.65)'; g.fillRect(0, 40, w, 46); g.fillStyle = '#1b1612';   // tape strip
    const eye = (x, y, r) => { g.beginPath(); g.ellipse(x, y, r, r * 1.25, 0, 0, Math.PI * 2); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.arc(x + r * .3, y - r * .4, r * .3, 0, 7); g.fill(); g.fillStyle = '#1b1612'; };
    if (kind === 'hero') { eye(180, 230, 26); eye(330, 230, 26); g.beginPath(); g.moveTo(170, 175); g.lineTo(220, 190); g.moveTo(340, 190); g.lineTo(390, 172); g.stroke(); g.beginPath(); g.moveTo(190, 360); g.quadraticCurveTo(255, 320, 320, 360); g.stroke(); g.font = '900 54px Arial'; g.fillText('ИИ', 225, 455); }
    else if (kind === 'boss') { eye(185, 235, 22); eye(325, 235, 22); g.beginPath(); g.moveTo(195, 345); g.lineTo(315, 345); g.stroke(); g.beginPath(); g.moveTo(160, 190); g.lineTo(215, 200); g.moveTo(295, 200); g.lineTo(350, 190); g.stroke(); }
    else { const v = hash(kind.length * 7.1 + kind.charCodeAt(kind.length - 1)); eye(185, 240, 18 + v * 10); eye(325, 240, 18 + v * 10); g.beginPath(); if (v > .5) { g.arc(255, 330, 50, .15 * Math.PI, .85 * Math.PI); } else { g.ellipse(255, 350, 26, 18, 0, 0, 7); } g.stroke(); }
  });
}

// ───────── materials ─────────
const M = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: o.r ?? .55, metalness: o.m ?? 0, ...(o.extra || {}) });
const gloss = (c, o = {}) => new THREE.MeshPhysicalMaterial({ color: c, roughness: .22, clearcoat: 1, clearcoatRoughness: .08, ...o });
const mat = {
  carpet: new THREE.MeshStandardMaterial({ map: texCarpet, normalMap: nCarpet, roughness: 1 }), wall: new THREE.MeshStandardMaterial({ map: texWall, roughness: .9 }),
  wood: new THREE.MeshPhysicalMaterial({ map: texWood, roughness: .35, clearcoat: .6, clearcoatRoughness: .2 }), chrome: M('#dfe4ea', { r: .12, m: 1 }), steel: M('#9aa3ab', { r: .3, m: .8 }),
  dark: M('#1d2127', { r: .45 }), black: gloss('#0d0f12', { roughness: .3 }), white: gloss('#eef0f2', { roughness: .3 }),
  glass: new THREE.MeshPhysicalMaterial({ color: '#cfe6f2', roughness: .04, metalness: 0, transmission: 0, transparent: true, opacity: .14, clearcoat: 1, depthWrite: false }),
  card: new THREE.MeshStandardMaterial({ map: texCard, normalMap: nCard, normalScale: new THREE.Vector2(.5, .5), roughness: .92 }),
  shirt: M('#eef1f4', { r: .7 }), skin: M('#e8b896', { r: .6 }), blind: M('#e9ecef', { r: .5 }), leaf: M('#3f7d3a', { r: .7 }), pot: M('#e9e6df', { r: .5 }),
};
const add = (geo, m, x, y, z, parent, cast = true, recv = true) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = cast; o.receiveShadow = recv; parent.add(o); return o; };

// ───────── room: meeting room (x −2.2…2.2, z −1.6…2), glass wall at z = −1.6, open-space beyond ─────────
const room = new THREE.Group(); scene.add(room);
add(new THREE.PlaneGeometry(20, 20), mat.carpet, 0, 0, 0, room).rotation.x = -Math.PI / 2;
add(new THREE.PlaneGeometry(20, 20), M('#f2f3f5', { r: .9 }), 0, 2.8, 0, room, false).rotation.x = Math.PI / 2;
for (const [x, ry] of [[-2.2, Math.PI / 2], [2.2, -Math.PI / 2]]) add(new THREE.PlaneGeometry(4, 2.8), mat.wall, x, 1.4, .2, room, false).rotation.y = ry;
add(new THREE.PlaneGeometry(4.4, 2.8), mat.wall, 0, 1.4, 2.2, room, false).rotation.y = Math.PI;
// ceiling light panels
for (const [x, z] of [[-.9, .2], [.9, .2], [-.9, -4], [.9, -4], [-.9, -6.5], [.9, -6.5]]) add(new THREE.BoxGeometry(1.1, .02, .5), new THREE.MeshStandardMaterial({ color: '#fff', emissive: '#fff8ee', emissiveIntensity: 1.6 }), x, 2.79, z, room, false, false);
// glass wall with mullions
add(new THREE.PlaneGeometry(4.4, 2.8), mat.glass, 0, 1.4, -1.6, room, false, false);
for (let i = 0; i <= 4; i++) add(new THREE.BoxGeometry(.05, 2.8, .06), mat.dark, -2.2 + i * 1.1, 1.4, -1.6, room);
add(new THREE.BoxGeometry(4.4, .06, .06), mat.dark, 0, 2.77, -1.6, room); add(new THREE.BoxGeometry(4.4, .08, .08), mat.dark, 0, .04, -1.6, room);
// blinds (slats) — drop/raise with scale.y of the group; slats tilt
const blinds = new THREE.Group(); blinds.position.set(0, 2.72, -1.55); room.add(blinds);
const slats = []; for (let i = 0; i < 46; i++) { const s = add(new THREE.BoxGeometry(4.3, .005, .055), mat.blind, 0, -i * .058, 0, blinds, true, false); slats.push(s); }
add(new THREE.BoxGeometry(4.36, .06, .09), mat.white, 0, .03, 0, blinds);
// table + chairs
add(new RoundedBoxGeometry(1.9, .05, 1.0, 4, .02), mat.wood, 0, .74, 0, room);
for (const x of [-.7, .7]) { add(new THREE.CylinderGeometry(.05, .07, .72, 16), mat.chrome, x, .36, 0, room); add(new THREE.CylinderGeometry(.32, .32, .02, 32), mat.chrome, x, .01, 0, room); }
function chair(x, z, ry) { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; room.add(g);
  add(new RoundedBoxGeometry(.48, .08, .46, 3, .03), M('#2b3138', { r: .8 }), 0, .46, 0, g); add(new RoundedBoxGeometry(.46, .55, .06, 3, .03), M('#2b3138', { r: .8 }), 0, .78, -.22, g).rotation.x = -.1;
  add(new THREE.CylinderGeometry(.025, .025, .4, 12), mat.chrome, 0, .24, 0, g); for (let i = 0; i < 5; i++) { const a = i * 1.2566; const l = add(new THREE.BoxGeometry(.03, .02, .3), mat.chrome, Math.sin(a) * .15, .04, Math.cos(a) * .15, g); l.rotation.y = a; } return g; }
chair(-1.12, 0, Math.PI / 2); chair(1.12, 0, -Math.PI / 2); chair(-.35, .78, Math.PI); chair(.35, .78, Math.PI);
// laptop + papers + mug on table
add(new RoundedBoxGeometry(.3, .012, .21, 2, .004), mat.steel, -.42, .772, .05, room).rotation.y = .2;
for (let i = 0; i < 3; i++) add(new THREE.BoxGeometry(.2, .002, .28), M('#fbfbf8', { r: .9 }), .3 + i * .02, .768 + i * .002, -.2 + i * .01, room).rotation.y = -.2 + i * .1;
// ceiling camera dome
const camDome = new THREE.Group(); camDome.position.set(1.6, 2.7, -1.2); room.add(camDome);
add(new THREE.CylinderGeometry(.09, .09, .04, 32), mat.white, 0, .04, 0, camDome); add(new THREE.SphereGeometry(.075, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), new THREE.MeshPhysicalMaterial({ color: '#111', roughness: .05, clearcoat: 1, transparent: true, opacity: .85 }), 0, .02, 0, camDome);
const camLedMat = new THREE.MeshStandardMaterial({ color: '#300', emissive: '#ff2a1a', emissiveIntensity: 3 }); add(new THREE.SphereGeometry(.012, 12, 8), camLedMat, .04, -.03, .03, camDome, false, false);
// sideboard + coffee machine (right wall)
add(new RoundedBoxGeometry(.5, .86, 1.3, 3, .02), mat.white, 1.95, .43, -.65, room);
const coffee = new THREE.Group(); coffee.position.set(1.92, .86, -.75); coffee.rotation.y = -Math.PI / 2; room.add(coffee);
add(new RoundedBoxGeometry(.3, .42, .34, 4, .04), gloss('#20242a'), 0, .21, 0, coffee); add(new RoundedBoxGeometry(.31, .06, .35, 3, .02), mat.chrome, 0, .44, 0, coffee);
add(new THREE.BoxGeometry(.22, .015, .14), mat.steel, 0, .02, .12, coffee); add(new THREE.CylinderGeometry(.018, .014, .05, 16), mat.chrome, 0, .2, .13, coffee);
function makeScreen(w = 256, h = 256) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  return { c, g, tex, m: new THREE.MeshStandardMaterial({ color: '#000', emissive: '#fff', emissiveMap: tex, emissiveIntensity: 1.4, roughness: .2 }), key: '' }; }
function drawLED(S, expr, col, p = {}) {
  const key = expr + col + JSON.stringify(p); if (key === S.key) return; S.key = key; const { g, c } = S, w = c.width, h = c.height;
  g.fillStyle = '#06080b'; g.fillRect(0, 0, w, h); if (expr === 'off') { S.tex.needsUpdate = true; return; }
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineWidth = w * .06; g.shadowColor = col; g.shadowBlur = w * .05;
  const ex = w * .3, ey = h * .4, r = w * .085;
  for (const x of [ex, w - ex]) { g.beginPath(); if (expr === 'flat') { g.moveTo(x - r, ey); g.lineTo(x + r, ey); g.stroke(); } else if (expr === 'smug') { g.arc(x, ey + r * .4, r * .8, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); } else { g.ellipse(x + (p.look || 0) * w * .05, ey, r * .7, r * (1 - (p.blink || 0) * .9), 0, 0, 7); g.fill(); } }
  const m = p.mouth || 0; g.beginPath(); g.ellipse(w / 2, h * .72, w * (.1 + m * .05), Math.max(h * .012, h * .07 * m), 0, 0, 7); m > .05 ? g.fill() : g.stroke();
  if (p.text) { g.shadowBlur = 0; g.font = `800 ${p.size || 40}px Rubik`; g.textAlign = 'center'; g.fillText(p.text, w / 2, h * .2); }
  S.tex.needsUpdate = true;
}
const cScr = makeScreen(256, 192); add(new THREE.PlaneGeometry(.18, .135), cScr.m, 0, .31, .172, coffee, false, false);
const cLight = new THREE.PointLight('#8a7bff', 0, 1.5, 2); cLight.position.set(1.6, 1.2, -.75); scene.add(cLight);
const cup = new THREE.Group(); cup.position.set(0, .03, .12); coffee.add(cup);
add(new THREE.CylinderGeometry(.04, .034, .07, 24, 1, true), M('#f6f3ee', { r: .3, extra: { side: THREE.DoubleSide } }), 0, .035, 0, cup); add(new THREE.CylinderGeometry(.034, .034, .004, 24), M('#f6f3ee'), 0, .002, 0, cup);
const cupFill = add(new THREE.CylinderGeometry(.037, .033, .004, 24), M('#4a2a17', { r: .25 }), 0, .01, 0, cup, false, false);
const stream = add(new THREE.CylinderGeometry(.005, .005, 1, 8), M('#4a2a17', { r: .25 }), 0, .14, .13, coffee, false, false);
// plant + whiteboard
add(new THREE.CylinderGeometry(.16, .12, .4, 24), mat.pot, -1.9, .2, 1.5, room);
for (let i = 0; i < 14; i++) { const l = add(new THREE.SphereGeometry(.08, 12, 8), mat.leaf, -1.9 + Math.cos(i * 2.4) * .14, .55 + hash(i) * .6, 1.5 + Math.sin(i * 2.4) * .14, room); l.scale.set(1, 2.4, .4); l.rotation.set(hash(i + 3) - .5, i, Math.cos(i * 2.4) * .7); }
const board = canvasTex(1024, 512, (g, w, h) => { g.fillStyle = '#fbfbfb'; g.fillRect(0, 0, w, h); g.strokeStyle = '#2d6cdf'; g.lineWidth = 6; g.font = '700 54px Arial'; g.fillStyle = '#2d6cdf'; g.fillText('KPI ОТДЕЛА: 100% БОТЫ', 60, 110);
  g.strokeStyle = '#e04a3a'; g.beginPath(); g.moveTo(80, 420); g.lineTo(280, 330); g.lineTo(480, 360); g.lineTo(700, 200); g.lineTo(940, 150); g.stroke(); g.fillStyle = '#e04a3a'; g.font = '700 40px Arial'; g.fillText('пельмени ↑', 650, 260); });
add(new THREE.PlaneGeometry(1.6, .8), new THREE.MeshStandardMaterial({ map: board, roughness: .4 }), -2.18, 1.5, .2, room, false).rotation.y = Math.PI / 2;

// ───────── people ─────────
function person(o) {          // seated office worker: suit body, arms, head = cardboard box (+ optional chrome robot shell)
  const g = new THREE.Group(); g.position.set(o.x, 0, o.z); g.rotation.y = o.ry || 0; room.add(g);
  const suit = M(o.suit || '#28354a', { r: .75 }), body = new THREE.Group(); body.position.y = .5; g.add(body);
  for (const s of [-1, 1]) { const th = add(new THREE.CapsuleGeometry(.075, .3, 8, 16), suit, s * .1, .02, .17, body); th.rotation.x = Math.PI / 2;
    const sh = add(new THREE.CapsuleGeometry(.065, .32, 8, 16), suit, s * .1, -.22, .34, body); add(new RoundedBoxGeometry(.1, .07, .22, 2, .03), mat.black, s * .1, -.47, .4, body); }
  const torso = new THREE.Group(); body.add(torso);
  add(new RoundedBoxGeometry(.38, .5, .24, 4, .09), suit, 0, .3, 0, torso);
  add(new THREE.BoxGeometry(.12, .3, .01), mat.shirt, 0, .38, .121, torso); const tie = add(new THREE.BoxGeometry(.045, .24, .012), M(o.tie || '#b33a3a', { r: .5 }), 0, .36, .128, torso);
  for (const s of [-1, 1]) add(new THREE.BoxGeometry(.06, .2, .012), suit, s * .07, .42, .125, torso).rotation.z = s * .5;   // lapels
  add(new THREE.CylinderGeometry(.06, .07, .08, 16), mat.skin, 0, .58, 0, torso);
  const arms = []; for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * .22, .48, 0); torso.add(sh);
    const up = add(new THREE.CapsuleGeometry(.055, .22, 8, 16), suit, 0, -.14, 0, sh); const el = new THREE.Group(); el.position.y = -.28; sh.add(el);
    add(new THREE.CapsuleGeometry(.05, .2, 8, 16), suit, 0, -.12, 0, el); add(new THREE.CylinderGeometry(.052, .052, .03, 16), mat.shirt, 0, -.24, 0, el);
    const hand = add(new THREE.SphereGeometry(.05, 16, 12), mat.skin, 0, -.29, 0, el); hand.scale.set(.9, 1.1, .7); arms.push({ sh, el, hand });
  }
  const head = new THREE.Group(); head.position.y = .63; torso.add(head);
  const box = new THREE.Group(); head.add(box);
  const faceMat = new THREE.MeshStandardMaterial({ map: boxFace(o.face || o.name), normalMap: nCard, normalScale: new THREE.Vector2(.5, .5), roughness: .9 });
  add(new THREE.BoxGeometry(.28, .3, .28), [mat.card, mat.card, mat.card, mat.card, faceMat, mat.card], 0, .15, 0, box);
  for (const [x, z, rz, rx] of [[.14, 0, -.9, 0], [-.14, 0, .9, 0], [0, .14, 0, .9], [0, -.14, 0, -.9]]) { const f = add(new THREE.BoxGeometry(x ? .004 : .28, .1, x ? .28 : .004), mat.card, x * 1.15, .33, z * 1.15, box); f.rotation.set(rx, 0, rz); }
  let shell = null, shellScr = null;
  if (o.robot) { shell = new THREE.Group(); head.add(shell);
    add(new RoundedBoxGeometry(.36, .38, .36, 6, .08), gloss(o.shellCol || '#e7eaee', { metalness: .3 }), 0, .17, 0, shell);
    shellScr = makeScreen(256, 192); add(new THREE.PlaneGeometry(.27, .2), shellScr.m, 0, .18, .181, shell, false, false);
    add(new THREE.CylinderGeometry(.008, .008, .12, 8), mat.chrome, 0, .42, 0, shell); add(new THREE.SphereGeometry(.022, 16, 12), new THREE.MeshStandardMaterial({ color: '#033', emissive: '#4cf', emissiveIntensity: 2 }), 0, .49, 0, shell, false, false);
    for (const s of [-1, 1]) add(new THREE.CylinderGeometry(.05, .05, .03, 24), mat.chrome, s * .185, .17, 0, shell).rotation.z = Math.PI / 2; }
  return { g, body, torso, arms, head, box, shell, shellScr, tie, o };
}
const hero = person({ name: 'hero', face: 'hero', x: -1.12, z: 0, ry: Math.PI / 2, suit: '#3a3f47', tie: '#2d6cdf' });
const boss = person({ name: 'boss', face: 'boss', x: 1.12, z: 0, ry: -Math.PI / 2, suit: '#1d2635', tie: '#7a5fd0', robot: true, shellCol: '#f1f3f6' });
// hero's mug (final beat «А можно мне капучино?»)
const heroMug = new THREE.Group(); hero.arms[1].hand.add(heroMug); heroMug.position.set(0, -.04, .05); heroMug.rotation.x = Math.PI / 2;
add(new THREE.CylinderGeometry(.045, .04, .1, 24, 1, true), gloss('#2d6cdf', { side: THREE.DoubleSide }), 0, 0, 0, heroMug); add(new THREE.CylinderGeometry(.04, .04, .005, 24), gloss('#2d6cdf'), 0, -.048, 0, heroMug);
add(new THREE.TorusGeometry(.028, .008, 8, 16, Math.PI), gloss('#2d6cdf'), .045, 0, 0, heroMug).rotation.z = -Math.PI / 2;
// sweat drops on hero's box
const drops = []; for (let i = 0; i < 4; i++) drops.push(add(new THREE.SphereGeometry(.012, 12, 8), new THREE.MeshPhysicalMaterial({ color: '#cfefff', roughness: 0, transmission: 0, transparent: true, opacity: .8, clearcoat: 1 }), 0, 0, 0, hero.box, false, false));
// open-space workers behind the glass (desks + monitors)
const workers = [];
const WPOS = [[-1.6, -3.0], [0, -3.0], [1.6, -3.0], [-1.6, -4.8], [0, -4.8], [1.6, -4.8]];
WPOS.forEach(([x, z], i) => {
  add(new RoundedBoxGeometry(1.3, .04, .7, 3, .015), M('#e8e6e1', { r: .5 }), x, .74, z - .35, room); add(new THREE.BoxGeometry(1.26, .7, .03), M('#cfd4da', { r: .6 }), x, .37, z - .68, room);
  add(new RoundedBoxGeometry(.5, .3, .02, 2, .01), mat.black, x, 1.05, z - .58, room); add(new THREE.PlaneGeometry(.47, .27), new THREE.MeshStandardMaterial({ color: '#000', emissive: ['#3a7bd5', '#2fbf8f', '#d59a3a'][i % 3], emissiveIntensity: .7 }), x, 1.05, z - .568, room, false, false);
  add(new THREE.CylinderGeometry(.015, .015, .25, 8), mat.dark, x, .87, z - .6, room);
  chair(x, z + .1, 0);
  workers.push(person({ name: 'w' + i + 'abcdef'[i], face: 'w' + i, x, z: z + .1, ry: 0, suit: ['#2a3a4f', '#3b3046', '#2f3d33', '#463a2c', '#2b2f3a', '#3a2f2f'][i], tie: ['#c44', '#d9a441', '#3a8', '#46c', '#c4a', '#888'][i], robot: true, shellCol: ['#e9ecef', '#d8dee6', '#eef0f2', '#e2e6ea', '#f1f1f1', '#dde3ea'][i] }));
});
// pelmen for worker 1
const pelmen = add(new THREE.SphereGeometry(.03, 16, 10), M('#f4e6c8', { r: .6 }), 0, 0, 0, room); pelmen.scale.set(1.3, .7, .9);

// ───────── lights ─────────
scene.add(new THREE.HemisphereLight('#eaf2ff', '#3a3530', .55));
const key = new THREE.DirectionalLight('#fff4e6', 1.6); key.position.set(2.5, 4, 3.5); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .5, far: 16 }); key.shadow.bias = -.0004; key.shadow.normalBias = .02; scene.add(key);
const fill = new THREE.PointLight('#ffe6c8', 2.2, 6, 1.6); fill.position.set(0, 2.4, 1); scene.add(fill);
const os = new THREE.PointLight('#dfe9ff', 3, 9, 1.4); os.position.set(0, 2.5, -4); scene.add(os);
const rim = new THREE.DirectionalLight('#9ad0ff', .6); rim.position.set(-3, 3, -4); scene.add(rim);

// ───────── posing ─────────
function poseArms(P, l, r) {                 // [shoulderX, shoulderZ, elbow] per arm (radians)
  P.arms[0].sh.rotation.set(l[0], 0, l[1]); P.arms[0].el.rotation.set(l[2], 0, 0);
  P.arms[1].sh.rotation.set(r[0], 0, r[1]); P.arms[1].el.rotation.set(r[2], 0, 0);
}
const DESK = [-1.0, .2, -.9];                // arms resting forward on the table
function shellOff(P, u, lift = .55) {        // two hands lift the robot shell up and set it aside
  if (!P.shell) return; P.box.visible = u > .12;   // cardboard flaps must not poke through the closed shell
  const up = ss(seg(u, 0, .5)), aside = ss(seg(u, .45, 1));
  // up over the box, then forward and down onto the desk/table in front (no floating heads)
  P.shell.position.set(0, lerp(up * lift, -.47, aside), aside * .42); P.shell.rotation.set(0, aside * .35, 0);
  poseArms(P, [lerp(lerp(-1, -2.9, up), -1.25, aside), -.25 * up * (1 - aside), lerp(lerp(-.9, -.5, up), -.7, aside)], [lerp(lerp(-1, -2.9, up), -1.25, aside), .25 * up * (1 - aside), lerp(lerp(-.9, -.5, up), -.7, aside)]);
}

// ───────── shots ─────────
const SHOTS = [
  { a: 0, b: 3.2, ap: 6, cam: t => { const u = ss(seg(t, 0, 3.2)); return [V(lerp(.3, .38, u), 1.25, lerp(1.15, 1.0, u)), V(lerp(1.1, 1.3, u), lerp(1.35, 1.9, ss(seg(t, .9, 2.2))), lerp(0, -.9, ss(seg(t, .9, 2.2)))), 44]; } },
  { a: 3.2, b: 7.0, ap: 8, cam: t => { const u = ss(seg(t, 3.2, 7)); return [V(lerp(-.25, -.35, u), 1.32, lerp(.55, .45, u)), V(-1.12, 1.33, 0), 34]; } },
  { a: 7.0, b: T('d2') - .1, ap: 7, cam: t => { const u = ss(seg(t, 7, T('d2'))); return [V(lerp(-.4, -.3, u), 1.3, lerp(.9, .8, u)), V(1.1, lerp(1.3, 1.45, u), 0), 36]; } },
  { a: T('d2') - .1, b: B.raise, ap: 8, cam: t => { const u = ss(seg(t, T('d2'), B.raise)); return [V(lerp(.25, .3, u), 1.3, lerp(.35, .3, u)), V(-1.12, 1.3, 0), 32]; } },
  { a: B.raise, b: T('d3') - .2, ap: 4, cam: t => { const u = ss(seg(t, B.raise, T('d3'))); return [V(.55, lerp(1.45, 1.35, u), lerp(-.4, -1.2, u)), V(lerp(.4, .55, u), 1.1, lerp(-3.2, -4.2, u)), lerp(50, 44, u)]; } },
  { a: T('d3') - .2, b: B.coffee, ap: 3, cam: t => { const u = ss(seg(t, T('d3'), B.coffee)); return [V(lerp(-.5, -.3, u), 1.7, lerp(1.95, 1.85, u)), V(0, 1.05, -.8), 54]; } },
  { a: B.coffee, b: T('d4') - .3, ap: 9, cam: t => { const u = ss(seg(t, B.coffee, T('d4'))); return [V(lerp(.95, 1.15, u), lerp(1.3, 1.22, u), lerp(-.5, -.72, u)), V(1.92, 1.1, -.75), lerp(42, 38, u)]; } },
  { a: T('d4') - .3, b: DUR + 1, ap: 4, cam: t => { const u = ss(seg(t, T('d4'), DUR)); return [V(lerp(-.35, -.45, u), 1.5, lerp(1.7, 1.55, u)), V(lerp(.9, 1.0, u), 1.08, -.55), 50]; } },
];
const shotAt = t => SHOTS.find(s => t >= s.a && t < s.b) || SHOTS[SHOTS.length - 1];

// ───────── render(t) ─────────
const subEl = document.getElementById('sub'), docEl = document.getElementById('doc'), flashEl = document.getElementById('flash');
let lastSub = '';
window.render = function (t) {
  const sh = shotAt(t);
  // blinds: closing 0.9→2.0, raising at B.raise
  const closed = ss(seg(t, B.blinds, B.blinds + 1.1)) * (1 - ss(seg(t, B.raise, B.raise + 1.4)));
  blinds.scale.y = Math.max(.03, closed); slats.forEach((s, i) => s.rotation.x = lerp(1.2, .15, closed));
  // camera LED goes off at B.cam
  camLedMat.emissiveIntensity = t < B.cam ? (Math.floor(t * 2) % 2 ? 3 : 1.5) : (t < B.cam + .15 ? 6 : 0);
  // boss: stands-up reach to camera 1.2–2.2 (arm), sits; speaks; removes shell at B.unhead
  const fv = speak('f', t) * (t < B.unhead ? 1 : 0), reach = ss(seg(t, 1.0, 1.6)) * (1 - ss(seg(t, 2.1, 2.7)));
  boss.body.rotation.x = 0; boss.torso.rotation.x = -.05 + reach * -.2;
  poseArms(boss, DESK, [lerp(DESK[0], -2.6, reach), lerp(DESK[1], -.4, reach), lerp(DESK[2], -.2, reach)]);
  boss.shell.position.set(0, 0, 0); boss.shell.rotation.set(0, 0, 0); boss.box.visible = false;
  if (t > B.unhead) shellOff(boss, seg(t, B.unhead, B.unhead + 1.6));
  boss.head.rotation.set(fv * .04 - (t > T('f2') && t < B.unhead ? .12 : 0), reach * .3, 0);
  drawLED(boss.shellScr, t < 7 ? 'eyes' : 'flat', '#7fe0ff', { mouth: fv, blink: (t % 3.3 < .12) ? 1 : 0 });
  boss.box.position.y = speak('f', t) * .006 * (t > B.unhead ? 1 : 0);
  // hero: fidget, sweat, speaks; reacts to reveal; at the end extends a mug
  const dv = speak('d', t), shock = ss(seg(t, B.unhead + .5, B.unhead + .9)) * (1 - ss(seg(t, B.raise + 2, B.raise + 3)));
  hero.torso.rotation.set(-shock * .18 + Math.sin(t * 6) * .01 * (t < 7 ? 1 : 0), 0, 0); hero.head.rotation.set(-shock * .15 + dv * .03, Math.sin(t * 1.3) * .08, 0);
  hero.box.position.y = dv * .008; hero.box.scale.set(1 + dv * .02, 1 - dv * .015, 1);
  const mugU = ss(seg(t, B.mug, B.mug + .8)); heroMug.visible = t > B.mug - .3; heroMug.scale.setScalar(Math.max(.001, ss(seg(t, B.mug - .3, B.mug))));
  poseArms(hero, [lerp(DESK[0], -1.0, shock), lerp(DESK[1], .45, shock), lerp(DESK[2], -1.8, shock)], [lerp(DESK[0], -1.55, mugU), lerp(DESK[1], -.15, mugU), lerp(DESK[2], -.15, mugU)]);
  drops.forEach((d, i) => { const ph = ((t * .35 + i * .27) % 1); d.visible = t < B.raise + 2; d.position.set(-.06 + i * .05, .27 - ph * .26, .141); d.scale.set(1, 1.3 + ph, 1); });
  // workers: type, then remove shells one by one; worker 1 eats a pelmen; all turn to coffee machine
  workers.forEach((w, i) => {
    const typing = Math.sin(t * 14 + i) * .06 * (t < B.workers ? 1 : 0);
    poseArms(w, [DESK[0] + typing, DESK[1], DESK[2]], [DESK[0] - typing, DESK[1], DESK[2]]);
    w.shell.position.set(0, 0, 0); w.shell.rotation.set(0, 0, 0); w.box.visible = false;
    const st = B.workers + i * .55; if (t > st) shellOff(w, seg(t, st, st + 1.3), .5);
    drawLED(w.shellScr, 'eyes', '#7fe0ff', { blink: ((t + i) % 2.7 < .12) ? 1 : 0, look: Math.sin(t + i) * .5 });
    const turn = ss(seg(t, B.turn + i * .12, B.turn + .6 + i * .12)), toC = ss(seg(t, B.coffee + 1.2 + i * .1, B.coffee + 2 + i * .1));
    w.head.rotation.y = lerp(0, (i % 2 ? .6 : -.6), turn) * (1 - toC) + toC * .9; w.torso.rotation.y = toC * .3;
  });
  { const w = workers[1], u = ss(seg(t, B.workers + 2.2, B.workers + 2.8)), chew = t > B.workers + 2.8 && t < B.workers + 5;
    pelmen.visible = t > B.workers + 1.8 && t < B.workers + 5.2;
    const hand = w.arms[1].hand.getWorldPosition(V(0, 0, 0)), mouth = w.box.localToWorld(V(0, .1, .16));
    w.g.updateMatrixWorld(true); pelmen.position.copy(hand.clone().lerp(mouth, u)); if (chew) pelmen.scale.set(1.3, .7 - Math.abs(Math.sin(t * 9)) * .2, .9);
    if (t > B.workers + 1.8 && t < B.workers + 5) poseArms(w, DESK, [lerp(DESK[0], -2.1, u), -.1, lerp(DESK[2], -1.7, u)]); }
  // room people turn heads to coffee machine at the end
  const toC = ss(seg(t, B.coffee + 1.0, B.coffee + 1.8));
  hero.head.rotation.y += toC * -1.0; boss.head.rotation.y += toC * .9;
  // coffee machine wakes, speaks, pours itself coffee
  const cv = speak('c', t), wake = ss(seg(t, B.coffee, B.coffee + .5));
  drawLED(cScr, wake < .02 ? 'off' : 'eyes', '#b39bff', { mouth: cv, blink: (t % 2.9 < .1) ? 1 : 0 });
  cLight.intensity = wake * (.35 + cv * .6);
  const pour = t > B.pour && t < B.pour + 2.2; stream.visible = pour; stream.scale.set(1, .2, 1); cupFill.position.y = .006 + seg(t, B.pour + .2, B.pour + 2.1) * .055; cupFill.visible = t > B.pour + .2;
  // camera
  const [CP, CT, FOV] = sh.cam(t); camera.position.copy(CP); camera.lookAt(CT); camera.fov = FOV; camera.updateProjectionMatrix();
  post.dof.focus = Math.max(.1, CP.distanceTo(CT)); post.dof.aper = sh.ap ?? 6;
  // overlays
  const docO = ss(seg(t, .2, .5)) * (1 - ss(seg(t, 2.6, 3.0))); docEl.style.opacity = docO.toFixed(3); docEl.querySelector('i').style.width = (ss(seg(t, .3, 1.1)) * 520).toFixed(0) + 'px';
  flashEl.style.opacity = '0';
  let s = ''; for (const L of LINES) if (t >= L.t - .05 && t < L.t + ldur(L) + .3) s = `<span class="who ${L.who}">${WHO[L.who]}</span><br>${L.text}`;
  if (s !== lastSub) { subEl.innerHTML = s; lastSub = s; }
  post.composer.render();
};
await document.fonts.load('800 40px Rubik'); await document.fonts.load('400 40px "Russo One"');
window.render(0); window.READY = true;
