# M1lash studio hardening: verified code changes

Current scope: one dedicated integration branch, not a replacement for completed videos or YouTube approval.

Completed in code:
- Original news narrator is fail-closed on ru-RU-DmitryNeural; no Piper fallback. Archived outro requires a newly verified Dima voice asset, human listening approval and exact SHA-256 attestation; otherwise rendering stays NO-GO. The historical published video is not altered.
- Technical MP4 QA respects short 1080x1920 and long 1920x1080 orientation; wrong orientation is P0, undersize P1.
- Offline regression tests for orientation, fallback, calendar conflicts and missing analytics.
- Live schedule is NOT assumed from local CSV. Script flags local collisions and records missing YouTube IDs.
- PySceneDetect 0.7.2 staged with read-only Github Actions and a preliminary ZIP inspection before isolated installation; dependency advisories queried by pip-audit. This is NOT a proof that no vulnerabilities exist.
- Security script inventories risky unpinned GitHub Actions and shell-to-exec patterns as technical debt; reports do not claim every historical PR is safe.
- Analytics distinguishes a measured zero from a missing value. Local coverage script reports absent metrics rather than manufacturing retention.

Commands:
    python -m unittest discover -s tests -p 'test_m1lash_*.py' -v
    python scripts/qa/test_news_voice_policy.py
    python scripts/m1lash_calendar_audit.py --input reports/videos.csv
    python tools/analytics/coverage.py
    python tools/security/workflow_audit.py
    python tools/m1lash_qa/preflight.py video.mp4 --profile short --strict

Open work requiring genuine observation / owner approval:
- Actual audio for a new Dima outro and new per-phoneme lip sync.
- Character artwork and animation at 8/10+ with real scene-by-scene human visual review.
- Verification of scheduled Metricool and YouTube posts before publishing.
- OAuth and authorized channel analytics access for actual view/retention numbers.
- Consolidation of old PRs by reviewing changes. No force-merges, deletions or uploads performed.
- Third-party copyright/asset license review (including NCS track and movie-edit footage).
