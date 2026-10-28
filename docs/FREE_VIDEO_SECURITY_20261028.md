# Free tools for M1lash: acquisition and threat review (2026-10-28)

Security gate: trusted origin -> exact version -> read license -> download into temporary isolated runner -> inspect wheel archive -> query advisories -> install into a throwaway virtualenv -> smoke test. No post-install script from a random website; no tokens/secrets in staging job. Passing a ZIP inspection is NOT proof of zero malware; dependency and media-decoder vulnerabilities still require updates. Do not process secret source footage in untrusted online converters.

## Candidate list and decision
- PySceneDetect headless 0.7.2 (BSD-3-Clause): ACCEPT FOR ISOLATED STAGING. Scene cuts, duplicate-shot audits, scene boundary CSV. Official: https://www.scenedetect.com/download/ ; https://github.com/Breakthrough/PySceneDetect. The staging workflow downloads and scans pinned wheels then installs in an ephemeral environment; no executable/vendor binary checked into Git.
- Blender 5.2 LTS (GPL): APPROVED SOURCE FOR MANUAL EVALUATION, NOT INSTALLED HERE. Local rendering, rigs, anatomy and camera. Obtain ONLY from https://www.blender.org/releases/ after checking official checksum/signature and host OS. Never load third-party .blend with auto-execute Python enabled.
- whisper.cpp 1.9.5 (MIT): CANDIDATE. On-device/local transcription and subtitle timing; download official releases, verify release checksums and test on dummy audio before production. https://github.com/ggml-org/whisper.cpp/releases. Its generated timestamps must be reviewed against the final Dmitry track.
- Rhubarb Lip Sync (MIT): CANDIDATE. Generates mouth shape timings; does not replace Dima voice, check actual viseme mapping. https://github.com/DanielSWolf/rhubarb-lip-sync .
- Shotcut 26.9 (GPLv3): OPTIONAL MANUAL DESKTOP EDITOR, NOT FOR CI. https://shotcut.com/ ; do not mirror unknown repackaged installers.
- Existing FFmpeg, Remotion and Python drawing tools remain the first-line code render pipeline.

## Known risks and non-claims
- Many pre-existing workflows reference mutable @v4/@v5 action tags rather than immutable 40-character commit SHAs. Review and pin after verifying upstream owner and SHA; do not bulk replace with guessed hashes.
- A public repository does not make external copyrighted movie footage redistributable. Check rights case-by-case before publication.
- The older videos and audio stems may have Liam or other voices. They are NOT verified Dima just because their file name says approved.
- Wheel staging does not install Blender, whisper.cpp, Rhubarb or Shotcut. They remain candidate options, not executable assets in this repo.
- Staging runs under permissions contents: read; no OAuth credentials passed. App code is not automatically published from this job.
- Protect against malicious media with up-to-date decoder packages; do not run unidentified installers or arbitrary pasted scripts.
- Run: python tools/security/workflow_audit.py; inspect reports; separately review GitHub Advisory Database / OSV for dependencies. An empty finding is not a safety guarantee.

## Safe local QA commands
python tools/m1lash_qa/preflight.py file.mp4 --profile short --strict
python tools/free_video/scene_report.py file.mp4 --output work/scene_audit
python scripts/m1lash_calendar_audit.py --input reports/videos.csv

## Production blockers still open
1. New Dima outro needs actual recording, synchronized lips and human listening approval plus hash attestation; no fake approval.
2. Character design and true motion remain below 8/10 in prior audited pilot; change the model/rig, not just line art.
3. Metricool/YouTube slots and analytics require live connected source verification; local CSV only lists previously recorded claims.

Staging run 40627450664: passed (GitHub Actions, 28 October 2026). PySceneDetect 0.7.2 and dependencies downloaded; ZIP checks and pip-audit reported no known vulnerabilities at that moment, isolated install and version smoke test passed. This does NOT certify that all possible threats are absent. A future run archives the inspected wheel files along with SHA256 manifest for owner download; no wheel is committed to Git.
