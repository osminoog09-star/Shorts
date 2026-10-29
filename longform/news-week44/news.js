// 2D-оверлеи выпуска: плашка главы, говорящий, карточки фактов, цифры, цитаты, источники
import { ctx, W, H, CSS, clamp, lerp, seg, easeOut, easeIn, easeInOut, spring } from './engine.js';

export const INK = '#2b2a3a', RED = '#e8706a', LAV = '#7a63e6', MINT = '#2fae86', SKY = '#3f8fd8';
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function inOut(t, t0, t1, a = 0.9, b = 0.45) { const k = spring(seg(t, t0, t0 + a) * 1.2, 8, 6), fo = t1 == null ? 0 : easeIn(seg(t, t1 - b, t1)); return { k, a: clamp(k) * (1 - fo), vis: k > 0.001 && fo < 1 }; }
function wrap(text, maxW) { const ws = text.split(' '); const L = []; let cur = ''; for (const w of ws) { const tt = cur ? cur + ' ' + w : w; if (ctx.measureText(tt).width > maxW && cur) { L.push(cur); cur = w; } else cur = tt; } if (cur) L.push(cur); return L; }

// Постоянная плашка: «НОВОСТИ НЕДЕЛИ · 3/8 · Название»
export function badge(n, total, name, t, t0) {
  const { a, k, vis } = inOut(t, t0, null); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(-40 * (1 - clamp(k)), 0);
  ctx.font = '700 26px "Rubik"'; const top = n ? `НОВОСТИ НЕДЕЛИ · ${n}/${total}` : 'НОВОСТИ НЕДЕЛИ'; const tw = ctx.measureText(top).width;
  ctx.font = '900 40px "Rubik"'; const nw = ctx.measureText(name).width;
  const w = Math.max(tw, nw) + 76;
  ctx.shadowColor = 'rgba(40,30,70,0.18)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
  rr(56, 44, w, 108, 26); ctx.fillStyle = 'rgba(255,255,255,0.93)'; ctx.fill(); ctx.shadowColor = 'transparent';
  rr(56, 44, 12, 108, 6); ctx.fillStyle = RED; ctx.fill();
  ctx.fillStyle = LAV; ctx.font = '700 26px "Rubik"'; ctx.fillText(top, 92, 86);
  ctx.fillStyle = INK; ctx.font = '900 40px "Rubik"'; ctx.fillText(name, 90, 132);
  ctx.restore();
}

// Заставка главы: крупный номер + название по центру
export function chapterCard(n, name, t, t0, t1) {
  const { a, k, vis } = inOut(t, t0, t1, 0.8, 0.4); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = 'rgba(30,26,52,0.38)'; ctx.fillRect(0, 0, W, H);
  const s = lerp(0.85, 1, clamp(k));
  ctx.translate(W / 2, H / 2); ctx.scale(s, s);
  ctx.textAlign = 'center';
  if (n) { ctx.font = '900 210px "Rubik"'; ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillText(String(n).padStart(2, '0'), 0, 40); }
  ctx.font = '700 40px "Rubik"'; ctx.fillStyle = '#ffdc7a'; ctx.fillText(n ? `НОВОСТЬ ${n} ИЗ 8` : 'НОВОСТИ НЕДЕЛИ', 0, -70);
  ctx.font = '900 92px "Rubik"'; ctx.fillStyle = '#ffffff';
  const L = wrap(name.toUpperCase(), 1500); L.forEach((l, i) => ctx.fillText(l, 0, 40 + i * 100));
  ctx.restore();
}

// Кто говорит: левый низ, имя + звуковые полоски
export function speaker(sp, talking, t, t0) {
  const { a, vis } = inOut(t, t0, null, 0.5); if (!vis) return;
  const name = sp === 'S' ? 'СВЕТА' : 'ДИМА', col = sp === 'S' ? '#ff98b1' : '#8cc8ff';
  ctx.save(); ctx.globalAlpha = a * 0.96;
  ctx.font = '800 30px "Rubik"'; const tw = ctx.measureText(name).width; const w = tw + 140;
  rr(56, H - 116, w, 64, 32); ctx.fillStyle = 'rgba(43,42,58,0.78)'; ctx.fill();
  ctx.beginPath(); ctx.arc(90, H - 84, 18, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill();
  ctx.fillStyle = '#fff'; ctx.fillText(name, 120, H - 73);
  for (let i = 0; i < 4; i++) { const h = talking ? 8 + 18 * Math.abs(Math.sin(t * (7 + i * 2.3) + i)) : 6; rr(132 + tw + i * 12, H - 84 - h / 2, 7, h, 3.5); ctx.fillStyle = col; ctx.fill(); }
  ctx.restore();
}

// Карточка факта: заголовок-метка + основной текст (до 3 строк)
export function fact(label, text, x, y, t, t0, t1, { w = 760, color = RED, size = 52, align = 'left' } = {}) {
  const { a, k, vis } = inOut(t, t0, t1); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a;
  ctx.font = `800 ${size}px "Rubik"`; const L = wrap(text, w - 90);
  const h = 84 + L.length * size * 1.18 + 26;
  const x0 = align === 'right' ? x - w : x;
  ctx.translate(0, 30 * (1 - clamp(k)));
  ctx.shadowColor = 'rgba(40,30,70,0.2)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  rr(x0, y, w, h, 30); ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fill(); ctx.shadowColor = 'transparent';
  rr(x0 + 40, y + 30, 0, 0, 0);
  ctx.font = '800 26px "Rubik"'; const lw = ctx.measureText(label).width + 36; rr(x0 + 40, y + 26, lw, 42, 21); ctx.fillStyle = color; ctx.fill();
  ctx.fillStyle = '#fff'; ctx.fillText(label, x0 + 58, y + 56);
  ctx.fillStyle = INK; ctx.font = `800 ${size}px "Rubik"`;
  L.forEach((l, i) => { const kk = easeOut(seg(t, t0 + 0.2 + i * 0.12, t0 + 0.6 + i * 0.12)); ctx.globalAlpha = a * kk; ctx.fillText(l, x0 + 42, y + 84 + size * 0.95 + i * size * 1.18); });
  ctx.restore();
}

// Большая цифра с подписью (счётчик набегает)
export function bigNum(value, suffix, label, x, y, t, t0, t1, { color = INK, size = 190, prefix = '', dec = 0, from = 0 } = {}) {
  const { a, k, vis } = inOut(t, t0, t1); if (!vis) return;
  const run = easeOut(seg(t, t0, t0 + 1.2)); const v = lerp(from, value, run);
  const txt = prefix + (dec ? v.toFixed(dec).replace('.', ',') : Math.round(v).toLocaleString('ru-RU')) + suffix;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y + 24 * (1 - clamp(k)));
  ctx.font = `900 ${size}px "Rubik"`; const tw = ctx.measureText(txt).width;
  ctx.font = '700 40px "Rubik"'; const L = wrap(label, Math.max(tw, 620)); const lw = Math.max(...L.map((l) => ctx.measureText(l).width));
  const w = Math.max(tw, lw) + 100, h = size * 1.05 + L.length * 50 + 60;
  ctx.shadowColor = 'rgba(40,30,70,0.2)'; ctx.shadowBlur = 44; ctx.shadowOffsetY = 16;
  rr(-50, -size * 0.95 - 20, w, h, 36); ctx.fillStyle = 'rgba(255,252,246,0.95)'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = color; ctx.font = `900 ${size}px "Rubik"`; if ('letterSpacing' in ctx) ctx.letterSpacing = '-4px'; ctx.fillText(txt, 0, 0);
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
  ctx.fillStyle = '#5a5870'; ctx.font = '700 40px "Rubik"'; L.forEach((l, i) => ctx.fillText(l, 4, 64 + i * 50));
  ctx.restore();
}

// Цитата
export function quote(text, who, x, y, t, t0, t1, { w = 900, size = 46 } = {}) {
  const { a, k, vis } = inOut(t, t0, t1); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a; ctx.font = `600 ${size}px "Rubik"`;
  const L = wrap(text, w - 140); const h = L.length * size * 1.3 + 150;
  ctx.translate(x, y + 30 * (1 - clamp(k)));
  ctx.shadowColor = 'rgba(40,30,70,0.2)'; ctx.shadowBlur = 44; ctx.shadowOffsetY = 16;
  rr(0, 0, w, h, 34); ctx.fillStyle = 'rgba(255,252,246,0.96)'; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#e9b97f'; ctx.font = '900 140px "NSerif"'; ctx.fillText('«', 24, 116);
  ctx.fillStyle = INK; ctx.font = `600 ${size}px "Rubik"`;
  L.forEach((l, i) => { const kk = easeOut(seg(t, t0 + 0.3 + i * 0.22, t0 + 0.8 + i * 0.22)); ctx.globalAlpha = a * kk; ctx.fillText(l, 76, 88 + i * size * 1.3); });
  ctx.globalAlpha = a; ctx.fillStyle = LAV; ctx.font = '700 34px "Rubik"'; ctx.fillText('— ' + who, 76, 88 + L.length * size * 1.3 + 26);
  ctx.restore();
}

// Список пунктов с галочками/крестиками
export function checklist(items, x, y, t, t0, t1, { w = 760, size = 40 } = {}) {
  const { a, vis } = inOut(t, t0, t1); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a;
  const h = items.length * (size * 1.6) + 60;
  ctx.shadowColor = 'rgba(40,30,70,0.2)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  rr(x, y, w, h, 30); ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fill(); ctx.shadowColor = 'transparent';
  items.forEach(([ok, txt], i) => {
    const kk = spring(seg(t, t0 + 0.25 + i * 0.35, t0 + 0.95 + i * 0.35) * 1.2, 8, 6); if (kk <= 0) return;
    const yy = y + 30 + i * size * 1.6 + size * 0.8;
    ctx.globalAlpha = a * clamp(kk);
    ctx.beginPath(); ctx.arc(x + 54, yy, size * 0.48, 0, Math.PI * 2); ctx.fillStyle = ok === true ? MINT : ok === false ? RED : '#c9a227'; ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = `900 ${size * 0.62}px "Rubik"`; ctx.textAlign = 'center'; ctx.fillText(ok === true ? '✓' : ok === false ? '✕' : '?', x + 54, yy + size * 0.22); ctx.textAlign = 'left';
    ctx.fillStyle = INK; ctx.font = `700 ${size}px "Rubik"`; ctx.fillText(txt, x + 100, yy + size * 0.35);
  });
  ctx.restore();
}

// Источник (мелкая плашка над говорящим)
export function source(text, t, t0, t1) {
  const { a, vis } = inOut(t, t0, t1, 0.5, 0.3); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a * 0.92; ctx.font = '600 24px "Rubik"';
  const s = 'Источник: ' + text; const w = ctx.measureText(s).width + 40;
  rr(56, H - 170, w, 40, 20); ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.fill();
  ctx.fillStyle = '#5a5870'; ctx.fillText(s, 76, H - 142); ctx.restore();
}

// Крупное слово-удар по центру сверху (кинетика)
export function punch(text, x, y, t, t0, t1, { size = 120, color = '#ffffff', bg = RED, rot = -0.04 } = {}) {
  const { a, k, vis } = inOut(t, t0, t1, 0.6, 0.35); if (!vis) return;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.rotate(rot); const s = lerp(1.6, 1, clamp(k)); ctx.scale(s, s);
  ctx.font = `900 ${size}px "Rubik"`; const tw = ctx.measureText(text).width;
  ctx.shadowColor = 'rgba(40,30,70,0.25)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  rr(-tw / 2 - 40, -size * 0.85, tw + 80, size * 1.2, 26); ctx.fillStyle = bg; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.fillText(text, 0, size * 0.25);
  ctx.restore();
}
