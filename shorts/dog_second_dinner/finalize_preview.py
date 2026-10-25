from pathlib import Path
import json,subprocess,numpy as np,wave
R=Path(__file__).resolve().parent;O=R/'out';f=O/'generated.mp4'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));dur=float(d['format']['duration']);v=next(s for s in d['streams'] if s['codec_type']=='video');w,h=v['width'],v['height']
# Minimal captions over the kitchen, leaving the dog and bowl visible.
(O/'hook.txt').write_text('ПЯТЬ МИНУТ ПОСЛЕ УЖИНА')
(O/'punch.txt').write_text('Я НЕ ЕЛ. Я ДЕГУСТИРОВАЛ.')
size=round(w*.046);font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
filters=[]
for text,start,end in [('hook.txt',0,dur*.47),('punch.txt',dur*.47,dur)]:
 filters.append(f"drawtext=fontfile={font}:textfile={O/text}:fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.48:boxborderw=14:x=(w-text_w)/2:y=h*0.10:enable='between(t,{start},{end})'")
# Original quiet metal-bowl taps. No imitation narrator or reused recording.
sr=48000;x=np.zeros(round(dur*sr));
for at in [dur*.48,dur*.48+.12]:
 t=np.arange(round(.35*sr))/sr;a=sum(np.sin(2*np.pi*hz*t)*np.exp(-t*decay) for hz,decay in [(790,16),(1343,21),(2170,29)])*.065;i=round(at*sr);n=min(len(a),len(x)-i);x[i:i+n]+=a[:n]
with wave.open(str(O/'bowl_taps.wav'),'wb') as q:q.setnchannels(1);q.setsampwidth(2);q.setframerate(sr);q.writeframes((x*32767).astype(np.int16).tobytes())
out=O/'dog_second_dinner_realistic_preview_ru.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(f),'-i',str(O/'bowl_taps.wav'),'-map','0:v:0','-map','1:a:0','-vf',','.join(filters),'-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','128k','-t',str(dur),'-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
report={'duration':dur,'native_dimensions':[w,h],'source':'Higgsfield Genjutsu free motion-control, original driver and imagegen reference','job_id':'cb0487f7-ac8a-4995-9a6f-f4b6d723fa16','quoted_credits':0,'publication':'reserved; do not schedule without Denis decision','audio':'original short synthetic metal-bowl taps, no narrator','full_decode':'passed','continuous_human_audio_motion_review':'not performed'}
(O/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(out,report)
