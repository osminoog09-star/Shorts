// Дополнительные сцены n1–n9 (расширение до ~10 минут). Тайминги берутся из слов озвучки: cue(id, 'слово').
import { render, clear2d, ctx, title, pill, counter, iris, project, W, H,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { THREE, C, CSS, matte, gloss, metal, gear, shadowAll, v3, orbit, newScene, rbox, sphere, cyl, puck, train, axle, textSprite, popScale,
  lump, amphora, bust, boat, diver, waves, cloud } from './kit.js';

export const VO = 0.6;
// время слова в локальном времени сцены (с учётом входа VO); nth — какое по счёту совпадение
export function cue(id, word, nth = 0) {
  const ws = (window.WORDS && window.WORDS[id]) || [];
  const w = word.toLowerCase();
  let k = 0;
  for (const x of ws) { if (x.w.toLowerCase().replace(/[«»"',.!?:;—]/g, '').startsWith(w)) { if (k === nth) return VO + x.start; k++; } }
  return 9999;
}
const dofOpts = (cam, tg, ap = 0.001) => ({ focus: cam.position.distanceTo(tg), aperture: ap, maxblur: 0.01 });
const PURPLE = '#7a63e6';

// Статуя «юноша» (стилизация)
function youth(mat) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.35, 1.3, 8, 20), mat); body.position.y = 1.2; g.add(body);
  const head = sphere(0.28, mat); head.position.y = 2.25; g.add(head);
  const armR = new THREE.Mesh(new THREE.CapsuleGeometry(0.09, 0.9, 6, 12), mat); armR.position.set(0.45, 2.0, 0.1); armR.rotation.z = -2.4; g.add(armR);
  const armL = new THREE.Mesh(new THREE.CapsuleGeometry(0.09, 0.8, 6, 12), mat); armL.position.set(-0.42, 1.2, 0); armL.rotation.z = 0.15; g.add(armL);
  for (const s of [-1, 1]) { const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.9, 6, 12), mat); leg.position.set(s * 0.17, 0.3, 0); g.add(leg); }
  const base = puck(0.55, 0.2, matte(C.cream)); base.position.y = -0.3; g.add(base);
  return shadowAll(g);
}
function navyShip() {
  const g = new THREE.Group();
  const hull = rbox(5.6, 0.9, 1.4, gloss(0x8d96b8), 0.3); g.add(hull);
  const deck = rbox(4.2, 0.5, 1.1, matte(C.cream), 0.15); deck.position.set(-0.2, 0.65, 0); g.add(deck);
  const fun = cyl(0.25, 1.1, gloss(C.coral), 20); fun.position.set(0.4, 1.4, 0); g.add(fun);
  const mast = cyl(0.05, 2.4, gloss(C.white), 12); mast.position.set(-1.5, 1.8, 0); g.add(mast);
  return shadowAll(g);
}

// ───────── n1. Экспедиция 1900–1901 и находки ─────────
const N1 = (() => {
  const S = newScene({ bg: 0xd8eaf3, floor: false, key: [6, 12, 6], shadowSize: 20 });
  const sea = waves(60, 40, 70, gloss(C.sea, { roughness: 0.25 })); S.scene.add(sea);
  const ship = navyShip(); ship.position.set(-2, 0.3, -1); S.scene.add(ship);
  const bt = boat(); bt.scale.setScalar(0.6); bt.position.set(2.2, 0.2, 1.4); S.scene.add(bt);
  // зал находок справа (на «полу» выше воды)
  const hall = new THREE.Group(); hall.position.set(16, 0, 0); S.scene.add(hall);
  const floor = rbox(16, 0.4, 7, matte(C.sand), 0.2); floor.position.y = -0.2; hall.add(floor);
  const yth = youth(metal(C.bronze)); yth.position.set(-4.5, 0.2, 0); hall.add(yth);
  const phil = bust(metal(C.bronze)); phil.scale.setScalar(0.8); phil.position.set(-1.7, 0.6, 0); hall.add(phil);
  const marbles = [];
  for (let i = 0; i < 6; i++) { const b = bust(matte(0xf4f1ee, { roughness: 0.45 })); b.scale.setScalar(0.55); b.position.set(0.8 + (i % 3) * 1.8, 0.45, (i < 3 ? -1.2 : 1.2)); hall.add(b); marbles.push(b); }
  return { ...S, sea, ship, bt, hall, yth, phil, marbles };
})();
export function n1(t) {
  const S = N1, id = 'n1';
  S.sea.userData.update(t, 0.8);
  const h = S.sea.userData.h;
  S.ship.position.y = 0.3 + h(-2, -1, t, 0.8); S.ship.rotation.z = (h(0, -1, t, 0.8) - h(-4, -1, t, 0.8)) * 0.12;
  S.bt.position.y = 0.15 + h(2.2, 1.4, t, 0.8); S.bt.rotation.z = (h(3.2, 1.4, t, 0.8) - h(1.2, 1.4, t, 0.8)) * 0.25;
  const tFinds = cue(id, 'находки') - 0.6;
  const pan = easeIO2(seg(t, tFinds, tFinds + 2.4));
  S.hall.position.y = lerp(-6, 0, easeOut(seg(t, tFinds - 0.4, tFinds + 1.4)));
  popScale(S.yth, t, cue(id, 'юноша') - 0.2, 0.9, v3(1, 1, 1));
  popScale(S.phil, t, cue(id, 'голова') - 0.2, 0.9, v3(0.8, 0.8, 0.8));
  S.marbles.forEach((m, i) => popScale(m, t, cue(id, 'тридцать') + i * 0.18, 0.9, v3(0.55, 0.55, 0.55)));
  const tg = v3(lerp(0, 15.5, pan), lerp(0.6, 1.0, pan), 0);
  orbit(S.cam, tg, lerp(15, 13, pan), lerp(0.55, 0.15, seg(t, 0, 40)) + pan * 0.2, lerp(0.28, 0.2, pan));
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#d8eaf3');
  title('первая большая подводная экспедиция', 140, 200, t, 0.8, { size: 72, align: 'left', out: tFinds - 0.3 });
  pill('с ноября 1900 · помогает флот Греции', 140, 300, t, cue(id, 'ноября'), { dot: CSS.sky, align: 'left', out: tFinds - 0.3 });
  pill('ныряльщик Георгиос Критикос погиб', 140, 395, t, cue(id, 'критикос'), { dot: CSS.coral, align: 'left', out: tFinds - 0.3 });
  pill('двое парализованы: декомпрессионная болезнь', 140, 490, t, cue(id, 'парализованы'), { dot: CSS.coral, align: 'left', out: tFinds - 0.3 });
  pill('лето 1901 — работы остановлены', 140, 585, t, cue(id, 'летом'), { dot: CSS.gold, align: 'left', out: tFinds - 0.3 });
  pill('«Юноша с Антикитеры» · ок. 340 г. до н. э.', 140, 150, t, cue(id, 'юноша'), { dot: CSS.gold, align: 'left' });
  pill('голова «Философа»', 140, 245, t, cue(id, 'голова'), { dot: CSS.gold, align: 'left' });
  pill('36 мраморных статуй', 140, 340, t, cue(id, 'тридцать'), { dot: CSS.white, align: 'left' });
}

// ───────── n2. Обломки и догадка Рема ─────────
const N2 = (() => {
  const S = newScene({ bg: C.cream, floorY: -1.6, key: [4, 10, 6] });
  const ped = rbox(5, 0.4, 3.5, matte(C.lav), 0.2); ped.position.y = -1.4; S.scene.add(ped);
  const pieces = [];
  for (let i = 0; i < 14; i++) {
    const p = lump({ r: 0.32 + hash(i) * 0.25, seed: i + 2 });
    const a = (i / 14) * Math.PI * 2; const r = 0.35 + hash(i * 5) * 0.5;
    p.userData.home = v3(Math.cos(a) * r * 1.3, 0.1 + Math.sin(a) * r * 0.8, (hash(i * 9) - 0.5) * 0.4);
    p.userData.out = v3(Math.cos(a) * (1.4 + hash(i * 3) * 1.8), -0.95, Math.sin(a * 1.7) * 1.2);
    p.rotation.set(hash(i) * 3, hash(i * 2) * 3, hash(i * 4) * 3);
    S.scene.add(p); pieces.push(p);
  }
  return { ...S, pieces };
})();
export function n2(t) {
  const S = N2, id = 'n2';
  const crack = easeIO2(seg(t, cue(id, 'трескалась') - 0.4, cue(id, 'трескалась') + 2.2));
  S.pieces.forEach((p, i) => {
    p.position.lerpVectors(p.userData.home, p.userData.out, crack);
    const bounce = crack > 0.98 ? 0 : Math.sin(crack * Math.PI) * 0.6;
    p.position.y += bounce;
  });
  const tg = v3(0, -0.2, 0);
  orbit(S.cam, tg, lerp(9, 11, easeIO2(seg(t, 0, 25))), t * 0.05 - 0.5, 0.32);
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('почему не поняли сразу?', 140, 200, t, 0.7, { size: 96, align: 'left', out: cue(id, 'сегодня') - 0.4 });
  pill('бронза высыхала и трескалась', 140, 300, t, cue(id, 'бронза'), { dot: CSS.patina, align: 'left', out: cue(id, 'сегодня') - 0.4 });
  const k = seg(t, cue(id, 'восемьдесят'), cue(id, 'восемьдесят') + 0.6);
  counter(k > 0 ? Math.round(82 * easeOut(k)) : '', 140, 330, { size: 220, align: 'left', color: PURPLE, alpha: clamp(k * 3) * (1 - seg(t, cue(id, 'первым') - 0.5, cue(id, 'первым'))) });
  pill('обломка · ≈ треть прибора', 140, 400, t, cue(id, 'трети') - 0.6, { align: 'left', out: cue(id, 'первым') - 0.5 });
  pill('Альберт Рем, филолог', 140, 150, t, cue(id, 'альберт'), { dot: CSS.gold, align: 'left' });
  title('«астрономический вычислитель»', 140, 300, t, cue(id, 'астрономический'), { size: 80, align: 'left', color: PURPLE });
}

// ───────── n3. Масштаб: футляр, шестерня 223, ручная работа ─────────
const N3 = (() => {
  const S = newScene({ bg: 0xeee8f6, floorY: -1.0, key: [4, 11, 6] });
  const table = rbox(9, 0.3, 6, matte(C.sand), 0.15); table.position.y = -0.85; S.scene.add(table);
  const caseM = rbox(3.4, 1.8, 0.9, gloss(0xd8a77a, { transparent: true, opacity: 0.35, depthWrite: false }), 0.08); caseM.position.set(0, 0.2, 0); caseM.castShadow = false; S.scene.add(caseM);
  const big = gear(223, 1.3 * 0.62, metal(C.bronze), { thick: 0.06, spokes: 4 }); big.position.set(0, 0.2, 0); big.scale.setScalar(1); S.scene.add(big);
  const ruler = rbox(3.6, 0.04, 0.4, matte(C.butter), 0.02); ruler.position.set(0, -0.68, 1.2); S.scene.add(ruler);
  for (let i = 0; i <= 34; i++) { const tk = rbox(0.015, 0.02, i % 5 === 0 ? 0.22 : 0.12, matte(C.deep), 0.005); tk.position.set(-1.7 + i * 0.1, -0.65, 1.1); S.scene.add(tk); }
  const file = new THREE.Group(); const blade = rbox(1.6, 0.05, 0.16, metal(0xb9bccb), 0.02); const handle = rbox(0.8, 0.18, 0.22, gloss(C.coral), 0.08); handle.position.x = 1.2; file.add(blade, handle); shadowAll(file); S.scene.add(file);
  return { ...S, caseM, big, file };
})();
export function n3(t) {
  const S = N3, id = 'n3';
  S.big.rotation.z = t * 0.08;
  const zoomT = cue(id, 'зубья') - 0.5;
  const macro = easeIO2(seg(t, zoomT, zoomT + 2.2));
  const fileOn = seg(t, cue(id, 'вручную') - 0.6, cue(id, 'вручную'));
  // напильник у кромки зубьев
  const edge = v3(Math.cos(0.9) * 0.8, 0.2 + Math.sin(0.9) * 0.8, 0.12);
  S.file.position.set(edge.x + 0.6 + Math.sin(t * 9) * 0.18 * fileOn, edge.y + 0.05, edge.z + 0.1); S.file.rotation.z = 0.9 - Math.PI / 2; S.file.visible = fileOn > 0;
  const tgA = v3(0, 0.1, 0), tgB = edge.clone();
  const tg = tgA.clone().lerp(tgB, macro);
  orbit(S.cam, tg, lerp(lerp(7.5, 6.5, seg(t, 0, zoomT)), 1.6, macro), lerp(0.5, 0.15, seg(t, 0, 30)), lerp(0.42, 0.25, macro));
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(tg), aperture: lerp(0.001, 0.004, macro), maxblur: 0.012 });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#eee8f6');
  title('теперь масштаб', 140, 200, t, 0.7, { size: 100, align: 'left', out: cue(id, 'шестерни') - 0.3 });
  pill('футляр ≈ 34 × 18 × 9 см', 140, 300, t, cue(id, 'тридцать'), { dot: CSS.gold, align: 'left', out: zoomT - 0.2 });
  pill('шестерни ≈ 1,4 мм толщиной', 140, 395, t, cue(id, 'шестерни'), { dot: CSS.gold, align: 'left', out: zoomT - 0.2 });
  pill('самая большая: ≈ 13 см · 223 зуба', 140, 490, t, cue(id, 'самая'), { dot: CSS.gold, align: 'left', out: zoomT - 0.2 });
  title('шаг зубьев ≈ 1,5 мм', 140, 200, t, zoomT + 0.4, { size: 90, align: 'left' });
  title('вырезаны вручную', 140, 1000, t, cue(id, 'вручную'), { size: 84, align: 'left', color: PURPLE });
}

// ───────── n4. Коринфский календарь и игры ─────────
const MONTHS = ['Фойникайос', 'Кранейос', 'Ланотропиос', 'Маханеус', 'Додекатеус', 'Эвклейос', 'Артемисиос', 'Псидреус', 'Гамейлиос', 'Агрианиос', 'Панамос', 'Апеллайос'];
const N4 = (() => {
  const S = newScene({ bg: 0xf2ece4, floorY: -1.8, key: [4, 11, 7] });
  const ringG = new THREE.Group(); S.scene.add(ringG);
  const disk = puck(3.0, 0.2, metal(C.bronze)); disk.rotation.x = Math.PI / 2; ringG.add(disk);
  const tabs = MONTHS.map((m, i) => { const a = (i / 12) * Math.PI * 2; const tb = textSprite(m, { size: 44, scale: 0.75, bg: '#fff7e8' }); tb.position.set(Math.cos(a) * 2.25, Math.sin(a) * 2.25, 0.3); ringG.add(tb); return tb; });
  ringG.position.set(2.2, 0.6, -1.0); ringG.scale.setScalar(0.8);
  // «карта»: плоскость-остров с булавками
  const mapG = new THREE.Group(); mapG.position.set(9, -1.5, 0); S.scene.add(mapG);
  const land = sphere(3.2, matte(C.sage), 32); land.scale.set(1.3, 0.12, 1.0); mapG.add(land);
  const pins = [['Сиракузы', -2.6, 2.0, C.coral, false], ['Эпир · Додона', -1.6, -0.6, C.mint, true], ['Коринф', 0.6, 0.2, C.lav, true], ['Олимпия', -0.6, 0.9, C.butter, true], ['Родос', 3.0, 1.6, C.sky, true]];
  const pinObjs = pins.map(([n, x, z, c]) => { const g = new THREE.Group(); const stem = cyl(0.04, 0.8, gloss(C.white), 10); stem.position.y = 0.4; g.add(stem); const head = sphere(0.18, gloss(c)); head.position.y = 0.85; g.add(head); g.position.set(x, 0.35, z); mapG.add(g); const l = textSprite(n, { size: 44, scale: 0.8 }); l.position.set(x, 1.6, z); mapG.add(l); return { g, l }; });
  return { ...S, ringG, tabs, mapG, pinObjs };
})();
export function n4(t) {
  const S = N4, id = 'n4';
  S.ringG.rotation.z = t * 0.12;
  const toMap = easeIO2(seg(t, cue(id, 'исследование') - 0.2, cue(id, 'исследование') + 2.0));
  S.ringG.visible = toMap < 0.9;
  const pinT = [cue(id, 'сиракуз'), cue(id, 'эпира'), cue(id, 'коринфские'), cue(id, 'олимпийскими'), cue(id, 'родос')];
  S.pinObjs.forEach((p, i) => { popScale(p.g, t, pinT[i] < 9000 ? Math.max(pinT[i], cue(id, 'исследование')) : 9999, 0.8, v3(1, 1, 1)); popScale(p.l, t, pinT[i] < 9000 ? Math.max(pinT[i], cue(id, 'исследование')) + 0.1 : 9999); });
  const tg = v3(lerp(0.6, 9, toMap), lerp(0.4, -1.0, toMap), 0);
  orbit(S.cam, tg, lerp(12, 11, toMap), lerp(0.25, 0.1, toMap) + Math.sin(t * 0.2) * 0.1, lerp(0.12, 0.75, toMap));
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#f2ece4');
  title('месяцы — коринфские', 140, 200, t, cue(id, 'названия') - 0.2, { size: 96, align: 'left', out: cue(id, 'исследование') - 0.3 });
  pill('2017: это не календарь Сиракуз', 140, 150, t, cue(id, 'исследование'), { dot: CSS.coral, align: 'left' });
  pill('похож на календарь Эпира', 140, 245, t, cue(id, 'эпира'), { dot: CSS.mint, align: 'left' });
  title('игры: Олимпия, Истм, Немея, Пифии,', 140, 940, t, cue(id, 'олимпийскими'), { size: 54, align: 'left' });
  title('Найи (Додона) и Галиейи (Родос)', 140, 1015, t, cue(id, 'найи'), { size: 54, align: 'left', color: PURPLE });
}

// ───────── n5. Когда сделали: спор о датах ─────────
const N5 = (() => {
  const S = newScene({ bg: C.cream, floorY: -0.6, key: [5, 12, 8], shadowSize: 20 });
  const bar = rbox(22, 0.3, 1.6, matte(C.sand), 0.14); bar.position.set(0, -0.45, 0); S.scene.add(bar);
  // ось лет: x = (год до н.э.) от 220 (слева) до 50 (справа)
  const X = (y) => lerp(-10, 10, (220 - y) / 170);
  for (let y = 220; y >= 50; y -= 10) { const tk = rbox(0.06, 0.06, y % 50 === 0 ? 1.4 : 0.8, matte(y % 50 === 0 ? C.lav : C.white), 0.02); tk.position.set(X(y), -0.27, 0); S.scene.add(tk); }
  const yl = [200, 150, 100, 50].map((y) => { const s = textSprite(`${y} до н. э.`, { size: 44, scale: 1.1, bg: null, color: CSS.deep, weight: 700 }); s.position.set(X(y), -0.1, 1.2); S.scene.add(s); return s; });
  const band = rbox(Math.abs(X(67) - X(76)), 0.1, 1.5, gloss(C.gold, { transparent: true, opacity: 0.8 }), 0.04); band.position.set((X(76) + X(67)) / 2, -0.24, 0); S.scene.add(band);
  const mk = (y, c, txt, ly = 2.2) => { const g = new THREE.Group(); const stem = cyl(0.05, 1.6, gloss(C.white), 12); stem.position.y = 0.8; g.add(stem); const head = sphere(0.25, gloss(c)); head.position.y = 1.7; g.add(head); g.position.set(X(y), -0.3, 0); S.scene.add(g); const l = textSprite(txt, { size: 52, scale: 1.1 }); l.position.set(X(y), ly, 0); S.scene.add(l); return { g, l }; };
  const m87 = mk(87, C.sky, 'Прайс: ≈ 87', 3.1), m205 = mk(205, C.coral, '2014: 205 · новолуние'), m178 = mk(178, C.mint, '2022: 178 · настройка', 2.9), coins = mk(71.5, C.gold, 'монеты 76–67');
  return { ...S, X, band, m87, m205, m178, coins };
})();
export function n5(t) {
  const S = N5, id = 'n5';
  const tc = cue(id, 'монеты'), tp = cue(id, 'прайс'), tce = cue(id, 'карман'), t22 = cue(id, 'двадцать');
  S.band.visible = t > tc; S.band.scale.x = easeOut(seg(t, tc, tc + 0.8)) + 0.001;
  popScale(S.coins.g, t, tc + 0.3, 0.8, v3(1, 1, 1)); popScale(S.coins.l, t, tc + 0.4);
  popScale(S.m87.g, t, tp, 0.8, v3(1, 1, 1)); popScale(S.m87.l, t, tp + 0.1);
  popScale(S.m205.g, t, tce, 0.8, v3(1, 1, 1)); popScale(S.m205.l, t, tce + 0.1);
  const t178 = cue(id, 'сто'); popScale(S.m178.g, t, t178, 0.8, v3(1, 1, 1)); popScale(S.m178.l, t, t178 + 0.1);
  // плавные переезды камеры между вехами
  const keys = [[0, S.X(71.5)], [tp, S.X(85)], [tce, S.X(200)], [t178, S.X(178)]];
  let fx = keys[0][1];
  for (let i = 1; i < keys.length; i++) fx = lerp(fx, keys[i][1], easeIO2(seg(t, keys[i][0] - 0.3, keys[i][0] + 1.5)));
  const wide = easeIO2(seg(t, cue(id, 'разброс') - 0.5, cue(id, 'разброс') + 1.5));
  const tg = v3(lerp(fx, 0, wide), 1.0, 0);
  orbit(S.cam, tg, lerp(10.5, 24, wide), 0.2 + Math.sin(t * 0.15) * 0.1, lerp(0.25, 0.35, wide));
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg, 0.0007) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('когда его сделали?', 140, 200, t, 0.7, { size: 100, align: 'left', out: tc - 0.2 });
  pill('механизм не моложе крушения', 140, 150, t, cue(id, 'значит'), { dot: CSS.gold, align: 'left', out: tp - 0.2 });
  title('разброс — больше 100 лет', 960, 1000, t, cue(id, 'разброс'), { size: 90, color: PURPLE });
}
