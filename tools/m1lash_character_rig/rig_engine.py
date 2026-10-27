#!/usr/bin/env python3
"""Reusable articulated PNG character engine. Transparent sprites + per-part pose timeline."""
import argparse,json,math,subprocess
from pathlib import Path
from PIL import Image

def easing(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def at(keys,t):
    keys=sorted(keys,key=lambda k:k["t"])
    if t<=keys[0]["t"]:return keys[0]["v"]
    for a,b in zip(keys,keys[1:]):
        if a["t"]<=t<=b["t"]:
            return a["v"]+(b["v"]-a["v"])*easing((t-a["t"])/(b["t"]-a["t"]))
    return keys[-1]["v"]
def paste(canvas,sprite,pivot,angle,x,y,scale):
    sprite=sprite.resize((max(1,round(sprite.width*scale)),max(1,round(sprite.height*scale))),Image.Resampling.BICUBIC)
    side=math.ceil(math.hypot(sprite.width,sprite.height)*1.7)+4
    blank=Image.new("RGBA",(side,side))
    ox=side//2-round(pivot[0]*scale);oy=side//2-round(pivot[1]*scale)
    blank.alpha_composite(sprite,(ox,oy))
    blank=blank.rotate(angle,resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(blank,(round(x-side/2),round(y-side/2)))
def validate(s):
    assert 0<s["duration"]<=300 and 1<=s["fps"]<=60
    assert 16<=s["width"]<=4096 and 16<=s["height"]<=4096
    for actor in s["characters"]:
        for part in actor["parts"].values():
            assert part["file"].endswith(".png") and len(part["anchor"])==2
            for axis,keys in part.get("animation",{}).items():
                assert axis in ("x","y","angle","scale")
                assert keys and all(keys[i]["t"]<keys[i+1]["t"] for i in range(len(keys)-1))
def render(s,sprites,t):
    scene=Image.new("RGBA",(s["width"],s["height"]),tuple(s.get("background",[240,242,243,255])))
    for actor in s["characters"]:
        for key,part in sorted(actor["parts"].items(),key=lambda kv:kv[1].get("z",0)):
            movement=part.get("animation",{})
            pose={}
            for axis,default in (("x",part["anchor"][0]),("y",part["anchor"][1]),("angle",0),("scale",1)):
                pose[axis]=at(movement[axis],t) if axis in movement else default
            img=sprites[(actor["id"],key)]
            paste(scene,img,part.get("pivot",[img.width//2,img.height//2]),pose["angle"],pose["x"],pose["y"],pose["scale"])
    return scene.convert("RGB")
def main():
    p=argparse.ArgumentParser();p.add_argument("project");p.add_argument("output");p.add_argument("--audio")
    args=p.parse_args()
    folder=Path(args.project).resolve().parent;s=json.loads(Path(args.project).read_text())
    validate(s)
    sprites={(actor["id"],name):Image.open(folder / part["file"]).convert("RGBA")
        for actor in s["characters"] for name,part in actor["parts"].items()}
    cmd=["ffmpeg","-y","-nostdin","-v","error","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f'{s["width"]}x{s["height"]}',"-r",str(s["fps"]),"-i","-"]
    if args.audio:cmd+=["-i",args.audio,"-map","0:v:0","-map","1:a:0"]
    cmd+=["-c:v","libx264","-crf","19","-pix_fmt","yuv420p"]
    if args.audio:cmd+=["-c:a","aac","-b:a","160k"]
    cmd+=["-t",str(s["duration"]),"-movflags","+faststart",args.output]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(round(s["duration"]*s["fps"])):
        proc.stdin.write(render(s,sprites,i/s["fps"]).tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError("ffmpeg render failed")
if __name__=="__main__":main()
