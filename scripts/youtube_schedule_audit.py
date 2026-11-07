#!/usr/bin/env python3
"""Read-only schedule audit (Claude, 07.11.2026): for every receipt in publishing/receipts with a video_id, GET the live
YouTube status (privacyStatus, publishAt) and compare with the receipt and publishing/queue.json. Changes nothing on YouTube.
Writes reports/youtube/schedule_audit.json and prints a table. Exit 0 always (it is a report), problems are listed.
"""
import datetime as dt, json, os, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youtube_direct as yd  # noqa: E402  (token_for)


def utc(s):
    if not s: return None
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def main():
    token = yd.token_for("ru")
    queue = {q["id"]: q for q in json.loads((ROOT / "publishing/queue.json").read_text(encoding="utf-8"))["items"]}
    receipts = {}
    for p in sorted((ROOT / "publishing/receipts").glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        vid = r.get("video_id")
        if vid: receipts[p.stem] = (r, vid)
    ids = [v for _, v in receipts.values()]
    live = {}
    for i in range(0, len(ids), 50):
        resp = requests.get(yd.API + "/videos", params={"part": "status,snippet", "id": ",".join(ids[i:i + 50])},
                            headers={"Authorization": "Bearer " + token, "Cache-Control": "no-cache"}, timeout=40)
        resp.raise_for_status()
        for it in resp.json().get("items", []):
            live[it["id"]] = {"privacy": it["status"].get("privacyStatus"), "publishAt": it["status"].get("publishAt"),
                              "title": it["snippet"].get("title"), "publishedAt": it["snippet"].get("publishedAt")}
    now = dt.datetime.now(dt.timezone.utc); rows = []; problems = []
    for slug, (r, vid) in receipts.items():
        L = live.get(vid); q = queue.get(slug, {})
        want = utc(r.get("publish_at_utc")) if r.get("status") == "scheduled" else None
        row = {"slug": slug, "video_id": vid, "receipt": r.get("status"), "receipt_publish_at": r.get("publish_at_utc"), "queue": q.get("status"), "queue_slot": q.get("slot"),
               "live_privacy": L and L["privacy"], "live_publishAt": L and L["publishAt"], "title": L and L["title"]}
        if not L and r.get("status") == "deleted": pass   # deleted on purpose by the owner's decision
        elif not L: row["problem"] = "видео не найдено на канале (удалено или нет доступа)"
        elif want and want > now and not (L["privacy"] == "private" and utc(L["publishAt"]) == want): row["problem"] = f"на YouTube другая дата/статус: {L['privacy']} {L['publishAt']}"
        elif want and want <= now and L["privacy"] != "public": row["problem"] = f"дата {r.get('publish_at_utc')} прошла, а видео {L['privacy']} (не вышло)"
        elif q.get("status") == "scheduled" and not want: row["problem"] = "в очереди scheduled, а в квитанции нет даты"
        if "problem" in row: problems.append(row)
        rows.append(row)
    out = {"checked_at": now.isoformat(), "count": len(rows), "problems": problems, "rows": rows}
    (ROOT / "reports/youtube/schedule_audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in sorted(rows, key=lambda r: r.get("receipt_publish_at") or ""):
        print(f"{r['slug'][:28]:28} {r['video_id']} receipt={r['receipt']:9} live={r['live_privacy']} publishAt={r['live_publishAt']}  {('!! ' + r['problem']) if r.get('problem') else 'OK'}")
    print(f"PROBLEMS: {len(problems)}")


if __name__ == "__main__":
    main()
