#!/usr/bin/env python3
"""Собирает cues.json для audio.py: голос по сценам, музыка, SFX по ключевым моментам."""
import json
DUR = [17.7, 27.5, 19.8, 17.3, 26.6, 32.4, 37.7, 26.3, 30.3, 20.6, 24.6, 32.0]
VO = 0.6
st = []; a = 0
for d in DUR: st.append(a); a += d
total = a
voice = [{"file": f"../../media/tts/antikythera/s{i+1:02d}.mp3", "at": round(st[i] + VO, 3)} for i in range(12)]
S = lambda i, t: round(st[i] + t, 3)
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
music = {"bpm": 100, "gain": 0.32, "sections": [
  {"at": 0, "style": "intro"}, {"at": S(0, 8.8), "style": "groove"},
  {"at": S(1, 3.2), "style": "tense"}, {"at": S(1, 10.3), "style": "mystery"},
  {"at": S(2, 0), "style": "intro"}, {"at": S(3, 0), "style": "groove"},
  {"at": S(4, 0), "style": "mystery"}, {"at": S(5, 0), "style": "groove"},
  {"at": S(6, 0), "style": "groove"}, {"at": S(7, 0), "style": "intro"},
  {"at": S(8, 0), "style": "mystery"}, {"at": S(8, 19.0), "style": "big"},
  {"at": S(9, 0), "style": "tense"}, {"at": S(10, 0), "style": "groove"},
  {"at": S(10, 9.2), "style": "tense"}, {"at": S(10, 14.0), "style": "intro"},
  {"at": S(11, 0), "style": "mystery"}, {"at": S(11, 18.8), "style": "big"},
]}
json.dump({"duration": round(total, 3), "voice": voice, "music": music, "sfx": sfx}, open("cues.json", "w"), ensure_ascii=False, indent=1)
print("total", total, "sfx", len(sfx))
