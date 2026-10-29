// Сцены s08–s14: включения, горячее смешивание, самозалечивание, море, Помпеи, будущее, финал
import { render, clear2d, ctx, title, pill, counter, project, W, H, THREE, C, CSS, matte, gloss, metal,
  clamp, lerp, seg, smooth, easeInOut, easeIO2, easeOut, easeIn, spring, hash, noise1 } from './engine.js';
import { VO, cue, dof, shot, v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite, popScale, waves, cloud,
  stone, concrete, marble, brick, wood, shadowAll, column, pantheon, lightBeam, pier, romanShip, beam, factory, smoke, kiln, volcano,
  pile, bucket, trowel, book, microscope, clastCube, drops, crystal, blade, chapter, quote, dimLine, stamp, bars } from './lib.js';
import { PAN, VOLC, CUBE } from './scenes_a.js';

const RED = '#e8706a', PURPLE = '#7a63e6', MINT = '#86dcbc';

// ───────── s08. Белые крапинки ─────────
const SLAB = (() => {
  const S = newScene({ bg: 0xece4dc, floorY: -0.6, key: [3, 8, 5], keyI: 3.2 });
  const desk = rbox(12, 0.4, 7, wood(), 0.08); desk.position.y = -0.4; S.scene.add(desk);
  const slab = rbox(5, 0.6, 3.4, concrete({ seed: 101, clasts: 40, n: 2200 }), 0.08); slab.position.y = 0.1; S.scene.add(slab);
  const cl = []; for (let i = 0; i < 26; i++) { const s = sphere(0.05 + hash(i + 3) * 0.07, gloss(0xffffff, { roughness: 0.55 }), 14); s.position.set((hash(i * 7) - 0.5) * 4.6, 0.38, (hash(i * 11) - 0.5) * 3.0); s.scale.y = 0.5; S.scene.add(s); cl.push(s); }
  for (let i = 0; i < 40; i++) { const a = rbox(0.12 + hash(i) * 0.25, 0.06, 0.1 + hash(i + 1) * 0.2, stone({ base: '#8a7d70', seed: 120 + (i % 4) }), 0.03); a.position.set((hash(i * 3 + 1) - 0.5) * 4.6, 0.39, (hash(i * 5 + 2) - 0.5) * 3.0); a.rotation.y = hash(i) * 3; S.scene.add(a); }
  const lens = new THREE.Group(); const ring = new THREE.Mesh(new THREE.TorusGeometry(0.75, 0.07, 14, 64), metal(C.gold)); ring.rotation.x = Math.PI / 2; lens.add(ring);
  const glass = new THREE.Mesh(new THREE.CircleGeometry(0.72, 48), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 0.9, roughness: 0.02, thickness: 0.2, transparent: true, opacity: 0.35 })); glass.rotation.x = -Math.PI / 2; lens.add(glass);
  const handle = rbox(0.16, 0.16, 1.4, wood(), 0.06); handle.position.set(0, 0, 1.4); lens.add(handle); S.scene.add(shadowAll(lens));
  const mic = microscope(); mic.position.set(4.3, -0.2, -1.6); mic.rotation.y = -0.6; S.scene.add(mic);
  return { ...S, slab, cl, lens };
})();
export function s08(t) {
  const id = 's08', S = SLAB;
  const tN = cue(id, 'называют', 0, 7), tB = cue(id, 'браком', 0, 11), tQ = cue(id, 'почему', 0, 17), tM = cue(id, 'команда', 0, 21), end = 34;
  const lx = lerp(-1.6, 1.4, easeInOut(seg(t, 2, 14))), lz = Math.sin(t * 0.5) * 0.6;
  S.lens.position.set(lx, 1.1, lz);
  S.cl.forEach((c, i) => { const d = Math.hypot(c.position.x - lx, c.position.z - lz); const k = clamp(1 - d / 0.8); c.scale.set(1 + k * 0.6, 0.5 + k * 0.4, 1 + k * 0.6); });
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 0.3, 0), lerp(8, 6.5, k), lerp(0.5, 0.25, k), 0.75); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.4, 0), 0.0012) });
      title('распил римского бетона', 120, 220, t, 0.4, { size: 80, align: 'left', out: tN - 0.3 }); }],
    [tN, (lt, k) => { orbit(S.cam, v3(lx, 0.4, lz), lerp(3.2, 2.6, k), 0.3, 0.9); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(lx, 0.4, lz), 0.0025, 0.014) });
      title('известковые включения', 120, 220, t, tN, { size: 84, align: 'left' }); pill('несколько миллиметров', 125, 330, t, tN + 1.2, { dot: '#ffffff', align: 'left' }); stamp('БРАК?', 560, 520, t, tB + 0.2, { size: 90 }); }],
    [tQ, (lt, k) => { orbit(S.cam, v3(0.5, 0.4, 0), lerp(9, 7.5, k), lerp(-0.3, -0.5, k), 0.4); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0.4, 0), 0.001) });
      title('почему один', 120, 220, t, tQ, { size: 96, align: 'left', out: tM - 0.2 }); title('и тот же «брак»?', 120, 330, t, tQ + 0.5, { size: 96, align: 'left', color: RED, out: tM - 0.2 }); }],
    [tM, (lt, k) => { orbit(S.cam, v3(4.2, 0.8, -1.6), lerp(6.5, 5.2, k), lerp(-0.9, -0.6, k), 0.3); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(4.3, 0.8, -1.6), 0.0014) });
      title('Адмир Масич', 120, 230, t, tM + 0.4, { size: 100, align: 'left' }); pill('Массачусетский технологический институт (MIT)', 125, 340, t, tM + 1.4, { dot: PURPLE, align: 'left', size: 36 }); }],
  ], end);
}

// ───────── s09. Горячее смешивание ─────────
const HOT = (() => {
  const S = newScene({ bg: 0xf4e4d6, floorY: 0, key: [5, 11, 8], shadowSize: 14 });
  // стена Приверно: облицовка из блоков + бетонное ядро в разрезе
  const wall = new THREE.Group(); wall.position.set(-6, 0, -2); S.scene.add(wall);
  for (let r = 0; r < 6; r++) for (let c = 0; c < 6; c++) { const b = rbox(0.95, 0.55, 0.6, stone({ base: '#cdbb9f', seed: 140 + ((r + c) % 5) }), 0.06); b.position.set(c - 2.5 + (r % 2) * 0.5, 0.3 + r * 0.58, 0.8); wall.add(b); }
  const core = rbox(5.8, 3.4, 1.0, concrete({ seed: 150, clasts: 24 }), 0.05); core.position.set(0, 1.7, 0); wall.add(core);
  const frag = rbox(0.3, 0.22, 0.2, concrete({ seed: 151, clasts: 10 }), 0.04); frag.position.set(1.2, 2.2, 0.55); wall.add(frag);
  const ringF = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.03, 8, 40), new THREE.MeshBasicMaterial({ color: 0xe8706a, toneMapped: false })); ringF.position.set(1.2, 2.2, 0.72); wall.add(ringF);
  // корыто
  const trough = new THREE.Group(); trough.position.set(2, 0, 1); S.scene.add(trough);
  for (const [x, z, w, d] of [[0, -1.0, 4.2, 0.18], [0, 1.0, 4.2, 0.18], [-2.1, 0, 0.18, 2.2], [2.1, 0, 0.18, 2.2]]) { const p = rbox(w, 0.9, d, wood(), 0.04); p.position.set(x, 0.45, z); trough.add(p); }
  const limeP = pile('#faf8f2', 0.95, 0.7, 11); limeP.position.set(-0.9, 0.05, 0); trough.add(limeP);
  const ashP = pile('#8d8581', 0.95, 0.7, 12); ashP.position.set(0.9, 0.05, 0); trough.add(ashP);
  const mix = rbox(4.0, 0.5, 1.9, concrete({ base: '#bdb2a6', seed: 152, n: 2000 }), 0.05); mix.position.set(0, 0.3, 0); trough.add(mix);
  const mixM = mix.material;
  const lumps = []; for (let i = 0; i < 16; i++) { const s = sphere(0.07 + hash(i + 40) * 0.07, gloss(0xffffff, { roughness: 0.6 }), 12); s.position.set((hash(i * 5) - 0.5) * 3.6, 0.56, (hash(i * 9) - 0.5) * 1.6); trough.add(s); lumps.push(s); }
  const water = drops(30, 0x8fd0e6, 0.07); S.scene.add(water);
  const steam = smoke(16, matte(0xffffff, { transparent: true, opacity: 0.55 })); steam.position.set(1.6, 0.6, 1); steam.scale.setScalar(0.6); S.scene.add(steam);
  const heat = new THREE.PointLight(0xff7a2a, 0, 7, 1.5); heat.position.set(2, 1.2, 1.6); S.scene.add(heat);
  const jug = new THREE.Group(); const jb = sphere(0.5, matte(0xc98f6a), 24); jb.scale.set(1, 1.2, 1); jug.add(jb); const jn = cyl(0.18, 0.45, matte(0xc98f6a), 16); jn.position.y = 0.7; jug.add(jn); jug.position.set(2.6, 2.6, 1); jug.rotation.z = 1.9; S.scene.add(shadowAll(jug));
  return { ...S, wall, ringF, trough, limeP, ashP, mix, mixM, lumps, water, steam, heat, jug };
})();
function thermo(x, y, k, t, t0) {
  const a = easeOut(seg(t, t0, t0 + 0.6)); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y);
  ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.beginPath(); ctx.roundRect(-34, -300, 68, 340, 34); ctx.fill();
  ctx.fillStyle = '#ffe3d6'; ctx.beginPath(); ctx.roundRect(-14, -270, 28, 270, 14); ctx.fill();
  const hgt = 270 * k; const g = ctx.createLinearGradient(0, 0, 0, -270); g.addColorStop(0, '#ffb04a'); g.addColorStop(1, '#e8706a');
  ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(-14, -hgt, 28, hgt, 14); ctx.fill();
  ctx.beginPath(); ctx.arc(0, 10, 30, 0, Math.PI * 2); ctx.fillStyle = '#e8706a'; ctx.fill();
  ctx.restore();
}
export function s09(t) {
  const id = 's09', S = HOT;
  const tT = cue(id, 'анализ', 0, 8), tDry = cue(id, 'негашёную', 0, 13), tW = cue(id, 'потом', 0, 16), tH = cue(id, 'реакция', 0, 19), tN = cue(id, 'это', 1, 24), tC = cue(id, 'запасы', 0, 30), end = 40;
  // сухие кучи сливаются, вода, нагрев
  const merge = easeInOut(seg(t, tDry + 0.5, tDry + 2.5));
  S.limeP.position.x = lerp(-0.9, -0.25, merge); S.ashP.position.x = lerp(0.9, 0.25, merge);
  const wet = smooth(seg(t, tW + 0.5, tW + 2.2));
  S.limeP.visible = S.ashP.visible = wet < 0.95; S.limeP.scale.y = S.ashP.scale.y = Math.max(0.01, 1 - wet);
  S.mix.visible = wet > 0.02; S.mix.scale.y = Math.max(0.02, wet);
  S.water.userData.ps.forEach((p, i) => { const ph = (t * 1.3 + hash(i)) % 1; p.position.set(2.2 + (hash(i + 1) - 0.5) * 0.3, lerp(2.3, 0.4, ph), 1 + (hash(i + 2) - 0.5) * 0.3); p.visible = t > tW && t < tW + 2.6 && ph < 0.95; });
  S.jug.visible = t > tW - 0.5 && t < tW + 3.2;
  const hot = smooth(seg(t, tH, tH + 2)) * (1 - smooth(seg(t, tC + 2, tC + 5)));
  S.heat.intensity = hot * (7 + 2 * Math.sin(t * 6));
  S.mixM.emissive = new THREE.Color(0xff6a1a); S.mixM.emissiveIntensity = hot * (0.18 + 0.06 * Math.sin(t * 5));
  S.steam.userData.update(t, 1.6); S.steam.visible = hot > 0.05;
  S.lumps.forEach((l, i) => { const k = easeOut(seg(t, tC - 1.5 + i * 0.12, tC - 0.9 + i * 0.12)); l.visible = k > 0.01 && wet > 0.5; l.scale.setScalar(k); });
  S.ringF.scale.setScalar(1 + 0.1 * Math.sin(t * 4));
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(-4.8, 2, -1.2), lerp(7, 5.5, k), lerp(0.2, 0.05, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-4.8, 2.2, -1.2), 0.0012) });
      chapter(4, 'Горячее смешивание', t, 0.2, 5.5); pill('Приверно · фрагмент ≈ 2 см', 125, 980, t, 2.2, { dot: RED, align: 'left', size: 38, out: tT - 0.2 }); }],
    [tT, (lt, k) => { orbit(S.cam, v3(-4.8, 2.2, -1.2), lerp(3.2, 2.6, k), 0.05, 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-4.8, 2.2, -1.25), 0.002, 0.014) });
      pill('Рим завоевал город в IV в. до н. э.', 125, 980, t, Math.max(0, tT - 6), { dot: '#e9b97f', align: 'left', size: 36, out: tT }); title('карбонат кальция,', 120, 220, t, tT + 0.6, { size: 84, align: 'left' }); title('рождённый в жару', 120, 320, t, tT + 1.4, { size: 100, align: 'left', color: RED }); }],
    [tDry, (lt, k) => { orbit(S.cam, v3(2, 0.6, 1), lerp(8, 6.5, k), lerp(0.35, 0.1, k), 0.45); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(2, 0.5, 1), 0.0012) });
      pill('1. сухая известь + пепел', 125, 230, t, tDry + 0.3, { dot: '#ffffff', align: 'left' }); pill('2. вода — в самом конце', 125, 330, t, tW, { dot: '#8fd0e6', align: 'left' }); }],
    [tH, (lt, k) => { orbit(S.cam, v3(2, 0.6, 1), lerp(5.5, 4.6, k), lerp(-0.2, 0.05, k), 0.35); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(2, 0.5, 1), 0.0016), flash: 0.04 * hot });
      thermo(1700, 900, smooth(seg(t, tH, tH + 3)) * 0.9, t, tH); title('смесь греется сама', 120, 230, t, tH + 0.3, { size: 90, align: 'left' }); pill('горячее смешивание', 125, 345, t, tN, { dot: RED, align: 'left', size: 46 }); }],
    [tC, (lt, k) => { orbit(S.cam, v3(2, 0.6, 1), lerp(3.6, 3.0, k), 0.4, 0.7); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(2, 0.55, 1), 0.002, 0.012) });
      title('белые комочки =', 120, 230, t, tC, { size: 90, align: 'left' }); title('запасы кальция', 120, 340, t, tC + 0.5, { size: 96, align: 'left', color: PURPLE }); pill('и быстрее схватывается', 125, 450, t, tC + 1.6, { dot: MINT, align: 'left' }); }],
  ], end);
}

// ───────── s10. Самозалечивание ─────────
const HEAL = (() => {
  const S = newScene({ bg: 0xe6eef4, floorY: -2.6, key: [4, 10, 7] });
  const m = concrete({ seed: 160, clasts: 14 });
  const L = rbox(3, 4.4, 2.6, m, 0.1), R = rbox(3, 4.4, 2.6, m, 0.1); S.scene.add(L); S.scene.add(R);
  const clast = sphere(0.45, gloss(0xffffff, { roughness: 0.5 }), 32); S.scene.add(clast);
  const water = drops(40, 0x8fd0e6, 0.07); S.scene.add(water);
  const sol = drops(30, 0xdff3ff, 0.06); S.scene.add(sol);
  const xs = []; for (let i = 0; i < 46; i++) { const c = crystal(0.1 + hash(i) * 0.08); c.position.set(0, -2 + (i / 46) * 4.1, (hash(i + 3) - 0.5) * 2.2); c.rotation.set(hash(i) * 3, hash(i + 1) * 3, 0); S.scene.add(c); xs.push(c); }
  const co2 = []; for (let i = 0; i < 8; i++) { const g = textSprite('CO₂', { size: 48, bg: '#ffffff', color: '#7a63e6', scale: 0.8 }); S.scene.add(g); co2.push(g); }
  // лаборатория: два цилиндра
  const lab = new THREE.Group(); lab.position.set(14, -2.6, 0); S.scene.add(lab);
  const bench = rbox(8, 0.3, 4, matte(0xf1eef6), 0.06); bench.position.y = 0.15; lab.add(bench);
  const cyls = [-1.8, 1.8].map((x, i) => { const g = new THREE.Group(); g.position.set(x, 0.3, 0); lab.add(g);
    const a = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 3, 40, 1, false, 0.05, Math.PI - 0.1), concrete({ seed: 170 + i, clasts: i === 0 ? 12 : 0 })); a.position.y = 1.5; g.add(a);
    const b = a.clone(); b.rotation.y = Math.PI; g.add(b);
    const fill = rbox(0.06, 3, 1.75, gloss(0xfdfcf7, { roughness: 0.3 }), 0.01); fill.position.y = 1.5; g.add(fill);
    const funnel = new THREE.Mesh(new THREE.ConeGeometry(0.6, 0.8, 32, 1, true), gloss(0xbfe3f2, { transparent: true, opacity: 0.6, side: THREE.DoubleSide })); funnel.rotation.x = Math.PI; funnel.position.y = 3.6; g.add(funnel);
    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.42, 0.6, 32, 1, true), gloss(0xbfe3f2, { transparent: true, opacity: 0.55, side: THREE.DoubleSide })); cup.position.set(0, -0.0, 1.6); g.add(cup);
    const d = drops(10, 0x8fd0e6, 0.06); g.add(d);
    return { g, fill, d };
  });
  const tags = [textSprite('горячее смешивание', { size: 50, bg: '#a9e6cf', scale: 0.75 }), textSprite('без негашёной извести', { size: 50, bg: '#ffc9a8', scale: 0.75 })];
  tags[0].position.set(14 - 2.0, 2.3, 1.2); tags[1].position.set(14 + 2.0, 2.3, 1.2); tags.forEach((x) => S.scene.add(x));
  return { ...S, L, R, clast, water, sol, xs, co2, cyls, tags };
})();
export function s10(t) {
  const id = 's10', S = HEAL;
  const tCr = cue(id, 'трещина', 0, 4), tW = cue(id, 'вода', 0, 6), tD = cue(id, 'растворяет', 0, 9), tCO = cue(id, 'углекислым', 0, 13), tF = cue(id, 'зарастает', 0, 18), tLab = cue(id, 'это', 1, 21),
    t2w = cue(id, 'через', 0, 30), tNo = cue(id, 'без', 0, 36), tPub = cue(id, 'работу', 0, 41), end = 52;
  // трещина и её зарастание
  const open = easeOut(seg(t, tCr, tCr + 1.2)) * (1 - easeInOut(seg(t, tF, tF + 3)) * 0.85);
  const gap = 0.05 + open * 0.42;
  S.L.position.set(-1.5 - gap / 2, -0.4, 0); S.R.position.set(1.5 + gap / 2, -0.4, 0);
  S.L.rotation.z = open * 0.02; S.R.rotation.z = -open * 0.02;
  const diss = smooth(seg(t, tD, tD + 4));
  S.clast.position.set(-gap / 2 - 0.15, 0.4, 0.4); S.clast.scale.setScalar(Math.max(0.05, 1 - diss * 0.7));
  S.water.userData.ps.forEach((p, i) => { const ph = (t * 0.6 + hash(i)) % 1; p.position.set((hash(i + 1) - 0.5) * gap * 0.6, lerp(2.4, -2.4, ph), (hash(i + 2) - 0.5) * 2.0); p.visible = t > tW && t < tF + 2 && ph < 0.98; });
  S.sol.userData.ps.forEach((p, i) => { const ph = (t * 0.45 + hash(i + 5)) % 1; p.position.set(-gap / 2 + ph * 0.1, lerp(0.4, -2.2, ph), 0.4 + (hash(i + 3) - 0.5) * 1.6); p.visible = t > tD + 0.8 && t < tF + 2.5 && ph < 0.97; });
  S.co2.forEach((c, i) => { const ph = (t * 0.25 + i / 8) % 1; c.position.set((hash(i) - 0.5) * 1.5, 2.8 - ph * 3.6, 1.6); c.visible = t > tCO && t < tF + 1; c.material.opacity = Math.sin(ph * Math.PI); });
  const grow = easeInOut(seg(t, tCO + 1, tF + 3));
  S.xs.forEach((c, i) => { const k = clamp(grow * 1.3 - (i / S.xs.length) * 0.3 - (1 - i / S.xs.length) * 0.0); c.visible = k > 0.02; c.scale.setScalar(k * (0.8 + 0.4 * gap / 0.47)); });
  // лаборатория: дни 0→14, левый закрывается
  const days = Math.round(lerp(0, 14, easeInOut(seg(t, t2w - 2, t2w + 1.5))));
  const heal0 = smooth(seg(t, t2w - 2, t2w + 1.5));
  S.cyls.forEach((c, i) => { const healed = i === 0 ? heal0 : 0; c.fill.scale.y = i === 0 ? Math.max(0.01, heal0) : 0.01; c.fill.visible = i === 0 && heal0 > 0.02;
    c.d.children.forEach((p, j) => { const ph = (t * 1.1 + hash(j + i * 7)) % 1; p.position.set(0, lerp(3.2, -0.1, ph), lerp(0, 1.6, smooth(seg(ph, 0.85, 1)))); p.visible = (1 - healed) > 0.15 && ph < 0.99; }); });
  S.tags.forEach((x, i) => popScale(x, t, tLab + 1 + i * 0.4));
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 0, 0), lerp(13, 11, k), lerp(0.5, 0.25, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 1), 0.0008) });
      title('главный трюк', 120, 220, t, 0.3, { size: 110, align: 'left', out: tW - 0.2 }); }],
    [tW, (lt, k) => { orbit(S.cam, v3(-0.2, 0.2, 0.4), lerp(6.5, 5.2, k), lerp(0.35, 0.15, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(-0.2, 0.3, 0.4), 0.0016) });
      pill('1. вода в трещине', 125, 230, t, tW + 0.2, { dot: '#8fd0e6', align: 'left' }); pill('2. растворяет кальций', 125, 330, t, tD, { dot: '#ffffff', align: 'left' }); pill('3. кальций + CO₂', 125, 430, t, tCO, { dot: PURPLE, align: 'left' }); }],
    [tF - 1.5, (lt, k) => { orbit(S.cam, v3(0, 0, 0.6), lerp(5.5, 7.5, easeIO2(k)), lerp(-0.25, 0.0, k), 0.05); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0.8), 0.0014) });
      title('трещина зарастает', 120, 230, t, tF, { size: 90, align: 'left' }); title('камнем', 120, 340, t, tF + 0.5, { size: 110, align: 'left', color: PURPLE }); pill('карбонат кальция = известняк', 125, 450, t, tF + 1.4, { dot: '#ffffff', align: 'left' }); }],
    [tLab, (lt, k) => { orbit(S.cam, v3(14, -0.8, 0), lerp(13, 11, k), lerp(0.25, 0.1, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(14, -0.8, 0.5), 0.0008) });
      counter(days, 120, 330, { size: 220, align: 'left' }); title(days === 1 ? 'день' : 'дней', 130, 420, t, t2w - 2.4, { size: 70, align: 'left' });
      stamp('ЗАЖИЛО', 640, 620, t, t2w + 1.6, { color: '#3aa37c', size: 64, out: tNo }); stamp('ТЕЧЁТ', 640, 620, t, tNo + 0.8, { color: RED, size: 64, rot: 0.08, out: tPub - 0.2 }); }],
    [tPub, (lt, k) => { orbit(S.cam, v3(0, 0, 0), lerp(12, 14, k), lerp(-0.3, -0.5, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 0, 0.8), 0.0008) });
      pill('Science Advances · январь 2023', 125, 230, t, tPub + 0.2, { dot: PURPLE, align: 'left', size: 44 }); }],
  ], end);
}

// ───────── s11. Море: тоберморит ─────────
const PORE = (() => {
  const S = newScene({ bg: 0x2f4a66, floor: false, key: [3, 6, 8], fill: 0.9, keyI: 2.2 });
  S.scene.fog = new THREE.Fog(0x2f4a66, 8, 24);
  const cav = new THREE.Mesh(new THREE.SphereGeometry(4, 48, 32), concrete({ base: '#bcae9c', seed: 180, n: 2600 })); cav.material.side = THREE.BackSide; S.scene.add(cav);
  const pl = new THREE.PointLight(0xbfe6ff, 30, 12, 1.4); pl.position.set(1, 1.5, 2); S.scene.add(pl);
  const plates = []; for (let i = 0; i < 70; i++) { const b = blade(0.6 + hash(i) * 0.6, 0.025, 0.22 + hash(i + 1) * 0.2, i % 3 ? 0xe9f6f3 : 0xd6eef7); const th = hash(i + 2) * Math.PI * 2, ph = Math.acos(2 * hash(i + 3) - 1); const r = 3.5; b.position.set(Math.sin(ph) * Math.cos(th) * r, Math.cos(ph) * r * 0.8, Math.sin(ph) * Math.sin(th) * r); b.lookAt(0, 0, 0); b.rotateX(Math.PI / 2); b.rotateZ(hash(i + 4) * 3); S.scene.add(b); plates.push(b); }
  const fibers = []; for (let i = 0; i < 40; i++) { const f = cyl(0.015, 1, gloss(0xf3fbff), 6); const th = hash(i + 50) * Math.PI * 2, ph = Math.acos(2 * hash(i + 51) - 1); f.position.set(Math.sin(ph) * Math.cos(th) * 3.4, Math.cos(ph) * 2.7, Math.sin(ph) * Math.sin(th) * 3.4); f.lookAt(0, 0, 0); f.rotateX(Math.PI / 2); S.scene.add(f); fibers.push(f); }
  const sw = drops(50, 0x6fc2e6, 0.05); S.scene.add(sw);
  const ions = []; for (let i = 0; i < 10; i++) { const s = textSprite(['Al', 'Ca', 'Si', 'Na'][i % 4], { size: 46, bg: '#ffffff', color: '#2f4a66', scale: 0.32 }); S.scene.add(s); ions.push(s); }
  return { ...S, plates, fibers, sw, ions };
})();
const CORE = (() => {
  const S = newScene({ bg: 0xcfe6f5, floor: false, key: [6, 12, 4], shadowSize: 18 });
  const sea = waves(60, 40, 70, gloss(0x7fc0db, { roughness: 0.15 })); S.scene.add(sea);
  const pr = pier(3); pr.position.set(0, 0.2, 0); S.scene.add(pr);
  const rig = new THREE.Group(); rig.position.set(0, 2.1, 0.4); S.scene.add(rig);
  for (const [x, z] of [[-0.9, -0.6], [0.9, -0.6], [0, 0.8]]) { const l = cyl(0.06, 3.4, metal(0xc9cbd6), 10); l.position.set(x * 0.6, 1.5, z * 0.6); l.rotation.set(-z * 0.25, 0, x * 0.25); rig.add(l); }
  const motor = rbox(0.6, 0.5, 0.6, gloss(C.coral), 0.1); motor.position.y = 3.1; rig.add(motor);
  const core = cyl(0.22, 2.2, concrete({ seed: 190, clasts: 6 }), 24); rig.add(core);
  return { ...S, sea, core };
})();
const SURT = (() => {
  const S = newScene({ bg: 0xcfdde8, floor: false, key: [6, 12, 4], shadowSize: 18 });
  const sea = waves(70, 50, 80, gloss(0x6faecb, { roughness: 0.2 })); S.scene.add(sea);
  const isl = volcano(); isl.scale.set(1.1, 0.7, 1.1); isl.position.set(0, -0.6, -1); isl.traverse((m) => { if (m.isMesh && m.material.map) { m.material = stone({ base: '#6f6866', dots: '#4f4a49', dots2: '#8d8582', seed: 330, rough: 0.9 }); } }); S.scene.add(isl);
  const moss = new THREE.Mesh(new THREE.TorusGeometry(5.6, 0.5, 8, 48), matte(0x9fbf8f)); moss.rotation.x = Math.PI / 2; moss.position.set(0, 0.05, -1); moss.scale.set(1, 1, 0.4); S.scene.add(moss);
  const rig = new THREE.Group(); rig.position.set(1.5, 1.6, 1.5); S.scene.add(rig);
  for (const [x, z] of [[-0.9, -0.6], [0.9, -0.6], [0, 0.8]]) { const l = cyl(0.06, 3.0, metal(0xc9cbd6), 10); l.position.set(x * 0.6, 1.3, z * 0.6); l.rotation.set(-z * 0.25, 0, x * 0.25); rig.add(l); }
  const motor = rbox(0.6, 0.5, 0.6, gloss(C.coral), 0.1); motor.position.y = 2.8; rig.add(motor);
  const core = cyl(0.2, 2.0, stone({ base: '#7d7573', seed: 331 }), 20); rig.add(core);
  return { ...S, sea, core };
})();
export function s11(t) {
  const id = 's11';
  const tJ = cue(id, 'джексон', 0, 5), tSw = cue(id, 'оказалось', 0, 11), tMin = cue(id, 'вырастают', 0, 18), tHot = cue(id, 'обычно', 0, 26), tLime = cue(id, 'причём', 0, 33), tSu = cue(id, 'похожие', 0, 41), tX = cue(id, 'оценке', 0, 56), end = 70;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = CORE; S.sea.userData.update(t, 0.9); S.core.position.y = lerp(-1.0, 2.0, easeInOut(seg(t, 2.5, tSw - 1))); S.core.rotation.y = t * 2;
      orbit(S.cam, v3(0, 1.8, 0.4), lerp(12, 9.5, k), lerp(0.6, 0.35, k), 0.15); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2, 0.4), 0.0008) });
      pill('Мари Джексон · Университет Юты · 2017', 125, 980, t, tJ, { dot: '#8fd0e6', align: 'left', size: 36, out: tSw - 0.2 }); pill('керн римского причала · Тоскана', 125, 880, t, tJ + 1.4, { dot: '#8fd0e6', align: 'left', size: 36, out: tSw - 0.2 }); }],
    [tSw, (lt, k) => { const S = PORE; const g = 0;
      S.plates.forEach((b, i) => b.scale.setScalar(0.001)); S.fibers.forEach((f) => (f.scale.y = 0.001));
      S.sw.userData.ps.forEach((p, i) => { const ph = (t * 0.25 + hash(i)) % 1; const a = hash(i + 1) * 6.28; p.position.set(Math.cos(a) * lerp(3.4, 0.6, ph), lerp(2.5, -2.5, hash(i + 2)) * (1 - ph * 0.5), Math.sin(a) * lerp(3.4, 0.6, ph)); });
      S.ions.forEach((s, i) => { const ph = (t * 0.2 + i / 10) % 1; s.position.set(Math.cos(i * 1.7) * lerp(3.2, 1.6, ph), Math.sin(i * 2.3) * 1.4, -1.2 + Math.sin(i * 1.7) * lerp(2.2, 1.0, ph)); s.material.opacity = Math.sin(ph * Math.PI); });
      S.cam.position.set(Math.sin(t * 0.12) * 1.2, 0.3, 1.8); S.cam.lookAt(0, 0, -3); S.cam.updateMatrixWorld(); render(S.scene, S.cam, { time: t, focus: 3.5, aperture: 0.0015 });
      title('морская вода', 120, 220, t, tSw + 0.2, { size: 96, align: 'left', color: '#ffffff' }); title('растворяет пепел', 120, 330, t, tSw + 0.8, { size: 96, align: 'left', color: '#a9d6ff' }); }],
    [tMin, (lt, k) => { const S = PORE; const grow = easeOut(seg(t, tMin, tMin + 6));
      S.plates.forEach((b, i) => b.scale.setScalar(Math.max(0.001, clamp(grow * 1.4 - hash(i + 9) * 0.4)))); S.fibers.forEach((f, i) => (f.scale.y = Math.max(0.001, clamp(grow * 1.5 - hash(i + 60) * 0.5) * 1.6)));
      S.sw.userData.ps.forEach((p, i) => { const ph = (t * 0.25 + hash(i)) % 1; const a = hash(i + 1) * 6.28; p.position.set(Math.cos(a) * lerp(3.4, 0.6, ph), lerp(2.5, -2.5, hash(i + 2)) * (1 - ph * 0.5), Math.sin(a) * lerp(3.4, 0.6, ph)); });
      const az = lerp(0.3, -0.5, easeIO2(k)); S.cam.position.set(Math.sin(az) * 1.5, lerp(0.8, -0.2, k), Math.cos(az) * 1.5); S.cam.lookAt(Math.sin(az + 3.14) * 3, 0, Math.cos(az + 3.14) * 3); S.cam.updateMatrixWorld();
      render(S.scene, S.cam, { time: t, focus: 2.2, aperture: 0.002, maxblur: 0.012 });
      title('алюминиевый тоберморит', 120, 220, t, tMin + 0.8, { size: 80, align: 'left', color: '#ffffff' }); pill('пластинки и волокна держат трещины', 125, 330, t, tMin + 2.4, { dot: MINT, align: 'left', size: 40 });
      pill('обычно растёт только в жару', 125, 430, t, tHot, { dot: RED, align: 'left', size: 40 }); pill('а тут — в холодном море, веками', 125, 530, t, tHot + 2.5, { dot: '#8fd0e6', align: 'left', size: 40 }); }],
    [tLime, (lt, k) => { const S = CORE; S.sea.userData.update(t, 1.0); S.core.position.y = 2;
      orbit(S.cam, v3(0, 1.4, 0.4), lerp(8, 6.5, k), lerp(1.2, 0.9, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1.4, 0.4), 0.0012) });
      bars([{ label: 'известь работает', v: 0.25, color: '#ffe7a3', text: 'десятилетия' }, { label: 'море работает', v: 1, color: '#a9d6ff', text: 'века' }], 120, 240, t, tLime + 0.4, { w: 640 }); }],
    [tSu, (lt, k) => { const S = SURT; S.sea.userData.update(t, 0.8); S.core.position.y = lerp(-1, 1.8, easeInOut(seg(t, tSu + 3, tSu + 9))); S.core.rotation.y = t * 2;
      orbit(S.cam, v3(0, 1.5, 0), lerp(20, 15, k), lerp(0.3, -0.1, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1.5, 0), 0.0006) });
      title('остров Сюртсей', 120, 230, t, tSu + 0.6, { size: 100, align: 'left' }); pill('Исландия · вулкану ≈ 50 лет', 125, 340, t, tSu + 1.8, { dot: '#8f8783', align: 'left' }); pill('бурили дважды · через 35 лет', 125, 440, t, tSu + 5.5, { dot: '#8fd0e6', align: 'left' }); }],
    [tX, (lt, k) => { const S = CORE; S.sea.userData.update(t, 1.1); S.core.position.y = 2;
      orbit(S.cam, v3(0, 1, 0), lerp(16, 20, k), lerp(-0.4, -0.7, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1, 0), 0.0005) });
      counter('×' + Math.round(lerp(1, 100, easeOut(seg(t, tX + 0.6, tX + 2.4)))), 120, 340, { size: 240, align: 'left', color: PURPLE });
      title('дольше в морской воде', 130, 440, t, tX + 1.2, { size: 60, align: 'left' }); pill('оценка исследователей', 135, 540, t, tX + 2.0, { dot: '#8fd0e6', align: 'left', size: 36 }); }],
  ], end);
}

// ───────── s12. Помпеи ─────────
const SITE = (() => {
  const S = newScene({ bg: 0xf0dcc8, floorY: 0, key: [-5, 11, 8], shadowSize: 14 });
  S.ground.material = stone({ base: '#d9c4ab', dots: '#b49b80', dots2: '#ead9c4', n: 900, seed: 200, rep: 10 });
  const wall = new THREE.Group(); wall.position.set(-1.5, 0, -1); S.scene.add(wall);
  for (let r = 0; r < 7; r++) for (let c = 0; c < 9; c++) { if (r > 3 && c > 9 - (r - 2) * 2) continue; const b = rbox(0.62, 0.3, 0.5, (r + c) % 3 ? brick() : stone({ base: '#bfae96', seed: 205 + c % 4 }), 0.04); b.position.set(c * 0.66 - 2.6 + (r % 2) * 0.3, 0.16 + r * 0.32, 0.45); wall.add(b); }
  const coreW = rbox(5.4, 1.6, 0.6, concrete({ seed: 210, clasts: 14 }), 0.04); coreW.position.set(0, 0.8, -0.05); wall.add(coreW);
  for (const x of [-3.2, 3.4]) { const p = cyl(0.07, 3.6, wood(), 10); p.position.set(x, 1.8, 1.2); wall.add(p); }
  const plank = rbox(7, 0.1, 0.5, wood(), 0.03); plank.position.set(0.1, 2.4, 1.2); wall.add(plank);
  const piles = [pile('#f6f3ec', 1.0, 0.75, 21), pile('#8e8682', 1.0, 0.75, 22), pile('#cfc9c2', 1.1, 0.8, 23, null)];
  piles[2].material = stone({ base: '#bdb6ae', dots: '#f8f6f1', dots2: '#7d7570', n: 3000, seed: 24, rough: 0.2 });
  piles[0].position.set(2.8, 0, 2.0); piles[1].position.set(4.8, 0, 1.4); piles[2].position.set(3.6, 0, 3.6); piles.forEach((p) => S.scene.add(p));
  const bk = bucket(); bk.position.set(1.4, 0, 2.6); S.scene.add(bk);
  const tr = trowel(); tr.position.set(1.9, 0.05, 3.3); tr.rotation.y = 0.8; S.scene.add(tr);
  const ash = drops(80, 0x8a8380, 0.05); S.scene.add(ash);
  const blanket = rbox(16, 0.05, 12, matte(0x9b938e, { transparent: true, opacity: 0 }), 0.02); blanket.position.y = 0.02; S.scene.add(blanket);
  const lbl = [textSprite('известь + пепел, сухая смесь', { size: 44, bg: '#ffe7a3', scale: 0.6 }), textSprite('недостроенная стена', { size: 44, scale: 0.8 })];
  lbl[0].position.set(3.6, 1.45, 3.6); lbl[1].position.set(-1.5, 3.2, -0.6); lbl.forEach((l) => S.scene.add(l));
  return { ...S, wall, piles, ash, blanket, lbl };
})();
export function s12(t) {
  const id = 's12';
  const tPm = cue(id, 'помпеях', 0, 6), tV = cue(id, 'семьдесят', 0, 7.5), tSt = cue(id, 'стройку', 0, 11), tPl = cue(id, 'кстати', 0, 16), tPub = cue(id, 'девятого', 0, 23), tSm = cue(id, 'пробы', 0, 29), tPile = cue(id, 'кучах', 0, 35), tFirst = cue(id, 'ровно', 0, 41), tQ = cue(id, 'масич', 1, 44), tVit = cue(id, 'выходит', 0, 54), end = 64;
  clear2d();
  shot(t, [
    [0, (lt, k) => { const S = VOLC; S.ash.userData.update(t, 0.6 + 2 * smooth(seg(t, tV, tV + 3))); S.sea.userData.update(t, 0.5);
      orbit(S.cam, v3(0, 3.5, -2), lerp(40, 32, k), lerp(0.25, -0.1, k), 0.2); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 3, -2), 0.0004), vig: 0.22 + 0.15 * smooth(seg(t, tV, tV + 3)) });
      chapter(6, 'Помпеи', t, 0.2, 5.0); pill('79 год н. э. · Везувий', 125, 980, t, tV, { dot: RED, align: 'left', size: 40 }); }],
    [tSt, (lt, k) => { const S = SITE; const fall = smooth(seg(t, tSt, tSt + 4));
      S.ash.userData.ps.forEach((p, i) => { const ph = (t * 0.35 + hash(i)) % 1; p.position.set((hash(i + 1) - 0.5) * 14, lerp(8, 0.1, ph), (hash(i + 2) - 0.5) * 10); p.visible = ph < 0.98; });
      S.blanket.material.opacity = 0.35 * fall; S.lbl.forEach((l) => (l.visible = false));
      orbit(S.cam, v3(1, 1, 1), lerp(16, 13, k), lerp(0.7, 0.45, k), 0.25); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(1, 1, 1), 0.0007), fade: 0.1 * fall });
      title('стройка застыла', 120, 230, t, tSt + 0.4, { size: 96, align: 'left' }); pill('стена · кучи сырья · инструменты', 125, 340, t, tSt + 1.4, { dot: '#e9b97f', align: 'left' }); }],
    [tPl, (lt, k) => { const S = VOLC; S.ash.userData.update(t, 2.4); S.sea.userData.update(t, 1.2); const hh = S.sea.userData.h; S.ship.position.y = hh(4, 12, t, 1.2) + 0.15; S.ship.position.x = 4 - lt * 0.15;
      orbit(S.cam, v3(3, 2, 10), lerp(10, 8, k), lerp(-2.2, -2.0, k), 0.1); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(3.5, 1.5, 12), 0.0008), vig: 0.36 });
      title('Плиний Старший', 120, 230, t, tPl + 0.5, { size: 100, align: 'left' }); pill('погиб в том же извержении', 125, 340, t, tPl + 1.4, { dot: RED, align: 'left' }); pill('плыл спасать людей', 125, 440, t, tPl + 4.2, { dot: '#8fd0e6', align: 'left' }); }],
    [tPub, (lt, k) => { const S = SITE; S.ash.userData.ps.forEach((p) => (p.visible = false)); S.blanket.material.opacity = 0; popScale(S.lbl[1], t, tPub + 0.8); popScale(S.lbl[0], t, tPile + 0.3);
      orbit(S.cam, v3(1.4, 0.8, 1.2), lerp(12, 9.5, k), lerp(-0.2, 0.15, k), 0.22); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(1.5, 0.8, 1.5), 0.0009) });
      pill('Nature Communications · 9 декабря 2025', 125, 230, t, tPub + 0.3, { dot: PURPLE, align: 'left', size: 40 }); pill('пробы: кучи сырья · стройка · готовые стены · старый ремонт', 125, 330, t, tSm + 0.2, { dot: '#e9b97f', align: 'left', size: 34 }); }],
    [tPile, (lt, k) => { const S = SITE; popScale(S.lbl[0], t, tPile + 0.3); S.lbl[1].visible = false;
      orbit(S.cam, v3(3.6, 0.6, 3.6), lerp(5.5, 4.2, k), lerp(0.6, 0.25, k), 0.35); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(3.6, 0.5, 3.6), 0.0016) });
      title('первый шаг', 120, 230, t, tFirst, { size: 96, align: 'left', out: tQ - 0.2 }); title('горячего смешивания', 120, 340, t, tFirst + 0.5, { size: 84, align: 'left', color: RED, out: tQ - 0.2 }); }],
    [tQ, (lt, k) => { const S = SITE; S.lbl.forEach((l) => (l.visible = false)); orbit(S.cam, v3(0.5, 1, 0.5), lerp(14, 17, k), lerp(-0.6, -0.3, k), 0.3); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0.5, 1, 0.5), 0.0006) });
      quote('нам повезло открыть эту капсулу времени — стройку', 'Адмир Масич, MIT', 110, 150, t, tQ + 0.2, tVit + 0.2, { w: 860, size: 50 }); pill('материал может лечить себя тысячелетиями', 125, 620, t, cue(id, 'лечить', 0, 99) - 0.4, { dot: MINT, align: 'left', size: 40, out: tVit });
      stamp('НЕ ПО ВИТРУВИЮ', 560, 560, t, tVit + 0.4, { color: PURPLE, size: 56 }); }],
  ], end);
}

// ───────── s13. Что дальше ─────────
const CITY = (() => {
  const S = newScene({ bg: 0xdfe8f2, floorY: 0, key: [7, 13, 9], shadowSize: 22 });
  S.ground.material.color.set(0xd8dde6);
  const blds = []; for (let i = 0; i < 16; i++) { const h = 2 + hash(i) * 7; const b = rbox(1.6 + hash(i + 1), h, 1.6 + hash(i + 2), gloss([0xc6cde0, 0xd9dce9, 0xb9c4dc, 0xe4e1ef][i % 4], { roughness: 0.4 }), 0.12); b.position.set(-9 + (i % 8) * 2.5, h / 2, -6 - Math.floor(i / 8) * 3.2); S.scene.add(b); blds.push(b);
    for (let w = 0; w < Math.floor(h / 0.9); w++) { const win = rbox(1.1, 0.25, 0.02, gloss(0xa9d6ff, { emissive: 0x6fb0ff, emissiveIntensity: 0.1 }), 0.02); win.position.set(b.position.x, 0.6 + w * 0.9, b.position.z + b.geometry.parameters.depth / 2 + 0.01); S.scene.add(win); } }
  const deck = rbox(14, 0.6, 2.2, concrete({ base: '#c9c7c1', seed: 230 }), 0.08); deck.position.set(0, 2.6, 3); S.scene.add(deck);
  const piers = []; for (const x of [-5, 0, 5]) { const p = rbox(0.9, 2.4, 1.4, concrete({ base: '#c4c1bb', seed: 231 }), 0.06); p.position.set(x, 1.2, 3); S.scene.add(p); piers.push(p); }
  const cars = []; for (let i = 0; i < 4; i++) { const c = rbox(0.9, 0.35, 0.5, gloss([C.coral, C.butter, C.sky, C.mint][i]), 0.12); c.position.y = 3.1; S.scene.add(c); cars.push(c); }
  const glow = []; for (let i = 0; i < 12; i++) { const s = sphere(0.06, gloss(0xffffff, { emissive: 0xffffff, emissiveIntensity: 0.8 }), 8); s.position.set(-5 + (i % 3) * 5 + (hash(i) - 0.5) * 0.6, 0.3 + hash(i + 1) * 2, 3.71); S.scene.add(s); glow.push(s); }
  return { ...S, cars, glow, deck };
})();
export function s13(t) {
  const id = 's13', S = CITY;
  const tNo = cue(id, 'уступает', 0, 6), tIdea = cue(id, 'идею', 0, 10), tR = cue(id, 'исследователи', 0, 12), tDm = cue(id, 'один', 0, 16), tM = cue(id, 'масич', 0, 24), tLess = cue(id, 'меньше', 0, 23), tRom = cue(id, 'римляне', 0, 30), end = 42;
  S.cars.forEach((c, i) => { c.position.x = ((t * 1.6 + i * 3.5) % 16) - 8; c.position.z = 2.5 + (i % 2) * 0.9; });
  S.glow.forEach((g, i) => (g.visible = t > tR + 1 && Math.sin(t * 3 + i) > -0.3));
  clear2d();
  shot(t, [
    [0, (lt, k) => { orbit(S.cam, v3(0, 3, 0), lerp(24, 19, k), lerp(0.5, 0.25, k), 0.18); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2.5, 3), 0.0005) });
      chapter(7, 'Что дальше', t, 0.2, 5.0); }],
    [tNo, (lt, k) => { orbit(S.cam, v3(0, 2, 3), lerp(14, 12, k), lerp(-0.5, -0.3, k), 0.12); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2, 3), 0.0006) });
      bars([{ label: 'прочность', v: 1, color: '#a9d6ff', text: 'современный' }, { label: 'долговечность', v: 1, color: '#a9e6cf', text: 'римский' }], 120, 230, t, tNo + 0.2, { w: 620 }); }],
    [tR, (lt, k) => { orbit(S.cam, v3(0, 1.5, 3.7), lerp(7, 5.5, k), lerp(0.25, 0.05, k), 0.08); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 1.5, 3.7), 0.0014) });
      title('цемент со встроенным', 120, 230, t, tR + 0.4, { size: 80, align: 'left' }); title('«ремонтом»', 120, 330, t, tR + 0.9, { size: 96, align: 'left', color: PURPLE }); pill('стартап DMAT (Италия) — соавтор работы 2023', 125, 450, t, tDm + 0.4, { dot: '#e9b97f', align: 'left', size: 36 }); }],
    [tM, (lt, k) => { orbit(S.cam, v3(0, 3, 0), lerp(20, 26, k), lerp(0.2, 0.55, k), lerp(0.18, 0.3, k)); render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 2.5, 3), 0.0005) });
      counter('+' + Math.round(lerp(0, 100, easeOut(seg(t, tM + 1.4, tM + 3.4)))), 120, 330, { size: 220, align: 'left', color: PURPLE }); title('лет жизни бетону', 130, 430, t, tM + 1.8, { size: 64, align: 'left' });
      pill('меньше ремонта', 135, 560, t, tLess, { dot: MINT, align: 'left' }); pill('меньше сноса', 135, 660, t, tLess + 0.5, { dot: MINT, align: 'left' }); pill('меньше выбросов', 135, 760, t, tLess + 1.6, { dot: MINT, align: 'left' }); }],
    [tRom, (lt, k) => { const P = PAN; orbit(P.cam, v3(0, 4.5, 0), lerp(26, 22, k), lerp(-0.2, 0.15, k), 0.12); render(P.scene, P.cam, { time: t, ...dof(P.cam, v3(0, 4, 2), 0.0005) });
      title('без химии —', 120, 230, t, tRom + 0.2, { size: 96, align: 'left' }); title('одним опытом', 120, 340, t, tRom + 0.8, { size: 96, align: 'left', color: PURPLE }); }],
  ], end);
}

// ───────── s14. Финал ─────────
export function s14(t) {
  const id = 's14';
  const tB = cue(id, 'бетон', 0, 5), tQ = cue(id, 'думаешь', 0, 9), tNx = cue(id, 'следующей', 0, 15), tSub = cue(id, 'подпишись', 0, 22), tThx = cue(id, 'спасибо', 0, 27), end = ((window.VDUR && window.VDUR.s14) || 36) + 4.4;
  const S = PAN; S.scene.background.set(new THREE.Color(0xdbe9f3).lerp(new THREE.Color(0xf7d6b8), smooth(seg(t, 0, 8))));
  orbit(S.cam, v3(-3, 4.5, 0), lerp(30, 24, easeIO2(seg(t, 0, 20))), lerp(0.7, 0.2, easeIO2(seg(t, 0, 25))), 0.12);
  render(S.scene, S.cam, { time: t, ...dof(S.cam, v3(0, 4, 2), 0.0005), fade: 0.5 * easeIn(seg(t, end - 2.5, end)) });
  clear2d();
  pill('известь', 125, 230, t, 0.6, { dot: '#ffffff', align: 'left', out: tQ - 0.3 }); pill('+ вулканический пепел', 125, 330, t, 1.6, { dot: '#8f8783', align: 'left', out: tQ - 0.3 }); pill('+ вода', 125, 430, t, 2.6, { dot: '#8fd0e6', align: 'left', out: tQ - 0.3 }); pill('+ горячее смешивание', 125, 530, t, 3.6, { dot: RED, align: 'left', out: tQ - 0.3 });
  title('= бетон, который чинит себя', 120, 680, t, tB, { size: 72, align: 'left', color: PURPLE, out: tQ - 0.3 });
  title('дома, которые сами', 120, 260, t, tQ, { size: 90, align: 'left', out: tNx - 0.3 }); title('залечивают трещины?', 120, 370, t, tQ + 0.5, { size: 90, align: 'left', color: RED, out: tNx - 0.3 });
  pill('пиши в комментариях 👇', 125, 490, t, tQ + 3.0, { dot: MINT, align: 'left', out: tNx - 0.3 });
  pill('в следующей серии', 125, 230, t, tNx, { dot: PURPLE, align: 'left', size: 38, out: tSub - 0.3 }); title('сейсмоскоп Чжан Хэна', 120, 360, t, tNx + 0.8, { size: 84, align: 'left', out: tSub - 0.3 });
  pill('ПОДПИСАТЬСЯ', 125, 300, t, tSub, { bg: '#ff3b3b', color: '#ffffff', size: 60, align: 'left', weight: 900, padX: 50, padY: 26 });
  title('спасибо за лайк и просмотр ❤', 120, 520, t, tThx, { size: 70, align: 'left' });
}

export function thumb() {}
