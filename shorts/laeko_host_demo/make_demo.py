from pathlib import Path
import subprocess
BASE=Path(__file__).resolve().parent
OUT=BASE.parent.parent/'videos'/'laeko_host_music_demo_ru.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(BASE/'silent.mp4'),'-ss','42.610','-t','12','-i',str(BASE/'laeko.mp3'),'-map','0:v','-map','1:a','-c:v','copy','-af','afade=t=in:st=0:d=0.06,afade=t=out:st=11.6:d=0.4,loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-t','12','-movflags','+faststart',str(OUT)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'],check=True)
print(OUT)
