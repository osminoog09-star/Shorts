import { iris } from './engine.js';
import * as CH from './chapters.js';
export { thumb } from './thumb.js';
const BG = '#f3e9dd';
export let CHAPS = [];
export let DURATION = 0;
const norm = (x) => x.toLowerCase().replace(/ё/g, 'е').replace(/[«»"',.!?:;—…()]/g, '');
export async function init() {
  const tl = await (await fetch('./timeline.json')).json();
  const W = {};
  await Promise.all(tl.chapters.flatMap((c) => c.lines).map(async (l) => { try { W[l.id] = (await (await fetch(`/media/tts/news_week44/${l.id}.json`)).json()).words; } catch (e) { W[l.id] = []; } }));
  CHAPS = tl.chapters.map((c) => {
    const byId = Object.fromEntries(c.lines.map((l) => [l.id, l]));
    const cue = (id, word, nth = 0, fb = 9999) => {
      const ln = byId[id]; if (!ln) return fb; const w = norm(word); let k = 0;
      for (const x of W[id] || []) {
        const parts = x.w.split(/\s+/).filter(Boolean); const Lx = x.w.length || 1; let pos = 0;
        for (const p of parts) { const a = x.w.indexOf(p, pos); pos = a + p.length;
          if (norm(p).startsWith(w)) { if (k === nth) return ln.s + x.start + (parts.length > 1 ? (a / Lx) * (x.end - x.start) : 0); k++; } }
      }
      return fb;
    };
    return { ...c, fn: CH[c.id], cue };
  });
  DURATION = tl.duration;
  return DURATION;
}
export function renderAt(t) {
  for (let k = 0; k < CHAPS.length; k++) {
    const c = CHAPS[k];
    if (t < c.start + c.dur || k === CHAPS.length - 1) {
      const ct = t - c.start;
      let i = -1; for (let j = 0; j < c.lines.length; j++) if (ct >= c.lines[j].s - 0.05) i = j;
      const line = i >= 0 ? c.lines[i] : c.lines[0];
      c.fn(ct, { ct, i, lt: ct - line.s, line, lines: c.lines, intro: c.intro, ch: c, cue: c.cue });
      if (k < CHAPS.length - 1) iris((ct - (c.dur - 0.6)) / 0.6, 960, 540, BG);
      if (k > 0 && ct < 0.6) iris(1 + ct / 0.6, 960, 540, BG);
      return;
    }
  }
}

// ───────── вертикальные нарезки (shorts/<имя>.json) ─────────
import { clear2d, ctx as C2, W as SW } from './engine.js';
import { hook as hookText, punch as punchText } from './news.js';
let SH = null;
export async function initShort(name) {
  await init();
  SH = await (await fetch(`./shorts/${name}.json`)).json();
  let t = 0; SH.pieces.forEach((p) => { p.at = t; p.len = p.kind === 'seg' ? p.to - p.from : p.dur; t += p.len; });
  return SH.duration;
}
export function renderShort(t) {
  let p = SH.pieces[0]; for (const q of SH.pieces) if (t >= q.at) p = q;
  const lt = t - p.at;
  if (p.kind === 'seg') { renderAt(p.from + lt); return; }
  renderAt(p.longAt + lt * 0.6); clear2d();
  if (p.kind === 'hook') hookText(p.lines, lt, 0.05, p.dur + 0.3);
  else {
    hookText([{ t: 'ПОЛНЫЙ ВЫПУСК', bg: '#2b2a3a', c: '#ffffff' }, { t: '— НА КАНАЛЕ', bg: '#ffdc7a' }], lt, 0.1, p.dur + 1, { y: 330, size: 76 });
    punchText('ПОДПИШИСЬ', SW / 2, 700, lt, p.sub ?? p.dur * 0.62, p.dur + 1, { size: 96 });
    punchText('СПАСИБО ЗА ЛАЙК ♥', SW / 2, 860, lt, (p.sub ?? p.dur * 0.62) + 1.1, p.dur + 1, { size: 58, bg: '#2b2a3a', rot: 0.03 });
  }
}
