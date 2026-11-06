#!/usr/bin/env python3
"""ПК Дениса: запись фрагмента фильма через браузер с ЛЕГАЛЬНОГО сайта (решение Дениса 06.11.2026).

Агент: открывает страницу фильма на разрешённом сайте → ставит нужное время → OBS записывает фрагмент
(видео + звук системы) → проверка на чёрный кадр (защита от записи = НЕ обходим, фильм пропускается) →
файл в C:\\M1lash\\Входящие\\clips → дальше монтажёр кино-Shorts.

Разрешены только сайты из publishing/clip_sources.json (legal: true). Любой другой домен — отказ.
Длина фрагмента ≤ max_fragment_sec (60 с). Ничего не скачивает с сайта, не трогает DRM, капчи и платный доступ.

Нужно на ПК: OBS 28+ (Инструменты → Настройки WebSocket-сервера → включить, пароль → переменная OBS_WS_PASSWORD;
сцена с «Захват окна/экрана» браузера + «Звук рабочего стола»), pip install playwright obsws-python, playwright install chromium.

usage: python scripts/pc/clip_recorder.py --url <страница фильма> --start 01:12:30 --dur 45 --id kino_012
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("M1LASH_ROOT", r"C:\M1lash")) / "Входящие" / "clips"


def allowed(url):
    cfg = json.loads((REPO / "publishing" / "clip_sources.json").read_text(encoding="utf-8"))
    host = (urlparse(url).hostname or "").lower()
    for s in cfg["sources"]:
        d = s["domain"].lower()
        if s.get("legal") and (host == d or host.endswith("." + d)):
            return s, int(cfg.get("max_fragment_sec", 60))
    return None, int(cfg.get("max_fragment_sec", 60))


def secs(t):
    p = [float(x) for x in str(t).split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def black_ratio(mp4):
    """Доля чёрных кадров: если сайт защищает видео, запись выходит чёрной — значит, этот фильм не берём."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-vf", "blackdetect=d=0.5:pix_th=0.08", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace")
    dur = sum(float(x) for x in re.findall(r"black_duration:([\d.]+)", r.stderr))
    total = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    tot = (int(total[1]) * 3600 + int(total[2]) * 60 + float(total[3])) if total else 0
    return dur / tot if tot else 1.0


def record(url, start, dur, vid):
    from playwright.sync_api import sync_playwright
    import obsws_python as obs
    cl = obs.ReqClient(host="localhost", port=4455, password=os.environ.get("OBS_WS_PASSWORD", ""), timeout=10)
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        # отдельный профиль студии (вход в аккаунт сайта, если нужен, Денис делает один раз вручную)
        ctx = p.chromium.launch_persistent_context(str(OUT.parent / "_browser_profile"), headless=False, channel="chrome",
                                                   args=["--start-fullscreen", "--autoplay-policy=no-user-gesture-required"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_selector("video", timeout=90000)
        page.evaluate("""([t]) => { const v = document.querySelector('video'); v.muted = false; v.currentTime = t; return v.play(); }""", [start])
        page.wait_for_function("document.querySelector('video') && document.querySelector('video').readyState >= 3", timeout=60000)
        page.evaluate("""() => { const v = document.querySelector('video'); (v.requestFullscreen ? v.requestFullscreen() : 0); }""")
        time.sleep(1.5)
        cl.start_record()
        time.sleep(dur + 0.5)
        res = cl.stop_record()
        page.evaluate("() => document.querySelector('video')?.pause()")
        ctx.close()
    src = Path(res.output_path)
    dst = OUT / f"{vid}_{int(start)}s.{src.suffix.lstrip('.')}"
    src.replace(dst)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True); ap.add_argument("--start", required=True)
    ap.add_argument("--dur", type=float, default=45); ap.add_argument("--id", required=True)
    a = ap.parse_args()
    src, cap = allowed(a.url)
    if not src:
        sys.exit("NO-GO: сайта нет в publishing/clip_sources.json (только легальные источники; новый добавляет Claude после проверки)")
    if not re.fullmatch(r"[a-z0-9_]{3,40}", a.id):
        sys.exit("NO-GO: id латиницей")
    dur = min(a.dur, cap)
    f = record(a.url, secs(a.start), dur, a.id)
    br = black_ratio(f)
    info = {"id": a.id, "file": str(f), "source": src["domain"], "url": a.url, "start": a.start, "dur": dur, "black_ratio": round(br, 2)}
    if br > 0.5:
        info["status"] = "BLOCKED_PROTECTED"  # сайт защищает видео от записи — не обходим, берём другой фильм
        f.unlink(missing_ok=True)
    else:
        info["status"] = "OK"
    (OUT / f"{a.id}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
