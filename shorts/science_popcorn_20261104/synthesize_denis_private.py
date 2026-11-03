#!/usr/bin/env python3
"""Private, offline Denis-only speech for the popcorn Short.

NEVER push reference, prompt, waveform or generated master to public Git.
Requires already cached Qwen3-TTS-12Hz-0.6B-Base and local Whisper. No network.
If requirements are unavailable, raises VOICE_BLOCKED (no fallback).
"""
import os
for k,v in {
 "ORT_DISABLE_TELEMETRY":"1", "HF_HUB_DISABLE_TELEMETRY":"1",
 "GRADIO_ANALYTICS_ENABLED":"False", "DO_NOT_TRACK":"1",
 "HF_HUB_OFFLINE":"1", "TRANSFORMERS_OFFLINE":"1",
 "TOKENIZERS_PARALLELISM":"false",
}.items(): os.environ[k]=v

import argparse, difflib, hashlib, json, re
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SPEC=json.loads((HERE/"spec.json").read_text(encoding="utf8"))
VOICE=SPEC["voice"]
assert VOICE["speaker"]=="denis" and VOICE["engine"]=="qwen3-tts-local"
assert VOICE["voice_id"]=="denis-qwen3tts-reference-v1"

def norm(s):
 return " ".join(re.findall(r"[а-яё0-9]+",s.lower()))

def run(args):
 a=args.parse_args()
 ref=Path(a.private_reference).resolve()
 out=Path(a.private_output).resolve()
 model_path=Path(a.local_model).resolve()
 if not ref.is_file(): raise RuntimeError("VOICE_BLOCKED: private approved reference absent")
 if not model_path.is_dir() or not list(model_path.rglob("*.safetensors")):
  raise RuntimeError("VOICE_BLOCKED: local Qwen weights absent; no online model download")
 whisper_path=Path(a.whisper_model).resolve()
 if not whisper_path.is_dir() or not list(whisper_path.rglob('*.bin')) and not list(whisper_path.rglob('*.model')):
  raise RuntimeError('VOICE_BLOCKED: offline Whisper model weights are absent; no download')
 if out==ROOT or ROOT in out.parents:
  raise RuntimeError("VOICE_BLOCKED: cannot create owner voice inside public Git repo")
 out.mkdir(parents=True,exist_ok=True)
 import torch
 from qwen_tts import Qwen3TTSModel
 from faster_whisper import WhisperModel
 torch.set_num_threads(4);torch.set_num_interop_threads(1)
 torch.manual_seed(20261104)
 engine=Qwen3TTSModel.from_pretrained(str(model_path),device_map="cpu",
    dtype=torch.float32,attn_implementation="eager",local_files_only=True)
 voice_prompt=engine.create_voice_clone_prompt(ref_audio=str(ref),x_vector_only_mode=True)
 # The independent word aligner must also stay entirely offline.
 whisper=WhisperModel(str(whisper_path),device="cpu",compute_type="int8",
    cpu_threads=4,local_files_only=True)
 at=0.0;segments=[];caps=[];clips=[];meta=[]
 for scene in SPEC["scenes"]:
  for line_idx,line in enumerate(scene["voice"]):
   idx=len(segments)+1; wav_path=out/("denis_%02d.wav"%idx)
   receipt=out/("denis_%02d.provenance.json"%idx)
   identity=dict(text=line,model=str(model_path),engine=VOICE["engine"],
                 voice_id=VOICE["voice_id"],speaker="denis",
                 ref_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),
                 seed=300+idx,temperature=.7,max_new_tokens=320)
   if wav_path.exists() or receipt.exists():
    if not wav_path.is_file() or not receipt.is_file():
     raise RuntimeError(f"VOICE_BLOCKED: incomplete checkpoint line {idx}; never trust orphan WAV")
    old=json.loads(receipt.read_text(encoding="utf8"))
    if any(old.get(k)!=v for k,v in identity.items()):
     raise RuntimeError(f"VOICE_BLOCKED: line {idx} checkpoint voice/ref/text mismatch")
    if old.get("wav_sha256")!=hashlib.sha256(wav_path.read_bytes()).hexdigest():
     raise RuntimeError(f"VOICE_BLOCKED: line {idx} checkpoint bytes changed")
    audio,sr=sf.read(wav_path,dtype="float32")
    print("VOICE_CHECKPOINT_REUSED",idx,flush=True)
   else:
    torch.manual_seed(300+idx)
    generated,sr=engine.generate_voice_clone(text=line,language="Russian",
        voice_clone_prompt=voice_prompt,max_new_tokens=320,temperature=.7)
    audio=np.asarray(generated[0],dtype=np.float32)
    nonzero=np.flatnonzero(np.abs(audio)>.002)
    if len(nonzero): audio=audio[max(0,nonzero[0]-round(sr*.06)):min(len(audio),nonzero[-1]+round(sr*.12))]
    if audio.size<sr*.4: raise RuntimeError("VOICE_BLOCKED: anomalous zero-length utterance")
    tmp=out/("denis_%02d.partial.wav"%idx)
    sf.write(tmp,audio,sr)
    wav_sha=hashlib.sha256(tmp.read_bytes()).hexdigest()
    tmp.replace(wav_path)
    identity["wav_sha256"]=wav_sha
    receipt.write_text(json.dumps(identity,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("VOICE_CHECKPOINT_SAVED",idx,wav_sha[:16],flush=True)
   rows,info=whisper.transcribe(str(wav_path),beam_size=3,language="ru",
         word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
   rows=list(rows)
   actual=" ".join(s.text for s in rows).strip()
   sim=difflib.SequenceMatcher(None,norm(line),norm(actual)).ratio()
   if sim<.85: raise RuntimeError(f"VOICE_REVIEW_REQUIRED line {idx}: similarity={sim:.3f}, generated={actual!r}")
   words=[w for row in rows for w in (row.words or [])]
   if not words:raise RuntimeError("VOICE_BLOCKED: missing actual word timestamps")
   dur=len(audio)/sr
   segments.append(dict(id=f"denis_{idx:02}",start=at,end=at+dur,
      text=line,scene=scene["n"],speaker="denis",
      voice_id=VOICE["voice_id"],engine=VOICE["engine"],
      rate=1.0,source_file=str(wav_path)))
   local_caps=[]
   for j in range(0,len(words),4):
    chunk=words[j:j+4]
    if not chunk: continue
    stop=words[j+4].start if j+4<len(words) else dur
    local_caps.append(dict(start=at+chunk[0].start,end=at+stop,words=[w.word.strip() for w in chunk]))
   # Actual word timing can yield a 0.1-0.5s final group; combine instead of flashing unreadable text.
   combined=[]
   for group in local_caps:
    if group["end"]-group["start"]<.85 and combined:
     combined[-1]["end"]=group["end"]
     combined[-1]["words"]+=group["words"]
    else:combined.append(group)
   if len(combined)>1 and combined[0]["end"]-combined[0]["start"]<.85:
    combined[1]["words"]=combined[0]["words"]+combined[1]["words"]
    combined[1]["start"]=combined[0]["start"]
    combined.pop(0)
   if any(x["end"]-x["start"]<.7 for x in combined):
    raise RuntimeError(f"VOICE_REVIEW_REQUIRED: unreadable caption group on line {idx}")
   caps.extend(combined)
   meta.append(dict(id=idx,expected=line,actual=actual,similarity=sim,seconds=dur))
   clips.append((audio,sr))
   at+=dur+.08
 if not 30<=at+6.6<=59:
  raise RuntimeError(f"VOICE_REVIEW_REQUIRED duration={at+6.6:.2f}s outside approved Shorts window")
 # Sample rate and speech consistent; concatenate only one model's lines.
 sr_set={sr for _,sr in clips}
 if len(sr_set)!=1: raise RuntimeError("VOICE_BLOCKED: mismatched sample rates")
 sr=sr_set.pop()
 pieces=[]
 for a,_ in clips: pieces.extend([a,np.zeros(round(sr*.08),dtype=np.float32)])
 joined=np.concatenate(pieces)
 sf.write(out/"denis_story_NO_OUTRO.wav",joined,sr)
 data=dict(id=SPEC["id"],theme="popcorn",label="M1lash · НАУКА",
  headlines=SPEC["headlines"],sources=SPEC["sources"],
  segments=segments,caps=caps,voice_id=VOICE["voice_id"],
  engine=VOICE["engine"],total=len(joined)/sr,
  cuts=[0.]+[segments[2*i]["start"] for i in range(1,6)]+[len(joined)/sr],
  actual_audio=True,qa=dict(asr=meta,personal_listening="PENDING_OWNER",
  no_old_dima=True,external_speech_transmission=False))
 (out/"denis_true_timeline_PRIVATE.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 print("PRIVATE_DENIS_AUDIO_ONLY",out,"seconds",round(data["total"],3))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--private-reference",required=True)
 p.add_argument("--local-model",required=True)
 p.add_argument("--private-output",required=True)
 p.add_argument("--whisper-model",required=True,help="Path to local faster-whisper model directory (no downloads)")
 run(p)
