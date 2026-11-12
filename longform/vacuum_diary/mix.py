#!/usr/bin/env python3
"""Timeline + mix for «Дневник робота-пылесоса». Runs on Denis's PC (voices are private, never committed).

The cut follows the voice: every diary day lasts as long as its line plus a short breath, so there is no dead air.
voices/<id>.wav (Denis, Qwen3-TTS) + CC-BY music bed (Kevin MacLeod) at 0.08 of active-speech voice RMS, fade in/out only.
No SFX (owner 07.11: background noises in the vacuum short were cringe).
Writes: ./timeline.json (numbers only, read by scene.js), <out>/mix.wav (48 kHz stereo), <out>/mix_report.json.
usage: py -3.11 mix.py <voices_dir> <music.mp3> <out_dir> [--timeline-only]
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR = 48000
HERE = Path(__file__).resolve().parent
SEGS = [['v0'], ['v1'], ['v2'], ['v3'], ['v4'], ['v5'], ['v6', 'v7']]   # hook + six diary days
LEAD0, LEAD, GAP, BREATH, TAIL = .15, .12, .4, .32, 1.0


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def piece(path):
    x = load(path)
    nz = np.where(np.abs(x) > .01)[0]
    if len(nz): x = x[max(0, nz[0] - int(.03 * SR)): nz[-1] + int(.08 * SR)]
    return x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .12


def main():
    vdir, music, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    clips = {i: piece(vdir / f'{i}.wav') for seg in SEGS for i in seg}
    lines, segs, t = {}, [], 0.0
    for s, ids in enumerate(SEGS):
        a, c = t, t + (LEAD if s else LEAD0)
        for i in ids:
            d = len(clips[i]) / SR; lines[i] = {'t': round(c, 3), 'd': round(d, 3)}; c += d + GAP
        t = c - GAP + (TAIL if s == len(SEGS) - 1 else BREATH); segs.append({'a': round(a, 3), 'b': round(t, 3)})
    dur = round(t, 3)
    (HERE / 'timeline.json').write_text(json.dumps({'dur': dur, 'lines': lines, 'segs': segs}, indent=1))
    print(f'TIMELINE body {dur:.2f} s:', {k: v['t'] for k, v in lines.items()})
    if '--timeline-only' in sys.argv: return
    N = int(dur * SR); voice = np.zeros(N, np.float32); active = np.zeros(N, bool)
    for i, x in clips.items():
        o = int(lines[i]['t'] * SR); e = min(N, o + len(x)); voice[o:e] += x[:e - o]; active[o:e] |= np.abs(x[:e - o]) > .01
    mus = load(music)[:N]
    if len(mus) < N: mus = np.pad(mus, (0, N - len(mus)))
    fade = np.ones(N, np.float32); fi, fo = int(.8 * SR), int(1.6 * SR); fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo); mus *= fade
    vr = np.sqrt(np.mean(voice[active] ** 2)); mus *= (.08 * vr) / (np.sqrt(np.mean(mus ** 2)) + 1e-9)
    ratio = float(np.sqrt(np.mean(mus ** 2)) / vr)
    mix = voice + mus; pk = float(np.abs(mix).max()); mix *= min(1.0, .89 / pk)
    st = np.stack([mix, mix], 1).astype(np.float32)
    raw = out / 'mix.f32'; raw.write_bytes(st.tobytes())
    wav = out / 'mix_pre.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(raw), '-c:a', 'pcm_s16le', str(wav)], check=True)
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(wav), '-af', 'loudnorm=I=-15:TP=-1.5:print_format=json', '-f', 'null', '-'],
                          capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rfind('{'):meas.rfind('}') + 1]); I0 = float(j['input_i'])
    gain = -15.0 - I0
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(raw),
                    '-af', f'volume={gain:.2f}dB,alimiter=limit=0.80:attack=3:release=60:level=false', '-c:a', 'pcm_s16le', str(out / 'mix.wav')], check=True)
    raw.unlink(); wav.unlink()
    rep = {'body_s': dur, 'body_lufs_before': I0, 'body_gain_db': round(gain, 2), 'music_to_voice_rms': round(ratio, 3), 'music': music.name, 'lines': lines}
    (out / 'mix_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1)); print(rep)


if __name__ == '__main__':
    main()
