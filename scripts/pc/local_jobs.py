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


MODELS = Path(os.environ.get("M1LASH_MODELS", ROOT / "models"))  # веса с pc-model-weights.yml (HF из песочницы Claude недоступен)


def model_dir(repo_id):
    local = MODELS / repo_id.split("/")[-1]
    if (local / "config.json").is_file():
        return local
    from huggingface_hub import snapshot_download  # кеш HF на ПК, скачивается один раз
    return snapshot_download(repo_id=repo_id)


def local_outro():
    """Утверждённые концовки v7 из C:\\M1lash\\private\\outro (SHA из tools/outro/approved.json) → media/outro (gitignored)."""
    import hashlib, shutil
    appr = json.loads((REPO / "tools" / "outro" / "approved.json").read_text(encoding="utf-8"))["assets"]
    ok = True
    for a in appr.values():
        src, dst = ROOT / "private" / "outro" / Path(a["path"]).name, REPO / a["path"]
        if dst.is_file() and hashlib.sha256(dst.read_bytes()).hexdigest() == a["sha256"]:
            continue
        if src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest() == a["sha256"]:
            dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
        else:
            ok = False
    return ok


def voice(a):
    guard()
    ref = Path(os.environ.get("M1LASH_VOICE_REF", ROOT / "private" / "voice_ref"))
    if not any(ref.glob("*")):
        ref.mkdir(parents=True, exist_ok=True)
        run([sys.executable, "scripts/voice_private_io.py", "fetch", "--dest", ref])
    run([sys.executable, "scripts/voice_private_io.py", "verify", "--dest", ref])
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    env = {"M1LASH_TTS_DEVICE": os.environ.get("M1LASH_DEVICE", "cuda"), "HF_HUB_DISABLE_TELEMETRY": "1"}
    wl = MODELS / "faster-whisper-small"
    if (wl / "model.bin").is_file():
        env["WHISPER_LOCAL_PATH"] = str(wl)
    run([sys.executable, "scripts/denis_voice_tts.py", "--job", a.job, "--assets", ref,
         "--model-dir", model_dir("Qwen/Qwen3-TTS-12Hz-1.7B-Base"), "--output", out], env=env)
    print("VOICE_OK", out / "manifest.json")


def render(a):
    guard()
    root = REPO / a.root
    workers = str(a.workers or max(2, (os.cpu_count() or 8) - 2))
    run(["node", "core/render/video.mjs", a.project, "--fps", a.fps, "--workers", workers, "--size", a.size, "--out", Path(a.out).resolve()], cwd=root)
    print("RENDER_OK", a.out)


def finish(a):
    if not local_outro():  # нет локальной копии — как в Actions, из приватного Drive (нужны секреты)
        run([sys.executable, "scripts/fetch_outro.py"])
    run([sys.executable, "scripts/fetch_outro.py", "--verify-only"])
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


def publish(a):
    """Готовый MP4 с ПК → ЧЕРНОВИК релиза (виден только владельцам репо) → youtube-direct mode=upload: PRIVATE, без даты.
    Секреты YouTube остаются в GitHub; MP4 не попадает в Git. После заливки черновик удаляется."""
    import hashlib, time
    mp4 = Path(a.mp4).resolve(); man = REPO / a.manifest
    sha = hashlib.sha256(mp4.read_bytes()).hexdigest()
    m = json.loads(man.read_text(encoding="utf-8"))
    if m.get("publish_at"):
        sys.exit("NO-GO: в манифесте есть дата — заливка только без даты (AGENTS §6)")
    tag, asset = f"private-{man.stem.replace('_', '-')}-{sha[:8]}", f"{man.stem}.mp4"
    stage = Path(os.environ.get("TEMP", ".")) / f"m1lash_{tag}"; stage.mkdir(exist_ok=True)
    staged = stage / asset
    if not staged.exists():
        import shutil; shutil.copy2(mp4, staged)
    gh = ["gh", "-R", a.repo]
    if subprocess.run(gh[:1] + ["release", "view", tag] + gh[1:], capture_output=True).returncode:
        run(gh[:1] + ["release", "create", tag, staged, "--draft", "--title", f"PRIVATE draft {man.stem} (auto-delete)",
                      "--notes", "Owner-private upload source; draft = not public; deleted after YouTube upload."] + gh[1:])
    m["source"] = {"type": "release", "tag": tag, "asset": asset, "sha256": sha}
    man.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run([sys.executable, "scripts/youtube_direct.py", "check", "--manifest", a.manifest])
    run(["git", "add", a.manifest]); subprocess.run(["git", "commit", "-qm", f"publish: {man.stem} → private draft source {sha[:12]}"], cwd=REPO)
    run(["git", "pull", "-q", "--rebase", "--autostash", "origin", "main"]); run(["git", "push", "-q", "origin", "HEAD:main"])
    run(gh[:1] + ["workflow", "run", "youtube-direct.yml", "--ref", "main", "-f", f"manifest={a.manifest}", "-f", "execute=true", "-f", "mode=upload"] + gh[1:])
    time.sleep(12)
    rid = subprocess.run(gh[:1] + ["run", "list", "--workflow", "youtube-direct.yml", "--limit", "1", "--json", "databaseId", "-q", ".[0].databaseId"] + gh[1:],
                         capture_output=True, text=True).stdout.strip()
    print("youtube-direct run", rid, flush=True)
    subprocess.run(gh[:1] + ["run", "watch", rid, "--interval", "30", "--exit-status"] + gh[1:])
    concl = subprocess.run(gh[:1] + ["run", "view", rid, "--json", "conclusion", "-q", ".conclusion"] + gh[1:], capture_output=True, text=True).stdout.strip()
    if concl == "success":
        subprocess.run(gh[:1] + ["release", "delete", tag, "--yes"] + gh[1:])
        run(["git", "pull", "-q", "--rebase", "--autostash", "origin", "main"])
        rc = REPO / "publishing" / "receipts" / man.name
        print("PUBLISH_OK", rc.read_text(encoding="utf-8") if rc.exists() else "(квитанция в main)")
    else:
        sys.exit(f"PUBLISH FAIL ({concl}): черновик {tag} оставлен для повтора; смотри run {rid}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where")
    v = sub.add_parser("voice"); v.add_argument("--job", required=True); v.add_argument("--out", required=True)
    r = sub.add_parser("render"); r.add_argument("--project", required=True); r.add_argument("--out", required=True)
    r.add_argument("--size", default="1080x1920"); r.add_argument("--fps", default="30"); r.add_argument("--workers", default="")
    r.add_argument("--root", default="longform/smart-strike")
    f = sub.add_parser("finish"); f.add_argument("--body", required=True); f.add_argument("--out", required=True); f.add_argument("--vertical", action="store_true")
    pb = sub.add_parser("publish"); pb.add_argument("--mp4", required=True); pb.add_argument("--manifest", required=True)
    pb.add_argument("--repo", default="osminoog09-star/Shorts")
    a = ap.parse_args()
    if a.cmd == "where":
        print(where())
    else:
        {"voice": voice, "render": render, "finish": finish, "publish": publish}[a.cmd](a)


if __name__ == "__main__":
    main()
