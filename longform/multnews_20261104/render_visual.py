#!/usr/bin/env python3
"""Original S3-D25 MultNews proof-of-style renderer. SILENT PILOT ONLY, not a longform master."""
from pathlib import Path
import argparse
import asyncio
import subprocess
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent

async def render(mode: str) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = await browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        # set_content bypasses file:// restrictions on locked-down Chromium builds.
        await page.set_content((ROOT / "film.html").read_text(encoding="utf-8"), wait_until="load")
        if mode in ("stills", "all"):
            directory = ROOT / "qa" / "stills"
            directory.mkdir(parents=True, exist_ok=True)
            for scene in range(6):
                await page.evaluate("([sec, scene]) => window.frame(sec, scene)", [3 + 10 * scene, scene])
                await page.locator("svg").screenshot(path=str(directory / f"scene_{scene:02d}.png"))
            print("SIX_STILLS_RENDERED 1920x1080")
        if mode in ("pilot", "all"):
            # 12 unique poses/s for comic stop-motion, deliver 30fps H264.
            await page.set_viewport_size({"width": 960, "height": 540})
            frames = ROOT / "qa" / "pilot_frames"
            frames.mkdir(parents=True, exist_ok=True)
            for k in range(120):
                await page.evaluate("([sec, scene]) => window.frame(sec, scene)", [k / 12, 0])
                await page.locator("svg").screenshot(path=str(frames / f"{k:04d}.png"))
            dest = ROOT / "qa" / "M1lash_MultNews01_SILENT_10s_PILOT.mp4"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-framerate", "12", "-i", str(frames / "%04d.png"),
                "-vf", "fps=30,scale=1280:720:flags=lanczos",
                "-c:v", "libx264", "-preset", "fast", "-crf", "24",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest),
            ], check=True)
            subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(dest),"-f","null","-"], check=True)
            print(f"PILOT_SILENT_FULL_DECODE_PASS {dest}")
        await browser.close()
        if errors:
            raise RuntimeError("Browser JS errors: " + repr(errors))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("stills","pilot","all"))
    args = parser.parse_args()
    asyncio.run(render(args.mode))
