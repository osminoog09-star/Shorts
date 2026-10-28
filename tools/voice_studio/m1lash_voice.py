#!/usr/bin/env python3
"""M1lash Voice Studio: ORIGINAL voice design -> persistent reference -> narrated WAV.

No model weights, external code, credentials or real-person voice samples are fetched by
this CLI. Explicitly place vetted official Qwen model snapshots on your own PC first.
This is an experimental ORIGINAL voice workflow, not an approved Dima/Sveta replacement.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name("voices.json")
MODELS = {
    "design": "Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "narrate": "Qwen3-TTS-12Hz-0.6B-Base",
}
ID = re.compile(r"[a-z][a-z0-9-]{1,31}\Z")
SENTENCES = re.compile(r"(?<=[.!?…])\s+")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_voices(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    voices = data["voices"]
    if not voices or len({v["id"] for v in voices}) != len(voices):
        raise ValueError("empty or duplicate voice IDs")
    for v in voices:
        if not ID.fullmatch(v["id"]) or v["language"] not in ("Russian", "English"):
            raise ValueError("invalid original voice profile")
        if len(v["reference_text"]) < 80 or len(v["design_instruct"]) < 60:
            raise ValueError("reference text or persona description too short")
    return {v["id"]: v for v in voices}


def segments(text, limit=240):
    """Sentence-aware reproducible segments; never truncate 21-minute scripts."""
    if not isinstance(text, str) or not text.strip() or len(text) > 80000:
        raise ValueError("text must have 1..80000 characters")
    if not 80 <= limit <= 500:
        raise ValueError("segment size must be 80..500 characters")
    norm = " ".join(text.split())
    sentences = SENTENCES.split(norm)
    output = []
    for sentence in sentences:
        pieces = []
        words = sentence.split()
        current = ""
        for word in words:
            if len(word) > limit:
                raise ValueError("unbroken word longer than segment maximum")
            trial = (current + " " + word).strip()
            if len(trial) > limit and current:
                pieces.append(current)
                current = word
            else:
                current = trial
        if current:
            pieces.append(current)
        for piece in pieces:
            if output and len(output[-1]) + 1 + len(piece) <= limit:
                output[-1] += " " + piece
            else:
                output.append(piece)
    if " ".join(output) != norm:
        raise ValueError("segmenter lost speech text")
    return output


def check_model(path, kind):
    path = Path(path).expanduser().resolve()
    if kind not in MODELS or not path.is_dir() or path.name != MODELS[kind]:
        raise ValueError("provide an existing verified local directory named " + MODELS[kind])
    if not (path / "config.json").is_file():
        raise ValueError("local model config.json absent")
    return path


def ref_manifest(directory, profile):
    directory = Path(directory)
    file = directory / "reference.wav"
    manifest = directory / "reference.json"
    if not file.is_file() or not manifest.is_file():
        raise ValueError("generate the original voice reference first")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (data.get("profile_id") != profile["id"]
        or data.get("provenance") != "original_qwen_voice_design"
        or data.get("reference_text") != profile["reference_text"]
        or data.get("audio_sha256") != sha256(file)):
        raise ValueError("voice reference manifest/provenance/hash mismatch")
    return file, data


def load_qwen(local_path, cpu=False):
    """Only optional local heavyweight dependencies; never download in tests."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    try:
        import torch
        from qwen_tts import Qwen3TTSModel
    except ImportError as exc:
        raise RuntimeError("Install vetted torch / qwen-tts / soundfile in an isolated environment") from exc
    if not cpu and not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU not available; --cpu is experimental and may be very slow")
    device = "cpu" if cpu else "cuda:0"
    dtype = torch.float32 if cpu else torch.bfloat16
    # 'sdpa' avoids compiling unreviewed FlashAttention extensions.
    return Qwen3TTSModel.from_pretrained(str(local_path), device_map=device,
                                         dtype=dtype, attn_implementation="sdpa")


def save_wav(out, waveforms, sr):
    import soundfile as sf
    if not waveforms or not isinstance(sr, int) or sr < 16000 or sr > 96000:
        raise ValueError("model returned no valid audio")
    values = waveforms[0]
    if len(values) < sr:  # < 1 second generally means empty/defective inference
        raise ValueError("model returned <1s of audio")
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("NaN/Inf audio output")
    sf.write(str(out), values, sr, subtype="PCM_16")
    return {
        "audio_sha256": sha256(out),
        "sample_rate": sr,
        "duration_s": round(len(values) / sr, 3),
        "bytes": out.stat().st_size,
    }


def create_reference(profile, out_dir, model, cpu=False, *, infer=None, save=None):
    """Create a brand-new fictional voice reference, never cloning third-party speech."""
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError("refuse to overwrite existing voice reference/approval history")
    out_dir.mkdir(parents=True, exist_ok=True)
    infer = infer or load_qwen
    save = save or save_wav
    try:
        wavs, sr = infer(model, cpu).generate_voice_design(
            text=profile["reference_text"], language=profile["language"],
            instruct=profile["design_instruct"])
        output = out_dir / "reference.wav"
        audit = save(output, wavs, sr)
        result = {
            "schema": 1,
            "status": "EXPERIMENTAL_NEEDS_LISTENING",
            "approved_for_channel": False,
            "profile_id": profile["id"],
            "language": profile["language"],
            "provenance": "original_qwen_voice_design",
            "model": MODELS["design"],
            "reference_text": profile["reference_text"],
            "design_instruct": profile["design_instruct"],
            **audit,
        }
        (out_dir / "reference.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    except Exception:
        # A partial output is never a valid reference; leave evidence for diagnostics.
        raise


def synthesize(profile, reference_dir, text, out_dir, model, cpu=False, *, infer=None, save=None):
    """Voice-clone OUR OWN generated/authorized reference, emit per-line audio + audit."""
    reference, ref_data = ref_manifest(reference_dir, profile)
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError("refuse to overwrite earlier audio manifest")
    parts = segments(text)
    out_dir.mkdir(parents=True, exist_ok=True)
    infer = infer or load_qwen
    save = save or save_wav
    engine = infer(model, cpu)
    prompt = engine.create_voice_clone_prompt(
        ref_audio=str(reference), ref_text=profile["reference_text"],
        x_vector_only_mode=False)
    rows = []
    for i, part in enumerate(parts, 1):
        wavs, sr = engine.generate_voice_clone(
            text=part, language=profile["language"], voice_clone_prompt=prompt)
        filename = f"line_{i:04}.wav"
        audit = save(out_dir / filename, wavs, sr)
        rows.append({"index": i, "file": filename, "text": part, **audit})
    report = {
        "schema": 1,
        "status": "EXPERIMENTAL_NOT_APPROVED_FOR_PUBLICATION",
        "approved_for_channel": False,
        "profile_id": profile["id"],
        "language": profile["language"],
        "model": MODELS["narrate"],
        "source_reference_sha256": ref_data["audio_sha256"],
        "script_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "script_characters": len(text),
        "total_lines": len(rows),
        "estimated_total_audio_s": round(sum(x["duration_s"] for x in rows), 3),
        "lines": rows,
        "disclaimer": "No listening, pronunciation, lip sync, licensing or channel-cast approval implied.",
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="M1lash ORIGINAL Voice Studio / offline")
    parser.add_argument("--catalog", default=str(CATALOG))
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list")
    design = sub.add_parser("design", help="Generate private original voice reference")
    narrate = sub.add_parser("narrate", help="Narrate using our design's saved voice")
    for p in (design, narrate):
        p.add_argument("--voice", required=True)
        p.add_argument("--model-dir", required=True, help="Verified LOCAL official Qwen model snapshot")
        p.add_argument("--out-dir", required=True)
        p.add_argument("--cpu", action="store_true")
        p.add_argument("--dry-run", action="store_true", help="Check inputs without loading AI")
    narrate.add_argument("--ref-dir", required=True)
    narrate.add_argument("--text-file", required=True)
    args = parser.parse_args(argv)
    profiles = read_voices(args.catalog)
    if args.action == "list":
        print(json.dumps([{"id": k, "name": p["name"], "language": p["language"]}
                          for k, p in profiles.items()], ensure_ascii=False, indent=2))
        return
    try:
        profile = profiles[args.voice]
        model = check_model(args.model_dir, args.action)
        if args.action == "design":
            if args.dry_run:
                result = {"mode": "design", "voice": args.voice, "model": str(model),
                          "planned_reference_text": profile["reference_text"],
                          "status": "DRY_RUN_NO_AUDIO"}
            else:
                result = create_reference(profile, args.out_dir, model, args.cpu)
        else:
            text = Path(args.text_file).read_text(encoding="utf-8")
            ref_manifest(args.ref_dir, profile)
            parts = segments(text)
            if args.dry_run:
                result = {"mode": "narrate", "voice": args.voice, "model": str(model),
                          "planned_lines": parts, "status": "DRY_RUN_NO_AUDIO"}
            else:
                result = synthesize(profile, args.ref_dir, text, args.out_dir, model, args.cpu)
    except (KeyError, ValueError, OSError, RuntimeError) as exc:
        raise SystemExit(f"VOICE NO-GO: {exc}") from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
