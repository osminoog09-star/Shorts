# Кинетический текст в стиле movie-edit: слова появляются по таймингу речи, свечение, градиенты, 3D.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

F = '/root/fonts/'
_fc = {}

def font(name, size, var=None):
    k = (name, size, var)
    if k not in _fc:
        f = ImageFont.truetype(F + name, size)
        if var:
            f.set_variation_by_name(var)
        _fc[k] = f
    return _fc[k]

PAL = {
    'fire':   [(255, 236, 140), (255, 150, 40), (230, 50, 20)],
    'gold':   [(255, 250, 215), (255, 205, 80), (210, 120, 20)],
    'yellow': [(255, 255, 170), (255, 232, 40), (230, 170, 0)],
    'orange': [(255, 220, 160), (255, 140, 50), (220, 70, 20)],
    'blue':   [(225, 245, 255), (80, 190, 255), (20, 110, 255)],
    'red':    [(255, 225, 225), (255, 60, 60), (200, 0, 20)],
    'purple': [(245, 215, 255), (200, 110, 255), (140, 40, 230)],
    'cyan':   [(220, 255, 255), (60, 240, 230), (0, 170, 190)],
    'green':  [(225, 255, 220), (90, 255, 110), (20, 170, 60)],
    'white':  [(255, 255, 255), (235, 235, 235), (200, 200, 200)],
}

STYLES = {
    #        шрифт, вариация, размер, разрядка, тип заливки
    'caps':   ('Montserrat[wght].ttf', 'ExtraBold', 72, 12, 'caps'),
    'ital':   ('Montserrat-Italic[wght].ttf', 'Black Italic', 175, 4, 'grad'),
    'neon':   ('Montserrat[wght].ttf', 'Black', 165, 8, 'neon'),
    'bubble': ('RubikMonoOne-Regular.ttf', None, 150, 2, 'bubble'),
    'wide':   ('Unbounded[wght].ttf', 'Black', 140, 10, 'neon'),
    'heis':   ('Unbounded[wght].ttf', 'Black', 104, 6, 'neon'),
}

MAXW = 940
PAD = 60


def text_mask(txt, f, spacing):
    w = int(sum(f.getlength(c) for c in txt) + spacing * max(len(txt) - 1, 0)) + 2 * PAD
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * PAD
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    x = PAD
    for c in txt:
        d.text((x, PAD), c, font=f, fill=255)
        x += f.getlength(c) + spacing
    return m


def vgrad(size, cols):
    w, h = size
    y = np.linspace(0, 1, h)[:, None]
    c = np.array(cols, float)
    top = c[0] * (1 - np.clip(y * 2, 0, 1)) + c[1] * np.clip(y * 2, 0, 1)
    bot = c[1] * (1 - np.clip(y * 2 - 1, 0, 1)) + c[2] * np.clip(y * 2 - 1, 0, 1)
    g = np.where(y < 0.5, top, bot)
    return Image.fromarray(np.broadcast_to(g.reshape(h, 1, 3), (h, w, 3)).astype(np.uint8), 'RGB')


def colorize(mask, col, alpha=1.0):
    im = Image.new('RGBA', mask.size, tuple(col) + (0,))
    im.putalpha(mask.point(lambda v: int(v * alpha)))
    return im


def glow(mask, col, r, a):
    return colorize(mask.filter(ImageFilter.GaussianBlur(r)), col, a)


def shadow(mask, r=10, a=0.55, dy=6):
    s = Image.new('L', mask.size, 0)
    s.paste(mask, (0, dy))
    return colorize(s.filter(ImageFilter.GaussianBlur(r)), (0, 0, 0), a)


def render_token(txt, style, pal, size_scale=1.0):
    fname, var, size, sp, kind = STYLES[style]
    f = font(fname, int(size * size_scale), var)
    sp = sp * size_scale
    m = text_mask(txt, f, sp)
    cols = PAL[pal]
    out = Image.new('RGBA', m.size, (0, 0, 0, 0))
    if kind == 'caps':
        out = Image.alpha_composite(out, shadow(m, 8, 0.7, 4))
        out = Image.alpha_composite(out, glow(m, (255, 255, 255), 9, 0.45))
        out = Image.alpha_composite(out, colorize(m, (255, 255, 255)))
    elif kind == 'grad':
        out = Image.alpha_composite(out, shadow(m, 12, 0.6, 8))
        out = Image.alpha_composite(out, glow(m, cols[1], 26, 0.9))
        g = vgrad(m.size, cols).convert('RGBA'); g.putalpha(m)
        out = Image.alpha_composite(out, g)
    elif kind == 'neon':
        out = Image.alpha_composite(out, shadow(m, 12, 0.55, 6))
        out = Image.alpha_composite(out, glow(m, cols[2], 30, 1.0))
        out = Image.alpha_composite(out, glow(m, cols[1], 12, 1.0))
        g = vgrad(m.size, [cols[0], cols[0], cols[1]]).convert('RGBA'); g.putalpha(m)
        out = Image.alpha_composite(out, g)
    elif kind == 'bubble':
        dark = tuple(int(c * 0.45) for c in cols[2])
        ext = Image.new('L', m.size, 0)
        for k in range(1, 11):                       # объёмная «экструзия»
            ext = ImageChops.lighter(ext, ImageChops.offset(m, k // 2, k))
        out = Image.alpha_composite(out, shadow(ext, 14, 0.6, 10))
        out = Image.alpha_composite(out, glow(m, cols[1], 24, 0.85))
        out = Image.alpha_composite(out, colorize(ext, dark))
        g = vgrad(m.size, cols).convert('RGBA'); g.putalpha(m)
        out = Image.alpha_composite(out, g)
        hl = m.filter(ImageFilter.GaussianBlur(2))   # блик сверху
        hl = ImageChops.subtract(m, ImageChops.offset(m, 0, 6))
        out = Image.alpha_composite(out, colorize(hl, (255, 255, 255), 0.35))
    return out, f


class Line:
    def __init__(self, style, tokens, gap_word=True):
        self.style, self.pal = style if isinstance(style, tuple) else (style, 'white')
        tokens = [(tx[:-1] if tx.endswith('.') and not tx.endswith('..') else tx, t) for tx, t in tokens]
        self.tokens = tokens  # [(txt, t)]
        scale = 1.0
        while True:
            imgs = [render_token(tx, self.style, self.pal, scale)[0] for tx, _ in tokens]
            f = render_token('А', self.style, self.pal, scale)[1]
            gap = (f.getlength(' ') * 1.1 + STYLES[self.style][3] * 2.5) if gap_word else 0
            inner = [im.width - 2 * PAD for im in imgs]
            width = sum(inner) + gap * (len(imgs) - 1)
            if width <= MAXW or scale < 0.45:
                break
            scale *= 0.92
        self.imgs, self.width, self.scale = imgs, width, scale
        self.height = imgs[0].height - 2 * PAD
        xs, x = [], -width / 2
        for w in inner:
            xs.append(x)
            x += w + gap
        self.xs = xs


def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def draw_line(canvas, line, cy, t, t_end, fx_scale=1.0):
    W = canvas.width
    for (txt, ts), im, x in zip(line.tokens, line.imgs, line.xs):
        d = t - ts
        if d < 0 or t > t_end:
            continue
        a = ease_out(d / 0.16)
        fade = min(1.0, (t_end - t) / 0.14)
        s = (1.32 - 0.32 * a) * (1 + 0.05 * (1 - fade)) * fx_scale
        alpha = a * fade
        if alpha <= 0.01:
            continue
        w, h = im.size
        tw, th = max(1, int(w * s)), max(1, int(h * s))
        piece = im.resize((tw, th), Image.BILINEAR) if abs(s - 1) > 0.01 else im
        if alpha < 0.999:
            r, g, b, al = piece.split()
            piece = Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * alpha))))
        cx = W / 2 + (x + (w - 2 * PAD) / 2) * fx_scale
        py = cy + 22 * (1 - a)
        canvas.alpha_composite(piece, (int(cx - tw / 2), int(py - th / 2)))
