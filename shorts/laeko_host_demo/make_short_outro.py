from pathlib import Path
import subprocess,json
BASE=Path(__file__).resolve().parent
OUT=BASE.parent.parent/'videos'/'m1lash_outro_short_ru.mp4'
# Same source-time transform as the approved speaking demo, without its intro/tail.
fc="[1:a]afade=t=in:st=0:d=0.025,loudnorm=I=-18:TP=-2:LRA=9,volume='if(lt(t,4.55),0.18,if(lt(t,5.25),0.18+0.82*(t-4.55)/0.7,1))':eval=frame,afade=t=out:st=5.55:d=0.25[m];[2:a]atrim=start=20,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7,afade=t=in:st=0:d=0.015,apad,atrim=duration=5.8[v];[m][v]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false:latency=true[a]"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(BASE/'short_outro_silent.mp4'),'-ss','44.110','-t','5.8','-i',str(BASE/'laeko.mp3'),'-i',str(BASE/'liam_source.mp3'),'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-ar','48000','-b:a','192k','-t','5.8','-movflags','+faststart',str(OUT)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'],check=True)
p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT)],capture_output=True,text=True,check=True)
q={'probe':json.loads(p.stdout),'full_decode':'passed','voice':'Approved existing Liam, source 20 sec to end, no new generation; no speed change','visemes':'Original Rhubarb source frame round((20+local_seconds)*30), same origin as voice','music_source_seconds':[44.110,49.910],'duration':5.8,'publication':'not scheduled; reusable asset','continuous_human_listen':False,'continuous_human_watch':False}
(BASE/'QA_SHORT_OUTRO.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(OUT)
