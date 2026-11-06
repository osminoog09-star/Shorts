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

Запуск:  python scripts/pc/agent_bridge.py            (чат раз в 60 с + циклы директора 08:30/13:30/19:30)
         python scripts/pc/agent_bridge.py --cycle-now  (цикл директора сразу)
         python scripts/pc/agent_bridge.py --once     (один проход)
         python scripts/pc/agent_bridge.py --dry-run  (показать, что взял бы)
Лог: agents/bridge.log (не коммитится).
"""
import argparse, json, os, re, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INBOX, OUTBOX = REPO / "agents" / "inbox", REPO / "agents" / "outbox"
LOG = REPO / "agents" / "bridge.log"
AGENT_RE = re.compile(r"^m1lash-[a-z-]+$")
DIRECTOR = "m1lash-studio-director"
# headless-запуск без вопросов о разрешениях, но только нужные инструменты (не --dangerously-skip-permissions)
TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Agent", "WebSearch", "WebFetch", "TodoWrite",
         "Bash(git:*)", "Bash(gh:*)", "Bash(python:*)", "Bash(python3:*)", "Bash(node:*)", "Bash(npx:*)",
         "Bash(ffmpeg:*)", "Bash(ffprobe:*)", "Bash(ls:*)", "Bash(mkdir:*)"]
CYCLE_PROMPT = ("Плановый цикл директора студии. Выполни свой цикл целиком по инструкции агента: состояние → план → "
                "делегирование субагентам → приёмка → отчёт Денису в agents/outbox → NOW/HANDOFF → push.")
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


GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}  # фоновый git не ждёт ввода пароля


def run_tree(cmd, timeout, **kw):
    """subprocess с таймаутом, который на Windows убивает и дочерние процессы (git-remote-https, node) — иначе зависает навсегда."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **kw)
    try:
        out, err = p.communicate(timeout=timeout)
        return subprocess.CompletedProcess(cmd, p.returncode, out, err)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        p.communicate()
        raise


def git(*args, check=True):
    try:
        r = run_tree(["git", "-c", "credential.interactive=never", *args], 180, cwd=REPO, env=GIT_ENV)
    except subprocess.TimeoutExpired:
        log(f"git {args[0]}: завис дольше 3 мин — прерван")
        return subprocess.CompletedProcess(args, 1, "", "timeout")
    if check and r.returncode:
        raise subprocess.CalledProcessError(r.returncode, r.args, r.stdout, r.stderr)
    return r


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pending():
    for f in sorted(INBOX.glob("*.json")):
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"пропуск {f.name}: {e}")
            continue
        if m.get("status") == "new" and m.get("from") in ("denis", DIRECTOR):
            yield f, m


# ── Экономия подписки (Денис 06.11: Claude и Codex по 20 €/мес) ──────────────────────────────
# По умолчанию ВСЁ идёт в локальную LLM на ПК через Ollama (Claude Code умеет работать с ней по
# Anthropic-совместимому API Ollama: ANTHROPIC_BASE_URL=http://localhost:11434). Настоящий Claude —
# только для тяжёлых агентов (код/графика/монтаж) или по эскалации "tier":"claude", и не больше
# CLAUDE_DAILY_CAP запусков в сутки. Модель выбирает scripts/pc/local_llm_bench.py → agents/local_model.txt.
OLLAMA = os.environ.get("M1_OLLAMA_URL", "http://localhost:11434")
CLAUDE_DAILY_CAP = int(os.environ.get("M1_CLAUDE_DAILY_CAP", "4"))
SETTINGS = REPO / "publishing" / "studio_settings.json"


def settings():
    """Настройки с сайта (Агенты → Управление студией); подхватываются после каждого git pull."""
    global CLAUDE_DAILY_CAP
    try:
        st = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        st = {}
    if "claude_daily_cap" in st and "M1_CLAUDE_DAILY_CAP" not in os.environ:
        CLAUDE_DAILY_CAP = int(st["claude_daily_cap"])
    return st
HEAVY = {"m1lash-studio-director", "m1lash-animator", "m1lash-editor", "m1lash-qa"}  # директор = Claude: локальная модель не ведёт оркестрацию (06.11: Gemma отвечала «готов» и ничего не делала)
BUDGET = REPO / "agents" / ".budget.json"


def local_model():
    m = settings().get("local_model", "auto")
    if m and m != "auto":
        return m
    f = REPO / "agents" / "local_model.txt"
    return (f.read_text(encoding="utf-8").strip() if f.exists() else "") or os.environ.get("M1_LOCAL_MODEL", "gemma4:12b")


def ollama_up():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def claude_budget_left():
    day = datetime.now().strftime("%Y-%m-%d")
    try:
        b = json.loads(BUDGET.read_text(encoding="utf-8"))
    except Exception:
        b = {}
    return CLAUDE_DAILY_CAP - (b.get("used", 0) if b.get("day") == day else 0)


def spend_claude():
    day = datetime.now().strftime("%Y-%m-%d")
    left = claude_budget_left()
    BUDGET.write_text(json.dumps({"day": day, "used": CLAUDE_DAILY_CAP - left + 1}), encoding="utf-8")


def pick_tier(agent, want=""):
    """local | claude | None (нельзя: Ollama выключена и лимит Claude исчерпан)."""
    heavy = want == "claude" or agent in HEAVY
    if not heavy and ollama_up():
        return "local"
    if claude_budget_left() > 0:
        return "claude"
    return "local" if ollama_up() else None


def ask_agent(agent, text, timeout, want=""):
    claude = shutil.which("claude")
    if not claude:
        return None, "claude CLI не найден в PATH (установи Claude Code на ПК)"
    if not AGENT_RE.match(agent) or not (REPO / ".claude" / "agents" / f"{agent}.md").exists():
        return None, f"неизвестный агент {agent}"
    tier = pick_tier(agent, want)
    if tier is None:
        return None, f"Ollama не запущена, а дневной лимит Claude ({CLAUDE_DAILY_CAP}) исчерпан — задача ждёт"
    env = dict(os.environ)
    cmd = [claude, "-p", "--agent", agent, "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS]
    if tier == "local":
        env.update(ANTHROPIC_BASE_URL=OLLAMA, ANTHROPIC_AUTH_TOKEN="ollama", ANTHROPIC_API_KEY="")
        cmd += ["--model", local_model()]
    else:
        spend_claude()
    log(f"   {agent} → {'локальная ' + local_model() if tier == 'local' else 'Claude (осталось ' + str(claude_budget_left()) + ' на сегодня)'}")
    try:
        r = run_tree(cmd + ["--", GUARD + text], timeout, cwd=REPO, env=env)
    except subprocess.TimeoutExpired:
        return None, f"агент не уложился в {timeout // 60} мин — задача продолжится в следующем запуске"
    out = (r.stdout or "").strip()
    if r.returncode != 0 or not out:
        return None, f"агент ({tier}) завершился с кодом {r.returncode}: {(r.stderr or '').strip()[-300:]}"
    return out[:MAX_REPLY], None


def handle(f, m, timeout, dry):
    agent = m.get("to", "")
    log(f"→ {agent}: {m.get('text', '')[:80]}")
    if dry:
        return False
    m["status"] = "taken"; m["taken_at"] = now()
    f.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reply, err = ask_agent(agent, m.get("text", ""), timeout, m.get("tier", ""))
    OUTBOX.mkdir(parents=True, exist_ok=True)
    rid = m["id"] + "-re"
    (OUTBOX / f"{rid}.json").write_text(json.dumps({
        "id": rid, "t": now(), "from": agent, "to": "denis", "re": m["id"],
        "text": reply if reply else f"⚠ {err}", "status": "ok" if reply else "error",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    m["status"] = "done" if reply else "error"; m["done_at"] = now()
    f.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"← {agent}: {'ответ' if reply else err}")
    STATE["last_reply"] = now()
    return True


def sync_push(n):
    git("add", "agents/inbox", "agents/outbox")
    if not git("diff", "--cached", "--quiet", check=False).returncode:
        return
    git("commit", "-m", f"agents: ответы агентов в чат студии ({n})")
    for _ in range(3):
        if git("pull", "--rebase", "--autostash", "-q", check=False).returncode == 0 and git("push", "-q", check=False).returncode == 0:
            log("push ok"); return
        time.sleep(5)
    log("push не удался — повторю в следующем цикле")


def director_cycle(timeout, dry):
    """Плановый автономный цикл: директор сам решает, что делать, и пишет отчёт в outbox."""
    log("⏱ цикл директора")
    if dry:
        return
    reply, err = ask_agent(DIRECTOR, CYCLE_PROMPT, timeout)
    if err:
        OUTBOX.mkdir(parents=True, exist_ok=True)
        rid = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-director-error"
        (OUTBOX / f"{rid}.json").write_text(json.dumps({"id": rid, "t": now(), "from": DIRECTOR, "to": "denis",
            "text": f"⚠ цикл не выполнен: {err}", "status": "error"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sync_push(1)
    STATE["last_cycle"] = now(); heartbeat(force=True)
    log("⏱ цикл директора завершён" + (f": {err}" if err else ""))


LAST_BEAT = [0.0]
STATE = {"last_cycle": None, "last_reply": None}


def heartbeat(force=False):
    """Статус ПК для сайта (Агенты → «ПК»): ветка pc-status, файл status.json. Раз в 10 мин, через gh (без коммитов в main)."""
    if not force and time.time() - LAST_BEAT[0] < 600:
        return
    LAST_BEAT[0] = time.time()
    gh = shutil.which("gh")
    if not gh:
        return
    st = settings()
    body = {"t": now(), "host": __import__("platform").node() or "pc",
            "ollama": ollama_up(), "local_model": local_model(), "claude_left": claude_budget_left(),
            "claude_cap": CLAUDE_DAILY_CAP, "paused": bool(st.get("paused")), "mode": st.get("mode", "on"), "autonomy": st.get("autonomy"),
            **STATE}
    import base64
    content = base64.b64encode((json.dumps(body, ensure_ascii=False, indent=1) + "\n").encode()).decode()
    repo = "osminoog09-star/Shorts"
    sha = subprocess.run([gh, "api", f"repos/{repo}/contents/status.json?ref=pc-status", "--jq", ".sha"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    if not sha:  # первая отправка: создать ветку pc-status от main
        base = subprocess.run([gh, "api", f"repos/{repo}/git/ref/heads/main", "--jq", ".object.sha"], capture_output=True, text=True, timeout=30).stdout.strip()
        subprocess.run([gh, "api", "-X", "POST", f"repos/{repo}/git/refs", "-f", "ref=refs/heads/pc-status", "-f", f"sha={base}"], capture_output=True, timeout=30)
    args = [gh, "api", "-X", "PUT", f"repos/{repo}/contents/status.json", "-f", "message=pc: heartbeat",
            "-f", f"content={content}", "-f", "branch=pc-status"] + (["-f", f"sha={sha}"] if sha else [])
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if r.returncode:
        log("heartbeat не отправлен: " + (r.stderr or "")[-200:])


LAST_MODE = ["on"]


def unload_ollama():
    """Игровой режим: освободить видеокарту — выгрузить все загруженные модели Ollama."""
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=3) as r:
            for m in json.loads(r.read()).get("models", []):
                req = urllib.request.Request(OLLAMA + "/api/generate", data=json.dumps({"model": m["name"], "keep_alive": 0}).encode(),
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10).read()
                log(f"видеокарта: выгружена модель {m['name']}")
    except Exception:
        pass


def studio_mode():
    """on | off | game — переключается на сайте или ярлыком «Панель M1lash» (scripts/pc/studio_panel.pyw)."""
    m = settings().get("mode", "on")
    if m != LAST_MODE[0]:
        log({"on": "▶ студия ВКЛЮЧЕНА", "off": "■ студия ВЫКЛЮЧЕНА", "game": "🎮 игровой режим: всё на паузе, видеокарта свободна"}.get(m, m))
        if m != "on":
            unload_ollama()
        LAST_MODE[0] = m
        heartbeat(force=True)
    return m


def run_once(timeout, dry):
    if git("pull", "--rebase", "--autostash", "-q", check=False).returncode != 0:
        r = git("status", "--porcelain", "-uno", check=False).stdout.strip()
        log("git pull не прошёл — пропускаю цикл" + (f" (правки: {r[:120]})" if r else ""))
        return
    if studio_mode() != "on":
        return  # сообщения из чата подождут включения студии
    n = sum(handle(f, m, timeout, dry) for f, m in pending())
    if n:
        sync_push(n)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=1800, help="сек на один ответ агента")
    ap.add_argument("--cycles", default="",
                    help="время циклов директора; пусто = из publishing/studio_settings.json (сайт)")
    ap.add_argument("--cycle-now", action="store_true", help="запустить цикл директора сразу")
    a = ap.parse_args()
    INBOX.mkdir(parents=True, exist_ok=True)
    log(f"мост запущен ({'один проход' if a.once else f'каждые {a.interval} с'})")
    fixed = [x.strip() for x in a.cycles.split(",") if x.strip()]
    done = set()
    if a.cycle_now:
        director_cycle(a.timeout * 2, a.dry_run)
    while True:
        st = settings()
        slots = fixed or st.get("director_cycles") or ["08:30", "13:30", "19:30"]
        hm, day = datetime.now().strftime("%H:%M"), datetime.now().date()
        for slot in ([] if st.get("paused") or st.get("mode", "on") != "on" else slots):
            if hm >= slot and (day, slot) not in done:
                done.add((day, slot))
                if hm < (datetime.strptime(slot, "%H:%M") + __import__("datetime").timedelta(minutes=30)).strftime("%H:%M"):
                    director_cycle(a.timeout * 2, a.dry_run)  # только если ПК был включён в своё время (±30 мин)
        try:
            run_once(a.timeout, a.dry_run)
            if not a.dry_run:
                heartbeat()
        except Exception as e:  # мост не должен падать из-за одного сообщения
            log(f"ошибка цикла: {e}")
        if a.once:
            break
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
