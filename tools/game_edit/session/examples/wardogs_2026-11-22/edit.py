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
                 "-map", "[v]", "-map", "1:a", "-map", "1:a", "-t", f"{d}",
                 "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(out)])
            return
        run(["ffmpeg", "-y", "-hide_banner", "-f", "lavfi", "-i", f"color=c=0x0b0b0f:s={Wd}x{Hd}:r={FPS}:d={d}",
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-map", "1:a", "-t", f"{d}",
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
    # 1-я дорожка: игра + голоса; 2-я: только голоса (по ней музыка приглушается под речь)
    # 22.11: громкость по замерам каждого файла (gains.py → gains.json); в OBS игра была −22 дБ, Discord −34 дБ
    G = json.load(open(W / "gains.json", encoding="utf-8")).get(f, dict(game=1.0, mic=1.4, discord=2.2))
    gg, gm, gd = G["game"], G["mic"], G["discord"]
    mixa = (f"[0:a:1]volume={gg}[g];[0:a:2]asplit=2[mc0][mcv];[0:a:3]asplit=2[dc0][dcv];"
            f"[mc0]volume={gm}[mc];[dc0]volume={gd}[dc];[g][mc][dc]amix=inputs=3:normalize=0,aresample=48000")
    voice = f"[mcv]volume={gm}[mv];[dcv]volume={gd}[dv];[mv][dv]amix=inputs=2:normalize=0,aresample=48000"
    if k == "m":
        post = ",volume=0"
    elif k == "s":
        post = f",asetrate={48000*sp:.0f},aresample=48000"
    elif k == "f":
        post = f",{atempo(sp)},volume=0.5"
    else:
        post = ""
    if s.get("freeze"): post += f",apad=pad_dur={s['freeze']},afade=t=out:st={(b-a)/sp:.3f}:d=0.4"
    af = mixa + post + "[ao];" + voice + post
    vin = []
    if s.get("va"):  # подкладка: картинка с другого места сессии (звук остаётся свой)
        fv, lv = locate(T(s["va"])); fv2, _ = locate(T(s["va"]) + (b - a) - 0.01)
        assert fv == fv2, f"подкладка {s['va']} пересекает границу файлов"
        vin = ["-ss", f"{lv:.3f}", "-t", f"{b-a:.3f}", "-i", fv]
        fc = f"[1:v:0]{vf}[vo];{af}[av]"
    else:
        fc = f"[0:v:0]{vf}[vo];{af}[av]"
    run(["ffmpeg", "-y", "-hide_banner", "-hwaccel", "cuda", "-ss", f"{la:.3f}", "-t", f"{b-a:.3f}", "-i", f, *vin,
         "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]", "-map", "[av]", "-t", f"{d:.3f}",
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
    fl.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0,loudnorm=I=-15:TP=-2:LRA=11,afade=t=in:d=0.2,aresample=192000,alimiter=limit=0.66:attack=0.3:release=80:level=disabled,aresample=48000[aout]")
    vf = f"subtitles=filename=caps.ass:fontsdir=fonts"
    body = out_dir / "body.mp4"
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[aout]",
         "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "19", "-b:v", "0", "-maxrate", "40M", "-bufsize", "80M",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-aac_coder", "twoloop", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(body)],
        cwd=out_dir)
    (out_dir / "edit_manifest.json").write_text(json.dumps({"total_s": round(total, 2), "segments": SEG,
        "music": sorted({m[3] for m in merged}), "sfx": "процедурные, game_edit/sfx.py"}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BODY", body, round(total, 2), flush=True)
    return body


# ===================== v3 (20.11, правки Дениса): субтитры на всю речь, ровная музыка с приглушением под голос, без SFX
FIX = [("миллаж", "Милаш"), ("Миллаж", "Милаш"), ("милаш", "Милаш"), ("Миллэш", "Милаш"), ("хандрэд", "Хандред"), ("Хандрэд", "Хандред"),
       ("хандред", "Хандред"), ("бист", "Бист"), ("Бизд", "Бист"), ("бизд", "Бист"), ("Хадрэд", "Хандред"), ("вертик", "вертик"), ("Тараса в", "Тарасов")]


def styles3(V):
    # name: (font, size, colour BGR, outline, align, marginV)
    if V:
        return {"low": ("Impact", 60, "&H00FFFFFF", 5, 8, 420), "big": ("Impact", 112, "&H0000D7FF", 7, 5, 0),
                "chap": ("Impact", 70, "&H0000D7FF", 5, 8, 330), "spd": ("Impact", 76, "&H00FFFFFF", 5, 9, 260),
                "card": ("Impact", 96, "&H00FFFFFF", 6, 5, 0), "top": ("Impact", 86, "&H0000D7FF", 6, 8, 230),
                "sm": ("Arial Black", 54, "&H00FFFFFF", 5, 2, 480), "sd": ("Arial Black", 54, "&H0060E8FF", 5, 2, 480)}
    return {"low": ("Impact", 56, "&H00FFFFFF", 5, 8, 120), "big": ("Impact", 116, "&H0000D7FF", 7, 5, 0),
            "chap": ("Impact", 66, "&H0000D7FF", 5, 7, 40), "spd": ("Impact", 76, "&H00FFFFFF", 5, 9, 40),
            "card": ("Impact", 104, "&H00FFFFFF", 6, 5, 0), "top": ("Impact", 80, "&H0000D7FF", 6, 8, 60),
            "sm": ("Arial Black", 46, "&H00FFFFFF", 4, 2, 52), "sd": ("Arial Black", 46, "&H0060E8FF", 4, 2, 52)}


def _wrap(txt, n=40):
    if len(txt) <= n: return txt
    words, a = txt.split(), ""
    for w in words:
        if len(a) + len(w) + 1 > len(txt) / 2 and a: break
        a = (a + " " + w).strip()
    return a + "\\N" + txt[len(a):].strip()


def build(name, SEG, V=False, music=None, mus_vol=0.11, top=None, only=None, autosubs=True):
    out_dir = W / name; parts_dir = out_dir / "parts"; parts_dir.mkdir(parents=True, exist_ok=True)
    Wd, Hd = (1080, 1920) if V else (1920, 1080)
    subs = json.load(open(W / "subs.json", encoding="utf-8")) if autosubs and (W / "subs.json").exists() else []
    parts, t, events, regions, levels = [], 0.0, [], [], []
    sig_file = parts_dir / "sig.json"
    old = json.loads(sig_file.read_text()) if sig_file.exists() else {}
    sig, last_trk = {}, music
    for i, s in enumerate(SEG):
        p = parts_dir / f"p{i:03d}.mkv"
        key = json.dumps({**{k: v for k, v in s.items() if k not in ("cap", "sfx", "mus", "trk", "frsfx", "ml")}, "_eng": 3}, sort_keys=True, ensure_ascii=False)
        sig[p.name] = key
        if not p.exists() or old.get(p.name) != key or (only and i in only):
            print("render", i, s.get("a"), s.get("b"), s["k"], flush=True); render(s, p, V)
        d = probe_dur(p); parts.append(p)
        a0, sp = (T(s["a"]) if s["k"] != "card" else 0), s.get("sp", 1.0)
        for c in s.get("cap", []):
            c0, c1, txt, st = c
            if autosubs and st in ("sub", "subbig"): continue  # ручные реплики заменены субтитрами на всю речь
            if isinstance(c0, str) and c0.startswith("@"):
                g = (hms(c0[1:]) - a0) / sp; c0, c1 = g, g + c1
            if c0 < d - 0.3:
                events.append((t + max(0, c0), t + min(c1, d), txt, st))
        if subs and s["k"] in ("n", "s"):
            b0 = T(s["b"])
            ph = [x for x in subs if a0 - 0.2 <= x[0] < b0 - 0.25]
            grp = []
            for x in ph:  # склейка кусков одной реплики
                if grp and grp[-1][2] == x[2] and x[0] - grp[-1][1] < 0.35 and len(grp[-1][3]) + len(x[3]) < 76:
                    grp[-1] = [grp[-1][0], x[1], x[2], grp[-1][3] + " " + x[3]]
                else:
                    grp.append(list(x))
            for j, (g0, g1, who, txt) in enumerate(grp):
                for a_, b_ in FIX: txt = txt.replace(a_, b_)
                r0 = max(0.0, (g0 - a0) / sp); r1 = min(d, (min(g1 + 0.35, b0) - a0) / sp)
                if r1 - r0 < 0.9: r1 = min(d, r0 + 0.9)
                events.append((t + r0, t + r1, _wrap(txt), "sm" if who == "m" else "sd"))
        trk = s.get("trk") or last_trk
        last_trk = trk
        regions.append([t, t + d, trk]); levels.append((t, t + d, s.get("ml", 1.0)))
        t += d
    sig_file.write_text(json.dumps(sig, ensure_ascii=False, indent=0))
    total = t
    print("total", round(total, 2), flush=True)
    lst = out_dir / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    cat = parts_dir / "concat.mkv"
    run(["ffmpeg", "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(lst), "-map", "0", "-c", "copy", str(cat)])
    fonts = out_dir / "fonts"; fonts.mkdir(exist_ok=True)
    shutil.copy(r"C:\Windows\Fonts\impact.ttf", fonts / "impact.ttf"); shutil.copy(r"C:\Windows\Fonts\ariblk.ttf", fonts / "ariblk.ttf")
    hdr = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {Wd}", f"PlayResY: {Hd}", "WrapStyle: 0", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"]
    for n, (fn, sz, col, ol, al, mv) in styles3(V).items():
        hdr.append(f"Style: {n},{fn},{sz},{col},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{ol},2,{al},60,60,{mv},204")
    hdr += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    if top: events.append((0.0, total, top, "top"))
    for a, b, txt, st in sorted(events):
        txt = txt.replace("\n", "\\N")
        if st in ("big", "card"): txt = r"{\fscx130\fscy130\t(0,120,\fscx100\fscy100)}" + txt
        elif st == "low": txt = r"{\fad(150,150)}" + txt.upper()
        elif st == "chap" and not V: txt = r"{\fad(150,250)\move(-400,40,60,40,0,220)}" + txt
        elif st in ("sm", "sd"): txt = r"{\fad(50,50)}" + txt
        hdr.append(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{txt}")
    (out_dir / "caps.ass").write_text("\n".join(hdr) + "\n", encoding="utf-8-sig")
    # музыка: одна непрерывная подложка, смена трека по сценам через кроссфейд 1,5 с, плавное приглушение под голос
    merged = []
    for a, b, trk in regions:
        if merged and merged[-1][2] == trk: merged[-1][1] = b
        else: merged.append([a, b, trk])
    inputs = ["-i", str(out_dir / "parts" / "concat.mkv")]; fl, mus_lbl, cursor = [], [], {}
    XF = 1.5
    for j, (a, b, trk) in enumerate(merged):
        p = trk if Path(trk).is_absolute() else MUSIC / trk
        tl = cursor.setdefault("_len_" + str(p), probe_dur(p))
        st0 = max(0.0, a - XF / 2); dur = (b - a) + XF
        c = cursor.get(str(p), 0.0)
        if c + dur > tl - 1: c = 0.0
        cursor[str(p)] = c + dur
        inputs += ["-stream_loop", "-1", "-ss", f"{c:.2f}", "-t", f"{dur:.2f}", "-i", str(p)]
        ms = int(st0 * 1000)
        fl.append(f"[{j+1}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d={XF},afade=t=out:st={dur-XF:.2f}:d={XF},"
                  f"adelay={ms}|{ms}[mu{j}]")
        mus_lbl.append(f"[mu{j}]")
    lv = [(a, b, m) for a, b, m in levels if abs(m - 1.0) > 1e-3]
    lvl = "1" + "".join(f"+{m-1:.2f}*clip(min(t-{a:.2f},{b:.2f}-t)/0.3,0,1)" for a, b, m in lv)
    fl.append(f"{''.join(mus_lbl)}amix=inputs={len(mus_lbl)}:normalize=0:dropout_transition=0,atrim=0:{total:.3f},volume={mus_vol:.3f},volume=eval=frame:volume='{lvl}'[mus]")
    fl.append("[0:a:1]aresample=48000,aformat=channel_layouts=stereo,volume=2.0[vsc]")
    fl.append("[mus][vsc]sidechaincompress=threshold=0.012:ratio=10:attack=100:release=1000:knee=6[musd]")
    # без адаптивного loudnorm: он вытягивал тихие места и музыка становилась громкой; громкость выравнивает finish линейно
    fl.append("[0:a:0][musd]amix=inputs=2:normalize=0:dropout_transition=0,afade=t=in:d=0.2,"
              "aresample=192000,alimiter=limit=0.66:attack=0.3:release=80:level=disabled,aresample=48000[aout]")
    body = out_dir / "body.mp4"
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[aout]",
         "-vf", "subtitles=filename=caps.ass:fontsdir=fonts", "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "19", "-b:v", "0",
         "-maxrate", "40M", "-bufsize", "80M", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-aac_coder", "twoloop",
         "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(body)], cwd=out_dir)
    (out_dir / "edit_manifest.json").write_text(json.dumps({"total_s": round(total, 2), "music": sorted({m[2] for m in merged}),
        "subs": len([e for e in events if e[3] in ("sm", "sd")]), "sfx": "нет"}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BODY", body, round(total, 2), flush=True)
    return body
