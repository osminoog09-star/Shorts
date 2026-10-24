// Вертикальные нарезки (Shorts) из сцен основного фильма. Запуск: index.html?portrait&short=<name>
import { iris, seg, clear2d, ctx, title, pill, W, H, CSS, easeOut, clamp } from './engine.js';
import { init as filmInit, FN as FN0, BG } from './film.js';
import { host1, hostShot } from './scenes_host.js';
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
  if (p.type === 'scene') FN[sid](p.local + lt);
  else if (p.type === 'vo') { FN[sid](p.local + lt * 0.6); if (p.clear) { clear2d(); hookText(p.text, lt); } }
  else if (p.type === 'outro') { FN[sid](p.local + lt * 0.5); clear2d(); outro(lt, p.dur); }
  if (i === 0 && p.type !== 'scene') iris(1 + seg(lt, 0, 0.5), 960, 540, BG[sid] || CSS.cream);
  const nx = P[i + 1];
  if (nx && nx.type !== 'outro') { const ns = nx.id || nx.scene; iris(seg(lt, p.dur - 0.6, p.dur), 960, 540, BG[ns] || CSS.cream); }
}
