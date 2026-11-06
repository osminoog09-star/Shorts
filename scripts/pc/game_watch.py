#!/usr/bin/env python3
"""ПК Дениса: игровой отдел — следит за папкой записей OBS и бесплатно (локально, без LLM-токенов)
готовит запись для агентов (решение Дениса 06.11.2026: прохождения на M1lash, запись OBS → папка на ПК).

Для каждой новой записи (размер не меняется 60 с):
  1. remux .mkv → .mp4 без перекодирования;
  2. тишина/паузы  → silences.json   (ffmpeg silencedetect);
  3. громкие всплески → highlights.json (ebur128 momentary, топ пиков + слова из транскрипта);
  4. транскрипт речи Дениса → transcript.json (faster-whisper на видеокарте, если установлен);
  5. задача руководителю игрового отдела → agents/inbox/<время>-m1lash-gaming-lead.json (мост отдаст агенту).

Папка — настройки студии gaming.folder (сайт) или M1LASH_GAMES, по умолчанию C:\\M1lash\\Игры.
Запуск: python scripts/pc/game_watch.py   (автозапуск ставит setup.ps1)   |  --once  — один проход
"""
import argparse, json, os, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXT = {".mkv", ".mp4", ".mov", ".flv"}
HYPE = re.compile(r"\b(а{3,}|вау|ого|офиг|бля|хаха|ахах|да ладно|не может быть|красава|победа|умер|сдох|босс)\w*", re.I)


def settings():
    subprocess.run(["git", "-C", str(REPO), "pull", "-q", "--rebase", "--autostash"], capture_output=True)  # режим с сайта
    try:
        return json.loads((REPO / "publishing" / "studio_settings.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def folder():
    g = settings().get("gaming") or {}
    return Path(os.environ.get("M1LASH_GAMES") or g.get("folder") or r"C:\M1lash\Игры")


def ff(*args, capture=True):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=capture, text=True, errors="replace")


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def silences(p):
    err = ff("-i", str(p), "-vn", "-af", "silencedetect=noise=-38dB:d=2", "-f", "null", "-").stderr
    out, cur = [], None
    for kind, val in re.findall(r"silence_(start|end): (-?[\d.]+)", err):  # события по порядку
        if kind == "start":
            cur = max(0.0, float(val))
        else:
            out.append({"start": round(cur if cur is not None else 0.0, 2), "end": round(float(val), 2)})
            cur = None
    return [x for x in out if x["end"] > x["start"]]


def loud_peaks(p, top=12):
    err = ff("-i", str(p), "-vn", "-af", "ebur128=peak=none", "-f", "null", "-").stderr
    pts = [(float(t), float(m)) for t, m in re.findall(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+)", err)]
    if not pts:
        return []
    base = sorted(m for _, m in pts)[len(pts) // 2]
    peaks, last = [], -999.0
    for t, m in sorted(pts, key=lambda x: -x[1]):
        if m - base < 8 or any(abs(t - q["t"]) < 30 for q in peaks):
            continue
        peaks.append({"t": round(t, 1), "lufs_m": m, "over_median_db": round(m - base, 1)})
        if len(peaks) >= top:
            break
    return sorted(peaks, key=lambda x: x["t"])


def transcribe(p):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = WhisperModel(os.environ.get("M1LASH_WHISPER", "large-v3"), device=os.environ.get("M1LASH_DEVICE", "cuda"), compute_type="float16")
        segs, _ = model.transcribe(str(p), language="ru", vad_filter=True)
        segs = list(segs)
    except Exception as e:  # нет модели/видеокарты — без транскрипта, остальное готовим
        print("whisper недоступен:", str(e)[:120], flush=True)
        return None
    return [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]


def prepare(src):
    out = src.parent / "_m1lash" / src.stem
    if (out / "done.json").exists():
        return None
    out.mkdir(parents=True, exist_ok=True)
    mp4 = src if src.suffix.lower() == ".mp4" else out / (src.stem + ".mp4")
    if mp4 != src and not mp4.exists():
        ff("-i", str(src), "-map", "0", "-c", "copy", "-movflags", "+faststart", str(mp4))
    dur = duration(mp4)
    sil = silences(mp4)
    peaks = loud_peaks(mp4)
    tr = transcribe(mp4)
    words = [{"t": s["start"], "text": s["text"]} for s in (tr or []) if HYPE.search(s["text"])]
    for name, data in (("silences", sil), ("highlights", {"loud": peaks, "speech": words}), ("transcript", tr)):
        if data is not None:
            (out / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    info = {"source": str(src), "mp4": str(mp4), "duration_min": round(dur / 60, 1),
            "silence_min": round(sum(x["end"] - x["start"] for x in sil) / 60, 1),
            "loud_peaks": len(peaks), "hype_phrases": len(words), "transcript": tr is not None, "prep_dir": str(out)}
    (out / "done.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mid = t.replace("-", "").replace(":", "").replace("T", "").replace("Z", "") + "-m1lash-gaming-lead"
    inbox = REPO / "agents" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / f"{mid}.json").write_text(json.dumps({
        "id": mid, "t": t, "from": "m1lash-studio-director", "to": "m1lash-gaming-lead", "status": "new",
        "text": (f"Новая запись игры: {src.name} ({info['duration_min']} мин, паузы {info['silence_min']} мин, "
                 f"{len(peaks)} громких пиков, {len(words)} эмоциональных фраз). Подготовка: {out}. "
                 "Реши серия/гайд/Shorts и раздай задачи по своей инструкции."),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return info


def stable(p, wait=60):
    s1 = p.stat().st_size; time.sleep(wait)
    return p.exists() and p.stat().st_size == s1 and s1 > 10_000_000


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--once", action="store_true"); ap.add_argument("--wait", type=int, default=60)
    a = ap.parse_args()
    while True:
        d = folder()
        st = settings()
        if d.exists() and (st.get("gaming") or {}).get("enabled", True) and st.get("mode", "on") == "on":  # off/game — копим, не грузим видеокарту
            for p in sorted(d.iterdir()):
                if p.suffix.lower() in EXT and p.is_file() and not (p.parent / "_m1lash" / p.stem / "done.json").exists():
                    if stable(p, a.wait):
                        print(datetime.now().strftime("%H:%M"), "готовлю", p.name, flush=True)
                        print(json.dumps(prepare(p), ensure_ascii=False), flush=True)
        if a.once:
            break
        time.sleep(120)


if __name__ == "__main__":
    sys.exit(main())
