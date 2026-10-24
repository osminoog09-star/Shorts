// 3D-версия 2D-ведущего (аниме-стиль, toon-шейдинг с контуром): овальное лицо с подбородком, тёмно-синие волосы
// с рваной чёлкой и фиолетовым бликом, миндалевидные карие глаза, длинная шея, наушники на шее (голубое/розовое кольцо),
// чёрная толстовка с голубой/розовой окантовкой и «</>».
// Черты лица — рисуются на текстуре головы каждый кадр (как в аниме-3D): моргание, брови, рот по громкости голоса.
import { THREE, lerp, clamp, smooth } from './engine.js';

const grad = (() => { const d = new Uint8Array([70, 160, 255]); const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();
const toon = (color, extra = {}) => new THREE.MeshToonMaterial({ color, gradientMap: grad, ...extra });
const OUT = new THREE.MeshBasicMaterial({ color: 0x14121e, side: THREE.BackSide });
function outlined(mesh, w = 0.035) { const o = new THREE.Mesh(mesh.geometry, OUT); o.scale.setScalar(1 + w); mesh.add(o); return mesh; }

const SKIN = 0xf3cdb4, HAIR = 0x23213a, CLOTH = 0x1b1b24;

// ── текстура лица ──
const FW = 2048, FH = 1024;
const fc = document.createElement('canvas'); fc.width = FW; fc.height = FH; const g = fc.getContext('2d');
const faceTex = new THREE.CanvasTexture(fc); faceTex.colorSpace = THREE.SRGBColorSpace; faceTex.anisotropy = 8;
const U = (u) => u * FW, V = (v) => v * FH;
function drawFace({ blink = 0, mouth = 0, smile = 0, brow = 0, look = 0, laugh = false, viseme = null }) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#f3cdb4'; g.fillRect(0, 0, FW, FH);
  g.setTransform(1.85, 0, 0, 1.85, U(0.25) * (1 - 1.85), V(0.55) * (1 - 1.85));
  const cx = U(0.25);
  // румянец
  for (const s of [-1, 1]) { const gr = g.createRadialGradient(cx + s * 110, V(0.585), 5, cx + s * 110, V(0.585), 55); gr.addColorStop(0, 'rgba(255,140,130,0.45)'); gr.addColorStop(1, 'rgba(255,140,130,0)'); g.fillStyle = gr; g.fillRect(cx + s * 110 - 60, V(0.585) - 60, 120, 120); }
  // глаза
  for (const s of [-1, 1]) {
    const ex = cx + s * 78, ey = V(0.525);
    const open = 1 - (laugh ? 0.85 : blink);
    g.save();
    if (open > 0.08) {
      g.beginPath(); g.moveTo(ex - 40, ey + 2); g.quadraticCurveTo(ex - 5, ey - 30 * open, ex + 40, ey - 4); g.quadraticCurveTo(ex + 5, ey + 18 * open, ex - 40, ey + 2); g.closePath();
      g.fillStyle = '#fbf7f2'; g.fill(); g.clip();
      const ix = ex + look * 12, iy = ey - 4;
      const ir = g.createRadialGradient(ix, iy - 6, 2, ix, iy, 22); ir.addColorStop(0, '#c58a4c'); ir.addColorStop(0.6, '#7a4a22'); ir.addColorStop(1, '#3b220e');
      g.fillStyle = ir; g.beginPath(); g.ellipse(ix, iy, 19, 22, 0, 0, 7); g.fill();
      g.fillStyle = '#120b06'; g.beginPath(); g.ellipse(ix, iy, 8, 10, 0, 0, 7); g.fill();
      g.fillStyle = '#ffffff'; g.beginPath(); g.arc(ix + 7, iy - 9, 6, 0, 7); g.fill(); g.beginPath(); g.arc(ix - 6, iy + 7, 2.5, 0, 7); g.fill();
      g.restore();
      // верхнее веко-подводка + ресницы
      g.strokeStyle = '#1c1420'; g.lineCap = 'round'; g.lineWidth = 7;
      g.beginPath(); g.moveTo(ex - 44, ey + 4); g.quadraticCurveTo(ex - 5, ey - 32 * open - 2, ex + 44, ey - 6); g.stroke();
      g.lineWidth = 4; g.beginPath(); g.moveTo(ex + s * 42, ey - 5); g.lineTo(ex + s * 52, ey - 12); g.stroke();
      g.lineWidth = 2; g.strokeStyle = 'rgba(80,50,50,0.6)'; g.beginPath(); g.moveTo(ex - 30, ey + 12 * open + 6); g.quadraticCurveTo(ex, ey + 20 * open + 4, ex + 30, ey + 8 * open + 4); g.stroke();
    } else {
      g.restore();
      g.strokeStyle = '#1c1420'; g.lineWidth = 7; g.lineCap = 'round';
      g.beginPath(); if (laugh) { g.moveTo(ex - 38, ey + 4); g.quadraticCurveTo(ex, ey - 22, ex + 38, ey + 4); } else { g.moveTo(ex - 40, ey + 2); g.quadraticCurveTo(ex, ey + 12, ex + 40, ey - 2); } g.stroke();
    }
    // бровь
    g.strokeStyle = '#2a2234'; g.lineWidth = 6; g.beginPath();
    const by = ey - 58 - brow * 14; g.moveTo(ex - 40, by + 8 + (s < 0 ? 0 : 0)); g.quadraticCurveTo(ex, by - 6, ex + 42, by + 6 + (brow < 0 ? s * -8 : 0)); g.stroke();
  }
  // нос
  g.strokeStyle = 'rgba(170,110,90,0.7)'; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + 4, V(0.565)); g.quadraticCurveTo(cx + 9, V(0.588), cx, V(0.596)); g.stroke();
  g.fillStyle = 'rgba(255,255,255,0.5)'; g.beginPath(); g.arc(cx - 3, V(0.588), 3, 0, 7); g.fill();
  // рот: виземы Rhubarb (A–H, X) если есть, иначе по громкости
  const my = V(0.625);
  const LIPC = '#7a2e30', INSIDE = '#5a1c22', TEETH = '#ffffff', TONGUE = '#d0626a';
  const MS = 1.6;
  const lineMouth = (w0, curve, th = 5) => { const w = w0 * MS; g.strokeStyle = LIPC; g.lineWidth = th; g.lineCap = 'round'; g.beginPath(); g.moveTo(cx - w, my - curve); g.quadraticCurveTo(cx, my + 6 + curve * 2, cx + w, my - curve); g.stroke(); };
  const openMouth = (w0, h0, { teeth = true, tongue = false, round = false } = {}) => { const w = w0 * MS, h = h0 * MS;
    g.fillStyle = INSIDE; g.beginPath();
    if (round) g.ellipse(cx, my + h * 0.35, w, h * 0.6, 0, 0, 7);
    else { g.moveTo(cx - w, my); g.quadraticCurveTo(cx, my - 5 - smile * 4, cx + w, my); g.quadraticCurveTo(cx, my + h * 1.25, cx - w, my); }
    g.fill();
    if (teeth) { g.fillStyle = TEETH; g.fillRect(cx - w * 0.62, my - 3, w * 1.24, Math.min(10, h * 0.3)); }
    if (tongue) { g.fillStyle = TONGUE; g.beginPath(); g.ellipse(cx, my + h * 0.8, w * 0.55, h * 0.25, 0, 0, 7); g.fill(); }
    g.strokeStyle = LIPC; g.lineWidth = 3; g.stroke();
  };
  const vz = laugh ? 'LAUGH' : viseme;
  if (vz === 'LAUGH') openMouth(42, 30, { tongue: true });
  else if (vz) {
    switch (vz) {
      case 'A': lineMouth(22, 0, 6); break;                       // м/б/п — губы сомкнуты
      case 'B': openMouth(26, 9); break;                          // согласные — чуть приоткрыт, зубы
      case 'C': openMouth(32, 17); break;                         // э/е
      case 'D': openMouth(34, 28, { tongue: true }); break;       // а — широко
      case 'E': openMouth(20, 22, { teeth: false, round: true }); break; // о — округлый
      case 'F': openMouth(11, 13, { teeth: false, round: true }); break; // у/в — трубочкой
      case 'G': openMouth(26, 8); g.strokeStyle = LIPC; g.lineWidth = 4; g.beginPath(); g.moveTo(cx - 20, my + 7); g.lineTo(cx + 20, my + 7); g.stroke(); break; // ф/в
      case 'H': openMouth(28, 18, { tongue: true }); break;       // л
      default: lineMouth(20 + smile * 8, smile * 4, 5);            // X — покой
    }
  } else {
    const mw = 40 + smile * 12 + mouth * 4, mo = clamp(mouth) * 30;
    if (mo < 3) lineMouth(mw * 0.6, smile * 4); else openMouth(mw * 0.6, mo);
  }
  g.setTransform(1, 0, 0, 1, 0, 0);
  faceTex.needsUpdate = true;
}

export function makeAnimeHost() {
  const H = new THREE.Group();
  const SK = toon(SKIN), HR = toon(HAIR), CL = toon(CLOTH);
  // ── голова: сфера, сужающаяся к острому подбородку ──
  const hg = new THREE.SphereGeometry(1, 96, 64); const p = hg.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    if (y < 0) { const k = Math.pow(-y, 1.8); x *= 1 - 0.3 * k; z *= 1 - 0.12 * k; y *= 1 + 0.14 * k; if (z > 0) z += 0.04 * k; }
    p.setXYZ(i, x * 0.84, y * 1.0, z * 0.86);
  }
  hg.computeVertexNormals();
  const head = new THREE.Group(); head.position.y = 1.15; H.add(head);
  const face = outlined(new THREE.Mesh(hg, toon(0xffffff, { map: faceTex })), 0.025); head.add(face);
  for (const s of [-1, 1]) { const ear = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), SK); ear.scale.set(0.45, 1, 0.75); ear.position.set(s * 0.8, 0, -0.02); head.add(ear); }
  // ── волосы ──
  const cap = outlined(new THREE.Mesh(new THREE.SphereGeometry(1.0, 64, 32, 0, Math.PI * 2, 0, Math.PI * 0.55), HR), 0.02);
  cap.scale.set(0.9, 1.0, 0.95); cap.position.set(0, 0.16, -0.1); cap.rotation.x = -0.62; head.add(cap);
  const back = outlined(new THREE.Mesh(new THREE.SphereGeometry(0.9, 48, 32), HR), 0.02); back.scale.set(0.95, 1.05, 0.85); back.position.set(0, 0.02, -0.25); head.add(back);
  const spike = (x, y, z, w, L, rx, rz) => { const c = outlined(new THREE.Mesh(new THREE.ConeGeometry(w, L, 4, 1), HR), 0.04); c.scale.z = 0.45; c.position.set(x, y, z); c.rotation.set(rx, 0, Math.PI + rz); head.add(c); return c; };
  // рваная чёлка
  [[-0.5, 0.42, 0.7, 0.2, 0.5, -0.35, -0.25], [-0.26, 0.47, 0.8, 0.22, 0.58, -0.4, -0.08], [-0.02, 0.48, 0.84, 0.2, 0.46, -0.42, 0.05], [0.22, 0.47, 0.8, 0.22, 0.6, -0.4, 0.12], [0.46, 0.42, 0.7, 0.2, 0.48, -0.35, 0.28]]
    .forEach((a) => spike(...a));
  // боковые пряди до скул и затылок
  for (const s of [-1, 1]) { spike(s * 0.74, 0.1, 0.32, 0.2, 0.85, -0.15, s * -0.08); spike(s * 0.7, 0.0, 0.0, 0.22, 0.9, 0, s * -0.12); }
  for (let i = 0; i < 5; i++) spike((i - 2) * 0.28, 0.05, -0.62, 0.22, 0.8, 0.3, (i - 2) * 0.1);
  // фиолетовый блик на макушке
  const hl = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.03, 8, 48, Math.PI * 0.7), new THREE.MeshBasicMaterial({ color: 0x8f7bd8 })); hl.position.set(0, 0.62, 0.22); hl.rotation.set(-0.9, 0, Math.PI * 0.15); head.add(hl);
  // ── шея, корпус ──
  const neck = outlined(new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.25, 1.0, 24), SK), 0.04); neck.position.y = 0.15; H.add(neck);
  const torso = outlined(new THREE.Mesh(new THREE.CapsuleGeometry(0.9, 1.0, 10, 32), CL), 0.02); torso.scale.set(1.2, 1, 0.58); torso.position.y = -1.6; H.add(torso);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.07, 12, 40), CL); collar.rotation.x = Math.PI / 2; collar.position.y = -0.42; H.add(collar);
  // окантовка (голубая слева, розовая справа)
  for (const [s, c] of [[-1, 0x58c8ff], [1, 0xff5fb0]]) {
    const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(s * 0.45, -0.55, 0.42), new THREE.Vector3(s * 0.95, -0.66, 0.3), new THREE.Vector3(s * 1.2, -1.05, 0.12)]);
    const pip = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.025, 8), new THREE.MeshBasicMaterial({ color: c })); H.add(pip);
  }
  // наушники на шее
  const band = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.05, 10, 40, Math.PI), toon(0x2a2a36)); band.rotation.set(Math.PI / 2 + 0.2, 0, 0); band.position.set(0, -0.3, -0.05); H.add(band);
  for (const [s, c] of [[-1, 0x4fc3ff], [1, 0xff4fa8]]) {
    const cup = outlined(new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.16, 32), toon(0x2a2a36)), 0.05); cup.rotation.x = Math.PI / 2; cup.rotation.z = s * 0.25; cup.position.set(s * 0.5, -0.3, 0.3); H.add(cup);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.03, 10, 40), new THREE.MeshBasicMaterial({ color: c })); ring.position.set(s * 0.5, -0.3, 0.39); ring.rotation.y = s * 0.25; H.add(ring);
  }
  const logo = (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const x = c.getContext('2d'); x.font = '700 80px "RMono", monospace'; x.fillStyle = '#7fd8ff'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('</>', 128, 64); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; const m = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.25), new THREE.MeshBasicMaterial({ map: t, transparent: true })); return m; })();
  logo.position.set(-0.5, -1.3, 0.54); H.add(logo);
  // ── руки ──
  const arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 1.05, -0.75, 0); H.add(sh);
    const up = outlined(new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.75, 8, 16), CL), 0.04); up.position.y = -0.45; sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.92; sh.add(el);
    const fo = outlined(new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.62, 8, 16), CL), 0.04); fo.position.y = -0.38; el.add(fo);
    const hand = outlined(new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 16), SK), 0.05); hand.scale.set(0.9, 1.15, 0.7); hand.position.y = -0.82; el.add(hand);
    arms.push({ s, sh, el });
  }
  H.userData = { head, arms, torso };
  return H;
}

const POSE = {
  rest: { L: [0.05, 0.1, 0.1], R: [0.05, 0.1, 0.1], head: [0, 0, 0] },
  talk: { L: [0.2, 0.7, 0.2], R: [0.45, 1.1, 0.25], head: [0.03, 0, 0] },
  point: { L: [0.05, 0.1, 0.1], R: [0.45, 0.3, 1.2], head: [-0.03, 0.22, 0.04] },
  facepalm: { L: [0.05, 0.1, 0.1], R: [1.1, 2.55, -0.45], head: [0.22, -0.05, -0.1] },
  shrug: { L: [0.25, 1.3, 0.6], R: [0.25, 1.3, 0.6], head: [0, 0, 0.12] },
  laugh: { L: [0.25, 1.0, 0.3], R: [0.25, 1.0, 0.3], head: [-0.12, 0, 0.05] },
  wave: { L: [0.05, 0.1, 0.1], R: [0.3, 2.3, 0.85], head: [0, 0.1, 0.06], wave: 1 },
};

export function animateAnimeHost(H, t, { pose = 'talk', prev = 'rest', k = 1, mouth = 0, look = 0, viseme = null } = {}) {
  const Ud = H.userData; const A = POSE[prev] || POSE.rest, B = POSE[pose] || POSE.rest; const e = smooth(clamp(k));
  const mix = (a, b) => a.map((v, i) => lerp(v, b[i], e));
  const L = mix(A.L, B.L), R = mix(A.R, B.R), hd = mix(A.head, B.head);
  const [l, r] = Ud.arms;
  const waveA = B.wave ? Math.sin(t * 9) * 0.3 * e : 0, gest = pose === 'talk' ? Math.sin(t * 2.3) * 0.22 * mouth : 0;
  l.sh.rotation.set(-L[0], 0, -L[2]); l.el.rotation.x = -L[1];
  r.sh.rotation.set(-R[0] - gest, 0, R[2] + waveA); r.el.rotation.x = -R[1] + gest * 0.5;
  Ud.head.rotation.set(hd[0] + mouth * 0.04 + Math.sin(t * 1.3) * 0.02, hd[1] + Math.sin(t * 0.6) * 0.05, hd[2] + Math.sin(t * 0.9) * 0.025 + (pose === 'laugh' ? Math.sin(t * 14) * 0.03 : 0));
  Ud.torso.scale.y = 1 + Math.sin(t * 2) * 0.01;
  const ph = (t * 0.31 + 0.2) % 1; const blink = ph < 0.04 ? 1 - Math.abs(ph - 0.02) / 0.02 : 0;
  drawFace({ blink: pose === 'facepalm' ? 0.5 : blink, mouth, smile: pose === 'laugh' || pose === 'wave' ? 1 : pose === 'point' ? 0.4 : 0.1, brow: pose === 'facepalm' ? -0.6 : pose === 'point' ? 0.5 : mouth * 0.3, look, laugh: pose === 'laugh', viseme });
}
