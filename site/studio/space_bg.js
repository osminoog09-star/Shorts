/* Живой космос за стеклом студии M1lash (Claude, 06.11.2026).
   Canvas 2D, без библиотек: звёзды с параллаксом и мерцанием, туманности в цветах бренда,
   планеты (одна с кольцом), чёрная дыра с аккреционным диском, кометы и падающие звёзды.
   Пауза в скрытой вкладке; prefers-reduced-motion → почти статично. */
(() => {
  const cv = document.createElement('canvas');
  cv.id = 'space';
  cv.setAttribute('aria-hidden', 'true');
  document.body.prepend(cv);
  const g = cv.getContext('2d');
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W = 0, H = 0, DPR = 1, t0 = performance.now(), last = t0, raf = 0;
  let mx = 0, my = 0, tmx = 0, tmy = 0;
  const rnd = (a, b) => a + Math.random() * (b - a);

  let stars = [], dust = [], planets = [], comets = [], shoots = [], hole;
  function build() {
    DPR = Math.min(devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    cv.width = W * DPR; cv.height = H * DPR;
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    g.setTransform(DPR, 0, 0, DPR, 0, 0);
    const n = Math.round(W * H / 2600);
    stars = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H, z: rnd(.15, 1), r: rnd(.3, 1.4),
      tw: rnd(.6, 2.2), ph: rnd(0, 6.28), hue: [210, 230, 280, 320, 40][Math.floor(Math.random() * 5)]
    }));
    dust = Array.from({ length: Math.round(n / 6) }, () => ({ x: Math.random() * W, y: Math.random() * H, r: rnd(20, 70), a: rnd(.015, .045), h: rnd(220, 330) }));
    const s = Math.min(W, H);
    planets = [
      { x: .82, y: .18, r: s * .085, c1: '#ffb36b', c2: '#c2410c', ring: true, tilt: -.35, sp: .004, band: '#fde3c4' },
      { x: .1, y: .78, r: s * .05, c1: '#8bd0ff', c2: '#1e3a8a', ring: false, sp: .006, band: '#c7e7ff' },
      { x: .55, y: .9, r: s * .022, c1: '#e9d5ff', c2: '#6d28d9', ring: false, sp: .01, band: '#f5ecff' }
    ];
    hole = { x: .2, y: .26, r: s * .045, parts: Array.from({ length: 420 }, () => ({ a: rnd(0, 6.28), d: rnd(1.25, 3.4), s: rnd(.4, 1.6), w: rnd(.5, 1.8) })) };
  }

  function spawnComet(now) {
    const fromLeft = Math.random() < .5, y = rnd(.05, .55) * H;
    comets.push({ x: fromLeft ? -80 : W + 80, y, vx: (fromLeft ? 1 : -1) * rnd(90, 160), vy: rnd(18, 55), born: now, life: rnd(9, 14), r: rnd(1.6, 2.6), hue: rnd(180, 210) });
  }
  function spawnShoot() {
    shoots.push({ x: rnd(.2, 1) * W, y: rnd(0, .4) * H, vx: -rnd(500, 800), vy: rnd(200, 360), life: rnd(.6, 1), age: 0 });
  }
  let nextComet = 2, nextShoot = 1.5;

  function drawPlanet(p, t) {
    const x = p.x * W + mx * 14, y = p.y * H + my * 10 + Math.sin(t * p.sp * 6) * 6, r = p.r;
    if (p.ring) ring(x, y, r, p, true);
    const gr = g.createRadialGradient(x - r * .4, y - r * .45, r * .1, x, y, r);
    gr.addColorStop(0, p.c1); gr.addColorStop(1, p.c2);
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 6.283); g.fill();
    g.save(); g.beginPath(); g.arc(x, y, r, 0, 6.283); g.clip();
    g.globalAlpha = .22; g.strokeStyle = p.band; g.lineWidth = r * .09;
    for (let i = -3; i <= 3; i++) { g.beginPath(); const yy = y + i * r * .28 + Math.sin(t * .2 + i) * r * .03; g.ellipse(x + ((t * p.sp * 400) % (r * 2)) - r, yy, r * 2, r * .08, 0, 0, 6.283); g.stroke(); }
    g.globalAlpha = 1;
    const sh = g.createRadialGradient(x + r * .6, y + r * .5, r * .2, x + r * .3, y + r * .3, r * 1.3);
    sh.addColorStop(0, 'rgba(5,4,20,.75)'); sh.addColorStop(1, 'rgba(5,4,20,0)');
    g.fillStyle = sh; g.fillRect(x - r, y - r, r * 2, r * 2); g.restore();
    const at = g.createRadialGradient(x, y, r * .95, x, y, r * 1.35);
    at.addColorStop(0, hexA(p.c1, .35)); at.addColorStop(1, hexA(p.c1, 0));
    g.fillStyle = at; g.beginPath(); g.arc(x, y, r * 1.35, 0, 6.283); g.fill();
    if (p.ring) ring(x, y, r, p, false);
  }
  function ring(x, y, r, p, back) {
    g.save(); g.translate(x, y); g.rotate(p.tilt);
    g.beginPath(); g.ellipse(0, 0, r * 1.9, r * .5, 0, back ? Math.PI : 0, back ? 2 * Math.PI : Math.PI);
    g.strokeStyle = 'rgba(253,227,196,.55)'; g.lineWidth = r * .16; g.stroke();
    g.strokeStyle = 'rgba(255,255,255,.25)'; g.lineWidth = r * .04; g.stroke();
    g.restore();
  }
  function hexA(h, a) { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; }

  function drawHole(t) {
    const x = hole.x * W + mx * 22, y = hole.y * H + my * 16, r = hole.r;
    const glow = g.createRadialGradient(x, y, r * .8, x, y, r * 5);
    glow.addColorStop(0, 'rgba(255,140,60,.28)'); glow.addColorStop(.4, 'rgba(139,92,246,.12)'); glow.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = glow; g.beginPath(); g.arc(x, y, r * 5, 0, 6.283); g.fill();
    g.save(); g.translate(x, y); g.rotate(-.3);
    for (const q of hole.parts) {
      const a = q.a + t * q.s / (q.d * q.d) * 1.6, d = q.d * r;
      const px = Math.cos(a) * d, py = Math.sin(a) * d * .28;
      const front = Math.sin(a) > 0;
      const heat = 1 - (q.d - 1.25) / 2.2;
      g.fillStyle = `hsla(${20 + (1 - heat) * 260},95%,${55 + heat * 25}%,${(front ? .9 : .5) * (.35 + heat * .6)})`;
      g.fillRect(px, py, q.w, q.w);
    }
    g.restore();
    g.beginPath(); g.arc(x, y, r * 1.12, 0, 6.283); g.strokeStyle = 'rgba(255,200,150,.55)'; g.lineWidth = 1.6; g.stroke();
    g.fillStyle = '#000'; g.beginPath(); g.arc(x, y, r, 0, 6.283); g.fill();
    g.save(); g.translate(x, y); g.rotate(-.3);
    g.beginPath(); g.ellipse(0, 0, r * 2.1, r * .55, 0, 0, Math.PI);
    g.strokeStyle = 'rgba(255,170,90,.35)'; g.lineWidth = r * .18; g.stroke(); g.restore();
  }

  function frame(now) {
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    const t = (now - t0) / 1000 * (RM ? .05 : 1);
    mx += (tmx - mx) * .04; my += (tmy - my) * .04;
    const bg = g.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#05040d'); bg.addColorStop(.55, '#0b0820'); bg.addColorStop(1, '#130722');
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    const neb = [[.75, .35, '#3b7bff', .16], [.25, .65, '#8b5cf6', .18], [.6, .75, '#f0479a', .12]];
    for (const [nx, ny, c, a] of neb) {
      const x = nx * W + Math.sin(t * .03 + nx * 9) * 40 + mx * 8, y = ny * H + Math.cos(t * .025 + ny * 7) * 30 + my * 6, R = Math.max(W, H) * .45;
      const ng = g.createRadialGradient(x, y, 0, x, y, R); ng.addColorStop(0, hexA(c, a)); ng.addColorStop(1, hexA(c, 0));
      g.fillStyle = ng; g.fillRect(0, 0, W, H);
    }
    for (const d of dust) { g.fillStyle = `hsla(${d.h},80%,70%,${d.a})`; g.beginPath(); g.arc(d.x + mx * 4, d.y + my * 3, d.r, 0, 6.283); g.fill(); }
    for (const s of stars) {
      const tw = .55 + .45 * Math.sin(t * s.tw + s.ph);
      const x = (s.x + mx * 30 * s.z - t * 2 * s.z + W * 10) % W, y = s.y + my * 20 * s.z;
      g.fillStyle = `hsla(${s.hue},90%,${85 + s.z * 10}%,${(.35 + .65 * s.z) * tw})`;
      g.beginPath(); g.arc(x, y, s.r * (.6 + s.z * .7), 0, 6.283); g.fill();
      if (s.r > 1.25 && tw > .9) { g.fillRect(x - 3, y - .3, 6, .6); g.fillRect(x - .3, y - 3, .6, 6); }
    }
    drawHole(t);
    for (const p of planets) drawPlanet(p, t);
    if (!RM) {
      nextComet -= dt; nextShoot -= dt;
      if (nextComet <= 0) { spawnComet(t); nextComet = rnd(7, 13); }
      if (nextShoot <= 0) { spawnShoot(); nextShoot = rnd(2.5, 6); }
    }
    comets = comets.filter(c => t - c.born < c.life);
    for (const c of comets) {
      c.x += c.vx * dt; c.y += c.vy * dt;
      const len = 170, ang = Math.atan2(c.vy, c.vx), tx = c.x - Math.cos(ang) * len, ty = c.y - Math.sin(ang) * len;
      const tg = g.createLinearGradient(c.x, c.y, tx, ty);
      tg.addColorStop(0, `hsla(${c.hue},100%,90%,.9)`); tg.addColorStop(.3, `hsla(${c.hue},100%,70%,.35)`); tg.addColorStop(1, `hsla(${c.hue},100%,60%,0)`);
      g.strokeStyle = tg; g.lineWidth = c.r * 2.4; g.lineCap = 'round'; g.beginPath(); g.moveTo(c.x, c.y); g.lineTo(tx, ty); g.stroke();
      const hg = g.createRadialGradient(c.x, c.y, 0, c.x, c.y, c.r * 7); hg.addColorStop(0, 'rgba(255,255,255,.95)'); hg.addColorStop(1, `hsla(${c.hue},100%,70%,0)`);
      g.fillStyle = hg; g.beginPath(); g.arc(c.x, c.y, c.r * 7, 0, 6.283); g.fill();
    }
    shoots = shoots.filter(s => (s.age += dt) < s.life);
    for (const s of shoots) {
      s.x += s.vx * dt; s.y += s.vy * dt; const a = 1 - s.age / s.life;
      const sg = g.createLinearGradient(s.x, s.y, s.x - s.vx * .12, s.y - s.vy * .12);
      sg.addColorStop(0, `rgba(255,255,255,${a})`); sg.addColorStop(1, 'rgba(255,255,255,0)');
      g.strokeStyle = sg; g.lineWidth = 1.4; g.beginPath(); g.moveTo(s.x, s.y); g.lineTo(s.x - s.vx * .12, s.y - s.vy * .12); g.stroke();
    }
    raf = requestAnimationFrame(frame);
  }
  addEventListener('resize', () => { cancelAnimationFrame(raf); build(); raf = requestAnimationFrame(frame); });
  addEventListener('pointermove', e => { tmx = e.clientX / innerWidth - .5; tmy = e.clientY / innerHeight - .5; }, { passive: true });
  addEventListener('deviceorientation', e => { if (e.gamma != null) { tmx = Math.max(-.5, Math.min(.5, e.gamma / 60)); tmy = Math.max(-.5, Math.min(.5, (e.beta - 45) / 90)); } }, { passive: true });
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancelAnimationFrame(raf); else { last = performance.now(); raf = requestAnimationFrame(frame); } });
  build(); raf = requestAnimationFrame(frame);
})();
