import { iris, seg } from './engine.js';
import { s01, s02, s03, s04, s05, s06 } from './scenes_a.js';
import { s07, s08, s09, s10, s11, s12 } from './scenes_b.js';

// Длительности = 0.6 (вход) + длина реплики + 1.1 (хвост), реплика начинается в 0.6
export const SCENES = [
  { fn: s01, voice: 's01', dur: 17.7, bg: '#8cc8ff' },
  { fn: s02, voice: 's02', dur: 27.5, bg: '#f3e9dd' },
  { fn: s03, voice: 's03', dur: 19.8, bg: '#f3e9dd' },
  { fn: s04, voice: 's04', dur: 17.3, bg: '#e8e4f3' },
  { fn: s05, voice: 's05', dur: 26.6, bg: '#e6eef7' },
  { fn: s06, voice: 's06', dur: 32.4, bg: '#f3e9dd' },
  { fn: s07, voice: 's07', dur: 37.7, bg: '#e9e3f5' },
  { fn: s08, voice: 's08', dur: 26.3, bg: '#e7e6f6' },
  { fn: s09, voice: 's09', dur: 30.3, bg: '#e4eef3' },
  { fn: s10, voice: 's10', dur: 20.6, bg: '#e9f2ec' },
  { fn: s11, voice: 's11', dur: 24.6, bg: '#f3e9dd' },
  { fn: s12, voice: 's12', dur: 32.0, bg: null },
];
export const VO = 0.6;
export const DURATION = SCENES.reduce((a, s) => a + s.dur, 0);
export function sceneStarts() { let acc = 0; return SCENES.map((s) => { const a = acc; acc += s.dur; return a; }); }
export function renderAt(t) {
  let acc = 0;
  for (let i = 0; i < SCENES.length; i++) {
    const s = SCENES[i];
    if (t < acc + s.dur || i === SCENES.length - 1) {
      const lt = t - acc;
      s.fn(lt);
      // закрытие шторкой цвета следующей сцены (кроме s01 и s02 — у них своё)
      if (s.bg && i > 1) iris(seg(lt, s.dur - 0.7, s.dur), 960, 540, s.bg);
      if (i === 1) iris(seg(lt, s.dur - 0.7, s.dur), 960, 540, s.bg);
      return;
    }
    acc += s.dur;
  }
}
