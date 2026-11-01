"""Evidence check for a dialogue-free but visibly active movie interval."""
from pathlib import Path
def assess_action_window(clip:Path,start:float,end:float,lufs:float)->dict:
    import cv2,numpy as np
    evidence={"start":round(start,2),"end":round(end,2),"lufs":round(lufs,1),"median_motion":0.0,"accepted":False}
    if not (3 <= end-start <= 12) or lufs <= -45:return evidence
    cap=cv2.VideoCapture(str(clip))
    values=[];last=None
    try:
        for t in np.arange(start+.1,end-.12,.7):
            cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
            ok,frame=cap.read()
            if not ok:continue
            gray=cv2.cvtColor(cv2.resize(frame,(320,180)),cv2.COLOR_BGR2GRAY)
            if last is not None:values.append(float(np.mean(cv2.absdiff(gray,last))))
            last=gray
    finally:cap.release()
    if len(values)>=5:
        evidence["median_motion"]=round(float(np.median(values)),2)
        evidence["accepted"]=evidence["median_motion"]>=18.0
    return evidence
