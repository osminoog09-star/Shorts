// «8 уровней ИИ» — painted 2.5D film engine (Claude, 07.11.2026). Each shot = painted keyframe (SDXL) displaced by its depth map
// into a relief mesh; the camera moves through it (real parallax + occlusion), plus living layers (snow, dust, glow, cursor), cards, quotes.
// Deterministic render(t). Timeline comes from timeline.json (shots + text) — the same file the mix uses.
import * as THREE from 'three';
const W = 1920, H = 1080;
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const TL = (await J(new URLSearchParams(location.search).get('tl') || 'timeline.json')) || { dur: 10, shots: [], text: [] };
window.DUR = TL.dur;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), lerp = (a, b, t) => a + (b - a) * t, seg = (t, a, b) => clamp((t - a) / (b - a));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const hash = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };

const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('c'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#000');
const camera = new THREE.PerspectiveCamera(36, W / H, .01, 50);
const loader = new THREE.TextureLoader();
const load = u => new Promise(r => loader.load(u, t => r(t), undefined, () => r(null)));

// relief material: depth displaces vertices toward the camera; slight edge stretching hidden by modest moves
const reliefMat = (tex, dep) => new THREE.ShaderMaterial({
  uniforms: { map: { value: tex }, dep: { value: dep }, amt: { value: .55 }, fade: { value: 1 }, glow: { value: 0 }, glowCol: { value: new THREE.Color('#7dff9a') } },
  vertexShader: `uniform sampler2D dep; uniform float amt; varying vec2 vUv; void main(){ vUv = uv; float d = texture2D(dep, uv).r; vec3 p = position; p.z += (d - .5) * amt; gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.); }`,
  fragmentShader: `uniform sampler2D map; uniform float fade, glow; uniform vec3 glowCol; varying vec2 vUv;
    void main(){ vec3 c = texture2D(map, vUv).rgb; float l = dot(c, vec3(.3,.59,.11)); c += glowCol * glow * smoothstep(.35, .9, l) * .25; gl_FragColor = vec4(c * fade, 1.); }`,
});
const geo = new THREE.PlaneGeometry(1.75 * 1.6, 1.6, 360, 206);   // image aspect 1344:768 = 1.75
const shots = [];
for (const s of TL.shots) {
  const [tex, dep] = await Promise.all([load(`assets/${s.img}.png`), load(`assets/${s.img}_depth.png`)]);
  if (tex) tex.colorSpace = THREE.NoColorSpace;
  const mesh = new THREE.Mesh(geo, reliefMat(tex, dep)); mesh.visible = false; scene.add(mesh); shots.push({ ...s, mesh });
}
// living layers
const snow = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: '#e9f2ff', size: .006, transparent: true, opacity: .85, depthWrite: false }));
{ const n = 1400, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { p[i * 3] = (hash(i) - .5) * 3; p[i * 3 + 1] = (hash(i + 7) - .5) * 1.8; p[i * 3 + 2] = .1 + hash(i + 13) * .9; } snow.geometry.setAttribute('position', new THREE.BufferAttribute(p, 3)); }
scene.add(snow);
const dust = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: '#ffd9a0', size: .004, transparent: true, opacity: .55, depthWrite: false, blending: THREE.AdditiveBlending }));
{ const n = 700, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { p[i * 3] = (hash(i * 3) - .5) * 2.6; p[i * 3 + 1] = (hash(i * 5) - .5) * 1.5; p[i * 3 + 2] = .2 + hash(i * 9) * .8; } dust.geometry.setAttribute('position', new THREE.BufferAttribute(p, 3)); }
scene.add(dust);
const cursor = new THREE.Mesh(new THREE.PlaneGeometry(.035, .05), new THREE.MeshBasicMaterial({ color: '#8dffa8', transparent: true, blending: THREE.AdditiveBlending })); cursor.visible = false; scene.add(cursor);

const subEl = document.getElementById('sub'), cardEl = document.getElementById('card'), quoteEl = document.getElementById('quote'), blackEl = document.getElementById('black');
let lastSub = '';
window.render = function (t) {
  // active shot + crossfade
  let cur = shots.find(s => t >= s.a && t < s.b) || shots[shots.length - 1];
  for (const s of shots) s.mesh.visible = false;
  if (!cur) { renderer.render(scene, camera); return; }
  const u = seg(t, cur.a, cur.b), m = cur.move || {};
  cur.mesh.visible = true;
  const fadeIn = ss(seg(t, cur.a, cur.a + (cur.xf ?? .6))), fadeOut = 1 - ss(seg(t, cur.b - (cur.xf ?? .6), cur.b));
  cur.mesh.material.uniforms.fade.value = Math.min(fadeIn, fadeOut);
  cur.mesh.material.uniforms.amt.value = m.depth ?? .55;
  cur.mesh.material.uniforms.glow.value = (m.glow || 0) * (.7 + .3 * Math.sin(t * 5));
  // camera: dolly (z), pan (x/y) and slight rotation — through the relief
  const e = ss(u);
  camera.position.set(lerp(m.x0 ?? 0, m.x1 ?? 0, e), lerp(m.y0 ?? 0, m.y1 ?? 0, e), lerp(m.z0 ?? 2.15, m.z1 ?? 1.9, e));
  camera.lookAt(lerp(m.tx0 ?? 0, m.tx1 ?? 0, e), lerp(m.ty0 ?? 0, m.ty1 ?? 0, e), 0); camera.rotation.z = lerp(m.r0 ?? 0, m.r1 ?? 0, e);
  // layers per shot
  snow.visible = !!cur.snow; if (snow.visible) { const p = snow.geometry.attributes.position; for (let i = 0; i < p.count; i++) { p.setY(i, ((hash(i + 7) * 1.8 - t * (.05 + hash(i) * .06)) % 1.8 + 1.8) % 1.8 - .9); p.setX(i, (hash(i) - .5) * 3 + Math.sin(t * .6 + i) * .02); } p.needsUpdate = true; }
  dust.visible = !!cur.dust; if (dust.visible) { const p = dust.geometry.attributes.position; for (let i = 0; i < p.count; i++) { p.setY(i, (hash(i * 5) - .5) * 1.5 + Math.sin(t * .3 + i) * .03); p.setX(i, (hash(i * 3) - .5) * 2.6 + Math.cos(t * .25 + i * 1.3) * .04); } p.needsUpdate = true; }
  cursor.visible = !!cur.cursor; if (cursor.visible) { cursor.position.set(cur.cursor[0], cur.cursor[1], cur.cursor[2] ?? .32); cursor.material.opacity = (Math.floor(t * 1.9) % 2 ? .95 : .08) * Math.min(fadeIn, fadeOut); }
  // text: title cards, quotes, subtitles
  let sub = '', card = null, quote = '';
  for (const x of TL.text) if (t >= x.t && t < x.t + x.d) { if (x.kind === 'card') card = x; else if (x.kind === 'quote') quote = x.text; else sub = x.text; }
  if (sub !== lastSub) { subEl.innerHTML = sub; lastSub = sub; }
  if (card) { const k = ss(seg(t, card.t, card.t + .5)) * (1 - ss(seg(t, card.t + card.d - .5, card.t + card.d))); cardEl.style.opacity = k.toFixed(3); cardEl.querySelector('b').textContent = card.text; cardEl.querySelector('small').textContent = card.small || ''; } else cardEl.style.opacity = 0;
  quoteEl.style.opacity = quote ? 1 : 0; if (quote) quoteEl.textContent = quote;
  blackEl.style.opacity = (TL.black || []).some(([a, b]) => t >= a && t < b) ? 1 : 0;
  renderer.render(scene, camera);
};
await document.fonts.load('800 40px Rubik'); await document.fonts.load('400 40px "Russo One"');
window.render(0); window.READY = true;
