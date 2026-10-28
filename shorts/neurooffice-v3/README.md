# M1lash — Нейроофис V3 (clean frame, authored code animation)

Owner feedback after V2 (5/10): remove style and technical labels in the top-left, and make modest polish without changing the approved graphic direction.

## Changes
- Removed M1LASH/NEURO top-left, episode test tag top-right, and all bottom technical captions.
- Kept actual story-related panels and dialogue subtitles.
- More natural moving pupils and brows; slightly floating idle animations and more responsive hands.
- The robot gains an animated speech equalizer and additional animated lights and highlights.
- Original Dmitry voice is extracted from V2 MP4 and preserved through `-c:a copy` without new speech generation.
- 51.79s, 24fps, 1080x1920 H.264/AAC; no uploading to YouTube, Metricool or other platforms.

### Build
```bash
sudo apt-get install -y ffmpeg fonts-dejavu-core
python -m pip install pillow numpy
ffmpeg -i videos/M1lash_Neurooffice_V2_RU.mp4 -map 0:a:0 -c:a copy shorts/neurooffice-v3/voice_dima.m4a
python shorts/neurooffice-v3/render_v3.py --render
```

The GitHub Actions workflow `neurooffice-v3-direct.yml` generates and commits `videos/M1lash_Neurooffice_V3_CLEAN_RU.mp4` as a directly downloadable file **only in this demo branch**. Artistic review before publishing is still required.
