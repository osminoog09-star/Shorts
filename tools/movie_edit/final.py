# Pass 2: кинетический текст + вспышки поверх base.mp4, потом звук.
import subprocess, sys
import numpy as np
from PIL import Image
from edit import *
from kinetic import Line, draw_line

base, out = sys.argv[1], sys.argv[2]
only = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None
import os
Y0 = int(os.environ.get('MOVIE_EDIT_CAPTION_Y', '1000'))

phr = []
for top_st, top, bot_st, bot, end in PHRASES:
    if isinstance(bot, str):  # по буквам
        t0, t1 = (edit_time(x) for x in LETTERS[bot])
        toks = [(c, t0 + (t1 - t0) * i / (len(bot) - 1)) for i, c in enumerate(bot)]
        bl = Line(bot_st, toks, gap_word=False)
    else:
        bl = Line(bot_st, [(w, edit_time(t)) for w, t in bot])
    tl = Line(top_st, [(w, edit_time(t)) for w, t in top]) if top else None
    s0 = bot[0][1] if not isinstance(bot, str) else LETTERS[bot][0]
    e = edit_time(min(end, max(b for a, b in SEGMENTS if a <= s0 <= b)))
    phr.append((tl, bl, e))

flashes = [edit_time(t) for t in FLASH]
punches = [edit_time(t) for t in PUNCH]

def overlay(t):
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for tl, bl, e in phr:
        start = min([x for _, x in (tl.tokens if tl else [])] + [x for _, x in bl.tokens])
        if not (start - 0.01 <= t <= e):
            continue
        # лёгкий «дых» текста на ударах
        fx = 1.0
        for p in punches:
            d = t - p
            if 0 <= d < 0.5:
                fx = 1 + 0.06 * np.exp(-d * 8)
        if tl:
            bh = bl.height
            draw_line(cv, tl, Y0 - bh * 0.55 - tl.height * 0.5 - 6, t, e)
            draw_line(cv, bl, Y0 + 10, t, e, fx)
        else:
            draw_line(cv, bl, Y0, t, e, fx)
    a = 0.0
    for f in flashes:
        d = t - f
        if 0 <= d < 0.25:
            a = max(a, 0.55 * (1 - d / 0.25))
    return cv, a

if only:
    for o in only:
        png = subprocess.run(['ffmpeg','-v','error','-ss',f'{o:.3f}','-i',base,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout
        import io
        fr = Image.open(io.BytesIO(png)).convert('RGBA')
        cv, fl = overlay(o); fr.alpha_composite(cv)
        fr.convert('RGB').resize((360, 640)).save(f'st_{o:06.2f}.jpg')
    sys.exit()

dec = subprocess.Popen(['ffmpeg','-v','error','-i',base,'-f','rawvideo','-pix_fmt','rgb24','-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
    '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',out], stdin=subprocess.PIPE)
i = 0
while True:
    buf = dec.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    t = i / FPS
    fr = Image.frombuffer('RGB', (W, H), buf).convert('RGBA')
    cv, fl = overlay(t)
    fr.alpha_composite(cv)
    if fl > 0:
        fr = Image.blend(fr, Image.new('RGBA', (W, H), (255, 255, 255, 255)), fl)
    enc.stdin.write(fr.convert('RGB').tobytes())
    i += 1
enc.stdin.close(); enc.wait()
print('frames', i)
