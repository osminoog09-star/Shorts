#!/usr/bin/env python3
"""Denis 07.11: «немного образовательным, чтобы и дети поняли — на все возраста».
Inserts short kid-friendly explanation beats (own frame each) + on-screen term cards (quote) into levels/*.json.
Order: chapters.py → extra_shots.py → edu.py. Idempotent."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPACE_NEG = "landscape, ground, horizon, mountains, desert, planet surface, terrain, boat, sea, water"
# after beat id: (new beat text, kind, frame prompt, term card or None, alias list or None)
INS = {
    "c1b06": ("Чтобы было понятнее: за одну секунду он пролетал расстояние, как через целый большой город.", "scene",
              "a big city seen from high above at night with a glowing streak crossing over it from one edge to the other in a single second, sense of speed, painting", "26 км за 1 секунду", None),
    "c2b03": ("Облако Оорта — это как огромная ледяная шуба вокруг Солнечной системы. Из неё к нам иногда падают кометы.", "space",
              "the solar system wrapped in a gigantic faint sphere of tiny icy specks like a snowy shell, the sun a small star in the center, deep space", "Облако Оорта — ледяная «шуба» Солнечной системы", None),
    "c2b04": ("Представь мяч, который катится мимо ямки. Медленный мяч упадёт в неё. Быстрый проскочит мимо и укатится навсегда. Наш гость был быстрым мячом.", "scene",
              "a ball rolling fast past a small round hole in a sandy playground, motion blur, warm sunset light, simple and clear illustration", "Гипербола — путь, который не замыкается", None),
    "c3b05": ("Возьми карандаш и покрути его перед фонариком. Тень становится то длинной, то короткой. Так и гость то вспыхивал, то тускнел.", "scene",
              "a child's hand rotating a pencil in front of a flashlight beam in a dark room, a long shadow on the wall, cozy, simple illustration", None, None),
    "c4b05": ("Это как если бы ты подбросил мяч, а он вдруг полетел чуть дальше, чем должен. Без ветра. Без толчка. Сам.", "scene",
              "a child throwing a ball high in a park at dusk, the ball flying slightly further along a glowing curved path, wonder, painting", "Ускорение без видимой причины", None),
    "c5b02": ("Свет давит на твою ладонь намного слабее, чем весит одна песчинка. Но в космосе нет воздуха и трения. И даже такой слабый толчок за много дней разгоняет лёгкий парус.", "scene",
              "an open palm in a beam of sunlight with a single grain of sand on it, dust particles in the light, macro, warm, gentle", "Давление света", None),
    "c6b13": ("Космические лучи — это крошечные частицы, которые носятся по галактике почти со скоростью света. За миллионы лет они меняют даже лёд.", "space",
              "tiny glowing particles streaking through the galaxy at enormous speed like rain of light, black space, stars", "Космические лучи", None),
    "c7b03": ("Кстати, у межзвёздных гостей есть свои номера. Первый — Оумуамуа. Второй — Борисов. Как первые гости в большой книге посещений.", "scene",
              "an old leather guest book open on a wooden desk with a quill pen, starlight falling on the pages from a window, cozy, no readable text", "1I · 2I · 3I", ["Кстати, у межзвёздных гостей есть свои номера. Первый — Умуамуа. Второй — Борисов. Как первые гости в большой книге посещений."]),
}
QUOTE = {  # existing beats: term card only
    "c3b14": "Спитцер — телескоп, который видит тепло",
    "c4b10": "Кома — облако газа и пыли вокруг кометы",
    "c8b11": "Оумуамуа — «посланник издалека, прибывший первым»",
}
for c in ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"]:
    p = HERE / "levels" / f"{c}.json"; j = json.loads(p.read_text(encoding="utf-8")); ids = {b["id"] for b in j["beats"]}
    for after, (text, kind, prompt, card, alias) in INS.items():
        if not after.startswith(c + "b") or after + "e" in ids: continue
        i = next(k for k, b in enumerate(j["beats"]) if b["id"] == after)
        sid = f"{c}_e{after[-2:]}"; s = {"id": sid, "seed": 3000 + int(c[1]) * 100 + int(after[-2:]), "prompt": prompt, "layers": ["dust"]}
        if kind == "space": s["neg"] = SPACE_NEG
        j["shots"].append(s)
        b = {"id": after + "e", "shot": sid, "text": text}
        if card: b["quote"] = card
        if alias: b["alias"] = alias
        j["beats"].insert(i + 1, b)
    for b in j["beats"]:
        if b["id"] in QUOTE: b["quote"] = QUOTE[b["id"]]
    p.write_text(json.dumps(j, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("edu beats", len(INS), "term cards", len(QUOTE))
