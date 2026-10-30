#!/usr/bin/env python3
"""Автоидеи дня (запасной вариант, если GPT сегодня не писал reports/ideas/latest.json).

Правило AGENTS.md §13: 3–5 идей, ~70 % проверенных цифрами, ~30 % экспериментов.
Проверенные — из лидеров reports/youtube/latest.json за окно аналитики; эксперименты — по очереди
из reports/ideas/backlog.json. Идеи GPT (author != "auto") за сегодня не перезаписываем.
"""
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "reports" / "ideas"


def main():
    today = dt.datetime.now(ZoneInfo("Europe/Tallinn")).date().isoformat()
    cur = {}
    try:
        cur = json.loads((IDEAS / "latest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    if cur.get("date") == today and cur.get("author") != "auto":
        print("ideas: GPT уже написал идеи на сегодня — не трогаю"); return
    d = json.loads((ROOT / "reports/youtube/latest.json").read_text(encoding="utf-8"))
    titles = {i["video_id"]: (i.get("title") or "", i.get("duration") or "") for i in d.get("inventory", [])}
    rows = []
    for vid, a in (d.get("videos") or {}).items():
        t, dur = titles.get(vid, ("", ""))
        if not t or (a.get("views") or 0) <= 0:
            continue
        rows.append((a.get("views") or 0, a.get("averageViewPercentage") or 0, a.get("subscribersGained") or 0, t))
    by_views = sorted(rows, key=lambda r: -r[0])
    by_avp = sorted([r for r in rows if r[0] >= 300], key=lambda r: -r[1])
    by_subs = sorted(rows, key=lambda r: -r[2])
    clean = lambda t: re.sub(r"\s*#\S+", "", t).strip()
    ideas, n = [], 0
    def add(**kw):
        nonlocal n
        n += 1
        ideas.append({"id": f"{today}-{n}", "status": "proposed", **kw})
    if by_views:
        r = by_views[0]
        add(kind="proven", format="Кино-Shorts" if re.search(r"\|", r[3]) else "Shorts",
            title=f"Ещё ролик в формате лидера: «{clean(r[3])[:60]}»", film=None,
            why=f"Лидер окна: {r[0]} просмотров, досмотр {r[1]:.0f} %")
    if by_avp:
        r = by_avp[0]
        add(kind="proven", format="Shorts", title=f"Повторить приём с самым высоким досмотром: «{clean(r[3])[:60]}»",
            film=None, why=f"Досмотр {r[1]:.0f} % при {r[0]} просмотрах")
    used = {by_views[0][3] if by_views else None, by_avp[0][3] if by_avp else None}
    by_subs = [r for r in by_subs if r[3] not in used and r[2] > 0]
    if by_subs:
        r = by_subs[0]
        add(kind="proven", format="Shorts", title=f"Тема, которая приводит подписчиков: «{clean(r[3])[:60]}»",
            film=None, why=f"+{r[2]} подписчиков")
    backlog = json.loads((IDEAS / "backlog.json").read_text(encoding="utf-8")).get("experiments", [])
    open_ = [e for e in backlog if not e.get("done")]
    if open_:
        e = open_[dt.date.fromisoformat(today).toordinal() % len(open_)]
        add(kind="experiment", format="Shorts", title=e["title"], hypothesis=e["hypothesis"],
            metric=e["metric"], control=e["control"])
    days = d.get("recent_daily_views") or []
    last7 = sum(x.get("views") or 0 for x in days[-7:])
    prev7 = sum(x.get("views") or 0 for x in days[-14:-7])
    trend = f"{(last7 - prev7) * 100 // prev7:+d} % к прошлой неделе" if prev7 else "нет базы для сравнения"
    out = {"date": today, "author": "auto",
           "summary": f"Автоидеи по аналитике до {d.get('last_observed_view_day')}: 7 дней — {last7} просмотров ({trend}).",
           "ideas": ideas}
    IDEAS.mkdir(parents=True, exist_ok=True)
    for p in (IDEAS / "latest.json", IDEAS / f"{today}.json"):
        p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ideas:", len(ideas), "auto ideas for", today)


if __name__ == "__main__":
    main()
