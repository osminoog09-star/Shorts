#!/usr/bin/env python3
"""Compare two real MP4 pilot versions without calling image changes 'new animation'.

Usage: python tools/m1lash_qa/pilot_compare.py old.mp4 candidate.mp4 --output pilot_compare.json
Requires cv2 + numpy. The output is diagnostic, NOT an artistic approval.
"""
import argparse, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np

def collect(path):
    cap=cv2.VideoCapture(str(path))
    fps=cap.get(cv2.CAP_PROP_FPS)
    frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if not fps or not frames: raise ValueError(f"Unable to decode video {path}")
    duration=frames/fps
    gray=[];color=[]
    for t in np.arange(0,duration,1):
        cap.set(cv2.CAP_PROP_POS_MSEC,float(t*1000))
        ok,frame=cap.read()
        if not ok: continue
        frame=cv2.resize(frame,(96,54),interpolation=cv2.INTER_AREA)
        color.append(frame)
        gray.append(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY))
    cap.release()
    if len(gray)<2:raise ValueError("Too few frames")
    deltas=[float(np.mean(cv2.absdiff(gray[i-1],gray[i]))) for i in range(1,len(gray))]
    rough_patterns=[tuple((cv2.resize(a,(8,8))>a.mean()).reshape(-1)) for a in gray]
    quiet=sum(v<3.0 for v in deltas)
    return {
        "duration_seconds":round(duration,3),"sampled_seconds":len(gray),
        "near_static_1s_transitions":quiet,
        "near_static_transition_ratio":round(quiet/len(deltas),3),
        "sampled_coarse_visual_patterns":len(set(rough_patterns)),
        "mean_frame_change":round(float(np.mean(deltas)),3),
        "limitations":"Cannot distinguish camera zoom from truly new acting, nor judge story fit, character identity or animation quality."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("baseline");ap.add_argument("candidate");ap.add_argument("--output")
    a=ap.parse_args()
    old,new=collect(a.baseline),collect(a.candidate)
    result={"baseline":old,"candidate":new,
      "delta_near_static_ratio":round(new["near_static_transition_ratio"]-old["near_static_transition_ratio"],3),
      "status":"AUTOMATED DIAGNOSTIC ONLY: requires director review of new actions, lipsync, visual design and end scene"}
    s=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s,encoding="utf-8")
    print(s)
