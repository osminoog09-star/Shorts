import { iris, seg } from './engine.js';
import { s01, s02, s03, s04, s04b, s05, s06, s07 } from './scenes_a.js';
import { s08, s09, s10, s11, s12, s13, s14 } from './scenes_b.js';
import { thumb } from './thumb.js';
import { s03b, s04c, s05b, s06b, s06c, s07b, s10c, s12b, s13b, s13c } from './scenes_c.js';
export { thumb };
export const FN = { s01, s02, s03, s03b, s04, s04b, s04c, s05, s05b, s06, s06b, s06c, s07, s07b, s08, s09, s10, s10c, s11, s12, s12b, s13, s13b, s13c, s14 };
const BG = '#f3e9dd';
export let SCENES = [];
export let DURATION = 0;
export async function init() {
  const tl = await (await fetch('./timeline.json')).json();
  window.WORDS = {}; window.VDUR = {}; tl.scenes.forEach((s) => (window.VDUR[s.id] = s.voice));
  await Promise.all(tl.scenes.map(async (s) => { try { const j = await (await fetch(`/media/tts/roman_concrete/${s.id}.json`)).json(); window.WORDS[s.id] = j.words; } catch (e) { window.WORDS[s.id] = []; } }));
  SCENES = tl.scenes.map((s, i) => ({ id: s.id, fn: FN[s.id], dur: s.dur, start: s.start, last: i === tl.scenes.length - 1 }));
  DURATION = tl.duration;
  return DURATION;
}
export function renderAt(t) {
  for (let i = 0; i < SCENES.length; i++) {
    const s = SCENES[i];
    if (t < s.start + s.dur || i === SCENES.length - 1) {
      const lt = t - s.start;
      s.fn(lt);
      if (!s.last) iris(seg(lt, s.dur - 0.7, s.dur), 960, 540, BG);
      if (i > 0 && lt < 0.7) iris(1 + seg(lt, 0, 0.7), 960, 540, BG);
      return;
    }
  }
}
