# M1lash — Serve robot delivery Shorts — complete preproduction / NO-GO
**Event** 29 October 2026; primary [release](https://newshub.medianet.com.au/2026/10/serve-robotics-and-doordash-launch-australias-first-footpath-delivery-robots-on-the-gold-coast/179064/), independent [SmartCompany](https://www.smartcompany.com.au/technology/doordash-launches-gold-coast-food-delivery-robot/), preview [Reuters 28.10](https://www.reuters.com/world/asia-pacific/serve-launches-robot-deliveries-australia-first-international-push-2026-10-28/). **Pilot in Southport, Gold Coast, not nationwide; remote human supervisors can assist.**

## Three truthful titles
1. «Робот привёз еду вместо курьера: это уже работает в Австралии 🤖»
2. «Еду доставляет робот на тротуаре. Как это устроено?»
3. «Австралия запустила доставку еды роботами — пока в одном районе»

**Hook 0–2 s:** «За едой приехал… робот!» (editorial short form of first line).

## Complete Dima narration, editorial time estimates
| Time | Fact/joke | Exact spoken Russian text |
|---|---|---|
|00–04|FACT|Представь: за едой приезжает не курьер, а маленький робот на колёсах.|
|04–09|FACT|Двадцать девятого октября такие доставки запустили в Австралии, на Голд-Косте.|
|09–14|FACT|Партнёры — Serve Robotics и DoorDash. Пока это пилот в районе Саутпорт.|
|14–19|FACT|Заказываешь еду в приложении и, если робот доступен, выбираешь доставку им.|
|19–24|FACT|Он забирает заказ из ресторана и едет по тротуару со скоростью пешехода.|
|24–29|FACT|Людям уступает дорогу, а при необходимости подключается удалённый оператор.|
|29–34|FACT|Приехал? Получаешь уведомление и открываешь отсек персональным кодом.|
|34–39|FACT|В начале участвует один ресторан. Другие планируют добавить позднее.|
|39–44|JOKE, FICTION|Теперь главное, чтобы робот не съел твою картошку по дороге.|
|44–50|CTA, DIMA|Ты бы доверил ему ужин? Подпишись! И спасибо всем, кто досмотрел и поставил лайк.|

**Timing caveat:** timings are provisional, NOT forced-aligned to synthesized audio. Exact SRT matching the script is in the current-turn source ZIP, not this repo. Recalculate when Dima voice is available.

## Storyboard / director's treatment
**Style selected S4-D25**: next not-yet-tested after S3/S6/S7/S2/S5/S1 per `style-library.md`; clean vector, subtle parallax. Alternative S7-D25 (tech) or S3-D25 (comic), but those already have queue entries. Huashu-motion concept: one thought/action/shot at a time; deterministic `frameAt(t)`, scene-specific animation; 2.5D not a crop of a landscape movie.
- 00–04: robot close-up on pavement; low camera push-in; label «КУРЬЕР БЕЗ ВОДИТЕЛЯ».
- 04–09: track past a restaurant as order is collected; «ГОЛД-КОСТ, АВСТРАЛИЯ».
- 09–14: abstract partner-name sign, no brand logos; «ПИЛОТ / САУТПОРТ».
- 14–19: invented phone checkout UI with selectable robot; «ВЫБОР В ПРИЛОЖЕНИИ».
- 19–24: wheel-height tracking along sidewalk; «СКОРОСТЬ ПЕШЕХОДА».
- 24–29: pedestrian crosses, robot yields, operator icon; «ПРОПУСКАЕТ ЛЮДЕЙ».
- 29–34: phone notification + code unlock; «ОТКРЫТИЕ ПО КОДУ».
- 34–39: abstract district schematic, **not real geographic map**; «ПИЛОТ, НЕ ВСЯ АВСТРАЛИЯ».
- 39–44: cartoon robot looks at fries, clearly a **joke**.
- 44–50: **unchanged approved M1lash HostCorner**, new Rhubarb visemes and original Dima CTA; «ТЫ БЫ ЗАКАЗАЛ?».

**Rights**: All 8 pilot keyframes are original Python/Pillow illustrations, explicitly «КОДОВАЯ РЕКОНСТРУКЦИЯ»; not a Serve/DoorDash photograph or real UI. No third-party logos, images, film footage, or copyrighted music imported. Final production must license every added asset. Use only original score (not yet created), no unverified Laeko track.

## Voice manifest
```json
{"speaker":"dima","voice_id":"ru-RU-DmitryNeural","engine":"Microsoft Edge TTS","rate":"+0%","source_file":null,"status":"NOT_GENERATED","host_lipsync":"NOT_GENERATED","cta_same_voice":true}
```
No automatic fallback to Piper/Liam. Svetlana not needed. Final render requires exact audio provenance, actual listening, new visemes and approved host overlay. Safe layout 1080×1920 full-bleed, reserve host lower-left and right/bottom YouTube overlays, no stacked info cards.

## Publication metadata
**Title**: Робот привёз еду вместо курьера: это уже работает в Австралии 🤖 #shorts

**Description**: 29 октября 2026 года Serve Robotics и DoorDash запустили ограниченный пилот доставки еды роботами на тротуарах района Саутпорт, Голд-Кост. При доступности робота его можно выбрать в приложении. Роботы уступают пешеходам, операторы могут помогать дистанционно, а отсек открывается персональным кодом. В начале участвует один ресторан. Видео использует авторскую кодовую реконструкцию, а не съёмку реальной доставки. Источники: https://newshub.medianet.com.au/2026/10/serve-robotics-and-doordash-launch-australias-first-footpath-delivery-robots-on-the-gold-coast/179064/ ; https://www.smartcompany.com.au/technology/doordash-launches-gold-coast-food-delivery-robot/ . #shorts #роботы #технологии #австралия #доставка #M1lash

**Tags**: робот-доставщик, Serve Robotics, DoorDash, Голд-Кост, Саутпорт, роботы, доставка еды, технологии, Австралия, научпоп, M1lash, shorts.

**Pinned**: «Ты бы доверил роботу ужин — да или нет? И почему? 👇»

## Actual pilot and release gate
Created a **46.00s, 1080×1920, 24fps H264 SILENT technical animatic**, with eight original coded static scenes. Full ffmpeg decode PASS; 8 keyframe contact sheet visually checked; clipped headlines corrected. SHA256 `e833b1e899d9a2835b99b523a53c039d385f42e68689dfc9bd4de62a72e73f5e`. No audio, no approved host, no lip-sync and no proper scene motion: **NO-GO**, NOT a final video. Art/code/QA/MP4 in owner's current conversation ZIP `M1lash_20261029_Radar_Serve_NO_GO.zip`, not in GitHub. Local TTS pip install attempted but environment DNS unavailable. No GitHub Actions dispatch action exposed by current connector. No uploads or publishing.


### Camera-motion improvement / actual additional artifact
After the original static pilot, created a **46.00 s 1080×1920 24fps H.264 deterministic zoom/pan camera animatic** from eight original coded keyframes: `serve_visual_animatic_camera_NO_VOICE_NO_GO.mp4`, 3,479,785 bytes, SHA256 `ee2c554ed5c08e83ab250d620a62e12030ad1b403f60da3486055f7bd9270404`. Full FFmpeg decode PASS. This is a **visual NO-GO preview**, no Dima audio, no approved host, no lip-sync; camera movement alone is not complete scene animation. Included in refreshed conversation ZIP, not committed to GitHub binary storage.
