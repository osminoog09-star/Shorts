#!/usr/bin/env python3
"""Real Chromium desktop/mobile smoke for M1lash Studio. No external APIs or secrets."""
import asyncio
import functools
import http.server
import tempfile
import threading
from pathlib import Path

SITE=Path(__file__).resolve().parents[1]


async def run():
    from playwright.async_api import async_playwright
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(SITE))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}/"
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch(headless=True)
            with tempfile.TemporaryDirectory() as tmp:
                for label,width,height in [("desktop",1440,900),("mobile",412,915)]:
                    page=await browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
                    errors=[]
                    page.on("pageerror",lambda exc:errors.append(str(exc)))
                    response=await page.goto(base,wait_until="networkidle")
                    assert response.status==200
                    assert await page.title()=="M1lash Studio · Продюсерская панель"
                    assert await page.locator("#submitJob").is_disabled()
                    await page.locator("#topic").fill("Проверенный сюжет о роботах")
                    assert await page.locator("#submitJob").is_enabled()
                    assert await page.locator("#sumDuration").inner_text()=="25:00"
                    await page.locator('[data-tab="news"]').click()
                    assert await page.locator("#newsStatus").is_visible()
                    assert await page.locator("#outlierStatus").is_visible()
                    await page.locator("#refreshOutliers").click()
                    # No live API key must be a graceful empty state, not a fake trend.
                    assert await page.locator("#outlierList").is_visible()
                    await page.locator('[data-tab="styles"]').click()
                    assert await page.locator("#allStyles .panel").count()==21
                    await page.locator('[data-tab="create"]').click()
                    await page.locator('[data-group="experimental"]').click()
                    await page.locator('#styleChoices button').first.click()
                    assert (await page.locator('#sumStyle').inner_text()).startswith("X")
                    await page.locator('#format').select_option('short')
                    assert await page.locator('#sumDuration').inner_text()=="0:45"
                    await page.locator('[data-tab="reference"]').click()
                    assert await page.locator('#referenceUrl').is_visible()
                    await page.screenshot(path=f"{tmp}/{label}.png",full_page=True)
                    if label=="mobile":
                        w=await page.evaluate("document.documentElement.scrollWidth")
                        assert w<=width+2,f"mobile horizontal overflow: {w}px > {width}px"
                    assert not errors, f"{label} javascript errors: {errors}"
                    await page.close()
            await browser.close()
    finally:
        server.shutdown()


if __name__=="__main__":
    asyncio.run(run())
    print("Chromium desktop and mobile UI smoke PASS")
