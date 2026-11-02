#!/usr/bin/env python3
"""Restore missing beginning of the first RU question; preserve existing approved edit."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import movie_short as s
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--master',required=True);ap.add_argument('--work',required=True);a=ap.parse_args();w=Path(a.work);w.mkdir(parents=True,exist_ok=True)
s.ass([],w/'opening.ass')
with (w/'opening.ass').open('a') as out:out.write('Dialogue: 0,0:00:00.08,0:00:01.45,Sub,,0,0,0,,ЧТО ПОВТОРЯЮТ?\n')
f="[0:v]trim=start=159.15:end=160,setpts=PTS-STARTPTS,fps=30,crop=450:800:735:140,scale=1080:1920,setsar=1[v0];[0:a]atrim=start=159.15:end=160,asetpts=PTS-STARTPTS,aresample=48000[a0];[1:v]trim=end=29.6,setpts=PTS-STARTPTS,fps=30,setsar=1[v1];[1:a]atrim=end=29.6,asetpts=PTS-STARTPTS,aresample=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a];[v]subtitles='"+str(w/'opening.ass')+"'[out]"
subprocess.run(['ffmpeg','-v','error','-y','-i',a.source,'-i',a.master,'-filter_complex_threads','1','-filter_complex',f,'-map','[out]','-map','[a]','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-c:a','aac','-b:a','256k',str(w/'body.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','36.2','-t','2.739','-i',a.master,'-vn','-c:a','pcm_s16le',str(w/'title.wav')],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/assemble_with_outro.py'),str(w/'body.mp4'),'-o',str(w/'kino_002_v52.mp4'),'--title',str(w/'title.wav'),'--audio-bitrate','256k','--preset','veryfast'],check=True)
subprocess.run([sys.executable,str(ROOT/'skills/ext/ffmpeg-skill/scripts/check.py'),str(w/'kino_002_v52.mp4'),'--platform','shorts','--json'],check=True)
subprocess.run([sys.executable,str(ROOT/'skills/ext/ffmpeg-skill/scripts/look.py'),str(w/'kino_002_v52.mp4'),'--tiles','3x2','--overwrite','-o',str(w/'look.jpg')],check=True)
