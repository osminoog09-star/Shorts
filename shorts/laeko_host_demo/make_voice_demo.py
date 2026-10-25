from pathlib import Path
import subprocess,json
BASE=Path(__file__).resolve().parent
OUT=BASE.parent.parent/'videos'/'laeko_host_voice_demo_ru.mp4'
fc="[1:a]afade=t=in:st=0:d=0.06,afade=t=out:st=11.6:d=0.4,loudnorm=I=-18:TP=-2:LRA=9,volume='if(lt(t,1.35),1,if(lt(t,1.5),1-0.82*(t-1.35)/0.15,if(lt(t,6.05),0.18,if(lt(t,6.75),0.18+0.82*(t-6.05)/0.7,1))))':eval=frame[m];[2:a]atrim=start=20,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7,afade=t=in:st=0:d=0.015,adelay=1500|1500,apad,atrim=duration=12[v];[m][v]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false:latency=true[a]"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(BASE/'voice_silent.mp4'),'-ss','42.610','-t','12','-i',str(BASE/'laeko.mp3'),'-i',str(BASE/'liam_source.mp3'),'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-ar','48000','-b:a','192k','-t','12','-movflags','+faststart',str(OUT)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'],check=True)
p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT)],capture_output=True,text=True,check=True)
qa={'probe':json.loads(p.stdout),'full_decode':'passed','voice':'Existing Liam recording reused: media/tts/host_demo/eleven.mp3, source seconds 20–end, delayed 1.5 seconds','text':'Подпишись! И спасибо всем, кто досмотрел и поставил лайк.','lipsync':'Original Rhubarb visemes, same time transform as audio; source mouth/audio envelope correlation 0.9757 at zero offset, rate 1.0','music':'42.610–54.610; automated gain 0.18 under speech; rise after 6.05 sec','new_paid_generations':0,'continuous_human_listen':False,'continuous_human_watch':False,'publication':'not scheduled'}
(BASE/'QA_VOICE.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(OUT)
