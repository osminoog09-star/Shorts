#!/usr/bin/env python3
"""Собирает cues.json для audio.py: голос по сценам, музыка, SFX по ключевым моментам."""
import json
VO = 0.6
TL = json.load(open("timeline.json"))
ST = {x["id"]: x["start"] for x in TL["scenes"]}
total = TL["duration"]
voice = [{"file": f"../../media/tts/antikythera/{x['id']}.mp3", "at": round(x["start"] + VO, 3)} for x in TL["scenes"]]
IDX = ["s01","s02","s03","s04","s05","s06","s07","s08","s09","s10","s11","s12"]
S = lambda i, t: round((ST[IDX[i]] if isinstance(i, int) else ST[i]) + t, 3)
WORDS = {x["id"]: json.load(open(f"../../media/tts/antikythera/{x['id']}.json"))["words"] for x in TL["scenes"]}
def W(sid, word, nth=0, off=0.0):
    k = 0
    for w in WORDS[sid]:
        if w["w"].lower().strip("«»\",.!?:;—").startswith(word):
            if k == nth: return round(ST[sid] + VO + w["start"] + off, 3)
            k += 1
    return None
sfx = []
def add(name, i, t, g=1.0): sfx.append({"name": name, "at": S(i, t), "gain": g})
# 01
for t in (1.5, 4.3, 5.1, 6.8): add("pop", 0, t, 0.6)
add("ding", 0, 9.4, 0.5); add("whoosh", 0, 16.9, 0.7)
# 02
add("thunder", 1, 4.1, 0.8); add("pop", 1, 0.7, 0.5); add("whoosh", 1, 9.7, 0.8); add("splash", 1, 10.1, 0.7)
add("bubbles", 1, 11.0, 0.6); add("bubbles", 1, 14.4, 0.8); add("ding", 1, 18.2, 0.45); add("pop", 1, 21.0, 0.5)
# 03
for t in (1.7, 2.4, 3.1): add("boing", 2, t, 0.35)
add("bam", 2, 5.8, 0.35); add("pop", 2, 7.5, 0.5); add("pop", 2, 12.2, 0.5); add("crunch", 2, 16.0, 0.4); add("ding", 2, 17.1, 0.6)
# 04
add("whoosh", 3, 4.0, 0.6); add("whoosh", 3, 9.9, 0.6); add("bam", 3, 10.6, 0.35)
# 05
for t in (3.7, 6.8, 10.4): add("pop", 4, t, 0.5)
add("scan", 4, 12.4, 0.7); add("crank", 4, 15.0, 0.5); add("pop", 4, 17.3, 0.5); add("whoosh", 4, 19.4, 0.5)
# 06
add("pop", 5, 1.9, 0.5); add("pop", 5, 4.5, 0.5); add("scan", 5, 9.0, 0.8); add("scan", 5, 10.7, 0.6); add("beep", 5, 12.4, 0.6)
add("riser", 5, 12.8, 0.4); add("ding", 5, 14.8, 0.5)
for k in range(6): add("pop", 5, 19.6 + k * 0.35, 0.35)
add("tick", 5, 27.4, 0.5); add("ding", 5, 29.8, 0.5)
# 07
add("crank", 6, 4.8, 0.6); add("crank", 6, 5.4, 0.5); add("whoosh", 6, 13.8, 0.6); add("ding", 6, 22.7, 0.4); add("pop", 6, 26.6, 0.5); add("pop", 6, 32.4, 0.5)
# 08
add("crank", 7, 8.6, 0.4); add("tick", 7, 10.8, 0.6); add("ding", 7, 17.6, 0.4)
# 09
add("pop", 8, 6.0, 0.5); add("pop", 8, 14.8, 0.6); add("pop", 8, 16.2, 0.6); add("whoosh", 8, 20.2, 0.5); add("riser", 8, 19.0, 0.35); add("chord", 8, 22.2, 0.5)
# 10
add("pop", 9, 0.9, 0.5); add("whoosh", 9, 9.6, 0.6)
for k in range(12): add("tick", 9, 12.6 + k * 0.2, 0.35)
add("ding", 9, 15.0, 0.6)
# 11
add("pop", 10, 0.9, 0.5); add("crunch", 10, 9.2, 0.9); add("bam", 10, 9.2, 0.3); add("beep", 10, 12.6, 0.6); add("ding", 10, 17.2, 0.4)
# 12
for k in range(3): add("pop", 11, 0.8 + k * 0.25, 0.5)
add("pop", 11, 11.8, 0.5); add("pop", 11, 15.6, 0.5); add("pop", 11, 16.6, 0.5); add("chord", 11, 18.8, 0.6); add("chord", 11, 26.6, 0.7)
# новые сцены n1–n9
def addw(name, sid, word, g=1.0, nth=0, off=0.0):
    t = W(sid, word, nth, off)
    if t is not None: sfx.append({"name": name, "at": t, "gain": g})
addw("pop", "n1", "ноября", 0.5); addw("tick", "n1", "критикос", 0.5); addw("pop", "n1", "летом", 0.5); addw("whoosh", "n1", "находки", 0.6, off=-0.3)
addw("ding", "n1", "юноша", 0.5); addw("pop", "n1", "голова", 0.5)
for k in range(6): addw("pop", "n1", "тридцать", 0.3, off=k * 0.18)
addw("crunch", "n2", "трескалась", 0.6); addw("tick", "n2", "восемьдесят", 0.5); addw("ding", "n2", "астрономический", 0.5)
addw("pop", "n3", "тридцать", 0.5); addw("pop", "n3", "шестерни", 0.5); addw("pop", "n3", "самая", 0.5); addw("whoosh", "n3", "зубья", 0.5, off=-0.4); addw("crank", "n3", "вручную", 0.6)
addw("whoosh", "n4", "исследование", 0.5); addw("pop", "n4", "эпира", 0.5); addw("pop", "n4", "олимпийскими", 0.4); addw("ding", "n4", "найи", 0.4)
addw("pop", "n5", "монеты", 0.5); addw("pop", "n5", "прайс", 0.5); addw("pop", "n5", "карман", 0.5); addw("pop", "n5", "сто", 0.5); addw("whoosh", "n5", "разброс", 0.5, off=-0.4)
addw("pop", "n6", "цицерон", 0.5); addw("ding", "n6", "архимеда", 0.5); addw("pop", "n6", "их", 0.4); addw("pop", "n6", "храм", 0.4); addw("pop", "n6", "посидония", 0.4)
addw("whoosh", "n7", "этот", 0.5, off=-0.3); addw("bubbles", "n7", "море", 0.5)
addw("pop", "n8", "кусто", 0.5); addw("pop", "n8", "двенадцатого", 0.4); addw("pop", "n8", "шестнадцатом", 0.4); addw("pop", "n8", "семнадцатом", 0.4); addw("riser", "n8", "валуна", 0.4, off=-0.6); addw("bubbles", "n8", "валуна", 0.6, off=0.6)
for k in range(8): addw("tick", "n9", "десятом", 0.3, off=k * 0.12)
addw("bam", "n9", "мексике", 0.3); addw("whoosh", "n9", "оригинал", 0.5, off=-0.3); addw("chord", "n9", "национальном", 0.4)
music = {"bpm": 100, "gain": 0.32, "sections": [
  {"at": 0, "style": "intro"}, {"at": S(0, 8.8), "style": "groove"},
  {"at": S(1, 3.2), "style": "tense"}, {"at": S(1, 10.3), "style": "mystery"},
  {"at": S(2, 0), "style": "intro"}, {"at": S(3, 0), "style": "groove"},
  {"at": S(4, 0), "style": "mystery"}, {"at": S(5, 0), "style": "groove"},
  {"at": S(6, 0), "style": "groove"}, {"at": S(7, 0), "style": "intro"},
  {"at": S(8, 0), "style": "mystery"}, {"at": S(8, 19.0), "style": "big"},
  {"at": S(9, 0), "style": "tense"}, {"at": S(10, 0), "style": "groove"},
  {"at": S(10, 9.2), "style": "tense"}, {"at": S(10, 14.0), "style": "intro"},
  {"at": S("n1", 0), "style": "intro"}, {"at": S("n2", 0), "style": "mystery"}, {"at": S("n3", 0), "style": "groove"},
  {"at": S("n4", 0), "style": "intro"}, {"at": S("n5", 0), "style": "groove"}, {"at": S("n6", 0), "style": "mystery"},
  {"at": S("n7", 0), "style": "tense"}, {"at": S("n8", 0), "style": "groove"}, {"at": S("n9", 0), "style": "intro"},
  {"at": S(11, 0), "style": "mystery"}, {"at": S(11, 18.8), "style": "big"},
]}
json.dump({"duration": round(total, 3), "voice": voice, "music": music, "sfx": sfx}, open("cues.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "sfx", len(sfx))
