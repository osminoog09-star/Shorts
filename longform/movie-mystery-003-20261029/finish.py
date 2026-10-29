from pathlib import Path
import json,subprocess,shutil,re
R=Path(__file__).resolve().parent;B=R/'build';F=B/'native/scene_92';O=B/'release';O.mkdir(exist_ok=True)
def run(*a):subprocess.run([str(x)for x in a],check=True)
s=json.loads((B/'short_92_timeline.json').read_text())['scenes'][0];D=s['duration']+.18
mp4=sorted((F/'out').glob('*.mp4'),key=lambda p:p.stat().st_mtime)[-1];target=O/'m1lash_movie_mystery_003_ru.mp4'
run('ffmpeg','-xerror','-v','error','-y','-i',mp4,'-t',str(D),'-c:v','copy','-af',f'loudnorm=I=-15:TP=-1.5:LRA=9,afade=t=out:st={D-.1}:d=0.1','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',target)
run('ffmpeg','-xerror','-v','error','-i',target,'-f','null','-')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]));v=next(x for x in info['streams']if x['codec_type']=='video');a=next(x for x in info['streams']if x['codec_type']=='audio');assert(v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'])==(1080,1920,'30/1','yuv420p');assert abs(float(v['duration'])-float(a['duration']))<.25
caps=json.loads((F/'captions.json').read_text())
def ts(t):
 n=round(t*1000);return f'{n//3600000:02d}:{n//60000%60:02d}:{n//1000%60:02d},{n%1000:03d}'
(O/'m1lash_movie_mystery_003_ru.srt').write_text('\n'.join(f'{i+1}\n{ts(c["start"])} --> {ts(c["end"])}\n{c["text"]}\n'for i,c in enumerate(caps)))
credit='(CC) Blender Foundation | mango.blender.org\nCreative Commons Attribution3.0: https://creativecommons.org/licenses/by/3.0/\nИзменения: выбор фрагментов, вертикальный монтаж, авторский русский пересказ, адаптированный перевод реплики и субтитры. Оригинальная звуковая дорожка не используется. Это не официальный русский дубляж. Музыка и SFX — оригинальная процедурная генерация huashu-motion.'
public=dict(title='Он бросил её. Через40лет за это расплачивается весь мир #shorts'.replace('Через40лет','Через 40 лет'),description='Она не забыла этот разговор. А людям приходится повторить его, чтобы спасти мир от роботов. Угадал фильм до последней реплики?\n\n'+credit,tags=['кино','угадай фильм','фантастика','роботы','кинозагадка','сцены из фильмов','кино shorts','русская озвучка','короткий пересказ','movie edit','M1lash'],hashtags=['#shorts','#Кино','#Фантастика','#Роботы','#УгадайФильм','#КиноЗагадка','#M1lash'],pinned_comment='Узнал фильм до последней реплики? На какой секунде?',thumbnail_text='ОНА НЕ ЗАБЫЛА',public_filename=target.name,captions=[c['text']for c in caps],chapters=[],end_card_text='Подпишись! Спасибо за лайк!')
manifest=dict(internal=dict(project_id='movie_mystery_003',film_title='Слёзы стали',film_title_aliases=['Слезы стали','Tears of Steel','Slyozy stali','Slezy stali'],film_year=2012,film_rights_verified=True),public=public,outro=dict(cta_voice_id='edge:ru-RU-DmitryNeural',last_title_voice_id='edge:ru-RU-DmitryNeural',cta_text='Подпишись! И спасибо всем, кто досмотрел и поставил лайк.',spoken_lines=['Подпишись! И спасибо всем, кто досмотрел и поставил лайк.','Слёзы стали'],title_visible_on_screen=False,lip_sync_verified=False),video=dict(width=1080,height=1920,full_bleed=True,dialogue_language='ru',music_license_verified=True,music_ducking=True,visual_qa_done=False,audio_qa_done=False),publication=dict(publish_ready=False))
(R/'mystery_release_private.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# Additional public-year/name scan, including actual exported SRT.
text=json.dumps(public,ensure_ascii=False).casefold()+(O/'m1lash_movie_mystery_003_ru.srt').read_text().casefold()
for x in ['слёзы стали','слезы стали','tears of steel','slyozy stali','slezy stali','2012','ian hubert','thom','celia']:assert x not in text,x
(O/'Movie_Mystery_003_Publication.md').write_text('Название:\n'+public['title']+'\n\nОписание:\n'+public['description']+'\n\n'+' '.join(public['hashtags'])+'\n\nТеги:\n'+', '.join(public['tags'])+'\n\nЗакреп:\n'+public['pinned_comment']+'\n\nПри загрузке использовать приложенный SRT; проверить и убрать разгадку из автоматических субтитров YouTube.\nСтатус: версия для просмотра, не опубликована. Полное субъективное прослушивание не сертифицировано автоматическими проверками.\n')
run('ffmpeg','-v','error','-y','-ss','1.5','-i',target,'-frames:v','1',O/'Movie_Mystery_003_Cover.png')
(O/'QA.json').write_text(json.dumps(dict(status='RELEASE_CANDIDATE',file=target.name,duration=info['format']['duration'],format='1080x1920 H26430fps yuv420p AAC',decode='PASS',public_text_spoilers='PASS',voice='ru-RU-DmitryNeural +0%',subjective_watch_listen='not certified'),ensure_ascii=False,indent=2))
shutil.copy2(F/'captions.json',O/'captions.json');print('VERIFIED_EXPORT',info['format']['duration'],flush=True)
