#!/usr/bin/env python3
"""ПК Дениса: мост «чат на сайте студии ↔ агенты Claude Code».

Сайт (вкладка «Агенты») кладёт сообщение Дениса в agents/inbox/<id>.json:
  {"id", "t", "from": "denis", "to": "m1lash-director", "text", "status": "new"}
Этот скрипт на ПК: git pull → берёт новые сообщения → запускает агента
`claude -p --agent <to>` в репозитории → пишет ответ в agents/outbox/<id>.json
({"id", "t", "from": <агент>, "to": "denis", "re": <id сообщения>, "text"}) →
помечает входящее status=done → commit + push. Сайт показывает ответ после
пересборки (motion-pages) — обычно 1–3 минуты.

Правила AGENTS.md действуют для агента как обычно: §6 (YouTube без «ок» Дениса
не трогать), PAUSED проекты не возобновлять, приватные WAV/фильмы не пушить.
Мост сам НИЧЕГО не публикует — только передаёт текст.

Запуск:  python scripts/pc/agent_bridge.py            (цикл, опрос раз в 60 с)
         python scripts/pc/agent_bridge.py --once     (один проход)
         python scripts/pc/agent_bridge.py --dry-run  (показать, что взял бы)
Лог: agents/bridge.log (не коммитится).
"""
import argparse, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INBOX, OUTBOX = REPO / "agents" / "inbox", REPO / "agents" / "outbox"
LOG = REPO / "agents" / "bridge.log"
AGENT_RE = re.compile(r"^m1lash-[a-z]+$")
MAX_REPLY = 4000

GUARD = ("Сообщение пришло от Дениса из чата сайта студии. Сначала AGENTS.md (приоритет) и tasks/NOW.md. "
         "Ответь по-русски коротко: что сделал или что сделаешь и к какому сроку. "
         "Ничего не публикуй и не назначай дат на YouTube без его «ок»; новый формат — только вопросы grill-me.\n\n"
         "Сообщение: ")


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=check)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pending():
    for f in sorted(INBOX.glob("*.json")):
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"пропуск {f.name}: {e}")
            continue
        if m.get("status") == "new" and m.get("from") == "denis":
            yield f, m


def ask_agent(agent, text, timeout):
    claude = shutil.which("claude")
    if not claude:
        return None, "claude CLI не найден в PATH (установи Claude Code на ПК)"
    if not AGENT_RE.match(agent) or not (REPO / ".claude" / "agents" / f"{agent}.md").exists():
        return None, f"неизвестный агент {agent}"
    try:
        r = subprocess.run([claude, "-p", "--agent", agent, GUARD + text], cwd=REPO,
                           capture_output=True, text=True, timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None, f"агент не уложился в {timeout // 60} мин — задача продолжится в следующем запуске"
    out = (r.stdout or "").strip()
    if r.returncode != 0 or not out:
        return None, f"агент завершился с кодом {r.returncode}: {(r.stderr or '').strip()[-300:]}"
    return out[:MAX_REPLY], None


def handle(f, m, timeout, dry):
    agent = m.get("to", "")
    log(f"→ {agent}: {m.get('text', '')[:80]}")
    if dry:
        return False
    m["status"] = "taken"; m["taken_at"] = now()
    f.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reply, err = ask_agent(agent, m.get("text", ""), timeout)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    rid = m["id"] + "-re"
    (OUTBOX / f"{rid}.json").write_text(json.dumps({
        "id": rid, "t": now(), "from": agent, "to": "denis", "re": m["id"],
        "text": reply if reply else f"⚠ {err}", "status": "ok" if reply else "error",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    m["status"] = "done" if reply else "error"; m["done_at"] = now()
    f.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"← {agent}: {'ответ' if reply else err}")
    return True


def sync_push(n):
    git("add", "agents/inbox", "agents/outbox")
    if not git("diff", "--cached", "--quiet", check=False).returncode:
        return
    git("commit", "-m", f"agents: ответы агентов в чат студии ({n})")
    for _ in range(3):
        if git("pull", "--rebase", "-q", check=False).returncode == 0 and git("push", "-q", check=False).returncode == 0:
            log("push ok"); return
        time.sleep(5)
    log("push не удался — повторю в следующем цикле")


def run_once(timeout, dry):
    if git("pull", "--rebase", "-q", check=False).returncode != 0:
        log("git pull не прошёл (локальные правки?) — пропускаю цикл")
        return
    n = sum(handle(f, m, timeout, dry) for f, m in pending())
    if n:
        sync_push(n)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=1800, help="сек на один ответ агента")
    a = ap.parse_args()
    INBOX.mkdir(parents=True, exist_ok=True)
    log(f"мост запущен ({'один проход' if a.once else f'каждые {a.interval} с'})")
    while True:
        try:
            run_once(a.timeout, a.dry_run)
        except Exception as e:  # мост не должен падать из-за одного сообщения
            log(f"ошибка цикла: {e}")
        if a.once:
            break
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
