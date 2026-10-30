// Возобновляемый покадровый рендер композиции через движок huashu-motion (openFilm из skills/ext/huashu-motion).
// Нужен, когда полный `om render` не укладывается в лимит времени: кадры пишутся в JPEG по одному, готовые пропускаются.
//   node tools/render_frames.mjs <from> <to> [outDir]      (номера кадров, 30 fps, to — не включительно)
import { existsSync, mkdirSync, writeFileSync, renameSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url)), film = resolve(here, '..');
const { openFilm } = await import(resolve(film, '../../../skills/ext/huashu-motion/cli/lib/capture.js'));
const [a, b] = [Number(process.argv[2]), Number(process.argv[3])];
const out = resolve(process.argv[4] || join(film, 'out/frames'));
mkdirSync(out, { recursive: true });
const f = await openFilm(join(film, 'index.html'), { shotFormat: 'jpeg', html: process.env.NOAA ? (await import('node:fs')).readFileSync(join(film, 'index.html'), 'utf8').replace('<head>', '<head><script>window.__FASTAA=1</script>') : null });
const t0 = Date.now(); let n = 0;
try {
  for (let i = a; i < b; i++) {
    const p = join(out, `f${String(i).padStart(5, '0')}.jpg`);
    if (existsSync(p)) continue;
    await f.seek(i / 30);
    const img = await f.shot({ format: 'jpeg', quality: 93 });
    writeFileSync(p + '.tmp', img); renameSync(p + '.tmp', p); n++;
    if (n % 25 === 0) console.log(`frame ${i}  ${((Date.now() - t0) / n / 1000).toFixed(2)} s/frame`);
  }
} finally { await f.close(); }
console.log(`done ${a}-${b}: ${n} frames, ${((Date.now() - t0) / Math.max(1, n) / 1000).toFixed(2)} s/frame`);
