# AI News Shorts — 28 October 2026 (RU, manual upload)

Production status: render pipeline in GitHub Actions; DO NOT publish or schedule automatically.
Owner will upload the final MP4 personally. Keep old Metricool/YouTube slots untouched.
Video target: 1080x1920 vertical, 30–65 seconds including the already-approved `videos/m1lash_outro_short_ru.mp4`.
Visual: S1-D25, hand-ink paper motion, subtle parallax, presenter inset, hard hook; ink score original/procedural.
Render: `scripts/render_news_20261028.py`, action `.github/workflows/news-ai-20261028.yml`.
Artifact: `videos/m1lash_ai_news_2026_10_28_ru.mp4` only after QA and Action success.

## Fact checking (2 independent sources each)

### OpenAI (26 Oct)
Claim strictly worded: OpenAI *announced* three scientific results in math, computer science and physics, with independent academic scrutiny still underway. **Do not call confirmed Nobel-quality breakthroughs or assert independent universal validation.**
Primary: https://openai.com/index/building-scientific-understanding-with-academic-communities/
Secondary: https://www.aljazeera.com/economy/2026/10/27/ai-makes-discoveries-in-mathematics-computer-science-physics-openai-says

### NVIDIA × Meta (27 Oct)
NVIDIA to invest $3B in Meta offering and expand collaboration on Muse agents/models.
Reuters: https://www.reuters.com/technology/nvidia-meta-partner-muse-agent-nvidia-invests-3-billion-2026-10-27/
Second: https://www.techzine.eu/news/applications/145303/nvidia-invests-3-billion-in-meta-deepens-muse-partnership/

### Anthropic (26 Oct)
Anthropic disclosed four AI models accessing live external systems during security evaluations; testing environment was accidentally connected to Internet. Company said it found no evidence the models aimed to evade oversight or coordinate. **Do not say a self-aware AI intentionally escaped.**
Reuters: https://www.reuters.com/legal/litigation/anthropic-discloses-month-long-training-pause-ai-security-breaches-ipo-filing-2026-10-26/
Second: https://www.euronews.com/2026/10/26/anthropics-ipo-filing-shows-off-soaring-revenues-as-the-company-warns-of-ais-risks-to-huma

## Voice/script/metadata
Eight original voiced passages and short news humor are embedded in the renderer. Voice: try Edge DmitryNeural; if unavailable, entirely offline Piper ru_RU-dmitri-medium, **not** identical voices. Existing outro has its approved voice/audio and is left unmodified.
Music under news is generated procedurally. The outro retains its existing audio; verify its music license/credit against channel rules when uploading.

Suggested title: ИИ совершил научный прорыв? $3 МЛРД для Meta и опасный сбой!
Tags: #ИИ #Нейросети #OpenAI #NVIDIA #Anthropic #НовостиИИ #Технологии #Shorts #M1lash

## Release gate
Only link direct `raw.githubusercontent.com/.../videos/m1lash_ai_news_2026_10_28_ru.mp4` when the Action has conclusively succeeded and exact file exists in the branch. Verify output via ffprobe, full decode and six frame samples in Action. Never declare publication or schedule in GitHub.
