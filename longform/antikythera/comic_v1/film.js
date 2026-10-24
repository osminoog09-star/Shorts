import { THREE, C, CSS, W, H, render, toon, lights, gear, clear2d, ctx, sticker, burst, speedLines, caption, iconSticker, dotWipe,
  clamp, lerp, seg, smooth, easeInOut, easeOut, backOut, spring, pop, noise1, project } from './engine.js';

// ───────── иконки ─────────
function crossed(drawBody) {
  return (c, pass, cut) => {
    const stroke = (w, col) => { c.lineWidth = w; c.strokeStyle = col; };
    const body = () => drawBody(c);
    if (pass === 'shadow') { c.fillStyle = 'rgba(0,0,0,.35)'; c.strokeStyle = 'rgba(0,0,0,.35)'; c.lineWidth = cut * 2 + 14; body(); c.stroke(); c.fill(); return; }
    if (pass === 'cut') { c.fillStyle = '#fff'; stroke(cut * 2 + 14, '#fff'); body(); c.stroke(); c.fill(); return; }
    body(); c.fillStyle = CSS.blue; c.fill(); stroke(10, CSS.ink); c.stroke();
  };
}
const ICONS = {
  screen: (c) => { c.beginPath(); c.roundRect(-95, -70, 190, 120, 14); c.moveTo(-30, 50); c.lineTo(-45, 85); c.lineTo(45, 85); c.lineTo(30, 50); },
  plug: (c) => { c.beginPath(); c.roundRect(-55, -40, 110, 90, 20); c.moveTo(-30, -40); c.lineTo(-30, -90); c.moveTo(30, -40); c.lineTo(30, -90); c.moveTo(0, 50); c.lineTo(0, 95); },
  chip: (c) => { c.beginPath(); c.roundRect(-60, -60, 120, 120, 12); for (let i = -1; i <= 1; i++) { c.moveTo(-60, i * 35); c.lineTo(-90, i * 35); c.moveTo(60, i * 35); c.lineTo(90, i * 35); c.moveTo(i * 35, -60); c.lineTo(i * 35, -90); c.moveTo(i * 35, 60); c.lineTo(i * 35, 90); } },
};
function redCross(x, y, p, s = 1) {
  if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  const seg1 = clamp(p * 2), seg2 = clamp(p * 2 - 1);
  for (const [w, col] of [[44, '#fff'], [26, CSS.ink], [14, CSS.red]]) {
    ctx.lineWidth = w; ctx.strokeStyle = col; ctx.beginPath();
    ctx.moveTo(-90, -90); ctx.lineTo(-90 + 180 * seg1, -90 + 180 * seg1);
    if (seg2 > 0) { ctx.moveTo(90, -90); ctx.lineTo(90 - 180 * seg2, -90 + 180 * seg2); }
    ctx.stroke();
  }
  ctx.restore();
}

// ───────── сцена 01: хук ─────────
const S1 = (() => {
  const scene = new THREE.Scene();
  lights(scene, { key: [4, 7, 9] });
  const cam = new THREE.PerspectiveCamera(38, W / H, 0.1, 200);
  const K = 22; // зубьев на единицу радиуса
  const gears = [];
  function add(r, x, y, z, color, phase = 0, ratioTo = null, opts = {}) {
    const teeth = Math.round(r * K);
    const m = gear(teeth, r, color, { thick: 0.38, spokes: r > 1 ? 4 : (r > 0.6 ? 3 : 0), holeR: 0.16, ...opts });
    m.position.set(x, y, z); scene.add(m);
    const g = { m, r, teeth, phase, ratio: 1 };
    gears.push(g); return g;
  }
  const pitch = (r) => r * 0.94;
  // главный привод
  const A = add(2.4, 0, 0, 0, C.bronze);
  const B = add(1.0, pitch(2.4) + pitch(1.0), 0.0, 0, C.sun);
  const ang1 = 2.2; // направление размещения следующей
  const Cg = add(0.7, B.m.position.x + Math.cos(ang1) * (pitch(1.0) + pitch(0.7)), Math.sin(ang1) * (pitch(1.0) + pitch(0.7)), 0, C.patina);
  const D = add(1.4, -(pitch(2.4) + pitch(1.4)) * Math.cos(0.5), -(pitch(2.4) + pitch(1.4)) * Math.sin(0.5), -0.25, C.red);
  const E = add(0.55, 0, 0, 0.2, C.patina, 0, null, { spokes: 0 });
  // передаточные отношения (сцепление: обратное направление, отношение зубьев)
  A.ratio = 1; B.ratio = -A.teeth / B.teeth; Cg.ratio = -B.ratio * B.teeth / Cg.teeth * -1; D.ratio = -A.teeth / D.teeth; E.ratio = 1;
  Cg.ratio = (B.teeth / Cg.teeth) * -B.ratio; // C вращается против B
  // фазы, чтобы зубья входили между зубьями
  B.phase = Math.PI / B.teeth; D.phase = Math.PI / D.teeth; Cg.phase = Math.PI / Cg.teeth + 0.1;
  // ось и штифт
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 1.2, 24), toon(C.paper));
  axle.rotation.x = Math.PI / 2; scene.add(axle);
  // пол-подложка «бумага» далеко сзади для глубины
  const back = new THREE.Group(); scene.add(back);
  for (let i = 0; i < 9; i++) {
    const r = 0.5 + (i % 3) * 0.45;
    const m = gear(Math.round(r * K), r, [C.patina, C.sun, C.pink][i % 3], { thick: 0.3, spokes: 3 });
    m.position.set(-9 + i * 2.3, ((i * 37) % 7) - 3.2, -7 - (i % 3) * 2.5);
    back.add(m);
  }
  function update(t) {
    const w = 0.55 + 0.35 * smooth(seg(t, 0, 2));
    const turn = t * w;
    for (const g of gears) g.m.rotation.z = turn * g.ratio + g.phase;
    E.m.rotation.z = -turn * 2.2;
    back.children.forEach((m, i) => { m.rotation.z = turn * (i % 2 ? 0.6 : -0.8); });
    // камера: облёт по дуге + медленный наезд, на конце рывок внутрь
    const a = lerp(-0.95, -0.25, easeInOut(seg(t, 0, 15)));
    const dist = lerp(12.5, 8.6, easeInOut(seg(t, 0, 14))) - 6.0 * Math.pow(seg(t, 15.6, 17.6), 2.2);
    cam.position.set(Math.sin(a) * dist, 3.2 + Math.sin(t * 0.5) * 0.5, Math.cos(a) * dist);
    cam.lookAt(-1.2 + 0.4 * Math.sin(t * 0.3), -0.3, 0);
    cam.rotation.z += Math.sin(t * 0.37) * 0.03;
    cam.updateMatrixWorld();
  }
  return { scene, cam, update };
})();

function s01(t) {
  S1.update(t);
  render(S1.scene, S1.cam, { time: t, bg: C.sea, line: 3.2 });
  clear2d();
  // «2000+ ЛЕТ»
  const p = pop(t, 1.6, 0.7);
  sticker('2000+ лет', 520, 230, { size: 150, fill: CSS.sun, rot: -0.08, sx: p.sx, sy: p.sy });
  // три перечёркнутых стикера
  const items = [['screen', 4.3, 'нет экрана'], ['plug', 5.2, 'нет тока'], ['chip', 6.8, 'нет чипа']];
  items.forEach(([k, t0, lbl], i) => {
    const q = pop(t, t0, 0.6);
    const x = 1180 + i * 260, y = 290 + (i % 2) * 60;
    iconSticker(crossed(ICONS[k]), x, y, { s: 0.75 * q.s, rot: (i - 1) * 0.12 });
    redCross(x, y, easeOut(seg(t, t0 + 0.35, t0 + 0.65)), 0.75 * q.s);
    sticker(lbl, x, y + 125, { size: 40, fill: CSS.paper, sx: q.sx * 0.9, sy: q.sy * 0.9, cut: 10, line: 5, shadow: 6 });
  });
  // «ЗАТМЕНИЯ!»
  const e = pop(t, 9.6, 0.7);
  burst('затмения!', 1460, 760, { s: e.s, fill: CSS.sun, txt: CSS.red, size: 70, r: 150, seed: 2 });
  speedLines(1460, 760, { r0: 260, r1: 420, alpha: clamp(1 - seg(t, 9.6, 10.6)) * (t > 9.6 ? 1 : 0), seed: 5 });
  // «другие компьютеры…?»
  const q = pop(t, 14.5, 0.6);
  sticker('…другие компьютеры?', 960, 900, { size: 74, fill: CSS.pink, rot: 0.03, sx: q.sx, sy: q.sy });
  dotWipe(seg(t, 16.3, 17.8), {});
}

export const SCENES = [{ dur: 17.8, fn: s01, voice: 's01', vo: 0.6 }];
export const DURATION = SCENES.reduce((a, s) => a + s.dur, 0);
export function renderAt(t) {
  let acc = 0;
  for (const s of SCENES) { if (t < acc + s.dur || s === SCENES[SCENES.length - 1]) { s.fn(t - acc); return; } acc += s.dur; }
}
