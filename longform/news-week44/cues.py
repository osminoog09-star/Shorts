#!/usr/bin/env python3
"""audio/cues.json для audio.py: голоса Димы и Светы по репликам, подложки Kevin MacLeod (CC BY 4.0) по главам, SFX."""
import json, re, subprocess
TL = json.load(open("timeline.json")); total = TL["duration"]
TTS = "../../media/tts/news_week44/"
voice, LS = [], {}
for c in TL["chapters"]:
    for l in c["lines"]:
        at = round(c["start"] + l["s"], 3); voice.append({"file": f"{TTS}{l['id']}.mp3", "at": at}); LS[l["id"]] = at
WORDS = {}
def W(lid, word, nth=0):
    if lid not in WORDS:
        try: WORDS[lid] = json.load(open(f"{TTS}{lid}.json"))["words"]
        except Exception: WORDS[lid] = []
    k = 0
    for w in WORDS[lid]:
        parts = w["w"].split(); L = len(w["w"]) or 1; pos = 0
        for p in parts:
            a = w["w"].find(p, pos); pos = a + len(p)
            if re.sub(r'[«»"\',.!?:;—…()]', '', p.lower().replace('ё', 'е')).startswith(word.replace('ё', 'е')):
                if k == nth: return round(LS[lid] + w["start"] + ((a / L) * (w["end"] - w["start"]) if len(parts) > 1 else 0), 3)
                k += 1
    return None
sfx = []
for c in TL["chapters"]:
    if c["id"] != "c0": sfx += [{"name": "whoosh", "at": round(c["start"] + 0.05, 3), "gain": 0.45}, {"name": "ding", "at": round(c["start"] + 0.5, 3), "gain": 0.32}]
# удары/всплывания на словах, к которым привязаны карточки (из chapters.js)
src = open("chapters.js", encoding="utf-8").read()
seen = set()
for lid, word in re.findall(r"at\(L, '(c\d_\d\d)', '([^']+)'", src):
    if (lid, word) in seen: continue
    seen.add((lid, word)); t = W(lid, word)
    if t is not None: sfx.append({"name": "pop", "at": t, "gain": 0.32})
for lid, word, name, g in [("c0_01", "грузовики", "bam", 0.3), ("c1_04", "протаранили", "crunch", 0.5), ("c1_14", "врезаются", "crunch", 0.4),
                           ("c2_07", "неверен", "crunch", 0.35), ("c2_09", "lean", "ding", 0.4), ("c3_05", "двенадцати", "scan", 0.4),
                           ("c4_02", "nasdaq", "ding", 0.45), ("c5_07", "дождь", "splash", 0.35), ("c6_08", "шестьдесят", "bam", 0.3),
                           ("c8_06", "шесть", "thunder", 0.6), ("c8_06", "один", "thunder", 0.35), ("c9_05", "подпишись", "chord", 0.5), ("c9_05", "спасибо", "ding", 0.45)]:
    t = W(lid, word)
    if t is not None: sfx.append({"name": name, "at": t, "gain": g})
MM = "../../media/music/"
def lvl(f):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", MM + f, "-t", "120", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", out).group(1))
BED = {"c0": "Volatile Reaction.mp3", "c1": "Spy Glass.mp3", "c2": "Mesmerize.mp3", "c3": "Hidden Agenda.mp3", "c4": "Crypto.mp3",
       "c5": "Dreamy Flashback.mp3", "c6": "Lightless Dawn.mp3", "c7": "Inspired.mp3", "c8": "Impact Prelude.mp3", "c9": "Clean Soul.mp3"}
music = {"gain": 0.2, "beds": []}
for c in TL["chapters"]:
    f = BED[c["id"]]; g = 10 ** ((-20.0 - lvl(f)) / 20)
    music["beds"].append({"file": MM + f, "from": c["start"], "to": round(c["start"] + c["dur"], 3), "gain": round(g, 3)})
json.dump({"duration": round(total, 3), "voice": voice, "music": music, "sfx": sfx}, open("audio/cues.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "voice", len(voice), "sfx", len(sfx), "beds", len(music["beds"]))
