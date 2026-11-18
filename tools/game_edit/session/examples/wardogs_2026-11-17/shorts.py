"""Shorts 1080x1920 из той же сессии. Титры (@-глобальные) подтягиваются из ep1 по попаданию во временное окно."""
import sys
from ep1 import SEG as EP
from edit import build, seg_dur
from src import hms

CAPS = [c for s in EP for c in s.get("cap", []) if isinstance(c[0], str) and c[0].startswith("@")]


def clip(a, b, k="n", **kw):
    A, B = hms(a), hms(b)
    caps = [c for c in CAPS if A <= hms(c[0][1:]) < B]
    seen, uniq = set(), []
    for c in caps:
        if c[0] not in seen: seen.add(c[0]); uniq.append(c)
    d = dict(a=a, b=b, k=k, cap=uniq + kw.pop("cap", []), **kw)
    if A < 1800: d["bright"] = 0.05
    d.setdefault("mus", 0.6)  # тихая подложка NCS под речью
    return d


SHORTS = {
    "short_friendly_fire": dict(top="ДРУЖЕСТВЕННЫЙ ОГОНЬ", music="ncs/bane.mp3", seg=[
        clip("0:28:30.0", "0:28:39.5", sfx=[(8.0, "riser", -10)]),
        dict(a="0:28:39.5", b="0:28:41.5", k="s", sp=0.4, zoom=1, bright=0.05, sfx=[(0.0, "boom", -3)],
             cap=[(0.0, 5.0, "ЭТО БЫЛ\nМОЙ ДРУГ", "big")]),
        clip("0:28:41.5", "0:29:11.0"),
        clip("0:29:27.0", "0:29:33.0", freeze=1.5, frsfx="fail"),
    ]),
    "short_ural": dict(top="УГНАЛИ УРАЛ", music="ncs/kapoeiraphonk.mp3", seg=[
        clip("0:34:13.0", "0:34:23.0"),
        clip("0:35:36.0", "0:35:50.0", zoom=1, sfx=[(0.0, "whoosh", -6)]),
        clip("0:39:03.0", "0:39:11.0", freeze=1.2, frsfx="ding"),
    ]),
    "short_give_me_driver": dict(top="КОГДА ТИММЕЙТ\nНЕ ДАЁТ РУЛЬ", music="ncs/ayuda.mp3", seg=[
        clip("2:34:28.0", "2:34:35.0"),
        clip("2:34:51.0", "2:35:09.5", freeze=1.2, frsfx="fail"),
    ]),
    "short_heli_stump": dict(top="ВЕРТУШКА VS ПЕНЬ", music="ncs/godslayer.mp3", seg=[
        clip("0:31:56.5", "0:32:21.0"),
        clip("0:32:38.0", "0:33:03.5", freeze=1.3, frsfx="fail"),
    ]),
    "short_alisa": dict(top="АЛИСА ПРОТИВ ГЕЙМЕРА", music="ncs/muppx2.mp3", seg=[
        clip("0:23:43.0", "0:23:58.3"),
        dict(k="card", dur=1.6, bg="2:24:30.0", cap=[(0.0, 1.6, "2 часа спустя…", "card")], sfx=[(0.0, "scratch", -6)]),
        clip("2:24:47.0", "2:25:00.5", freeze=1.2, frsfx="fail"),
    ]),
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(SHORTS)
    for n in names:
        sh = SHORTS[n]
        print(n, round(sum(seg_dur(s) for s in sh["seg"]), 1), "с")
        build(n, sh["seg"], V=True, music=sh["music"], mus_vol=0.12, top=sh["top"])



