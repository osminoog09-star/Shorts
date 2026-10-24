import { iris, seg } from './engine.js';
import { s01, s02, s03, s04, s05, s06 } from './scenes_a.js';
import { s07, s08, s09, s10, s11, s12, thumb } from './scenes_b.js';
import { n1, n2, n3, n4, n5 } from './scenes_c.js';
import { n6, n7, n8, n9 } from './scenes_d.js';
export { thumb };

export const FN = { s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, n1, n2, n3, n4, n5, n6, n7, n8, n9 };
// цвет фона следующей сцены для шторки
export const BG = { s01: '#8cc8ff', s02: '#f3e9dd', s03: '#f3e9dd', s04: '#e8e4f3', s05: '#e6eef7', s06: '#f3e9dd', s07: '#e9e3f5', s08: '#e7e6f6', s09: '#e4eef3', s10: '#e9f2ec', s11: '#f3e9dd', s12: '#f3e9dd',
  n1: '#d8eaf3', n2: '#f3e9dd', n3: '#eee8f6', n4: '#f2ece4', n5: '#f3e9dd', n6: '#f1ebe2', n7: '#f3e6dc', n8: '#bfdbe8', n9: '#f3e9dd' };
export let SCENES = [];
export let DURATION = 0;
export async function init() {
  const tl = await (await fetch('./timeline.json')).json();
  window.WORDS = {};
  await Promise.all(tl.scenes.map(async (s) => { const j = await (await fetch(`/media/tts/antikythera/${s.id}.json`)).json(); window.WORDS[s.id] = j.words; }));
  SCENES = tl.scenes.map((s, i) => ({ id: s.id, fn: FN[s.id], dur: s.dur, start: s.start, next: tl.scenes[i + 1] ? BG[tl.scenes[i + 1].id] : null }));
  DURATION = tl.duration;
  return DURATION;
}
export function renderAt(t) {
  for (let i = 0; i < SCENES.length; i++) {
    const s = SCENES[i];
    if (t < s.start + s.dur || i === SCENES.length - 1) {
      const lt = t - s.start;
      s.fn(lt);
      if (s.next && s.id !== 's01') iris(seg(lt, s.dur - 0.7, s.dur), 960, 540, s.next);
      return;
    }
  }
}
