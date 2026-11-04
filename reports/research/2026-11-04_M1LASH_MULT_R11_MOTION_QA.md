# M1lash Мульт EP01 · r11 actual 7s MP4 audit — 04.11.2026

Source: GitHub Actions `motion-render.yml` run **41797520706 SUCCESS**, artifact **13306166724**. Actual exported MP4: `M1lashMult_ep01_SILENT_7s_pilot.mp4`.

- **Technical gate:** H.264, 1080×1920, 30fps, 210 frames, 7.000000s, **2,267,591 bytes**, SHA256 `516bdef6f129bca97df1aa8d03bc92528daf8d6da3e941c8c8b65dba519854ef`. Physical `ffmpeg -xerror -i ... -f null -` **PASS**.
- **Visual source:** actual MP4 decoded every 0.5s into 14 JPEGs. Actual contact opened/inspected visually at `/mnt/data/m1lash_mult_r11_pilot/qa/contact_14_actual_mp4.jpg`, not substituted from the 6 stills.
- **Stills visual gate before pilot:** run **41797183647 SUCCESS**, artifact **13305993241**. Six real Chrome shots t2.8,3.1,3.5,3.9,4.3,4.5 opened. `badge_gate.json`: all **9/9** projected plaque bounds within safe area; t3.1–3.7 hand projected next to plaque's right edge (3–13px).
- **What improved from r10c:** no abrupt shrinking/clipping of `ДИРЕКТОР` during close-up, no jump between unrelated world-space anchors; MIL visibly reaches the plaque, it moves away from his hand toward AKS. Robot stays visible. Scene cut remains at t7, not t6.5.
- **Limits:** R11 uses a camera-facing Three.js plaque positioned relative to projected hand coordinates, i.e. a **directed visual contact**, not proven 3D rigid-body contact. Don't call it simulated physics.
- **P1 observed:** at **t5.0–6.5s** both actors settle into near-static neutral poses while the punchline text remains. The badge visually arrives at AKS but AKS has no clearly visible victorious reaction and MIL has no defeated comic response. The sequence still feels like a tech-demo rather than a finished joke.
- **Editorial verdict:** first interaction is meaningfully improved, **full first-scene ART NO-GO** pending reaction acting. No audio, no approved outro, no YouTube upload.

**Specific next patch:** 4.6–6.5s: AKS swivels/lifts/celebrates receipt of director plaque, MIL slumps/looks at him and gives a defeated hand gesture; preserve all 9 badge and hand safety checks. Four or six real stills → real 7s MP4 → ffmpeg + 14 frames editorial gate. After first-scene ART PASS, do actual 2–6 scene action gates. Main voice Denis private Qwen, optional different licensed female voice for AKS only after auditions; approved Denis v7 voice10 outro only on full version. Do not publish.
