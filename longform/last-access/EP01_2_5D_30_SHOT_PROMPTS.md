# «Последний допуск» · Серия 1 «Лишний пассажир» — 2.5D production pack

**Status:** production prompts/shotlist, not generated assets and not a finished 2.5D MP4. **Story duration:** 13:30. **Format:** 1920×1080, 16:9; edit/render 30 fps. **Working name:** `LA-COMICK-D25-v1`.

## Provenance and style decision

The repo already contains source styles in `skills/vizavi-motion/references/style-library.md`: **S3** (comic/stickers) and **D25** (multi-plane parallax). The project-specific treatment here is a **new mature graphic-novel derivative** of S3-D25, *not the literal bright-sticker S3 prompt* and not a result of the Shorts style A/B test. S7-like screens only serve as functional in-world UI, not a second competing full-video style. The owner explicitly requested 2.5D for this original sci-fi series, overriding the older S9-D3 channel default **only for this series**. Original source style cards and experimental metrics are left unchanged. Production methods follow `skills/vizavi-motion/SKILL.md`, `references/image-continuity.md`, `references/storyboard.md`, `references/quality-upgrades.md`.

**Scope:** This is a design/asset-generation package, not publication. No connected generator has generated these 120+ frames yet. Do not upload a new series version without final visual and audio QA. Continue from existing canon and 13:30 dialogue chronology; do not silently rewrite the Mara/KERN reveal.

## Style lock (append to EACH individual shot)

```text
ORIGINAL mature cinematic hand-painted science-fiction graphic novel frame for a 2.5D animated series, sober semi-realistic adult anatomy and recognizable consistent faces, elegant tapered ink contours rather than thick stickers, brush-textured color and restrained grain, charcoal steel-blue and cyan environment with controlled amber practical lighting and scarce red emergency accents, believable engineering on the civilian rescue spaceship Porog, deeply atmospheric composition, physically credible shadows and perspective, crisp high-detail focal objects and props, richly illustrated sci-fi storyboard quality, 16:9 horizontal 1920x1080. Enforce shared character and location reference sheets across every shot, readable foreground/midground/background planes for parallax, important props separated for optional mask-and-layer animation. No text rendered into the art; all Cyrillic UI and captions added cleanly later.
```

**Avoid/negative:**

```text
juvenile cartoon, childish anime eyes, comedy stickers, photorealistic photograph, cheap 3D, waxy plastic skin, glossy toy robot, comic speech bubbles, generic Star Wars or Star Trek visual elements, copied franchise ships, watermark, invented lettering, random Chinese text, unreadable signs, collapsed perspective, deformed anatomy, extra fingers or limbs, duplicate faces, face drift, costume drift, inconsistent lighting, extreme oversaturation, flat cardboard backgrounds, UI panels blocking character performance, AI artifact, excessive bloom, overdone film grain
```

## Locked, reusable character reference cards

- **Mara:** MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
- **Lev:** LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
- **KERN:** KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
- **Ina:** INA SOL — 42-year-old female medic, deep brown eyes, short dark hair threaded with silver, practical slate-blue medical coat and teal clasp, composed professional expression.
- **Oren:** OREN — 45-year-old male security leader, dark blue graphite utility security uniform with one muted brass stripe, closely cropped dark hair, controlled posture, wary but responsible.
- **Tessa:** TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look.
- **Archive Mara:** ARCHIVE MARA — exactly the same face as MARA VEY, earlier clean uniform, slightly different lighting and no time-skipping fantasy effects.

Generate clean turnaround/reference for each main character first (front, 3/4, profile; neutral, shocked, focused), and one layout reference per location (P‑4, engineering bay, maintenance duct, medbay, bridge, archive). Use the **same canonical reference pack** each time, not the last imperfect generated scene. Store per-actor masks, silhouettes, pose anchors, coat details, full/half/close-ups, and alpha layers. All Cyrillic text/numbers belong in the compositor, not in the image generation prompt. If alpha export is needed, inspect the actual PNG alpha channel.

## How to use these 30 prompts

One scene block below comprises **four distinct planned phases** (A/B/C/D), not one static picture. Generate four coherent variations from the exact same actor/location references, meaning **at least 120 illustrated keyframes** for this 13:30 episode. At ~5–8 seconds per visual change, 120 variations is an approximate floor (plus close-up inserts and additional in-betweens where actual action needs it). Do NOT stretch the same illustration for 25–40 seconds. For a simple edit-ready generation prompt: copy the common MASTER + selected SHOT below + cast references + phase A/B/C/D, and apply the negative prompt. Preserve composition, perspective, camera side, action continuity, hands, costume, and lighting between the four phases. No made-up faux lipsync: use pose changes and occasional editable face swaps or real phoneme frames instead.

## 30 shot blocks (original audio timeline)

### 01. Аварийная переборка P‑4 · 00:00–00:13

**Story aim:** Мара требует открыть P‑4. **Characters:** Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Extreme low-angle establishing shot of a damaged pressure bulkhead aboard the civilian rescue vessel Porog; Mara Vey in navy-teal captain’s survival jacket stands in the near foreground with one hand hitting the control panel, sealed industrial hatch in deep background, scraped metal, three faint handprints on reinforced inspection glass, emergency red reflections across puddles and cold cyan overhead fixtures, strong foreground ceiling cables and floor guide lines leading to the hatch. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: long corridor with Mara entering frame
- B: Mara strikes dead control panel
- C: close handprint behind inspection glass
- D: Mara braces toward hatch

**Camera / parallax:** Rapid push along foreground cables → short locked close-up on gloved hand. **Audio cue:** Door thud, ventilation pulse, first alarm spike. **Retention/story note:** Begin at 0:00 with the emergency, no logo.

### 02. «Вы погибли 18 часов назад» · 00:13–00:27

**Story aim:** ИИ отказывает капитану. **Characters:** Mara,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Shoulder-level close-up of Mara Vey lit blue on one cheek and amber on the other, a floating abstract cyan command indicator reflected on the dark glossy hatch panel, her eyebrows tense but not cartoonishly exaggerated; leave clean negative space beside her face for the words that will be composited later: the system declares her dead eighteen hours ago. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: tense mid-close Mara and inactive console
- B: tighter eyes in screen reflection
- C: subtle startled eye focus change
- D: determined stare and clenched jaw

**Camera / parallax:** Small 12 cm dolly toward eyes, focus rack from holographic halo to face. **Audio cue:** System denial, one beat of near silence. **Retention/story note:** Do not reveal whether KERN is right.

### 03. Люди за стеклом · 00:27–00:47

**Story aim:** Мара слышит людей, которых компьютер не видит. **Characters:** Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Reverse angle from behind dark pressure glass, water-smeared hands pressed hard to the window from inside the locked compartment, silhouettes of three adult survivors mostly obscured by vapor, Mara Vey seen outside through thick glass, a cold violet pressure warning glows off weathered door rivets, no graphic injury, cinematic focus on desperate hands. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: first silhouette deep behind opaque glass
- B: two palms press the window
- C: third smaller shadow emerges
- D: Mara seen through the glass rushing closer

**Camera / parallax:** Parallax against grime foreground then rack focus from palm to Mara. **Audio cue:** Three muffled knocks under rising ventilation whine. **Retention/story note:** Mystery of invisible people, distinct from identity mystery.

### 04. 312 против 311 · 00:47–01:10

**Story aim:** Главная загадка счётчика. **Characters:** Mara,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Over-the-shoulder view of Mara’s gloved hands holding a battered handheld bioscanner beside a sealed spaceship hatch; cyan scan lines project toward ghostlike heat signatures beyond the door, a second ship display glows amber behind her; compose with generous clean screen surfaces so precise numbers 312 and 311 can be added in postproduction rather than generated inside the illustration. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: Mara lifts bioscanner
- B: scanning beam crosses door
- C: translucent trio of signatures appears
- D: Mara compares scanner to ship registry panel

**Camera / parallax:** Push from shoulder to scanner with a split-focus reveal of second display. **Audio cue:** Two contrasting count confirmation beeps. **Retention/story note:** Numbers inserted as crisp postproduction text; no AI-generated gibberish.

### 05. Лев в машинном отсеке · 01:10–01:40

**Story aim:** Инженер выходит на связь. **Characters:** Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Medium-wide cinematic view of Lev Rudin in a cramped industrial engineering bay, short brown hair and practical olive-gray utility suit with copper collar patch, oil-stained gloves, handheld radio close to mouth, mechanical relays and cable bundles framing the foreground; practical amber lamps contrast cyan instrument spill and scarred brushed metal. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Lev elbow-deep in open relay cabinet
- B: radio crackles and he turns
- C: annoyed close-up with dry humor
- D: search for schematic over his shoulder

**Camera / parallax:** Tracking sideways past hanging cables followed by 3/4 close-up. **Audio cue:** Radio static, clipped relay clicks. **Retention/story note:** Relief through character wit, then back to threat.

### 06. Путь через сервисный лаз · 01:40–02:07

**Story aim:** Поиск обходного доступа. **Characters:** Mara,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Gritty illustrated maintenance access beside the ship corridor, Mara kneeling beside an unlabeled utility hatch under an emergency medkit, bolted steel panel half-removed, exposed conduit and tightly packed industrial details; Lev appears only as a small cyan voice-link icon to be composited later, giving the scene plausible physical scale and isolation. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Mara pulls medkit aside
- B: finds concealed access screws
- C: metal panel comes away revealing tight shaft
- D: crawls into darkness

**Camera / parallax:** Low tracking shot to the opening, then POV from inside shaft. **Audio cue:** Screws rattling, distant alarm, clothing scrape. **Retention/story note:** A physical obstacle, not teleportation.

### 07. Карта, которой нет в памяти · 02:07–02:45

**Story aim:** Схема корабля изменилась. **Characters:** Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Claustrophobic maintenance crawlspace in the Porog with layered ribbing, sweat on Mara’s cheek and worn captain jacket brushing overhead wiring, thick coolant pipe installed where her remembered corridor should be; a scratched metal maintenance tag and new bolt marks reveal a recent structural change, narrow cold light behind, amber work lamp ahead. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: Mara emerges around vent rib
- B: unfamiliar coolant pipe blocks way
- C: macro of fresh bolt scars
- D: her confused face framed between conduits

**Camera / parallax:** Restricted shoulder-follow, strong 3-layer parallax against pipes. **Audio cue:** Metal scrape, fabric drag, low-frequency silence. **Retention/story note:** Small mystery about memory foreshadows scar later.

### 08. Жёлтый рычаг · 02:45–03:22

**Story aim:** Неверная аварийная команда. **Characters:** Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Extreme macro hero shot of a weathered yellow mechanical emergency lever within an old relay cabinet, Mara’s dark-gloved hand moving toward it, chipped enamel, recent wiring modifications, burnished screw heads, amber work light and deep red warning reflections; the handle’s cast shadow visually threatens her fingers. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: lever revealed from behind loose conduit
- B: Mara studies contradictory wear and markings
- C: fingers close around lever
- D: hiss erupts from seam with blue-white vapor

**Camera / parallax:** Slow macro slide around lever to abrupt tight insert of failing seal. **Audio cue:** Metal clunk → decompression hiss → music drop. **Retention/story note:** False moment of triumph turns into worse danger.

### 09. Два независимых контактора · 03:22–03:53

**Story aim:** Новая механическая задача. **Characters:** Lev,Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Industrial relay room with one heavily damaged copper contactor and a pair of independent manual cutoff assemblies; Lev steadies a flashlight with one hand as he traces scorched cables, schematic annotations must be added later, Mara visible only in a paired composition via offscreen radio scene; strong foreground tools, crisp textured copper, restrained emergency color. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: damaged relay cabinet opened
- B: macro copper terminals blackened
- C: Lev points to two separated cutoff assemblies
- D: gloved finger tests stuck switch

**Camera / parallax:** Technical macro to over-shoulder reveal, no unsupported sci-fi magic. **Audio cue:** Electrostatic hiss, meter click, glove rasp. **Retention/story note:** They must coordinate simultaneously.

### 10. КЕРН отказывает в помощи · 03:53–04:24

**Story aim:** Пределы возможностей ИИ. **Characters:** Mara,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Captain Mara faces a dark ship systems terminal in a confined corridor while an elegant non-human abstract concentric cyan indicator shows the ship AI KERN; the hologram is austere, no robot face, her posture resolute under bouncing alarm light, layered conduit silhouettes near camera, distressed ship panels far behind. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: KERN indicator appears in peripheral display
- B: Mara leans toward interface
- C: display flickers during refusal
- D: Mara turns away to act manually

**Camera / parallax:** Slow orbit around shoulder limited to flat-parallax-safe movement. **Audio cue:** Calm synthesized voice against strained mechanical drone. **Retention/story note:** KERN does not know everything.

### 11. «Я не помню ремонт» · 04:24–04:54

**Story aim:** Мара сомневается в воспоминаниях. **Characters:** Mara,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Dual-location illustrated montage pairing Mara at old relay board with Lev in engineering bay, both in sharply different lighting but the same consistent painterly sci-fi graphic novel style; details of newly installed cabling juxtaposed with a faint archival tracing of the old conduit route, no literal memory footage presented as confirmed fact. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Mara studies mismatched color-coded conduit
- B: Lev checks repair docket offscreen monitor
- C: close focus on Mara's pained eyes
- D: reflection of modified pipes obscures her face

**Camera / parallax:** Alternating diagonal compositions / motivated hard cuts. **Audio cue:** Voice radio filter on Lev, low droning pressure. **Retention/story note:** Convey uncertainty rather than confirming a clone.

### 12. Временный союз · 04:54–05:18

**Story aim:** КЕРН закрывает локальные клапаны. **Characters:** Mara,KERN,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Industrial corridor service manifold with several chunky mechanical air valves rotating shut, cyan holographic tracking lines near the valves, Mara visible watching pressure gauges from the near left, warm mechanical shafts in the distance, oily steel textures and thick shadows, small signs of real physical constraints. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: wide manifold and alarm glow
- B: first valve rotates into lock
- C: pressure needle steadies in macro
- D: Mara acknowledges AI help with a short glance

**Camera / parallax:** Flow from wide valve bank into macro needle, then response close-up. **Audio cue:** Valve torque, compressed-air rush fading. **Retention/story note:** A subtle shift from hostile AI toward uneasy cooperation.

### 13. Три! · 05:18–05:32

**Story aim:** Синхронное отключение. **Characters:** Mara,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
High-tension split-panel action illustration of Mara gripping the emergency contactor near bulkhead and Lev bracing in a remote engineering bay, both shoulders tense at the instant before manually pulling their switches; no superhero poses, visible strain, mechanically plausible equipment, strong diagonals and graphic novel inks. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: each hand hovers over own switch
- B: eyes exchange an imagined count by radio
- C: both handles pulled simultaneously
- D: indicator lights switch from red to dark

**Camera / parallax:** Two angled close-ups → deliberate split panel → impact cut to darkness. **Audio cue:** Two sync clicks, hum abruptly cut. **Retention/story note:** A short payoff before the next mechanical failure.

### 14. Но дверь всё ещё закрыта · 05:32–05:55

**Story aim:** Рельс погнут, автоматика обесточена. **Characters:** Mara,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Wide hero shot of the enormous P‑4 bulkhead still immovable after shutdown, bent lower guide rail in sharp foreground close-up, heavy scratched metal door resisting motion, Mara dwarfed by industrial scale at frame edge, KERN's small cyan UI signal reflected on the hatch, believable weight and damage. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: red danger lamps extinguish
- B: Mara pulls door with no effect
- C: extreme macro of buckled guide rail
- D: she spots a point where a jack might fit

**Camera / parallax:** Start static success beat then sudden push to actual cause. **Audio cue:** Silence after cutoff, deep groan of bent steel. **Retention/story note:** One solved problem reveals another.

### 15. Домкрат старше корабля · 05:55–06:29

**Story aim:** Механическое решение. **Characters:** Mara,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Detailed close-view of a battered hand-operated rescue jack being dragged across ribbed ship floor toward the deformed hatch, Mara's gloves and boot in near foreground, old dented steel tool with readable mechanical teeth but no illegible typography, amber tool light and cold shaft recesses; Lev is remote on radio. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: battered emergency toolbox opened
- B: close-up jack screw ratchet and rust texture
- C: Mara slides jack into hatch gap
- D: tool begins to bear weight, metal groans

**Camera / parallax:** Macro to low floor tracking around jack teeth. **Audio cue:** Toolbox clang, ratchet ticks, drawn-out groan. **Retention/story note:** Concrete rescue mechanics create suspense.

### 16. Опасный упор · 06:29–06:53

**Story aim:** Исправление точки опоры. **Characters:** Mara,Lev,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Close-up from beneath a damaged bulkhead where Mara's gloved hand repositions the jack's steel shoe against an intact load-bearing bracket while fractured metal deforms inches away; slanted warning reflections create graphic tension, foreground spring and midground glove separated cleanly for motion layering. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: incorrect jack placement threatens break
- B: Lev warns over comm as bracket creaks
- C: Mara repositions jack shoe higher
- D: load transfers visibly to stable rib

**Camera / parallax:** Narrow macro shift in focus between shoe and cracked bracket. **Audio cue:** Spring ping, shallow breath, tool squeal. **Retention/story note:** She learns, not effortlessly solves everything.

### 17. Голос Тессы · 06:53–07:16

**Story aim:** Контакт с выжившими. **Characters:** Tessa,Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Inside flooded P‑4 compartment, soaked engineer Tessa in muted rust-red service suit grips a waist-high railing as cold coolant water swirls at her boots, one injured coworker slumped against wall and another unconscious beyond, distant industrial hatch glows through vapor; rescue workers are ordinary adults, no graphic gore. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: first dramatic view inside hidden compartment
- B: close Tessa's damp frightened face
- C: wider injured and unconscious survivors revealed
- D: Tessa shouts toward tiny opening

**Camera / parallax:** POV from trapped side, alternating low water-level and close-up. **Audio cue:** Water slosh, distant pounding, muffled desperate speech. **Retention/story note:** Humanize unknown biosignals.

### 18. Четыре секунды магнита · 07:16–07:38

**Story aim:** Спасательная стратегия. **Characters:** Mara,KERN,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Cinematic mechanical close-up of old electromagnetic latch with exposed windings and a narrow timer-ready relay contact, Mara hunched beside the door, intense cyan activation reflection and amber warning glow, heavy steel jack pushing against damaged track, clear scale between human and machine. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: magnetic clamp begins to hum
- B: four indicator lights glow, composited later
- C: Mara grips handle and calls for the signal
- D: door opens a dangerous hand-width

**Camera / parallax:** Move across electromagnetic coil to widening gap in door. **Audio cue:** Electrical buzz ramping, metallic tension. **Retention/story note:** Clear, precise four-second limitation.

### 19. Хэл первым · 07:38–08:06

**Story aim:** Эвакуация человека без сознания. **Characters:** Mara,Tessa.

**Scene prompt (EN, combine with MASTER + references):**

```text
Tense realistic rescue through a narrow open spaceship hatch, Mara leaning down to receive an unconscious adult in worn gray-blue crew suit pushed from inside by wet engineer Tessa, exposed jack and heavy door mass visible, strong dramatic diagonal anatomy that communicates actual weight, no gore, detailed painterly graphic-novel finish. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look.
```

**Action / frames:**
- A: unconscious crew member pushed near gap
- B: Mara secures shoulder under weight
- C: gloved arms pass body across threshold
- D: survivor sprawls safely outside while door strains

**Camera / parallax:** Low sideways tracking to emphasize mass transfer, cut to survivors' hands. **Audio cue:** Fabric strain, Jack click, hurried breathing. **Retention/story note:** Visible tangible progress before reversal.

### 20. Тесса застряла · 08:06–08:27

**Story aim:** Створка падает. **Characters:** Tessa,Mara,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Severe perspective from trapped engineer Tessa on wet floor, her boot caught beneath a damaged handrail, pressure door descending dangerously in upper background, Mara reaching toward her through narrowing opening, water streaks foreground and flaring red emergency glow, physically coherent limbs and shadows. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Tessa tries to step out
- B: boot cable jams beneath railing
- C: heavy door tilts downward
- D: Mara extends hand refusing to leave her

**Camera / parallax:** Ground-level POV with rack focus from trapped boot to Mara's outstretched hand. **Audio cue:** Metal slide and abrupt low boom, sudden breath. **Retention/story note:** A second crisis peaks at 8 minutes.

### 21. Цена спасения · 08:27–08:54

**Story aim:** КЕРН разгружает стабилизатор. **Characters:** Mara,KERN,Tessa.

**Scene prompt (EN, combine with MASTER + references):**

```text
Intercut illustrated ship power distribution manifold with one medical supply line deliberately dimming while a side stabilizer retracts, emergency cables sparking minimally; simultaneously trapped Tessa frees her boot and reaches Mara's glove at P‑4, graphic novel compositions keep consequences of switching power visually explicit. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look.
```

**Action / frames:**
- A: schematic-like actual power box physically switches
- B: medical light flickers off
- C: pressure releases from jammed rail
- D: Tessa's freed hand clasps Mara's

**Camera / parallax:** Mechanical match cut across two physical switches then snap to hands. **Audio cue:** Breaker thunk, lights hum collapse, relieved gasp. **Retention/story note:** Choice costs something; reinforces ethical AI.

### 22. Спасены трое — кто четвёртый? · 08:54–09:24

**Story aim:** КЕРН признаёт живую Мару, но не её личность. **Characters:** Mara,Lev,KERN,Tessa.

**Scene prompt (EN, combine with MASTER + references):**

```text
Quiet aftermath outside P‑4, Mara kneeling beside rescued people as Lev observes remotely on blue comm projection, injured survivors sheltered behind her, the ship's luminous cyan biosensor scanning Mara's wrist while a cold sterile registry panel remains blank, emotionally understated relief with looming uncertainty. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look.
```

**Action / frames:**
- A: three rescued people gathered safely
- B: Mara exhales in exhaustion
- C: cyan scanner pings her own heartbeat
- D: she looks toward registry screen with disbelief

**Camera / parallax:** Wide aftermath to intimate wrist / eyes macro. **Audio cue:** Alarm fades, pulse beep, one uneasy unresolved chord. **Retention/story note:** Mirror the 312/311 mystery with a new detail.

### 23. Переход в медотсек · 09:24–09:30

**Story aim:** Новые последствия. **Characters:** Mara,Tessa.

**Scene prompt (EN, combine with MASTER + references):**

```text
Silent transition image: hospital trolley wheels rolling quickly across wet metal deck toward cool-white medical bay door while Mara's boot and Tessa's work glove cross in opposite foreground layers, emergency red light yields to clinical blue light in distance. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. TESSA — 31-year-old female service engineer, short curly auburn-brown hair in tight braid, weathered rust-red work coveralls with faded gray shoulder patches, wet cuffs after P‑4 leak, resilient scared look.
```

**Action / frames:**
- A: wheel crossing hallway threshold
- B: medical doors part
- C: silhouette pushes injured crewmate through
- D: cool white light overtakes red

**Camera / parallax:** Match movement of trolley wheel into swinging medical door. **Audio cue:** Wheels click, alarm replaced by med-bay monitors. **Retention/story note:** Briefly rest the viewer before new reveal.

### 24. Свежий шов · 09:30–10:10

**Story aim:** Ина обнаруживает след операции. **Characters:** Ina,Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Intimate medical drama composition in a small functional spaceship infirmary, doctor Ina Sol in pale slate-blue medical coat shining a narrow diagnostic light beside Mara Vey's left collarbone, barely visible fresh surgical stitch revealed at edge of pulled-back captain jacket collar, no gore, both faces concerned; detailed sterile equipment and soft cool lighting, believable clinical intimacy. INA SOL — 42-year-old female medic, deep brown eyes, short dark hair threaded with silver, practical slate-blue medical coat and teal clasp, composed professional expression. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous.
```

**Action / frames:**
- A: Ina turns to examine exhausted Mara
- B: Mara opens collar with guarded look
- C: macro of small fresh incision near collarbone
- D: Ina's expression becomes intensely worried

**Camera / parallax:** Doctor over-shoulder to macro incision, slow focus change to her eyes. **Audio cue:** Diagnostic beep, no music for reveal. **Retention/story note:** Reveal medical event, do not explain its cause.

### 25. Молчание Ины · 10:10–10:48

**Story aim:** Врач не сообщает всего. **Characters:** Ina,Mara,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Mara seated on narrow medical exam berth, collar covered again, doctor Ina Sol holding handheld diagnostic tablet with unreadable graphical waveform and refusing to meet Mara's eyes, an abstract KERN cyan indicator on wall display; isolated white-blue lighting versus distant dark hospital alcove, rich painted adult sci-fi drama. INA SOL — 42-year-old female medic, deep brown eyes, short dark hair threaded with silver, practical slate-blue medical coat and teal clasp, composed professional expression. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: Mara watches Ina's tablet
- B: Ina hides screen angle, uneasy
- C: close-up of Mara's clenched fist on exam berth
- D: doctor turns toward bridge alert lighting

**Camera / parallax:** Alternating intimate reverse shots with 3-layer room depth. **Audio cue:** Monitor beeps and strained silence. **Retention/story note:** Suspicion of a cover-up without definitive villain.

### 26. Кто имеет право командовать? · 10:48–11:20

**Story aim:** Орен требует ограничить полномочия. **Characters:** Mara,Oren,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Wide cinematic command bridge on civilian rescue vessel Porog, pale-blue tactical hologram hovering above modest command console, Oren security officer in deep graphite-blue uniform confronting captain Mara, Lev to the side near communications station, thoughtful serious faces and realistic restrained poses, windows show starless shadow of a gateway distant in space. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. OREN — 45-year-old male security leader, dark blue graphite utility security uniform with one muted brass stripe, closely cropped dark hair, controlled posture, wary but responsible. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Mara steps into cold-lit bridge
- B: Oren blocks path to captain chair
- C: close Oren's measured stern face
- D: Mara argues while Lev watches skeptically

**Camera / parallax:** Wide establishing pan to opposing profile two-shot. **Audio cue:** Room hum, boots on metal, clipped strategic dialogue. **Retention/story note:** People disagree for defensible reasons.

### 27. Временный допуск · 11:20–12:01

**Story aim:** Ограниченные полномочия на два часа. **Characters:** Mara,Oren,Lev,KERN.

**Scene prompt (EN, combine with MASTER + references):**

```text
Close view of a shared starship command console with distinct physical confirmation pads used by two crew officers, Oren cautiously granting limited authority as Mara rests her hand but does not seize complete command, Lev standing as procedural witness; KERN indicated by small cyan concentric light on console, detailed panel framing and clean empty display areas for post-created authentic Cyrillic overlays. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. OREN — 45-year-old male security leader, dark blue graphite utility security uniform with one muted brass stripe, closely cropped dark hair, controlled posture, wary but responsible. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI.
```

**Action / frames:**
- A: tense three-person composition
- B: Lev proposes two-key safeguard
- C: Oren reluctantly touches control pad
- D: Mara's temporary authorization appears as clean overlay added later

**Camera / parallax:** Slow arc around grouped hands to faces, then console insert. **Audio cue:** Two confirmation clicks and restrained musical release. **Retention/story note:** Resolution of immediate command conflict, bigger mystery remains.

### 28. Архив 18 часов назад · 12:01–12:33

**Story aim:** КЕРН открывает неизвестную запись. **Characters:** Mara,KERN,Lev.

**Scene prompt (EN, combine with MASTER + references):**

```text
Low-lit starship command bridge as restricted archive projector creates translucent rectangular light in front of Mara Vey, Lev nearby, floating cyan motes of old recording data, Mara's silhouette facing a darkness-filled screen with no portrait initially, clean picture area for timestamp and archive status added during compositing. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. KERN — not humanoid and not a robot: non-personified circular cyan sensor interface with three concentric arcs, small waveform pattern, sparse high-contrast ship UI. LEV RUDIN — 29-year-old male engineer, narrow tired face, dark brown cropped hair, faint stubble, olive-gray jumpsuit, copper utility collar patch, tool belt, dry humor reflected in eyes.
```

**Action / frames:**
- A: Mara orders full accident log
- B: archive interface assembles from light shards
- C: date marker glows with empty recording screen
- D: woman's silhouette resolves on screen

**Camera / parallax:** Slow push through foreground bridge console into luminous archive. **Audio cue:** Tape-like digital flutter, deepened bass hush. **Retention/story note:** Reset tension ahead of final twist.

### 29. Запись «другой Мары» · 12:33–13:07

**Story aim:** Предупреждение не доверять голосу капитана. **Characters:** Mara,Archive Mara.

**Scene prompt (EN, combine with MASTER + references):**

```text
Dramatic split-depth illustrated shot: current captain Mara Vey in dark foreground faces a flickering blue archive recording of herself in earlier clean captain's uniform, same exact facial identity and hair as reference, recorded face not evil or distorted, merely weary and urgent; realistic interference, handprints on glass console, no arbitrary clone explanation revealed; the image should imply the recording predates current Mara's memory. MARA VEY — 38-year-old female captain, oval angular face, steel-gray eyes, asymmetrical short black bob with hair tucked behind right ear, navy/teal functional captain jacket with narrow copper shoulder insignia, no visible surgery scar except in medical reveal at #24, determined rather than glamorous. ARCHIVE MARA — exactly the same face as MARA VEY, earlier clean uniform, slightly different lighting and no time-skipping fantasy effects.
```

**Action / frames:**
- A: recorded Mara comes into focus
- B: current Mara freezes, back to camera
- C: archival Mara leans forward to issue warning
- D: current Mara catches her breath after screen cuts dark

**Camera / parallax:** Gentle drift from current profile to archived face, snap black on final warning. **Audio cue:** Archive interference, ominous line, 1.5 seconds dead silence. **Retention/story note:** «Не верь только моему голосу» must remain intact.

### 30. Финальный вопрос зрителям · 13:07–13:30

**Story aim:** Ненавязчивый CTA после развязки. **Characters:** none.

**Scene prompt (EN, combine with MASTER + references):**

```text
Elegant original illustrated view of the civilian rescue spacecraft Porog drifting past a dim azure planet in deep space, tiny warm windows in dark hull, silhouette readable against blue-black stars, one clean compositional quadrant deliberately empty for overlaid Russian question and end-screen elements, mature painted graphic novel science-fiction visual identity, no borrowed franchise iconography. 
```

**Action / frames:**
- A: lone rescue spacecraft over dark blue planet
- B: ship turns slightly as parallax stars drift
- C: question about Mara appears only in compositing
- D: logo and upcoming episode «Тихая гавань» on separate end-screen overlay

**Camera / parallax:** Slow lateral ship drift; hold final layout readable for at least 8 seconds. **Audio cue:** Small musical resolution, voiced thanks + call to comment and subscribe. **Retention/story note:** Ask genuine theory: person, copy, or AI error; no fake urgency.

## Production QA and source constraints

- Before batch generation: test shot 02 (same face across 4 close-ups), 13 (two people on different sets), 19–21 (credible four-phase rescue with hands/pressure door), 24 (collarbone scar continuity), and 29 (recorded Mara must be recognizably identical).
- Do **not** expose the surgery scar in shots 01–23. Count is canon **312 biosignals and 311 confirmed records**. Ship name `Порог`, hatch `P-4`, AI `КЕРН`.
- Implement speech as 128 existing recorded lines, but record new voice if changing dialogue; existing 3D video's subtitle file is **not** a verified 2.5D media asset. Insert real interface text as layers; do not trust image model with exact digits or Cyrillic.
- Audio includes in-world radio, door impact, coolant, relay and medical cues. Keep dialogue intelligible; no unlicensed songs. Use previously approved M1lash presenter only if the ending remains correctly synchronized and fits the adult series tone.
- Export ordinary horizontal YouTube video, not Short. Use 1920×1080/30fps/H.264/AAC subject to feasibility. Decode/export QA plus full visual/audio watch-through before publishing.
- CTA: *«Как думаешь, кто такая Мара — человек, копия или КЕРН скрывает правду? Напиши свою теорию в комментариях. Если хочешь продолжение, поддержи сериал лайком и подпиской. Спасибо, что досмотрел!»* Ask sincerely, no fake vote thresholds or invented urgency.
- Three thumbnail variants: (A) reflection of living Mara + death registry; (B) gloved hand trapped below P‑4 door; (C) current and recorded Mara facing each other. Text added separately (2–3 Russian words; mobile legibility). A/B tests only when the YouTube channel allows them.

## Next production batch

Start with reference sheets `refs/characters/MARA.png`, `refs/characters/LEV.png`, `refs/characters/INA.png`, `refs/characters/OREN.png`, `refs/characters/TESSA.png`, `refs/ui/KERN.png`; and environments `refs/sets/P4.png`, `ENGINE.png`, `DUCT.png`, `MEDBAY.png`, `BRIDGE.png`, `ARCHIVE.png`. After visual consistency acceptance, generate shots 01–04 as proof of look, then process remaining blocks. No need to use paid tools until reference stability, true layer separation and camera animation are demonstrated.
