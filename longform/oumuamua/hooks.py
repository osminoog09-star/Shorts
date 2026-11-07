#!/usr/bin/env python3
"""Denis 07.11 «Да, вставляй»: retention edits from reports/research/2026-11-07_oumuamua_audit.md §5–6.
New 25 s cold-open hook, chapter-end hooks, viewer question, «сделай сам», version counter cards, subscribe ask at the peak, comment poll.
Order: chapters.py → extra_shots.py → edu.py → hooks.py → pron.py. Idempotent."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPACE_NEG = "landscape, ground, horizon, mountains, desert, planet surface, terrain, boat, sea, water"
S, N = "space", "scene"
# (chapter, insert after beat id or None = at start, new beat id, text, kind, prompt, extra)
ADD = [
    ("c0", None, "c0a01", "В октябре две тысячи семнадцатого через нашу Солнечную систему пролетел объект, который нарушил законы физики.", S,
     "a dramatic close view of an elongated dark red cigar shaped asteroid flying past the blazing sun, lens flare, stars, cinematic, awe", {"alias": ["В октябре 2017 через нашу Солнечную систему пролетел объект, который нарушил законы физики.", "В октябре 2017 года через нашу Солнечную систему пролетел объект, который нарушил законы физики."]}),
    ("c0", "c0a01", "c0a02", "Он ускорялся, хотя его ничто не толкало. У него не было хвоста. И формы, как у него, мы не видели никогда.", S,
     "an elongated reddish asteroid accelerating away from the sun with glowing speed lines, no tail, no gas, black space, mysterious", {}),
    ("c0", "c0a02", "c0a03", "Одни учёные называют его ледяным осколком. Другие — обломком чужого корабля.", S,
     "split composition in deep space: on the left a translucent icy shard, on the right a dark broken alien spacecraft fragment, stars, dramatic", {}),
    ("c0", "c0a03", "c0a04", "К концу этого фильма ты сам решишь, кто прав.", S,
     "a lone dark elongated object drifting toward the viewer out of a glowing nebula, stars, cinematic, invitation, mysterious", {}),
    ("c2", "c2b19", "c2b19k", "Но пока он уходил, астрономы успели заметить в нём кое-что ещё более странное. Его форму.", S,
     "a dark elongated asteroid silhouette against a bright star field, its strange shape outlined by thin light, black space, intrigue", {}),
    ("c3", "c3b05e", "c3b05k", "Можешь поставить видео на паузу и попробовать сам. Это работает.", N,
     "a child at a desk at night holding a pencil in front of a flashlight, a long shadow on the wall, playful, cozy, warm lamp", {}),
    ("c5", "c5b17", "c5b17k", "Если тебе тоже интересно, кто прилетит к нам следующим, — подпишись. Мы будем следить за межзвёздными гостями вместе.", N,
     "a cozy observatory dome at night with its slit open to a sky full of stars, warm light inside, inviting, painting", {}),
    ("c6", None, "c6a00", "А как думаешь ты? Что могло бы ускоряться без видимой причины? Запомни свой ответ. И сравни с тем, что придумали учёные.", N,
     "a curious child looking up at the night sky from a window, stars reflected in the eyes, thoughtful, warm room light", {}),
    ("c7", "c7b16", "c7b16k", "А теперь самое главное. Что всё это значит для нас?", S,
     "the earth seen from far away as a small blue dot with a faint stream of tiny visitors passing by, deep space, contemplative", {}),
    ("c8", "c8b12", "c8b12k", "А ты как думаешь, чем он был? Камень, лёд или корабль? Напиши в комментариях. Мне правда интересно.", N,
     "three objects on a dark table under a lamp: a small rock, a piece of ice and a tiny toy spaceship, playful still life, warm light", {}),
]
VERSION_CARD = {"c6b01": "Версия 1 из 4 · водородный айсберг", "c6b05": "Версия 2 из 4 · осколок чужого Плутона",
                "c6b10": "Версия 3 из 4 · пушистый комок пыли", "c6b12": "Версия 4 из 4 · водород в обычном льду"}

for c in sorted({a[0] for a in ADD} | {"c6"}):
    p = HERE / "levels" / f"{c}.json"; j = json.loads(p.read_text(encoding="utf-8"))
    ids = {b["id"] for b in j["beats"]}; sids = {s["id"] for s in j["shots"]}
    for ch, after, bid, text, kind, prompt, extra in ADD:
        if ch != c or bid in ids: continue
        sid = f"{c}_k{bid[-3:]}"
        if sid not in sids:
            s = {"id": sid, "seed": 4000 + int(c[1]) * 100 + len(sids), "prompt": prompt, "layers": ["dust"]}
            if kind == S: s["neg"] = SPACE_NEG
            j["shots"].append(s); sids.add(sid)
        b = {"id": bid, "shot": sid, "text": text, **extra}
        i = 0 if after is None else next(k for k, x in enumerate(j["beats"]) if x["id"] == after) + 1
        if after is None:   # keep several «at start» inserts in their given order
            while i < len(j["beats"]) and j["beats"][i]["id"] in {a[2] for a in ADD if a[0] == c}: i += 1
        j["beats"].insert(i, b); ids.add(bid)
    for b in j["beats"]:
        if b["id"] in VERSION_CARD: b["quote"] = VERSION_CARD[b["id"]]
    p.write_text(json.dumps(j, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("inserted", len(ADD), "beats; version cards", len(VERSION_CARD))
