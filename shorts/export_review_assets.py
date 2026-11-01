from pathlib import Path
import shutil, asyncio
from edge_tts import Communicate
R=Path(__file__).resolve().parents[1]
out=R/"motion-output"
out.mkdir(exist_ok=True)
shutil.copy2(R/"media/outro/m1lash_outro_v1_vertical.mp4",out/"outro_rev4_vertical.mp4")
shutil.copy2(R/"tools/assemble_with_outro.py",out/"assemble_with_outro.py")
async def go():
  films={"001":"Старикам тут не место","002":"Старикам тут не место","003":"Одержимость","004":"Из машины","005":"Стрингер","006":"Интерстеллар"}
  for code,name in films.items():
    await Communicate("Это был фильм… "+name+".","ru-RU-DmitryNeural").save(str(out/("dima_"+code+".mp3")))
asyncio.run(go())
shutil.copy2(R/"videos/pretend_bot3_gpt_ru_v3.mp4",R/"videos/review_asset_carrier.mp4")
