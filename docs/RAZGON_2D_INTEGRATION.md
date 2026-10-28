# M1lash × Razgon 2D Studio — experimental adapter (28.10.2026)

**Status: optional production tool, NOT an automatic video publisher.** It does not replace
Remotion, Motion Studio 2.0, approved M1lash character rigs, or the existing QA workflows.

## Why this is separate

Razgon is a complete **code-rendered stick-figure engine** (Canvas, Three.js, Playwright,
FFmpeg), not a provider of talking photorealistic presenters. Its bundled character design
does **not** automatically meet M1lash's MODEL / CONTACT / ACTING / art-direction gates.
Use it for original 2D/2.5D diagrams, experiments and approved shot types. Visual QC is
required before any final film. No promise of 8/10 quality from installing software.

## Source / audit

Input: user-provided `razgon-2d-studio.plugin.zip` (plugin metadata version `0.3.0`).
Audited sample SHA256:
`3376259460a0d6efb11dd808d5cb9e4b0fcdfdd5503e6e5ef6eb4991f48e2812`.
All 30 vendor-file hashes passed vendor's `verify_kit.py`; Python `compileall` and
Node `--check` passed locally. Local 9:16 project creation and WAV duration passed.
**Full animation render was NOT verified** in the audit environment: missing npm
packages and Playwright Chromium; package installation timed out. The example has
no bundled narration recording. Runtime quality/accuracy unproven.

The code in `tools/razgon2d/bridge.py` is an integration adapter; the vendor kit is
**not checked into the repository**. Bring a copy of the original ZIP to the PC or
build runner. Do not fetch unverified third-party mirrors or put the owner's voice
files into a public repository.

## Local workflow (Python 3.10+, Node 18+, ffmpeg)

```bash
python tools/razgon2d/bridge.py install --zip /path/to/razgon-2d-studio.plugin.zip
cd tools/razgon2d/kit
npm install
npx playwright install chromium
python tools/doctor.py
```

`faster-whisper` is needed only if transcribing speech rather than using a
time-coded script. Use the existing M1lash TTS step to synthesize **Dima**
(`ru-RU-DmitryNeural`) and optional **Sveta**
(`ru-RU-SvetlanaNeural`). Keep their audio files and manifests outside public Git.
No Liam/Piper/eSpeak fallback. Vendor creates **no** valid Dima audio on its own.

```bash
# Run these commands from tools/razgon2d/kit:
python tools/new_project.py --name m1lash-test --voice /secure/path/dima.wav --aspect 9:16 --resolution 1080p --title "Private pilot" --captions
# Create and review projects/m1lash-test/story/shots.json and scene JS files.
# Save a verified voice manifest at projects/m1lash-test/input/voice_manifest.json

# Then run from the repository root:
python tools/razgon2d/bridge.py render --project tools/razgon2d/kit/projects/m1lash-test --sheet
python tools/razgon2d/bridge.py render --project tools/razgon2d/kit/projects/m1lash-test --from-sec 0 --to-sec 10
# For a full render, omit --from-sec and --to-sec.
```

Voice manifest example, located in `input/voice_manifest.json` with segment
files referenced relative to that folder:

```json
{
  "segments": [
    {
      "speaker": "dima",
      "voice_id": "ru-RU-DmitryNeural",
      "engine": "edge-tts",
      "rate": "+0%",
      "source_file": "dima_segment_01.wav"
    }
  ]
}
```

Important: this manifest is a provenance **claim**, not a voice biometric check;
audio sources and actual voice identity must still be verified. The main narration
file in config.json must exist. The shot timeline must be contiguous.

After the silent render, run the upstream `audio/mix.py` in the kit project to
produce the final mixed MP4. Then validate:

```bash
python tools/razgon2d/bridge.py qa \
  --project tools/razgon2d/kit/projects/m1lash-test \
  --video tools/razgon2d/kit/projects/m1lash-test/out/Private_pilot.mp4 \
  --kind pilot
```

For a true long-form release, choose `--kind long`; this checks MP4 duration
>= 1260 s along with audio/video streams, but **does NOT replace**
`python scripts/qa/longform_duration_gate.py FILM.mp4`, voice-cast QA,
rights audit, lip-sync QA, camera/art review, nor human release approval.
Drafts and pilots must never be represented as completed long videos.

## Integration limitations / next steps

- The adapter can safely unpack the locally supplied ZIP and run a pilot. To run
  on GitHub Actions, the vendor kit must first be made available to the authorized
  runner through a reviewed source/artifact. The PR does not fake online rendering.
- No YouTube upload, scheduling, Metricool, or automatic mutation of jobs/queues.
- The bundle does not provide ready-made M1lash characters or verified lip-sync.
- Before production: check multi-shot render and sound mix; compare 5 style sheets;
  upgrade approved character models; run MODEL, CONTACT, ACTING, AUDIO gates.
- This tool is **opt-in**. Existing M1lash workflows remain unchanged.
