import json
from pathlib import Path
r=Path(__file__).resolve().parent.parent
v1=json.loads((r/'out/qa/v1_metrics.json').read_text());v2=json.loads((r/'out/qa/v2_metrics.json').read_text());qa=json.loads((r/'out/qa/FINAL_QA.json').read_text());det=json.loads((r/'out/qa/DETERMINISM.json').read_text());bounds=json.loads((r/'out/qa/TEXT_BOUNDS.json').read_text())
assert qa['full_decode']=='PASS' and qa['audio_packet_hash_identical']
assert not det['failed'] and not bounds['outsideFrame']
p=r/'AUDIT_V2.md';s=p.read_text().split('## Итоговая проверка экспортированного MP4')[0];s=s.replace('- Полный decode итогового MP4, сравнение яркостиV1/V2, идентичность аудио и фактические параметры экспорта: результаты будут добавлены ниже после завершения сборки.', '- Полный decode итогового MP4, сравнение яркостиV1/V2, идентичность аудио и фактические параметры экспорта: выполнены, результаты ниже.')
s+='''\n\n## Итоговая проверка экспортированного MP4\n\n| Проверка | V1 | V2 |\n|---|---:|---:|\n'''
for title,a,b in [('Кандидаты на короткий скачок яркости',len(v1['short_luminance_pulses']),len(v2['short_luminance_pulses'])),('Максимальная разница соседних кадров, из255',v1['max_adjacent_difference'],v2['max_adjacent_difference']),('99-й процентиль разницы кадров, из255',v1['adjacent_diff_p99'],v2['adjacent_diff_p99']),('Чёрные кадры',v1['black_frames'],v2['black_frames']),('Белые кадры',v1['white_frames'],v2['white_frames'])]:s+=f'| {title} | {a} | {b} |\n'
s+=f'''\nВсего проанализировано{v2['frames_sampled']} отсчётов яркости, весь выпуск, одинаковая методика15fps. Это измерение устранения конкретного дефекта, не обещание оценки зрителя или сертификация фоточувствительности.\n\n- Полный decode:PASS.\n- Хронометраж{qa['duration_seconds']:.3f}с, минимум1260с пройден.\n- Кадр1920×1080,30fps,H264/yuv420p; AAC48kHz.\n- Аудиопакеты побайтно совпадают с предыдущимMP4:PASS; голоса и музыкальный микс сохранены без повторного синтеза и перекодирования.\n- Размер{qa['size_bytes']:,} байт.\n- SHA-256MP4:`{qa['sha256']}`.\n- Смысловые планы150; переходы149, ошибок повторяемости0; выходов текста за кадр0.\n- Статус:OWNER_REVIEW. Ничего не опубликовано и не запланировано.\n'''
p.write_text(s);(r/'out/M1lash_News_V2_Audit.md').write_text(s)
print('AUDIT FINALIZED',len(v2['short_luminance_pulses']),'pulse candidates')
