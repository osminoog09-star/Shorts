// Набор объектов и помощников для фильма (премиальный 3D)
import { THREE, RoundedBoxGeometry, C, CSS, W, H, matte, gloss, metal, studio, shadowAll, gear,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash } from './engine.js';

export const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
export function orbit(cam, target, r, az, el) {
  cam.position.set(target.x + Math.sin(az) * Math.cos(el) * r, target.y + Math.sin(el) * r, target.z + Math.cos(az) * Math.cos(el) * r);
  cam.lookAt(target); cam.updateMatrixWorld();
}
export function newScene(opts = {}) {
  const scene = new THREE.Scene();
  const st = studio(scene, opts);
  const cam = new THREE.PerspectiveCamera(opts.fov || 32, W / H, 0.1, 150);
  return { scene, cam, ...st };
}
export function rbox(w, h, d, mat, r = 0.12) { const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001)), mat); m.castShadow = m.receiveShadow = true; return m; }
export function sphere(r, mat, seg = 32) { const m = new THREE.Mesh(new THREE.SphereGeometry(r, seg, Math.round(seg * 0.75)), mat); m.castShadow = m.receiveShadow = true; return m; }
export function cyl(r, h, mat, seg = 32) { const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat); m.castShadow = m.receiveShadow = true; return m; }
// скруглённый цилиндр (капсула-шайба)
export function puck(r, h, mat) {
  const pts = []; const rr = Math.min(h / 2, r * 0.3);
  pts.push(new THREE.Vector2(0, -h / 2));
  for (let i = 0; i <= 6; i++) { const a = -Math.PI / 2 + (i / 6) * Math.PI / 2; pts.push(new THREE.Vector2(r - rr + Math.cos(a) * rr, -h / 2 + rr + Math.sin(a) * rr)); }
  for (let i = 0; i <= 6; i++) { const a = (i / 6) * Math.PI / 2; pts.push(new THREE.Vector2(r - rr + Math.cos(a) * rr, h / 2 - rr + Math.sin(a) * rr)); }
  pts.push(new THREE.Vector2(0, h / 2));
  const m = new THREE.Mesh(new THREE.LatheGeometry(pts, 48), mat); m.castShadow = m.receiveShadow = true; return m;
}

const K = 20;
export const pitch = (r) => r * 0.945;
export function train(defs) {
  const grp = new THREE.Group(); const gs = [];
  defs.forEach((d) => {
    const teeth = Math.max(10, Math.round(d.r * K));
    const m = gear(teeth, d.r, d.mat, { thick: d.thick ?? 0.34, spokes: d.spokes ?? (d.r > 1.1 ? 4 : d.r > 0.65 ? 3 : 0), holeR: 0.16 });
    let x = d.x || 0, y = d.y || 0, ratio = 1;
    if (d.parent != null) { const p = gs[d.parent]; const dist = pitch(p.r) + pitch(d.r); x = p.x + Math.cos(d.ang) * dist; y = p.y + Math.sin(d.ang) * dist; ratio = -p.ratio * p.teeth / teeth; }
    m.position.set(x, y, d.z || 0); grp.add(m);
    const g = { m, r: d.r, teeth, x, y, ratio, phase: 0 };
    if (d.parent != null) { const p = gs[d.parent]; g.phase = -(p.teeth / teeth) * (p.phase - d.ang) + d.ang + Math.PI + Math.PI / teeth; }
    gs.push(g);
  });
  return { grp, gs, update: (a) => gs.forEach((g) => { g.m.rotation.z = a * g.ratio + g.phase; }) };
}
export function axle(len = 0.8, r = 0.13, mat = gloss(C.white)) { const m = cyl(r, len, mat, 24); m.rotation.x = Math.PI / 2; return m; }

// Текстовый спрайт (пилюля) в 3D
export function textSprite(text, { size = 64, color = CSS.ink, bg = CSS.white, weight = 700, font = 'Rubik', scale = 1, pad = 30, radius = null } = {}) {
  const c = document.createElement('canvas'); const x = c.getContext('2d');
  const F = `${weight} ${size}px "${font}"`; x.font = F;
  const w = Math.ceil(x.measureText(text).width + pad * 2), h = Math.ceil(size * 1.5);
  c.width = w + 40; c.height = h + 40;
  const y = c.getContext('2d'); y.font = F; y.textBaseline = 'middle'; y.textAlign = 'center';
  if (bg) { y.shadowColor = 'rgba(60,40,80,.2)'; y.shadowBlur = 16; y.shadowOffsetY = 6; y.beginPath(); y.roundRect(20, 20, w, h, radius ?? h / 2); y.fillStyle = bg; y.fill(); y.shadowColor = 'transparent'; }
  y.fillStyle = color; y.fillText(text, c.width / 2, c.height / 2 + size * 0.05);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false }));
  const k = 0.006 * scale; sp.scale.set(c.width * k, c.height * k, 1);
  sp.userData.base = sp.scale.clone();
  return sp;
}
export function popScale(obj, t, t0, dur = 0.8, base = null) {
  const b = base || obj.userData.base || new THREE.Vector3(1, 1, 1);
  const k = spring(seg(t, t0, t0 + dur) * 1.3, 8, 5.5);
  obj.visible = k > 0.002;
  obj.scale.set(b.x * k, b.y * k, b.z * k);
}

// Ком корродированной бронзы
export function lump({ r = 1.4, color = C.patina, seed = 1, mat = null } = {}) {
  const g = new THREE.IcosahedronGeometry(r, 5);
  const p = g.attributes.position; const v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i); const n = v.clone().normalize();
    const d = 1 + 0.12 * Math.sin(n.x * 3.1 + seed) * Math.cos(n.y * 2.3 + seed * 2) + 0.05 * Math.sin(n.z * 5 + n.x * 4 + seed);
    v.copy(n).multiplyScalar(r * d); v.z *= 0.5; v.x *= 1.25; p.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeVertexNormals();
  const m = new THREE.Mesh(g, mat || matte(color, { roughness: 0.85 })); m.castShadow = m.receiveShadow = true; return m;
}

export function amphora(mat) {
  const pts = [[0, -1.2], [0.25, -1.15], [0.55, -0.7], [0.62, -0.1], [0.5, 0.45], [0.22, 0.75], [0.2, 1.05], [0.3, 1.15], [0.24, 1.2], [0, 1.2]].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.LatheGeometry(pts, 40), mat); g.add(body);
  for (const s of [-1, 1]) { const h = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.055, 12, 24, Math.PI), mat); h.position.set(s * 0.33, 0.82, 0); h.rotation.z = s > 0 ? -Math.PI / 2 : Math.PI / 2; g.add(h); }
  return shadowAll(g);
}
export function coinStack(mat, n = 5) { const g = new THREE.Group(); for (let i = 0; i < n; i++) { const c = puck(0.38, 0.1, mat); c.position.set(hash(i) * 0.08, -0.45 + i * 0.11, hash(i + 9) * 0.08); g.add(c); } return g; }
export function bust(mat) {
  const g = new THREE.Group();
  const head = sphere(0.62, mat); head.scale.set(0.9, 1.1, 0.95); head.position.y = 1.1; g.add(head);
  const nose = sphere(0.13, mat, 16); nose.scale.set(0.8, 1.4, 1); nose.position.set(0, 1.08, 0.58); g.add(nose);
  const beard = sphere(0.42, mat); beard.scale.set(1, 0.85, 0.7); beard.position.set(0, 0.62, 0.3); g.add(beard);
  for (let i = 0; i < 7; i++) { const c = sphere(0.19, mat, 16); const a = -1.4 + i * 0.47; c.position.set(Math.sin(a) * 0.56, 1.62 + Math.cos(a) * 0.1, Math.cos(a) * 0.45 - 0.1); g.add(c); }
  const neck = cyl(0.3, 0.5, mat); neck.position.y = 0.3; g.add(neck);
  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.85, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), mat); chest.scale.set(1.3, 0.7, 0.8); chest.position.y = -0.3; g.add(chest);
  return shadowAll(g);
}
export function boat() {
  const g = new THREE.Group();
  const sh = new THREE.Shape(); sh.moveTo(-2.2, 0.4); sh.quadraticCurveTo(-1.6, -0.6, 0, -0.65); sh.quadraticCurveTo(1.6, -0.6, 2.4, 0.6); sh.quadraticCurveTo(0.2, 0.25, -2.2, 0.4);
  const hull = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 1.1, bevelEnabled: true, bevelSize: 0.12, bevelThickness: 0.14, bevelSegments: 4, curveSegments: 24 }), gloss(C.coral)); hull.position.z = -0.55; g.add(hull);
  const deck = rbox(3.6, 0.12, 1.2, matte(C.sand), 0.05); deck.position.y = 0.32; g.add(deck);
  const mast = cyl(0.07, 3.2, gloss(C.white), 16); mast.position.set(0.2, 1.9, 0); g.add(mast);
  const ss = new THREE.Shape(); ss.moveTo(0, 0); ss.quadraticCurveTo(1.2, 0.6, 1.6, 0.15); ss.lineTo(0, 2.5); ss.lineTo(0, 0);
  const sail = new THREE.Mesh(new THREE.ExtrudeGeometry(ss, { depth: 0.04, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03, bevelSegments: 2 }), matte(C.white)); sail.position.set(0.28, 0.65, 0); g.add(sail);
  return shadowAll(g);
}
export function diver() {
  const g = new THREE.Group();
  const suit = gloss(C.butter);
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 0.8, 8, 20), suit); g.add(body);
  const helm = sphere(0.5, metal(C.gold)); helm.position.y = 0.95; g.add(helm);
  const win = puck(0.22, 0.12, gloss(C.sky)); win.rotation.x = Math.PI / 2; win.position.set(0, 0.97, 0.45); g.add(win);
  for (const s of [-1, 1]) {
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.14, 0.6, 6, 12), suit); arm.position.set(s * 0.55, 0.1, 0); arm.rotation.z = s * 0.5; arm.name = s < 0 ? 'armL' : 'armR'; g.add(arm);
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.6, 6, 12), suit); leg.position.set(s * 0.22, -0.95, 0); g.add(leg);
    const boot = rbox(0.3, 0.2, 0.42, matte(C.deep), 0.08); boot.position.set(s * 0.22, -1.4, 0.06); g.add(boot);
  }
  return shadowAll(g);
}
export function waves(w = 60, d = 40, segs = 90, mat = gloss(C.sea, { roughness: 0.2 })) {
  const geo = new THREE.PlaneGeometry(w, d, segs, Math.round(segs * d / w)); geo.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(geo, mat); m.receiveShadow = true;
  const base = geo.attributes.position.array.slice();
  const h = (x, z, t, a) => a * (0.35 * Math.sin(x * 0.45 + t * 1.3) + 0.22 * Math.sin(z * 0.7 - t * 1.0 + x * 0.2) + 0.08 * Math.sin((x + z) * 1.4 + t * 2.4));
  m.userData.update = (t, a = 1) => {
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) p.array[i * 3 + 1] = h(base[i * 3], base[i * 3 + 2], t, a);
    p.needsUpdate = true; geo.computeVertexNormals();
  };
  m.userData.h = h;
  return m;
}
export function cloud(mat = matte(C.white)) {
  const g = new THREE.Group();
  [[0, 0, 0, 1], [0.9, -0.15, 0.1, 0.75], [-0.95, -0.2, 0, 0.7], [0.3, 0.45, -0.1, 0.7], [-0.4, 0.35, 0.1, 0.6]].forEach(([x, y, z, r]) => { const s = sphere(r, mat, 24); s.position.set(x, y, z); g.add(s); });
  return g;
}
export function island() {
  const g = new THREE.Group();
  const rock = sphere(2.4, matte(C.sage), 32); rock.scale.set(1.6, 0.55, 1.1); g.add(rock);
  const top = sphere(1.3, matte(C.mint), 24); top.scale.set(1.2, 0.6, 1); top.position.set(-0.6, 0.9, 0); g.add(top);
  const top2 = sphere(0.9, matte(C.sage), 24); top2.scale.set(1.1, 0.7, 1); top2.position.set(1.0, 0.75, 0.3); g.add(top2);
  return shadowAll(g);
}

// Корпус механизма (реконструкция): рамка-ящик, передний циферблат, ручка, задние спирали
export function mechanismBox() {
  const g = new THREE.Group();
  const wood = matte(0xd8a77a, { roughness: 0.6 });
  const box = rbox(3.2, 4.2, 1.3, wood, 0.18); g.add(box);
  const face = rbox(2.8, 3.8, 0.1, metal(C.bronze), 0.08); face.position.z = 0.66; g.add(face);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.12, 0.09, 16, 96), metal(C.gold)); ring.position.set(0, 0.2, 0.74); ring.castShadow = true; g.add(ring);
  const dial = puck(1.02, 0.06, matte(C.cream)); dial.rotation.x = Math.PI / 2; dial.position.set(0, 0.2, 0.72); g.add(dial);
  for (let i = 0; i < 12; i++) { const tk = rbox(0.05, 0.18, 0.04, matte(C.deep), 0.02); const a = (i / 12) * Math.PI * 2; tk.position.set(Math.cos(a) * 0.9, 0.2 + Math.sin(a) * 0.9, 0.77); tk.rotation.z = a + Math.PI / 2; g.add(tk); }
  const sunP = new THREE.Group(); sunP.position.set(0, 0.2, 0.8); g.add(sunP);
  const sp = rbox(0.07, 0.95, 0.04, gloss(C.butter), 0.03); sp.position.y = 0.48; sunP.add(sp);
  const sb = sphere(0.16, gloss(C.butter, { emissive: 0xffb400, emissiveIntensity: 0.25 })); sb.position.y = 0.95; sunP.add(sb);
  const moonP = new THREE.Group(); moonP.position.set(0, 0.2, 0.88); g.add(moonP);
  const mp = rbox(0.06, 0.7, 0.04, gloss(C.white), 0.03); mp.position.y = 0.35; moonP.add(mp);
  const moonBall = new THREE.Group(); moonBall.position.y = 0.7; moonP.add(moonBall);
  const mw = new THREE.Mesh(new THREE.SphereGeometry(0.14, 32, 24, 0, Math.PI), gloss(0xf4f1ea)); moonBall.add(mw);
  const md = new THREE.Mesh(new THREE.SphereGeometry(0.14, 32, 24, Math.PI, Math.PI), gloss(C.deep)); moonBall.add(md);
  const hub = puck(0.14, 0.18, gloss(C.coral)); hub.rotation.x = Math.PI / 2; hub.position.set(0, 0.2, 0.9); g.add(hub);
  const crank = new THREE.Group(); crank.position.set(1.68, 0, 0); g.add(crank);
  const ax = cyl(0.1, 0.4, metal(C.bronze), 16); ax.rotation.z = Math.PI / 2; ax.position.x = 0.2; crank.add(ax);
  const arm = rbox(0.14, 0.95, 0.14, metal(C.bronze), 0.06); arm.position.set(0.42, 0.4, 0); crank.add(arm);
  const knob = cyl(0.12, 0.45, gloss(C.coral), 16); knob.rotation.z = Math.PI / 2; knob.position.set(0.62, 0.85, 0); crank.add(knob);
  const back = new THREE.Group(); back.position.z = -0.66; back.rotation.y = Math.PI; g.add(back);
  const plate = rbox(2.8, 3.8, 0.08, metal(C.bronze), 0.06); back.add(plate);
  const spiral = (cy, turns, r0, r1, mat) => {
    const pts = []; const n = turns * 64;
    for (let i = 0; i <= n; i++) { const a = (i / 64) * Math.PI * 2; const r = lerp(r0, r1, i / n); pts.push(new THREE.Vector3(Math.cos(a) * r, cy + Math.sin(a) * r, 0.06)); }
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n, 0.035, 8), mat); m.castShadow = true; return m;
  };
  back.add(spiral(0.95, 5, 0.18, 0.8, gloss(C.butter)));
  back.add(spiral(-0.95, 4, 0.18, 0.8, gloss(C.lav)));
  const bp1 = new THREE.Group(); bp1.position.set(0, 0.95, 0.12); back.add(bp1); const b1 = rbox(0.06, 0.82, 0.04, gloss(C.coral), 0.02); b1.position.y = 0.41; bp1.add(b1);
  const bp2 = new THREE.Group(); bp2.position.set(0, -0.95, 0.12); back.add(bp2); const b2 = rbox(0.06, 0.82, 0.04, gloss(C.coral), 0.02); b2.position.y = 0.41; bp2.add(b2);
  shadowAll(g);
  return { g, sunP, moonP, moonBall, crank, back, bp1, bp2 };
}

export function laptop() {
  const g = new THREE.Group();
  const al = gloss(0xd9dde8, { metalness: 0.3, roughness: 0.3 });
  const base = rbox(2.4, 0.12, 1.6, al, 0.05); g.add(base);
  const lid = new THREE.Group(); lid.position.set(0, 0.06, -0.78); g.add(lid);
  const scr = rbox(2.4, 1.6, 0.08, al, 0.05); scr.position.set(0, 0.8, 0); lid.add(scr);
  const disp = new THREE.Mesh(new THREE.PlaneGeometry(2.15, 1.38), new THREE.MeshBasicMaterial({ color: 0x9fb4ff, toneMapped: false })); disp.position.set(0, 0.8, 0.045); lid.add(disp);
  lid.rotation.x = -0.28;
  return shadowAll(g);
}
export function scanner() {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.62, 32, 96), gloss(C.white)); g.add(ring);
  const band = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.635, 16, 96, Math.PI * 0.35), gloss(C.lav)); band.rotation.z = Math.PI * 0.32; g.add(band);
  const glow = new THREE.Mesh(new THREE.TorusGeometry(1.98, 0.045, 12, 96), new THREE.MeshBasicMaterial({ color: 0x9fe8ff, toneMapped: false })); g.add(glow);
  const stand = rbox(2.4, 1.6, 1.6, gloss(C.white), 0.3); stand.position.y = -3.0; g.add(stand);
  return shadowAll(g);
}
export function clockTower() {
  const g = new THREE.Group();
  const tower = rbox(1.6, 5, 1.6, matte(C.cream), 0.15); tower.position.y = 2.5; g.add(tower);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(1.3, 1.8, 4), gloss(C.coral)); roof.position.y = 5.9; roof.rotation.y = Math.PI / 4; roof.castShadow = true; g.add(roof);
  const face = puck(0.6, 0.12, matte(C.butter)); face.rotation.x = Math.PI / 2; face.position.set(0, 3.9, 0.82); g.add(face);
  const hand = rbox(0.07, 0.5, 0.05, matte(C.deep), 0.03); hand.geometry.translate(0, 0.22, 0); hand.position.set(0, 3.9, 0.9); g.add(hand); g.userData.hand = hand;
  const hand2 = rbox(0.07, 0.35, 0.05, matte(C.deep), 0.03); hand2.geometry.translate(0, 0.15, 0); hand2.position.set(0, 3.9, 0.92); g.add(hand2); g.userData.hand2 = hand2;
  const door = rbox(0.6, 1.0, 0.1, gloss(C.lav), 0.08); door.position.set(0, 0.5, 0.82); g.add(door);
  return shadowAll(g);
}
export function questionMark(mat) {
  const g = new THREE.Group();
  const curve = new THREE.CatmullRomCurve3([v3(-0.45, 0.55, 0), v3(-0.35, 0.95, 0), v3(0, 1.1, 0), v3(0.42, 0.92, 0), v3(0.45, 0.5, 0), v3(0.12, 0.22, 0), v3(0.02, -0.15, 0)]);
  g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.16, 16), mat));
  const capA = sphere(0.16, mat, 16); capA.position.copy(curve.getPoint(0)); g.add(capA);
  const capB = sphere(0.16, mat, 16); capB.position.copy(curve.getPoint(1)); g.add(capB);
  const dot = sphere(0.2, mat); dot.position.set(0.02, -0.6, 0); g.add(dot);
  return shadowAll(g);
}
export { THREE, C, CSS, matte, gloss, metal, gear, shadowAll };
