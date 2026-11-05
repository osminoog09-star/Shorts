#!/usr/bin/env python3
"""Female second voice for M1lash (AGENTS §3а): Qwen3-TTS 1.7B VoiceDesign, fixed
'designed_warm' description + fixed seed (casting round 3, variant 3). Synthetic
voice designed from a text description — no cloning of a real person.

Job file: jobs/voice_female/<id>.json
  {"job_id": "...", "voice_id": "female-qwen3-voicedesign-warm-v1",
   "utterances": [{"id": "...", "text": "...", "instruct_extra": "optional acting note"}]}
Output: <out>/<id>.wav (24 kHz mono) + manifest.json with faster-whisper ASR score.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

VOICE_ID = "female-qwen3-voicedesign-warm-v1"
SEED = 151
BASE_INSTRUCT = (
    "A native Russian-speaking woman in her early thirties, with a warm, velvety, medium-low female voice. "
    "Natural Russian pronunciation and lexical stress, clear consonants. Moderate pace, subtle intonation. "
    "Not breathy, not childish, not a newsreader."
)
NAME = re.compile(r"[a-z][a-z0-9_]{1,48}\Z")


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t).lower().replace("ё", "е")
    return " ".join(re.findall(r"[а-яa-z0-9]+", t))


def load(job: Path):
    o = json.loads(job.read_text(encoding="utf-8"))
    if o.get("voice_id") != VOICE_ID:
        raise SystemExit("NO-GO: voice_id must be " + VOICE_ID)
    if job.stem != o.get("job_id"):
        raise SystemExit("NO-GO: job_id must match file name")
    u = o.get("utterances") or []
    if not 1 <= len(u) <= 12:
        raise SystemExit("NO-GO: 1..12 utterances")
    for x in u:
        if not NAME.fullmatch(x.get("id", "")) or not 3 <= len(x.get("text", "").strip()) <= 220:
            raise SystemExit("NO-GO: bad utterance " + json.dumps(x, ensure_ascii=False))
    return o


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    job = load(Path(a.job))
    out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
    import torch, soundfile as sf
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "2")))
    model = Qwen3TTSModel.from_pretrained(a.model_dir, device_map="cpu", dtype=torch.bfloat16,
                                          attn_implementation="eager", local_files_only=True)
    from faster_whisper import WhisperModel
    wl = os.environ.get("WHISPER_LOCAL_PATH", "")
    whisper = WhisperModel(wl or "small", device="cpu", compute_type="int8")
    rows, bad = [], 0
    for u in job["utterances"]:
        instruct = BASE_INSTRUCT + (" " + u["instruct_extra"] if u.get("instruct_extra") else "")
        best = None
        for attempt in range(3):
            torch.manual_seed(SEED + attempt)
            t0 = time.monotonic()
            w, sr = model.generate_voice_design(text=u["text"], language="Russian", instruct=instruct,
                                                max_new_tokens=int(len(u["text"]) * 2.2 + 60), temperature=0.7)
            f = out / f"{u['id']}.wav"
            sf.write(f, w[0], sr)
            segs, _ = whisper.transcribe(str(f), language="ru", beam_size=4)
            got = norm(" ".join(s.text for s in segs))
            score = SequenceMatcher(None, norm(u["text"]), got).ratio()
            row = {"id": u["id"], "text": u["text"], "asr": got, "asr_score": round(score, 3),
                   "duration": round(len(w[0]) / sr, 3), "seed": SEED + attempt, "attempt": attempt,
                   "speaker": "domashnya", "voice_id": VOICE_ID, "engine": "qwen3-tts-voicedesign-1.7b",
                   "rate": 1.0, "source_file": f.name, "gen_seconds": round(time.monotonic() - t0, 1)}
            print(json.dumps(row, ensure_ascii=False), flush=True)
            if best is None or score > best["asr_score"]:
                best = row
                (out / f"{u['id']}.best.wav").write_bytes(f.read_bytes())
            if score >= 0.85:
                break
        (out / f"{u['id']}.best.wav").replace(out / f"{u['id']}.wav")
        rows.append(best)
        bad += best["asr_score"] < 0.80
    (out / "manifest.json").write_text(json.dumps({"job_id": job["job_id"], "voice_id": VOICE_ID,
        "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", "instruct": BASE_INSTRUCT, "lines": rows},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("ASR fails:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
