#!/usr/bin/env python3
"""ПК Дениса: слежка за папкой «Входящие» → кино-Shorts по плану недели → приватная заливка.

План недели — plans/week.json (пишут агенты в воскресенье):
{"week": "2026-11-02", "films": [
  {"match": "stringer", "film": "Стрингер", "scenes": [
    {"id": "stringer_night", "start": "12:30", "end": "13:20", "title": "Он снял то, что нельзя #shorts",
     "question": "Ты бы продал такое видео?", "lang": "ru", "request": ""}]}]}

Денис кладёт файл фильма в C:\\M1lash\\Входящие; имя файла должно содержать "match" (регистр/пробелы/точки не важны).
Скрипт: Входящие → Работа → movie_short.py по каждой сцене (whisper large-v3 на CUDA) → git push → youtube-direct
mode=upload (приватно, без даты, AGENTS §6). Через 7 дней после последней нарезки файл фильма удаляется из Работа.
Файлы фильмов никогда не попадают в репо — только готовые Shorts. Лог: C:\\M1lash\\inbox.log.
"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("M1LASH_ROOT", r"C:\M1lash"))
REPO = Path(__file__).resolve().parents[2]
INBOX, WORK, DONE = ROOT / "Входящие", ROOT / "Работа", ROOT / "Готово"
STATE = ROOT / "inbox_state.json"
VIDEO = {".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm"}
KEEP_DAYS = 7


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(ROOT / "inbox.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def norm(s):
    return re.sub(r"[^0-9a-zа-яё]", "", s.lower())


def run(cmd, **kw):
    log("$ " + " ".join(map(str, cmd)))
    return subprocess.run(cmd, cwd=REPO, check=True, **kw)


def stable(p):  # файл докачан: размер не меняется 30 с
    a = p.stat().st_size; time.sleep(30); return a == p.stat().st_size and a > 0


def state():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": {}, "files": {}}


def save(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def plan():
    subprocess.run(["git", "pull", "-q", "--rebase"], cwd=REPO)
    p = REPO / "plans" / "week.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"films": []}


def cut(film, src, st):
    for sc in film["scenes"]:
        if sc["id"] in st["done"]:
            continue
        try:
            run([sys.executable, "scripts/movie_short.py", "--src", str(src), "--id", sc["id"],
                 "--start", str(sc.get("start", "0")), "--end", str(sc.get("end", "")), "--title", sc["title"],
                 "--film", film["film"], "--lang", sc.get("lang", "ru"), "--request", sc.get("request", ""),
                 "--question", sc.get("question", "А ты бы как поступил?")])
            run(["git", "add", f"videos/{sc['id']}.mp4", f"publishing/queue/{sc['id']}.json",
                 "publishing/queue.json", f"reports/qa/{sc['id']}"])
            run(["git", "commit", "-qm", f"pc movie-short: {sc['id']} собран и проверен на ПК (без даты)"])
            for _ in range(3):
                if subprocess.run(["git", "pull", "-q", "--rebase"], cwd=REPO).returncode == 0 and \
                   subprocess.run(["git", "push", "-q"], cwd=REPO).returncode == 0:
                    break
                time.sleep(5)
            run(["gh", "workflow", "run", "youtube-direct.yml", "--ref", "main",
                 "-f", f"manifest=publishing/queue/{sc['id']}.json", "-f", "execute=true", "-f", "mode=upload"])
            st["done"][sc["id"]] = datetime.now().isoformat(timespec="seconds")
            log(f"OK {sc['id']} → приватная заливка запущена")
        except subprocess.CalledProcessError as e:
            st["done"].setdefault("_failed", {})[sc["id"]] = str(e)
            log(f"NO-GO {sc['id']}: {e} — см. reports/qa/{sc['id']}/qa.json")
        save(st)


def tick():
    st, pl = state(), plan()
    for f in sorted(INBOX.iterdir()):
        if f.suffix.lower() not in VIDEO or not stable(f):
            continue
        film = next((x for x in pl["films"] if norm(x["match"]) in norm(f.stem)), None)
        if not film:
            log(f"? {f.name}: нет в плане недели (plans/week.json) — жду"); continue
        dst = WORK / f.name
        f.replace(dst)
        st["files"][dst.name] = datetime.now().isoformat(timespec="seconds"); save(st)
        log(f"→ {f.name}: «{film['film']}», сцен {len(film['scenes'])}")
        cut(film, dst, st)
    for name, ts in list(st["files"].items()):  # чистка через 7 дней
        if datetime.fromisoformat(ts) < datetime.now() - timedelta(days=KEEP_DAYS):
            (WORK / name).unlink(missing_ok=True); st["files"].pop(name); save(st); log(f"удалён {name} (7 дней)")


if __name__ == "__main__":
    for d in (INBOX, WORK, DONE):
        d.mkdir(parents=True, exist_ok=True)
    log("M1lash Inbox запущен")
    while True:
        try:
            tick()
        except Exception as e:  # noqa: BLE001
            log(f"ошибка: {e}")
        time.sleep(60)
