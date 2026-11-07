"""Монтаж записи 2026-11-07 22:08 → тело ролика 1920x1080 60fps (без концовки).
Сегменты исходника → скорость/слоумо/зум/стоп-кадр → склейка → титры (ASS) + свои SFX + музыка (MacLeod, CC BY).
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

SRC = r"C:\Users\osmin\Videos\Gameplay\Recordings\Game_2026-11-07_22-08-28.mkv"
W = Path(r"C:\M1lash\Работа\game_2026-11-07")
PARTS = W / "parts"; PARTS.mkdir(exist_ok=True)
TMP = Path(os.environ.get("ASCII_TMP", r"C:\Users\osmin\AppData\Local\Temp\claude\581b418b047542e5\79e740ae-6c98-4830-a685-97c79e8f8d1b\scratchpad\game"))
TMP.mkdir(parents=True, exist_ok=True)
MUSIC = Path(r"C:\M1lash\Shorts\media\music")
FPS = 60

# kind: n=обычно, f=быстро (звук ускорен/приглушён), m=быстро без звука (музыка), s=слоумо с низким звуком
# опции: zoom=удар-зум в начале, zin=плавный наезд, gray=ч/б, freeze=сек стоп-кадра в конце (ч/б)
SEG = [
    # --- ХУК
    dict(a=148.6, b=151.5, k="n", cap=[(0.2, 2.9, "Новый костюм. Новый я.", "low")]),
    dict(a=151.5, b=152.4, k="s", sp=0.35, zin=1, cap=[(0.0, 2.5, "…и новый труп", "big")], sfx=[(0.0, "riser", -8)]),
    dict(a=152.4, b=153.0, k="n", freeze=1.6, sfx=[(0.0, "boom", -3), (0.25, "fail", -6)]),
    dict(a=0.0, b=0.0, k="card", dur=1.6, cap=[(0.0, 1.6, "3 минуты назад…", "card")], sfx=[(0.0, "scratch", -4), (0.3, "whoosh", -6)]),
    # --- ГЛАВА 1
    dict(a=0.0, b=18.0, k="n", cap=[(0.2, 3.6, "ГЛАВА 1 · ОХОТА НА КОНТЕЙНЕРАХ", "chap"), (9.6, 12.0, "цель обнаружена", "low")], sfx=[(0.0, "whoosh", -6)]),
    dict(a=48.0, b=66.0, k="n", cap=[(9.0, 12.5, "он на контейнере. я тоже на контейнере", "low")]),
    dict(a=66.0, b=84.0, k="f", sp=2, cap=[(0.0, 9.0, "×2", "spd"), (1.0, 8.0, "ждём, когда высунется…", "low")]),
    dict(a=84.0, b=89.4, k="n", sfx=[(3.0, "riser", -10)]),
    dict(a=89.4, b=90.8, k="s", sp=0.4, zoom=1, cap=[(0.1, 3.5, "МИНУС ОДИН", "big")], sfx=[(0.0, "boom", -3), (0.2, "ding", -8)]),
    dict(a=90.8, b=97.0, k="n"),
    dict(a=98.0, b=112.0, k="m", sp=4, cap=[(0.0, 3.5, "×4", "spd"), (0.0, 3.5, "переодеваюсь в шмот покойника. ему уже не надо", "low")], sfx=[(0.0, "whoosh", -6)], mus=1),
    dict(a=113.0, b=146.0, k="f", sp=2, cap=[(0.0, 16.5, "×2", "spd")]),
    dict(a=146.0, b=151.5, k="n", cap=[(0.3, 5.5, "снова инвентарь. что может пойти не так?", "low")]),
    dict(a=151.5, b=152.4, k="s", sp=0.35, zin=1, cap=[(0.0, 2.6, "ВОТ ЧТО.", "big")], sfx=[(0.0, "scratch", -5)]),
    dict(a=152.4, b=156.0, k="n", cap=[(0.6, 3.6, "RonaldoRM, с 5 метров. Без шансов.", "low")], sfx=[(0.0, "boom", -4)], freeze=1.4, frsfx="fail"),
    dict(a=156.0, b=200.0, k="m", sp=8, gray=1, cap=[(0.0, 5.5, "×8", "spd"), (0.0, 3.0, "лежу, жду, что поднимут…", "low"), (3.0, 5.5, "…никто не пришёл", "low")], mus=1),
    # --- ГЛАВА 2
    dict(a=220.0, b=336.0, k="m", sp=10, cap=[(0.0, 11.6, "×10", "spd"), (0.3, 4.0, "ГЛАВА 2 · ТАКСИ НА ВОЙНУ", "chap"), (5.0, 11.0, "вертолёт. музыка. минута тишины в эфире", "low")], sfx=[(0.0, "whoosh", -6)], mus=1),
    dict(a=336.0, b=344.4, k="n", cap=[(1.5, 6.0, "прыжок веры", "low")]),
    dict(a=344.4, b=345.6, k="s", sp=0.5, zoom=1, sfx=[(0.0, "boom", -2)], cap=[(0.2, 4.4, "приземление на 5 баллов. из 100", "big")]),
    dict(a=345.6, b=351.0, k="n"),
    dict(a=351.0, b=400.0, k="f", sp=3, mus=1, cap=[(0.0, 16.3, "×3", "spd"), (1.0, 6.0, "ноги целы? вроде да. бежим к вышке", "low")]),
    dict(a=400.0, b=412.0, k="f", sp=2, mus=1, cap=[(0.0, 6.0, "×2", "spd")]),
    # --- ГЛАВА 3 (речь — без ускорения)
    dict(a=412.0, b=425.3, k="n", cap=[(0.2, 3.6, "ГЛАВА 3 · ВЫШКА", "chap"),
                                        (9.8, 13.3, "Ты чё, конченый, что ли, дядя?!", "sub")]),
    dict(a=429.8, b=436.0, k="n", sfx=[(0.0, "whoosh", -10)], cap=[(0.4, 4.2, "…ты, блять, игрок, блять", "sub")]),
    dict(a=436.0, b=450.0, k="f", sp=3, cap=[(0.0, 4.7, "×3", "spd"), (0.3, 4.7, "тишина. осмысление.", "low")]),
    dict(a=450.0, b=452.6, k="n", cap=[(0.4, 2.6, "Я тут, блять, вышку…", "sub")]),
    dict(a=452.6, b=455.4, k="n", zoom=1, cap=[(0.0, 2.8, "…КРОВЬЮ СВОЕГО ПРИКРЫВАЛ", "subbig")], sfx=[(0.0, "boom", -6)]),
    dict(a=455.4, b=467.0, k="f", sp=2, cap=[(0.0, 5.8, "×2", "spd")]),
    dict(a=467.0, b=480.0, k="m", sp=4, cap=[(0.0, 3.2, "×4", "spd"), (0.0, 3.2, "лутаю, пока никто не видит", "low")], mus=1),
    # --- ГЛАВА 4
    dict(a=480.0, b=540.0, k="m", sp=4, cap=[(0.0, 15.0, "×4", "spd"), (0.2, 3.6, "ГЛАВА 4 · ЗАВОД", "chap")], mus=1),
    dict(a=540.0, b=568.0, k="n", cap=[(19.0, 23.0, "стреляю по вышке. вышка не сдаётся", "low")]),
    dict(a=568.0, b=598.0, k="f", sp=3, mus=1, cap=[(0.0, 10.0, "×3", "spd")]),
    dict(a=598.0, b=605.6, k="n", sfx=[(5.0, "riser", -10)]),
    dict(a=605.6, b=606.8, k="s", sp=0.4, zoom=1, sfx=[(0.0, "boom", -3), (0.3, "ding", -8)], cap=[(0.1, 3.0, "ТУК-ТУК", "big")]),
    dict(a=606.8, b=609.0, k="n"),
    dict(a=609.0, b=624.0, k="m", sp=4, cap=[(0.0, 3.7, "×4", "spd"), (0.0, 3.7, "FREZYYY, спасибо за подарки", "low")], mus=1),
    dict(a=624.0, b=646.0, k="n", cap=[(5.0, 9.0, "дымовая. значит, тут кто-то есть", "low")]),
    dict(a=646.0, b=692.0, k="f", sp=3, mus=1, cap=[(0.0, 15.3, "×3", "spd")]),
    dict(a=692.0, b=697.8, k="n", cap=[(0.5, 5.6, "спокойно иду по кустам…", "low")]),
    dict(a=697.8, b=698.6, k="s", sp=0.35, zin=1, sfx=[(0.0, "scratch", -5)], cap=[(0.0, 2.3, "…ну конечно", "big")]),
    dict(a=698.6, b=702.0, k="n", sfx=[(0.0, "boom", -4)], freeze=2.0, frsfx="fail"),
    dict(a=0.0, b=0.0, k="card", dur=3.2, cap=[(0.0, 3.2, "Итог: 2 захода, 2 раза лёг.\nВышку — прикрыли.", "card")], sfx=[(0.0, "whoosh", -6)]),
]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode:
        print(" ".join(map(str, cmd))[:600]); print(r.stderr[-2500:]); sys.exit(1)
    return r

def atempo(sp):
    out, s = [], sp
    while s > 2.0: out.append("atempo=2.0"); s /= 2.0
    while s < 0.5: out.append("atempo=0.5"); s /= 0.5
    out.append(f"atempo={s:.4f}")
    return ",".join(out)

def seg_dur(s):
    if s["k"] == "card": return s["dur"]
    sp = s.get("sp", 1.0)
    return (s["b"] - s["a"]) / sp + s.get("freeze", 0)

def render(i, s):
    out = PARTS / f"p{i:03d}.mkv"
    d = seg_dur(s)
    if s["k"] == "card":  # тёмная карточка с размытием последнего/следующего кадра не нужна — чёрный фон + текст позже
        run(["ffmpeg", "-y", "-hide_banner", "-f", "lavfi", "-i", f"color=c=0x0b0b0f:s=1920x1080:r={FPS}:d={d}",
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d}",
             "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(out)])
        return out
    sp = s.get("sp", 1.0); a, b = s["a"], s["b"]
    v = [f"setpts=(PTS-STARTPTS)/{sp}", "scale=1920:1080:flags=lanczos", f"fps={FPS}"]
    if s.get("zoom"):   # удар-зум: 1.22 → 1.0 за 0.5 с
        v.append("scale=w='trunc(1920*(1+0.22*max(0,1-t/0.5))/2)*2':h='trunc(1080*(1+0.22*max(0,1-t/0.5))/2)*2':eval=frame,crop=1920:1080")
    if s.get("zin"):    # медленный наезд до 1.18
        v.append(f"scale=w='trunc(1920*(1+0.18*min(1,t/{d:.3f}))/2)*2':h='trunc(1080*(1+0.18*min(1,t/{d:.3f}))/2)*2':eval=frame,crop=1920:1080")
    if s.get("gray"): v.append("hue=s=0")
    if s.get("freeze"):
        v.append(f"tpad=stop_mode=clone:stop_duration={s['freeze']}")
    vf = ",".join(v)
    if s.get("freeze"):  # стоп-кадр в ч/б и с виньеткой
        fr0 = (b - a) / sp
        vf += f",hue=s=0:enable='gte(t,{fr0:.3f})',vignette=angle=PI/4:enable='gte(t,{fr0:.3f})'"
    k = s["k"]
    if k == "m":
        af = f"volume=0,atrim=0:{d:.3f}"
        ain = ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        amap = "1:a"
    else:
        if k == "s":    # слоумо: низкий «замедленный» звук
            af = f"aresample=48000,asetrate={48000*sp:.0f},aresample=48000"
        elif k == "f":
            af = f"aresample=48000,{atempo(sp)},volume=0.55"
        else:
            af = "aresample=48000"
        if s.get("freeze"): af += f",apad=pad_dur={s['freeze']},afade=t=out:st={(b-a)/sp:.3f}:d=0.4"
        ain, amap = [], "0:1"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-hwaccel", "cuda", "-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", SRC, *ain,
           "-map", "0:v:0", "-map", amap, "-vf", vf, "-af", af, "-t", f"{d:.3f}",
           "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(out)]
    run(cmd)
    return out

def probe_dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    return float(r.stdout.strip())

STY = {  # name: (font, size, primary, outline, align, marginV, bold)
    "low":    ("Impact", 64, "&H00FFFFFF", 5, 2, 70),
    "big":    ("Impact", 120, "&H0000D7FF", 7, 5, 0),
    "chap":   ("Impact", 70, "&H0000D7FF", 5, 7, 50),
    "spd":    ("Impact", 80, "&H00FFFFFF", 5, 9, 50),
    "sub":    ("Impact", 76, "&H00FFFFFF", 6, 2, 110),
    "subbig": ("Impact", 96, "&H003C3CFF", 7, 2, 110),
    "card":   ("Impact", 110, "&H00FFFFFF", 6, 5, 0),
}

def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def main():
    only = set(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else None
    parts, t, events, sfx, mus = [], 0.0, [], [], []
    for i, s in enumerate(SEG):
        p = PARTS / f"p{i:03d}.mkv"
        if only is None or i in only or not p.exists():
            print("render", i, s["a"], s["b"], s["k"], flush=True); render(i, s)
        d = probe_dur(p); parts.append(p)
        for c0, c1, txt, st in s.get("cap", []):
            events.append((t + c0, t + min(c1, d), txt, st))
        for c0, name, g in s.get("sfx", []):
            sfx.append((t + c0, name, g))
        if s.get("frsfx"):
            sfx.append((t + (s["b"] - s["a"]) / s.get("sp", 1) + 0.05, s["frsfx"], -6))
        if s.get("mus"):
            mus.append((t, t + d))
        t += d
    total = t
    print("total", round(total, 2))
    # склейка
    lst = TMP / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    cat = PARTS / "concat.mkv"
    run(["ffmpeg", "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)])
    # титры
    fonts = TMP / "fonts"; fonts.mkdir(exist_ok=True)
    shutil.copy(r"C:\Windows\Fonts\impact.ttf", fonts / "impact.ttf")
    hdr = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 0", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"]
    for n, (f, sz, col, ol, al, mv) in STY.items():
        hdr.append(f"Style: {n},{f},{sz},{col},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,{ol},3,{al},60,60,{mv},204")
    hdr += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for a, b, txt, st in events:
        txt = txt.replace("\n", "\\N")
        if st in ("big", "subbig", "card"):   # «впрыгивание»
            txt = r"{\fscx140\fscy140\t(0,120,\fscx100\fscy100)}" + txt
        elif st == "low":
            txt = r"{\fad(120,120)}" + txt.upper()
        elif st == "chap":
            txt = r"{\fad(150,250)\move(-400,50,60,50,0,220)}" + txt
        hdr.append(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{txt}")
    ass = TMP / "caps.ass"; ass.write_text("\n".join(hdr) + "\n", encoding="utf-8-sig")
    # звук: исходник + SFX + музыка в «быстрых» беззвучных кусках
    inputs = ["-i", str(cat)]
    fl, mixin = [], ["[0:a]"]
    for j, (st, name, g) in enumerate(sfx):
        inputs += ["-i", str(W / "sfx" / f"{name}.wav")]
        ms = int(st * 1000)
        fl.append(f"[{j+1}:a]volume={g}dB,adelay={ms}|{ms}[s{j}]"); mixin.append(f"[s{j}]")
    mi = len(sfx) + 1
    inputs += ["-stream_loop", "-1", "-i", str(MUSIC / "Volatile Reaction.mp3")]
    # громкость музыки: только в беззвучных ускоренных кусках, плавно
    vol = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in mus) or "0"
    fl.append(f"[{mi}:a]aresample=48000,atrim=0:{total:.3f},volume='0.22*min(1,({vol}))':eval=frame,lowpass=f=9000[mus]")
    mixin.append("[mus]")
    fl.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0,alimiter=limit=0.89[aout]")
    vf = f"subtitles=filename='{ass.as_posix().replace(':', chr(92)+':')}':fontsdir='{fonts.as_posix().replace(':', chr(92)+':')}'"
    body = W / "body.mp4"
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[aout]",
         "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "19", "-b:v", "0", "-maxrate", "40M", "-bufsize", "80M",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(body)])
    (W / "edit_manifest.json").write_text(json.dumps({"source": SRC, "total_s": round(total, 2),
        "segments": [{k: v for k, v in s.items() if k in ("a", "b", "k", "sp", "freeze", "dur")} for s in SEG],
        "music": "Kevin MacLeod — Volatile Reaction (CC BY 4.0)", "sfx": "процедурные, sfx.py"}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BODY", body, round(total, 2))

if __name__ == "__main__":
    main()
