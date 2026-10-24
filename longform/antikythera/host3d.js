// 3D-ведущий канала M1lash: стилизованный «премиальный» персонаж (скруглённые формы, глянец/мат),
// узнаваемые черты 2D-ведущего: тёмная причёска с чёлкой, карие глаза, наушники с голубым/розовым кольцом, тёмное худи с «</>».
import { THREE, C, matte, gloss, metal, lerp, clamp, smooth, seg } from './engine.js';
import { sphere, cyl, rbox, textSprite } from './kit.js';

const SKIN = new THREE.MeshPhysicalMaterial({ color: 0xf2c4a6, roughness: 0.55, sheen: 0.6, sheenColor: new THREE.Color(0xffd9c4), clearcoat: 0.08 });
const HAIR = new THREE.MeshPhysicalMaterial({ color: 0x1d1b2a, roughness: 0.35, clearcoat: 0.6, clearcoatRoughness: 0.3 });
const HOOD = new THREE.MeshStandardMaterial({ color: 0x23232f, roughness: 0.85 });
const WHITE = gloss(0xffffff, { roughness: 0.12, clearcoat: 1 });
const IRIS = new THREE.MeshPhysicalMaterial({ color: 0x7a4a22, roughness: 0.2, clearcoat: 1 });
const PUPIL = new THREE.MeshBasicMaterial({ color: 0x0d0907 });
const LIP = matte(0xb85e55, { roughness: 0.5 });
const MOUTH_IN = new THREE.MeshBasicMaterial({ color: 0x4a1a1c });
const BLUSH = new THREE.MeshBasicMaterial({ color: 0xff8f86, transparent: true, opacity: 0.25, depthWrite: false });
const RING_C = new THREE.MeshStandardMaterial({ color: 0x58c8ff, emissive: 0x2aa8ff, emissiveIntensity: 1.6 });
const RING_P = new THREE.MeshStandardMaterial({ color: 0xff5fb0, emissive: 0xff2f90, emissiveIntensity: 1.6 });
const DARKM = metal(0x30313d, { roughness: 0.35 });

function limb(r, len, mat) { // капсула вдоль -Y от точки крепления
  const g = new THREE.Group(); const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 20), mat); m.position.y = -len / 2; m.castShadow = true; g.add(m); g.userData.len = len; return g;
}

export function makeHost() {
  const H = new THREE.Group();
  // ── корпус: худи ──
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.95, 1.2, 10, 32), HOOD); torso.scale.set(1.05, 1, 0.7); torso.position.y = -2.05; torso.castShadow = true; H.add(torso);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.16, 16, 48), HOOD); collar.rotation.x = Math.PI / 2; collar.position.y = -0.92; collar.scale.set(0.9, 0.9, 0.7); H.add(collar);
  const logo = textSprite('</>', { size: 60, scale: 0.42, bg: null, color: '#9fe8ff', font: 'RMono' }); logo.position.set(0.45, -1.75, 0.7); H.add(logo);
  // ── шея и голова ──
  const neck = cyl(0.26, 0.6, SKIN, 24); neck.position.y = -0.6; H.add(neck);
  const head = new THREE.Group(); head.position.y = 0.45; H.add(head);
  const skull = sphere(0.92, SKIN, 64); skull.scale.set(0.95, 1.08, 0.95); head.add(skull);
  const jaw = sphere(0.7, SKIN, 48); jaw.scale.set(0.95, 0.75, 0.9); jaw.position.set(0, -0.42, 0.12); head.add(jaw);
  for (const s of [-1, 1]) { const ear = sphere(0.18, SKIN, 24); ear.scale.set(0.5, 1, 0.8); ear.position.set(s * 0.9, -0.02, 0); head.add(ear); }
  // волосы: гладкая масса сверху/сзади + крупные пряди чёлки (не шлем, не «шарики»)
  const strands = [];
  const mass = new THREE.Mesh(new THREE.SphereGeometry(1.0, 64, 32, 0, Math.PI * 2, 0, Math.PI * 0.56), HAIR);
  mass.scale.set(1.03, 1.0, 1.04); mass.position.set(0, 0.06, -0.06); mass.rotation.x = -0.42; mass.castShadow = true; head.add(mass);
  const nape = sphere(0.9, HAIR, 48); nape.position.set(0, -0.12, -0.32); nape.scale.set(1.02, 0.95, 0.8); head.add(nape);
  // пряди чёлки: сплющенные капсулы, свисают на лоб
  [[-0.5, 0.0, -0.5, 0.42], [-0.22, 0.04, -0.18, 0.48], [0.08, 0.05, 0.12, 0.46], [0.36, 0.02, 0.4, 0.42], [0.6, -0.06, 0.65, 0.36], [-0.72, -0.1, -0.8, 0.36]]
    .forEach(([x, dy, rz, L]) => { const c = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, L, 8, 16), HAIR); c.scale.set(1.3, 1, 0.55); c.position.set(x, 0.56 + dy - L * 0.35, 0.78 - Math.abs(x) * 0.28); c.rotation.set(-0.5, -x * 0.5, rz * 0.35); c.castShadow = true; head.add(c); strands.push(c); });
  for (const sd of [-1, 1]) { const sl = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.5, 8, 16), HAIR); sl.scale.set(1, 1, 0.6); sl.position.set(sd * 0.86, 0.12, 0.3); sl.rotation.z = sd * 0.12; head.add(sl); }
  // глаза
  const eyes = [];
  for (const s of [-1, 1]) {
    const e = new THREE.Group(); e.position.set(s * 0.33, -0.04, 0.75); head.add(e);
    const ball = sphere(0.2, WHITE, 32); ball.scale.set(1, 1.1, 0.6); e.add(ball);
    const iris = sphere(0.12, IRIS, 32); iris.scale.set(1, 1.1, 0.4); iris.position.z = 0.1; e.add(iris);
    const pupil = sphere(0.06, PUPIL, 16); pupil.scale.set(1, 1.1, 0.4); pupil.position.z = 0.14; e.add(pupil);
    const hl = sphere(0.025, new THREE.MeshBasicMaterial({ color: 0xffffff }), 8); hl.position.set(0.04, 0.05, 0.16); e.add(hl);
    const lid = new THREE.Mesh(new THREE.SphereGeometry(0.215, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), SKIN); lid.scale.set(1, 1.1, 0.66); lid.rotation.x = -1.4; e.add(lid);
    const brow = rbox(0.3, 0.06, 0.06, HAIR, 0.03); brow.position.set(0, 0.27, 0.09); brow.rotation.z = s * -0.08; e.add(brow);
    eyes.push({ e, iris, pupil, lid, brow, s });
  }
  const nose = sphere(0.07, SKIN, 16); nose.scale.set(1, 0.8, 1.2); nose.position.set(0, -0.2, 0.86); head.add(nose);
  for (const s of [-1, 1]) { const b = new THREE.Mesh(new THREE.CircleGeometry(0.13, 24), BLUSH); b.position.set(s * 0.5, -0.25, 0.78); b.rotation.y = s * 0.45; head.add(b); }
  // рот: внутренность + губы (масштабируются по артикуляции)
  const mouth = new THREE.Group(); mouth.position.set(0, -0.45, 0.8); head.add(mouth);
  const inner = sphere(0.14, MOUTH_IN, 24); inner.scale.set(1.3, 0.2, 0.4); mouth.add(inner);
  const lipU = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.03, 8, 32, Math.PI), LIP); lipU.rotation.z = 0; lipU.scale.set(1.15, 0.25, 1); mouth.add(lipU);
  const lipD = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.035, 8, 32, Math.PI), LIP); lipD.rotation.z = Math.PI; lipD.scale.set(1.15, 0.3, 1); mouth.add(lipD);
  const teeth = rbox(0.22, 0.05, 0.05, WHITE, 0.02); teeth.position.set(0, 0.03, 0.02); mouth.add(teeth);
  // наушники
  const band = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.07, 12, 64, Math.PI), DARKM); band.position.set(0, 0.05, -0.05); band.rotation.z = 0; head.add(band);
  for (const [s, m] of [[-1, RING_C], [1, RING_P]]) { const cup = cyl(0.3, 0.2, DARKM, 32); cup.rotation.z = Math.PI / 2; cup.position.set(s * 0.98, 0.0, -0.02); head.add(cup); const ring = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.035, 12, 40), m); ring.rotation.y = Math.PI / 2; ring.position.set(s * 1.09, 0.0, -0.02); head.add(ring); }
  // руки
  const arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 1.02, -1.15, 0); H.add(sh);
    const up = limb(0.22, 0.75, HOOD); sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.9; up.add(el);
    const fo = limb(0.19, 0.65, HOOD); el.add(fo);
    const hand = sphere(0.2, SKIN, 24); hand.position.y = -0.88; fo.add(hand);
    const finger = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.28, 6, 12), SKIN); finger.position.set(0, -1.12, 0.04); finger.visible = false; fo.add(finger);
    arms.push({ s, sh, el, finger });
  }
  H.userData = { head, eyes, mouth, inner, lipU, lipD, teeth, arms, strands, torso };
  return H;
}

// Позы: rest / talk / point / facepalm / shrug / laugh / wave
const POSE = {
  // [подъём вперёд, сгиб локтя, разведение в сторону]
  rest: { L: [0.1, 0.15, 0.12], R: [0.1, 0.15, 0.12], head: [0, 0, 0] },
  talk: { L: [0.35, 0.9, 0.25], R: [0.6, 1.2, 0.3], head: [0.04, 0, 0] },
  point: { L: [0.1, 0.15, 0.12], R: [0.5, 0.35, 1.25], head: [-0.05, 0.25, 0.05], finger: 1 },
  facepalm: { L: [0.1, 0.15, 0.12], R: [1.0, 2.5, -0.35], head: [0.25, -0.05, -0.12] },
  shrug: { L: [0.3, 1.4, 0.7], R: [0.3, 1.4, 0.7], head: [0, 0, 0.12] },
  laugh: { L: [0.3, 1.2, 0.35], R: [0.3, 1.2, 0.35], head: [-0.15, 0, 0.05] },
  wave: { L: [0.1, 0.15, 0.12], R: [0.4, 2.4, 0.9], head: [0, 0.1, 0.06], wave: 1 },
};

// t — время, pose/prev/k — переход позы, mouth 0..1 — громкость голоса, look — смещение взгляда
export function animateHost(H, t, { pose = 'talk', prev = 'rest', k = 1, mouth = 0, look = [0, 0] } = {}) {
  const U = H.userData; const A = POSE[prev] || POSE.rest, B = POSE[pose] || POSE.rest; const e = smooth(clamp(k));
  const mix = (a, b) => a.map((v, i) => lerp(v, b[i], e));
  const L = mix(A.L, B.L), R = mix(A.R, B.R), hd = mix(A.head, B.head);
  const wob = Math.sin(t * 1.7) * 0.04 + mouth * 0.05;
  const [l, r] = U.arms;
  const waveA = B.wave ? Math.sin(t * 9) * 0.3 * e : 0;
  const gest = pose === 'talk' ? Math.sin(t * 2.3) * 0.25 * mouth : 0;
  l.sh.rotation.set(-L[0], 0, -L[2]); l.el.rotation.x = -L[1];
  r.sh.rotation.set(-R[0] - gest, 0, R[2] + waveA); r.el.rotation.x = -R[1] + gest * 0.5;
  r.finger.visible = !!B.finger && e > 0.5;
  U.head.rotation.set(hd[0] + wob, hd[1] + Math.sin(t * 0.6) * 0.06 + look[0] * 0.2, hd[2] + Math.sin(t * 0.9) * 0.03 + (pose === 'laugh' ? Math.sin(t * 14) * 0.04 : 0));
  U.torso.scale.y = 1 + Math.sin(t * 2) * 0.012; // дыхание
  // моргание + глаза
  const blinkPh = (t * 0.31 + 0.2) % 1; const blink = blinkPh < 0.04 ? 1 - Math.abs(blinkPh - 0.02) / 0.02 : 0;
  const closed = pose === 'laugh' ? 0.75 : pose === 'facepalm' ? 0.55 : 0;
  U.eyes.forEach(({ lid, iris, pupil, brow, s }) => {
    lid.rotation.x = lerp(-1.22, -0.2, Math.max(blink, closed));
    iris.position.x = look[0] * 0.05; iris.position.y = look[1] * 0.04; pupil.position.x = look[0] * 0.06; pupil.position.y = look[1] * 0.05;
    brow.position.y = 0.27 + mouth * 0.04 + (pose === 'shrug' ? 0.06 : 0) + (pose === 'point' ? 0.04 : 0); brow.rotation.z = s * (-0.08 + (pose === 'facepalm' ? 0.25 : 0));
  });
  // рот: открытие по громкости, улыбка в смехе
  const m = clamp(mouth * 1.25);
  U.inner.scale.set(1.25 - m * 0.3, 0.05 + m * 1.15, 0.4);
  U.lipD.position.y = -m * 0.12; U.lipU.position.y = m * 0.02; U.teeth.visible = m > 0.4 || pose === 'laugh'; U.teeth.scale.x = 0.8;
  U.mouth.scale.x = pose === 'laugh' ? 1.25 : 1;
}
