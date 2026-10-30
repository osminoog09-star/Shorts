#!/usr/bin/env python3
"""Прогресс к монетизации YouTube (YPP) + прогноз по текущему темпу. Только чтение.

Пороги (проверено 30.10.2026, air.io / ppc.land / support.google.com/youtube/answer/72851):
  базовый (донаты, Super Thanks, членство): 500 подписчиков + 3 публичные загрузки за 90 дн
      + 3 млн просмотров Shorts за 90 дн ИЛИ 3000 ч просмотра длинных за 365 дн;
  полный (реклама): 1000 подписчиков + 10 млн Shorts/90 дн ИЛИ 4000 ч/365 дн;
      с 01.02.2027 для новых заявок 20 млн / 8000 ч.
YouTube считает «квалифицированные» просмотры — ближе всего engagedViews; если его нет, берём views
(тогда прогноз оптимистичный). Официальный прогресс — YouTube Studio → «Заработок».
Выход: reports/youtube/ypp.json. Запускается в youtube-analytics.yml.
"""
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.youtube_direct import token_for  # noqa: E402
from scripts.youtube_analytics import ApiError, Client  # noqa: E402

CHANGE = date(2027, 2, 1)


def series(client, start, end):
    """day -> {shorts, shorts_engaged, long_min}."""
    out = {}
    for metrics in (["views", "engagedViews", "estimatedMinutesWatched"], ["views", "estimatedMinutesWatched"]):
        try:
            rows = client.query(start, end, "day,creatorContentType", metrics)
            break
        except ApiError as exc:
            if exc.status != 400:
                raise
    else:
        return out, False
    engaged = "engagedViews" in metrics
    for r in rows:
        d = out.setdefault(r["day"], {"shorts": 0, "shorts_engaged": 0, "long_min": 0})
        kind = (r.get("creatorContentType") or "").upper()
        if kind == "SHORTS":
            d["shorts"] += r.get("views") or 0
            d["shorts_engaged"] += (r.get("engagedViews") or 0) if engaged else (r.get("views") or 0)
        elif kind in ("VIDEO_ON_DEMAND", "LIVE_STREAM"):
            d["long_min"] += r.get("estimatedMinutesWatched") or 0
    return out, engaged


def eta(history, window, target, rate, today, horizon=730):
    """Дней до момента, когда скользящая сумма за window дней достигнет target при темпе rate/день."""
    hist = history[-window:]
    if sum(hist) >= target:
        return 0
    for t in range(1, horizon + 1):
        kept = hist[t:] if t < len(hist) else []
        if sum(kept) + rate * min(t, window) >= target:
            return t
    return None


def main():
    now = datetime.now(timezone.utc)
    today = now.astimezone(ZoneInfo("Europe/Tallinn")).date()
    end = min(today - timedelta(days=1), now.astimezone(ZoneInfo("America/Los_Angeles")).date() - timedelta(days=1))
    client = Client(token_for("ru"))
    data, engaged = series(client, end - timedelta(days=364), end)
    subs_rows, _ = client.metrics(end - timedelta(days=27), end, "day", metrics=["subscribersGained", "subscribersLost"])
    latest = json.loads((ROOT / "reports/youtube/latest.json").read_text(encoding="utf-8"))
    subs = int((latest.get("channel_statistics") or {}).get("subscriberCount", 0) or 0)
    uploads_90 = sum(1 for v in latest.get("inventory", []) if v.get("privacy") == "public"
                     and v.get("published_at", "") >= (today - timedelta(days=90)).isoformat())
    days = [end - timedelta(days=i) for i in range(364, -1, -1)]
    sv = [data.get(str(d), {}).get("shorts_engaged", 0) for d in days]
    sv_all = [data.get(str(d), {}).get("shorts", 0) for d in days]
    lh = [data.get(str(d), {}).get("long_min", 0) / 60 for d in days]
    net28 = sum((r.get("subscribersGained") or 0) - (r.get("subscribersLost") or 0) for r in subs_rows)
    subs_rate = net28 / 28
    sv_rate = sum(sv[-14:]) / 14
    lh_rate = sum(lh[-28:]) / 28

    def goal(name, cur, target, days_left, unit, need=None):
        when = (today + timedelta(days=days_left)).isoformat() if days_left is not None else None
        return {"name": name, "current": round(cur, 1), "target": target, "unit": unit,
                "pct": round(min(100, cur * 100 / target), 1), "eta_days": days_left, "eta_date": when, "need": need}

    def subs_goal(target):
        left = max(0, target - subs)
        d = 0 if not left else (math.ceil(left / subs_rate) if subs_rate > 0 else None)
        return goal(f"{target} подписчиков", subs, target, d, "подп.", f"нужно ~{math.ceil(left / 30)}/день, чтобы за месяц" if left else None)

    def shorts_goal(target):
        d = eta(sv, 90, target, sv_rate, today)
        return goal(f"{target // 1_000_000} млн просмотров Shorts / 90 дн", sum(sv[-90:]), target, d, "просм.",
                    f"нужно ≈{math.ceil(target / 90):,} в день".replace(",", " "))

    def hours_goal(target):
        d = eta(lh, 365, target, lh_rate, today)
        return goal(f"{target} ч длинных / 365 дн", sum(lh), target, d, "ч",
                    f"нужно ≈{target / 365:.1f} ч в день")

    full_sv = 20_000_000 if today >= CHANGE else 10_000_000
    full_h = 8000 if today >= CHANGE else 4000
    tiers = [
        {"id": "base", "title": "Базовая монетизация (донаты, спонсорство)", "subs": subs_goal(500),
         "uploads": {"current": uploads_90, "target": 3, "ok": uploads_90 >= 3},
         "paths": [shorts_goal(3_000_000), hours_goal(3000)]},
        {"id": "full", "title": "Полная (реклама)", "subs": subs_goal(1000),
         "paths": [shorts_goal(full_sv), hours_goal(full_h)],
         "note": "С 01.02.2027 для новых заявок порог 20 млн Shorts / 8000 ч" if today < CHANGE else None},
    ]
    for t in tiers:
        best = [p["eta_days"] for p in t["paths"] if p["eta_days"] is not None]
        parts = [t["subs"]["eta_days"], min(best) if best else None]
        t["eta_days"] = None if None in parts else max(parts)
        t["eta_date"] = (today + timedelta(days=t["eta_days"])).isoformat() if t["eta_days"] is not None else None
    tf = tiers[1]
    if tf["eta_date"] and tf["eta_date"] >= CHANGE.isoformat() and today < CHANGE:
        tf["warn"] = "По текущему темпу успеваем только после 01.02.2027 — тогда нужен уже порог 20 млн / 8000 ч."
    out = {"as_of": str(end), "built": now.isoformat(), "engaged_views": engaged,
           "pace": {"subs_per_day": round(subs_rate, 2), "shorts_views_per_day": round(sv_rate),
                    "long_hours_per_day": round(lh_rate, 2)},
           "shorts_daily_90": [{"day": str(d), "views": v, "all": a} for d, v, a in zip(days[-90:], sv[-90:], sv_all[-90:])],
           "tiers": tiers,
           "sources": ["https://support.google.com/youtube/answer/72851",
                       "https://ppc.land/youtube-vp-cites-a-few-cents-to-justify-10-million-shorts-view-floor/"]}
    p = ROOT / "reports/youtube/ypp.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("ypp:", subs, "subs;", round(sum(sv[-90:])), "shorts views/90d; pace", round(sv_rate), "/day")


if __name__ == "__main__":
    try:
        main()
    except (ApiError, KeyError, ValueError) as e:
        sys.exit(f"ypp progress failed: {type(e).__name__} (no secrets logged)")
