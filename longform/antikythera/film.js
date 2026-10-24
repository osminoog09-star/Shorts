import { THREE, RoundedBoxGeometry, C, CSS, W, H, render, matte, gloss, metal, studio, shadowAll, gear, clear2d, ctx, title, pill, counter, leader, iris,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, pop, hash, noise1, project } from './engine.js';

// ───────── помощники ─────────
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
function orbit(cam, target, r, az, el) {
  cam.position.set(target.x + Math.sin(az) * Math.cos(el) * r, target.y + Math.sin(el) * r, target.z + Math.cos(az) * Math.cos(el) * r);
  cam.lookAt(target); cam.updateMatrixWorld();
}
const K = 20;
const pitch = (r) => r * 0.945;
function train(defs) {
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
function axle(len = 0.8, r = 0.13, mat = gloss(C.white)) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 24), mat); m.rotation.x = Math.PI / 2; m.castShadow = true; return m;
}

// ───────── сцена 01: хук — механизм на пьедестале ─────────
const S1 = (() => {
  const scene = new THREE.Scene();
  studio(scene, { bg: C.cream, floorY: -3.2, key: [5, 10, 7] });
  const cam = new THREE.PerspectiveCamera(32, W / H, 0.1, 120);
  const ped = new THREE.Mesh(new RoundedBoxGeometry(9, 0.7, 4.2, 6, 0.3), matte(C.sand)); ped.position.y = -2.85; shadowAll(ped); scene.add(ped);
  const back = new THREE.Mesh(new RoundedBoxGeometry(8.4, 5.6, 0.35, 6, 0.16), matte(C.lav)); back.position.set(0.2, 0.1, -1.1); shadowAll(back); scene.add(back);
  const tr = train([
    { r: 2.1, mat: metal(C.bronze), x: -0.6, y: 0.1 },
    { r: 0.95, mat: gloss(C.mint), parent: 0, ang: 0.15 },
    { r: 0.62, mat: gloss(C.peach), parent: 1, ang: 1.9, z: 0.02 },
    { r: 1.25, mat: gloss(C.pink), parent: 0, ang: 3.75, z: -0.02 },
    { r: 0.55, mat: metal(C.gold), parent: 3, ang: 1.6 },
    { r: 0.72, mat: gloss(C.sky), parent: 1, ang: -1.4 },
  ]);
  tr.grp.position.z = -0.55; scene.add(tr.grp);
  tr.gs.forEach((g) => { const a = axle(0.7); a.position.set(g.x, g.y, 0.05); tr.grp.add(a); });
  const ptr = new THREE.Group(); ptr.position.set(-0.6, 0.1, 0.35); tr.grp.add(ptr);
  const bar = new THREE.Mesh(new RoundedBoxGeometry(0.16, 1.9, 0.12, 3, 0.06), gloss(C.white)); bar.position.y = 0.95; bar.castShadow = true; ptr.add(bar);
  const moon = new THREE.Mesh(new THREE.SphereGeometry(0.24, 32, 24), gloss(C.butter)); moon.position.y = 1.9; moon.castShadow = true; ptr.add(moon);
  const target = v3(-0.2, 0.2, -0.4);
  function update(t) {
    const a = t * 0.42 + 0.3 * smooth(seg(t, 9.4, 10.4));
    tr.update(a);
    ptr.rotation.z = -a * 0.37;
    const az = lerp(-0.62, 0.28, easeIO2(seg(t, 0, 16)));
    const el = lerp(0.36, 0.16, easeIO2(seg(t, 0, 16)));
    let r = lerp(15.5, 11.2, easeIO2(seg(t, 0, 15)));
    r -= 7.5 * easeIn(seg(t, 15.8, 17.8));
    orbit(cam, target, r, az, el);
  }
  return { scene, cam, update, target };
})();

function s01(t) {
  S1.update(t);
  const focus = S1.cam.position.distanceTo(S1.target);
  render(S1.scene, S1.cam, { time: t, focus, aperture: 0.0009, maxblur: 0.01 });
  clear2d();
  title('2000+ лет', 150, 250, t, 1.5, { size: 150, align: 'left', out: 8.8 });
  pill('без экрана', 150, 360, t, 4.3, { dot: CSS.coral, out: 8.8, align: 'left' });
  pill('без электричества', 150, 452, t, 5.1, { dot: CSS.coral, out: 8.8, align: 'left' });
  pill('без единого чипа', 150, 544, t, 6.6, { dot: CSS.coral, out: 8.8, align: 'left' });
  title('Предсказывал', 150, 300, t, 8.9, { size: 110, align: 'left', out: 14.0 });
  title('затмения', 150, 420, t, 9.4, { size: 110, align: 'left', color: CSS.coral, out: 14.0 });
  title('…и его разгадали', 1780, 860, t, 13.6, { size: 84, align: 'right' });
  title('другие компьютеры', 1780, 960, t, 14.4, { size: 84, align: 'right', color: '#7a63e6' });
  iris(seg(t, 16.6, 17.8), 960, 540, CSS.sky);
}

export const SCENES = [{ dur: 17.8, fn: s01, voice: 's01', vo: 0.6 }];
export const DURATION = SCENES.reduce((a, s) => a + s.dur, 0);
export function renderAt(t) {
  let acc = 0;
  for (const s of SCENES) { if (t < acc + s.dur || s === SCENES[SCENES.length - 1]) { s.fn(t - acc); return; } acc += s.dur; }
}
