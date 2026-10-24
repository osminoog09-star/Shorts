// Фон для Shorts «ведущий рассказывает» (вертикаль 1080×1920): детализированный 3D-предмет в тёмной студии.
// Ведущий и титры накладываются отдельным слоем (Remotion, прозрачный фон) — здесь только 3D.
import { THREE, C, render, clear2d, seg, smooth, easeIO2, lerp, matte, gloss, metal, studio, gear } from './engine.js';
import { v3, orbit, newScene, rbox, sphere, cyl, puck, textSprite } from './kit.js';

// ── процедурные текстуры (детали вместо «пластилина») ──
function canvasTex(w, h, draw, repeat = 1, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat, repeat); t.anisotropy = 8; if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t;
}
const rnd = (() => { let s = 7; return () => ((s = (s * 16807) % 2147483647) / 2147483647); })();
const woodMap = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#6e4127'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 260; i++) { const y = rnd() * h, a = 0.05 + rnd() * 0.12; g.strokeStyle = rnd() < 0.5 ? `rgba(60,32,18,${a})` : `rgba(190,130,85,${a})`; g.lineWidth = 1 + rnd() * 3; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x * 0.01 + i) * 6 + (rnd() - 0.5) * 3); g.stroke(); }
  for (let k = 0; k < 6; k++) { g.fillStyle = 'rgba(40,20,10,0.5)'; g.fillRect(0, (k / 6) * h, w, 3); } // стыки досок
});
const bronzeMap = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#9a6634'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 160; i++) { const x = rnd() * w, y = rnd() * h, r = 30 + rnd() * 120; const gr = g.createRadialGradient(x, y, 0, x, y, r); const c = rnd() < 0.6 ? '84,150,122' : '60,34,16'; gr.addColorStop(0, `rgba(${c},${0.18 + rnd() * 0.2})`); gr.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
  for (let i = 0; i < 300; i++) { g.strokeStyle = `rgba(255,230,190,${0.06 + rnd() * 0.1})`; g.lineWidth = 0.6; const x = rnd() * w, y = rnd() * h; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (rnd() - 0.5) * 60, y + (rnd() - 0.5) * 12); g.stroke(); } // царапины
});
const roughMap = canvasTex(512, 512, (g, w, h) => {/*lin*/ g.fillStyle = '#888'; g.fillRect(0, 0, w, h); for (let i = 0; i < 2000; i++) { const v = 90 + rnd() * 120 | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(rnd() * w, rnd() * h, 2 + rnd() * 10, 2 + rnd() * 10); } }, 1, false);
const marbleMap = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#cfc7bf'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(110,100,120,${0.15 + rnd() * 0.3})`; g.lineWidth = 0.6 + rnd() * 2.5; g.beginPath(); let x = rnd() * w, y = 0; g.moveTo(x, y); while (y < h) { x += (rnd() - 0.5) * 50; y += 20 + rnd() * 30; g.lineTo(x, y); } g.stroke(); }
});
const WOOD = new THREE.MeshStandardMaterial({ map: woodMap, bumpMap: woodMap, bumpScale: 0.6, roughness: 0.62, roughnessMap: roughMap });
const BRONZE = new THREE.MeshStandardMaterial({ map: bronzeMap, roughnessMap: roughMap, roughness: 0.5, metalness: 0.7, envMapIntensity: 0.8 });
const BRASS = metal(0xe2b56b, { roughness: 0.28 });
const MARBLE = new THREE.MeshStandardMaterial({ map: marbleMap, roughness: 0.4, envMapIntensity: 0.5 });
const IRON = metal(0x3b3d48, { roughness: 0.4 });

function bolt(r = 0.07) { const g = new THREE.Group(); const h = cyl(r, 0.05, BRASS, 6); h.rotation.x = Math.PI / 2; g.add(h); const d = rbox(r * 1.2, r * 0.25, 0.02, IRON, 0.01); d.position.z = 0.03; g.add(d); return g; }
function plaque(text, w = 2.2, h = 0.42) {
  const tex = canvasTex(1024, 200, (g, W, H) => {
    g.fillStyle = '#d9ab5f'; g.fillRect(0, 0, W, H); g.strokeStyle = '#7a5520'; g.lineWidth = 8; g.strokeRect(10, 10, W - 20, H - 20);
    g.font = '700 84px "NSerif", serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = 'rgba(255,240,200,0.6)'; g.fillText(text, W / 2 + 2, H / 2 + 3); g.fillStyle = '#5a3b12'; g.fillText(text, W / 2, H / 2); // гравировка
  });
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.04), [BRASS, BRASS, BRASS, BRASS, new THREE.MeshStandardMaterial({ map: tex, metalness: 0.7, roughness: 0.35 }), BRASS]);
  m.castShadow = true; return m;
}

const S = (() => {
  const S = newScene({ bg: 0x161b33, floorY: -2.6, key: [4, 10, 7], shadowSize: 12, keyI: 2.4, fill: 0.18 });
  S.scene.fog = new THREE.Fog(0x161b33, 14, 40);
  S.scene.background = new THREE.Color(0x161b33);
  // цветные контровые (как кольца на наушниках ведущего)
  const c1 = new THREE.PointLight(0x58c8ff, 30, 30); c1.position.set(-6, 3, -4); S.scene.add(c1);
  const c2 = new THREE.PointLight(0xff5fb0, 26, 30); c2.position.set(6, 2, -5); S.scene.add(c2);

  const G = new THREE.Group(); S.scene.add(G);
  // постамент из мрамора с бронзовым кольцом
  const ped = cyl(2.4, 1.0, MARBLE, 64); ped.position.y = -2.1; G.add(ped);
  const pr = new THREE.Mesh(new THREE.TorusGeometry(2.42, 0.06, 12, 96), BRASS); pr.rotation.x = Math.PI / 2; pr.position.y = -1.62; G.add(pr);
  // деревянный корпус
  const box = rbox(3.0, 3.6, 1.3, WOOD, 0.08); box.position.y = 0.2; G.add(box);
  const face = rbox(2.6, 3.2, 0.08, BRONZE, 0.05); face.position.set(0, 0.2, 0.68); G.add(face);
  for (const [x, y] of [[-1.35, 1.85], [1.35, 1.85], [-1.35, -1.45], [1.35, -1.45], [0, 1.85], [0, -1.45]]) { const b = bolt(); b.position.set(x, y, 0.66); G.add(b); }
  // циферблат: кольцо, деления, греческие знаки зодиака
  const dial = puck(1.05, 0.05, matte(0xf1e6d2)); dial.rotation.x = Math.PI / 2; dial.position.set(0, 0.45, 0.74); G.add(dial);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.07, 16, 120), BRASS); ring.position.set(0, 0.45, 0.78); G.add(ring);
  for (let i = 0; i < 72; i++) { const a = (i / 72) * Math.PI * 2; const L = i % 6 === 0 ? 0.16 : 0.08; const t = rbox(0.018, L, 0.02, IRON, 0.005); t.position.set(Math.cos(a) * (0.95 - L / 2), 0.45 + Math.sin(a) * (0.95 - L / 2), 0.79); t.rotation.z = a + Math.PI / 2; G.add(t); }
  const Z = ['ΚΡΙΟΣ', 'ΤΑΥΡΟΣ', 'ΔΙΔΥΜΟΙ', 'ΚΑΡΚΙΝΟΣ', 'ΛΕΩΝ', 'ΠΑΡΘΕΝΟΣ'];
  Z.forEach((z, i) => { const a = (i / 6) * Math.PI * 2 + 0.3; const s = textSprite(z, { size: 34, scale: 0.32, bg: null, color: '#5a3b12', font: 'NSerif' }); s.position.set(Math.cos(a) * 0.66, 0.45 + Math.sin(a) * 0.66, 0.8); G.add(s); });
  const sunP = new THREE.Group(); sunP.position.set(0, 0.45, 0.84); G.add(sunP);
  const sp = rbox(0.05, 0.85, 0.03, BRASS, 0.02); sp.position.y = 0.42; sunP.add(sp);
  const sb = sphere(0.12, gloss(0xffd36b, { emissive: 0xffaa00, emissiveIntensity: 0.4 })); sb.position.y = 0.85; sunP.add(sb);
  const moonP = new THREE.Group(); moonP.position.set(0, 0.45, 0.88); G.add(moonP);
  const mp = rbox(0.04, 0.62, 0.03, metal(0xdfe6f2), 0.02); mp.position.y = 0.31; moonP.add(mp);
  const mb = sphere(0.1, gloss(0xdfe6f2)); mb.position.y = 0.62; moonP.add(mb);
  const pin = cyl(0.07, 0.12, BRASS, 16); pin.rotation.x = Math.PI / 2; pin.position.set(0, 0.45, 0.9); G.add(pin);
  const pl = plaque('ΑΝΤΙΚΥΘΗΡΑ'); pl.position.set(0, -1.0, 0.74); G.add(pl);
  // ручка сбоку
  const crank = new THREE.Group(); crank.position.set(1.55, 0.2, 0); G.add(crank);
  const ax = cyl(0.07, 0.4, IRON, 16); ax.rotation.z = Math.PI / 2; ax.position.x = 0.15; crank.add(ax);
  const arm = rbox(0.1, 0.9, 0.1, BRASS, 0.04); arm.position.set(0.35, 0.4, 0); crank.add(arm);
  const knob = cyl(0.1, 0.35, WOOD, 16); knob.rotation.z = Math.PI / 2; knob.position.set(0.5, 0.8, 0); crank.add(knob);
  // открытые шестерни сзади-сбоку (бронза с патиной)
  const gears = [];
  [[64, 1.1, -1.6, 1.4, -0.9], [24, 0.45, -0.25, 1.95, -0.9], [48, 0.85, 1.65, 1.5, -1.0], [32, 0.6, 2.2, 0.0, -0.8]].forEach(([n, r, x, y, z], i) => {
    const g = gear(n, r, BRONZE, { thick: 0.09, spokes: 4 }); g.position.set(x, y, z); G.add(g); gears.push({ g, s: (i % 2 ? -1 : 1) * (64 / n) });
  });
  // боке-огни сзади
  const bk = [];
  for (let i = 0; i < 26; i++) { const m = sphere(0.08 + rnd() * 0.12, new THREE.MeshBasicMaterial({ color: rnd() < 0.5 ? 0x58c8ff : 0xff7fc0, transparent: true, opacity: 0.85 }), 12); m.position.set((rnd() - 0.5) * 18, 1 + rnd() * 10, -8 - rnd() * 6); m.scale.setScalar(2.2); S.scene.add(m); bk.push(m); }
  // колонны на заднем плане
  for (const x of [-7, 7]) { const col = cyl(0.55, 9, MARBLE, 32); col.position.set(x, 1.8, -6); S.scene.add(col); for (let k = 0; k < 12; k++) { const fl = rbox(0.08, 8.8, 0.08, matte(0xd8d0c6), 0.03); const a = (k / 12) * Math.PI * 2; fl.position.set(x + Math.cos(a) * 0.55, 1.8, -6 + Math.sin(a) * 0.55); S.scene.add(fl); } }
  return { ...S, G, sunP, moonP, crank, gears, bk };
})();

export function host1(t) {
  // такты под реплики (см. shorts/host_demo.json → window.HOSTBEATS); по умолчанию 4 равных части
  const B = window.HOSTBEATS || [0, 5, 13, 18, 24];
  const turn = smooth(seg(t, B[1] + 1.0, B[2] + 0.5)) * 6 + smooth(seg(t, B[3], B[4])) * 2;
  S.crank.rotation.x = -turn * Math.PI * 2;
  S.sunP.rotation.z = -turn * 0.8; S.moonP.rotation.z = -turn * 10.7 * 0.8 * 0.25 - t * 0.05;
  S.gears.forEach(({ g, s }) => { g.rotation.z = (turn * 2 + t * 0.06) * s; });
  S.bk.forEach((m, i) => { m.position.y += Math.sin(t * 0.4 + i) * 0.0015; });
  S.G.rotation.y = Math.sin(t * 0.25) * 0.12;
  // камера: наезд на хуке → облёт к шестерням (макро) → общий план → финал
  const k1 = easeIO2(seg(t, 0, B[1])), k2 = easeIO2(seg(t, B[1], B[2])), k3 = easeIO2(seg(t, B[2], B[3])), k4 = easeIO2(seg(t, B[3], B[4]));
  let r = lerp(19, 15.5, k1), az = lerp(-0.25, 0.05, k1), el = lerp(0.1, 0.05, k1);
  let tg = v3(0, -1.3, 0);
  r = lerp(r, 7.5, k2); az = lerp(az, 1.0, k2); el = lerp(el, 0.12, k2); tg.lerp(v3(1.9, -0.4, -0.9), k2);
  r = lerp(r, 17, k3); az = lerp(az, -0.35, k3); el = lerp(el, 0.08, k3); tg.lerp(v3(0, -1.5, 0), k3);
  r = lerp(r, 16, k4); az = lerp(az, 0.15, k4); tg.lerp(v3(0, -1.3, 0), k4);
  orbit(S.cam, tg, r, az, el);
  const focusP = k2 > 0.3 && k3 < 0.5 ? v3(1.65, 1.5, -1.0) : v3(0, 0.45, 0.7);
  render(S.scene, S.cam, { time: t, focus: S.cam.position.distanceTo(focusP), aperture: k2 > 0.3 && k3 < 0.5 ? 0.0028 : 0.0012, maxblur: 0.012, vig: 0.35 });
  clear2d();
}

// ── студия ведущего (крупный план, фон в боке) ──
import { makeHost, animateHost } from './host3d.js';
import { makeAnimeHost, animateAnimeHost } from './host_anime.js';
const HS = (() => {
  const S = newScene({ bg: 0x141a33, floorY: -4.5, key: [3, 6, 8], shadowSize: 8, keyI: 2.2, fill: 0.3 });
  S.scene.background = new THREE.Color(0x141a33); S.scene.fog = new THREE.Fog(0x141a33, 12, 30);
  const c1 = new THREE.PointLight(0x58c8ff, 22, 14); c1.position.set(-4, 2, -2); S.scene.add(c1);
  const c2 = new THREE.PointLight(0xff5fb0, 20, 14); c2.position.set(4, 1.5, -2); S.scene.add(c2);
  const host = makeAnimeHost(); host.position.y = -0.6; S.scene.add(host);
  // фон: шестерни и огни (в расфокусе)
  [[64, 1.6, -3.2, 2.2, -6], [32, 0.9, 3.4, 3.0, -7], [48, 1.2, 2.8, -0.8, -6.5]].forEach(([n, r, x, y, z]) => { const g = gear(n, r, BRONZE, { thick: 0.12, spokes: 4 }); g.position.set(x, y, z); S.scene.add(g); host.userData['g' + n] = g; });
  for (let i = 0; i < 30; i++) { const m = sphere(0.12, new THREE.MeshBasicMaterial({ color: rnd() < 0.5 ? 0x58c8ff : 0xff7fc0, transparent: true, opacity: 0.8 }), 10); m.position.set((rnd() - 0.5) * 16, -2 + rnd() * 9, -8 - rnd() * 6); m.scale.setScalar(2); S.scene.add(m); }
  return { ...S, host };
})();
export function hostShot(t, { pose = 'talk', prev = 'rest', k = 1, mouth = 0, push = 0 } = {}) {
  animateAnimeHost(HS.host, t, { pose, prev, k, mouth, look: Math.sin(t * 0.4) * 0.3 });
  ['g64', 'g32', 'g48'].forEach((n, i) => { const g = HS.host.userData[n]; if (g) g.rotation.z = t * (i % 2 ? -0.2 : 0.15); });
  const tg = v3(0, 0.9 - push * 0.2, 0);
  orbit(HS.cam, tg, lerp(12.5, 10.5, push), Math.sin(t * 0.3) * 0.08, 0.06);
  render(HS.scene, HS.cam, { time: t, focus: HS.cam.position.distanceTo(v3(0, 0.6, 0.8)), aperture: 0.004, maxblur: 0.014, vig: 0.4 });
  clear2d();
}
