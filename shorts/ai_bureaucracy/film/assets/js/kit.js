/* «Я нанял ИИ» — игрушечный 3D-мир: герой, боты, реквизит, текстовые таблички.
 * Всё детерминировано: никакого Math.random/Date. Требует window.THREE. */
(function () {
  const K = (window.KIT = {});
  const T = THREE;

  // ---------- math ----------
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const prog = (t, t0, d) => clamp((t - t0) / d);
  const sm = (x) => x * x * (3 - 2 * x);
  const eio = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const eout = (x) => 1 - Math.pow(1 - x, 3);
  const expo = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));
  const back = (x, s = 1.7) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
  // пружина: 0 → 1 с перелётом, x — секунды после старта
  const spring = (x, k = 9, w = 13) => (x <= 0 ? 0 : 1 - Math.exp(-x * k) * Math.cos(x * w));
  // детерминированный шум
  const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  Object.assign(K, { clamp, lerp, prog, sm, eio, eout, expo, back, spring, hash });

  // ---------- materials ----------
  const M = (color, o = {}) => new T.MeshPhysicalMaterial({ color, roughness: o.r ?? 0.45, metalness: o.m ?? 0, clearcoat: o.cc ?? 0.3, clearcoatRoughness: 0.25, ...(o.extra || {}) });
  const Mm = (color, r = 0.7) => new T.MeshStandardMaterial({ color, roughness: r });
  const glow = (color, i = 1.6) => new T.MeshStandardMaterial({ color: '#000', emissive: color, emissiveIntensity: i, roughness: 0.4 });
  K.M = M; K.Mm = Mm; K.glow = glow;
  const mesh = (geo, mat, cast = true) => { const m = new T.Mesh(geo, mat); m.castShadow = cast; m.receiveShadow = true; return m; };
  K.mesh = mesh;
  const rbox = (w, h, d, r, mat, seg = 4) => mesh(new T.RoundedBoxGeometry(w, h, d, seg, Math.min(r, Math.min(w, h, d) / 2 - 1e-3)), mat);
  K.rbox = rbox;
  const caps = (r, len, mat, seg = 12) => mesh(new T.CapsuleGeometry(r, len, 6, seg), mat);
  K.caps = caps;
  const sph = (r, mat, seg = 32) => mesh(new T.SphereGeometry(r, seg, Math.round(seg * 0.75)), mat);
  K.sph = sph;
  const cyl = (r1, r2, h, mat, seg = 32) => mesh(new T.CylinderGeometry(r1, r2, h, seg), mat);
  K.cyl = cyl;

  // ---------- canvas textures ----------
  const FONT = '"Rubik", "Inter", sans-serif';
  K.FONT = FONT;
  // рисует холст и возвращает текстуру; draw(g, W, H)
  K.canvasTex = function (W, H, draw) {
    const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    const tex = new T.CanvasTexture(cv); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 8;
    const api = { cv, tex, redraw(fn) { const g = cv.getContext('2d'); g.clearRect(0, 0, W, H); (fn || draw)(g, W, H); tex.needsUpdate = true; } };
    if (window.OM3) OM3.ready(document.fonts.ready.then(() => api.redraw()));
    api.redraw();
    return api;
  };
  K.rrect = (g, x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };
  K.fit = (g, text, maxW, size, weight = 800) => { let s = size; g.font = `${weight} ${s}px ${FONT}`; while (g.measureText(text).width > maxW && s > 10) { s -= 2; g.font = `${weight} ${s}px ${FONT}`; } return s; };
  // плоская табличка с текстом (unlit — цвета как нарисованы)
  K.plane = function (w, h, tex, opts = {}) {
    const mat = new T.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false, side: opts.side ?? T.FrontSide, depthWrite: opts.depthWrite ?? true });
    const m = new T.Mesh(new T.PlaneGeometry(w, h), mat);
    return m;
  };
  // освещаемая табличка (бумага, доска)
  K.litPlane = function (w, h, tex, rough = 0.85) {
    const m = mesh(new T.PlaneGeometry(w, h), new T.MeshStandardMaterial({ map: tex, roughness: rough, transparent: true }), false);
    return m;
  };

  // процедурные текстуры материалов
  K.woodTex = function (base = '#b97a4a', dark = '#8a5530', planks = 6, seed = 1) {
    return K.canvasTex(1024, 1024, (g, W, H) => {
      g.fillStyle = base; g.fillRect(0, 0, W, H);
      const ph = H / planks;
      for (let p = 0; p < planks; p++) {
        const y0 = p * ph, tint = hash(p * 7 + seed) * 0.18 - 0.09;
        g.fillStyle = `rgba(${tint > 0 ? 255 : 0},${tint > 0 ? 220 : 0},${tint > 0 ? 180 : 0},${Math.abs(tint)})`; g.fillRect(0, y0, W, ph);
        for (let i = 0; i < 26; i++) {
          const yy = y0 + hash(p * 31 + i + seed) * ph, a = 0.05 + hash(i * 3 + p) * 0.1;
          g.strokeStyle = `rgba(70,35,15,${a})`; g.lineWidth = 1 + hash(i + p * 5) * 3;
          g.beginPath(); g.moveTo(0, yy);
          for (let x = 0; x <= W; x += 64) g.lineTo(x, yy + Math.sin(x * 0.01 + i + p) * 3);
          g.stroke();
        }
        g.fillStyle = dark; g.globalAlpha = 0.6; g.fillRect(0, y0, W, 4); g.globalAlpha = 1;
        const off = hash(p + seed * 9) * W; g.fillStyle = 'rgba(60,30,12,0.45)'; g.fillRect(off, y0, 4, ph);
      }
    }).tex;
  };
  K.tileTex = function (a = '#e9e4dc', b = '#ddd6cb', n = 8) {
    return K.canvasTex(1024, 1024, (g, W, H) => {
      const s = W / n;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { g.fillStyle = (i + j) % 2 ? a : b; g.fillRect(i * s, j * s, s, s); }
      g.strokeStyle = 'rgba(0,0,0,0.12)'; g.lineWidth = 4;
      for (let i = 0; i <= n; i++) { g.beginPath(); g.moveTo(i * s, 0); g.lineTo(i * s, H); g.stroke(); g.beginPath(); g.moveTo(0, i * s); g.lineTo(W, i * s); g.stroke(); }
    }).tex;
  };

  // ---------- герой (внешность ведущего M1lash) ----------
  const SKIN = '#f3c9a9', HAIR = '#1a1720', TEE = '#1d1d24', JEANS = '#36415e';
  K.hero = function () {
    const root = new T.Group();
    const skin = M(SKIN, { r: 0.55, cc: 0.15 }), hairM = M(HAIR, { r: 0.5, cc: 0.5 }), tee = M(TEE, { r: 0.85, cc: 0 }), jeans = M(JEANS, { r: 0.8, cc: 0 });
    const hips = new T.Group(); hips.position.y = 0.55; root.add(hips);
    // ноги (сидит: бёдра вперёд)
    for (const s of [-1, 1]) {
      const thigh = caps(0.085, 0.3, jeans); thigh.rotation.x = Math.PI / 2; thigh.position.set(s * 0.1, 0, 0.18); hips.add(thigh);
      const shin = caps(0.075, 0.32, jeans); shin.position.set(s * 0.1, -0.25, 0.38); hips.add(shin);
      const shoe = rbox(0.13, 0.08, 0.22, 0.04, M('#f2f2f2', { r: 0.5 })); shoe.position.set(s * 0.1, -0.5, 0.43); hips.add(shoe);
      const sole = rbox(0.135, 0.025, 0.225, 0.01, M('#3a3a44', { r: 0.7 })); sole.position.set(s * 0.1, -0.54, 0.43); hips.add(sole);
    }
    const spine = new T.Group(); hips.add(spine);
    const torso = caps(0.2, 0.28, tee); torso.position.y = 0.28; torso.scale.set(1.05, 1, 0.8); spine.add(torso);
    // логотип M1 на футболке
    const logo = K.canvasTex(256, 128, (g) => { g.fillStyle = '#ff4d6d'; g.font = `900 92px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('M1', 128, 68); });
    const lp = K.plane(0.14, 0.07, logo.tex); lp.position.set(0.07, 0.36, 0.163); lp.rotation.y = 0.25; spine.add(lp);
    const neck = cyl(0.07, 0.08, 0.1, skin); neck.position.y = 0.55; spine.add(neck);
    const head = new T.Group(); head.position.y = 0.78; spine.add(head);
    const skull = sph(0.26, skin, 48); skull.scale.set(1, 0.97, 0.95); head.add(skull);
    for (const s of [-1, 1]) { const ear = sph(0.055, skin, 16); ear.scale.set(0.5, 1, 0.8); ear.position.set(s * 0.255, 0.0, -0.01); head.add(ear); }
    const nose = sph(0.035, M('#eab496', { r: 0.5 }), 16); nose.position.set(0, -0.03, 0.25); head.add(nose);
    // глаза
    const eyes = [], lids = [], pupils = [], brows = [];
    for (const s of [-1, 1]) {
      const eg = new T.Group(); eg.position.set(s * 0.095, 0.035, 0.215); head.add(eg);
      const white = sph(0.058, M('#ffffff', { r: 0.25, cc: 0.8 }), 24); white.scale.set(0.9, 1.15, 0.5); eg.add(white);
      const pg = new T.Group(); eg.add(pg);
      const pupil = sph(0.034, M('#14121a', { r: 0.2, cc: 1 }), 20); pupil.scale.set(1, 1.15, 0.6); pupil.position.z = 0.022; pg.add(pupil);
      const hl = sph(0.011, new T.MeshBasicMaterial({ color: '#fff' }), 8); hl.position.set(0.012, 0.016, 0.045); pg.add(hl);
      const lid = sph(0.062, skin, 24); lid.scale.set(0.95, 1.2, 0.55); lid.position.z = 0.004; eg.add(lid);
      const brow = rbox(0.11, 0.026, 0.03, 0.012, hairM); brow.position.set(s * 0.1, 0.135, 0.225); head.add(brow);
      eyes.push(eg); lids.push(lid); pupils.push(pg); brows.push(brow);
    }
    // рот: тёмный овал + язычок
    const mouthG = new T.Group(); mouthG.position.set(0, -0.11, 0.232); mouthG.rotation.x = -0.25; head.add(mouthG);
    const mouth = sph(0.05, M('#5a1f2a', { r: 0.6 }), 20); mouth.scale.set(1, 0.18, 0.35); mouthG.add(mouth);
    // волосы: шапка + пряди
    const capG = new T.SphereGeometry(0.275, 40, 24, 0, Math.PI * 2, 0, 1.25);
    const cap = mesh(capG, hairM); cap.position.set(0, 0.03, -0.015); cap.rotation.x = -0.28; head.add(cap);
    const back = sph(0.262, hairM, 32); back.position.set(0, 0.0, -0.05); back.scale.set(1.02, 0.95, 0.9); head.add(back);
    const spikes = [[-0.17, 0.2, 0.15, 0.5, -0.55], [-0.06, 0.25, 0.19, 0.25, -0.7], [0.07, 0.25, 0.19, -0.15, -0.75], [0.18, 0.2, 0.14, -0.55, -0.55],
      [-0.12, 0.29, 0.02, 0.4, 0.1], [0.1, 0.3, 0.0, -0.3, 0.05], [0.0, 0.3, -0.12, 0, 0.5], [-0.2, 0.18, -0.1, 0.8, 0.2], [0.21, 0.17, -0.08, -0.8, 0.2]];
    for (const [x, y, z, rz, rx] of spikes) { const c = mesh(new T.ConeGeometry(0.075, 0.2, 14), hairM); c.position.set(x, y, z); c.rotation.set(rx, 0, rz); head.add(c); }
    // руки: плечо → локоть → кисть
    const arms = {};
    for (const s of [-1, 1]) {
      const sh = new T.Group(); sh.position.set(s * 0.25, 0.47, 0); spine.add(sh);
      const sleeve = caps(0.085, 0.12, tee); sleeve.position.y = -0.08; sh.add(sleeve);
      const upper = caps(0.06, 0.16, skin); upper.position.y = -0.17; sh.add(upper);
      const el = new T.Group(); el.position.y = -0.27; sh.add(el);
      const fore = caps(0.055, 0.17, skin); fore.position.y = -0.1; el.add(fore);
      const hand = new T.Group(); hand.position.y = -0.22; el.add(hand);
      const palm = sph(0.07, skin, 20); palm.scale.set(1, 1.05, 0.75); hand.add(palm);
      const finger = caps(0.022, 0.08, skin, 8); finger.position.set(0, -0.09, 0.02); finger.visible = false; hand.add(finger);
      const thumb = caps(0.025, 0.04, skin, 8); thumb.position.set(-s * 0.06, -0.02, 0.03); thumb.rotation.z = s * 0.8; hand.add(thumb);
      arms[s < 0 ? 'L' : 'R'] = { sh, el, hand, finger };
    }
    const rig = { root, hips, spine, head, eyes, lids, pupils, brows, mouth, arms };
    // поза: значения в радианах; a = { shX, shZ, elX } для каждой руки
    rig.pose = function (p) {
      spine.rotation.set(p.lean || 0, p.twist || 0, p.tilt || 0);
      head.rotation.set(p.nod || 0, p.turn || 0, p.headTilt || 0);
      for (const k of ['L', 'R']) {
        const a = arms[k], s = k === 'L' ? -1 : 1, q = p[k] || {};
        a.sh.rotation.set(q.x ?? 0.15, q.y ?? 0, (q.z ?? 0.12) * s);
        a.el.rotation.set(q.ex ?? -0.35, 0, 0);
        a.finger.visible = !!q.point;
      }
      const blink = p.blink ?? 0, open = 1 - clamp(blink);
      lids.forEach((l, i) => { l.position.z = -0.02 + 0.03 * (1 - open); l.scale.set(0.95, 1.2 * (0.25 + 0.75 * (1 - open)) + 0.02, 0.55); l.position.y = 0.05 * open; });
      pupils.forEach((pg) => { pg.position.set((p.lookX || 0) * 0.02, (p.lookY || 0) * 0.02, 0); });
      eyes.forEach((e) => e.scale.setScalar(1 + (p.wide || 0) * 0.25));
      const b = p.brow || 0, ang = p.browAng || 0;
      brows.forEach((br, i) => { const s = i ? 1 : -1; br.position.y = 0.135 + b * 0.04; br.rotation.z = s * ang; });
      const mo = clamp(p.mouth || 0), sm = p.smile || 0;
      mouth.scale.set(1 + sm * 0.4 - mo * 0.2, 0.16 + mo * 0.75, 0.35);
      mouth.position.y = sm * 0.01;
    };
    rig.pose({});
    return rig;
  };

  // ---------- боты ----------
  // opts: { color, w, h, tie, glasses, badge, halo, scale }
  K.bot = function (o = {}) {
    const root = new T.Group(), body = new T.Group(); root.add(body);
    const W = o.w || 0.42, H = o.h || 0.38, D = 0.34;
    const shell = M(o.color || '#9fd3ff', { r: 0.28, cc: 0.9 });
    const torso = rbox(W, H, D, 0.11, shell, 5); torso.position.y = H / 2 + 0.1; body.add(torso);
    // шов и винты
    const seam = rbox(W * 1.005, 0.012, D * 1.005, 0.006, M('#00000022'.slice(0, 7), { r: 0.6 })); seam.material.color.set('#6b7387'); seam.position.y = 0.16; body.add(seam);
    for (const s of [-1, 1]) { const sc = cyl(0.012, 0.012, 0.01, M('#c9ced8', { r: 0.25, m: 0.8 }), 12); sc.rotation.x = Math.PI / 2; sc.position.set(s * (W / 2 - 0.04), 0.13, D / 2 + 0.003); body.add(sc); }
    // экран-лицо
    const face = rbox(W * 0.78, H * 0.56, 0.03, 0.05, M('#141826', { r: 0.15, cc: 1 })); face.position.set(0, H / 2 + 0.13, D / 2 - 0.005); body.add(face);
    const faceG = new T.Group(); faceG.position.set(0, H / 2 + 0.13, D / 2 + 0.013); body.add(faceG);
    const eyeC = o.eye || '#7ff3ff';
    const eyes = [];
    for (const s of [-1, 1]) { const e = caps(0.022, 0.035, glow(eyeC, 2.2), 8); e.position.set(s * W * 0.17, 0.015, 0); e.castShadow = false; faceG.add(e); eyes.push(e); }
    const mouth = rbox(0.09, 0.014, 0.01, 0.006, glow(eyeC, 2)); mouth.position.set(0, -0.055, 0); mouth.castShadow = false; faceG.add(mouth);
    // антенна
    const ant = cyl(0.008, 0.008, 0.1, M('#c9ced8', { r: 0.3, m: 0.8 }), 8); ant.position.y = H + 0.15; body.add(ant);
    const bulb = sph(0.028, glow(o.bulb || '#ff7aa8', 2.5), 16); bulb.position.y = H + 0.21; body.add(bulb);
    // ручки
    const arms = [];
    for (const s of [-1, 1]) {
      const sh = new T.Group(); sh.position.set(s * (W / 2 + 0.01), H / 2 + 0.08, 0); body.add(sh);
      const a = caps(0.03, 0.12, M('#e9edf5', { r: 0.35, m: 0.2 })); a.position.y = -0.08; sh.add(a);
      const h = sph(0.042, M('#e9edf5', { r: 0.35, m: 0.2 }), 16); h.position.y = -0.17; sh.add(h);
      sh.rotation.z = s * 0.25; arms.push(sh);
    }
    // «ножка»-подставка (боты парят)
    const foot = cyl(0.1, 0.13, 0.08, M('#d7dce6', { r: 0.35, m: 0.3 }), 24); foot.position.y = 0.05; body.add(foot);
    const jet = cyl(0.07, 0.07, 0.01, glow(eyeC, 1.2), 20); jet.position.y = 0.006; jet.castShadow = false; body.add(jet);
    if (o.tie) {
      const knot = rbox(0.05, 0.04, 0.03, 0.01, M(o.tie, { r: 0.5 })); knot.position.set(0, 0.165, D / 2 + 0.01); body.add(knot);
      const tie = rbox(0.06, 0.12, 0.02, 0.01, M(o.tie, { r: 0.5 })); tie.position.set(0, 0.1, D / 2 + 0.008); tie.rotation.z = 0.04; body.add(tie);
    }
    if (o.glasses) {
      const gm = M('#1d1d24', { r: 0.3 });
      for (const s of [-1, 1]) { const ring = mesh(new T.TorusGeometry(0.045, 0.008, 8, 24), gm); ring.position.set(s * W * 0.17, H / 2 + 0.145, D / 2 + 0.03); body.add(ring); }
      const bridge = cyl(0.005, 0.005, W * 0.18, gm, 6); bridge.rotation.z = Math.PI / 2; bridge.position.set(0, H / 2 + 0.15, D / 2 + 0.03); body.add(bridge);
    }
    if (o.badge) {
      const bt = K.canvasTex(256, 96, (g) => { K.rrect(g, 4, 4, 248, 88, 16); g.fillStyle = '#fff'; g.fill(); g.fillStyle = '#ff4d6d'; g.fillRect(4, 4, 30, 88); g.fillStyle = '#1d1d24'; K.fit(g, o.badge, 200, 54, 900); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(o.badge, 142, 52); });
      const bp = K.plane(0.13, 0.05, bt.tex); bp.position.set(W * 0.27, 0.16, D / 2 + 0.006); body.add(bp);
    }
    if (o.halo) {
      const halo = mesh(new T.TorusGeometry(W * 0.62, 0.012, 10, 64), glow('#7ff3ff', 2.5)); halo.rotation.x = Math.PI / 2; halo.position.y = H + 0.29; halo.castShadow = false; body.add(halo);
    }
    const s = o.scale || 1; root.scale.setScalar(s);
    const rig = { root, body, eyes, mouth, arms, faceG, W, H, D, bulb };
    // настроение: { blink, squint, happy, tilt, look, talk, armL, armR }
    rig.set = function (p = {}) {
      const bl = clamp(p.blink || 0), sq = clamp(p.squint || 0);
      eyes.forEach((e, i) => {
        const sgn = i ? 1 : -1;
        e.scale.set(1, Math.max(0.08, (1 - bl) * (1 - sq * 0.6)), 1);
        e.rotation.z = (p.angry || 0) * sgn * 0.5 + (p.happy || 0) * Math.PI / 2;
        e.position.x = sgn * W * 0.17 + (p.look || 0) * 0.03;
        e.position.y = 0.015 + (p.lookY || 0) * 0.02 + (p.happy || 0) * 0.01;
      });
      const tk = clamp(p.talk || 0);
      mouth.scale.set(1 + tk * 0.3 + (p.smile || 0) * 0.4, 1 + tk * 4, 1);
      arms[0].rotation.z = -(p.armL ?? 0.25); arms[1].rotation.z = p.armR ?? 0.25;
      arms[0].rotation.x = p.armLx || 0; arms[1].rotation.x = p.armRx || 0;
    };
    rig.set({});
    return rig;
  };

  // ---------- реквизит ----------
  K.envelope = function (label) {
    const g = new T.Group();
    const tex = K.canvasTex(512, 320, (c, W, H) => {
      c.fillStyle = '#fbf6ec'; c.fillRect(0, 0, W, H);
      c.strokeStyle = '#d9cdb8'; c.lineWidth = 6; c.beginPath(); c.moveTo(0, 0); c.lineTo(W / 2, H * 0.55); c.lineTo(W, 0); c.stroke();
      c.fillStyle = '#ff4d6d'; c.beginPath(); c.arc(W / 2, H * 0.55, 26, 0, Math.PI * 2); c.fill();
      if (label) { c.fillStyle = '#1d1d24'; K.fit(c, label, W - 60, 52, 900); c.textAlign = 'center'; c.fillText(label, W / 2, H - 40); }
    });
    const front = rbox(0.32, 0.2, 0.012, 0.01, new T.MeshStandardMaterial({ color: '#fbf6ec', roughness: 0.8 }));
    g.add(front);
    const face = K.plane(0.315, 0.195, tex.tex); face.position.z = 0.0065; g.add(face);
    return g;
  };
})();
