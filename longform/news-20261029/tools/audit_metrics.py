import subprocess,json,sys
import numpy as np
from pathlib import Path
src,out=sys.argv[1:3];fps=15;w,h=160,90
p=subprocess.Popen(['ffmpeg','-v','error','-i',src,'-vf',f'fps={fps},scale={w}:{h}:flags=area,format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
means=[];diffs=[];prev=None
while True:
 b=p.stdout.read(w*h)
 if len(b)!=w*h:break
 a=np.frombuffer(b,np.uint8).astype(np.float32);means.append(float(a.mean()));diffs.append(0 if prev is None else float(np.abs(a-prev).mean()));prev=a
p.wait();peaks=[]
for i in range(2,len(diffs)-2):
 if diffs[i]>18 and diffs[i]>=max(diffs[i-1],diffs[i+1]):peaks.append({'t':round(i/fps,3),'difference':round(diffs[i],2)})
flashes=[]
for i in range(2,len(means)-3):
 base=(means[i-2]+means[i+3])/2
 if abs(means[i]-base)>25 and abs(means[i-2]-means[i+3])<12:
  if not flashes or i/fps-flashes[-1]['t']>.5:flashes.append({'t':round(i/fps,3),'luminance':round(means[i],2),'baseline':round(base,2)})
r={'video':Path(src).name,'frames_sampled':len(means),'fps':fps,'max_adjacent_difference':round(max(diffs),2),'adjacent_diff_p99':round(float(np.percentile(diffs,99)),2),'large_change_peaks':peaks,'short_luminance_pulses':flashes,'black_frames':sum(x<3 for x in means),'white_frames':sum(x>250 for x in means),'method':'160x90 luma at15fps; short pulse is >25/255 from two-sided baseline returning within 5 frames; candidate detector, not medical certification'}
Path(out).write_text(json.dumps(r,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in r.items() if k not in ['large_change_peaks','short_luminance_pulses']},ensure_ascii=False));print('peaks',len(peaks),'pulses',len(flashes),flashes[:8])
