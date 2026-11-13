// ---------- M1lash demo: room, robot vacuum, sock, dock, HUD ----------
const FLOOR = 1650;          // feet / floor contact line (world y)
const WALL_END = 1330;       // where the wall meets the floor

function roomBG(ctx, t, cam, o = {}) {
  applyCam(ctx, cam, .25);
  ctx.fillStyle = o.wall || '#f1d9b2'; ctx.fillRect(-3000, -2000, 9000, 3600);
  for (let x = -3000; x < 6000; x += 120) { ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(x, -2000, 46, 3600); }
  if (o.window !== false) {
    const wx = o.winX ?? 600, wy = 330;
    rrect(ctx, wx, wy, 380, 560, 16);
    const g = ctx.createLinearGradient(0, wy, 0, wy + 560); g.addColorStop(0, '#5cb8f0'); g.addColorStop(1, '#cfeefc');
    ctx.save(); ctx.fillStyle = g; ctx.fill(); ctx.clip(); drawCloud(ctx, wx + 120 + (t * 8) % 300, wy + 160, 70, 2); drawSun(ctx, wx + 300, wy + 110, 40, t, .6); ctx.restore();
    rrect(ctx, wx, wy, 380, 560, 16); fillStroke(ctx, null, 14, '#fbf7ef'); rrect(ctx, wx, wy, 380, 560, 16); fillStroke(ctx, null, 5);
    line(ctx, wx + 190, wy, wx + 190, wy + 560, 12, '#fbf7ef'); line(ctx, wx, wy + 280, wx + 380, wy + 280, 12, '#fbf7ef');
  }
  if (o.frame !== false) { // framed doodle on the wall
    const fx = o.frameX ?? 180, fy = 520;
    rrect(ctx, fx, fy, 200, 160, 8); fillStroke(ctx, '#fff8e6', 10, '#7a4a2a');
    ctx.save(); ctx.translate(fx + 100, fy + 80); line(ctx, -50, 40, 0, -30, 7); line(ctx, 0, -30, 50, 40, 7); circle(ctx, 30, -40, 14); fillStroke(ctx, '#f2b52a', 5); ctx.restore();
  }
  applyCam(ctx, cam, 1);
  // skirting board + parquet floor
  ctx.fillStyle = '#c4874a'; ctx.fillRect(-3000, WALL_END, 9000, 2000);
  const R = rng(9);
  for (let y = WALL_END + 40, row = 0; y < WALL_END + 1400; y += 64, row++) {
    ctx.fillStyle = row % 2 ? '#b97b41' : '#cc9152'; ctx.fillRect(-3000, y, 9000, 64);
    line(ctx, -3000, y, 6000, y, 3, 'rgba(60,30,20,.35)');
    for (let x = -3000 + (row % 3) * 130; x < 6000; x += 390) line(ctx, x, y, x, y + 64, 3, 'rgba(60,30,20,.3)');
  }
  ctx.fillStyle = '#fbf7ef'; ctx.fillRect(-3000, WALL_END - 10, 9000, 52); line(ctx, -3000, WALL_END + 42, 6000, WALL_END + 42, 5);
  line(ctx, -3000, WALL_END - 10, 6000, WALL_END - 10, 4, 'rgba(34,28,34,.5)');
}

function drawCouch(ctx, x, y, s = 1, under = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  // shadow + dark gap under the couch
  ellipse(ctx, 0, 0, 470, 34); ctx.fillStyle = 'rgba(40,20,30,.28)'; ctx.fill();
  ctx.fillStyle = '#1a1418'; ctx.fillRect(-400, -90, 800, 90);
  if (under > 0) { // red glow from the dark
    const g = ctx.createRadialGradient(0, -40, 5, 0, -40, 260); g.addColorStop(0, `rgba(255,40,40,${.55 * under})`); g.addColorStop(1, 'rgba(255,40,40,0)');
    ctx.fillStyle = g; ctx.fillRect(-400, -90, 800, 90);
  }
  for (const lx of [-380, 360]) { rrect(ctx, lx, -95, 22, 95, 6); fillStroke(ctx, '#5b3a22', 5); }
  rrect(ctx, -440, -470, 880, 170, 40); fillStroke(ctx, '#2f8f8a', 7);            // back
  rrect(ctx, -440, -320, 880, 230, 30); fillStroke(ctx, '#2a807b', 7);            // base
  for (const cx of [-390, 10]) { rrect(ctx, cx, -350, 380, 90, 30); fillStroke(ctx, '#3aa9a2', 6); }   // cushions
  for (const ax of [-500, 420]) { rrect(ctx, ax, -400, 90, 320, 40); fillStroke(ctx, '#2f8f8a', 7); }  // arms
  ctx.restore();
}

// robot vacuum, side view. y = floor contact, r = radius (px). o: dir, glow, mood, spin, suck, t
function drawVac(ctx, x, y, r, o = {}) {
  const d = o.dir || 1, t = o.t || 0;
  ctx.save(); ctx.translate(x, y + (o.hop || 0));
  ellipse(ctx, 0, 0, r * 1.05, r * .08); ctx.fillStyle = 'rgba(40,20,30,.3)'; ctx.fill();
  // wheels
  for (const wx of [-.6, .6]) { circle(ctx, wx * r, -.09 * r, .1 * r); fillStroke(ctx, '#15161a', r * .02); const a = (o.spin || 0) * d; line(ctx, wx * r, -.09 * r, wx * r + Math.cos(a) * .08 * r, -.09 * r + Math.sin(a) * .08 * r, r * .02, '#888'); }
  // body
  rrect(ctx, -r, -.46 * r, 2 * r, .38 * r, .16 * r); fillStroke(ctx, '#2e333b', r * .025);
  ctx.save(); rrect(ctx, -r, -.46 * r, 2 * r, .38 * r, .16 * r); ctx.clip(); ctx.fillStyle = '#1b1e24'; ctx.fillRect(-r, -.2 * r, 2 * r, .06 * r); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fillRect(-r, -.46 * r, 2 * r, .08 * r); ctx.restore();
  // dome
  ellipse(ctx, 0, -.46 * r, .78 * r, .14 * r); fillStroke(ctx, '#444b56', r * .022);
  circle(ctx, -d * .35 * r, -.5 * r, .035 * r); ctx.fillStyle = (o.glow || 0) > .5 ? '#ff4040' : '#5fe08a'; ctx.fill();
  // side brush
  ctx.save(); ctx.translate(d * .95 * r, -.04 * r); for (let k = 0; k < 3; k++) { const a = (o.spin || 0) * 3 + k * TAU / 3; line(ctx, 0, 0, Math.cos(a) * .16 * r, Math.sin(a) * .05 * r, r * .012, '#6b6f78'); } ctx.restore();
  // eye visor + red eye
  const ex = d * .55 * r, ey = -.28 * r;
  ellipse(ctx, ex, ey, .3 * r, .11 * r); fillStroke(ctx, '#0c0d10', r * .02);
  const gl = o.glow || 0;
  if (gl > 0) {
    ctx.save(); ctx.shadowColor = '#ff2a2a'; ctx.shadowBlur = 40 * gl; const lk = (o.look || 0) * .12 * r;
    circle(ctx, ex + lk, ey, .07 * r * (.6 + .4 * gl)); ctx.fillStyle = `rgba(255,${60 - 40 * gl},${50 - 40 * gl},${gl})`; ctx.fill(); ctx.restore();
    circle(ctx, ex + lk - .02 * r, ey - .025 * r, .018 * r); ctx.fillStyle = `rgba(255,255,255,${gl})`; ctx.fill();
  }
  if (o.mood === 'angry') { line(ctx, ex - .3 * r, ey - .2 * r, ex + .28 * r, ey - .1 * r, r * .045); }
  if (o.mood === 'smug') { ctx.save(); ellipse(ctx, ex, ey, .3 * r, .11 * r); ctx.clip(); ctx.fillStyle = '#2e333b'; ctx.fillRect(ex - .32 * r, ey - .12 * r, .64 * r, .1 * r); ctx.restore(); line(ctx, ex - .3 * r, ey - .02 * r, ex + .3 * r, ey - .02 * r, r * .03); }
  // suction lines in front of the intake
  if (o.suck > 0) {
    ctx.save(); ctx.globalAlpha = clamp(o.suck);
    for (let k = 0; k < 4; k++) {
      const ph = ((t * 2.2 + k / 4) % 1); const dist = (1 - ph) * 1.6 * r + .95 * r;
      ctx.beginPath(); ctx.arc(d * (dist - .9 * r) + d * .95 * r * 0, -.12 * r, .35 * r * (1 - ph * .5), d > 0 ? -1.0 : Math.PI - 1.0, d > 0 ? 1.0 : Math.PI + 1.0);
      ctx.translate(0, 0); ctx.lineWidth = r * .025; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.stroke();
    }
    ctx.restore();
  }
  ctx.restore();
}

// sock: centre (x,y), length s, rotation, flip, colours
function drawSock(ctx, x, y, s, rot = 0, flip = 1, col = '#ffcf33', str = '#2f63c9') {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * flip, s);
  const shape = () => { ctx.beginPath(); ctx.moveTo(-.35, -.5); ctx.lineTo(0, -.5); ctx.lineTo(0, .1); ctx.lineTo(.42, .1); ctx.quadraticCurveTo(.6, .1, .6, .28); ctx.quadraticCurveTo(.6, .46, .42, .46); ctx.lineTo(-.18, .46); ctx.quadraticCurveTo(-.35, .46, -.35, .28); ctx.closePath(); };
  shape(); ctx.fillStyle = col; ctx.fill();
  ctx.save(); shape(); ctx.clip(); ctx.fillStyle = str; for (const yy of [-.46, -.34, -.22]) ctx.fillRect(-.4, yy, .5, .06); ctx.fillStyle = 'rgba(0,0,0,.12)'; ctx.fillRect(.3, .1, .4, .4); ctx.restore();
  shape(); ctx.lineWidth = .04; ctx.strokeStyle = INK; ctx.lineJoin = 'round'; ctx.stroke();
  ctx.restore();
}

function drawDock(ctx, x, y, s, open = 0, pile = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (pile > 0) { // mountain of stolen socks
    const cols = [['#ffcf33', '#2f63c9'], ['#e0392f', '#fff'], ['#3fa35b', '#f2b52a'], ['#7a4bc4', '#fff'], ['#2f63c9', '#ffcf33'], ['#f6f1e8', '#e0392f'], ['#ff8fb1', '#7a4bc4']];
    const R = rng(21); const n = Math.round(47 * clamp(pile));
    for (let i = 0; i < n; i++) { const row = Math.floor(Math.sqrt(i * 2.2)); const px = (R() - .5) * (520 - row * 50), py = -150 - row * 70 - R() * 30; const c = cols[i % cols.length]; drawSock(ctx, px, py, 120 + R() * 30, (R() - .5) * 2.4, R() > .5 ? 1 : -1, c[0], c[1]); }
  }
  rrect(ctx, -300, -150, 600, 150, 24); fillStroke(ctx, '#e9edf2', 7);
  ctx.save(); ctx.translate(-300, -150); ctx.rotate(-open * 1.9); rrect(ctx, 0, -40, 600, 44, 18); fillStroke(ctx, '#cfd6de', 7); ctx.restore();
  circle(ctx, 0, -80, 22); fillStroke(ctx, '#5fe08a', 5);
  text(ctx, 'ДОК', 0, -30, 34, '#5a6270', INK, 0, 'Unb', 800);
  ctx.restore();
}

function drawAlarm(ctx, x, y, s, str, ring = 0, t = 0) {
  ctx.save(); ctx.translate(x + (ring ? Math.sin(t * 60) * 6 * ring : 0), y); ctx.rotate(ring ? Math.sin(t * 47) * .08 * ring : 0); ctx.scale(s, s);
  for (const bx of [-60, 60]) { circle(ctx, bx, -125, 32); fillStroke(ctx, '#e0392f', 6); }
  rrect(ctx, -110, -120, 220, 120, 26); fillStroke(ctx, '#2a2f38', 7);
  rrect(ctx, -88, -100, 176, 78, 12); fillStroke(ctx, '#0f1a12', 4);
  text(ctx, str, 0, -60, 52, '#ff4a3d', INK, 0, 'Unb', 800);
  ctx.restore();
}

function bubble(ctx, x, y, str, size = 64, a = 1, tail = -1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.font = `800 ${size}px Unb`;
  const w = ctx.measureText(str).width + size * 1.1, h = size * 1.7;
  const sc = .7 + .3 * backOut(clamp(a)); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.moveTo(tail * w * .15, h / 2 - 4); ctx.lineTo(tail * w * .32, h / 2 + 50); ctx.lineTo(tail * w * .02, h / 2 - 4);
  fillStroke(ctx, '#fff', 8);
  text(ctx, str, 0, 4, size, INK, INK, 0, 'Unb', 800);
  ctx.restore();
}

// screen-space scoreboard
function scoreboard(ctx, a, l, r, pulseR = 0) {
  if (a <= 0) return;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = clamp(a);
  const y = 300 - (1 - backOut(clamp(a))) * 120;
  rrect(ctx, 150, y - 95, 780, 190, 40); fillStroke(ctx, 'rgba(20,16,26,.88)', 8, '#fff');
  text(ctx, 'ГЕРОЙ', 300, y - 40, 34, '#9fd4ff', INK, 0, 'Unb', 800);
  text(ctx, 'ПЫЛЕСОС', 780, y - 40, 34, '#ff8a80', INK, 0, 'Unb', 800);
  text(ctx, String(l), 300, y + 30, 84, '#fff', INK, 0, 'Unb', 800);
  text(ctx, ':', 540, y + 20, 84, '#fff', INK, 0, 'Unb', 800);
  ctx.save(); ctx.translate(780, y + 30); const k = 1 + .35 * pulseR; ctx.scale(k, k); text(ctx, String(r), 0, 0, 84, pulseR > 0 ? '#ff5a4d' : '#fff', INK, 0, 'Unb', 800); ctx.restore();
  ctx.restore();
}
function flash(ctx, a, col = '#fff') { if (a <= 0) return; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = clamp(a); ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore(); }
function speedLines(ctx, a, t, dir = 1) {
  if (a <= 0) return; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = clamp(a) * .5; const R = rng(7);
  for (let i = 0; i < 26; i++) { const y = R() * H, len = 200 + R() * 400, x = ((R() * W * 2 - t * 3000 * dir) % (W * 2) + W * 2) % (W * 2) - W * .5; line(ctx, x, y, x + len * dir, y, 4 + R() * 5, '#fff'); }
  ctx.restore();
}
