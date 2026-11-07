#!/usr/bin/env python3
"""Mix for «Притворись ботом · серия 4». Voice only (owner 07.11: no music/background SFX in the body).
Lays the lines out by the action beats, writes voices/timing.json (line starts + body duration), voices/dur.json, voices/lips.json for scene.js,
and <out>/mix.wav normalised to -15 LUFS (TP <= -1.5) for the body.
usage: py -3.11 mix.py <voices_dir> <out_dir>    (voices_dir holds d1..d4.wav, f1..f4.wav; f3b/f4b override f3/f4 when present)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR = 48000
HERE = Path(__file__).resolve().parent
# (id, earliest start, min gap after the previous line) — gaps leave room for the visual beats in scene.js
PLAN = [('f1', .3, 0), ('d1', 3.3, .45), ('f2', 7.0, .5), ('d2', 0, .6),   # d2 after the boss lifts her robot head (f2 + 1.15 … + 2.75)
        ('f3', 0, .45), ('d3', 0, 1.8),                                     # workers unhead one by one during the gap
        ('f4', 0, 1.6), ('d4', 0, 1.9)]                                     # coffee machine wakes before f4, pours itself coffee before d4
TAIL = 1.3
OVERRIDE = {'f3': 'f3b', 'f4': 'f4b'}


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); nz = np.where(np.abs(x) > .01)[0]
    if len(nz): x = x[max(0, nz[0] - int(.03 * SR)): nz[-1] + int(.08 * SR)]
    return x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .12


def main():
    vd, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    clips, starts, durs, used, t = {}, {}, {}, {}, 0.0
    for lid, earliest, gap in PLAN:
        name = OVERRIDE.get(lid) if (vd / f'{OVERRIDE.get(lid, "")}.wav').exists() else lid
        x = load(vd / f'{name}.wav'); used[lid] = name
        s = max(earliest, t + gap); starts[lid] = round(s, 3); durs[lid] = round(len(x) / SR, 3); clips[lid] = x; t = s + durs[lid]
    dur = round(t + TAIL, 2); N = int(dur * SR); mix = np.zeros(N, np.float32); lips = {}
    for lid, x in clips.items():
        o = int(starts[lid] * SR); mix[o:o + len(x)] += x[:N - o]
        hop = SR // 30; fr = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]; m = max(fr) or 1
        lips[lid] = [round(min(1, (v / m) ** .7 * 1.15), 3) for v in fr]
    st = np.stack([mix, mix], 1).astype(np.float32); (out / 'mix.f32').write_bytes(st.tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(out / 'mix.f32'), '-c:a', 'pcm_s16le', str(out / 'raw.wav')], check=True)
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(out / 'raw.wav'), '-af', 'loudnorm=I=-15:TP=-1.5:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rfind('{'):meas.rfind('}') + 1]); gain = -15.0 - float(j['input_i']) + .3
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out / 'raw.wav'), '-af', f'volume={gain:.2f}dB,alimiter=limit=0.80:attack=3:release=60:level=false', str(out / 'mix.wav')], check=True)
    (out / 'mix.f32').unlink(); (out / 'raw.wav').unlink()
    v = HERE / 'voices'; v.mkdir(exist_ok=True)
    (v / 'timing.json').write_text(json.dumps({'lines': starts, 'dur': dur}, indent=1)); (v / 'dur.json').write_text(json.dumps(durs, indent=1)); (v / 'lips.json').write_text(json.dumps(lips))
    rep = {'starts': starts, 'durs': durs, 'dur': dur, 'used': used, 'gain_db': round(gain, 2)}
    (out / 'mix_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1)); print(rep)


if __name__ == '__main__':
    main()
