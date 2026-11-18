"""Манифесты publishing/queue/*.json для 6 роликов Wardogs (PRIVATE, без даты)."""
import json
from pathlib import Path
Q = Path(r"C:\M1lash\Shorts\publishing\queue")
NCS = lambda art, name, slug: f"Track: {art} - {name} [NCS Release]\nMusic provided by NoCopyrightSounds\nFree Download/Stream: http://ncs.io/{slug}"
TAGS = ["wardogs", "wardogs игра", "wardogs геймплей", "тактический шутер", "смешные моменты", "приколы в играх", "с друзьями", "M1lash"]

ep_desc = """Три с половиной часа Wardogs с пацанами из дискорда, ужатые до 23 минут. Нас выгнали с сервера за слишком высокий уровень, я всадил другу шесть пуль в спину, мы угнали Урал, посадили вертушку на пень, а Алиса так и не выключила свет.

0:00 Хук
0:28 Глава 1 · Разминка (нас выгнали с сервера)
1:31 Глава 2 · Отель
2:44 Глава 3 · Дружественный огонь
4:00 Глава 4 · Вертушка и пень
5:46 Глава 5 · Урал
9:08 Глава 6 · За красных
15:39 Глава 7 · Завод
17:48 Глава 8 · База и Алиса
20:02 Финал · Оборона базы

Музыка:
""" + "\n\n".join([NCS("ANIZYZ", "THE REDEEMER", "theredeemer"), NCS("1$K1", "GODSLAYER", "godslayer"),
                   NCS("HXDES, DYNAMIS", "Kapoeira Phonk", "kapoeiraphonk"), NCS("Grioten, XI$OW", "Rally Up!", "rallyup"),
                   NCS("Strybo", "Curse", "curse"), NCS("Emin Nilsen", "VIDA NOVA", "vidanova"),
                   NCS("THIRST", "fellshortofhell", "fellshortofhell")]) + "\n\n#wardogs #m1lash"

ITEMS = {
    "wardogs_ep1": dict(type="long", title="Я РАССТРЕЛЯЛ ДРУГА, УГНАЛ УРАЛ И РАЗБИЛ ВЕРТУШКУ О ПЕНЬ — Wardogs",
                        description=ep_desc, tags=TAGS + ["дружественный огонь", "вертолёт", "урал"]),
    "wardogs_short_friendly_fire": dict(type="short", title="Шесть хитов в спину. Другу. 💀 #wardogs #shorts",
        description="Он просто вышел пикнуть…\n\n" + NCS("Emin Nilsen", "BANE", "bane") + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"]),
    "wardogs_short_ural": dict(type="short", title="«Это мой Урал, и я на нём еду!» #wardogs #shorts",
        description="Угон века.\n\n" + NCS("HXDES, DYNAMIS", "Kapoeira Phonk", "kapoeiraphonk") + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"]),
    "wardogs_short_give_me_driver": dict(type="short", title="Give me driver. GIVE ME DRIVER. #wardogs #shorts",
        description="Международные переговоры за руль.\n\n" + NCS("MXRCVRY", "AYUDA", "ayuda") + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"]),
    "wardogs_short_heli_stump": dict(type="short", title="Вертушка против пня: 0:1 #wardogs #shorts",
        description="Посадка на 5 баллов. Из 100.\n\n" + NCS("1$K1", "GODSLAYER", "godslayer") + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"]),
    "wardogs_short_alisa": dict(type="short", title="Алиса, выключи свет. АЛИСА. #wardogs #shorts",
        description="Умный дом против геймера.\n\n" + NCS("MUPP", "X2", "muppx2") + "\n\n#shorts #wardogs #m1lash", tags=TAGS + ["shorts"]),
}
for k, v in ITEMS.items():
    m = {"channel": "ru", "metadata": {"type": v["type"], "title": v["title"], "description": v["description"],
         "tags": v["tags"], "category_id": "20", "made_for_kids": False, "contains_synthetic_media": False}, "publish_at": None}
    assert len(v["title"]) <= 100 and len(v["description"]) <= 5000
    (Q / f"{k}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(k, len(v["title"]), len(v["description"]))
