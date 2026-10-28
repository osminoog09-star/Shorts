# M1lash · Нейроофис V5

**Code animation only** · owner-reviewed improvement of V4 (human, robot, windows, schedule, subtitles).

- `render_v3.py`: prior scene choreography, base 2D routines and cut timings.
- `render_v4.py`: original Dmitry word timestamps and legible phrase captions.
- `render_v5.py`: fully redrawn articulated actors, robot and office; schedule UI rewrite; full render+audio checks.
- `AUDIT_V5.md`: cause-by-cause audit with defects and corrections.
- Video output: `videos/M1LASH_NEUROOFFICE_V5_RU.mp4`, produced automatically by GitHub Actions in **this branch only**.

Run manually with a local copy of the original Dmitry voice in this directory as `voice_dima.m4a`:

```bash
python -m pip install pillow numpy
python render_v5.py --preview
python render_v5.py --render
```

The rendering workflow restores the approved Dmitry audio losslessly from the previous owner-approved V2 MP4; it checks the full MP4 decode and commits the downloadable video. It never publishes to YouTube or Metricool. Artistic evaluation remains separate from technical QA.
