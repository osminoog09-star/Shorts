#!/usr/bin/env python3
"""Read-only snapshot of the M1lash channel: every video + YouTube Analytics.

Runs in GitHub Actions (workflow youtube-stats.yml) with the OAuth secrets from
scripts/youtube_direct.py. Writes reports/youtube/snapshot-<date>.json. Never uploads.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_direct import RU_ID, token_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
API = "https://www.googleapis.com/youtube/v3"
YTA = "https://youtubeanalytics.googleapis.com/v2/reports"


def get(url, token, **params):
    r = requests.get(url, params=params, headers={"Authorization": "Bearer " + token}, timeout=60)
    if not r.ok:
        return {"_error": r.status_code, "_body": r.text[:300]}
    return r.json()


def iso_seconds(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return None
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def report(token, start, end, metrics, dimensions=None, filters=None, sort=None, max_results=None):
    p = {"ids": "channel==MINE", "startDate": start, "endDate": end, "metrics": ",".join(metrics)}
    if dimensions:
        p["dimensions"] = ",".join(dimensions)
    if filters:
        p["filters"] = filters
    if sort:
        p["sort"] = sort
    if max_results:
        p["maxResults"] = max_results
    data = get(YTA, token, **p)
    if "_error" in data:
        return data
    cols = [c["name"] for c in data.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in data.get("rows", [])]


def main():
    token = token_for("ru")
    today = dt.date.today()
    end = today.isoformat()
    start = "2026-09-01"
    ch = get(API + "/channels", token, part="id,snippet,statistics,contentDetails", mine="true")
    item = ch["items"][0]
    assert item["id"] == RU_ID, "wrong channel"
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if page:
            params["pageToken"] = page
        pl = get(API + "/playlistItems", token, **params)
        ids += [x["contentDetails"]["videoId"] for x in pl.get("items", [])]
        page = pl.get("nextPageToken")
        if not page:
            break
    videos = []
    for i in range(0, len(ids), 50):
        vs = get(API + "/videos", token, part="snippet,contentDetails,statistics,status",
                 id=",".join(ids[i:i + 50]))
        for v in vs.get("items", []):
            videos.append({
                "id": v["id"], "title": v["snippet"]["title"],
                "published": v["snippet"].get("publishedAt"),
                "privacy": v["status"].get("privacyStatus"),
                "publishAt": v["status"].get("publishAt"),
                "duration_s": iso_seconds(v["contentDetails"].get("duration")),
                "views_public": int(v.get("statistics", {}).get("viewCount", 0)),
                "likes_public": int(v.get("statistics", {}).get("likeCount", 0)),
                "comments_public": int(v.get("statistics", {}).get("commentCount", 0)),
            })
    per_video = report(token, start, end,
                       ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration",
                        "averageViewPercentage", "subscribersGained", "likes", "comments", "shares"],
                       dimensions=["video"], sort="-views", max_results=200)
    by_type = report(token, start, end, ["views", "engagedViews", "estimatedMinutesWatched",
                                         "averageViewDuration", "subscribersGained"],
                     dimensions=["creatorContentType"])
    traffic = report(token, start, end, ["views", "estimatedMinutesWatched"],
                     dimensions=["insightTrafficSourceType"], sort="-views")
    daily = report(token, start, end, ["views", "engagedViews", "subscribersGained", "subscribersLost"],
                   dimensions=["day"], sort="day")
    geo = report(token, start, end, ["views"], dimensions=["country"], sort="-views", max_results=10)
    demo = report(token, start, end, ["viewerPercentage"], dimensions=["ageGroup", "gender"])
    retention = {}
    for v in videos:
        if (v["duration_s"] or 0) > 180 and v["privacy"] == "public":
            retention[v["id"]] = report(token, start, end, ["audienceWatchRatio", "relativeRetentionPerformance"],
                                        dimensions=["elapsedVideoTimeRatio"], filters="video==" + v["id"])
            retention[v["id"] + "_traffic"] = report(token, start, end, ["views"],
                                                     dimensions=["insightTrafficSourceType"],
                                                     filters="video==" + v["id"], sort="-views")
    out = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(), "period": [start, end],
           "channel": {"title": item["snippet"]["title"], **item.get("statistics", {})},
           "videos": videos, "analytics_per_video": per_video, "by_content_type": by_type,
           "traffic_sources": traffic, "daily": daily, "countries": geo, "demographics": demo,
           "long_video_retention": retention}
    path = ROOT / "reports" / "youtube" / ("snapshot-%s.json" % end)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("SNAPSHOT_OK", path.relative_to(ROOT), "videos=%d" % len(videos))


if __name__ == "__main__":
    main()
