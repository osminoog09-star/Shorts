from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent
async def run():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content((ROOT/'boltyk_rig.html').read_text(),wait_until='load')
  await page.screenshot(path=str(ROOT/'BOLTYK_12_POSES_MODEL_SHEET.png'))
  for i in range(12):
   await page.evaluate('(i)=>window.variant(i)',i)
   await page.screenshot(path=str(ROOT/f'pose_{i:02d}.png'))
  await b.close()
  assert not errors,errors
  print('MODEL_SHEET_12_VARIANTS_1080P RENDER PASS')
if __name__=='__main__':asyncio.run(run())