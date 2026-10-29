// Сцены расширенной версии (21+ мин): s03b купол, s04c маяк Смитона, s05b ржавчина и Генуя, s06b пепел,
// s06c римская стройка, s07b круг извести, s10c РОМАКОНС, s12b находки Помпей, s13b бактерии, s13c три мифа
import { render, clear2d, ctx, title, pill, counter, project, W, H, THREE, C, CSS, matte, gloss, metal,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { VO, cue, dof, shot, v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, waves, cloud,
  stone, concrete, marble, brick, wood, shadowAll, column, pantheon, lightBeam, pier, romanShip, beam, factory, smoke, kiln, volcano,
  pile, bucket, trowel, book, microscope, clastCube, drops, crystal, chapter, quote, dimLine, stamp, bars } from './lib.js';
import { diver, boat } from './kit.js';
import { PAN, PANI, BEAM, beamAt, VOLC, CUBE, SEA, CAES } from './scenes_a.js';

const RED = '#e8706a', PURPLE = '#7a63e6', MINT = '#86dcbc', SKY = '#8fd0e6', SAND = '#e9b97f';
// cue с запасным временем как доля длительности голоса сцены
const fc = (id, w, nth, frac) => cue(id, w, nth, VO + frac * ((window.VDUR && window.VDUR[id]) || 60));

// табличка/надпись как плоскость с текстурой
function plaque(text, { w = 6, h = 0.6, size = 64, color = '#3b342c', bg = null, font = '700', serif = true, spacing = 6 } = {}) {
  const cv = document.createElement('canvas'); cv.width = 2048; cv.height = Math.round(2048 * h / w);
  const g = cv.getContext('2d'); if (bg) { g.fillStyle = bg; g.fillRect(0, 0, cv.width, cv.height); }
  g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = `${font} ${size}px ${serif ? '"NSerif", serif' : '"Rubik"'}`;
  if (g.letterSpacing !== undefined) g.letterSpacing = spacing + 'px';
  g.fillText(text, cv.width / 2, cv.height / 2 + 4);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 4;
  return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: tx, transparent: !bg, roughness: 0.8 }));
}
const lumps = (n, r, mat, seed) => { const g = new THREE.Group(); for (let i = 0; i < n; i++) { const s = sphere(r * (0.6 + hash(i + seed) * 0.8), mat, 14); s.scale.set(1, 0.7 + hash(i * 3 + seed) * 0.4, 1); g.add(s); } return g; };

// ═════════ s03b. Как держится купол ═════════
const FAC = (() => {
  const S = newScene({ bg: 0xe5ecf4, floorY: 0, key: [6, 10, 12], shadowSize: 14 });
  S.ground.material = stone({ base: '#e3d8c8', dots: '#c3b39d', dots2: '#f3ece2', n: 700, seed: 401, rep: 14 }); S.ground.material.map.repeat.set(14, 14);
  const g = new THREE.Group(); S.scene.add(g);
  const gran = stone({ base: '#cfc3b2', dots: '#a8988a', dots2: '#ece4d8', n: 500, seed: 402 });
  for (let i = 0; i < 8; i++) { const c = column(6, 0.42, gran); c.position.set(-5.25 + i * 1.5, 0.6, 0); g.add(c); }
  const st = rbox(12.6, 0.6, 3.6, marble(), 0.05); st.position.set(0, 0.3, -0.6); g.add(st);
  const arch = rbox(12.2, 1.1, 1.3, marble(), 0.04); arch.position.set(0, 7.35, 0); g.add(arch);
  const cor = rbox(12.6, 0.3, 1.5, marble(), 0.04); cor.position.set(0, 8.05, 0); g.add(cor);
  const tri = new THREE.Shape(); tri.moveTo(-6.3, 0); tri.lineTo(6.3, 0); tri.lineTo(0, 2.4); tri.lineTo(-6.3, 0);
  const ped = new THREE.Mesh(new THREE.ExtrudeGeometry(tri, { depth: 1.3, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 2 }), marble()); ped.position.set(0, 8.2, -0.65); g.add(ped);
  const insc = plaque('M·AGRIPPA·L·F·COS·TERTIVM·FECIT', { w: 11.4, h: 0.8, size: 118, color: '#5b4a36', spacing: 10 }); insc.position.set(0, 7.35, 0.66); g.add(insc);
  const back = rbox(11, 7, 1, stone({ base: '#d9ccb9', seed: 403 }), 0.05); back.position.set(0, 4.1, -3.2); g.add(back);
  const door = rbox(2.4, 4.2, 0.12, metal(C.bronze, { roughness: 0.45 }), 0.04); door.position.set(0, 2.7, -2.65); g.add(door);
  shadowAll(g);
  // кирпич с клеймом
  const bk = new THREE.Group(); bk.position.set(4.5, 0.9, 5.5); S.scene.add(bk);
  const bb = rbox(1.8, 0.35, 1.8, brick(), 0.04); bk.add(bb);
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.32, 0.6, 48, 1, 0, Math.PI * 1.6), matte(0x9a5134, { side: THREE.DoubleSide })); ring.rotation.x = -Math.PI / 2; ring.position.y = 0.18; bk.add(ring);
  const lbl = plaque('OPVS DOLIARE', { w: 1.0, h: 0.16, size: 120, color: '#7b3b22', spacing: 4 }); lbl.rotation.x = -Math.PI / 2; lbl.position.set(0, 0.181, 0.0); bk.add(lbl);
  shadowAll(bk);
  return { ...S, g, insc, bk };
})();
const DRUM = (() => {
  const S = newScene({ bg: 0xeee6f6, floorY: 0, key: [8, 14, 9], shadowSize: 14 });
  S.ground.material.color.set(0xe7dfd3);
  const wallM = concrete({ base: '#d6c8b6', seed: 410, clasts: 4 });
  const R0 = 5.2, R1 = 6.6, Hh = 4.6;
  const piers = new THREE.Group(); S.scene.add(piers);
  // 8 опор кольцом, между ними ниши; разгрузочные арки из кирпича над нишами
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    const p = new THREE.Mesh(new THREE.CylinderGeometry(R1, R1, Hh, 24, 1, false, a - 0.2, 0.4), wallM); p.position.y = Hh / 2; piers.add(p);
    const pin = new THREE.Mesh(new THREE.CylinderGeometry(R0, R0, Hh, 24, 1, true, a - 0.2, 0.4), wallM); pin.material.side = THREE.DoubleSide; pin.position.y = Hh / 2; piers.add(pin);
    // тонкая стенка ниши
    const sk = new THREE.Mesh(new THREE.CylinderGeometry(R1, R1, Hh, 24, 1, true, a + 0.2, Math.PI / 4 - 0.4), wallM); sk.material = wallM.clone(); sk.material.side = THREE.DoubleSide; sk.position.y = Hh / 2; piers.add(sk);
    const am = a + Math.PI / 8; const arch = new THREE.Mesh(new THREE.TorusGeometry(1.25, 0.2, 8, 20, Math.PI), brick()); arch.position.set(Math.sin(am) * (R1 + 0.02), Hh - 1.5, Math.cos(am) * (R1 + 0.02)); arch.rotation.y = am; piers.add(arch);
  }
  const top = new THREE.Mesh(new THREE.RingGeometry(R0, R1, 64), wallM); top.rotation.x = -Math.PI / 2; top.position.y = Hh; piers.add(top);
  shadowAll(piers);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(R1 - 0.2, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2 - 0.13), concrete({ base: '#e7dccb', seed: 411 }));
  dome.position.y = Hh; S.scene.add(dome); dome.castShadow = true;
  const gold = gloss(0xe0b04a, { metalness: 0.7, roughness: 0.3, clearcoat: 0.5 });
  const steps = []; for (let i = 0; i < 5; i++) { const r = R1 + 0.25 - i * 0.18; const s = cyl(r, 0.32, concrete({ base: '#d8cbb9', seed: 412 + i }), 64); s.position.y = Hh + 0.16 + i * 0.32; s.scale.set(1 - i * 0.045, 1, 1 - i * 0.045); S.scene.add(s); steps.push(s); }
  // вертикальные трещины: тонкие трубки по поверхности купола вдоль меридианов
  const cracks = []; const cm = matte(0x3b3732);
  for (let i = 0; i < 8; i++) { const a0 = (i / 8) * Math.PI * 2 + 0.39; const pts = []; const r = R1 - 0.17;
    for (let k = 0; k <= 10; k++) { const ph = 0.02 + k * 0.075; const a = a0 + (hash(i * 13 + k) - 0.5) * 0.05; pts.push(new THREE.Vector3(Math.sin(a) * Math.cos(ph) * r, Hh + Math.sin(ph) * r, Math.cos(a) * Math.cos(ph) * r)); }
    const g = new THREE.Group(); const seg = 5; for (let q = 0; q < seg; q++) { const sub = pts.slice(q * 2, q * 2 + 3); const tb = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(sub), 12, 0.035, 5), cm); g.add(tb); }
    S.scene.add(g); cracks.push(g); }
  const oc = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.18, 10, 40), concrete({ base: '#d0c2ae', seed: 419 })); oc.rotation.x = Math.PI / 2; oc.position.y = Hh + (R1 - 0.2) * Math.cos(0.13) * 0 + (R1 - 0.2) * Math.sin(Math.PI / 2 - 0.13); S.scene.add(oc);
  const people = []; for (let i = 0; i < 3; i++) { const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.14, 0.5, 6, 12), matte([C.coral, C.lav, C.mint][i])); b.position.y = 0.42; g.add(b); const h = sphere(0.11, matte(0xf1c9a8)); h.position.y = 0.86; g.add(h); g.position.set(8 + i * 0.7, 0, 3 - i * 0.9); S.scene.add(shadowAll(g)); people.push(g); }
  return { ...S, piers, dome, steps, cracks, gold, concreteDome: dome.material };
})();
export function s03b(t) {
  const id = 's03b';
  const tIn = fc(id, 'там', 0, 0.06), tAg = fc(id, 'агриппа', 1, 0.11), tTr = fc(id, 'судя', 0, 0.18), tAd = fc(id, 'старую', 0, 0.25),
    tDome = fc(id, 'теперь', 0, 0.29), tVoid = fc(id, 'пустоты', 0, 0.37), tSteps = fc(id, 'снаружи', 0, 0.44), tCr = fc(id, 'вертикальные', 0, 0.52),
    tFell = fc(id, 'купол', 2, 0.62), tGold = fc(id, 'снаружи', 1, 0.66), tUrb = fc(id, 'семнадцатом', 0, 0.78), tQ = fc(id, 'по', 0, 0.91), end = 200;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = FAC; orbit(S.cam, v3(0, 5, 0), lerp(30, 24, easeIO2(k)), lerp(0.35, 0.12, k), lerp(0.05, 0.12, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 6, 0), 0.0005) });
      title('как держится', 120, 230, t, 0.3, { size: 100, align: 'left', out: tIn - 0.2 }); title('купол?', 120, 345, t, 0.8, { size: 110, align: 'left', color: PURPLE, out: tIn - 0.2 }); }],
    [tIn, (lt, k) => { const S = FAC; S.cam.fov = 32; orbit(S.cam, v3(lerp(-3, 3, easeInOut(k)), 7.3, 0.6), 9.5, lerp(-0.18, 0.18, k), 0.02); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 7.3, 0.66), 0.0009) });
      pill('«Марк Агриппа, консул в третий раз, построил»', 125, 900, t, tIn + 0.8, { dot: SAND, align: 'left', size: 40 });
      stamp('НАДПИСЬ ВРЁТ', 1400, 300, t, tAg + 1.2, { size: 64 }); }],
    [tTr, (lt, k) => { const S = FAC; orbit(S.cam, v3(4.5, 0.9, 5.5), lerp(5, 3.8, k), lerp(0.2, -0.15, k), 0.75); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(4.5, 1, 5.5), 0.0016) });
      pill('Пантеон Агриппы · 27–25 гг. до н. э. — сгорел', 125, 230, t, tTr + 0.2, { dot: RED, align: 'left', size: 38 });
      pill('нынешний — третий на этом месте', 125, 330, t, tTr + 0.4, { dot: PURPLE, align: 'left', size: 38 });
      pill('клейма на кирпичах → начали при Траяне', 125, 430, t, tTr + 1.6, { dot: SAND, align: 'left', size: 38 });
      pill('закончил Адриан · ≈ 125 г.', 125, 530, t, tTr + 4.0, { dot: MINT, align: 'left', size: 38 }); }],
    [tAd, (lt, k) => { const S = FAC; orbit(S.cam, v3(0, 7.3, 0), lerp(16, 13, k), lerp(-0.5, -0.3, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 7.3, 0.6), 0.0007) });
      title('надпись вернули', 120, 230, t, tAd + 0.2, { size: 90, align: 'left' }); title('на место', 120, 335, t, tAd + 0.6, { size: 90, align: 'left', color: PURPLE }); }],
    [tDome, (lt, k) => { const S = DRUM; S.dome.visible = false; S.steps.forEach((s) => (s.visible = false)); S.cracks.forEach((c) => (c.visible = false));
      orbit(S.cam, v3(0, 2.3, 0), lerp(26, 20, easeIO2(k)), lerp(0.6, 0.15, k), lerp(0.55, 0.42, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2.3, 0), 0.0005) });
      const a = project(v3(Math.sin(0.0) * 5.2, 4.7, Math.cos(0.0) * 5.2), S.cam), b = project(v3(0, 4.7, 6.6), S.cam);
      dimLine(a, b, '≈ 6 м', t, tDome + 2.0, { size: 40 });
      title('кольцевая стена', 120, 230, t, tDome + 0.4, { size: 90, align: 'left' });
      pill('внутри — ниши и арки из кирпича', 125, 345, t, tDome + 4.5, { dot: SAND, align: 'left', size: 40 });
      pill('пустоты ≈ ¼ объёма', 125, 445, t, tVoid, { dot: RED, align: 'left', size: 40 });
      pill('по сути — 8 опор в кольце', 125, 545, t, tVoid + 2.5, { dot: PURPLE, align: 'left', size: 40 }); }],
    [tSteps, (lt, k) => { const S = DRUM; S.dome.visible = true; S.dome.material = S.concreteDome; S.cracks.forEach((c) => (c.visible = false));
      S.steps.forEach((s, i) => { s.visible = true; const kk = easeOut(seg(t, tSteps + 0.4 + i * 0.35, tSteps + 1.2 + i * 0.35)); s.scale.y = Math.max(0.01, kk); });
      orbit(S.cam, v3(0, 5.5, 0), lerp(20, 17, k), lerp(-0.4, -0.15, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 5.5, 4), 0.0006) });
      title('ступенчатые кольца', 120, 230, t, tSteps + 0.3, { size: 84, align: 'left' }); pill('прижимают низ купола — он не расползается', 125, 340, t, tSteps + 1.6, { dot: MINT, align: 'left', size: 38 }); }],
    [tCr, (lt, k) => { const S = DRUM; S.dome.visible = true; S.steps.forEach((s) => { s.visible = true; s.scale.y = 1; });
      S.cracks.forEach((c, i) => { c.visible = true; c.children.forEach((m, j) => (m.visible = t > tCr + 0.6 + i * 0.12 + j * 0.15)); });
      orbit(S.cam, v3(0, 7, 0), lerp(19, 16, k), lerp(0.5, 0.8, k), lerp(0.55, 0.65, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 8, 0), 0.0006) });
      pill('трещины появились очень рано', 125, 230, t, tCr + 0.3, { dot: RED, align: 'left', size: 40 });
      pill('кольцо арок с общим замком у окулуса', 125, 330, t, tCr + 4.0, { dot: PURPLE, align: 'left', size: 40 });
      title('треснул —', 120, 520, t, tFell, { size: 100, align: 'left' }); title('но не упал', 120, 635, t, tFell + 0.6, { size: 100, align: 'left', color: MINT }); }],
    [tGold, (lt, k) => { const S = DRUM; S.cracks.forEach((c) => (c.visible = false)); const gk = smooth(seg(t, tGold + 0.3, tGold + 2)); S.dome.material = gk > 0.5 ? S.gold : S.concreteDome;
      orbit(S.cam, v3(0, 6, 0), lerp(24, 20, k), lerp(1.4, 1.0, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 6, 0), 0.0005), flash: 0.25 * (1 - Math.abs(gk - 0.5) * 2) });
      pill('позолоченная бронзовая черепица', 125, 230, t, tGold + 0.6, { dot: '#e0b04a', align: 'left', size: 40 });
      pill('663 г. — Констант II снял и увёз', 125, 330, t, tGold + 3.5, { dot: RED, align: 'left', size: 40 }); }],
    [tUrb, (lt, k) => { const S = FAC; orbit(S.cam, v3(0, 6, 0), lerp(22, 28, k), lerp(-0.7, -0.4, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 6, 0), 0.0005) });
      pill('XVII век · папа Урбан VIII (Барберини)', 125, 230, t, tUrb + 0.3, { dot: PURPLE, align: 'left', size: 40 });
      counter(Math.round(lerp(0, 200, easeOut(seg(t, tUrb + 2, tUrb + 4)))) + ' т', 120, 450, { size: 170, align: 'left', color: '#b07a2a' });
      title('бронзы портика', 130, 545, t, tUrb + 2.6, { size: 60, align: 'left' }); pill('→ на укрепления замка Святого Ангела', 135, 660, t, tUrb + 5.0, { dot: SAND, align: 'left', size: 38, out: tQ - 0.2 });
      quote('Чего не сделали варвары, сделали Барберини', 'римская поговорка (Quod non fecerunt barbari…)', 110, 640, t, tQ, end, { w: 980, size: 48 }); }],
  ], end);
}

// ═════════ s04c. Маяк Смитона ═════════
const EDDY = (() => {
  const S = newScene({ bg: 0xc9d9e6, floor: false, key: [6, 12, 6], shadowSize: 16 });
  const sea = waves(90, 60, 90, gloss(0x6aa8c6, { roughness: 0.18 })); S.scene.add(sea);
  const rockM = stone({ base: '#7f7a76', dots: '#5d5855', dots2: '#a39d97', n: 900, seed: 430, rough: 0.8 });
  const rocks = new THREE.Group(); S.scene.add(rocks);
  for (let i = 0; i < 7; i++) { const r = sphere(1 + hash(i) * 1.2, rockM, 20); r.scale.set(1.2, 0.55 + hash(i + 3) * 0.3, 1); r.position.set(-5 + i * 1.7 + (hash(i + 1) - 0.5), -0.1, (hash(i + 2) - 0.5) * 3); rocks.add(r); }
  const base = sphere(2.4, rockM, 28); base.scale.set(1.3, 0.6, 1.2); rocks.add(base); shadowAll(rocks);
  // Уинстенли: узорная деревянная башня
  const win = new THREE.Group(); win.position.y = 1.0; S.scene.add(win);
  const wm = wood();
  for (let i = 0; i < 4; i++) { const b = rbox(1.6 - i * 0.2, 1.3, 1.6 - i * 0.2, i % 2 ? matte(0xe9dcc4) : wm, 0.06); b.position.y = 0.65 + i * 1.3; win.add(b); }
  for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2; const p = cyl(0.05, 1.0, wm, 8); p.position.set(Math.sin(a) * 1.1, 5.6, Math.cos(a) * 1.1); p.rotation.z = Math.sin(a) * 0.4; p.rotation.x = -Math.cos(a) * 0.4; win.add(p); }
  const wl = cyl(0.6, 0.9, gloss(0xffe2a0, { emissive: 0xffb84d, emissiveIntensity: 0.5 }), 12); wl.position.y = 5.9; win.add(wl);
  shadowAll(win);
  // деревянная башня Радьерда (сгорела)
  const rud = new THREE.Group(); rud.position.y = 1.0; S.scene.add(rud);
  const rb = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.5, 5.5, 20), wood()); rb.position.y = 2.75; rud.add(rb); const rl = cyl(0.65, 0.8, gloss(0xffe2a0, { emissive: 0xffb84d, emissiveIntensity: 0.6 }), 16); rl.position.y = 5.9; rud.add(rl);
  shadowAll(rud);
  const fire = new THREE.Group(); rud.add(fire); const fps = []; for (let i = 0; i < 12; i++) { const f = sphere(0.35, gloss(0xff8a30, { emissive: 0xff6a10, emissiveIntensity: 1.4 }), 12); fire.add(f); fps.push(f); }
  const fsm = smoke(14, matte(0x6d6a72, { transparent: true, opacity: 0.8 })); fsm.position.set(0, 6, 0); rud.add(fsm);
  // Смитон: гранитная башня из колец
  const sm = new THREE.Group(); sm.position.y = 1.0; S.scene.add(sm);
  const gm = stone({ base: '#d9d5cf', dots: '#9c968f', dots2: '#f3f0ec', n: 900, seed: 431 });
  const rings = []; for (let i = 0; i < 14; i++) { const y = i * 0.42; const r = lerp(1.7, 0.95, Math.pow(i / 13, 0.7)); const c = new THREE.Mesh(new THREE.CylinderGeometry(r - 0.03, r, 0.4, 32), gm); c.position.y = 0.2 + y; sm.add(c); rings.push(c); }
  const gal = puck(1.25, 0.12, metal(0x4b4f5a)); gal.position.y = 6.0; sm.add(gal);
  const lan = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 1.0, 12), new THREE.MeshPhysicalMaterial({ color: 0xfff6d8, transmission: 0.5, roughness: 0.1, transparent: true, opacity: 0.75 })); lan.position.y = 6.55; sm.add(lan);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.85, 0.7, 12), metal(0x4b4f5a)); roof.position.y = 7.4; sm.add(roof);
  const lamp = sphere(0.35, gloss(0xfff0c0, { emissive: 0xffd070, emissiveIntensity: 0 }), 16); lamp.position.y = 6.5; sm.add(lamp);
  const pl = new THREE.PointLight(0xffd080, 0, 30, 1.5); pl.position.y = 6.6; sm.add(pl);
  const beamL = lightBeam(16, 0.3, 2.4, 0xfff0c0); beamL.rotation.z = Math.PI / 2; beamL.position.set(8, 6.55, 0); const pivot = new THREE.Group(); pivot.position.y = 6.55; beamL.position.set(8, 0, 0); pivot.add(beamL); sm.add(pivot);
  const red = []; for (let i = 0; i < 3; i++) { const b = cyl(lerp(1.42, 1.2, i / 2), 0.4, matte(0xc4554a), 32); b.position.y = 0.2 + (8 + i * 2) * 0.42; b.visible = false; sm.add(b); red.push(b); }
  shadowAll(sm);
  const hill = sphere(9, matte(0x9fc28e), 40); hill.scale.set(1.6, 0.35, 1.2); hill.position.set(0, -2.2, 0); hill.visible = false; S.scene.add(hill);
  const ship = romanShip(); ship.position.set(9, 0, 6); ship.rotation.y = -0.6; S.scene.add(ship);
  const spray = drops(50, 0xffffff, 0.08); S.scene.add(spray);
  const clouds = [[-10, 10, -18, 2.6], [10, 12, -22, 3.2], [2, 13, -26, 2.8]].map(([x, y, z, s]) => { const c = cloud(matte(0xdfe3ea)); c.position.set(x, y, z); c.scale.setScalar(s); S.scene.add(c); return c; });
  return { ...S, sea, rocks, win, rud, fire, fps, fsm, sm, rings, lamp, pl, pivot, beamL, red, hill, ship, spray };
})();
const DOVE = (() => {
  const S = newScene({ bg: 0xe9e4dc, floorY: -0.5, key: [4, 9, 6], keyI: 3.1 });
  const gm = stone({ base: '#dcd8d1', dots: '#a29b93', dots2: '#f5f2ee', n: 800, seed: 435 });
  const sh = new THREE.Shape(); sh.moveTo(-0.6, -0.5); sh.lineTo(0.6, -0.5); sh.lineTo(0.35, 0.1); sh.lineTo(0.75, 0.6); sh.lineTo(-0.75, 0.6); sh.lineTo(-0.35, 0.1); sh.lineTo(-0.6, -0.5);
  const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.6, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03, bevelSegments: 2 });
  const blocks = []; for (let i = 0; i < 7; i++) { const m = new THREE.Mesh(geo, gm); m.castShadow = m.receiveShadow = true; m.rotation.x = -Math.PI / 2; const flip = i % 2; m.rotation.z = flip ? Math.PI : 0; m.position.set((i - 3) * 1.0, 0, flip ? 0.1 : -0.1); S.scene.add(m); blocks.push(m); }
  const pails = []; for (let i = 0; i < 3; i++) { const b = bucket(); b.position.set(-3 + i * 1.4, -0.5, -2.6); S.scene.add(b); const w = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.05, 28), gloss(0x7fc0db, { roughness: 0.1 })); w.position.set(-3 + i * 1.4, 0.0, -2.6); S.scene.add(w); const l = sphere(0.18, matte([0xf3efe6, 0xe8dfcc, 0xd8d0c4][i]), 14); l.position.set(-3 + i * 1.4, 0.02, -2.6); S.scene.add(l); pails.push(l); }
  const extra = S.scene.children.filter((o) => o.position.z < -2); const hideP = (h) => extra.forEach((o) => (o.visible = !h));
  return { ...S, blocks, pails, hideP };
})();
export function s04c(t) {
  const id = 's04c', S = EDDY;
  const tRock = fc(id, 'плимута', 0, 0.12), tW = fc(id, 'первый', 0, 0.2), tStorm = fc(id, 'великая', 0, 0.25), tBurn = fc(id, 'второй', 0, 0.31), tSm = fc(id, 'тогда', 0, 0.36),
    tLime = fc(id, 'нашёл', 0, 0.45), tDove = fc(id, 'башню', 0, 0.52), tLit = fc(id, 'шестнадцатого', 0, 0.6), tMove = fc(id, 'убрали', 0, 0.71), tFather = fc(id, 'смитона', 1, 0.85), end = 200;
  const amp = t > tStorm && t < tStorm + 6 ? 2.0 : 1.1;
  S.sea.userData.update(t, amp); const hh = S.sea.userData.h;
  S.ship.position.set(9 - t * 0.05, hh(9, 6, t, amp) + 0.1, 6);
  S.spray.userData.ps.forEach((p, i) => { const ph = (t * 0.8 + hash(i)) % 1; const a = hash(i + 1) * 6.28; p.position.set(Math.cos(a) * 3.2, 0.5 + Math.sin(ph * Math.PI) * 2.6 * amp, Math.sin(a) * 2.5 + 1); p.visible = ph > 0.05 && ph < 0.9; });
  const phase = t < tBurn ? 0 : t < tSm ? 1 : 2;
  S.win.visible = phase === 0 && t < tStorm + 3.5; S.rud.visible = phase === 1; S.sm.visible = phase === 2;
  if (phase === 0) { const fall = easeIn(seg(t, tStorm + 1.2, tStorm + 3.4)); S.win.rotation.z = fall * 1.3; S.win.position.set(fall * 2, 1.0 - fall * 2.5, 0); }
  const burn = phase === 1 ? smooth(seg(t, tBurn + 1, tBurn + 4)) : 0;
  S.fps.forEach((f, i) => { const ph = (t * 0.9 + hash(i)) % 1; f.position.set(Math.sin(i * 2.3) * (1.2 - ph * 0.5), 1 + ph * 5.5, Math.cos(i * 2.3) * (1.2 - ph * 0.5)); f.scale.setScalar(burn * (1 - ph) * 1.4 + 0.001); });
  S.fsm.userData.update(t, 1.5); S.fsm.visible = burn > 0.1;
  const lit = phase === 2 ? smooth(seg(t, tLit + 0.6, tLit + 2.2)) : 0;
  S.lamp.material.emissiveIntensity = lit * 2.5; S.pl.intensity = lit * 40; S.beamL.visible = lit > 0.05; S.beamL.material.opacity = 0.22 * lit; S.pivot.rotation.y = t * 0.8;
  const night = t > tLit && t < tMove ? smooth(seg(t, tLit, tLit + 1.5)) : 0;
  S.scene.background.set(new THREE.Color(0xc9d9e6).lerp(new THREE.Color(0x2b3550), night * 0.85));
  const moved = t > tMove + 3.0; S.hill.visible = moved; S.sea.visible = !moved; S.rocks.visible = !moved; S.ship.visible = !moved; S.spray.visible = !moved;
  S.sm.position.y = moved ? 1.0 : 1.0; S.red.forEach((r) => (r.visible = moved)); S.rings.forEach((r, i) => (r.visible = !moved || i < 14));
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 1, 0), lerp(32, 24, easeIO2(k)), lerp(0.9, 0.5, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1, 0), 0.0004) });
      chapter(2, 'Маяк Смитона', t, 0.2, 6.0); pill('после Рима — века без больших бетонных куполов и гаваней', 125, 980, t, 2.0, { dot: SAND, align: 'left', size: 34, out: tRock - 0.2 }); }],
    [tRock, (lt, k) => { orbit(S.cam, v3(0, 0.5, 0), lerp(14, 11, k), lerp(-0.3, 0.1, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.5, 0), 0.0008) });
      title('рифы Эддистоун', 120, 230, t, tRock + 0.3, { size: 96, align: 'left' }); pill('у Плимута, Англия · губили корабли', 125, 340, t, tRock + 1.2, { dot: SKY, align: 'left', size: 40 }); }],
    [tW, (lt, k) => { orbit(S.cam, v3(0, 3.5, 0), lerp(16, 13, k), lerp(0.4, 0.2, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, 0), 0.0006), vig: 0.22 + (t > tStorm ? 0.2 : 0) });
      pill('маяк №1 · Генри Уинстенли', 125, 230, t, tW + 0.3, { dot: SAND, align: 'left', size: 40 }); stamp('1703 · ВЕЛИКАЯ БУРЯ', 1300, 320, t, tStorm + 0.6, { size: 56 }); }],
    [tBurn, (lt, k) => { orbit(S.cam, v3(0, 3.5, 0), lerp(14, 12, k), lerp(-0.4, -0.2, k), 0.14); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, 0), 0.0006) });
      pill('маяк №2 · деревянный', 125, 230, t, tBurn + 0.3, { dot: SAND, align: 'left', size: 40 }); stamp('СГОРЕЛ · 1755', 1300, 320, t, tBurn + 2.4, { size: 60 }); }],
    [tSm, (lt, k) => { const D = DOVE; D.hideP(false); D.pails.forEach((p, i) => { const sink = i === 2 ? 0 : easeIn(seg(t, tSm + 3 + i, tSm + 6 + i)); p.position.y = 0.02 - sink * 0.0; p.scale.setScalar(i === 2 ? 1 : Math.max(0.02, 1 - sink)); });
      orbit(D.cam, v3(-1.6, -0.1, -2.6), lerp(7, 5.5, k), lerp(0.2, -0.1, k), 0.45); render(D.scene, D.cam, { time: t, ...dof(D.cam, v3(-1.6, 0, -2.6), 0.0016) });
      title('Джон Смитон', 120, 230, t, tSm + 0.3, { size: 100, align: 'left' }); pill('опыты: какая известь твердеет под водой', 125, 340, t, tSm + 1.6, { dot: SKY, align: 'left', size: 40 });
      pill('гидравлическая известь ✓', 125, 440, t, tLime + 0.2, { dot: MINT, align: 'left', size: 44 }); }],
    [tDove, (lt, k) => { const D = DOVE; D.hideP(true); D.blocks.forEach((b, i) => { const kk = easeOut(seg(t, tDove + 0.5 + i * 0.25, tDove + 1.3 + i * 0.25)); b.position.z = (i % 2 ? 0.1 : -0.1) + (1 - kk) * (i % 2 ? 2.5 : -2.5); });
      orbit(D.cam, v3(0, 0, 0), lerp(9, 7, k), lerp(0.3, -0.2, k), 0.85); render(D.scene, D.cam, { time: t, ...dof(D.cam, v3(0, 0, 0), 0.001) });
      title('«ласточкин хвост»', 120, 230, t, tDove + 0.6, { size: 90, align: 'left' }); pill('гранитные блоки сцеплены, как пазл', 125, 340, t, tDove + 1.6, { dot: SAND, align: 'left', size: 40 }); }],
    [tLit, (lt, k) => { orbit(S.cam, v3(0, 3.5, 0), lerp(22, 17, k), lerp(0.7, 0.3, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3.5, 0), 0.0005) });
      title('16.10.1759', 120, 240, t, tLit + 0.4, { size: 110, align: 'left', color: '#ffffff' }); pill('маяк зажёгся · простоял больше 100 лет', 125, 360, t, tLit + 2.4, { dot: '#ffdc7a', align: 'left', size: 40 }); }],
    [tMove, (lt, k) => { orbit(S.cam, v3(0, 3, 0), lerp(20, 15, k), lerp(-0.5, 0.0, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, 0), 0.0005) });
      pill('море подмыло скалу, а не башню', 125, 230, t, tMove + 0.3, { dot: SKY, align: 'left', size: 40 }); pill('верх башни собрали на берегу в Плимуте', 125, 330, t, tMove + 3.0, { dot: MINT, align: 'left', size: 40 });
      title('отец гражданского', 120, 560, t, tFather, { size: 84, align: 'left' }); title('строительства', 120, 660, t, tFather + 0.4, { size: 84, align: 'left', color: PURPLE });
      pill('его опыты → путь к современному цементу', 125, 790, t, tFather + 2.6, { dot: SAND, align: 'left', size: 38 }); }],
  ], end);
}

// ═════════ s05b. Ржавчина и мост ═════════
const BRIDGE = (() => {
  const S = newScene({ bg: 0xdfe3ea, floorY: 0, key: [8, 14, 9], shadowSize: 24 });
  S.ground.material.color.set(0xdcd9d0);
  const cm = concrete({ base: '#cfccc5', seed: 450 });
  const spans = [];
  for (let i = 0; i < 3; i++) { const g = new THREE.Group(); g.position.x = (i - 1) * 9; S.scene.add(g);
    const deck = rbox(8.8, 0.5, 2.0, cm, 0.05); deck.position.y = 6; g.add(deck);
    const legA = rbox(0.6, 6, 0.6, cm, 0.05); legA.position.set(0, 3, 0); g.add(legA);
    const twr = new THREE.Group(); g.add(twr); for (const s of [-1, 1]) { const l = rbox(0.4, 6, 0.4, cm, 0.05); l.position.set(s * 0.9, 9, 0); l.rotation.z = -s * 0.15; twr.add(l); }
    const stays = []; for (const s of [-1, 1]) { const st = rbox(0.12, 6.6, 0.18, cm, 0.04); st.position.set(s * 2.0, 8.9, 0); st.rotation.z = s * 0.65; g.add(st); stays.push(st); }
    shadowAll(g); spans.push({ g, deck, stays });
  }
  const houses = []; for (let i = 0; i < 10; i++) { const h = 1.2 + hash(i) * 2; const b = rbox(1.6, h, 1.4, matte([0xf2d7b6, 0xe9c9a8, 0xf0e2c8][i % 3]), 0.1); b.position.set(-12 + i * 2.6, h / 2, -5); S.scene.add(b); houses.push(b); }
  return { ...S, spans };
})();
const PILE = (() => {
  const S = newScene({ bg: 0xe6e3dc, floorY: 0, key: [6, 12, 8], shadowSize: 16 });
  const blocks = []; const cm = concrete({ base: '#c8c4bd', seed: 455 });
  for (let i = 0; i < 120; i++) { const b = rbox(0.9, 0.9, 0.9, cm, 0.08); const lay = Math.floor(i / 30), j = i % 30; b.position.set((j % 6) * 0.95 - 2.4, 0.45 + lay * 0.92, Math.floor(j / 6) * 0.95 - 2); S.scene.add(b); blocks.push(b); }
  const man = new THREE.Group(); const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.18, 0.7, 6, 12), matte(C.coral)); body.position.y = 0.55; man.add(body); const hd = sphere(0.15, matte(0xf1c9a8)); hd.position.y = 1.12; man.add(hd); man.position.set(3.6, 0, 1.5); S.scene.add(shadowAll(man));
  const water = new THREE.Mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.2, 40), gloss(0x7fc0db, { roughness: 0.1 })); water.position.set(-5, 0.1, 0); S.scene.add(water);
  return { ...S, blocks };
})();
function cycle2d(items, cx, cy, r, t, t0, { size = 38 } = {}) {
  const n = items.length; const k0 = easeOut(seg(t, t0, t0 + 0.8)); if (k0 <= 0) return;
  ctx.save(); ctx.globalAlpha = k0; ctx.strokeStyle = '#7a63e6'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  const rot = t * 0.15;
  for (let i = 0; i < n; i++) { const a0 = rot + (i / n) * Math.PI * 2 + 0.35, a1 = rot + ((i + 1) / n) * Math.PI * 2 - 0.35; const kk = easeOut(seg(t, t0 + i * 0.5, t0 + i * 0.5 + 0.7)); if (kk <= 0) continue; ctx.beginPath(); ctx.arc(cx, cy, r, a0, lerp(a0, a1, kk)); ctx.stroke();
    if (kk > 0.95) { const ax = cx + Math.cos(a1) * r, ay = cy + Math.sin(a1) * r; ctx.save(); ctx.translate(ax, ay); ctx.rotate(a1 + Math.PI / 2); ctx.fillStyle = '#7a63e6'; ctx.beginPath(); ctx.moveTo(10, 0); ctx.lineTo(-10, -12); ctx.lineTo(-10, 12); ctx.fill(); ctx.restore(); } }
  items.forEach((it, i) => { const a = rot + (i / n) * Math.PI * 2; const kk = spring(seg(t, t0 + i * 0.5, t0 + i * 0.5 + 0.8) * 1.2, 8, 6); if (kk <= 0.01) return; const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
    ctx.font = `800 ${size}px "Rubik"`; const tw = ctx.measureText(it.text).width + 50; ctx.save(); ctx.translate(x, y); ctx.scale(clamp(kk, 0, 1.2), clamp(kk, 0, 1.2));
    ctx.shadowColor = 'rgba(60,40,80,0.2)'; ctx.shadowBlur = 24; ctx.beginPath(); ctx.roundRect(-tw / 2, -size * 0.85, tw, size * 1.7, size * 0.85); ctx.fillStyle = it.bg || '#ffffff'; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.fillStyle = CSS.ink; ctx.textAlign = 'center'; ctx.fillText(it.text, 0, size * 0.35); ctx.restore(); });
  ctx.restore();
}
export function s05b(t) {
  const id = 's05b';
  const tR = fc(id, 'прут', 0, 0.1), tCyc = fc(id, 'появляются', 0, 0.18), tG = fc(id, 'четырнадцатого', 0, 0.27), tInv = fc(id, 'итальянские', 0, 0.4), tSym = fc(id, 'но', 0, 0.5),
    tMuch = fc(id, 'бетона', 1, 0.66), tUN = fc(id, 'данным', 0, 0.7), tSec = fc(id, 'второе', 0, 0.8), tPer = fc(id, 'почти', 0, 0.9), end = 200;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = BEAM; beamAt(S, t, 0.3, smooth(seg(t, 1, tR + 3)), 0, 1); S.b.bars.forEach((b, i) => { if (i < 4) b.scale.set(1 + 1.3 * smooth(seg(t, tR, tR + 4)), 1, 1 + 1.3 * smooth(seg(t, tR, tR + 4))); });
      orbit(S.cam, v3(0.6, -0.2, 1.1), lerp(7.5, 6, k), lerp(0.45, 0.25, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, -0.2, 1.1), 0.001) });
      title('ржавчина', 120, 230, t, 0.3, { size: 110, align: 'left', color: '#b4572d', out: tCyc - 0.2 }); title('занимает больше места, чем сталь', 120, 340, t, 1.2, { size: 60, align: 'left', out: tCyc - 0.2 });
      pill('прут раздувается и распирает бетон', 125, 450, t, tR + 0.6, { dot: RED, align: 'left', size: 40, out: tCyc - 0.2 }); }],
    [tCyc, (lt, k) => { const S = BEAM; beamAt(S, t, 1, 1, easeIn(seg(t, tCyc + 1, tCyc + 4)), 1); orbit(S.cam, v3(0, 0.3, 0), lerp(11, 9.5, k), lerp(0.55, 0.4, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.3, 1.1), 0.0006), vig: 0.3 });
      cycle2d([{ text: 'трещина' }, { text: 'вода и соль', bg: '#d9f0fa' }, { text: 'ржавчина', bg: '#f6d4c4' }, { text: 'распирает' }], 1450, 470, 260, t, tCyc + 0.3);
      title('замкнутый круг', 120, 230, t, tCyc + 2.6, { size: 90, align: 'left' }); }],
    [tG, (lt, k) => { const S = BRIDGE; const fall = easeIn(seg(t, tG + 3.0, tG + 4.6)); const sp = S.spans[1]; sp.deck.position.y = lerp(6, 0.4, fall); sp.deck.rotation.z = fall * 0.15; sp.stays.forEach((s) => (s.visible = fall < 0.05));
      orbit(S.cam, v3(0, 5, 0), lerp(34, 28, k), lerp(0.35, 0.15, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 5, 0), 0.0004), vig: 0.3 });
      pill('Генуя · 14 августа 2018', 125, 230, t, tG + 0.3, { dot: RED, align: 'left', size: 42 }); pill('мост Моранди · 43 погибших', 125, 330, t, tG + 2.6, { dot: '#6b6b78', align: 'left', size: 42 }); pill('мосту ≈ 50 лет', 125, 430, t, tG + 6.0, { dot: SAND, align: 'left', size: 40 }); }],
    [tInv, (lt, k) => { const S = BRIDGE; const sp = S.spans[1]; sp.deck.position.y = 0.4; sp.stays.forEach((s) => (s.visible = false)); const sp0 = S.spans[2];
      orbit(S.cam, v3(9, 8.5, 0), lerp(9, 7, k), lerp(0.5, 0.2, k), 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(9, 8.5, 0), 0.0009), vig: 0.28 });
      pill('подозрение: коррозия стальных тросов в бетоне', 125, 230, t, tInv + 0.3, { dot: '#b4572d', align: 'left', size: 38 }); pill('расследование и суд — годами', 125, 330, t, tInv + 3.6, { dot: '#6b6b78', align: 'left', size: 38 });
      title('сила — от стали,', 120, 560, t, tSym + 1.0, { size: 84, align: 'left' }); title('а сталь боится воды', 120, 665, t, tSym + 1.6, { size: 84, align: 'left', color: '#b4572d' }); }],
    [tMuch, (lt, k) => { const S = PILE; S.blocks.forEach((b, i) => { const kk = easeOut(seg(t, tMuch + 0.4 + i * 0.03, tMuch + 0.9 + i * 0.03)); b.scale.setScalar(Math.max(0.01, kk)); });
      orbit(S.cam, v3(0, 1.6, 0), lerp(15, 12, k), lerp(0.7, 0.4, k), 0.28); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1.6, 0), 0.0007) });
      counter(Math.round(lerp(0, 12, easeOut(seg(t, tUN, tUN + 2)))) + ' млрд т', 120, 330, { size: 150, align: 'left', color: PURPLE }); title('бетона в год · ООН', 130, 420, t, tUN + 0.6, { size: 54, align: 'left' });
      pill('№2 по объёму после воды', 125, 560, t, tSec, { dot: SKY, align: 'left', size: 42 }); pill('≈ 3 т на каждого жителя Земли', 125, 660, t, tPer, { dot: SAND, align: 'left', size: 42 }); }],
  ], end);
}

// ═════════ s06b. Почему пепел ═════════
const GLASS = (() => {
  const S = newScene({ bg: 0x2e2a3a, floor: false, key: [3, 6, 5], keyI: 2.2, fill: 0.5 });
  S.scene.fog = new THREE.Fog(0x2e2a3a, 8, 30);
  const gl = new THREE.MeshPhysicalMaterial({ color: 0xbfc6d6, transmission: 0.7, roughness: 0.15, thickness: 0.6, transparent: true, opacity: 0.9, clearcoat: 1 });
  const drops_ = []; for (let i = 0; i < 18; i++) { const s = sphere(0.25 + hash(i) * 0.35, gl, 24); s.position.set((hash(i * 3) - 0.5) * 7, (hash(i * 5) - 0.5) * 4, -1 - hash(i * 7) * 4); S.scene.add(s); drops_.push(s); }
  const si = [], al = [], ca = [];
  const mk = (arr, n, col, r, seed) => { for (let i = 0; i < n; i++) { const s = sphere(r, gloss(col, { emissive: col, emissiveIntensity: 0.25 }), 14); s.position.set((hash(i + seed) - 0.5) * 6, (hash(i * 2 + seed) - 0.5) * 3.6, (hash(i * 3 + seed) - 0.5) * 2); S.scene.add(s); arr.push(s); } };
  mk(si, 14, 0x8fb8ff, 0.12, 470); mk(al, 10, 0xc7b8ff, 0.12, 480); mk(ca, 14, 0xffffff, 0.14, 490);
  const xt = []; for (let i = 0; i < 26; i++) { const c = crystal(0.14 + hash(i) * 0.12, [0xffe7a3, 0xa9e6cf, 0xf3d1ff][i % 3]); c.position.set((hash(i + 500) - 0.5) * 5, (hash(i + 510) - 0.5) * 3, (hash(i + 520) - 0.5) * 2); c.rotation.set(hash(i) * 3, hash(i + 1) * 3, 0); S.scene.add(c); xt.push(c); }
  const lbl = [textSprite('кремний', { size: 54, bg: '#d9e6ff', scale: 0.9 }), textSprite('алюминий', { size: 54, bg: '#e6ddff', scale: 0.9 }), textSprite('кальций (известь)', { size: 54, scale: 0.9 })];
  lbl[0].position.set(-2.2, 1.25, 0.5); lbl[1].position.set(0.1, 1.45, 0.5); lbl[2].position.set(2.2, 1.2, 0.5); lbl.forEach((l) => S.scene.add(l));
  return { ...S, drops_, si, al, ca, xt, lbl };
})();
export function s06b(t) {
  const id = 's06b';
  const tDrop = fc(id, 'пепел', 1, 0.08), tGl = fc(id, 'получилось', 0, 0.17), tMeet = fc(id, 'когда', 0, 0.25), tNew = fc(id, 'образуются', 0, 0.36), tPz = fc(id, 'такие', 0, 0.43),
    tKn = fc(id, 'римляне', 0, 0.53), tVit = fc(id, 'витрувий', 0, 0.6), tShip = fc(id, 'поэтому', 0, 0.9), end = 200;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = VOLC; S.ash.userData.update(t, 2.0); S.sea.userData.update(t, 0.5); orbit(S.cam, v3(0, 3.5, -6), lerp(30, 24, k), lerp(-0.4, -0.1, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 4, -6), 0.0005) });
      title('почему пепел?', 120, 230, t, 0.3, { size: 110, align: 'left', out: tGl - 0.2 }); pill('капли расплава застыли в воздухе', 125, 350, t, tDrop + 0.3, { dot: RED, align: 'left', size: 40, out: tGl - 0.2 }); }],
    [tGl, (lt, k) => { const S = GLASS; S.xt.forEach((c) => (c.visible = false)); S.lbl.forEach((l) => (l.visible = false)); S.si.concat(S.al, S.ca).forEach((s) => (s.visible = false));
      S.drops_.forEach((d, i) => { d.position.y += 0; d.rotation.y = t * 0.3; }); S.cam.position.set(Math.sin(t * 0.1) * 1.5, 0.2, 5.5 - lt * 0.12); S.cam.lookAt(0, 0, -2); S.cam.updateMatrixWorld();
      render(S.scene, S.cam, { time: t, focus: 6, aperture: 0.0018, maxblur: 0.012 });
      title('вулканическое стекло', 120, 230, t, tGl + 0.3, { size: 90, align: 'left', color: '#ffffff' }); pill('много кремния и алюминия', 125, 345, t, tGl + 1.5, { dot: '#8fb8ff', align: 'left', size: 40 }); }],
    [tMeet, (lt, k) => { const S = GLASS; S.drops_.forEach((d) => (d.visible = false)); S.si.concat(S.al, S.ca).forEach((s, i) => { s.visible = true; const mv = easeInOut(seg(t, tMeet + 1 + hash(i) * 2, tNew + 1)); const tgt = S.xt[i % S.xt.length].position; s.position.lerp(tgt, mv * 0.04); });
      S.xt.forEach((c, i) => { c.visible = true; c.scale.setScalar(Math.max(0.001, easeOut(seg(t, tNew + i * 0.12, tNew + 1 + i * 0.12)))); c.rotation.y += 0.0; });
      S.lbl.forEach((l, i) => popScale(l, t, tMeet + 0.4 + i * 0.5));
      orbit(S.cam, v3(0, 0, 0), lerp(8, 6.5, k), lerp(-0.3, 0.3, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0), 0.0012) });
      title('+ известь + вода', 120, 900, t, tMeet + 0.6, { size: 70, align: 'left', color: '#ffffff', out: tNew - 0.2 }); title('= новые минералы-«клей»', 120, 900, t, tNew + 0.4, { size: 70, align: 'left', color: '#a9e6cf' }); }],
    [tPz, (lt, k) => { const S = VOLC; S.ash.userData.update(t, 0.8); S.sea.userData.update(t, 0.6); orbit(S.cam, v3(0, 1, 6), lerp(26, 20, k), lerp(0.4, 0.15, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1, 6), 0.0005) });
      title('пуццоланы', 120, 230, t, tPz + 0.3, { size: 110, align: 'left' }); pill('в честь Поццуоли', 125, 345, t, tPz + 1.4, { dot: SAND, align: 'left', size: 42 }); pill('римляне понимали: материал особый', 125, 445, t, tKn + 0.2, { dot: PURPLE, align: 'left', size: 40 }); }],
    [tVit, (lt, k) => { const S = CAES; S.sea.userData.update(t, 0.8); S.ship.position.x = -9 + lt * 0.3; S.ship.position.y = S.sea.userData.h(S.ship.position.x, 6, t, 0.8) + 0.1;
      orbit(S.cam, v3(S.ship.position.x, 1, 6), lerp(14, 11, k), lerp(-0.6, -0.3, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(S.ship.position.x, 1, 6), 0.0008) });
      quote('есть порошок… у Байи и вокруг Везувия. С известью и щебнем он даёт прочность постройкам, и даже опоры в море твердеют под водой', 'Витрувий, «Десять книг об архитектуре», II', 110, 150, t, tVit + 0.2, tShip, { w: 980, size: 42 });
      pill('пепел возили кораблями через всё Средиземное море', 125, 900, t, tShip + 0.2, { dot: SKY, align: 'left', size: 40 }); }],
  ], end);
}

// ═════════ s06c. Римская стройка ═════════
const BUILD = (() => {
  const S = newScene({ bg: 0xf1e3d1, floorY: 0, key: [-6, 12, 9], shadowSize: 14 });
  S.ground.material = stone({ base: '#dcc9b0', dots: '#b89f84', dots2: '#ecdcc6', n: 800, seed: 600, rep: 10 });
  const tuf = stone({ base: '#d2b98f', dots: '#a88f69', dots2: '#e8d6b4', n: 500, seed: 601 });
  const skins = [], core = [];
  const L = 6;
  for (let r = 0; r < 8; r++) for (let side of [-1, 1]) for (let c = 0; c < 8; c++) { const b = rbox(0.72, 0.3, 0.3, (r + c) % 4 ? tuf : brick(), 0.04); b.position.set(-L / 2 + 0.4 + c * 0.75 + (r % 2) * 0.2, 0.16 + r * 0.32, side * 0.75); S.scene.add(b); skins.push({ b, r }); }
  for (let r = 0; r < 8; r++) { const m = rbox(L - 0.3, 0.3, 1.15, concrete({ seed: 610 + r, clasts: 6 }), 0.03); m.position.set(0, 0.16 + r * 0.32, 0); S.scene.add(m); const st = lumps(9, 0.13, stone({ base: '#8f857c', seed: 620 + r }), r * 7); st.children.forEach((s, i) => s.position.set(-L / 2 + 0.5 + i * 0.6, 0.18, (hash(i + r) - 0.5) * 0.7)); st.position.y = 0.16 + r * 0.32; S.scene.add(st); core.push({ m, st, r }); }
  const scaff = new THREE.Group(); for (const x of [-3.6, 3.6]) for (const z of [-1.5, 1.5]) { const p = cyl(0.06, 3.6, wood(), 10); p.position.set(x, 1.8, z); scaff.add(p); } for (const y of [1.2, 2.4]) { const pl = rbox(7.6, 0.08, 0.5, wood(), 0.02); pl.position.set(0, y, 1.5); scaff.add(pl); } S.scene.add(shadowAll(scaff));
  const bk = bucket(); bk.position.set(2.6, 0, 2.6); S.scene.add(bk); const tr = trowel(); tr.position.set(1.8, 0.05, 2.9); S.scene.add(tr);
  return { ...S, skins, core };
})();
const WALLS = (() => {
  const S = newScene({ bg: 0xe9e2f2, floorY: 0, key: [4, 10, 10], shadowSize: 14 });
  const mor = matte(0xe8e0d0);
  const mk = (x) => { const back = rbox(3.2, 3.2, 0.3, mor, 0.03); back.position.set(x, 1.7, -0.1); S.scene.add(back); const g = new THREE.Group(); g.position.set(x, 1.7, 0.1); S.scene.add(g); return g; };
  const inc = mk(-4); for (let i = 0; i < 46; i++) { const s = rbox(0.3 + hash(i) * 0.3, 0.22 + hash(i + 1) * 0.25, 0.18, stone({ base: '#b8ab98', seed: 640 + (i % 5) }), 0.08); s.position.set((hash(i * 3) - 0.5) * 2.8, (hash(i * 5) - 0.5) * 2.8, 0.05); s.rotation.z = hash(i * 7) * 3; inc.add(s); }
  const ret = mk(0); const tufM = stone({ base: '#d8c39c', dots: '#ad966f', dots2: '#efe0c2', n: 300, seed: 650 }); for (let i = -5; i <= 5; i++) for (let j = -5; j <= 5; j++) { if (Math.abs(i) + Math.abs(j) > 6) continue; const s = rbox(0.34, 0.34, 0.16, tufM, 0.03); s.rotation.z = Math.PI / 4; s.position.set((i + j) * 0.25, (i - j) * 0.25, 0.05); if (Math.abs(s.position.x) < 1.5 && Math.abs(s.position.y) < 1.5) ret.add(s); }
  const tes = mk(4); for (let r = 0; r < 12; r++) for (let c = 0; c < 6; c++) { const b = rbox(0.48, 0.2, 0.16, brick(), 0.02); b.position.set(-1.3 + c * 0.52 + (r % 2) * 0.26 - 0.13, -1.4 + r * 0.245, 0.05); if (Math.abs(b.position.x) < 1.55) tes.add(b); }
  shadowAll(S.scene);
  const labels = ['opus incertum', 'opus reticulatum', 'opus testaceum'].map((s) => textSprite(s, { size: 56, scale: 1.0 }));
  labels.forEach((l, i) => { l.position.set(-4 + i * 4, 3.55, 0.2); S.scene.add(l); });
  return { ...S, inc, ret, tes, labels };
})();
const MARKET = (() => {
  const S = newScene({ bg: 0xf3dfcf, floorY: 0, key: [-4, 14, 12], shadowSize: 22 });
  S.ground.material = stone({ base: '#e2d0bb', dots: '#c2ab92', dots2: '#efe2d1', n: 700, seed: 660, rep: 14 });
  const g = new THREE.Group(); S.scene.add(g); const bm = brick();
  for (let lev = 0; lev < 3; lev++) { const R = 9 - lev * 1.6; const n = 12 - lev * 2; for (let i = 0; i < n; i++) { const a = -Math.PI / 2 + (i + 0.5) / n * Math.PI; const bay = new THREE.Group(); bay.position.set(Math.sin(a) * R, lev * 2.2, -Math.cos(a) * R * 0.75); bay.rotation.y = -a; g.add(bay);
    const wl = rbox(1.9, 2.2, 0.5, bm, 0.04); wl.position.y = 1.1; bay.add(wl); const door = rbox(0.9, lev ? 1.0 : 1.4, 0.1, matte(0x5a3a2c), 0.03); door.position.set(0, lev ? 1.1 : 0.75, 0.27); bay.add(door);
    const arch = new THREE.Mesh(new THREE.TorusGeometry(0.45, 0.09, 8, 16, Math.PI), stone({ base: '#efe6d8', seed: 661 })); arch.position.set(0, lev ? 1.6 : 1.45, 0.3); bay.add(arch); }
    const fl = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.5, R + 0.5, 0.25, 40, 1, false, -Math.PI / 2, Math.PI), stone({ base: '#e8dccb', seed: 662 + lev })); fl.scale.z = 0.75; fl.rotation.y = Math.PI; fl.position.y = (lev + 1) * 2.2; g.add(fl); }
  const vault = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 9, 24, 1, true, 0, Math.PI), concrete({ seed: 663 })); vault.material.side = THREE.DoubleSide; vault.rotation.z = Math.PI / 2; vault.position.set(0, 7.4, -9); g.add(vault);
  shadowAll(g);
  const people = []; for (let i = 0; i < 8; i++) { const p = new THREE.Group(); const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.14, 0.45, 6, 12), matte([C.coral, C.lav, C.mint, C.butter][i % 4])); b.position.y = 0.4; p.add(b); const h = sphere(0.1, matte(0xf1c9a8)); h.position.y = 0.8; p.add(h); S.scene.add(shadowAll(p)); people.push(p); }
  return { ...S, people };
})();
export function s06c(t) {
  const id = 's06c';
  const tOp = fc(id, 'сам', 0, 0.02), tCm = fc(id, 'отсюда', 0, 0.08), tDate = fc(id, 'появился', 0, 0.11), tPour = fc(id, 'его', 0, 0.15), tSk = fc(id, 'облицовка', 0, 0.25),
    tInc = fc(id, 'самая', 0, 0.33), tRet = fc(id, 'примерно', 0, 0.39), tVit = fc(id, 'витрувий', 0, 0.48), tTes = fc(id, 'после', 0, 0.54), tMk = fc(id, 'бетон', 1, 0.63), tApo = fc(id, 'их', 0, 0.72), tMall = fc(id, 'его', 1, 0.86), end = 200;
  clear2d();
  const B = BUILD; const grow = clamp(seg(t, tPour, tSk + 4) * 8.5);
  B.skins.forEach(({ b, r }) => (b.visible = r < grow + 0.5)); B.core.forEach(({ m, st, r }) => { m.visible = r < grow - 0.3; st.visible = r < grow; });
  shot(t, [
    [0, (lt, k) => { orbit(B.cam, v3(0, 1.3, 0), lerp(14, 11, k), lerp(0.6, 0.35, k), 0.3); render(B.scene, B.cam, { time: t, ...dof(B.cam, v3(0, 1.3, 0), 0.0008) });
      title('opus caementicium', 120, 230, t, tOp + 0.3, { size: 92, align: 'left', font: 'Rubik' }); pill('caementa — куски камня → «цемент»', 125, 345, t, tCm + 0.2, { dot: SAND, align: 'left', size: 40 }); pill('с конца III в. до н. э.', 125, 445, t, tDate + 0.2, { dot: PURPLE, align: 'left', size: 40 }); }],
    [tPour, (lt, k) => { orbit(B.cam, v3(0, 1.0, 0), lerp(8, 6.5, k), lerp(-0.9, -0.5, k), 0.45); render(B.scene, B.cam, { time: t, ...dof(B.cam, v3(0, 1.0, 0), 0.0012) });
      pill('не сплошная опалубка, как сейчас', 125, 230, t, tPour + 0.3, { dot: RED, align: 'left', size: 40 }); pill('две облицовки + слои раствора и камней «с кулак»', 125, 330, t, tPour + 3.0, { dot: SAND, align: 'left', size: 38 });
      pill('облицовка = форма + защита', 125, 430, t, tSk + 0.2, { dot: MINT, align: 'left', size: 40 }); }],
    [tInc, (lt, k) => { const S = WALLS; const x = t < tRet ? -4 : t < tTes ? 0 : 4; S.labels.forEach((l, i) => popScale(l, t, [tInc, tRet, tTes][i] + 0.3));
      const cx = lerp(S.cam.position.x || x, x, 1); orbit(S.cam, v3(x, 1.9, 0), lerp(9, 8.2, seg(t, tInc, tMk)), lerp(-0.12, 0.12, (t * 0.05) % 1), 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(x, 1.8, 0), 0.0012) });
      title('облицовка датирует стену', 120, 230, t, tInc + 0.2, { size: 72, align: 'left', out: tRet - 0.2 });
      pill('неровные камни · самая ранняя', 125, 900, t, tInc + 1.0, { dot: SAND, align: 'left', size: 38, out: tRet - 0.2 });
      pill('≈ с 100 г. до н. э. · квадраты туфа ромбами', 125, 900, t, tRet + 0.4, { dot: SAND, align: 'left', size: 38, out: tTes - 0.2 });
      stamp('Витрувий: трескается по швам', 1250, 250, t, tVit + 1.5, { size: 46, out: tTes - 0.3 });
      pill('после пожара 64 г. (Нерон) — кирпич', 125, 900, t, tTes + 0.4, { dot: RED, align: 'left', size: 38, out: tMk - 0.2 }); }],
    [tMk, (lt, k) => { const S = MARKET; S.people.forEach((p, i) => { const a = ((t * 0.04 + i / 8) % 1) * Math.PI - Math.PI / 2; p.position.set(Math.sin(a) * 6.6, 0, -Math.cos(a) * 5 + 1.5); p.rotation.y = a; });
      orbit(S.cam, v3(0, 3.5, -3), lerp(30, 22, easeIO2(k)), lerp(0.45, -0.2, k), lerp(0.4, 0.22, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, -3), 0.0005) });
      title('рынки Траяна', 120, 230, t, tMk + 2.0, { size: 100, align: 'left' }); pill('≈ 100–110 гг. · архитектор Аполлодор Дамасский', 125, 345, t, tApo + 0.3, { dot: SAND, align: 'left', size: 38 });
      pill('лавки и конторы под бетонными сводами', 125, 445, t, tApo + 3.4, { dot: PURPLE, align: 'left', size: 38 }); pill('«древнейший торговый центр» · часть уровней открыта', 125, 545, t, tMall + 0.3, { dot: MINT, align: 'left', size: 36 }); }],
  ], end);
}

// ═════════ s07b. Круг извести ═════════
const LIME = (() => {
  const S = newScene({ bg: 0xf3eadf, floorY: 0, key: [5, 12, 8], shadowSize: 12 });
  const R = 5;
  const st = []; // 4 станции по кругу
  const a = (i) => (i / 4) * Math.PI * 2;
  const g0 = new THREE.Group(); const ls = rbox(1.6, 1.1, 1.2, stone({ base: '#e4dccd', dots: '#bdb19f', dots2: '#f5f0e8', n: 700, seed: 700 }), 0.12); ls.position.y = 0.55; g0.add(ls); const ch = rbox(0.6, 0.4, 0.5, stone({ base: '#e4dccd', seed: 701 }), 0.08); ch.position.set(1.2, 0.2, 0.4); g0.add(ch);
  const g1 = new THREE.Group(); const kl = kiln(); kl.scale.setScalar(0.6); g1.add(kl); const ksm = smoke(10); ksm.position.set(0, 1.9, 0); ksm.scale.setScalar(0.5); g1.add(ksm);
  const g2 = new THREE.Group(); const ql = lumps(10, 0.22, matte(0xfbfaf6), 702); ql.position.y = 0.2; g2.add(ql); const tub = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 0.85, 0.7, 32, 1, true), wood()); tub.material.side = THREE.DoubleSide; tub.position.y = 0.35; g2.add(tub); const steam = smoke(14, matte(0xffffff, { transparent: true, opacity: 0.85 })); steam.position.y = 0.5; steam.scale.setScalar(0.45); g2.add(steam); const wat = drops(20, 0x8fd0e6, 0.06); g2.add(wat);
  const g3 = new THREE.Group(); const pit = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 0.12, 40), matte(0xf7f3ea)); pit.position.y = 0.06; g3.add(pit); const rim = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.12, 8, 40), wood()); rim.rotation.x = Math.PI / 2; rim.position.y = 0.12; g3.add(rim);
  const wall = rbox(2.2, 1.4, 0.4, matte(0xf1ece2), 0.06); wall.position.set(0, 0.7, -1.5); g3.add(wall); const co2 = []; for (let i = 0; i < 10; i++) { const s = sphere(0.08, gloss(0xb8c4d6, { transparent: true, opacity: 0.8 }), 10); g3.add(s); co2.push(s); }
  [g0, g1, g2, g3].forEach((g, i) => { g.position.set(Math.sin(a(i)) * R, 0, Math.cos(a(i)) * R); S.scene.add(shadowAll(g)); st.push(g); });
  const lbl = ['известняк · CaCO₃', 'печь ≈ 900 °C', 'негашёная · CaO', 'гашёная · Ca(OH)₂'].map((s) => textSprite(s, { size: 52, scale: 0.9 }));
  lbl.forEach((l, i) => { l.position.set(Math.sin(a(i)) * R, i === 1 ? 2.6 : 1.7, Math.cos(a(i)) * R); S.scene.add(l); });
  const path = new THREE.Mesh(new THREE.TorusGeometry(R, 0.06, 8, 120), matte(0xd8c9f2)); path.rotation.x = Math.PI / 2; path.position.y = 0.03; S.scene.add(path);
  return { ...S, st, ksm, ql, steam, wat, co2, lbl, R, kl };
})();
export function s07b(t) {
  const id = 's07b', S = LIME;
  const tK = fc(id, 'если', 0, 0.12), tQ = fc(id, 'остаётся', 0, 0.22), tW = fc(id, 'если', 1, 0.33), tSl = fc(id, 'получается', 0, 0.48), tPit = fc(id, 'строители', 0, 0.54), tC = fc(id, 'потом', 0, 0.66), tCir = fc(id, 'круг', 0, 0.82), tRem = fc(id, 'запомни', 0, 0.93), end = 200;
  S.ksm.userData.update(t, 1.2); const boil = smooth(seg(t, tW + 0.5, tW + 2)) * (1 - smooth(seg(t, tSl + 3, tSl + 5)));
  S.steam.userData.update(t, 2); S.steam.visible = boil > 0.05; S.steam.scale.setScalar(0.45 * boil + 0.01);
  S.wat.userData.ps.forEach((p, i) => { const ph = (t * 1.2 + hash(i)) % 1; p.position.set(-0.6 + hash(i) * 0.3, lerp(2.2, 0.3, ph), (hash(i + 1) - 0.5) * 0.4); p.visible = t > tW && t < tW + 2.5; });
  S.ql.children.forEach((l, i) => { l.position.set((hash(i) - 0.5) * 1.2, 0.1 + boil * 0.04 * Math.sin(t * 20 + i), (hash(i + 4) - 0.5) * 1.2); });
  S.co2.forEach((s, i) => { const ph = (t * 0.3 + i / 10) % 1; s.position.set((hash(i) - 0.5) * 2, lerp(2.5, 0.8, ph), lerp(-0.2, -1.3, ph)); s.visible = t > tC; });
  S.lbl.forEach((l, i) => popScale(l, t, [0.8, tK + 0.5, tQ + 0.3, tSl + 0.3][i]));
  const target = (i) => v3(Math.sin((i / 4) * Math.PI * 2) * S.R, 0.8, Math.cos((i / 4) * Math.PI * 2) * S.R);
  const close = (i, lt, k, r0 = 7, r1 = 5.5) => { const az = (i / 4) * Math.PI * 2 + 0.3 - k * 0.5; orbit(S.cam, target(i), lerp(r0, r1, k), az, 0.35); render(S.scene, S.cam, { time: t, ...dof(S.cam, target(i), 0.0014) }); };
  clear2d();
  shot(t, [
    [0, (lt, k) => { close(0, lt, k); title('известь:', 120, 230, t, 0.3, { size: 100, align: 'left' }); title('в чём подвох', 120, 340, t, 0.8, { size: 90, align: 'left', color: PURPLE }); }],
    [tK, (lt, k) => { close(1, lt, k, 8, 6.5); pill('углекислый газ уходит', 125, 230, t, tK + 2.5, { dot: '#b8c4d6', align: 'left', size: 40 }); }],
    [tQ, (lt, k) => { close(2, lt, k); pill('жадно тянет воду', 125, 230, t, tQ + 2.0, { dot: SKY, align: 'left', size: 40 }); }],
    [tW, (lt, k) => { close(2, lt, k, 5.5, 4.2); title('шипит, парит,', 120, 230, t, tW + 1.2, { size: 90, align: 'left' }); title('кипит', 120, 340, t, tW + 1.8, { size: 100, align: 'left', color: RED }); }],
    [tSl, (lt, k) => { close(3, lt, k); pill('гасили заранее в ямах', 125, 230, t, tPit + 0.2, { dot: SAND, align: 'left', size: 40 }); pill('выдерживали пасту месяцами', 125, 330, t, tPit + 2.4, { dot: SAND, align: 'left', size: 40 }); }],
    [tC, (lt, k) => { close(3, lt, k, 5, 4); pill('забирает CO₂ из воздуха', 125, 230, t, tC + 0.6, { dot: '#b8c4d6', align: 'left', size: 40 }); pill('→ снова CaCO₃, камень', 125, 330, t, tC + 2.6, { dot: MINT, align: 'left', size: 40 }); }],
    [tCir, (lt, k) => { orbit(S.cam, v3(0, 0.5, 0), lerp(20, 17, k), t * 0.12, lerp(0.75, 0.9, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.5, 0), 0.0006) });
      title('камень → печь → раствор → камень', 120, 200, t, tCir + 0.2, { size: 64, align: 'left' }); pill('запомни этот круг — он про трещины', 125, 900, t, tRem + 0.3, { dot: PURPLE, align: 'left', size: 42 }); }],
  ], end);
}

// ═════════ s10c. РОМАКОНС ═════════
const DRILL = (() => {
  const S = newScene({ bg: 0xcde4f2, floor: false, key: [6, 12, 4], shadowSize: 16 });
  const sea = waves(80, 50, 80, gloss(0x7fc0db, { roughness: 0.15 })); S.scene.add(sea);
  const pr = pier(3); pr.position.set(0, 0.2, 0); S.scene.add(pr);
  const rig = new THREE.Group(); rig.position.set(0, 2.05, 0); S.scene.add(rig);
  for (const [x, z] of [[-0.9, -0.6], [0.9, -0.6], [0, 0.8]]) { const l = cyl(0.06, 3.0, metal(0xc9cbd6), 10); l.position.set(x * 0.6, 1.3, z * 0.6); l.rotation.set(-z * 0.25, 0, x * 0.25); rig.add(l); }
  const motor = rbox(0.6, 0.5, 0.6, gloss(C.coral), 0.1); motor.position.y = 2.8; rig.add(motor);
  const lbl = plaque('ITALCEMENTI', { w: 0.58, h: 0.12, size: 140, color: '#ffffff', serif: false, spacing: 2 }); lbl.position.set(0, 2.8, 0.31); rig.add(lbl);
  const core = cyl(0.2, 2.2, stone({ base: '#7d7573', dots: '#ffffff', dots2: '#5b5552', n: 600, seed: 760 }), 20); rig.add(core);
  shadowAll(rig);
  const bt = boat(); bt.position.set(6, 0, 5); bt.rotation.y = 0.5; bt.scale.setScalar(0.8); S.scene.add(bt);
  const cores = []; for (let i = 0; i < 4; i++) { const c = cyl(0.2, 1.6, stone({ base: '#8a827e', dots: '#ffffff', dots2: '#6e6763', n: 600, seed: 761 + i }), 20); c.rotation.z = Math.PI / 2; c.position.set(-2.2 + i * 0.5, 2.25, 1.0); S.scene.add(c); cores.push(c); }
  return { ...S, sea, core, bt, cores };
})();
const UNDER = (() => {
  const S = newScene({ bg: 0x2f6f8f, floorY: -3, key: [2, 12, 3], keyI: 2.0, fill: 0.6 });
  S.scene.fog = new THREE.Fog(0x2f6f8f, 6, 26); S.ground.material = stone({ base: '#b8ae94', dots: '#8f866f', dots2: '#d8cfb6', n: 800, seed: 770, rep: 8 });
  const blk = rbox(5, 2.4, 3, concrete({ base: '#a49e8a', seed: 771, clasts: 10 }), 0.1); blk.position.set(0, -1.8, -1); S.scene.add(blk);
  for (let i = 0; i < 9; i++) { const w = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 1.2 + hash(i), 4, 8), matte(0x6fa87a)); w.position.set(-3 + i * 0.8, -2.4, 1.5 + hash(i) * 1.5); S.scene.add(w); }
  const dv = diver(); dv.position.set(1.2, -0.2, 1.0); dv.rotation.y = -0.6; dv.scale.setScalar(0.8); S.scene.add(dv);
  const dr = cyl(0.08, 1.0, metal(0x9aa0aa), 12); dr.rotation.x = Math.PI / 2.4; dr.position.set(0.6, -0.4, 0.2); S.scene.add(dr);
  const bub = drops(30, 0xe8f6ff, 0.06); S.scene.add(bub);
  const rays = []; for (let i = 0; i < 4; i++) { const r = lightBeam(14, 0.4, 1.6, 0xcff4ff); r.position.set(-4 + i * 3, 5, -3 + i); r.rotation.z = 0.2; S.scene.add(r); rays.push(r); }
  return { ...S, dv, bub };
})();
function medMap(t, t0, pins, { x = 1080, y = 250, w = 760, h = 430 } = {}) {
  const k = easeOut(seg(t, t0, t0 + 0.8)); if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = k; ctx.translate(x, y + 20 * (1 - k));
  ctx.shadowColor = 'rgba(40,60,80,0.2)'; ctx.shadowBlur = 40; ctx.beginPath(); ctx.roundRect(0, 0, w, h, 36); ctx.fillStyle = '#d9eef8'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#efe4cf';
  const land = [[[0, 0], [w, 0], [w, 90], [560, 120], [470, 70], [380, 140], [330, 90], [250, 60], [180, 120], [90, 100], [0, 140]], [[300, 95], [345, 120], [420, 260], [445, 300], [410, 310], [360, 220], [310, 150]], [[0, h], [w, h], [w, 330], [600, 360], [420, 400], [250, 360], [0, 380]], [[w, 120], [w, 330], [700, 300], [690, 200]]];
  for (const poly of land) { ctx.beginPath(); poly.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py))); ctx.closePath(); ctx.fill(); }
  pins.forEach((p, i) => { const kk = spring(seg(t, p.t, p.t + 0.7) * 1.2, 8, 5); if (kk <= 0.01) return; ctx.save(); ctx.translate(p.x, p.y); ctx.scale(clamp(kk, 0, 1.3), clamp(kk, 0, 1.3)); ctx.fillStyle = p.c || '#e8706a'; ctx.beginPath(); ctx.arc(0, -18, 14, 0, Math.PI * 2); ctx.fill(); ctx.beginPath(); ctx.moveTo(-9, -12); ctx.lineTo(0, 4); ctx.lineTo(9, -12); ctx.fill(); if (p.label) { ctx.font = '700 26px "Rubik"'; ctx.fillStyle = CSS.ink; ctx.fillText(p.label, 18, -10); } ctx.restore(); });
  ctx.restore();
}
export function s10c(t) {
  const id = 's10c';
  const tHow = fc(id, 'но', 0, 0.06), tTeam = fc(id, 'в', 0, 0.2), tIt = fc(id, 'итальянская', 0, 0.36), tDr = fc(id, 'команда', 0, 0.48), tUw = fc(id, 'иногда', 0, 0.6), tCo = fc(id, 'две', 0, 0.68), tAll = fc(id, 'потом', 0, 0.85), end = 200;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = SEA; S.sea.userData.update(t, 1.0); orbit(S.cam, v3(-1, 1, 0), lerp(26, 18, easeIO2(k)), lerp(0.9, 0.5, k), lerp(0.3, 0.14, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1, 1, 0), 0.0005) });
      chapter(5, 'Море', t, 0.2, 5.5); title('как изучить бетон', 120, 900, t, tHow + 0.2, { size: 64, align: 'left', out: tTeam - 0.2 }); }],
    [tTeam, (lt, k) => { const S = DRILL; S.sea.userData.update(t, 0.9); S.core.position.y = -1.2; S.core.rotation.y = t * 3; S.cores.forEach((c) => (c.visible = false));
      orbit(S.cam, v3(0, 2.5, 0), lerp(13, 10, k), lerp(0.7, 0.4, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, 0), 0.0008) });
      title('ROMACONS', 120, 230, t, tTeam + 0.4, { size: 110, align: 'left' }); pill('Джон Олесон · Кристофер Брэндон · Роберт Холфельдер', 125, 345, t, tTeam + 1.4, { dot: SKY, align: 'left', size: 34 });
      pill('буровую дала компания Italcementi', 125, 445, t, tIt + 0.3, { dot: SAND, align: 'left', size: 38 }); }],
    [tDr, (lt, k) => { const S = DRILL; S.sea.userData.update(t, 0.9); const up = easeInOut(seg(t, tDr + 1.5, tDr + 6)); S.core.position.y = lerp(-1.2, 2.2, up); S.core.rotation.y = up < 1 ? t * 3 : 0; S.cores.forEach((c, i) => (c.visible = up > 0.9 && i < 3));
      orbit(S.cam, v3(0, 2.6, 0.3), lerp(6.5, 5, k), lerp(-0.4, 0.1, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2.6, 0.3), 0.0016) });
      pill('керн — длинный цилиндр бетона', 125, 230, t, tDr + 1.5, { dot: '#8f8783', align: 'left', size: 40 }); pill('из причалов и волнорезов', 125, 330, t, tDr + 3.4, { dot: SKY, align: 'left', size: 40 }); }],
    [tUw, (lt, k) => { const S = UNDER; S.bub.userData.ps.forEach((p, i) => { const ph = (t * 0.4 + hash(i)) % 1; p.position.set(1.2 + Math.sin(i + t) * 0.2 + (hash(i) - 0.5) * 0.3, lerp(0.6, 6, ph), 1.0 + (hash(i + 1) - 0.5) * 0.3); });
      S.dv.rotation.z = Math.sin(t * 0.8) * 0.05; orbit(S.cam, v3(0.6, -0.6, 0.6), lerp(7, 5.5, k), lerp(0.7, 0.3, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0.8, -0.4, 0.8), 0.0016), vig: 0.35 });
      pill('иногда — прямо под водой, с аквалангом', 125, 230, t, tUw + 0.3, { dot: '#cff4ff', align: 'left', size: 40 }); }],
    [tCo, (lt, k) => { const S = SEA; S.sea.userData.update(t, 0.8); orbit(S.cam, v3(-1, 0.6, 0), lerp(18, 22, k), lerp(-0.6, -0.9, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-1, 1, 0), 0.0005), vig: 0.3 });
      title('2003 · гавань Коза', 120, 230, t, tCo + 0.3, { size: 80, align: 'left' }); pill('Тоскана · возможно, древнейшие морские стройки из гидравлического бетона', 125, 335, t, tCo + 1.6, { dot: SAND, align: 'left', size: 30 });
      medMap(t, tAll, [{ x: 330, y: 130, t: tCo + 0.6, label: 'Коза' }, { x: 350, y: 175, t: tAll + 0.5, label: 'Байи' }, { x: 690, y: 290, t: tAll + 1.0, label: 'Кесария' }, { x: 520, y: 360, t: tAll + 1.4, label: 'Александрия' }, { x: 440, y: 300, t: tAll + 1.8 }, { x: 600, y: 130, t: tAll + 2.1 }], { x: 1060, y: 440 });
      pill('керны → целая волна исследований', 125, 900, t, tAll + 2.6, { dot: MINT, align: 'left', size: 40 }); }],
  ], end);
}

// ═════════ s12b. Что нашли в Помпеях ═════════
const FINDS = (() => {
  const S = newScene({ bg: 0xeee0cf, floorY: 0, key: [-4, 10, 7], keyI: 3.0 });
  const desk = rbox(10, 0.3, 6, stone({ base: '#d8c3a8', seed: 800 }), 0.06); desk.position.y = -0.15; S.scene.add(desk);
  const plumb = new THREE.Group(); const cone = new THREE.Mesh(new THREE.ConeGeometry(0.25, 0.6, 24), metal(0x8a8c90, { roughness: 0.5 })); cone.rotation.x = Math.PI; cone.position.y = 0.3; plumb.add(cone); const cap = sphere(0.25, metal(0x8a8c90, { roughness: 0.5 })); cap.scale.y = 0.5; cap.position.y = 0.62; plumb.add(cap); const str = cyl(0.01, 2.2, matte(0xd8c9a8), 6); str.position.y = 1.7; plumb.add(str); plumb.position.set(-2.2, 0.6, 0); S.scene.add(shadowAll(plumb));
  const weights = []; for (let i = 0; i < 3; i++) { const w = puck(0.3 - i * 0.06, 0.24 - i * 0.04, metal(0x6e7076, { roughness: 0.55 })); w.position.set(-0.6 + i * 0.7, 0.12, 1.2); S.scene.add(w); weights.push(w); }
  const sq = new THREE.Group(); const a1 = rbox(1.6, 0.08, 0.18, metal(C.bronze, { roughness: 0.4 }), 0.02); a1.position.x = 0.8; sq.add(a1); const a2 = rbox(0.18, 0.08, 1.2, metal(C.bronze, { roughness: 0.4 }), 0.02); a2.position.z = -0.6; sq.add(a2); sq.position.set(1.2, 0.05, -0.6); S.scene.add(shadowAll(sq));
  const tr = trowel(); tr.position.set(2.8, 0.05, 1.0); tr.rotation.y = -0.7; S.scene.add(tr);
  const pum = new THREE.Mesh(new THREE.IcosahedronGeometry(0.7, 2), stone({ base: '#d8d2c6', dots: '#a39c90', dots2: '#f3efe7', n: 1400, seed: 801, rough: 0.9 }, { bumpScale: 3 })); pum.position.set(0, 1.4, -1.6); S.scene.add(pum);
  const px = []; for (let i = 0; i < 22; i++) { const c = crystal(0.07 + hash(i) * 0.06, [0xa9e6cf, 0xffe7a3, 0xffffff][i % 3]); const th = hash(i * 3) * 6.28, ph = hash(i * 5) * 3.14; c.position.set(Math.sin(ph) * Math.cos(th) * 0.74, 1.4 + Math.cos(ph) * 0.74, -1.6 + Math.sin(ph) * Math.sin(th) * 0.74); c.lookAt(0, 1.4, -1.6); S.scene.add(c); px.push(c); }
  const flasks = []; for (let i = 0; i < 2; i++) { const f = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.45, 1.0, 24, 1, true), gloss(0xeaf4ff, { transparent: true, opacity: 0.28, side: THREE.DoubleSide, depthWrite: false })); f.position.set(3.4 + i * 1.1, 0.5, -1.2); S.scene.add(f); const liq = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.43, 0.4, 24), gloss(i ? 0xe8706a : 0x86dcbc, { transparent: true, opacity: 0.85 })); liq.position.set(3.4 + i * 1.1, 0.22, -1.2); S.scene.add(liq); flasks.push(liq); const tg = textSprite(i ? 'горячая' : 'заранее', { size: 48, scale: 0.55 }); tg.position.set(3.4 + i * 1.1, 1.25, -1.2); S.scene.add(tg); }
  const bk = book(10); bk.position.set(-2.8, 0.1, 1.6); bk.scale.setScalar(0.5); bk.rotation.y = 0.4; S.scene.add(bk);
  const glow = new THREE.PointLight(0xff9a40, 0, 6, 1.6); glow.position.set(-2.8, 1.0, 1.6); S.scene.add(glow);
  return { ...S, plumb, weights, sq, pum, px, flasks, glow };
})();
export function s12b(t) {
  const id = 's12b';
  const tSite = fc(id, 'в', 0, 0.06), tPiles = fc(id, 'остались', 0, 0.22), tTools = fc(id, 'среди', 0, 0.27), tIso = fc(id, 'чтобы', 0, 0.39), tHot = fc(id, 'и', 2, 0.53), tPum = fc(id, 'нашёлся', 0, 0.62), tGrow = fc(id, 'они', 0, 0.74), tVit = fc(id, 'а', 1, 0.82), end = 200;
  clear2d();
  const F = FINDS;
  shot(t, [
    [0, (lt, k) => { const S = VOLC; S.ash.userData.update(t, 0.6); S.sea.userData.update(t, 0.5); orbit(S.cam, v3(0, 3, -2), lerp(34, 28, k), lerp(0.1, -0.2, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, -2), 0.0004) });
      title('что нашли', 120, 230, t, 0.3, { size: 100, align: 'left' }); title('в Помпеях?', 120, 340, t, 0.8, { size: 100, align: 'left', color: RED });
      pill('IX район · стройка, брошенная посреди работы', 125, 470, t, tSite + 0.6, { dot: SAND, align: 'left', size: 38 }); }],
    [tPiles, (lt, k) => { orbit(F.cam, v3(0, 0.4, 0.4), lerp(9, 7, k), lerp(0.4, 0.15, k), 0.5); render(F.scene, F.cam, { time: t, ...dof(F.cam, v3(0, 0.4, 0.4), 0.0012) });
      pill('кучи сырья и инструменты', 125, 230, t, tPiles + 0.2, { dot: SAND, align: 'left', size: 40 }); pill('грузы и измерительные инструменты', 125, 330, t, tTools + 0.3, { dot: '#8a8c90', align: 'left', size: 40 }); pill('возможно — для пропорций и ровных стен', 125, 430, t, tTools + 2.5, { dot: PURPLE, align: 'left', size: 36 }); }],
    [tIso, (lt, k) => { F.flasks.forEach((f, i) => (f.scale.y = 0.4 + 0.6 * easeOut(seg(t, tIso + 1 + i * 0.6, tIso + 3 + i * 0.6)))); orbit(F.cam, v3(3.95, 0.5, -1.2), lerp(4.5, 3.6, k), lerp(0.3, -0.1, k), 0.25); render(F.scene, F.cam, { time: t, ...dof(F.cam, v3(3.95, 0.5, -1.2), 0.0018) });
      title('изотопный анализ', 120, 230, t, tIso + 0.3, { size: 90, align: 'left' }); pill('как кальций реагировал с CO₂', 125, 345, t, tIso + 2.0, { dot: '#b8c4d6', align: 'left', size: 40 });
      pill('гашёная заранее', 125, 445, t, tHot + 0.4, { dot: MINT, align: 'left', size: 40 }); pill('или смешанная горячей', 125, 545, t, tHot + 1.2, { dot: RED, align: 'left', size: 40 }); }],
    [tPum, (lt, k) => { const g = easeOut(seg(t, tGrow, tGrow + 4)); F.px.forEach((c, i) => c.scale.setScalar(Math.max(0.001, clamp(g * 1.5 - hash(i) * 0.5)))); F.pum.rotation.y = t * 0.15;
      orbit(F.cam, v3(0, 1.4, -1.6), lerp(4.2, 3.0, k), lerp(-0.5, 0.2, k), 0.15); render(F.scene, F.cam, { time: t, ...dof(F.cam, v3(0, 1.4, -1.6), 0.002) });
      title('герой №2 — пемза', 120, 230, t, tPum + 0.3, { size: 90, align: 'left' }); pill('реагирует с водой в порах', 125, 345, t, tPum + 2.0, { dot: SKY, align: 'left', size: 40 }); pill('растит минералы · затягивает трещины', 125, 445, t, tGrow + 0.4, { dot: MINT, align: 'left', size: 40 }); }],
    [tVit, (lt, k) => { F.glow.intensity = 6 * smooth(seg(t, tVit + 3, tVit + 5)); orbit(F.cam, v3(-2.8, 0.3, 1.6), lerp(4.5, 3.5, k), lerp(0.6, 0.3, k), 0.6); render(F.scene, F.cam, { time: t, ...dof(F.cam, v3(-2.8, 0.2, 1.6), 0.0016) });
      title('Витрувия просто', 120, 230, t, tVit + 0.6, { size: 80, align: 'left' }); title('неправильно читали?', 120, 330, t, tVit + 1.1, { size: 80, align: 'left', color: PURPLE }); pill('он упоминает «скрытый жар» при смешивании', 125, 455, t, tVit + 3.4, { dot: RED, align: 'left', size: 38 }); }],
  ], end);
}

// ═════════ s13b. Бактерии ═════════
const BIO = (() => {
  const S = newScene({ bg: 0xe2ecf0, floorY: -1.6, key: [4, 9, 6], keyI: 3.0 });
  const cm = concrete({ base: '#c9c6c0', seed: 830 });
  const L = rbox(3, 3, 3, cm, 0.1); L.position.set(-1.78, 0, 0); S.scene.add(L); const R = rbox(3, 3, 3, cm, 0.1); R.position.set(1.78, 0, 0); S.scene.add(R);
  const sp = []; for (let i = 0; i < 26; i++) { const s = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.14, 4, 10), gloss(0xc7b8ff, { emissive: 0x9a7bff, emissiveIntensity: 0.0 })); s.position.set((hash(i) - 0.5) * 0.3, (hash(i + 1) - 0.5) * 2.6, 1.4 - hash(i + 2) * 1.6); s.rotation.set(hash(i) * 3, hash(i + 3) * 3, 0); S.scene.add(s); sp.push(s); }
  const food = []; for (let i = 0; i < 14; i++) { const s = sphere(0.05, gloss(0xffe7a3), 10); s.position.set((hash(i + 40) - 0.5) * 0.3, (hash(i + 41) - 0.5) * 2.6, 1.4 - hash(i + 42) * 1.6); S.scene.add(s); food.push(s); }
  const xt = []; for (let i = 0; i < 40; i++) { const c = crystal(0.09 + hash(i) * 0.05); c.position.set((hash(i + 70) - 0.5) * 0.32, (hash(i + 71) - 0.5) * 2.8, 1.45 - hash(i + 72) * 2.0); c.rotation.set(hash(i) * 3, hash(i + 1) * 3, 0); S.scene.add(c); xt.push(c); }
  const wat = drops(30, 0x8fd0e6, 0.06); S.scene.add(wat);
  const lab = rbox(5, 0.2, 3, matte(0xf4f4f8), 0.06); lab.position.set(5.5, -1.5, -2); S.scene.add(lab); const mic = microscope(); mic.position.set(5.5, -1.4, -2); mic.rotation.y = -0.5; S.scene.add(mic);
  return { ...S, L, R, sp, food, xt, wat };
})();
export function s13b(t) {
  const id = 's13b', S = BIO;
  const tJ = fc(id, 'с', 0, 0.1), tSp = fc(id, 'в', 1, 0.3), tSl = fc(id, 'споры', 1, 0.46), tW = fc(id, 'когда', 0, 0.5), tLs = fc(id, 'тот', 0, 0.62), tH = fc(id, 'трещина', 1, 0.7), tWay = fc(id, 'пути', 0, 0.76), tR = fc(id, 'римляне', 0, 0.88), end = 200;
  const wake = smooth(seg(t, tW + 1, tW + 3)); const heal = easeOut(seg(t, tLs, tH + 4));
  S.sp.forEach((s, i) => { s.material.emissiveIntensity = wake * (0.6 + 0.4 * Math.sin(t * 4 + i)); s.scale.setScalar(1 + wake * 0.4); s.visible = heal < 0.95; });
  S.food.forEach((f) => (f.visible = t > tSp && heal < 0.5));
  S.xt.forEach((c, i) => c.scale.setScalar(Math.max(0.001, clamp(heal * 1.5 - hash(i) * 0.5))));
  S.wat.userData.ps.forEach((p, i) => { const ph = (t * 0.6 + hash(i)) % 1; p.position.set((hash(i) - 0.5) * 0.2, lerp(2.2, -1.2, ph), 1.3 - hash(i + 1) * 1.5); p.visible = t > tW && t < tH + 2; });
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 0, 0), lerp(13, 10, k), lerp(0.55, 0.35, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0), 0.0008) });
      title('другой путь:', 120, 230, t, 0.3, { size: 96, align: 'left' }); title('бетон с бактериями', 120, 340, t, 0.8, { size: 90, align: 'left', color: PURPLE });
      pill('Хенк Йонкерс · TU Delft · с 2006', 125, 470, t, tJ + 0.4, { dot: SKY, align: 'left', size: 40 }); }],
    [tSp, (lt, k) => { orbit(S.cam, v3(0, 0, 1.0), lerp(5, 4, k), lerp(0.25, 0.1, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 1.2), 0.0016) });
      pill('споры, которые выдерживают щёлочь', 125, 230, t, tSp + 0.4, { dot: '#c7b8ff', align: 'left', size: 40 }); pill('+ еда для них', 125, 330, t, tSp + 2.6, { dot: '#ffe7a3', align: 'left', size: 40 }); title('спят', 120, 500, t, tSl, { size: 100, align: 'left', color: '#8a86a0', out: tW }); }],
    [tW, (lt, k) => { orbit(S.cam, v3(0, 0, 1.0), lerp(4, 3.2, k), lerp(-0.2, 0.05, k), lerp(0.1, 0.35, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 1.2), 0.0016) });
      pill('вода → просыпаются, едят', 125, 230, t, tW + 0.6, { dot: SKY, align: 'left', size: 40 }); pill('выделяют известняк · CaCO₃', 125, 330, t, tLs + 0.2, { dot: MINT, align: 'left', size: 40 }); title('трещина зарастает', 120, 500, t, tH + 0.2, { size: 84, align: 'left', color: PURPLE }); }],
    [tWay, (lt, k) => { const C2 = CUBE; C2.cube.rotation.set(0.35, t * 0.3, 0); orbit(C2.cam, v3(0, 0, 0), lerp(9, 7.5, k), 0.4, 0.25); render(C2.scene, C2.cam, { time: t, ...dof(C2.cam, v3(0, 0, 0), 0.0012) });
      title('пути разные —', 120, 230, t, tWay + 0.2, { size: 96, align: 'left' }); title('химия одна', 120, 340, t, tWay + 0.8, { size: 96, align: 'left', color: MINT });
      pill('римляне: комочки извести', 125, 480, t, tR + 0.3, { dot: '#ffffff', align: 'left', size: 40 }); pill('сегодня: живые бактерии', 125, 580, t, tR + 2.0, { dot: '#c7b8ff', align: 'left', size: 40 }); }],
  ], end);
}

// ═════════ s13c. Три мифа ═════════
const RUINS = (() => {
  const S = newScene({ bg: 0xf0e2d0, floorY: 0, key: [-6, 11, 8], shadowSize: 18 });
  S.ground.material = stone({ base: '#d9c7ae', dots: '#b39c80', dots2: '#ead9c3', n: 800, seed: 860, rep: 12 });
  const g = new THREE.Group(); S.scene.add(g);
  for (let i = 0; i < 6; i++) { const c = column(4, 0.36); c.position.set(-6 + i * 2.4, 0, -2); if (i === 2 || i === 4) { c.rotation.z = Math.PI / 2; c.position.set(-6 + i * 2.4, 0.36, 1 + hash(i)); c.rotation.y = hash(i) * 2; } else if (i === 3) c.scale.y = 0.45; g.add(c); }
  for (let i = 0; i < 14; i++) { const b = rbox(0.8 + hash(i) * 0.6, 0.5, 0.6, (i % 3) ? marble() : brick(), 0.06); b.position.set((hash(i * 3) - 0.5) * 12, 0.25, (hash(i * 5) - 0.2) * 6); b.rotation.y = hash(i) * 3; g.add(b); }
  const wall = rbox(5, 2.2, 0.6, brick(), 0.05); wall.position.set(5, 1.1, -4); g.add(wall);
  shadowAll(g);
  return { ...S };
})();
export function s13c(t) {
  const id = 's13c';
  const t1 = fc(id, 'миф', 0, 0.05), tN1 = fc(id, 'нет', 0, 0.1), tRw = fc(id, 'римский', 1, 0.2), t2 = fc(id, 'миф', 1, 0.28), tN2 = fc(id, 'тоже', 0, 0.33), tGap = fc(id, 'не', 1, 0.42), t3 = fc(id, 'миф', 2, 0.52), tSurv = fc(id, 'это', 0, 0.58), tFall = fc(id, 'огромное', 0, 0.66), tPan = fc(id, 'даже', 0, 0.76), tPh = fc(id, 'в', 3, 0.8), tCh = fc(id, 'церковь', 0, 0.92), end = 200;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = CUBE; S.cube.rotation.set(0.35, t * 0.3, 0); orbit(S.cam, v3(-2, 0, 0), lerp(10, 8.5, k), -0.4, 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0), 0.0012) });
      chapter(8, 'Три мифа', t, 0.2, 5.0); }],
    [t1 + 1.0, (lt, k) => { const S = BEAM; beamAt(S, t, 0, 0, 0, 0); orbit(S.cam, v3(0, 0.3, 0), lerp(12, 10, k), lerp(0.4, 0.2, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.3, 0), 0.0006) });
      title('миф 1:', 120, 200, t, t1 + 1.0, { size: 64, align: 'left', color: PURPLE }); title('римский бетон прочнее', 120, 290, t, t1 + 1.3, { size: 80, align: 'left' }); stamp('МИФ', 1450, 300, t, tN1 + 0.2, { size: 90 });
      bars([{ label: 'прочность на сжатие', v: 1, color: '#a9d6ff', text: 'современный' }, { label: 'долголетие и самолечение', v: 1, color: '#a9e6cf', text: 'римский' }], 120, 520, t, tRw, { w: 620 }); }],
    [t2, (lt, k) => { const S = FINDS; orbit(S.cam, v3(-2.8, 0.3, 1.6), lerp(5, 4, k), lerp(0.2, 0.5, k), 0.7); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-2.8, 0.2, 1.6), 0.0014) });
      title('миф 2:', 120, 200, t, t2 + 0.2, { size: 64, align: 'left', color: PURPLE }); title('рецепт утерян навсегда', 120, 290, t, t2 + 0.5, { size: 80, align: 'left' }); stamp('МИФ', 1450, 300, t, tN2 + 0.2, { size: 90 });
      pill('состав известен: о пуццолане писал Витрувий', 125, 480, t, tN2 + 1.6, { dot: SAND, align: 'left', size: 38 }); pill('не хватало «как смешивали» → Приверно и Помпеи', 125, 580, t, tGap + 0.3, { dot: MINT, align: 'left', size: 38 }); }],
    [t3, (lt, k) => { const S = RUINS; orbit(S.cam, v3(0, 1.2, 0), lerp(20, 15, k), lerp(0.5, 0.1, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1, 0), 0.0006) });
      title('миф 3:', 120, 200, t, t3 + 0.2, { size: 64, align: 'left', color: PURPLE }); title('всё римское стоит до сих пор', 120, 290, t, t3 + 0.5, { size: 74, align: 'left' }); stamp('ОШИБКА ВЫЖИВШЕГО', 1350, 320, t, tSurv + 0.4, { size: 54 });
      pill('многое рухнуло, сгорело, разобрано на камень', 125, 480, t, tFall + 0.3, { dot: RED, align: 'left', size: 38 }); }],
    [tPan, (lt, k) => { const S = PAN; orbit(S.cam, v3(0, 4.5, 0), lerp(28, 22, k), lerp(-0.3, 0.1, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 4, 2), 0.0005) });
      title('Пантеону помог', 120, 230, t, tPan + 0.3, { size: 84, align: 'left' }); title('не только бетон', 120, 335, t, tPan + 0.8, { size: 84, align: 'left', color: PURPLE });
      pill('609 г. · Фока → папа Бонифаций IV', 125, 470, t, tPh + 0.3, { dot: SAND, align: 'left', size: 40 }); pill('храм стал церковью — его берегли и чинили', 125, 570, t, tCh + 0.2, { dot: MINT, align: 'left', size: 40 }); }],
  ], end);
}
