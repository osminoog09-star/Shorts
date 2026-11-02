#!/usr/bin/env python3
"""Rebuild movie mystery 004 from approved local RU film clip with safe subtitles.

Requires a private owner-provided movie file. Does NOT download/copy movie media
into git. Body cuts may use ffmpeg concat filter; approved outro is joined ONLY
by tools/assemble_with_outro.py, never stream-copy or AAC packet manipulation.
"""
from pathlib import Path
import argparse
import subprocess

TIMED_TEXT = [
    (.10,2.60,"ОНА ЗНАЛА ПРАВДУ","Hook"),
    (3.35,4.55,"И в чём же?","Main"),
    (5.10,6.10,"В Нейтоне.","Main"),
    (9.00,10.15,"В смысле?","Main"),
    (12.10,13.80,"ОН ТЕБЕ НЕ ДРУГ","Main"),
    (16.28,17.30,"Извини?","Main"),
    (19.55,22.80,r"Прости, Ава,\Nя не понимаю.","Main"),
    (23.92,25.50,"НЕ ВЕРЬ ЕМУ","Main"),
    (27.10,30.20,r"НЕ ВЕРЬ НИ\NЕДИНОМУ ЕГО СЛОВУ","Main"),
]

def ts(t):
    return f"{int(t//3600)}:{int(t//60)%60:02d}:{t%60:05.2f}"

def write_ass(path):
    header = """[Script Info]
Title: M1lash 004 V49 RU-safe
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,DejaVu Sans,70,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,2,110,160,510,1
Style: Hook,DejaVu Sans,73,&H00FFFFFF,&H000000FF,&HCC11111A,&H99111118,-1,0,0,0,100,100,0,0,3,2,0,8,160,210,350,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    for a,b,txt,style in TIMED_TEXT:
        header += f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{txt}\n"
    path.write_text(header,encoding="utf-8")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path,help="PRIVATE approved Russian-dub source (not GitHub)")
    parser.add_argument("--out-dir",type=Path,required=True)
    parser.add_argument("--title",type=Path,required=True,help="Existing Dima title MP3")
    a=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    a.out_dir.mkdir(parents=True,exist_ok=True)
    sub=a.out_dir/"004_V49_RU_SAFE.ass"
    write_ass(sub)
    x="if(lt(t,7.934),510,if(lt(t,12.564),930,if(lt(t,19.821),510,if(lt(t,27.829),740,510))))"
    x=x.replace(",",r"\,")
    v0="trim=start=33.195:duration=2.7,setpts=PTS-STARTPTS,fps=30,crop=452:804:750:0,scale=1080:1920:flags=lanczos,eq=gamma=1.12:brightness=0.015,setsar=1"
    v1=f"trim=start=65.395:duration=27.6,setpts=PTS-STARTPTS,fps=30,crop=452:804:{x}:0,scale=1080:1920:flags=lanczos,eq=gamma=1.12:brightness=0.015,setsar=1"
    f=(f"[0:v]{v0}[v0];[0:a]atrim=start=33.195:duration=2.7,asetpts=PTS-STARTPTS,aresample=48000[a0];"
       f"[0:v]{v1}[v1];[0:a]atrim=start=65.395:duration=27.6,asetpts=PTS-STARTPTS,aresample=48000[a1];"
       f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a];"
       f"[v]subtitles='{sub}'[outv]")
    body=a.out_dir/"004_BODY_V49_RU_SAFE.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-i",str(a.source),
      "-filter_complex_threads","1","-filter_complex",f,"-map","[outv]","-map","[a]",
      "-c:v","libx264","-threads","2","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
      "-r","30","-c:a","aac","-b:a","224k","-ar","48000","-ac","2",str(body)],check=True)
    final=a.out_dir/"004_V49_OFFICIAL_PRIVATE.mp4"
    subprocess.run(["python3",str(root/"tools/assemble_with_outro.py"),str(body),
      "-o",str(final),"--title",str(a.title),"--preset","ultrafast",
      "--crf","19","--audio-bitrate","256k","--body-lufs","-14.5","--body-gain-db","0.5"],check=True)
    subprocess.run(["python3",str(root/"skills/ext/ffmpeg-skill/scripts/check.py"),
      str(final),"--platform","shorts","--json"],check=True)
    subprocess.run(["python3",str(root/"skills/ext/ffmpeg-skill/scripts/look.py"),
      str(final),"--overwrite","--tiles","3x2","--safe","shorts","-o",
      str(a.out_dir/"004_V49_final_look.jpg")],check=True)
    print("PRIVATE_REVIEW_ONLY",final)

if __name__=="__main__":
    main()
