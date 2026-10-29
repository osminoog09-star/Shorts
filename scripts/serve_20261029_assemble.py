#!/usr/bin/env python3
"""Assemble a review-only vertical cut using genuine DmitryNeural audio.
Not a final release: lip sync and approved host must still be checked.
"""
import json, pathlib, subprocess, sys, tempfile
P=pathlib.Path("work/serve_20261029")
def run(*args):
 subprocess.run(args,check=True)
def main():
 if len(sys.argv)!=3:sys.exit("usage: python scripts/serve_20261029_assemble.py ANIMATIC.mp4 OUTPUT.mp4")
 animatic,out=map(pathlib.Path,sys.argv[1:])
 m=json.loads((P/"voice_manifest.json").read_text())
 if len(m)!=10:sys.exit("NO-GO: expected ten voice segments")
 files=[]
 for seg in m:
  if seg.get("voice_id")!="ru-RU-DmitryNeural" or seg.get("engine")!="Microsoft Edge TTS":sys.exit("NO-GO: wrong voice")
  f=pathlib.Path(seg["source_file"]).resolve()
  if not f.is_file() or f.stat().st_size<1000:sys.exit("NO-GO: missing audio")
  files.append(f)
 if not animatic.is_file():sys.exit("NO-GO: missing animatic")
 out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  td=pathlib.Path(td)
  # Decode each segment to the same PCM format before concatenation.
  wavs=[]
  for i,f in enumerate(files):
   wav=td/f"{i:02}.wav"
   run("ffmpeg","-nostdin","-y","-v","error","-i",str(f),"-ar","48000","-ac","2",str(wav))
   wavs.append(wav)
  listing=td/"list.txt"
  listing.write_text("".join("file '"+str(f)+"'\n" for f in wavs))
  audio=td/"narration.wav"
  run("ffmpeg","-nostdin","-y","-v","error","-f","concat","-safe","0","-i",str(listing),"-c:a","pcm_s16le",str(audio))
  duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(audio)],text=True))
  if not 25<=duration<=100:sys.exit(f"NO-GO: unexpected narration duration {duration}")
  # Extend the original moving animatic if narration exceeds it; never accelerate narration.
  run("ffmpeg","-nostdin","-y","-v","error","-stream_loop","-1","-i",str(animatic),"-i",str(audio),"-t",str(duration),"-map","0:v:0","-map","1:a:0","-vf","scale=1080:1920:flags=lanczos,setsar=1","-r","30","-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",str(out))
 print("REVIEW-ONLY MP4:",out,"voice seconds:",round(duration,2))
 print("NO-GO: approved presenter lip sync and frame-by-frame visual QA still required")
if __name__=="__main__":main()
