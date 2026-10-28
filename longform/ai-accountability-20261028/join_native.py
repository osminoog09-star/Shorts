from pathlib import Path
import json,subprocess,shutil
R=Path(__file__).resolve().parent;B=R/'build';M=B/'masters';OUT=B/'release';OUT.mkdir(exist_ok=True)
def run(*args,capture=False):
 return subprocess.check_output([str(x)for x in args],text=True)if capture else subprocess.run([str(x)for x in args],check=True)
def probe(p):return json.loads(run('ffprobe','-v','error','-show_format','-show_streams','-of','json',p,capture=True))
scenes=json.loads((B/'timeline.json').read_text())['scenes'];paths=[M/f"part_{s['id']:02d}.mp4"for s in scenes]
for p in paths+[M/'Short_RU.mp4']:
 if not p.is_file()or p.stat().st_size<1000:raise RuntimeError('Missing verified part '+str(p))
cat=OUT/'parts.txt';cat.write_text('\n'.join("file '"+str(p.resolve())+"'"for p in paths))
raw=OUT/'joined.mp4';run('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',cat,'-c','copy',raw)
for src,name in [(raw,'M1lash_AI_News_20261028_RU.mp4'),(M/'Short_RU.mp4','M1lash_AI_Context_Shorts_20261028_RU.mp4')]:
 dest=OUT/name
 run('ffmpeg','-v','error','-y','-i',src,'-c:v','copy','-af','loudnorm=I=-15:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',dest)
 run('ffmpeg','-v','error','-i',dest,'-f','null','-')
 info=probe(dest);v=next(x for x in info['streams']if x['codec_type']=='video');a=next(x for x in info['streams']if x['codec_type']=='audio');vd=float(v.get('duration',info['format']['duration']));ad=float(a.get('duration',info['format']['duration']))
 if abs(vd-ad)>.25:raise RuntimeError('A/V drift >0.25s '+name)
 if 'Shorts'not in name and float(info['format']['duration'])<1260:raise RuntimeError('Longform below 21:00')
 if v['width']!=(1080 if 'Shorts'in name else 1920)or v['height']!=(1920 if 'Shorts'in name else 1080):raise RuntimeError('Wrong native layout')
 (OUT/(name+'.probe.json')).write_text(json.dumps(info,indent=2));print(name,info['format']['duration'],flush=True)
for p in M.glob('*_contact.jpg'):shutil.copy2(p,OUT/p.name)
# Chapters follow measured video part durations, including real container timebases.
at=0;chapters=[]
for s,p in zip(scenes,paths):
 if s['id']in{0,2,9,18,23,35,37}:
  n=int(at);chapters.append(f'{n//60:02d}:{n%60:02d} {s["chapter"]}')
 at+=float(probe(p)['format']['duration'])
(R/'PUBLISH.md').write_text('''# Упаковка выпуска · 28.10.2026

Название: ИИ работает за тебя. А кто отвечает за ошибки? | Новости 28.10

Выпуск о свежих публикациях Amazon, Cloudflare и Opera: как отличать активность ИИ от полезного результата, почему важны границы данных и что меняет локальная обработка. Схемы и рабочие ситуации — подписанные условные примеры.

'''+ '\n'.join(chapters)+'''

Источники:
https://www.aboutamazon.com/news/company-news/amazon-software-engineer-role-guideline-ai
https://thenextweb.com/news/amazon-tokenmaxxing-memo-engineers-ai-metrics
https://blog.cloudflare.com/kv-cache-exposure-remediation/
https://www.knostic.ai/blog/hallucination-or-cross-tenant-when-an-llm-answers-with-another-users-context
https://www.lmsys.org/blog/2026-10-26-cf-security/
https://press.opera.com/2026/10/27/opera-doubles-down-on-local-ai-shipping-models-directly-in-its-browsers/
https://www.techrepublic.com/article/news-opera-webai-local-ai-browser-models/

Музыка и SFX: оригинальная процедурная генерация huashu-motion; чужие песни и архивное Liam-аудио не использованы. Голос Димы: ru-RU-DmitryNeural. Ведущий M1lash — утверждённый Narrator2/HostCorner. Кодовые сцены не являются видеозаписями реальных событий.

Вопрос: какую конкретную задачу ты доверишь ИИ и как проверишь результат?

#ИИ #Нейросети #Технологии #НовостиИИ #M1lash

Теги: новости ИИ, искусственный интеллект, нейросети, Amazon, Cloudflare, Opera WebAI, локальный ИИ, ИИ агенты, безопасность данных, автоматизация, M1lash
Категория: EDUCATION. Не для детей. Не опубликовано и не запланировано.

Shorts: Нейросеть ответила чужими данными — это не галлюцинация? #shorts
Описание Shorts: Cloudflare раскрыла уже исправленный инцидент с чужим контекстом в ответах. Полный разбор — в длинном выпуске на канале. После ручной загрузки выбрать основное видео в поле «Связанное видео»; ссылку добавлять только после получения реального YouTube ID.
''')
shutil.copy2(R/'PUBLISH.md',OUT/'PUBLISH.md');raw.unlink();print('All technical gates passed. Visual and listening review still required.')
