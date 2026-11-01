#!/usr/bin/env python3
"""Export only approved studio outro and Dima reveal lines to PRIVATE Actions artifact.

No movie media included in this exporter. Useful for legitimate recovery of
local private drafts when ephemeral /mnt/data is reset between chat sessions.
"""
import asyncio
import json
import shutil
from pathlib import Path
import edge_tts

ROOT=Path(__file__).resolve().parents[2]
DST=ROOT/"recovery-output"/"studio-assets"
SPOKEN={
 "001":"Это был фильм «Старикам тут не место»",
 "002":"Это был фильм «Старикам тут не место»",
 "003":"Это был фильм «Одержимость»",
 "004":"Это был фильм «Из машины»",
 "005":"Это был фильм «Стрингер»",
 "006":"Это был фильм «Интерстеллар»",
}
async def main():
    DST.mkdir(parents=True,exist_ok=True)
    outro=ROOT/"media/outro/m1lash_outro_v1_vertical.mp4"
    if not outro.is_file() or outro.stat().st_size<200_000:
        raise FileNotFoundError("Approved rev4 vertical outro missing")
    shutil.copy2(outro,DST/"m1lash_outro_v1_vertical.mp4")
    for key,text in SPOKEN.items():
        path=DST/f"title_{key}_dima.mp3"
        await edge_tts.Communicate(text,voice="ru-RU-DmitryNeural",rate="+4%").save(str(path))
        if path.stat().st_size<4000:raise RuntimeError(f"TTS empty for {key}")
    (DST/"titles.json").write_text(json.dumps(
        {"voice":"ru-RU-DmitryNeural","rate":"+4%","titles":SPOKEN,
         "usage":"private movie Shorts; film title only after approved outro",
         "media_rights":"no movie media included"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("STUDIO_ASSETS",sorted(x.name for x in DST.iterdir()))
if __name__=="__main__":
    asyncio.run(main())
