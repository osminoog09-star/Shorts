#!/usr/bin/env python3
"""
ClipForge — длинное видео -> пачка вертикальных клипов 9:16 с субтитрами.

Пайплайн:
  1. (опц.) скачать по ссылке (yt-dlp / Google Drive / Dropbox / прямая ссылка)
  2. транскрипция faster-whisper с таймкодами слов
  3. выбор лучших моментов: Claude API (если есть ANTHROPIC_API_KEY) или эвристика громкость+темп речи
  4. кроп 9:16: трекинг лица (OpenCV YuNet) или режим "blur" (кадр целиком поверх размытого фона)
  5. субтитры по словам (караоке-подсветка) + хук сверху первые секунды
  6. у каждого клипа свой стиль/зум — чтобы клипы не выглядели дубликатами

Пример:
  python clipforge.py video.mp4 --clips 8
  python clipforge.py "https://drive.google.com/file/d/..." --clips 10 --mode auto
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")

import numpy as np

OUT_W, OUT_H, FPS = 1080, 1920, 30


# ───────────────────────── utils ─────────────────────────

def log(msg: str) -> None:
    print(f"[clipforge] {msg}", flush=True)


def need(binary: str) -> None:
    if not shutil.which(binary):
        sys.exit(f"Не найден {binary}. Установи ffmpeg и добавь в PATH.")


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if not v:
        sys.exit("В файле нет видеодорожки.")
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = abs(int(sd["rotation"])) % 180
    if rot == 90:
        w, h = h, w
    has_audio = any(s["codec_type"] == "audio" for s in data["streams"])
    return {"w": w, "h": h, "duration": float(data["format"]["duration"]), "audio": has_audio}


def _direct(url: str, dst: Path) -> Path:
    subprocess.run(["curl", "-sSfL", "-o", str(dst), url], check=True)
    return dst


def download(url: str, workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?id=)([\w-]+)", url)
    if m:
        try:
            import gdown  # type: ignore
        except ImportError:
            sys.exit("Для Google Drive нужен gdown: pip install gdown")
        dst = workdir / "source.mp4"
        gdown.download(id=m.group(1), output=str(dst), quiet=True)
        if dst.exists():
            return dst
    if "dropbox.com" in url:
        u = re.sub(r"([?&])dl=0", r"\1dl=1", url)
        if "dl=1" not in u:
            u += ("&" if "?" in u else "?") + "dl=1"
        return _direct(u, workdir / "source.mp4")
    if re.search(r"\.(mp4|mov|mkv|webm)(\?|$)", url, re.I):
        return _direct(url, workdir / "source.mp4")
    try:
        import yt_dlp  # type: ignore
    except ImportError:
        sys.exit("Для ссылок нужен yt-dlp: pip install yt-dlp")
    opts = {
        "outtmpl": str(workdir / "source.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
    if not path.exists():
        cands = sorted(workdir.glob("source.*"))
        if not cands:
            sys.exit("Не удалось скачать видео.")
        path = cands[0]
    return path


# ───────────────────────── transcription ─────────────────────────

def transcribe(video: Path, model_size: str, lang: str | None, cache: Path) -> dict:
    if cache.exists():
        log(f"транскрипт из кэша: {cache.name}")
        return json.loads(cache.read_text(encoding="utf-8"))
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        sys.exit("Нужен faster-whisper: pip install faster-whisper")
    log(f"транскрибирую (whisper {model_size})… это самый долгий шаг")
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segs, info = model.transcribe(str(video), language=lang, word_timestamps=True, vad_filter=True)
    out = {"language": info.language, "segments": []}
    for s in segs:
        words = [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for w in (s.words or []) if w.word.strip()]
        if words:
            out["segments"].append({"start": words[0]["start"], "end": words[-1]["end"],
                                    "text": s.text.strip(), "words": words})
        print(f"\r  {s.end:7.1f}s / {info.duration:.0f}s", end="", flush=True)
    print()
    cache.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def split_sentences(segments: list[dict]) -> list[dict]:
    """Режем whisper-сегменты на предложения по пунктуации — для точных границ клипов."""
    sents, cur = [], []
    for seg in segments:
        for w in seg["words"]:
            cur.append(w)
            if re.search(r"[.!?…]$", w["w"]):
                sents.append(cur); cur = []
        if cur and len(cur) > 25:
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    return [{"start": s[0]["start"], "end": s[-1]["end"],
             "text": " ".join(w["w"] for w in s), "words": s} for s in sents]


# ───────────────────────── highlight picking ─────────────────────────

@dataclass
class Clip:
    start: float
    end: float
    hook: str
    title: str = ""
    description: str = ""
    hashtags: list[str] = field(default_factory=list)
    score: float = 0.0
    reason: str = ""


def audio_rms(video: Path, duration: float, step: float = 0.5) -> np.ndarray:
    sr = 8000
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True,
    ).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    n = int(sr * step)
    if len(a) < n:
        return np.zeros(max(1, int(duration / step)))
    a = a[: len(a) // n * n].reshape(-1, n)
    return np.sqrt((a ** 2).mean(axis=1) + 1e-9)


def pick_heuristic(sents, video, duration, n, lo, hi) -> list[Clip]:
    log("выбираю моменты эвристикой (громкость + темп речи + эмоции)")
    rms = audio_rms(video, duration)
    z = (rms - rms.mean()) / (rms.std() + 1e-6)
    target = (lo + hi) / 2
    cands = []
    for i in range(len(sents)):
        j = i
        while j < len(sents) and sents[j]["end"] - sents[i]["start"] < target:
            j += 1
        j = min(j, len(sents) - 1)
        s, e = sents[i]["start"], sents[j]["end"]
        d = e - s
        if d < lo or d > hi + 5:
            continue
        words = sum(len(x["words"]) for x in sents[i:j + 1])
        text = " ".join(x["text"] for x in sents[i:j + 1])
        loud = float(z[int(s / 0.5): int(e / 0.5) + 1].mean()) if len(z) else 0
        hook_loud = float(z[int(s / 0.5): int((s + 3) / 0.5) + 1].mean()) if len(z) else 0
        emo = text.count("!") + text.count("?")
        score = loud + 0.6 * hook_loud + 0.15 * (words / d) + 0.2 * min(emo, 5)
        cands.append((score, s, e, sents[i]["text"]))
    cands.sort(reverse=True)
    chosen: list[Clip] = []
    for score, s, e, first in cands:
        if any(not (e <= c.start or s >= c.end) for c in chosen):
            continue
        hook = " ".join(first.split()[:7]).rstrip(".,")
        chosen.append(Clip(s, e, hook=hook, title=hook, score=score, reason="heuristic"))
        if len(chosen) >= n:
            break
    return sorted(chosen, key=lambda c: c.start)


def pick_llm(sents, n, lo, hi, lang, niche) -> list[Clip] | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        log("anthropic не установлен — fallback на эвристику (pip install anthropic)")
        return None
    model = os.environ.get("CLIPFORGE_MODEL", "claude-sonnet-5-5")
    lines = "\n".join(f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in sents)
    if len(lines) > 400_000:
        lines = lines[:400_000]
    prompt = f"""Ты — топовый монтажёр вирусных Shorts/Reels/TikTok. Ниже транскрипт длинного видео с таймкодами предложений (секунды).

Выбери {n} лучших самостоятельных фрагментов для вертикальных клипов.
Требования:
- длительность каждого {lo}-{hi} сек; границы — строго по началу/концу предложений из транскрипта
- первые 3 секунды должны цеплять (сильное заявление, вопрос, конфликт, цифра, неожиданность)
- фрагмент понятен без контекста и заканчивается на смысловой точке (вывод, панчлайн)
- фрагменты не пересекаются; сортируй по виральности
- язык hook/title/description = язык видео ({lang})
{f'- ниша/контекст: {niche}' if niche else ''}

Ответь ТОЛЬКО JSON-массивом без пояснений:
[{{"start": 12.3, "end": 48.0, "hook": "текст-хук на экран, до 7 слов", "title": "заголовок поста до 70 символов",
"description": "1-2 предложения описания", "hashtags": ["#tag1","#tag2","#tag3"], "score": 0-100, "reason": "почему зайдёт"}}]

ТРАНСКРИПТ:
{lines}"""
    log(f"выбираю моменты через Claude ({model})")
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(model=model, max_tokens=4000,
                                     messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        arr = json.loads(re.search(r"\[.*\]", text, re.S).group(0))
    except Exception as ex:  # noqa: BLE001
        log(f"Claude не ответил корректно ({ex}) — fallback на эвристику")
        return None

    starts = [s["start"] for s in sents]
    ends = [s["end"] for s in sents]
    clips = []
    for it in arr:
        try:
            s = min(starts, key=lambda x: abs(x - float(it["start"])))
            e = min(ends, key=lambda x: abs(x - float(it["end"])))
        except (KeyError, ValueError, TypeError):
            continue
        if e - s < lo * 0.7 or e - s > hi * 1.3:
            continue
        if any(not (e <= c.start or s >= c.end) for c in clips):
            continue
        clips.append(Clip(s, e, hook=str(it.get("hook", ""))[:80], title=str(it.get("title", "")),
                          description=str(it.get("description", "")),
                          hashtags=[str(h) for h in it.get("hashtags", [])][:6],
                          score=float(it.get("score", 0) or 0), reason=str(it.get("reason", ""))))
    return clips[:n] or None


# ───────────────────────── framing (9:16) ─────────────────────────

def ffmpeg_reader(video: Path, start: float, dur: float, vf: str, fps: float):
    return subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(video),
         "-vf", f"{vf},fps={fps}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8,
    )


def scaled_size(w: int, h: int, max_h: int = 1080) -> tuple[int, int]:
    if h <= max_h:
        return w - w % 2, h - h % 2
    nw = int(round(w * max_h / h))
    return nw - nw % 2, max_h


YUNET = "face_detection_yunet_2023mar.onnx"
YUNET_URL = f"https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/{YUNET}"
CASCADE = "haarcascade_frontalface_default.xml"
CASCADE_URL = f"https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/{CASCADE}"
_detector_cache: dict = {}


def _fetch(name: str, url: str) -> Path | None:
    cands = [Path(__file__).with_name(name), Path.home() / ".clipforge" / name]
    for c in cands:
        if c.exists() and c.stat().st_size > 1000:
            return c
    try:
        import urllib.request
        dst = cands[1]
        dst.parent.mkdir(parents=True, exist_ok=True)
        log(f"качаю модель лица {name} (один раз)…")
        urllib.request.urlretrieve(url, dst)
        return dst
    except Exception as ex:  # noqa: BLE001
        log(f"не удалось скачать {name}: {ex}")
        return None


def make_detector(sw: int, sh: int):
    """Детектор лиц: YuNet (точный, OpenCV 4.8+), запасной — Haar. Возвращает f(bgr)->[(x,y,w,h)]."""
    import cv2  # type: ignore
    key = (sw, sh)
    if key in _detector_cache:
        return _detector_cache[key]
    fn = None
    if hasattr(cv2, "FaceDetectorYN"):
        m = _fetch(YUNET, YUNET_URL)
        if m:
            yn = cv2.FaceDetectorYN.create(str(m), "", (sw, sh), 0.7, 0.3, 50)

            def fn(img, yn=yn):
                _, faces = yn.detect(img)
                return [] if faces is None else [tuple(f[:4]) for f in faces]
    if fn is None and hasattr(cv2, "CascadeClassifier"):
        path = None
        if hasattr(cv2, "data"):
            pth = Path(cv2.data.haarcascades) / CASCADE
            path = pth if pth.exists() else None
        path = path or _fetch(CASCADE, CASCADE_URL)
        if path:
            hc = cv2.CascadeClassifier(str(path))

            def fn(img, hc=hc):
                g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
                return list(hc.detectMultiScale(g, scaleFactor=1.15, minNeighbors=5, minSize=(sh // 12, sh // 12)))
    if fn is None:
        log("детектор лиц недоступен — будет режим blur")
    _detector_cache[key] = fn
    return fn


def track_faces(video: Path, start: float, dur: float, w: int, h: int) -> tuple[np.ndarray | None, float]:
    """Возвращает массив x-центров лица (в долях ширины) с шагом 1/5 сек и долю кадров с лицом."""
    det_fps = 5.0
    sw = 480
    sh = int(round(h * sw / w)); sh -= sh % 2
    det = make_detector(sw, sh)
    if det is None:
        return None, 0.0
    p = ffmpeg_reader(video, start, dur, f"scale={sw}:{sh}", det_fps)
    fsz = sw * sh * 3
    xs, hits, prev = [], 0, None
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        faces = det(np.frombuffer(buf, np.uint8).reshape(sh, sw, 3))
        if len(faces):
            hits += 1

            def cost(f):
                cx = (f[0] + f[2] / 2) / sw
                size = f[2] * f[3] / (sw * sh)
                return -size * 4 + (abs(cx - prev) if prev is not None else 0)
            f = min(faces, key=cost)
            prev = (f[0] + f[2] / 2) / sw
            xs.append(prev)
        else:
            xs.append(np.nan)
    p.wait()
    if not xs:
        return None, 0.0
    arr = np.array(xs, dtype=float)
    ratio = hits / len(arr)
    if ratio == 0:
        return None, 0.0
    idx = np.arange(len(arr)); ok = ~np.isnan(arr)
    arr = np.interp(idx, idx[ok], arr[ok])
    k = 5
    pad = np.pad(arr, (k, k), mode="edge")
    med = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(len(arr))])
    out = med.copy()
    for i in range(1, len(out)):
        if abs(med[i] - out[i - 1]) < 0.035:
            out[i] = out[i - 1]
        else:
            out[i] = out[i - 1] + (med[i] - out[i - 1]) * 0.35
    return out, ratio


class Framer:
    """Превращает кадр исходника в кадр 1080x1920."""

    def __init__(self, mode: str, sw: int, sh: int, xs: np.ndarray | None, zoom: float):
        import cv2  # type: ignore
        self.cv2 = cv2
        self.mode, self.sw, self.sh, self.xs, self.zoom = mode, sw, sh, xs, zoom

    def __call__(self, frame: np.ndarray, t: float) -> np.ndarray:
        cv2 = self.cv2
        sw, sh = self.sw, self.sh
        if self.mode == "track":
            cw = min(sw, int(sh * OUT_W / OUT_H / self.zoom))
            ch = min(sh, int(cw * OUT_H / OUT_W))
            if self.xs is not None and len(self.xs):
                i = min(len(self.xs) - 1, int(t * 5.0))
                cx = self.xs[i] * sw
            else:
                cx = sw / 2
            x0 = int(np.clip(cx - cw / 2, 0, sw - cw))
            y0 = int((sh - ch) * 0.35)
            crop = frame[y0:y0 + ch, x0:x0 + cw]
            return cv2.resize(crop, (OUT_W, OUT_H), interpolation=cv2.INTER_LINEAR)
        bg_scale = max(OUT_W / sw, OUT_H / sh)
        small = cv2.resize(frame, (max(2, sw // 8), max(2, sh // 8)), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 6)
        bw, bh = int(sw * bg_scale), int(sh * bg_scale)
        bg = cv2.resize(small, (bw, bh), interpolation=cv2.INTER_LINEAR)
        x0, y0 = (bw - OUT_W) // 2, (bh - OUT_H) // 2
        canvas = (bg[y0:y0 + OUT_H, x0:x0 + OUT_W].astype(np.float32) * 0.45).astype(np.uint8)
        fw = int(OUT_W * self.zoom)
        fh = int(sh * fw / sw)
        if fh > OUT_H:
            fh = OUT_H; fw = int(sw * fh / sh)
        fg = cv2.resize(frame, (fw, fh), interpolation=cv2.INTER_AREA)
        cx0 = max(0, (fw - OUT_W) // 2)
        fg = fg[:, cx0:cx0 + OUT_W]
        fh, fw = fg.shape[:2]
        top = int((OUT_H - fh) * 0.42)
        left = (OUT_W - fw) // 2
        canvas[top:top + fh, left:left + fw] = fg
        return canvas


# ───────────────────────── captions (ASS) ─────────────────────────

# ASS цвет: &HAABBGGRR
STYLES = [
    {"name": "yellow", "primary": "&H00FFFFFF", "hi": "&H0000E5FF", "outline": "&H00000000", "border": 1, "size": 82},
    {"name": "green", "primary": "&H00FFFFFF", "hi": "&H0050FF39", "outline": "&H00000000", "border": 1, "size": 80},
    {"name": "cyan", "primary": "&H00FFFFFF", "hi": "&H00FFE600", "outline": "&H00101010", "border": 1, "size": 84},
    {"name": "pink", "primary": "&H00FFFFFF", "hi": "&H00B43CFF", "outline": "&H00000000", "border": 1, "size": 80},
    {"name": "boxed", "primary": "&H00FFFFFF", "hi": "&H0000D7FF", "outline": "&H64000000", "border": 3, "size": 76},
]


def ass_time(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def chunk_words(words: list[dict], max_words: int, max_chars: int) -> list[list[dict]]:
    chunks, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            text_len = len(" ".join(x["w"] for x in cur + [w]))
            if len(cur) >= max_words or text_len > max_chars or gap > 0.35 or re.search(r"[.!?,…:;]$", cur[-1]["w"]):
                chunks.append(cur); cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(words: list[dict], clip: Clip, style: dict, font: str, upper: bool, hook_secs: float) -> str:
    st = style
    margin_v = 560
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{st['size']},{st['primary']},{st['hi']},{st['outline']},&H96000000,-1,0,0,0,100,100,0,0,{st['border']},{8 if st['border'] == 1 else 14},3,2,70,70,{margin_v},1
Style: Hook,{font},64,&H00111111,&H00111111,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,90,90,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if clip.hook and hook_secs > 0:
        hook = ass_escape(clip.hook.upper() if upper else clip.hook)
        ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(hook_secs)},Hook,,0,0,0,,"
                  f"{{\\fad(120,200)\\fscx85\\fscy85\\t(0,140,\\fscx100\\fscy100)}}{hook}")
    chunks = chunk_words(words, max_words=3, max_chars=18)
    for ci, ch in enumerate(chunks):
        nxt = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else ch[-1]["end"] + 0.4
        chunk_end = min(nxt, ch[-1]["end"] + 0.6)
        for wi, w in enumerate(ch):
            ws = w["start"]
            we = ch[wi + 1]["start"] if wi + 1 < len(ch) else chunk_end
            if we <= ws:
                continue
            parts = []
            for k, x in enumerate(ch):
                t = ass_escape(x["w"].upper() if upper else x["w"])
                if k == wi:
                    parts.append(f"{{\\c{st['hi']}\\fscx108\\fscy108}}{t}{{\\c{st['primary']}\\fscx100\\fscy100}}")
                else:
                    parts.append(t)
            pop = "{\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
            ev.append(f"Dialogue: 0,{ass_time(ws)},{ass_time(we)},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    return header + "\n".join(ev) + "\n"


def ass_filter_path(p: Path) -> str:
    s = str(p.resolve()).replace("\\", "/")
    s = s.replace(":", r"\:").replace("'", r"\'")
    return s


# ───────────────────────── render ─────────────────────────

def render_clip(video: Path, meta: dict, clip: Clip, words: list[dict], out_path: Path,
                mode: str, style: dict, zoom: float, font: str, upper: bool, hook_secs: float) -> str:
    dur = clip.end - clip.start + 0.25
    sw, sh = scaled_size(meta["w"], meta["h"])

    used_mode = mode
    xs = None
    if mode in ("auto", "track"):
        xs, ratio = track_faces(video, clip.start, dur, meta["w"], meta["h"])
        if mode == "auto":
            used_mode = "track" if (xs is not None and ratio >= 0.4) else "blur"
    if meta["w"] / meta["h"] <= OUT_W / OUT_H + 0.01:
        used_mode = "blur"

    rel_words = [{"w": w["w"], "start": w["start"] - clip.start, "end": w["end"] - clip.start}
                 for w in words if w["start"] >= clip.start - 0.05 and w["end"] <= clip.end + 0.3]
    ass_path = out_path.with_suffix(".ass")
    ass_path.write_text(build_ass(rel_words, clip, style, font, upper, hook_secs), encoding="utf-8")

    framer = Framer(used_mode, sw, sh, xs, zoom)
    reader = ffmpeg_reader(video, clip.start, dur, f"scale={sw}:{sh}", FPS)
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-"]
    if meta["audio"]:
        cmd += ["-ss", f"{clip.start:.3f}", "-t", f"{dur:.3f}", "-i", str(video), "-map", "0:v", "-map", "1:a"]
    cmd += ["-vf", f"ass='{ass_filter_path(ass_path)}'",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"]
    if meta["audio"]:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    cmd += ["-shortest", "-movflags", "+faststart", str(out_path)]
    writer = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    fsz = sw * sh * 3
    i = 0
    try:
        while True:
            buf = reader.stdout.read(fsz)
            if len(buf) < fsz:
                break
            frame = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
            writer.stdin.write(framer(frame, i / FPS).tobytes())
            i += 1
    except BrokenPipeError:
        pass
    writer.stdin.close()
    reader.wait()
    err = writer.stderr.read().decode(errors="ignore")
    if writer.wait() != 0:
        raise RuntimeError(f"ffmpeg упал: {err[-800:]}")
    ass_path.unlink(missing_ok=True)
    return used_mode


# ───────────────────────── main ─────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="ClipForge: длинное видео -> вертикальные клипы с субтитрами")
    ap.add_argument("input", help="путь к видео или ссылка (YouTube/Twitch/Drive/Dropbox/прямая)")
    ap.add_argument("-o", "--out", default="clips_out", help="папка для результата")
    ap.add_argument("-n", "--clips", type=int, default=8, help="сколько клипов сделать")
    ap.add_argument("--min", dest="lo", type=float, default=20, help="мин. длительность клипа, сек")
    ap.add_argument("--max", dest="hi", type=float, default=55, help="макс. длительность клипа, сек")
    ap.add_argument("--mode", choices=["auto", "track", "blur"], default="auto")
    ap.add_argument("--whisper", default="small", help="модель whisper: tiny/base/small/medium/large-v3")
    ap.add_argument("--lang", default=None, help="язык речи (ru/en/...), по умолчанию автоопределение")
    ap.add_argument("--transcript", default=None, help="готовый transcript.json (пропустить whisper)")
    ap.add_argument("--no-llm", action="store_true", help="не звать Claude, только эвристика")
    ap.add_argument("--niche", default="", help="контекст для ИИ: 'подкаст про бизнес', 'стрим CS2' и т.п.")
    ap.add_argument("--font", default="Montserrat Black", help="шрифт субтитров (должен быть установлен)")
    ap.add_argument("--no-upper", action="store_true", help="не переводить субтитры в КАПС")
    ap.add_argument("--hook-secs", type=float, default=3.0, help="сколько секунд держать хук сверху (0 — выкл)")
    ap.add_argument("--seed", type=int, default=None, help="seed для стилей (повторяемость)")
    args = ap.parse_args()

    need("ffmpeg"); need("ffprobe")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    if re.match(r"https?://", args.input):
        log("качаю видео…")
        video = download(args.input, out / "_source")
    else:
        video = Path(args.input)
        if not video.exists():
            sys.exit(f"Файл не найден: {video}")

    meta = probe(video)
    log(f"исходник {meta['w']}x{meta['h']}, {meta['duration']:.0f} сек")

    if args.transcript:
        tr = json.loads(Path(args.transcript).read_text(encoding="utf-8"))
    else:
        tr = transcribe(video, args.whisper, args.lang, out / "transcript.json")
    sents = [s for s in split_sentences(tr["segments"]) if s["end"] <= meta["duration"]]
    words = [w for s in tr["segments"] for w in s["words"] if w["end"] <= meta["duration"]]
    if not words:
        sys.exit("В видео не нашлось речи — резать нечего.")

    clips = None if args.no_llm else pick_llm(sents, args.clips, args.lo, args.hi, tr.get("language", "auto"), args.niche)
    if not clips:
        clips = pick_heuristic(sents, video, meta["duration"], args.clips, args.lo, args.hi)
    if not clips:
        sys.exit("Не нашёл подходящих фрагментов. Попробуй --min 10 --max 90.")

    rng = random.Random(args.seed)
    styles = STYLES[:]; rng.shuffle(styles)
    results = []
    for k, c in enumerate(clips, 1):
        style = styles[(k - 1) % len(styles)]
        zoom = round(rng.uniform(1.0, 1.07), 3)
        name = f"clip_{k:02d}.mp4"
        log(f"[{k}/{len(clips)}] {c.start:.1f}–{c.end:.1f}s ({c.end - c.start:.0f}s) «{c.hook}»")
        used = render_clip(video, meta, c, words, out / name, args.mode, style, zoom,
                           args.font, not args.no_upper, args.hook_secs)
        results.append({"file": name, "start": round(c.start, 2), "end": round(c.end, 2),
                        "duration": round(c.end - c.start, 1), "hook": c.hook, "title": c.title,
                        "description": c.description, "hashtags": c.hashtags, "score": c.score,
                        "reason": c.reason, "mode": used, "style": style["name"], "zoom": zoom})

    (out / "clips.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"готово: {len(results)} клипов в {out.resolve()}")


if __name__ == "__main__":
    main()
