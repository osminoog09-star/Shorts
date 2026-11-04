#!/usr/bin/env python3
"""M1lash Chigur film-only. Strict PRIVATE assembly of real film and real Denis WAVs.
No CGI, Dima/Edge fallback, public upload, or invented actor dialogue.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, wave
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
PROJECT=REPO/"longform/chigur"
OUTRO_SHA="70b066b067cec45dbaaae91ef39ee79543ac9c396d0d1bd896885b1511867dae"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def run(cmd):
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)

def probe(path):
    return json.loads(subprocess.check_output(
        ["ffprobe","-v","error","-show_entries",
         "format=duration:stream=codec_type,width,height,avg_frame_rate",
         "-of","json",str(path)],text=True))

def validate(args,edl,voices,media_index):
    if len(edl["chapters"])!=12 or len(voices["chapters"])!=12:
        raise RuntimeError("NO-GO: expected 12 chapters")
    if len(voices["utterances"])<35:
        raise RuntimeError("NO-GO: missing Denis script chunks")
    for v in voices["utterances"]:
        if (v["speaker"]!="denis" or v["engine"]!="qwen3-tts-local"
            or v["voice_id"]!="denis-qwen3tts-reference-v1"):
            raise RuntimeError("NO-GO: only authentic owner-Qwen3 WAVs, no Dima/Edge")
    timeline={}
    for ch in edl["chapters"]:
        for w in ch["broll"]+ch["proofs_after_author_section"]:
            if not 0<=w["in_s"]<w["out_s"]:
                raise RuntimeError("NO-GO: bad shot IN/OUT")
            timeline.setdefault(w["source"],[]).append((w["in_s"],w["out_s"],ch["chapter"]))
    for key,intervals in timeline.items():
        intervals.sort()
        if max(x[1] for x in intervals)>media_index["sources"][key]["usable_before_seconds"]:
            raise RuntimeError("NO-GO: nonfilm intro/outro in "+key)
        for a,b in zip(intervals,intervals[1:]):
            if a[1]>b[0]+1e-5:
                raise RuntimeError("NO-GO: repeated/overlapping source ranges: "+key)
    sources={}
    for key,meta in media_index["sources"].items():
        matched=list((args.media/"source"/key/"originals").glob("*.mp4"))
        if len(matched)!=1:raise RuntimeError("NO-GO: missing or ambiguous movie "+key)
        if sha(matched[0])!=meta["sha256"]:
            raise RuntimeError("NO-GO: movie SHA mismatch "+key)
        sources[key]=matched[0]
    if args.mode=="render" and (not args.outro.is_file() or sha(args.outro)!=OUTRO_SHA):
        raise RuntimeError("NO-GO: approved private Denis-v7 horizontal outro missing/mismatch")
    # body-review is strictly a PRIVATE intermediate, never a finished master.
    # The approved horizontal v7 must still be supplied for 'render'.
    expected={c["chapter"]:c for c in voices["chapters"]}
    result={"chapters":{}, "estimated_total_seconds":(0 if args.mode=="body-review" else 6.6),
            "author_wav_count":sum((args.voice/(u["id"]+".wav")).is_file() for u in voices["utterances"]),
            "author_wav_expected":len(voices["utterances"]),
            "actor_dialogue_semantics_verified":all(
                p["semantics_verified"] for c in edl["chapters"]
                for p in c["proofs_after_author_section"]
                if p.get("proof_type","actor_dialogue")=="actor_dialogue"),
            "ambient_windows_owner_hearing_pending":[
                p["id"] for c in edl["chapters"]
                for p in c["proofs_after_author_section"]
                if p.get("proof_type")=="source_ambient_sound"
                   and p.get("human_listening")!="verified"],
            "outro_sha256":OUTRO_SHA if args.mode=="render" else None,
            "outro_present":args.outro.is_file() and sha(args.outro)==OUTRO_SHA,
            "sources_sha256":"verified",
            "status":"INPUT_PLAN_ONLY_NOT_APPROVED"}
    for ch in edl["chapters"]:
        c=expected[ch["chapter"]]
        estimated=c["word_count"]*60/135+max(0,c["chunk_count"]-1)*.18
        available=sum(x["out_s"]-x["in_s"] for x in ch["broll"])
        if estimated>available+1:
            raise RuntimeError("NO-GO: insufficient real B-roll for "+ch["chapter"])
        result["chapters"][ch["chapter"]]={"voice_estimate_135wpm":round(estimated,2),
                                           "nonrepeating_film_pool":round(available,2)}
        result["estimated_total_seconds"]+=estimated+sum(
            x["out_s"]-x["in_s"] for x in ch["proofs_after_author_section"])
    result["estimated_total_seconds"]=round(result["estimated_total_seconds"],2)
    return sources,result

def pick_shots(pool,length):
    shots=[]
    remaining=length
    for row in pool:
        cursor=row["in_s"]
        while remaining>.003 and cursor<row["out_s"]-.10:
            dur=min(6.8,row["out_s"]-cursor,remaining)
            if dur<.15:break
            shots.append((row["source"],cursor,dur))
            remaining-=dur
            cursor+=dur
        if remaining<=.003:break
    if remaining>.04:raise RuntimeError("NO-GO: ran out of unused cinema: "+str(remaining))
    return shots

def concat(paths,out):
    txt=out.with_suffix(".concat.txt")
    txt.write_text("".join("file '"+str(p.resolve())+"'\n" for p in paths))
    run(["ffmpeg","-v","error","-nostdin","-y","-f","concat",
         "-safe","0","-i",str(txt),"-c","copy",str(out)])

def slice_video(source,start,length,dest,actor_audio,review_720=False):
    # Only private body-review may be encoded 720p/ultrafast for fast QA;
    # publishable full render remains 1920x1080 with approved outro SHA.
    width,height,preset=(1280,720,"ultrafast") if review_720 else (1920,1080,"veryfast")
    argv=["ffmpeg","-v","error","-nostdin","-y","-ss",str(round(start,6)),
          "-i",str(source),"-t",str(round(length,6)),
          "-vf",f"fps=30,scale={width}:{height}:flags=lanczos,format=yuv420p",
          "-fps_mode","cfr","-r","30","-c:v","libx264","-preset",preset,
          "-crf","21","-pix_fmt","yuv420p",
          "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709"]
    if actor_audio:
        argv+=["-map","0:v:0","-map","0:a:0",
               "-af","acompressor=threshold=-22dB:ratio=1.65:attack=15:release=170:makeup=2.5dB,loudnorm=I=-15:TP=-1.5:LRA=10,aresample=48000",
               "-ar","48000","-ac","2","-c:a","aac","-b:a","192k"]
    else:argv+=["-an"]
    run(argv+["-movflags","+faststart",str(dest)])

def sum_wav(paths):
    secs=0
    for p in paths:
        if not p.is_file():raise RuntimeError("NO-GO: missing owner WAV "+p.name)
        with wave.open(str(p),"rb") as w:
            if (w.getnchannels(),w.getframerate(),w.getsampwidth())!=(1,24000,2):
                raise RuntimeError("NO-GO: unexpected Qwen WAV format "+p.name)
            secs+=w.getnframes()/w.getframerate()
    return secs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["plan","render","body-review"])
    ap.add_argument("--media",type=Path,default=Path("/mnt/data/chigur_film_only"))
    ap.add_argument("--voice",type=Path,default=Path("/mnt/data/chigur_film_only/private_restored/voice/chigur_segments"))
    ap.add_argument("--outro",type=Path,default=Path("/mnt/data/chigur_film_only/private_restored/M1lash_outro_Denis_v7_voice10_horizontal.mp4"))
    ap.add_argument("--output",type=Path,default=Path("/mnt/data/chigur_film_only/M1lash_Chigur_FilmOnly_NEW_PRIVATE_REVIEW.mp4"))
    args=ap.parse_args()
    edl=json.loads((PROJECT/"film_only_edit_decisions_v2.json").read_text())
    voices=json.loads((PROJECT/"voice_chunks_denis_film_only.json").read_text())
    media=json.loads((PROJECT/"film_only_source_index.json").read_text())
    source,plan=validate(args,edl,voices,media)
    if args.mode=="plan":
        print(json.dumps(plan,ensure_ascii=False,indent=2));return
    proofs=[p for c in edl["chapters"] for p in c["proofs_after_author_section"]]
    unclassified=[p["id"] for p in proofs if p.get("proof_type","actor_dialogue") not in ("actor_dialogue","source_ambient_sound")]
    if unclassified:raise RuntimeError("NO-GO: unclassified proof windows: "+", ".join(unclassified))
    bad=[p["id"] for p in proofs if p.get("proof_type","actor_dialogue")=="actor_dialogue" and not p["semantics_verified"]]
    if bad:raise RuntimeError("NO-GO: actual actor RU dialogue not independently checked: "+", ".join(bad))
    # Sound-only windows are NOT spoken RU lines: require source-specific
    # waveform/signal measurement before private render. Owner must listen
    # before any upload, but this cannot veto assembly of a PRIVATE draft.
    unmeasured=[p["id"] for p in proofs if p.get("proof_type")=="source_ambient_sound"
                and ("RMS" not in p.get("asr_reference","") or p.get("human_listening") not in ("pending","verified"))]
    if unmeasured:raise RuntimeError("NO-GO: source ambience not measured: "+", ".join(unmeasured))
    absent=[u["id"] for u in voices["utterances"] if not (args.voice/(u["id"]+".wav")).is_file()]
    if absent:raise RuntimeError("NO-GO: "+str(len(absent))+" real Denis Qwen3 WAVs missing")
    tmp=args.media/"film_only_compose_work";tmp.mkdir(exist_ok=True,parents=True)
    finalpieces=[]
    for ch in edl["chapters"]:
        id=ch["chapter"]
        wavs=[args.voice/(v["id"]+".wav") for v in voices["utterances"] if v["chapter"]==id]
        length=sum_wav(wavs)
        shots=pick_shots(ch["broll"],length)
        encoded=[]
        for ix,(src,start,dur) in enumerate(shots):
            segment=tmp/f"{id}_shot{ix:02d}.mp4"
            slice_video(source[src],start,dur,segment,False,review_720=(args.mode=="body-review"))
            encoded.append(segment)
        broll=tmp/f"{id}_broll.mp4";concat(encoded,broll)
        wavlist=tmp/f"{id}_wavs.txt"
        wavlist.write_text("".join("file '"+str(w.resolve())+"'\n" for w in wavs))
        author=tmp/f"{id}_denis.wav"
        run(["ffmpeg","-v","error","-nostdin","-y","-f","concat","-safe","0",
             "-i",str(wavlist),"-ar","48000","-ac","2","-c:a","pcm_s16le",str(author)])
        chapterfilm=tmp/f"{id}_with_denis.mp4"
        run(["ffmpeg","-v","error","-nostdin","-y",
             "-i",str(broll),"-i",str(author),"-t",str(round(length,3)),
             "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac",
             "-ar","48000","-ac","2","-b:a","192k",
             "-af","loudnorm=I=-15:TP=-2:LRA=11","-movflags","+faststart",str(chapterfilm)])
        finalpieces.append(chapterfilm)
        for p in ch["proofs_after_author_section"]:
            actor=tmp/f"{id}_{p['id']}_actor.mp4"
            slice_video(source[p["source"]],p["in_s"],p["out_s"]-p["in_s"],actor,True,review_720=(args.mode=="body-review"))
            finalpieces.append(actor)
    if args.mode=="render":
        finalpieces.append(args.outro)
    else:
        print("PRIVATE BODY REVIEW: approved Denis-v7 not accessible in this environment; DO NOT PUBLISH.",flush=True)
    args.output.parent.mkdir(exist_ok=True,parents=True)
    concat(finalpieces,args.output)
    run(["ffmpeg","-v","error","-xerror","-i",str(args.output),
         "-map","0:v:0","-map","0:a:0","-f","null","-"])
    sec=float(probe(args.output)["format"]["duration"])
    if not 480<=sec<=720:
        raise RuntimeError("NO-GO: final duration outside movie-review range "+str(sec))
    print("PRIVATE "+("BODY WITHOUT OUTRO" if args.mode=="body-review" else "FULL WITH APPROVED OUTRO")+" REVIEW ONLY, no publishing authorization:",args.output,sec)

if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,FileNotFoundError,subprocess.CalledProcessError) as e:
        print("FAIL-CLOSED:",str(e),file=sys.stderr)
        sys.exit(2)
