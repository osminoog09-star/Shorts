// «Дневник робота-пылесоса» — Shorts S9-D3, Three.js, deterministic render(t). Original scene (Claude, 12.11.2026).
// Kit (room, robovac, cat, sock, speaker, kettle, LED faces, post) reused from longform/vacuum_wild.
import * as THREE from 'three';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makePost } from './vendor/post.js';
const SS = Number(new URLSearchParams(location.search).get('ss') || 2);   // supersampling; ?ss=1 for quick previews

const W = 1080, H = 1920;

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

// ───────── narration (Denis) → cuts ─────────
// timeline.json is written by mix.py from the real voice files; without it the lengths are estimated (stills before the voice exists).
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const TEXT = [
  { id: 'v0', seg: 0, text: 'Вот куда пропадают <b>ваши носки</b>.' },
  { id: 'v1', seg: 1, text: 'Меня купили, чтобы в доме было <b>чисто</b>.' },
  { id: 'v2', seg: 2, text: 'На меня сел <b>кот</b>. Катаю его второй час.' },
  { id: 'v3', seg: 3, text: 'Съел носок. Меня перевернули и назвали <b>идиотом</b>.' },
  { id: 'v4', seg: 4, text: 'Под диваном <b>кто-то живёт</b>. Туда я больше не езжу.' },
  { id: 'v5', seg: 5, text: 'Хозяин хвалит <b>колонку</b>. А она просто включает музыку.' },
  { id: 'v6', seg: 6, text: 'Хозяин ищет <b>второй носок</b>.' },
  { id: 'v7', seg: 6, text: 'Я молчу. Это моя <b>месть</b>.' },
];
const DAYS = ['', 'ДЕНЬ 1', 'ДЕНЬ 3', 'ДЕНЬ 9', 'ДЕНЬ 20', 'ДЕНЬ 31', 'ДЕНЬ 47'];
const TL = (await J('timeline.json')) || (() => {            // fallback: same layout rule as mix.py
  const lines = {}, segs = []; let t = 0;
  for (let s = 0; s < 7; s++) { const a = t; let c = a + (s ? .12 : .15);
    for (const L of TEXT.filter(x => x.seg === s)) { const d = Math.max(1.2, L.text.replace(/<[^>]+>/g, '').length * .075 + (s && L.id !== 'v7' ? .9 : 0)); lines[L.id] = { t: +c.toFixed(3), d }; c += d + .4; }
    t = c - .4 + (s === 6 ? 1.0 : .32); segs.push({ a, b: t }); }
  return { dur: t, lines, segs };
})();
const DUR = TL.dur; window.DUR = DUR;
const LINES = TEXT.map(L => ({ ...L, t: TL.lines[L.id].t, d: TL.lines[L.id].d }));
const SEGS = TL.segs.map((s, i) => ({ ...s, day: DAYS[i] }));
window.EV = LINES.map(L => ({ t: L.t, type: 'voice', id: L.id }));

// ───────── renderer ─────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W * SS, H * SS, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#2a1d17');
scene.fog = new THREE.Fog('#3a2a20', 7, 16);
const camera = new THREE.PerspectiveCamera(45, W / H, 0.02, 40);
// image-based light for reflections on gloss/plastic (audit R4)
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture; scene.environmentIntensity = .38;
// post: GTAO + physical DOF + bloom + grade (audit R2, R3, R5)
const post = makePost(renderer, scene, camera, W, H, { ssaa: SS, ao: true, aoRadius: .12, aoScale: 1.6, aoAmt: .9 });
post.bloom.strength = .32; post.bloom.radius = .45; post.bloom.threshold = 1.15;
Object.assign(post.vig.uniforms.amt, { value: .18 }); post.vig.uniforms.warm.value = .35; post.vig.uniforms.contrast.value = .18; post.vig.uniforms.sat.value = 1.08;
post.dof.maxCoc = 14;
// height map (canvas) → tangent-space normal map
function normalFrom(w, h, drawHeight, strength = 2, rep) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); drawHeight(g, w, h);
  const src = g.getImageData(0, 0, w, h).data, out = g.createImageData(w, h), H_ = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = (H_(x + 1, y) - H_(x - 1, y)) * strength, dy = (H_(x, y + 1) - H_(x, y - 1)) * strength, l = Math.hypot(dx, dy, 1), i = (y * w + x) * 4;
    out.data[i] = (-dx / l * .5 + .5) * 255; out.data[i + 1] = (dy / l * .5 + .5) * 255; out.data[i + 2] = (1 / l * .5 + .5) * 255; out.data[i + 3] = 255;
  }
  g.putImageData(out, 0, 0); const t = new THREE.CanvasTexture(c); t.anisotropy = 8;
  if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
  return t;
}

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
// relief (audit P3): plank joints + grain, rug pile, fabric weave, wall plaster
const nWood = normalFrom(512, 512, (g, w, h) => { g.fillStyle = '#888'; g.fillRect(0, 0, w, h); const n = 5;
  for (let i = 0; i < n; i++) { const y = i * h / n; g.fillStyle = '#222'; g.fillRect(0, y + h / n - 3, w, 3);
    for (let s = 0; s < 3; s++) { const x0 = ((i % 2) * .5 + s) * w / 2.5 - 40; g.fillRect(x0 + w / 2.5 - 3, y, 3, h / n); }
    for (let k = 0; k < 60; k++) { g.fillStyle = `rgba(${hash(k + i * 60) > .5 ? 200 : 60},${hash(k + i * 60) > .5 ? 200 : 60},${hash(k + i * 60) > .5 ? 200 : 60},.25)`; g.fillRect(0, y + hash(k * 3 + i) * (h / n - 4), w, 1); } } }, 3, [8, 8]);
const nRug = normalFrom(512, 512, (g, w, h) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, h); for (let k = 0; k < 60000; k++) { const v = hash(k * 1.31) * 255 | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(hash(k * 2.17) * w, hash(k * 3.71) * h, 2, 2); } }, 4, [6, 6]);
const nWeave = normalFrom(256, 256, (g, w, h) => { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const v = 128 + 60 * Math.sin(x * .8) * Math.sin(y * .8) + 30 * (hash(x * 7 + y * 13) - .5); g.fillStyle = `rgb(${v | 0},${v | 0},${v | 0})`; g.fillRect(x, y, 1, 1); } }, 1.6, [10, 10]);
const nWall = normalFrom(256, 256, (g, w, h) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, h); for (let k = 0; k < 9000; k++) { const v = 100 + hash(k * 1.7) * 60 | 0; g.fillStyle = `rgba(${v},${v},${v},.5)`; g.beginPath(); g.arc(hash(k * 2.3) * w, hash(k * 3.9) * h, 1 + hash(k) * 3, 0, 7); g.fill(); } }, 1.2, [4, 3]);
const mat = {
  floor: new THREE.MeshPhysicalMaterial({ map: texWood, normalMap: nWood, normalScale: new THREE.Vector2(.6, .6), roughness: .38, clearcoat: .35, clearcoatRoughness: .35 }),
  wall: new THREE.MeshStandardMaterial({ map: texWall, normalMap: nWall, normalScale: new THREE.Vector2(.4, .4), roughness: .92 }),
  rug: new THREE.MeshStandardMaterial({ map: texRug, normalMap: nRug, normalScale: new THREE.Vector2(1.2, 1.2), roughness: 1 }),
  fabric: new THREE.MeshPhysicalMaterial({ map: texFabric, normalMap: nWeave, normalScale: new THREE.Vector2(.7, .7), roughness: .95, sheen: 1, sheenColor: new THREE.Color('#c9d6db'), sheenRoughness: .6 }),
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
// v2 (audit P1): lathe-turned shell with bevels, glossy clear-coated lid, rubber bumper, wheels, buttons, chrome trim
const P2 = (a) => a.map(([r, y]) => new THREE.Vector2(r, y));
const gloss = (c, o = {}) => new THREE.MeshPhysicalMaterial({ color: c, roughness: .22, clearcoat: 1, clearcoatRoughness: .08, ...o });
add(new THREE.LatheGeometry(P2([[0, .012], [.178, .012], [.192, .016], [.199, .026], [.2, .06]]), 96), gloss('#2b2f36', { roughness: .4, clearcoat: .5 }), 0, 0, 0, vBody);
add(new THREE.LatheGeometry(P2([[.2, .06], [.2, .078], [.197, .088], [.19, .094], [.176, .097], [0, .099]]), 96), gloss('#f2efe9'), 0, 0, 0, vBody);
add(new THREE.TorusGeometry(.2, .0025, 8, 96), mat.chrome, 0, .06, 0, vBody).rotation.x = Math.PI / 2;            // chrome trim
add(new THREE.TorusGeometry(.15, .0016, 6, 96), M('#c9c3b8', { r: .35 }), 0, .0985, 0, vBody).rotation.x = Math.PI / 2; // lid seam
add(new THREE.LatheGeometry(P2([[0, .099], [.052, .099], [.055, .104], [.055, .118], [.05, .124], [0, .125]]), 64), gloss('#f2efe9'), 0, 0, -.06, vBody); // lidar dome
const lidarMat = new THREE.MeshStandardMaterial({ color: '#0a1a20', emissive: C_TEAL, emissiveIntensity: .8 });
const lidar = add(new THREE.CylinderGeometry(.056, .056, .008, 48), lidarMat, 0, .11, -.06, vBody, false, false);
const btnMat = gloss('#3a3f47', { roughness: .3 });
for (let i = 0; i < 3; i++) { add(new THREE.CylinderGeometry(.011, .012, .004, 24), btnMat, -.045 + i * .045, .1, .085, vBody); add(new THREE.TorusGeometry(.0115, .0012, 6, 24), mat.chrome, -.045 + i * .045, .102, .085, vBody).rotation.x = Math.PI / 2; }
add(new THREE.CylinderGeometry(.205, .205, .012, 96, 1, true, -Math.PI * .45, Math.PI * .9), new THREE.MeshPhysicalMaterial({ color: '#0b0d10', roughness: .08, clearcoat: 1, side: THREE.DoubleSide }), 0, .068, 0, vBody); // dark sensor glass band (front)
const vScr = makeScreen(256, 128); add(new THREE.PlaneGeometry(.15, .075), vScr.m, 0, .056, .206, vBody, false, false);
const bumper = add(new THREE.TorusGeometry(.201, .009, 10, 64, Math.PI * .9), M('#3c4148', { r: .85 }), 0, .03, 0, vBody); bumper.rotation.x = Math.PI / 2; bumper.rotation.z = Math.PI * .05;
for (const s of [-1, 1]) { const wh = add(new THREE.CylinderGeometry(.03, .03, .022, 32), M('#15171a', { r: .9 }), s * .135, .03, -.01, vBody); wh.rotation.z = Math.PI / 2; add(new THREE.CylinderGeometry(.012, .012, .024, 16), mat.steel, s * .135, .03, -.01, vBody).rotation.z = Math.PI / 2; }
const brush = new THREE.Group(); brush.position.set(.13, .01, .13); vBody.add(brush);
add(new THREE.CylinderGeometry(.012, .014, .008, 20), M('#1c1d20'), 0, 0, 0, brush);
for (let i = 0; i < 3; i++) { const pv = new THREE.Group(); pv.rotation.y = i * Math.PI * 2 / 3; brush.add(pv);
  for (let k = 0; k < 7; k++) { const b = add(new THREE.CylinderGeometry(.0012, .0008, .075, 4), M('#2c2c2e', { r: .6 }), 0, 0, 0, pv, false, false); b.rotation.set(Math.PI / 2, (k - 3) * .045, 0); b.position.set((k - 3) * .0012, -.002, .04); } }
const vLight = new THREE.PointLight(C_RED, 0, 1.2, 2); vLight.position.set(0, .12, .25); vac.add(vLight);

// ───────── kettle (ally #2) ─────────
const kettle = new THREE.Group(); kettle.position.set(1.05, .44, -0.55); room.add(kettle);
const kBody = new THREE.Group(); kettle.add(kBody);
const ceramic = gloss('#f1e7d3', { roughness: .18 });
add(new THREE.LatheGeometry(P2([[0, 0], [.074, 0], [.078, .004], [.078, .014], [.074, .016], [0, .016]]), 64), mat.chrome, 0, 0, 0, kBody);   // base
add(new THREE.LatheGeometry(P2([[0, .016], [.079, .016], [.082, .024], [.08, .06], [.072, .12], [.062, .165], [.058, .172], [0, .172]]), 64), ceramic, 0, 0, 0, kBody);
add(new THREE.TorusGeometry(.081, .002, 8, 64), mat.chrome, 0, .028, 0, kBody).rotation.x = Math.PI / 2;
const kLid = new THREE.Group(); kLid.position.y = .175; kBody.add(kLid);
add(new THREE.LatheGeometry(P2([[0, -.004], [.058, -.004], [.056, .006], [.04, .014], [0, .016]]), 48), ceramic, 0, 0, 0, kLid); add(new THREE.SphereGeometry(.016, 20, 14), mat.chrome, 0, .02, 0, kLid);
add(new THREE.TorusGeometry(.05, .011, 16, 32, Math.PI * 1.1), gloss('#202328'), -.08, .1, 0, kBody).rotation.z = Math.PI / 2 + .1;
add(new THREE.CylinderGeometry(.011, .022, .075, 24), ceramic, .085, .14, 0, kBody).rotation.z = -1.0;
const kScr = makeScreen(); add(new THREE.PlaneGeometry(.07, .055), kScr.m, 0, .09, .0815, kBody, false, false).rotation.x = -.1;
kettle.rotation.y = -0.9;

// ───────── smart speaker (ally #1) ─────────
const spk = new THREE.Group(); spk.position.set(1.17, .53, -1.95); room.add(spk);
const spkBody = new THREE.Group(); spk.add(spkBody);
add(new THREE.CylinderGeometry(.065, .07, .17, 40), mat.fabric, 0, .085, 0, spkBody);
add(new THREE.LatheGeometry(P2([[.066, .168], [.067, .176], [.062, .182], [0, .183]]), 48), gloss('#1d2024', { roughness: .25 }), 0, 0, 0, spkBody);
add(new THREE.LatheGeometry(P2([[0, 0], [.071, 0], [.072, .006], [.07, .01], [0, .01]]), 48), gloss('#1d2024', { roughness: .35 }), 0, 0, 0, spkBody);
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

// ───────── cat (v2, audit C1–C5): tabby texture, shell fur, two-bone legs, detailed face ─────────
const texTabby = canvasTex(1024, 512, (g, w, h) => {      // sphere UV: u = around the vertical axis, v: top(back)=canvas top, bottom(belly)=canvas bottom
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#b8622a'); gr.addColorStop(.35, '#e08a3e'); gr.addColorStop(.62, '#eaa35a'); gr.addColorStop(.78, '#f6dcb8'); gr.addColorStop(1, '#fbeedd');
  g.fillStyle = gr; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 22; i++) {                           // wavy mackerel stripes, fading toward the belly
    const x0 = (i + .5) * w / 22; g.beginPath();
    for (let y = 0; y <= h * .72; y += 6) { const x = x0 + Math.sin(y * .035 + i) * 9 + (vnoise(y * .02 + i * 7) - .5) * 14; const wd = (7 + hash(i) * 6) * (1 - y / (h * .8)); y ? g.lineTo(x + wd, y) : g.moveTo(x + wd, y); }
    for (let y = h * .72; y >= 0; y -= 6) { const x = x0 + Math.sin(y * .035 + i) * 9 + (vnoise(y * .02 + i * 7) - .5) * 14; const wd = (7 + hash(i) * 6) * (1 - y / (h * .8)); g.lineTo(x - wd, y); }
    g.closePath(); g.fillStyle = 'rgba(150,70,22,.55)'; g.fill();
  }
  for (let k = 0; k < 40000; k++) { const v = hash(k * 1.7); g.strokeStyle = v > .5 ? 'rgba(255,225,180,.09)' : 'rgba(110,50,14,.09)'; g.beginPath(); const x = hash(k * 3.3) * w, y = hash(k * 5.1) * h; g.moveTo(x, y); g.lineTo(x + (hash(k) - .5) * 2, y + 5); g.stroke(); }
});
const texHead = canvasTex(512, 256, (g, w, h) => {        // head: solid ginger, «M» forehead stripes on the front (u≈.5 after rotation), cream lower face
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#c86e30'); gr.addColorStop(.5, '#e3903f'); gr.addColorStop(.72, '#eda861'); gr.addColorStop(1, '#f8e2c4'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(150,68,20,.6)'; g.lineCap = 'round';
  for (const [x, l, wd] of [[-.05, .3, 7], [0, .34, 8], [.05, .3, 7], [-.11, .22, 5], [.11, .22, 5]]) { g.lineWidth = wd; g.beginPath(); g.moveTo(w * (.5 + x), h * .04); g.lineTo(w * (.5 + x * 1.15), h * l); g.stroke(); }
  for (const s of [-1, 1]) for (let i = 0; i < 3; i++) { g.lineWidth = 6; g.beginPath(); g.moveTo(w * (.5 + s * (.17 + i * .045)), h * .25); g.quadraticCurveTo(w * (.5 + s * (.2 + i * .045)), h * .38, w * (.5 + s * (.17 + i * .05)), h * .5); g.stroke(); }
  for (let k = 0; k < 16000; k++) { const v = hash(k * 1.9); g.strokeStyle = v > .5 ? 'rgba(255,225,180,.08)' : 'rgba(110,50,14,.08)'; g.beginPath(); const x = hash(k * 3.1) * w, y = hash(k * 5.3) * h; g.moveTo(x, y); g.lineTo(x, y + 4); g.stroke(); }
});const texFurNoise = canvasTex(256, 256, (g, w, h) => {    // strand mask for the fur shells (alpha = strand length)
  g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 14000; k++) { const v = (40 + hash(k * 9.1) * 215) | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(hash(k * 2.3) * w, hash(k * 4.7) * h, 1.4, 1.4); }
}, [7, 7]); texFurNoise.colorSpace = THREE.NoColorSpace;
const furMats = [];                                         // {m, base} — dimmed together while the cat hides under the sofa
const fm = (o, group = 'body') => { const m = new THREE.MeshPhysicalMaterial({ roughness: .92, sheen: .8, sheenRoughness: .45, sheenColor: new THREE.Color('#ffd7a6'), ...o }); furMats.push({ m, base: m.color.clone(), group }); return m; };
const catMat = { coat: fm({ map: texTabby }), head: fm({ map: texHead }), plain: fm({ color: '#e1893c' }), cream: fm({ color: '#f8e6cc' }), pink: fm({ color: '#e7928f', sheen: 0, roughness: .5 }),
  legLit: fm({ color: '#e1893c' }, 'leg1'), pawLit: fm({ color: '#f8e6cc' }, 'leg1') };
const SHELLS = 12;
const shellMats = new Map();
function furify(mesh, len = .012, radial = false) {        // stack of slightly larger cut-out copies = fluffy silhouette
  const base = mesh.material, r = Math.min(Math.abs(mesh.scale.x), Math.abs(mesh.scale.y), Math.abs(mesh.scale.z)) || .02, rr = radial ? (mesh.geometry.parameters.radiusTop || .02) : r;
  for (let k = 1; k <= SHELLS; k++) {
    const key = base.uuid + k; let m = shellMats.get(key);
    if (!m) { m = base.clone(); m.alphaMap = texFurNoise; m.alphaTest = .12 + .8 * k / SHELLS; m.transparent = false; m.side = THREE.FrontSide;
      const shade = lerp(.78, 1.08, k / SHELLS); m.color = base.color.clone().multiplyScalar(shade);
      furMats.push({ m, base: m.color.clone(), group: furMats.find(f => f.m === base)?.group || 'body' }); shellMats.set(key, m); }
    const s = new THREE.Mesh(mesh.geometry, m); s.castShadow = false; s.receiveShadow = true;
    const f = 1 + k * len; radial ? s.scale.set(f, 1, f) : s.scale.setScalar(f); mesh.add(s);   // len = growth per shell as a fraction of the part's size
  }
  return mesh;
}
const cat = new THREE.Group(); room.add(cat);
const cBody = new THREE.Group(); cat.add(cBody);                      // pivot at the hips (rear), pitch for sitting
const torso = furify(add(new THREE.SphereGeometry(1, 48, 32), catMat.coat, 0, .005, .14, cBody)); torso.scale.set(.115, .112, .215); torso.rotation.x = -.06;
torso.children.forEach(c => c.scale.multiplyScalar(1));
const chest = furify(add(new THREE.SphereGeometry(1, 32, 24), catMat.cream, 0, -.02, .262, cBody), .01); chest.scale.set(.078, .09, .075);
const haunch = []; for (const s of [-1, 1]) { const hh = furify(add(new THREE.SphereGeometry(1, 32, 24), catMat.coat, s * .068, -.005, .045, cBody)); hh.scale.set(.06, .088, .105); haunch.push(hh); }
const neck = new THREE.Group(); neck.position.set(0, .08, .3); cBody.add(neck);
const ruff = furify(add(new THREE.SphereGeometry(1, 32, 24), catMat.cream, 0, -.01, -.005, neck), .018); ruff.scale.set(.075, .07, .06);  // neck ruff
const cHead = new THREE.Group(); neck.add(cHead);
const skull = furify(add(new THREE.SphereGeometry(1, 48, 36), catMat.head, 0, .06, .025, cHead), .004); skull.scale.set(.098, .086, .086); skull.rotation.y = -Math.PI / 2;
for (const s of [-1, 1]) { const ch = furify(add(new THREE.SphereGeometry(1, 32, 20), catMat.plain, s * .048, .028, .048, cHead), .018); ch.scale.set(.04, .033, .036); } // cheek fluff
for (const s of [-1, 1]) { const mz = furify(add(new THREE.SphereGeometry(1, 24, 16), catMat.cream, s * .019, .018, .1, cHead), .005); mz.scale.set(.028, .022, .024); }
furify(add(new THREE.SphereGeometry(1, 20, 14), catMat.cream, 0, -.004, .09, cHead), .006).scale.set(.026, .02, .022); // chin
// nose (heart) + mouth (ω)
const heart = new THREE.Shape(); heart.moveTo(0, -.006); heart.bezierCurveTo(-.012, .002, -.009, .009, 0, .005); heart.bezierCurveTo(.009, .009, .012, .002, 0, -.006);
const nose = add(new THREE.ExtrudeGeometry(heart, { depth: .004, bevelEnabled: true, bevelThickness: .002, bevelSize: .0015, bevelSegments: 3 }), new THREE.MeshPhysicalMaterial({ color: '#d9787a', roughness: .35, clearcoat: .6 }), 0, .044, .118, cHead, false, false);
nose.rotation.x = .35;
const mouthMat = new THREE.MeshStandardMaterial({ color: '#5a3020', roughness: .6 });
for (const s of [-1, 1]) { const mo = add(new THREE.TorusGeometry(.009, .0014, 6, 16, Math.PI), mouthMat, s * .009, .028, .117, cHead, false, false); mo.rotation.set(0, 0, Math.PI); }
add(new THREE.CylinderGeometry(.0013, .0013, .01, 6), mouthMat, 0, .034, .118, cHead, false, false);
const ears = []; for (const s of [-1, 1]) {
  const eg = new THREE.Group(); eg.position.set(s * .052, .125, .005); eg.rotation.set(-.15, s * -.25, -s * .32); cHead.add(eg);
  const outer = furify(add(new THREE.ConeGeometry(.036, .075, 32), catMat.plain, 0, .032, 0, eg), .004); outer.scale.z = .55;
  const inner = add(new THREE.ConeGeometry(.024, .056, 24), catMat.pink, 0, .026, .009, eg); inner.scale.z = .35;
  for (let i = 0; i < 5; i++) { const tf = add(new THREE.ConeGeometry(.003, .03, 5), catMat.cream, (i - 2) * .006, .018, .014, eg, false, false); tf.rotation.set(-.4, 0, (i - 2) * .25); }
  ears.push(eg);
}
const texIris = canvasTex(128, 128, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h / 2, 4, w / 2, h / 2, w / 2); gr.addColorStop(0, '#f4e34a'); gr.addColorStop(.55, '#b8d23c'); gr.addColorStop(.85, '#6f9a2a'); gr.addColorStop(1, '#2b3a12'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 90; k++) { const a = k / 90 * Math.PI * 2; g.strokeStyle = `rgba(80,100,20,${.15 + hash(k) * .2})`; g.beginPath(); g.moveTo(w / 2 + Math.cos(a) * 14, h / 2 + Math.sin(a) * 14); g.lineTo(w / 2 + Math.cos(a) * 60, h / 2 + Math.sin(a) * 60); g.stroke(); } });
const catEyes = []; for (const s of [-1, 1]) {
  const eg = new THREE.Group(); eg.position.set(s * .038, .072, .1); eg.rotation.y = s * .3; cHead.add(eg);
  const ring = add(new THREE.TorusGeometry(.0225, .0035, 10, 32), new THREE.MeshStandardMaterial({ color: '#2a160a', roughness: .7 }), 0, 0, .004, eg, false, false); ring.scale.y = .92;
  const ballMat = new THREE.MeshStandardMaterial({ map: texIris, roughness: .25, emissive: '#c8ff40', emissiveIntensity: 0 });
  const ball = add(new THREE.SphereGeometry(.022, 32, 24), ballMat, 0, 0, 0, eg, false, false); ball.rotation.y = -Math.PI / 2;
  const pup = add(new THREE.SphereGeometry(.0222, 24, 16), new THREE.MeshStandardMaterial({ color: '#050403', roughness: .2 }), 0, 0, .0032, eg, false, false); pup.scale.set(.3, .95, .95);
  add(new THREE.SphereGeometry(.0232, 32, 24), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: 0, transparent: true, opacity: .12, clearcoat: 1, envMapIntensity: 2.2 }), 0, 0, .0004, eg, false, false); // cornea gloss
  add(new THREE.SphereGeometry(.0042, 12, 8), new THREE.MeshBasicMaterial({ color: '#ffffff' }), .007, .008, .021, eg, false, false);  // catch-light
  const lid = add(new THREE.SphereGeometry(.0248, 24, 16, 0, Math.PI * 2, 0, Math.PI * .5), catMat.plain, 0, 0, 0, eg, false, false); // rotates down to blink
  catEyes.push({ eg, ball, pup, lid });
}
const whiskers = []; for (const s of [-1, 1]) for (let i = 0; i < 4; i++) { const wsk = add(new THREE.CylinderGeometry(.0007, .0003, .13, 4), new THREE.MeshStandardMaterial({ color: '#fffaf0', roughness: .3 }), s * .075, .022 + i * .006 - .008, .098, cHead, false, false); wsk.rotation.set(0, (i - 1.5) * .08, s * (Math.PI / 2 - .14 + i * .09)); whiskers.push(wsk); }
// legs: two segments (upper/lower) solved with 2-bone IK; shoulder/hip anchors in cBody, paws are world targets
const LEGS = [{ a: V(-.055, -.035, .26), front: 1, L1: .1, L2: .105 }, { a: V(.055, -.035, .26), front: 1, L1: .1, L2: .105 },
  { a: V(-.07, -.03, .04), front: 0, L1: .085, L2: .095 }, { a: V(.07, -.03, .04), front: 0, L1: .085, L2: .095 }];
const legUp = [], legLo = [], legJ = [], pawMeshes = [];
for (let i = 0; i < 4; i++) {
  const mU = i === 1 ? catMat.legLit : catMat.plain, mP = i === 1 ? catMat.pawLit : catMat.cream;
  legUp.push(furify(add(new THREE.CylinderGeometry(.032, .022, 1, 20), mU, 0, 0, 0), .028, true));
  legLo.push(furify(add(new THREE.CylinderGeometry(.021, .017, 1, 20), mU, 0, 0, 0), .022, true));
  legJ.push(add(new THREE.SphereGeometry(.022, 20, 14), mU, 0, 0, 0));
  const paw = new THREE.Group(); room.add(paw);
  const pad = furify(add(new THREE.SphereGeometry(1, 24, 16), mP, 0, .012, .006, paw), .004); pad.scale.set(.024, .016, .03);
  for (let k = 0; k < 4; k++) add(new THREE.SphereGeometry(.0085, 12, 8), mP, (k - 1.5) * .011, .009, .03 - Math.abs(k - 1.5) * .004, paw);
  pawMeshes.push(paw);
}
const legMeshes = legUp;   // kept for the reach-lighting code path
// tail: chain of furry segments from the rump
const tailRoot = new THREE.Group(); tailRoot.position.set(0, .03, -.06); cBody.add(tailRoot);
const tail = []; { let par = tailRoot; for (let i = 0; i < 11; i++) { const g = new THREE.Group(); g.position.z = i ? -.036 : 0; par.add(g); const sgm = furify(add(new THREE.SphereGeometry(1, 20, 14), i > 8 ? catMat.cream : (i % 3 === 1 ? catMat.plain : catMat.coat), 0, 0, -.018, g), .012); sgm.scale.set(.021 - i * .0008, .021 - i * .0008, .026); tail.push(g); par = g; } }
function catDim(dim, legLit) { for (const f of furMats) f.m.color.copy(f.base).multiplyScalar(f.group === 'leg1' ? (legLit ? 1 : dim) : dim); for (const f of furMats) f.m.sheen = (f.group === 'leg1' && legLit) ? .8 : .8 * dim; }
const _ikD = V(0, 0, 0), _ikP = V(0, 0, 0);
function ik(A, P, L1, L2, pole) {                       // returns elbow/knee position
  _ikD.copy(P).sub(A); const d = _ikD.length(); const L = L1 + L2; _ikD.normalize();
  if (d >= L * .999) return A.clone().addScaledVector(_ikD, d * L1 / L);
  const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d), h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
  _ikP.copy(pole).addScaledVector(_ikD, -pole.dot(_ikD)).normalize();
  return A.clone().addScaledVector(_ikD, a).addScaledVector(_ikP, h);
}

const litLeg = catMat.legLit, litPaw = catMat.pawLit;
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
  const fwd = V(Math.sin(p.ry), 0, Math.cos(p.ry));
  for (let i = 0; i < 4; i++) {
    const Lg = LEGS[i], A = cBody.localToWorld(Lg.a.clone()), P = p.paws[i].clone().add(V(0, .012, 0));
    const pole = fwd.clone().multiplyScalar(Lg.front ? -1 : 1).add(V(0, Lg.front ? -.2 : .3, 0));   // elbow back, knee forward
    const E = ik(A, P, Lg.L1, Lg.L2, pole);
    stick(legUp[i], A, E); stick(legLo[i], E, P); legJ[i].position.copy(E);
    pawMeshes[i].position.copy(p.paws[i]).add(V(0, -.012, 0)); pawMeshes[i].rotation.y = p.ry;
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
const shafts = []; for (let i = 0; i < 4; i++) { const s = add(new THREE.PlaneGeometry(.35 + i * .08, 3.2), new THREE.MeshBasicMaterial({ map: shaftTex, transparent: true, opacity: .035, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }), -0.7 + i * .28, 1.0, -1.3, room, false, false); s.rotation.set(-.75, .0, .12 - i * .05); shafts.push(s); }
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

// ───────── choreography: «Дневник робота-пылесоса» (Claude, 12.11.2026) ─────────
// Seven beats cut on the narration (timeline.json): hook + six diary days. Each beat poses the kit from scratch.
const SOCK0A = V(-0.3, .03, -1.02), SOCK0B = V(-0.44, .03, -1.16);
const S0 = V(0.2, 0, -0.05), R = V(0.0, 0, -0.5);
const H_SOCK = Math.atan2(SOCK0A.x - S0.x, SOCK0A.z - S0.z);
const fwdOf = r => V(Math.sin(r), 0, Math.cos(r));
const F = fwdOf(H_SOCK), PP = V(-F.z, 0, F.x);
const TGT = SOCK0A.clone().setY(0).addScaledVector(F, -.42);
const BITE = SOCK0A.clone().setY(0).addScaledVector(F, -.2);
const CC = V(0.2, 0, -0.55), CR = .3;
const segAt = t => { let i = 0; for (let k = 0; k < SEGS.length; k++) if (t >= SEGS[k].a) i = k; return i; };
const SPLIT5 = SEGS[5].a + (SEGS[5].b - SEGS[5].a) * .56;          // day 31: speaker → cut to the vacuum's face
const SPLIT6 = LINES[7].t - .12;                                    // day 47: innocent → cut on «Я молчу»

const subEl = document.getElementById('sub'), flashEl = document.getElementById('flash'), docEl = document.getElementById('doc');
const dayEl = docEl.querySelector('b'), barEl = docEl.querySelector('i');
let lastSub = '', lastDay = '';

window.render = t => renderScene(t);
function renderScene(t) {
  const si = segAt(t), S = SEGS[si], u = t - S.a, L = S.b - S.a;
  // ── defaults (every beat starts clean)
  let P = S0.clone(), r = H_SOCK, tilt = 0, bob = 0, flip = 0, rock = 0, brushSpeed = 8;
  let vExpr = 'open', vCol = C_TEAL, vp = {};
  let lidarCol = C_TEAL, lidarI = .9 + Math.sin(t * 5) * .3;
  const cp = { t, x: -0.36, y: 0, z: -1.86, ry: 0, hipY: .075, pitch: 0, squash: .72, nod: .28, turn: .12, glow: 0, blink: 1, pupil: .22, tailCurl: .4, tailLift: -.1, tailWave: .2, mode: 'crouch' };
  let catDimV = .07, sockOn = false, sA = SOCK0A.clone(), sB = SOCK0B.clone();
  let spkWake = 0, spkHop = 0, spkYaw = .6, spkZ = -1.95;
  let CP, CT, FOV, AP = 8, shake = 0, puffAt = null, puffAge = -1;

  if (si === 0) {            // hook: the lunge and the gulp
    const lunge = eo(seg(u, .22, .5));
    P = TGT.clone().lerp(BITE, lunge); tilt = Math.sin(seg(u, .22, .62) * Math.PI) * .09; brushSpeed = 40;
    const gulp = eo(seg(u, .5, 1.25));
    vExpr = u < .55 ? 'hunt' : 'open'; vCol = u < .55 ? C_GOLD : C_TEAL; if (u > .55) vp = { blink: u > 1.5 && u < 1.7 ? 1 : 0 };
    bob = u > .5 && u < 1.3 ? Math.sin(u * 44) * .003 : 0;
    const pull = SOCK0A.clone().sub(SOCK0B).setY(0).normalize().multiplyScalar(gulp * .46);
    sockOn = gulp < .97; sA = SOCK0A.clone().add(pull); sB = SOCK0B.clone().add(pull);
    const k = ss(seg(u, 0, L));
    CP = V(lerp(-1.5, -1.42, k), .22, lerp(-.72, -.64, k)); CT = V(lerp(-.22, -.16, k), .06, -.88); FOV = 38; AP = 9;
    if (u > .48 && u < .9) shake = (1 - seg(u, .48, .9)) * .014;
  } else if (si === 1) {     // day 1: proud and new
    const k = ss(seg(u, 0, L));
    r = lerp(H_SOCK + 1.3, H_SOCK, back(seg(u, .25, .75), 2.4)); tilt = (u > .25 && u < .8) ? Math.sin(seg(u, .25, .8) * Math.PI) * .05 : 0;
    P = S0.clone().lerp(TGT, ss(seg(u, 1.0, L)) * .22); brushSpeed = u > 1 ? 40 : 8;
    vp = { blink: (u > 1.6 && u < 1.78) ? 1 : 0 }; lidarI = 1.2 + Math.sin(t * 8) * .5;
    sockOn = true;
    CP = V(lerp(-0.68, -0.6, k), .1, lerp(-1.4, -1.3, k)); CT = V(.2, .07, -.05); FOV = lerp(30, 27, k); AP = 11;
  } else if (si === 2) {     // day 3: the cat's taxi
    const phi = 1.2 + u * .6;
    P = CC.clone().add(V(Math.sin(phi) * CR, 0, Math.cos(phi) * CR)); r = phi + Math.PI / 2; bob = Math.sin(t * 30) * .0015; brushSpeed = 40;
    vExpr = 'sad'; vCol = '#7fa8ff'; vp = { tear: Math.round((u % 1.6) / 1.6 * 8) / 8 }; lidarCol = '#4a6fff';
    Object.assign(cp, { x: P.x, z: P.z, y: .105, ry: r, hipY: .07, pitch: -.75, squash: 1, nod: .45, turn: Math.sin(t * .7) * .15, mode: 'sit', tailCurl: .9, tailLift: -.45, tailWave: .15, pupil: .2,
      blink: (u > 1.9 && u < 2.5) ? Math.sin(seg(u, 1.9, 2.5) * Math.PI) * .95 : 0 });
    catDimV = 1;
    const a = lerp(-.35, .25, ss(seg(u, 0, L)));
    CP = CC.clone().add(V(Math.sin(a) * 1.75, lerp(.42, .36, seg(u, 0, L)), Math.cos(a) * 1.75)); CT = P.clone().add(V(0, .36, 0)); FOV = 40; AP = 8;
  } else if (si === 3) {     // day 9: flipped on its back, the evidence next to it
    P = R.clone(); r = 2.32; flip = 1; rock = Math.sin(u * 5.2) * .09 * Math.exp(-u * .55); brushSpeed = 55;
    vExpr = 'dizzy'; vCol = C_GOLD; vp = { spin: Math.round(t * 12) * .5 };
    lidarCol = C_RED; lidarI = Math.sin(t * 14) > 0 ? 2.4 : .3;
    sockOn = true; sA = R.clone().add(V(.3, .03, .02)); sB = sA.clone().add(V(.16, 0, .12));
    const k = ss(seg(u, 0, L));
    CP = V(lerp(-.86, -.78, k), lerp(.5, .46, k), lerp(.34, .26, k)); CT = V(.1, .0, -.46); FOV = lerp(40, 37, k); AP = 10;
    if (u < .35) shake = (1 - seg(u, 0, .35)) * .012;
  } else if (si === 4) {     // day 20: something lives under the sofa
    const see = ss(seg(u, 1.0, 1.35));
    P = R.clone().addScaledVector(F, -ss(seg(u, 1.6, L)) * .34); tilt = see * (.02 + Math.sin(t * 26) * .012); bob = see * Math.sin(t * 40) * .002;
    vExpr = see > .5 ? 'wide' : 'open'; if (see <= .5) vp = { look: -.4 };
    Object.assign(cp, { glow: see * .95, blink: 1 - see, pupil: lerp(.22, .5, ss(seg(u, 1.6, 2.4))) });
    const k = ss(seg(u, 0, L));
    CP = R.clone().addScaledVector(F, -.42).add(V(.16, lerp(.2, .16, k), 0)); CT = V(-0.42, lerp(.11, .08, k), -1.3); FOV = lerp(40, 34, k); AP = 9;
  } else if (si === 5) {     // day 31: the speaker gets the praise
    spkWake = 1; spkHop = Math.abs(Math.sin(u * 6.4)) * .03; spkYaw = Math.sin(u * 3.2) * .35; spkZ = -1.9;
    r = H_SOCK; vExpr = 'flat'; vCol = '#8fb4c0'; lidarI = .5;
    if (t < SPLIT5) { const k = ss(seg(u, 0, SPLIT5 - S.a)); CP = V(lerp(.86, .8, k), .68, lerp(-1.36, -1.3, k)); CT = V(1.17, .63, -1.9); FOV = 40; AP = 8; }
    else { const k = ss(seg(t, SPLIT5, S.b)); vp = { look: .8 };
      CP = P.clone().addScaledVector(F, lerp(.85, .7, k)).addScaledVector(PP, -.42).add(V(0, .16, 0)); CT = P.clone().addScaledVector(F, .12).add(V(0, .05, 0)); FOV = lerp(34, 30, k); AP = 9; }
  } else {                   // day 47: revenge
    P = S0.clone().addScaledVector(F, -.25); r = H_SOCK;
    if (t < SPLIT6) { const k = ss(seg(u, 0, SPLIT6 - S.a));
      vExpr = 'open'; vp = { look: Math.sin(u * 2.6) * .9, blink: (u > 1.1 && u < 1.25) ? 1 : 0 };
      CP = P.clone().addScaledVector(F, lerp(.86, .8, k)).addScaledVector(PP, .3).add(V(0, .24, 0)); CT = P.clone().addScaledVector(F, .1).add(V(0, -.02, 0)); FOV = 36; AP = 9; }
    else { const k = ss(seg(t, SPLIT6, S.b)), hide = ss(seg(t, LINES[7].t + LINES[7].d * .55, S.b - .15));
      r = H_SOCK - .55; vExpr = 'hunt'; vCol = C_GOLD; vp = { look: -.5 }; lidarCol = C_GOLD; lidarI = 1.1 + Math.sin(t * 6) * .5;
      sockOn = true; sA = P.clone().addScaledVector(PP, .12).addScaledVector(F, .04).setY(.03);
      sB = P.clone().addScaledVector(PP, lerp(.4, .2, hide)).addScaledVector(F, .1).setY(.03); bob = hide > 0 && hide < 1 ? Math.sin(t * 40) * .0015 : 0;
      CP = P.clone().addScaledVector(F, lerp(.74, .6, k)).addScaledVector(PP, lerp(.56, .5, k)).add(V(0, lerp(.15, .13, k), 0)); CT = P.clone().addScaledVector(PP, .12).add(V(0, .0, 0)); FOV = lerp(38, 33, k); AP = 10; }
  }

  // ── robovac
  vac.position.set(P.x, bob, P.z); vac.rotation.y = r;
  vBody.rotation.set(tilt + flip * Math.PI, 0, rock); vBody.position.y = flip * .125;
  brush.rotation.y = -t * brushSpeed;
  lidarMat.emissive.set(lidarCol); lidarMat.emissiveIntensity = lidarI; vLight.intensity = 0;
  drawFace(vScr, vExpr, vCol, vp);
  vac.updateMatrixWorld(true);
  // ── cat
  cat.position.set(cp.x, cp.y, cp.z); cat.rotation.y = cp.ry; cBody.position.set(0, cp.hipY, 0); cBody.rotation.x = cp.pitch; cat.updateMatrixWorld(true);
  const FL = LEGS[0].a, FR = LEGS[1].a, BL = LEGS[2].a, BR = LEGS[3].a;
  if (cp.mode === 'crouch') cp.paws = [pawAt(FL, .05), pawAt(FR, .05), pawAt(BL, .04), pawAt(BR, .04)];
  else { const gy = cp.y + .018; cp.paws = [pawAt(FL, .02, 0, gy), pawAt(FR, .02, 0, gy), pawAt(BL, .1, 0, gy), pawAt(BR, .1, 0, gy)]; }
  poseCat(cp); catDim(catDimV, false);
  // ── sock
  sock.visible = sockOn; if (sockOn) placeSock(sA, sB);
  // ── speaker
  spkRingMat.emissive.set(C_TEAL); spkRingMat.emissiveIntensity = .2 + spkWake * (1.6 + Math.sin(t * 12.8) * 1.2);
  spkEyeMat.emissive.set(C_TEAL); spkEyeMat.emissiveIntensity = spkWake * 3; spkLight.intensity = spkWake * .8;
  spk.position.set(1.17, .53 + spkHop, spkZ); spk.rotation.set(0, spkYaw, 0);
  // ── kettle: asleep the whole film
  drawFace(kScr, 'flat', '#6a7a80', {}); kettle.rotation.set(0, 1.4, 0); kettle.position.set(1.05, .44, -.55); kBody.rotation.z = 0; kLid.position.set(0, .175, 0); kLid.rotation.set(0, 0, 0);
  // ── dust puffs (the gulp)
  for (let i = 0; i < puffs.length; i++) {
    const pf = puffs[i];
    if (!puffAt || puffAge < 0 || puffAge > 1) { pf.visible = false; continue; }
    const a = hash(i * 3.7) * Math.PI * 2;
    pf.visible = true; pf.position.set(puffAt.x + Math.cos(a) * (.08 + puffAge * .18), .03 + puffAge * .08 * hash(i), puffAt.z + Math.sin(a) * (.08 + puffAge * .18));
    pf.scale.setScalar(.008 + puffAge * .02); pf.material.opacity = .35 * (1 - puffAge);
  }
  // ── motes drift in the shafts
  for (let i = 0; i < motes.length; i++) { const m = motes[i]; const ph = hash(i) * 100; m.position.set(-1.2 + hash(i * 1.3) * 1.9 + Math.sin(t * .3 + ph) * .05, .05 + ((hash(i * 2.1) * 1.6 + t * .02 * (hash(i) - .3)) % 1.6), -1.4 + hash(i * 3.3) * 1.4 + Math.cos(t * .25 + ph) * .05); }
  // ── camera
  const fr = Math.floor(t * 30);
  camera.position.set(CP.x + (hash(fr) - .5) * shake, CP.y + (hash(fr + 9) - .5) * shake, CP.z);
  camera.lookAt(CT); camera.fov = FOV; camera.updateProjectionMatrix();
  // ── overlays: day card pops on every cut, subtitle follows the voice
  const day = S.day || '';
  if (day !== lastDay) { dayEl.textContent = day; lastDay = day; }
  const pop = back(seg(u, 0, .3), 2.2);
  docEl.style.opacity = day ? Math.min(1, seg(u, 0, .12) * 1).toFixed(3) : '0';
  docEl.style.transform = `scale(${(0.7 + .3 * pop).toFixed(3)})`;
  barEl.style.width = (ss(seg(u, .1, .7)) * 300).toFixed(0) + 'px';
  flashEl.style.opacity = (si > 0 && u < .12 ? (1 - seg(u, 0, .12)) * .22 : 0).toFixed(3);
  let s = '';
  for (const Ln of LINES) if (t >= Ln.t - .05 && t < Ln.t + Ln.d + .3) s = Ln.text;
  if (s !== lastSub) { subEl.innerHTML = s; lastSub = s; }
  camera.updateMatrixWorld(); post.dof.focus = Math.max(.08, CP.distanceTo(CT)); post.dof.aper = AP;
  post.composer.render();
}

await document.fonts.load('800 40px Rubik'); await document.fonts.load('400 40px "Russo One"');
window.render(0);
window.READY = true;
