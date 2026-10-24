// Общие 3D-ассеты и помощники камеры для фильма
import { THREE, C, W, H, toon, gear, lights, lerp, clamp, hash, noise1 } from './engine.js';

export function mk(opts = {}) {
  const scene = new THREE.Scene();
  lights(scene, opts);
  const cam = new THREE.PerspectiveCamera(opts.fov || 38, W / H, 0.1, 200);
  return { scene, cam };
}

export function orbit(cam, target, r, az, el, roll = 0) {
  cam.position.set(target.x + Math.sin(az) * Math.cos(el) * r, target.y + Math.sin(el) * r, target.z + Math.cos(az) * Math.cos(el) * r);
  cam.up.set(0, 1, 0);
  cam.lookAt(target);
  cam.rotateZ(roll);
  cam.updateMatrixWorld();
}

export const v3 = (x, y, z) => new THREE.Vector3(x, y, z);

// Набор сцепленных шестерён: возвращает группу и update(angle)
const K = 22;
export const pitch = (r) => r * 0.94;
export function gearTrain(defs, opts = {}) {
  // defs: [{r, color, parent: idx|null, ang: радианы направления от родителя, z, coax: idx (на одной оси)}]
  const grp = new THREE.Group();
  const gs = [];
  defs.forEach((d, i) => {
    const teeth = Math.max(8, Math.round(d.r * K));
    const m = gear(teeth, d.r, d.color ?? C.bronze, { thick: d.thick ?? opts.thick ?? 0.3, spokes: d.spokes ?? (d.r > 1 ? 4 : d.r > 0.6 ? 3 : 0), holeR: 0.16 });
    let x = 0, y = 0, ratio = 1, phase = 0;
    if (d.parent != null) {
      const p = gs[d.parent];
      const dist = pitch(p.r) + pitch(d.r);
      x = p.x + Math.cos(d.ang) * dist; y = p.y + Math.sin(d.ang) * dist;
      ratio = -p.ratio * p.teeth / teeth;
      // фаза: зуб напротив впадины
      phase = Math.PI / teeth + (d.ang + Math.PI) - (p.phase + d.ang) * (p.teeth / teeth) * -1;
      phase = (Math.PI + d.ang) + (d.ang - p.phase) * (p.teeth / teeth) + Math.PI / teeth;
    } else if (d.coax != null) {
      const p = gs[d.coax]; x = p.x; y = p.y; ratio = p.ratio; phase = 0;
    } else { x = d.x || 0; y = d.y || 0; }
    m.position.set(x, y, d.z || 0);
    grp.add(m);
    gs.push({ m, r: d.r, teeth, x, y, ratio, phase });
  });
  // корректная фаза для сцепления: θc = -(tp/tc)(θp - a) + a + π + π/tc
  gs.forEach((g, i) => {
    const d = defs[i];
    if (d.parent != null) {
      const p = gs[d.parent];
      g.phase = -(p.teeth / g.teeth) * (p.phase - d.ang) + d.ang + Math.PI + Math.PI / g.teeth;
    } else if (d.coax != null) g.phase = gs[d.coax].phase;
  });
  function update(a) { gs.forEach((g) => { g.m.rotation.z = a * g.ratio + g.phase; }); }
  return { grp, gs, update };
}

// Ком корродированной бронзы
export function lump({ r = 1.6, color = C.patina, seed = 1 } = {}) {
  const g = new THREE.IcosahedronGeometry(r, 4);
  const p = g.attributes.position; const v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    const n = v.clone().normalize();
    const d = 1 + 0.16 * Math.sin(n.x * 3.1 + seed) * Math.cos(n.y * 2.3 + seed * 2) + 0.08 * Math.sin(n.z * 6 + n.x * 4 + seed);
    v.copy(n).multiplyScalar(r * d);
    v.z *= 0.55; v.x *= 1.25;
    p.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeVertexNormals();
  return new THREE.Mesh(g, toon(color));
}

// Амфора
export function amphora(color = C.red) {
  const pts = [[0, -1.2], [0.25, -1.15], [0.55, -0.7], [0.62, -0.1], [0.5, 0.45], [0.22, 0.75], [0.2, 1.05], [0.3, 1.15], [0, 1.15]].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.LatheGeometry(pts, 20), toon(color)));
  for (const s of [-1, 1]) {
    const h = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.05, 8, 16, Math.PI), toon(color));
    h.position.set(s * 0.32, 0.8, 0); h.rotation.z = s > 0 ? -Math.PI / 2 : Math.PI / 2; g.add(h);
  }
  return g;
}

// Монета
export function coin(color = C.sun) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.08, 24), toon(color));
  m.rotation.x = Math.PI / 2; const g = new THREE.Group(); g.add(m);
  const s = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.1, 6), toon(C.bronze)); s.rotation.x = Math.PI / 2; g.add(s);
  return g;
}

// Бюст статуи (стилизация)
export function bust(color = C.bronze) {
  const g = new THREE.Group();
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.7, 24, 18), toon(color)); head.scale.set(0.9, 1.1, 0.95); head.position.y = 1.1; g.add(head);
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.35, 8), toon(color)); nose.position.set(0, 1.05, 0.7); nose.rotation.x = Math.PI / 2; g.add(nose);
  const beard = new THREE.Mesh(new THREE.SphereGeometry(0.45, 16, 12), toon(color)); beard.scale.set(1, 0.8, 0.7); beard.position.set(0, 0.6, 0.35); g.add(beard);
  for (let i = 0; i < 7; i++) {
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), toon(color));
    const a = -1.4 + i * 0.47; c.position.set(Math.sin(a) * 0.62, 1.65 + Math.cos(a) * 0.12, Math.cos(a) * 0.5 - 0.1); g.add(c);
  }
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.4, 0.5, 16), toon(color)); neck.position.y = 0.25; g.add(neck);
  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.9, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), toon(color)); chest.scale.set(1.3, 0.7, 0.8); chest.position.y = -0.35; g.add(chest);
  return g;
}

// Лодка ловцов губок
export function boat() {
  const g = new THREE.Group();
  const sh = new THREE.Shape(); sh.moveTo(-2.2, 0.4); sh.quadraticCurveTo(-1.6, -0.6, 0, -0.65); sh.quadraticCurveTo(1.6, -0.6, 2.4, 0.6); sh.lineTo(-2.2, 0.4);
  const hull = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 1.2, bevelEnabled: true, bevelSize: 0.08, bevelThickness: 0.08, bevelSegments: 1 }), toon(C.red));
  hull.position.z = -0.6; g.add(hull);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(4.3, 0.12, 1.42), toon(C.paper)); stripe.position.y = 0.25; g.add(stripe);
  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 3.4, 8), toon(C.bronze)); mast.position.set(0.2, 1.9, 0); g.add(mast);
  const ss = new THREE.Shape(); ss.moveTo(0, 0); ss.lineTo(1.7, 0.2); ss.lineTo(0, 2.6); ss.lineTo(0, 0);
  const sail = new THREE.Mesh(new THREE.ExtrudeGeometry(ss, { depth: 0.04, bevelEnabled: false }), toon(C.paper)); sail.position.set(0.28, 0.6, 0); g.add(sail);
  return g;
}

// Ныряльщик в шлеме
export function diver() {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 0.8, 6, 14), toon(C.sun)); g.add(body);
  const helm = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 16), toon(C.bronze)); helm.position.y = 0.95; g.add(helm);
  const win = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.12, 20), toon(C.sea)); win.rotation.x = Math.PI / 2; win.position.set(0, 0.97, 0.47); g.add(win);
  for (const s of [-1, 1]) {
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.14, 0.6, 4, 8), toon(C.sun)); arm.position.set(s * 0.55, 0.1, 0); arm.rotation.z = s * 0.5; arm.name = s < 0 ? 'armL' : 'armR'; g.add(arm);
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.6, 4, 8), toon(C.sun)); leg.position.set(s * 0.22, -0.95, 0); leg.name = s < 0 ? 'legL' : 'legR'; g.add(leg);
    const boot = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.18, 0.4), toon(C.ink)); boot.position.set(s * 0.22, -1.38, 0.06); g.add(boot);
  }
  return g;
}

// Волны: плоскость с анимацией
export function waves(w = 40, d = 30, seg = 70) {
  const geo = new THREE.PlaneGeometry(w, d, seg, Math.round(seg * d / w)); geo.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(geo, toon(C.sea));
  const base = geo.attributes.position.array.slice();
  m.userData.update = (t, amp = 1) => {
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = base[i * 3], z = base[i * 3 + 2];
      p.array[i * 3 + 1] = amp * (0.45 * Math.sin(x * 0.55 + t * 1.6) + 0.3 * Math.sin(z * 0.8 - t * 1.2 + x * 0.2) + 0.12 * Math.sin((x + z) * 1.7 + t * 3));
    }
    p.needsUpdate = true; geo.computeVertexNormals();
  };
  m.userData.height = (x, z, t, amp = 1) => amp * (0.45 * Math.sin(x * 0.55 + t * 1.6) + 0.3 * Math.sin(z * 0.8 - t * 1.2 + x * 0.2) + 0.12 * Math.sin((x + z) * 1.7 + t * 3));
  return m;
}

// Корпус механизма (реконструкция) с передним циферблатом и ручкой
export function mechanismBox() {
  const g = new THREE.Group();
  const box = new THREE.Mesh(new THREE.BoxGeometry(3.2, 4.2, 1.2), toon(0xc9874a)); g.add(box);
  const face = new THREE.Mesh(new THREE.BoxGeometry(2.8, 3.8, 0.08), toon(C.bronze)); face.position.z = 0.62; g.add(face);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.09, 10, 64), toon(C.sun)); ring.position.set(0, 0.2, 0.7); g.add(ring);
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(0.85, 0.05, 8, 64), toon(C.paper)); ring2.position.set(0, 0.2, 0.7); g.add(ring2);
  for (let i = 0; i < 12; i++) {
    const tk = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.22, 0.05), toon(C.ink));
    const a = (i / 12) * Math.PI * 2; tk.position.set(Math.cos(a) * 1.0, 0.2 + Math.sin(a) * 1.0, 0.72); tk.rotation.z = a + Math.PI / 2; g.add(tk);
  }
  const sunP = new THREE.Group(); sunP.position.set(0, 0.2, 0.78); g.add(sunP);
  const sp = new THREE.Mesh(new THREE.BoxGeometry(0.07, 1.1, 0.04), toon(C.sun)); sp.position.y = 0.55; sunP.add(sp);
  const sb = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), toon(C.sun)); sb.position.y = 1.1; sunP.add(sb);
  const moonP = new THREE.Group(); moonP.position.set(0, 0.2, 0.86); g.add(moonP);
  const mp = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.8, 0.04), toon(C.paper)); mp.position.y = 0.4; moonP.add(mp);
  const mb = new THREE.Mesh(new THREE.SphereGeometry(0.14, 16, 12), toon(0xeeeeee)); mb.position.y = 0.8; moonP.add(mb);
  const mbd = new THREE.Mesh(new THREE.SphereGeometry(0.142, 16, 12, 0, Math.PI), toon(0x333344)); mbd.position.y = 0.8; moonP.add(mbd); mbd.name = 'moonDark';
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.2, 16), toon(C.red)); hub.rotation.x = Math.PI / 2; hub.position.set(0, 0.2, 0.86); g.add(hub);
  // ручка сбоку
  const crank = new THREE.Group(); crank.position.set(1.62, 0, 0); g.add(crank);
  const ax = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.4, 12), toon(C.bronze)); ax.rotation.z = Math.PI / 2; ax.position.x = 0.2; crank.add(ax);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.9, 0.12), toon(C.bronze)); arm.position.set(0.42, 0.4, 0); crank.add(arm);
  const knob = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.45, 12), toon(C.red)); knob.rotation.z = Math.PI / 2; knob.position.set(0.62, 0.82, 0); crank.add(knob);
  // задняя панель: две спирали
  const back = new THREE.Group(); back.position.z = -0.64; back.rotation.y = Math.PI; g.add(back);
  const spiral = (cx, cy, turns, r0, r1, color) => {
    const pts = []; const n = turns * 60;
    for (let i = 0; i <= n; i++) { const a = (i / 60) * Math.PI * 2; const r = lerp(r0, r1, i / n); pts.push(new THREE.Vector3(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 0.02)); }
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n, 0.035, 6), toon(color)); return m;
  };
  const plate = new THREE.Mesh(new THREE.BoxGeometry(2.8, 3.8, 0.06), toon(C.bronze)); back.add(plate);
  const s1 = spiral(0, 0.95, 5, 0.2, 0.8, C.sun); back.add(s1);
  const s2 = spiral(0, -0.95, 4, 0.2, 0.8, C.paper); back.add(s2);
  const bp1 = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.85, 0.04), toon(C.red)); bp1.geometry.translate(0, 0.42, 0); bp1.position.set(0, 0.95, 0.08); back.add(bp1);
  const bp2 = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.85, 0.04), toon(C.red)); bp2.geometry.translate(0, 0.42, 0); bp2.position.set(0, -0.95, 0.08); back.add(bp2);
  return { g, sunP, moonP, crank, back, bp1, bp2, mbd };
}

// Ноутбук (финал)
export function laptop() {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.12, 1.6), toon(0xb8c4d6)); g.add(base);
  const lid = new THREE.Group(); lid.position.set(0, 0.06, -0.8); g.add(lid);
  const scr = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.6, 0.08), toon(0xb8c4d6)); scr.position.set(0, 0.8, 0); lid.add(scr);
  const disp = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 1.35), toon(C.blue)); disp.position.set(0, 0.8, 0.05); lid.add(disp);
  lid.rotation.x = -0.25;
  return g;
}

// Кольцо томографа
export function scanner() {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.55, 16, 64), toon(0xe8eef7)); g.add(ring);
  const band = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.57, 8, 64, Math.PI * 0.3), toon(C.blue)); band.rotation.z = Math.PI * 0.35; g.add(band);
  const light = new THREE.Mesh(new THREE.TorusGeometry(2.05, 0.06, 8, 64), new THREE.MeshBasicMaterial({ color: C.sun })); g.add(light);
  return g;
}

// Башня с часами (XIV век)
export function clockTower() {
  const g = new THREE.Group();
  const tower = new THREE.Mesh(new THREE.BoxGeometry(1.6, 5, 1.6), toon(C.paper)); tower.position.y = 2.5; g.add(tower);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(1.35, 1.8, 4), toon(C.red)); roof.position.y = 5.9; roof.rotation.y = Math.PI / 4; g.add(roof);
  const face = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.1, 32), toon(C.sun)); face.rotation.x = Math.PI / 2; face.position.set(0, 3.9, 0.82); g.add(face);
  const hand = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.5, 0.05), toon(C.ink)); hand.geometry.translate(0, 0.22, 0); hand.position.set(0, 3.9, 0.9); g.add(hand); hand.name = 'hand';
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.0, 0.1), toon(C.bronze)); door.position.set(0, 0.5, 0.82); g.add(door);
  return g;
}

export { THREE, C, toon, gear, lerp, clamp, hash, noise1 };
