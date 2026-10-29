// Общие объекты и помощники фильма «Римский бетон» (премиальный стилизованный 3D + детали)
import { THREE, C, CSS, W, H, ctx, matte, gloss, metal, render, clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, waves, cloud } from './kit.js';
export { v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, waves, cloud };

export const VO = 0.6;
// время слова в локальном времени сцены (вход VO); nth — номер совпадения
export function cue(id, word, nth = 0, fb = 9999) {
  const ws = (window.WORDS && window.WORDS[id]) || [];
  const w = word.toLowerCase();
  const norm = (x) => x.toLowerCase().replace(/[«»"',.!?:;—…()]/g, '');
  let k = 0;
  for (const x of ws) {
    // WordBoundary: одно слово; SentenceBoundary: фраза — время слова интерполируем по позиции символа
    const parts = x.w.split(/\s+/).filter(Boolean); const L = x.w.length || 1; let pos = 0;
    for (const p of parts) { const at = x.w.indexOf(p, pos); pos = at + p.length;
      if (norm(p).startsWith(w)) { if (k === nth) return VO + x.start + (parts.length > 1 ? (at / L) * (x.end - x.start) : 0); k++; } }
  }
  return fb;
}
export const dof = (cam, tg, ap = 0.0009, mb = 0.01) => ({ focus: cam.position.distanceTo(tg), aperture: ap, maxblur: mb });
// монтаж внутри сцены: shots = [[t0, (lt, k)=>void], ...]; k — 0..1 прогресс шота
export function shot(t, shots, end) {
  let i = 0; for (let j = 0; j < shots.length; j++) if (t >= shots[j][0]) i = j;
  const t0 = shots[i][0], t1 = i + 1 < shots.length ? shots[i + 1][0] : end;
  shots[i][1](t - t0, clamp((t - t0) / Math.max(0.1, t1 - t0)), i);
  return i;
}

// ───────── процедурные текстуры ─────────
const texCache = new Map();
export function stoneTex({ base = '#cfc4b4', dots = '#8f857a', dots2 = '#e9e2d6', clasts = 0, seed = 1, n = 900, rough = 0.5, size = 512, rep = 1 } = {}) {
  const key = JSON.stringify(arguments[0] || {});
  if (texCache.has(key)) return texCache.get(key);
  const c = document.createElement('canvas'); c.width = c.height = size; const x = c.getContext('2d');
  x.fillStyle = base; x.fillRect(0, 0, size, size);
  const r = (i) => hash(i * 13.37 + seed * 101.1);
  for (let i = 0; i < 260; i++) { // пятна
    const g = x.createRadialGradient(r(i) * size, r(i + 1) * size, 0, r(i) * size, r(i + 1) * size, 20 + r(i + 2) * 70);
    const a = (r(i + 3) - 0.5) * 0.16 * rough;
    g.addColorStop(0, a > 0 ? `rgba(255,255,255,${a})` : `rgba(0,0,0,${-a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(0, 0, size, size);
  }
  for (let i = 0; i < n; i++) { // заполнитель
    const s = 1 + r(i + 500) * (r(i + 77) > 0.93 ? 9 : 3);
    x.fillStyle = r(i + 900) > 0.5 ? dots : dots2; x.globalAlpha = 0.35 + r(i + 4) * 0.5;
    x.beginPath(); x.ellipse(r(i + 200) * size, r(i + 300) * size, s, s * (0.6 + r(i + 8) * 0.5), r(i + 9) * 3, 0, Math.PI * 2); x.fill();
  }
  x.globalAlpha = 1;
  for (let i = 0; i < clasts; i++) { // белые известковые включения
    const s = 4 + r(i + 1500) * 9, px = r(i + 1600) * size, py = r(i + 1700) * size;
    const g = x.createRadialGradient(px - s * 0.3, py - s * 0.3, 0, px, py, s);
    g.addColorStop(0, '#ffffff'); g.addColorStop(0.8, '#f4f1ea'); g.addColorStop(1, 'rgba(230,225,215,0)');
    x.fillStyle = g; x.beginPath(); x.arc(px, py, s, 0, Math.PI * 2); x.fill();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); t.anisotropy = 4;
  texCache.set(key, t); return t;
}
export function stone(opts = {}, extra = {}) { const t = stoneTex(opts); return new THREE.MeshStandardMaterial({ map: t, bumpMap: t, bumpScale: opts.bump ?? 1.2, roughness: 0.92, metalness: 0, envMapIntensity: 0.5, ...extra }); }
export const concrete = (opts = {}) => stone({ base: '#cdbfae', dots: '#8a7f73', dots2: '#efe6d8', n: 1400, ...opts });
export const marble = () => stone({ base: '#f1ebe1', dots: '#d9cfc1', dots2: '#ffffff', n: 260, rough: 0.25 }, { roughness: 0.55 });
export const brick = () => stone({ base: '#d58a63', dots: '#a9603f', dots2: '#e9a986', n: 500, rough: 0.6 });
export const wood = () => stone({ base: '#c99766', dots: '#a27449', dots2: '#ddb184', n: 300, rough: 0.5 }, { roughness: 0.7 });

// ───────── объекты ─────────
export function shadowAll(o) { o.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return o; }
export function column(h = 4, r = 0.32, mat = marble()) {
  const g = new THREE.Group();
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.9, r, h, 24, 1), mat); shaft.position.y = h / 2; g.add(shaft);
  for (let i = 0; i < 12; i++) { const fl = new THREE.Mesh(new THREE.BoxGeometry(0.03, h * 0.92, 0.03), matte(0xe2d8c8)); const a = (i / 12) * Math.PI * 2; fl.position.set(Math.cos(a) * r * 0.95, h / 2, Math.sin(a) * r * 0.95); g.add(fl); }
  const base = puck(r * 1.35, 0.22, mat); base.position.y = 0.11; g.add(base);
  const cap = rbox(r * 2.7, 0.26, r * 2.7, mat, 0.06); cap.position.y = h + 0.13; g.add(cap);
  const ech = puck(r * 1.15, 0.18, mat); ech.position.y = h - 0.02; g.add(ech);
  return shadowAll(g);
}
// Пантеон: ротонда + купол с кессонами + окулус + портик
export function pantheon({ cut = false } = {}) {
  const g = new THREE.Group();
  const wallM = concrete({ base: '#d9ccb9', seed: 3 });
  const R = 5, Hd = 4.6;
  const drum = new THREE.Mesh(new THREE.CylinderGeometry(R, R, Hd, 64, 1, cut, 0, cut ? Math.PI : Math.PI * 2), wallM); drum.position.y = Hd / 2; g.add(drum);
  for (const y of [1.6, 3.2]) { const band = new THREE.Mesh(new THREE.TorusGeometry(R + 0.02, 0.06, 8, 96, cut ? Math.PI : Math.PI * 2), matte(0xc7b8a2)); band.rotation.x = Math.PI / 2; band.position.y = y; g.add(band); }
  // купол: внешняя оболочка (ступенчатые кольца у основания) и внутренняя с кессонами
  const pts = []; for (let i = 0; i <= 24; i++) { const a = (i / 24) * (Math.PI / 2 - 0.09); pts.push(new THREE.Vector2(Math.cos(a) * R, Math.sin(a) * R)); }
  pts.push(new THREE.Vector2(0.45, R - 0.02));
  const dome = new THREE.Mesh(new THREE.LatheGeometry(pts, 72, 0, cut ? Math.PI : Math.PI * 2), concrete({ base: '#cfc3b1', seed: 5 })); dome.position.y = Hd; dome.material.side = THREE.DoubleSide; g.add(dome);
  for (let k = 0; k < 3; k++) { const st = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.05 - k * 0.35, R + 0.15 - k * 0.35, 0.32, 64, 1, cut, 0, cut ? Math.PI : Math.PI * 2), wallM); st.position.y = Hd + 0.16 + k * 0.32; g.add(st); }
  const oc = new THREE.Mesh(new THREE.TorusGeometry(0.48, 0.07, 10, 48), matte(0xbfae96)); oc.rotation.x = Math.PI / 2; oc.position.y = Hd + R - 0.05; g.add(oc);
  // кессоны (5 рядов по 28) — изнутри
  const inner = new THREE.Group(); inner.position.y = Hd; g.add(inner);
  const cof = new THREE.BoxGeometry(0.62, 0.5, 0.16); const cm = matte(0xbcae98);
  for (let row = 0; row < 5; row++) {
    const a = 0.12 + row * 0.24, rr = (R - 0.1) * Math.cos(a), yy = (R - 0.1) * Math.sin(a), sc = Math.cos(a) * 1.05;
    for (let j = 0; j < 28; j++) {
      const b = (j / 28) * Math.PI * 2; if (cut && Math.sin(b) < -0.02) continue;
      const m = new THREE.Mesh(cof, cm); m.position.set(Math.cos(b) * rr, yy, Math.sin(b) * rr); m.lookAt(0, yy * 0.6, 0); m.scale.set(sc, 1 - row * 0.1, 1); inner.add(m);
    }
  }
  // портик
  const por = new THREE.Group(); por.position.set(0, 0, R + 1.9); g.add(por);
  for (let i = 0; i < 8; i++) { const c = column(4.0, 0.3); c.position.set(-3.5 + i, 0, 0.6); por.add(c); }
  for (let i = 0; i < 4; i++) { const c = column(4.0, 0.3); c.position.set(-1.5 + i, 0, -0.9); por.add(c); }
  const arch = rbox(8.4, 0.55, 3.2, marble(), 0.08); arch.position.set(0, 4.55, -0.15); por.add(arch);
  const ped = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 8.4, 3, 1), marble()); ped.rotation.z = Math.PI / 2; ped.scale.set(1, 1, 1.6); ped.scale.set(0.95, 1, 0.55); ped.position.set(0, 5.25, -0.15); ped.rotation.set(0, 0, Math.PI / 2); por.add(ped);
  const tri = new THREE.Shape(); tri.moveTo(-4.25, 0); tri.lineTo(4.25, 0); tri.lineTo(0, 1.35); tri.lineTo(-4.25, 0);
  const pedi = new THREE.Mesh(new THREE.ExtrudeGeometry(tri, { depth: 3.2, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05, bevelSegments: 2 }), marble()); pedi.position.set(0, 4.82, -1.75); por.add(pedi);
  por.remove(ped);
  const step = rbox(9.6, 0.5, 4.6, marble(), 0.05); step.position.set(0, -0.25, -0.2); por.add(step);
  const door = rbox(1.6, 2.8, 0.1, metal(C.bronze, { roughness: 0.45 }), 0.04); door.position.set(0, 1.4, -1.55); por.add(door);
  const conn = rbox(4.5, 4.3, 2.0, wallM, 0.05); conn.position.set(0, 2.15, -2.3); por.add(conn);
  return shadowAll(g);
}
// Луч света из окулуса
export function lightBeam(len = 8, r0 = 0.45, r1 = 1.3, color = 0xfff3d6) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r0, r1, len, 32, 1, true), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.16, depthWrite: false, side: THREE.DoubleSide, toneMapped: false, blending: THREE.AdditiveBlending }));
  return m;
}
// Пирс/волнорез из бетона с арками
export function pier(n = 4) {
  const g = new THREE.Group(); const m = concrete({ base: '#c9bcaa', seed: 9, clasts: 6 });
  const deck = rbox(n * 2.6, 0.9, 2.6, m, 0.1); deck.position.y = 1.6; g.add(deck);
  for (let i = 0; i <= n; i++) { const p = rbox(0.9, 3.6, 2.4, m, 0.12); p.position.set(-n * 1.3 + i * 2.6, -0.4, 0); g.add(p); }
  for (let i = 0; i < n; i++) { const ar = new THREE.Mesh(new THREE.TorusGeometry(0.85, 0.22, 10, 24, Math.PI), m); ar.position.set(-n * 1.3 + 1.3 + i * 2.6, 1.0, 1.21); g.add(ar); const ar2 = ar.clone(); ar2.position.z = -1.21; g.add(ar2); }
  for (let i = 0; i < n * 3; i++) { const b = puck(0.12, 0.25, metal(C.bronze)); b.position.set(-n * 1.3 + 0.4 + i * 0.85, 2.15, 1.05); g.add(b); }
  return shadowAll(g);
}
export function romanShip() {
  const g = new THREE.Group();
  const hull = new THREE.Mesh(new THREE.CapsuleGeometry(0.7, 3.4, 8, 20), wood()); hull.rotation.z = Math.PI / 2; hull.scale.set(1, 1, 0.75); hull.position.y = 0.2; g.add(hull);
  const deck = rbox(3.6, 0.15, 1.0, wood(), 0.05); deck.position.y = 0.75; g.add(deck);
  const mast = cyl(0.07, 3.2, wood(), 12); mast.position.y = 2.3; g.add(mast);
  const sail = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.7, 8, 6), matte(0xf2e6cf, { side: THREE.DoubleSide })); sail.position.set(0, 2.6, 0.05); g.add(sail);
  const st = rbox(0.12, 0.12, 2.6, matte(C.coral), 0.04); st.position.set(0, 2.6, 0.12); st.rotation.y = Math.PI / 2; g.add(st);
  return shadowAll(g);
}
// бетонная балка с арматурой (разрез)
export function beam() {
  const g = new THREE.Group();
  const body = rbox(7, 2.2, 2.2, concrete({ base: '#bdbab4', dots: '#8d8a84', dots2: '#dcdad5', seed: 12 }), 0.06); g.add(body);
  const bars = [];
  for (const [y, z] of [[-0.65, 0.6], [-0.65, -0.6], [0.65, 0.6], [0.65, -0.6]]) { const b = cyl(0.11, 7.1, metal(0x9a9ea6, { roughness: 0.4 }), 16); b.rotation.z = Math.PI / 2; b.position.set(0, y, z); g.add(b); bars.push(b); }
  for (let i = 0; i < 12; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.04, 6, 4), metal(0x9a9ea6)); r.rotation.y = Math.PI / 2; r.rotation.x = Math.PI / 4; r.position.x = -3.1 + i * 0.56; g.add(r); bars.push(r); }
  return { g: shadowAll(g), body, bars };
}
export function factory() {
  const g = new THREE.Group();
  const b = rbox(4, 2.2, 2.4, matte(0xb8b6c8), 0.1); b.position.y = 1.1; g.add(b);
  const silo = cyl(0.7, 3.6, gloss(0xd9d7e6), 32); silo.position.set(2.8, 1.8, 0); g.add(silo);
  const ch = cyl(0.32, 5.2, matte(0xc9a7a0), 24); ch.position.set(-1.2, 2.6, -0.4); g.add(ch);
  const band = cyl(0.34, 0.25, matte(C.coral), 24); band.position.set(-1.2, 4.6, -0.4); g.add(band);
  return shadowAll(g);
}
export function smoke(n = 14, mat = matte(0x9a98aa, { transparent: true, opacity: 0.85 })) {
  const g = new THREE.Group(); const ps = [];
  for (let i = 0; i < n; i++) { const s = sphere(0.5, mat, 20); g.add(s); ps.push(s); }
  g.userData.update = (t, rate = 1) => ps.forEach((s, i) => { const ph = ((t * 0.18 * rate + i / n) % 1); s.position.set(Math.sin(i * 2.1 + t * 0.3) * ph * 1.2 + ph * 1.5, ph * 5, Math.cos(i * 1.3) * ph); s.scale.setScalar(0.3 + ph * 1.6); s.visible = ph > 0.02; });
  return g;
}
export function kiln() {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(2, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), brick()); body.scale.set(1, 1.15, 1); g.add(body);
  const base = puck(2.15, 0.4, stone({ base: '#bdb2a2', seed: 21 })); base.position.y = 0.05; g.add(base);
  const mouth = new THREE.Mesh(new THREE.CircleGeometry(0.62, 32, 0, Math.PI), new THREE.MeshBasicMaterial({ color: 0xffa040, toneMapped: false })); mouth.position.set(0, 0.25, 1.97); g.add(mouth);
  const glow = new THREE.PointLight(0xff8a30, 6, 9, 1.6); glow.position.set(0, 0.6, 2.4); g.add(glow);
  const chim = cyl(0.35, 0.8, brick(), 20); chim.position.y = 2.5; g.add(chim);
  g.userData.glow = glow; g.userData.mouth = mouth;
  return shadowAll(g);
}
export function volcano({ snow = false } = {}) {
  const g = new THREE.Group();
  const cone = new THREE.Mesh(new THREE.ConeGeometry(6, 4.2, 48, 6, true), stone({ base: '#9d8f86', dots: '#7a6d66', dots2: '#b9aca2', seed: 31, rough: 0.8 }));
  const p = cone.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y > 2.0) p.setY(i, 1.75); const k = 1 + noise1(i * 0.37) * 0.04; p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k); }
  cone.geometry.computeVertexNormals(); cone.position.y = 2.1; g.add(cone);
  const crater = new THREE.Mesh(new THREE.CircleGeometry(1.15, 32), matte(0x5e5450)); crater.rotation.x = -Math.PI / 2; crater.position.y = 3.86; g.add(crater);
  return shadowAll(g);
}
export function pile(color, r = 1.2, h = 0.9, seed = 1, mat = null) {
  const geo = new THREE.ConeGeometry(r, h, 40, 6); const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y < h / 2 - 0.01) { const k = 1 + (hash(i * 3 + seed) - 0.5) * 0.12; p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k); } }
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, mat || stone({ base: color, dots: color, dots2: '#ffffff', n: 600, seed, rough: 0.3 })); m.position.y = h / 2; m.scale.y = 1; m.castShadow = m.receiveShadow = true; return m;
}
export function bucket(mat = wood()) {
  const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.34, 0.7, 28, 1, true), mat); b.material.side = THREE.DoubleSide; b.position.y = 0.35; g.add(b);
  const bot = puck(0.34, 0.06, mat); bot.position.y = 0.03; g.add(bot);
  for (const y of [0.15, 0.55]) { const h = new THREE.Mesh(new THREE.TorusGeometry(0.4 - y * 0.1, 0.025, 6, 32), metal(0x7d7a74)); h.rotation.x = Math.PI / 2; h.position.y = y; g.add(h); }
  return shadowAll(g);
}
export function trowel() {
  const g = new THREE.Group(); const blade = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.02, 3), metal(0x9c9a95)); blade.scale.set(1, 1, 1.8); g.add(blade);
  const h = cyl(0.045, 0.45, wood(), 10); h.rotation.x = Math.PI / 2.6; h.position.set(0, 0.16, -0.48); g.add(h); return shadowAll(g);
}
// раскрытый кодекс/свиток
export function book(lines = 10) {
  const g = new THREE.Group();
  const cover = rbox(4.2, 0.12, 2.8, matte(0x9b5c45), 0.04); g.add(cover);
  for (const s of [-1, 1]) {
    const pg = rbox(1.95, 0.14, 2.6, matte(0xf3e8d2), 0.03); pg.position.set(s * 1.02, 0.12, 0); pg.rotation.z = -s * 0.05; g.add(pg);
    for (let i = 0; i < lines; i++) { const l = rbox(1.5 - hash(i + s * 7) * 0.5, 0.01, 0.05, matte(0x8a7b68), 0.005); l.position.set(s * 1.02 - 0.1 + hash(i) * 0.05, 0.2, -1.05 + i * 0.22); g.add(l); }
  }
  return shadowAll(g);
}
export function microscope() {
  const g = new THREE.Group(); const w = gloss(0xf2f0f7), d = gloss(0x3d3a5c);
  const base = rbox(1.6, 0.25, 1.2, w, 0.1); g.add(base);
  const arm = rbox(0.35, 2.2, 0.4, w, 0.12); arm.position.set(-0.45, 1.2, 0); arm.rotation.z = 0.18; g.add(arm);
  const stage = rbox(1.0, 0.1, 0.9, d, 0.03); stage.position.set(0.15, 0.9, 0); g.add(stage);
  const tube = cyl(0.17, 1.2, w, 24); tube.position.set(0.1, 2.0, 0); tube.rotation.z = -0.25; g.add(tube);
  const obj = cyl(0.09, 0.35, metal(0x9aa0aa), 16); obj.position.set(0.25, 1.35, 0); g.add(obj);
  const eye = cyl(0.12, 0.35, d, 16); eye.position.set(-0.05, 2.65, 0); eye.rotation.z = -0.25; g.add(eye);
  return shadowAll(g);
}
// куб бетона с белыми включениями (видимыми в объёме)
export function clastCube(size = 2.4, n = 26, seed = 4) {
  const g = new THREE.Group();
  const body = rbox(size, size, size, concrete({ seed, clasts: 18 }), 0.12); g.add(body);
  const cl = []; for (let i = 0; i < n; i++) { const s = sphere(0.06 + hash(i + seed) * 0.09, gloss(0xffffff, { roughness: 0.6, clearcoat: 0.2 }), 14); const f = Math.floor(hash(i * 3 + seed) * 3), sgn = hash(i * 5) > 0.5 ? 1 : -1; const p = [(hash(i * 7) - 0.5) * size * 0.85, (hash(i * 11) - 0.5) * size * 0.85, (hash(i * 13) - 0.5) * size * 0.85]; p[f] = sgn * size / 2; s.position.set(...p); g.add(s); cl.push(s); }
  g.userData.clasts = cl; return shadowAll(g);
}
// капли/частицы воды
export function drops(n = 30, color = 0x8fd0e6, r = 0.06) {
  const g = new THREE.Group(); const m = gloss(color, { transparent: true, opacity: 0.85, roughness: 0.1 }); const ps = [];
  for (let i = 0; i < n; i++) { const s = sphere(r * (0.7 + hash(i) * 0.6), m, 12); g.add(s); ps.push(s); }
  g.userData.ps = ps; return g;
}
// кристалл кальцита (ромбоэдр)
export function crystal(s = 0.12, color = 0xfdfcf7) {
  const geo = new THREE.OctahedronGeometry(s, 0); geo.scale(1, 1.35, 0.8);
  const m = new THREE.Mesh(geo, gloss(color, { roughness: 0.15, transmission: 0.0, clearcoat: 1 })); m.castShadow = true; return m;
}
export function blade(w = 0.5, h = 0.03, d = 0.18, color = 0xe8f4f2) { return rbox(w, h, d, gloss(color, { roughness: 0.3 }), 0.01); }

// ───────── 2D-оверлеи ─────────
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// карточка главы (левый верх): «Глава N» + название
export function chapter(n, name, t, t0, t1) {
  const k = spring(seg(t, t0, t0 + 0.9) * 1.2, 8, 6), fo = easeIn(seg(t, t1 - 0.5, t1));
  if (k <= 0.001 || fo >= 1) return;
  ctx.save(); ctx.globalAlpha = clamp(k) * (1 - fo);
  ctx.translate(-60 * (1 - k), 0);
  ctx.font = '700 34px "Rubik"'; const a = `ГЛАВА ${n}`; const aw = ctx.measureText(a).width;
  ctx.font = '900 78px "Rubik"'; const bw = ctx.measureText(name).width;
  const w = Math.max(aw, bw) + 90;
  ctx.shadowColor = 'rgba(60,40,80,0.18)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  rr(90, 80, w, 170, 34); ctx.fillStyle = 'rgba(255,255,255,0.92)'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#e8706a'; rr(90, 80, 14, 170, 7); ctx.fill();
  ctx.fillStyle = '#7a63e6'; ctx.font = '700 34px "Rubik"'; ctx.fillText(a, 135, 132);
  ctx.fillStyle = CSS.ink; ctx.font = '900 78px "Rubik"'; ctx.fillText(name, 132, 218);
  ctx.restore();
}
// карточка-цитата
export function quote(text, who, x, y, t, t0, t1, { w = 900, size = 48 } = {}) {
  const k = spring(seg(t, t0, t0 + 0.9) * 1.2, 8, 6), fo = easeIn(seg(t, t1 - 0.5, t1));
  if (k <= 0.001 || fo >= 1) return;
  ctx.save(); ctx.globalAlpha = clamp(k) * (1 - fo);
  ctx.font = `600 ${size}px "Rubik"`;
  const words = text.split(' '); const lines = []; let cur = '';
  for (const wd of words) { const tt = cur ? cur + ' ' + wd : wd; if (ctx.measureText(tt).width > w - 120) { lines.push(cur); cur = wd; } else cur = tt; }
  if (cur) lines.push(cur);
  const h = lines.length * size * 1.3 + 150;
  ctx.translate(x, y + 30 * (1 - k));
  ctx.shadowColor = 'rgba(60,40,80,0.2)'; ctx.shadowBlur = 44; ctx.shadowOffsetY = 16;
  rr(0, 0, w, h, 36); ctx.fillStyle = 'rgba(255,252,246,0.95)'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#e9b97f'; ctx.font = '900 140px "NSerif"'; ctx.fillText('«', 26, 118);
  ctx.fillStyle = CSS.ink; ctx.font = `600 ${size}px "Rubik"`;
  lines.forEach((l, i) => { const kk = easeOut(seg(t, t0 + 0.3 + i * 0.25, t0 + 0.9 + i * 0.25)); ctx.globalAlpha = clamp(k) * (1 - fo) * kk; ctx.fillText(l, 70, 92 + i * size * 1.3); });
  ctx.globalAlpha = clamp(k) * (1 - fo) * easeOut(seg(t, t0 + 0.6 + lines.length * 0.25, t0 + 1.4 + lines.length * 0.25));
  ctx.fillStyle = '#7a63e6'; ctx.font = '700 36px "Rubik"'; ctx.fillText('— ' + who, 70, 92 + lines.length * size * 1.3 + 28);
  ctx.restore();
}
// размерная линия между двумя точками экрана
export function dimLine(a, b, label, t, t0, { color = '#e8706a', size = 44 } = {}) {
  const k = easeOut(seg(t, t0, t0 + 0.8)); if (k <= 0) return;
  const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
  const ax = lerp(mx, a.x, k), ay = lerp(my, a.y, k), bx = lerp(mx, b.x, k), by = lerp(my, b.y, k);
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 5; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
  const ang = Math.atan2(b.y - a.y, b.x - a.x);
  for (const [px, py, s] of [[ax, ay, -1], [bx, by, 1]]) { ctx.save(); ctx.translate(px, py); ctx.rotate(ang); ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(0, 18); ctx.stroke(); ctx.restore(); }
  if (k > 0.6) { ctx.globalAlpha = (k - 0.6) / 0.4; ctx.font = `900 ${size}px "Rubik"`; const tw = ctx.measureText(label).width + 40; rr(mx - tw / 2, my - size * 0.95 - 20, tw, size * 1.4, size * 0.7); ctx.fillStyle = '#fff'; ctx.fill(); ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.fillText(label, mx, my - 30); }
  ctx.restore();
}
// значок «перечёркнуто» / галочка / вопрос
export function stamp(text, x, y, t, t0, { color = '#e8706a', size = 70, rot = -0.12, out = null } = {}) {
  const k = spring(seg(t, t0, t0 + 0.7) * 1.3, 9, 5); const fo = out != null ? easeIn(seg(t, out, out + 0.4)) : 0;
  if (k <= 0.001 || fo >= 1) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(lerp(1.8, 1, clamp(k)), lerp(1.8, 1, clamp(k))); ctx.globalAlpha = clamp(k) * (1 - fo);
  ctx.font = `900 ${size}px "Rubik"`; const tw = ctx.measureText(text).width;
  ctx.strokeStyle = color; ctx.lineWidth = 8; rr(-tw / 2 - 30, -size * 0.8, tw + 60, size * 1.25, 18); ctx.stroke();
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.fillText(text, 0, size * 0.3);
  ctx.restore();
}
// шкала-сравнение (две полосы)
export function bars(items, x, y, t, t0, { w = 760, max = 1 } = {}) {
  items.forEach((it, i) => {
    const k = easeInOut(seg(t, t0 + i * 0.6, t0 + i * 0.6 + 1.6));
    if (t < t0 + i * 0.6) return;
    const yy = y + i * 120;
    ctx.save(); ctx.globalAlpha = clamp(k * 3);
    ctx.font = '700 38px "Rubik"'; ctx.fillStyle = CSS.ink; ctx.fillText(it.label, x, yy - 18);
    rr(x, yy, w, 44, 22); ctx.fillStyle = 'rgba(255,255,255,0.75)'; ctx.fill();
    rr(x, yy, Math.max(44, w * (it.v / max) * k), 44, 22); ctx.fillStyle = it.color; ctx.fill();
    ctx.font = '900 34px "Rubik"'; ctx.fillStyle = CSS.ink; ctx.fillText(it.text, x + Math.max(44, w * (it.v / max) * k) + 18, yy + 34);
    ctx.restore();
  });
}
