# Сборка вертикальных нарезок: таймлайн (out/short_<name>_tl.json → shorts/<name>.json) + звук (audio/short_<name>.m4a)
# python3 make_shorts.py [name ...]
import json, subprocess, sys, os
import numpy as np
import audio

SR = audio.SR
HERE = os.path.dirname(os.path.abspath(__file__))
TTS = os.path.join(HERE, '../../media/tts/antikythera_shorts')
MUS = os.path.join(HERE, '../../media/music')
tl = json.load(open(os.path.join(HERE, 'timeline.json')))
SC = {s['id']: s for s in tl['scenes']}
cfg = json.load(open(os.path.join(HERE, 'shorts.json')))
main = audio.load_audio(os.path.join(HERE, 'audio/antikythera_mix.m4a'))
XF = int(SR * 0.25)


def dur_of(p):
    return len(audio.load_audio(p)) / SR


def build(name):
    c = cfg[name]
    parts, t = [], 0.0
    for p in c['parts']:
        if p['type'] == 'scene':
            s = SC[p['id']]; a = p.get('from', 0.0); b = p.get('to', s['dur'])
            parts.append({**p, 'start': t, 'dur': b - a, 'local': a, 'src': s['start'] + a})
        else:
            vd = dur_of(f"{TTS}/{p['vo']}.mp3") + 0.55
            parts.append({**p, 'start': t, 'dur': vd, 'local': p.get('from', 0.0), 'vfile': f"{p['vo']}.mp3"})
        t += parts[-1]['dur']
    od = dur_of(f'{TTS}/outro.mp3') + 1.6
    last = parts[-1]
    parts.append({'type': 'outro', 'scene': last.get('id') or last.get('scene'), 'start': t, 'dur': od,
                  'local': last['local'] + last['dur'], 'vfile': 'outro.mp3'})
    total = t + od
    os.makedirs(os.path.join(HERE, 'shorts'), exist_ok=True)
    json.dump({'name': name, 'duration': round(total, 3), 'parts': parts}, open(os.path.join(HERE, f'shorts/{name}.json'), 'w'), ensure_ascii=False, indent=1)
    # звук
    n = int(SR * total) + SR
    out = np.zeros(n)
    bed = audio.load_audio(f"{MUS}/{c['bed']}")
    for p in parts:
        a0, L = int(p['start'] * SR), int(p['dur'] * SR)
        if p['type'] == 'scene':
            src = main[int(p['src'] * SR): int(p['src'] * SR) + L + XF].copy()
        else:
            v = audio.load_audio(f"{TTS}/{p['vfile']}")
            src = np.zeros(L + XF); src[int(0.25 * SR): int(0.25 * SR) + len(v)] += v[: L + XF - int(0.25 * SR)] * 0.95
            b0 = int((p['start'] * 0.37 % 20) * SR)
            mb = np.resize(bed[b0:], L + XF) * 0.16
            env = np.convolve(np.abs(src), np.ones(int(SR * 0.25)) / int(SR * 0.25), 'same')
            src += mb * (1 - 0.55 * np.clip(env / 0.05, 0, 1))
        e = np.ones(len(src)); k = min(XF, len(src) // 2)
        e[:k] = np.linspace(0, 1, k); e[-k:] = np.linspace(1, 0, k)
        out[a0: a0 + len(src)] += (src * e)[: n - a0]
    out = out[: int(SR * total)]
    fade = int(SR * 0.8); out[-fade:] *= np.linspace(1, 0, fade)
    pk = np.max(np.abs(out)) or 1
    pcm = (np.tanh(out / pk * 1.1) * 0.9 * 32767).astype(np.int16)
    raw = os.path.join(HERE, f'out/short_{name}.wav'); os.makedirs(os.path.dirname(raw), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', raw], input=pcm.tobytes(), check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '192k',
                    os.path.join(HERE, f'audio/short_{name}.m4a')], check=True)
    print(name, round(total, 2), 's', [(p['type'], p.get('id') or p.get('scene'), round(p['dur'], 2)) for p in parts])


for nm in (sys.argv[1:] or list(cfg)):
    build(nm)
