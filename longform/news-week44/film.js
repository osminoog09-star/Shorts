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
