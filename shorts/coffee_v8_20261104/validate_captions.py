"""Validate actual word coverage, order, positive holds and non-overlap."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parent;d=json.loads((P/'timeline.json').read_text())
def tokens(s):return re.findall('[а-яa-z0-9]+',s.lower().replace('ё','е'))
expected=tokens(' '.join(w['w'] for w in d['words']));actual=tokens(' '.join(' '.join(c['words']) for c in d['caps']))
assert expected==actual,'Dropped, duplicated or reordered subtitle words'
for i,c in enumerate(d['caps']):
 assert c['end']-c['start']>=.8-1e-5,('Short/zero caption',i,c)
 assert 0<=c['start']<c['end']<=d['total']+1e-5,('Range',i,c)
 if i:assert d['caps'][i-1]['end']<=c['start']+1e-5,('Overlap',i)
print('CAPTIONS_OK:',len(d['caps']),'groups,',len(actual),'words, exact order/coverage, holds>=0.8s')
