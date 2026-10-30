#!/usr/bin/env python3
"""Azure Speech backend for M1lash TTS (решение Дениса 30.10.2026).

Тот же голос, что и edge-tts (ru-RU-DmitryNeural / ru-RU-SvetlanaNeural), но через официальный API:
стабильно, SSML (паузы, ударение, интонация), точные тайминги слов и виземы Azure для липсинка.
Секреты: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION (например westeurope).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

ENGINE = "azure-speech"
TICKS = 1e7  # Azure: 100-ns ticks


def available() -> bool:
    return bool(os.environ.get("AZURE_SPEECH_KEY") and os.environ.get("AZURE_SPEECH_REGION"))


def build_ssml(text: str, voice: str, rate: str, pitch: str, ssml: str | None = None) -> str:
    """text — обычный текст (экранируется). ssml — готовая разметка внутри <voice> (паузы <break/>, <emphasis>)."""
    inner = ssml if ssml else escape(text)
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="ru-RU">'
        f'<voice name="{voice}"><prosody rate="{rate}" pitch="{pitch}">{inner}</prosody></voice></speak>'
    )


def synth(text: str, voice: str, rate: str, pitch: str, mp3: Path, meta: Path, speaker: str,
          ssml: str | None = None) -> None:
    import azure.cognitiveservices.speech as speechsdk  # noqa: PLC0415  (ставится только в Actions)

    cfg = speechsdk.SpeechConfig(subscription=os.environ["AZURE_SPEECH_KEY"],
                                 region=os.environ["AZURE_SPEECH_REGION"])
    cfg.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)
    cfg.set_property(speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary, "false")
    synth_ = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)

    words: list[dict] = []
    visemes: list[dict] = []

    def on_word(evt):
        if evt.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word:
            start = evt.audio_offset / TICKS
            words.append({"w": evt.text, "start": round(start, 3),
                          "end": round(start + evt.duration.total_seconds(), 3)})

    def on_viseme(evt):
        visemes.append({"id": evt.viseme_id, "t": round(evt.audio_offset / TICKS, 3)})

    synth_.synthesis_word_boundary.connect(on_word)
    synth_.viseme_received.connect(on_viseme)
    result = synth_.speak_ssml_async(build_ssml(text, voice, rate, pitch, ssml)).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        detail = ""
        if result.reason == speechsdk.ResultReason.Canceled:
            c = result.cancellation_details
            detail = f"{c.reason} {c.error_details}"
        raise RuntimeError(f"NO-GO: Azure did not synthesize {voice}: {result.reason} {detail}")
    data = result.audio_data
    if not data or len(data) < 1024:
        raise RuntimeError(f"NO-GO: Azure returned no usable audio for {voice}")
    mp3.write_bytes(data)
    meta.write_text(json.dumps({
        "text": text, "ssml": ssml, "words": words, "visemes": visemes,
        "voice_id": voice, "speaker": speaker, "engine": ENGINE,
        "rate": rate, "pitch": pitch, "boundary": "WordBoundary",
        "duration": round(result.audio_duration.total_seconds(), 3),
        "source_file": str(mp3)}, ensure_ascii=False, indent=1), encoding="utf-8")
