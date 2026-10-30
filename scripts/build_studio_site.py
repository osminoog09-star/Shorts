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
GRID = {  # AGENTS.md §5 (решение Дениса 31.10) — менять вместе
    0: [("10:00", "Shorts"), ("16:00", "Shorts")],
    1: [("10:00", "новости ИИ"), ("16:00", "Shorts")],
    2: [("10:00", "Shorts"), ("16:00", "Shorts")],
    3: [("10:00", "Shorts"), ("16:00", "кино-Shorts воронки")],
    4: [("10:00", "Shorts"), ("16:00", "кино-Shorts воронки")],
    5: [("16:00", "Shorts"), ("19:00", "кино-разбор")],
    6: [("16:00", "Shorts")],
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

    traffic = ((latest.get("traffic") or {}).get("videos") or {})
    csv_rows = {}
    try:
        import csv as _csv
        with open(ROOT / "reports/videos.csv", encoding="utf-8") as f:
            for r in _csv.DictReader(f):
                csv_rows[r.get("video_id")] = r
    except OSError:
        pass
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
            "thumb": f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
            "traffic": {r.get("insightTrafficSourceType"): r.get("views") for r in traffic.get(vid, []) if r.get("views")},
            "v48": int(csv_rows.get(vid, {}).get("views_48h") or 0) or None,
            "v7d": int(csv_rows.get(vid, {}).get("views_7d") or 0) or None,
            "engaged_views": a.get("engagedViews"),
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
    # Сетка AGENTS §5 на 7 дней: занятые слоты + пустые (их надо заполнить).
    for mf in sorted((ROOT / "publishing" / "queue").glob("*.json")):
        m = load(str(mf.relative_to(ROOT)), {}) or {}
        if m.get("publish_at"):
            local = dt.datetime.fromisoformat(m["publish_at"].replace("Z", "+00:00")).astimezone(TZ)
            scheduled[(local.date().isoformat(), local.strftime("%H:%M"))] = {
                "title": (m.get("metadata") or {}).get("title") or mf.stem, "status": "scheduled"}
    plan = []
    now_local = dt.datetime.now(TZ)
    for i in range(7):
        day = today + dt.timedelta(days=i)
        slots = {tm: what for tm, what in GRID[day.weekday()]}
        for (d, tm), hit in scheduled.items():
            if d == day.isoformat():
                slots.setdefault(tm, "")
        for tm in sorted(slots):
            if i == 0 and tm <= now_local.strftime("%H:%M") and (day.isoformat(), tm) not in scheduled:
                continue
            hit = scheduled.get((day.isoformat(), tm))
            plan.append({"date": day.isoformat(), "time": tm, "what": slots[tm], "who": "",
                         "title": hit["title"] if hit else None, "status": hit["status"] if hit else "пусто",
                         "video_id": hit.get("video_id") if hit else None})

    review = [{"id": k, "video_id": r.get("video_id"), "title": r.get("title") or k, "manifest": f"publishing/queue/{k}.json"} for k, r in receipts.items()
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
                "span_h": round((dt.datetime.fromisoformat(cur["t"]) - dt.datetime.fromisoformat(ago(24)["t"])).total_seconds() / 3600, 2),
                "recent": [{**r, "views": cur["videos"].get(r["id"], 0),
                            "views_1h": cur["videos"].get(r["id"], 0) - ago(1)["videos"].get(r["id"], cur["videos"].get(r["id"], 0))}
                           for r in rec]}
    if live:
        dur = {r["id"]: seconds(r.get("duration")) for r in (pulse.get("recent") or [])}
        cur = snaps[-1]
        prev = snaps[-2] if len(snaps) > 1 else cur
        shorts = [r for r in (pulse.get("recent") or []) if (dur.get(r["id"]) or 0) and dur[r["id"]] <= 180]
        if shorts:
            r = shorts[0]
            live["fresh_short"] = {"id": r["id"], "title": re.sub(r"\s*#\S+", "", r["title"]).strip(),
                                   "views": cur["videos"].get(r["id"], 0),
                                   "views_1h": cur["videos"].get(r["id"], 0) - prev["videos"].get(r["id"], cur["videos"].get(r["id"], 0)),
                                   "published": r.get("published")}
    comments = pulse.get("comments") or []
    day_ago = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)).isoformat()
    events["requests_24h"] = sum(1 for c in comments if "request" in c.get("flags", []) and (c.get("published") or "") >= day_ago[:19])
    events["to_me_24h"] = sum(1 for c in comments if "to_me" in c.get("flags", []) and (c.get("published") or "") >= day_ago[:19])
    exp = []
    try:
        for line in (ROOT / "reports/experiments.md").read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(cells) >= 8 and cells[0] not in ("Старт",) and not set(cells[0]) <= set("-: "):
                exp.append(dict(zip(["start", "hypothesis", "videos", "control", "metric", "h48", "d7", "verdict"], cells[:8])))
    except OSError:
        pass
    ypp = load("reports/youtube/ypp.json")
    if ypp and live:
        ypp["live_subs"] = live["subs"]
    # Занятые слоты для режима «Авто»: publish_at из манифестов очереди (будущие).
    taken = []
    for mf in sorted((ROOT / "publishing" / "queue").glob("*.json")):
        m = load(str(mf.relative_to(ROOT)), {}) or {}
        if m.get("publish_at"):
            taken.append({"id": mf.stem, "at": m["publish_at"], "kind": (m.get("metadata") or {}).get("type")})
    kinds = {mf.stem: ((load(str(mf.relative_to(ROOT)), {}) or {}).get("metadata") or {}).get("type") for mf in (ROOT / "publishing" / "queue").glob("*.json")}
    pending = {mf.stem for mf in (ROOT / "publishing" / "queue").glob("*.json")
               if (load(str(mf.relative_to(ROOT)), {}) or {}).get("publish_at")}
    review = [r for r in review if r["id"] not in pending]
    merged = {}
    for r in review:
        m = merged.setdefault(r["id"], {})
        for k, v in r.items():
            if v and (k not in m or not m[k] or (k == "title" and m[k] == r["id"])):
                m[k] = v
    review = list(merged.values())
    for r in review:
        r["kind"] = kinds.get(r["id"]) or "short"
        r["manifest"] = r.get("manifest") or (f"publishing/queue/{r['id']}.json" if r["id"] in kinds else None)
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
        "ideas": ideas, "events": events, "app": app, "ypp": ypp, "best_times": load("publishing/best_times.json"), "taken": taken, "live": live, "comments": comments, "comments_status": (pulse.get("status") or {}).get("comments"), "experiments": exp,
        "playlists": {k: v.get("id") for k, v in playlists.items() if isinstance(v, dict)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("studio data:", len(videos), "videos,", len(plan), "slots,", len(review), "to review")


if __name__ == "__main__":
    main()
