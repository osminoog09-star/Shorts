// Вертикальные нарезки (Shorts) из сцен основного фильма. Запуск: index.html?portrait&short=<name>
import { iris, seg, clear2d, ctx, title, pill, W, H, CSS, easeOut, clamp } from './engine.js';
import { init as filmInit, FN as FN0, BG } from './film.js';
import { host1, hostShot, hostPiP } from './scenes_host.js';
import { title as T2, pill as P2 } from './engine.js';
const FN = { ...FN0, host1, hostTest: (t) => hostShot(t, { pose: ['talk','point','facepalm','laugh','wave'][Math.floor(t / 2) % 5], prev: 'rest', k: (t % 2) / 0.5, mouth: Math.abs(Math.sin(t * 9)) * 0.8 }) };

let TL = null;
export async function init(name) {
  await filmInit(); // слова и сцены основного фильма
  TL = await (await fetch(`./shorts/${name}.json`)).json();
  if (TL.beats) window.HOSTBEATS = TL.beats;
  return TL.duration;
}

function hookText(lines, lt) {
  const g = ctx.createLinearGradient(0, 0, 0, 900); g.addColorStop(0, 'rgba(246,239,230,0.95)'); g.addColorStop(0.75, 'rgba(246,239,230,0.85)'); g.addColorStop(1, 'rgba(246,239,230,0)');
  ctx.save(); ctx.globalAlpha = clamp(lt / 0.3); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 900); ctx.restore();
  // крупный хук сверху (координаты 1920×1080 — движок сам переносит в вертикаль)
  title(lines[0], 960, 230, lt, 0.15, { size: 130, color: CSS.ink });
  if (lines[1]) title(lines[1], 960, 400, lt, 0.45, { size: 130, color: '#7a63e6' });
}

function outro(lt, d) {
  const k = easeOut(seg(lt, 0, 0.6));
  ctx.save(); ctx.globalAlpha = 0.72 * k; ctx.fillStyle = '#f6efe6'; ctx.fillRect(0, 0, W, H); ctx.restore();
  title('полная история', 960, 260, lt, 0.2, { size: 120 });
  title('на канале', 960, 390, lt, 0.45, { size: 120, color: '#7a63e6' });
  pill('Антикитерский механизм · 10 минут', 960, 960, lt, 0.9, { size: 60, dot: CSS.gold });
}

export function renderAt(t) {
  const P = TL.parts;
  let i = P.findIndex((p) => t < p.start + p.dur); if (i < 0) i = P.length - 1;
  const p = P[i], lt = t - p.start;
  const sid = p.id || p.scene;
  if (TL.name === 'host_v2') return TL.pip ? renderHostPiP(t) : renderHostV2(t);
  if (p.type === 'scene') FN[sid](p.local + lt);
  else if (p.type === 'vo') { FN[sid](p.local + lt * 0.6); if (p.clear) { clear2d(); hookText(p.text, lt); } }
  else if (p.type === 'outro') { FN[sid](p.local + lt * 0.5); clear2d(); outro(lt, p.dur); }
  if (i === 0 && p.type !== 'scene') iris(1 + seg(lt, 0, 0.5), 960, 540, BG[sid] || CSS.cream);
  const nx = P[i + 1];
  if (nx && nx.type !== 'outro') { const ns = nx.id || nx.scene; iris(seg(lt, p.dur - 0.6, p.dur), 960, 540, BG[ns] || CSS.cream); }
}

// Формат «ведущий + сцены»: ведущий в кадре только на хуке/реакции/финале, остальное — полноэкранные 3D-сцены
function renderHostV2(t) {
  const P = TL.parts; let i = P.findIndex((p) => t < p.end); if (i < 0) i = P.length - 1;
  const p = P[i], lt = t - p.start, f = Math.floor(t * 30);
  const mouth = (TL.mouth || [])[f] || 0;
  if (p.type === 'host') {
    const pose = p.pose === 'facepalm' && lt > 1.6 ? 'laugh' : p.pose;
    const prev = p.pose === 'facepalm' && lt > 1.6 ? 'facepalm' : p.prev;
    const k = p.pose === 'facepalm' && lt > 1.6 ? (lt - 1.6) / 0.35 : lt / 0.35;
    hostShot(t, { pose, prev, k, mouth: pose === 'laugh' ? Math.max(mouth, 0.3) : mouth, push: p.push + lt * 0.05 });
  } else {
    FN[p.id](p.local + lt);
  }
  // тёмная полоса сверху под титры (читаемость)
  { const g = ctx.createLinearGradient(0, 0, 0, 760); g.addColorStop(0, 'rgba(12,14,30,0.78)'); g.addColorStop(0.6, 'rgba(12,14,30,0.45)'); g.addColorStop(1, 'rgba(12,14,30,0)'); ctx.save(); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 760); ctx.restore(); }
  // титры
  if (p.text) T2(p.text[0], 960, p.type === 'host' ? 250 : 230, lt, 0.1, { size: p.text[0].length > 16 ? 96 : 130, color: p.text[1] });
  if (p.cta) {
    P2('ПОДПИСАТЬСЯ', 960, 360, lt, 0.4, { size: 72, bg: '#ff2d3d', color: '#ffffff', weight: 900 });
    T2('спасибо за просмотр и лайк', 960, 520, lt, 0.9, { size: 64, color: '#ffffff' });
  }
  P2('M1 · ИНЖЕНЕРИЯ ДРЕВНОСТИ', 960, 1075, 1, 0, { size: 30, bg: 'rgba(20,24,48,0.75)', color: '#cfe8ff' });
  // короткая вспышка на склейке
  if (lt < 0.08 && i > 0) { ctx.save(); ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}

// Формат «рассказчик в окошке»: фон — непрерывные 3D-сцены, ведущий маленьким окном слева внизу (вне зоны кнопок Shorts)
function renderHostPiP(t) {
  const P = TL.parts; let i = P.findIndex((p) => t < p.end); if (i < 0) i = P.length - 1;
  const p = P[i], lt = t - p.start, f = Math.floor(t * 30);
  const mouth = (TL.mouth || [])[f] || 0;
  FN.host1(t);
  { const g = ctx.createLinearGradient(0, 0, 0, 760); g.addColorStop(0, 'rgba(12,14,30,0.78)'); g.addColorStop(0.6, 'rgba(12,14,30,0.45)'); g.addColorStop(1, 'rgba(12,14,30,0)'); ctx.save(); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 760); ctx.restore(); }
  const pose = t < 2.6 ? 'point' : t < 17.2 ? 'talk' : t < 19.0 ? 'facepalm' : t < 20.0 ? 'laugh' : 'wave';
  const starts = { point: 0, talk: 2.6, facepalm: 17.2, laugh: 19.0, wave: 20.0 };
  const prevOf = { point: 'rest', talk: 'point', facepalm: 'talk', laugh: 'facepalm', wave: 'laugh' };
  const big = t > 17.2 && t < 20.0 ? 1.3 : 1;
  const bw = 360 * big, bh = 440 * big;
  hostPiP(t, { pose, prev: prevOf[pose], k: (t - starts[pose]) / 0.35, mouth: pose === 'laugh' ? Math.max(mouth, 0.3) : mouth, viseme: TL.visemes ? (TL.visemes[f] || 'X') : null, pop: easeOut(seg(t, 0.15, 0.6)), box: { x: 40, y: 1530 - bh, w: bw, h: bh } });
  if (p.text) title(p.text[0], 960, 230, lt, 0.1, { size: p.text[0].length > 16 ? 96 : 130, color: p.text[1] });
  if (p.cta) { pill('ПОДПИСАТЬСЯ', 960, 360, lt, 0.4, { size: 72, bg: '#ff2d3d', color: '#ffffff', weight: 900 }); title('спасибо за просмотр и лайк', 960, 520, lt, 0.9, { size: 64, color: '#ffffff' }); }
  if (lt < 0.08 && i > 0 && P[i - 1].type === 'scene' && p.type === 'scene') { ctx.save(); ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}
