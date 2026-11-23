"""Shorts 1080x1920 из сессии Wardogs 22–23.11. Субтитры — автоматически по subs.json (вся речь)."""
import sys
from ep1 import CALM, CHASE, FUN, PHONK, GOD, K
from edit import build, seg_dur


def clip(a, b, k="n", **kw):
    d = dict(a=a, b=b, k=k, cap=kw.pop("cap", []), **kw)
    d.setdefault("mus", 0.6)
    return d


SHORTS = {
    "short_headshots": dict(top="ХЕДШОТ\nЗА ХЕДШОТОМ", music=GOD, seg=[
        K(16, pre=3.0, post=1.0, ml=6), K(19, pre=3.0, post=-0.1, ml=6), K(22, pre=3.0, post=1.0, ml=6),
        K(48, pre=3.0, post=1.0, ml=6), K(52, pre=3.0, post=1.0, ml=6), K(39, pre=3.0, post=1.0, ml=6),
        K(9, pre=3.0, post=1.0, ml=6), K(12, pre=3.0, post=1.0, ml=6), K(34, pre=3.0, post=1.0, ml=6),
    ]),
    "short_nick": dict(top="«ТЕБЯ Я МОГУ\nТОЛЬКО ТИПОМ НАЗВАТЬ»", music=PHONK, seg=[
        clip("21:53:14.4", "21:53:25.0", va="21:47:05.0"),
        clip("21:53:31.0", "21:53:50.0", va="21:47:28.5"),
    ]),
    "short_emo": dict(top="«Я ПРОСТО ОЧЕНЬ\nЭМОЦИОНАЛЬНЫЙ ИГРОК»", music=PHONK, seg=[
        clip("21:51:58.5", "21:52:22.2"),
        dict(k="card", dur=1.4, bg="22:21:10.0", cap=[(0.0, 1.4, "через полчаса…", "card")]),
        clip("22:23:03.0", "22:23:26.0", zin=1),
    ]),
    "short_pilot": dict(top="«Я НЕ ПИЛОТ.\nЯ БОЛЬШЕ НЕ ЛЕТАЮ»", music=CALM, seg=[
        clip("20:42:36.6", "20:43:05.4", va="20:43:20.0"),
        clip("20:44:17.5", "20:44:36.5"),
    ]),
    "short_learn": dict(top="«Я НАУЧУСЬ\nЛЕТАТЬ»", music=CHASE, seg=[
        clip("23:04:20.4", "23:04:24.3"),
        clip("23:09:52.4", "23:10:05.8"),
        clip("23:13:22.6", "23:13:26.4"),
        clip("23:18:09.0", "23:18:15.6"),
        clip("23:21:48.8", "23:21:57.2", va="23:17:42.0"),
    ]),
    "short_kind": dict(top="«Я ВООБЩЕ НЕ ЗЛОЙ.\nЯ ДОБРЫЙ САМЫЙ»", music=FUN, seg=[
        clip("22:28:15.5", "22:28:37.0"),
        clip("22:34:55.4", "22:35:07.5"),
    ]),
}

if __name__ == "__main__":
    for n in ([x for x in sys.argv[1:] if not x.startswith("--")] or list(SHORTS)):
        sh = SHORTS[n]
        print(n, round(sum(seg_dur(s) for s in sh["seg"]), 1), "с")
        if "--dry" not in sys.argv:
            build(n, sh["seg"], V=True, music=sh["music"], mus_vol=0.05, top=sh["top"])
