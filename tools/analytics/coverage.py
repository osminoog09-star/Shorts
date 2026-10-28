#!/usr/bin/env python3
"""Explicitly report missing analytics, not imaginary YouTube reach."""
import argparse,csv,json
from pathlib import Path
MEASURES=("views_48h","views_7d","avd_s","likes","comments","shares","subs")
def summarize(rows):
    published=[r for r in rows if (r.get("video_id") or "").strip()]
    n=len(published)
    counts={k:sum((r.get(k) or "").strip()!="" for r in published) for k in MEASURES}
    return {"scope":"local metrics coverage; does not retrieve YouTube Analytics",
            "published_with_id":n,"known_counts":counts,
            "missing_counts":{k:n-v for k,v in counts.items()},
            "recommendation":"do not infer algorithm performance without 48h/7d synchronized data"}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",default="reports/videos.csv");a=p.parse_args()
    with open(a.input,encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
    print(json.dumps(summarize(rows),ensure_ascii=False,indent=2))
