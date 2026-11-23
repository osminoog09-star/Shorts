"""Серия Wardogs 22–23.11.2026 «Очень эмоциональный игрок» v2: разговоры + мои убийства (лента наград OCR, kills.json) под музыку.
Время глобальное (0:00 = 22.11 02:25:17; записи 19–20.11 — от 55:30:00). Нарезки убийств: k=n, ml — во сколько раз громче музыка."""
import json, sys
from pathlib import Path
from edit import build, seg_dur
from src import hms as _h, W

CALM, CHASE, FUN, PHONK, EPIC = "ncs/cruising.mp3", "ncs/ignoringmyheart.mp3", "ncs/jenjoystick.mp3", "ncs/kapoeiraphonk.mp3", "ncs/turnitup.mp3"
GOD, RED = "ncs/godslayer.mp3", "ncs/theredeemer.mp3"
KJ = {e["i"]: e for e in json.load(open(W / "kills.json", encoding="utf-8"))}
LAB = {"headshot": "ХЕДШОТ", "revenge": "В ОТМЕСТКУ", "vehicle": "ТЕХНИКА", "teamkill": "…ПО СВОЕМУ"}


def ts(g):
    return f"{int(g // 3600)}:{int(g % 3600 // 60):02d}:{g % 60:06.3f}"


def K(i, pre=6.5, post=1.0, trk=GOD, ml=6.0, j=None, **kw):
    """Нарезка убийства #i (по kills.json): pre с до появления плашки награды, post после. j — второй номер, чтобы взять серию одним куском."""
    e = KJ[i]; g0 = e["g"] - pre; g1 = (KJ[j]["g"] if j is not None else e["g"]) + post
    cap = kw.pop("cap", [])
    for x in ([i] + ([j] if j is not None else [])):
        lab = LAB.get(KJ[x]["type"])
        if lab: cap.append((f"@{ts(KJ[x]['g'] - 0.6)}", 1.3, lab, "big"))
    return dict(a=ts(g0), b=ts(g1), k="n", trk=trk, ml=ml, cap=cap, **kw)


SEG = [
    # ===== ХУК
    K(16, pre=2.6, post=0.8, trk=PHONK, ml=5),
    K(19, pre=2.8, post=-0.7, trk=PHONK, ml=5),
    dict(a="22:23:06.0", b="22:23:12.4", k="n", zin=1, trk=PHONK),
    dict(a="21:53:16.0", b="21:53:24.7", k="n", va="22:21:03.0", trk=PHONK),
    dict(a="23:04:20.4", b="23:04:24.3", k="n", trk=PHONK, cap=[(0.0, 3.9, "а это — другой друг. И вертолёт", "low")]),
    dict(k="card", dur=2.8, bg="20:43:40.0", cap=[(0.0, 2.8, "WARDOGS\nочень эмоциональный игрок", "card")]),

    # ===== РАЗМИНКА: убийства вечера 22.11
    K(26, cap=[(0.2, 3.4, "РАЗМИНКА", "chap")]),
    K(27), K(28, j=29), K(30, pre=7.0, post=-0.6), K(32, post=-0.6), K(33, post=-0.6),

    # ===== ГЛАВА 1 · «Я НЕ ПИЛОТ»
    dict(a="20:42:36.6", b="20:43:05.4", k="n", va="20:43:20.0", trk=CALM, cap=[(0.2, 3.6, "ГЛАВА 1 · «Я НЕ ПИЛОТ»", "chap")]),
    dict(a="20:43:55.0", b="20:44:00.6", k="n", trk=CALM),
    dict(a="20:44:15.5", b="20:44:42.5", k="n", trk=CALM),
    dict(a="20:46:11.8", b="20:46:20.4", k="n", trk=GOD, ml=4, cap=[("@20:46:18.6", 1.3, "ХЕДШОТ", "big")]),
    K(35), K(36),

    # ===== ГЛАВА 2 · БИСТ
    dict(a="21:21:40.0", b="21:21:59.9", k="n", trk=FUN, cap=[(0.2, 3.6, "ГЛАВА 2 · ЗАХОДИТ БИСТ", "chap")]),
    K(37, trk=FUN, ml=3),
    K(38, trk=PHONK), K(39, trk=PHONK),
    dict(a="21:51:58.5", b="21:52:28.0", k="n", trk=PHONK, cap=[(0.0, 2.8, "свой кидает гранаты под ноги", "low")]),
    dict(a="21:53:02.0", b="21:53:25.0", k="n", va="21:47:05.0", trk=PHONK),
    dict(a="21:53:31.0", b="21:53:50.0", k="n", va="21:47:28.5", trk=PHONK),
    K(41, j=42, trk=PHONK),
    dict(a="22:06:16.0", b="22:06:33.0", k="n", va="22:06:25.0", trk=EPIC, cap=[(0.0, 2.6, "выиграли раунд", "low")]),
    K(43, trk=EPIC),
    dict(a="22:21:00.0", b="22:21:38.0", k="n", trk=EPIC),
    dict(a="22:22:57.0", b="22:23:28.0", k="n", zin=1, trk=FUN, cap=[(0.0, 2.6, "разбор полётов", "low")]),
    dict(a="22:27:12.5", b="22:27:28.8", k="n", trk=FUN),
    dict(a="22:28:15.5", b="22:28:37.0", k="n", trk=FUN),
    dict(a="22:34:52.4", b="22:35:13.9", k="n", trk=FUN),

    # ===== ГЛАВА 3 · «Я НАУЧУСЬ»
    K(44, trk=CHASE, cap=[(0.2, 3.4, "ГЛАВА 3 · «Я НАУЧУСЬ»", "chap")]), K(47, trk=CHASE), K(48, pre=4.6, trk=CHASE),
    dict(a="23:02:07.5", b="23:02:20.0", k="n", trk=CHASE, cap=[(0.2, 3.0, "друг впервые садится за вертолёт", "low")]),
    dict(a="23:04:09.0", b="23:04:24.3", k="n", trk=CHASE),
    K(49, trk=CHASE),
    dict(a="23:09:02.0", b="23:09:08.0", k="n", trk=CHASE, cap=[(0.0, 2.6, "я внизу, строю. Он — в воздухе", "low")]),
    dict(a="23:09:46.0", b="23:10:24.6", k="n", trk=CHASE),
    dict(a="23:13:10.0", b="23:13:26.6", k="n", trk=CHASE),
    K(50, trk=CHASE),
    dict(a="23:18:04.8", b="23:18:15.6", k="n", trk=CHASE),
    dict(a="23:21:46.5", b="23:22:08.6", k="n", va="23:17:42.0", trk=CALM),
    dict(a="23:24:37.5", b="23:24:49.5", k="n", trk=CALM),

    # ===== ГЛАВА 4 · ЛУЧШЕЕ ЗА НЕДЕЛЮ (19–23.11)
    K(1, trk=RED, cap=[(0.2, 3.4, "ГЛАВА 4 · ЛУЧШЕЕ ЗА НЕДЕЛЮ", "chap")]),
    K(3, trk=RED, ml=3), K(6, trk=RED), K(9, trk=RED), K(12, trk=RED), K(13, trk=RED), K(15, trk=RED),
    K(22, trk=RED), K(24, j=25, trk=RED), K(52, trk=RED), K(53, trk=RED), K(54, trk=RED), K(55, trk=RED), K(57, trk=RED),
    dict(k="card", dur=5.0, bg="20:43:40.0", cap=[(0.0, 5.0, "ИТОГ:\n«больше не летаю» — сказал один\n«я научусь» — сказал другой\nБист — добрый самый", "card")]),
]

for _s in SEG:
    if _s["k"] == "n" and "mus" not in _s:
        _s["mus"] = 0.2

if __name__ == "__main__":
    print(f"план: {len(SEG)} сегментов, {sum(seg_dur(s) for s in SEG)/60:.1f} мин")
    if "--dry" not in sys.argv:
        build("ep1", SEG, V=False, mus_vol=0.05)
