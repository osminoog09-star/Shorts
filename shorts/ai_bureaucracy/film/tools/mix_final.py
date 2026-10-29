#!/usr/bin/env python3
"""Финальное сведение: видео из `om render` + речь (Дима/Света) + музыка/эффекты `om sound` с дакингом под речь.
Запуск из папки film:  python3 tools/mix_final.py out/<render>.mp4 ../../../videos/ai_bureaucracy_claude_ru.mp4
"""
import json, subprocess, sys
from pathlib import Path

FILM = Path(__file__).resolve().parent.parent
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
voice, bed = FILM / 'assets/voice/voice.wav', FILM / 'assets/sound.wav'
dur = json.loads((FILM / 'assets/voice/timeline.js').read_text()[11:-2])['total']

fc = (
    "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,loudnorm=I=-15:TP=-2:LRA=7,asplit=2[v][key];"
    "[2:a]aresample=48000,volume=0.62[bed];"
    # дакинг: под речью музыка/эффекты уходят примерно на 8–10 дБ, между репликами возвращаются
    "[bed][key]sidechaincompress=threshold=0.025:ratio=7:attack=12:release=320:makeup=1[duck];"
    "[v][duck]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,"
    f"atrim=0:{dur},afade=t=out:st={dur - 0.35}:d=0.35[a]"
)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-i', str(voice), '-i', str(bed),
                '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', str(dur), '-movflags', '+faststart', str(dst)], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-i', str(dst), '-f', 'null', '-'], check=True)   # полный decode
print('ok', dst)
