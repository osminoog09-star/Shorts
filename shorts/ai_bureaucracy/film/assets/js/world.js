/* Локации: A — домашний офис героя, B — переговорка, C — коридор отдела кадров,
 * D — «подиум» монтажного всплеска, E — кнопка «Отправить всем». Каждая — своя группа со своим светом. */
(function () {
  const K = window.KIT, T = THREE;
  const W = (window.WORLD = {});

  function keyLight(group, at, span, color = '#fff4e6', intensity = 2.4, from = [3, 6, 4]) {
    const key = new T.DirectionalLight(color, intensity);
    key.position.set(at[0] + from[0], at[1] + from[1], at[2] + from[2]);
    key.target.position.set(...at);
    key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -span, right: span, top: span, bottom: -span, near: 0.5, far: 30 });
    key.shadow.radius = 5; key.shadow.bias = -0.0005; key.shadow.normalBias = 0.02;
    group.add(key, key.target);
    return key;
  }
  W.keyLight = keyLight;
  function rimLight(group, color, intensity, from, at = [0, 1, 0]) {
    const l = new T.DirectionalLight(color, intensity); l.position.set(...from); l.target.position.set(...at); group.add(l, l.target); return l;
  }

  // ================= A: домашний офис =================
  W.office = function () {
    const g = new T.Group();
    const floorTex = K.woodTex('#c79563', '#8f5f37', 10, 3); floorTex.wrapS = floorTex.wrapT = T.RepeatWrapping; floorTex.repeat.set(3, 3);
    const floor = K.mesh(new T.PlaneGeometry(14, 14), new T.MeshStandardMaterial({ map: floorTex, roughness: 0.55 }), false); floor.rotation.x = -Math.PI / 2; g.add(floor);
    // задняя стена с панелями
    const wallM = K.Mm('#c9d8ec', 0.9);
    const wall = K.mesh(new T.PlaneGeometry(14, 6), wallM, false); wall.position.set(0, 3, -2.2); g.add(wall);
    const wains = K.rbox(14, 0.9, 0.06, 0.02, K.Mm('#aebfd8', 0.8)); wains.position.set(0, 0.45, -2.17); g.add(wains);
    const rail = K.rbox(14, 0.05, 0.09, 0.02, K.M('#f4f1ea', { r: 0.4 })); rail.position.set(0, 0.92, -2.15); g.add(rail);
    // боковая стена с дверью (справа)
    const side = K.mesh(new T.PlaneGeometry(8, 6), K.Mm('#bccbe2', 0.9), false); side.rotation.y = -Math.PI / 2; side.position.set(2.6, 3, 1.5); g.add(side);
    const doorG = new T.Group(); doorG.position.set(2.58, 0, -0.9); g.add(doorG);
    const frame = K.rbox(0.12, 2.2, 1.1, 0.03, K.M('#f4f1ea', { r: 0.4 })); frame.position.set(0, 1.1, 0); doorG.add(frame);
    const hinge = new T.Group(); hinge.position.set(-0.03, 0, -0.48); doorG.add(hinge);
    const leaf = K.rbox(0.06, 2.05, 0.96, 0.02, K.M('#e0b080', { r: 0.5 })); leaf.position.set(0, 1.04, 0.48); hinge.add(leaf);
    const knob = K.sph(0.035, K.M('#d9b44a', { r: 0.2, m: 0.9 }), 16); knob.position.set(-0.06, 1.0, 0.85); hinge.add(knob);
    const doorDark = K.mesh(new T.PlaneGeometry(0.96, 2.05), new T.MeshBasicMaterial({ color: '#141826' }), false); doorDark.rotation.y = -Math.PI / 2; doorDark.position.set(0.04, 1.04, 0); doorG.add(doorDark);
    // окно
    const winG = new T.Group(); winG.position.set(-1.1, 1.75, -2.18); g.add(winG);
    const sky = K.canvasTex(512, 512, (c, w, h) => { const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#ffd7a8'); gr.addColorStop(1, '#ffeacc'); c.fillStyle = gr; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(120,140,190,0.35)'; for (let i = 0; i < 7; i++) c.fillRect(i * 80 - 10, 300 - (i % 3) * 60, 70, 300); });
    const night = K.canvasTex(512, 512, (c, w, h) => { const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#1b2350'); gr.addColorStop(1, '#3a3f7a'); c.fillStyle = gr; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(10,12,30,0.7)'; for (let i = 0; i < 7; i++) c.fillRect(i * 80 - 10, 300 - (i % 3) * 60, 70, 300); c.fillStyle = '#ffe7a0'; for (let i = 0; i < 18; i++) c.fillRect(20 + (i * 97) % 480, 330 + (i * 53) % 150, 10, 12); });
    const pane = K.plane(1.2, 1.0, sky.tex); pane.position.z = 0.01; winG.add(pane);
    const paneN = K.plane(1.2, 1.0, night.tex); paneN.position.z = 0.012; paneN.material.opacity = 0; winG.add(paneN);
    const wm = K.M('#f4f1ea', { r: 0.4 });
    for (const [x, y, w, h] of [[0, 0.53, 1.32, 0.07], [0, -0.53, 1.32, 0.07], [0.63, 0, 0.07, 1.1], [-0.63, 0, 0.07, 1.1], [0, 0, 0.04, 1.0], [0, 0, 1.2, 0.04]]) { const b = K.rbox(w, h, 0.06, 0.015, wm); b.position.set(x, y, 0.03); winG.add(b); }
    const sill = K.rbox(1.45, 0.05, 0.22, 0.02, wm); sill.position.set(0, -0.58, 0.1); winG.add(sill);
    // часы на стене
    const clockG = new T.Group(); clockG.position.set(0.75, 2.05, -2.15); g.add(clockG);
    const rim = K.cyl(0.24, 0.24, 0.06, K.M('#2b2b35', { r: 0.3, m: 0.4 }), 40); rim.rotation.x = Math.PI / 2; clockG.add(rim);
    const dial = K.canvasTex(256, 256, (c) => { c.fillStyle = '#fbf8f1'; c.beginPath(); c.arc(128, 128, 126, 0, 7); c.fill(); c.fillStyle = '#2b2b35'; for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; c.fillRect(128 + Math.sin(a) * 100 - 4, 128 - Math.cos(a) * 100 - 10, 8, i % 3 ? 14 : 24); } });
    const face = K.plane(0.42, 0.42, dial.tex); face.position.z = 0.032; clockG.add(face);
    const hm = K.M('#1d1d24', { r: 0.4 });
    const hourH = new T.Group(), minH = new T.Group(); hourH.position.z = 0.04; minH.position.z = 0.045; clockG.add(hourH, minH);
    const hb = K.rbox(0.025, 0.11, 0.008, 0.004, hm); hb.position.y = 0.05; hourH.add(hb);
    const mb = K.rbox(0.016, 0.17, 0.008, 0.004, K.M('#ff4d6d', { r: 0.4 })); mb.position.y = 0.08; minH.add(mb);
    // полка с мелочами
    const shelf = K.rbox(1.0, 0.04, 0.22, 0.015, K.M('#e9d2b4', { r: 0.6 })); shelf.position.set(1.15, 1.45, -2.08); g.add(shelf);
    const books = ['#ff8fa3', '#7fb3ff', '#ffd166', '#9be7c4', '#c3a6ff'];
    books.forEach((c, i) => { const b = K.rbox(0.07, 0.24 + (i % 2) * 0.05, 0.17, 0.01, K.M(c, { r: 0.6 })); b.position.set(0.8 + i * 0.085, 1.6 + (i % 2) * 0.025, -2.06); b.rotation.z = i === 4 ? -0.25 : 0; g.add(b); });
    const pot = K.cyl(0.1, 0.08, 0.16, K.M('#e8794f', { r: 0.6 }), 24); pot.position.set(1.45, 1.55, -2.06); g.add(pot);
    for (let i = 0; i < 6; i++) { const lf = K.sph(0.07, K.M('#5bbf7a', { r: 0.5 }), 12); lf.scale.set(0.6, 1.4, 0.4); lf.position.set(1.45 + Math.sin(i * 1.1) * 0.06, 1.72 + (i % 3) * 0.03, -2.06 + Math.cos(i * 1.1) * 0.05); lf.rotation.z = Math.sin(i * 1.1) * 0.6; g.add(lf); }

    // стол
    const deskG = new T.Group(); g.add(deskG);
    const wood = K.woodTex('#c8915c', '#8a5530', 4, 7);
    const top = K.rbox(1.7, 0.06, 0.85, 0.02, new T.MeshPhysicalMaterial({ map: wood, roughness: 0.42, clearcoat: 0.5 })); top.position.set(0, 0.78, 0); deskG.add(top);
    for (const [x, z] of [[-0.78, -0.35], [0.78, -0.35], [-0.78, 0.35], [0.78, 0.35]]) { const l = K.rbox(0.06, 0.75, 0.06, 0.02, K.M('#2b2b35', { r: 0.35, m: 0.6 })); l.position.set(x, 0.375, z); deskG.add(l); }
    const drawer = K.rbox(0.5, 0.16, 0.7, 0.02, new T.MeshPhysicalMaterial({ map: wood, roughness: 0.5 })); drawer.position.set(0.5, 0.66, 0); deskG.add(drawer);
    const handle = K.rbox(0.14, 0.02, 0.02, 0.008, K.M('#c9ced8', { r: 0.2, m: 0.9 })); handle.position.set(0.5, 0.66, 0.36); deskG.add(handle);
    // стул
    const chair = new T.Group(); chair.position.set(0, 0, -0.62); g.add(chair);
    const seat = K.rbox(0.55, 0.08, 0.5, 0.04, K.M('#3a3f55', { r: 0.6 })); seat.position.y = 0.48; chair.add(seat);
    const backrest = K.rbox(0.55, 0.6, 0.08, 0.05, K.M('#3a3f55', { r: 0.6 })); backrest.position.set(0, 0.85, -0.24); chair.add(backrest);
    const post = K.cyl(0.03, 0.03, 0.4, K.M('#c9ced8', { r: 0.25, m: 0.8 }), 12); post.position.y = 0.24; chair.add(post);
    // ноутбук (экраном к герою)
    const lap = new T.Group(); lap.position.set(0.0, 0.81, -0.02); g.add(lap);
    const alu = K.M('#cfd3dc', { r: 0.25, m: 0.85 });
    const base = K.rbox(0.62, 0.025, 0.42, 0.012, alu); lap.add(base);
    const lid = new T.Group(); lid.position.set(0, 0.012, 0.2); lid.rotation.x = 0.28; lap.add(lid);
    const lidM = K.rbox(0.62, 0.4, 0.018, 0.012, alu); lidM.position.y = 0.2; lid.add(lidM);
    const appleish = K.sph(0.035, K.M('#ffffff', { r: 0.2, m: 0.3 }), 16); appleish.scale.set(1, 1, 0.15); appleish.position.set(0, 0.21, 0.01); lid.add(appleish);
    const glowScreen = K.plane(0.58, 0.36, null); glowScreen.material = new T.MeshBasicMaterial({ color: '#cfe8ff', toneMapped: false }); glowScreen.rotation.y = Math.PI; glowScreen.position.set(0, 0.2, -0.011); lid.add(glowScreen);
    // кружка M1, лампа, стикеры, телефон
    const mug = new T.Group(); mug.position.set(-0.6, 0.81, 0.1); g.add(mug);
    const mb2 = K.cyl(0.06, 0.055, 0.13, K.M('#f6f3ee', { r: 0.3, cc: 0.8 }), 28); mb2.position.y = 0.065; mug.add(mb2);
    const mh = K.mesh(new T.TorusGeometry(0.035, 0.012, 10, 20), K.M('#f6f3ee', { r: 0.3 })); mh.position.set(0.07, 0.07, 0); mh.rotation.z = Math.PI / 2; mug.add(mh);
    const ml = K.canvasTex(256, 128, (c) => { c.fillStyle = '#ff3b3b'; c.font = `900 96px ${K.FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('M1', 128, 70); });
    const mlp = K.plane(0.07, 0.035, ml.tex); mlp.position.set(0, 0.07, 0.061); mug.add(mlp);
    const lamp = new T.Group(); lamp.position.set(0.65, 0.81, -0.25); g.add(lamp);
    const lbase = K.cyl(0.09, 0.1, 0.03, K.M('#ffcf5c', { r: 0.35 }), 24); lamp.add(lbase);
    const arm1 = K.cyl(0.012, 0.012, 0.42, K.M('#ffcf5c', { r: 0.35 }), 10); arm1.position.set(0, 0.21, 0); arm1.rotation.z = 0.25; lamp.add(arm1);
    const shade = K.cyl(0.04, 0.11, 0.13, K.M('#ffcf5c', { r: 0.35 }), 24); shade.position.set(-0.12, 0.42, 0.05); shade.rotation.z = 0.9; lamp.add(shade);
    const bulbL = new T.PointLight('#ffd59a', 0.0, 2.5, 2); bulbL.position.set(-0.18, 0.36, 0.08); lamp.add(bulbL);
    const notes = ['#ffe066', '#ff9ec7', '#8ce0ff'];
    notes.forEach((c, i) => { const n = K.rbox(0.09, 0.004, 0.09, 0.002, K.Mm(c, 0.8)); n.position.set(-0.35 + i * 0.1, 0.812, 0.28); n.rotation.y = (i - 1) * 0.3; g.add(n); });
    const phone = new T.Group(); phone.position.set(-0.32, 0.815, 0.18); phone.rotation.set(-Math.PI / 2, 0, 0.35); g.add(phone);
    const pbody = K.rbox(0.09, 0.18, 0.012, 0.012, K.M('#1d1d24', { r: 0.2, m: 0.6, cc: 1 })); phone.add(pbody);
    const pscr = K.plane(0.08, 0.165, null); pscr.material = new T.MeshBasicMaterial({ color: '#0c0f18', toneMapped: false }); pscr.position.z = 0.0065; phone.add(pscr);

    const fill = new T.HemisphereLight('#fff6ec', '#7b6a5e', 0.7); g.add(fill);
    const key = keyLight(g, [0, 0.8, 0], 3.2, '#fff1de', 2.6, [2.4, 4.5, 3.6]);
    rimLight(g, '#9fd0ff', 1.3, [-3, 3, -3]);
    return { g, door: hinge, clock: { hourH, minH }, win: { pane, paneN }, lamp: bulbL, phone, pscr, lap, glowScreen, fill, key, mug };
  };

  // ================= B: переговорка =================
  W.meeting = function (ox) {
    const g = new T.Group(); g.position.x = ox;
    const floor = K.mesh(new T.PlaneGeometry(14, 14), K.Mm('#a99a8c', 0.8), false); floor.rotation.x = -Math.PI / 2; g.add(floor);
    const rug = K.cyl(1.55, 1.55, 0.01, K.Mm('#6f86b8', 0.95), 48); rug.position.y = 0.005; g.add(rug);
    const wall = K.mesh(new T.PlaneGeometry(14, 6), K.Mm('#e9b98f', 0.9), false); wall.position.set(0, 3, -2.4); g.add(wall);
    const stripe = K.rbox(14, 0.3, 0.04, 0.01, K.Mm('#c9835a', 0.8)); stripe.position.set(0, 0.9, -2.37); g.add(stripe);
    // стол
    const tw = K.woodTex('#b9814f', '#7d4d2a', 8, 11); const tableTop = K.cyl(0.85, 0.85, 0.07, new T.MeshPhysicalMaterial({ map: tw, roughness: 0.4, clearcoat: 0.6 }), 64); tableTop.position.y = 0.74; g.add(tableTop);
    const tableEdge = K.mesh(new T.TorusGeometry(0.85, 0.035, 12, 64), K.M('#5c3a22', { r: 0.45 })); tableEdge.rotation.x = Math.PI / 2; tableEdge.position.y = 0.74; g.add(tableEdge);
    const leg = K.cyl(0.08, 0.3, 0.72, K.M('#2b2b35', { r: 0.35, m: 0.6 }), 24); leg.position.y = 0.36; g.add(leg);
    // доска
    const boardG = new T.Group(); boardG.position.set(0, 1.85, -2.3); g.add(boardG);
    const frame = K.rbox(1.4, 1.8, 0.06, 0.03, K.M('#c9ced8', { r: 0.25, m: 0.8 })); boardG.add(frame);
    const boardTex = K.canvasTex(1024, 1340, () => {});
    const board = K.litPlane(1.3, 1.7, boardTex.tex, 0.35); board.position.z = 0.032; boardG.add(board);
    const tray = K.rbox(1.2, 0.03, 0.08, 0.01, K.M('#c9ced8', { r: 0.25, m: 0.8 })); tray.position.set(0, -0.93, 0.05); boardG.add(tray);
    for (const [x, c] of [[-0.3, '#ff4d6d'], [-0.15, '#2b6bff'], [0.0, '#1d1d24']]) { const mk = K.caps(0.012, 0.09, K.M(c, { r: 0.4 }), 8); mk.rotation.z = Math.PI / 2; mk.position.set(x, -0.9, 0.07); boardG.add(mk); }
    // подвесная лампа
    const pend = K.cyl(0.25, 0.32, 0.18, K.M('#2b2b35', { r: 0.35, m: 0.5 }), 32); pend.position.set(0, 2.55, 0); g.add(pend);
    const cord = K.cyl(0.006, 0.006, 1.2, K.M('#2b2b35', { r: 0.5 }), 6); cord.position.set(0, 3.2, 0); g.add(cord);
    const pg = K.cyl(0.24, 0.24, 0.01, K.glow('#fff1cf', 3), 32); pg.position.set(0, 2.455, 0); pg.castShadow = false; g.add(pg);
    // растение и кулер
    const pot = K.cyl(0.18, 0.14, 0.35, K.M('#e8794f', { r: 0.6 }), 24); pot.position.set(-1.9, 0.175, -1.7); g.add(pot);
    for (let i = 0; i < 9; i++) { const lf = K.sph(0.13, K.M('#4fae6c', { r: 0.5 }), 12); lf.scale.set(0.6, 1.6, 0.4); lf.position.set(-1.9 + Math.sin(i * 0.7) * 0.12, 0.6 + (i % 3) * 0.12, -1.7 + Math.cos(i * 0.7) * 0.1); lf.rotation.z = Math.sin(i * 0.7) * 0.7; g.add(lf); }
    const cooler = K.rbox(0.36, 0.9, 0.34, 0.05, K.M('#f4f6fa', { r: 0.35 })); cooler.position.set(1.9, 0.45, -1.9); g.add(cooler);
    const bottle = K.cyl(0.15, 0.15, 0.42, new T.MeshPhysicalMaterial({ color: '#9fd8ff', roughness: 0.05, transmission: 0.6, transparent: true, opacity: 0.7 }), 24); bottle.position.set(1.9, 1.11, -1.9); g.add(bottle);
    // часы-плакат «ПЛАН»
    const fill = new T.HemisphereLight('#fff1e2', '#5a4a40', 0.45); g.add(fill);
    keyLight(g, [0, 0.8, 0], 3.5, '#ffe9cf', 1.8, [1.8, 5, 3.5]);
    rimLight(g, '#ffd0e8', 1.0, [-3, 3, -3]);
    return { g, boardTex, boardG, board };
  };

  // ================= C: коридор отдела кадров =================
  W.hr = function (ox) {
    const g = new T.Group(); g.position.x = ox;
    const ft = K.tileTex('#ece7df', '#ddd5c9', 10); ft.wrapS = ft.wrapT = T.RepeatWrapping; ft.repeat.set(2, 4);
    const floor = K.mesh(new T.PlaneGeometry(5, 14), new T.MeshStandardMaterial({ map: ft, roughness: 0.45 }), false); floor.rotation.x = -Math.PI / 2; floor.position.z = 1; g.add(floor);
    const wallM = K.Mm('#86c4a6', 0.9);
    for (const s of [-1, 1]) { const w = K.mesh(new T.PlaneGeometry(14, 9), wallM, false); w.rotation.y = -s * Math.PI / 2; w.position.set(s * 2.2, 4.5, 1); g.add(w); const b = K.rbox(0.06, 0.15, 14, 0.02, K.Mm('#9ccdb2', 0.7)); b.position.set(s * 2.17, 0.075, 1); g.add(b); }
    const back = K.mesh(new T.PlaneGeometry(5, 9), K.Mm('#2f5f63', 0.9), false); back.position.set(0, 4.5, -3); g.add(back);
    // дверь
    const doorG = new T.Group(); doorG.position.set(0, 0, -2.97); g.add(doorG);
    const frame = K.rbox(1.25, 2.3, 0.1, 0.03, K.M('#f4f1ea', { r: 0.4 })); frame.position.y = 1.15; doorG.add(frame);
    const dark = K.mesh(new T.PlaneGeometry(1.05, 2.15), new T.MeshBasicMaterial({ color: '#1b2236' }), false); dark.position.set(0, 1.08, 0.055); doorG.add(dark);
    const glowIn = K.mesh(new T.PlaneGeometry(1.05, 2.15), new T.MeshBasicMaterial({ color: '#7ff3ff', transparent: true, opacity: 0.18, toneMapped: false }), false); glowIn.position.set(0, 1.08, 0.056); doorG.add(glowIn);
    const hinge = new T.Group(); hinge.position.set(-0.52, 0, 0.06); doorG.add(hinge);
    const leaf = K.rbox(1.04, 2.14, 0.05, 0.02, K.M('#7fb3ff', { r: 0.45 })); leaf.position.set(0.52, 1.08, 0.02); hinge.add(leaf);
    const signTex = K.canvasTex(1024, 256, (c, w, h) => { K.rrect(c, 8, 8, w - 16, h - 16, 40); c.fillStyle = '#1d1d24'; c.fill(); c.fillStyle = '#ffffff'; K.fit(c, 'ОТДЕЛ КАДРОВ', w - 120, 130, 900); c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('ОТДЕЛ КАДРОВ', w / 2, h / 2 + 6); });
    const sign = K.plane(1.3, 0.325, signTex.tex); sign.position.set(0, 2.55, 0.08); doorG.add(sign);
    // оргструктура над дверью: 40 карточек
    const chart = new T.Group(); chart.position.set(0, 2.95, -2.93); g.add(chart);
    const cards = [];
    const cols = 5, rows = 8, CW = 0.72, CH = 0.42, GX = 0.84, GY = 0.56;
    const palette = ['#c3b2ff', '#ffe08a', '#9fd3ff', '#ffb99a', '#ffadd2', '#9ff0c9'];
    const roles = ['ЮРИСТ', 'ТОН', 'ПЛАН', 'КОПИЯ', 'ТОЧКА', 'СОЗВОН', 'ОТЧЁТ', 'РИСК'];
    for (let r = 0; r < rows; r++) for (let q = 0; q < cols; q++) {
      const i = r * cols + q, col = palette[i % 6], role = roles[(i * 3) % roles.length];
      const tx = K.canvasTex(360, 210, (c, w, h) => { K.rrect(c, 6, 6, w - 12, h - 12, 26); c.fillStyle = '#ffffff'; c.fill(); K.rrect(c, 22, 30, 120, 150, 24); c.fillStyle = col; c.fill(); c.fillStyle = '#141826'; K.rrect(c, 40, 60, 84, 60, 14); c.fill(); c.fillStyle = '#7ff3ff'; c.fillRect(58, 80, 12, 20); c.fillRect(94, 80, 12, 20); c.fillStyle = '#161826'; K.fit(c, role, 190, 50, 900); c.fillText(role, 158, 100); c.fillStyle = '#9aa1b4'; c.font = `700 32px ${K.FONT}`; c.fillText('агент №' + (i + 1), 158, 150); });
      const cd = K.plane(CW, CH, tx.tex); cd.position.set((q - (cols - 1) / 2) * GX, r * GY + 0.25, 0.02); chart.add(cd); cards.push(cd);
    }
    const lineM = new T.MeshBasicMaterial({ color: '#f4f1ea' });
    const lines = [];
    for (let r = 0; r < rows; r++) { const ln = new T.Mesh(new T.PlaneGeometry(cols * GX - 0.3, 0.025), lineM); ln.position.set(0, r * GY + 0.5, 0.01); chart.add(ln); lines.push(ln); }
    const trunk = new T.Mesh(new T.PlaneGeometry(0.025, rows * GY), lineM); trunk.position.set(0, rows * GY / 2 + 0.25, 0.005); chart.add(trunk);
    // столик HR со штампом
    const desk = K.rbox(0.8, 0.06, 0.5, 0.02, K.M('#f4f1ea', { r: 0.4 })); desk.position.set(-1.3, 0.78, -0.6); g.add(desk);
    const dleg = K.rbox(0.7, 0.75, 0.4, 0.02, K.M('#9ccdb2', { r: 0.6 })); dleg.position.set(-1.3, 0.375, -0.6); g.add(dleg);
    const pad = K.rbox(0.2, 0.02, 0.14, 0.01, K.M('#ff4d6d', { r: 0.6 })); pad.position.set(-1.15, 0.82, -0.55); g.add(pad);
    const fill = new T.HemisphereLight('#f2fff8', '#4a5a50', 0.5); g.add(fill);
    keyLight(g, [0, 1, -0.5], 4.5, '#fff3e0', 1.9, [1.5, 6, 4.5]);
    const ceilingLamps = [];
    for (let i = 0; i < 4; i++) { const p = K.rbox(0.9, 0.04, 0.25, 0.02, K.glow('#fffbe8', 2.4)); p.castShadow = false; p.position.set(0, 3.4, 2.5 - i * 1.6); p.rotation.x = 0; g.add(p); ceilingLamps.push(p); }
    return { g, door: hinge, cards, lines, trunk, chart, pad };
  };

  // ================= D: подиум для всплеска =================
  W.podium = function (ox) {
    const g = new T.Group(); g.position.x = ox;
    const backM = new T.MeshStandardMaterial({ color: '#cfc4ff', roughness: 0.92 });
    // циклорама
    const geo = new T.PlaneGeometry(14, 14, 1, 80), p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { const s = p.getY(i) + 7; let y, z; if (s < 6) { y = 0; z = 3 - s; } else { const a = Math.min(Math.PI / 2, (s - 6) / 2.2); y = 2.2 - 2.2 * Math.cos(a); z = -3 - 2.2 * Math.sin(a); if (s - 6 > 2.2 * Math.PI / 2) { y = 2.2 + (s - 6 - 2.2 * Math.PI / 2); z = -5.2; } } p.setXYZ(i, p.getX(i), y, z); }
    geo.computeVertexNormals();
    const cyc = K.mesh(geo, backM, false); g.add(cyc);
    const ped = K.cyl(0.55, 0.6, 0.35, K.M('#ffffff', { r: 0.3, cc: 0.8 }), 64); ped.position.y = 0.175; g.add(ped);
    const pedRing = K.mesh(new T.TorusGeometry(0.575, 0.02, 10, 64), K.M('#ffd166', { r: 0.25, m: 0.8 })); pedRing.rotation.x = Math.PI / 2; pedRing.position.y = 0.35; g.add(pedRing);
    const fill = new T.HemisphereLight('#ffffff', '#8a8090', 0.8); g.add(fill);
    keyLight(g, [0, 0.6, 0], 3, '#fff6ea', 2.4, [2.2, 5, 3.5]);
    rimLight(g, '#ffffff', 1.6, [-2, 3, -3]);
    return { g, backM };
  };

  // ================= E: кнопка «Отправить всем» =================
  W.sendRoom = function (ox) {
    const g = new T.Group(); g.position.x = ox;
    const floor = K.mesh(new T.PlaneGeometry(14, 14), K.Mm('#2c3352', 0.7), false); floor.rotation.x = -Math.PI / 2; g.add(floor);
    const wall = K.mesh(new T.PlaneGeometry(14, 9), K.Mm('#3a4470', 0.9), false); wall.position.set(0, 4.5, -2.6); g.add(wall);
    const ped = K.rbox(0.9, 0.9, 0.9, 0.08, K.M('#e9edf5', { r: 0.35 })); ped.position.set(0, 0.45, 0); g.add(ped);
    const labTex = K.canvasTex(1024, 256, (c, w, h) => { c.fillStyle = '#1d1d24'; K.rrect(c, 10, 10, w - 20, h - 20, 30); c.fill(); c.fillStyle = '#fff'; K.fit(c, 'ОТПРАВИТЬ ВСЕМ', w - 100, 120, 900); c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('ОТПРАВИТЬ ВСЕМ', w / 2, h / 2 + 4); });
    const lab = K.plane(0.8, 0.2, labTex.tex); lab.position.set(0, 0.55, 0.456); g.add(lab);
    const ring = K.cyl(0.32, 0.34, 0.08, K.M('#c9ced8', { r: 0.2, m: 0.9 }), 48); ring.position.y = 0.94; g.add(ring);
    const btnG = new T.Group(); btnG.position.y = 0.98; g.add(btnG);
    const btn = K.mesh(new T.SphereGeometry(0.28, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), K.M('#ff3b4f', { r: 0.18, cc: 1 })); btn.scale.y = 0.55; btnG.add(btn);
    // пневмотруба
    const tube = K.cyl(0.32, 0.32, 3.5, new T.MeshPhysicalMaterial({ color: '#cfefff', roughness: 0.05, transmission: 0.5, transparent: true, opacity: 0.35 }), 40); tube.position.set(0.9, 2.2, -1.2); g.add(tube);
    const collar = K.cyl(0.38, 0.38, 0.18, K.M('#c9ced8', { r: 0.2, m: 0.9 }), 40); collar.position.set(0.9, 0.5, -1.2); g.add(collar);
    const fill = new T.HemisphereLight('#c8d4ff', '#2a2440', 0.9); g.add(fill);
    keyLight(g, [0, 0.8, 0], 3, '#ffe9d6', 2.6, [2, 5, 3]);
    const red = new T.PointLight('#ff4d6d', 0, 3, 2); red.position.set(0, 1.4, 0.4); g.add(red);
    return { g, btnG, red };
  };
})();
