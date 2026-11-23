"""killscan/*.tsv -> events.json: события (файл, локальная сек., тип) + серии убийств (кластеры)."""
import json, re
from pathlib import Path
W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
REC = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings\Вардокс")
RULES = [("teamkill", r"СВОЕГО"), ("headshot", r"ГОЛОВ"), ("revenge", r"ОТМЕСТК"), ("vehicle", r"УНИЧТОЖ\w*\s*(ОБНАРУЖ\w*\s*)?ТРАНСП|УНИЧ.{0,6}Ж.{0,12}ТРАНСП"),
         ("assist", r"ПОМОЩ|ОМРЩ|ОМОЩ|МО.?Щ|ЩЬ\s*В|В\s*УБИ.?СТВЕ"), ("kill", r"УБИ.?СТВ[ОУ]|УЖ.?СТВО"), ("equip", r"ЭКИПИР"), ("supply", r"ПРИПАС.*УНИЧТ|ПРИПКЫ"),
         ("capture", r"ЗАХВАТ|ЗАХВАЧ|НЕЙТРАЛИЗ")]
ev = []
other = {}
for tsv in sorted((W / "killscan").glob("*.tsv")):
    last = {}
    for line in tsv.read_text(encoding="utf-8").splitlines():
        sec, txt = line.split("\t", 1); sec = float(sec); up = txt.upper()
        for typ, rx in RULES:
            if re.search(rx, up):
                if sec - last.get(typ, -99) > 4.5:  # та же плашка видна на 2 ключевых кадрах подряд
                    ev.append(dict(stem=tsv.stem, t=sec, type=typ, text=txt))
                last[typ] = sec
                break
        else:
            if "ZONE" in up and "ПРИСУТ" not in up and "ВХОД" not in up: other[txt] = other.get(txt, 0) + 1
# серии: убийства/хедшоты/отместка/техника в пределах 25 с одного файла
KILL = {"kill", "headshot", "revenge", "vehicle"}
ser, cur = [], []
for e in [e for e in ev if e["type"] in KILL]:
    if cur and (e["stem"] != cur[-1]["stem"] or e["t"] - cur[-1]["t"] > 25):
        ser.append(cur); cur = []
    cur.append(e)
if cur: ser.append(cur)
json.dump(dict(events=ev, series=[[dict(stem=s[0]["stem"], t0=s[0]["t"], t1=s[-1]["t"], n=len(s), types=[x["type"] for x in s])] for s in ser]),
          open(W / "events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
from collections import Counter
print(Counter(e["type"] for e in ev))
print("по файлам:", Counter(e["stem"][5:] for e in ev if e["type"] in KILL))
print("серии >=2:")
for s in ser:
    if len(s) >= 2: print(f'  {s[0]["stem"][5:]} {s[0]["t"]:.0f}-{s[-1]["t"]:.0f}s  x{len(s)} {[x["type"] for x in s]}')
print("прочее ZONE:", sorted(other.items(), key=lambda x: -x[1])[:15])
