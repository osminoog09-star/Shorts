// «Дикая природа: пылесос» — Shorts S9-D3, Three.js, deterministic render(t). Original scene (Claude, 06.11.2026).
// Kit (room textures, robovac/kettle look, LED faces) reused from longform/smart-strike/mini.
import * as THREE from 'three';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';

const W = 1080, H = 1920;
export const DUR = 38.5;
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
function K(keys, t) { // [[t, v|[...]]…] smoothstep between keys
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [a, va] = keys[i], [b, vb] = keys[i + 1];
    if (t <= b) { const u = ss((t - a) / (b - a)); return Array.isArray(va) ? va.map((x, j) => lerp(x, vb[j], u)) : lerp(va, vb, u); }
  }
  return keys[keys.length - 1][1];
}
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ───────── narration (Denis) ─────────
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const DURS = (await J('voices/dur.json')) || {};
const LINES = [
  { id: 'v1', t: 0.2, text: 'Впервые в истории: робот-пылесос <b>на охоте</b>.' },
  { id: 'v2', t: 3.55, text: 'Он замечает добычу. Одинокий <b>носок</b>. Отбился от пары.' },
  { id: 'v3', t: 9.85, text: '<b>Бросок!</b> Хватка мёртвая.' },
  { id: 'v4', t: 13.3, text: 'Но у носка есть <b>хозяин</b>.' },
  { id: 'v5', t: 18.2, text: 'Охотник зовёт стаю. <b>Колонка. Чайник.</b>' },
  { id: 'v6', t: 23.9, text: '<b>Хищник</b> выходит из тени.' },
  { id: 'v7', t: 29.3, text: 'Ну всё. П**дец <b>экосистеме</b>.' },
  { id: 'v8', t: 32.7, text: 'Природа жестока. Особенно за <b>сорок тысяч рублей</b>.' },
];
const ldur = L => DURS[L.id] ?? Math.max(1.2, L.text.replace(/<[^>]+>/g, '').length * 0.07);
window.EV = LINES.map(L => ({ t: L.t, type: 'voice', id: L.id }));

// ───────── renderer ─────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.08;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#2a1d17');
scene.fog = new THREE.Fog('#3a2a20', 7, 16);
const camera = new THREE.PerspectiveCamera(45, W / H, 0.02, 40);

// ───────── textures ─────────
function canvasTex(w, h, draw, rep) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
  return t;
}
const texWood = canvasTex(1024, 1024, (g, w, h) => { // herringbone-ish oak planks
  g.fillStyle = '#a8703f'; g.fillRect(0, 0, w, h);
  const n = 10;
  for (let i = 0; i < n; i++) {
    const y = i * h / n;
    for (let s = 0; s < 3; s++) {
      const x0 = ((i % 2) * .5 + s) * w / 2.5 - 80, len = w / 2.5;
      g.fillStyle = `hsl(${25 + hash(i * 7 + s) * 9},${42 + hash(i + s * 3) * 12}%,${35 + hash(i * 3 + s) * 11}%)`; g.fillRect(x0, y, len - 3, h / n - 3);
      for (let k = 0; k < 26; k++) { g.strokeStyle = `rgba(60,30,10,${.06 + hash(i * 50 + k + s) * .12})`; g.lineWidth = 1 + hash(k) * 2; g.beginPath(); const yy = y + hash(i * 9 + k + s * 4) * (h / n - 4); g.moveTo(x0, yy); g.bezierCurveTo(x0 + len * .3, yy + 4, x0 + len * .6, yy - 4, x0 + len, yy + 2); g.stroke(); }
      g.fillStyle = 'rgba(35,18,6,.6)'; g.fillRect(x0 + len - 3, y, 3, h / n - 3);
    }
    g.fillStyle = 'rgba(35,18,6,.55)'; g.fillRect(0, y + h / n - 3, w, 3);
  }
}, [4, 4]);
const texWall = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#d9c7a8'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 3000; k++) { g.fillStyle = `rgba(${hash(k) > .5 ? 255 : 80},${hash(k) > .5 ? 250 : 60},${hash(k) > .5 ? 235 : 40},.04)`; g.fillRect(hash(k * 3.1) * w, hash(k * 7.7) * h, 3, 3); }
}, [3, 2]);
const texRug = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#2f5d63'; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#e9d7b4'; g.lineWidth = 26; g.strokeRect(50, 50, w - 100, h - 100);
  g.strokeStyle = '#c4683a'; g.lineWidth = 12; g.strokeRect(100, 100, w - 200, h - 200);
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) {
    const x = 200 + i * 125, y = 200 + j * 125; g.fillStyle = (i + j) % 2 ? '#e9d7b4' : '#c4683a';
    g.beginPath(); g.moveTo(x, y - 40); g.lineTo(x + 40, y); g.lineTo(x, y + 40); g.lineTo(x - 40, y); g.closePath(); g.fill();
  }
  for (let k = 0; k < 9000; k++) { g.fillStyle = `rgba(0,0,0,${hash(k) * .08})`; g.fillRect(hash(k * 1.3) * w, hash(k * 2.9) * h, 2, 4); }
});
const texFabric = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#6f7f86'; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 3) { g.fillStyle = `rgba(0,0,0,${.04 + hash(y) * .05})`; g.fillRect(0, y, w, 1); }
  for (let x = 0; x < w; x += 3) { g.fillStyle = `rgba(255,255,255,${.03 + hash(x + 9) * .04})`; g.fillRect(x, 0, 1, h); }
}, [3, 3]);
const texFur = canvasTex(512, 512, (g, w, h) => { // ginger tabby: stripes run around the body (u = around)
  g.fillStyle = '#e48a3c'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 9; i++) { const x = (i + .5) * w / 9 + (hash(i) - .5) * 20; g.fillStyle = 'rgba(168,84,28,.75)'; g.beginPath(); g.ellipse(x, h * .5, 14 + hash(i + 4) * 10, h * .55, 0, 0, Math.PI * 2); g.fill(); }
  for (let k = 0; k < 16000; k++) { const v = hash(k * 1.7); g.strokeStyle = v > .5 ? 'rgba(255,214,160,.10)' : 'rgba(120,55,15,.10)'; g.beginPath(); const x = hash(k * 3.3) * w, y = hash(k * 5.1) * h; g.moveTo(x, y); g.lineTo(x + 1, y + 6); g.stroke(); }
});
const texSock = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#d93b3b'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 5; i++) { g.fillStyle = '#f4efe6'; g.fillRect(0, 20 + i * 48, w, 18); }
  for (let k = 0; k < 3000; k++) { g.fillStyle = `rgba(0,0,0,${hash(k) * .1})`; g.fillRect(hash(k * 1.3) * w, hash(k * 2.9) * h, 2, 2); }
});
const texArt = canvasTex(512, 640, (g, w, h) => { // abstract poster
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#f2c27b'); gr.addColorStop(1, '#e0794a'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.fillStyle = '#2f5d63'; g.beginPath(); g.arc(w * .5, h * .42, w * .26, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fff3dc'; g.fillRect(w * .12, h * .72, w * .76, 14); g.fillRect(w * .2, h * .78, w * .6, 10);
});

// ───────── materials ─────────
const M = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: o.r ?? .55, metalness: o.m ?? 0, ...(o.extra || {}) });
const mat = {
  floor: new THREE.MeshStandardMaterial({ map: texWood, roughness: .45 }),
  wall: new THREE.MeshStandardMaterial({ map: texWall, roughness: .92 }),
  rug: new THREE.MeshStandardMaterial({ map: texRug, roughness: 1 }),
  fabric: new THREE.MeshPhysicalMaterial({ map: texFabric, roughness: .95, sheen: 1, sheenColor: new THREE.Color('#c9d6db'), sheenRoughness: .6 }),
  wood: M('#7a4a2a', { r: .5 }), woodL: M('#c79a62', { r: .45 }),
  chrome: M('#d8dde2', { r: .18, m: .9 }), steel: M('#9aa3ab', { r: .3, m: .8 }), dark: M('#23262b', { r: .4 }),
  cream: M('#f2e6cf', { r: .4 }), white: M('#f4f1ea', { r: .35 }), black: M('#111', { r: .3 }),
  fur: new THREE.MeshPhysicalMaterial({ map: texFur, roughness: .9, sheen: 1, sheenColor: new THREE.Color('#ffd09a'), sheenRoughness: .5 }),
  furPlain: new THREE.MeshPhysicalMaterial({ color: '#e08638', roughness: .9, sheen: 1, sheenColor: new THREE.Color('#ffd09a'), sheenRoughness: .5 }),
  belly: new THREE.MeshPhysicalMaterial({ color: '#f7e2c4', roughness: .95, sheen: 1, sheenColor: new THREE.Color('#ffffff'), sheenRoughness: .5 }),
  pink: M('#e88f93', { r: .6 }), sock: new THREE.MeshStandardMaterial({ map: texSock, roughness: .95 }),
  leaf: M('#4f8a3c', { r: .7 }), pot: M('#c25b3a', { r: .7 }),
};

// ───────── room ─────────
const room = new THREE.Group(); scene.add(room);
const add = (geo, m, x, y, z, parent = room, cast = true, recv = true) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = cast; o.receiveShadow = recv; parent.add(o); return o; };
add(new THREE.PlaneGeometry(14, 14), mat.floor, 0, 0, 0).rotation.x = -Math.PI / 2;
add(new THREE.PlaneGeometry(10, 3.4), mat.wall, 0, 1.7, -2.3, room, false);
const wl = add(new THREE.PlaneGeometry(8, 3.4), mat.wall, -2.2, 1.7, 0, room, false); wl.rotation.y = Math.PI / 2;
const wr = add(new THREE.PlaneGeometry(8, 3.4), mat.wall, 2.6, 1.7, 0, room, false); wr.rotation.y = -Math.PI / 2;
add(new THREE.PlaneGeometry(10, .1), mat.white, 0, .05, -2.29, room, false); // skirting
// rug
const rug = add(new RoundedBoxGeometry(2.3, .012, 1.7, 2, .005), mat.rug, 0.35, .006, -0.55); rug.castShadow = false;
// window on back wall (behind sofa)
const winG = new THREE.Group(); winG.position.set(-0.45, 1.55, -2.28); room.add(winG);
add(new THREE.PlaneGeometry(1.5, 1.3), new THREE.MeshBasicMaterial({ color: '#ffe2b0' }), 0, 0, 0.005, winG, false, false);
for (const [w, h, x, y] of [[1.65, .08, 0, .69], [1.65, .08, 0, -.69], [.08, 1.45, .79, 0], [.08, 1.45, -.79, 0], [.05, 1.3, 0, 0], [1.5, .05, 0, .15]]) add(new THREE.BoxGeometry(w, h, .1), mat.white, x, y, .05, winG);
// curtains
for (const s of [-1, 1]) for (let i = 0; i < 5; i++) add(new THREE.CylinderGeometry(.06, .07, 2.3, 12), M('#e9dcc2', { r: .95 }), s * (.98 + i * .07), -.05, .18, winG).scale.z = .5;

// sofa
const sofa = new THREE.Group(); sofa.position.set(-0.4, 0, -1.7); room.add(sofa);
add(new RoundedBoxGeometry(2.0, .24, .9, 4, .06), mat.fabric, 0, .32, 0, sofa);              // base (bottom at .2 → dark gap)
for (const x of [-.5, .5]) add(new RoundedBoxGeometry(.98, .16, .78, 4, .07), mat.fabric, x, .5, .04, sofa); // seat cushions
add(new RoundedBoxGeometry(2.0, .55, .24, 4, .09), mat.fabric, 0, .66, -.36, sofa);           // back
for (const x of [-.5, .5]) add(new RoundedBoxGeometry(.9, .4, .18, 4, .08), mat.fabric, x, .78, -.2, sofa).rotation.x = -.18;
for (const s of [-1, 1]) add(new RoundedBoxGeometry(.2, .5, .9, 4, .08), mat.fabric, s * 1.0, .45, 0, sofa); // arms
for (const [x, z] of [[-.9, .38], [.9, .38], [-.9, -.38], [.9, -.38]]) add(new THREE.CylinderGeometry(.025, .018, .2, 10), mat.wood, x, .1, z, sofa);
add(new RoundedBoxGeometry(.36, .3, .1, 3, .05), M('#e2a253', { r: .9 }), -.55, .66, -.12, sofa).rotation.set(-.2, .2, .08); // throw pillow
// darkness under the sofa (occluder plate so the gap reads black) + dark floor patch fading to the front edge
add(new THREE.PlaneGeometry(1.95, .85), M('#0d0907', { r: 1 }), 0, .199, 0, sofa, false, false).rotation.x = Math.PI / 2;
const shadeTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(8,5,3,.97)'); gr.addColorStop(.75, 'rgba(8,5,3,.9)'); gr.addColorStop(1, 'rgba(8,5,3,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
add(new THREE.PlaneGeometry(1.96, .98), new THREE.MeshBasicMaterial({ map: shadeTex, transparent: true, depthWrite: false }), 0, .004, .04, sofa, false, false).rotation.x = -Math.PI / 2;
for (const s of [-1, 1]) add(new THREE.PlaneGeometry(.9, .2), M('#0d0907', { r: 1, extra: { side: THREE.DoubleSide } }), s * .99, .1, 0, sofa, false, false).rotation.y = Math.PI / 2;
add(new THREE.PlaneGeometry(2, .2), M('#0d0907', { r: 1 }), 0, .1, -.44, sofa, false, false);

// console (TV stand) + speaker on top
const consoleG = new THREE.Group(); consoleG.position.set(1.45, 0, -2.0); room.add(consoleG);
add(new RoundedBoxGeometry(.95, .3, .4, 3, .03), mat.woodL, 0, .38, 0, consoleG);
for (const x of [-.12, .12]) add(new THREE.BoxGeometry(.4, .24, .01), M('#b3864f', { r: .5 }), x * 1.9, .38, .2, consoleG);
for (const [x, z] of [[-.42, .16], [.42, .16], [-.42, -.16], [.42, -.16]]) add(new THREE.CylinderGeometry(.018, .014, .23, 10), mat.dark, x, .115, z, consoleG);
for (let i = 0; i < 4; i++) add(new RoundedBoxGeometry(.04, .2 - i * .02, .15, 2, .006), M(['#c0392b', '#2f5d63', '#e9a23b', '#3d4f6e'][i]), .2 + i * .045, .63 - i * .01, 0, consoleG);
const potC = add(new THREE.CylinderGeometry(.07, .055, .12, 18), mat.pot, .38, .59, 0, consoleG);
for (let i = 0; i < 9; i++) { const l = add(new THREE.SphereGeometry(.05, 12, 8), mat.leaf, .38 + Math.cos(i * 2.4) * .05, .7 + hash(i) * .14, Math.sin(i * 2.4) * .05, consoleG); l.scale.set(1, 1.9, .5); l.rotation.z = Math.cos(i * 2.4) * .6; }
// TV on the wall
add(new RoundedBoxGeometry(1.0, .58, .04, 2, .01), mat.black, 1.45, 1.25, -2.27);
add(new THREE.PlaneGeometry(.96, .54), new THREE.MeshStandardMaterial({ color: '#0b0d10', roughness: .12, metalness: .5 }), 1.45, 1.25, -2.245, room, false, false);
// poster on the left
add(new THREE.BoxGeometry(.5, .64, .02), mat.white, -1.75, 1.6, -2.28);
add(new THREE.PlaneGeometry(.44, .58), new THREE.MeshStandardMaterial({ map: texArt, roughness: .7 }), -1.75, 1.6, -2.268, room, false, false);
// floor lamp left
add(new THREE.CylinderGeometry(.14, .16, .02, 24), mat.dark, -1.75, .01, -1.3);
add(new THREE.CylinderGeometry(.01, .01, 1.5, 8), mat.dark, -1.75, .76, -1.3);
add(new THREE.ConeGeometry(.2, .26, 24, 1, true), M('#efe3c8', { r: .9, extra: { side: THREE.DoubleSide } }), -1.75, 1.55, -1.3);
// big plant right-front
add(new THREE.CylinderGeometry(.16, .12, .32, 20), mat.pot, 2.1, .16, -0.3);
for (let i = 0; i < 16; i++) { const l = add(new THREE.SphereGeometry(.09, 12, 8), mat.leaf, 2.1 + Math.cos(i * 2.4) * .14, .5 + hash(i) * .55, -0.3 + Math.sin(i * 2.4) * .14); l.scale.set(1, 2.4, .45); l.rotation.set(hash(i + 3) - .5, i, Math.cos(i * 2.4) * .7); }

// coffee table + kettle
const table = new THREE.Group(); table.position.set(1.15, 0, -0.55); room.add(table);
add(new THREE.CylinderGeometry(.34, .34, .04, 48), mat.woodL, 0, .42, 0, table);
add(new THREE.TorusGeometry(.34, .012, 8, 48), mat.wood, 0, .42, 0, table).rotation.x = Math.PI / 2;
for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; const lg = add(new THREE.CylinderGeometry(.018, .013, .41, 10), mat.wood, Math.cos(a) * .22, .2, Math.sin(a) * .22, table); lg.rotation.set(Math.sin(a) * .12, 0, -Math.cos(a) * .12); }
add(new THREE.CylinderGeometry(.06, .05, .09, 16), mat.white, .18, .485, .12, table); // mug
add(new RoundedBoxGeometry(.2, .02, .14, 2, .005), M('#3d4f6e'), -.12, .45, .15, table).rotation.y = .3; // book

// ───────── LED face screens ─────────
function makeScreen(w = 256, h = 256) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.MeshStandardMaterial({ color: '#000', emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 1.3, roughness: .25 });
  return { c, g, tex, m, key: '' };
}
function drawFace(S, expr, col, p = {}) {
  const key = expr + col + JSON.stringify(p); if (key === S.key) return; S.key = key;
  const { g, c } = S, w = c.width, h = c.height; g.fillStyle = '#0b0f12'; g.fillRect(0, 0, w, h);
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = Math.min(w, h * 2) * .07;
  g.shadowColor = col; g.shadowBlur = w * .05;
  const ex = w * .3, ey = h * .42, r = Math.min(w * .1, h * .2), look = (p.look || 0) * w * .06, blink = p.blink || 0, sq = p.squint || 0;
  const eye = (x, kind, side) => {
    g.beginPath();
    if (kind === 'open') { g.ellipse(x + look, ey, r * .75, Math.max(.05, r * (1 - blink * .95) * (1 - sq * .7)), 0, 0, Math.PI * 2); g.fill(); }
    else if (kind === 'hunt') { g.ellipse(x + look, ey + r * .15, r * .85, r * .32, 0, 0, Math.PI * 2); g.fill(); g.beginPath(); g.moveTo(x - r * 1.1, ey - r * (side < 0 ? .75 : .25)); g.lineTo(x + r * 1.1, ey - r * (side < 0 ? .25 : .75)); g.stroke(); }
    else if (kind === 'wide') { g.lineWidth = w * .045; g.ellipse(x, ey, r * 1.0, r * 1.1, 0, 0, Math.PI * 2); g.stroke(); g.beginPath(); g.ellipse(x + look, ey, r * .25, r * .25, 0, 0, Math.PI * 2); g.fill(); }
    else if (kind === 'sad') { g.arc(x, ey + r * .9, r * .8, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); }
    else if (kind === 'dizzy') { g.lineWidth = w * .035; for (let k = 0; k < 28; k++) { const a = k * .45 + (p.spin || 0), rr = r * k / 28; const X = x + Math.cos(a) * rr, Y = ey + Math.sin(a) * rr; k ? g.lineTo(X, Y) : g.moveTo(X, Y); } g.stroke(); }
    else if (kind === 'flat') { g.moveTo(x - r, ey); g.lineTo(x + r, ey); g.stroke(); }
  };
  if (p.text) { g.shadowBlur = w * .03; g.font = `800 ${p.size || h * .7}px Rubik`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(p.text, w / 2, h * .54); S.tex.needsUpdate = true; return; }
  eye(ex, expr, -1); eye(w - ex, expr, 1);
  g.beginPath(); const my = h * .78, mw = w * .14;
  if (expr === 'sad') { g.arc(w / 2, my + h * .12, mw * .6, Math.PI * 1.2, Math.PI * 1.8); g.stroke(); g.beginPath(); g.fillStyle = '#9fe8ff'; g.shadowColor = '#9fe8ff'; g.ellipse(w - ex + r * .6, ey + r * 1.4 + (p.tear || 0) * h * .25, r * .22, r * .34, 0, 0, Math.PI * 2); g.fill(); }
  else if (expr === 'wide' || expr === 'dizzy') { g.ellipse(w / 2, my, mw * .35, h * .07, 0, 0, Math.PI * 2); g.stroke(); }
  else if (expr === 'hunt') { g.moveTo(w / 2 - mw * .5, my); g.lineTo(w / 2 + mw * .5, my - h * .02); g.stroke(); }
  S.tex.needsUpdate = true;
}
const C_RED = '#ff4a3d', C_TEAL = '#5fe3ff', C_GOLD = '#ffc35a';

// ───────── robovac (hunter) ─────────
const vac = new THREE.Group(); room.add(vac);
const vBody = new THREE.Group(); vac.add(vBody);
add(new THREE.CylinderGeometry(.2, .2, .075, 64), M('#30343b', { r: .32 }), 0, .048, 0, vBody);
add(new THREE.CylinderGeometry(.192, .2, .012, 64), M('#e9e6df', { r: .28 }), 0, .09, 0, vBody);
add(new THREE.TorusGeometry(.17, .003, 6, 64), M('#b9b4aa', { r: .3 }), 0, .097, 0, vBody).rotation.x = Math.PI / 2; // panel seam
add(new THREE.CylinderGeometry(.05, .05, .018, 32), M('#e9e6df'), 0, .103, -.06, vBody);
const lidarMat = new THREE.MeshStandardMaterial({ color: '#0a1a20', emissive: C_TEAL, emissiveIntensity: .8 });
const lidar = add(new THREE.CylinderGeometry(.045, .045, .008, 32), lidarMat, 0, .114, -.06, vBody, false, false);
for (let i = 0; i < 3; i++) add(new THREE.CylinderGeometry(.008, .008, .004, 12), M('#555'), -.06 + i * .06, .1, .1, vBody);
const vScr = makeScreen(256, 128); add(new THREE.PlaneGeometry(.17, .085), vScr.m, 0, .055, .201, vBody, false, false);
const bumper = add(new THREE.TorusGeometry(.2, .013, 8, 48, Math.PI * .9), M('#555c66'), 0, .03, 0, vBody); bumper.rotation.x = Math.PI / 2; bumper.rotation.z = Math.PI * .05;
const brush = new THREE.Group(); brush.position.set(.13, .008, .13); vBody.add(brush);
for (let i = 0; i < 3; i++) { const b = add(new THREE.CylinderGeometry(.003, .002, .09, 6), M('#2a2a2a'), 0, 0, .045, brush); b.rotation.x = Math.PI / 2; b.parent.remove(b); const pv = new THREE.Group(); pv.rotation.y = i * Math.PI * 2 / 3; pv.add(b); b.position.set(0, 0, .045); brush.add(pv); }
const vLight = new THREE.PointLight(C_RED, 0, 1.2, 2); vLight.position.set(0, .12, .25); vac.add(vLight);

// ───────── kettle (ally #2) ─────────
const kettle = new THREE.Group(); kettle.position.set(1.05, .44, -0.55); room.add(kettle);
const kBody = new THREE.Group(); kettle.add(kBody);
add(new THREE.CylinderGeometry(.075, .075, .015, 32), mat.dark, 0, .007, 0, kBody);
add(new THREE.CylinderGeometry(.06, .08, .16, 32), mat.cream, 0, .095, 0, kBody);
const kLid = new THREE.Group(); kLid.position.y = .175; kBody.add(kLid);
add(new THREE.CylinderGeometry(.045, .06, .02, 32), mat.cream, 0, 0, 0, kLid); add(new THREE.SphereGeometry(.018, 14, 10), mat.dark, 0, .016, 0, kLid);
add(new THREE.TorusGeometry(.05, .011, 10, 20, Math.PI * 1.1), mat.dark, -.08, .1, 0, kBody).rotation.z = Math.PI / 2 + .1;
add(new THREE.CylinderGeometry(.011, .022, .075, 14), mat.cream, .085, .14, 0, kBody).rotation.z = -1.0;
const kScr = makeScreen(); add(new THREE.PlaneGeometry(.07, .055), kScr.m, 0, .09, .074, kBody, false, false).rotation.x = -.13;
kettle.rotation.y = -0.9;

// ───────── smart speaker (ally #1) ─────────
const spk = new THREE.Group(); spk.position.set(1.17, .53, -1.95); room.add(spk);
const spkBody = new THREE.Group(); spk.add(spkBody);
add(new THREE.CylinderGeometry(.065, .07, .17, 40), mat.fabric, 0, .085, 0, spkBody);
add(new THREE.CylinderGeometry(.066, .066, .015, 40), mat.dark, 0, .175, 0, spkBody);
const spkRingMat = new THREE.MeshStandardMaterial({ color: '#051418', emissive: C_TEAL, emissiveIntensity: .2 });
add(new THREE.TorusGeometry(.052, .007, 8, 40), spkRingMat, 0, .184, 0, spkBody, false, false).rotation.x = Math.PI / 2;
const spkEyeMat = new THREE.MeshStandardMaterial({ color: '#051418', emissive: C_TEAL, emissiveIntensity: 0 });
for (const x of [-.022, .022]) add(new THREE.SphereGeometry(.009, 12, 8), spkEyeMat, x, .12, .064, spkBody, false, false);
const spkLight = new THREE.PointLight(C_TEAL, 0, 1.0, 2); spkLight.position.set(0, .25, .05); spk.add(spkLight);

// ───────── sock ─────────
const sock = new THREE.Group(); room.add(sock);
const sockLeg = add(new THREE.CylinderGeometry(.03, .032, 1, 18, 1, false), mat.sock, 0, 0, 0, sock); // unit length along Y, stretched between A and B
const sockCuffA = add(new THREE.SphereGeometry(.031, 16, 10), mat.sock, 0, 0, 0, sock);
const sockToe = add(new THREE.SphereGeometry(.034, 16, 12), mat.sock, 0, 0, 0, sock); sockToe.scale.set(1, 1, 1.5);
const UP = V(0, 1, 0);
function stick(mesh, A, B, r = 1) { // orient a unit-Y cylinder between A and B
  const d = B.clone().sub(A), L = Math.max(1e-4, d.length());
  mesh.position.copy(A).addScaledVector(d, .5); mesh.quaternion.setFromUnitVectors(UP, d.normalize()); mesh.scale.set(r, L, r);
}
function placeSock(A, B) { stick(sockLeg, A, B); sockCuffA.position.copy(A); const d = B.clone().sub(A).normalize(); sockToe.position.copy(B).addScaledVector(d, .01); sockToe.lookAt(B.clone().add(d)); }

// ───────── cat ─────────
const cat = new THREE.Group(); room.add(cat);
const cBody = new THREE.Group(); cat.add(cBody);                      // pivot at the hips (rear), pitch for sitting
const torso = add(new THREE.SphereGeometry(1, 40, 28), mat.fur, 0, 0, .14, cBody); torso.scale.set(.12, .115, .22);
const chest = add(new THREE.SphereGeometry(1, 30, 20), mat.belly, 0, -.02, .27, cBody); chest.scale.set(.09, .095, .09);
const haunch = []; for (const s of [-1, 1]) { const hh = add(new THREE.SphereGeometry(1, 28, 20), mat.fur, s * .075, -.01, .04, cBody); hh.scale.set(.06, .085, .1); haunch.push(hh); }
const neck = new THREE.Group(); neck.position.set(0, .08, .3); cBody.add(neck);
const cHead = new THREE.Group(); neck.add(cHead);
const skull = add(new THREE.SphereGeometry(1, 40, 30), mat.fur, 0, .06, .03, cHead); skull.scale.set(.1, .088, .09);
for (const s of [-1, 1]) { const ch = add(new THREE.SphereGeometry(1, 24, 16), mat.furPlain, s * .055, .03, .055, cHead); ch.scale.set(.05, .045, .045); } // cheek fluff
for (const s of [-1, 1]) { const mz = add(new THREE.SphereGeometry(1, 20, 14), mat.belly, s * .02, .02, .1, cHead); mz.scale.set(.03, .024, .026); }
add(new THREE.SphereGeometry(1, 16, 10), mat.belly, 0, .0, .088, cHead).scale.set(.028, .02, .022); // chin
const nose = add(new THREE.SphereGeometry(1, 14, 10), mat.pink, 0, .042, .118, cHead); nose.scale.set(.011, .008, .007);
const ears = []; for (const s of [-1, 1]) {
  const eg = new THREE.Group(); eg.position.set(s * .055, .13, .01); eg.rotation.z = -s * .35; cHead.add(eg);
  add(new THREE.ConeGeometry(.035, .07, 4), mat.furPlain, 0, .03, 0, eg).rotation.y = Math.PI / 4;
  add(new THREE.ConeGeometry(.022, .05, 4), mat.pink, 0, .026, .008, eg).rotation.y = Math.PI / 4;
  ears.push(eg);
}
const catEyes = []; for (const s of [-1, 1]) {
  const eg = new THREE.Group(); eg.position.set(s * .04, .07, .09); cHead.add(eg);
  const ball = add(new THREE.SphereGeometry(.022, 24, 16), new THREE.MeshStandardMaterial({ color: '#b9d84a', roughness: .1, emissive: '#c8ff40', emissiveIntensity: 0 }), 0, 0, 0, eg, false, false);
  const pup = add(new THREE.SphereGeometry(.0225, 20, 14), mat.black, 0, 0, .0015, eg, false, false); pup.scale.set(.22, .9, .9);
  const lid = add(new THREE.SphereGeometry(.0245, 20, 14, 0, Math.PI * 2, 0, Math.PI * .5), mat.furPlain, 0, 0, 0, eg, false, false); // rotates down to blink
  catEyes.push({ eg, ball, pup, lid });
}
const whiskers = []; for (const s of [-1, 1]) for (let i = 0; i < 3; i++) { const wsk = add(new THREE.CylinderGeometry(.0009, .0006, .12, 4), M('#fffaf0', { r: .3 }), s * .07, .025 + i * .008 - .008, .1, cHead, false, false); wsk.rotation.set(0, 0, s * (Math.PI / 2 - .12 + i * .12)); whiskers.push(wsk); }
// legs: shoulder/hip anchors in cBody, paws are world targets
const legMeshes = [], pawMeshes = [];
const LEGS = [{ a: V(-.06, -.04, .26), front: 1 }, { a: V(.06, -.04, .26), front: 1 }, { a: V(-.075, -.03, .03), front: 0 }, { a: V(.075, -.03, .03), front: 0 }];
for (let i = 0; i < 4; i++) { legMeshes.push(add(new THREE.CylinderGeometry(.026, .022, 1, 16), mat.furPlain, 0, 0, 0)); const pw = add(new THREE.SphereGeometry(1, 18, 12), mat.belly, 0, 0, 0); pw.scale.set(.026, .018, .034); pawMeshes.push(pw); }
// tail: chain of segments from the rump
const tailRoot = new THREE.Group(); tailRoot.position.set(0, .02, -.07); cBody.add(tailRoot);
const tail = []; { let par = tailRoot; for (let i = 0; i < 9; i++) { const g = new THREE.Group(); g.position.z = i ? -.045 : 0; par.add(g); const sgm = add(new THREE.SphereGeometry(1, 16, 10), i > 6 ? mat.belly : mat.fur, 0, 0, -.022, g); sgm.scale.set(.024 - i * .001, .024 - i * .001, .032); tail.push(g); par = g; } }

const litLeg = mat.furPlain.clone(), litPaw = mat.belly.clone();
function poseCat(p) {
  cat.position.set(p.x, p.y || 0, p.z); cat.rotation.y = p.ry;
  cBody.position.set(0, p.hipY, 0); cBody.rotation.x = p.pitch || 0; cBody.scale.y = p.squash || 1;
  neck.rotation.set(p.nod || 0, p.turn || 0, p.tilt || 0); cHead.rotation.x = p.headPitch || 0;
  neck.position.y = .08 + (p.neckUp || 0);
  for (const e of catEyes) {
    const bl = clamp(p.blink || 0); e.lid.rotation.x = lerp(-1.7, -.05, bl) ; e.lid.visible = bl > .02;
    e.ball.material.emissiveIntensity = p.glow || 0; e.pup.scale.x = p.pupil ?? .22;
  }
  ears.forEach((e, i) => { e.rotation.x = p.earBack || 0; });
  cat.updateMatrixWorld(true);
  for (let i = 0; i < 4; i++) {
    const A = cBody.localToWorld(LEGS[i].a.clone());
    const P = p.paws[i];
    stick(legMeshes[i], A, P); pawMeshes[i].position.copy(P); pawMeshes[i].rotation.y = p.ry;
  }
  const tw = p.tailWave || 0, tc = p.tailCurl ?? .25;
  tail.forEach((g, i) => { g.rotation.x = (p.tailLift ?? -.25) * (i === 0 ? 1 : .15) + Math.sin(p.t * 2.2 - i * .6) * .04; g.rotation.y = tc * .35 + Math.sin(p.t * 3 - i * .7) * tw * .25; });
}
// floor point under a body anchor, pushed forward
function pawAt(local, fwd = 0, side = 0, y = .018) { const P = cBody.localToWorld(local.clone()); const f = V(Math.sin(cat.rotation.y), 0, Math.cos(cat.rotation.y)), r = V(Math.cos(cat.rotation.y), 0, -Math.sin(cat.rotation.y)); P.addScaledVector(f, fwd).addScaledVector(r, side); P.y = y; return P; }

// ───────── dust motes + light shafts ─────────
const motes = []; const moteMat = new THREE.MeshBasicMaterial({ color: '#fff1d0', transparent: true, opacity: .6, depthWrite: false });
for (let i = 0; i < 120; i++) { const m = add(new THREE.SphereGeometry(.0035, 6, 4), moteMat, 0, 0, 0, room, false, false); motes.push(m); }
const shaftTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,230,180,.0)'); gr.addColorStop(.2, 'rgba(255,230,180,.55)'); gr.addColorStop(1, 'rgba(255,230,180,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
const shafts = []; for (let i = 0; i < 4; i++) { const s = add(new THREE.PlaneGeometry(.35 + i * .08, 3.2), new THREE.MeshBasicMaterial({ map: shaftTex, transparent: true, opacity: .1, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }), -0.7 + i * .28, 1.0, -1.3, room, false, false); s.rotation.set(-.75, .0, .12 - i * .05); shafts.push(s); }
// dust puffs (vac impacts / drag trail)
const puffMat = new THREE.MeshStandardMaterial({ color: '#efe6d6', transparent: true, opacity: .5, roughness: 1, depthWrite: false });
const puffs = []; for (let i = 0; i < 30; i++) { const p = add(new THREE.SphereGeometry(1, 10, 8), puffMat.clone(), 0, 0, 0, room, false, false); p.visible = false; puffs.push(p); }

// ───────── lights ─────────
const hemi = new THREE.HemisphereLight('#ffe9cc', '#5a3a26', .7); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffd49a', 2.8); sun.position.set(-1.6, 4.5, -5.5); sun.target.position.set(0.3, 0, -0.5);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: .5, far: 14 }); sun.shadow.bias = -0.0004; sun.shadow.normalBias = .02;
scene.add(sun, sun.target);
const key = new THREE.DirectionalLight('#fff0dc', 1.25); key.position.set(1.5, 2.2, 3.5); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -2.5, right: 2.5, top: 2.5, bottom: -2.5, near: .5, far: 12 }); key.shadow.bias = -0.0005; key.shadow.normalBias = .02; scene.add(key);
const fill = new THREE.PointLight('#ffb070', 1.0, 6, 1.6); fill.position.set(-1.75, 1.45, -1.3); scene.add(fill);
const rim = new THREE.DirectionalLight('#9ad0ff', .55); rim.position.set(3, 2, -3); scene.add(rim);

// ───────── choreography ─────────
const SOCK0A = V(-0.3, .03, -1.02), SOCK0B = V(-0.44, .03, -1.16);
const S0 = V(0.2, 0, -0.05), R = V(0.0, 0, -0.5);
const H_SOCK = Math.atan2(SOCK0A.x - S0.x, SOCK0A.z - S0.z);
const TGT = SOCK0A.clone().setY(0).addScaledVector(V(Math.sin(H_SOCK), 0, Math.cos(H_SOCK)), -.42);
const Q = V(-0.12, 0, -0.66), C1 = V(0.72, 0, -0.74), C2 = V(0.98, 0, -1.5), E = V(0.6, 0, -1.02);
const CC = V(0.2, 0, -0.55), CR = .3;
const CAT_SIT = V(-0.36, 0, -1.02);
const fwdOf = r => V(Math.sin(r), 0, Math.cos(r));

function vacState(t) {
  let P, r = H_SOCK, tilt = 0, spin = 0, bob = 0;
  if (t < 3.6) { P = S0.clone(); r = lerp(H_SOCK + 1.3, H_SOCK, back(seg(t, .35, .7), 2.4)); tilt = (t > .35 && t < .8) ? Math.sin(seg(t, .35, .8) * Math.PI) * .05 : 0; }
  else if (t < 9.3) { const u = K([[3.6, 0], [4.6, .25], [5.5, .25], [6.6, .6], [7.6, .6], [8.9, .8]], t); P = S0.clone().lerp(TGT, u); tilt = -ss(seg(t, 7.6, 8.0)) * .06 * (1 - ss(seg(t, 8.9, 9.2))); bob = (t > 7.6 && t < 9.2) ? Math.sin(t * 30) * .002 : 0; }
  else if (t < 9.75) { const u = eo(seg(t, 9.3, 9.6)); const lung = TGT.clone().lerp(SOCK0A.clone().setY(0).addScaledVector(fwdOf(H_SOCK), -.2), u); P = lung; tilt = Math.sin(seg(t, 9.3, 9.75) * Math.PI) * .09; }
  else if (t < 13) { const A0 = SOCK0A.clone().setY(0).addScaledVector(fwdOf(H_SOCK), -.2); P = A0.lerp(R, ss(seg(t, 9.9, 12.6))); bob = Math.sin(t * 35) * .002; }
  else if (t < 23.2) { const tug = (t > 14.9) ? (Math.sin(t * 7.3) * .5 + .5) * .05 + seg(t, 14.9, 23) * .12 : 0; P = R.clone().addScaledVector(fwdOf(H_SOCK), tug); tilt = (t > 14.9) ? .05 + Math.sin(t * 14) * .02 : 0; bob = (t > 14.9) ? Math.sin(t * 40) * .003 : 0; }
  else if (t < 27.9) { const u = eo(seg(t, 23.2, 23.6)); const Rt = R.clone().addScaledVector(fwdOf(H_SOCK), .17); P = Rt.lerp(Q, u); tilt = Math.sin(seg(t, 23.2, 23.7) * Math.PI) * -.1; if (t > 27.5) { P.addScaledVector(fwdOf(H_SOCK), -ss(seg(t, 27.5, 27.9)) * .04); tilt = -.04; } }
  else if (t < 29.6) {
    const u1 = seg(t, 27.95, 28.35), u2 = seg(t, 28.35, 28.8), u3 = seg(t, 28.8, 29.6);
    P = t < 28.35 ? Q.clone().lerp(C1, eo(u1)) : t < 28.8 ? C1.clone().lerp(C2, ss(u2)) : C2.clone().lerp(E, eo(u3));
    spin = (1 - Math.pow(1 - seg(t, 27.95, 29.6), 2)) * Math.PI * 7; tilt = Math.sin(t * 25) * .05 * (1 - seg(t, 28.8, 29.6));
  }
  else if (t < 32.9) { P = E.clone(); spin = Math.PI * 7; }
  else {
    const phi0 = Math.atan2(E.x - CC.x, E.z - CC.z), phi = phi0 + (t - 33.6) * .55;
    const onC = CC.clone().add(V(Math.sin(phi) * CR, 0, Math.cos(phi) * CR));
    const st = CC.clone().add(V(Math.sin(phi0) * CR, 0, Math.cos(phi0) * CR));
    if (t < 33.6) { P = E.clone().lerp(st, ss(seg(t, 32.9, 33.6))); } else P = onC;
    const hd = phi + Math.PI / 2; r = H_SOCK + Math.PI * 7 - (H_SOCK + Math.PI * 7 - hd) * 0; spin = 0; r = lerp(H_SOCK + Math.PI * 7, hd + Math.PI * 2 * Math.round((H_SOCK + Math.PI * 7 - hd) / (Math.PI * 2)), ss(seg(t, 32.9, 33.8)));
    bob = Math.sin(t * 30) * .0015;
  }
  return { P, r: r + spin, tilt, bob };
}

function catState(t) { // returns pose params (paws resolved after body placement)
  const p = { t, x: -0.36, z: -1.86, ry: 0, hipY: .075, pitch: 0, squash: .72, nod: .25, turn: 0, glow: 0, blink: 0, pupil: .25, tailCurl: .4, tailLift: -.1, tailWave: .2, mode: 'crouch' };
  if (t < 23.0) {
    p.glow = t < 13.2 ? (t > 6.2 && t < 6.6 ? .6 * Math.sin(seg(t, 6.2, 6.6) * Math.PI) : 0) : ss(seg(t, 13.2, 13.6)) * .9;
    p.blink = t < 6.2 ? 1 : t < 6.6 ? 1 - Math.sin(seg(t, 6.2, 6.6) * Math.PI) : t < 13.2 ? 1 : 1 - ss(seg(t, 13.2, 13.5));
    p.pupil = t > 14.3 ? .5 : .22; p.mode = t > 14.4 ? 'reach' : 'crouch'; p.nod = .28; p.turn = .12;
  } else if (t < 27.5) {
    const out = ss(seg(t, 23.0, 25.0)), sit = ss(seg(t, 24.6, 25.6));
    p.z = lerp(-1.86, CAT_SIT.z, out); p.x = CAT_SIT.x; p.squash = lerp(.72, 1, ss(seg(t, 23.2, 24.6)));
    p.hipY = lerp(.075, .07, sit); p.pitch = -sit * .75; p.nod = lerp(.25, .5, sit); p.headPitch = 0; p.turn = -sit * .55;
    p.mode = sit > .5 ? 'sit' : 'walk'; p.glow = .25 * (1 - out);
    p.blink = t > 26.0 && t < 26.8 ? Math.sin(seg(t, 26.0, 26.8) * Math.PI) * .95 : 0; p.pupil = lerp(.5, .2, out);
    p.tailCurl = .8; p.tailLift = lerp(-.1, -.5, sit); p.tailWave = .1;
  } else if (t < 31.0) {
    p.x = CAT_SIT.x; p.z = CAT_SIT.z; p.hipY = .07; p.pitch = -.75; p.nod = .5; p.turn = .45 - ss(seg(t, 28.2, 29.5)) * .25; p.mode = 'swipe';
    p.earBack = ss(seg(t, 27.4, 27.7)) * .5 * (1 - ss(seg(t, 28.4, 28.9))); p.pupil = .55 - ss(seg(t, 28.3, 28.8)) * .35; p.tailWave = .5; p.tailLift = -.5;
    p.blink = t > 29.8 && t < 30.3 ? Math.sin(seg(t, 29.8, 30.3) * Math.PI) * .9 : 0;
  } else {
    // pick up sock (31.0) → crouch 31.2 → jump 31.5–32.1 → sit on vac
    const v = vacState(t); const top = V(v.P.x, .105, v.P.z);
    const j = seg(t, 31.5, 32.1);
    if (t < 31.5) { p.x = CAT_SIT.x; p.z = CAT_SIT.z; const c = ss(seg(t, 31.1, 31.45)); p.hipY = lerp(.07, .06, c); p.pitch = lerp(-.75, -.15, c); p.nod = lerp(.5, .3, c); p.turn = .2; p.mode = 'prep'; p.squash = 1 - c * .12; p.tailLift = -.3; }
    else if (t < 32.1) { const A = CAT_SIT, B = top; p.x = lerp(A.x, B.x, j); p.z = lerp(A.z, B.z, j); p.y = Math.sin(j * Math.PI) * .32 + lerp(0, .105, j); p.hipY = .09; p.pitch = lerp(-.3, .15, j); p.nod = .2; p.mode = 'air'; p.tailLift = -.05; p.ry = lerp(0, -v.r + v.r, 0); }
    else { const land = spring(t - 32.1, 9, .4); p.x = top.x; p.z = top.z; p.y = .105; p.hipY = .07 - (1 - land) * .02; p.pitch = -.75; p.nod = .45; p.turn = Math.sin(t * .7) * .15; p.mode = 'throne'; p.tailCurl = .9; p.tailLift = -.45; p.tailWave = .15;
      p.blink = t > 35.2 && t < 35.9 ? Math.sin(seg(t, 35.2, 35.9) * Math.PI) * .95 : 0; p.pupil = .2; }
    p.ry = t < 31.5 ? Math.atan2(top.x - CAT_SIT.x, top.z - CAT_SIT.z) * ss(seg(t, 30.9, 31.4)) : (t < 32.1 ? Math.atan2(top.x - CAT_SIT.x, top.z - CAT_SIT.z) : v.r);
  }
  return p;
}

// ───────── shots ─────────
const vacPos = () => vac.position.clone();
const catHead = () => cHead.localToWorld(V(0, .05, .03));
const SHOTS = [
  { a: 0, b: 3.6, cam: t => { const u = ss(seg(t, 0, 3.6)); return [V(lerp(-0.68, -0.6, u), .1, lerp(-1.4, -1.3, u)), V(.2, .07, -.05), lerp(30, 27, u)]; } },
  { a: 3.6, b: 9.25, cam: t => { const v = vacPos(); const d = fwdOf(H_SOCK); const pp = V(-d.z, 0, d.x); const u = seg(t, 3.6, 9.25);
      return [v.clone().addScaledVector(pp, lerp(-1.5, -1.4, u)).addScaledVector(d, lerp(-.2, .0, u)).add(V(0, .2, 0)), v.clone().addScaledVector(d, .15).add(V(0, .06, 0)), 36]; } },
  { a: 9.25, b: 13.0, cam: t => { const u = ss(seg(t, 9.25, 13)); return [V(lerp(-1.5, -1.44, u), .22, lerp(-.72, -.66, u)), V(lerp(-.2, -.08, u), .06, lerp(-.85, -.66, u)), 38]; } },
  { a: 13.0, b: 18.0, cam: t => { const v = vacPos(); const b = fwdOf(H_SOCK); const u = ss(seg(t, 13, 18)); return [v.clone().addScaledVector(b, -.42).add(V(.16, lerp(.2, .16, u), 0)), V(-0.42, lerp(.11, .08, u), -1.3), lerp(40, 34, u)]; } },
  { a: 18.0, b: 19.7, cam: t => { const v = vacPos(); const f = fwdOf(H_SOCK); const u = ss(seg(t, 18, 19.7)); const pp = V(-f.z, 0, f.x); return [v.clone().addScaledVector(f, lerp(.85, .78, u)).addScaledVector(pp, -.42).add(V(0, .16, 0)), v.clone().addScaledVector(f, .12).add(V(0, .05, 0)), 34]; } },
  { a: 19.7, b: 20.5, cam: t => { const u = ss(seg(t, 19.7, 20.5)); return [V(lerp(.86, .83, u), .68, lerp(-1.36, -1.4, u)), V(1.17, .62, -1.92), 40]; } },
  { a: 20.5, b: 23.0, cam: t => { const u = ss(seg(t, 20.5, 23)); return [V(lerp(.6, .62, u), .6, lerp(-.08, -.12, u)), V(.97, .5, -.52), 40]; } },
  { a: 23.0, b: 27.3, cam: t => { const u = ss(seg(t, 23, 27.3)); return [V(lerp(-1.0, -0.94, u), lerp(.15, .18, u), lerp(.08, .0, u)), V(-0.36, lerp(.12, .22, u), lerp(-1.4, -1.02, ss(seg(t, 23, 25.2)))), lerp(48, 44, u)]; } },
  { a: 27.3, b: 31.0, cam: t => { const u = ss(seg(t, 27.3, 31)); return [V(lerp(.12, .16, u), lerp(1.0, 1.05, u), lerp(1.25, 1.35, u)), V(.22, .18, -1.05), 60]; } },
  { a: 31.0, b: 32.9, cam: t => { const u = ss(seg(t, 31, 32.9)); return [V(lerp(-.1, .05, u), .38, lerp(.45, .5, u)), V(lerp(-.1, .5, u), .2, -1.0), 46]; } },
  { a: 32.9, b: DUR + 1, cam: t => { const v = vacPos(); const a = lerp(-.35, .3, ss(seg(t, 32.9, 38.5))); return [CC.clone().add(V(Math.sin(a) * 1.45, lerp(.38, .32, seg(t, 33, 38)), Math.cos(a) * 1.45)), v.clone().add(V(0, .24, 0)), 40]; } },
];
const shotAt = t => SHOTS.find(s => t >= s.a && t < s.b) || SHOTS[SHOTS.length - 1];

// ───────── render(t) ─────────
const subEl = document.getElementById('sub'), flashEl = document.getElementById('flash'), docEl = document.getElementById('doc'), recEl = document.getElementById('rec');
let lastSub = '';
window.render = function (t) {
  const sh = shotAt(t);
  // ── robovac
  const v = vacState(t);
  vac.position.set(v.P.x, v.bob, v.P.z); vac.rotation.y = v.r; vBody.rotation.x = v.tilt;
  const moving = (t > 3.6 && t < 13) || (t > 14.9 && t < 23.6) || (t > 27.9 && t < 29.6) || t > 32.9;
  brush.rotation.y = -t * (moving ? 40 : 8);
  const alarm = t > 18.0 && t < 23.2;
  lidarMat.emissive.set(alarm ? C_RED : t > 32.1 ? '#4a6fff' : C_TEAL); lidarMat.emissiveIntensity = alarm ? (Math.sin(t * 18) > 0 ? 3 : .4) : .9 + Math.sin(t * 5) * .3;
  vLight.intensity = alarm ? (Math.sin(t * 18) > 0 ? 1.4 : .1) : 0;
  let vExpr = 'open', vCol = C_TEAL, vp = {};
  if (t < .5) vExpr = 'open';
  else if (t < 9.3) { vExpr = 'hunt'; vp = { look: -.3 }; }
  else if (t < 13.4) { vExpr = 'hunt'; vCol = C_GOLD; }
  else if (t < 14.9) { vExpr = 'wide'; }
  else if (t < 18.0) { vExpr = 'hunt'; vCol = C_RED; vp = { squint: .4 }; }
  else if (t < 23.2) { vExpr = 'x'; vCol = C_RED; vp = { text: Math.floor(t * 4) % 2 ? '!!!' : '!', size: 90 }; }
  else if (t < 27.9) { vExpr = 'wide'; vp = { look: Math.sin(t * 2) * .3 }; }
  else if (t < 32.1) { vExpr = 'dizzy'; vCol = C_GOLD; vp = { spin: Math.round(t * 12) * .5 }; }
  else { vExpr = 'sad'; vCol = '#7fa8ff'; vp = { tear: Math.round(((t - 32.1) % 1.6) / 1.6 * 8) / 8 }; }
  drawFace(vScr, vExpr, vCol, vp);
  vac.updateMatrixWorld(true);
  // ── cat
  const p = catState(t);
  cat.position.set(p.x, p.y || 0, p.z); cat.rotation.y = p.ry; cBody.position.set(0, p.hipY, 0); cBody.rotation.x = p.pitch; cat.updateMatrixWorld(true);
  const sockA = vac.localToWorld(V(.13, .03, .19)); // caught by the side brush
  let paws;
  const FL = LEGS[0].a, FR = LEGS[1].a, BL = LEGS[2].a, BR = LEGS[3].a;
  if (p.mode === 'crouch' || p.mode === 'reach') {
    paws = [pawAt(FL, .05), pawAt(FR, .05), pawAt(BL, .04), pawAt(BR, .04)];
    if (p.mode === 'reach') { // left paw (on +x side) shoots out to the sock's far end, then tugs
      const shoot = eo(seg(t, 14.4, 14.75)); const tugB = SOCK0B.clone();
      const pull = (t > 14.9) ? Math.sin(t * 7.3 + 1.2) * .03 : 0;
      paws[1] = pawAt(FR, .05).lerp(tugB.clone().add(V(0, .015, pull)), shoot);
    }
  } else if (p.mode === 'walk') {
    const ph = t * 9; paws = [pawAt(FL, .05 + Math.sin(ph) * .05), pawAt(FR, .05 - Math.sin(ph) * .05), pawAt(BL, .04 - Math.sin(ph) * .04), pawAt(BR, .04 + Math.sin(ph) * .04)];
    paws[0].y += Math.max(0, Math.cos(ph)) * .03; paws[1].y += Math.max(0, -Math.cos(ph)) * .03;
  } else if (p.mode === 'air') {
    paws = [pawAt(FL, .14, 0, 0), pawAt(FR, .14, 0, 0), pawAt(BL, -.1, 0, 0), pawAt(BR, -.1, 0, 0)];
    for (const q of paws) q.y = cat.position.y + lerp(-.02, .02, 0) + .03;
  } else { // sit / swipe / prep / throne: front paws on the ground in front of the chest, rear paws tucked by the haunches
    const gy = (p.y || 0) + .018;
    paws = [pawAt(FL, .02, 0, gy), pawAt(FR, .02, 0, gy), pawAt(BL, .1, 0, gy), pawAt(BR, .1, 0, gy)];
    if (p.mode === 'swipe') { // +x paw: wind-up 27.5→27.9, strike 27.9→28.05, settle
      const wind = ss(seg(t, 27.45, 27.85)) * (1 - ss(seg(t, 27.9, 28.0))), strike = ss(seg(t, 27.88, 28.02)) * (1 - ss(seg(t, 28.25, 28.7)));
      const sh0 = cBody.localToWorld(FR.clone());
      const up = sh0.clone().add(V(.04, .2, -.02)); const hit = Q.clone().add(V(-.05, .07, -.05));
      paws[1] = paws[1].clone().lerp(up, wind).lerp(hit, strike);
    }
  }
  p.paws = paws; poseCat(p);
  // hidden under the sofa: only the eyes (and the reaching paw) read; fur brightens as the cat steps out
  const dim = t < 23.0 ? .07 : lerp(.07, 1, ss(seg(t, 23.0, 24.3)));
  mat.fur.color.setScalar(dim); mat.furPlain.color.set('#e08638').multiplyScalar(dim); mat.belly.color.set('#f7e2c4').multiplyScalar(dim); mat.pink.color.set('#e88f93').multiplyScalar(dim);
  for (const m of [mat.fur, mat.furPlain, mat.belly]) m.sheen = dim;
  const reachLit = t > 14.4 && t < 23.0;
  legMeshes[1].material = reachLit ? litLeg : mat.furPlain; pawMeshes[1].material = reachLit ? litPaw : mat.belly;
  // ── sock
  let A, B;
  if (t < 9.55) { A = SOCK0A.clone(); B = SOCK0B.clone(); }
  else if (t < 23.25) {
    A = sockA.clone();
    if (t < 14.75) { const f = fwdOf(H_SOCK); B = A.clone().addScaledVector(f, .2).add(V(-.03, 0, 0)); B.y = .03; if (t > 14.4) B.lerp(pawMeshes[1].position, eo(seg(t, 14.4, 14.75))); }
    else B = pawMeshes[1].position.clone().add(V(0, .01, 0));
    A.y = .03;
  } else if (t < 31.0) { const pw = pawMeshes[1].position; const yank = eo(seg(t, 23.2, 23.32)); const rest = CAT_SIT.clone().add(V(.08, .03, .2));
    A = sockA.clone().setY(.03).lerp(rest.clone().add(V(.12, 0, .05)), yank); B = (t < 25 ? pw.clone() : rest.clone()); if (t >= 25) { A = rest.clone().add(V(.13, 0, .06)); B = rest.clone(); } }
  else { const pick = ss(seg(t, 31.0, 31.25)); const mouth = cHead.localToWorld(V(0, .005, .11)); const rest = CAT_SIT.clone().add(V(.08, .03, .2));
    A = rest.clone().add(V(.13, 0, .06)).lerp(mouth, pick); B = rest.clone().lerp(mouth.clone().add(V(0, -.14, .02)), pick); if (pick >= 1) { const sw = Math.sin(t * 3) * .02; B = mouth.clone().add(V(sw, -.14, .03)); } }
  placeSock(A, B);
  // ── speaker: wakes 19.6, looks, hops to the edge; falls off at 28.8
  const wake = ss(seg(t, 19.6, 20.0));
  spkRingMat.emissive.set(alarm ? (Math.floor(t * 6) % 2 ? C_RED : C_TEAL) : C_TEAL); spkRingMat.emissiveIntensity = .2 + wake * 2.6 * (t < 28.8 ? 1 : (Math.floor(t * 9) % 3 ? .1 : .6) * (1 - seg(t, 30, 31)));
  spkEyeMat.emissive.set(t > 28.8 ? C_GOLD : C_TEAL); spkEyeMat.emissiveIntensity = wake * 3;
  spkLight.intensity = wake * .8 * (t < 28.8 ? 1 : .2);
  if (t < 28.8) {
    const hops = Math.max(0, Math.sin(seg(t, 20.4, 22.2) * Math.PI * 3)) * .04 * (t > 20.4 && t < 22.2 ? 1 : 0);
    spk.position.set(1.17, .53 + hops, lerp(-1.95, -1.86, ss(seg(t, 20.4, 22.2)))); spk.rotation.set(0, lerp(.6, -.5, back(wake, 1.4)), 0);
    if (t > 28.6) spk.rotation.z = Math.sin(seg(t, 28.6, 28.8) * Math.PI) * .15;
  } else { // tip off the front edge, fall, bounce, lie on its side
    const u = t - 28.8; const y0 = .53, g = 4.9; let y = y0 - g * u * u; let rx = Math.min(1, u / .3) * Math.PI / 2;
    if (y < .065) { const u2 = u - Math.sqrt((y0 - .065) / g); y = .065 + Math.max(0, Math.sin(Math.min(1, u2 / .22) * Math.PI)) * .05; }
    spk.position.set(1.17 - u * .08 * (u < .5 ? 1 : 0) - Math.min(u, .5) * 0, y, -1.86 + Math.min(u, .45) * .5); spk.rotation.set(rx, .6, 0);
  }
  // ── kettle: wakes 21.4, turns, slides to edge; topples at 28.35
  const kw = ss(seg(t, 20.6, 21.0));
  drawFace(kScr, t < 20.6 ? 'flat' : t < 28.35 ? (alarm ? 'hunt' : 'wide') : 'dizzy', t < 20.6 ? '#6a7a80' : t < 28.35 ? C_RED : C_GOLD, t >= 28.35 ? { spin: Math.round(t * 12) * .5 } : {});
  if (t < 28.35) { kettle.rotation.set(0, lerp(1.4, -0.69, back(kw, 1.4)), 0); kettle.position.set(lerp(1.05, .95, ss(seg(t, 22.0, 22.9))), .44 + (t > 22.0 && t < 22.9 ? Math.abs(Math.sin(t * 22)) * .012 : 0), lerp(-.55, -.5, ss(seg(t, 22, 22.9))));
    kBody.rotation.z = (t > 28.2) ? Math.sin(seg(t, 28.2, 28.35) * Math.PI * 2) * .1 : 0; kLid.position.set(0, .175, 0); kLid.rotation.set(0, 0, 0); }
  else { const u = seg(t, 28.35, 28.75); kBody.rotation.z = -back(u, 1.2) * Math.PI / 2 * .98; kettle.position.y = .44 + Math.sin(u * Math.PI) * .03;
    const lu = t - 28.45; if (lu > 0) { kLid.position.set(-Math.min(lu, .5) * .25, .175 + Math.max(.0, .25 * lu - 2.5 * lu * lu) * 1.0, Math.min(lu, .5) * .1); kLid.rotation.set(lu * 9, 0, lu * 6); if (lu > .32) { kLid.position.y = .06; kLid.rotation.set(Math.PI / 2 * .9, 0, .4); } } }
  // ── dust puffs: lunge 9.4, drag trail 10-12.5, swipe hits 28.0 / 28.35 / 28.8, cat lands 32.1
  const bursts = [[9.45, sockA], [28.0, null], [28.35, C1], [28.8, C2], [32.1, null]];
  for (let i = 0; i < puffs.length; i++) {
    const pf = puffs[i]; const bi = i % bursts.length; const [bt, at] = bursts[bi]; const age = (t - bt) / .9;
    if (age < 0 || age > 1) { pf.visible = false; continue; }
    const base = at ? at.clone() : vac.position.clone(); const a = hash(i * 3.7) * Math.PI * 2;
    pf.visible = true; pf.position.set(base.x + Math.cos(a) * (.1 + age * .18), .03 + age * .08 * hash(i), base.z + Math.sin(a) * (.1 + age * .18));
    pf.scale.setScalar(.015 + age * .04); pf.material.opacity = .55 * (1 - age);
  }
  // ── motes drift in the shafts
  for (let i = 0; i < motes.length; i++) { const m = motes[i]; const ph = hash(i) * 100; m.position.set(-1.2 + hash(i * 1.3) * 1.9 + Math.sin(t * .3 + ph) * .05, .05 + ((hash(i * 2.1) * 1.6 + t * .02 * (hash(i) - .3)) % 1.6), -1.4 + hash(i * 3.3) * 1.4 + Math.cos(t * .25 + ph) * .05); }
  // ── camera
  const [CP, CT, FOV] = sh.cam(t);
  let shake = 0;
  for (const [s0, amp] of [[9.4, .012], [28.0, .03], [28.35, .02], [28.8, .02], [32.1, .015]]) if (t > s0 && t < s0 + .4) shake = Math.max(shake, (1 - seg(t, s0, s0 + .4)) * amp);
  if (t > 14.9 && t < 23) shake = Math.max(shake, .002);
  const fr = Math.floor(t * 30);
  camera.position.set(CP.x + (hash(fr) - .5) * shake, CP.y + (hash(fr + 9) - .5) * shake, CP.z);
  camera.lookAt(CT); camera.fov = FOV; camera.updateProjectionMatrix();
  // ── overlays
  const docO = ss(seg(t, .25, .6)) * (1 - ss(seg(t, 3.0, 3.4)));
  docEl.style.opacity = docO.toFixed(3); docEl.style.transform = `translateY(${((1 - ss(seg(t, .25, .7))) * 20).toFixed(1)}px)`;
  docEl.querySelector('i').style.width = (ss(seg(t, .4, 1.2)) * 520).toFixed(0) + 'px';
  recEl.style.opacity = (docO * (Math.floor(t * 2) % 2 ? 1 : .35)).toFixed(3);
  flashEl.style.opacity = (t > 28.0 && t < 28.25 ? (1 - seg(t, 28.0, 28.25)) * .35 : 0).toFixed(3);
  let s = '';
  for (const L of LINES) if (t >= L.t - .05 && t < L.t + ldur(L) + .35) s = L.text;
  if (s !== lastSub) { subEl.innerHTML = s; lastSub = s; }
  renderer.render(scene, camera);
};

await document.fonts.load('800 40px Rubik'); await document.fonts.load('400 40px "Russo One"');
window.render(0);
window.READY = true;
