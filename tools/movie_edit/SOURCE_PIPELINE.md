# Movie-edit source pipeline (draft)

Workflow: `.github/workflows/movie-edit-source.yml`.

## What it does

- On a push to `codex/movie-edit-download-pipeline-20261027`, checks the FFmpeg concat manifest with two locally generated test videos.
- On manual `workflow_dispatch`, accepts 1–8 HTTPS video URLs that the channel is authorized to reuse, downloads them using `yt-dlp`, takes the first eight seconds from each, center-crops to 1080×1920, and exports an MP4 artifact named `movie-edit-draft`.
- The output is **silent source footage**, not a finished M1lash Short. It does not add voice, subtitles, music, narrator or branded outro and does not publish anything.

## How to test

1. Review the GitHub Actions smoke-test status on the branch.
2. After merging the workflow to the default branch, use Actions → Movie edit source-to-short → Run workflow with an authorized video URL (or test on the branch if GitHub exposes it).
3. Download the `movie-edit-draft` artifact from the completed run; check the duration, image framing, clip order, and licensing before continuing.
4. Use the existing `tools/movie_edit` pipeline for word-timed captions and the `studio/src/EditOutro.tsx` presenter, after creating a new edit plan for the actual footage.

## Limitations

- `yt-dlp` cannot download DRM-protected or login-restricted videos without access. It does not confer reuse rights.
- Film and TV clips generally require a rights review, including for commentary/parody. Do not attempt Content ID evasion.
- Input URLs are workflow inputs visible to repository collaborators; never put credentials or private signed URLs there.
- GitHub workflow runs and successful external downloads have **not** been verified yet.
