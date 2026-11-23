"""Громкость дорожек по файлам (EBU R128, интегральная с гейтом) -> gains.json: усиление Game/Mic/Discord, чтобы
голос Дениса ≈ -20 LUFS, друзья вровень с ним, игра на ~6 дБ тише голосов. Дорожки: a:1 Game, a:2 Mic, a:3 Discord."""
import json, re, subprocess, sys
from pathlib import Path
W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
sys.path.insert(0, str(W))
NAMES = __import__("analyze2_names").NAMES if __name__ == "__main__" else []
R = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings")

def lufs(f, tr):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-map", f"0:a:{tr}", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace").stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); p = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", r)
    return (float(i[-1]) if i else -70.0), (float(p[-1]) if p and p[-1] != "-inf" else -99.0)

TARGET_VOICE, GAME_UNDER = -20.0, 6.0
out = {}
for n in NAMES:
    f = R / (n + ".mkv")
    g, m, d = (lufs(f, t) for t in (1, 2, 3))
    gain = lambda lv, tgt, pk: round(min(10 ** ((tgt - lv) / 20), 10 ** ((-1.0 - pk) / 20)), 3) if lv > -69 else 1.0
    out[str(f)] = dict(game=gain(g[0], TARGET_VOICE - GAME_UNDER, g[1]), mic=gain(m[0], TARGET_VOICE, m[1]), discord=gain(d[0], TARGET_VOICE, d[1]),
                       raw=dict(game=g, mic=m, discord=d))
    print(Path(f).name, out[str(f)], flush=True)
if __name__ == "__main__": json.dump(out, open(W / "gains.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
