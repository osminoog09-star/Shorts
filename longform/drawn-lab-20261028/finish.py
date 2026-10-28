from pathlib import Path
import json,subprocess,shutil
R=Path(__file__).resolve().parent;B=R/'build';M=B/'masters';O=B/'release';O.mkdir(exist_ok=True)
def run(*a):subprocess.run([str(x)for x in a],check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def dur(p):return float(probe(p)['format']['duration'])
scenes=json.loads((B/'timeline.json').read_text())['scenes'];ids=[s['id']for s in scenes]
assert len(ids)==29
for i in ids+[90,91,92]:
 assert(M/f'part_{i:02d}.mp4').stat().st_size>1000
 meta=json.loads((M/f'part_{i:02d}.json').read_text());assert meta['voice_id']=='ru-RU-DmitryNeural'and meta['rate']=='+0%'
cat=O/'parts.txt';cat.write_text('\n'.join("file '"+str((M/f'part_{i:02d}.mp4').resolve())+"'"for i in ids))
raw=O/'joined.mov';run('ffmpeg','-xerror','-v','error','-y','-f','concat','-safe','0','-i',cat,'-c:v','copy','-af','aresample=async=1:first_pts=0','-c:a','pcm_s16le',raw)
packages=[(raw,'M1lash_Battery_Drawn_RU',ids),(M/'part_90.mp4','M1lash_Plane_Drawn_Shorts_RU',[90]),(M/'part_91.mp4','M1lash_Venus_Drawn_Shorts_RU',[91]),(M/'part_92.mp4','m1lash_movie_mystery_002_ru',[92])];checks=[]
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
for src,name,partids in packages:
 target=O/(name+'.mp4')
 run('ffmpeg','-xerror','-v','error','-y','-i',src,'-c:v','copy','-af','loudnorm=I=-15:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',target)
 run('ffmpeg','-xerror','-v','error','-i',target,'-f','null','-')
 p=probe(target);v=next(x for x in p['streams']if x['codec_type']=='video');a=next(x for x in p['streams']if x['codec_type']=='audio');short=len(partids)==1
 assert(v['width'],v['height'])==((1080,1920)if short else(1920,1080))
 assert v['r_frame_rate']=='30/1'and v['pix_fmt']=='yuv420p'
 assert abs(float(v['duration'])-float(a['duration']))<=.25
 assert short or float(p['format']['duration'])>=1260
 offset=0;lines=[]
 for i in partids:
  for c in json.loads((M/f'part_{i:02d}.captions.json').read_text()):
   lines.append(f'{len(lines)+1}\n{stamp(offset+c["start"])} --> {stamp(offset+c["end"])}\n{c["text"]}\n')
  offset+=dur(M/f'part_{i:02d}.mp4')
 (O/(name+'.srt')).write_text('\n'.join(lines));checks.append(dict(file=target.name,duration=dur(target),width=v['width'],height=v['height'],fps=v['r_frame_rate'],decode='PASS',voice_id='ru-RU-DmitryNeural',rate='+0%'))
 print('VERIFIED_FINAL',checks[-1],flush=True)
raw.unlink();cat.unlink()
for p in M.glob('*_contact.jpg'):shutil.copy2(p,O/p.name)
chapters=[];at=0
for s in scenes:
 if s['id']in{0,2,5,9,13,17,21,24,27,31}:chapters.append(f'{int(at)//60:02d}:{int(at)%60:02d} {s["chapter"]}')
 at+=dur(M/f'part_{s["id"]:02d}.mp4')
common='Музыка и звуки: оригинальная процедурная генерация huashu-motion. Голос Димы: ru-RU-DmitryNeural. Ведущий и иллюстрации созданы кодом. Схемы объясняют механизмы; это не результаты замеров конкретного устройства.'
pub='''# Готовые тексты для загрузки

Статус: RELEASE_CANDIDATE — требуется финальный просмотр и прослушивание. Ничего не опубликовано.

## Длинный ролик
Название: Куда исчезает заряд телефона? Разбираем батарею на рисунке

Описание:
С утра было сто процентов — а к вечеру телефон просит розетку? На рисунке разберём, что происходит внутри батареи, куда уходит энергия и как найти причину быстрого разряда. Экран, связь, приложения, температура и износ — без обещаний волшебного прироста автономности.

'''+ '\n'.join(chapters)+'''

Источники:
https://www.energy.gov/science/doe-explainsbatteries
https://www.apple.com/batteries/maximizing-performance/
https://support.apple.com/en-us/101575
https://support.google.com/pixelphone/answer/6090599
https://developer.android.com/training/monitoring-device-state/doze-standby

'''+common+'''

Теги: батарея телефона, телефон быстро разряжается, заряд аккумулятора, литий ионная батарея, автономность, экран, смартфон, наука, объяснение, M1lash
Хештеги: #Смартфон #Батарея #Технологии #Наука #M1lash
Закреп: Что первым оказалось причиной разряда на твоём телефоне — экран, связь или приложение?

## Шортс — самолёт
Название: Двигатели замолчали. Почему самолёт не падает камнем? #shorts
Описание: Без тяги самолёт может планировать, расходуя высоту. На рисунке разбираем, что держит его в воздухе и почему посадка зависит от условий. Это объяснение принципа, а не инструкция пилоту.
Источники: NASA — gliders; FAA — Airplane Flying Handbook, emergency procedures.
https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/gliders/
https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/airplane_handbook
'''+common+'''
Теги: самолет, планирование, подъемная сила, авиация, физика, наука, M1lash
Хештеги: #shorts #Самолёт #Авиация #Физика #Наука #КакЭтоРаботает #M1lash
Закреп: Думал, что выключенный двигатель сразу означает падение?

## Шортс — Венера
Название: Сутки длиннее года? С Венерой есть подвох #shorts
Описание: Оборот вокруг оси, год и солнечные сутки — разные часы. У Венеры примерно 243, 225 и 117 земных суток соответственно. Показываем разницу на рисунке.
Источники:
https://solarsystem.nasa.gov/internal_resources/1028/
https://blogs.esa.int/venustransit/2012/05/31/venus-and-earth-worlds-apart/
'''+common+'''
Теги: Венера, космос, солнечные сутки, планеты, астрономия, наука, M1lash
Хештеги: #shorts #Венера #Космос #Астрономия #Планеты #Наука #M1lash
Закреп: Какие сутки ты представлял — оборот относительно звёзд или от полудня до полудня?

## Кинозагадка
Название: Они решили выстрелить собой из пушки 😳 Угадай фильм #shorts
Описание: Самая безумная экспедиция начинается с огромной пушки. Узнал фильм до последней реплики? Напиши, на какой секунде догадался!
Немые исторические кадры сопровождает наш авторский русский рассказ; это не оригинальный русский дубляж. Музыка и звуки — оригинальная процедурная генерация huashu-motion. Голос ведущего — Дима, ru-RU-DmitryNeural.
Теги: кино, угадай фильм, кинонарезка, кинозагадка, немое кино, невероятная сцена, movie edit, shorts, M1lash
Хештеги: #shorts #Кино #УгадайФильм #КиноЗагадка #КиноМоменты #НемоеКино #M1lash
Закреп: Узнал до последнего слова? На какой секунде?
Обложка: ОНИ ЭТО СДЕЛАЛИ?!

При загрузке киношортса использовать приложенный SRT. Проверить автоматические субтитры YouTube и убрать разгадку из них: название допустимо только в последней звуковой фразе. Внутренние исследовательские и производственные файлы не копировать в публичное описание.

Общие настройки: русский язык; не предназначено специально для детей; категория EDUCATION для научных выпусков, ENTERTAINMENT для кинозагадки. Не включать расписание автоматически. Эти шортсы самостоятельные, ссылку на несвязанную тему не подставлять.
'''
(O/'PUBLISH.md').write_text(pub)
(O/'CHECKS.json').write_text(json.dumps(dict(status='RELEASE_CANDIDATE',files=checks,full_decode='PASS',continuous_subjective_watch_and_listen='not certified',publication='not published or scheduled'),ensure_ascii=False,indent=2))
m=json.loads((R.parent.parent/'tools/movie_edit/mystery_release.example.json').read_text())
m['internal'].update(project_id='movie_mystery_002',film_title='Путешествие на Луну',film_title_aliases=['Le Voyage dans la Lune','A Trip to the Moon','Puteshestvie na Lunu'],film_rights_verified=True)
m['public'].update(title='Они решили выстрелить собой из пушки 😳 Угадай фильм #shorts',description='Немые исторические кадры и наш авторский русский рассказ. Узнал фильм до последней реплики? Музыка и SFX — оригинальные, процедурные.',public_filename='m1lash_movie_mystery_002_ru.mp4',captions=[c['text']for c in json.loads((M/'part_92.captions.json').read_text())])
m['outro'].update(spoken_lines=['Подпишись! И спасибо всем, кто досмотрел и поставил лайк.','Путешествие на Луну'])
m['video'].update(music_license_verified=True,dialogue_note='Silent film with authored Russian narration, not an original dub')
(R/'mystery_release_private.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
print('Technical gates passed; final subjective review remains.')
