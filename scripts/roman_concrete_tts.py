#!/usr/bin/env python3
"""Устойчивая озвучка «Римского бетона» Димой (ru-RU-DmitryNeural, Edge TTS).
Повторы, таймаут, параллельность 3. Слова: WordBoundary; если Edge их не отдал — SentenceBoundary,
а время слов внутри предложения распределяется по длине слов (поле timing='sentence-interp')."""
import asyncio, json, os, re, subprocess, sys
from pathlib import Path
import edge_tts

JOB = Path('jobs/tts/roman_concrete.json'); OUT = Path('media/tts/roman_concrete'); OUT.mkdir(parents=True, exist_ok=True)
VOICE, RATE = 'ru-RU-DmitryNeural', '+4%'

def interp(sents):
    words = []
    for s in sents:
        toks = s['w'].split(); L = sum(len(t) + 1 for t in toks) or 1; cur = s['start']; span = s['end'] - s['start']
        for t in toks:
            d = span * (len(t) + 1) / L; words.append({'w': t, 'start': round(cur, 3), 'end': round(cur + d, 3)}); cur += d
    return words

async def stream(text, boundary, mp3):
    com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary=boundary)
    marks = []
    async with asyncio.timeout(60):
        with mp3.open('wb') as f:
            async for ch in com.stream():
                if ch['type'] == 'audio': f.write(ch['data'])
                elif ch['type'] in ('WordBoundary', 'SentenceBoundary'):
                    marks.append({'w': ch['text'], 'start': ch['offset'] / 1e7, 'end': (ch['offset'] + ch['duration']) / 1e7})
    assert mp3.stat().st_size > 2000, 'empty audio'
    return marks

async def synth(line):
    mp3, meta = OUT / f"{line['id']}.mp3", OUT / f"{line['id']}.json"
    if mp3.exists() and meta.exists():
        m = json.loads(meta.read_text())
        if m.get('text') == line['text'] and m.get('voice_id') == VOICE and m.get('rate') == RATE:
            print('cached', line['id'], flush=True); return True
    for a in range(14):
        boundary = 'WordBoundary' if a % 2 == 0 else 'SentenceBoundary'
        try:
            marks = await stream(line['text'], boundary, mp3)
            words, timing = (marks, 'word') if boundary == 'WordBoundary' and len(marks) > 3 else (interp(marks), 'sentence-interp')
            if not words: raise RuntimeError('no boundaries')
            dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp3)]))
            meta.write_text(json.dumps({'text': line['text'], 'words': words, 'timing': timing, 'speaker': 'dima', 'voice_id': VOICE,
                                        'engine': 'edge-tts', 'rate': RATE, 'pitch': '+0Hz', 'source_file': str(mp3), 'duration': dur}, ensure_ascii=False, indent=1))
            print('OK', line['id'], timing, round(dur, 1), flush=True); return True
        except Exception as e:
            mp3.unlink(missing_ok=True); print('RETRY', line['id'], a + 1, boundary, type(e).__name__, str(e)[:80], flush=True)
            await asyncio.sleep(min(15, 3 + a * 2))
    return False

async def main():
    lines = json.loads(JOB.read_text())['lines']
    sem = asyncio.Semaphore(3)
    async def one(l):
        async with sem: return await synth(l)
    rs = await asyncio.gather(*(one(l) for l in lines))
    print('RESULT', sum(rs), '/', len(rs), flush=True)
    sys.exit(0 if all(rs) else 1)

asyncio.run(main())
