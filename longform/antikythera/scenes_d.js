// Дополнительные сцены n6–n9
import { render, clear2d, ctx, title, pill, counter, iris, project, W, H,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { THREE, C, CSS, matte, gloss, metal, gear, shadowAll, v3, orbit, newScene, rbox, sphere, cyl, puck, train, axle, textSprite, popScale,
  lump, amphora, bust, diver } from './kit.js';
import { cue } from './scenes_c.js';
const PURPLE = '#7a63e6';
const dofOpts = (cam, tg, ap = 0.001) => ({ focus: cam.position.distanceTo(tg), aperture: ap, maxblur: 0.01 });

function armillary(c1, c2) {
  const g = new THREE.Group();
  const base = puck(0.8, 0.3, matte(C.cream)); base.position.y = -1.6; g.add(base);
  const stand = cyl(0.08, 1.2, metal(C.gold), 16); stand.position.y = -1.0; g.add(stand);
  const rings = [];
  [1.0, 0.85, 0.7].forEach((r, i) => { const m = new THREE.Mesh(new THREE.TorusGeometry(r, 0.04, 12, 96), metal(i % 2 ? c2 : c1)); m.rotation.set(i * 0.7, i * 1.1, 0); g.add(m); rings.push(m); });
  const core = sphere(0.22, gloss(C.butter, { emissive: 0xffb400, emissiveIntensity: 0.3 })); g.add(core);
  return { g: shadowAll(g), rings };
}

// ───────── n6. Цицерон и сферы Архимеда ─────────
const N6 = (() => {
  const S = newScene({ bg: 0xf1ebe2, floorY: -1.75, key: [4, 11, 7] });
  const a1 = armillary(C.gold, C.bronze); a1.g.position.set(-2.4, 0.2, 0); S.scene.add(a1.g);
  const a2 = armillary(C.bronze, C.gold); a2.g.position.set(2.4, 0.2, 0); S.scene.add(a2.g);
  const scroll = new THREE.Group(); const rod1 = cyl(0.12, 2.6, gloss(C.coral), 16); rod1.rotation.z = Math.PI / 2; const sheet = rbox(2.4, 0.02, 1.0, matte(0xfff6e2), 0.01); sheet.position.z = 0.5; const rod2 = rod1.clone(); rod2.position.z = 1.0; scroll.add(rod1, sheet, rod2); shadowAll(scroll); scroll.position.set(0, -1.55, 2.0); S.scene.add(scroll);
  const temple = new THREE.Group(); [-0.8, -0.27, 0.27, 0.8].forEach((x) => { const c = cyl(0.12, 1.4, matte(C.cream), 20); c.position.set(x, 0.7, 0); temple.add(c); }); const roof = rbox(2.2, 0.25, 0.9, matte(C.cream), 0.06); roof.position.y = 1.5; temple.add(roof); const st = rbox(2.3, 0.2, 1.0, matte(C.sand), 0.05); temple.add(st); shadowAll(temple); temple.position.set(2.4, -1.65, -2.6); S.scene.add(temple);
  return { ...S, a1, a2, scroll, sheet, temple };
})();
export function n6(t) {
  const S = N6, id = 'n6';
  [S.a1, S.a2].forEach((a, k) => a.rings.forEach((r, i) => { r.rotation.y += 0; r.rotation.z = t * (0.2 + i * 0.15) * (k ? -1 : 1); }));
  popScale(S.a1.g, t, cue(id, 'архимеда') - 0.2, 0.9, v3(1, 1, 1)); popScale(S.a2.g, t, cue(id, 'архимеда') + 0.2, 0.9, v3(1, 1, 1));
  const unroll = easeOut(seg(t, cue(id, 'цицерон'), cue(id, 'цицерон') + 1.2)); S.sheet.scale.z = Math.max(0.01, unroll); S.sheet.position.z = 0.5 * unroll; S.scroll.children[2].position.z = 1.0 * unroll;
  popScale(S.temple, t, cue(id, 'храм') - 0.2, 0.9, v3(1, 1, 1));
  const tg = v3(0, 0, 0);
  orbit(S.cam, tg, lerp(12, 10, easeIO2(seg(t, 0, 28))), lerp(-0.35, 0.35, easeIO2(seg(t, 0, 28))), 0.22);
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#f1ebe2');
  title('были ли другие такие машины?', 140, 200, t, 0.7, { size: 84, align: 'left', out: cue(id, 'цицерон') - 0.2 });
  pill('Цицерон, «О государстве»', 140, 150, t, cue(id, 'цицерон'), { dot: CSS.gold, align: 'left', out: cue(id, 'их') - 0.2 });
  title('приборы Архимеда', 140, 280, t, cue(id, 'архимеда') - 0.1, { size: 96, align: 'left', out: cue(id, 'их') - 0.2 });
  pill('Солнце, Луна и 5 планет', 140, 380, t, cue(id, 'солнца'), { dot: CSS.butter, align: 'left', out: cue(id, 'их') - 0.2 });
  pill('212 до н. э. · Сиракузы → Рим, полководец Марцелл', 140, 150, t, cue(id, 'их'), { dot: CSS.coral, align: 'left', out: cue(id, 'цицерон', 1) - 0.3 });
  pill('один — в храм Доблести', 140, 245, t, cue(id, 'храм'), { align: 'left', out: cue(id, 'цицерон', 1) - 0.3 });
  pill('ещё прибор Посидония', 140, 150, t, cue(id, 'посидония') - 0.3, { dot: CSS.lav, align: 'left' });
  title('но наш — скорее всего, ни один из них', 140, 1000, t, cue(id, 'наш'), { size: 66, align: 'left', color: PURPLE });
}

// ───────── n7. Почему остался один: переплавка vs море ─────────
const N7 = (() => {
  const S = newScene({ bg: 0xf3e6dc, floorY: -1.6, key: [5, 10, 6] });
  const furnace = new THREE.Group();
  const body = rbox(2.6, 2.6, 2.2, matte(0xc9a48a), 0.4); body.position.y = -0.3; furnace.add(body);
  const mouth = rbox(1.2, 0.8, 0.1, new THREE.MeshBasicMaterial({ color: 0xff9a3c, toneMapped: false }), 0.2); mouth.position.set(0, -0.3, 1.12); furnace.add(mouth);
  const chim = cyl(0.35, 1.6, matte(0xb98f78), 20); chim.position.set(0.6, 1.6, -0.4); furnace.add(chim);
  shadowAll(furnace); S.scene.add(furnace);
  const items = []; for (let i = 0; i < 5; i++) { const g = i % 2 ? gear(18, 0.42, metal(C.bronze), { thick: 0.12, spokes: 3 }) : amphora(metal(C.bronze)); if (i % 2 === 0) g.scale.setScalar(0.35); S.scene.add(g); items.push(g); }
  // морское дно справа
  const sea = new THREE.Group(); sea.position.set(12, 0, 0); S.scene.add(sea);
  const sand = rbox(8, 0.4, 6, matte(0xe6d2ad), 0.2); sand.position.y = -1.4; sea.add(sand);
  const lp = lump({ r: 0.8, seed: 4 }); lp.position.set(0, -0.9, 0); lp.rotation.z = 0.3; sea.add(lp);
  const water = new THREE.Mesh(new THREE.BoxGeometry(8.2, 4, 6.2), gloss(C.sea, { transparent: true, opacity: 0.22, depthWrite: false })); water.position.y = 0.6; sea.add(water);
  const weeds = []; for (let i = 0; i < 7; i++) { const w = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 1.0 + hash(i) * 0.8, 4, 8), gloss(C.mint)); w.position.set(-3 + i * 1.0, -0.6, -1.8 + hash(i * 3) * 3.6); sea.add(w); weeds.push(w); }
  return { ...S, mouth, items, sea, weeds, lp };
})();
export function n7(t) {
  const S = N7, id = 'n7';
  S.mouth.material.color.setHSL(0.07, 1, 0.55 + 0.08 * Math.sin(t * 7));
  S.items.forEach((g, i) => { const t0 = 1.6 + i * 1.1; const k = seg(t, t0, t0 + 1.6); g.visible = k > 0 && k < 1; g.position.set(lerp(-4.5, 0, easeIn(k)), lerp(1.2, -0.3, easeIn(k)) + Math.sin(k * Math.PI) * 0.6, lerp(1.5, 1.2, k)); const s = (i % 2 === 0 ? 0.35 : 1) * (1 - easeIn(seg(k, 0.75, 1))); g.scale.setScalar(Math.max(0.001, s)); g.rotation.z = k * 3; });
  S.weeds.forEach((w, i) => { w.rotation.z = Math.sin(t * 1.2 + i) * 0.2; w.rotation.x = Math.sin(t * 0.9 + i * 2) * 0.15; });
  const toSea = easeIO2(seg(t, cue(id, 'этот') - 0.4, cue(id, 'этот') + 1.8));
  const tg = v3(lerp(-1, 12, toSea), lerp(0, -0.6, toSea), 0);
  orbit(S.cam, tg, lerp(10, 9, toSea), lerp(0.4, -0.2, toSea) + Math.sin(t * 0.2) * 0.05, lerp(0.22, 0.3, toSea));
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#f3e6dc');
  title('почему дошёл только один?', 140, 200, t, 0.7, { size: 90, align: 'left', out: cue(id, 'бронза') - 0.2 });
  title('бронзу переплавляли', 140, 200, t, cue(id, 'бронза'), { size: 100, align: 'left', out: cue(id, 'этот') - 0.3, color: '#e8706a' });
  title('этот спасло кораблекрушение', 140, 200, t, cue(id, 'этот'), { size: 90, align: 'left' });
  pill('2000 лет на дне моря', 140, 300, t, cue(id, 'море'), { dot: CSS.sky, align: 'left' });
}

// ───────── n8. Раскопки продолжаются ─────────
const N8 = (() => {
  const S = newScene({ bg: 0xbfdbe8, floorY: -1.8, key: [3, 12, 5], fill: 0.5 });
  S.scene.fog = new THREE.Fog(0xbfdbe8, 14, 40);
  S.ground.material.color.set(0xe6d2ad);
  const grid = new THREE.Group(); for (let i = -4; i <= 4; i++) { const a = rbox(0.04, 0.03, 8, matte(C.coral), 0.01); a.position.set(i, -1.77, 0); grid.add(a); const b = rbox(8, 0.03, 0.04, matte(C.coral), 0.01); b.position.set(0, -1.77, i); grid.add(b); } S.scene.add(grid);
  const d1 = diver(); d1.position.set(-2.2, -0.2, 1.2); d1.rotation.set(0.9, 0.6, 0); S.scene.add(d1);
  const amph = []; for (let i = 0; i < 6; i++) { const a = amphora(gloss(C.coral)); a.scale.setScalar(0.5); a.rotation.z = 1.4; a.position.set(-3 + i * 1.3, -1.6, -2 + hash(i) * 1.5); S.scene.add(a); amph.push(a); }
  const coins = []; for (let i = 0; i < 12; i++) { const c = puck(0.16, 0.05, metal(C.gold)); c.position.set((hash(i) - 0.5) * 3, -1.72, 1 + (hash(i * 2) - 0.5) * 2); S.scene.add(c); coins.push(c); }
  const disk = puck(0.5, 0.08, metal(C.bronze)); disk.rotation.x = Math.PI / 2 - 0.3; disk.position.set(2.2, -1.1, 1.5); S.scene.add(disk);
  const boulders = []; for (let i = 0; i < 3; i++) { const b = lump({ r: 1.0 + i * 0.15, seed: 20 + i, mat: matte(0xa9a3a0, { roughness: 0.9 }) }); b.position.set(3.2 + i * 1.9, -1.0, -1.5 + i * 0.8); S.scene.add(b); const bag = sphere(0.45, gloss(C.butter)); bag.scale.y = 1.2; bag.position.set(b.position.x, 2.5, b.position.z); S.scene.add(bag); const line = cyl(0.02, 3.2, matte(C.deep), 6); S.scene.add(line); boulders.push({ b, bag, line, y0: -1.0 }); }
  return { ...S, d1, amph, coins, disk, boulders };
})();
export function n8(t) {
  const S = N8, id = 'n8';
  S.d1.position.x = -2.2 + Math.sin(t * 0.4) * 0.6; S.d1.position.y = -0.2 + Math.sin(t * 0.9) * 0.15;
  const tc = cue(id, 'кусто'); S.coins.forEach((c, i) => popScale(c, t, tc + 0.3 + i * 0.06, 0.6, v3(1, 1, 1)));
  popScale(S.disk, t, cue(id, 'диск') - 0.2, 0.8, v3(1, 1, 1)); S.disk.rotation.z = t * 0.3;
  const tb = cue(id, 'валуна') - 0.4;
  S.boulders.forEach((o, i) => { const k = easeIO2(seg(t, tb + i * 0.4, tb + 3.0 + i * 0.4)); o.b.position.y = o.y0 + k * 5; o.bag.position.y = o.b.position.y + 2.6; o.line.position.set(o.b.position.x, o.b.position.y + 1.3, o.b.position.z); o.b.visible = o.bag.visible = o.line.visible = t > tb - 1.0; });
  const tg = v3(lerp(-0.5, 3.8, easeIO2(seg(t, tb - 1.5, tb + 1.0))), lerp(-1.0, 0.2, easeIO2(seg(t, tb - 1.5, tb + 2.5))), 0);
  orbit(S.cam, tg, lerp(12, 11, seg(t, 0, 30)), lerp(-0.4, 0.3, easeIO2(seg(t, 0, 30))), 0.28);
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, '#bfdbe8');
  title('раскопки продолжаются', 140, 200, t, 0.7, { size: 96, align: 'left', out: tc - 0.3 });
  pill('1976 · Кусто: почти 300 предметов, монеты', 140, 150, t, tc, { dot: CSS.gold, align: 'left', out: cue(id, 'двенадцатого') - 0.2 });
  pill('с 2012 · «Возвращение на Антикитеру»', 140, 150, t, cue(id, 'двенадцатого'), { dot: CSS.sky, align: 'left', out: tb - 0.3 });
  pill('2016 · скелет «Памфил»', 140, 245, t, cue(id, 'шестнадцатом'), { align: 'left', out: tb - 0.3 });
  pill('2017 · бронзовая рука и диск с быком', 140, 340, t, cue(id, 'семнадцатом'), { align: 'left', out: tb - 0.3 });
  pill('2022 · убраны 3 валуна по 8,5 т', 140, 150, t, tb + 0.2, { dot: CSS.coral, align: 'left' });
}

// ───────── n9. Реплики и музей ─────────
const N9 = (() => {
  const S = newScene({ bg: C.cream, floorY: -1.8, key: [5, 11, 7], shadowSize: 18 });
  const bricks = []; const cols = [C.coral, C.butter, C.sky, C.mint, C.lav];
  for (let i = 0; i < 24; i++) { const g = new THREE.Group(); const b = rbox(0.8, 0.4, 0.4, gloss(cols[i % 5]), 0.05); g.add(b); for (const dx of [-0.2, 0.2]) { const s = cyl(0.09, 0.08, gloss(cols[i % 5]), 16); s.position.set(dx, 0.24, 0); g.add(s); } shadowAll(g); const col = i % 4, row = Math.floor(i / 4); g.userData.home = v3(-4.6 + col * 0.82, -1.6 + row * 0.42, 0); S.scene.add(g); bricks.push(g); }
  const giant = new THREE.Group(); const gb = rbox(3, 4, 1.2, matte(0xd8a77a), 0.2); giant.add(gb); const gr = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.1, 16, 96), metal(C.gold)); gr.position.set(0, 0.3, 0.65); giant.add(gr); shadowAll(giant); giant.position.set(1.6, 0.2, -1); S.scene.add(giant);
  const person = new THREE.Group(); const pb = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.32, 6, 12), gloss(C.deep)); pb.position.y = 0.26; const ph = sphere(0.09, gloss(C.peach)); ph.position.y = 0.56; person.add(pb, ph); shadowAll(person); person.position.set(3.4, -1.8, 0.2); S.scene.add(person);
  const vit = new THREE.Group(); const plinth = rbox(3, 1.2, 1.8, matte(C.white), 0.12); plinth.position.y = -1.2; vit.add(plinth); const glass = rbox(2.8, 1.6, 1.6, gloss(0xffffff, { transparent: true, opacity: 0.18, depthWrite: false }), 0.08); glass.position.y = 0.2; vit.add(glass);
  for (let i = 0; i < 5; i++) { const l = lump({ r: 0.22 + hash(i) * 0.15, seed: 30 + i }); l.position.set(-0.9 + i * 0.45, -0.45, (hash(i * 3) - 0.5) * 0.6); vit.add(l); }
  shadowAll(vit); vit.position.set(9, 0, 0); S.scene.add(vit);
  return { ...S, bricks, giant, person, vit };
})();
export function n9(t) {
  const S = N9, id = 'n9';
  const tl = cue(id, 'десятом');
  S.bricks.forEach((b, i) => { const k = spring(seg(t, tl + i * 0.08, tl + i * 0.08 + 0.9) * 1.3, 7, 5); b.position.copy(b.userData.home).add(v3(0, (1 - k) * 4, 0)); b.visible = k > 0.01; });
  const tg2 = cue(id, 'мексике'); popScale(S.giant, t, tg2, 1.0, v3(1, 1, 1)); S.person.visible = t > tg2 + 0.5;
  const tm = cue(id, 'оригинал') - 0.3;
  const toM = easeIO2(seg(t, tm, tm + 2.0));
  const tg = v3(lerp(lerp(-3.4, 1.0, easeIO2(seg(t, tg2 - 0.5, tg2 + 1.5))), 9, toM), lerp(-0.6, 0, toM), 0);
  orbit(S.cam, tg, lerp(10, 7, toM), lerp(0.4, 0.1, toM) + Math.sin(t * 0.2) * 0.08, 0.2);
  render(S.scene, S.cam, { time: t, ...dofOpts(S.cam, tg) });
  clear2d();
  iris(1 + seg(t, 0, 0.6), 960, 540, CSS.cream);
  title('механизм вдохновляет', 140, 200, t, 0.7, { size: 96, align: 'left', out: tl - 0.2 });
  pill('2010 · Энди Кэрол: рабочая модель из конструктора', 140, 150, t, tl, { dot: CSS.gold, align: 'left', out: tg2 - 0.2 });
  pill('2024 · Университет Соноры: копия ×10', 140, 150, t, tg2, { dot: CSS.sky, align: 'left', out: tm - 0.2 });
  title('оригинал — в Афинах', 140, 200, t, tm + 0.3, { size: 96, align: 'left' });
  pill('Национальный археологический музей', 140, 300, t, cue(id, 'национальном'), { dot: CSS.patina, align: 'left' });
}
