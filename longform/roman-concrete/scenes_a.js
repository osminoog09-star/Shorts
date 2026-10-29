// Сцены s01–s07: хук, вступление, Пантеон, гавани, современный бетон, рецепт, Витрувий
import { render, clear2d, ctx, title, pill, counter, project, W, H, THREE, C, CSS, matte, gloss, metal,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { VO, cue, dof, shot, v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, waves, cloud,
  stone, concrete, marble, brick, wood, shadowAll, column, pantheon, lightBeam, pier, romanShip, beam, factory, smoke, kiln, volcano,
  pile, bucket, trowel, book, microscope, clastCube, drops, crystal, chapter, quote, dimLine, stamp, bars } from './lib.js';

const RED = '#e8706a', PURPLE = '#7a63e6';

// ───────── общие сцены (используются в нескольких местах) ─────────
export const PAN = (() => {
  const S = newScene({ bg: 0xdbe9f3, floorY: 0, key: [9, 14, 10], shadowSize: 20, keyI: 3.1 });
  S.ground.material = stone({ base: '#e6dccd', dots: '#c9bba7', dots2: '#f5efe6', n: 700, seed: 41, rep: 18 }); S.ground.material.map.repeat.set(18, 18);
  const p = pantheon(); S.scene.add(p);
  for (let i = 0; i < 9; i++) { const c = new THREE.Mesh(new THREE.ConeGeometry(0.55, 3.2, 16), matte(0x9fbf8f)); const a = -0.9 + i * 0.22; c.position.set(Math.sin(a) * 15 + (i % 2) * 1.5, 1.6, Math.cos(a) * 15 - 3); c.castShadow = true; S.scene.add(c); }
  for (let i = 0; i < 5; i++) { const b = rbox(2.2, 0.45, 0.7, marble(), 0.08); b.position.set(-8 + i * 4, 0.22, 13); S.scene.add(b); }
  const fount = puck(1.4, 0.5, marble()); fount.position.set(0, 0.25, 15); S.scene.add(fount);
  const ob = rbox(0.5, 4.5, 0.5, stone({ base: '#d8b997', seed: 44 }), 0.05); ob.position.set(0, 2.5, 15); S.scene.add(ob);
  const clouds = [[-14, 13, -20, 2.4], [10, 15, -24, 3], [20, 11, -12, 1.8]].map(([x, y, z, s]) => { const c = cloud(); c.position.set(x, y, z); c.scale.setScalar(s); S.scene.add(c); return c; });
  return { ...S, p, clouds };
})();
export const PANI = (() => {
  const S = newScene({ bg: 0xfff1d6, floorY: 0, key: [0, 30, 0.5], shadowSize: 8, keyI: 2.4, fill: 0.55 });
  S.ground.material = stone({ base: '#e9dfd2', dots: '#b9a58e', dots2: '#cfd9e2', n: 500, seed: 51, rep: 6 });
  const p = pantheon(); p.traverse((m) => { if (m.isMesh) m.material.side = THREE.DoubleSide; }); S.scene.add(p);
  const beamM = lightBeam(8.5, 0.5, 1.6); beamM.position.y = 5.3; S.scene.add(beamM);
  const spot = new THREE.SpotLight(0xfff0d0, 120, 20, 0.22, 0.5, 1.4); spot.position.set(0, 9.6, 0); spot.target.position.set(0.6, 0, 0.8); spot.castShadow = true; S.scene.add(spot); S.scene.add(spot.target);
  const disc = new THREE.Mesh(new THREE.CircleGeometry(1.5, 48), new THREE.MeshBasicMaterial({ color: 0xfff6e2, transparent: true, opacity: 0.5, toneMapped: false })); disc.rotation.x = -Math.PI / 2; disc.position.set(0.6, 0.01, 0.8); S.scene.add(disc);
  return { ...S, p, beamM };
})();
export const BEAM = (() => {
  const S = newScene({ bg: 0xd9dbe6, floorY: -2.2, key: [5, 9, 7] });
  const b = beam(); b.g.position.y = 0.6; S.scene.add(b.g);
  for (const x of [-3, 3]) { const s = rbox(0.9, 2.2, 2.4, concrete({ base: '#c4c2bc', seed: 61 }), 0.05); s.position.set(x, -1.1, 0); S.scene.add(s); }
  // трещина на передней грани — ломаная из тонких тёмных брусков
  const crack = new THREE.Group(); crack.position.set(0, 0.6, 1.11); S.scene.add(crack);
  const pts = [[0.1, -1.05], [0.25, -0.7], [0.05, -0.35], [0.3, 0.0], [0.12, 0.35], [0.28, 0.7]];
  const segs = [];
  for (let i = 0; i < pts.length - 1; i++) { const [x0, y0] = pts[i], [x1, y1] = pts[i + 1]; const L = Math.hypot(x1 - x0, y1 - y0); const m = rbox(0.06, L + 0.04, 0.02, matte(0x3b3732), 0.01); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, 0); m.rotation.z = -Math.atan2(x1 - x0, y1 - y0); crack.add(m); segs.push(m); }
  const rust = new THREE.Group(); rust.position.set(0, 0.6, 1.115); S.scene.add(rust);
  const rmat = matte(0xb4572d, { transparent: true, opacity: 0 });
  for (let i = 0; i < 7; i++) { const st = rbox(0.08 + hash(i) * 0.06, 0.5 + hash(i + 3) * 0.6, 0.01, rmat, 0.02); st.position.set(-0.2 + i * 0.12, -0.75 - hash(i + 7) * 0.2, 0); rust.add(st); }
  const chunks = []; for (let i = 0; i < 6; i++) { const c = rbox(0.25 + hash(i) * 0.2, 0.12, 0.22, concrete({ base: '#bdbab4', seed: 62 }), 0.04); S.scene.add(c); chunks.push(c); }
  const dr = drops(16, 0x7fb9d6, 0.05); S.scene.add(dr);
  const fac = factory(); fac.position.set(14, -2.2, -6); fac.scale.setScalar(1.1); S.scene.add(fac);
  const sm = smoke(16); sm.position.set(14 - 1.32, 3.6, -6.4); S.scene.add(sm);
  return { ...S, b, crack, segs, rust, rmat, chunks, dr, fac, sm };
})();
export function beamAt(S, t, crackK, rustK, spallK, rainK) {
  S.segs.forEach((m, i) => { const k = clamp(crackK * S.segs.length - i); m.visible = k > 0.01; m.scale.set(1 + rustK * 1.5, k, 1); });
  S.rmat.opacity = rustK * 0.9;
  S.b.bars.forEach((b, i) => { if (i < 4) { b.material.color.set(new THREE.Color(0x9a9ea6).lerp(new THREE.Color(0xa4532c), rustK)); b.material.metalness = lerp(0.75, 0.25, rustK); b.scale.set(1 + rustK * 0.5, 1, 1 + rustK * 0.5); } });
  S.chunks.forEach((c, i) => { const k = clamp(spallK * 1.6 - i * 0.12); const x = -0.6 + i * 0.25; c.position.set(x, lerp(-0.45, -2.1, easeIn(k)), 1.0 + hash(i) * 0.1); c.rotation.set(k * (2 + i), k * i, k); c.visible = spallK > 0; });
  S.dr.userData.ps.forEach((p, i) => { const ph = (t * 0.8 + hash(i)) % 1; p.position.set(0.2 + (hash(i + 2) - 0.5) * 0.3, lerp(3.2, 1.6, ph), 1.15); p.visible = rainK > 0 && ph < 0.95; p.scale.setScalar(rainK); });
}
export const VOLC = (() => {
  const S = newScene({ bg: 0xf0d9c6, floorY: 0, key: [-6, 12, 8], shadowSize: 18 });
  S.ground.material.color.set(0xe3cdb7);
  const v = volcano(); v.scale.setScalar(1.6); v.position.set(0, 0, -6); S.scene.add(v);
  const sea = waves(80, 30, 60, gloss(0x8fc6dc, { roughness: 0.2 })); sea.position.set(0, 0.05, 14); S.scene.add(sea);
  const ash = smoke(22, matte(0x6f6870, { transparent: true, opacity: 0.9 })); ash.position.set(0, 6.3, -6); ash.scale.setScalar(1.6); S.scene.add(ash);
  const houses = []; for (let i = 0; i < 14; i++) { const h = rbox(0.9 + hash(i) * 0.6, 0.6 + hash(i + 1) * 0.5, 0.9, matte([0xf1e3cf, 0xe9cdb2, 0xf3d9c4][i % 3]), 0.06); h.position.set(-8 + (i % 7) * 2.3 + hash(i + 2), 0.3, 5 + Math.floor(i / 7) * 1.8); S.scene.add(h); const r = rbox(1.05 + hash(i) * 0.6, 0.12, 1.05, matte(0xc4714f), 0.04); r.position.copy(h.position); r.position.y = h.position.y + h.geometry.parameters.height / 2 + 0.06; S.scene.add(r); houses.push(h); }
  const ship = romanShip(); ship.position.set(4, 0, 12); ship.rotation.y = -2.3; S.scene.add(ship);
  return { ...S, v, sea, ash, ship };
})();
export const CUBE = (() => {
  const S = newScene({ bg: C.cream, floorY: -1.8, key: [4, 9, 6] });
  const cube = clastCube(2.6, 30, 7); S.scene.add(cube);
  const ped = puck(2.2, 0.35, marble()); ped.position.y = -1.62; S.scene.add(ped);
  return { ...S, cube };
})();

// ───────── s01. Хук ─────────
export function s01(t) {
  const id = 's01';
  const tB = cue(id, 'нём', 0, 4.2), tC = cue(id, 'современные', 0, 7.3), tD = cue(id, 'римляне', 0, 12.5), tE = cue(id, 'конце', 0, 17.5), end = 30;
  clear2d();
  shot(t, [
    [0, (lt, k) => {
      const S = PAN; S.clouds.forEach((c, i) => (c.position.x += 0.0));
      orbit(S.cam, v3(0, 4.2, 0), lerp(34, 24, easeIO2(k)), lerp(0.55, 0.32, easeIO2(k)), lerp(0.05, 0.13, k));
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 4, 4), 0.0005) });
      title('1900 лет', 120, 250, t, 0.4, { size: 170, align: 'left', out: tB - 0.45 });
      pill('и он всё ещё стоит', 125, 360, t, 1.6, { dot: RED, align: 'left', out: tB - 0.45 });
    }],
    [tB, (lt, k) => {
      const S = PANI;
      S.cam.fov = 58; S.cam.updateProjectionMatrix();
      S.cam.position.set(Math.sin(lt * 0.15) * 1.2, 1.4, 2.4); S.cam.lookAt(0.4 * Math.sin(lt * 0.1), 8.2, -0.5); S.cam.updateMatrixWorld();
      render(S.scene, S.cam, { time: t, focus: 7, aperture: 0.0003 });
      title('0 стальных прутьев', 120, 930, t, tB + 0.3, { size: 110, align: 'left', out: tC - 0.4 });
    }],
    [tC, (lt, k) => {
      const S = BEAM; beamAt(S, lt, easeOut(seg(lt, 0.5, 2.5)), smooth(seg(lt, 1.5, 4.5)), easeIn(seg(lt, 3.6, 5.2)), 1);
      orbit(S.cam, v3(0, 0.3, 0), lerp(9.5, 8, k), lerp(0.4, 0.15, k), 0.12);
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.3, 1.1)) });
      title('а наш бетон', 120, 230, t, tC + 0.2, { size: 100, align: 'left', out: tD - 0.4 });
      title('крошится через десятилетия', 120, 345, t, tC + 0.9, { size: 80, align: 'left', color: RED, out: tD - 0.4 });
    }],
    [tD, (lt, k) => {
      const S = CUBE; S.cube.rotation.set(0.4 + lt * 0.15, lt * 0.5, 0);
      orbit(S.cam, v3(0, 0, 0), lerp(8.5, 6.5, easeIO2(k)), 0.3, 0.25);
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0), 0.0012) });
      title('секрет —', 120, 250, t, tD + 0.2, { size: 110, align: 'left', out: tE - 0.4 });
      title('внутри', 120, 370, t, tD + 0.7, { size: 130, align: 'left', color: PURPLE, out: tE - 0.4 });
    }],
    [tE, (lt, k) => {
      const S = VOLC; S.ash.userData.update(t, 1.4); S.sea.userData.update(t, 0.5);
      orbit(S.cam, v3(0, 3, -2), lerp(30, 24, k), lerp(-0.25, 0.05, k), 0.14);
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, -4), 0.0005) });
      title('доказательство', 120, 250, t, tE + 0.3, { size: 110, align: 'left' });
      pill('Помпеи · декабрь 2025', 125, 360, t, tE + 1.1, { dot: RED, align: 'left' });
    }],
  ], end);
}

// ───────── s02. Вступление (ведущий справа внизу) ─────────
export function s02(t) {
  const S = CUBE; S.cube.rotation.set(0.35, t * 0.35, 0);
  orbit(S.cam, v3(-2.4, 0.2, 0), lerp(10, 8.5, easeIO2(seg(t, 0, 10))), lerp(-0.45, -0.2, easeIO2(seg(t, 0, 10))), 0.2);
  render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0), 0.0012) });
  clear2d();
  title('РИМСКИЙ БЕТОН', 120, 250, t, 0.3, { size: 120, align: 'left' });
  title('который чинит себя сам', 120, 360, t, 0.9, { size: 72, align: 'left', color: PURPLE });
  const cc = (w, n, f) => cue('s02', w, n, 0.6 + f * ((window.VDUR && window.VDUR.s02) || 24));
  const L = [['как стоит купол без прута', 'купол', 0, 0.2, '#ffdc7a'], ['почему наш бетон ржавеет', 'почему', 0, 0.33, RED], ['маяк английского инженера', 'английский', 0, 0.45, '#8fd0e6'],
    ['что достали буром со дна моря', 'буром', 0, 0.6, '#8fd0e6'], ['кучи рабочих в Помпеях', 'кучи', 0, 0.72, '#e9b97f'], ['и три мифа о римском бетоне', 'мифа', 0, 0.85, '#86dcbc']];
  L.forEach(([tx, w, n, f, dot], i) => pill(tx, 125, 470 + i * 88, t, cc(w, n, f), { dot, align: 'left', size: 36 }));
}

// ───────── s03. Пантеон ─────────
const DOME = (() => {
  const S = newScene({ bg: 0xeee6f6, floorY: 0, key: [7, 12, 9], shadowSize: 12 });
  const p = pantheon({ cut: true }); S.scene.add(p);
  // слои заполнителя в разрезе купола: тяжёлый → лёгкий
  const bands = [];
  const cols = [0x8d8178, 0xa89a8d, 0xc8b8a6, 0xe5d8c3, 0xf6efe2];
  for (let i = 0; i < 5; i++) {
    const a0 = (i / 5) * (Math.PI / 2 - 0.09), a1 = ((i + 1) / 5) * (Math.PI / 2 - 0.09);
    const sh = new THREE.Shape(); const Ri = 4.55, Ro = 5.0 + (5 - i) * 0.12;
    sh.moveTo(Math.cos(a0) * Ri, Math.sin(a0) * Ri); sh.lineTo(Math.cos(a0) * Ro, Math.sin(a0) * Ro);
    for (let k = 1; k <= 8; k++) { const a = lerp(a0, a1, k / 8); sh.lineTo(Math.cos(a) * Ro, Math.sin(a) * Ro); }
    for (let k = 8; k >= 0; k--) { const a = lerp(a0, a1, k / 8); sh.lineTo(Math.cos(a) * Ri, Math.sin(a) * Ri); }
    for (const sgn of [1, -1]) { const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), matte(cols[i], { side: THREE.DoubleSide })); m.position.set(0, 4.6, 0.01); m.scale.x = sgn; S.scene.add(m); bands.push(m); }
  }
  const lab = ['травертин', 'туф', 'туф и кирпич', 'кирпич', 'пемза'].map((tx) => textSprite(tx, { size: 54, scale: 1.1 }));
  lab.forEach((l, i) => { const a = ((i + 0.5) / 5) * (Math.PI / 2 - 0.09); l.position.set(Math.cos(a) * 6.4 + 1.2, 4.6 + Math.sin(a) * 6.2, 0.3); S.scene.add(l); });
  const people = []; for (let i = 0; i < 4; i++) { const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.45, 6, 12), matte([C.coral, C.lav, C.mint, C.butter][i])); b.position.y = 0.38; g.add(b); const h = sphere(0.1, matte(0xf1c9a8)); h.position.y = 0.78; g.add(h); g.position.set(-2.5 + i * 1.6, 0, 0.6 + hash(i)); S.scene.add(shadowAll(g)); people.push(g); }
  return { ...S, p, bands, lab };
})();
export function s03(t) {
  const id = 's03';
  const tCup = cue(id, 'купол', 0, 6), tWorld = cue(id, 'самый', 0, 9), tOc = cue(id, 'окулус', 0, 14), tLight = cue(id, 'легче', 0, 19), tCof = cue(id, 'изнутри', 0, 26), tEnd = cue(id, 'девятнадцать', 0, 33), end = 46;
  clear2d();
  shot(t, [
    [0, (lt, k) => {
      const S = PAN; orbit(S.cam, v3(0, 4.2, 0), lerp(28, 22, easeIO2(k)), lerp(-0.6, -0.2, easeIO2(k)), lerp(0.18, 0.1, k));
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 4, 2), 0.0005) });
      chapter(1, 'Загадка', t, 0.2, 5.5);
      pill('Рим · 128 год н. э. · император Адриан', 125, 980, t, 1.4, { dot: RED, align: 'left', size: 38, out: tCup - 0.3 });
    }],
    [tCup, (lt, k) => {
      const S = DOME; orbit(S.cam, v3(0, 5, 0), lerp(24, 20, k), lerp(0.05, -0.08, k), 0.12);
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 5, 0), 0.0004) });
      const a = project(v3(-5, 4.6, 0.2), S.cam), b = project(v3(5, 4.6, 0.2), S.cam);
      dimLine(a, b, '43,3 м', t, tCup + 0.5);
      title('самый большой', 120, 220, t, tWorld, { size: 84, align: 'left', out: tOc - 0.3 });
      title('купол без арматуры', 120, 320, t, tWorld + 0.4, { size: 84, align: 'left', color: PURPLE, out: tOc - 0.3 });
    }],
    [tOc, (lt, k) => {
      const S = PANI; S.cam.fov = 62; S.cam.updateProjectionMatrix();
      S.cam.position.set(1.8 - lt * 0.12, 1.3, 3.0); S.cam.lookAt(0, 9.2, -0.2); S.cam.updateMatrixWorld();
      render(S.scene, S.cam, { time: t, focus: 8, aperture: 0.0002 });
      pill('окулус · ≈ 9 м неба', 125, 230, t, tOc + 0.3, { dot: '#ffdc7a', align: 'left', size: 44 });
      pill('140 кессонов облегчают купол', 125, 330, t, Math.min(cue(id, 'кессонов', 0, 99), tOc + 30), { dot: '#86dcbc', align: 'left', size: 40 });
    }],
    [tLight, (lt, k) => {
      const S = DOME; S.lab.forEach((l, i) => popScale(l, t, tLight + 0.6 + i * 0.45));
      orbit(S.cam, v3(2.5, 6.5, 0), lerp(15, 13, k), lerp(0.25, 0.1, k), 0.1);
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(2.5, 7, 0), 0.0006) });
      title('легче к вершине', 120, 220, t, tLight + 0.2, { size: 90, align: 'left', out: tEnd - 0.3 });
    }],
    [tCof, (lt, k) => {
      const S = PANI; S.cam.fov = 70; S.cam.updateProjectionMatrix();
      S.cam.position.set(-1.2 + lt * 0.08, 1.5, 1.5); S.cam.lookAt(2.5, 7.4, -1.5); S.cam.updateMatrixWorld();
      render(S.scene, S.cam, { time: t, focus: 6, aperture: 0.0003 });
      title('140 кессонов', 120, 230, t, tCof + 0.6, { size: 110, align: 'left' }); pill('5 рядов × 28', 125, 340, t, tCof + 1.6, { dot: '#86dcbc', align: 'left' });
    }],
    [tEnd, (lt, k) => {
      const S = PAN; orbit(S.cam, v3(0, 5, 0), lerp(20, 30, easeIO2(k)), lerp(0.35, 0.7, k), lerp(0.08, 0.3, k));
      render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 5, 0), 0.0004) });
      counter(Math.round(lerp(0, 1898, easeOut(seg(t, tEnd, tEnd + 2.2)))), 120, 300, { size: 200, align: 'left' });
      title('лет — и стоит', 130, 400, t, tEnd + 0.6, { size: 70, align: 'left', color: PURPLE });
    }],
  ], end);
}

// ───────── s04. Гавани и Плиний ─────────
export const SEA = (() => {
  const S = newScene({ bg: 0xcfe6f5, floor: false, key: [6, 12, 4], shadowSize: 18 });
  const sea = waves(80, 50, 90, gloss(0x7fc0db, { roughness: 0.15 })); S.scene.add(sea);
  const pr = pier(4); pr.position.set(-1, 0.2, 0); S.scene.add(pr);
  const pr2 = pier(3); pr2.position.set(8, 0.2, -9); pr2.rotation.y = 0.6; S.scene.add(pr2);
  const sh = romanShip(); sh.position.set(5, 0, 5); sh.rotation.y = -0.4; S.scene.add(sh);
  const lh = new THREE.Group(); const t1 = rbox(1.6, 3, 1.6, concrete({ seed: 71 }), 0.1); t1.position.y = 1.5; lh.add(t1); const t2 = rbox(1.1, 1.6, 1.1, concrete({ seed: 72 }), 0.1); t2.position.y = 3.8; lh.add(t2); const fire = sphere(0.35, gloss(0xffb04a, { emissive: 0xff8a20, emissiveIntensity: 1.2 })); fire.position.y = 4.9; lh.add(fire); lh.position.set(-9, 0, -7); S.scene.add(shadowAll(lh));
  const spray = drops(40, 0xffffff, 0.09); S.scene.add(spray);
  const clouds = [[-8, 9, -16, 2.2], [9, 10, -20, 2.6]].map(([x, y, z, s]) => { const c = cloud(); c.position.set(x, y, z); c.scale.setScalar(s); S.scene.add(c); return c; });
  return { ...S, sea, pr, sh, spray };
})();
export function s04(t) {
  const id = 's04', S = SEA;
  const tP = cue(id, 'плиний', 0, 9), tPr = cue(id, 'звучит', 0, 20), tG = cue(id, 'геологи', 0, 22), end = 34;
  const amp = 1.0 + 0.3 * Math.sin(t * 0.4);
  S.sea.userData.update(t, amp);
  const hh = S.sea.userData.h;
  S.sh.position.y = hh(5, 5, t, amp) + 0.1; S.sh.rotation.z = (hh(6, 5, t, amp) - hh(4, 5, t, amp)) * 0.3;
  S.spray.userData.ps.forEach((p, i) => { const ph = (t * 0.7 + hash(i)) % 1; const x = -6 + hash(i + 1) * 9; p.position.set(x, 0.8 + Math.sin(ph * Math.PI) * 2.2, 1.4 + ph * 0.8); p.visible = ph > 0.05 && ph < 0.9; p.scale.setScalar(1 - ph * 0.6); });
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(-1, 1, 0), lerp(22, 15, easeIO2(k)), lerp(0.75, 0.4, k), lerp(0.25, 0.12, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1, 1, 0), 0.0005) });
      title('2000 лет в море', 120, 230, t, 1.2, { size: 110, align: 'left', out: tP - 0.3 }); pill('римские причалы и волнорезы', 125, 340, t, 2.2, { dot: '#8fd0e6', align: 'left', out: tP - 0.3 }); }],
    [tP, (lt, k) => { orbit(S.cam, v3(-2, 1.2, 1), lerp(9, 7.5, k), lerp(-0.3, -0.05, k), 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-2, 1, 1.2), 0.0012) });
      quote('становится единой каменной массой, неприступной для волн, и с каждым днём всё прочнее', 'Плиний Старший, I век', 110, 150, t, tP + 0.6, tPr, { w: 880, size: 46 }); }],
    [tPr, (lt, k) => { orbit(S.cam, v3(-1, 0.6, 0), lerp(14, 18, k), lerp(0.1, 0.5, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1, 1, 0), 0.0005) });
      stamp('ПРЕУВЕЛИЧЕНИЕ?', 520, 300, t, tPr + 0.2, { out: tG + 0.4 }); stamp('ПРАВДА', 520, 300, t, tG + 0.9, { color: '#3aa37c', rot: 0.08 }); }],
  ], end);
}

// ───────── s04b. Кесария: технология, а не чудо ─────────
export const CAES = (() => {
  const S = newScene({ bg: 0xd6eaf4, floor: false, key: [6, 12, 4], shadowSize: 18 });
  const sea = waves(80, 50, 90, gloss(0x79bcd8, { roughness: 0.15 })); S.scene.add(sea);
  const brk = new THREE.Group(); S.scene.add(brk);
  for (let i = 0; i < 6; i++) { const b = rbox(2.6, 1.4, 2.0, concrete({ seed: 300 + i, clasts: 6 }), 0.12); b.position.set(-7 + i * 2.7, 0.1, -2 + Math.sin(i) * 0.3); brk.add(b); }
  const big = rbox(3.2, 1.0, 2.4, concrete({ seed: 310, clasts: 10 }), 0.1); big.position.set(4, 0.2, 1.5); S.scene.add(shadowAll(big));
  const form = new THREE.Group(); form.position.set(-1, 0, 3); S.scene.add(form);
  for (const [x, z, w, d] of [[0, -1.1, 3.4, 0.16], [0, 1.1, 3.4, 0.16], [-1.7, 0, 0.16, 2.4], [1.7, 0, 0.16, 2.4]]) { const p = rbox(w, 1.6, d, wood(), 0.03); p.position.set(x, 0, z); form.add(p); }
  for (let i = 0; i < 6; i++) { const post = cyl(0.08, 2.6, wood(), 10); post.position.set(-1.6 + (i % 3) * 1.6, 0.3, i < 3 ? -1.25 : 1.25); form.add(post); }
  const fill = rbox(3.2, 1.4, 2.1, concrete({ seed: 320 }), 0.04); form.add(fill);
  const ship = romanShip(); ship.position.set(-6, 0, 6); ship.rotation.y = 0.3; S.scene.add(ship);
  const sacks = []; for (let i = 0; i < 6; i++) { const sk = sphere(0.28, matte(0xc9b79a), 16); sk.scale.set(1, 0.7, 0.8); sk.position.set(-1 + (i % 3) * 0.7, 1.0 + Math.floor(i / 3) * 0.3, (i % 2) * 0.3 - 0.15); ship.add(sk); sacks.push(sk); }
  shadowAll(ship);
  const clouds = [[-8, 9, -16, 2.2], [9, 10, -20, 2.6]].map(([x, y, z, s]) => { const c = cloud(); c.position.set(x, y, z); c.scale.setScalar(s); S.scene.add(c); return c; });
  return { ...S, sea, big, form, fill, ship };
})();
export function s04b(t) {
  const id = 's04b', S = CAES;
  const tH = cue(id, 'между', 0, 3), tB = cue(id, 'под', 0, 10), tA = cue(id, 'пепел', 0, 17), tF = cue(id, 'бетон', 1, 24), tM = cue(id, 'такие', 0, 31), end = 44;
  S.sea.userData.update(t, 0.9); const hh = S.sea.userData.h;
  S.ship.position.x = -9 + t * 0.25; S.ship.position.y = hh(S.ship.position.x, 6, t, 0.9) + 0.1;
  const sink = easeInOut(seg(t, tF + 1.5, tF + 5)); S.form.position.y = lerp(0.6, -1.6, sink); S.fill.scale.y = Math.max(0.02, smooth(seg(t, tF + 0.5, tF + 4))); S.fill.position.y = -0.7 + 0.7 * S.fill.scale.y;
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 0.5, 0), lerp(20, 16, k), lerp(0.6, 0.35, k), 0.22); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.5, 0), 0.0005) });
      title('не чудо —', 120, 230, t, 0.3, { size: 100, align: 'left', out: tB - 0.3 }); title('технология', 120, 340, t, 0.9, { size: 110, align: 'left', color: PURPLE, out: tB - 0.3 }); pill('Кесария · царь Ирод · 23–10 гг. до н. э.', 125, 460, t, tH + 0.4, { dot: '#e9b97f', align: 'left', size: 38, out: tB - 0.3 }); }],
    [tB, (lt, k) => { orbit(S.cam, v3(4, 0.3, 1.5), lerp(9, 7.5, k), lerp(0.5, 0.3, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(4, 0.3, 1.5), 0.0012) });
      const a = project(v3(2.4, 0.8, 2.8), S.cam), b = project(v3(5.6, 0.8, 2.8), S.cam); dimLine(a, b, '≈ 15 × 11,5 м', t, tB + 1.2, { size: 40 }); }],
    [tA, (lt, k) => { orbit(S.cam, v3(S.ship.position.x, 1, 6), lerp(9, 7.5, k), lerp(-0.4, -0.1, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(S.ship.position.x, 1, 6), 0.0012) });
      pill('пепел и туф из Неаполитанского залива', 125, 230, t, tA + 0.3, { dot: '#8f8783', align: 'left', size: 40 }); pill('≈ 2000 км морем', 125, 330, t, tA + 2.2, { dot: '#8fd0e6', align: 'left', size: 40 }); }],
    [tF, (lt, k) => { orbit(S.cam, v3(-1, 0, 3), lerp(9, 7, k), lerp(0.3, 0.0, k), 0.3); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1, 0, 3), 0.0012) });
      pill('опалубку топили прямо в море', 125, 230, t, tF + 0.6, { dot: '#c99766', align: 'left' }); pill('схватывался в солёной воде', 125, 330, t, tF + 3.4, { dot: '#86dcbc', align: 'left' }); }],
    [tM, (lt, k) => { orbit(S.cam, v3(0, 0.5, 0), lerp(18, 24, k), lerp(-0.4, -0.7, k), lerp(0.2, 0.32, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.5, 0), 0.0005) });
      title('Италия · Египет · Крит', 120, 230, t, tM + 1.6, { size: 80, align: 'left' }); }],
  ], end);
}

// ───────── s05. Современный бетон: арматура, ржавчина, выбросы ─────────
export function s05(t) {
  const id = 's05', S = BEAM;
  const tW = cue(id, 'слабость', 0, 9), tR = cue(id, 'ржавеет', 0, 13), tD = cue(id, 'десятилетия', 0, 18), tPc = cue(id, 'сам', 0, 20), tCl = cue(id, 'около', 0, 32), tCO = cue(id, 'итоге', 0, 40), tQ = cue(id, 'вопрос', 0, 47), end = 60;
  S.sm.userData.update(t, 1);
  beamAt(S, t, easeOut(seg(t, tW, tW + 3)), smooth(seg(t, tR, tR + 3)), easeIn(seg(t, tR + 2.5, tR + 4.5)), t > tW ? 1 : 0);
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 0.5, 0), lerp(12, 9.5, k), lerp(-0.5, -0.2, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.5, 1)) });
      title('наш бетон', 120, 220, t, 0.3, { size: 110, align: 'left', out: tW - 0.3 }); pill('прочнее на сжатие', 125, 330, t, 2.0, { dot: '#86dcbc', align: 'left', out: tW - 0.3 }); pill('со стальной арматурой', 125, 430, t, 3.6, { dot: '#86dcbc', align: 'left', out: tW - 0.3 }); }],
    [tW, (lt, k) => { orbit(S.cam, v3(0.2, 0, 1), lerp(6, 4.8, k), lerp(0.25, 0.08, k), 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0.2, 0, 1.1), 0.0016) });
      pill('вода + соль → трещина', 125, 230, t, tW + 0.4, { dot: '#8fd0e6', align: 'left' }); pill('сталь ржавеет и разбухает', 125, 330, t, tR, { dot: RED, align: 'left' }); pill('бетон лопается изнутри', 125, 430, t, tR + 2.6, { dot: RED, align: 'left' }); }],
    [tPc, (lt, k) => { orbit(S.cam, v3(13, 2.2, -6), lerp(11, 9, k), lerp(-0.6, -0.3, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(13, 2, -6), 0.0008) });
      title('портландцемент', 120, 230, t, tPc + 0.3, { size: 100, align: 'left' }); pill('1824 · Джозеф Аспдин, Лидс', 125, 340, t, tPc + 1.6, { dot: '#e9b97f', align: 'left' }); pill('печь ≈ 1450 °C → клинкер', 125, 440, t, tPc + 5.0, { dot: RED, align: 'left' }); }],
    [tCl, (lt, k) => { orbit(S.cam, v3(12.7, 4.5, -6.4), lerp(9, 7.5, k), lerp(0.4, 0.2, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(12.7, 5, -6.4), 0.0008) });
      counter(Math.round(lerp(0, 70, easeOut(seg(t, tCl + 0.5, tCl + 2)))), 120, 330, { size: 220, suffix: '%', align: 'left', color: RED }); title('CO₂ — из самого известняка', 130, 430, t, tCl + 1.2, { size: 60, align: 'left' }); pill('30% — топливо', 135, 530, t, tCl + 3.0, { dot: '#9a98aa', align: 'left' }); }],
    [tCO, (lt, k) => { orbit(S.cam, v3(9, 2.5, -4), lerp(20, 16, k), lerp(0.2, 0.45, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(13, 2, -6), 0.0005) });
      counter(Math.round(lerp(0, 8, easeOut(seg(t, tCO + 0.8, tCO + 2.4)))), 120, 330, { size: 240, suffix: '%', align: 'left', color: RED });
      title('мировых выбросов', 130, 440, t, tCO + 1.2, { size: 64, align: 'left' }); pill('производство цемента', 135, 540, t, tCO + 1.8, { dot: '#9a98aa', align: 'left', size: 38 }); }],
    [tQ, (lt, k) => { const C2 = CUBE; C2.cube.rotation.set(0.3, t * 0.4, 0); orbit(C2.cam, v3(0, 0, 0), lerp(9, 7, k), 0.4, 0.25); render(C2.scene, C2.cam, { time: t, ...dof(C2.cam, v3(0, 0, 0), 0.001) });
      title('как римляне', 120, 230, t, tQ + 0.2, { size: 100, align: 'left' }); title('сделали это?', 120, 345, t, tQ + 0.7, { size: 100, align: 'left', color: PURPLE }); }],
  ], end);
}

// ───────── s06. Рецепт: известь + вулканический пепел ─────────
const RECIPE = (() => {
  const S = newScene({ bg: 0xf3e6d8, floorY: 0, key: [6, 11, 8], shadowSize: 14 });
  const k = kiln(); k.position.set(-3.5, 0, 0); S.scene.add(k);
  const stones = []; for (let i = 0; i < 7; i++) { const s = rbox(0.5 + hash(i) * 0.3, 0.4, 0.5, stone({ base: '#e7ddc9', seed: 80 + i }), 0.1); s.position.set(-6.4 + hash(i + 3) * 1.2, 0.2 + (i % 3) * 0.42, 1.2 + hash(i + 5) * 0.8); s.rotation.y = hash(i) * 2; S.scene.add(s); stones.push(s); }
  const lime = pile('#f8f6f0', 1.1, 0.8, 3); lime.position.set(0.3, 0, 1.8); S.scene.add(lime);
  const ash = pile('#8f8783', 1.1, 0.85, 5); ash.position.set(2.9, 0, 1.6); S.scene.add(ash);
  const v = volcano(); v.scale.setScalar(0.9); v.position.set(7, 0, -9); S.scene.add(v);
  const plume = smoke(14, matte(0x8d8790, { transparent: true, opacity: 0.85 })); plume.position.set(7, 3.6, -9); S.scene.add(plume);
  const form = new THREE.Group(); form.position.set(5.6, 0, 2.2); S.scene.add(form);
  for (const [x, z, w, d] of [[0, -0.75, 2.4, 0.12], [0, 0.75, 2.4, 0.12], [-1.2, 0, 0.12, 1.6], [1.2, 0, 0.12, 1.6]]) { const p = rbox(w, 1.2, d, wood(), 0.03); p.position.set(x, 0.6, z); form.add(p); }
  const layers = []; for (let i = 0; i < 4; i++) { const l = rbox(2.25, 0.26, 1.38, i % 2 ? concrete({ seed: 90 + i, clasts: 8 }) : stone({ base: '#b9a48e', seed: 95 + i, n: 1600 }), 0.04); l.position.set(0, 0.14 + i * 0.27, 0); form.add(l); layers.push(l); }
  const labels = [textSprite('негашёная известь', { size: 52 }), textSprite('вулканический пепел', { size: 52 }), textSprite('Поццуоли', { size: 52, bg: '#ffe7a3' })];
  labels[0].position.set(0.3, 1.8, 1.8); labels[1].position.set(2.9, 1.8, 1.6); labels[2].position.set(7, 5.6, -9); labels.forEach((l) => S.scene.add(l));
  return { ...S, k, lime, ash, plume, form, layers, labels };
})();
export function s06(t) {
  const id = 's06', S = RECIPE;
  const tK = cue(id, 'известняк', 0, 4), tL = cue(id, 'негашёная', 0, 7), tA = cue(id, 'вторая', 0, 10.5), tPz = cue(id, 'путеоланским', 0, 17), tMix = cue(id, 'смесь', 0, 19), end = 32;
  S.plume.userData.update(t, 0.8);
  S.k.userData.glow.intensity = 5 + 2 * Math.sin(t * 7) + 1.5 * noise1(t * 3);
  popScale(S.lime, t, tL, 1.0, new THREE.Vector3(1, 1, 1)); popScale(S.ash, t, tA + 0.5, 1.0, new THREE.Vector3(1, 1, 1));
  popScale(S.labels[0], t, tL + 0.4); popScale(S.labels[1], t, tA + 1.0); popScale(S.labels[2], t, tA + 2.2);
  S.layers.forEach((l, i) => { const k = easeOut(seg(t, tMix + 0.6 + i * 0.6, tMix + 1.2 + i * 0.6)); l.visible = k > 0.01; l.scale.set(1, Math.max(0.01, k), 1); l.position.y = 0.14 + i * 0.27 + (1 - k) * 1.5; });
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(-3.2, 1.2, 0.5), lerp(11, 8.5, k), lerp(0.55, 0.3, k), 0.16); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-3.5, 1, 1), 0.0009) });
      chapter(3, 'Рецепт', t, 0.2, 5); }],
    [tL, (lt, k) => { orbit(S.cam, v3(0.8, 0.6, 1.6), lerp(8, 6.5, k), lerp(-0.1, 0.12, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0.3, 0.5, 1.8), 0.0012) });
      pill('известняк + огонь → негашёная известь', 125, 230, t, tL + 0.2, { dot: RED, align: 'left' }); }],
    [tA, (lt, k) => { orbit(S.cam, v3(4, 2.5, -3), lerp(19, 16, k), lerp(0.15, -0.1, k), 0.13); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(5, 2, -5), 0.0005) });
      pill('Неаполитанский залив', 125, 230, t, tA + 1.6, { dot: '#ffdc7a', align: 'left' }); }],
    [tMix, (lt, k) => { orbit(S.cam, v3(5.6, 0.7, 2.2), lerp(7.5, 6, k), lerp(0.4, 0.15, k), 0.35); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(5.6, 0.6, 2.2), 0.0012) });
      title('известь + пепел', 120, 230, t, tMix + 0.1, { size: 90, align: 'left' }); title('+ вода + камни', 120, 330, t, tMix + 0.7, { size: 90, align: 'left', color: PURPLE }); pill('слоями в опалубку', 125, 440, t, tMix + 2.0, { dot: '#86dcbc', align: 'left' }); }],
  ], end);
}

// ───────── s07. Витрувий и «правильный» рецепт ─────────
const VIT = (() => {
  const S = newScene({ bg: 0xeee5f4, floorY: -1.3, key: [4, 10, 6] });
  const table = rbox(9, 0.5, 5, wood(), 0.1); table.position.y = -1.05; S.scene.add(table);
  const bk = book(10); bk.position.set(-1.8, -0.7, 0.2); bk.rotation.y = 0.15; S.scene.add(bk);
  const bowl = new THREE.Mesh(new THREE.SphereGeometry(0.9, 36, 18, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), matte(0xc98f6a, { side: THREE.DoubleSide })); bowl.position.set(2.2, -0.0, 0.4); S.scene.add(shadowAll(bowl));
  const paste = new THREE.Mesh(new THREE.CircleGeometry(0.82, 36), matte(0xf4f2ec)); paste.rotation.x = -Math.PI / 2; paste.position.set(2.2, -0.35, 0.4); S.scene.add(paste);
  const water = drops(20, 0x8fd0e6, 0.07); S.scene.add(water);
  const ashF = drops(24, 0x8f8783, 0.06); S.scene.add(ashF);
  const steam = smoke(10, matte(0xffffff, { transparent: true, opacity: 0.6 })); steam.position.set(2.2, -0.2, 0.4); steam.scale.setScalar(0.35); S.scene.add(steam);
  const candle = cyl(0.12, 0.6, matte(0xf6ead2), 16); candle.position.set(-4.4, -0.5, -1); S.scene.add(candle);
  const fl = sphere(0.08, gloss(0xffc061, { emissive: 0xffa020, emissiveIntensity: 1.5 })); fl.position.set(-4.4, -0.1, -1); fl.scale.y = 1.6; S.scene.add(fl);
  const pl = new THREE.PointLight(0xffb060, 3, 6); pl.position.set(-4.4, 0.3, -1); S.scene.add(pl);
  const ink = cyl(0.25, 0.4, gloss(0x3d3a5c), 20); ink.position.set(-4.2, -0.6, 1.0); S.scene.add(ink);
  return { ...S, bk, paste, water, ashF, steam };
})();
export function s07(t) {
  const id = 's07', S = VIT;
  const tV = cue(id, 'витрувия', 0, 4), tB = cue(id, 'сначала', 0, 10), tAsh = cue(id, 'пепел', 0, 14), tD = cue(id, 'аккуратно', 0, 16), tX = cue(id, 'деталь', 0, 19), end = 28;
  S.water.userData.ps.forEach((p, i) => { const ph = (t * 1.2 + hash(i)) % 1; p.position.set(2.2 + (hash(i + 1) - 0.5) * 0.4, lerp(1.8, -0.3, ph), 0.4 + (hash(i + 2) - 0.5) * 0.4); p.visible = t > tB && t < tB + 3.2 && ph < 0.95; });
  S.ashF.userData.ps.forEach((p, i) => { const ph = (t * 1.0 + hash(i + 9)) % 1; p.position.set(2.2 + (hash(i + 3) - 0.5) * 0.6, lerp(1.8, -0.3, ph), 0.4 + (hash(i + 4) - 0.5) * 0.5); p.visible = t > tAsh && t < tAsh + 3 && ph < 0.95; });
  S.steam.userData.update(t, 1); S.steam.visible = t > tB + 0.8 && t < tAsh + 2;
  S.paste.material.color.set(new THREE.Color(0xf4f2ec).lerp(new THREE.Color(0xb0a69e), smooth(seg(t, tAsh, tAsh + 2.5))));
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(-1.6, -0.5, 0.2), lerp(7, 5.5, k), lerp(0.2, 0.45, k), 0.65); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1.8, -0.6, 0.2), 0.0014) });
      title('Витрувий', 120, 230, t, tV, { size: 120, align: 'left' }); pill('римский архитектор · I век до н. э.', 125, 340, t, tV + 0.8, { dot: '#e9b97f', align: 'left', size: 38 }); pill('«Десять книг об архитектуре»', 125, 440, t, tV + 1.8, { dot: '#e9b97f', align: 'left', size: 38 }); }],
    [tB, (lt, k) => { orbit(S.cam, v3(2.2, -0.1, 0.4), lerp(5.5, 4.4, k), lerp(-0.2, 0.05, k), 0.5); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(2.2, -0.3, 0.4), 0.0016) });
      pill('1. известь + вода → паста', 125, 230, t, tB + 0.3, { dot: '#8fd0e6', align: 'left' }); pill('2. потом пепел', 125, 330, t, tAsh, { dot: '#8f8783', align: 'left' }); stamp('ТАК ДУМАЛИ 2000 ЛЕТ', 560, 520, t, tD + 0.3, { color: PURPLE, size: 56, out: tX }); }],
    [tX, (lt, k) => { orbit(S.cam, v3(0.2, -0.4, 0.3), lerp(9, 7.5, k), lerp(0.3, 0.1, k), 0.35); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0.2, -0.4, 0.3), 0.001) });
      title('но одна деталь', 120, 230, t, tX - 0.2, { size: 96, align: 'left' }); title('не вписывалась', 120, 340, t, tX + 0.4, { size: 96, align: 'left', color: RED }); }],
  ], end);
}
