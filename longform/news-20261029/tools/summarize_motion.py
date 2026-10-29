import json,re
from pathlib import Path
r=Path(__file__).resolve().parent.parent
s=(r/'out/qa/OM_QA_FINAL.txt').read_text()
m=re.search(r'motion per second: (.*?)\(contrast',s,re.S)
values=[float(x) for x in m.group(1).split()] if m else []
c=re.search(r'(\d+) hard cut',s)
result={'single_frame_pops_absent':'✓ no single-frame pops' in s,'hard_cuts_detected':int(c.group(1)) if c else None,'mean_motion':round(sum(values)/len(values),3) if values else None,'peak_motion':max(values) if values else None,'flat_opening_flag':'✗ flat opening' in s,'barely_moves_flag':'✗ the whole film barely moves' in s,'reading_hold_flag':'✗ still for' in s,'limitations':'Motion thresholds come from short launch films; evidence-reading holds in a long narrated news program are deliberate. This is not an audience-retention guarantee.'}
(r/'out/qa/MOTION_QA_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
p=r/'AUDIT_V2.md';a=p.read_text().split('## Итоговая проверка экспортированного MP4')[0]
a+=f"\n\nФинальный анализ движения: найдено{result['hard_cuts_detected']} прямых склеек, среднее движение{result['mean_motion']} (промежуточный проход0,24). Флаг плоского начала:{result['flat_opening_flag']}; флаг почти неподвижного фильма:{result['barely_moves_flag']}. Покадровых вспышек поom qa нет:{result['single_frame_pops_absent']}. Отдельные удержания чтения первоисточников и схем сохранены; предупреждение о низком движении на таких участках не выдано за полное отсутствие неподвижных кадров.\n"
p.write_text(a)
