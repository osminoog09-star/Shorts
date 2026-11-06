/* M1lash Studio — объёмный интерфейс (Claude, 06.11.2026).
   Всё в 3D: стеклянные панели живут в перспективе, наклоняются за курсором/гироскопом,
   содержимое приподнято над стеклом (translateZ), блик-«линза» следует за светом,
   карточки въезжают из глубины, орбы агентов — шары с орбитой и спутником.
   Только transform/opacity, один rAF, пружина без overshoot, учитывает reduced-motion. */
(() => {
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const HOVER = matchMedia('(hover:hover) and (pointer:fine)').matches;
  const SEL = '.card,.idea,.ag,.vrow,.cm';
  const root = document.documentElement;

  // общий «взгляд» сцены: курсор на ПК, гироскоп на телефоне
  let gx = 0, gy = 0, cx = 0, cy = 0;
  addEventListener('pointermove', e => { gx = e.clientX / innerWidth - .5; gy = e.clientY / innerHeight - .5; }, { passive: true });
  addEventListener('deviceorientation', e => {
    if (e.gamma == null) return;
    gx = Math.max(-.5, Math.min(.5, e.gamma / 60)); gy = Math.max(-.5, Math.min(.5, (e.beta - 45) / 90));
  }, { passive: true });

  // наклон отдельной панели под курсором (ПК)
  const tilt = new Map();
  let hot = null;
  if (HOVER && !RM) {
    document.addEventListener('pointermove', e => {
      const el = e.target.closest?.(SEL);
      if (hot && hot !== el) { const t = tilt.get(hot); if (t) { t.tx = 0; t.ty = 0; t.tl = 0; } }
      hot = el; if (!el) return;
      const r = el.getBoundingClientRect();
      const nx = (e.clientX - r.left) / r.width, ny = (e.clientY - r.top) / r.height;
      let t = tilt.get(el); if (!t) { t = { x: 0, y: 0, l: 0, tx: 0, ty: 0, tl: 0 }; tilt.set(el, t); }
      const k = Math.max(.35, Math.min(1, 380 / r.width)); // большие панели наклоняются меньше
      t.tx = (nx - .5) * 9 * k; t.ty = (.5 - ny) * 7 * k; t.tl = 1;
      el.style.setProperty('--mx', (nx * 100).toFixed(1) + '%'); el.style.setProperty('--my', (ny * 100).toFixed(1) + '%');
    }, { passive: true });
    document.addEventListener('pointerleave', () => { if (hot) { const t = tilt.get(hot); if (t) { t.tx = t.ty = t.tl = 0; } hot = null; } });
  }

  // вход из глубины: панель поднимается из-под стекла при появлении в кадре
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => {
    for (const en of es) if (en.isIntersecting) { en.target.classList.add('d3-in'); io.unobserve(en.target); }
  }, { rootMargin: '0px 0px -6% 0px' }) : null;
  function scan() {
    document.querySelectorAll(SEL).forEach(el => {
      if (el.dataset.d3) return; el.dataset.d3 = '1'; el.classList.add('d3');
      if (io && !RM) io.observe(el); else el.classList.add('d3-in');
    });
    // орбы агентов: шар + наклонная орбита со спутником (настоящий CSS 3D)
    document.querySelectorAll('.ag .orb:not([data-d3])').forEach(o => {
      o.dataset.d3 = '1'; o.innerHTML = '<i class="ring"><b></b></i>';
    });
  }
  new MutationObserver(scan).observe(document.getElementById('view') || document.body, { childList: true, subtree: true });
  scan();

  // один кадр на всё: пружина (critically damped) к цели
  const k = RM ? 1 : .14;
  function frame() {
    cx += (gx - cx) * k; cy += (gy - cy) * k;
    // пишем только изменившиеся значения: покой = ноль перерисовок стекла
    const sx = cx.toFixed(3), sy = cy.toFixed(3);
    if (sx !== lx) { root.style.setProperty('--gx', sx); lx = sx; }
    if (sy !== ly) { root.style.setProperty('--gy', sy); ly = sy; }
    for (const [el, t] of tilt) {
      if (!el.isConnected) { tilt.delete(el); continue; }
      t.x += (t.tx - t.x) * .16; t.y += (t.ty - t.y) * .16; t.l += (t.tl - t.l) * .12;
      const v = t.y.toFixed(2) + '|' + t.x.toFixed(2) + '|' + t.l.toFixed(2);
      if (v === t.v) continue; t.v = v;
      el.style.setProperty('--rx', t.y.toFixed(2) + 'deg'); el.style.setProperty('--ry', t.x.toFixed(2) + 'deg'); el.style.setProperty('--lit', t.l.toFixed(2));
      if (!t.tl && Math.abs(t.x) + Math.abs(t.y) + t.l < .005) { el.style.removeProperty('--rx'); el.style.removeProperty('--ry'); el.style.removeProperty('--lit'); tilt.delete(el); }
    }
    if (!document.hidden) requestAnimationFrame(frame); else paused = true;
  }
  let lx = '', ly = '', paused = false;
  if (!RM) requestAnimationFrame(frame);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && paused && !RM) { paused = false; requestAnimationFrame(frame); } });
})();
