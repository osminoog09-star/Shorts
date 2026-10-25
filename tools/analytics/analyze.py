#!/usr/bin/env python3
"""Расчёты по журналу роликов reports/videos.csv (без сети).

python3 tools/analytics/analyze.py [--kind short|long] [--last 15]

Печатает Markdown: таблицу роликов с индексом залёта и досмотром, затем сравнение групп
(формат, стиль, глубина, тема, длина, слот, автор). Пустые метрики пропускаются.
"""
import argparse
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "reports" / "videos.csv"


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def length_bucket(s):
    if s is None:
        return "?"
    return "≤30" if s <= 30 else "31–45" if s <= 45 else "46–60" if s <= 60 else ">60"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="short")
    ap.add_argument("--last", type=int, default=15, help="сколько последних роликов брать для медианы")
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8")) if (r.get("kind") or "short") == a.kind]
    rows.sort(key=lambda r: (r["date"], r.get("time", "")))
    for r in rows:
        r["_v"] = num(r.get("views_7d")) or num(r.get("views_48h"))
        r["_age"] = "7д" if num(r.get("views_7d")) else "48ч" if num(r.get("views_48h")) else "—"
        L, avd = num(r.get("length_s")), num(r.get("avd_s"))
        r["_apv"] = (avd / L * 100) if L and avd else None
        v = r["_v"]
        r["_like"] = (num(r.get("likes")) or 0) / v * 100 if v else None
        r["_share"] = (num(r.get("shares")) or 0) / v * 100 if v else None

    def median_for(r):
        key = "views_7d" if r["_age"] == "7д" else "views_48h"
        pool = [num(x[key]) for x in rows if num(x.get(key))][-a.last:]
        return statistics.median(pool) if len(pool) >= 3 else None

    print(f"## Ролики ({a.kind}, {len(rows)})\n")
    print("| дата | id | формат | стиль | тема | длина | просм. | возраст | индекс | досмотр | лайки % | репосты % |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        m = median_for(r)
        r["_idx"] = r["_v"] / m if (r["_v"] and m) else None
        tag = "" if r["_idx"] is None else " 🔥" if r["_idx"] >= 2 else " ⚠️" if r["_idx"] <= 0.5 else ""
        f = lambda x, d=1: "—" if x is None else f"{x:.{d}f}"
        print(f"| {r['date']} | {r['video_id']} | {r.get('format','')} | {r.get('style','')} | {r.get('topic','')[:24]} | "
              f"{r.get('length_s','')} | {f(r['_v'],0)} | {r['_age']} | {f(r['_idx'],2)}{tag} | {f(r['_apv']) + ('%' if r['_apv'] is not None else '')} | {f(r['_like'],2)} | {f(r['_share'],2)} |")

    groups = {
        "формат": lambda r: r.get("format") or "?",
        "стиль": lambda r: r.get("style") or "?",
        "глубина": lambda r: r.get("depth") or "?",
        "тема": lambda r: r.get("topic_group") or "?",
        "длина": lambda r: length_bucket(num(r.get("length_s"))),
        "слот": lambda r: (r.get("time") or "?")[:5],
        "автор": lambda r: r.get("agent") or "?",
    }
    for name, key in groups.items():
        agg = {}
        for r in rows:
            if r.get("_idx") is None:
                continue
            agg.setdefault(key(r), []).append(r)
        if not agg:
            continue
        print(f"\n### По группе «{name}»\n")
        print("| значение | n | средний индекс | медиана досмотра % | вывод |")
        print("|---|---|---|---|---|")
        for k, rs in sorted(agg.items(), key=lambda kv: -statistics.mean(x["_idx"] for x in kv[1])):
            idx = statistics.mean(x["_idx"] for x in rs)
            apvs = [x["_apv"] for x in rs if x["_apv"]]
            apv = f"{statistics.median(apvs):.0f}" if apvs else "—"
            verdict = "гипотеза (n<3)" if len(rs) < 3 else "лучше нормы" if idx >= 1.3 else "хуже нормы" if idx <= 0.7 else "норма"
            print(f"| {k} | {len(rs)} | {idx:.2f} | {apv} | {verdict} |")


if __name__ == "__main__":
    main()
