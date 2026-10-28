#!/usr/bin/env python3
"""Real M1lash tobacco documentary build. No model-generated padding and no voice substitutes.
1) Curated 7-chapter manuscript -> 2) real Dmitry neural narration ->
3) measured audio-cued original graphics -> 4) MP4 ffprobe technical gate.
"""
from __future__ import annotations
import argparse,asyncio,datetime,json,math,re,subprocess,sys,wave,os,html,urllib.request,urllib.error
from pathlib import Path
import edge_tts
from render_visuals import render

HERE=Path(__file__).resolve().parent
VOICE="ru-RU-DmitryNeural"
MIN_DURATION=1260
SOURCES={
 "archaeology":"https://pubmed.ncbi.nlm.nih.gov/34635825/",
 "museum":"https://americanhistory.si.edu/explore/exhibitions/on-the-water/online/living-atlantic-world/new-tastes-new-trades/tobacco-trade",
 "patent":"https://patents.google.com/patent/US238640A/en",
 "clinical1964":"https://www.cdc.gov/tobacco-surgeon-general-reports/about/history.html",
 "nicotine1988":"https://stacks.cdc.gov/view/cdc/22014",
 "WHO2026":"https://www.who.int/ru/news-room/fact-sheets/detail/tobacco/",
 "neurobiology":"https://www.ncbi.nlm.nih.gov/books/NBK53018/"
}
def run_cmd(*args):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=300)
    if p.returncode:raise RuntimeError("FFmpeg/ffprobe failed: "+p.stderr[-1000:])
    return p.stdout

def textdata():
    chapters=[]
    for idx in range(1,8):
        path=HERE/"script"/f"{idx:02}.json"
        c=json.loads(path.read_text(encoding="utf-8"))
        if c.get("chapter")!=idx or not c.get("sources") or len(c.get("lines",[]))<7:
            raise ValueError("Missing chapter, paragraphs, or citations: "+str(path))
        chapters.append(c)
    paragraphs=[(ch,txt) for ch in chapters for txt in ch["lines"]]
    words=sum(len(txt.split()) for _,txt in paragraphs)
    print(f"MANUSCRIPT {len(paragraphs)} substantive paragraphs; {words} spoken words; {len(chapters)} chapters",flush=True)
    if words<3000 or words>5500:raise ValueError("Incomplete or unnaturally lengthy manuscript")
    return chapters,paragraphs,words

def azure_speak(text,dest):
    """Authorized Azure Speech resource; identical voice ID, never a substitute."""
    key=os.environ.get("AZURE_SPEECH_KEY","")
    region=os.environ.get("AZURE_SPEECH_REGION","")
    if not key or not re.fullmatch(r"[a-z0-9]{3,25}",region):
        raise ValueError("Azure TTS requires key and valid region")
    xml=("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
         "xml:lang='ru-RU'><voice name='ru-RU-DmitryNeural'>"
         "<prosody rate='-7%'>"+html.escape(text)+"</prosody></voice></speak>")
    headers={"Ocp-Apim-Subscription-Key":key,"Content-Type":"application/ssml+xml",
             "X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3",
             "User-Agent":"M1lash54DocumentaryTTS/1.0"}
    url="https://"+region+".tts.speech.microsoft.com/cognitiveservices/v1"
    req=urllib.request.Request(url,data=xml.encode("utf-8"),headers=headers,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=75) as response:
            data=response.read(12_000_000)
    except urllib.error.HTTPError as error:
        raise RuntimeError("Azure Speech HTTP "+str(error.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("Azure Speech connectivity failure") from None
    if len(data)<500 or data[:3]!=b"ID3" and data[:2]!=bytes([255,251]) and data[:2]!=bytes([255,243]):
        # MP3 often starts with ID3 or MPEG frame sync; ffprobe will verify later.
        if len(data)<500:raise RuntimeError("Azure returned empty speech")
    dest.write_bytes(data)

async def make_audio(text,dest):
    # Same exact ru-RU-DmitryNeural ID with either official Azure account or Edge.
    # Azure is preferred if credentials are configured; never use any other voice.
    error=None
    azure_available=bool(os.environ.get("AZURE_SPEECH_KEY") and os.environ.get("AZURE_SPEECH_REGION"))
    for attempt in range(3):
        try:
            if azure_available:
                await asyncio.to_thread(azure_speak,text,dest)
            else:
                await edge_tts.Communicate(text,voice=VOICE,rate="-7%").save(str(dest))
            if dest.stat().st_size<500:raise RuntimeError("Speech empty")
            return
        except Exception as ex:
            error=ex
            try:dest.unlink(missing_ok=True)
            except OSError:pass
            print(f"TTS TRY {attempt+1}/3 FAILED: {type(ex).__name__}",flush=True)
            await asyncio.sleep(2*(attempt+1))
    raise RuntimeError(("Authorized Azure" if azure_available else "Edge")+
                       " Dmitry neural did not return spoken audio: "+type(error).__name__)

def tc(t):
    m=round(t*1000)
    return f"{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}"

async def build(out,only_audio=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    chapters,paragraphs,words=textdata()
    # Always preserve the full original screenplay and citations, even when TTS fails.
    (out/"script_full.txt").write_text("\n\n".join(ch["title"]+"\n\n"+"\n\n".join(ch["lines"]) for ch in chapters),encoding="utf-8")
    (out/"sources.json").write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"voice_status.json").write_text(json.dumps({"voice":VOICE,"state":"SYNTHESIS_REQUESTED_NOT_CONFIRMED","substitutes_allowed":False},indent=2),encoding="utf-8")
    audio_folder=out/"audio-parts";audio_folder.mkdir(exist_ok=True)
    cues=[];subtitles=[];offset=0
    combined=out/"narration.wav"
    with wave.open(str(combined),"wb") as wav:
        wav.setparams((1,2,24000,0,"NONE","not compressed"))
        for i,(chapter,txt) in enumerate(paragraphs):
            file=audio_folder/f"part-{i:03}.mp3"
            if not file.exists():await make_audio(txt,file)
            norm=audio_folder/f"part-{i:03}.wav"
            if not norm.exists():
                run_cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-i",file,
                        "-ac","1","-ar","24000","-af","apad=pad_dur=0.14",norm)
            with wave.open(str(norm),"rb") as segment:
                if segment.getnchannels()!=1 or segment.getframerate()!=24000:
                    raise ValueError("Invalid audio sample format")
                duration=segment.getnframes()/segment.getframerate()
                if not 2<=duration<=120:raise ValueError("Invalid spoken paragraph length "+str(duration))
                wav.writeframes(segment.readframes(segment.getnframes()))
            cue={"chapter":chapter["chapter"],"title":chapter["title"],
                 "visual":chapter["visual"],"duration":round(duration,5),
                 "words":len(txt.split()),"start_s":round(offset,3),"end_s":round(offset+duration,3)}
            cues.append(cue)
            # SRT time divisions are approximate, content faithfully matches spoken text.
            wd=txt.split()
            blocks=max(1,math.ceil(len(wd)/13))
            for k in range(blocks):
                start=offset+duration*k/blocks;end=offset+duration*(k+1)/blocks
                subtitles.append(f"{len(subtitles)+1}\n{tc(start)} --> {tc(end)}\n"
                                 +" ".join(wd[k*13:(k+1)*13])+"\n")
            offset+=duration
            print(f"TTS {i+1}/{len(paragraphs)}; total {offset:.1f}s",flush=True)
    manifest={"issue":54,"voice":VOICE,"voice_rate":"-7%","duration_s":round(offset,3),
              "words":words,"source_urls":list(SOURCES.values()),"cues":cues,
              "status":"VOICE_COMPLETE_RENDER_PENDING"}
    (out/"cues.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"subtitles.srt").write_text("\n".join(subtitles),encoding="utf-8")
    (out/"script_full.txt").write_text("\n\n".join(
         ch["title"]+"\n\n"+"\n\n".join(ch["lines"]) for ch in chapters),encoding="utf-8")
    (out/"sources.json").write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2),encoding="utf-8")
    if offset<MIN_DURATION:
        manifest["status"]="BLOCKED_UNDER_21_MINUTES"
        (out/"cues.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
        raise RuntimeError(f"Real narration only {offset:.1f} seconds, do not add silence to pad 21 minutes")
    if only_audio:return None
    video=out/"M1lash_Tobacco_54_25min_Dima.mp4"
    render(cues,video,combined,fps=10)
    probe=json.loads(run_cmd("ffprobe","-v","error","-show_entries",
       "format=duration:stream=codec_type,width,height,duration",
       "-of","json",video))
    duration=float(probe["format"]["duration"])
    v=next((s for s in probe["streams"] if s["codec_type"]=="video"),None)
    a=next((s for s in probe["streams"] if s["codec_type"]=="audio"),None)
    status={"technical_pass":bool(duration>=1260 and v and a and v["width"]>=1920 and v["height"]>=1080
                             and abs(duration-offset)<=2.5),
            "duration_s":duration,"narration_duration_s":offset,
            "video_stream":v,"audio_stream":a,
            "visual_quality_review":"PENDING_HUMAN_WATCH",
            "rights":"Original generated vectors; original Russian manuscript; no external photo/music",
            "publish":False,
            "voice":VOICE,
            "limitations":"Programmatic vector illustration, NOT professional historical documentary photography. "
                          "SRT segmentation approximate. Human audiovisual review still required."}
    (out/"film54_qa.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not status["technical_pass"]:raise RuntimeError("Film54 fails 21min / HD / audio technical gate")
    print("FILM READY FOR HUMAN VISUAL AUDIT:",video,str(round(duration,1))+"s",flush=True)
    return video

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="film54-output")
    ap.add_argument("--audio-only",action="store_true")
    args=ap.parse_args()
    asyncio.run(build(args.out,args.audio_only))
if __name__=="__main__":main()
