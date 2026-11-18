"""Движок монтажа записи 2026-11-17 (Wardogs). Наследник Shorts/tools/game_edit/build.py:
- несколько исходных файлов (глобальное время сессии, src.locate);
- свой звук: Game + Mic×1.4 + Discord×2.2 (а не готовый Mix, где друзья тихие);
- горизонталь 1920x1080 и вертикаль 1080x1920 (центр-кроп) для Shorts;
- титры: время можно задавать глобально ("@0:28:45.8") — переводится в время ролика.
kind: n обычно, f быстро (звук ускорен/тише), m быстро без звука (музыка), s слоумо, card карточка.
"""
import json, shutil, subprocess, sys
from pathlib import Path
from src import W, locate, hms

FPS = 60
SFX = Path(r"C:\M1lash\Работа\game_2026-11-07\sfx")
MUSIC = Path(r"C:\M1lash\Shorts\media\music")


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", cwd=cwd)
    if r.returncode:
        print(" ".join(map(str, cmd))[:800]); print(r.stderr[-3000:]); sys.exit(1)
    return r


def T(x):
    return hms(x) if isinstance(x, str) else float(x)


def atempo(sp):
    out, s = [], sp
    while s > 2.0: out.append("atempo=2.0"); s /= 2.0
    while s < 0.5: out.append("atempo=0.5"); s /= 0.5
    out.append(f"atempo={s:.4f}")
    return ",".join(out)


def seg_dur(s):
    if s["k"] == "card": return s["dur"]
    return (T(s["b"]) - T(s["a"])) / s.get("sp", 1.0) + s.get("freeze", 0)


def render(s, out, V):
    Wd, Hd = (1080, 1920) if V else (1920, 1080)
    d = seg_dur(s)
    if s["k"] == "card":
        if s.get("bg"):  # размытый затемнённый кадр из игры вместо чёрного фона
            f, la = locate(T(s["bg"]))
            crop = "crop=810:1440:875:0" if V else "crop=2304:1296:128:72"
            run(["ffmpeg", "-y", "-hide_banner", "-ss", f"{la:.3f}", "-i", f, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-filter_complex", f"[0:v]trim=end_frame=1,{crop},scale={Wd}:{Hd},gblur=sigma=18,eq=brightness=-0.18,"
                 f"loop=loop=-1:size=1,fps={FPS},setpts=N/{FPS}/TB,trim=duration={d}[v]",
                 "-map", "[v]", "-map", "1:a", "-t", f"{d}",
                 "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(out)])
            return
        run(["ffmpeg", "-y", "-hide_banner", "-f", "lavfi", "-i", f"color=c=0x0b0b0f:s={Wd}x{Hd}:r={FPS}:d={d}",
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d}",
             "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(out)])
        return
    a, b = T(s["a"]), T(s["b"]); sp = s.get("sp", 1.0)
    f, la = locate(a); f2, _ = locate(b - 0.01)
    assert f == f2, f"сегмент {s['a']}–{s['b']} пересекает границу файлов"
    v = [f"setpts=(PTS-STARTPTS)/{sp}"]
    if V:
        cx = s.get("cx", 0.5)  # центр кропа по горизонтали (доля ширины)
        v.append(f"crop=810:1440:{int(2560*cx-405)}:0")
    else:  # игра рендерится 2304x1440 (16:10) с чёрными полосами — режем до 16:9 без полос
        v.append("crop=2304:1296:128:72")
    v += [f"scale={Wd}:{Hd}:flags=lanczos", f"fps={FPS}"]
    if s.get("zoom"):
        v.append(f"scale=w='trunc({Wd}*(1+0.22*max(0,1-t/0.5))/2)*2':h='trunc({Hd}*(1+0.22*max(0,1-t/0.5))/2)*2':eval=frame,crop={Wd}:{Hd}")
    if s.get("zin"):
        v.append(f"scale=w='trunc({Wd}*(1+0.18*min(1,t/{d:.3f}))/2)*2':h='trunc({Hd}*(1+0.18*min(1,t/{d:.3f}))/2)*2':eval=frame,crop={Wd}:{Hd}")
    if s.get("gray"): v.append("hue=s=0")
    if s.get("bright"): v.append(f"eq=brightness={s['bright']}:gamma=1.25")
    if s.get("freeze"): v.append(f"tpad=stop_mode=clone:stop_duration={s['freeze']}")
    vf = ",".join(v)
    if s.get("freeze"):
        fr0 = (b - a) / sp
        vf += f",hue=s=0:enable='gte(t,{fr0:.3f})',vignette=angle=PI/4:enable='gte(t,{fr0:.3f})'"
    k = s["k"]
    mixa = "[0:a:1]volume=1.0[g];[0:a:2]volume=1.4[mc];[0:a:3]volume=2.2[dc];[g][mc][dc]amix=inputs=3:normalize=0,aresample=48000"
    if k == "m":
        af = f"{mixa},volume=0"
    elif k == "s":
        af = f"{mixa},asetrate={48000*sp:.0f},aresample=48000"
    elif k == "f":
        af = f"{mixa},{atempo(sp)},volume=0.5"
    else:
        af = mixa
    if s.get("freeze"): af += f",apad=pad_dur={s['freeze']},afade=t=out:st={(b-a)/sp:.3f}:d=0.4"
    fc = f"[0:v:0]{vf}[vo];{af}[ao]"
    run(["ffmpeg", "-y", "-hide_banner", "-hwaccel", "cuda", "-ss", f"{la:.3f}", "-t", f"{b-a:.3f}", "-i", f,
         "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", "-t", f"{d:.3f}",
         "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(out)])


def probe_dur(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout.strip())


def styles(V):
    if V:  # 1080x1920
        return {"low": ("Impact", 64, "&H00FFFFFF", 5, 2, 560), "big": ("Impact", 118, "&H0000D7FF", 7, 5, 0),
                "chap": ("Impact", 74, "&H0000D7FF", 5, 8, 260), "spd": ("Impact", 80, "&H00FFFFFF", 5, 9, 260),
                "sub": ("Impact", 72, "&H00FFFFFF", 6, 2, 520), "subbig": ("Impact", 92, "&H003C3CFF", 7, 2, 520),
                "card": ("Impact", 100, "&H00FFFFFF", 6, 5, 0), "top": ("Impact", 86, "&H0000D7FF", 6, 8, 230)}
    return {"low": ("Impact", 64, "&H00FFFFFF", 5, 2, 70), "big": ("Impact", 120, "&H0000D7FF", 7, 5, 0),
            "chap": ("Impact", 70, "&H0000D7FF", 5, 7, 50), "spd": ("Impact", 80, "&H00FFFFFF", 5, 9, 50),
            "sub": ("Impact", 70, "&H00FFFFFF", 6, 2, 100), "subbig": ("Impact", 92, "&H003C3CFF", 7, 2, 100),
            "card": ("Impact", 110, "&H00FFFFFF", 6, 5, 0), "top": ("Impact", 80, "&H0000D7FF", 6, 8, 60)}


def ts(x):
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"


def build(name, SEG, V=False, music="Volatile Reaction.mp3", mus_vol=0.2, top=None, only=None):
    out_dir = W / name; parts_dir = out_dir / "parts"; parts_dir.mkdir(parents=True, exist_ok=True)
    Wd, Hd = (1080, 1920) if V else (1920, 1080)
    parts, t, events, sfx, mus = [], 0.0, [], [], []
    sig_file = parts_dir / "sig.json"
    old = json.loads(sig_file.read_text()) if sig_file.exists() else {}
    sig = {}
    for i, s in enumerate(SEG):
        p = parts_dir / f"p{i:03d}.mkv"
        key = json.dumps({**{k: v for k, v in s.items() if k not in ("cap", "sfx", "mus", "trk")}, "_eng": 2}, sort_keys=True, ensure_ascii=False)
        sig[p.name] = key
        if not p.exists() or old.get(p.name) != key or (only and i in only):
            print("render", i, s.get("a"), s.get("b"), s["k"], flush=True); render(s, p, V)
        d = probe_dur(p); parts.append(p)
        a0, sp = (T(s["a"]) if s["k"] != "card" else 0), s.get("sp", 1.0)
        for c in s.get("cap", []):
            c0, c1, txt, st = c
            if isinstance(c0, str) and c0.startswith("@"):  # глобальное время + длительность
                g = (hms(c0[1:]) - a0) / sp; c0, c1 = g, g + c1
            if c0 < d - 0.3:  # титр вне укороченного сегмента — выбросить
                events.append((t + max(0, c0), t + min(c1, d), txt, st))
        for c0, nm, g in s.get("sfx", []):
            if isinstance(c0, str) and c0.startswith("@"): c0 = (hms(c0[1:]) - a0) / sp
            sfx.append((t + c0, nm, g))
        if s.get("freeze"):
            sfx.append((t + (T(s["b"]) - a0) / sp + 0.05, s.get("frsfx", "fail"), -6))
        if s["k"] in ("m", "f") or s.get("mus"):
            w = 1.0 if s["k"] == "m" else (0.35 if s["k"] == "f" else s.get("mus"))
            mus.append((t, t + d, w, s.get("trk", music)))
        t += d
    sig_file.write_text(json.dumps(sig, ensure_ascii=False, indent=0))
    total = t
    print("total", round(total, 2), flush=True)
    lst = out_dir / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    cat = parts_dir / "concat.mkv"
    run(["ffmpeg", "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)])
    fonts = out_dir / "fonts"; fonts.mkdir(exist_ok=True)
    shutil.copy(r"C:\Windows\Fonts\impact.ttf", fonts / "impact.ttf")
    hdr = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {Wd}", f"PlayResY: {Hd}", "WrapStyle: 0", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"]
    for n, (fn, sz, col, ol, al, mv) in styles(V).items():
        hdr.append(f"Style: {n},{fn},{sz},{col},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,{ol},3,{al},50,50,{mv},204")
    hdr += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    if top:  # постоянная плашка сверху (Shorts)
        events.append((0.0, total, top, "top"))
    for a, b, txt, st in events:
        txt = txt.replace("\n", "\\N")
        if st in ("big", "subbig", "card"):
            txt = r"{\fscx140\fscy140\t(0,120,\fscx100\fscy100)}" + txt
        elif st == "low":
            txt = r"{\fad(120,120)}" + txt.upper()
        elif st == "chap" and not V:
            txt = r"{\fad(150,250)\move(-400,50,60,50,0,220)}" + txt
        elif st == "sub":
            txt = r"{\fad(60,60)}" + txt
        hdr.append(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{txt}")
    ass = out_dir / "caps.ass"; ass.write_text("\n".join(hdr) + "\n", encoding="utf-8-sig")
    inputs = ["-i", str(cat)]; fl, mixin = [], ["[0:a]"]
    for j, (st, nm, g) in enumerate(sfx):
        inputs += ["-i", str(SFX / f"{nm}.wav")]; ms = int(st * 1000)
        fl.append(f"[{j+1}:a]volume={g}dB,adelay={ms}|{ms}[s{j}]"); mixin.append(f"[s{j}]")
    # музыка: соседние интервалы с одним треком сливаются; трек играет дальше с места, где остановился
    merged = []
    for a, b, w, trk in mus:
        if merged and merged[-1][3] == trk and abs(merged[-1][1] - a) < 0.05 and merged[-1][2] == w:
            merged[-1][1] = b
        else:
            merged.append([a, b, w, trk])
    cursor, nin = {}, len(sfx) + 1
    for j, (a, b, w, trk) in enumerate(merged):
        p = trk if Path(trk).is_absolute() else MUSIC / trk
        tl = cursor.setdefault("_len_" + str(p), probe_dur(p))
        c = cursor.get(str(p), 0.0)
        if c + (b - a) > tl - 1: c = 0.0
        cursor[str(p)] = c + (b - a)
        inputs += ["-ss", f"{c:.2f}", "-t", f"{b-a+0.6:.2f}", "-i", str(p)]
        ms = int(a * 1000); fo = max(0.0, b - a - 0.5)
        fl.append(f"[{nin}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.25,afade=t=out:st={fo:.2f}:d=0.6,"
                  f"volume={mus_vol*w:.3f},adelay={ms}|{ms}[mu{j}]")
        mixin.append(f"[mu{j}]"); nin += 1
    fl.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,alimiter=limit=0.75:level=disabled,aresample=48000[aout]")
    vf = f"subtitles=filename=caps.ass:fontsdir=fonts"
    body = out_dir / "body.mp4"
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[aout]",
         "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "19", "-b:v", "0", "-maxrate", "40M", "-bufsize", "80M",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(body)],
        cwd=out_dir)
    (out_dir / "edit_manifest.json").write_text(json.dumps({"total_s": round(total, 2), "segments": SEG,
        "music": sorted({m[3] for m in merged}), "sfx": "процедурные, game_edit/sfx.py"}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BODY", body, round(total, 2), flush=True)
    return body
