#!/usr/bin/env python3
"""Diagnostic of local publishing CSV; never asserts live YouTube/Metricool status."""
import argparse,csv,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo
TZ=ZoneInfo("Europe/Tallinn")
def audit(rows):
    issues=[]; per_day={}
    for r in rows:
        date=(r.get("date") or "").strip(); time=(r.get("time") or "").strip()
        if not date or not time:continue
        try: timestamp=dt.datetime.fromisoformat(date+"T"+time).replace(tzinfo=TZ)
        except ValueError:
            issues.append({"date":date,"issue":"invalid date/time","title":r.get("title")});continue
        if (r.get("kind") or "").strip().lower()=="short":
            per_day.setdefault(date,[]).append((timestamp,r.get("title","")))
    for date,items in per_day.items():
        items.sort()
        if len(items)>2:issues.append({"date":date,"issue":"more than two locally recorded Shorts"})
        for (first,_),(second,_) in zip(items,items[1:]):
            if (second-first).total_seconds()<21600:
                issues.append({"date":date,"issue":"Shorts closer than six hours"})
    unconfirmed=[{"date":r.get("date"),"time":r.get("time"),"title":r.get("title")}
      for r in rows if "scheduled" in (r.get("notes") or "").lower() and not (r.get("video_id") or "").strip()]
    return {"scope":"local CSV only; no live YouTube/Metricool check","issues":issues,
            "scheduled_without_youtube_id":unconfirmed}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",default="reports/videos.csv");p.add_argument("--output");a=p.parse_args()
    with open(a.input,encoding="utf-8-sig",newline="") as f:r=audit(list(csv.DictReader(f)))
    out=json.dumps(r,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(out,encoding="utf-8")
    print(out)
