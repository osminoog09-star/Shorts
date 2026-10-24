// Сцены 07–12
import { render, clear2d, ctx, title, pill, counter, iris, project, W, H,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { THREE, C, CSS, matte, gloss, metal, gear, shadowAll, v3, orbit, newScene, rbox, sphere, cyl, puck, train, axle, textSprite, popScale,
  lump, mechanismBox, laptop, scanner, questionMark } from './kit.js';

// ───────── 07. Как он работал ─────────
const S7 = (() => {
  const S = newScene({ bg: C.cream, floorY: -2.6, key: [5, 10, 7] });
  const ped = rbox(5, 0.5, 3.4, matte(C.sand), 0.22); ped.position.y = -2.35; S.scene.add(ped);
  const M = mechanismBox(); M.g.position.y = 0.0; S.scene.add(M.g);
  // мини-затмение для пояснения
  const ecl = new THREE.Group(); ecl.position.set(-3.6, 2.3, 0); S.scene.add(ecl);
  const sun = sphere(0.55, gloss(C.butter, { emissive: 0xffb400, emissiveIntensity: 0.4 })); ecl.add(sun);
  const mn = sphere(0.5, gloss(C.deep)); mn.position.z = 0.8; ecl.add(mn);
  const wreath = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.12, 16, 48, Math.PI * 1.6), gloss(C.mint)); wreath.rotation.z = -Math.PI * 0.3; wreath.position.set(-3.6, 2.3, 0); wreath.castShadow = true; S.scene.add(wreath);
  return { ...S, M, ecl, mn, wreath };
})();
export function s07(t) {
  const S = S7, M = S.M;
  const crank = seg(t, 4.8, 99) * (t - 4.8);
  const a = Math.max(0, t - 4.8) * 1.6;
  M.crank.rotation.x = -a;
  M.sunP.rotation.z = -a * 0.08;
  M.moonP.rotation.z = -a * 0.08 * 13.37 / 4;
  M.moonBall.rotation.y = a * 0.25;
  M.bp1.rotation.z = -a * 0.05; M.bp2.rotation.z = -a * 0.04;
  // камера: спереди → сбоку (ручка) → сзади (спирали)
  const back = easeIO2(seg(t, 13.6, 16.4));
  const side = easeIO2(seg(t, 1.8, 3.4)) * (1 - easeIO2(seg(t, 6.6, 8.2)));
  const az = lerp(-0.35, 0.25, seg(t, 0, 13)) + side * 0.95 + back * (Math.PI - 0.6);
  const tg = v3(lerp(0.4, -0.6, back), 0.2, 0);
  orbit(S.cam, tg, lerp(11.5, 10.5, side), az, 0.18);
  const ec = easeOut(seg(t, 26.6, 27.6)) * (1 - easeIn(seg(t, 31.6, 32.4)));
  S.ecl.visible = ec > 0.01; S.ecl.scale.setScalar(ec); S.mn.position.x = lerp(1.4, 0, smooth(seg(t, 27.0, 29.0)));
  const wr = easeOut(seg(t, 32.4, 33.4)); S.wreath.visible = wr > 0.01; S.wreath.scale.setScalar(spring(seg(t, 32.4, 33.6) * 1.3, 7, 5)); S.wreath.rotation.y = t * 0.6;
  // эклипс/венок ставим со стороны камеры, слева в кадре
  const sideV = v3(Math.cos(az), 0, -Math.sin(az)).multiplyScalar(3.6);
  S.ecl.position.set(sideV.x, 2.3, sideV.z); S.wreath.position.set(sideV.x, 2.3, sideV.z);
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.0009 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('ручка сбоку', 140, 220, t, 2.6, { size: 100, align: 'left', out: 7.4 });
  title('крутишь — время идёт', 140, 340, t, 4.8, { size: 76, align: 'left', out: 7.4, color: '#7a63e6' });
  pill('Солнце', 140, 150, t, 10.3, { dot: CSS.butter, align: 'left', out: 13.6, size: 44 });
  pill('Луна', 140, 245, t, 10.9, { dot: '#c9c4d8', align: 'left', out: 13.6, size: 44 });
  pill('фаза Луны', 140, 340, t, 12.3, { dot: CSS.deep, align: 'left', out: 13.6, size: 44 });
  title('сзади — две спирали', 140, 220, t, 15.0, { size: 90, align: 'left', out: 20.8 });
  pill('19 лет: Луна сходится с Солнцем', 140, 330, t, 16.9, { dot: CSS.butter, align: 'left', out: 21.4 });
  title('223 месяца', 140, 220, t, 22.7, { size: 120, align: 'left', out: 29.0 });
  pill('цикл Сарос', 140, 330, t, 24.8, { dot: CSS.lav, align: 'left', out: 29.0 });
  title('предсказывал затмения', 140, 1000, t, 26.6, { size: 76, align: 'left', out: 32.0 });
  title('и даже игры', 140, 220, t, 31.0, { size: 100, align: 'left', out: 37.0 });
  pill('включая Олимпийские', 140, 330, t, 34.6, { dot: CSS.mint, align: 'left', out: 37.0 });
}

// ───────── 08. Луна: штифт в прорези ─────────
const S8 = (() => {
  const S = newScene({ bg: 0xe9e3f5, floorY: -1.2, key: [3, 11, 6] });
  const plate = rbox(9, 0.3, 7, matte(C.cream), 0.15); plate.position.y = -1.05; S.scene.add(plate);
  const e = 0.35; // смещение осей
  const g1 = gear(36, 1.8, metal(C.bronze), { thick: 0.3, spokes: 4 }); g1.rotation.x = -Math.PI / 2; g1.position.set(0, -0.6, 0); S.scene.add(g1);
  const pin = cyl(0.11, 0.45, gloss(C.coral), 20); pin.position.set(1.15, -0.25, 0); S.scene.add(pin);
  const g2 = new THREE.Group(); g2.position.set(e, -0.15, 0); S.scene.add(g2);
  const g2gear = gear(36, 1.8, gloss(C.lav, { transparent: true, opacity: 0.92 }), { thick: 0.25, spokes: 4 }); g2gear.rotation.x = -Math.PI / 2; g2.add(g2gear);
  const slot = rbox(1.0, 0.1, 0.34, matte(C.deep), 0.05); slot.position.set(1.0, 0.12, 0); g2.add(slot);
  const ptr = rbox(3.6, 0.1, 0.16, gloss(C.white), 0.05); ptr.position.set(1.8, 0.35, 0); g2.add(ptr);
  const moon = sphere(0.32, gloss(C.butter)); moon.position.set(3.7, 0.45, 0); g2.add(moon);
  const ax1 = cyl(0.12, 0.9, gloss(C.white), 20); ax1.position.set(0, -0.4, 0); S.scene.add(ax1);
  // «призраки» положений Луны через равные промежутки времени
  const ghosts = []; for (let i = 0; i < 16; i++) { const s = sphere(0.12, gloss(C.butter, { transparent: true, opacity: 0.55 }), 16); S.scene.add(s); ghosts.push(s); }
  const orbitRing = new THREE.Mesh(new THREE.TorusGeometry(3.85, 0.025, 8, 128), matte(C.lav)); orbitRing.rotation.x = Math.PI / 2; orbitRing.position.set(e, 0.45, 0); S.scene.add(orbitRing);
  return { ...S, g1, pin, g2, e, ghosts, moon };
})();
function moonAngle(th1, e) { const px = Math.cos(th1) * 1.15, pz = Math.sin(th1) * 1.15; return Math.atan2(pz, px - e); }
export function s08(t) {
  const S = S8;
  const th = t * 0.9;
  S.g1.rotation.z = -th; // вид сверху
  S.pin.position.set(Math.cos(th) * 1.15, -0.25, Math.sin(th) * 1.15);
  const a2 = moonAngle(th, S.e);
  S.g2.rotation.y = -a2;
  const show = seg(t, 13.0, 14.0);
  S.ghosts.forEach((g, i) => { const thi = th - (i + 1) * 0.42; const ai = moonAngle(thi, S.e); g.position.set(S.e + Math.cos(ai) * 3.7, 0.45, Math.sin(ai) * 3.7); g.visible = show > 0; g.scale.setScalar(show * (1 - i / 18)); });
  const tg = v3(0.5, 0, 0);
  orbit(S.cam, tg, lerp(13, 11, easeIO2(seg(t, 0, 25))), lerp(0.4, -0.3, easeIO2(seg(t, 0, 25))), lerp(0.75, 0.6, seg(t, 0, 25)));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.0011 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e9e3f5');
  title('самое безумное — Луна', 140, 200, t, 0.8, { size: 90, align: 'left', out: 6.0 });
  // индикатор скорости
  const w = (moonAngle(th + 0.01, S.e) - moonAngle(th - 0.01, S.e)) / 0.02;
  const fast = w > 1.0;
  if (t > 3.6 && t < 17.5) pill(fast ? 'быстрее ▶▶' : 'медленнее ▶', 1780, 150, t, 3.6, { align: 'right', bg: fast ? '#ffe0d6' : '#e6e2ff', size: 44 });
  pill('две шестерни со смещением осей', 140, 150, t, 8.6, { align: 'left', out: 13.0 });
  pill('штифт в прорези', 140, 245, t, 10.8, { align: 'left', dot: CSS.coral, out: 13.0 });
  title('одна толкает другую', 140, 1000, t, 12.6, { size: 76, align: 'left', out: 17.4 });
  title('модель теории Гиппарха', 140, 200, t, 17.6, { size: 90, align: 'left', out: 25.6 });
  pill('из бронзы · 2000 лет назад', 140, 300, t, 21.2, { align: 'left', dot: CSS.gold, out: 25.6 });
}

// ───────── 09. Космос 2021 ─────────
const S9 = (() => {
  const S = newScene({ bg: 0xe7e6f6, floorY: -2.4, key: [4, 12, 7] });
  const base = rbox(7, 0.4, 7, matte(C.sand), 0.2); base.position.y = -2.2; S.scene.add(base);
  const plate = puck(3.4, 0.25, metal(C.bronze)); plate.position.y = -1.85; S.scene.add(plate);
  const cols = [C.butter, 0xdedbe8, C.sky, C.peach, C.coral, C.mint, C.lav];
  const names = ['Солнце', 'Луна', 'Меркурий', 'Венера', 'Марс', 'Юпитер', 'Сатурн'];
  const speeds = [1.0, 13.4, 4.2, 1.6, 0.53, 0.084, 0.034];
  const rings = []; const bodies = []; const labels = [];
  cols.forEach((c, i) => {
    const r = 0.55 + i * 0.42;
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r, 0.035, 10, 128), gloss(C.white)); ring.rotation.x = Math.PI / 2; ring.castShadow = true; S.scene.add(ring); rings.push(ring);
    const b = sphere(i === 0 ? 0.26 : 0.17, gloss(c, i === 0 ? { emissive: 0xffb400, emissiveIntensity: 0.3 } : {})); S.scene.add(b); bodies.push(b);
    const l = textSprite(names[i], { size: 44, scale: 0.8 }); S.scene.add(l); labels.push(l);
  });
  const n462 = textSprite('462', { size: 90, weight: 900, color: '#7a63e6', scale: 1.1 }); S.scene.add(n462);
  const n442 = textSprite('442', { size: 90, weight: 900, color: '#7a63e6', scale: 1.1 }); S.scene.add(n442);
  return { ...S, rings, bodies, labels, speeds, n462, n442 };
})();
export function s09(t) {
  const S = S9;
  const rise = (i) => easeOut(seg(t, 18.6 + i * 0.45, 19.6 + i * 0.45));
  S.rings.forEach((r, i) => { const k = rise(i); r.position.y = lerp(-1.7, -0.4 + i * 0.32, k); r.visible = k > 0 || t > 5; r.scale.setScalar(lerp(0.4, 1, k)); });
  S.bodies.forEach((b, i) => {
    const k = rise(i); const rad = (0.55 + i * 0.42) * lerp(0.4, 1, k); const a = t * 0.25 * Math.pow(S.speeds[i], 0.35) + i;
    b.position.set(Math.cos(a) * rad, S.rings[i].position.y + 0.02, Math.sin(a) * rad); b.visible = k > 0.02;
    const l = S.labels[i]; l.position.copy(b.position).add(v3(0, 0.42, 0)); popScale(l, t, 22.6 + i * 0.45); l.visible = l.visible && t < 29.6;
  });
  // числа летят к Венере и Сатурну
  const fly = easeIO2(seg(t, 20.2, 21.8));
  const v = S.bodies[3].visible ? S.bodies[3].position : v3(-1.8, 1.5, 0); const sa = S.bodies[6].visible ? S.bodies[6].position : v3(2.6, 2.0, 0);
  S.n462.position.lerpVectors(v3(-2.6, 2.6, 1.5), v3(v.x, v.y + 0.7, v.z), fly); popScale(S.n462, t, 14.8);
  S.n442.position.lerpVectors(v3(2.6, 2.6, 1.5), v3(sa.x, sa.y + 0.7, sa.z), fly); popScale(S.n442, t, 16.2);
  if (t > 23.4) { S.n462.visible = false; S.n442.visible = false; }
  const tg = v3(0, 0.2, 0);
  orbit(S.cam, tg, lerp(12.5, 10, easeIO2(seg(t, 0, 30))), t * 0.06 - 0.6, lerp(0.35, 0.62, easeIO2(seg(t, 20, 27))));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.001 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e7e6f6');
  title('большая часть утеряна', 140, 200, t, 0.8, { size: 90, align: 'left', out: 5.4 });
  pill('2021 · Университетский колледж Лондона', 140, 150, t, 6.0, { dot: CSS.gold, align: 'left', out: 14.2 });
  pill('команда Тони Фрита', 140, 245, t, 7.8, { align: 'left', out: 14.2 });
  title('сканы + надписи + математика', 140, 1000, t, 10.4, { size: 72, align: 'left', out: 14.4 });
  title('циклы Венеры и Сатурна', 140, 1000, t, 18.6, { size: 72, align: 'left', out: 22.0, color: '#7a63e6' });
  title('модель целого космоса', 140, 200, t, 22.2, { size: 100, align: 'left', out: 29.6 });
}

// ───────── 10. Глазго 2024 ─────────
const S10 = (() => {
  const S = newScene({ bg: 0xe4eef3, floorY: -3, key: [4, 12, 6] });
  const N = 60; const geo = new THREE.PlaneGeometry(16, 16, N, N); geo.rotateX(-Math.PI / 2);
  const grid = new THREE.Mesh(geo, gloss(C.sky, { roughness: 0.35 })); grid.receiveShadow = true; S.scene.add(grid);
  const wire = new THREE.LineSegments(new THREE.WireframeGeometry(geo), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 })); S.scene.add(wire);
  const base = geo.attributes.position.array.slice();
  const bh1 = sphere(0.45, gloss(C.deep)), bh2 = sphere(0.4, gloss(C.deep)); S.scene.add(bh1, bh2);
  // кольцо-календарь (дуга) с отверстиями
  const ring = new THREE.Group(); S.scene.add(ring);
  const arcShape = new THREE.Shape(); const R0 = 2.6, R1 = 3.2, A0 = -0.35, A1 = 0.75;
  arcShape.absarc(0, 0, R1, A0, A1, false); arcShape.absarc(0, 0, R0, A1, A0, true);
  const arc = new THREE.Mesh(new THREE.ExtrudeGeometry(arcShape, { depth: 0.18, bevelEnabled: true, bevelSize: 0.04, bevelThickness: 0.04, bevelSegments: 3, curveSegments: 64 }), metal(C.bronze)); arc.castShadow = true; ring.add(arc);
  const ghost = new THREE.Mesh(new THREE.TorusGeometry(2.9, 0.3, 8, 128), gloss(C.lav, { transparent: true, opacity: 0.35 })); ghost.scale.z = 0.4; ring.add(ghost);
  const holes = []; const NH = 354;
  for (let i = 0; i < NH; i++) { const a = (i / NH) * Math.PI * 2; const h = sphere(0.035, i < 0 ? gloss(C.deep) : matte(C.deep), 8); h.position.set(Math.cos(a) * 2.9, Math.sin(a) * 2.9, 0.24); ring.add(h); holes.push({ h, a }); }
  ring.rotation.x = -Math.PI / 2 + 0.25; ring.position.set(0, 0.4, 0);
  return { ...S, grid, wire, geo, base, bh1, bh2, ring, ghost, holes, A0, A1 };
})();
export function s10(t) {
  const S = S10;
  const swap = smooth(seg(t, 9.6, 11.0));
  const p = S.geo.attributes.position; const om = t * 2.2;
  const x1 = Math.cos(om) * 1.2, z1 = Math.sin(om) * 1.2;
  for (let i = 0; i < p.count; i++) {
    const x = S.base[i * 3], z = S.base[i * 3 + 2]; const r = Math.hypot(x, z);
    const well = -1.6 / (1 + r * r * 0.6);
    const wave = 0.22 * Math.sin(r * 2.4 - t * 4.4 + 2 * Math.atan2(z, x)) * Math.exp(-r * 0.12) * (r > 1 ? 1 : r);
    p.array[i * 3 + 1] = (well + wave) * (1 - swap) - 3 * swap;
  }
  p.needsUpdate = true; S.geo.computeVertexNormals();
  S.wire.geometry.dispose(); S.wire.geometry = new THREE.WireframeGeometry(S.geo);
  S.bh1.position.set(x1, -0.8 - 3 * swap, z1); S.bh2.position.set(-x1, -0.8 - 3 * swap, -z1);
  S.grid.visible = swap < 1; S.wire.visible = swap < 1; S.bh1.visible = S.bh2.visible = swap < 1;
  const rk = easeOut(seg(t, 10.0, 11.4)); S.ring.visible = rk > 0; S.ring.scale.setScalar(spring(seg(t, 10.0, 11.8) * 1.3, 7, 5));
  S.ghost.material.opacity = 0.35 * smooth(seg(t, 11.6, 12.6));
  const nShow = Math.floor(354 * easeIO2(seg(t, 12.6, 15.0)));
  S.holes.forEach((o, i) => { const onArc = o.a > S.A0 + 0.02 && o.a < S.A1 - 0.02; o.h.visible = rk > 0 && (onArc || i < nShow); o.h.material = onArc ? S.holes[0].h.material : o.h.material; });
  const tg = v3(0, 0, 0);
  orbit(S.cam, tg, lerp(13, 10.5, easeIO2(seg(t, 0, 20))), lerp(0.3, -0.25, easeIO2(seg(t, 0, 20))), lerp(0.55, 0.85, swap));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.0009 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e4eef3');
  pill('2024 · Университет Глазго', 140, 150, t, 0.9, { dot: CSS.gold, align: 'left', out: 9.4 });
  title('охотники за гравитационными волнами', 140, 1000, t, 4.6, { size: 66, align: 'left', out: 9.6 });
  title('посчитали отверстия кольца', 140, 1000, t, 10.0, { size: 72, align: 'left', out: 13.2 });
  const c = Math.floor(354 * easeIO2(seg(t, 12.6, 15.0)));
  counter(c > 0 ? c : '', 140, 330, { size: 240, align: 'left', color: '#7a63e6', alpha: clamp(seg(t, 12.6, 12.9)) });
  pill('отверстий', 140, 400, t, 13.0, { align: 'left' });
  title('почти ровно лунный год', 140, 1000, t, 16.2, { size: 72, align: 'left' });
}

// ───────── 11. Заклинило (2025) ─────────
const S11 = (() => {
  const S = newScene({ bg: 0xe9f2ec, floorY: -2.4, key: [5, 10, 7] });
  const ped = rbox(8, 0.5, 3.6, matte(C.sand), 0.22); ped.position.y = -2.15; S.scene.add(ped);
  const holo = (c) => gloss(c, { emissive: c, emissiveIntensity: 0.25, transparent: true, opacity: 0.92 });
  const tr = train([{ r: 1.6, mat: holo(C.mint), x: -0.6, y: 0.2 }, { r: 0.85, mat: holo(C.sky), parent: 0, ang: 0.2 }, { r: 0.6, mat: holo(C.lav), parent: 1, ang: 2.0 }, { r: 1.0, mat: holo(C.peach), parent: 0, ang: 3.6 }]);
  S.scene.add(tr.grp);
  const printer = new THREE.Group(); const pb = rbox(2.2, 1.0, 1.5, gloss(C.white), 0.25); printer.add(pb);
  const paper = rbox(1.2, 0.04, 1.0, matte(0xffffff), 0.02); paper.position.set(0, 0.55, 0.3); paper.rotation.x = -0.6; printer.add(paper);
  const led = sphere(0.07, new THREE.MeshBasicMaterial({ color: 0xff6b6b, toneMapped: false }), 12); led.position.set(0.85, 0.2, 0.76); printer.add(led);
  printer.position.set(3.6, -1.4, 0.6); shadowAll(printer); S.scene.add(printer);
  const lp = lump({ r: 0.9, seed: 9 }); lp.position.set(-3.8, -1.2, 0.5); S.scene.add(lp);
  return { ...S, tr, printer, lp, paper };
})();
export function s11(t) {
  const S = S11;
  const jamT = 9.2;
  let a = t < jamT ? t * 0.7 : jamT * 0.7 + 0.04 * Math.exp(-(t - jamT) * 4) * Math.sin((t - jamT) * 40);
  if (t > 14.0) a = jamT * 0.7 + (t - 14.0) * 0.5 * smooth(seg(t, 14.0, 15.0));
  S.tr.update(a);
  const shake = t > jamT && t < jamT + 0.6 ? (1 - seg(t, jamT, jamT + 0.6)) * 0.12 : 0;
  S.tr.grp.position.set(Math.sin(t * 60) * shake, Math.cos(t * 53) * shake, 0);
  popScale(S.printer, t, 12.5, 0.8, v3(1, 1, 1)); S.paper.rotation.z = Math.sin(t * 8) * 0.15 * (t > 12.5 && t < 14 ? 1 : 0);
  popScale(S.lp, t, 19.8, 0.8, v3(1, 1, 1));
  const tg = v3(0, 0, 0);
  const close = easeIO2(seg(t, 5.6, 7.0)) * (1 - easeIO2(seg(t, 8.4, 9.4)));
  orbit(S.cam, v3(lerp(0, 0.9, close), lerp(0, 0.9, close), 0), lerp(lerp(12, 11, seg(t, 0, 24)), 5, close), lerp(-0.3, 0.3, easeIO2(seg(t, 0, 24))), 0.22);
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(v3(0, 0.2, 0)), aperture: lerp(0.0009, 0.0022, close), flash: t > jamT && t < jamT + 0.15 ? 0.25 : 0 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e9f2ec');
  pill('2025 · исследователи из Аргентины', 140, 150, t, 0.9, { dot: CSS.gold, align: 'left', out: 8.6 });
  title('компьютерная модель', 140, 1000, t, 3.0, { size: 76, align: 'left', out: 5.8 });
  title('с треугольными зубцами', 140, 1000, t, 5.8, { size: 76, align: 'left', out: 8.8 });
  title('заклинило', 140, 260, t, 9.2, { size: 150, align: 'left', color: '#e8706a', out: 13.6 });
  pill('примерно через 4 месяца работы', 140, 360, t, 10.4, { align: 'left', out: 13.6 });
  pill('как принтер', 1780, 150, t, 12.6, { align: 'right', out: 14.0 });
  title('но, скорее всего —', 140, 230, t, 14.2, { size: 84, align: 'left' });
  title('погрешности измерений', 140, 340, t, 17.2, { size: 84, align: 'left', color: '#7a63e6' });
  pill('бронза 2000 лет пролежала в море', 140, 450, t, 20.0, { align: 'left', dot: CSS.patina });
}

// ───────── 12. Финал ─────────
const S12 = (() => {
  const S = newScene({ bg: C.cream, floorY: -2.6, key: [5, 11, 8], shadowSize: 18 });
  const peds = []; const qs = []; const names = ['ученики Гиппарха?', 'мастерская на Родосе?', 'наследники Архимеда?'];
  [-4.5, 0, 4.5].forEach((x, i) => {
    const p = puck(1.3, 1.4, matte([C.lav, C.sand, C.mint][i])); p.position.set(x, -1.9, 0); S.scene.add(p); peds.push(p);
    const q = questionMark(gloss([C.coral, C.gold, C.sky][i])); q.position.set(x, 0.0, 0); S.scene.add(q); qs.push(q);
  });
  const labels = names.map((n, i) => { const l = textSprite(n, { size: 46, scale: 0.9 }); l.position.set(-4.5 + i * 4.5, 2.1, 0); S.scene.add(l); return l; });
  const M = (() => { const m = new THREE.Group(); const box = rbox(1.6, 2.1, 0.65, matte(0xd8a77a), 0.12); m.add(box); const f = rbox(1.4, 1.9, 0.06, metal(C.bronze), 0.05); f.position.z = 0.33; m.add(f); const r = new THREE.Mesh(new THREE.TorusGeometry(0.56, 0.05, 12, 64), metal(C.gold)); r.position.z = 0.38; m.add(r); return shadowAll(m); })();
  M.position.set(0, -0.15, 0); S.scene.add(M);
  const lap = laptop(); lap.position.set(3.4, -1.2, 0.6); lap.rotation.y = -0.5; S.scene.add(lap);
  const sc = scanner(); sc.scale.setScalar(0.42); sc.position.set(-3.6, 0.05, -0.4); sc.rotation.y = 0.6; S.scene.add(sc);
  return { ...S, peds, qs, labels, M, lap, sc };
})();
export function s12(t) {
  const S = S12;
  const out1 = easeIO2(seg(t, 10.6, 12.0));
  S.qs.forEach((q, i) => { popScale(q, t, 0.8 + i * 0.25, 0.9, v3(1, 1, 1)); q.rotation.y = t * 0.6 + i; q.position.y = 0.2 + Math.sin(t * 1.4 + i) * 0.15 - out1 * 6; });
  S.labels.forEach((l, i) => { popScale(l, t, [3.9, 6.8, 9.0][i]); if (t > 10.6) l.visible = false; });
  S.peds.forEach((p, i) => { p.position.y = -1.9 - out1 * (i === 1 ? 0 : 4); });
  const mk = spring(seg(t, 11.8, 13.4) * 1.3, 7, 5); S.M.visible = mk > 0.01; S.M.scale.setScalar(mk); S.M.rotation.y = Math.sin(t * 0.5) * 0.4; S.M.position.y = 0.0;
  popScale(S.lap, t, 15.6, 0.9, v3(1, 1, 1)); popScale(S.sc, t, 16.6, 0.9, v3(0.42, 0.42, 0.42));
  const dim = smooth(seg(t, 26.0, 27.2));
  const tg = v3(0, lerp(0.4, 0.2, out1), 0);
  orbit(S.cam, tg, lerp(15, 12, easeIO2(seg(t, 0, 25))) + dim * 2, lerp(-0.3, 0.3, easeIO2(seg(t, 0, 31))), lerp(0.2, 0.28, seg(t, 0, 31)));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.001, fade: dim * 0.82 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('кто его построил?', 960, 190, t, 0.7, { size: 110, out: 10.4 });
  title('компьютер из бронзы', 960, 190, t, 12.6, { size: 100, out: 18.2 });
  title('а мы построили свои', 960, 190, t, 15.6, { size: 90, out: 18.2, color: '#7a63e6' });
  title('самый древний компьютер', 960, 170, t, 18.8, { size: 92, out: 25.8 });
  title('прочитали самые новые', 960, 285, t, 20.2, { size: 92, out: 25.8, color: '#7a63e6' });
  title('а что найдут от наших', 960, 920, t, 22.6, { size: 80, out: 25.8 });
  title('через 2000 лет?', 960, 1020, t, 24.2, { size: 80, out: 25.8, color: '#e8706a' });
  title('пиши в комментариях', 960, 500, t, 26.6, { size: 110 });
  pill('M1lash · инженерия древности', 960, 640, t, 27.6, { size: 44, dot: CSS.gold });
}
