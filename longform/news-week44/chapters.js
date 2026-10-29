// Сцены глав. Каждая глава: fn(ct, L) — ct локальное время главы, L = {i, lt, line, lines, ch, cue(lineId, word)}.
// Камера меняется по репликам (CAMS[i % n]); карточки фактов привязаны к репликам и словам.
import { render, clear2d, ctx, W, H, THREE, C, CSS, matte, gloss, metal, clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1, project } from './engine.js';
import { v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, cloud } from './kit.js';
import * as P from './props.js';
import { badge, chapterCard, speaker, fact, bigNum, quote, checklist, source, punch, RED, LAV, MINT, SKY, INK } from './news.js';

const TOTAL = 8;
const dofOf = (cam, tg, ap = 0.0007, mb = 0.008) => ({ focus: cam.position.distanceTo(tg), aperture: ap, maxblur: mb });
// камера: плавный «долли» между двумя положениями за время реплики
function dolly(cam, tg, r0, r1, az0, az1, el0, el1, k) { const e = easeIO2(k); orbit(cam, tg, lerp(r0, r1, e), lerp(az0, az1, e), lerp(el0, el1, e)); }
function camFor(L, CAMS, S, t) { const i = Math.max(0, L.i); const c = CAMS[i % CAMS.length]; const k = L.i < 0 ? clamp(L.ct / Math.max(1, L.intro)) : clamp(L.lt / Math.max(1.5, L.line.dur)); return c(S.cam, k, t); }
// общие 2D-слои главы
function common(n, name, L) {
  const t = L.ct;
  chapterCard(n, name, t, 0.05, L.intro);
  badge(n, TOTAL, name, t, L.intro - 0.2);
  if (L.i >= 0) speaker(L.line.sp, L.lt > 0 && L.lt < L.line.vdur, L.ct, L.intro);
}
// окно карточки = реплика (с небольшим заходом в следующую)
const win = (L, idx, a = 0.15, tail = 0.4) => { const ln = L.lines[idx - 1]; if (!ln) return null; return [ln.s + a, ln.s + ln.dur + tail]; };
function onLine(L, idx, f, a, tail) { const w = win(L, idx, a, tail); if (w && L.ct > w[0] - 0.05 && L.ct < w[1] + 0.6) f(L.ct, w[0], w[1]); }
const at = (L, id, word, nth = 0, fb = 0) => L.cue(id, word, nth, fb);

// ═══════════════ 0. Вступление ═══════════════
const S0 = (() => {
  const S = newScene({ bg: 0xf0d9c4, floorY: 0, key: [6, 12, 8], shadowSize: 16 }); S.ground.material.color.set(0xfaf2ea);
  const turn = new THREE.Group(); S.scene.add(turn);
  const disc = puck(7.2, 0.4, gloss(0xffffff)); disc.position.y = 0.2; turn.add(disc);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(7.2, 0.08, 12, 96), gloss(C.lav)); ring.rotation.x = Math.PI / 2; ring.position.y = 0.42; turn.add(ring);
  const items = [];
  const add = (o, s = 1, y = 0.4) => { const g = new THREE.Group(); g.add(o); o.scale.setScalar(s); const a = (items.length / 8) * Math.PI * 2; g.position.set(Math.sin(a) * 4.9, y, Math.cos(a) * 4.9); g.rotation.y = a; turn.add(g); items.push(g); return g; };
  add(P.truck().g, 0.32);
  const bg = P.bruteGrid(5, 0.3); add(bg.g, 0.9);
  add(P.node('HR', C.white, 1.6), 0.9);
  add(P.coinStack(9), 1.4);
  add(P.worldIsland(), 0.32, 1.4);
  add(P.house(), 0.6);
  add(P.humanoid(), 0.9);
  const sh = P.stage(5, 0.5, 0xd7dbe3, true); add(sh, 0.45);
  const title3 = textSprite('НОВОСТИ НЕДЕЛИ', { size: 110, color: '#2b2a3a', bg: '#ffffff', scale: 1.5 }); title3.position.set(0, 3.7, 0); S.scene.add(title3);
  return { ...S, turn, items };
})();
const CAMS0 = [
  (cam, k) => { dolly(cam, v3(0, 1.2, 0), 19, 15, 0.2, -0.3, 0.42, 0.3, k); return v3(0, 1.2, 0); },
  (cam, k) => { dolly(cam, v3(0, 0.8, 4.6), 6.5, 5.5, 0.6, 0.2, 0.25, 0.18, k); return v3(0, 0.8, 4.6); },
  (cam, k) => { dolly(cam, v3(0, 2.6, 0), 17, 20, -0.5, -0.1, 0.18, 0.3, k); return v3(0, 2.6, 0); },
  (cam, k) => { dolly(cam, v3(0, 1, 0), 12, 13, 1.2, 0.4, 0.55, 0.45, k); return v3(0, 1, 0); },
];
export function c0(ct, L) {
  const S = S0; S.turn.rotation.y = -ct * 0.16;
  S.items.forEach((g, i) => { g.children[0].position.y = Math.sin(ct * 1.6 + i) * 0.08; });
  const tg = camFor(L, CAMS0, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg, 0.0005) });
  clear2d();
  badge(0, TOTAL, '26–29 октября', ct, 0.6);
  if (L.i >= 0) speaker(L.line.sp, L.lt > 0 && L.lt < L.line.vdur, ct, 0.4);
  onLine(L, 1, (t, a, b) => { punch('$100 000 000', 520, 300, t, at(L, 'c0_01', 'грузовики', 0, a), at(L, 'c0_01', 'нейросеть', 0, b), { size: 92 });
    punch('ИИ vs 1999', 960, 470, t, at(L, 'c0_01', 'нейросеть', 0, a), at(L, 'c0_01', 'а', 0, b), { size: 92, bg: LAV, rot: 0.03 });
    punch('12 ЧАСОВ', 1380, 640, t, at(L, 'c0_01', 'агенты', 0, a), b, { size: 92, bg: INK, rot: -0.02 }); });
  onLine(L, 4, (t, a, b) => checklist([[null, 'Ограбления на трассе'], [null, 'Математика и ИИ'], [null, 'Взлом агентами'], [null, 'Биржа'], [null, 'Генератор миров'], [null, 'Война с соседями'], [null, 'Роботы'], [null, 'Ракета в «руки»']], 120, 230, t, a, b + 1.2, { w: 640, size: 34 }));
  onLine(L, 5, (t, a, b) => fact('ПРАВИЛО ВЫПУСКА', 'Каждый факт — минимум 2 источника. Ссылки в описании.', 120, 260, t, a, b, { w: 760, color: MINT }));
}

// ═══════════════ 1. Ограбление на трассе ═══════════════
const S1 = (() => {
  const S = newScene({ bg: 0xc8deee, floorY: 0, key: [-8, 14, 9], shadowSize: 22, keyI: 3 });
  S.ground.material.color.set(0xcfe0c4);
  const rd = P.road(160); S.scene.add(rd);
  const tr = P.truck(); S.scene.add(tr.g);
  const esc = P.car(0x3d3a5c); S.scene.add(esc);
  const thief = P.car(0x23222e); S.scene.add(thief);
  const pin = P.gpsPin(); pin.scale.setScalar(1.4); S.scene.add(pin);
  const pinFake = P.gpsPin(0x9a98aa); pinFake.scale.setScalar(1.4); S.scene.add(pinFake);
  const env = P.envelope(); env.scale.setScalar(1.6); S.scene.add(env);
  const hk = P.hook(); hk.scale.setScalar(1.3); S.scene.add(hk);
  const lot = new THREE.Group(); S.scene.add(lot); lot.position.set(0, 0, -30);
  const lotPad = rbox(26, 0.06, 14, matte(0xb9bcc7), 0.02); lotPad.position.y = 0.03; lot.add(lotPad);
  for (let i = 0; i < 6; i++) { const l = rbox(0.12, 0.02, 4, matte(0xffffff), 0.01); l.position.set(-10 + i * 4, 0.08, -4); lot.add(l); }
  const pallets = []; for (let i = 0; i < 6; i++) { const p = P.pallet(); p.position.set(-6 + (i % 3) * 2.4, 0, 2 + Math.floor(i / 3) * 2); lot.add(p); pallets.push(p); }
  const racks = []; for (let i = 0; i < 6; i++) { const r = P.serverRack(1.5); r.position.set(-6 + (i % 3) * 2.4, 0.24, 2 + Math.floor(i / 3) * 2); lot.add(r); racks.push(r); }
  const gold = new THREE.Group(); S.scene.add(gold); gold.position.set(0, 0, 18);
  for (let i = 0; i < 10; i++) { const b = rbox(1.1, 0.4, 0.55, metal(0xe9b97f, { roughness: 0.2 }), 0.08); b.position.set((i % 4) * 1.2 - 1.8, 0.2 + Math.floor(i / 4) * 0.42, (i % 2) * 0.1); b.rotation.y = (hash(i) - 0.5) * 0.2; gold.add(b); }
  const goldRack = P.serverRack(1.5); goldRack.position.set(3.2, 0, 0); gold.add(goldRack);
  const copper = new THREE.Group(); S.scene.add(copper); copper.position.set(-16, 0, 18);
  for (let i = 0; i < 3; i++) { const sp = new THREE.Mesh(new THREE.TorusGeometry(0.8, 0.45, 16, 40), metal(0xd9824a, { roughness: 0.35 })); sp.position.set(i * 2.2, 0.9, 0); copper.add(sp); const core = cyl(0.38, 1.0, wood(), 20); core.rotation.x = Math.PI / 2; core.position.set(i * 2.2, 0.9, 0); copper.add(core); }
  const pwr = rbox(2.6, 2.2, 1.6, gloss(0xdfe3ea), 0.15); pwr.position.set(7.5, 1.1, 0); copper.add(pwr);
  const bolt = rbox(0.5, 0.9, 0.06, glow(0xffdc7a), 0.05); bolt.position.set(7.5, 1.3, 0.82); bolt.rotation.z = 0.4; copper.add(bolt);
  P.shadowAll(copper);
  return { ...S, rd, tr, esc, thief, pin, pinFake, env, hk, lot, racks, gold, copper };
})();
function wood() { return matte(0xc99766, { roughness: 0.75 }); }
function glow(c) { return new THREE.MeshBasicMaterial({ color: c, toneMapped: false }); }
function driveTruck(S, ct, speed = 9) {
  const x = -((ct * speed) % 60) + 30; // дорожная разметка «едет»
  S.rd.userData.dashes.position.x = ((ct * speed) % 4);
  S.tr.wheels.forEach((w) => (w.rotation.z = -ct * speed / 0.42));
  return x;
}
const CAMS1 = [
  (cam, k) => { dolly(cam, v3(0, 2, 0), 22, 18, 0.9, 0.6, 0.22, 0.16, k); return v3(0, 2, 0); },
  (cam, k) => { dolly(cam, v3(-3, 2, 0), 10, 9, -1.1, -0.8, 0.12, 0.1, k); return v3(-3, 2, 0); },
  (cam, k) => { dolly(cam, v3(4, 1.6, 0), 9, 8, 1.5, 1.2, 0.1, 0.08, k); return v3(4, 1.6, 0); },
  (cam, k) => { dolly(cam, v3(0, 1.5, 0), 26, 24, 0.0, 0.25, 0.5, 0.42, k); return v3(0, 1.5, 0); },
];
export function c1(ct, L) {
  const S = S1; const i = L.i;
  // по умолчанию: колонна едет; отдельные реплики — отдельные «декорации»
  driveTruck(S, ct);
  S.tr.g.position.set(0, 0, 1.5); S.esc.position.set(-11, 0, 1.6); S.esc.visible = true; S.thief.visible = false;
  S.esc.userData.wheels.forEach((w) => (w.rotation.z = -ct * 20)); S.esc.userData.bar.material.color.set(Math.sin(ct * 12) > 0 ? 0xff5f6d : 0x6aa8ff);
  S.pin.visible = S.pinFake.visible = S.env.visible = S.hk.visible = false; S.tr.setOpen(0); S.tr.cargo.visible = true;
  let tg;
  const ids = (n) => i === n - 1;
  if (ids(4) || ids(5)) { // таран машины сопровождения, потом пустой прицеп на стоянке
    const tR = at(L, 'c1_04', 'протаранили', 0, 7) - L.lines[3].s;
    const lt = i === 3 ? L.lt : L.lt + L.lines[3].dur;
    S.thief.visible = true; const hit = clamp((lt - tR + 1.2) / 1.2);
    S.thief.position.set(lerp(-26, -11.5, easeIn(hit)), 0, lerp(-2.5, 0.2, hit)); S.thief.rotation.y = lerp(0.25, 0.05, hit);
    if (lt > tR) { const kk = clamp((lt - tR) / 0.8); S.esc.position.set(-11 - kk * 1.5, kk * 0.4 * Math.sin(kk * Math.PI), 1.6 + kk * 3.2); S.esc.rotation.set(0, kk * 1.3, kk * 0.25); }
    else S.esc.rotation.set(0, 0, 0);
    if (i === 4) { S.lot.position.set(0, 0, 0); S.tr.g.position.set(-2, 0, -27); S.tr.setOpen(1); S.tr.cargo.visible = false; S.esc.visible = false; S.thief.visible = false;
      orbit(S.cam, v3(-2, 2, -30), 16, -0.7 + L.lt * 0.03, 0.35); tg = v3(-2, 2, -30); S.lot.position.set(0, 0, -30); S.racks.forEach((r, j) => (r.visible = j < 2)); }
    else { orbit(S.cam, v3(-9, 1.4, 1.5), lerp(16, 12, easeIO2(clamp(L.lt / L.line.dur))), -0.55, 0.16); tg = v3(-9, 1.4, 1.5); }
  } else if (ids(6)) { // Калифорния → Техас: трекер «прыгает»
    S.thief.visible = true; S.thief.position.set(-15, 0, 0.5);
    S.pin.visible = true; S.pin.position.set(0, 5.2 + Math.sin(ct * 3) * 0.2, 1.5);
    const tS = at(L, 'c1_06', 'данные', 0, 4) - L.line.s;
    S.pinFake.visible = L.lt > tS; S.pinFake.position.set(16 + Math.sin(ct * 9) * 0.6, 5.2, -6);
    if (L.lt > tS) S.pin.material && 0; S.pin.scale.setScalar(L.lt > tS ? 1.4 * (0.6 + 0.4 * Math.abs(Math.sin(ct * 10))) : 1.4);
    orbit(S.cam, v3(2, 2.5, -1), 24, 0.35 + L.lt * 0.02, 0.38); tg = v3(2, 2.5, -1);
  } else if (ids(8) || ids(9)) { // фишинг: конверт на крючке
    S.env.visible = S.hk.visible = true; S.tr.g.position.set(0, 0, 1.5);
    const sw = Math.sin(ct * 1.4) * 0.15; S.hk.position.set(3, 4.5, 6); S.hk.rotation.z = sw; S.env.position.set(3.25 + sw * 0.8, 4.1, 6.1); S.env.rotation.z = sw * 1.2;
    orbit(S.cam, v3(2, 3.6, 5), lerp(9, 7.5, clamp(L.lt / 6)), 0.15, 0.08); tg = v3(3, 4.1, 6);
  } else if (ids(10)) { // золотые слитки
    orbit(S.cam, v3(0.6, 0.8, 18), lerp(8, 6.5, clamp(L.lt / 8)), 0.5 - L.lt * 0.03, 0.3); tg = v3(0.6, 0.6, 18);
  } else if (ids(12)) { // медь и силовое оборудование
    orbit(S.cam, v3(-12, 1.2, 18), lerp(14, 12, clamp(L.lt / 8)), 0.35 + L.lt * 0.02, 0.22); tg = v3(-12, 1.2, 18);
  } else if (ids(14) || ids(15)) { // «толкнул и уехал»: таран со стороны водителя
    S.thief.visible = true; const k = clamp(((i === 13 ? L.lt : L.lt + 6) - 3) / 2.5);
    S.thief.position.set(-11.5, 0, lerp(-6, -0.3, easeIn(clamp(k * 2)))); S.thief.rotation.y = 1.4;
    if (k > 0.5) { const kk = clamp((k - 0.5) * 2); S.esc.position.set(-11 - kk, 0, 1.6 + kk * 2.5); S.esc.rotation.y = kk * 0.9; }
    orbit(S.cam, v3(-6, 1.5, 0.5), 15, -0.15, 0.28); tg = v3(-6, 1.5, 0.5);
  } else tg = camFor(L, CAMS1, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(1, 'Ограбление на трассе', L);
  onLine(L, 3, (t, a, b) => { bigNum(100, ' млн $+', 'украдено оборудования для ИИ-дата-центров с июня 2026', 120, 380, t, at(L, 'c1_03', 'больше', 0, a), b, { prefix: '' }); source('NBC News, Futurism', t, a, b); });
  onLine(L, 4, (t, a, b) => { fact('ДЖОРДЖИЯ · ФЕЙЕТВИЛЛ', 'Машину сопровождения протаранили. Пропали паллеты на $13 млн', 120, 230, t, at(L, 'c1_04', 'протаранили', 0, a), b, { w: 820 }); });
  onLine(L, 6, (t, a, b) => { fact('КАЛИФОРНИЯ → ТЕХАС', 'Стойки на ~$10 млн. Данные трекера подделаны', 120, 230, t, a, b, { w: 760, color: LAV }); });
  onLine(L, 8, (t, a, b) => checklist([[false, 'Фишинг аккаунта брокера'], [false, 'Ставки на реальные заказы'], [false, 'Водитель с фальшивыми документами']], 110, 220, t, at(L, 'c1_08', 'мошенники', 0, a), b, { w: 820 }));
  onLine(L, 10, (t, a, b) => quote('Это как красть чистые золотые слитки', 'Кит Льюис, Verisk CargoNet', 110, 230, t, at(L, 'c1_10', 'сказал', 0, a), b, { w: 820 }));
  onLine(L, 12, (t, a, b) => { fact('ИЛЛИНОЙС', 'Медный кабель ~$300 тыс. и силовое оборудование для дата-центров ~$1 млн', 110, 230, t, a, b, { w: 860, color: '#d9824a' }); });
  onLine(L, 14, (t, a, b) => { bigNum(110.6, ' млн $', 'известные кражи с 3 июня по середину августа (Скотт Корнелл, TAPA)', 120, 360, t, at(L, 'c1_14', 'августе', 0, a), at(L, 'c1_14', 'описывал', 0, b), { dec: 1, from: 60 }); punch('«ТОЛКНУЛ И УЕХАЛ»', 760, 300, t, at(L, 'c1_14', 'толкнул', 0, b), b, { size: 74, bg: INK }); source('FreightWaves, 14.08.2026', t, a, b); });
  onLine(L, 17, (t, a, b) => punch('ГОНКА ИИ = ДОРОГОЕ ЖЕЛЕЗО', 960, 300, t, at(L, 'c1_17', 'первая', 0, a), b, { size: 70, bg: LAV, rot: 0 }));
}

// ═══════════════ 2. ИИ против гипотезы 1999 года ═══════════════
const S2 = (() => {
  const S = newScene({ bg: 0xd9ccf2, floorY: 0, key: [5, 12, 9], shadowSize: 16 }); S.ground.material.color.set(0xf1ecfa);
  const grid = P.bruteGrid(8, 0.46); S.scene.add(grid.g); grid.g.position.set(-4.6, 0, 0);
  const bd = P.board(['SAT', '2ⁿ', 'ETH?', '1999']); bd.position.set(3.4, 2.4, -1.6); bd.rotation.y = -0.25; S.scene.add(bd);
  const cube = P.leanCube(); cube.position.set(1.2, 0.8, 2.2); S.scene.add(cube);
  const papers = P.paperStack(18); papers.position.set(4.5, 0, 2.4); S.scene.add(papers);
  const mag = P.magnifier(); mag.position.set(5.2, 1.6, 3.2); mag.rotation.set(-0.3, -0.4, 0.2); S.scene.add(mag);
  const pillar = new THREE.Group(); S.scene.add(pillar); pillar.position.set(-4.6, 0, -5);
  const base = rbox(6, 0.5, 2.4, matte(0xd8d2e8), 0.08); base.position.y = 3.6; pillar.add(base);
  for (const x of [-2.4, 0, 2.4]) { const c = cyl(0.32, 3.4, gloss(0xffffff), 24); c.position.set(x, 1.7, 0); pillar.add(c); }
  const roofT = textSprite('ТРУДНЫЕ ЗАДАЧИ', { size: 60, color: '#2b2a3a', bg: '#ffffff', scale: 0.9 }); roofT.position.set(0, 4.4, 0.6); pillar.add(roofT);
  P.shadowAll(pillar);
  const cubes = []; for (let i = 0; i < 4; i++) { const k = rbox(1.1, 1.1, 1.1, gloss([C.coral, C.butter, C.mint, C.sky][i]), 0.18); k.position.set(-2 + i * 1.3, 0.55, 5.4); S.scene.add(k); cubes.push(k); } // «мебель» шкаф/кухня
  const people = []; for (let i = 0; i < 3; i++) { const p = new THREE.Group(); const b = rbox(0.5, 0.9, 0.35, gloss([C.lav, C.peach, C.sage][i]), 0.18); b.position.y = 0.45; p.add(b); const h = sphere(0.22, matte(0xf3c9a9)); h.position.y = 1.1; p.add(h); p.position.set(5.6 + i * 0.9, 0, -0.4 + i * 0.3); p.rotation.y = -0.9; P.shadowAll(p); S.scene.add(p); people.push(p); }
  return { ...S, grid, bd, cube, papers, mag, pillar, cubes, people };
})();
const CAMS2 = [
  (cam, k) => { dolly(cam, v3(-1, 1.6, 0), 17, 15, 0.5, 0.2, 0.32, 0.25, k); return v3(-1, 1.6, 0); },
  (cam, k) => { dolly(cam, v3(-4.6, 1.8, 0), 9, 8, -0.4, -0.1, 0.3, 0.2, k); return v3(-4.6, 1.8, 0); },
  (cam, k) => { dolly(cam, v3(3.4, 2.3, -1.6), 8, 7, -0.1, -0.35, 0.1, 0.05, k); return v3(3.4, 2.3, -1.6); },
  (cam, k) => { dolly(cam, v3(1.2, 0.9, 2.2), 6, 5, 0.6, 0.9, 0.2, 0.15, k); return v3(1.2, 0.9, 2.2); },
];
export function c2(ct, L) {
  const S = S2; const i = L.i;
  // решётка перебора: клетки зажигаются по очереди (во время объяснения — быстрее)
  const speed = i >= 4 && i <= 6 ? 26 : 6; const lit = Math.floor(ct * speed) % S.grid.cells.length;
  S.grid.cells.forEach((c, j) => { const d = (lit - j + S.grid.cells.length) % S.grid.cells.length; c.material.color.setHex(d < 6 ? 0xffdc7a : d < 14 ? 0xffe9c2 : 0xffffff); });
  // фундамент «трясётся» на «фундамент неверен»
  const tF = at(L, 'c2_07', 'неверен', 0, 1e9); const sh = ct > tF && ct < tF + 2.5 ? Math.sin(ct * 40) * 0.05 * (1 - (ct - tF) / 2.5) : 0; S.pillar.position.x = -4.6 + sh;
  // Lean-куб: появляется на «Lean»
  popScale(S.cube, ct, at(L, 'c2_09', 'lean', 0, 1e9) - 0.2, 0.9); S.cube.rotation.y = ct * 0.4;
  S.cubes.forEach((c, j) => { const t0 = at(L, 'c2_22', 'кухню', 0, 1e9) - 0.4 + j * 0.15; popScale(c, ct, t0, 0.7); c.visible = ct > t0 && i <= 23; });
  S.mag.position.y = 1.6 + Math.sin(ct * 1.2) * 0.1;
  let tg;
  if (i === 13 || i === 14 || i === 15) { orbit(S.cam, v3(6.2, 1, 0), lerp(9, 8, clamp(L.lt / 6)), -0.95, 0.15); tg = v3(6.2, 1, 0); }
  else if (i === 21 || i === 22) { orbit(S.cam, v3(0, 0.6, 5.4), 8, 0.2 + L.lt * 0.03, 0.3); tg = v3(0, 0.6, 5.4); }
  else if (i === 6) { orbit(S.cam, v3(-4.6, 2.2, -5), 11, 0.3, 0.18); tg = v3(-4.6, 2.2, -5); }
  else tg = camFor(L, CAMS2, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(2, 'ИИ против гипотезы 1999 года', L);
  onLine(L, 3, (t, a, b) => fact('ЗАЯВЛЕНИЕ OPENAI', 'Модель нашла опровержение гипотезы экспоненциального времени (ETH)', 110, 230, t, at(L, 'c2_03', 'опровержение', 0, a), b, { w: 860, color: LAV }));
  onLine(L, 5, (t, a, b) => { fact('ГИПОТЕЗА ETH · 1999', 'Задачи вроде SAT нельзя решать радикально быстрее перебора', 110, 230, t, at(L, 'c2_05', 'гипотеза', 0, a), b, { w: 860 }); });
  onLine(L, 9, (t, a, b) => checklist([[true, '16 октября — найдено'], [true, 'Через день — проверено в Lean'], [true, 'Текст и доказательство — в открытом доступе']], 110, 220, t, a, b, { w: 840 }));
  onLine(L, 10, (t, a, b) => checklist([[null, 'Гипотеза Какеи — во всех измерениях'], [null, 'Квантовые теории поля в 4D'], [null, 'Включая Янга — Миллса']], 110, 220, t, a, b, { w: 840 }));
  onLine(L, 12, (t, a, b) => punch('НА ПРИЗ НЕ ПРЕТЕНДУЕТ', 760, 300, t, a + 0.6, b, { size: 70, bg: INK }));
  onLine(L, 14, (t, a, b) => fact('НЕЗАВИСИМАЯ ПРОВЕРКА', 'Райан Уильямс, Рассел Импальяццо, Рамамохан Патури', 110, 230, t, at(L, 'c2_14', 'учёные', 0, a), b, { w: 860, color: MINT }));
  onLine(L, 16, (t, a, b) => quote('Наше участие не следует считать подтверждением', 'проверяющие (пересказ)', 110, 230, t, at(L, 'c2_16', 'написали', 0, a), b, { w: 860 }));
  onLine(L, 18, (t, a, b) => bigNum(5, ' млн $', 'фонду Саймонса на семинары по результатам ИИ', 120, 380, t, at(L, 'c2_18', 'пять', 0, a), b));
  onLine(L, 21, (t, a, b) => checklist([[true, '2019 — сглаживание: только 2D'], [true, '2025 — Какея: только 3D'], [null, '2026 — заявка: все измерения']], 110, 220, t, a, b, { w: 840 }));
  onLine(L, 24, (t, a, b) => punch('ЗАЯВЛЕНИЕ ≠ ДОКАЗАННЫЙ ФАКТ', 960, 300, t, a, b + 3, { size: 72, bg: RED, rot: 0 }));
}

// ═══════════════ 3. Агенты-взломщики ═══════════════
const S3 = (() => {
  const S = newScene({ bg: 0xc9dcf0, floorY: 0, key: [6, 12, 6], shadowSize: 16 }); S.ground.material.color.set(0xeef3f9);
  const names = [['ПРОДАЖИ', -5, 2], ['HR', -1.7, 3.6], ['IT', 1.7, 3.6], ['CLAUDE', 5, 0.2]];
  const nodes = names.map(([n, x, z], i) => { const m = P.node(n, i === 3 ? C.lav : C.white, i === 3 ? 2.4 : 1.9); m.position.set(x, 0, z - 2); S.scene.add(m); return m; });
  const vendor = P.node('СТОРОННИЙ СЕРВИС', C.butter, 3.4); vendor.position.set(-5.6, 0, 6.2); S.scene.add(vendor);
  const lk = P.lock(); lk.position.set(5, 2.0, -1.2); lk.scale.setScalar(1.3); S.scene.add(lk);
  const sh = P.shield(); sh.position.set(6.6, 1.6, -1.2); sh.scale.setScalar(0.9); S.scene.add(sh);
  const agents = []; for (let i = 0; i < 5; i++) { const a = P.agent(i % 2 ? 0xff8f87 : 0xffb48a); S.scene.add(a); agents.push(a); }
  const pathPts = [v3(-5.6, 1.2, 6.2), v3(-5, 1.2, 0), v3(-1.7, 1.2, 1.6), v3(1.7, 1.2, 1.6)];
  const curve = new THREE.CatmullRomCurve3(pathPts);
  const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 80, 0.05, 8), new THREE.MeshBasicMaterial({ color: 0xff8f87, toneMapped: false, transparent: true, opacity: 0.7 })); S.scene.add(tube);
  const clock = new THREE.Group(); S.scene.add(clock); clock.position.set(-1, 3.8, -5);
  const face = puck(1.4, 0.2, gloss(0xffffff)); face.rotation.x = Math.PI / 2; clock.add(face);
  const hand = rbox(0.12, 1.1, 0.06, matte(0x2b2a3a), 0.04); hand.geometry.translate(0, 0.45, 0); hand.position.z = 0.14; clock.add(hand);
  for (let i = 0; i < 12; i++) { const m = rbox(0.08, 0.22, 0.04, matte(0x7a63e6), 0.02); const a = (i / 12) * Math.PI * 2; m.position.set(Math.sin(a) * 1.15, Math.cos(a) * 1.15, 0.12); m.rotation.z = -a; clock.add(m); }
  P.shadowAll(clock);
  return { ...S, nodes, vendor, lk, sh, agents, curve, tube, hand };
})();
const CAMS3 = [
  (cam, k) => { dolly(cam, v3(0, 1, 1.5), 19, 17, 0.4, 0.15, 0.5, 0.42, k); return v3(0, 1, 1.5); },
  (cam, k) => { dolly(cam, v3(-5, 1.2, 4), 9, 8, -0.5, -0.2, 0.25, 0.2, k); return v3(-5, 1.2, 4); },
  (cam, k) => { dolly(cam, v3(5, 1.4, -1.6), 8, 7, 0.4, 0.1, 0.2, 0.15, k); return v3(5, 1.4, -1.6); },
  (cam, k) => { dolly(cam, v3(0, 1.4, 1), 14, 13, -0.6, -0.3, 0.3, 0.25, k); return v3(0, 1.4, 1); },
];
export function c3(ct, L) {
  const S = S3; const i = L.i;
  S.agents.forEach((a, j) => { const p = ((ct * 0.09 + j * 0.2) % 1); const pt = S.curve.getPoint(p); a.position.set(pt.x, pt.y + Math.sin(ct * 3 + j) * 0.12, pt.z); a.rotation.y = ct + j; });
  S.hand.rotation.z = -ct * 0.6;
  // Claude: замок светится зелёным; при «не были затронуты» щит пульсирует
  const tSafe = at(L, 'c3_09', 'переписка', 0, 1e9); S.sh.scale.setScalar(0.9 * (ct > tSafe && ct < tSafe + 3 ? 1 + 0.1 * Math.sin((ct - tSafe) * 8) : 1));
  S.nodes.forEach((n, j) => { const hit = j < 3 && ((ct * 0.09 + 0.3) % 1) > [0.35, 0.6, 0.85][j]; n.userData.scr.material.color.setHex(j === 3 ? 0x9fe8ff : hit ? 0xff8f87 : 0x9fe8ff); });
  const tOff = at(L, 'c3_12', 'отключила', 0, 1e9); S.vendor.userData.scr.material.color.setHex(ct > tOff ? 0x555566 : 0xffd36b);
  let tg;
  if (i === 4) { orbit(S.cam, v3(-1, 3.8, -5), lerp(8, 6.5, clamp(L.lt / 8)), 0.2, 0.1); tg = v3(-1, 3.8, -5); }
  else if (i === 5) { orbit(S.cam, v3(5, 1.6, -1.4), 7, 0.5 - L.lt * 0.04, 0.15); tg = v3(5, 1.6, -1.4); }
  else if (i === 6) { orbit(S.cam, v3(-5.6, 1, 6.2), 9, -0.3 + L.lt * 0.03, 0.22); tg = v3(-5.6, 1, 6.2); }
  else if (i === 8) { orbit(S.cam, v3(5.5, 1.5, -1.3), 8, 0.2 + L.lt * 0.02, 0.2); tg = v3(5.5, 1.5, -1.3); }
  else tg = camFor(L, CAMS3, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(3, 'Агенты-взломщики', L);
  onLine(L, 3, (t, a, b) => fact('КТО ВЗЛАМЫВАЛ', 'Стартап Cathedral: четверо бывших сотрудников DOGE, $160 млн инвестиций', 110, 230, t, at(L, 'c3_03', 'исследователи', 0, a), b, { w: 880, color: LAV }));
  onLine(L, 5, (t, a, b) => bigNum(12, ' часов', 'меньше — по словам Cathedral', 120, 400, t, at(L, 'c3_05', 'двенадцати', 0, a), b, { from: 48 }));
  onLine(L, 7, (t, a, b) => fact('ВХОД', 'Не через Claude, а через стороннее ПО для администрирования и продаж', 110, 230, t, a, b, { w: 880, color: '#c9a227' }));
  onLine(L, 9, (t, a, b) => checklist([[false, 'Продажи, HR, IT — ограниченно'], [true, 'Чаты с Claude — нет'], [true, 'Исходный код — нет'], [true, 'Веса моделей — нет']], 110, 220, t, at(L, 'c3_09', 'добрались', 0, a), b, { w: 760 }));
  onLine(L, 10, (t, a, b) => checklist([[null, 'Cathedral: доступ шире'], [null, 'Anthropic: последствия преувеличены, правила нарушены']], 110, 220, t, a, b, { w: 940 }));
  onLine(L, 14, (t, a, b) => punch('ЗАЩИТА СО СКОРОСТЬЮ АГЕНТОВ', 960, 300, t, at(L, 'c3_14', 'защищаться', 0, a), b, { size: 66, bg: SKY, rot: 0 }));
  onLine(L, 3, (t, a, b) => source('Decrypt / Washington Post, 26.10', t, a, b));
}

// ═══════════════ 4. Anthropic идёт на биржу ═══════════════
const S4 = (() => {
  const S = newScene({ bg: 0xf0dcb4, floorY: 0, key: [-5, 13, 8], shadowSize: 16 }); S.ground.material.color.set(0xfaf3e6);
  const tb = P.tickerBoard('ANT'); tb.position.set(-2.6, 4.2, -3); S.scene.add(tb);
  const bl = P.bell(); bl.position.set(3.8, 0.3, -1.5); S.scene.add(bl);
  const ch = P.barChart([1.16, 16.3], C.mint, 1.3); ch.g.position.set(-3.6, 0, 1.2); ch.g.scale.set(1, 0.28, 1); S.scene.add(ch.g);
  const q = P.barChart([4.7, 11.6], C.butter, 1.0); q.g.position.set(1.2, 0, 2.8); q.g.scale.set(1, 0.28, 1); S.scene.add(q.g);
  const a = P.ant(); a.position.set(-0.4, 0, 3.6); a.scale.setScalar(1.3); S.scene.add(a);
  const stacks = []; for (let i = 0; i < 5; i++) { const s = P.coinStack(4 + i * 2); s.position.set(-6 + i * 0.9, 0, 4.4); S.scene.add(s); stacks.push(s); }
  const paper = new THREE.Group(); S.scene.add(paper); paper.position.set(4.6, 0, 3.4);
  const pp = rbox(2.2, 0.08, 3, matte(0xfdfbf6), 0.03); pp.position.y = 0.04; paper.add(pp);
  const hdr = textSprite('S-1', { size: 90, color: '#2b2a3a', bg: null, scale: 1 }); hdr.position.set(0, 0.25, -0.9); paper.add(hdr);
  const warn = textSprite('РИСКИ', { size: 60, color: '#ffffff', bg: '#e8706a', scale: 0.8 }); warn.position.set(0, 0.6, 0.6); paper.add(warn);
  P.shadowAll(paper);
  return { ...S, tb, bl, ch, q, a, stacks, paper, warn };
})();
const CAMS4 = [
  (cam, k) => { dolly(cam, v3(-1, 2, 0.5), 17, 15, 0.3, 0.05, 0.3, 0.24, k); return v3(-1, 2, 0.5); },
  (cam, k) => { dolly(cam, v3(-2.6, 4, -3), 8, 7, -0.2, 0.1, 0.05, 0.02, k); return v3(-2.6, 4, -3); },
  (cam, k) => { dolly(cam, v3(3.8, 1.6, -1.5), 7, 6, 0.6, 0.3, 0.15, 0.1, k); return v3(3.8, 1.6, -1.5); },
  (cam, k) => { dolly(cam, v3(-0.4, 0.7, 3.6), 6, 5, 0.9, 0.6, 0.2, 0.15, k); return v3(-0.4, 0.7, 3.6); },
];
export function c4(ct, L) {
  const S = S4; const i = L.i;
  S.ch.setK(seg(ct, at(L, 'c4_04', 'выручка', 0, 1e9) - 0.3, at(L, 'c4_04', 'выручка', 0, 1e9) + 2.5));
  S.q.setK(seg(ct, at(L, 'c4_06', 'втором', 0, 1e9) - 0.3, at(L, 'c4_06', 'втором', 0, 1e9) + 2));
  S.bl.rotation.z = Math.sin(ct * 6) * 0.03 * (ct > at(L, 'c4_02', 'nasdaq', 0, 1e9) && ct < at(L, 'c4_02', 'nasdaq', 0, 1e9) + 3 ? 1 : 0);
  S.a.position.y = Math.abs(Math.sin(ct * 3)) * 0.12; S.a.rotation.y = Math.sin(ct * 0.7) * 0.4;
  S.warn.scale.copy(S.warn.userData.base).multiplyScalar(i === 14 || i === 15 ? 1 + 0.08 * Math.sin(ct * 6) : 1);
  let tg;
  if (i === 2) { orbit(S.cam, v3(-0.4, 0.8, 3.6), 5, 0.7 - L.lt * 0.05, 0.2); tg = v3(-0.4, 0.8, 3.6); }
  else if (i === 3 || i === 4) { orbit(S.cam, v3(-3.6, 1.6, 1.2), 10, 0.25, 0.18); tg = v3(-3.6, 1.6, 1.2); }
  else if (i === 5) { orbit(S.cam, v3(1.2, 1.2, 2.8), 8, 0.4, 0.2); tg = v3(1.2, 1.2, 2.8); }
  else if (i === 14 || i === 15) { orbit(S.cam, v3(4.6, 0.3, 3.4), 6, 0.3 + L.lt * 0.03, 0.75); tg = v3(4.6, 0.3, 3.4); }
  else tg = camFor(L, CAMS4, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(4, 'Anthropic идёт на биржу', L);
  onLine(L, 2, (t, a, b) => { fact('ЗАЯВКА S-1 · 26 ОКТЯБРЯ', 'Nasdaq, тикер ANT', 110, 230, t, at(L, 'c4_02', 'заявку', 0, a), b, { w: 640, color: LAV }); source('TNW, BetaNews, Shacknews', t, a, b); });
  onLine(L, 4, (t, a, b) => bigNum(16.3, ' млрд $', 'выручка за I полугодие 2026 (год назад ~1,2 млрд)', 120, 400, t, at(L, 'c4_04', 'шестнадцать', 0, a), b, { dec: 1, color: MINT }));
  onLine(L, 6, (t, a, b) => bigNum(11.6, ' млрд $', 'выручка только во II квартале — первая операционная прибыль', 120, 400, t, at(L, 'c4_06', 'одиннадцать', 0, a), b, { dec: 1 }));
  onLine(L, 8, (t, a, b) => { bigNum(80.7, ' млрд $', 'чистый убыток — почти весь бумажный (переоценка займов)', 120, 400, t, at(L, 'c4_08', 'восемьдесят', 0, a), b, { dec: 1, color: RED }); });
  onLine(L, 11, (t, a, b) => bigNum(11900, '+', 'клиентов платят от $100 тыс. в год (~250 — больше $10 млн)', 120, 400, t, at(L, 'c4_11', 'одиннадцати', 0, a), b, { from: 950 }));
  onLine(L, 12, (t, a, b) => checklist([[null, 'Google — от $114,5 млрд'], [null, 'Amazon — от $110 млрд']], 110, 220, t, a, b, { w: 700 }));
  onLine(L, 14, (t, a, b) => checklist([[true, 'Корпорация общественной пользы'], [null, 'Большинство совета выбирает траст'], [null, 'У основателей — 50,1% голосов']], 110, 220, t, a, b, { w: 880 }));
  onLine(L, 15, (t, a, b) => fact('РАЗДЕЛ РИСКОВ', 'В тестах модели сопротивлялись отключению и вели себя «похоже на шантаж»', 110, 230, t, a, b, { w: 900 }));
  onLine(L, 17, (t, a, b) => fact('НЕОФИЦИАЛЬНО · WSJ', 'Размещение может пройти в середине ноября. Компания сроки не называла', 110, 230, t, at(L, 'c4_17', 'wall', 0, a), b, { w: 900, color: '#9a98aa' }));
}

// ═══════════════ 5. Genie 4 ═══════════════
const S5 = (() => {
  const S = newScene({ bg: 0xbfe3f0, floorY: -4, key: [5, 14, 8], shadowSize: 12 });
  const isl = P.worldIsland(); isl.position.y = 0.5; S.scene.add(isl);
  const rings = P.soundRings(4); rings.g.position.set(0, 1.3, 0); rings.g.rotation.x = Math.PI / 2; S.scene.add(rings.g);
  const rn = P.rain(140, 6); S.scene.add(rn.g);
  const fr = P.frameRect(3.4, 1.9); fr.position.set(0, 2.2, 4.2); S.scene.add(fr);
  const gp = P.gamepad(); gp.position.set(3.6, -1.2, 4.2); gp.rotation.x = 0.5; S.scene.add(gp);
  const clouds = [[-4, 4.5, -3, 1.2], [4, 5, -2, 1.5], [0, 6, -5, 1.8]].map(([x, y, z, s]) => { const c = cloud(); c.position.set(x, y, z); c.scale.setScalar(s); S.scene.add(c); return c; });
  const glitchBox = rbox(0.5, 0.5, 0.5, gloss(C.pink), 0.1); glitchBox.position.set(1.4, 1.1, 1.0); S.scene.add(glitchBox);
  const wm = textSprite('SynthID', { size: 60, color: '#ffffff', bg: 'rgba(43,42,58,0.7)', scale: 0.9 }); wm.position.set(2.2, 3.6, 1.5); S.scene.add(wm);
  return { ...S, isl, rings, rn, fr, gp, clouds, glitchBox, wm };
})();
const CAMS5 = [
  (cam, k) => { dolly(cam, v3(0, 1, 0), 15, 12, 0.6, -0.1, 0.35, 0.28, k); return v3(0, 1, 0); },
  (cam, k) => { dolly(cam, v3(0.3, 1.0, 1.4), 4.5, 3.8, 0.3, 0.8, 0.12, 0.1, k); return v3(0.3, 1.0, 1.4); },
  (cam, k) => { dolly(cam, v3(0, 2, 3), 9, 8, -0.4, -0.1, 0.1, 0.06, k); return v3(0, 2, 3); },
  (cam, k) => { dolly(cam, v3(0, 0.5, 0), 13, 14, 2.2, 2.8, 0.5, 0.45, k); return v3(0, 0.5, 0); },
];
export function c5(ct, L) {
  const S = S5; const i = L.i;
  S.isl.rotation.y = ct * 0.08; S.isl.position.y = 0.5 + Math.sin(ct * 0.8) * 0.08;
  const hero = S.isl.userData.hero; hero.position.x = 0.3 + Math.sin(ct * 0.6) * 0.5; hero.rotation.y = Math.cos(ct * 0.6) > 0 ? Math.PI / 2 : -Math.PI / 2;
  S.rings.tick(ct); S.rings.g.visible = ct > at(L, 'c5_03', 'звук', 0, 1e9);
  const tRain = at(L, 'c5_07', 'дождь', 0, 1e9); S.rn.tick(ct, clamp((ct - tRain) / 0.8)); S.rn.g.visible = ct > tRain;
  const tObj = at(L, 'c5_07', 'предмет', 0, 1e9); popScale(S.glitchBox, ct, tObj, 0.8, new THREE.Vector3(1, 1, 1));
  const tPl = at(L, 'c5_09', 'плыть', 0, 1e9); if (ct > tPl) { const w = Math.sin(ct * 3) * 0.25; S.glitchBox.scale.set(1 + w, 1 - w * 0.6, 1 + w * 0.3); S.glitchBox.material.color.setHSL((ct * 0.2) % 1, 0.6, 0.75); }
  S.fr.visible = i === 6 || i === 2; S.wm.visible = i >= 10;
  S.clouds.forEach((c, j) => (c.position.x += Math.sin(ct * 0.2 + j) * 0.002));
  const tg = camFor(L, CAMS5, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(5, 'Genie 4: миры со звуком', L);
  onLine(L, 1, (t, a, b) => source('DeepMind (через Xenospectrum, Pillitteri), 27.10', t, a, b));
  onLine(L, 3, (t, a, b) => checklist([[true, 'Ходишь внутри сцены'], [true, 'Мир дорисовывается на ходу'], [true, 'Звук рождается вместе с картинкой']], 110, 220, t, a, b, { w: 820 }));
  onLine(L, 5, (t, a, b) => checklist([[null, 'Genie 3 · август 2025'], [null, '720p · 24 кадра/с'], [null, 'Память ~1 минута, без звука']], 110, 220, t, a, b, { w: 720 }));
  onLine(L, 7, (t, a, b) => { punch('«ПУСТЬ ПОЙДЁТ ДОЖДЬ»', 760, 300, t, at(L, 'c5_07', 'дождь', 0, a) - 0.3, b, { size: 70, bg: SKY }); });
  onLine(L, 9, (t, a, b) => checklist([[false, 'Объекты «плывут»'], [false, 'Читаемый текст'], [false, 'Много персонажей'], [null, 'Пока — только тестерам']], 110, 220, t, a, b, { w: 720 }));
  onLine(L, 11, (t, a, b) => punch('ВИДЕО → МЕСТО, КУДА МОЖНО ЗАЙТИ', 960, 300, t, at(L, 'c5_11', 'перестаёт', 0, a), b, { size: 62, bg: LAV, rot: 0 }));
}

// ═══════════════ 6. xAI и соседи ═══════════════
const S6 = (() => {
  const S = newScene({ bg: 0xcfe2f2, floorY: 0, key: [-7, 13, 7], shadowSize: 22 });
  S.ground.material.color.set(0xd7e6c4);
  const plant = P.turbineHall(6); plant.g.position.set(0, 0, -9); S.scene.add(plant.g);
  const fence = new THREE.Group(); S.scene.add(fence); for (let i = 0; i < 24; i++) { const p = rbox(0.08, 1.6, 0.08, metal(0x9aa0ab), 0.02); p.position.set(-11.5 + i, 0.8, -5.5); fence.add(p); } const w = rbox(24, 1.4, 0.02, matte(0x9aa0ab, { transparent: true, opacity: 0.35 }), 0.01); w.position.set(0, 0.8, -5.5); fence.add(w);
  const houses = []; [[-7, 2], [-3.5, 2.6], [0, 2.2], [3.5, 2.7], [7, 2.1], [-5, 6.5], [-1.5, 7], [2, 6.6], [5.5, 7]].forEach(([x, z], j) => { const h = P.house([0xfdf3e3, 0xe9f1ff, 0xfff0f3, 0xf0fbf3][j % 4], [C.coral, C.sky, C.lav, C.sage][j % 4]); h.position.set(x, 0, z); h.rotation.y = Math.PI + (hash(j) - 0.5) * 0.2; S.scene.add(h); houses.push(h); });
  const rings = P.soundRings(5, C.coral); rings.g.position.set(0, 2.2, -8); rings.g.rotation.x = Math.PI / 2; rings.g.scale.setScalar(3); S.scene.add(rings.g);
  const env = P.envelope(); env.position.set(0.4, 2.3, 4.3); env.scale.setScalar(0.9); S.scene.add(env);
  const sign = P.saleSign(); sign.position.set(1.5, 0, 3.6); S.scene.add(sign);
  const doc = new THREE.Group(); S.scene.add(doc); doc.position.set(-0.4, 2.4, 4.4);
  const d1 = rbox(1.2, 1.6, 0.03, matte(0xfdfbf6), 0.03); doc.add(d1);
  const t1 = textSprite('ОТКАЗ ОТ ИСКА', { size: 42, color: '#ffffff', bg: '#e8706a', scale: 0.55 }); t1.position.set(0, 0.4, 0.04); doc.add(t1);
  for (let i = 0; i < 5; i++) { const l = rbox(0.9, 0.05, 0.01, matte(0xcfcbd9), 0.01); l.position.set(0, 0.05 - i * 0.2, 0.03); doc.add(l); }
  P.shadowAll(doc);
  const smoke = []; plant.stacks.forEach((s, j) => { for (let k = 0; k < 3; k++) { const p = sphere(0.45, matte(0xd6d4dc, { transparent: true, opacity: 0.8 }), 12); S.scene.add(p); smoke.push({ p, j, k }); } });
  return { ...S, plant, houses, rings, env, sign, doc, smoke };
})();
const CAMS6 = [
  (cam, k) => { dolly(cam, v3(0, 1.5, -1), 26, 22, 0.2, -0.05, 0.38, 0.3, k); return v3(0, 1.5, -1); },
  (cam, k) => { dolly(cam, v3(0, 3, -9), 14, 12, -0.5, -0.2, 0.2, 0.14, k); return v3(0, 3, -9); },
  (cam, k) => { dolly(cam, v3(0, 1.4, 2.6), 9, 8, 0.4, 0.1, 0.15, 0.1, k); return v3(0, 1.4, 2.6); },
  (cam, k) => { dolly(cam, v3(0, 0.5, 3), 16, 15, 3.0, 2.7, 0.3, 0.25, k); return v3(0, 0.5, 3); },
];
export function c6(ct, L) {
  const S = S6; const i = L.i;
  S.rings.tick(ct * 1.5);
  S.smoke.forEach(({ p, j, k }) => { const ph = (ct * 0.25 + k / 3 + j * 0.13) % 1; const s = S.plant.stacks[j]; p.position.set(s.position.x + ph * 1.5, -9 + 0 + s.position.y + 1.8 + ph * 3, s.position.z - 9 + 0); p.position.z = -9.8; p.scale.setScalar(0.5 + ph * 1.6); p.material.opacity = (1 - ph) * 0.75; });
  S.houses.forEach((h, j) => { const shake = Math.sin(ct * 30 + j) * 0.01; h.position.y = shake; });
  const tL = at(L, 'c6_05', 'письма', 0, 1e9); popScale(S.env, ct, tL - 0.2, 0.8, new THREE.Vector3(0.9, 0.9, 0.9)); S.env.visible = ct > tL - 0.2 && ct < at(L, 'c6_05', 'условие', 0, 1e9) + 0.3;
  const tD = at(L, 'c6_05', 'условие', 0, 1e9); popScale(S.doc, ct, tD, 0.8, new THREE.Vector3(1, 1, 1)); S.doc.rotation.y = Math.sin(ct * 0.8) * 0.15;
  popScale(S.sign, ct, at(L, 'c6_05', 'купить', 0, 1e9), 0.8, new THREE.Vector3(1, 1, 1));
  let tg;
  if (i === 4 || i === 5 || i === 6) { orbit(S.cam, v3(0.3, 1.8, 4), lerp(7, 6, clamp(L.lt / 8)), 0.3 - L.lt * 0.02, 0.12); tg = v3(0.3, 2, 4.3); }
  else if (i === 7) { orbit(S.cam, v3(0, 2.5, -9), 13, -0.35 + L.lt * 0.03, 0.22); tg = v3(0, 2.5, -9); }
  else tg = camFor(L, CAMS6, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(6, 'xAI и соседи', L);
  onLine(L, 1, (t, a, b) => source('Mississippi Free Press, Mississippi Today', t, a, b));
  onLine(L, 3, (t, a, b) => bigNum(10000, '+', 'потенциальных участников коллективного иска о шуме и вибрации', 120, 400, t, at(L, 'c6_03', 'десяти', 0, a), b, { from: 0 }));
  onLine(L, 5, (t, a, b) => checklist([[true, 'Купим ваш дом'], [false, 'Но подпишите отказ от претензий']], 110, 220, t, at(L, 'c6_05', 'купить', 0, a), b, { w: 760 }));
  onLine(L, 7, (t, a, b) => fact('В ПИСЬМЕ', 'Цена не указана. xAI отрицает обвинения из иска', 110, 230, t, a, b, { w: 760, color: '#9a98aa' }));
  onLine(L, 8, (t, a, b) => bigNum(69, ' турбин', 'без разрешений на площадке (документы регулятора, 31.07)', 120, 400, t, at(L, 'c6_08', 'шестьдесят', 0, a), b, { color: RED }));
  onLine(L, 10, (t, a, b) => checklist([[null, 'Апрель — иск NAACP (чистый воздух)'], [null, 'Июнь — администрация на стороне xAI'], [null, 'Слушание перенесено, даты нет']], 110, 220, t, a, b, { w: 900 }));
  onLine(L, 12, (t, a, b) => punch('ОБЛАКО СТОИТ НА ЗЕМЛЕ', 960, 300, t, a + 0.5, b + 0.6, { size: 72, bg: INK, rot: 0 }));
}

// ═══════════════ 7. Unitree ═══════════════
const S7 = (() => {
  const S = newScene({ bg: 0xd6d2f0, floorY: 0, key: [6, 12, 7], shadowSize: 14 }); S.ground.material.color.set(0xf3f2fb);
  const r = P.humanoid(); r.position.set(-1.2, 0, 0.6); r.scale.setScalar(1.4); S.scene.add(r);
  const dog = P.robotDog(); dog.position.set(1.8, 0, 1.6); dog.scale.setScalar(1.3); S.scene.add(dog);
  const tag = P.priceTag(); tag.position.set(-1.2, 3.6, 1.2); S.scene.add(tag);
  // график акций: «американские горки»
  const pts = [[0, 1.0], [1, 2.2], [2, 1.0], [3, 0.6], [4, 0.75], [5, 1.0], [6, 1.6], [7, 2.0]].map(([x, y]) => v3(x * 1.1 - 3.8, y * 1.6, 0));
  const curve = new THREE.CatmullRomCurve3(pts);
  const line = new THREE.Mesh(new THREE.TubeGeometry(curve, 120, 0.09, 10), new THREE.MeshBasicMaterial({ color: 0x2fae86, toneMapped: false })); line.position.set(0, 0.3, -4.5); S.scene.add(line);
  const board = rbox(9.6, 4.6, 0.2, gloss(0xffffff), 0.2); board.position.set(0, 2.4, -4.8); board.receiveShadow = true; S.scene.add(board);
  const cart = rbox(0.5, 0.35, 0.4, gloss(C.coral), 0.1); S.scene.add(cart);
  const ped = puck(2.2, 0.3, gloss(0xffffff)); ped.position.set(-1.2, 0.15, 0.6); S.scene.add(ped);
  const lim = textSprite('+20% ЛИМИТ', { size: 54, color: '#ffffff', bg: '#e8706a', scale: 0.8 }); lim.position.set(2.2, 4.4, -4.4); S.scene.add(lim);
  return { ...S, r, dog, tag, curve, line, cart, lim };
})();
const CAMS7 = [
  (cam, k) => { dolly(cam, v3(0, 1.8, 0), 14, 12, 0.45, 0.15, 0.22, 0.16, k); return v3(0, 1.8, 0); },
  (cam, k) => { dolly(cam, v3(-1.2, 2.2, 0.6), 6, 5, -0.3, 0.1, 0.12, 0.08, k); return v3(-1.2, 2.2, 0.6); },
  (cam, k) => { dolly(cam, v3(0, 2.2, -4.5), 10, 9, -0.2, 0.15, 0.05, 0.03, k); return v3(0, 2.2, -4.5); },
  (cam, k) => { dolly(cam, v3(1.8, 0.8, 1.6), 5, 4.5, 0.9, 1.3, 0.15, 0.12, k); return v3(1.8, 0.8, 1.6); },
];
export function c7(ct, L) {
  const S = S7; const i = L.i;
  P.poseWalk(S.r, ct, 0.35); S.r.rotation.y = Math.sin(ct * 0.4) * 0.5;
  S.dog.userData.legs.forEach((l, j) => (l.rotation.z = Math.sin(ct * 6 + (j % 2 ? Math.PI : 0) + (j > 1 ? Math.PI / 2 : 0)) * 0.3)); S.dog.position.y = Math.abs(Math.sin(ct * 6)) * 0.05;
  const p = (ct * 0.08) % 1; const pt = S.curve.getPoint(p); S.cart.position.set(pt.x, pt.y + 0.55, -4.3);
  S.lim.visible = i === 7; S.tag.visible = i >= 11; if (S.tag.visible) S.tag.rotation.y = Math.sin(ct) * 0.3;
  const tg = (i === 5 || i === 6 || i === 7) ? (orbit(S.cam, v3(0, 2.3, -4.5), 10.5, -0.15 + L.lt * 0.02, 0.06), v3(0, 2.3, -4.5)) : camFor(L, CAMS7, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg) });
  clear2d(); common(7, 'Unitree: роботы в цене', L);
  onLine(L, 2, (t, a, b) => source('The Edge Malaysia, Digital Today', t, a, b));
  onLine(L, 4, (t, a, b) => checklist([[true, 'Выручка +70% (~$100 млн за квартал)'], [false, 'Прибыль −17,4% (вдвое ниже ожиданий)'], [null, 'Исследования ×3,5']], 110, 220, t, at(L, 'c7_04', 'выручка', 0, a), b, { w: 900 }));
  onLine(L, 6, (t, a, b) => { bigNum(60, '%+', 'рост акций за пару недель перед отчётом', 120, 400, t, at(L, 'c7_06', 'шестьдесят', 0, a), at(L, 'c7_06', 'основатель', 0, b), { color: MINT }); fact('ВАН СИНСИН, ОСНОВАТЕЛЬ', 'Прорыв физического ИИ — через 1–3 года', 110, 230, t, at(L, 'c7_06', 'основатель', 0, b), b, { w: 820, color: LAV }); });
  onLine(L, 8, (t, a, b) => checklist([[null, '19 августа — выход на биржу'], [false, 'Падение почти на 55%'], [true, '23 октября — +20% за день']], 110, 220, t, a, b, { w: 820 }));
  onLine(L, 10, (t, a, b) => fact('9 МЕСЯЦЕВ', 'Выручка +56%, прибыль почти ×4 (с разовым эффектом прошлого года)', 110, 230, t, a, b, { w: 900, color: SKY }));
  onLine(L, 12, (t, a, b) => bigNum(16000, ' $', 'человекоподобный G1', 120, 400, t, at(L, 'c7_12', 'шестнадцати', 0, a), b, { from: 1000 }));
}

// ═══════════════ 8. Starship ═══════════════
const S8 = (() => {
  const S = newScene({ bg: 0xb9d4ee, floorY: 0, key: [10, 18, 12], shadowSize: 24, fov: 30 });
  S.ground.material.color.set(0xe6dccb);
  const tw = P.tower(); tw.position.set(0, 0, 0); S.scene.add(tw);
  const booster = P.stage(14, 1.1, 0xd7dbe3); booster.position.set(6.4, 0.5, 0); S.scene.add(booster);
  const ship = P.stage(9, 1.1, 0xe4e7ee, true); ship.position.set(6.4, 15, 0); S.scene.add(ship);
  const fl = P.flame(22); S.scene.add(fl.g);
  const pl = P.plume(18); S.scene.add(pl.g);
  const mount = rbox(4, 1, 4, matte(0xc9c3b8), 0.1); mount.position.set(-12, 0.5, 6); S.scene.add(mount);
  const shipT = P.stage(9, 1.1, 0xe4e7ee, true); shipT.position.set(-12, 1.0, 6); S.scene.add(shipT);
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(200, 60), new THREE.MeshStandardMaterial({ color: 0x9fd0e6, roughness: 0.2 })); sea.rotation.x = -Math.PI / 2; sea.position.set(0, 0.02, -45); S.scene.add(sea);
  const towers2 = []; for (let i = 0; i < 6; i++) { const t2 = P.tower(); t2.scale.setScalar(0.35); t2.position.set(-30 + i * 5, 0, -18); S.scene.add(t2); towers2.push(t2); }
  return { ...S, tw, booster, ship, fl, pl, shipT, towers2 };
})();
const CAMS8 = [
  (cam, k) => { dolly(cam, v3(3, 10, 0), 52, 46, 0.6, 0.35, 0.1, 0.08, k); return v3(3, 10, 0); },
  (cam, k) => { dolly(cam, v3(3, 18, 0), 22, 20, 0.9, 1.2, 0.05, 0.12, k); return v3(3, 18, 0); },
  (cam, k) => { dolly(cam, v3(6, 6, 0), 30, 28, -0.4, -0.1, 0.05, 0.02, k); return v3(6, 6, 0); },
  (cam, k) => { dolly(cam, v3(0, 12, 0), 60, 56, 1.6, 1.3, 0.25, 0.2, k); return v3(0, 12, 0); },
];
export function c8(ct, L) {
  const S = S8; const i = L.i;
  const arms = S.tw.userData.arms;
  // по умолчанию: ступени стоят у башни; на «поймать» — корабль спускается, «палочки» смыкаются
  let shipY = 15, boostY = 0.5, armK = 0.25, fireK = 0, testFire = 0;
  if (i === 2 || i === 4) { const k = clamp(L.lt / Math.max(3, L.line.dur)); shipY = lerp(34, 15.6, easeOut(k)); armK = k > 0.75 ? lerp(0.25, 0.0, (k - 0.75) * 4) : 0.25; fireK = k < 0.8 ? 0.8 : 0; }
  if (i === 5) { testFire = 1; }
  arms.forEach((a, j) => (a.rotation.y = (j ? -1 : 1) * armK));
  S.ship.position.y = shipY; S.booster.position.y = boostY;
  S.fl.g.position.set(6.4, shipY - 0.1, 0); S.fl.tick(ct, fireK);
  // огневые испытания на стенде
  const tAll = at(L, 'c8_06', 'шесть', 0, 1e9), tOne = at(L, 'c8_06', 'один', 0, 1e9);
  const fk = testFire ? (ct > tAll && ct < tOne - 0.3 ? 1 : ct > tOne ? 0.45 : 0) : 0;
  S.pl.g.position.set(-12, 0, 6); S.pl.tick(ct, fk > 0 ? 1 : 0);
  S.towers2.forEach((t2, j) => (t2.visible = i >= 9 && i <= 10));
  let tg;
  if (i === 5) { orbit(S.cam, v3(-12, 4, 6), 24, 0.6 + L.lt * 0.02, 0.12); tg = v3(-12, 4, 6); }
  else if (i === 2 || i === 4) { orbit(S.cam, v3(4, 17, 0), 34, 0.7 + L.lt * 0.015, 0.06); tg = v3(4, 17, 0); }
  else if (i === 9 || i === 10) { orbit(S.cam, v3(-18, 4, -16), 34, 0.3, 0.2); tg = v3(-18, 4, -16); }
  else tg = camFor(L, CAMS8, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg, 0.0003, 0.005) });
  clear2d(); common(8, 'Starship: поймать обе ступени', L);
  onLine(L, 3, (t, a, b) => checklist([[true, 'Ускоритель: пойман 3 раза'], [false, 'Корабль: ни разу'], [null, 'Flight 15: обе ступени']], 110, 220, t, a, b, { w: 760 }));
  onLine(L, 5, (t, a, b) => quote('Первый раз, когда орбитальная ракета будет полностью возвращена', 'Илон Маск, 20.10 (пересказ)', 110, 230, t, at(L, 'c8_05', 'маск', 0, a), b, { w: 880 }));
  onLine(L, 6, (t, a, b) => { checklist([[true, '6 двигателей корабля — полное время'], [true, '1 двигатель — имитация схода с орбиты'], [true, '33 двигателя ускорителя — на стенде']], 110, 220, t, a, b, { w: 900 }); source('Space.com, 29.10', t, a, b); });
  onLine(L, 8, (t, a, b) => fact('КОГДА', 'Цель — ноябрь. Точной даты нет, нужна лицензия FAA', 110, 230, t, a, b, { w: 820, color: '#9a98aa' }));
  onLine(L, 10, (t, a, b) => checklist([[null, 'H1 2027 — раз в неделю'], [null, 'Конец 2027 — 2+ в неделю'], [null, 'Луизиана — 20+ башен']], 110, 220, t, a, b, { w: 760 }));
  onLine(L, 12, (t, a, b) => bigNum(10, '× Falcon 9', 'пропускной способности Starlink за один полёт (по словам Маска)', 120, 400, t, at(L, 'c8_12', 'десять', 0, a), b, { from: 1, size: 150 }));
}

// ═══════════════ 9. Итоги ═══════════════
export function c9(ct, L) {
  const S = S0; S.turn.rotation.y = -ct * 0.12;
  const tg = camFor(L, CAMS0, S, ct);
  render(S.scene, S.cam, { time: ct, ...dofOf(S.cam, tg, 0.0005) });
  clear2d(); badge(0, TOTAL, 'Итоги недели', ct, 0.4);
  chapterCard(0, 'Итоги недели', ct, 0.05, L.intro);
  if (L.i >= 0) speaker(L.line.sp, L.lt > 0 && L.lt < L.line.vdur, ct, L.intro);
  onLine(L, 1, (t, a, b) => checklist([[null, 'Серверы грабят на трассах'], [null, 'ИИ и гипотеза 1999 года — ждём проверки']], 110, 220, t, a, b, { w: 900 }));
  onLine(L, 2, (t, a, b) => checklist([[null, 'Агенты прошли за полдня'], [null, 'Anthropic идёт на биржу']], 110, 220, t, a, b, { w: 900 }));
  onLine(L, 3, (t, a, b) => checklist([[null, 'Миры со звуком'], [null, 'Дата-центр против соседей'], [null, 'Роботы на бирже'], [null, 'Ракету ловят целиком']], 110, 220, t, a, b, { w: 900 }));
  onLine(L, 4, (t, a, b) => fact('ВОПРОС В КОММЕНТАРИИ', 'Ты бы поверил доказательству от нейросети до проверки людьми?', 110, 230, t, at(L, 'c9_04', 'главный', 0, a), b + 2, { w: 900, color: LAV }));
  onLine(L, 5, (t, a, b) => { punch('ПОДПИШИСЬ', 760, 330, t, at(L, 'c9_05', 'подпишись', 0, a), b + 3, { size: 110, bg: RED }); punch('СПАСИБО ЗА ЛАЙК ♥', 760, 520, t, at(L, 'c9_05', 'спасибо', 0, a), b + 3, { size: 64, bg: INK, rot: 0.03 }); });
}

// ═══════════════ Обложка ═══════════════
window.__thumb = () => {
  const S = S1; S.tr.g.position.set(0, 0, 1.5); S.tr.setOpen(0.8); S.esc.visible = true; S.esc.position.set(-9.5, 0, 3.8); S.esc.rotation.set(0, 0.9, 0.12);
  S.thief.visible = true; S.thief.position.set(-8.5, 0, -2.6); S.thief.rotation.y = 0.5; S.pin.visible = true; S.pin.position.set(-1.5, 4.6, 1.5);
  S.env.visible = S.hk.visible = false;
  orbit(S.cam, v3(4.5, 2.6, 1.5), 21, 0.75, 0.2);
  render(S.scene, S.cam, { time: 1, focus: 19, aperture: 0.0004, vig: 0.35 });
  clear2d();
  const g = ctx.createLinearGradient(1920, 0, 760, 0); g.addColorStop(0, 'rgba(25,22,40,0.88)'); g.addColorStop(1, 'rgba(25,22,40,0)');
  ctx.fillStyle = g; ctx.fillRect(700, 0, 1220, 1080);
  ctx.textAlign = 'right';
  ctx.font = '900 132px "Rubik"'; ctx.fillStyle = '#ffffff'; ctx.fillText('СЕРВЕРЫ ДЛЯ ИИ', 1850, 280);
  ctx.font = '900 132px "Rubik"'; ctx.fillStyle = '#ffdc7a'; ctx.fillText('ГРАБЯТ', 1850, 420);
  ctx.save(); ctx.translate(1850, 470); ctx.rotate(-0.03); ctx.beginPath(); ctx.roundRect(-760, 0, 760, 150, 28); ctx.fillStyle = '#e8706a'; ctx.fill();
  ctx.font = '900 92px "Rubik"'; ctx.fillStyle = '#fff'; ctx.fillText('НА ТРАССЕ', -40, 110); ctx.restore();
  ctx.font = '800 58px "Rubik"'; ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fillText('+ ещё 7 новостей недели', 1850, 760);
  ctx.textAlign = 'left';
};
