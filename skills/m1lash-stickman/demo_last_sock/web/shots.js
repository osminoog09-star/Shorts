// ---------- «Последний носок» — M1lash stickman demo, 9:16, no narration ----------
const HERO = { cols: PAL.blue, hat: 'none', belt: false };
const C = (base, extra) => Object.assign({}, base, extra);
const run = (t, sp = 16, amp = .8) => ({ L: [Math.sin(t * sp) * amp + .1, -Math.max(0, Math.sin(t * sp + 1)) * 1.1], R: [-Math.sin(t * sp) * amp + .1, -Math.max(0, -Math.sin(t * sp + 1)) * 1.1] });
const pump = (t, sp = 16, amp = 1) => ({ L: [.4 - Math.sin(t * sp) * amp, -1.6], R: [.4 + Math.sin(t * sp) * amp, -1.6] });
const hh = (t, a = 4) => shake(t * .35, a, 1, 2);

const SHOTS = [];

// 1 · HOOK (0–3.4): the last clean sock slides away by itself
SHOTS.push({ start: 0, end: 3.4, tr: 'whip', draw(ctx, lt, t) {
  const h = hh(t, 4); const cam = { x: 600 + h[0] + lt * 20, y: 1180 + h[1], z: 1.08 + lt * .05 };
  roomBG(ctx, t, cam, { winX: 640, frameX: 120 });
  applyCam(ctx, cam, 1);
  drawCouch(ctx, 120, FLOOR, 1);
  drawAlarm(ctx, -230, FLOOR - 400, .8, '07:59', lt > 2.6 ? 1 : 0, t);
  const sx = kf(lt, [[.3, 760], [2.9, 1020, easeIn]]); const wob = Math.sin(lt * 18) * .08;
  drawSock(ctx, sx, FLOOR - 60, 190, wob, 1);
  // suction streaks pulling to the right
  const sa = kf(lt, [[.4, 0], [.9, 1]]);
  ctx.save(); ctx.globalAlpha = sa * .9; for (let k = 0; k < 5; k++) { const ph = (lt * 1.8 + k / 5) % 1; const x0 = sx - 200 + ph * 500; line(ctx, x0, FLOOR - 60 - k * 18, x0 + 120, FLOOR - 55 - k * 18, 7, '#fff'); } ctx.restore();
  // hero hopping on one bare foot, grabbing after it
  const lean = kf(lt, [[0, .15], [1.2, .45], [3, .55]]); const hop = Math.abs(Math.sin(lt * 9)) * -40;
  const reach = [kf(lt, [[0, .3], [2.5, .55]]), -.05];
  drawStick(ctx, C(HERO, { x: 560 + lt * 70, y: FLOOR + hop, s: 760, lean, bob: 0,
    legs: { L: [.25, -.2], R: [-.9, -1.4] }, arms: { L: [1.5, -.3], R: { ik: reach, bend: -1 } },
    face: { eyes: lt > .9 ? 'wide' : 'normal', look: [1, .6], mouth: lt > .9 ? 'o' : 'flat', browUp: lt > .9 ? 1 : 0 } }));
  // his other sock is already on the left foot
  drawSock(ctx, 560 + lt * 70 - 70, FLOOR + hop - 30, 90, 0, -1);
  bubble(ctx, 470 + lt * 70, 760, 'СТОЙ!', 66, kf(lt, [[1.3, 0], [1.5, 1], [3.1, 1], [3.3, 0]]), 1);
} });

// 2 · REVEAL (3.4–6.6): a robot vacuum wakes up and swallows the sock
SHOTS.push({ start: 3.4, end: 6.6, tr: 'cut', draw(ctx, lt, t) {
  const slurp = kf(lt, [[1.5, 0], [2.3, 1, easeIn]]);
  const sh = slurp > 0 && slurp < 1 ? shake(t, 14) : [0, 0]; const h = hh(t, 3);
  const cam = { x: 620 + h[0] + sh[0], y: 1500 + h[1] + sh[1], z: 1.45 + lt * .07 };
  roomBG(ctx, t, cam, { window: false, frame: false });
  applyCam(ctx, cam, 1);
  const glow = kf(lt, [[.25, 0], [.6, 1, backOut]]);
  const r = 300, vx = 760;
  // sock disappearing into the intake
  if (slurp < 1) drawSock(ctx, lerp(vx - r - 60, vx - r * .6, slurp), FLOOR - 40 - Math.sin(lt * 25) * 6 * (1 - slurp), 150 * (1 - slurp * .7), Math.sin(lt * 20) * .2, 1);
  drawVac(ctx, vx, FLOOR, r, { dir: -1, glow, mood: lt > .9 ? 'angry' : '', spin: t * 14, suck: kf(lt, [[.5, 0], [.8, 1], [2.3, 1], [2.6, 0]]), t, look: kf(lt, [[2.4, 0], [2.8, -1]]), hop: slurp > .95 && slurp < 1 ? -10 : 0 });
  if (lt > 2.3 && lt < 2.9) burst(ctx, vx - r * .6, FLOOR - 140, 90 * (1 - (lt - 2.3) / .6), 9, '#fff', 4);
  flash(ctx, kf(lt, [[.3, 0], [.4, .35], [.6, 0]]), '#ff3030');
} });

// 3 · CHASE (6.6–11.0): across the parquet
SHOTS.push({ start: 6.6, end: 11.0, tr: 'whip', draw(ctx, lt, t) {
  const vacX = 500 + lt * 520, heroX = lt * 470 + 40;
  const h = hh(t, 6); const cam = { x: heroX + 380 + h[0], y: 1240 + h[1], z: 1.0 };
  roomBG(ctx, t, cam, { winX: 1400, frameX: 400 });
  applyCam(ctx, cam, 1);
  for (let k = 0; k < 4; k++) { const px = vacX - 260 - k * 140, a = clamp(1 - k * .22); puff(ctx, px, FLOOR - 40 - k * 6, 40 + k * 14, t, '#efe6d6', 3 + k + Math.floor(t * 6), a * .9); }
  drawVac(ctx, vacX, FLOOR, 210, { dir: 1, glow: 1, mood: 'angry', spin: t * 30, t, hop: -Math.abs(Math.sin(t * 22)) * 8 });
  drawStick(ctx, C(HERO, { x: heroX, y: FLOOR - Math.abs(Math.sin(t * 16)) * 30, s: 700, lean: .32, legs: run(t), arms: pump(t),
    face: { eyes: 'normal', look: [1, 0], mouth: 'teeth', browAng: .35 } }));
  drawSock(ctx, heroX - 70, FLOOR - 30 - Math.abs(Math.sin(t * 16)) * 30, 80, Math.sin(t * 16) * .5, -1);
  bubble(ctx, heroX + 40, 830, 'ОТДАЙ!', 70, kf(lt, [[.8, 0], [1.0, 1], [2.6, 1], [2.8, 0]]), -1);
  speedLines(ctx, .8, t, -1);
} });

// 4 · OBSTACLE (11.0–14.6): vacuum dives under the couch, hero slides and bonks
SHOTS.push({ start: 11.0, end: 14.6, tr: 'cut', draw(ctx, lt, t) {
  const bonk = lt > 2.0; const sh = bonk && lt < 2.5 ? shake(t, 22) : [0, 0]; const h = hh(t, 3);
  const cam = { x: 620 + h[0] + sh[0], y: 1280 + h[1] + sh[1], z: 1.1 };
  roomBG(ctx, t, cam, { winX: 200, frameX: 760 });
  applyCam(ctx, cam, 1);
  const vacX = kf(lt, [[0, -200], [1.2, 760, easeOut]]);
  if (vacX < 700) drawVac(ctx, vacX, FLOOR, 200, { dir: 1, glow: 1, mood: 'angry', spin: t * 30, t });
  drawCouch(ctx, 900, FLOOR, 1, lt > 1.2 ? 1 : 0);
  // hero: run in -> dive -> slide -> bonk into the couch arm
  const phase = kf(lt, [[.6, 0], [1.1, 1]]);
  const hx = kf(lt, [[0, -350], [1.1, 120], [2.0, 400, easeOut], [3.6, 400]]);
  const lean = lerp(.3, Math.PI / 2, phase);
  const y = FLOOR - phase * 40;
  drawStick(ctx, C(HERO, { x: hx - phase * 300, y, s: 680, lean,
    legs: phase < 1 ? run(t) : { L: [.15, -.1], R: [-.1, -.2] }, arms: phase < .5 ? pump(t) : { L: [2.9, 0], R: [2.8, .1] },
    face: { eyes: bonk ? 'spiral' : 'wide', mouth: bonk ? 'o' : 'teeth', browAng: bonk ? 0 : .3 }, t }));
  if (bonk) {
    const k = clamp((lt - 2.0) / .5); if (k < 1) burst(ctx, 470, FLOOR - 120, 150 * (1 - k * .5), 11, '#ffd23a', 5);
    for (let i = 0; i < 3; i++) { const a = t * 6 + i * TAU / 3; star5(ctx, 360 + Math.cos(a) * 110, FLOOR - 230 + Math.sin(a) * 35, 26, a); }
  }
} });

// 5 · TUG OF WAR (14.6–19.6): the sock sticks out from under the couch
SHOTS.push({ start: 14.6, end: 19.6, tr: 'cut', draw(ctx, lt, t) {
  const lift = kf(lt, [[2.0, 0], [3.2, 1, easeOut]]);
  const amp = 4 + lift * 16 + (lt > 4 ? 10 : 0); const sh = shake(t, amp, 1.4); const h = hh(t, 3);
  const cam = { x: lerp(520, 760, lift) + h[0] + sh[0], y: 1280 + h[1] + sh[1], z: 1.15 + lt * .02 };
  roomBG(ctx, t, cam, { winX: 160, frameX: 900 });
  applyCam(ctx, cam, 1);
  drawCouch(ctx, 1150, FLOOR, 1, .6 + .4 * Math.sin(t * 8) ** 2);
  // the red eye in the darkness under the couch
  ctx.save(); ctx.shadowColor = '#ff2a2a'; ctx.shadowBlur = 30; circle(ctx, 1080, FLOOR - 45, 16); ctx.fillStyle = '#ff3a3a'; ctx.fill(); ctx.restore();
  const tug = Math.sin(t * 7) * 30 * (1 - lift) - lift * 60;
  // hero: braced and leaning back, then lifted off his feet by the suction
  const lean = lerp(-.55, Math.PI / 2 - .1, lift) + Math.sin(t * 11) * .05 * lift;
  const hx = lerp(440, 260, lift) + tug, hy = FLOOR - lift * 330, S = 640;
  const G = [lerp(hx - 10, hx + 530, lift), lerp(hy - 300, hy - 20, lift)];          // where his fists grip the sock
  const loc = ([X, Y]) => { const dx = (X - hx) / S, dy = (Y - hy) / S, c = Math.cos(-lean), s = Math.sin(-lean); return [dx * c - dy * s, dx * s + dy * c]; };
  // the sock, stretched like a rope from the dark gap to his fists
  const P0 = [990, FLOOR - 45], sag = 40 * (1 - lift) + Math.sin(t * 9) * 10;
  const mid = [(P0[0] + G[0]) / 2, (P0[1] + G[1]) / 2 + sag];
  for (const [w, c] of [[50, INK], [36, '#ffcf33']]) { ctx.beginPath(); ctx.moveTo(...P0); ctx.quadraticCurveTo(...mid, ...G); ctx.lineWidth = w; ctx.strokeStyle = c; ctx.lineCap = 'round'; ctx.stroke(); }
  for (const k of [.06, .12, .18]) { const q = 1 - k; const x = (1 - q) ** 2 * P0[0] + 2 * (1 - q) * q * mid[0] + q * q * G[0], y = (1 - q) ** 2 * P0[1] + 2 * (1 - q) * q * mid[1] + q * q * G[1]; circle(ctx, x, y, 15); ctx.fillStyle = '#2f63c9'; ctx.fill(); }
  const flap = lift > .2 ? { L: [Math.sin(t * 20) * .6 + .2, -.6], R: [-Math.sin(t * 20) * .6 + .2, -.6] } : { L: [-.4, -.3], R: [.35, -.1] };
  drawStick(ctx, C(HERO, { x: hx, y: hy, s: S, lean, legs: flap,
    arms: { L: { ik: loc(G), bend: 1 }, R: { ik: loc(G), bend: -1 } },
    face: { eyes: lift > .5 ? 'wide' : 'squint', mouth: 'teeth', browAng: .4 }, shadow: lift < .3 }));
  const head = [hx + .765 * S * Math.sin(lean), hy - .765 * S * Math.cos(lean)];
  if (lt > 1) sweat(ctx, head[0] - 110, head[1] - 90 + Math.sin(t * 9) * 10, 30, 1);
  bubble(ctx, 520, 760, 'НУ УЖ НЕТ!', 62, kf(lt, [[.3, 0], [.5, 1], [1.9, 1], [2.1, 0]]), 1);
  bubble(ctx, 720, 700, 'А-А-А!', 76, kf(lt, [[3.3, 0], [3.5, 1], [4.8, 1], [5.0, 0]]), -1);
} });

// 6 · POP (19.6–22.6): the sock rips free, hero flies back with it
SHOTS.push({ start: 19.6, end: 22.6, tr: 'whip', draw(ctx, lt, t) {
  const h = hh(t, 4); const sh = lt < .5 ? shake(t, 26) : [0, 0];
  const cam = { x: 560 + h[0] + sh[0], y: 1250 + h[1] + sh[1], z: 1.0 };
  roomBG(ctx, t, cam, { winX: 120, frameX: 700 });
  applyCam(ctx, cam, 1);
  drawCouch(ctx, 1150, FLOOR, 1, kf(lt, [[0, 1], [.6, 0]]));
  const k = kf(lt, [[0, 0], [1.2, 1, easeOut]]);
  const hx = lerp(700, 330, k), hy = FLOOR - Math.sin(k * Math.PI) * 420;
  const land = lt > 1.2;
  drawStick(ctx, C(HERO, { x: hx, y: land ? FLOOR : hy, s: 680, lean: land ? 0 : -k * TAU * .9,
    legs: land ? { L: [1.3, -1.4], R: [1.5, -1.6] } : { L: [.8, -.4], R: [-.6, -.3] }, squash: land ? kf(lt, [[1.2, .8], [1.45, 1, backOut]]) : 1,
    arms: land ? { L: [2.6, .2], R: [2.5, .3] } : { L: [2.2, .5], R: [1.6, -.4] },
    face: { eyes: land ? 'happy' : 'wide', mouth: land ? 'grin' : 'o' } }));
  // sock arcs up and lands draped on his raised hand
  const sk = kf(lt, [[0, 0], [1.6, 1, easeOut]]);
  drawSock(ctx, lerp(820, 400, sk), lerp(FLOOR - 120, FLOOR - 900, Math.sin(sk * Math.PI * .85)) + (sk >= 1 ? 0 : 0), 170, sk * 8, 1);
  if (lt < .5) { burst(ctx, 820, FLOOR - 80, 220 * (1 - lt * 1.6), 12, '#fff', 8); }
  flash(ctx, kf(lt, [[0, .9], [.18, 0]]));
  speedLines(ctx, kf(lt, [[0, 1], [1.1, 0]]), t, 1);
} });

// 7 · WIN (22.6–25.6): sock on, alarm says he made it
SHOTS.push({ start: 22.6, end: 25.6, tr: 'cut', draw(ctx, lt, t) {
  const h = hh(t, 3); const cam = { x: 540 + h[0], y: 1230 + h[1], z: 1.15 - lt * .03 };
  roomBG(ctx, t, cam, { winX: 640, frameX: 120 });
  applyCam(ctx, cam, 1);
  drawCouch(ctx, 80, FLOOR, 1);
  drawAlarm(ctx, -260, FLOOR - 400, .8, '08:00', lt > .3 && lt < 1.6 ? 1 : 0, t);
  drawStick(ctx, C(HERO, { x: 620, y: FLOOR, s: 760, legs: { L: [.15, -.05], R: [.15, -.05] }, arms: { L: [.9, -2.2], R: [.9, -2.2] },
    face: { eyes: 'normal', look: [-.4, 0], mouth: 'grin', browOne: 1 }, headTilt: -.06 }));
  for (const [fx, fl] of [[620 - 760 * .08, -1], [620 + 760 * .08, 1]]) drawSock(ctx, fx, FLOOR - 30, 95, 0, fl);
  sparkle(ctx, 760, FLOOR - 650, 70 * kf(lt, [[.3, 0], [.6, 1], [1.2, 0]]), 1);
  scoreboard(ctx, kf(lt, [[.6, 0], [.9, 1]]), 1, 0);
} });

// 8 · TWIST (25.6–31.5): the vacuum docks... on a mountain of socks
SHOTS.push({ start: 25.6, end: 31.5, tr: 'cut', draw(ctx, lt, t) {
  const h = hh(t, 3); const cam = { x: 700 + h[0], y: kf(lt, [[2.0, 1300], [3.4, 1120]]) + h[1], z: kf(lt, [[0, 1.2], [2.0, 1.2], [3.4, .95]]) };
  roomBG(ctx, t, cam, { winX: 60, frameX: 500 });
  applyCam(ctx, cam, 1);
  const open = kf(lt, [[1.8, 0], [2.4, 1, backOut]]);
  drawDock(ctx, 980, FLOOR, 1.1, open, kf(lt, [[2.0, 0], [3.0, 1]]));
  const vx = kf(lt, [[0, 200], [1.6, 640, easeOut]]);
  drawVac(ctx, vx, FLOOR, 200, { dir: 1, glow: 1, mood: lt > 2.6 ? 'smug' : '', spin: lt < 1.6 ? t * 25 : 0, t, hop: lt > 4.2 && lt < 4.5 ? -14 : 0 });
  if (lt > 4.1 && lt < 4.4) bubble(ctx, vx, FLOOR - 260, 'БИП', 58, 1, -1);
  const flip = lt > 3.8;
  scoreboard(ctx, 1, 1, flip ? 47 : 0, flip ? kf(lt, [[3.8, 1], [4.3, 0]]) : 0);
} });
