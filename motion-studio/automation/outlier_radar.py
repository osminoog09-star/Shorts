#!/usr/bin/env python3
"""M1lash SCAN 2.0: YouTube niche outlier research with API quota safety.

No unauthorized videos/downloads. No inference of channel audience country, faceless
status, RPM, actual retention or current velocity without two snapshots.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import statistics
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UTC=dt.timezone.utc
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data"/"outliers.json"
YOUTUBE="https://www.googleapis.com/youtube/v3/"
QUERIES=[
 "AI robots documentary","AI tools explained 2026","robotics breakthrough",
 "NVIDIA AI technology","space discoveries NASA","space engineering documentary",
 "artificial intelligence experiment","future technology documentary",
 "robot manufacturing automation","science breakthrough explained",
 "history of inventions documentary","AI agents explained"
]
MAX_SEARCH_CALLS=12
MAX_CHANNELS=22
MAX_CANDIDATES=55
MAX_SEARCH_RESULTS=50
MAX_PLAYLIST_RESULTS=50


def parse_time(s):
    if not isinstance(s,str):return None
    try:
        d=dt.datetime.fromisoformat(s.replace("Z","+00:00"))
        if not d.tzinfo:d=d.replace(tzinfo=UTC)
        return d.astimezone(UTC)
    except ValueError:return None


def iso(d):
    return d.astimezone(UTC).isoformat().replace("+00:00","Z")


def seconds_iso8601(value):
    """YouTube PT#H#M#S duration, strict and independent from search 'long'."""
    m=re.fullmatch(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",value or "")
    if not m or not any(m.groups()):return None
    d,h,mi,s=[int(x or 0) for x in m.groups()]
    return d*86400+h*3600+mi*60+s


def group_of(duration):
    if not isinstance(duration,int):return None
    if duration>=1260:return "long"
    if 30<=duration<=180:return "short"
    return None


def median_outlier(views, baseline):
    """Avoid bogus 100x scores from zero/too few similar prior uploads."""
    valid=[int(x) for x in baseline if isinstance(x,int) and x>0]
    if len(valid)<5 or not isinstance(views,int) or views<0:
        return None
    median=statistics.median(valid)
    if median<=0:return None
    return round(views/median,2)


def growth_velocity(video_id,views,old,now):
    """Measured rate, unlike total views divided by age."""
    prev=(old or {}).get(video_id)
    if not isinstance(prev,dict):return None
    before=parse_time(prev.get("measured_at"))
    if before is None:return None
    prior=prev.get("views")
    if type(prior)!=int or views<prior:return None
    hours=(now-before).total_seconds()/3600
    if hours<1 or hours>96:return None
    return round((views-prior)/hours,2)


def rank_row(row):
    """Prioritize measured acceleration, then same-format baseline, then age-adjusted reach."""
    growth=row.get("recent_views_per_hour")
    ratio=row.get("outlier_ratio")
    daily=row.get("average_views_per_day")
    return (
        1 if isinstance(growth,(int,float)) else 0,
        math.log1p(max(0,growth or 0)),
        math.log1p(max(0,ratio or 0)),
        math.log1p(max(0,daily or 0))
    )


def validate_row(row,now):
    try:
        published=parse_time(row["published_at"])
        views=int(row["views"])
        seconds=int(row["duration_s"])
        if not published or seconds<1 or views<0:return False
        if (now-published).total_seconds() < -3600 or (now-published).days>11:return False
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}",row["video_id"]):return False
        return group_of(seconds) is not None
    except (KeyError,TypeError,ValueError):return False


class YouTubeAPI:
    def __init__(self,key,request=None):
        if not key:raise ValueError("YouTube API key required in GitHub Secrets")
        self._key=key
        self.calls={}
        self.request=request

    def get(self,method,**params):
        self.calls[method]=self.calls.get(method,0)+1
        if method=="search" and self.calls[method]>MAX_SEARCH_CALLS:
            raise ValueError("YouTube search cap per scan exceeded")
        if self.request:
            return self.request(method,params)
        args=urllib.parse.urlencode({**params,"key":self._key})
        url=YOUTUBE+method+"?"+args
        # Exception messages are sanitized. Never log URLs containing API keys.
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"M1lashResearch/2.0"})
            with urllib.request.urlopen(req,timeout=22) as resp:
                return json.loads(resp.read(2_000_000))
        except urllib.error.HTTPError as ex:
            raise RuntimeError("YouTube API HTTP status "+str(ex.code)) from None
        except (urllib.error.URLError,TimeoutError):
            raise RuntimeError("YouTube API connectivity failure") from None

    def batched(self,method,ids,part):
        ids=list(dict.fromkeys(ids))
        result=[]
        for i in range(0,len(ids),50):
            if ids[i:i+50]:
                response=self.get(method,id=",".join(ids[i:i+50]),part=part,maxResults=50)
                result.extend(response.get("items",[]))
        return result


def channel_baseline(api,channel,target,detail_cache):
    """At most one uploads playlist request per candidate channel.

    Use up to ten OTHER uploads published before the candidate; same length class.
    Public API lacks matched-age historical watch curves. This is an approximation.
    """
    uploads=((channel.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads")
    if not uploads:return []
    response=api.get("playlistItems",part="snippet",playlistId=uploads,maxResults=MAX_PLAYLIST_RESULTS)
    entries=response.get("items",[])
    ids=[]
    for entry in entries:
        snippet=entry.get("snippet") or {}
        vid=(snippet.get("resourceId") or {}).get("videoId")
        published=parse_time(snippet.get("publishedAt"))
        if vid and published and vid!=target["video_id"] and published<parse_time(target["published_at"]):
            ids.append(vid)
    missing=[x for x in ids if x not in detail_cache]
    for video in api.batched("videos",missing,part="snippet,contentDetails,statistics"):
        detail_cache[video.get("id")]=video
    group=target["format"]
    views=[]
    for vid in ids:
        v=detail_cache.get(vid) or {}
        length=seconds_iso8601((v.get("contentDetails") or {}).get("duration"))
        stats=v.get("statistics") or {}
        if group_of(length)==group and str(stats.get("viewCount","")).isdigit():
            num=int(stats["viewCount"])
            if num>0:views.append(num)
        if len(views)>=10:break
    return views


def existing_snapshots(old):
    return {str(x["video_id"]):{"views":x["views"],"measured_at":x["measured_at"]}
            for x in (old or {}).get("items",[])
            if isinstance(x,dict) and isinstance(x.get("views"),int)
            and isinstance(x.get("video_id"),str) and isinstance(x.get("measured_at"),str)}


def scan(api,old=None,now=None):
    now=now or dt.datetime.now(UTC)
    seen={}
    # 12 search queries, 50 results each max. This is search sampling, not all YouTube.
    for query in QUERIES:
        response=api.get("search",part="snippet",type="video",
            q=query,publishedAfter=iso(now-dt.timedelta(days=10)),
            maxResults=MAX_SEARCH_RESULTS,order="viewCount",
            regionCode="US",relevanceLanguage="en",videoDuration="long")
        for item in response.get("items",[]):
            vid=(item.get("id") or {}).get("videoId")
            if vid and re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
                seen[vid]=query
    # Long-form scan first: >=21m. A short-form scan would use separate search calls.
    details=api.batched("videos",list(seen),part="snippet,statistics,contentDetails")
    by_channel={}
    for v in details:
        sn=v.get("snippet") or {}; stats=v.get("statistics") or {}
        ident=v.get("id")
        duration=seconds_iso8601((v.get("contentDetails") or {}).get("duration"))
        published=parse_time(sn.get("publishedAt"))
        if not ident or not duration or duration<1260 or not published:
            continue
        channel=sn.get("channelId")
        if not channel or not str(stats.get("viewCount","")).isdigit():
            continue
        views=int(stats["viewCount"])
        age=max(1/24,(now-published).total_seconds()/86400)
        candidate={"video_id":ident,"title":str(sn.get("title") or "")[:240],
            "channel_id":channel,"channel_name":str(sn.get("channelTitle") or "")[:120],
            "published_at":iso(published),"duration_s":duration,"views":views,
            "average_views_per_day":round(views/age,1),
            "format":"long","query":seen.get(ident,""),
            "url":"https://www.youtube.com/watch?v="+ident,
            "measured_at":iso(now),"sample_region":"US_VIEWABLE_NOT_US_AUDIENCE"}
        if validate_row(candidate,now):
            by_channel.setdefault(channel,[]).append(candidate)
    # Avoid scanning hundreds of near-duplicate videos from one channel.
    representatives=sorted((max(rows,key=lambda x:x["average_views_per_day"])
                            for rows in by_channel.values()),
                           key=lambda x:x["average_views_per_day"],reverse=True)[:MAX_CHANNELS]
    channel_map={x.get("id"):x for x in api.batched(
        "channels",[r["channel_id"] for r in representatives],
        part="snippet,statistics,contentDetails")}
    prior=existing_snapshots(old)
    detail_cache={v.get("id"):v for v in details if v.get("id")}
    rows=[]
    for candidate in representatives[:MAX_CANDIDATES]:
        channel=channel_map.get(candidate["channel_id"])
        if not channel:continue
        cs=channel.get("statistics") or {}
        count=int(cs.get("subscriberCount")) if str(cs.get("subscriberCount","")).isdigit() else None
        if cs.get("hiddenSubscriberCount") or count is None or count>300000:
            continue
        baseline=channel_baseline(api,channel,candidate,detail_cache)
        candidate.update({
            "subscribers_rounded":count,
            "baseline_sample_count":len(baseline),
            "baseline_median_views":round(statistics.median(baseline),1) if len(baseline)>=5 else None,
            "outlier_ratio":median_outlier(candidate["views"],baseline),
            "recent_views_per_hour":growth_velocity(candidate["video_id"],candidate["views"],prior,now),
            "faceless_status":"NOT_ASSESSED_API_CANNOT_CONFIRM",
            "engagement_and_retention":"NOT_AVAILABLE_FROM_PUBLIC_API",
            "earning_estimate":"NOT_AVAILABLE_FROM_PUBLIC_API",
            "baseline_warning":"Last <=10 older same-format uploads at CURRENT view counts; not age-matched",
        })
        rows.append(candidate)
    rows.sort(key=rank_row,reverse=True)
    return {
        "status":"success",
        "updated_at":iso(now),
        "items":rows,
        "api_calls":api.calls,
        "requested_searches":len(QUERIES),
        "methodology":"Public YouTube Data API; sampled results only; no presenter/US audience/retention inferred",
        "quota_notice":"Search bucket default 100 calls/day; scanner capped at 12 calls per scan (24/day)",
        "velocity_notice":"recent_views_per_hour is ONLY a measured delta between snapshots, never lifetime avg",
        "baseline_notice":"Same-format earlier uploads, current lifetime views; caution with age and small samples",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default=str(DEST))
    args=ap.parse_args()
    dest=Path(args.output)
    old={}
    if dest.is_file():
        try:old=json.loads(dest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:old={}
    key=os.environ.get("YOUTUBE_API_KEY","")
    if not key:
        data={**old,"status":"not_configured",
              "message":"Set YOUTUBE_API_KEY in GitHub Actions Secrets; no fake scan performed",
              "last_attempt_at":iso(dt.datetime.now(UTC))}
    else:
        try:
            data=scan(YouTubeAPI(key),old=old)
            data["last_attempt_at"]=data["updated_at"]
        except Exception as error:
            # Preserve prior verified snapshots and don't leak URL/API key in error messages.
            data={**old,"status":"scan_failed",
                  "error_type":type(error).__name__,
                  "last_attempt_at":iso(dt.datetime.now(UTC))}
    data.setdefault("items",[])
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SCAN status="+str(data["status"])+" candidates="+str(len(data["items"])))


if __name__=="__main__":
    main()
