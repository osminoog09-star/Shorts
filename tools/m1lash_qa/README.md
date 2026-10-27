# M1lash Media QA

Required local dependencies: `ffmpeg`, `ffprobe` on PATH. Zero cloud/API calls.

```bash
python tools/m1lash_qa/preflight.py videos/sample.mp4 --json-out reports/sample_qa.json --strict
```

The tool checks stream metadata, end-to-end decode, long audio silence at the end and diagnostic freeze/black regions in the last 35 seconds. P0 triggers failure in strict mode. P1 indicates quality warnings (e.g. <1080p) but is not a corrupt file.

**Critical:** this is technical preflight, not aesthetic approval. Humans or vision-capable reviewers must inspect a shotlist, listen to dialogue/mix, compare each newly created action to the audio, and examine the last 30 seconds. No automated test confirms correct voice identity merely by finding AAC. Voice provenance must be checked against the TTS manifest.

No upload or publish is performed. For reference copyright, use analysis only; never include source video frames in final outputs without rights.
