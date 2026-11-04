#!/usr/bin/env python3
"""M1lash Мульт EP01: original 3D, deterministic browser stills/pilot ONLY.
No voice, no outro, no YouTube, no writes to other shorts.
"""
from __future__ import annotations
import json,math,os,sys,shutil,subprocess,hashlib,urllib.request,time
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
JOB=ROOT/os.environ["M1LASH_JOB_PATH"]
cfg=json.loads((HERE/"episode.json").read_text(encoding="utf8"))
job=json.loads(JOB.read_text(encoding="utf8"))
assert cfg["id"]=="m1lash_mult_ep01"
assert cfg["style"]=="S9-D3"
assert cfg["characters"][0]["voice"]["speaker"]=="denis"
assert cfg["characters"][1]["voice"]["speaker"]=="aks"
assert cfg["characters"][1]["voice"]["voice_id"]!="denis-qwen3tts-reference-v1"
assert job.get("only_id")=="m1lash_mult_ep01"
assert job.get("mode") in ("stills","pilot")
assert job.get("preflight_only") is True
assert job.get("save_review_mp4") is not True
OUT=ROOT/"motion-output"/"m1lash_mult_ep01"/job["mode"]
OUT.mkdir(parents=True,exist_ok=True)
def get_three():
 p=HERE/"three.min.js"
 if p.is_file() and p.stat().st_size>300000:return
 endpoints=[
  "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
  "https://unpkg.com/three@0.128.0/build/three.min.js",
  "https://raw.githubusercontent.com/mrdoob/three.js/r128/build/three.min.js",
 ]
 for url in endpoints:
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"M1lashStudio/1.0"})
   with urllib.request.urlopen(request,timeout=18) as stream:
    data=stream.read()
   if len(data)<300000:raise RuntimeError("three library too short")
   p.write_bytes(data)
   print("THREE_LOCAL",len(data),flush=True)
   return
  except Exception as ex:
   print("THREE_SOURCE_FAIL",url,str(ex)[:150],flush=True)
 raise RuntimeError("THREE_FETCH_BLOCKED — no browser rendering attempted")
def ff(args):
 subprocess.run([str(x) for x in args],check=True)
def main():
 get_three()
 stills=[]; stat=[]
 with sync_playwright() as play:
  browser=play.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files",
   "--use-gl=angle","--use-angle=swiftshader","--enable-webgl",
   "--disable-background-timer-throttling"])
  page=browser.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
  errors=[]
  page.on("pageerror",lambda err:errors.append(str(err)))
  page.goto((HERE/"film.html").as_uri(),wait_until="load",timeout=30000)
  page.wait_for_function("window.ready===true",timeout=30000)
  meta=page.evaluate("() => ({three:THREE.REVISION,canSeek:typeof window.seek==='function',canvas:document.querySelector('canvas')?.width})")
  print("RENDERER",meta,flush=True)
  if meta["canvas"]!=1080 or not meta["canSeek"]:raise RuntimeError("Wrong 3D viewport")
  times=[1.5,8.0,14.5,21.5,27.0,34.5]
  for i,t in enumerate(times):
   page.evaluate("(t)=>window.seek(t)",t)
   path=OUT/f"scene_{i+1:02}.jpg"
   page.screenshot(path=str(path),type="jpeg",quality=87)
   im=Image.open(path).convert("RGB")
   extrema=im.getextrema()
   if im.size!=(1080,1920) or all(hi-lo<5 for lo,hi in extrema):
    raise RuntimeError(f"Scene {i+1} blank or wrong-size screenshot")
   pix=im.resize((54,96)).convert("RGB"); colors=len(pix.getcolors(54*96) or [])
   stat.append({"n":i+1,"t":t,"path":str(path.relative_to(ROOT)),"colors":colors,"bytes":path.stat().st_size})
   if colors<200:raise RuntimeError("Scene has unexpectedly low color diversity")
   stills.append(path)
  # QA probes from the actual WebGL camera at high-risk acting times.
  acting=[]
  for t in (1.5,2.1,2.5,3.0,3.5,4.0,4.5,5.1,5.9):
   row=page.evaluate("(t)=>window.inspectActing(t)",t)
   hands=row["hands"]
   row["hands_inside_viewport"]=all(25<h["x"]<950 and 190<h["y"]<1690 for h in hands)
   row["elbows_articulated"]=all(abs(h["elbow"])>.1 for h in hands)
   acting.append(row)
  (OUT/"acting_gate.json").write_text(json.dumps({
   "source":"Actual Three.js rendered camera projection",
   "measurements":acting,"hand_clip_count":sum(not q["hands_inside_viewport"] for q in acting),
   "joint_articulation_count":sum(q["elbows_articulated"] for q in acting),
   "notes":"Numeric preflight only. Must visually inspect full MP4 for occlusions and pose quality."
  },ensure_ascii=False,indent=2)+"\n")
  # R11: independent 3D-projection gate for the plot-critical Director plaque.
  # Real screenshot at each story beat, not synthetic PIL drawing.
  badge_checks=[]
  for t in (2.8,3.1,3.3,3.5,3.7,3.9,4.1,4.3,4.5):
   q=page.evaluate("(t)=>window.inspectActing(t)",t)
   bounds=q.get("badge_bounds")
   if not bounds:raise RuntimeError(f"Director plaque has no projected bounds at {t}")
   safe=(50<bounds["left"]<bounds["right"]<970 and
         350<bounds["top"]<bounds["bottom"]<1530)
   badge_checks.append({"t":t,"bounds":bounds,"safe":safe,"hand":q["hands"][1]})
  (OUT/"badge_gate.json").write_text(json.dumps({
    "source":"Actual Three.js camera/projection of 3D prop corners",
    "samples":badge_checks,
    "unsafe_count":sum(not q["safe"] for q in badge_checks),
    "warning":"Safe bounding boxes do not establish physically readable story motion."
  },ensure_ascii=False,indent=2)+"\n")
  for t in (2.8,3.1,3.5,3.9,4.3,4.5):
   page.evaluate("(t)=>window.seek(t)",t)
   page.screenshot(path=str(OUT/f"contact_{str(t).replace('.','_')}s.jpg"),
                   type="jpeg",quality=88)
  if any(not q["safe"] for q in badge_checks):
   raise RuntimeError("ART_QA_PLAQUE_CLIPPED: scene's director text outside Shorts-safe image")
  # Save actual close-up frames even if a hard gate rejects the render.
  for t in (2.0,3.5,4.5):
   page.evaluate("(t)=>window.seek(t)",t)
   page.screenshot(path=str(OUT/f"acting_{str(t).replace('.','_')}s.jpg"),
                   type="jpeg",quality=88)
  print("ACTING_GATE","samples",len(acting),
        "hand_clips",sum(not q["hands_inside_viewport"] for q in acting),flush=True)
  if any(not q["hands_inside_viewport"] for q in acting):
   raise RuntimeError("ART_QA_HAND_CLIP: hand outside 25..950px horizontal or 190..1690px vertical safe-area")
  if not all(q["elbows_articulated"] for q in acting):
   raise RuntimeError("ART_QA_ELBOW: one or more sample poses have straight, unarticulated arms")
  sheet=Image.new("RGB",(900,1100),(21,29,44))
  draw=ImageDraw.Draw(sheet)
  for i,path in enumerate(stills):
   im=Image.open(path).convert("RGB");im.thumbnail((300,530))
   x=i%3*300;y=i//3*550
   sheet.paste(im,(x,y+18));draw.text((x+9,y+3),f"{i+1:02} • {times[i]}s",fill="#ffffff")
  sheet.save(OUT/"contact_6_original_3d.jpg",quality=89)
  if job["mode"]=="pilot":
   out=OUT/"M1lashMult_ep01_SILENT_7s_pilot.mp4"
   cmd=["ffmpeg","-v","error","-nostdin","-y","-f","image2pipe","-vcodec","mjpeg",
   "-framerate","30","-i","-","-c:v","libx264","-preset","fast","-crf","22",
   "-pix_fmt","yuv420p","-r","30","-colorspace","bt709",
   "-color_primaries","bt709","-color_trc","bt709",str(out)]
   proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
   try:
    for n in range(210):
     page.evaluate("(t)=>window.seek(t)",n/30)
     proc.stdin.write(page.screenshot(type="jpeg",quality=80))
    proc.stdin.close()
    if proc.wait():raise RuntimeError("ffmpeg pilot encode failed")
   except BaseException:
    proc.kill();raise
   ff(["ffmpeg","-v","error","-xerror","-i",out,"-f","null","-"])
   probe=json.loads(subprocess.check_output(["ffprobe","-v","error",
   "-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate:format=duration",
   "-of","json",str(out)]))
   (OUT/"pilot_ffprobe.json").write_text(json.dumps(probe,indent=2)+"\n")
   print("PILOT_ONLY_SILENT",out.stat().st_size,flush=True)
  browser.close()
 if errors:raise RuntimeError("JS exceptions: "+str(errors[:3]))
 manifest={"id":cfg["id"],"mode":job["mode"],"run_id":os.environ.get("GITHUB_RUN_ID"),
  "stills":stat,"scene_count":6,"visual_src":"Three.js r128 + Playwright",
  "stills_are_real_browser_screenshots":True,"voice":"NOT_GENERATED",
  "supporting_voice":"CAST_PENDING","outro":"NOT_ATTACHED","published":False,
  "qa":"AUTOMATIC_FRAME_SANITY_ONLY — human visual QA still required"}
 (OUT/"preflight.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 print("M1LASH_MULT_VISUAL_PREFLIGHT",job["mode"],"6 browser stills",flush=True)
if __name__=="__main__":main()
