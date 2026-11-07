#!/usr/bin/env python3
"""Builder for «Оумуамуа» demo (based on ai_levels / Живая картина) (Claude, 07.11.2026). Everything runs on Denis's PC.
  py -3.11 build.py voice  l1 [l2 …]   → jobs/voice/ai_<lvl>_<n>.json (≤8 lines) → local Qwen (Denis) → C:\\M1lash\\Работа\\oumuamua\\voice\\<lvl>\\<beat>.wav + ASR report
  py -3.11 build.py frames l1 [l2 …]   → SDXL keyframes + depth → longform/oumuamua/assets/
  py -3.11 build.py timeline l1 [l2 …] → longform/oumuamua/timeline.json (+ voice placement for the mix)
  py -3.11 build.py mix                → C:\\M1lash\\Работа\\oumuamua\\mix.wav (voice + quiet CC-BY music bed, −15 LUFS body)
"""
import json, subprocess, sys, shutil, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[1]; WORK = Path(r'C:\M1lash\Работа\oumuamua')
PY = sys.executable
MUSIC = REPO / 'media' / 'music' / 'Interloper.mp3'
GAP, MARK_GAP, LEVEL_GAP, LEAD = .45, 1.1, 1.6, 1.2


def level(l): return json.loads((HERE / 'levels' / f'{l}.json').read_text(encoding='utf-8'))


ALIAS = {}   # beat id → ASR spellings (e.g. years written in digits); threshold unchanged


def _synth(jid, items):
    """items: [(id, text, rate)] ≤8 → {id: (wav_path, sim, asr_text, pass)}"""
    job = {'job_id': jid, 'speaker': 'denis', 'voice_id': 'denis-qwen3tts-reference-v1', 'test_scope': 'private_owner_hearing_only',
           'utterances': [{'id': i, 'text': tx, 'rate': r, **({'asr_text_aliases': ALIAS[i]} if i in ALIAS else {})} for i, tx, r in items]}
    jp = REPO / 'jobs' / 'voice' / f'{jid}.json'; jp.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding='utf-8')
    tmp = WORK / 'voice_tmp' / jid
    import os
    r = subprocess.run([PY, 'scripts/pc/local_jobs.py', 'voice', '--job', str(jp.relative_to(REPO)), '--out', str(tmp)], cwd=REPO, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', env={**os.environ, 'M1LASH_ASR_SOFT': '1', 'PYTHONIOENCODING': 'utf-8'})
    if r.returncode or not (tmp / 'manifest.json').exists(): print('VOICE FAIL', jid, (r.stdout + r.stderr)[-500:]); return {}
    man = json.loads((tmp / 'manifest.json').read_text(encoding='utf-8'))
    return {u['id']: (tmp / u['source_file'], u['asr_similarity'], u['asr_text'], u.get('asr_pass', True)) for u in man['utterances']}


def voice(levels):
    import re
    for l in levels:
        L = level(l); beats = L['beats']; out = WORK / 'voice' / l; out.mkdir(parents=True, exist_ok=True)
        todo = [b for b in beats if not (out / f"{b['id']}.wav").exists()]
        ALIAS.update({b['id']: b['alias'] for b in beats if b.get('alias')})
        for attempt in range(3):                                  # whole lines, retried (sampling differs each run)
            if not todo: break
            for n in range(0, len(todo), 8):
                chunk = todo[n:n + 8]; res = _synth(f'ou_{l}_{attempt}_{n // 8 + 1}', [(b['id'], b.get('say', b['text']), b.get('rate', .97)) for b in chunk])
                for b in chunk:
                    if b['id'] in res and res[b['id']][3]:
                        shutil.copy2(res[b['id']][0], out / f"{b['id']}.wav"); print(f"{b['id']} {res[b['id']][1]:.2f} | {res[b['id']][2]}", flush=True)
            todo = [b for b in beats if not (out / f"{b['id']}.wav").exists()]
        for b in todo:                                            # still failing → split into sentences, synthesize, stitch
            parts = [p.strip() for p in re.split(r'(?<=[.!?…])\s+', b.get('say', b['text'])) if len(p.strip()) >= 5]
            res = _synth(f"ou_{l}_split_{b['id']}", [(f"{b['id']}p{i}", p, b.get('rate', .97)) for i, p in enumerate(parts[:8])])
            if parts and all(f"{b['id']}p{i}" in res and res[f"{b['id']}p{i}"][3] for i in range(len(parts))):
                lst = WORK / 'voice_tmp' / f"{b['id']}_concat.txt"
                sil = WORK / 'voice_tmp' / 'sil250.wav'
                if not sil.exists(): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', '.25', str(sil)], check=True)
                lst.write_text(''.join(f"file '{res[f'{b[chr(105)+chr(100)]}p{i}'][0].as_posix()}'\nfile '{sil.as_posix()}'\n" for i in range(len(parts))), encoding='utf-8')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-ar', '24000', '-ac', '1', str(out / f"{b['id']}.wav")], check=True)
                print(f"{b['id']} SPLIT ok ({len(parts)} parts)", flush=True)
            else:
                print(f"{b['id']} FAILED — нужна правка текста: {b['text']}", flush=True)


def frames(levels):
    assets = HERE / 'assets'; assets.mkdir(exist_ok=True)
    for l in levels:
        shots = [s for s in level(l)['shots'] if not (assets / f"{s['id']}.png").exists()]
        if not shots: continue
        sj = WORK / f'shots_{l}.json'; sj.parent.mkdir(parents=True, exist_ok=True); sj.write_text(json.dumps(shots, ensure_ascii=False), encoding='utf-8')
        fd = WORK / 'frames' / l
        subprocess.run([PY, str(HERE / 'gen_frames.py'), str(sj), str(fd)], check=True)
        subprocess.run([PY, str(HERE / 'depth.py'), str(fd)], check=True)
        for f in fd.glob('*.png'): shutil.copy2(f, assets / f.name)
        print('FRAMES', l, len(shots), flush=True)


def wav_len(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def move_for(i, n):        # deterministic varied camera moves (dolly in/out, lateral pans, crane), always through the depth relief
    k = (i * 7 + n) % 6
    return [
        {'z0': 2.15, 'z1': 1.7, 'x0': -.06, 'x1': .05},
        {'z0': 1.75, 'z1': 2.05, 'x0': .08, 'x1': -.04, 'ty0': .03, 'ty1': 0},
        {'z0': 1.95, 'z1': 1.8, 'x0': -.16, 'x1': .14, 'tx0': -.08, 'tx1': .08},
        {'z0': 2.0, 'z1': 1.72, 'y0': .1, 'y1': -.02, 'ty0': .06, 'ty1': 0},
        {'z0': 1.9, 'z1': 1.85, 'x0': .15, 'x1': -.14, 'tx0': .06, 'tx1': -.06, 'r0': .01, 'r1': -.01},
        {'z0': 2.2, 'z1': 1.6, 'depth': .65},
    ][k]


def timeline(levels):
    t = LEAD; shots, text, place, black = [], [], [], []
    for li, l in enumerate(levels):
        L = level(l); vdir = WORK / 'voice' / l; sh = {s['id']: s for s in L['shots']}
        if L.get('card'): text.append({'kind': 'card', 't': t - .2 + L.get('card_delay', 0), 'd': 3.6, 'text': L['card'][0], 'small': L['card'][1]})
        cur = None
        for bi, b in enumerate(L['beats']):
            d = wav_len(vdir / f"{b['id']}.wav"); place.append({'id': b['id'], 'level': l, 't': round(t, 3)})
            if b.get('mark'): text.append({'kind': 'card', 't': t, 'd': d + MARK_GAP, 'text': 'МЕТКА УРОВНЯ', 'small': b['text'].split(':', 1)[1].strip()})
            else: text.append({'kind': 'sub', 't': t, 'd': d + .25, 'text': b['text']})
            if b.get('quote'): text.append({'kind': 'quote', 't': t + d * .45, 'd': d * .55 + GAP, 'text': b['quote']})
            end = t + d + (MARK_GAP if b.get('mark') else GAP)
            if cur and cur['img'] == b['shot'] and end - cur['a'] < 11: cur['b'] = end
            else:
                if cur: shots.append(cur)
                s = sh[b['shot']]; cur = {'img': b['shot'], 'a': t - (.3 if cur else .6), 'b': end, 'move': {**move_for(len(shots), li), **s.get('move', {})}}
                for layer in s.get('layers', []): cur[layer] = True
                if s.get('cursor'): cur['cursor'] = [*s['cursor'], .3]
            t = end
        shots.append(cur); cur = None
        if li < len(levels) - 1: black.append([t, t + LEVEL_GAP * .6]); t += LEVEL_GAP
    tl = {'dur': round(t + 1.5, 2), 'shots': shots, 'text': text, 'black': black}
    (HERE / 'timeline.json').write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding='utf-8')
    (WORK / 'placement.json').write_text(json.dumps({'dur': tl['dur'], 'place': place}, ensure_ascii=False), encoding='utf-8')
    print('TIMELINE', levels, 'dur', tl['dur'], 's =', round(tl['dur'] / 60, 2), 'min, shots', len(shots), flush=True)


def mix():
    import numpy as np
    P = json.loads((WORK / 'placement.json').read_text(encoding='utf-8')); SR = 48000; N = int(P['dur'] * SR)
    def load(p):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], check=True, capture_output=True).stdout
        return np.frombuffer(raw, np.float32).copy()
    voice = np.zeros(N, np.float32); act = np.zeros(N, bool)
    for p in P['place']:
        x = load(WORK / 'voice' / p['level'] / f"{p['id']}.wav"); x = x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .12
        o = int(p['t'] * SR); e = min(N, o + len(x)); voice[o:e] += x[:e - o]; act[o:e] |= np.abs(x[:e - o]) > .01
    mus = load(MUSIC); reps = int(np.ceil(N / len(mus))); mus = np.tile(mus, reps)[:N]
    fade = np.ones(N, np.float32); k = int(3 * SR); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k); mus *= fade
    vr = np.sqrt(np.mean(voice[act] ** 2)); mus *= (.08 * vr) / (np.sqrt(np.mean(mus ** 2)) + 1e-9)
    st = np.stack([voice + mus, voice + mus], 1).astype(np.float32); (WORK / 'mix.f32').write_bytes(st.tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(WORK / 'mix.f32'), '-c:a', 'pcm_s16le', str(WORK / 'raw.wav')], check=True)
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(WORK / 'raw.wav'), '-af', 'loudnorm=I=-15:TP=-1.5:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rfind('{'):meas.rfind('}') + 1]); g = -15 - float(j['input_i']) + .3
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(WORK / 'raw.wav'), '-af', f'volume={g:.2f}dB,alimiter=limit=0.80:attack=3:release=60:level=false', str(WORK / 'mix.wav')], check=True)
    (WORK / 'mix.f32').unlink(); (WORK / 'raw.wav').unlink(); print('MIX', round(N / SR, 1), 's gain', round(g, 2), flush=True)


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'voice': voice, 'frames': frames, 'timeline': timeline, 'mix': lambda a: mix()}[cmd](args)
