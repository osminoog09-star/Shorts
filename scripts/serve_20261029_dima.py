#!/usr/bin/env python3
"""Dima-only voice gate for Serve S4-D25. No fallback; never publish."""
import asyncio, json, subprocess, pathlib, wave
import edge_tts
P=pathlib.Path("work/serve_20261029");P.mkdir(parents=True,exist_ok=True)
lines=[
"Представь: за едой приезжает не курьер, а маленький робот на колёсах.",
"Двадцать девятого октября такие доставки запустили в Австралии, на Голд-Косте.",
"Партнёры — Serve Robotics и DoorDash. Пока это пилот в районе Саутпорт.",
"Заказываешь еду в приложении и, если робот доступен, выбираешь доставку им.",
"Он забирает заказ из ресторана и едет по тротуару со скоростью пешехода.",
"Людям уступает дорогу, а при необходимости подключается удалённый оператор.",
"Приехал? Получаешь уведомление и открываешь отсек персональным кодом.",
"В начале участвует один ресторан. Другие планируют добавить позднее.",
"Теперь главное, чтобы робот не съел твою картошку по дороге.",
"Ты бы доверил ему ужин? Подпишись! И спасибо всем, кто досмотрел и поставил лайк."
]
async def main():
 manifest=[]
 for i,s in enumerate(lines):
  path=P/f"dima_{i:02}.mp3"
  last_error=None
  for attempt in range(3):
   try:
    await asyncio.wait_for(edge_tts.Communicate(s,"ru-RU-DmitryNeural",rate="+0%").save(str(path)),timeout=35)
    if path.stat().st_size<1000:raise RuntimeError("Empty TTS file")
    last_error=None
    break
   except Exception as exc:
    last_error=exc
    if path.exists():path.unlink()
    print(f"Edge TTS attempt {attempt+1}/3 for segment {i} failed: {type(exc).__name__}",flush=True)
    await asyncio.sleep(2*(attempt+1))
  if last_error:raise RuntimeError("DmitryNeural unavailable; NO-GO, no fallback") from last_error
  if path.stat().st_size<1000:raise RuntimeError(f"Empty TTS {i}")
  p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
  duration=float(p.stdout.strip())
  if duration<1:raise RuntimeError(f"Invalid duration {i}")
  manifest.append(dict(speaker="dima",voice_id="ru-RU-DmitryNeural",engine="Microsoft Edge TTS",rate="+0%",source_file=str(path),duration_s=duration,text=s))
 (P/"voice_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
 print("DIMA TTS PASS; segments",len(manifest),"total speech",sum(x["duration_s"] for x in manifest))
 print("NO-GO: approved HostCorner lip sync, visual integration and subjective listening still required")
asyncio.run(main())
