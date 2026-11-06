#!/usr/bin/env python3
"""ПК Дениса: выбор локальной LLM для агентов студии (экономия подписок Claude/Codex, решение 06.11.2026).

Прогоняет кандидатов через Ollama на реальных задачах студии и записывает лучшую в agents/local_model.txt —
её берёт scripts/pc/agent_bridge.py. Ничего не покупает и не отправляет наружу (только localhost).

Тесты (каждый 0..1):
  tools   — вызывает инструмент с правильными аргументами (без этого агент в Claude Code бесполезен);
  json    — отвечает строгим JSON по схеме (отчёты комьюнити/директора);
  russian — живой русский ответ подписчику, без английских вставок, не длиннее 2 фраз;
  fit     — модель целиком в видеопамяти (на 12 ГБ частичная выгрузка в RAM = в разы медленнее);
  speed   — токенов/с (≥25 = 1.0).
Итог = 0.35*tools + 0.2*json + 0.2*russian + 0.1*fit + 0.15*speed.

Запуск:  python scripts/pc/local_llm_bench.py --pull          (скачать кандидатов и проверить)
         python scripts/pc/local_llm_bench.py gemma4:12b qwen3:14b
"""
import argparse, json, re, sys, time, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OLLAMA = "http://localhost:11434"
# Кандидаты под 12 ГБ VRAM / 32 ГБ RAM. Теги проверь в библиотеке Ollama (раздел tools) — несуществующие пропускаются.
CANDIDATES = ["gemma4:12b", "qwen3.5:9b", "qwen3:14b", "qwen3:8b", "gpt-oss:20b", "mistral-small3.2:24b"]
CTX = 32768  # агенту Claude Code нужен длинный контекст; меньше 32k — частые обрывы


def call(path, body=None, timeout=600):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if path == "/api/pull":
            for line in r:
                st = json.loads(line).get("status", "")
                if st == "success":
                    return {"ok": True}
            return {"ok": False}
        return json.loads(r.read())


def chat(model, messages, **kw):
    t = time.time()
    r = call("/api/chat", {"model": model, "messages": messages, "stream": False,
                           "options": {"num_ctx": CTX, "temperature": 0.2}, **kw})
    r["_sec"] = time.time() - t
    return r


TOOL = [{"type": "function", "function": {
    "name": "queue_task", "description": "Поставить задачу агенту студии",
    "parameters": {"type": "object", "required": ["agent", "task", "slot"], "properties": {
        "agent": {"type": "string", "enum": ["m1lash-editor", "m1lash-writer", "m1lash-community"]},
        "task": {"type": "string"}, "slot": {"type": "string", "description": "ISO дата-время слота"}}}}}]


def t_tools(m):
    r = chat(m, [{"role": "user", "content": "Завтра 2026-11-08 в 20:00 пустой слот вечернего скетча. Поставь задачу нужному агенту."}], tools=TOOL)
    calls = r.get("message", {}).get("tool_calls") or []
    if not calls:
        return 0.0
    a = calls[0]["function"].get("arguments", {})
    a = json.loads(a) if isinstance(a, str) else a
    return (0.4 if calls[0]["function"]["name"] == "queue_task" else 0) + (0.3 if a.get("agent") == "m1lash-writer" else 0) \
        + (0.3 if "2026-11-08" in str(a.get("slot", "")) and "20" in str(a.get("slot", "")) else 0)


def t_json(m):
    r = chat(m, [{"role": "user", "content": 'Комментарий зрителя: «Сделайте фильм Престиж, сцену с фокусом!» (автор @kino_max). '
                  'Верни ТОЛЬКО JSON {"requests":[{"nick":str,"film_or_topic":str}],"risks":[]} без текста вокруг.'}], format="json")
    try:
        d = json.loads(r["message"]["content"])
        q = d["requests"][0]
        return 0.5 + (0.25 if "kino_max" in q["nick"] else 0) + (0.25 if "рест" in q["film_or_topic"].lower() else 0)
    except Exception:
        return 0.0


def t_russian(m):
    r = chat(m, [{"role": "system", "content": "Ты ведёшь YouTube-канал M1lash: юмор про ИИ и кино. Отвечай подписчикам коротко, по-русски, живо."},
                 {"role": "user", "content": "Комментарий: «ахах робот пылесос жиза, у меня такой же бастует». Напиши ответ."}])
    txt = r["message"]["content"].strip()
    txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()
    cyr = len(re.findall(r"[а-яё]", txt.lower())); lat = len(re.findall(r"[a-z]", txt.lower()))
    sentences = len([x for x in re.split(r"[.!?…]+", txt) if x.strip()])
    score = (0.5 if cyr > 15 and lat < 5 else 0) + (0.3 if sentences <= 3 else 0) + (0.2 if len(txt) < 260 else 0)
    ev = r.get("eval_count", 0); dur = r.get("eval_duration", 1) / 1e9
    return score, (ev / dur if dur > 0 else 0), txt


def fit(m):
    for x in call("/api/ps").get("models", []):
        if x["name"].startswith(m.split(":")[0]) and x.get("size"):
            return min(1.0, x.get("size_vram", 0) / x["size"])
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="*")
    ap.add_argument("--pull", action="store_true", help="скачать кандидатов, которых нет")
    a = ap.parse_args()
    try:
        have = {x["name"] for x in call("/api/tags")["models"]}
    except Exception:
        sys.exit("Ollama не запущена: установи https://ollama.com и запусти `ollama serve`")
    models, rows = a.models or CANDIDATES, []
    for m in models:
        if m not in have and not (a.pull and call("/api/pull", {"model": m, "stream": True}, timeout=7200).get("ok")):
            print(f"— {m}: нет локально (добавь --pull или проверь тег)"); continue
        try:
            tl, js = t_tools(m), t_json(m)
            ru, tps, sample = t_russian(m)
            f = fit(m)
        except Exception as e:
            print(f"— {m}: ошибка {e}"); continue
        total = 0.35 * tl + 0.2 * js + 0.2 * ru + 0.1 * f + 0.15 * min(1, tps / 25)
        rows.append({"model": m, "total": round(total, 3), "tools": tl, "json": js, "russian": ru,
                     "vram_fit": round(f, 2), "tok_s": round(tps, 1), "sample": sample[:160]})
        print(f"{m:24s} итог {total:.2f} | tools {tl:.2f} json {js:.2f} ru {ru:.2f} vram {f:.0%} {tps:.0f} ток/с | «{sample[:70]}»")
        call("/api/generate", {"model": m, "keep_alive": 0})  # выгрузить, чтобы не мешать следующему
    if not rows:
        sys.exit("ни одна модель не проверена")
    best = max(rows, key=lambda r: r["total"])
    (REPO / "agents").mkdir(exist_ok=True)
    (REPO / "agents" / "local_model.txt").write_text(best["model"] + "\n", encoding="utf-8")
    (REPO / "agents" / "local_llm_bench.json").write_text(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M"), "ctx": CTX, "rows": rows},
                                                                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nЛучшая: {best['model']} → agents/local_model.txt (её берёт agent_bridge.py)")
    if best["tools"] < 0.7:
        print("⚠ Даже лучшая плохо вызывает инструменты — директор будет чаще эскалировать в Claude.")


if __name__ == "__main__":
    main()
