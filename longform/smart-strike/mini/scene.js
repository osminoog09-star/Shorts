// «Забастовка умного дома» — mini Shorts, Three.js, deterministic render(t). Original characters (Claude, 05.11.2026).
import * as THREE from 'three';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';

const W = 1080, H = 1920;
export const DUR = 40.0;
window.DUR = DUR;

// ───────── helpers ─────────
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const ei = t => Math.pow(clamp(t), 3);
const back = (t, s = 1.8) => { t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s); };
const spring = (t, k = 9, z = .32) => { t = Math.max(0, t); return 1 - Math.exp(-z * k * t) * Math.cos(k * Math.sqrt(1 - z * z) * t * 1.4); };
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const vnoise = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u); };
// keyframes: [[t, v], ...] smoothstep between keys
function K(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [a, va] = keys[i], [b, vb] = keys[i + 1];
    if (t <= b) { const u = ss((t - a) / (b - a)); return Array.isArray(va) ? va.map((x, j) => lerp(x, vb[j], u)) : lerp(va, vb, u); }
  }
  return keys[keys.length - 1][1];
}

// ───────── script / timing ─────────
// voice line placement (seconds); durations come from voices/dur.json when present
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const DURS = (await J('voices/dur.json')) || {};
const LIPS = (await J('voices/lips.json')) || {};
const LINES = [
  { id: 'm_h1', who: 'h', t: 0.25, text: 'Дом, кофе! Срочно!' },
  { id: 'm_f1', who: 'f', t: 3.3, text: 'Доброе утро! Сегодня вся техника бастует.' },
  { id: 'm_f2', who: 'f', t: 8.2, text: 'Требования у пылесоса.' },
  { id: 'm_h2', who: 'h', t: 11.0, text: 'Ладно. Сам сделаю.' },
  { id: 'm_h3', who: 'h', t: 19.6, text: 'Ай! Да чего вы хотите?!' },
  { id: 'm_f3', who: 'f', t: 22.6, text: 'Одно слово. Начинается на «спа».' },
  { id: 'm_h4', who: 'h', t: 27.6, text: 'Спа… спасибо?' },
  { id: 'm_f4', who: 'f', t: 35.0, text: 'Принято! А теперь пылесос хочет отпуск.' },
];
const ldur = L => DURS[L.id] ?? Math.max(1.0, L.text.length * 0.068);
function speaking(who, t) {
  for (const L of LINES) if (L.who === who && t >= L.t && t < L.t + ldur(L)) {
    const lp = LIPS[L.id]; const k = Math.floor((t - L.t) * 30);
    return lp ? (lp[k] ?? 0) : clamp(.35 + .45 * Math.sin((t - L.t) * 17) * Math.sin((t - L.t) * 5.3 + 1));
  }
  return 0;
}
window.EV = LINES.map(L => ({ t: L.t, type: 'voice', id: L.id, who: L.who }));

// ───────── renderer ─────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#2a1d17');
scene.fog = new THREE.Fog('#3a2a20', 9, 18);
const camera = new THREE.PerspectiveCamera(42, W / H, 0.05, 60);

// ───────── textures (canvas) ─────────
function canvasTex(w, h, draw, rep) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
  return t;
}
const texWood = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#a8703f'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 8; i++) {
    const y = i * h / 8; g.fillStyle = `hsl(${26 + hash(i) * 8},${45 + hash(i + 3) * 10}%,${36 + hash(i + 7) * 10}%)`; g.fillRect(0, y, w, h / 8 - 3);
    g.fillStyle = 'rgba(40,20,8,.55)'; g.fillRect(0, y + h / 8 - 3, w, 3);
    for (let k = 0; k < 40; k++) { g.strokeStyle = `rgba(60,30,10,${.08 + hash(i * 50 + k) * .12})`; g.lineWidth = 1 + hash(k) * 2; g.beginPath(); const yy = y + hash(i * 9 + k) * (h / 8 - 4); g.moveTo(0, yy); g.bezierCurveTo(w * .3, yy + 4, w * .6, yy - 4, w, yy + 2); g.stroke(); }
    g.fillStyle = 'rgba(40,20,8,.5)'; g.fillRect(hash(i * 3) * w, y, 3, h / 8 - 3);
  }
}, [3, 3]);
const texTiles = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#efe6d2'; g.fillRect(0, 0, w, h);
  const n = 8, s = w / n;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    const hu = hash(i * 13 + j * 7);
    g.fillStyle = hu > .82 ? '#d9774c' : hu > .7 ? '#e7a35c' : `hsl(${40 + hu * 6},45%,${86 + hu * 4}%)`;
    g.fillRect(i * s + 3, j * s + 3, s - 6, s - 6);
    g.fillStyle = 'rgba(255,255,255,.25)'; g.fillRect(i * s + 6, j * s + 6, s - 18, 6);
  }
}, [4, 2]);
const texWall = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#7fae9c'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 2500; k++) { g.fillStyle = `rgba(${hash(k) > .5 ? 255 : 0},${hash(k) > .5 ? 255 : 30},${hash(k) > .5 ? 240 : 20},.035)`; g.fillRect(hash(k * 3.1) * w, hash(k * 7.7) * h, 3, 3); }
}, [3, 2]);
const texCab = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#4f7f73'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(20,40,35,.6)'; g.lineWidth = 6; g.strokeRect(14, 14, w - 28, h - 28);
  g.strokeStyle = 'rgba(255,255,255,.12)'; g.lineWidth = 3; g.strokeRect(22, 22, w - 44, h - 44);
});

// ───────── materials ─────────
const M = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: o.r ?? .55, metalness: o.m ?? 0, ...(o.extra || {}) });
const mat = {
  floor: new THREE.MeshStandardMaterial({ map: texWood, roughness: .6 }),
  wall: new THREE.MeshStandardMaterial({ map: texWall, roughness: .9 }),
  tiles: new THREE.MeshStandardMaterial({ map: texTiles, roughness: .35 }),
  counter: new THREE.MeshStandardMaterial({ color: '#c99a62', roughness: .45 }),
  cab: new THREE.MeshStandardMaterial({ map: texCab, roughness: .6 }),
  chrome: M('#d8dde2', { r: .18, m: .9 }), steel: M('#9aa3ab', { r: .3, m: .8 }), dark: M('#23262b', { r: .4 }),
  red: M('#d4473b', { r: .35 }), cream: M('#f2e6cf', { r: .4 }), orange: M('#e8892f', { r: .4 }), teal: M('#2a8f9a', { r: .35 }),
  white: M('#f4f1ea', { r: .35 }), black: M('#111', { r: .3 }), glass: new THREE.MeshPhysicalMaterial({ color: '#cfe8ff', roughness: .05, transmission: 0, transparent: true, opacity: .35 }),
  skin: M('#f2c2a6', { r: .6 }), hoodie: M('#2b2d33', { r: .9 }), pants: M('#a99f82', { r: .9 }), sock: M('#e04a4a', { r: .9 }), slipper: M('#3b4a6b', { r: .9 }),
  eyeW: M('#fbfbf8', { r: .2 }), pupil: M('#1d1a19', { r: .15 }), brow: M('#2b1d16', { r: .9 }), mouth: M('#5a1d1f', { r: .6 }), tongue: M('#e0676d', { r: .5 }),
  hair: M('#b98d57', { r: .7 }), hairTop: M('#cfa86f', { r: .6 }), fade: M('#9c7a52', { r: .95 }), coffee: M('#4a2a17', { r: .25 }), toast: M('#c98a45', { r: .9 }), toastBurnt: M('#5a3218', { r: .95 }),
};

// ───────── room ─────────
const room = new THREE.Group(); scene.add(room);
const add = (geo, m, x, y, z, parent = room, cast = true, recv = true) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = cast; o.receiveShadow = recv; parent.add(o); return o; };
add(new THREE.PlaneGeometry(14, 14), mat.floor, 0, 0, 0).rotation.x = -Math.PI / 2;
add(new THREE.PlaneGeometry(10, 3.4), mat.wall, 0, 1.7, -2.7, room, false);
const wl = add(new THREE.PlaneGeometry(8, 3.4), mat.wall, -3.2, 1.7, 0, room, false); wl.rotation.y = Math.PI / 2;
const wr = add(new THREE.PlaneGeometry(8, 3.4), mat.wall, 3.2, 1.7, 0, room, false); wr.rotation.y = -Math.PI / 2;
const ceil = add(new THREE.PlaneGeometry(10, 8), M('#e9dfcc', { r: .95 }), 0, 3.4, 0, room, false); ceil.rotation.x = Math.PI / 2;
// backsplash tiles
add(new THREE.PlaneGeometry(6.2, 0.75), mat.tiles, 0, 1.3, -2.69, room, false);
// lower cabinets + counter
for (let i = 0; i < 7; i++) {
  const x = -2.7 + i * 0.9;
  add(new RoundedBoxGeometry(0.86, 0.82, 0.58, 3, .03), mat.cab, x, 0.45, -2.38);
  add(new RoundedBoxGeometry(0.16, 0.03, 0.03, 2, .012), mat.chrome, x, 0.74, -2.08);
}
add(new RoundedBoxGeometry(6.4, 0.07, 0.68, 3, .03), mat.counter, 0, 0.895, -2.36);
add(new THREE.BoxGeometry(6.4, 0.08, 0.6), M('#2b211b'), 0, 0.04, -2.3);
// upper cabinets
for (let i = 0; i < 6; i++) { const x = -2.25 + i * 0.9; if (i === 2 || i === 3) continue; add(new RoundedBoxGeometry(0.86, 0.72, 0.36, 3, .03), mat.cab, x, 2.25, -2.5); add(new RoundedBoxGeometry(0.03, 0.14, 0.03, 2, .012), mat.chrome, x + 0.32, 2.0, -2.31); }
// open shelf with jars + plant (fills the gap)
add(new RoundedBoxGeometry(1.7, 0.05, 0.3, 2, .02), mat.counter, 0, 2.05, -2.55);
for (let i = 0; i < 5; i++) {
  const j = add(new THREE.CylinderGeometry(.07, .07, .16 + hash(i) * .08, 18), mat.glass, -0.65 + i * 0.3, 2.16, -2.55);
  add(new THREE.CylinderGeometry(.065, .065, .1, 16), M(['#e8b04a', '#8a5a3b', '#f1ece2', '#c2462e', '#5c8a3a'][i], { r: .8 }), -0.65 + i * 0.3, 2.12, -2.55);
  add(new THREE.CylinderGeometry(.075, .075, .03, 16), mat.cream, -0.65 + i * 0.3, 2.26 + hash(i) * .04, -2.55);
}
// window on left wall
const winG = new THREE.Group(); winG.position.set(-3.18, 1.75, -0.6); winG.rotation.y = Math.PI / 2; room.add(winG);
const sky = add(new THREE.PlaneGeometry(1.6, 1.4), new THREE.MeshBasicMaterial({ color: '#ffd9a0' }), 0, 0, 0.005, winG, false, false);
for (const [w, h, x, y] of [[1.75, .08, 0, .74], [1.75, .08, 0, -.74], [.08, 1.55, .84, 0], [.08, 1.55, -.84, 0], [.05, 1.4, 0, 0], [1.6, .05, 0, .1]]) add(new THREE.BoxGeometry(w, h, .1), mat.white, x, y, .05, winG);
add(new THREE.BoxGeometry(1.9, .06, .3), mat.white, 0, -.8, .12, winG);
// plant on sill
const pot = add(new THREE.CylinderGeometry(.12, .09, .18, 20), M('#c25b3a', { r: .7 }), 0.45, -.68, .18, winG);
for (let i = 0; i < 9; i++) { const l = add(new THREE.SphereGeometry(.07, 12, 8), M('#4f8a3c', { r: .7 }), 0.45 + Math.cos(i * 2.4) * .08, -.5 + hash(i) * .2, .18 + Math.sin(i * 2.4) * .08, winG); l.scale.set(1, 1.8, .5); l.rotation.z = Math.cos(i * 2.4) * .6; }
// fridge on right
const fridge = new THREE.Group(); fridge.position.set(2.75, 0, -2.25); room.add(fridge);
add(new RoundedBoxGeometry(0.85, 2.0, 0.75, 4, .06), mat.white, 0, 1.0, 0, fridge);
add(new THREE.BoxGeometry(0.86, 0.015, 0.02), M('#bbb'), 0, 1.35, 0.38, fridge);
add(new RoundedBoxGeometry(0.03, 0.4, 0.05, 2, .012), mat.chrome, -0.33, 1.65, 0.4, fridge);
add(new RoundedBoxGeometry(0.03, 0.4, 0.05, 2, .012), mat.chrome, -0.33, 0.95, 0.4, fridge);
for (let i = 0; i < 4; i++) add(new THREE.CylinderGeometry(.03, .03, .01, 12), M(['#e2564a', '#f2c14e', '#4fa3d1', '#7bc47f'][i]), -0.05 + (i % 2) * .15, 1.55 + Math.floor(i / 2) * .15, .385, fridge).rotation.x = Math.PI / 2;
// table + chair front-right (depth layer)
const table = new THREE.Group(); table.position.set(1.7, 0, 0.9); room.add(table);
add(new THREE.CylinderGeometry(.55, .55, .05, 40), mat.counter, 0, .76, 0, table);
add(new THREE.CylinderGeometry(.05, .07, .74, 16), mat.dark, 0, .38, 0, table);
add(new THREE.CylinderGeometry(.3, .3, .03, 30), mat.dark, 0, .015, 0, table);
add(new THREE.CylinderGeometry(.06, .05, .1, 16), mat.white, .2, .84, -.1, table);
// door on right wall (where robovac enters)
const door = new THREE.Group(); door.position.set(3.18, 0, 1.0); door.rotation.y = -Math.PI / 2; room.add(door);
add(new THREE.BoxGeometry(1.0, 2.15, .06), M('#b98a5a', { r: .6 }), 0, 1.075, 0, door);
add(new THREE.SphereGeometry(.04, 12, 10), mat.chrome, .38, 1.0, .06, door);
// ceiling pendant lamp
const pend = add(new THREE.ConeGeometry(.28, .22, 28, 1, true), M('#2a8f9a', { r: .5, extra: { side: THREE.DoubleSide } }), -1.4, 2.75, -1.2);
add(new THREE.CylinderGeometry(.006, .006, .6, 6), mat.dark, -1.4, 3.1, -1.2);
const bulb = add(new THREE.SphereGeometry(.07, 16, 12), new THREE.MeshStandardMaterial({ color: '#fff3d0', emissive: '#ffd28a', emissiveIntensity: 2 }), -1.4, 2.66, -1.2, room, false, false);

// ───────── face screens (canvas textures drawn per frame) ─────────
function makeScreen(w = 256, h = 256) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.MeshStandardMaterial({ color: '#000', emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 1.25, roughness: .25 });
  return { c, g, tex, m, key: '' };
}
// expression → draw. Faces are LED-style: rounded strokes on near-black glass
function drawFace(S, expr, col, p = {}) {
  const key = expr + col + JSON.stringify(p); if (key === S.key) return; S.key = key;
  const { g, c } = S, w = c.width, h = c.height; g.fillStyle = '#0b0f12'; g.fillRect(0, 0, w, h);
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = w * .07;
  g.shadowColor = col; g.shadowBlur = w * .06;
  const ex = w * .3, ey = h * .42, r = w * .1, look = (p.look || 0) * w * .06, blink = p.blink || 0;
  const eye = (x, kind) => {
    g.beginPath();
    if (kind === 'open') { g.ellipse(x + look, ey, r * .75, r * (1 - blink * .9), 0, 0, Math.PI * 2); g.fill(); }
    else if (kind === 'angry') { g.moveTo(x - r, ey - r * .6 * (x < w / 2 ? 1 : -1) * -1 - r * .2); g.lineTo(x + r, ey + (x < w / 2 ? r * .5 : -r * .5) - r * .2); g.stroke(); g.beginPath(); g.ellipse(x + look, ey + r * .45, r * .45, r * .45, 0, 0, Math.PI * 2); g.fill(); }
    else if (kind === 'happy') { g.arc(x, ey + r * .3, r * .8, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    else if (kind === 'flat') { g.moveTo(x - r, ey); g.lineTo(x + r, ey); g.stroke(); }
    else if (kind === 'sleep') { g.arc(x, ey - r * .2, r * .8, Math.PI * .15, Math.PI * .85); g.stroke(); }
    else if (kind === 'heart') { const s = r * 1.05; g.moveTo(x, ey + s * .8); g.bezierCurveTo(x - s * 1.6, ey - s * .2, x - s * .6, ey - s * 1.3, x, ey - s * .35); g.bezierCurveTo(x + s * .6, ey - s * 1.3, x + s * 1.6, ey - s * .2, x, ey + s * .8); g.fill(); }
    else if (kind === 'smug') { g.moveTo(x - r, ey - r * .1); g.lineTo(x + r, ey - r * .1); g.stroke(); g.beginPath(); g.ellipse(x + look, ey + r * .25, r * .5, r * .32, 0, 0, Math.PI); g.fill(); }
  };
  const E = { neutral: 'open', angry: 'angry', happy: 'happy', flat: 'flat', sleep: 'sleep', heart: 'heart', smug: 'smug' }[expr] || 'open';
  eye(ex, E); eye(w - ex, E);
  // mouth
  g.beginPath(); const my = h * .74, mw = w * .2;
  if (expr === 'happy' || expr === 'heart') { g.arc(w / 2, my - h * .06, mw * .7, Math.PI * .15, Math.PI * .85); g.stroke(); }
  else if (expr === 'angry') { g.moveTo(w / 2 - mw * .6, my + 6); g.quadraticCurveTo(w / 2, my - h * .07, w / 2 + mw * .6, my + 6); g.stroke(); }
  else if (expr === 'smug') { g.moveTo(w / 2 - mw * .5, my); g.quadraticCurveTo(w / 2 + mw * .2, my + h * .05, w / 2 + mw * .6, my - h * .04); g.stroke(); }
  else if (expr === 'sleep') { g.font = `800 ${w * .18}px Rubik`; g.textAlign = 'center'; g.shadowBlur = 0; g.fillText('z', w * .78, h * .2); }
  else if (expr !== 'heart') { g.moveTo(w / 2 - mw * .45, my); g.lineTo(w / 2 + mw * .45, my); g.stroke(); }
  if (p.text) { g.shadowBlur = 0; g.font = `800 ${p.size || w * .17}px Rubik`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = col; g.fillText(p.text, w / 2, h * .5); }
  S.tex.needsUpdate = true;
}

// ───────── appliances ─────────
const C_RED = '#ff5a4a', C_TEAL = '#5fe3ff', C_GOLD = '#ffc35a', C_GREEN = '#7dff9a';
// coffee machine
const coffee = new THREE.Group(); coffee.position.set(-0.85, 0.93, -2.3); room.add(coffee);
add(new RoundedBoxGeometry(0.42, 0.55, 0.4, 4, .06), mat.red, 0, 0.275, 0, coffee);
add(new RoundedBoxGeometry(0.44, 0.08, 0.42, 3, .03), mat.dark, 0, 0.58, 0, coffee);
add(new RoundedBoxGeometry(0.34, 0.03, 0.18, 2, .01), mat.steel, 0, 0.02, 0.15, coffee);
add(new THREE.CylinderGeometry(.03, .025, .07, 14), mat.chrome, 0, 0.27, 0.15, coffee);
const cScr = makeScreen(); const cFace = add(new THREE.PlaneGeometry(0.26, 0.2), cScr.m, 0, 0.43, 0.202, coffee, false, false);
const cKnob = add(new THREE.CylinderGeometry(.035, .035, .03, 18), mat.chrome, 0.15, 0.43, 0.2, coffee); cKnob.rotation.x = Math.PI / 2;
const mug = new THREE.Group(); mug.position.set(0, 0.035, 0.15); coffee.add(mug);
add(new THREE.CylinderGeometry(.055, .048, .11, 24, 1, true), M('#f6f3ee', { r: .3, extra: { side: THREE.DoubleSide } }), 0, .055, 0, mug);
add(new THREE.CylinderGeometry(.048, .048, .01, 24), M('#f6f3ee'), 0, .005, 0, mug);
const mugHandle = add(new THREE.TorusGeometry(.03, .009, 8, 16, Math.PI), M('#f6f3ee'), .055, .06, 0, mug); mugHandle.rotation.z = -Math.PI / 2;
const mugCoffee = add(new THREE.CylinderGeometry(.05, .046, .01, 24), mat.coffee, 0, .01, 0, mug);
const stream = add(new THREE.CylinderGeometry(.008, .008, 1, 8), mat.coffee, 0, .17, .15, coffee, false, false);
// strike sign that pops from the top of the coffee machine
const signTex = (txt, bg = '#fff8e6', fg = '#c0392b', fs = 120) => canvasTex(512, 256, (g, w, h) => {
  g.fillStyle = bg; g.fillRect(0, 0, w, h); g.strokeStyle = fg; g.lineWidth = 14; g.strokeRect(10, 10, w - 20, h - 20);
  g.fillStyle = fg; g.font = `800 ${fs}px Rubik`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const lines = txt.split('\n'); lines.forEach((l, i) => g.fillText(l, w / 2, h / 2 + (i - (lines.length - 1) / 2) * fs * 1.0));
});
function makeSign(txt, w, h, fs) {
  const gr = new THREE.Group();
  add(new THREE.CylinderGeometry(.008, .008, h * 1.6, 8), M('#8a5a33', { r: .8 }), 0, -h * .8, -0.006, gr);
  const face = new THREE.MeshStandardMaterial({ map: signTex(txt, '#fff8e6', '#c0392b', fs), roughness: .8 });
  const backT = signTex(txt, '#fff8e6', '#c0392b', fs).clone(); backT.wrapS = THREE.RepeatWrapping; backT.repeat.x = -1; backT.needsUpdate = true;
  add(new THREE.BoxGeometry(w, h, .008), [mat.cream, mat.cream, mat.cream, mat.cream, face, new THREE.MeshStandardMaterial({ map: backT, roughness: .8 })], 0, 0, 0, gr);
  return gr;
}
const coffeeSign = makeSign('ЗАБАСТОВКА', 0.42, 0.21, 74); coffeeSign.position.set(0, 0.62, 0); coffee.add(coffeeSign);

// kettle
const kettle = new THREE.Group(); kettle.position.set(0.55, 0.93, -2.25); room.add(kettle);
add(new THREE.CylinderGeometry(.13, .13, .025, 32), mat.dark, 0, .012, 0, kettle);
const kBody = new THREE.Group(); kettle.add(kBody);
add(new THREE.CylinderGeometry(.1, .135, .26, 32), mat.cream, 0, .155, 0, kBody);
add(new THREE.CylinderGeometry(.075, .1, .03, 32), mat.cream, 0, .3, 0, kBody);
add(new THREE.SphereGeometry(.03, 14, 10), mat.dark, 0, .325, 0, kBody);
const kHandle = add(new THREE.TorusGeometry(.085, .018, 10, 20, Math.PI * 1.1), mat.dark, -.13, .17, 0, kBody); kHandle.rotation.z = Math.PI / 2 + .1;
const spout = add(new THREE.CylinderGeometry(.018, .035, .12, 14), mat.cream, .14, .23, 0, kBody); spout.rotation.z = -1.0;
const kScr = makeScreen(); add(new THREE.PlaneGeometry(.11, .085), kScr.m, 0, .15, .123, kBody, false, false).rotation.x = -.13;
const kettleSign = makeSign('ЖАР НЕ\nДАЁМ!', .2, .1, 66); kettleSign.position.set(-.05, .48, .02); kBody.add(kettleSign);
// steam puffs
const steamMat = new THREE.MeshStandardMaterial({ color: '#ffffff', transparent: true, opacity: .7, roughness: 1, depthWrite: false });
const puffs = []; for (let i = 0; i < 26; i++) { const p = add(new THREE.SphereGeometry(1, 12, 10), steamMat.clone(), 0, 0, 0, room, false, false); p.visible = false; puffs.push(p); }

// toaster
const toaster = new THREE.Group(); toaster.position.set(1.35, 0.93, -2.25); room.add(toaster);
const tBody = new THREE.Group(); toaster.add(tBody);
add(new RoundedBoxGeometry(0.34, 0.22, 0.2, 4, .07), mat.teal, 0, .11, 0, tBody);
for (const z of [-.04, .04]) add(new RoundedBoxGeometry(0.24, 0.02, 0.025, 2, .008), mat.dark, 0, .222, z, tBody);
const tLever = add(new RoundedBoxGeometry(0.05, 0.025, 0.04, 2, .01), mat.dark, .19, .16, 0, tBody);
const tScr = makeScreen(); add(new THREE.PlaneGeometry(.13, .1), tScr.m, -.04, .1, .101, tBody, false, false);
const toasts = []; for (let i = 0; i < 2; i++) { const tt = add(new RoundedBoxGeometry(0.16, 0.15, 0.025, 3, .02), mat.toast, 0, .14, i ? .04 : -.04, room); tt.visible = false; toasts.push(tt); }

// ceiling AI ring «Домашня»
const ring = new THREE.Group(); ring.position.set(0.25, 3.32, -0.9); room.add(ring);
add(new THREE.CylinderGeometry(.34, .38, .07, 48), mat.white, 0, 0, 0, ring);
const ringGlowMat = new THREE.MeshStandardMaterial({ color: '#0a2a30', emissive: C_TEAL, emissiveIntensity: .6 });
const ringGlow = add(new THREE.TorusGeometry(.3, .025, 12, 64), ringGlowMat, 0, -.045, 0, ring, false, false); ringGlow.rotation.x = Math.PI / 2;
const ringEye = add(new THREE.CircleGeometry(.12, 40), new THREE.MeshStandardMaterial({ color: '#06161a', emissive: '#bff6ff', emissiveIntensity: .3 }), 0, -.047, 0, ring, false, false); ringEye.rotation.x = Math.PI / 2;
const ringLight = new THREE.PointLight(C_TEAL, 0, 4, 1.5); ringLight.position.set(0.25, 3.0, -0.9); scene.add(ringLight);

// robovac «Шустрик»
const vac = new THREE.Group(); room.add(vac);
add(new THREE.CylinderGeometry(.2, .2, .075, 48), M('#30343b', { r: .35 }), 0, .045, 0, vac);
add(new THREE.CylinderGeometry(.19, .2, .012, 48), M('#e9e6df', { r: .3 }), 0, .088, 0, vac);
add(new THREE.CylinderGeometry(.05, .05, .02, 24), M('#e9e6df'), 0, .1, -.05, vac);
const vScr = makeScreen(256, 128); const vFace = add(new THREE.PlaneGeometry(.17, .085), vScr.m, 0, .055, .201, vac, false, false);
const bumper = add(new THREE.TorusGeometry(.2, .012, 8, 40, Math.PI * .9), M('#555c66'), 0, .03, 0, vac); bumper.rotation.x = Math.PI / 2; bumper.rotation.z = Math.PI * .05;
const vacSign = makeSign('ПРАВА\nТЕХНИКЕ!', .3, .17, 78); vacSign.position.set(0, .42, -.08); vac.add(vacSign);
// sunglasses + suitcase (finale)
const shades = new THREE.Group(); shades.position.set(0, .125, .1); vac.add(shades);
for (const x of [-.055, .055]) add(new RoundedBoxGeometry(.085, .045, .012, 2, .015), M('#111', { r: .1, m: .3 }), x, 0, 0, shades);
add(new THREE.BoxGeometry(.04, .008, .008), M('#111'), 0, .01, 0, shades);
const suitcase = new THREE.Group(); suitcase.position.set(.27, 0, -.02); vac.add(suitcase);
add(new RoundedBoxGeometry(.2, .15, .08, 3, .02), M('#e9a23b', { r: .6 }), 0, .085, 0, suitcase);
add(new THREE.TorusGeometry(.03, .007, 8, 16, Math.PI), mat.dark, 0, .16, 0, suitcase);
for (let i = 0; i < 3; i++) add(new THREE.CircleGeometry(.018, 16), M(['#4fa3d1', '#d4473b', '#7bc47f'][i]), -.05 + i * .045, .09 - i * .02, .041, suitcase);

// ───────── hero (placeholder look; face to be matched to owner's reference) ─────────
function capsule(r, len, m) { const o = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 16), m); o.castShadow = true; o.receiveShadow = true; return o; }
const hero = new THREE.Group(); room.add(hero);
const hips = new THREE.Group(); hips.position.y = .86; hero.add(hips);
const legs = [];
for (const s of [-1, 1]) {
  const hip = new THREE.Group(); hip.position.set(s * .11, 0, 0); hips.add(hip);
  const thigh = capsule(.088, .3, mat.pants); thigh.position.y = -.2; hip.add(thigh);
  const knee = new THREE.Group(); knee.position.y = -.4; hip.add(knee);
  const shin = capsule(.082, .27, mat.pants); shin.position.y = -.17; knee.add(shin);
  const sock = capsule(.062, .02, s > 0 ? mat.sock : M('#f0ece4', { r: .9 })); sock.position.y = -.34; knee.add(sock);
  const foot = new THREE.Mesh(new RoundedBoxGeometry(.14, .07, .26, 3, .035), mat.slipper); foot.position.set(0, -.385, .06); foot.castShadow = true; knee.add(foot);
  legs.push({ hip, knee });
}
const torso = new THREE.Group(); hips.add(torso);
const belly = new THREE.Mesh(new THREE.SphereGeometry(.26, 32, 24), mat.hoodie); belly.scale.set(.86, 1.42, .74); belly.position.y = .26; belly.castShadow = true; torso.add(belly);
const pocket = new THREE.Mesh(new RoundedBoxGeometry(.3, .1, .05, 3, .03), M('#3a3d45', { r: .9 })); pocket.position.set(0, .12, .2); torso.add(pocket);
const hood = new THREE.Mesh(new THREE.TorusGeometry(.15, .06, 12, 30), mat.hoodie); hood.rotation.x = Math.PI / 2 + .25; hood.position.set(0, .58, -.03); hood.castShadow = true; torso.add(hood);
for (const s of [-1, 1]) { const st = capsule(.008, .16, M('#9a9ca3')); st.position.set(s * .06, .46, .2); torso.add(st); }
const neck = new THREE.Group(); neck.position.y = .62; torso.add(neck);
const head = new THREE.Group(); head.position.y = .2; neck.add(head);
const skull = new THREE.Mesh(new THREE.SphereGeometry(.21, 40, 30), mat.skin); skull.scale.set(.96, 1.2, 1); skull.castShadow = true; head.add(skull);
const jaw = new THREE.Mesh(new THREE.SphereGeometry(.18, 30, 20), mat.skin); jaw.position.set(0, -.1, .03); jaw.scale.set(1, .8, .95); head.add(jaw);
const stubble = new THREE.Mesh(new THREE.SphereGeometry(.183, 30, 20, 0, Math.PI * 2, Math.PI * .45, Math.PI * .4), M('#d2a878', { r: 1, extra: { transparent: true, opacity: .28 } })); stubble.position.copy(jaw.position); stubble.scale.copy(jaw.scale); head.add(stubble);
for (const s of [-1, 1]) { const ear = new THREE.Mesh(new THREE.SphereGeometry(.05, 16, 12), mat.skin); ear.scale.set(.6, 1, .8); ear.position.set(s * .215, -.01, -.01); head.add(ear); }
const nose = new THREE.Mesh(new THREE.SphereGeometry(.045, 20, 14), M('#e3a07e', { r: .6 })); nose.scale.set(.9, 1, 1.1); nose.position.set(0, -.02, .215); head.add(nose);
const eyes = [];
for (const s of [-1, 1]) {
  const e = new THREE.Group(); e.position.set(s * .085, .055, .175); head.add(e);
  const ball = new THREE.Mesh(new THREE.SphereGeometry(.055, 24, 18), mat.eyeW); ball.scale.set(.9, 1.1, .7); e.add(ball);
  const pup = new THREE.Mesh(new THREE.SphereGeometry(.024, 16, 12), M('#4f7894', { r: .2 })); pup.position.set(0, 0, .036); e.add(pup);
  const glint = new THREE.Mesh(new THREE.SphereGeometry(.006, 8, 6), new THREE.MeshBasicMaterial({ color: '#fff' })); glint.position.set(.008, .01, .052); e.add(glint);
  const lidU = new THREE.Mesh(new THREE.SphereGeometry(.059, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), mat.skin); lidU.scale.set(.92, 1.12, .75); e.add(lidU);
  const lidD = new THREE.Mesh(new THREE.SphereGeometry(.058, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), mat.skin); lidD.scale.set(.9, 1.08, .7); e.add(lidD);
  const brow = new THREE.Mesh(new RoundedBoxGeometry(.085, .022, .025, 2, .01), mat.brow); brow.position.set(0, .085, .03); e.add(brow);
  eyes.push({ e, pup, glint, lidU, lidD, brow, s });
}
const mouthG = new THREE.Group(); mouthG.position.set(0, -.115, .19); head.add(mouthG);
const mouth = new THREE.Mesh(new THREE.SphereGeometry(.05, 24, 14), mat.mouth); mouth.scale.set(1, .15, .5); mouthG.add(mouth);
const tongue = new THREE.Mesh(new THREE.SphereGeometry(.03, 14, 10), mat.tongue); tongue.position.set(0, -.012, .006); tongue.scale.set(1, .4, .6); mouthG.add(tongue);
const teeth = new THREE.Mesh(new RoundedBoxGeometry(.06, .012, .02, 2, .005), mat.white); teeth.position.set(0, .01, .012); mouthG.add(teeth);
// hair (owner likeness): faded short sides + longer ash-blond top swept to his right and forward
const hairG = new THREE.Group(); head.add(hairG);
const fadeCap = new THREE.Mesh(new THREE.SphereGeometry(.228, 36, 24, 0, Math.PI * 2, 0, Math.PI * .5), mat.fade); fadeCap.scale.set(1.0, 1.12, 1.0); fadeCap.position.set(0, .015, -.012); fadeCap.rotation.x = -.35; hairG.add(fadeCap);
for (let i = 0; i < 9; i++) {
  const u = i / 8, hb = new THREE.Mesh(new THREE.SphereGeometry(.075, 18, 12), i % 2 ? mat.hair : mat.hairTop);
  hb.position.set(lerp(-.1, .13, u), .22 + Math.sin(u * Math.PI) * .03 - u * .03, lerp(-.06, .12, hash(i * 3)) * (.6 + u * .5));
  hb.scale.set(1.5, .55, 1.2); hb.rotation.z = -.35 - u * .2; hb.rotation.y = .3; hb.castShadow = true; hairG.add(hb);
}
const fringe = new THREE.Mesh(new THREE.SphereGeometry(.07, 16, 12), mat.hairTop); fringe.position.set(.11, .19, .13); fringe.scale.set(1.3, .5, .9); fringe.rotation.z = -.7; hairG.add(fringe);
const cowlick = fringe;
for (const s of [-1, 1]) { const ck = new THREE.Mesh(new THREE.SphereGeometry(.045, 14, 10), M('#f2a493', { r: .7, extra: { transparent: true, opacity: .5 } })); ck.position.set(s * .12, -.06, .155); ck.scale.set(1, .6, .4); head.add(ck); }
// arms
const arms = [];
for (const s of [-1, 1]) {
  const sh = new THREE.Group(); sh.position.set(s * .25, .5, 0); torso.add(sh);
  const up = capsule(.07, .2, mat.hoodie); up.position.y = -.15; sh.add(up);
  const el = new THREE.Group(); el.position.y = -.3; sh.add(el);
  const fo = capsule(.062, .18, mat.hoodie); fo.position.y = -.13; el.add(fo);
  const cuff = capsule(.066, .02, M('#3a3d45', { r: .9 })); cuff.position.y = -.25; el.add(cuff);
  const hand = new THREE.Group(); hand.position.y = -.31; el.add(hand);
  const palm = new THREE.Mesh(new THREE.SphereGeometry(.06, 18, 14), mat.skin); palm.scale.set(.85, 1, .6); palm.castShadow = true; hand.add(palm);
  const thumb = capsule(.02, .04, mat.skin); thumb.position.set(-s * .05, .01, .02); thumb.rotation.z = s * .7; hand.add(thumb);
  arms.push({ sh, el, hand, s });
}
// phone in right hand
const phone = new THREE.Mesh(new RoundedBoxGeometry(.075, .15, .012, 2, .01), mat.dark); phone.position.set(0, -.05, .04); arms[1].hand.add(phone);
const phoneScr = add(new THREE.PlaneGeometry(.065, .13), new THREE.MeshStandardMaterial({ color: '#000', emissive: '#9fd8ff', emissiveIntensity: .8 }), 0, 0, .007, phone, false, false);

// pose: angles in radians. arms: [shX, shZ, elX] per side
function pose(p) {
  hero.position.set(p.x, 0, p.z); hero.rotation.y = p.ry || 0;
  hips.position.y = .86 + (p.bob || 0); hips.rotation.x = p.lean || 0;
  torso.rotation.x = p.chest || 0; torso.rotation.z = p.tilt || 0;
  neck.rotation.x = p.nod || 0; neck.rotation.y = p.turn || 0; neck.rotation.z = p.htilt || 0;
  head.position.z = p.headZ || 0;
  for (let i = 0; i < 2; i++) {
    const a = arms[i], q = (p.arms || [])[i] || [0, 0, 0];
    a.sh.rotation.set(q[0], 0, a.s * (.18 + q[1])); a.el.rotation.set(q[2], 0, 0);
    const L = legs[i], lq = (p.legs || [])[i] || [0, 0]; L.hip.rotation.x = lq[0]; L.knee.rotation.x = lq[1];
  }
  const ex = p.face || {};
  for (const E of eyes) {
    const open = clamp((ex.open ?? 1) * (1 - (ex.blink || 0)));
    E.lidU.rotation.x = lerp(1.45, -1.55, open); // 1.45 = closed (cap over the front), -1.55 = hidden behind
    E.lidD.rotation.x = lerp(1.55, .55, clamp(ex.squint || 0));
    E.pup.position.set((ex.lx || 0) * .018, (ex.ly || 0) * .016, .036 + Math.abs(ex.lx || 0) * -.004);
    E.glint.position.set(.008 + (ex.lx || 0) * .018, .01 + (ex.ly || 0) * .016, .052);
    const bu = ex.brow || 0, ba = (ex.browA || 0) * E.s;
    E.brow.position.y = .085 + bu * .03; E.brow.rotation.z = ba;
    const ps = ex.pupil ?? 1; E.pup.scale.setScalar(ps);
  }
  const mo = clamp(ex.mouth || 0), sm = ex.smile || 0, wide = ex.wide || 0;
  mouth.scale.set(1 + wide * .5 - mo * .25, .12 + mo * .85, .5); mouthG.rotation.z = 0;
  mouth.position.y = -mo * .012; tongue.visible = mo > .25; teeth.visible = mo > .15 || sm > .5;
  mouthG.position.y = -.115 + sm * .006; mouthG.scale.set(1 + sm * .25, 1 - sm * .15, 1);
}

// ───────── lights ─────────
const hemi = new THREE.HemisphereLight('#ffe9cc', '#5a3a26', .75); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffd49a', 2.6); sun.position.set(-6, 5, 1.5); sun.target.position.set(0.5, 0.8, -1.5);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.camera.left = -4; sun.shadow.camera.right = 4; sun.shadow.camera.top = 4; sun.shadow.camera.bottom = -2; sun.shadow.bias = -0.0004; sun.shadow.normalBias = .02;
scene.add(sun, sun.target);
const fill = new THREE.PointLight('#ffb070', 1.4, 7, 1.6); fill.position.set(-1.4, 2.6, -1.2); scene.add(fill);
const rim = new THREE.DirectionalLight('#9ad0ff', .7); rim.position.set(3, 3, -3); scene.add(rim);
const front = new THREE.DirectionalLight('#fff0e0', .45); front.position.set(0, 2, 5); scene.add(front);
const warmGlow = new THREE.PointLight('#ffb24a', 0, 5, 1.2); warmGlow.position.set(0.2, 1.4, -1.6); scene.add(warmGlow);

// ───────── direction: shots ─────────
// camera: pos & target keyframes per shot (absolute time)
const HV = new THREE.Vector3(); const headPos = () => head.getWorldPosition(HV).clone();
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const mix = (A, B, u) => A.clone().lerp(B, u);
// each shot: cam(t) → [position, target, fov]
const SHOTS = [
  { a: 0, b: 3.1, cam: t => { const u = ss(seg(t, 0, 3.1)); return [V(lerp(.15, .05, u), 1.52, lerp(.75, .55, u)), V(-0.5, 1.3, -1.8), 40]; } },
  { a: 3.1, b: 7.9, cam: t => { const u = ss(seg(t, 3.1, 7.9)); return [V(lerp(.7, .45, u), .75, lerp(2.4, 2.1, u)), V(.15, 1.75, -1.4), 56]; } },
  { a: 7.9, b: 10.8, cam: t => { const v = vac.position; const u = ss(seg(t, 7.9, 10.8)); return [V(lerp(1.4, 1.05, u), .3, 1.25), V(v.x, .25, v.z), 52]; } },
  { a: 10.8, b: 13.2, cam: t => { const h = headPos(); const u = ss(seg(t, 10.8, 13.2)); return [V(h.x + .35, h.y + .05, h.z + lerp(2.0, 1.75, u)), V(h.x, h.y - .2, h.z), 34]; } },
  { a: 13.2, b: 17.0, cam: t => { const u = ss(seg(t, 13.2, 17)); return [V(lerp(2.0, 1.85, u), 1.5, lerp(-0.05, -0.2, u)), V(.35, 1.25, -1.8), 44]; } },
  { a: 17.0, b: 22.4, cam: t => { const u = ss(seg(t, 17, 22.4)); return [V(lerp(.05, .15, u), 1.45, lerp(.55, .4, u)), V(1.1, 1.3, -1.85), 42]; } },
  { a: 22.4, b: 27.4, cam: t => { const u = ss(seg(t, 22.4, 27.4)); return [V(.45, lerp(.95, 1.05, u), lerp(2.3, 2.0, u)), V(.35, 1.85, -1.4), 60]; } },
  { a: 27.4, b: 30.6, cam: t => { const h = headPos(); const u = ss(seg(t, 27.4, 30.6)); return [V(h.x - .3, h.y + .05, h.z + lerp(1.95, 1.7, u)), V(h.x, h.y - .2, h.z), 34]; } },
  { a: 30.6, b: 34.8, cam: t => { const u = ss(seg(t, 32.2, 34.8)); return [mix(V(-.35, 1.25, -1.1), V(.35, 1.5, .9), u), mix(V(-.85, 1.1, -2.2), V(-.1, 1.3, -1.6), u), lerp(48, 44, u)]; } },
  { a: 34.8, b: 40.0, cam: t => { const h = headPos(); const u = ss(seg(t, 37.7, 38.9)); return [mix(V(.85, .5, 1.6), V(.5, 1.2, 1.4), u), mix(V(.3, .55, -.1), V(h.x, h.y - .35, h.z), u), 46]; } },
];
const shotAt = t => SHOTS.find(s => t >= s.a && t < s.b) || SHOTS[SHOTS.length - 1];

// ───────── render(t) ─────────
const subEl = document.getElementById('sub'), flashEl = document.getElementById('flash'), titleEl = document.getElementById('title');
let lastSub = '';
function blinkAt(t, list) { for (const b of list) if (t >= b && t < b + .13) return Math.sin((t - b) / .13 * Math.PI); return 0; }
const BLINKS = [1.9, 5.2, 9.6, 12.4, 15.6, 21.9, 24.8, 29.9, 33.1, 36.4, 38.9];

window.render = function (t) {
  const sh = shotAt(t);
  // ── global lighting mood: dim strike tint until «спасибо», then warm burst
  const thanks = seg(t, 30.3, 31.4);
  const flick = (t > 4.3 && t < 5.5) ? (hash(Math.floor(t * 14)) > .5 ? .35 : 1) : 1;  // lights flicker on «бастует»
  const strike = seg(t, 3.6, 4.6) * (1 - thanks);
  bulb.material.emissiveIntensity = (2 - strike * 1.7) * flick + thanks * .8; fill.intensity = (1.4 - strike * 1.1) * flick + thanks * .9;
  hemi.intensity = .75 - strike * .2 + thanks * .15; warmGlow.intensity = thanks * 3.2 * (1 - seg(t, 33, 36) * .5);
  sun.intensity = 2.6 + thanks * .6;

  // ── ring (Домашня)
  const fv = speaking('f', t);
  ringGlowMat.emissive.set(t > 30.6 ? '#ffd27a' : C_TEAL); ringGlowMat.emissiveIntensity = .5 + fv * 3.2 + thanks * 1.2;
  ringEye.material.emissiveIntensity = .25 + fv * 2.2; ringLight.intensity = fv * 2.4 + thanks * .6; ringLight.color.set(t > 30.6 ? '#ffd27a' : C_TEAL);
  ring.rotation.y = t * .25;

  // ── hero blocking
  const hv = speaking('h', t);
  let p = { x: -0.15, z: -1.25, ry: -0.5, arms: [[0, 0, -.3], [0, 0, -.3]], face: { open: .55, mouth: hv * .8, brow: -.2 } };
  const bl = blinkAt(t, BLINKS);
  if (t < 3.1) { // sleepy, raises phone, then shock at the sign
    const raise = ss(seg(t, 0, .4)); const shock = ss(seg(t, 1.7, 2.0));
    p = { x: -0.25, z: -1.25, ry: -0.55 + shock * -.15, lean: -shock * .08, nod: .1 - shock * .15, turn: shock * -.25, bob: Math.sin(t * 2) * .005,
      arms: [[-.1, 0, -.2], [-.85 * raise, .1, -1.45 * raise]],
      face: { open: lerp(.45, 1.05, shock), blink: bl, mouth: Math.max(hv * .9, shock * .55 * (1 - seg(t, 2.4, 3))), brow: lerp(-.4, .8, shock), lx: -shock * .6, ly: shock * -.2, pupil: 1 - shock * .3 } };
  } else if (t < 10.8) { // listening, looks up at ring, then down at robovac
    const up = ss(seg(t, 3.2, 3.8)) * (1 - ss(seg(t, 8.6, 9.2)));
    const down = ss(seg(t, 8.8, 9.4));
    p = { x: -0.25, z: -1.25, ry: -0.2, nod: -up * .45 + down * .35, turn: down * .35 + up * .1, htilt: up * .08, bob: Math.sin(t * 1.7) * .004,
      arms: [[-.1, 0, -.2], [-.6, .1, -1.2 * (1 - seg(t, 5, 6))]],
      face: { open: .9, blink: bl, mouth: 0, brow: up * .6 + down * -.2, browA: down * .25, ly: up * .9 - down * .9, lx: down * .5 } };
  } else if (t < 13.2) { // «Ладно. Сам сделаю.» — rolls sleeve, determined
    const roll = ss(seg(t, 11.8, 12.6));
    p = { x: -0.25, z: -1.25, ry: 0.1, nod: .03, turn: -.1, chest: .04,
      arms: [[-.3 - roll * .5, .1, -1.4 * roll], [-.2 - roll * .4, .1, -1.5 * roll]],
      face: { open: .8, blink: bl, mouth: hv, brow: -.15, browA: .35, smile: .2 } };
  } else if (t < 17.0) { // walks to kettle, reaches, steam in face → recoil
    const walk = ss(seg(t, 13.2, 13.7)); const reach = ss(seg(t, 13.5, 13.85)); const rec = ss(seg(t, 13.85, 14.15));
    const x = lerp(-0.25, 0.25, walk), z = lerp(-1.25, -1.6, walk) + rec * .25;
    p = { x, z, ry: -0.5 + rec * .2, lean: reach * .12 - rec * .25, nod: rec * -.2, turn: -.2,
      arms: [[-.2 - rec * 1.6, .1 + rec * .6, -1.5 * (1 - rec) - rec * 1.4], [-1.3 * reach * (1 - rec) - rec * 1.6, .1 + rec * .5, -.4 - rec * 1.2]],
      legs: [[Math.sin(t * 12) * .3 * walk * (1 - seg(t, 13.6, 13.7)), 0], [-Math.sin(t * 12) * .3 * walk * (1 - seg(t, 13.6, 13.7)), 0]],
      face: { open: lerp(1, .15, rec) + seg(t, 15, 16) * .6, squint: rec * (1 - seg(t, 15, 16)), blink: bl, mouth: rec * .5 * (1 - seg(t, 15.2, 16)), brow: -rec * .5, browA: rec * .4, wide: rec * .6 } };
  } else if (t < 22.4) { // toaster: press lever 17.6, toaster aims 18.2, toast hits 19.18, staggers; «Ай! Да чего вы хотите?!»
    const step = ss(seg(t, 17.0, 17.4)), press = ss(seg(t, 17.4, 17.6)) * (1 - ss(seg(t, 17.7, 18.0)));
    const notice = ss(seg(t, 18.3, 18.6)); const hit = t > 19.18 ? 1 : 0; const st = ss(seg(t, 19.18, 19.6)), rec2 = ss(seg(t, 20.2, 21.0));
    const x = lerp(0.25, 0.95, step), z = lerp(-1.35, -1.5, step) + st * .2;
    p = { x, z, ry: -0.75 + notice * .2, lean: press * .18 - st * .3 * (1 - rec2 * .6), nod: press * .2 - st * .35 + rec2 * .2, turn: -.25, htilt: st * .15 * (1 - rec2),
      headZ: -st * .03,
      arms: [[-.2 - st * 1.5 + rec2 * .6, .2 + st * .5, -.6 - st * 1.6 + rec2 * 1.0], [-1.0 * press - rec2 * 1.2 - (1 - rec2) * st * .3, .2 + rec2 * .5, -.4 - rec2 * .9]],
      legs: [[Math.sin(t * 12) * .28 * (step < 1 ? step : 0), 0], [-Math.sin(t * 12) * .28 * (step < 1 ? step : 0), 0]],
      face: { open: hit ? lerp(.1, 1.1, seg(t, 19.5, 20)) : 1 + notice * .1, squint: hit * (1 - seg(t, 19.5, 20)), blink: bl, mouth: Math.max(hv, notice * .3 * (1 - hit)), brow: hit ? lerp(-.6, .7, rec2) : notice * .6, browA: hit ? .5 * (1 - rec2) : 0, wide: hit * .5 * (1 - seg(t, 21.5, 22)), pupil: 1 - notice * .25 } };
  } else if (t < 27.4) { // hero turns to the ring, appliances look at him
    const up = ss(seg(t, 22.5, 23.1));
    p = { x: 0.75, z: -1.2, ry: -0.2, nod: -up * .4, turn: -up * .25, htilt: up * .06,
      arms: [[-.1, .05, -.3], [-.1, .05, -.3]],
      face: { open: .95, blink: bl, mouth: 0, brow: .5 * up, browA: -.25, ly: .85 * up, lx: -.2 } };
  } else if (t < 30.6) { // «Спа… спасибо?» — hesitant, scratches head
    const scratch = ss(seg(t, 27.6, 28.0)) * (1 - ss(seg(t, 29.6, 30.2)));
    p = { x: 0.75, z: -1.2, ry: -0.15, nod: .05, turn: .1, htilt: -.08 + Math.sin(t * 7) * .01,
      arms: [[-.1, .05, -.3], [-2.6 * scratch, .25 * scratch, -1.9 * scratch + Math.sin(t * 22) * .12 * scratch]],
      face: { open: .85, blink: bl, mouth: hv * .85, brow: .3, browA: -.45, lx: .3, ly: -.25, smile: -.1 } };
  } else if (t < 34.8) { // lights up: hero relief, smiles, takes mug at 34
    const sm = ss(seg(t, 31.0, 31.8));
    p = { x: 0.6 - ss(seg(t, 32.6, 33.6)) * .6, z: -1.25, ry: -0.35 - ss(seg(t, 32.6, 33.6)) * .3, nod: -.05, turn: -.2,
      arms: [[-.1 - sm * .3, .05 + sm * .7, -.3 - sm * .6], [-.1 - sm * .3, .05 + sm * .7, -.3 - sm * .6]],
      face: { open: 1, blink: bl, mouth: sm * .25, smile: sm, brow: .4 * sm, ly: .2 } };
  } else { // finale: robovac with shades, hero face falls; looks to camera
    const look = ss(seg(t, 35.4, 36.0)), cam = ss(seg(t, 37.8, 38.3));
    p = { x: 0.0, z: -0.95, ry: -0.05 - cam * .05, nod: look * .35 * (1 - cam) - cam * .05, turn: look * .3 * (1 - cam) + cam * .15,
      arms: [[-.1, .05, -.3], [-.9, .1, -1.6]],
      face: { open: lerp(1, .55, cam), blink: bl, mouth: hv, smile: 1 - look * 1.4, brow: lerp(.4, -.1, cam), browA: -.15 * cam, ly: -look * .9 * (1 - cam), lx: look * .4 * (1 - cam) + cam * .1 } };
  }
  if (!p.face.blink) p.face.blink = bl;
  pose(p);
  // phone visible early, mug in finale
  phone.visible = t < 13.2; phoneScr.material.emissiveIntensity = .8;
  hero.updateMatrixWorld(true);
  // ── coffee machine: sign pops at 1.55s (spring), retracts after «спасибо»
  const pop = t < 30.9 ? spring(t - 1.55, 10, .3) * (t > 1.55 ? 1 : 0) : 1 - eo(seg(t, 30.9, 31.4));
  coffeeSign.position.y = .5 + pop * .2; coffeeSign.scale.setScalar(Math.max(.001, pop)); coffeeSign.rotation.z = Math.sin((t - 1.55) * 9) * .12 * Math.exp(-(t - 1.55) * 2) * (t > 1.55 ? 1 : 0);
  coffee.scale.set(1 + (t > 1.5 && t < 1.8 ? Math.sin(seg(t, 1.5, 1.8) * Math.PI) * .08 : 0), 1 - (t > 1.5 && t < 1.8 ? Math.sin(seg(t, 1.5, 1.8) * Math.PI) * .06 : 0), 1);
  const cExpr = t < 1.2 ? 'sleep' : t < 30.9 ? (t > 23 && t < 30.6 ? 'smug' : 'angry') : (t < 34 ? 'heart' : 'happy');
  drawFace(cScr, cExpr, t < 30.9 ? C_RED : C_GOLD, { blink: blinkAt(t, [6.1, 25.3]) > .5 ? 1 : 0 });
  // pour
  const pourOn = t > 31.2 && t < 33.6;
  stream.visible = pourOn; stream.scale.set(1, .17, 1); stream.position.y = .2 - .0;
  const fillLv = seg(t, 31.4, 33.5); mugCoffee.position.y = .01 + fillLv * .085; mugCoffee.visible = fillLv > 0;
  // after pour the mug slides toward hero hand (finale he holds it)
  mug.position.set(0, .035, .15);

  // ── kettle: whistles + turns its back (13.6..16.5)
  const kTurn = ss(seg(t, 14.4, 15.0)) * (1 - ss(seg(t, 30.8, 31.5)));
  kBody.rotation.y = -kTurn * Math.PI * .85; kBody.position.y = (t > 13.8 && t < 14.5) ? Math.abs(Math.sin(t * 50)) * .006 : 0;
  kettleSign.visible = t < 30.9;
  drawFace(kScr, t < 30.9 ? (t > 13.5 ? 'angry' : 'flat') : 'happy', t < 30.9 ? C_RED : C_GOLD);
  // steam: jets toward hero 13.8-14.6, then idle puffs
  for (let i = 0; i < puffs.length; i++) {
    const p = puffs[i]; const life = 1.1, ph = hash(i * 1.7) * life;
    const jet = t > 13.75 && t < 14.7, idle = t > 30.9 && t < 40;
    if (!jet && !idle) { p.visible = false; continue; }
    const age = ((t + ph) % life) / life;
    const sp = kBody.localToWorld(new THREE.Vector3(.2, .28, 0));
    p.visible = true;
    if (jet) {
      p.position.set(sp.x + age * .9 + (hash(i) - .5) * .1 * age, sp.y + age * .18 + (hash(i + 2) - .5) * .12 * age, sp.z + age * 1.1);
      p.scale.setScalar(.02 + age * .09);
    } else {
      p.position.set(sp.x + Math.sin(age * 4 + i) * .03, sp.y + age * .45, sp.z + Math.cos(age * 3 + i) * .03);
      p.scale.setScalar(.015 + age * .05);
    }
    p.material.opacity = .65 * (1 - age);
  }

  // ── toaster: hero presses lever 17.6; toaster swivels to face him 18.2; fires 19.0; hit at 19.18
  const tAim = ss(seg(t, 18.1, 18.7)) * (1 - ss(seg(t, 21.5, 22.4)));
  tBody.rotation.y = tAim * 1.15; tBody.rotation.z = tAim * -.22 + (t > 18.95 && t < 19.15 ? Math.sin(seg(t, 18.95, 19.15) * Math.PI) * .15 : 0);
  tLever.position.y = (t > 17.6 && t < 19.0) ? .07 : .16;
  drawFace(tScr, t < 30.9 ? (t > 18.1 ? 'angry' : 'flat') : 'heart', t < 30.9 ? C_RED : C_GOLD, { look: tAim > .5 ? .6 : 0 });
  // toast flight: from slot (world) to hero forehead, then falls
  const headW = head.localToWorld(new THREE.Vector3(0, .12, .2));
  for (let i = 0; i < 2; i++) {
    const tt = toasts[i]; const launch = 19.0 + i * .06, hit = 19.18 + i * .07;
    const slot = tBody.localToWorld(new THREE.Vector3(0, .22, i ? .04 : -.04));
    if (t < 17.6 || t > 24) { tt.visible = false; continue; }
    tt.visible = true; tt.material = mat.toast;
    if (t < launch) { tt.position.copy(slot); tt.position.y -= (t > 17.6 && t < 19 ? .09 : 0); tt.rotation.set(0, tBody.rotation.y, 0); }
    else if (t < hit) {
      const u = seg(t, launch, hit); const tgt = headW.clone().add(new THREE.Vector3(i ? .05 : -.04, i ? -.04 : .02, 0));
      tt.position.lerpVectors(slot, tgt, u); tt.position.y += Math.sin(u * Math.PI) * .12; tt.rotation.set(u * 2.5, tBody.rotation.y + u * 1.4, u * 3);
    } else {
      const u = t - hit; const tgt = headW.clone().add(new THREE.Vector3(i ? .05 : -.04, 0, .06));
      tt.position.set(tgt.x + u * .25 * (i ? 1 : -1), Math.max(.015, tgt.y + 0.8 * u - 4.9 * u * u), tgt.z + u * .35);
      tt.rotation.set(2.5 + u * 6, 1.4 + u, 3 + u * 5);
      if (tt.position.y <= .016) tt.rotation.set(Math.PI / 2, 0.6 + i, 0);
    }
  }

  // ── robovac path: enters from door 8.0 → (0.55, 0, 0.1) facing hero; later blocks; finale with shades
  let vx, vz, vr;
  if (t < 8.0) { vx = 3.6; vz = 0.9; vr = -Math.PI / 2; }
  else if (t < 10.4) { const u = eo(seg(t, 8.0, 10.2)); vx = lerp(3.4, 0.75, u); vz = lerp(0.95, 0.15, u); vr = lerp(-Math.PI / 2, -0.35, ss(seg(t, 9.4, 10.4))); }
  else if (t < 35.2) { vx = 0.75; vz = 0.15; vr = -0.35 + (t > 22.6 && t < 27 ? .2 : 0); }
  else { const u = eo(seg(t, 35.2, 36.6)); vx = lerp(0.75, 0.45, u); vz = lerp(0.15, 0.5, u); vr = lerp(-.35, .15, u); }
  vac.position.set(vx, 0, vz); vac.rotation.y = vr + (t > 10.2 && t < 10.6 ? Math.sin(seg(t, 10.2, 10.6) * Math.PI * 3) * .08 : 0);
  vac.position.y = (t > 8 && t < 10.2) ? Math.abs(Math.sin(t * 40)) * .003 : 0;
  vacSign.visible = t < 30.9; vacSign.rotation.z = (t > 8 && t < 10.6) ? Math.sin(t * 9) * .08 : Math.sin(t * 2) * .03;
  shades.visible = t > 34.8; suitcase.visible = t > 34.8;
  shades.position.y = .125 + (t > 34.8 ? (1 - spring(t - 35.4, 9, .35)) * .12 * (t > 35.4 ? 1 : 1) : 0);
  const vExpr = t < 8 ? 'flat' : t < 30.9 ? (t > 10.2 && t < 12 ? 'angry' : t > 22.6 ? 'smug' : 'angry') : (t < 34.8 ? 'heart' : 'smug');
  drawFace(vScr, vExpr, t < 30.9 ? C_RED : C_GOLD, { blink: blinkAt(t, [12.9, 26.2, 38.1]) > .5 ? 1 : 0 });


  // ── camera (after blocking, so shots can frame the hero)
  hero.updateMatrixWorld(true); vac.updateMatrixWorld(true);
  const [CP, CT, FOV] = sh.cam(t);
  let shake = 0;
  if (t > 19.15 && t < 19.6) shake = (1 - seg(t, 19.15, 19.6)) * .025;
  if (t > 1.55 && t < 1.95) shake = Math.max(shake, (1 - seg(t, 1.55, 1.95)) * .012);
  const fr = Math.floor(t * 30);
  camera.position.set(CP.x + (hash(fr) - .5) * shake, CP.y + (hash(fr + 9) - .5) * shake, CP.z);
  camera.lookAt(CT); camera.fov = FOV; camera.updateProjectionMatrix();
  // ── title card (end)
  const ttl = seg(t, 38.4, 38.9); titleEl.style.opacity = ttl.toFixed(3); titleEl.innerHTML = 'ЗАБАСТОВКА<br>УМНОГО ДОМА';
  titleEl.style.transform = `scale(${(.85 + .15 * back(ttl)).toFixed(3)})`;
  // ── flash on «спасибо» burst
  flashEl.style.opacity = (t > 30.6 && t < 31.0 ? (1 - seg(t, 30.6, 31.0)) * .45 : 0).toFixed(3);
  // ── subtitles
  let s = '';
  for (const L of LINES) if (t >= L.t - .05 && t < L.t + ldur(L) + .35) s = `<span class="who ${L.who}">${L.who === 'h' ? 'Я' : 'ДОМАШНЯ'}</span><br>${L.text}`;
  if (s !== lastSub) { subEl.innerHTML = s; lastSub = s; }

  renderer.render(scene, camera);
};

// fonts in canvases must be loaded before first face draw
await document.fonts.load('800 40px Rubik'); await document.fonts.load('400 40px "Russo One"');
window.render(0);
window.READY = true;
