"""Громкость + wav (мик/Discord 16 кГц) для дополнительных файлов: gains2.py <stem> ... -> дописывает gains.json, wav/<stem>_{mic,discord}.wav"""
import json, sys, subprocess
from pathlib import Path
from gains import lufs, TARGET_VOICE, GAME_UNDER  # noqa (gains.py при импорте не выполняет цикл — см. guard ниже)
W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
REC = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings\Вардокс")
G = json.load(open(W / "gains.json", encoding="utf-8"))
for stem in sys.argv[1:]:
    f = REC / (stem + ".mkv")
    if str(f) not in G:
        g, m, d = (lufs(f, t) for t in (1, 2, 3))
        gain = lambda lv, tgt, pk: round(min(10 ** ((tgt - lv) / 20), 10 ** ((-1.0 - pk) / 20)), 3) if lv > -69 else 1.0
        G[str(f)] = dict(game=gain(g[0], TARGET_VOICE - GAME_UNDER, g[1]), mic=gain(m[0], TARGET_VOICE, m[1]), discord=gain(d[0], TARGET_VOICE, d[1]),
                         raw=dict(game=g, mic=m, discord=d))
        print(stem, G[str(f)], flush=True)
    for tr, who in ((2, "mic"), (3, "discord")):
        out = W / "wav" / f"{stem}_{who}.wav"
        if not out.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-map", f"0:a:{tr}", "-ac", "1", "-ar", "16000", str(out)], check=True)
    json.dump(G, open(W / "gains.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
