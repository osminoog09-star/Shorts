#!/usr/bin/env python3
"""Сборщик кино-Shorts M1lash «от записи до приватной заливки» (решение Дениса 31.10).

Запускается в GitHub Actions (`movie-short.yml`), потому что нужен интернет (Whisper, edge-tts).
Исходник (запись экрана Дениса) скачивается во временную папку и НИКУДА не сохраняется — в репо
попадает только готовый Short `videos/<id>.mp4` + паспорт. AGENTS §8, §12.

Шаги: обрезка черных полей → вырезка [start, end] → вертикаль 1080×1920 с ведением кадра по лицам
(OpenCV) → распознавание речи (faster-whisper) → кинетические субтитры (2–3 слова) → финал Димы
(edge-tts + живая подача; последние слова — название фильма голосом) + фирменная карточка M1lash →
громкость −16 LUFS → проверка (полный decode, контрольные кадры, длительность, название фильма не
светится в публичных полях) → паспорт без даты.
"""
import argparse
import asyncio
import json
import math
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
W, H, FPS = 1080, 1920, 30
FONT = "DejaVu Sans"


def sh(*a, capture=False):
    r = subprocess.run(list(a), check=True, text=True, capture_output=capture)
    return r.stdout if capture else None


def ff(*a):
    sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a)


def dur(p):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p), capture=True).strip())


def tsec(s):
    s = str(s).strip()
    if ":" in s:
        parts = [float(x) for x in s.split(":")]
        return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))
    return float(s)


def cropdetect(src, start, length):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(start), "-t", str(min(length, 20)), "-i", str(src),
                          "-vf", "cropdetect=24:2:0", "-f", "null", "-"], capture_output=True, text=True).stderr
    crops = re.findall(r"crop=(\d+:\d+:\d+:\d+)", out)
    if not crops:
        return None
    best = max(set(crops), key=crops.count)
    w, h, x, y = map(int, best.split(":"))
    return (w, h, x, y) if w > 100 and h > 100 else None


def face_track(clip):
    """Центр кадра по x (0..1) для каждого кадра: крупнейшее лицо, сглажено."""
    import cv2  # noqa: PLC0415
    cap = cv2.VideoCapture(str(clip))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    fps = cap.get(cv2.CAP_PROP_FPS) or FPS
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    prof = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    step = max(1, int(fps / 4))
    pts, i = {}, 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        if i % step == 0:
            ok, fr = cap.retrieve()
            if ok:
                g = cv2.cvtColor(cv2.resize(fr, (640, int(640 * fr.shape[0] / fr.shape[1]))), cv2.COLOR_BGR2GRAY)
                faces = list(casc.detectMultiScale(g, 1.15, 5, minSize=(30, 30))) + list(prof.detectMultiScale(g, 1.15, 5, minSize=(30, 30)))
                if faces:
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    pts[i] = (x + w / 2) / g.shape[1]
        i += 1
    cap.release()
    n = max(n, i)
    keys = sorted(pts)
    xs = []
    for k in range(n):
        if not keys:
            xs.append(0.5)
            continue
        prev = max([q for q in keys if q <= k], default=keys[0])
        nxt = min([q for q in keys if q >= k], default=keys[-1])
        if prev == nxt:
            xs.append(pts[prev])
        else:
            a = (k - prev) / (nxt - prev)
            xs.append(pts[prev] * (1 - a) + pts[nxt] * a)
    # сглаживание (камера не дёргается): скользящее среднее ~1 с + ограничение скорости
    win = int(fps)
    sm = [sum(xs[max(0, j - win):j + win + 1]) / len(xs[max(0, j - win):j + win + 1]) for j in range(n)]
    out, cur = [], sm[0]
    for v in sm:
        cur += max(-0.012, min(0.012, v - cur))
        out.append(cur)
    return out, fps


def vertical(clip, dst):
    """1080×1920 без полей: масштаб по высоте, окно ведётся за лицом."""
    import cv2  # noqa: PLC0415
    xs, fps = face_track(clip)
    cap = cv2.VideoCapture(str(clip))
    p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", str(dst)], stdin=subprocess.PIPE)
    k = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        h0, w0 = fr.shape[:2]
        sw = int(round(w0 * H / h0))
        fr = cv2.resize(fr, (sw, H), interpolation=cv2.INTER_LANCZOS4)
        cx = xs[min(k, len(xs) - 1)] * sw
        x0 = int(max(0, min(sw - W, cx - W / 2))) if sw > W else 0
        crop = fr[:, x0:x0 + W]
        if crop.shape[1] < W:  # исходник уже уже 9:16 — растягиваем без полей
            crop = cv2.resize(fr, (W, H))
        p.stdin.write(crop.tobytes())
        k += 1
    cap.release()
    p.stdin.close()
    p.wait()
    return fps


def transcribe(wav, lang):
    from faster_whisper import WhisperModel  # noqa: PLC0415
    import os  # noqa: PLC0415
    # облако: small/cpu; ПК Дениса (12 ГБ NVIDIA): M1LASH_WHISPER=large-v3, M1LASH_DEVICE=cuda
    dev = os.environ.get("M1LASH_DEVICE", "cpu")
    model = WhisperModel(os.environ.get("M1LASH_WHISPER", "small"), device=dev,
                         compute_type="float16" if dev == "cuda" else "int8")
    segs, _ = model.transcribe(str(wav), language=lang, word_timestamps=True, vad_filter=True,
                               condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if t:
                words.append((w.start, w.end, t))
    return words


def ass_time(t):
    t = max(0.0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass(words, path, top_text=None, top_until=3.0):
    """Кинетические субтитры: 2–3 слова, пауза > 0.6 с или знак — новый блок; появление с подскоком."""
    groups, cur = [], []
    for st, en, w in words:
        if cur and (len(cur) >= 3 or st - cur[-1][1] > 0.6 or re.search(r"[.!?…,]$", cur[-1][2])):
            groups.append(cur)
            cur = []
        cur.append((st, en, w))
    if cur:
        groups.append(cur)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FONT},84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,3,2,80,80,560,1
Style: Top,{FONT},62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,3,18,0,8,80,80,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for i, g in enumerate(groups):
        st = g[0][0]
        en = max(g[-1][1], st + 0.45)
        if i + 1 < len(groups):
            en = min(en + 0.25, groups[i + 1][0][0])
        txt = " ".join(w for _, _, w in g).upper().replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Sub,,0,0,0,,"
                     f"{{\\fscx88\\fscy88\\t(0,90,\\fscx104\\fscy104)\\t(90,160,\\fscx100\\fscy100)}}{txt}")
    if top_text:
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(top_until)},Top,,0,0,0,,{{\\fad(150,250)}}{top_text}")
    Path(path).write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return len(groups)


async def outro_voice(text, out_mp3):
    import tts_job  # noqa: PLC0415
    import voice_humanize  # noqa: PLC0415
    meta = Path(str(out_mp3) + ".json")

    async def _one(t, v, r, p, m, j):
        await tts_job.one(t, v, r, p, m, j)
    for k in range(6):
        try:
            await voice_humanize.humanized(_one, text, "ru-RU-DmitryNeural", "+8%", "+0Hz", out_mp3, meta, {})
            return
        except Exception:  # noqa: BLE001
            if k == 5:
                raise
            await asyncio.sleep(5 + k * 5)


def card(png):
    """Фирменная карточка M1lash: логотип + «Подпишись»."""
    from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415
    img = Image.new("RGB", (W, H), (14, 12, 22))
    d = ImageDraw.Draw(img)
    for y in range(H):  # мягкий градиент
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(14 + 30 * k), int(12 + 4 * k), int(22 + 34 * k)))
    logo = Image.open(ROOT / "site/studio/i/wordmark.png").convert("RGBA")
    lw = 820
    logo = logo.resize((lw, int(logo.height * lw / logo.width)))
    img.paste(logo, ((W - lw) // 2, 640), logo)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 78)
    except OSError:
        f = ImageFont.load_default()
    btn = (W // 2 - 330, 1000, W // 2 + 330, 1150)
    d.rounded_rectangle(btn, radius=75, fill=(240, 71, 154))
    d.text((W // 2, 1075), "ПОДПИШИСЬ", font=f, fill="white", anchor="mm")
    img.save(png)


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFKC", s).casefold().replace("ё", "е") if c.isalnum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--start", default="0")
    ap.add_argument("--end", default="")
    ap.add_argument("--title", required=True)
    ap.add_argument("--film", required=True, help="название фильма — звучит голосом только в самом конце")
    ap.add_argument("--lang", default="ru")
    ap.add_argument("--request", default="", help="@ник для «По заявке»")
    ap.add_argument("--question", default="А ты бы как поступил?")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9_]{3,60}", a.id):
        sys.exit("id: только латиница/цифры/_")
    if norm(a.film) and norm(a.film) in norm(a.title):
        sys.exit("NO-GO: название фильма в заголовке (AGENTS §8)")
    import os  # noqa: PLC0415
    work = Path(os.environ.get("M1LASH_WORK", "/tmp/ms")) / a.id
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    src = Path(a.src)
    total = dur(src)
    start = tsec(a.start)
    end = tsec(a.end) if a.end else total
    # Финал (AGENTS §4, решение Дениса 31.10): готовая фирменная концовка media/outro/… + для кино
    # одна фраза Димы с названием фильма — последние слова ролика (§8). Вопрос зрителям — в описании/закрепе.
    std = ROOT / "media/outro/m1lash_outro_v1_vertical.mp4"
    std_d = dur(std)
    vo = work / "name.mp3"
    asyncio.run(outro_voice(f"Это был фильм… {a.film}.", vo))
    vd = dur(vo)
    length = min(end - start, 52.0, 59.3 - std_d - (vd + 0.4))
    if length < 8:
        sys.exit("Слишком короткий фрагмент")
    c = cropdetect(src, start, length)
    vf = [f"crop={c[0]}:{c[1]}:{c[2]}:{c[3]}"] if c else []
    clip = work / "clip.mp4"
    ff("-ss", f"{start:.3f}", "-t", f"{length:.3f}", "-i", str(src), "-vf", ",".join(vf + [f"fps={FPS}"]) if vf else f"fps={FPS}",
       "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(clip))
    vert = work / "vert.mp4"
    vertical(clip, vert)
    wav = work / "a.wav"
    ff("-i", str(clip), "-vn", "-ac", "1", "-ar", "16000", str(wav))
    words = transcribe(wav, a.lang)
    if a.lang != "ru" and not a.request:
        sys.exit("NO-GO: не русский звук разрешён только для заявок зрителей (AGENTS §8)")
    top = f"ПО ЗАЯВКЕ {a.request.upper()}" if a.request else None
    subs = work / "s.ass"
    n_sub = ass(words, subs, top)
    body = work / "body.mp4"
    ff("-i", str(vert), "-i", str(clip), "-map", "0:v", "-map", "1:a", "-vf", f"ass={subs}",
       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(body))
    # финал: стандартная концовка M1lash → её последний кадр держится, Дима называет фильм
    last = work / "last.png"
    ff("-sseof", "-0.05", "-i", str(std), "-frames:v", "1", "-update", "1", str(last))
    tail = work / "tail.mp4"
    ff("-loop", "1", "-t", f"{vd + 0.4:.2f}", "-i", str(last), "-i", str(vo), "-filter_complex",
       f"[0]scale={W}:{H},fps={FPS},setsar=1[v];[1]loudnorm=I=-16:TP=-1.5,apad[au]", "-map", "[v]", "-map", "[au]",
       "-t", f"{vd + 0.4:.2f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(tail))
    stdn = work / "std.mp4"
    ff("-i", str(std), "-vf", f"scale={W}:{H},fps={FPS},setsar=1", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(stdn))
    outro = work / "outro.mp4"
    (work / "o.txt").write_text(f"file '{stdn}'\nfile '{tail}'\n")
    ff("-f", "concat", "-safe", "0", "-i", str(work / "o.txt"), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(outro))
    lst = work / "l.txt"
    bodyn = work / "body2.mp4"
    ff("-i", str(body), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(bodyn))
    lst.write_text(f"file '{bodyn}'\nfile '{outro}'\n")
    out = ROOT / "videos" / f"{a.id}.mp4"
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out))
    # ---- проверка §12 ----
    err = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "null", "-"], capture_output=True, text=True).stderr.strip()
    probe = json.loads(sh("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(out), capture=True))
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    D = float(probe["format"]["duration"])
    qa = {"decode_errors": err[:500], "width": v["width"], "height": v["height"], "duration": round(D, 2),
          "subtitle_blocks": n_sub, "words": len(words), "lang": a.lang, "outro_voice_s": round(vd, 2),
          "size_mb": round(out.stat().st_size / 1e6, 1)}
    qdir = ROOT / "reports" / "qa" / a.id
    qdir.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate([0.5, D * 0.2, D * 0.4, D * 0.6, D * 0.8, D - 1.0]):
        ff("-ss", f"{t:.2f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=360:-2", str(qdir / f"f{i}.jpg"))
    (qdir / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1), encoding="utf-8")
    problems = []
    if err:
        problems.append("ошибки декодирования")
    if (v["width"], v["height"]) != (W, H):
        problems.append("не 1080×1920")
    if D > 60.5:
        problems.append("длиннее 60 с")
    if len(words) < 5:
        problems.append("речь не распознана (субтитров почти нет)")
    if qa["size_mb"] > 95:
        problems.append("файл > 95 МБ")
    qa["problems"] = problems
    (qdir / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False))
    if problems:
        sys.exit("NO-GO: " + "; ".join(problems))
    # ---- паспорт без даты (AGENTS §6) ----
    import hashlib  # noqa: PLC0415
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    title = (f"По заявке {a.request} 💀 " if a.request else "") + a.title
    title = title if title.endswith("#shorts") else title + " #shorts"
    tags = ["кино", "фильм", "сцена из фильма", "угадай фильм", "кино shorts", "лучшие сцены", "M1lash", "shorts", "фильмы", "кинофакты"]
    NCS = "Музыка в концовке:\nSong: Laeko - DONT WANNA KNOW!!!\nMusic provided by NoCopyrightSounds\nFree Download/Stream: http://ncs.io/dontwannaknow\nWatch: https://ncs.lnk.to/dontwannaknowAT/youtube"
    desc = f"{a.question} Пиши в комментариях 👇\n\n{NCS}\n\n#shorts #кино #фильм #угадайфильм #сценаизфильма #m1lash #кинолюбитель"
    for s in [title, desc, *tags]:
        if norm(a.film) and norm(a.film) in norm(s):
            sys.exit("NO-GO: название фильма в публичных полях (AGENTS §8)")
    manifest = {"channel": "ru", "source": {"type": "repo", "path": f"videos/{a.id}.mp4", "sha256": sha},
                "metadata": {"type": "short", "title": title[:100], "description": desc, "tags": tags,
                             "category_id": "1", "made_for_kids": False, "contains_synthetic_media": True}}
    (ROOT / "publishing" / "queue" / f"{a.id}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qp = ROOT / "publishing" / "queue.json"
    q = json.loads(qp.read_text(encoding="utf-8"))
    q["items"] = [i for i in q["items"] if i.get("id") != a.id] + [{
        "id": a.id, "kind": "short", "author": "movie-short.yml", "status": "review", "slot": None, "style": "S6-D25",
        "mp4": f"videos/{a.id}.mp4", "publish_md": None, "title": title[:100],
        "note": f"Собрано автоматически из записи Дениса. Закреп: {('@' + a.request.lstrip('@') + ', сделали по твоей заявке! ') if a.request else ''}{a.question}"}]
    qp.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("READY", out, sha)


if __name__ == "__main__":
    main()
