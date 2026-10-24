// node render.mjs --out out/frames.mp4 --fps 30 [--from 0 --to 14] [--stills 1,3.5,7]
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';

const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith('--') ? [...a, [v.slice(2), arr[i + 1]]] : a), []));
const fps = +(args.fps || 30);
const root = path.dirname(new URL(import.meta.url).pathname);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.woff2': 'font/woff2', '.woff': 'font/woff', '.png': 'image/png', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
}).listen(0);
const port = srv.address().port;
const exe = args.browser || process.env.BROWSER || fs.readFileSync(path.join(root, '../../studio/.browser'), 'utf8').trim();
const browser = await chromium.launch({ executablePath: exe, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('console', (m) => { if (m.type() === 'error') console.error('[page]', m.text()); });
page.on('pageerror', (e) => console.error('[pageerror]', e.message));
await page.goto(`http://127.0.0.1:${port}/index.html`);
await page.waitForFunction('window.READY === true', null, { timeout: 60000 });
const dur = await page.evaluate('window.DURATION');
const stage = await page.$('#stage');

async function frameAt(t) {
  await page.evaluate((tt) => window.renderAt(tt), t);
  return stage.screenshot({ type: 'jpeg', quality: 93 });
}

if (args.stills) {
  fs.mkdirSync(path.join(root, 'out'), { recursive: true });
  for (const s of args.stills.split(',')) {
    const t0 = Date.now(); const buf = await frameAt(+s);
    fs.writeFileSync(path.join(root, `out/still_${s}.jpg`), buf); console.log('still', s, Date.now() - t0, 'ms');
  }
} else {
  const from = +(args.from || 0), to = +(args.to || dur);
  const n0 = args.f0 != null ? +args.f0 : Math.round(from * fps), n1 = args.f1 != null ? Math.min(+args.f1, Math.round(dur * fps)) : Math.round(to * fps);
  const out = args.out || 'out/video.mp4';
  fs.mkdirSync(path.dirname(path.join(root, out)), { recursive: true });
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(fps), path.join(root, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = n0; i < n1; i++) {
    const buf = await frameAt(i / fps);
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if ((i - n0) % 30 === 0) { const el = (Date.now() - t0) / 1000; console.log(`frame ${i}/${n1} ${(el / Math.max(1, i - n0 + 1)).toFixed(2)}s/f`); }
  }
  ff.stdin.end(); await new Promise((r) => ff.on('close', r));
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0), 's');
}
await browser.close(); srv.close();
