"""Манифесты для заливки Wardogs-3 (PRIVATE, без даты) → JSON в папке out (publishing/queue в worktree)."""
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
NCS = lambda art, name, slug: f"Track: {art} - {name} [NCS Release]\nMusic provided by NoCopyrightSounds\nFree Download/Stream: http://ncs.io/{slug}"
TAGS = ["wardogs", "wardogs игра", "тактический шутер", "хедшоты", "смешные моменты", "приколы в играх", "с друзьями", "вертолёт", "M1lash"]
PH, GOD, CR, JOY, TU, IMH, RED = (("HXDES, DYNAMIS", "Kapoeira Phonk", "kapoeiraphonk"), ("1$K1", "GODSLAYER", "godslayer"),
    ("Dosi, Aisake", "Cruising", "cruising"), ("Jensation", "Joystick", "jenjoystick"), ("Anikdote", "Turn It Up", "turnitup"),
    ("T-Mass", "Ignoring My Heart", "ignoringmyheart"), ("ANIZYZ", "THE REDEEMER", "theredeemer"))
ep_desc = """Неделя в Wardogs с пацанами: хедшоты, один больше не летает после первого вертолёта, второй впервые садится за штурвал и обещает научиться, а Бист орёт на всех — потому что он просто очень эмоциональный игрок. И добрый самый.

0:00 Хук
0:27 Разминка
1:13 Глава 1 · «Я не пилот»
2:38 Глава 2 · Заходит Бист
7:25 Глава 3 · «Я научусь»
10:14 Глава 4 · Лучшее за неделю

Музыка:
""" + "\n\n".join(NCS(*t) for t in (PH, GOD, CR, JOY, TU, IMH, RED)) + "\n\n#wardogs #m1lash"
sh = lambda title, line, trk: dict(type="short", title=title, description=f"{line}\n\n" + NCS(*trk) + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"])
ITEMS = {
    "wardogs3_ep": dict(type="long", title="ОЧЕНЬ ЭМОЦИОНАЛЬНЫЙ ИГРОК — Wardogs с друзьями", description=ep_desc, tags=TAGS),
    "wardogs3_short_headshots": sh("Хедшот за хедшотом 🎯 #wardogs #shorts", "Неделя в Wardogs — только хедшоты.", GOD),
    "wardogs3_short_emo": sh("«Я просто очень эмоциональный игрок» 😤 #wardogs #shorts", "Сначала орёт на своего за гранаты, через полчаса — объясняет.", PH),
    "wardogs3_short_nick": sh("«Тебя я могу только типом назвать» #wardogs #shorts", "Ник себе поставь — иероглифы никто читать не умеет.", PH),
    "wardogs3_short_pilot": sh("«Я не пилот. Я больше не летаю» 🚁 #wardogs #shorts", "Один раз купил вертолёт — и всё.", CR),
    "wardogs3_short_learn": sh("«Я научусь летать на этой штуке» #wardogs #shorts", "Первый полёт друга: «он очень инертный».", IMH),
    "wardogs3_short_kind": sh("«Я вообще не злой. Я добрый самый» #wardogs #shorts", "Бист всех напасалал — все обиделись.", JOY),
}
for k, v in ITEMS.items():
    assert len(v["title"]) <= 100 and len(v["description"]) <= 5000
    m = {"channel": "ru", "metadata": {"type": v["type"], "title": v["title"], "description": v["description"], "tags": v["tags"],
         "category_id": "20", "made_for_kids": False, "contains_synthetic_media": False}, "publish_at": None}
    (out / f"{k}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(k, len(v["title"]))
