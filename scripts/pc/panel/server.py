#!/usr/bin/env python3
"""M1lash · живая панель производства (Claude, 07.11.2026). Только локально, только чтение файлов.
  py -3.11 scripts/pc/panel/server.py [--project longform/oumuamua] [--work C:\\M1lash\\Работа\\oumuamua] [--final C:\\M1lash\\Готово\\oumuamua_film.mp4] [--port 8790]
Открыть: http://127.0.0.1:8790"""
import argparse, json, re, subprocess, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[2]
ap = argparse.ArgumentParser()
ap.add_argument('--project', default='longform/oumuamua'); ap.add_argument('--work', default=r'C:\M1lash\Работа\oumuamua')
ap.add_argument('--final', default=r'C:\M1lash\Готово\oumuamua_film.mp4'); ap.add_argument('--port', type=int, default=8790)
A = ap.parse_args()
PROJ = (REPO / A.project).resolve(); WORK = Path(A.work); FINAL = Path(A.final); THUMBS = WORK / 'panel_thumbs'; THUMBS.mkdir(parents=True, exist_ok=True)
T0 = time.time(); HIST = []; LOCK = threading.Lock()


def read_text(p):
    b = p.read_bytes()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'): return b.decode('utf-16', 'ignore')
    return b.decode('utf-8', 'ignore')


def gpu():
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'],
                             capture_output=True, text=True, timeout=10).stdout.strip().split(', ')
        n = lambda x: round(float(x))
        return {'name': out[0], 'util': n(out[1]), 'mem': n(out[2]), 'mem_total': n(out[3]), 'temp': n(out[4])}
    except Exception: return None


def status():
    chapters, beats_all, shots_all = [], [], []
    for f in sorted((PROJ / 'levels').glob('*.json')):
        j = json.loads(f.read_text(encoding='utf-8')); cid = j['id']
        v = sum((WORK / 'voice' / cid / f"{b['id']}.wav").exists() for b in j['beats'])
        fr = sum((PROJ / 'assets' / f"{s['id']}.png").exists() for s in j['shots'])
        card = j.get('card') or ['Холодный старт', '']
        chapters.append({'id': cid, 'title': card[0], 'sub': card[1], 'beats': len(j['beats']), 'voice': v, 'shots': len(j['shots']), 'frames': fr,
                         'words': sum(len(b['text'].split()) for b in j['beats'])})
        beats_all += j['beats']; shots_all += j['shots']
    imgs = [p for p in (PROJ / 'assets').glob('*.png') if not p.stem.endswith('_depth')]
    depth = len(list((PROJ / 'assets').glob('*_depth.png')))
    latest = sorted(imgs, key=lambda p: p.stat().st_mtime, reverse=True)[:12]
    prompts = {s['id']: s['prompt'] for s in shots_all}
    # voice lines with ASR score from builder logs
    lines = []
    for lg in sorted(WORK.glob('voice*.log'), key=lambda p: p.stat().st_mtime):
        for l in read_text(lg).splitlines():
            m = re.match(r'^(c\d+b\d+\w?)\s+([\d.]+)\s+\|\s+(.*)$', l.strip())
            if m: lines.append({'id': m[1], 'sim': float(m[2]), 'asr': m[3][:140]})
    failed = sum(1 for lg in WORK.glob('voice*.log') for l in read_text(lg).splitlines() if 'FAILED' in l)
    # render progress (workers print "wN done/total"), only a log newer than the panel start counts as live
    rd = rt = 0; rlog = WORK / 'render_full.log'; render_done = False; rlines = []
    if rlog.exists():
        last = {}
        rlines = read_text(rlog).splitlines()
        for l in rlines[-600:]:
            m = re.match(r'^(w\d+)\s+(\d+)/(\d+)', l.strip())
            if m: last[m[1]] = (int(m[2]), int(m[3]))
            if l.startswith('done '): render_done = True
        rd = sum(a for a, b in last.values()); rt = sum(b for a, b in last.values())
        if render_done and rt: rd = rt
    fin = FINAL.exists() and FINAL.stat().st_mtime > (rlog.stat().st_mtime if rlog.exists() else 0)
    tl = json.loads((PROJ / 'timeline.json').read_text(encoding='utf-8')) if (PROJ / 'timeline.json').exists() else {}
    st = {
        't': time.time(), 'uptime': time.time() - T0, 'project': PROJ.name,
        'voice': {'done': sum(c['voice'] for c in chapters), 'total': len(beats_all), 'failed': failed, 'lines': lines[-10:][::-1]},
        'frames': {'done': len(imgs), 'total': len(shots_all), 'depth': depth,
                   'latest': [{'id': p.stem, 'prompt': prompts.get(p.stem, '')[:120], 'age': time.time() - p.stat().st_mtime, 'depth': (p.parent / f'{p.stem}_depth.png').exists()} for p in latest]},
        'render': {'done': rd, 'total': rt, 'finished': render_done, 'log': [l for l in rlines[-6:]]},
        'final': {'ready': bool(fin), 'path': str(FINAL), 'mb': round(FINAL.stat().st_size / 1e6, 1) if FINAL.exists() else 0},
        'chapters': chapters, 'film_dur': tl.get('dur'), 'words': sum(c['words'] for c in chapters), 'gpu': gpu(),
    }
    with LOCK:
        HIST.append({'t': st['t'], 'f': st['frames']['done'], 'v': st['voice']['done'], 'r': rd})
        del HIST[:-600]; st['hist'] = HIST[-120:]
    return st


def thumb(name):
    src = PROJ / 'assets' / f'{name}.png'; dst = THUMBS / f'{name}.jpg'
    if not src.exists(): return None
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        from PIL import Image
        im = Image.open(src).convert('RGB'); im.thumbnail((420, 240)); im.save(dst, quality=82)
    return dst


def background():
    dst = THUMBS / '_bg.jpg'
    if not dst.exists():
        from PIL import Image, ImageFilter
        cands = sorted(p for p in (PROJ / 'assets').glob('*.png') if not p.stem.endswith('_depth'))
        if not cands: return None
        im = Image.open(cands[min(len(cands) - 1, 6)]).convert('RGB').resize((1600, 914)).filter(ImageFilter.GaussianBlur(28)); im.save(dst, quality=80)
    return dst


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype):
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p = self.path.split('?')[0]
        if p in ('/', '/index.html'): return self.send(200, (HERE / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if p == '/api/status':
            try: return self.send(200, json.dumps(status(), ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except Exception as e: return self.send(500, json.dumps({'error': str(e)}).encode(), 'application/json')
        if p == '/bg.jpg':
            f = background(); return self.send(200, f.read_bytes(), 'image/jpeg') if f else self.send(404, b'', 'text/plain')
        m = re.fullmatch(r'/thumb/([\w-]+)\.jpg', p)
        if m:
            f = thumb(m[1]); return self.send(200, f.read_bytes(), 'image/jpeg') if f else self.send(404, b'', 'text/plain')
        self.send(404, b'not found', 'text/plain')


if __name__ == '__main__':
    print(f'M1lash panel → http://127.0.0.1:{A.port}  ({PROJ})', flush=True)
    ThreadingHTTPServer(('127.0.0.1', A.port), H).serve_forever()
