"""M1lash S1 V3: distinct head geometry (no scaleX fake profile).
This module describes independently drawn frontal, 3/4, and profile SVG
head paths. See docs/M1LASH_S1_MODEL_V3_QA.md for full test and usage.
"""
VIEWS={
 "front": {
   "face":"M-76-43 Q-88-97 -30-110 Q47-128 79-62 Q91 29 57 68 Q21 100 -33 81 Q-84 50-76-43 Z",
   "hair":"M-78-49 Q-109-103 -53-132 Q-12-156 19-132 Q57-143 86-106 L83-56 L54-83 L27-66 L-14-96 L-43-78 L-71-78Z",
   "eyes":[(-34,-5,15), (35,-5,15)],"nose":"M4 0 Q-2 23 9 25 L20 22","ear":None},
 "threequarter": {
   "face":"M-70-45 Q-87-94 -24-113 Q40-125 69-73 Q85-25 75 13 L87 24 Q91 33 76 39 Q63 83 26 88 Q-28 92 -60 57 Q-79 22-70-45 Z",
   "hair":"M-76-48 Q-104-104 -56-135 Q-26-151 7-132 Q38-144 69-110 L73-58 L45-84 L23-67 L-18-101 L-38-83 L-66-82Z",
   "eyes":[(-39,-4,15),(35,-5,10)],"nose":"M11 1 Q6 17 26 25 L37 22","ear":None},
 "profile": {
   "face":"M-66 -44 Q-79-91 -27-112 Q24-129 56-82 Q72-53 58-19 L82 1 Q91 8 71 19 L56 25 Q56 65 36 87 Q-4 104-46 66 Q-72 34-66-44 Z",
   "hair":"M-68-55 Q-93-102 -46-130 Q-14-148 11-132 Q42-145 62-113 L58-64 Q37-89 7-77 L-18-105 L-40-88 L-67-75 Z",
   "eyes":[(36,-15,12)],"nose":"M67 20 L55 27","ear":(-56,5,13,21)}
}
def render_head(view='front',emotion='neutral'):
 if view not in VIEWS:raise ValueError(view)
 v=VIEWS[view]
 ink='#241f24';skin='#e4aa88'
 s=[f'<path d="{v["face"]}" fill="{skin}" stroke="{ink}" stroke-width="5"/>',
    f'<path d="{v["hair"]}" fill="#30272b" stroke="{ink}" stroke-width="5"/>']
 if v['ear']:
  x,y,rx,ry=v['ear'];s.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{skin}" stroke="{ink}" stroke-width="3"/>')
 for x,y,rx in v['eyes']:
  ry=12 if emotion=='shock' else 7
  s.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#fffaf2" stroke="{ink}" stroke-width="3"/>')
  s.append(f'<circle cx="{x+3}" cy="{y}" r="5" fill="#293f50"/>')
 s.append(f'<path d="{v["nose"]}" stroke="#bd8066" stroke-width="3" fill="none"/>')
 mouth={'neutral':'Q8 58 29 47','smug':'Q9 70 29 47','angry':'L29 51','shock':'Q8 84 28 51','sad':'Q8 35 29 63','laugh':'Q8 81 29 48'}[emotion]
 s.append(f'<path d="M-14 50 {mouth}" stroke="#633738" stroke-width="3" fill="none"/>')
 return '<g>' + ''.join(s) + '</g>'
