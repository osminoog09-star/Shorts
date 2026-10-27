# M1lash V6: first focused hand/contact code-animation cycle (2026-10-27)

## Produced
- `M1lash_V6_HAND_CONTACT_STUDY.mp4`: 6s, 960×540 24fps H.264, **silenced technical study**.
- Independently coded frame-by-frame SVG via Python/CairoSVG; camera locked; palm, wrist cuff, separate finger shapes, curved jacket sleeve and moving button.
- Exact source `m1lash_v6_hand_study.py` and MP4 supplied as ChatGPT attachments; not part of the repository until separately committed.
- Full final MP4 decoding: PASS, duration 6.000s.

## Actual self-audit
- First contact pass: fingertip x≈607 compared to button centered x=687 — contact was off left edge. **NO-GO**.
- Corrected horizontal hand travel by +55px. Second inspected frame at t=3.0s shows finger above the button cap near center left, but finger penetrates rather than compressing naturally. CONTACT_GATE still **NO-GO**.
- Hand has recognizable thumb / index but remaining fingers overlap geometrically. Anatomy **3/10**, contact **4/10**, acting **3/10**, background **3/10**, close-up staging **5/10**, technical decode **9/10**. **Target >=8/10 is unmet.**
- Important: this is one **focused** subsystem improvement, not a complete revised video episode. No Dmitry speech; lipsync not assessed.

## New skill requirements
- Compute and export target-space `finger_tip_xy` and `button_contact_bounds`, and compare before rendering.
- At impact, ensure visible skin/button boundary, 2-4 pixels of *controlled button travel*, and no unexplained interpenetration.
- Model finger joints and hand volumes, including curled remaining fingers, rather than free-floating paths.
- Inspect exact contact frames, not merely start/end of clip; veto finished claims when physical mechanics look wrong.
- Separate `model beauty`, `contact physics`, `acting`, `visual continuity`, `audio` quality scores. 8/10 on every applicable criterion is hard gate.
