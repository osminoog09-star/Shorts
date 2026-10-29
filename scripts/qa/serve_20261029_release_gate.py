#!/usr/bin/env python3
"""Fail-closed Serve Shorts audio/visual release gate. Does NOT claim perceptual lip sync."""
import json, subprocess, sys, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/"work/serve_20261029"
def probe(path):
 return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],text=True))
def main():
 manifest=P/"voice_manifest.json"
 if not manifest.exists():sys.exit("NO-GO: missing genuine Dima TTS manifest")
 m=json.loads(manifest.read_text(encoding="utf-8"))
 if len(m)!=10 or any(x.get("speaker")!="dima" or x.get("voice_id")!="ru-RU-DmitryNeural" or x.get("engine")!="Microsoft Edge TTS" or not pathlib.Path(x["source_file"]).is_file() for x in m):
  sys.exit("NO-GO: wrong/missing voice segment")
 for x in m:
  if not any(s["codec_type"]=="audio" for s in probe(x["source_file"])["streams"]):sys.exit("NO-GO: voice stream missing")
 video=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else None
 if not video or not video.exists():sys.exit("NO-GO: final MP4 not present")
 info=probe(video);streams=info["streams"]
 if not any(s.get("codec_type")=="video" and s.get("width")==1080 and s.get("height")==1920 for s in streams):sys.exit("NO-GO: not 1080x1920")
 if not any(s.get("codec_type")=="audio" for s in streams):sys.exit("NO-GO: no audio")
 subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(video),"-f","null","-"],check=True)
 lip=P/"lipsync_review.json"
 if not lip.exists():sys.exit("NO-GO: approved host lip-sync evidence missing")
 evidence=json.loads(lip.read_text(encoding="utf-8"))
 if evidence.get("approved_host") is not True or evidence.get("reviewed_audio") is not True or evidence.get("reviewed_lipsync") is not True:sys.exit("NO-GO: manual host/audio/lipsync review missing")
 print("Technical gate PASS; manual review evidence present; verify rights and metadata before publication")
if __name__=="__main__":main()
