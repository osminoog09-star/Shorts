#!/usr/bin/env python3
"""ПК Дениса: рендер и голос на своей видеокарте (решение Дениса 06.11.2026) — те же скрипты, что в GitHub Actions,
но локально: быстрее (NVIDIA 12 ГБ), без очереди Actions, личный образец голоса не покидает ПК.

Где считать решает настройка студии `compute` (сайт → Агенты → Управление студией):
  auto    — ПК, если студия в режиме «работает» и ПК онлайн; в игровом режиме/выключенной студии — GitHub Actions;
  pc      — только ПК;   actions — только GitHub Actions (как раньше).
Агенты зовут:  python scripts/pc/local_jobs.py where            → "pc" или "actions"
               python scripts/pc/local_jobs.py voice  --job jobs/voice/<id>.json --out <папка>
               python scripts/pc/local_jobs.py render --project mini --size 1080x1920 --fps 30 --out <mp4> [--root longform/smart-strike]
               python scripts/pc/local_jobs.py finish --body <mp4> --out <mp4> [--vertical]   (концовка v7 + check.py + look.py)
Личный образец голоса: C:\\M1lash\\private\\voice_ref (или M1LASH_VOICE_REF); если пусто — забирается из приватного Drive
(scripts/voice_private_io.py fetch, нужны те же переменные, что в Actions). В Git не попадает никогда.
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get("M1LASH_ROOT", r"C:\M1lash"))


def settings():
    try:
        return json.loads((REPO / "publishing" / "studio_settings.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def where():
    st = settings()
    c = st.get("compute", "auto")
    if c in ("pc", "actions"):
        return c
    return "pc" if st.get("mode", "on") == "on" else "actions"


def run(cmd, cwd=REPO, env=None):
    print("$", " ".join(map(str, cmd)), flush=True)
    r = subprocess.run(list(map(str, cmd)), cwd=cwd, env={**os.environ, **(env or {})})
    if r.returncode:
        sys.exit(f"FAIL ({r.returncode}): {cmd[0]} — смотри вывод выше")


def guard():
    if settings().get("mode", "on") == "game" and settings().get("compute", "auto") != "pc":
        sys.exit("NO-GO: игровой режим — видеокарта занята игрой; запусти в GitHub Actions (where → actions)")


def model_dir(repo_id):
    from huggingface_hub import snapshot_download  # кеш HF на ПК, скачивается один раз
    return snapshot_download(repo_id=repo_id)


def voice(a):
    guard()
    ref = Path(os.environ.get("M1LASH_VOICE_REF", ROOT / "private" / "voice_ref"))
    if not any(ref.glob("*")):
        ref.mkdir(parents=True, exist_ok=True)
        run([sys.executable, "scripts/voice_private_io.py", "fetch", "--dest", ref])
    run([sys.executable, "scripts/voice_private_io.py", "verify", "--dest", ref])
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "scripts/denis_voice_tts.py", "--job", a.job, "--assets", ref,
         "--model-dir", model_dir("Qwen/Qwen3-TTS-12Hz-1.7B-Base"), "--output", out],
        env={"M1LASH_TTS_DEVICE": os.environ.get("M1LASH_DEVICE", "cuda"), "HF_HUB_DISABLE_TELEMETRY": "1"})
    print("VOICE_OK", out / "manifest.json")


def render(a):
    guard()
    root = REPO / a.root
    workers = str(a.workers or max(2, (os.cpu_count() or 8) - 2))
    run(["node", "core/render/video.mjs", a.project, "--fps", a.fps, "--workers", workers, "--size", a.size, "--out", Path(a.out).resolve()], cwd=root)
    print("RENDER_OK", a.out)


def finish(a):
    run([sys.executable, "scripts/fetch_outro.py"]); run([sys.executable, "scripts/fetch_outro.py", "--verify-only"])
    args = [sys.executable, "tools/assemble_with_outro.py", a.body, "-o", a.out]
    if a.vertical:
        args += ["--max-seconds", "59"]
    run(args)
    qa = Path(a.out).with_suffix("")
    qa = qa.parent / (qa.name + "_qa"); qa.mkdir(exist_ok=True)
    plat = "youtube-shorts" if a.vertical else "youtube"
    r = subprocess.run([sys.executable, "skills/ext/ffmpeg-skill/scripts/check.py", a.out, "--platform", plat, "--json"], cwd=REPO, capture_output=True, text=True)
    (qa / "check.json").write_text(r.stdout, encoding="utf-8")
    run([sys.executable, "skills/ext/ffmpeg-skill/scripts/look.py", a.out, "--tiles", "4x3", "--width", "1600", "-o", qa / "look_sheet.png"])
    print("FINISH_OK", a.out, "QA:", qa)


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where")
    v = sub.add_parser("voice"); v.add_argument("--job", required=True); v.add_argument("--out", required=True)
    r = sub.add_parser("render"); r.add_argument("--project", required=True); r.add_argument("--out", required=True)
    r.add_argument("--size", default="1080x1920"); r.add_argument("--fps", default="30"); r.add_argument("--workers", default="")
    r.add_argument("--root", default="longform/smart-strike")
    f = sub.add_parser("finish"); f.add_argument("--body", required=True); f.add_argument("--out", required=True); f.add_argument("--vertical", action="store_true")
    a = ap.parse_args()
    if a.cmd == "where":
        print(where())
    else:
        {"voice": voice, "render": render, "finish": finish}[a.cmd](a)


if __name__ == "__main__":
    main()
