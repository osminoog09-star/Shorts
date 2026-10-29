# M1lash original video style/prompt laboratory

## Official vs experimental
Official style experiment is S1-S9 and depths D2/D25/D3 in skills/vizavi-motion/references/style-library.md. Do not modify those names, prompts or measured results in this laboratory. This independent catalog introduces experimental X01-X12 visual-direction presets based on original descriptions, to evaluate later with owner permission. An X preset is NOT an approved channel replacement. It never authorizes copying a living artist, studio characters, protected logos or real news screenshots.

## Styles X01-X12
- X01 cinematic documentary macro: ancient technology, mechanical demonstrations, 3D.
- X02 robot engineering cross-section: joints and sensors.
- X03 newsroom fact check: source cards, timelines and verified figures.
- X04 blueprint assembly: real geometry with scientific labels.
- X05 museum-historical reconstruction: licensed props, source transparency.
- X06 paper investigation: original collaged research objects.
- X07 scientific space: accurate orbits/scale disclosures.
- X08 AI-agent workflow: each node performs a justified action.
- X09 robot-human sitcom: expressive acting and real contact.
- X10 miniature experiment lab: precise material detail.
- X11 cybersecurity incident: show factual attack path, no invented hacks.
- X12 editorial science explainer: original infographics and experiments.

## Generate full production prompt bundle
For long video (full 23 minutes; min 21:00):
python tools/studio/prompt_compose.py --style X01 --format long --duration 1380 --topic "Как Герон создал паровой шар" --output work/prompt_lab/heron_long.json

For a 44-second short:
python tools/studio/prompt_compose.py --style X09 --format short --duration 44 --topic "Робот случайно увольняет директора" --output work/prompt_lab/sketch_short.json

JSON fields: research_prompt, script_prompt, director_prompt, visual_prompt, voice_prompt, qa_prompt. This is a textual brief, NOT a working render, not an approved claim, not a guarantee of model quality. Script length, pronunciation, source verification, licensed assets and actual voice must be tested separately.

## Quality benchmark
1. Use 1 original story topic, identical text, narrator, duration and copyright-safe references.
2. Evaluate 2 or 3 styles as unlisted test videos, not simultaneously as public uploads.
3. On each: fact QA, original shot diversity, actor anatomy, contact/motion, readability, temporal consistency, voice/mouth synch, technical MP4 and last 30sec.
4. Score each category 0–10. Any <8 -> NO-GO. Count only visibly separate actions, not zoom variants.
5. Use 48h/7d channel metrics only after publication with owner approval, control for topic/format/age. A positive score without real viewing data is an opinion.

## Rights, research and monetization
YouTube rejects mass-produced repetitive inauthentic content without material originality: https://support.google.com/youtube/answer/1311392 . Original storytelling, novel demonstrations and real commentary are mandatory even when a generation engine or template is used. For synthetic-media disclosure follow current official YouTube requirements, and distinguish visualization from misleading real footage.
