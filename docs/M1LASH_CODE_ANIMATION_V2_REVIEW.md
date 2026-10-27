# M1lash Code Animation — V2 measured iteration, 27.10.2026

## What was actually produced
- Local output: `M1lash_CODE_ANIMATION_V2_ACTING.mp4`; 12.000 sec, 960×540, 24fps, 1,002,808 bytes; complete FFmpeg video decode PASS.
- Procedural render from Python/Pillow via FFmpeg; NO still-image/camera-pan video. No dialogue audio in this isolated motion test.
- Compared to `M1lash_CODE_ANIMATION_CLAUDE_STYLE_V1.mp4`: sampled at 1 fps, grayscale 96×54.
- Mean absolute frame change baseline **5.78/255**, candidate **5.97/255**; near-static transitions (difference <3) **4/11 in both**. These metrics do NOT imply better animation quality, nor retention.

## Improvements
- Anticipation before button press, hand acceleration/deceleration and slight delayed head follow-through.
- More independent startled-employee gestures and blink timing.
- Robot secondary head tilt/body bobbing.
- Programmatic joints and shapes, not edits of approved still illustration.

## Artistic QA NO-GO
- Design is still simplified line/shape art, below approved high-quality character style.
- No actual audio-driven lip-sync, dramatic physical reaction, believable fingers, face acting or natural shading.
- Most of the 12 seconds is still low-information motion.
- In the press shot, check **physical finger/button contact** in video before ever marking PASS. Programmatic hand target alone does not prove contact.

## Grounded study applied
- Disney Animation's publicly described principles include timing, clear staging, anticipation, follow-through and secondary action: https://www.disneyanimation.com/process/animation/
- Microsoft animation principles explain physical anticipation, overlapping motion and easing: https://learn.microsoft.com/en-us/windows/win32/lwef/animation-principles
- Blender docs on rigs, IK/FK, weight painting and action editor: https://www.blender.org/features/animation/
- Blender storyboarding should precede polish; thumbnails and staging support each scene: https://disneyanimation.com/process/story/

## Updated actionable skill requirements
1. **Character sheet before polish**: consistent 3/4/profile/side appearance, legible silhouette, proportion guide; refuse generic same-face procedural heads.
2. **Pose-to-pose beats**: for each acting action save anticipation, primary contact, physical recoil, settle. No random shaking disguised as acting.
3. **IK physical contact QA**: identify hand/world contact coordinates, verify minimum distance on frames of contact and actual prop displacement, no clipping/detachment.
4. **Eye-line acting**: character must look at actual prop/other character; eye target is world-space, not cosmetic wandering.
5. **Secondary action**: delayed eyebrows/head/hair/hands after primary motion; not identical sine waves for everyone.
6. **Dialogue**: mouth keyed to original Dmitry speech timings, with actual phoneme/word boundaries when available; never equate sine wave with lip sync.
7. **Independent review**: pair 1fps diff with viewed full-motion acting. V2 numerical delta +0.19 is weak evidence, not a pass.
8. **Escalate design method**: next iteration must improve silhouette, facial structure and multi-part body model, NOT add extra screen titles or camera pans.

Next acceptance: 10–20 second fixed-camera scene: clear button press with joint contact, distinct human shock reaction and robot consequential movement, polished faces, and playable original full Russian voice. Raise quality to user-set rating; current technical demo remains NO-GO.
