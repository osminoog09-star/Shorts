"""Generate estimated mouth poses from Russian word times and the narration envelope."""
from pathlib import Path
import argparse, json, re
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

def pose(letter):
    if letter in "бпм":
        return 0
    if letter in "оёую":
        return 3
    if letter in "ая":
        return 2
    if letter in "вфзсцджчшщ":
        return 4
    return 1

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("base",type=Path)
    p.add_argument("out",type=Path)
    p.add_argument("model",type=Path)
    args=p.parse_args()
    model=WhisperModel(str(args.model),device="cpu",compute_type="int8",cpu_threads=4,local_files_only=True)
    samples,rate=sf.read(args.base/"narration_raw.wav",dtype="float32")
    assert rate==24000 and samples.ndim==1
    wav=resample_poly(samples,2,3).astype("float32")
    env=np.fromfile(args.out/"voice_envelope.u8",dtype="u1")
    result=np.full(len(env),255,dtype="u1")
    audit=json.loads((args.base/"full_audio_audit.json").read_text("utf-8"))
    words_found=0
    for index,u in enumerate(audit["utterances"],1):
        offset=max(0,u["start"]-.07)
        piece=wav[round(offset*16000):round((u["end"]+.07)*16000)].copy()
        segments,_=model.transcribe(piece,language="ru",beam_size=1,word_timestamps=True,
                                    vad_filter=False,condition_on_previous_text=False)
        for segment in segments:
            for word in segment.words or []:
                letters=re.sub(r"[^а-яё]","",word.word.lower())
                a=max(0,round((offset+word.start)*30))
                b=min(len(result),round((offset+word.end)*30))
                if not letters or b<=a:
                    continue
                words_found+=1
                for j in range(a,b):
                    k=min(len(letters)-1,int((j-a+.5)*len(letters)/(b-a)))
                    result[j]=pose(letters[k]) if env[j]>=8 else 0
        if index%20==0:
            print(index,words_found,flush=True)
    result.tofile(args.out/"mouth_poses.u8")
    stat={"words":words_found,"frames":len(result),"timed_frames":int(np.sum(result!=255)),
          "voiced_frames":int(np.sum(env>=8)),"timed_voiced_frames":int(np.sum((env>=8)&(result!=255)))}
    (args.out/"mouth_poses.json").write_text(json.dumps(stat,indent=2)+"\n",encoding="utf-8")
    print(stat,flush=True)

if __name__=="__main__":
    main()
