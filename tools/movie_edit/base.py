# Pass 1: вертикальный кадр 9:16 с наездами на лица, ударами камеры, тряской и цветокором.
import subprocess, sys, math, random
import numpy as np
from PIL import Image
from edit import *

PX, PY, PW, PH = PIC
out = sys.argv[1] if len(sys.argv) > 1 else 'base.mp4'
only = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None  # превью: монтажные времена

def ease(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3

def zoom_at(src):
    (s0, cx, cy), nxt = shot_at(src)
    p = (src - s0) / max(nxt - s0, 0.5)
    z = 1.0 + 0.10 * ease(p * 0.9)            # медленный наезд внутри шота
    for t in PUNCH:                           # резкий удар на ключевом слове
        d = src - t
        if 0 <= d < 0.9:
            z *= 1 + 0.10 * math.exp(-d * 5) * ease(d / 0.05)
    return z, cx, cy

def shake_at(src):
    for t, dur in SHAKE:
        d = src - t
        if 0 <= d < dur:
            k = math.exp(-d * 4) * 9
            r = random.Random(int(src * 1000))
            return r.uniform(-k, k), r.uniform(-k, k)
    return 0, 0

def frame_box(src):
    z, cx, cy = zoom_at(src)
    h = PH / z
    w = h * 9 / 16
    x = cx * PW - w / 2
    y = cy * PH - h / 2
    sx, sy = shake_at(src)
    x = min(max(x + sx, 0), PW - w)
    y = min(max(y + sy, 0), PH - h)
    return (x, y, x + w, y + h)

enc = None
if only is None:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
        '-vf', 'cas=0.75,unsharp=5:5:0.6:5:5:0,eq=contrast=1.08:saturation=1.18:brightness=0.035,vignette=PI/8,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', out], stdin=subprocess.PIPE)

et = 0.0
n_out = 0
for a, b in SEGMENTS:
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', SRC,
        '-vf', f'crop={PW}:{PH}:{PX}:{PY},fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    nfr = int(round((b - a) * FPS))
    for i in range(nfr):
        buf = dec.stdout.read(PW * PH * 3)
        if len(buf) < PW * PH * 3:
            break
        src = a + i / FPS
        t_edit = et + i / FPS
        if only is not None and not any(abs(t_edit - o) < 0.5 / FPS for o in only):
            continue
        img = Image.frombuffer('RGB', (PW, PH), buf)
        fr = img.resize((W, H), Image.LANCZOS, box=frame_box(src))
        if only is not None:
            fr.save(f'prev_{t_edit:06.2f}.png')
        else:
            enc.stdin.write(fr.tobytes())
        n_out += 1
    dec.stdout.close(); dec.wait()
    et += nfr / FPS

if enc:
    enc.stdin.close(); enc.wait()
print('frames', n_out, 'dur', et)
