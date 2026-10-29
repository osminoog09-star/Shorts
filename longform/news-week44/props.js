// Реквизит выпуска «Новости недели» — премиальный стилизованный 3D (скругления, глянец/мат, мелкие детали)
import { THREE, C, matte, gloss, metal, hash, clamp, lerp } from './engine.js';
import { v3, rbox, sphere, cyl, puck, textSprite } from './kit.js';

export const shadowAll = (o) => { o.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return o; };
const glow = (color, op = 1) => new THREE.MeshBasicMaterial({ color, toneMapped: false, transparent: op < 1, opacity: op });
function wheel(r = 0.42, w = 0.32) {
  const g = new THREE.Group();
  const tire = cyl(r, w, matte(0x2a2a33, { roughness: 0.9 }), 28); tire.rotation.x = Math.PI / 2; g.add(tire);
  const hub = cyl(r * 0.55, w + 0.02, metal(0xc9ccd6), 20); hub.rotation.x = Math.PI / 2; g.add(hub);
  for (let i = 0; i < 5; i++) { const b = sphere(0.035, metal(0x777b88), 8); const a = (i / 5) * Math.PI * 2; b.position.set(Math.cos(a) * r * 0.33, Math.sin(a) * r * 0.33, w / 2 + 0.01); g.add(b); }
  return g;
}

// ───────── 1. Грузовик с серверами, машина сопровождения, дорога ─────────
export function serverRack(h = 1.6) {
  const g = new THREE.Group();
  const body = rbox(0.62, h, 0.7, gloss(0x30334a, { roughness: 0.35 }), 0.05); body.position.y = h / 2; g.add(body);
  const n = Math.floor(h / 0.16);
  for (let i = 0; i < n; i++) {
    const u = rbox(0.54, 0.11, 0.02, matte(0x464a63), 0.02); u.position.set(0, 0.12 + i * 0.15, 0.36); g.add(u);
    const led = sphere(0.017, glow(i % 3 === 0 ? 0x6bffb8 : i % 3 === 1 ? 0x7ec8ff : 0xffd36b), 8); led.position.set(0.21, 0.12 + i * 0.15, 0.375); g.add(led);
  }
  return shadowAll(g);
}
export function pallet() {
  const g = new THREE.Group(); const w = matte(0xd2a36d);
  for (let i = 0; i < 3; i++) { const p = rbox(1.4, 0.06, 0.25, w, 0.02); p.position.set(0, 0.17, -0.45 + i * 0.45); g.add(p); }
  for (let i = 0; i < 3; i++) { const b = rbox(0.18, 0.14, 1.2, w, 0.02); b.position.set(-0.6 + i * 0.6, 0.07, 0); g.add(b); }
  return shadowAll(g);
}
export function truck({ color = C.coral, open = 0 } = {}) {
  const g = new THREE.Group();
  const cab = new THREE.Group(); g.add(cab); cab.position.set(3.55, 0, 0);
  const cb = rbox(1.7, 1.9, 2.2, gloss(color), 0.28); cb.position.y = 1.55; cab.add(cb);
  const hood = rbox(0.9, 1.0, 2.1, gloss(color), 0.2); hood.position.set(1.15, 1.1, 0); cab.add(hood);
  const glass = rbox(0.06, 0.8, 1.8, gloss(0x9fd0f0, { roughness: 0.05 }), 0.04); glass.position.set(0.86, 2.0, 0); glass.rotation.z = -0.12; cab.add(glass);
  const grill = rbox(0.06, 0.55, 1.6, metal(0xd8dbe6), 0.04); grill.position.set(1.62, 0.95, 0); cab.add(grill);
  for (const z of [-0.7, 0.7]) { const hl = sphere(0.12, glow(0xfff4c8), 12); hl.position.set(1.64, 0.8, z); cab.add(hl); }
  const stack = cyl(0.08, 1.3, metal(0xd8dbe6), 12); stack.position.set(-0.75, 2.6, 0.95); cab.add(stack);
  const mirror = rbox(0.1, 0.35, 0.08, matte(0x2b2a3a), 0.03); mirror.position.set(0.7, 2.1, 1.2); cab.add(mirror);
  const trailer = new THREE.Group(); g.add(trailer);
  const tb = rbox(6.2, 2.7, 2.4, matte(0xf4f1ea), 0.12); tb.position.set(-0.6, 2.0, 0); trailer.add(tb);
  const stripe = rbox(6.21, 0.22, 2.42, gloss(C.lav), 0.05); stripe.position.set(-0.6, 1.0, 0); trailer.add(stripe);
  for (let i = 0; i < 9; i++) { const rib = rbox(0.05, 2.5, 2.44, matte(0xe4e0d6), 0.02); rib.position.set(-3.5 + i * 0.72, 2.0, 0); trailer.add(rib); }
  const chassis = rbox(9, 0.3, 1.6, matte(0x3a3a46), 0.06); chassis.position.set(0.3, 0.55, 0); g.add(chassis);
  const wheels = [];
  for (const x of [-3.1, -2.2, 2.4, 4.6]) for (const z of [-1.0, 1.0]) { const w = wheel(); w.position.set(x, 0.42, z); g.add(w); wheels.push(w); }
  // задние двери (open 0..1)
  const doorL = new THREE.Group(); doorL.position.set(-3.7, 2.0, -1.2); trailer.add(doorL);
  const dl = rbox(0.06, 2.6, 1.2, matte(0xebe7dd), 0.04); dl.position.z = 0.6; doorL.add(dl);
  const doorR = new THREE.Group(); doorR.position.set(-3.7, 2.0, 1.2); trailer.add(doorR);
  const dr = rbox(0.06, 2.6, 1.2, matte(0xebe7dd), 0.04); dr.position.z = -0.6; doorR.add(dr);
  const cargo = new THREE.Group(); trailer.add(cargo);
  for (let i = 0; i < 4; i++) { const p = pallet(); p.position.set(-3.0 + i * 1.5, 0.72, 0); p.rotation.y = Math.PI / 2; cargo.add(p); const r = serverRack(1.5); r.position.set(-3.0 + i * 1.5, 0.95, 0); cargo.add(r); }
  shadowAll(g);
  const setOpen = (k) => { doorL.rotation.y = -k * 1.9; doorR.rotation.y = k * 1.9; };
  setOpen(open);
  return { g, wheels, cargo, setOpen, trailer };
}
export function car(color = 0x3d3a5c) {
  const g = new THREE.Group();
  const b = rbox(3.4, 0.7, 1.7, gloss(color), 0.25); b.position.y = 0.75; g.add(b);
  const top = rbox(1.9, 0.6, 1.5, gloss(color), 0.25); top.position.set(-0.2, 1.3, 0); g.add(top);
  const win = rbox(1.7, 0.42, 1.52, gloss(0x9fd0f0, { roughness: 0.05 }), 0.15); win.position.set(-0.2, 1.33, 0); g.add(win);
  const bar = rbox(0.5, 0.12, 0.9, glow(0xff5f6d), 0.04); bar.position.set(-0.2, 1.67, 0); g.add(bar); g.userData.bar = bar;
  const wheels = []; for (const x of [-1.1, 1.1]) for (const z of [-0.8, 0.8]) { const w = wheel(0.34, 0.26); w.position.set(x, 0.34, z); g.add(w); wheels.push(w); }
  g.userData.wheels = wheels;
  return shadowAll(g);
}
export function road(len = 140) {
  const g = new THREE.Group();
  const asphalt = new THREE.Mesh(new THREE.PlaneGeometry(len, 9), matte(0x8e8ea0, { roughness: 0.95 })); asphalt.rotation.x = -Math.PI / 2; asphalt.position.y = 0.01; asphalt.receiveShadow = true; g.add(asphalt);
  const dashes = new THREE.Group(); g.add(dashes);
  for (let i = 0; i < len / 4; i++) { const d = rbox(1.8, 0.02, 0.18, matte(0xfdf7e8), 0.01); d.position.set(-len / 2 + i * 4, 0.03, 0); dashes.add(d); }
  for (const z of [-4.3, 4.3]) { const e = rbox(len, 0.03, 0.16, matte(0xfdf7e8), 0.01); e.position.set(0, 0.03, z); g.add(e); }
  for (let i = 0; i < 26; i++) { // столбики и кусты вдоль дороги
    const x = -len / 2 + i * (len / 26) + hash(i) * 2;
    const p = rbox(0.14, 0.9, 0.14, matte(0xffffff), 0.04); p.position.set(x, 0.45, 5.2); g.add(p);
    const r = rbox(0.16, 0.12, 0.05, glow(0xff8f87), 0.02); r.position.set(x, 0.8, 5.13); g.add(r);
    const bush = sphere(0.7 + hash(i + 9) * 0.5, matte(0x9fc58f), 14); bush.position.set(x + 1.3, 0.4, -7 - hash(i + 3) * 3); bush.scale.y = 0.7; g.add(bush);
  }
  g.userData.dashes = dashes;
  return shadowAll(g);
}
export function gpsPin(color = 0xff5f6d) {
  const g = new THREE.Group();
  const head = sphere(0.45, gloss(color), 24); head.position.y = 1.2; g.add(head);
  const cone = new THREE.Mesh(new THREE.ConeGeometry(0.33, 0.9, 24), gloss(color)); cone.rotation.x = Math.PI; cone.position.y = 0.6; g.add(cone);
  const dot = sphere(0.18, matte(0xffffff), 16); dot.position.set(0, 1.25, 0.32); g.add(dot);
  return shadowAll(g);
}
export function envelope(color = 0xfdfaf4) {
  const g = new THREE.Group();
  const b = rbox(1.6, 1.05, 0.08, matte(color), 0.06); g.add(b);
  const flap = new THREE.Mesh(new THREE.ConeGeometry(0.98, 0.6, 4, 1), matte(0xf1ebdf)); flap.rotation.set(Math.PI / 2, Math.PI / 4, 0); flap.scale.set(1, 1, 0.08); flap.position.set(0, 0.22, 0.06); g.add(flap);
  const seal = puck(0.14, 0.05, gloss(0xe8706a)); seal.rotation.x = Math.PI / 2; seal.position.set(0, 0.05, 0.1); g.add(seal);
  return shadowAll(g);
}
export function hook() { // фишинговый крючок
  const g = new THREE.Group(); const m = metal(0xcfd3dd);
  const curve = new THREE.CatmullRomCurve3([v3(0, 1.4, 0), v3(0, 0.2, 0), v3(0.05, -0.25, 0), v3(0.35, -0.42, 0), v3(0.55, -0.2, 0), v3(0.5, 0.05, 0)]);
  g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 40, 0.05, 10), m));
  const line = cyl(0.012, 4, matte(0x555566), 6); line.position.y = 3.4; g.add(line);
  return shadowAll(g);
}

// ───────── 2. Математика: решётка перебора, доска, Lean-куб ─────────
export function bruteGrid(n = 8, s = 0.42) {
  const g = new THREE.Group(); const cells = [];
  for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) for (let z = 0; z < 3; z++) {
    const m = rbox(s * 0.86, s * 0.86, s * 0.86, gloss(0xffffff, { roughness: 0.35 }), 0.06);
    m.position.set((x - (n - 1) / 2) * s, y * s + s / 2, (z - 1) * s); g.add(m); cells.push(m);
  }
  return { g: shadowAll(g), cells };
}
export function board(lines = ['SAT', '2ⁿ', 'ETH?']) {
  const g = new THREE.Group();
  const frame = rbox(5.2, 3.2, 0.2, wood0(), 0.08); g.add(frame);
  const face = rbox(4.9, 2.9, 0.06, matte(0x2f4d45, { roughness: 0.95 }), 0.04); face.position.z = 0.1; g.add(face);
  lines.forEach((tx, i) => { const s = textSprite(tx, { size: 80, color: '#f3efe2', bg: null, font: 'Rubik', weight: 700, scale: 0.9 }); s.position.set(-1.15 + (i % 2) * 2.3, 0.6 - Math.floor(i / 2) * 1.0, 0.2); g.add(s); });
  const tray = rbox(4.6, 0.1, 0.3, wood0(), 0.03); tray.position.set(0, -1.62, 0.18); g.add(tray);
  const chalk = cyl(0.04, 0.4, matte(0xffffff), 10); chalk.rotation.z = Math.PI / 2; chalk.position.set(1.2, -1.53, 0.2); g.add(chalk);
  return shadowAll(g);
}
function wood0() { return matte(0xc99766, { roughness: 0.75 }); }
export function leanCube() {
  const g = new THREE.Group();
  const cube = rbox(1.6, 1.6, 1.6, gloss(C.mint, { roughness: 0.25, transmission: 0.0 }), 0.22); g.add(cube);
  const tick = new THREE.Group(); tick.position.z = 0.82; g.add(tick);
  const a = rbox(0.18, 0.55, 0.08, matte(0xffffff), 0.05); a.position.set(-0.22, -0.08, 0); a.rotation.z = 0.75; tick.add(a);
  const b = rbox(0.18, 1.0, 0.08, matte(0xffffff), 0.05); b.position.set(0.18, 0.12, 0); b.rotation.z = -0.62; tick.add(b);
  const lbl = textSprite('LEAN', { size: 54, color: '#2b2a3a', bg: '#ffffff', scale: 0.9 }); lbl.position.set(0, 1.25, 0); g.add(lbl);
  return shadowAll(g);
}
export function paperStack(n = 14) {
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) { const p = rbox(1.5, 0.03, 2.0, matte(0xfdfbf6), 0.01); p.position.set((hash(i) - 0.5) * 0.08, i * 0.035, (hash(i + 5) - 0.5) * 0.08); p.rotation.y = (hash(i + 2) - 0.5) * 0.1; g.add(p); }
  return shadowAll(g);
}
export function magnifier() {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.09, 16, 48), metal(0xe9b97f)); g.add(ring);
  const lens = new THREE.Mesh(new THREE.CircleGeometry(0.58, 40), gloss(0xcfe9ff, { transparent: true, opacity: 0.35, roughness: 0.05 })); g.add(lens);
  const handle = rbox(0.18, 1.1, 0.18, wood0(), 0.08); handle.position.set(0.62, -0.85, 0); handle.rotation.z = 0.6; g.add(handle);
  return shadowAll(g);
}

// ───────── 3. Сеть компании и агенты ─────────
export function node(label, color = C.white, w = 2.0) {
  const g = new THREE.Group();
  const b = rbox(w, 1.1, 1.1, gloss(color), 0.22); b.position.y = 0.55; g.add(b);
  const scr = rbox(w * 0.7, 0.42, 0.03, glow(0x9fe8ff, 0.9), 0.04); scr.position.set(0, 0.62, 0.56); g.add(scr);
  const t = textSprite(label, { size: 52, color: '#2b2a3a', bg: '#ffffff', scale: 0.85 }); t.position.set(0, 1.55, 0); g.add(t);
  g.userData.scr = scr;
  return shadowAll(g);
}
export function lock(color = C.butter) {
  const g = new THREE.Group();
  const body = rbox(0.9, 0.75, 0.4, gloss(color), 0.12); g.add(body);
  const sh = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.08, 12, 32, Math.PI), metal(0xd8dbe6)); sh.position.y = 0.38; g.add(sh);
  const kh = cyl(0.07, 0.42, matte(0x2b2a3a), 12); kh.rotation.x = Math.PI / 2; g.add(kh);
  return shadowAll(g);
}
export function agent(color = 0xff8f87) {
  const g = new THREE.Group();
  const b = sphere(0.32, gloss(color), 24); g.add(b);
  const eye = rbox(0.34, 0.1, 0.05, glow(0xffffff), 0.04); eye.position.set(0, 0.04, 0.29); g.add(eye);
  const ant = cyl(0.02, 0.25, matte(0x2b2a3a), 6); ant.position.y = 0.42; g.add(ant);
  const tip = sphere(0.05, glow(color), 8); tip.position.y = 0.56; g.add(tip);
  return shadowAll(g);
}
export function shield(color = C.sky) {
  const g = new THREE.Group();
  const s = new THREE.Shape(); s.moveTo(0, 1); s.quadraticCurveTo(0.8, 0.9, 0.9, 0.7); s.quadraticCurveTo(0.9, -0.3, 0, -1); s.quadraticCurveTo(-0.9, -0.3, -0.9, 0.7); s.quadraticCurveTo(-0.8, 0.9, 0, 1);
  const m = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.2, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06, bevelSegments: 4 }), gloss(color)); m.position.z = -0.1; g.add(m);
  return shadowAll(g);
}

// ───────── 4. Биржа ─────────
export function bell() {
  const g = new THREE.Group();
  const pts = []; for (let i = 0; i <= 16; i++) { const t = i / 16; pts.push(new THREE.Vector2(0.15 + 0.85 * Math.pow(t, 1.8), 1.4 - t * 1.4)); }
  const b = new THREE.Mesh(new THREE.LatheGeometry(pts, 40), metal(0xe9b97f)); b.material.side = THREE.DoubleSide; g.add(b);
  const lip = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.07, 12, 40), metal(0xd9a06b)); lip.rotation.x = Math.PI / 2; g.add(lip);
  const knob = sphere(0.16, metal(0xe9b97f)); knob.position.y = 1.48; g.add(knob);
  const stand = rbox(2.6, 0.18, 1.0, wood0(), 0.06); stand.position.y = -0.3; g.add(stand);
  for (const x of [-1.15, 1.15]) { const p = rbox(0.12, 2.1, 0.12, wood0(), 0.04); p.position.set(x, 0.75, 0); g.add(p); }
  const top = rbox(2.42, 0.14, 0.14, wood0(), 0.04); top.position.y = 1.78; g.add(top);
  return shadowAll(g);
}
export function barChart(vals, color = C.mint, w = 0.9) {
  const g = new THREE.Group(); const bars = [];
  vals.forEach((v, i) => { const b = rbox(w, 1, w, gloss(i === vals.length - 1 ? color : 0xffffff), 0.12); b.position.set((i - (vals.length - 1) / 2) * (w + 0.45), 0.5, 0); b.userData.v = v; g.add(b); bars.push(b); });
  const setK = (k) => bars.forEach((b, i) => { const h = Math.max(0.05, b.userData.v * clamp(k * 1.4 - i * 0.2)); b.scale.y = h; b.position.y = h / 2; });
  return { g: shadowAll(g), bars, setK };
}
export function coinStack(n = 8, color = 0xe9b97f) {
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) { const c = puck(0.42, 0.11, metal(color)); c.position.set((hash(i) - 0.5) * 0.05, 0.055 + i * 0.115, (hash(i + 3) - 0.5) * 0.05); g.add(c); }
  return shadowAll(g);
}
export function ant() { // муравей-талисман тикера ANT (своё, не бренд)
  const g = new THREE.Group(); const m = gloss(0x3d3a5c);
  const a = sphere(0.36, m); a.position.set(-0.55, 0.5, 0); a.scale.set(1.2, 0.9, 0.9); g.add(a);
  const b = sphere(0.26, m); b.position.set(0, 0.52, 0); g.add(b);
  const h = sphere(0.3, m); h.position.set(0.5, 0.62, 0); g.add(h);
  for (const z of [-0.12, 0.12]) { const e = sphere(0.07, matte(0xffffff), 12); e.position.set(0.72, 0.7, z); g.add(e); const p = sphere(0.035, matte(0x111111), 8); p.position.set(0.78, 0.7, z); g.add(p); }
  for (const z of [-1, 1]) for (let i = 0; i < 3; i++) { const l = cyl(0.03, 0.55, m, 6); l.position.set(-0.2 + i * 0.22, 0.25, z * 0.25); l.rotation.x = z * 0.7; g.add(l); }
  for (const z of [-1, 1]) { const an = cyl(0.02, 0.45, m, 6); an.position.set(0.62, 1.0, z * 0.12); an.rotation.set(z * 0.4, 0, -0.5); g.add(an); }
  return shadowAll(g);
}
export function tickerBoard(text = 'ANT') {
  const g = new THREE.Group();
  const b = rbox(4.6, 1.5, 0.3, gloss(0x2b2a3a), 0.2); g.add(b);
  const t = textSprite(text, { size: 150, color: '#86dcbc', bg: null, font: 'RMono', weight: 400, scale: 1.2 }); t.position.set(-0.9, 0, 0.22); g.add(t);
  const arr = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.55, 3), glow(0x86dcbc)); arr.position.set(1.55, 0.05, 0.22); g.add(arr);
  return shadowAll(g);
}

// ───────── 5. Генератор миров ─────────
export function worldIsland() {
  const g = new THREE.Group();
  const top = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.0, 0.5, 48), matte(0x9fd38f)); top.position.y = 0; g.add(top);
  const rock = new THREE.Mesh(new THREE.ConeGeometry(3.0, 2.8, 24), matte(0xc9a27a)); rock.rotation.x = Math.PI; rock.position.y = -1.65; g.add(rock);
  for (let i = 0; i < 9; i++) { const a = hash(i) * Math.PI * 2, r = 0.8 + hash(i + 4) * 1.9;
    const tr = new THREE.Group(); tr.position.set(Math.cos(a) * r, 0.25, Math.sin(a) * r); g.add(tr);
    const trunk = cyl(0.07, 0.5, wood0(), 8); trunk.position.y = 0.25; tr.add(trunk);
    const crown = new THREE.Mesh(new THREE.ConeGeometry(0.38, 0.9, 12), matte(0x5fa86b)); crown.position.y = 0.85; crown.castShadow = true; tr.add(crown); }
  const house = rbox(0.8, 0.6, 0.7, matte(0xfdf3e3), 0.08); house.position.set(-0.6, 0.55, 0.9); g.add(house);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.62, 0.45, 4), gloss(C.coral)); roof.rotation.y = Math.PI / 4; roof.position.set(-0.6, 1.07, 0.9); g.add(roof);
  const lake = new THREE.Mesh(new THREE.CircleGeometry(0.8, 32), gloss(0x8fd0e6, { roughness: 0.1 })); lake.rotation.x = -Math.PI / 2; lake.position.set(1.0, 0.26, -0.6); g.add(lake);
  const hero = new THREE.Group(); hero.position.set(0.3, 0.25, 1.4); g.add(hero);
  const hb = rbox(0.22, 0.34, 0.16, gloss(C.lav), 0.08); hb.position.y = 0.3; hero.add(hb); const hh = sphere(0.12, matte(0xf3c9a9), 12); hh.position.y = 0.58; hero.add(hh);
  g.userData.hero = hero;
  return shadowAll(g);
}
export function soundRings(n = 4, color = C.lav) {
  const g = new THREE.Group(); const rs = [];
  for (let i = 0; i < n; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(1, 0.03, 8, 64), glow(color, 0.8)); g.add(r); rs.push(r); }
  const tick = (t) => rs.forEach((r, i) => { const ph = (t * 0.6 + i / n) % 1; r.scale.setScalar(0.4 + ph * 2.6); r.material.opacity = (1 - ph) * 0.85; });
  return { g, tick };
}
export function rain(n = 120, area = 7) {
  const g = new THREE.Group(); const ds = [];
  const m = glow(0x9fd6ff, 0.7);
  for (let i = 0; i < n; i++) { const d = rbox(0.025, 0.28, 0.025, m, 0.01); d.userData.p = [(hash(i) - 0.5) * area, hash(i + 3), (hash(i + 7) - 0.5) * area]; g.add(d); ds.push(d); }
  const tick = (t, k) => ds.forEach((d) => { const [x, y0, z] = d.userData.p; const y = 6 - ((t * 7 + y0 * 6) % 6); d.position.set(x, y, z); d.visible = k > 0.02; d.scale.setScalar(Math.max(0.01, k)); });
  return { g, tick };
}
export function frameRect(w = 3.2, h = 1.8, color = 0xffffff) { // рамка «камеры»
  const g = new THREE.Group(); const m = glow(color);
  for (const [x, y, ww, hh] of [[0, h / 2, w, 0.05], [0, -h / 2, w, 0.05], [w / 2, 0, 0.05, h], [-w / 2, 0, 0.05, h]]) { const b = rbox(ww, hh, 0.04, m, 0.01); b.position.set(x, y, 0); g.add(b); }
  return g;
}
export function gamepad() {
  const g = new THREE.Group();
  const b = rbox(2.0, 0.35, 1.0, gloss(0xfdfaf4), 0.17); g.add(b);
  for (const x of [-0.85, 0.85]) { const gr = sphere(0.45, gloss(0xfdfaf4), 20); gr.scale.set(1, 0.4, 1.2); gr.position.set(x, -0.05, 0.25); g.add(gr); }
  const st = cyl(0.13, 0.15, matte(0x3d3a5c), 16); st.position.set(-0.45, 0.22, 0.05); g.add(st);
  [[0.55, 0.15, C.coral], [0.75, -0.05, C.mint], [0.55, -0.25, C.sky], [0.35, -0.05, C.butter]].forEach(([x, z, c]) => { const k = puck(0.08, 0.06, gloss(c)); k.position.set(x, 0.2, z); g.add(k); });
  return shadowAll(g);
}

// ───────── 6. Пригород и энергоцентр ─────────
export function house(color = 0xfdf3e3, roofC = C.coral) {
  const g = new THREE.Group();
  const b = rbox(2.2, 1.6, 1.9, matte(color), 0.1); b.position.y = 0.8; g.add(b);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(1.75, 1.1, 4), gloss(roofC)); roof.rotation.y = Math.PI / 4; roof.position.y = 2.15; roof.scale.set(1, 1, 0.92); g.add(roof);
  const door = rbox(0.45, 0.85, 0.06, gloss(0x8a6b55), 0.05); door.position.set(0.3, 0.43, 0.96); g.add(door);
  const win = rbox(0.5, 0.45, 0.05, gloss(0xbfe3ff, { roughness: 0.05 }), 0.04); win.position.set(-0.5, 0.95, 0.96); g.add(win);
  const chim = rbox(0.25, 0.7, 0.25, matte(0xc98a6a), 0.04); chim.position.set(0.6, 2.4, -0.3); g.add(chim);
  const fence = new THREE.Group(); g.add(fence); for (let i = 0; i < 7; i++) { const p = rbox(0.08, 0.45, 0.06, matte(0xffffff), 0.02); p.position.set(-1.2 + i * 0.4, 0.22, 1.6); fence.add(p); }
  const rail = rbox(2.5, 0.06, 0.05, matte(0xffffff), 0.02); rail.position.set(0, 0.32, 1.6); g.add(rail);
  return shadowAll(g);
}
export function turbineHall(n = 6) {
  const g = new THREE.Group(); const stacks = [];
  const hall = rbox(9, 2.6, 4, matte(0xd6d9e0), 0.12); hall.position.y = 1.3; g.add(hall);
  for (let i = 0; i < 12; i++) { const r = rbox(0.06, 2.4, 4.02, matte(0xc4c8d1), 0.02); r.position.set(-4.2 + i * 0.76, 1.3, 0); g.add(r); }
  for (let i = 0; i < n; i++) {
    const t = cyl(0.55, 2.6, metal(0xbfc4cf), 24); t.rotation.z = Math.PI / 2; t.position.set(-3.4 + i * 1.36, 0.6, 2.7); g.add(t);
    const s = cyl(0.28, 3.4, metal(0xa9aebb), 16); s.position.set(-3.4 + i * 1.36, 4.1, -0.8); g.add(s); stacks.push(s);
    const band = cyl(0.3, 0.2, gloss(C.coral), 16); band.position.set(-3.4 + i * 1.36, 5.4, -0.8); g.add(band);
  }
  return { g: shadowAll(g), stacks };
}
export function saleSign(text = 'ПРОДАЁТСЯ') {
  const g = new THREE.Group();
  const post = rbox(0.12, 1.6, 0.12, matte(0xffffff), 0.04); post.position.y = 0.8; g.add(post);
  const arm = rbox(0.9, 0.08, 0.08, matte(0xffffff), 0.03); arm.position.set(0.4, 1.5, 0); g.add(arm);
  const pan = rbox(1.0, 0.6, 0.05, gloss(0xe8706a), 0.06); pan.position.set(0.45, 1.1, 0); g.add(pan);
  const t = textSprite(text, { size: 46, color: '#ffffff', bg: null, scale: 0.55 }); t.position.set(0.45, 1.1, 0.06); g.add(t);
  return shadowAll(g);
}

// ───────── 7. Роботы ─────────
export function humanoid(color = 0xf4f4f6, accent = C.sky) {
  const g = new THREE.Group(); const m = gloss(color), d = gloss(0x3d3a5c), a = gloss(accent);
  const parts = {};
  const pelvis = rbox(0.55, 0.22, 0.3, d, 0.08); pelvis.position.y = 1.0; g.add(pelvis);
  const torso = new THREE.Group(); torso.position.y = 1.1; g.add(torso); parts.torso = torso;
  const chest = rbox(0.7, 0.75, 0.4, m, 0.16); chest.position.y = 0.42; torso.add(chest);
  const plate = rbox(0.4, 0.22, 0.05, a, 0.06); plate.position.set(0, 0.52, 0.21); torso.add(plate);
  const headG = new THREE.Group(); headG.position.y = 0.95; torso.add(headG); parts.head = headG;
  const head = rbox(0.42, 0.4, 0.38, m, 0.16); headG.add(head);
  const visor = rbox(0.34, 0.12, 0.04, glow(0x7ee8ff), 0.04); visor.position.set(0, 0.02, 0.19); headG.add(visor);
  const mk = (x, side) => {
    const sh = new THREE.Group(); sh.position.set(x, 0.72, 0); torso.add(sh);
    const j = sphere(0.12, d, 16); sh.add(j);
    const up = rbox(0.17, 0.42, 0.17, m, 0.07); up.position.y = -0.25; sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.48; sh.add(el);
    const lo = rbox(0.15, 0.4, 0.15, m, 0.06); lo.position.y = -0.2; el.add(lo);
    const hand = sphere(0.09, d, 12); hand.position.y = -0.44; el.add(hand);
    return { sh, el };
  };
  parts.armL = mk(-0.47, -1); parts.armR = mk(0.47, 1);
  const leg = (x) => {
    const hp = new THREE.Group(); hp.position.set(x, 0.95, 0); g.add(hp);
    const th = rbox(0.2, 0.46, 0.2, m, 0.08); th.position.y = -0.25; hp.add(th);
    const kn = new THREE.Group(); kn.position.y = -0.5; hp.add(kn);
    const sh = rbox(0.18, 0.42, 0.18, m, 0.07); sh.position.y = -0.22; kn.add(sh);
    const ft = rbox(0.22, 0.08, 0.34, d, 0.04); ft.position.set(0, -0.43, 0.06); kn.add(ft);
    return { hp, kn };
  };
  parts.legL = leg(-0.17); parts.legR = leg(0.17);
  g.userData.parts = parts;
  return shadowAll(g);
}
export function poseWalk(r, t, amp = 1) {
  const P = r.userData.parts; const s = Math.sin(t * 5) * 0.45 * amp;
  P.legL.hp.rotation.x = s; P.legR.hp.rotation.x = -s; P.legL.kn.rotation.x = Math.max(0, -s) * 0.9; P.legR.kn.rotation.x = Math.max(0, s) * 0.9;
  P.armL.sh.rotation.x = -s * 0.8; P.armR.sh.rotation.x = s * 0.8; P.armL.el.rotation.x = -0.3; P.armR.el.rotation.x = -0.3;
  P.torso.rotation.y = s * 0.12; P.head.rotation.y = -s * 0.1;
}
export function robotDog(color = 0xf4f4f6) {
  const g = new THREE.Group(); const m = gloss(color), d = gloss(0x3d3a5c);
  const body = rbox(1.2, 0.36, 0.5, m, 0.15); body.position.y = 0.75; g.add(body);
  const head = rbox(0.36, 0.28, 0.36, m, 0.1); head.position.set(0.72, 0.88, 0); g.add(head);
  const eye = rbox(0.04, 0.08, 0.26, glow(0x7ee8ff), 0.02); eye.position.set(0.91, 0.9, 0); g.add(eye);
  const legs = [];
  for (const x of [-0.45, 0.45]) for (const z of [-0.22, 0.22]) {
    const hp = new THREE.Group(); hp.position.set(x, 0.68, z); g.add(hp);
    const th = rbox(0.12, 0.34, 0.12, d, 0.05); th.position.y = -0.15; th.rotation.z = 0.35; hp.add(th);
    const sh = rbox(0.1, 0.36, 0.1, m, 0.04); sh.position.set(0.1, -0.45, 0); sh.rotation.z = -0.35; hp.add(sh);
    legs.push(hp);
  }
  g.userData.legs = legs;
  return shadowAll(g);
}
export function priceTag(text = '$16 000') {
  const g = new THREE.Group();
  const b = rbox(1.6, 0.7, 0.06, gloss(0xffdc7a), 0.1); g.add(b);
  const hole = cyl(0.07, 0.08, matte(0x2b2a3a), 12); hole.rotation.x = Math.PI / 2; hole.position.set(-0.62, 0, 0.01); g.add(hole);
  const t = textSprite(text, { size: 70, color: '#2b2a3a', bg: null, scale: 0.75 }); t.position.set(0.12, 0, 0.06); g.add(t);
  return shadowAll(g);
}

// ───────── 8. Starship ─────────
export function stage(len, r, color, nose = false) {
  const g = new THREE.Group();
  const b = cyl(r, len, metal(color, { roughness: 0.25 }), 40); b.position.y = len / 2; g.add(b);
  for (let i = 1; i < 6; i++) { const ring = cyl(r + 0.01, 0.04, metal(0x9aa0ab), 40); ring.position.y = (len / 6) * i; g.add(ring); }
  if (nose) {
    const n = new THREE.Mesh(new THREE.SphereGeometry(r, 40, 20, 0, Math.PI * 2, 0, Math.PI / 2), metal(color, { roughness: 0.25 })); n.scale.y = 2.2; n.position.y = len; g.add(n);
    for (const s of [-1, 1]) { const f = rbox(0.12, 1.6, 0.9, matte(0x3d3a5c), 0.05); f.position.set(s * (r + 0.05), len - 0.6, 0); g.add(f); const f2 = rbox(0.12, 2.0, 1.2, matte(0x3d3a5c), 0.05); f2.position.set(s * (r + 0.05), 1.4, 0); g.add(f2); }
    const tiles = new THREE.Mesh(new THREE.CylinderGeometry(r + 0.012, r + 0.012, len, 40, 1, true, -Math.PI / 2, Math.PI), matte(0x2f3040)); tiles.position.y = len / 2; tiles.rotation.y = Math.PI; g.add(tiles);
  } else {
    for (let i = 0; i < 4; i++) { const gf = rbox(0.5, 0.06, 0.5, metal(0x9aa0ab), 0.02); const a = (i / 4) * Math.PI * 2; gf.position.set(Math.cos(a) * (r + 0.2), len - 0.4, Math.sin(a) * (r + 0.2)); gf.rotation.y = -a; g.add(gf); }
  }
  for (let i = 0; i < (nose ? 6 : 13); i++) { const a = (i / (nose ? 6 : 13)) * Math.PI * 2; const rr = i === 0 ? 0 : r * 0.6; const e = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.4, 14, 1, true), metal(0x6f7280)); e.position.set(Math.cos(a) * rr, -0.18, Math.sin(a) * rr); g.add(e); }
  return shadowAll(g);
}
export function tower() {
  const g = new THREE.Group(); const m = metal(0x8f95a3, { roughness: 0.4 });
  const H = 26;
  for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const p = rbox(0.3, H, 0.3, m, 0.04); p.position.set(x * 1.3, H / 2, z * 1.3); g.add(p); }
  for (let i = 0; i < 13; i++) { for (const r of [0, Math.PI / 2]) { const b = rbox(2.9, 0.12, 0.12, m, 0.02); b.position.set(0, 1 + i * 2, 0); b.rotation.y = r; const bb = b.clone(); b.position.z = 1.3; g.add(b); bb.position.z = -1.3; if (r) { b.position.set(1.3, 1 + i * 2, 0); bb.position.set(-1.3, 1 + i * 2, 0); } g.add(bb); } }
  const carriage = new THREE.Group(); carriage.position.set(0, 18, 0); g.add(carriage);
  const cb = rbox(3.2, 1.2, 3.2, gloss(0x3d3a5c), 0.1); carriage.add(cb);
  const arms = [];
  for (const s of [-1, 1]) { const piv = new THREE.Group(); piv.position.set(1.6, 0, s * 1.2); carriage.add(piv); const a = rbox(8.5, 0.8, 0.6, gloss(0xe9eaee), 0.12); a.position.x = 4.25; piv.add(a); const pad = rbox(0.6, 0.9, 0.8, gloss(C.coral), 0.1); pad.position.set(6.4, 0, -s * 0.2); piv.add(pad); arms.push(piv); }
  const base = rbox(7, 1, 7, matte(0xd9d4ca), 0.1); base.position.y = -0.5; g.add(base);
  g.userData = { carriage, arms };
  return shadowAll(g);
}
export function flame(n = 18, color = 0xffb46b) {
  const g = new THREE.Group(); const ps = [];
  for (let i = 0; i < n; i++) { const p = new THREE.Mesh(new THREE.ConeGeometry(0.28, 1.6, 10), glow(i % 3 ? color : 0xfff1b8, 0.85)); p.rotation.x = Math.PI; g.add(p); ps.push(p); }
  const tick = (t, k) => ps.forEach((p, i) => { const a = (i / n) * Math.PI * 2; const r = 0.55 * hash(i); p.position.set(Math.cos(a) * r, -0.8 - hash(i + 2) * 0.6 * (0.7 + 0.3 * Math.sin(t * 30 + i)), Math.sin(a) * r); p.scale.set(k, k * (0.8 + 0.4 * Math.sin(t * 25 + i * 1.7)), k); p.visible = k > 0.02; });
  return { g, tick };
}
export function plume(n = 16) { // клубы пара/дыма у стенда
  const g = new THREE.Group(); const ps = [];
  for (let i = 0; i < n; i++) { const s = sphere(1, matte(0xf4f1ec, { transparent: true, opacity: 0.9 }), 16); g.add(s); ps.push(s); }
  const tick = (t, k) => ps.forEach((s, i) => { const ph = (t * 0.35 + hash(i)) % 1; const a = hash(i + 5) * Math.PI * 2; s.position.set(Math.cos(a) * (1 + ph * 6), 0.6 + ph * 2.5, Math.sin(a) * (1 + ph * 6)); s.scale.setScalar((0.6 + ph * 1.8) * k); s.material.opacity = (1 - ph) * 0.85; s.visible = k > 0.02; });
  return { g, tick };
}
