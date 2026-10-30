#!/usr/bin/env python3
"""Apply owner-approved channel branding with strict channel & media checks.

Never logs tokens, never changes title or deletes videos. Upload banner only once on job run.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_direct import token_for, verify_channel, RU_ID

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT/"publishing/branding/channel.json").read_text(encoding="utf-8"))
banner = ROOT/cfg["banner_path"]
if not banner.is_file() or not (10000 < banner.stat().st_size < 6_000_000):
    raise SystemExit("NO-GO: approved PNG banner missing or wrong size")
if len(cfg["description"]) > 1000: raise SystemExit("NO-GO: description too long")
keywords = " ".join('"' + s.replace('"', '') + '"' if " " in s else s for s in cfg["keywords"])
if len(keywords) > 500: raise SystemExit("NO-GO: channel keywords too long")

token = token_for("ru")
verify_channel(token, RU_ID)
headers = {"Authorization": "Bearer " + token}
API = "https://www.googleapis.com/youtube/v3"

def request(method, url, **kwargs):
    request_headers = {**headers, **kwargs.pop("headers", {})}
    r = requests.request(method, url, headers=request_headers, timeout=60, **kwargs)
    if not r.ok:
        raise RuntimeError("%s %s -> HTTP %s (%s)" % (method, url.split("?")[0], r.status_code, r.text[:220]))
    return r.json() if r.content else {}

def channel():
    data=request("GET",API+"/channels",params={"part":"snippet,brandingSettings","mine":"true"})
    items=data.get("items",[])
    if len(items) != 1 or items[0]["id"] != RU_ID:
        raise SystemExit("NO-GO: authenticated YouTube channel differs from M1lash")
    return items[0]

cur=channel()
if cur["snippet"].get("title","").casefold()!=cfg["channel_name"].casefold():
    raise SystemExit("NO-GO: channel title differs; no remote write")
vid=request("GET",API+"/videos",params={"part":"snippet,status","id":cfg["trailer_video_id"]}).get("items",[])
if len(vid)!=1 or vid[0]["snippet"].get("channelId")!=RU_ID or vid[0]["status"].get("privacyStatus")!="public":
    raise SystemExit("NO-GO: requested trailer not a public channel video")
# NOTE channels.update overwrites the *whole* brandingSettings part, so read first.
brand=cur.get("brandingSettings",{})
oldchan=brand.get("channel",{})
mutable=["title","country","defaultLanguage","trackingAnalyticsAccountId"]
newchan={k:oldchan[k] for k in mutable if k in oldchan}
newchan["description"]=cfg["description"]
newchan["keywords"]=keywords
newchan["unsubscribedTrailer"]=cfg["trailer_video_id"]

with banner.open("rb") as f:
    payload=f.read()
r=request("POST","https://www.googleapis.com/upload/youtube/v3/channelBanners/insert",
          params={"uploadType":"media"},data=payload,
          headers={**headers,"Content-Type":"image/png"})
banner_url=r.get("url")
if not banner_url or not banner_url.startswith("https://"):
    raise SystemExit("NO-GO: banner upload returned no usable URL")
updated=request("PUT",API+"/channels",params={"part":"brandingSettings"},
                json={"id":RU_ID,"brandingSettings":{"channel":newchan,"image":{"bannerExternalUrl":banner_url}}})
# YouTube may return stale brandingSettings for a short time after channels.update.
import time
state={}
for attempt in range(6):
    check=channel()
    checkchan=check.get("brandingSettings",{}).get("channel",{})
    current_description=checkchan.get("description") or check.get("snippet",{}).get("description","")
    image=check.get("brandingSettings",{}).get("image",{})
    state={
      "description_verified": current_description.strip()==cfg["description"].strip(),
      "trailer_verified": checkchan.get("unsubscribedTrailer")==cfg["trailer_video_id"],
      "banner_confirmed_by_api": bool(image.get("bannerImageUrl") or image.get("bannerExternalUrl") or image.get("bannerMobileImageUrl")),
      "keywords_verified": cfg["keywords"][0] in checkchan.get("keywords",""),
    }
    print("BRANDING_READBACK",attempt+1,state,"fields",sorted(checkchan.keys()),"snippet_desc",bool(check.get("snippet",{}).get("description")))
    if all(state.values()): break
    time.sleep(3)
result={"status":"verified" if all(state.values()) else "partial",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "channel_id":RU_ID,"channel_name":cur["snippet"]["title"],**state}
(ROOT/"publishing/branding/status.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if result["status"]!="verified":
    raise RuntimeError("YouTube returned a partial branding readback; no success claim")
print("CHANNEL_BRANDING_VERIFIED",result["channel_name"],"banner=YES","trailer=YES","description=YES","keywords=YES")
