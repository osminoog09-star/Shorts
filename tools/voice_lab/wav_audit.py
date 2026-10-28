#!/usr/bin/env python3
"""M1lash voice lab: objective WAV hygiene. Not a naturalness or identity judge.
Use only audio you own or have explicit rights to process.
"""
import argparse
import hashlib
import json
import math
import struct
import wave
from pathlib import Path

def inspect(path):
    path=Path(path)
    if not path.is_file() or path.suffix.lower()!=".wav":
        raise ValueError("WAV file required")
    with wave.open(str(path),"rb") as w:
        channels=w.getnchannels();sw=w.getsampwidth();sr=w.getframerate()
        frames=w.getnframes();comp=w.getcomptype()
        if comp!="NONE" or sw!=2 or channels not in (1,2):
            raise ValueError("must be uncompressed 16-bit PCM mono/stereo")
        if sr<16000 or sr>96000 or frames<=0:
            raise ValueError("unsupported sample rate/empty file")
        # Stream the samples in chunks; do not load a whole 21-minute recording.
        count=0;peaks=0;silent=0;sum2=0.0;max_abs=0
        for _ in range(0,frames,8192):
            raw=w.readframes(8192)
            if not raw:break
            values=struct.unpack("<"+"h"*(len(raw)//2),raw)
            for x in values:
                v=abs(x);max_abs=max(max_abs,v);sum2+=x*x;count+=1
                if v>=32700:peaks+=1
                if v<328:silent+=1
    if count==0:raise ValueError("no PCM samples")
    duration=frames/sr
    with path.open("rb") as source: digest=hashlib.file_digest(source,"sha256").hexdigest()
    return {
      "file":path.name,"sha256":digest,"duration_s":round(duration,3),
      "sample_rate":sr,"channels":channels,"rms_dbfs":round(20*math.log10(max(math.sqrt(sum2/count)/32768,1e-12)),2),
      "sample_peak_dbfs":round(20*math.log10(max(max_abs/32768,1e-12)),2),
      "near_clip_samples_pct":round(100*peaks/count,4),
      "below_minus40dbfs_samples_pct":round(100*silent/count,2),
      "warning":"No proof of voice identity, pronunciation, clipping distortion, rights or speech naturalness; listen manually and transcribe."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("--output")
    a=p.parse_args()
    x=inspect(a.wav)
    out=json.dumps(x,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(out+"\n",encoding="utf-8")
    print(out)
if __name__=="__main__":main()
