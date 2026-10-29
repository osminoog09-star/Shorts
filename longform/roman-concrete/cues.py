#!/usr/bin/env python3
"""cues.json для audio.py: голос Димы по сценам, лицензированные подложки Kevin MacLeod (CC BY 4.0) по главам, SFX по словам."""
import json, re, subprocess
VO = 0.6
TL = json.load(open("timeline.json")); total = TL["duration"]
ST = {x["id"]: x["start"] for x in TL["scenes"]}
TTS = "../../media/tts/roman_concrete/"
voice = [{"file": f"{TTS}{x['id']}.mp3", "at": round(x["start"] + VO, 3)} for x in TL["scenes"]]
WORDS = {x["id"]: json.load(open(f"{TTS}{x['id']}.json"))["words"] for x in TL["scenes"]}
def W(sid, word, nth=0, off=0.0):
    k = 0
    for w in WORDS[sid]:
        parts = w["w"].split(); L = len(w["w"]) or 1; pos = 0
        for p in parts:
            at = w["w"].find(p, pos); pos = at + len(p)
            if re.sub(r'[«»"\',.!?:;—…()]', '', p.lower()).startswith(word):
                if k == nth: return round(ST[sid] + VO + w["start"] + ((at / L) * (w["end"] - w["start"]) if len(parts) > 1 else 0) + off, 3)
                k += 1
    return None
sfx = []
def add(name, sid, word=None, g=0.6, nth=0, off=0.0, at=None):
    t = (round(ST[sid] + at, 3) if at is not None else W(sid, word, nth, off))
    if t is not None: sfx.append({"name": name, "at": t, "gain": g})
# главы: шорох перехода + мягкий аккорд
for sid in ["s03", "s04c", "s06", "s09", "s10c", "s12", "s13", "s13c"]:
    add("whoosh", sid, at=0.05, g=0.45); add("ding", sid, at=0.5, g=0.3)
add("pop", "s01", "нём", 0.5); add("bam", "s01", "современные", 0.25); add("riser", "s01", "конце", 0.3, off=-1.0); add("chord", "s01", "помпеях", 0.45)
for w in ["купол", "ржавеет", "английский", "буром", "помпеях", "мифа"]: add("pop", "s02", w, 0.45)
add("bam", "s03b", "агриппа", 0.3, off=0.4); add("crunch", "s03b", "сгорел", 0.4); add("pop", "s03b", "клеймам", 0.4); add("scan", "s03b", "пустоты", 0.4)
add("crunch", "s03b", "трещины", 0.5); add("ding", "s03b", "треснул", 0.45); add("chord", "s03b", "блестел", 0.3)
for k in range(10): add("tick", "s03b", "урбан", 0.3, off=0.6 + k * 0.2)
add("ding", "s03b", "ходила", 0.4)
add("splash", "s04", "волны", 0.4); add("splash", "s04b", "море", 0.35)
add("thunder", "s04c", "великая", 0.8); add("crunch", "s04c", "снесла", 0.5); add("whoosh", "s04c", "сгорел", 0.4); add("bubbles", "s04c", "опыты", 0.5, off=2.0)
add("ding", "s04c", "гидравлическую", 0.45); add("pop", "s04c", "гранитных", 0.3)
add("riser", "s04c", "шестнадцатого", 0.35, off=-0.5); add("chord", "s04c", "зажёгся", 0.5); add("whoosh", "s04c", "плимуте", 0.4)
add("crunch", "s05", "лопается", 0.5); add("crunch", "s05b", "распирает", 0.5); add("scan", "s05b", "замкнутый", 0.3)
for k in range(8): add("tick", "s05b", "двенадцати", 0.3, off=k * 0.15)
add("thunder", "s06b", "пепел", 0.25); add("scan", "s06b", "встречает", 0.35); add("ding", "s06b", "пуццоланами", 0.45); add("splash", "s06b", "возили", 0.35)
add("bam", "s06c", "цемент", 0.3, nth=1)
# монтажный взрыв: удар на каждую склейку (кадры в scenes_c.js: +0.4, +0.95, +1.45, +1.9, +2.3 от «датировать»)
add("pop", "s06c", "инцертум", 0.4); add("pop", "s06c", "ретикулатум", 0.4); add("crunch", "s06c", "трескается", 0.4); add("whoosh", "s06c", "пожара", 0.4); add("pop", "s06c", "тестацеум", 0.4); add("chord", "s06c", "рынки", 0.35)
add("riser", "s07b", "девятисот", 0.3, off=-0.8); add("splash", "s07b", "плеснуть", 0.5, off=0.4); add("bubbles", "s07b", "закипеть", 0.6); add("ding", "s07b", "запомни", 0.4)
add("scan", "s10c", "сверлила", 0.5); add("bubbles", "s10c", "аквалангом", 0.6); add("pop", "s10c", "козы", 0.4)
for k in range(7): add("pop", "s10c", "средиземноморью", 0.3, off=0.3 + k * 0.35)
add("pop", "s12b", "грузы", 0.4); add("scan", "s12b", "изотопный", 0.4); add("ding", "s12b", "пемза", 0.4); add("chord", "s12b", "скрытый", 0.35)
add("bubbles", "s13b", "просыпаются", 0.5); add("ding", "s13b", "известняк", 0.4)
add("bam", "s13c", "нет", 0.35); add("bam", "s13c", "тоже", 0.35); add("bam", "s13c", "выжившего", 0.35); add("crunch", "s13c", "рухнуло", 0.4); add("chord", "s13c", "шестьсот", 0.4)
add("chord", "s14", "подпишись", 0.5); add("ding", "s14", "спасибо", 0.5)
MM = "../../media/music/"
def lvl(f):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", MM + f, "-t", "120", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", out).group(1))
beds = [("Investigations.mp3", 0, "s03"), ("Echoes of Time v2.mp3", "s03", "s04"), ("Lightless Dawn.mp3", "s04", "s05"), ("Ossuary 6 - Air.mp3", "s05", "s06"),
        ("Clean Soul.mp3", "s06", "s08"), ("Mesmerize.mp3", "s08", "s10c"), ("Spy Glass.mp3", "s10c", "s12"), ("Investigations.mp3", "s12", "s13"), ("Inspired.mp3", "s13", None)]
music = {"gain": 0.2, "beds": []}
for f, a, b in beds:
    g = 10 ** ((-20.0 - lvl(f)) / 20)  # выравнивание громкости подложек к −20 dB
    music["beds"].append({"file": MM + f, "from": 0 if a == 0 else ST[a], "to": total if b is None else ST[b], "gain": round(g * 1.0, 3)})
json.dump({"duration": round(total, 3), "voice": voice, "music": music, "sfx": sfx}, open("audio/cues.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "sfx", len(sfx), "beds", [(b['file'].split('/')[-1], round(b['gain'], 2)) for b in music['beds']])
