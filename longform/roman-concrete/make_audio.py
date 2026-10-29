#!/usr/bin/env python3
"""Сведение «Римского бетона»: голос Димы по timeline.json (вход 0.6 с) + музыка Kevin MacLeod (CC BY 4.0)
с приглушением под речь + SFX из studio/public → audio/roman_mix.m4a, audio/cues.json, audio/voice_manifest.json.
Запуск: cd longform/roman-concrete && python3 make_audio.py"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR = 48000
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
TTS = REPO / 'media/tts/roman_concrete'
MUS = REPO / 'media/music'
SFX = REPO / 'studio/public'
VO = 0.6

# музыка по разделам: (первая сцена раздела, трек)
SECTIONS = [('s01', 'Echoes of Time v2'), ('s04', 'Mesmerize'), ('s05', 'Investigations'), ('s06', 'Thatched Villagers'),
            ('s08', 'Inspired'), ('s10c', 'Dreamy Flashback'), ('s13', 'Clean Soul')]
CHAPTERS = {'s03', 's04c', 's06', 's09', 's10c', 's12', 's13', 's13c'}


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def put(buf, x, at, g=1.0):
    i = int(round(at * SR)); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i] * g


def main():
    tl = json.loads((ROOT / 'timeline.json').read_text())
    job = json.loads((REPO / 'jobs/tts/roman_concrete.json').read_text())
    texts = {l['id']: l['text'] for l in job['lines']}
    D = tl['duration']; N = int(SR * (D + 1))
    voice = np.zeros(N); manifest = []
    for s in tl['scenes']:
        mp3, meta = TTS / f"{s['id']}.mp3", TTS / f"{s['id']}.json"
        m = json.loads(meta.read_text())
        if m.get('voice_id') != 'ru-RU-DmitryNeural' or m.get('text') != texts[s['id']]:
            sys.exit(f"NO-GO: {s['id']} голос/текст не совпадает ({m.get('voice_id')})")
        x = load(mp3); put(voice, x, s['start'] + VO)
        manifest.append({'scene': s['id'], 'at': round(s['start'] + VO, 3), 'dur': round(len(x) / SR, 3), 'speaker': 'dima', 'voice_id': m['voice_id'],
                         'engine': m.get('engine', 'edge-tts'), 'rate': m.get('rate'), 'source_file': f"media/tts/roman_concrete/{s['id']}.mp3"})
    # музыка
    starts = {s['id']: s['start'] for s in tl['scenes']}
    music = np.zeros(N); credits = []
    bounds = [starts[a] for a, _ in SECTIONS] + [D]
    XF = 3.0
    for k, (sid, name) in enumerate(SECTIONS):
        a, b = bounds[k], bounds[k + 1]
        tr = load(MUS / f'{name}.mp3'); tr = tr / (np.max(np.abs(tr)) + 1e-9)
        seg = np.zeros(int(SR * (b - a + XF)))
        pos = 0
        while pos < len(seg):  # зацикливание с кроссфейдом 2 с
            n = min(len(tr), len(seg) - pos); piece = tr[:n].copy()
            f = int(SR * 2)
            if pos > 0: piece[:f] *= np.linspace(0, 1, f)[:len(piece[:f])]
            if n == len(tr): piece[-f:] *= np.linspace(1, 0, f)
            seg[pos:pos + n] += piece; pos += len(tr) - f
        fi, fo = int(SR * (XF if k else 1.5)), int(SR * XF)
        seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
        put(music, seg, max(0, a - (XF / 2 if k else 0)))
        credits.append(name)
    # огибающая ducking по наличию речи
    win = int(SR * 0.05); e = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
    talk = (e > 0.01).astype(float)
    # удержание 0.6 с, сглаживание 0.35 с
    hold = int(SR * 0.6); talk = np.convolve(talk, np.ones(hold), mode='same') > 0
    sm = int(SR * 0.35); duck = np.convolve(talk.astype(float), np.ones(sm) / sm, mode='same')
    gain = 0.23 - (0.23 - 0.075) * duck
    # финал: после последней фразы музыка выходит вперёд и затухает
    end_fade = np.clip((D - np.arange(N) / SR) / 3.0, 0, 1)
    mix = voice * 0.95 + music * gain * end_fade
    # SFX: мягкий whoosh на стыках, chime на главах
    wh, ch = load(SFX / 'whoosh.wav'), load(SFX / 'chime.wav')
    sfx_log = []
    for s in tl['scenes'][1:]:
        put(mix, wh, s['start'] - 0.35, 0.16); sfx_log.append({'name': 'whoosh', 'at': round(s['start'] - 0.35, 2)})
        if s['id'] in CHAPTERS: put(mix, ch, s['start'] + 0.25, 0.14); sfx_log.append({'name': 'chime', 'at': round(s['start'] + 0.25, 2)})
    peak = np.max(np.abs(mix)); mix = mix / peak * 0.89 if peak > 0.89 else mix
    out = ROOT / 'audio'; out.mkdir(exist_ok=True)
    wav = out / 'roman_mix.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '1', '-i', '-', '-ac', '2', str(wav)], input=mix.astype(np.float64).tobytes(), check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', str(out / 'roman_mix.m4a')], check=True)
    wav.unlink()
    (out / 'cues.json').write_text(json.dumps({'duration': D, 'voice': manifest, 'sfx': sfx_log, 'music': [{'track': n, 'from': bounds[i]} for i, n in enumerate(credits)]}, ensure_ascii=False, indent=1))
    (out / 'voice_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    (out / 'music_credits.txt').write_text('\n'.join(f'"{n}" Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/\n' for n in credits))
    print('mix ok', round(D, 1), 's', credits)


if __name__ == '__main__':
    main()
