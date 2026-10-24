// Сцены 01–06
import { render, clear2d, ctx, title, pill, counter, iris, project, W, H,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { THREE, C, CSS, matte, gloss, metal, gear, shadowAll, v3, orbit, newScene, rbox, sphere, cyl, puck, train, axle, textSprite, popScale,
  lump, amphora, coinStack, bust, boat, diver, waves, cloud, island, clockTower } from './kit.js';

const dof = (S, target, ap = 0.0009, mb = 0.01) => ({ focus: S.cam.position.distanceTo(target), aperture: ap, maxblur: mb });

// ───────── 01. Хук ─────────
const S1 = (() => {
  const S = newScene({ bg: C.cream, floorY: -3.2, key: [5, 10, 7] });
  const ped = rbox(9, 0.7, 4.4, matte(C.sand), 0.3); ped.position.y = -2.85; S.scene.add(ped);
  const back = rbox(8.4, 5.6, 0.35, matte(C.lav), 0.16); back.position.set(0.2, 0.1, -1.1); S.scene.add(back);
  const tr = train([
    { r: 2.1, mat: metal(C.bronze), x: -0.6, y: 0.1 },
    { r: 0.95, mat: gloss(C.mint), parent: 0, ang: 0.15 },
    { r: 0.62, mat: gloss(C.peach), parent: 1, ang: 1.9, z: 0.02 },
    { r: 1.25, mat: gloss(C.pink), parent: 0, ang: 3.75, z: -0.02 },
    { r: 0.55, mat: metal(C.gold), parent: 3, ang: 1.6 },
    { r: 0.72, mat: gloss(C.sky), parent: 1, ang: -1.4 },
  ]);
  tr.grp.position.z = -0.55; S.scene.add(tr.grp);
  tr.gs.forEach((g) => { const a = axle(0.7); a.position.set(g.x, g.y, 0.05); tr.grp.add(a); });
  const ptr = new THREE.Group(); ptr.position.set(-0.6, 0.1, 0.35); tr.grp.add(ptr);
  const bar = rbox(0.16, 1.9, 0.12, gloss(C.white), 0.06); bar.position.y = 0.95; ptr.add(bar);
  const moon = sphere(0.24, gloss(C.butter)); moon.position.y = 1.9; ptr.add(moon);
  const target = v3(-0.4, 0.1, -0.4);
  return { ...S, tr, ptr, target };
})();
export function s01(t) {
  const S = S1;
  const a = t * 0.42; S.tr.update(a); S.ptr.rotation.z = -a * 0.37;
  const az = lerp(0.55, -0.15, easeIO2(seg(t, 0, 16.5)));
  const el = lerp(0.34, 0.14, easeIO2(seg(t, 0, 16.5)));
  const r = lerp(16, 11.5, easeIO2(seg(t, 0, 15))) - 6 * easeIn(seg(t, 15.6, 17.7));
  // объект держим справа, текст — слева
  const tg = S.target.clone().add(v3(-2.6 * (1 - 0.4 * easeIO2(seg(t, 13, 16))), 0, 0));
  orbit(S.cam, tg, r, az, el);
  render(S.scene, S.cam, { time: t, ...dof(S, S.target) });
  clear2d();
  title('2000+ лет', 140, 260, t, 1.5, { size: 160, align: 'left', out: 8.6 });
  pill('без экрана', 140, 375, t, 4.3, { dot: CSS.coral, out: 8.6, align: 'left', size: 44 });
  pill('без электричества', 140, 475, t, 5.1, { dot: CSS.coral, out: 8.6, align: 'left', size: 44 });
  pill('без единого чипа', 140, 575, t, 6.8, { dot: CSS.coral, out: 8.6, align: 'left', size: 44 });
  title('предсказывал', 140, 290, t, 8.8, { size: 120, align: 'left', out: 13.4 });
  title('затмения', 140, 420, t, 9.4, { size: 120, align: 'left', color: '#e8706a', out: 13.4 });
  title('а разгадали его…', 140, 820, t, 13.5, { size: 90, align: 'left', out: 16.4 });
  title('другие компьютеры', 140, 930, t, 14.6, { size: 90, align: 'left', color: '#7a63e6', out: 16.4 });
}

// ───────── 02. 1900 год, шторм и ныряльщик ─────────
const S2 = (() => {
  const A = newScene({ bg: 0xcfe6f5, floor: false, key: [6, 12, 4], shadowSize: 18 });
  const sea = waves(70, 50, 80); A.scene.add(sea);
  const b = boat(); A.scene.add(b);
  const isl = island(); isl.position.set(-9, -0.4, -12); A.scene.add(isl);
  const clouds = [[-6, 7, -10, 1.6], [4, 8, -14, 2.2], [10, 6.5, -8, 1.3], [-12, 6, -6, 1.4]].map(([x, y, z, s]) => { const c = cloud(); c.position.set(x, y, z); c.scale.setScalar(s); A.scene.add(c); return c; });
  const cmat = clouds[0].children[0].material;
  const islLabel = textSprite('о. Антикитера', { size: 60, scale: 1.2 }); islLabel.position.set(-9, 3.4, -12); A.scene.add(islLabel);
  // подводная часть
  const B = newScene({ bg: 0x6fb3d6, floorY: -3, key: [2, 12, 3], fill: 0.8, keyI: 1.6, shadowSize: 16 });
  B.scene.fog = new THREE.Fog(0x6fb3d6, 12, 38);
  B.ground.material.color.set(0xe9d6b0);
  const dv = diver(); B.scene.add(dv);
  const statues = [];
  [[-2.6, -2.4, 0.5, 1.2, 0.3], [1.8, -2.45, -0.8, -1.25, -0.5], [4.6, -2.5, 1.6, 1.35, 0.9], [-5.2, -2.5, -2, -1.3, 0.2]].forEach(([x, y, z, rz, ry]) => {
    const s = bust(metal(C.bronze, { roughness: 0.5 })); s.position.set(x, y + 0.2, z); s.rotation.set(0, ry, rz); B.scene.add(s); statues.push(s);
  });
  const wreck = boat(); wreck.scale.setScalar(2.3); wreck.position.set(-1, -2.6, -9); wreck.rotation.set(0.1, 0.5, 0.35); B.scene.add(wreck);
  const amph = [[-4, -2.4, 2], [3, -2.5, 2.4], [0.5, -2.5, -3]].map(([x, y, z], i) => { const a = amphora(gloss(C.coral)); a.position.set(x, y, z); a.rotation.z = 1.4 + i * 0.3; a.scale.setScalar(0.7); B.scene.add(a); return a; });
  const bubbles = []; for (let i = 0; i < 18; i++) { const s = sphere(0.06 + hash(i) * 0.06, gloss(0xffffff, { transparent: true, opacity: 0.7 }), 12); B.scene.add(s); bubbles.push(s); }
  return { A, B, sea, b, clouds, cmat, islLabel, dv, statues, bubbles };
})();
export function s02(t) {
  const S = S2;
  if (t < 10.3) {
    const storm = smooth(seg(t, 3.2, 5.2));
    S.A.scene.background.setRGB(...new THREE.Color(0xcfe6f5).lerp(new THREE.Color(0x8e93b8), storm).toArray());
    S.A.scene.fog = null;
    const amp = lerp(0.7, 1.8, storm);
    S.sea.userData.update(t, amp);
    const hh = S.sea.userData.h;
    const by = hh(0, 0, t, amp); const tilt = (hh(1.5, 0, t, amp) - hh(-1.5, 0, t, amp)) / 3;
    S.b.position.set(0, by + 0.25, 0); S.b.rotation.set((hh(0, 0.6, t, amp) - hh(0, -0.6, t, amp)) * 0.4, 0.3, Math.atan(tilt));
    S.clouds.forEach((c, i) => { c.position.x += 0; c.position.x = [-6, 4, 10, -12][i] + Math.sin(t * 0.2 + i) * 0.8; });
    S.cmat.color.setRGB(...new THREE.Color(C.white).lerp(new THREE.Color(0xa7a9c9), storm).toArray());
    popScale(S.islLabel, t, 6.6);
    const az = lerp(0.9, 0.25, easeIO2(seg(t, 0, 10.3)));
    const el = lerp(0.42, 0.16, easeIO2(seg(t, 0, 10.3)));
    orbit(S.A.cam, v3(-1.5, 0.8, -2), lerp(17, 13, easeIO2(seg(t, 0, 10))), az, el);
    const flash = (t > 4.2 && t < 4.5 ? (1 - seg(t, 4.2, 4.5)) * 0.55 : 0) + (t > 4.75 && t < 4.95 ? 0.3 : 0);
    render(S.A.scene, S.A.cam, { time: t, focus: S.A.cam.position.distanceTo(v3(0, 0.5, 0)), aperture: 0.0006, flash });
    clear2d();
    pill('весна 1900', 140, 140, t, 0.7, { dot: CSS.sky, align: 'left', out: 9.6, size: 46 });
    title('ловцы губок', 140, 290, t, 3.8, { size: 110, align: 'left', out: 9.6, color: CSS.white });
    pill('между Критом и материковой Грецией', 140, 380, t, 7.6, { align: 'left', out: 9.8 });
    iris(seg(t, 9.6, 10.3) * 1, 960, 540, '#6fb3d6');
    return;
  }
  const u = t - 10.3;
  // ныряльщик спускается
  const dy = lerp(5.5, -0.9, easeOut(seg(u, 0, 3.6)));
  S.dv.position.set(0.3 + Math.sin(u * 0.7) * 0.2, dy, 1.6);
  S.dv.rotation.set(0, -0.4 + Math.sin(u * 0.5) * 0.15, Math.sin(u * 1.3) * 0.05);
  const panic = seg(u, 3.9, 5.2) * (1 - seg(u, 6.6, 7.4));
  S.dv.children.forEach((c) => { if (c.name === 'armL') c.rotation.z = -0.5 - panic * 1.6 * (0.6 + 0.4 * Math.sin(u * 18)); if (c.name === 'armR') c.rotation.z = 0.5 + panic * 1.6 * (0.6 + 0.4 * Math.sin(u * 18 + 1)); });
  S.dv.position.y += panic * 1.2;
  S.bubbles.forEach((b, i) => { const ph = (u * 0.6 + hash(i)) % 1; b.position.set(S.dv.position.x + (hash(i * 3) - 0.5) * 0.6, S.dv.position.y + 1.4 + ph * 5, S.dv.position.z + (hash(i * 7) - 0.5) * 0.6); });
  // статуи: сначала в тени, затем свет
  const reveal = smooth(seg(u, 7.0, 8.6));
  S.statues.forEach((s, i) => { s.traverse((o) => { if (o.isMesh) { o.material.color.set(C.bronze).multiplyScalar(lerp(0.35, 1, reveal)); } }); });
  const az = lerp(-0.6, 0.35, easeIO2(seg(u, 0, 17)));
  const el = lerp(0.1, 0.32, easeIO2(seg(u, 0, 17)));
  const tgt = v3(0, lerp(1.0, -1.4, easeIO2(seg(u, 0, 5))), 0);
  orbit(S.B.cam, tgt, lerp(10, 14.5, easeIO2(seg(u, 5, 17))), az, el);
  render(S.B.scene, S.B.cam, { time: t, focus: S.B.cam.position.distanceTo(tgt), aperture: 0.0012, maxblur: 0.012 });
  clear2d();
  iris(1 + seg(u, 0, 0.7), 960, 540, '#6fb3d6');
  pill('глубина ≈ 45 м', 140, 140, t, 11.6, { dot: CSS.sky, align: 'left', out: 15.6, size: 46 });
  title('на дне — тела?!', 140, 300, t, 15.0, { size: 110, align: 'left', out: 17.4, color: CSS.deep });
  title('нет — бронзовые статуи', 140, 300, t, 18.2, { size: 100, align: 'left', out: 26.2, color: CSS.deep });
  pill('римский корабль · ок. 70–60 гг. до н. э.', 140, 400, t, 21.0, { align: 'left', out: 26.4, size: 42 });
}

// ───────── 03. Находки и ком бронзы ─────────
const S3 = (() => {
  const S = newScene({ bg: C.cream, floorY: -1.5, key: [-4, 10, 6] });
  const peds = []; const items = [];
  const xs = [-6, -3, 0, 3.4];
  xs.forEach((x, i) => { const p = rbox(2.2, 1.6 + (i % 2) * 0.4, 2.2, matte(i === 3 ? C.lav : C.sand), 0.2); p.position.set(x, -1.5 + (1.6 + (i % 2) * 0.4) / 2, 0); S.scene.add(p); peds.push(p); });
  const st = bust(metal(C.bronze)); st.scale.setScalar(0.7); items.push(st);
  const am = amphora(gloss(C.coral)); am.scale.setScalar(0.75); items.push(am);
  const cs = coinStack(metal(C.gold)); items.push(cs);
  const lp = new THREE.Group(); const half1 = lump({ r: 0.95, seed: 3 }); const half2 = lump({ r: 0.95, seed: 3 });
  // две половины кома: клип по плоскости
  const cp1 = new THREE.Plane(v3(1, 0, 0), 0), cp2 = new THREE.Plane(v3(-1, 0, 0), 0);
  half1.material = matte(C.patina, { roughness: 0.85, clippingPlanes: [cp1], clipShadows: true, side: THREE.DoubleSide });
  half2.material = matte(C.patina, { roughness: 0.85, clippingPlanes: [cp2], clipShadows: true, side: THREE.DoubleSide });
  lp.add(half1, half2);
  const innerGear = gear(26, 0.62, metal(C.gold), { thick: 0.2, spokes: 4 }); innerGear.rotation.y = Math.PI / 2; lp.add(innerGear);
  items.push(lp);
  items.forEach((it, i) => { S.scene.add(it); });
  const shoe = rbox(3.0, 1.3, 1.9, gloss(C.lav, { transparent: true, opacity: 0.28, depthWrite: false }), 0.1); shoe.castShadow = false; S.scene.add(shoe);
  return { ...S, peds, items, xs, half1, half2, innerGear, shoe, lp, cp1, cp2 };
})();
export function s03(t) {
  const S = S3;
  const land = [1.7, 2.4, 3.1, 5.8];
  S.items.forEach((it, i) => {
    const top = S.peds[i].position.y + S.peds[i].geometry.parameters.height / 2;
    const restY = top + [0.95, 0.9, 0.5, 0.75][i];
    const k = seg(t, land[i] - 0.7, land[i]);
    const y = t < land[i] ? lerp(restY + 7, restY, easeIn(k)) : restY + Math.abs(Math.sin((t - land[i]) * 9)) * Math.exp(-(t - land[i]) * 5) * 0.5;
    it.position.set(S.xs[i], y, 0);
    it.visible = t > land[i] - 0.7;
    const sq = t > land[i] ? 1 - 0.15 * Math.exp(-(t - land[i]) * 8) * Math.cos((t - land[i]) * 20) : 1;
    it.scale.y = (i === 3 ? 1 : it.scale.x) * sq;
  });
  S.items[0].rotation.y = 0.4; S.items[1].rotation.y = t * 0.2;
  // трещина: половины расходятся
  const open = easeOut(seg(t, 16.0, 17.4));
  S.cp1.constant = -S.xs[3] - open * 0.35; S.cp2.constant = S.xs[3] - open * 0.35;
  S.half1.position.x = open * 0.35; S.half2.position.x = -open * 0.35;
  S.half1.rotation.z = -open * 0.12; S.half2.rotation.z = open * 0.12;
  S.innerGear.visible = open > 0.01; S.innerGear.rotation.x = t * 1.2;
  S.innerGear.material.emissive = new THREE.Color(0xffb84d); S.innerGear.material.emissiveIntensity = 0.35 * open * (0.7 + 0.3 * Math.sin(t * 6));
  S.shoe.position.set(S.xs[3], S.lp.position.y, 0);
  S.shoe.visible = t > 7.3 && t < 10.5;
  // камера: проезд вдоль витрины, затем наезд на ком
  const cx = lerp(-4.5, 3.4, easeIO2(seg(t, 0.5, 7.0)));
  const tgt = v3(cx, 0.9, 0);
  const push = easeIO2(seg(t, 13.5, 17.2));
  const r = lerp(12, 4.6, push);
  orbit(S.cam, tgt, r, lerp(-0.25, 0.25, seg(t, 0, 19)) + push * 0.2, lerp(0.22, 0.12, push));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tgt), aperture: lerp(0.0009, 0.002, push), maxblur: 0.012 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  const lab = (txt, i, t0, out) => { const p = project(v3(S.xs[i], 3.4, 0), S.cam); pill(txt, p.x, p.y, t, t0, { out, size: 40 }); };
  lab('статуи', 0, 1.8, 5.0); lab('амфоры', 1, 2.5, 5.0); lab('монеты', 2, 3.2, 5.0);
  title('и невзрачный ком бронзы', 140, 200, t, 5.4, { size: 84, align: 'left', out: 10.4 });
  pill('размером с обувную коробку', 140, 290, t, 7.5, { align: 'left', out: 10.4, dot: '#7a63e6' });
  pill('май 1902', 140, 150, t, 12.2, { dot: CSS.gold, align: 'left', size: 46, out: 18.6 });
  pill('археолог Валериос Стаис', 140, 245, t, 14.2, { align: 'left', out: 18.6 });
  title('…шестерёнка', 1780, 960, t, 17.0, { size: 120, align: 'right', color: '#c98a3e' });
}

// ───────── 04. Полторы тысячи лет ─────────
const S4 = (() => {
  const S = newScene({ bg: C.cream, floorY: -0.6, key: [6, 12, 8], shadowSize: 30 });
  const road = rbox(46, 0.3, 2.4, matte(C.sand), 0.14); road.position.set(20, -0.45, 0); S.scene.add(road);
  const marks = [];
  for (let i = 0; i <= 15; i++) { const m = rbox(0.12, 0.08, 2.0, matte(i % 5 === 0 ? C.lav : C.white), 0.03); m.position.set(i * 2.8, -0.26, 0); S.scene.add(m); marks.push(m); }
  const g = gear(24, 1.0, metal(C.gold), { thick: 0.3, spokes: 3 }); g.position.set(0, 1.1, 0); S.scene.add(g);
  const tw = clockTower(); tw.position.set(42, -0.3, 0); tw.scale.setScalar(0.85); S.scene.add(tw);
  const l1 = textSprite('II–I вв. до н. э.', { size: 56, scale: 1.3 }); l1.position.set(0, 2.9, 0); S.scene.add(l1);
  const l2 = textSprite('XIV век', { size: 56, scale: 1.3 }); l2.position.set(42, 6.8, 0); S.scene.add(l2);
  const miles = [[8, '0 г.'], [17, '500'], [26, '1000'], [35, '1300']].map(([x, txt]) => { const sp = textSprite(txt, { size: 50, scale: 1.1, bg: '#f4eefe' }); sp.position.set(x, 1.6, 1.4); S.scene.add(sp); return sp; });
  const col = (x, z, h, c) => { const g = new THREE.Group(); const b = puck(0.45, 0.25, matte(C.cream)); b.position.y = 0; g.add(b); const sh = cyl(0.3, h, matte(c), 24); sh.position.y = h / 2; g.add(sh); const cap = rbox(0.9, 0.25, 0.9, matte(C.cream), 0.08); cap.position.y = h; g.add(cap); g.position.set(x, -0.3, z); shadowAll(g); S.scene.add(g); };
  col(3, -2.4, 2.4, C.sand); col(4.4, -2.6, 1.8, C.sand); col(12, -2.6, 2.0, C.peach);
  const dome = sphere(1.4, matte(C.mint)); dome.scale.y = 0.7; dome.position.set(21, -0.3, -3); S.scene.add(dome);
  const tower2 = rbox(1.2, 3.2, 1.2, matte(C.lav), 0.15); tower2.position.set(30, 1.3, -3); S.scene.add(tower2);
  return { ...S, g, tw, l1, l2 };
})();
export function s04(t) {
  const S = S4;
  S.g.rotation.z = t * 0.8; S.g.rotation.y = Math.sin(t * 0.6) * 0.3;
  S.tw.userData.hand.rotation.z = -t * 2; S.tw.userData.hand2.rotation.z = -t * 0.3;
  popScale(S.l1, t, 2.4); popScale(S.l2, t, 7.6);
  const k = easeIO2(seg(t, 3.8, 9.8));
  const up = easeIO2(seg(t, 9.8, 13.0));
  const tgt = v3(lerp(0, 42, k) * (1 - up) + 21 * up, lerp(1.4, 3.0, k) * (1 - up) + 1.0 * up, 0);
  const r = lerp(9, 11, k) * (1 - up) + 46 * up;
  orbit(S.cam, tgt, r, lerp(0.75, 0.5, k) * (1 - up) + 0.0 * up, lerp(0.15, 0.2, k) * (1 - up) + 0.42 * up);
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tgt), aperture: lerp(0.0012, 0.0003, up), maxblur: 0.01 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('В Древней Греции?', 140, 220, t, 1.7, { size: 100, align: 'left', out: 5.0 });
  title('1500 лет', 960, 330, t, 10.6, { size: 230, color: '#7a63e6' });
  title('разницы', 960, 460, t, 11.2, { size: 110 });
  pill('многие просто не поверили', 960, 600, t, 13.4, { size: 44 });
}

// ───────── 05. Прайс и рентген ─────────
const S5 = (() => {
  const S = newScene({ bg: 0xe8e4f3, floorY: -1.6, key: [4, 10, 5] });
  const box = rbox(6, 0.5, 4, gloss(C.white), 0.2); box.position.y = -1.35; S.scene.add(box);
  const glow = rbox(5.2, 0.06, 3.2, new THREE.MeshBasicMaterial({ color: 0xcff2ff, toneMapped: false }), 0.05); glow.position.y = -1.08; S.scene.add(glow);
  const shell = lump({ r: 1.5, seed: 5, mat: matte(C.patina, { roughness: 0.85, transparent: true, opacity: 1 }) }); shell.position.y = 0.3; S.scene.add(shell);
  const inner = train([{ r: 0.9, mat: metal(C.gold) }, { r: 0.45, mat: gloss(C.sky), parent: 0, ang: 0.3 }, { r: 0.55, mat: gloss(C.pink), parent: 0, ang: 3.6 }, { r: 0.32, mat: gloss(C.mint), parent: 1, ang: 1.9 }]);
  inner.grp.position.set(-0.2, 0.3, 0); inner.grp.scale.setScalar(0.9); S.scene.add(inner.grp);
  const book = new THREE.Group();
  const cover = rbox(2.2, 2.9, 0.3, gloss(C.lav), 0.08); book.add(cover);
  const pages = rbox(2.05, 2.75, 0.26, matte(C.white), 0.04); pages.position.set(0.06, 0, 0.01); book.add(pages);
  const bt = textSprite('Gears from the Greeks', { size: 48, bg: null, color: CSS.white, weight: 900, scale: 0.75 }); bt.position.set(0, 0.5, 0.2); book.add(bt);
  book.position.set(3.4, 0.2, 0.6); S.scene.add(book);
  return { ...S, shell, inner, book, glow };
})();
export function s05(t) {
  const S = S5;
  const x = smooth(seg(t, 12.6, 14.2));
  S.shell.material.opacity = lerp(1, 0.16, x); S.shell.material.depthWrite = x < 0.5;
  S.inner.grp.visible = x > 0.02;
  const spin = smooth(seg(t, 15.0, 16.0)) * (1 - smooth(seg(t, 22.2, 23.4)));
  S.inner.update(t * 0.9 * spin + 0.4);
  S.glow.material.color.setRGB(...new THREE.Color(0xcff2ff).lerp(new THREE.Color(0x9fe8ff), x).toArray());
  const bk = easeOut(seg(t, 19.4, 20.4)); S.book.visible = bk > 0; S.book.position.y = lerp(-4, 0.4, bk) + Math.sin(t) * 0.05; S.book.rotation.set(-0.15, -0.5 + Math.sin(t * 0.5) * 0.1, 0.05);
  const tgt = v3(0.6, 0.3, 0);
  orbit(S.cam, tgt, lerp(11, 9, easeIO2(seg(t, 0, 26))), lerp(-0.5, 0.45, easeIO2(seg(t, 0, 26))), 0.24);
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(v3(0, 0.3, 0)), aperture: 0.001 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e8e4f3');
  title('полвека тишины', 140, 220, t, 0.8, { size: 100, align: 'left', out: 3.4 });
  pill('1951', 140, 150, t, 3.7, { dot: CSS.gold, align: 'left', size: 46, out: 16.5 });
  pill('Дерек де Солла Прайс · историк науки', 140, 245, t, 6.8, { align: 'left', out: 16.5 });
  pill('Хараламбос Каракалос · физик', 140, 335, t, 10.4, { align: 'left', out: 16.5 });
  title('рентген и гамма-лучи', 140, 1000, t, 12.4, { size: 76, align: 'left', out: 16.6 });
  title('внутри — десятки колёс', 140, 1000, t, 15.0, { size: 76, align: 'left', out: 21.0, color: '#7a63e6' });
  pill('1974', 140, 150, t, 17.3, { dot: CSS.gold, align: 'left', size: 46, out: 25.8 });
  title('но до конца — не успел', 140, 1000, t, 22.0, { size: 76, align: 'left', out: 25.8 });
}

// ───────── 06. Томограф 2005 ─────────
const S6 = (() => {
  const S = newScene({ bg: 0xe6eef7, floorY: -3.4, key: [5, 11, 6] });
  const ring = new THREE.Group(); S.scene.add(ring);
  const tor = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.62, 32, 96), gloss(C.white)); tor.castShadow = true; ring.add(tor);
  const band = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.64, 16, 96, Math.PI * 0.35), gloss(C.lav)); band.rotation.z = Math.PI * 0.32; ring.add(band);
  const glowR = new THREE.Mesh(new THREE.TorusGeometry(1.98, 0.045, 12, 96), new THREE.MeshBasicMaterial({ color: 0x8fe3ff, toneMapped: false })); ring.add(glowR);
  ring.rotation.y = Math.PI / 2;
  const stand = rbox(1.6, 2.3, 4.2, gloss(C.white), 0.3); stand.position.set(0, -2.3, 0); S.scene.add(stand);
  const bed = rbox(12, 0.25, 1.4, gloss(C.sky), 0.1); bed.position.set(0, -0.95, 0); S.scene.add(bed);
  const lmp = lump({ r: 1.0, seed: 7 }); S.scene.add(lmp);
  const slices = [];
  for (let i = 0; i < 14; i++) {
    const s = puck(0.9, 0.04, gloss(C.sky, { transparent: true, opacity: 0.55 })); s.rotation.z = Math.PI / 2; S.scene.add(s); slices.push(s);
    const gg = gear(20, 0.55, gloss(C.gold, { transparent: true, opacity: 0.9 }), { thick: 0.05, spokes: 3 }); gg.rotation.y = Math.PI / 2; s.add(gg); gg.rotation.set(0, 0, hash(i) * 3); gg.position.y = 0.03;
  }
  const model = train([{ r: 0.8, mat: metal(C.gold) }, { r: 0.42, mat: gloss(C.mint), parent: 0, ang: 0.4 }, { r: 0.5, mat: gloss(C.pink), parent: 0, ang: 3.5 }, { r: 0.3, mat: gloss(C.peach), parent: 1, ang: 2.2 }]);
  model.grp.position.set(5.2, 0.4, 0); S.scene.add(model.grp);
  const letters = ['ΗΛΙΟΣ', 'ΣΕΛΗΝΗ', 'ΖΩΔΙΑΚΟΣ', 'ΕΚΛΕΙΨΙΣ', 'ΟΛΥΜΠΙΑ', 'ΑΦΡΟΔΙΤΗ'].map((s, i) => { const sp = textSprite(s, { size: 58, scale: 1.1, color: CSS.deep, bg: '#fff7e8', font: 'NSerif', weight: 700 }); S.scene.add(sp); return sp; });
  return { ...S, ring, lmp, slices, model, letters, glowR };
})();
export function s06(t) {
  const S = S6;
  // ком проезжает сквозь кольцо, за ним остаются срезы
  const pass = seg(t, 9.0, 12.4);
  const lx = lerp(-4.5, 4.5, easeIO2(pass));
  S.lmp.position.set(lx, 0.3, 0); S.lmp.visible = t < 13.2;
  S.lmp.scale.setScalar(1 - smooth(seg(t, 12.4, 13.2)));
  S.glowR.material.color.setHSL(0.52, 0.9, 0.7 + 0.15 * Math.sin(t * 10) * (pass > 0 && pass < 1 ? 1 : 0));
  S.slices.forEach((s, i) => {
    const xi = -1.6 + i * 0.25; const born = 9.0 + ((xi + 4.5) / 9) * 3.4;
    const gather = easeIO2(seg(t, 12.6 + i * 0.05, 15.4 + i * 0.05));
    s.visible = t > born && gather < 0.999;
    s.position.set(lerp(xi + 3.2, 5.2, gather), lerp(2.6 + Math.sin(i) * 0.1, 0.4, gather), lerp(0, 0, gather));
    s.scale.setScalar(lerp(1, 0.2, gather));
  });
  const mk = easeOut(seg(t, 14.6, 15.8)); S.model.grp.visible = mk > 0; S.model.grp.scale.setScalar(spring(seg(t, 14.6, 16.2) * 1.3, 7, 5));
  S.model.update(t * 0.6); S.model.grp.rotation.y = -0.6 + Math.sin(t * 0.4) * 0.2;
  S.letters.forEach((l, i) => {
    const t0 = 19.6 + i * 0.35; popScale(l, t, t0);
    const a = i * 1.05 + t * 0.15; l.position.set(5.2 + Math.cos(a) * 2.4, 0.6 + Math.sin(a * 1.3) * 1.3 + (i % 2) * 0.5, Math.sin(a) * 1.6);
  });
  const tg = v3(lerp(0, 4.2, easeIO2(seg(t, 12, 16))), 0.3, 0);
  orbit(S.cam, tg, lerp(13, 9.5, easeIO2(seg(t, 0, 30))), lerp(0.75, 0.25, easeIO2(seg(t, 0, 31))) , lerp(0.28, 0.18, seg(t, 0, 30)));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: 0.0009 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#e6eef7');
  pill('2005', 140, 150, t, 1.9, { dot: CSS.gold, align: 'left', size: 46, out: 12.0 });
  pill('Майк Эдмундс · Кардиффский университет', 140, 245, t, 4.5, { align: 'left', out: 12.0 });
  title('компьютерный томограф', 140, 1000, t, 7.6, { size: 76, align: 'left', out: 11.8 });
  counter('82', 1700, 330, { size: 220, color: '#7a63e6', alpha: clamp(seg(t, 9.7, 10.2)) * (1 - seg(t, 12.6, 13.0)), align: 'right' });
  pill('обломка', 1700, 400, t, 10.0, { align: 'right', out: 12.6 });
  title('слой за слоем → 3D-модель', 140, 1000, t, 12.6, { size: 76, align: 'left', out: 18.2 });
  title('и внутри — текст', 140, 1000, t, 18.2, { size: 76, align: 'left', out: 24.4 });
  title('инструкция пользователя', 140, 1000, t, 24.6, { size: 76, align: 'left', color: '#7a63e6', out: 31.4 });
  const cnt = Math.round(3000 * easeOut(seg(t, 27.4, 29.8)));
  counter(cnt > 0 ? cnt.toLocaleString('ru-RU') + '+' : '', 140, 330, { size: 170, align: 'left', alpha: clamp(seg(t, 27.4, 27.8)) * (1 - seg(t, 31.4, 31.8)) });
  pill('символов прочитано', 140, 400, t, 28.6, { align: 'left', out: 31.6 });
}
