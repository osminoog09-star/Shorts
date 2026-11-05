#!/usr/bin/env python3
"""Offline Qwen3-TTS 1.7B Base ICL for the owner's private Denis voice.

No TTS provider fallback. References NEVER leave runner.temp. Output is WAV +
manifest, with a separate faster-whisper ASR check and owner hearing pending.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import gc
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata

NAME = re.compile(r"[a-z][a-z0-9_]{1,48}\Z")
JOB_NAME = re.compile(r"[a-z][a-z0-9_]{2,48}\Z")
EXPECTED_VOICE = "denis-qwen3tts-reference-v1"


class VoiceError(RuntimeError):
    pass


def job_config(job_path: Path) -> tuple[str, list[dict]]:
    if not job_path.as_posix().endswith(".json"):
        raise VoiceError("NO-GO: ожидается jobs/voice/<id>.json")
    try:
        obj = json.loads(job_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise VoiceError("NO-GO: jobs/voice JSON отсутствует/испорчен") from exc
    job_id = obj.get("job_id")
    if not isinstance(job_id, str) or not JOB_NAME.fullmatch(job_id):
        raise VoiceError("NO-GO: некорректный ID голосового задания")
    if obj.get("voice_id") != EXPECTED_VOICE or obj.get("speaker") != "denis":
        raise VoiceError("NO-GO: только подтверждённый голос Дениса, другой запрещён")
    lines = obj.get("utterances")
    if not isinstance(lines, list) or not 1 <= len(lines) <= 8:
        raise VoiceError("NO-GO: от одной до восьми коротких реплик за workflow")
    ids = set()
    for u in lines:
        if not isinstance(u, dict):
            raise VoiceError("NO-GO: каждая реплика должна быть объектом")
        name, phrase, rate = u.get("id"), u.get("text"), u.get("rate")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in ids:
            raise VoiceError("NO-GO: повторяющийся или некорректный id реплики")
        ids.add(name)
        if not isinstance(phrase, str) or not 5 <= len(phrase.strip()) <= 220:
            raise VoiceError("NO-GO: текст реплики должен содержать от 5 до 220 символов")
        if not isinstance(rate, (float, int)) or isinstance(rate, bool) or not 0.85 <= rate <= 1.15:
            raise VoiceError("NO-GO: rate от 0.85 до 1.15, не меняй голос через сильный time-stretch")
    return job_id, lines


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower().replace("ё", "е")
    return " ".join(re.findall(r"[а-яa-z0-9]+", text))


def check_inputs(assets: Path, job: Path, model_dir: Path) -> tuple[str, list[dict], dict]:
    job_id, lines = job_config(job)
    for filename in ("reference_clean.wav", "ref_text.txt", "params.json"):
        if not (assets / filename).is_file():
            raise VoiceError("BLOCKED: нет проверенного private " + filename)
    try:
        ref_text = (assets / "ref_text.txt").read_text(encoding="utf-8").strip()
        params = json.loads((assets / "params.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise VoiceError("NO-GO: private reference text/params не читаются") from exc
    if (not ref_text or len(ref_text) < 20
            or params.get("voice_id") != EXPECTED_VOICE
            or params.get("model_id") != "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
            or params.get("no_fallback") is not True
            or params.get("clone_mode") != "icl"):
        raise VoiceError("NO-GO: private Denis ICL parameters invalid; no fallback")
    if not model_dir.is_dir() or not (model_dir / "config.json").is_file():
        raise VoiceError("BLOCKED: Qwen3-TTS 1.7B Base model weights not downloaded")
    return job_id, lines, params


def encode_rate(src: Path, dst: Path, rate: float) -> None:
    if abs(rate - 1.0) < 0.0001:
        src.replace(dst)
        return
    cmd = ["ffmpeg", "-v", "error", "-xerror", "-y", "-i", str(src),
           "-af", "atempo=" + format(rate, ".4f"), "-ac", "1", "-ar", "24000",
           "-c:a", "pcm_s16le", str(dst)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if p.returncode:
        raise VoiceError("NO-GO: не удалось применить rate без изменения тембра")
    src.unlink(missing_ok=True)


def generate(job: Path, assets: Path, model_dir: Path, output: Path) -> dict:
    job_id, lines, params = check_inputs(assets, job, model_dir)
    for k, v in {"ORT_DISABLE_TELEMETRY": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
                 "TRANSFORMERS_OFFLINE": "1", "DO_NOT_TRACK": "1",
                 "GRADIO_ANALYTICS_ENABLED": "False", "TOKENIZERS_PARALLELISM": "false"}.items():
        os.environ[k] = v
    import torch
    import numpy as np
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    started = time.monotonic()
    try:
        model = Qwen3TTSModel.from_pretrained(
            str(model_dir), device_map="cpu", dtype=torch.bfloat16,
            attn_implementation="eager", local_files_only=True
        )
    except Exception as exc:
        raise VoiceError("BLOCKED: Qwen3-TTS 1.7B Base failed to load; check CPU RAM/weights/torch") from exc
    ref_text = (assets / "ref_text.txt").read_text(encoding="utf-8").strip()
    try:
        prompt = model.create_voice_clone_prompt(
            ref_audio=str(assets / "reference_clean.wav"),
            ref_text=ref_text, x_vector_only_mode=False
        )
    except Exception as exc:
        raise VoiceError("BLOCKED: Qwen3-TTS ICL failed to encode private Denis reference") from exc
    print("QWEN_MODEL_READY seconds=", round(time.monotonic() - started, 1), flush=True)
    out_audio = output / "audio"
    out_audio.mkdir(parents=True, exist_ok=True)
    utterances = []
    for i, u in enumerate(lines):
        print("SYNTHESIZE", u["id"], "length_chars", len(u["text"]), flush=True)
        torch.manual_seed(733 + i)
        args = params.get("inference", {})
        try:
            audio, sample_rate = model.generate_voice_clone(
                text=u["text"], language="Russian", voice_clone_prompt=prompt,
                max_new_tokens=int(args.get("max_new_tokens", 400)),
                temperature=float(args.get("temperature", 0.55)),
                top_p=float(args.get("top_p", 0.85)),
                repetition_penalty=float(args.get("repetition_penalty", 1.05))
            )
            arr = np.asarray(audio[0], dtype=np.float32)
        except Exception as exc:
            raise VoiceError("NO-GO: Qwen3-TTS failed to generate id=" + u["id"]) from exc
        if arr.ndim != 1 or not np.isfinite(arr).all() or len(arr) < sample_rate // 2:
            raise VoiceError("NO-GO: Qwen3-TTS returned empty/nonfinite audio " + u["id"])
        temp = out_audio / (u["id"] + ".unrate.wav")
        wav = out_audio / (u["id"] + ".wav")
        sf.write(str(temp), arr, sample_rate, subtype="PCM_16")
        encode_rate(temp, wav, float(u["rate"]))
        if not wav.is_file() or wav.stat().st_size < 16000:
            raise VoiceError("NO-GO: WAV output incomplete " + u["id"])
        utterances.append({
            "id": u["id"], "text": u["text"], "rate": u["rate"],
            "speaker": "denis", "voice_id": EXPECTED_VOICE, "engine": "qwen3-tts-local",
            "source_file": "audio/" + u["id"] + ".wav",
            "sha256": hashlib.sha256(wav.read_bytes()).hexdigest(),
            "sample_rate": 24000, "asr_text": None, "asr_similarity": None,
            "owner_hearing": "pending",
        })
        print("WAV_GENERATED", u["id"], wav.stat().st_size, "bytes", flush=True)
    del model, prompt
    gc.collect()
    # Do not load Whisper while 1.7B Qwen weights occupy runner RAM.
    try:
        from faster_whisper import WhisperModel
        # GitHub Actions pre-downloads the PUBLIC CTranslate2 model before Qwen
        # inference. Loading that exact local snapshot avoids network/timeouts
        # after a lengthy CPU synthesis run. This is ASR verification, NOT a
        # voice engine fallback or a private sample download.
        whisper_local = os.environ.get("WHISPER_LOCAL_PATH", "").strip()
        if whisper_local:
            if not (Path(whisper_local) / "model.bin").is_file():
                raise VoiceError("BLOCKED: cached faster-whisper model.bin is missing")
            whisper = WhisperModel(whisper_local, device="cpu", compute_type="int8",
                                   cpu_threads=2, num_workers=1, local_files_only=True)
        else:
            whisper = WhisperModel("small", device="cpu", compute_type="int8",
                                   cpu_threads=2, num_workers=1, download_root=os.path.join(
                                       os.environ.get("HF_HOME", "/tmp"), "whisper"))
    except VoiceError:
        raise
    except Exception as exc:
        raise VoiceError("BLOCKED: faster-whisper small model unavailable (" +
                         type(exc).__name__ + "); pre-download the PUBLIC CTranslate2 snapshot") from exc
    for item in utterances:
        wav = output / item["source_file"]
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1",
                            "-ar", "16000", "-f", "f32le", "-"], capture_output=True)
        if p.returncode:
            raise VoiceError("NO-GO: unable to decode WAV for ASR")
        data = np.frombuffer(p.stdout, dtype=np.float32)
        try:
            segs, _ = whisper.transcribe(data, language="ru", beam_size=4,
                                         vad_filter=False, condition_on_previous_text=False)
            recognized = " ".join(s.text.strip() for s in segs).strip()
        except Exception as exc:
            raise VoiceError("NO-GO: ASR inference failed: " + item["id"]) from exc
        expected = norm(item["text"])
        got = norm(recognized)
        score = SequenceMatcher(None, expected, got).ratio()
        item["asr_text"] = recognized
        item["asr_similarity"] = round(score, 4)
        print("ASR", item["id"], "similarity=", round(score, 4), flush=True)
        if score < 0.80 or len(got) < max(5, int(len(expected) * 0.55)):
            report = {"job_id": job_id, "failed_id": item["id"], "expected": item["text"],
                      "asr_text": recognized, "similarity": score}
            (output / "asr_failure.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            raise VoiceError("NO-GO: ASR does not match Denis speech id=" + item["id"])
    manifest = {
        "job_id": job_id, "speaker": "denis", "voice_id": EXPECTED_VOICE,
        "engine": "qwen3-tts-local", "model": "Qwen3-TTS-12Hz-1.7B-Base",
        "reference": "owner-private Drive SHA256-verified; not included in artifact",
        "utterances": utterances, "owner_hearing": "pending", "publication": "forbidden",
        "generation_seconds": round(time.monotonic() - started, 1)
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("TTS_ASR_PASS", job_id, len(utterances), "owner_hearing=pending", flush=True)
    return manifest


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--assets", type=Path, required=True)
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        generate(args.job, args.assets, args.model_dir, args.output)
    except VoiceError as exc:
        print("::error::" + str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print("::error::NO-GO: unexpected local Qwen/ASR runtime failure " + type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
