#!/usr/bin/env python3
"""Собрать ролик: ТЕЛО + утверждённая концовка M1lash (+ название фильма голосом на последнем кадре).

Одна команда вместо ручной склейки. Почему так (01.11.2026, Claude):
- Склейка `concat -c copy` тела и концовки ломается: у них разные параметры кодирования,
  на стыке остаются служебные пакеты AAC, звук уезжает на десятки мс, вылезают пики.
- Здесь всё декодируется и кодируется ОДИН раз через concat-фильтр. Звук концовки
  НЕ проходит ни через какие фильтры громкости — только приведение формата (48 кГц, стерео),
  поэтому звучит как утверждённый файл (AGENTS §4: не перемикшировать). Это проверяется в конце.
- Тело выравнивается по громкости в ДВА прохода (точно, без «дыхания»): −15 LUFS, пик ≤ −1,5 dBTP.

Пример:
  python3 tools/assemble_with_outro.py body.mp4 -o videos/<id>.mp4 --title media/tts/<id>/title.mp3
  python3 tools/assemble_with_outro.py long_body.mp4 -o out.mp4 --horizontal

Код возврата 0 — все проверки прошли (отчёт JSON рядом: <out>.qa.json). Иначе NO-GO с причиной.
"""
import argparse, json, math, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTRO = {"v": ROOT / "media/outro/m1lash_outro_v1_vertical.mp4",
         "h": ROOT / "media/outro/m1lash_outro_v1_horizontal.mp4"}
FPS, SR = 30, 48000
TARGET_I, TARGET_TP = -15.0, -1.5


def run(*a, capture=False):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *a], capture_output=True, text=True)
    if p.returncode:
        sys.exit("ffmpeg error:\n" + p.stderr[-1500:])
    return p.stderr if capture else None


def probe(f):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return v, a, float(j["format"]["duration"])


def loud(f, ss=None, t=None):
    args = ([] if ss is None else ["-ss", f"{ss:.3f}"]) + ([] if t is None else ["-t", f"{t:.3f}"])
    err = run(*args, "-i", str(f), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-", capture=True)
    tail = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    to = lambda m: float("-inf") if not m or m.group(1) == "-inf" else float(m.group(1))
    return to(i), to(p)


def measure_loudnorm(f):
    err = run("-i", str(f), "-vn", "-af", f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=11:print_format=json",
              "-f", "null", "-", capture=True)
    return json.loads(err[err.rfind("{"):err.rfind("}") + 1])


def pcm(f, ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-t", f"{t:.4f}", "-i", str(f), "-vn",
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    import array
    return array.array("h", raw)


def best_offset(a, b, max_lag):
    """Сдвиг b относительно a (в сэмплах) с минимальной разницей; возвращает (lag, разница в дБ к сигналу)."""
    n = min(len(a), len(b)) - 2 * max_lag
    step = 7
    sig = sum(a[i] * a[i] for i in range(max_lag, max_lag + n, step)) or 1
    best = None
    for lag in range(-max_lag, max_lag + 1, 4):
        e = 0
        for i in range(max_lag, max_lag + n, step):
            d = a[i] - b[i + lag]
            e += d * d
        if best is None or e < best[1]:
            best = (lag, e)
    lag0 = best[0]
    for lag in range(lag0 - 4, lag0 + 5):
        e = sum((a[i] - b[i + lag]) ** 2 for i in range(max_lag, max_lag + n, step))
        if e < best[1]:
            best = (lag, e)
    return best[0], 10 * math.log10(best[1] / sig + 1e-12)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("body", help="тело ролика (видео + звук), без концовки")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", help="mp3/wav с голосом Димы «Это был фильм… X» (кино-Shorts, AGENTS §8)")
    ap.add_argument("--horizontal", action="store_true", help="длинное 1920×1080")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--max-seconds", type=float, default=None, help="лимит длины (Shorts: 59)")
    a = ap.parse_args()

    outro = OUTRO["h" if a.horizontal else "v"]
    W, H = (1920, 1080) if a.horizontal else (1080, 1920)
    if a.max_seconds is None and not a.horizontal:
        a.max_seconds = 59.0
    body, out = Path(a.body), Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bv, ba, bdur = probe(body)
    if not bv:
        sys.exit("NO-GO: в теле нет видео")
    _, _, odur = probe(outro)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 1) тело: звук в 2 прохода → −16 LUFS / ≤ −1,5 dBTP (линейно, без компрессии)
        if ba:
            m = measure_loudnorm(body)
            body_af = (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=11:measured_I={m['input_i']}:"
                       f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                       f"offset={m['target_offset']}:linear=true,"
                       # запас под кодек AAC (+0,5…0,8 дБ к пику): лимитер на 4× частоте, с компенсацией задержки
                       f"aresample=192000,alimiter=limit=0.63:attack=1:release=50:level=false:latency=1,aresample={SR}")
            ain0 = "[0:a]"
        else:
            body_af, ain0 = "anull", None
        # 2) хвост: последний кадр концовки держится, пока звучит название
        inputs = ["-i", str(body), "-i", str(outro)]
        n = 2
        title_dur = 0.0
        if a.title:
            _, _, title_dur = probe(a.title)
            last = td / "last.png"
            run("-sseof", "-0.04", "-i", str(outro), "-frames:v", "1", "-update", "1", str(last))
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{title_dur + 0.35:.3f}", "-i", str(last),
                       "-i", str(a.title)]
            n = 3
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p,setpts=PTS-STARTPTS"
        af = f"aresample={SR},aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS"
        g = []
        if ain0:
            g.append(f"[0:v]{vf},trim=duration={bdur:.4f}[v0];[0:a]{body_af},{af},atrim=duration={bdur:.4f}[a0]")
        else:
            g.append(f"[0:v]{vf},trim=duration={bdur:.4f}[v0];anullsrc=r={SR}:cl=stereo,atrim=duration={bdur:.4f},{af}[a0]")
        # концовка: только формат, без фильтров громкости
        g.append(f"[1:v]{vf}[v1];[1:a]{af},atrim=duration={odur:.4f}[a1]")
        if n == 3:
            tdur = title_dur + 0.35
            g.append(f"[2:v]{vf},trim=duration={tdur:.4f}[v2];[3:a]loudnorm=I={TARGET_I}:TP={TARGET_TP},{af},apad,atrim=duration={tdur:.4f}[a2]")
            g.append("[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]")
        else:
            g.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
        run(*inputs, "-filter_complex", ";".join(g), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-movflags", "+faststart", str(out))

    # ---- проверки ----
    problems = []
    dec = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-xerror", "-i", str(out), "-f", "null", "-"],
                         capture_output=True, text=True)
    if dec.returncode or dec.stderr.strip():
        problems.append("ошибки полного декодирования")
    ov, oa, D = probe(out)
    vdur, adur = float(ov.get("duration", D)), float(oa.get("duration", D))
    if (ov["width"], ov["height"]) != (W, H):
        problems.append(f"размер {ov['width']}×{ov['height']}")
    if abs(vdur - adur) > 1.0 / FPS + 0.03:
        problems.append(f"видео и звук разной длины: {vdur:.3f} / {adur:.3f} с")
    expect = bdur + odur + (title_dur + 0.35 if a.title else 0)
    if abs(D - expect) > 0.15:
        problems.append(f"длина {D:.2f} с, ожидалось {expect:.2f} с")
    if a.max_seconds and D > a.max_seconds:
        problems.append(f"длиннее {a.max_seconds:.0f} с ({D:.1f})")
    bi, bp = loud(out, 0, bdur)
    oi, op = loud(out, bdur, odur)
    if bp > -1.0:
        problems.append(f"пик тела {bp:.1f} dBTP > −1")
    if abs(bi - oi) > 3.0:
        problems.append(f"тело {bi:.1f} LUFS vs концовка {oi:.1f} LUFS — скачок громкости > 3 LU")
    # концовка в готовом файле звучит как утверждённая, без сдвига
    seg = max(1.0, odur - 0.4)
    ref, got = pcm(outro, 0.2, seg), pcm(out, bdur + 0.2 - 0.05, seg + 0.1)
    lag, diff_db = best_offset(ref, got[int(0.05 * SR):], int(0.04 * SR)) if len(got) > SR else (0, 0.0)
    lag_ms = lag / SR * 1000
    if abs(lag_ms) > 1000.0 / FPS:
        problems.append(f"звук концовки сдвинут на {lag_ms:.0f} мс")
    if diff_db > -15:
        problems.append(f"звук концовки отличается от утверждённого ({diff_db:.1f} дБ к сигналу)")
    qa = {"out": str(out), "duration": round(D, 3), "video_s": round(vdur, 3), "audio_s": round(adur, 3),
          "body_s": round(bdur, 3), "outro_s": round(odur, 3), "title_s": round(title_dur, 3),
          "body_lufs": round(bi, 1), "body_tp": round(bp, 1), "outro_lufs": round(oi, 1), "outro_tp": round(op, 1),
          "outro_lag_ms": round(lag_ms, 1), "outro_diff_db": round(diff_db, 1),
          "decode_ok": not (dec.returncode or dec.stderr.strip()), "problems": problems}
    Path(str(out) + ".qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=1))
    if problems:
        sys.exit("NO-GO: " + "; ".join(problems))
    print("OK: склейка чистая. Дальше обязательно: check.py + look.py глазами + прослушать (m1lash-studio §2а).")


if __name__ == "__main__":
    main()
