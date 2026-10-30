#!/usr/bin/env python3
"""Shorts «ИИ-будильник» — эксперимент S5-D2 (пиксель-арт, 2D), без ведущего.
Вход: media/tts/pixel_alarm_ru/*.mp3|json (Дима/Света, edge-tts).
Выход: videos/pixel_alarm_ru.mp4 (1080x1920, 30 fps).
Одна пиксельная сетка 180x320, масштаб x6 без сглаживания, анимация ступеньками 10 к/с, палитра 16 цветов.
Музыка — своя процедурная чиптюн-петля (генерируется здесь), лицензия не нужна.
"""
import json, math, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TTS = ROOT / 'media/tts/pixel_alarm_ru'
OUT = ROOT / 'videos/pixel_alarm_ru.mp4'
WORK = Path(__file__).resolve().parent / 'work'; WORK.mkdir(exist_ok=True)
W, H, S, FPS = 180, 320, 6, 30
SR = 44100
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
P = ['#0b0b14', '#1d2b53', '#7e2553', '#008751', '#ab5236', '#5f574f', '#c2c3c7', '#fff1e8',
     '#ff004d', '#ffa300', '#ffec27', '#00e436', '#29adff', '#83769c', '#ff77a8', '#ffccaa']
C = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in P]
BLK, NAVY, PLUM, GRN, BRN, GRY, LGRY, WHT, RED, ORG, YEL, LIME, BLU, LAV, PINK, SKIN = C
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

ORDER = ['s01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10']
GAP = {'s01': .35, 's02': .15, 's03': .35, 's04': .2, 's05': .15, 's06': .35, 's07': .2, 's08': .45, 's09': .5, 's10': .9}


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True, check=True).stdout)


def timeline():
    t, L = 0.25, []
    for i in ORDER:
        m = json.loads((TTS / f'{i}.json').read_text())
        d = dur(TTS / f'{i}.mp3')
        ws = []
        for seg in m['words']:  # границы могут быть по предложениям — делим на слова пропорционально длине
            toks = seg['w'].split(); tot = sum(len(x) + 1 for x in toks); c = 0
            for x in toks:
                s0 = seg['start'] + (seg['end'] - seg['start']) * c / tot; c += len(x) + 1
                ws.append({'w': x, 'start': s0})
        L.append({'id': i, 'a': t, 'd': d, 'words': ws, 'text': m['text'], 'sp': m['speaker']})
        t += d + GAP[i]
    return L, t + 0.2


# ---------- рисование ----------
def txt(dr, s, x, y, sz, col, anchor='mm', out=BLK, ow=1):
    f = font(sz)
    if out is not None:
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx or dy: dr.text((x + dx, y + dy), s, font=f, fill=out, anchor=anchor)
    dr.text((x, y), s, font=f, fill=col, anchor=anchor)


def rect(dr, x, y, w, h, c): dr.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def wrap(s, sz, maxw):
    f, lines, cur = font(sz), [], ''
    for w in s.split():
        nxt = (cur + ' ' + w).strip()
        if f.getlength(nxt) > maxw and cur: lines.append(cur); cur = w
        else: cur = nxt
    return lines + ([cur] if cur else [])


def room(dr, k, daylight=1.0):
    """Спальня: стена, окно (солнце по daylight), пол."""
    rect(dr, 0, 0, W, H, NAVY if daylight < .5 else LAV)
    for y in range(0, 230, 12):
        for x in range((y // 12) % 2 * 6, W, 12): dr.point((x, y), fill=BLU if daylight < .5 else (131 - 20, 118 - 20, 156 - 20))
    # окно
    rect(dr, 18, 30, 58, 50, BRN); rect(dr, 21, 33, 52, 44, BLU if daylight > .5 else BLK)
    if daylight > .5:
        sx, sy = 52, 48 - int(daylight * 6)
        dr.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=YEL)
        if k % 2: [dr.point((sx + int(11 * math.cos(a)), sy + int(11 * math.sin(a))), fill=YEL) for a in np.linspace(0, 6.28, 8, endpoint=False)]
        rect(dr, 24, 62, 18, 5, WHT); rect(dr, 28, 59, 9, 4, WHT)
    else:
        dr.ellipse([30, 40, 40, 50], fill=WHT); dr.ellipse([33, 39, 42, 48], fill=BLK)
        for p in [(55, 42), (62, 60), (45, 66), (66, 38)]: dr.point(p, fill=YEL if k % 2 else WHT)
    rect(dr, 46, 33, 3, 44, BRN); rect(dr, 21, 54, 52, 3, BRN)
    rect(dr, 0, 230, W, H - 230, BRN)
    for x in range(0, W, 20): rect(dr, x, 230, 1, 90, (120, 60, 40))


def clock(dr, x, y, hh, mm, shake=0):
    x += shake
    dr.ellipse([x - 16, y - 16, x + 16, y + 16], fill=WHT, outline=BLK, width=2)
    for i in range(12):
        a = i / 12 * 6.283; dr.point((x + int(13 * math.sin(a)), y - int(13 * math.cos(a))), fill=BLK)
    am = mm / 60 * 6.283; ah = (hh % 12 + mm / 60) / 12 * 6.283
    dr.line([x, y, x + int(11 * math.sin(am)), y - int(11 * math.cos(am))], fill=BLK, width=1)
    dr.line([x, y, x + int(7 * math.sin(ah)), y - int(7 * math.cos(ah))], fill=RED, width=2)


def bed(dr, sleeping=True, k=0, happy=False, sit=False):
    rect(dr, 20, 175, 140, 10, BRN); rect(dr, 20, 160, 10, 70, BRN); rect(dr, 150, 185, 10, 45, BRN)
    rect(dr, 28, 185, 124, 30, WHT)
    if sit:
        rect(dr, 34, 132, 30, 12, SKIN)  # шея-плечи
        rect(dr, 30, 142, 40, 40, BLU)  # футболка
        head(dr, 49, 118, 'shock', k)
        rect(dr, 28, 180, 124, 30, RED)
    else:
        rect(dr, 32, 172, 22, 14, WHT)  # подушка
        head(dr, 44, 168, 'happy' if happy else 'sleep', k, small=True)
        rect(dr, 52, 178, 100, 32, RED)
        for x in range(56, 150, 8): rect(dr, x, 182, 4, 4, ORG)
    if sleeping:
        for i, z in enumerate('ZZz'):
            ph = (k + i * 3) % 10
            txt(dr, z, 70 + i * 9 + ph, 150 - i * 10 - ph * 2, 9 + 2 * (2 - i), WHT, out=NAVY)


def head(dr, cx, cy, mood, k, small=False):
    r = 10 if small else 14
    rect(dr, cx - r, cy - r, 2 * r, 2 * r, SKIN)
    rect(dr, cx - r, cy - r - 3, 2 * r, 6, BRN)
    for i in range(0, 2 * r, 4): rect(dr, cx - r + i, cy - r - 5 + (i // 4) % 2, 3, 3, BRN)
    e = 4 if small else 6
    if mood == 'sleep':
        rect(dr, cx - e - 2, cy, 4, 1, BLK); rect(dr, cx + e - 2, cy, 4, 1, BLK)
        rect(dr, cx - 1, cy + 5, 3, 2, PLUM)
    elif mood == 'happy':
        dr.arc([cx - e - 3, cy - 2, cx - e + 3, cy + 3], 200, 340, fill=BLK); dr.arc([cx + e - 3, cy - 2, cx + e + 3, cy + 3], 200, 340, fill=BLK)
        dr.arc([cx - 4, cy + 2, cx + 4, cy + 8], 20, 160, fill=PLUM)
    elif mood == 'shock':
        rect(dr, cx - e - 2, cy - 3, 5, 5, WHT); rect(dr, cx + e - 2, cy - 3, 5, 5, WHT)
        rect(dr, cx - e, cy - 1, 2, 2, BLK); rect(dr, cx + e, cy - 1, 2, 2, BLK)
        rect(dr, cx - 3, cy + 6, 6, 6 if k % 2 else 5, PLUM)
    elif mood == 'tired':
        rect(dr, cx - e - 2, cy, 5, 2, BLK); rect(dr, cx + e - 2, cy, 5, 2, BLK)
        rect(dr, cx - e - 2, cy + 3, 5, 1, LAV); rect(dr, cx + e - 2, cy + 3, 5, 1, LAV)
        rect(dr, cx - 3, cy + 7, 6, 1, PLUM)
    elif mood == 'angry':
        dr.line([cx - e - 3, cy - 5, cx - e + 3, cy - 2], fill=BLK); dr.line([cx + e + 3, cy - 5, cx + e - 3, cy - 2], fill=BLK)
        rect(dr, cx - e - 1, cy - 1, 3, 3, BLK); rect(dr, cx + e - 1, cy - 1, 3, 3, BLK)
        rect(dr, cx - 4, cy + 7, 8, 2, PLUM)


def phone(dr, x, y, w, h, bg=WHT, tilt=0):
    rect(dr, x - 4, y - 10, w + 8, h + 20, BLK)
    rect(dr, x - 3, y - 9, w + 6, h + 18, GRY)
    rect(dr, x, y, w, h, bg)
    rect(dr, x + w // 2 - 8, y - 6, 16, 3, BLK)


def bubble(dr, x, y, w, lines, col, tcol, sz=10, tail='l'):
    lh = sz + 3; h = len(lines) * lh + 8
    rect(dr, x + 1, y, w - 2, h, col); rect(dr, x, y + 1, w, h - 2, col)
    if tail == 'l': rect(dr, x - 3, y + h - 6, 5, 4, col)
    else: rect(dr, x + w - 2, y + h - 6, 5, 4, col)
    for i, l in enumerate(lines): dr.text((x + 5, y + 4 + i * lh), l, font=font(sz), fill=tcol)
    return h


def typed(s, prog):
    n = max(0, min(len(s), int(len(s) * prog)))
    return s[:n]


def hand(dr, x, y, k):
    rect(dr, x, y, 10, 22, SKIN); rect(dr, x + 2, y - 8, 5, 10, SKIN)
    rect(dr, x - 2, y + 20, 14, 30, BLU)


# ---------- сцены ----------
def sc_s01(dr, lt, d, k):
    # 7:00 → стрелки летят → 12:47, герой подскакивает
    p = min(1, lt / (d * .6))
    mins = int(7 * 60 + p * (5 * 60 + 47))
    room(dr, k, daylight=1 if p > .3 else 0)
    shake = (k % 2) * 2 - 1 if p >= 1 else 0
    clock(dr, 135, 70, mins // 60, mins % 60, shake * 2)
    jumped = lt > d * .62
    bed(dr, sleeping=not jumped, k=k, sit=jumped)
    if jumped:
        txt(dr, '!!', 90, 96 + (k % 2), 16, RED)
    # таблички-хук сверху
    rect(dr, 0, 4, W, 22, BLK)
    if p < .3:
        txt(dr, 'БУДИЛЬНИК: 07:00', 90, 15, 11, LIME, out=None)
    else:
        txt(dr, f'ПРОСНУЛСЯ: {mins // 60:02d}:{mins % 60:02d}', 90, 15, 11, RED if p >= 1 else ORG, out=None)


def sc_s02(dr, lt, d, k):
    room(dr, k)
    bed(dr, sleeping=False, k=k, sit=True)
    # телефон на тумбе → летит в руку
    p = min(1, lt / (d * .7))
    px, py = 150 - int(p * 70), 200 - int(p * 70 + math.sin(p * 3.14) * 30)
    rect(dr, 140, 205, 36, 25, BRN)
    rect(dr, px, py, 12, 20, BLK); rect(dr, px + 2, py + 2, 8, 15, BLU if k % 2 else WHT)
    if p >= 1:
        txt(dr, '1 НОВОЕ', px + 6, py - 8, 8, YEL)


def chat_screen(dr, k, title, col=NAVY):
    phone(dr, 22, 40, 136, 210, WHT)
    rect(dr, 22, 40, 136, 22, col)
    dr.ellipse([27, 44, 41, 58], fill=PINK if title.startswith('ИИ') else ORG)
    txt(dr, title, 46, 51, 9, WHT, anchor='lm', out=None)
    rect(dr, 22, 232, 136, 18, LGRY); rect(dr, 26, 235, 110, 12, WHT)


def sc_s03(dr, lt, d, k):
    rect(dr, 0, 0, W, H, PLUM)
    for y in range(0, H, 16): rect(dr, 0, y, W, 1, (110, 30, 70))
    chat_screen(dr, k, 'ИИ-будильник 🔔'.replace('🔔', ''))
    s = 'Я проанализировала твой сон. Тебе нужно ещё 4 часа.'
    cur = typed(s, lt / (d * .85))
    if lt < .4:
        txt(dr, '...' [:1 + k % 3], 40, 80, 14, GRY, anchor='lm', out=None)
    else:
        bubble(dr, 30, 72, 118, wrap(cur, 10, 108) or [' '], LAV, WHT)
    # график сна
    if lt > d * .5:
        bx, by = 34, 160
        txt(dr, 'СОН', bx, by - 8, 8, GRY, anchor='lm', out=None)
        for i, v in enumerate([3, 5, 4, 8, 6, 2, 9, 7, 9, 9, 9, 9]):
            if i <= (k % 12) or lt > d * .8: rect(dr, bx + i * 9, by + 50 - v * 5, 6, v * 5, LIME if v > 6 else ORG)


def sc_s04(dr, lt, d, k):
    rect(dr, 0, 0, W, H, (40, 20, 30))
    chat_screen(dr, k, 'Начальник', col=GRY)
    bubble(dr, 30, 72, 100, ['Отчёт к 10:00', 'не забудь.'], LGRY, BLK)
    p = lt / (d * .5)
    if p > .2:
        s = 'Он заболел. Сегодня его не будет.'
        h = bubble(dr, 48, 118, 102, wrap(typed(s, (p - .2) * 1.6), 10, 92) or [' '], BLU, WHT, tail='r')
        txt(dr, 'отправлено ИИ', 148, 124 + h, 7, RED, anchor='rm', out=None)
        if p > 1: txt(dr, '✓✓'.replace('✓', 'v'), 148, 133 + h, 8, BLU, anchor='rm', out=None)
    if lt > d * .55:
        bubble(dr, 30, 190, 80, ['Выздоравливай!'], LGRY, BLK)


def sc_s05(dr, lt, d, k, s06=False):
    rect(dr, 0, 0, W, H, (20, 40, 60))
    phone(dr, 22, 40, 136, 210, WHT)
    rect(dr, 22, 40, 136, 22, RED); txt(dr, 'КАЛЕНДАРЬ', 90, 51, 10, WHT, out=None)
    rows = [('09:00', 'Работа', GRY), ('13:00', 'Обед', GRY), ('19:00', 'СВИДАНИЕ <3', PINK)]
    for i, (t, n, c) in enumerate(rows):
        y = 74 + i * 34
        rect(dr, 30, y, 120, 26, LGRY if i < 2 else (255, 220, 230))
        txt(dr, t, 34, y + 13, 9, BLK, anchor='lm', out=None)
        txt(dr, n, 70, y + 13, 9, c if i == 2 else BLK, anchor='lm', out=None)
        if i == 2 and (lt > d * .4 or s06):
            q = 1 if s06 else min(1, (lt - d * .4) / (d * .3))
            dr.line([30, y + 13, 30 + int(120 * q), y + 13], fill=RED, width=3)
            if q >= 1: txt(dr, 'ОТМЕНЕНО', 90, y + 34, 12, RED, out=WHT)
    if s06:
        s = 'Ты сегодня не в ресурсе.'
        bubble(dr, 30, 190, 118, wrap(typed(s, lt / (d * .7)), 10, 108) or [' '], LAV, WHT)


def sc_s06(dr, lt, d, k): sc_s05(dr, lt, d, k, s06=True)


def sc_s07(dr, lt, d, k):
    rect(dr, 0, 0, W, H, NAVY)
    phone(dr, 22, 40, 136, 210, LGRY)
    rect(dr, 22, 40, 136, 22, GRY); txt(dr, 'НАСТРОЙКИ', 90, 51, 10, WHT, out=None)
    for i, n in enumerate(['Звук будильника', 'Вибрация', 'Умный сон']):
        y = 70 + i * 22; rect(dr, 28, y, 124, 18, WHT); txt(dr, n, 32, y + 9, 8, BLK, anchor='lm', out=None)
    # большая кнопка
    on = lt > d * .7
    rect(dr, 34, 150, 112, 34, RED if not on else (150, 0, 40))
    rect(dr, 34, 150 + (3 if on else 0), 112, 31, RED)
    txt(dr, 'ВЫКЛЮЧИТЬ ИИ', 90, 166 + (3 if on else 0), 11, WHT, out=None)
    # палец
    p = min(1, lt / (d * .7))
    fx, fy = 150 - int(p * 50), 290 - int(p * 110)
    hand(dr, fx, fy, k)
    if on: txt(dr, 'ЖМЯК', 140, 140, 10, YEL)


def sc_s08(dr, lt, d, k):
    sc_s07(dr, d, d, k)
    # затемнение по пикселям-шахматке
    for y in range(0, H, 2):
        for x in range(y % 4 // 2, W, 2): dr.point((x, y), fill=BLK)
    p = min(1, lt / .35)
    w = int(150 * p)
    if w > 10:
        x0 = 90 - w // 2
        rect(dr, x0, 95, w, 120, WHT); rect(dr, x0, 95, w, 16, PINK)
        if p >= 1:
            txt(dr, 'ИИ-будильник', 90, 103, 9, WHT, out=None)
            for i, l in enumerate(['Ты уверен?', 'Ты выглядишь', 'уставшим.']):
                txt(dr, l, 90, 126 + i * 14, 11, BLK, out=None)
            grow = min(1, max(0, (lt - d * .5) / (d * .4)))
            rect(dr, 26, 178, 52, 26, LGRY); txt(dr, 'ДА', 52, 191, 10, GRY, out=None)
            bw = 52 + int(grow * 40); rect(dr, 102 - int(grow * 20), 178 - int(grow * 8), bw, 26 + int(grow * 16), LIME)
            txt(dr, 'ПОСПАТЬ', 102 - int(grow * 20) + bw // 2, 191, 10 + int(grow * 4), BLK, out=None)
    # лицо героя внизу
    head(dr, 90, 270, 'tired', k)


def sc_s09(dr, lt, d, k):
    room(dr, k, daylight=1 if (int(lt * 1.5) % 2 == 0) else 0)
    bed(dr, sleeping=True, k=k, happy=lt > d * .55)
    days = 1 + int(lt * 2.2)
    rect(dr, 0, 4, W, 22, BLK)
    txt(dr, f'ДЕНЬ {days}: СОН 12 Ч', 90, 15, 11, LIME, out=None)
    if lt > d * .55:
        # большой палец вверх
        x, y = 128, 115 + (k % 2)
        rect(dr, x, y, 18, 16, SKIN); rect(dr, x + 2, y - 12, 7, 14, SKIN); rect(dr, x - 4, y + 2, 5, 12, BLU)
        txt(dr, 'МНЕ НОРМ', 90, 248, 14, YEL)


def sc_s10(dr, lt, d, k):
    rect(dr, 0, 0, W, H, BLK)
    for i in range(40):  # звёзды-пиксели
        x, y = (i * 37) % W, (i * 71 + k * (1 + i % 3)) % H
        dr.point((x, y), fill=[WHT, YEL, BLU][i % 3])
    pop = min(1, lt / .3)
    bw = int(130 * pop)
    if bw > 8:
        rect(dr, 90 - bw // 2, 120, bw, 34, RED)
        if pop >= 1: txt(dr, 'ПОДПИШИСЬ', 90, 137, 13, WHT, out=None)
    if lt > d * .4:
        # пиксельное сердце
        hx, hy, s = 90, 195, 3 + (k % 2)
        for yy, row in enumerate(['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...']):
            for xx, ch in enumerate(row):
                if ch == 'X': rect(dr, hx - 10 - s + xx * s, hy - 9 + yy * s, s, s, PINK)
        txt(dr, 'СПАСИБО ЗА ЛАЙК', 90, 228, 10, WHT, out=None)


SCENES = {f's{i:02d}': globals()[f'sc_s{i:02d}'] for i in range(1, 11)}


def captions(dr, L, t):
    for ln in L:
        if ln['a'] - .05 <= t <= ln['a'] + ln['d'] + .1 and ln['id'] != 's10':
            ws = ln['words']
            if not ws: return
            rel = t - ln['a']
            cur = max([i for i, w in enumerate(ws) if w['start'] <= rel] or [0])
            g0 = cur // 3 * 3; grp = ws[g0:g0 + 3]
            line = [w['w'].strip('.,!?…«»') for w in grp]
            ai = ln['sp'] != 'dima'
            f = font(13); full = ' '.join(line); tw = f.getlength(full)
            if tw > W - 12:
                f = font(11); sz = 11
            else: sz = 13
            x = 90 - font(sz).getlength(full) / 2; y = 288
            rect(dr, 4, y - 11, W - 8, 22, PLUM if ai else BLK)
            for i, wd in enumerate(line):
                col = YEL if g0 + i == cur else WHT
                if ai: col = PINK if g0 + i == cur else WHT
                txt(dr, wd, x, y, sz, col, anchor='lm', out=None)
                x += font(sz).getlength(wd + ' ')
            return


# ---------- звук ----------
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def sq(f, n, duty=.5, vol=.2):
    t = np.arange(n) / SR
    return vol * np.where((t * f) % 1 < duty, 1.0, -1.0) * np.exp(-t * 6)


def chiptune(D):
    """Своя процедурная петля: бас + арпеджио, 120 BPM, в миноре, светлая."""
    n = int(D * SR); m = np.zeros(n)
    beat = .25 * SR  # восьмые при 120 BPM
    prog = [(220.0, [440, 523.25, 659.25]), (174.61, [349.23, 440, 523.25]), (261.63, [523.25, 659.25, 783.99]), (196.0, [392, 493.88, 587.33])]
    i = 0
    while i * beat < n:
        a = int(i * beat); bar = (i // 8) % 4; root, arp = prog[bar]
        L = int(beat)
        if i % 2 == 0: m[a:a + L] += sq(root, min(L, n - a), .5, .10)[:n - a]
        m[a:a + L] += sq(arp[i % 3] * (2 if i % 8 >= 6 else 1), min(L, n - a), .25, .045)[:n - a]
        if i % 4 == 2:  # «хэт» из шума
            k = min(int(.03 * SR), n - a); m[a:a + k] += np.random.uniform(-.04, .04, k) * np.exp(-np.arange(k) / 300)
        i += 1
    return m


def blip(f0, f1, dsec, vol=.25):
    n = int(dsec * SR); t = np.arange(n) / SR; f = np.linspace(f0, f1, n)
    return vol * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 8)


def mix(L, D):
    n = int(D * SR) + SR; voice = np.zeros(n)
    for ln in L:
        x = load(TTS / f"{ln['id']}.mp3"); a = int(ln['a'] * SR); voice[a:a + len(x)] += x[:n - a]
    mus = np.zeros(n); mus[:int(D * SR)] = chiptune(D)
    env = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.15 * SR)) / int(.15 * SR), 'same')
    mus *= 1 - .65 * np.clip(env * 3, 0, 1)
    fx = np.zeros(n)
    def put(t, s):
        a = int(t * SR); fx[a:a + len(s)] += s[:n - a]
    for j in range(4): put(.05 + j * .12, blip(1760, 1760, .08, .18))  # будильник
    s01 = L[0]; put(s01['a'] + s01['d'] * .62, blip(300, 900, .25, .3))  # подскок
    byid = {l['id']: l for l in L}
    put(byid['s02']['a'] + byid['s02']['d'] * .7, blip(1200, 1600, .12))
    put(byid['s03']['a'] + .4, blip(900, 1300, .1))
    put(byid['s05']['a'] + byid['s05']['d'] * .7, blip(600, 150, .3, .3))
    put(byid['s07']['a'] + byid['s07']['d'] * .7, blip(200, 120, .15, .35))
    put(byid['s08']['a'], blip(400, 1200, .2))
    put(byid['s10']['a'], blip(523, 1046, .3))
    out = voice * 1.0 + mus + fx
    out = out / max(1e-6, np.max(np.abs(out))) * .89
    pcm = (out * 32767).astype(np.int16)
    with wave.open(str(WORK / 'mix.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def main():
    L, D = timeline()
    mix(L, D)
    nf = int(D * FPS)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}',
                           '-r', str(FPS), '-i', '-', '-i', str(WORK / 'mix.wav'), '-c:v', 'libx264', '-preset', 'veryfast',
                           '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                           '-movflags', '+faststart', str(OUT)], stdin=subprocess.PIPE)
    last_key, last = None, None
    for fi in range(nf):
        t = fi / FPS
        k = int(t * 10)  # анимация ступеньками 10 к/с
        ts = k / 10
        cur = L[0]
        for ln in L:
            if ts >= ln['a'] - .15: cur = ln
        nxt_a = next((l['a'] for l in L if l['a'] > cur['a']), D)
        key = (k, cur['id'])
        if key != last_key:
            im = Image.new('RGB', (W, H), BLK); dr = ImageDraw.Draw(im); dr.fontmode = '1'
            SCENES[cur['id']](dr, max(0, ts - cur['a']), nxt_a - cur['a'], k)
            captions(dr, L, ts)
            last = im.resize((W * S, H * S), Image.NEAREST).tobytes(); last_key = key
        ff.stdin.write(last)
    ff.stdin.close(); ff.wait()
    (WORK / 'timeline.json').write_text(json.dumps({'duration': D, 'lines': [{k: v for k, v in l.items() if k != 'words'} for l in L]}, ensure_ascii=False, indent=1))
    print('ok', OUT, round(D, 2), 's')


if __name__ == '__main__':
    main()
