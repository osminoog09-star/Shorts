#!/usr/bin/env python3
"""Two fresh Chigur Shorts: genuine movie audio, Dima hook/reveal, approved outro.

The licensed/copyrighted source is NOT added to the public repository. Uses
recoverable private Actions artifacts or explicitly mounted local source paths.
Never invent actor lines, overdub their speech, set YouTube dates or upload.
"""
from pathlib import Path
import os, json, subprocess, hashlib, io, zipfile, shutil, urllib.request
ROOT=Path(__file__).resolve().parents[2]
JOB=json.loads((ROOT/os.environ['M1LASH_JOB_PATH']).read_text(encoding="utf8"))
WORK=ROOT/"motion-output"/"nov04_movies";WORK.mkdir(parents=True,exist_ok=True)
TTS=ROOT/"media/tts/next_two_movies_20261104"
QA=ROOT/"reports/research/qa/nov04_movies";QA.mkdir(parents=True,exist_ok=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ITEMS=[
 dict(id="chigur_roadstop_20261104",tag="ДВЕ МАШИНЫ. ОДНА ОСТАНОВКА",src_id=13070052528,
      filename="chigur_actual_driver_2007_ru.mp4",start=66.0,duration=32.0,
      hook="driver_hook",reveal="driver_reveal",scene="Встреча на пустой дороге"),
 dict(id="chigur_tracker_20261104",tag="КТО-ТО УЖЕ БЛИЗКО",src_id=13070325354,
      filename="chigur_tracker_ok_candidate.mp4",start=5.0,duration=38.0,
      hook="tracker_hook",reveal="tracker_reveal",scene="Сигнал в мотеле")
]
def call(cmd):
 print("RUN",str(cmd[:6]),flush=True)
 return subprocess.run([str(x) for x in cmd],check=True)
def probe_dur(src):
 return float(json.loads(subprocess.check_output(
 ["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(src)]))["format"]["duration"])
def fetch_source(item):
 local=os.environ.get("CHIGUR_PRIVATE_SOURCE_DIR")
 if local:
  pp=list(Path(local).rglob(item["filename"]))
  if pp:return pp[0]
 token=os.environ.get("GITHUB_TOKEN")
 if not token:raise RuntimeError("Missing approved private movie source: set CHIGUR_PRIVATE_SOURCE_DIR or GITHUB_TOKEN")
 url="https://api.github.com/repos/osminoog09-star/Shorts/actions/artifacts/"+str(item["src_id"])+"/zip"
 req=urllib.request.Request(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"m1lash-studio"})
 zipdata=urllib.request.urlopen(req,timeout=180).read()
 with zipfile.ZipFile(io.BytesIO(zipdata)) as z:
  found=[n for n in z.namelist() if n.endswith("/"+item["filename"])]
  if len(found)!=1:raise RuntimeError("No expected licensed input file in source artifact")
  dest=WORK/item["filename"];dest.write_bytes(z.read(found[0]));return dest
def drawfilter(label):
 # 9:16 full-frame composition: center-safe live video, top banner not over eyes.
 safe=label.replace(":"," ").replace("'","").replace("\\","")
 return ("fps=30,crop=608:1080:(iw-608)/2:0,scale=1080:1920,setsar=1,"
         "drawbox=x=0:y=43:w=1080:h=165:color=black@0.54:t=fill,"
         f"drawtext=fontfile={FONT}:text='{safe}':fontcolor=white:fontsize=37:x=(w-text_w)/2:y=101,"
         "format=yuv420p")
def make_part(src,aud,start,duration,label,output,still=False):
 filt=drawfilter(label)
 cmd=["ffmpeg","-v","error","-nostdin","-y","-ss",f"{start:.3f}","-i",str(src)]
 if aud:
  cmd+=["-i",str(aud)]
 if still:
  # reveal: freeze a film frame, not a fake actor line.
  filt=filt+",tpad=stop_mode=clone:stop_duration=8"
 cmd+=["-t",f"{duration:.3f}","-vf",filt,"-map","0:v:0"]
 cmd+=["-map",("1:a:0" if aud else "0:a:0"),"-c:v","libx264","-preset","veryfast","-crf","18",
       "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k","-ar","48000",
       "-ac","2","-af","aresample=async=1:first_pts=0","-movflags","+faststart",str(output)]
 call(cmd)
 if abs(probe_dur(output)-duration)>.2:raise RuntimeError("unexpected segment duration")
def master(item):
 src=fetch_source(item)
 if probe_dur(src)<item["start"]+item["duration"]:raise RuntimeError("source unexpectedly truncated")
 base=WORK/item["id"];base.mkdir(parents=True,exist_ok=True)
 hook=TTS/(item["hook"]+".mp3");reveal=TTS/(item["reveal"]+".mp3")
 if not hook.exists() or not reveal.exists():raise FileNotFoundError("Dima TTS missing")
 a=probe_dur(hook)+.05;b=probe_dur(reveal)+.08
 intro=base/"intro.mp4";movie=base/"real_movie_sound.mp4";ending=base/"dima_reveal.mp4"
 make_part(src,hook,item["start"],a,item["tag"],intro)
 make_part(src,None,item["start"],item["duration"],item["tag"],movie)
 make_part(src,reveal,item["start"]+item["duration"]-.2,b,"ФИЛЬМ: СТАРИКАМ ТУТ НЕ МЕСТО",ending,True)
 listing=base/"body_concat.txt";listing.write_text("".join(f"file '{x}'\n" for x in [intro,movie,ending]))
 body=base/"body.mp4"
 call(["ffmpeg","-v","error","-nostdin","-y","-f","concat","-safe","0","-i",str(listing),
       "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30",
       "-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-movflags","+faststart",str(body)])
 out=ROOT/"videos"/(item["id"]+".mp4");out.parent.mkdir(exist_ok=True)
 call(["python",str(ROOT/"tools/assemble_with_outro.py"),str(body),"-o",str(out),"--max-seconds","65",
       "--preset","fast","--crf","18"])
 from pathlib import Path
 check=base/"check.json"
 with check.open("w") as f:
  subprocess.run(["python",str(ROOT/"skills/ext/ffmpeg-skill/scripts/check.py"),str(out),
       "--platform","shorts","--json"],stdout=f,check=True)
 call(["python",str(ROOT/"skills/ext/ffmpeg-skill/scripts/look.py"),str(out),"--tiles","3x2",
       "--output",str(base/"look.jpg")])
 call(["ffmpeg","-v","error","-xerror","-i",str(out),"-f","null","-"])
 report=dict(id=item["id"],title_policy="only movie title in Dima's final reveal",source_artifact_id=item["src_id"],
      source_span=[item["start"],item["start"]+item["duration"]],actor_sound="original source AAC reencoded in proof only, no synthetic actor voice",
      owner_listening="NOT VERIFIED",actor_ru_asr="NOT VERIFIED",visual="CONTACT GENERATED; OWNER REVIEW PENDING",
      rights="Original film copyright; no license implied",bytes=out.stat().st_size,
      sha256=hashlib.sha256(out.read_bytes()).hexdigest(),duration=probe_dur(out),source_file_not_committed=True)
 (base/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 shutil.copy2(out,WORK/out.name);shutil.copy2(base/"look.jpg",QA/(item["id"]+"_look.jpg"))
 print("PRIVATE_REVIEW",item["id"],report["duration"],report["sha256"],flush=True)
if __name__=="__main__":
 for item in ITEMS:
  if JOB.get("only_ids") and item["id"] not in JOB["only_ids"]:continue
  master(item)
