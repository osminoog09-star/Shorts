// node render.mjs [fps] [from] [to] → frames.mp4 (без звука). Кадры: canvas → JPEG → ffmpeg stdin.
import {createRequire} from 'module';
const {chromium} = createRequire(import.meta.url)('playwright');
import {spawn} from 'child_process';
import http from 'http';
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const fps = +(process.argv[2] || 30), from = +(process.argv[3] || 0);
const types = {'.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.js': 'text/javascript'};
const srv = http.createServer((q, r) => {
  const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, {'content-type': types[path.extname(p)] || 'application/octet-stream'}); fs.createReadStream(p).pipe(r);
}).listen(0);
const port = srv.address().port;
const b = await chromium.launch();
const pg = await b.newPage({viewport: {width: 1080, height: 1920}});
pg.on('console', m => console.log('[page]', m.text()));
await pg.goto(`http://localhost:${port}/shorts/ai_blackmail/page.html`);
const info = await pg.evaluate(() => window.ready);
fs.writeFileSync(path.join(here, 'check.txt'), info.check.join('\n'));
fs.writeFileSync(path.join(here, 'events.json'), JSON.stringify(info.ev));
const to = +(process.argv[4] || info.dur);
const out = process.argv[5] || path.join(here, 'frames.mp4');
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out], {stdio: ['pipe', 'inherit', 'inherit']});
const N = Math.round((to - from) * fps); const t0 = Date.now();
for (let i = 0; i < N; i++) {
  const data = await pg.evaluate((t) => { window.draw(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, from + i / fps);
  const buf = Buffer.from(data.split(',')[1], 'base64');
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await b.close(); srv.close(); console.log('done', out);
