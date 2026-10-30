#!/usr/bin/env python3
"""Собирает данные для сайта «Студия M1lash» (site/studio/) из файлов репо.

Источники: reports/youtube/latest.json (Codex, аналитика), publishing/queue.json и
publishing/receipts/*.json (паспорта и заливки), publishing/playlists.json, reports/learnings.md,
reports/weekly/*.md. Сетка слотов — AGENTS.md, раздел 5 (дублируется тут, менять вместе).
Выход: site/studio/data.json. Запускается в motion-pages.yml перед деплоем GitHub Pages.
"""
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "studio" / "data.json"
TZ = ZoneInfo("Europe/Tallinn")

# AGENTS.md §5 — день недели (0=пн) -> [(время, что, кто)]
GRID = {
    0: [("10:00", "скетч", "Claude"), ("16:00", "нарезка 2 к субботнему", "Claude")],
    1: [("10:00", "новости ИИ", "Codex")],
    2: [("10:00", "скетч", "Codex"), ("19:00", "длинное", "Codex")],
    3: [("10:00", "кино-Shorts", "Claude"), ("16:00", "нарезка 1", "Codex")],
    4: [("10:00", "скетч", "Claude"), ("16:00", "нарезка 2", "Codex")],
    5: [("10:00", "скетч", "Codex"), ("19:00", "длинное", "Claude")],
    6: [("10:00", "Топ-5 недели", "Claude"), ("16:00", "нарезка 1", "Claude")],
}


def load(path, default=None):
    p = ROOT / path
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def seconds(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def section(md, name):
    m = re.search(r"^## " + name + r"\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        return []
    items = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return [i for i in items if not i.startswith("_(")]


def main():
    latest = load("reports/youtube/latest.json", {}) or {}
    queue = (load("publishing/queue.json", {}) or {}).get("items", [])
    playlists = load("publishing/playlists.json", {}) or {}
    kino_ids = set(playlists.get("kino_shorts", {}).get("seed", []))
    receipts = {}
    for p in sorted((ROOT / "publishing" / "receipts").glob("*.json")):
        r = load(str(p.relative_to(ROOT)), {}) or {}
        receipts[p.stem] = r

    videos = []
    an = latest.get("videos", {}) or {}
    for inv in latest.get("inventory", []):
        vid = inv["video_id"]
        dur = seconds(inv.get("duration"))
        title = inv.get("title", "")
        a = an.get(vid, {}) or {}
        t = title.lower()
        if dur and dur > 180:
            fmt = "Длинное"
        elif vid in kino_ids or re.search(r"сцена|фильм|\| во все|волк с уолл|стыковка|назвать сво", t):
            fmt = "Кино-Shorts"
        elif "притворись ботом" in t:
            fmt = "Притворись ботом"
        elif "новост" in t:
            fmt = "Новости ИИ"
        elif re.search(r"\bии\b|робот|нейросет|chatgpt|claude|бот", t):
            fmt = "ИИ-скетчи"
        elif re.search(r"компьютер|древн|луну|самол|венер|батаре|заряд|бросил её", t):
            fmt = "Наука"
        else:
            fmt = "Юмор/прочее"
        stats = inv.get("statistics", {}) or {}
        videos.append({
            "id": vid, "title": title, "published": inv.get("published_at"), "privacy": inv.get("privacy"),
            "duration": dur, "format": fmt,
            "views": a.get("views") if a.get("views") is not None else int(stats.get("viewCount", 0) or 0),
            "engaged": a.get("engagedViews"), "avp": a.get("averageViewPercentage"),
            "avd": a.get("averageViewDuration"), "subs": a.get("subscribersGained"),
            "likes": a.get("likes") if a.get("likes") is not None else int(stats.get("likeCount", 0) or 0),
            "comments": a.get("comments"), "shares": a.get("shares"),
        })
    videos = [v for v in videos if (v["duration"] or 0) > 0]

    # Сводка по форматам
    by_fmt = {}
    for v in videos:
        if v["privacy"] != "public":
            continue
        f = by_fmt.setdefault(v["format"], {"format": v["format"], "n": 0, "views": 0, "avp": [], "subs": 0})
        f["n"] += 1
        f["views"] += v["views"] or 0
        f["subs"] += v["subs"] or 0
        if v["avp"] is not None:
            f["avp"].append(v["avp"])
    formats = []
    for f in by_fmt.values():
        formats.append({"format": f["format"], "n": f["n"], "avg_views": round(f["views"] / f["n"]) if f["n"] else 0,
                        "avg_avp": round(sum(f["avp"]) / len(f["avp"]), 1) if f["avp"] else None,
                        "subs": f["subs"]})
    formats.sort(key=lambda x: -x["avg_views"])

    # План на 14 дней
    today = dt.datetime.now(TZ).date()
    scheduled = {}
    for key, r in receipts.items():
        when = r.get("publish_at_utc")
        if r.get("status") in ("scheduled", "uploaded") and when:
            local = dt.datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(TZ)
            scheduled[(local.date().isoformat(), local.strftime("%H:%M"))] = {"title": key, "status": r["status"],
                                                                                "video_id": r.get("video_id")}
    for q in queue:
        if q.get("slot"):
            d, t = q["slot"].split("T")
            scheduled.setdefault((d, t[:5]), {"title": q.get("title") or q["id"], "status": q.get("status")})
    # Решение Дениса 30.10: шаблон сетки пока не показываем (расписание ещё не выбрано) —
    # только реально запланированные/залитые ролики на ближайшие 14 дней.
    plan = []
    for (date, time), hit in sorted(scheduled.items()):
        if today.isoformat() <= date <= (today + dt.timedelta(days=14)).isoformat():
            plan.append({"date": date, "time": time, "what": "", "who": "",
                         "title": hit["title"], "status": hit["status"], "video_id": hit.get("video_id")})

    review = [{"id": k, "video_id": r.get("video_id"), "title": k} for k, r in receipts.items()
              if r.get("status") == "uploaded" and not r.get("publish_at_utc")]
    review += [{"id": q["id"], "title": q.get("title") or q["id"], "video_id": None}
               for q in queue if q.get("status") == "review"]

    learn_md = (ROOT / "reports" / "learnings.md").read_text(encoding="utf-8") if (ROOT / "reports" / "learnings.md").exists() else ""
    weekly = sorted((ROOT / "reports" / "weekly").glob("*.md"))
    weekly_txt = weekly[-1].read_text(encoding="utf-8")[:4000] if weekly else ""

    ideas = load("reports/ideas/latest.json", {}) or {}
    pubs = sorted([v for v in videos if v["privacy"] == "public" and v["published"]], key=lambda v: v["published"])
    vals = [x.get("views") or 0 for x in (latest.get("recent_daily_views") or [])]
    spike = None
    if len(vals) >= 8:
        base = sum(vals[-8:-1]) / 7
        if base > 0 and vals[-1] >= 2 * base:
            spike = {"day": latest["recent_daily_views"][-1]["day"], "views": vals[-1], "avg7": round(base)}
    events = {"last_video": {"id": pubs[-1]["id"], "title": pubs[-1]["title"]} if pubs else None,
              "ideas_date": ideas.get("date"), "ideas_count": len(ideas.get("ideas", [])), "spike": spike}
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)).isoformat()
    fresh = [v for v in pubs if v["published"] >= cutoff and v["views"]]
    top = max(fresh, key=lambda v: v["views"]) if fresh else None
    events["top_recent"] = {"title": re.sub(r"\s*#\S+", "", top["title"]).strip(), "views": top["views"]} if top else None
    gradle = (ROOT / "android-widget/app/build.gradle.kts").read_text(encoding="utf-8")
    vc = re.search(r"versionCode = (\d+)", gradle)
    vn = re.search(r'versionName = "([^"]+)"', gradle)
    app = {"version": int(vc.group(1)) if vc else 0, "name": vn.group(1) if vn else "",
           "apk": "https://github.com/osminoog09-star/Shorts/releases/download/widget/m1lash-widget.apk"}
    pulse = load("reports/youtube/pulse.json", {}) or {}
    snaps = pulse.get("snapshots") or []
    live = None
    if snaps:
        cur = snaps[-1]
        def ago(h):
            return snaps[-1 - h] if len(snaps) > h else snaps[0]
        rec = (pulse.get("recent") or [])[:3]
        live = {"t": cur["t"], "subs": cur["subs"], "views": cur["views"],
                "views_1h": cur["views"] - ago(1)["views"], "views_24h": cur["views"] - ago(24)["views"],
                "subs_24h": cur["subs"] - ago(24)["subs"],
                "recent": [{**r, "views": cur["videos"].get(r["id"], 0),
                            "views_1h": cur["videos"].get(r["id"], 0) - ago(1)["videos"].get(r["id"], cur["videos"].get(r["id"], 0))}
                           for r in rec]}
    ypp = load("reports/youtube/ypp.json")
    if ypp and live:
        ypp["live_subs"] = live["subs"]
    ch = latest.get("channel_statistics", {}) or {}
    daily = latest.get("recent_daily_views", []) or []
    out = {
        "built": dt.datetime.now(TZ).strftime("%d.%m.%Y %H:%M"),
        "analytics_as_of": latest.get("last_observed_view_day"),
        "channel": {"subs": live["subs"] if live else int(ch.get("subscriberCount", 0) or 0),
                    "views": live["views"] if live else int(ch.get("viewCount", 0) or 0),
                    "videos": int(ch.get("videoCount", 0) or 0)},
        "daily": daily, "formats": formats,
        "videos": sorted(videos, key=lambda v: v["published"] or "", reverse=True),
        "plan": plan, "review": review,
        "learn": {"works": section(learn_md, "Работает"), "fails": section(learn_md, "Не работает"),
                  "hyp": section(learn_md, "Гипотезы на проверку")},
        "weekly": {"name": weekly[-1].stem if weekly else None, "text": weekly_txt},
        "ideas": ideas, "events": events, "app": app, "ypp": ypp, "live": live,
        "playlists": {k: v.get("id") for k, v in playlists.items() if isinstance(v, dict)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("studio data:", len(videos), "videos,", len(plan), "slots,", len(review), "to review")


if __name__ == "__main__":
    main()
