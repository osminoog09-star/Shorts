#!/usr/bin/env python3
"""No-cost scheduler for reviewed YouTube manifests; never renders or pays for AI.

Opt-in activation requires publishing/autopilot.json enabled AND repository
variable YOUTUBE_AUTOPUBLISH_ENABLED=true. A manifest must be explicitly
approved and free of a Metricool booking. Uses youtube-direct.yml for the
actual preflight, reservation, channel verification and upload.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

import youtube_direct as direct

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "publishing" / "autopilot.json"


def load_settings():
    config = direct.load_json(SETTINGS)
    if config.get("max_dispatch_per_run") != 1:
        raise ValueError("Safe autopilot dispatch limit must be exactly 1")
    if int(config.get("max_days_ahead", 0)) not in range(1, 31):
        raise ValueError("max_days_ahead must be 1..30")
    if int(config.get("min_lead_hours", 0)) < 6:
        raise ValueError("min_lead_hours must be at least 6")
    return config


def select(config, current=None):
    current = current or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        raise ValueError("current time must be timezone-aware")
    hold = direct.event_time(config["migration_hold_until"])
    channels = direct.load_json(direct.CHANNELS)
    selected, skipped = [], []
    for path in sorted(direct.QUEUE.glob("*.json")):
        try:
            data = direct.load_json(path)
            if not all(data.get(name) is True for name in
                       ("auto_publish", "approved", "quality_checked", "rights_checked", "metricool_clear")):
                raise ValueError("requires all five explicit approvals")
            if config.get("require_sha256", True) and not data.get("source", {}).get("sha256"):
                raise ValueError("MP4 SHA-256 required for automatic dispatch")
            _, _, when = direct.validate(data, channels, check_future=False)
            direct.validate_queue(path, data, channels)
            if direct.receipt_path(path).exists():
                raise ValueError("already reserved or uploaded")
            if when < hold:
                raise ValueError("date falls in Metricool migration hold")
            if when < current + dt.timedelta(hours=int(config["min_lead_hours"])):
                raise ValueError("insufficient upload lead time")
            if when > current + dt.timedelta(days=int(config["max_days_ahead"])):
                raise ValueError("outside dispatch horizon")
            selected.append((when, path))
        except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            skipped.append({"manifest": path.name, "reason": str(exc)})
    selected.sort(key=lambda entry: (entry[0], entry[1].name))
    return selected[:1], skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="dispatch GitHub workflow, NEVER upload directly")
    args = parser.parse_args()
    config = load_settings()
    if not config.get("enabled"):
        print("AUTOPILOT DISABLED in publishing/autopilot.json; zero dispatches")
        return
    if os.environ.get("YOUTUBE_AUTOPUBLISH_ENABLED") != "true":
        print("AUTOPILOT DISABLED: repository Actions variable YOUTUBE_AUTOPUBLISH_ENABLED != true")
        return
    picked, skipped = select(config)
    print(json.dumps({"ready": [str(p.relative_to(ROOT)) for _, p in picked],
                      "skipped": skipped}, ensure_ascii=False))
    if not args.execute:
        print("DRY RUN: no workflows dispatched")
        return
    if not picked:
        print("No reviewed, unreserved, eligible YouTube jobs")
        return
    lang = direct.load_json(picked[0][1])["channel"]
    if os.environ.get("YOUTUBE_REFRESH_TOKEN_" + lang.upper() + "_EXISTS") != "true":
        print("No OAuth refresh token configured for " + lang.upper() + "; skip dispatch safely")
        return
    if not os.environ.get("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN is required for Actions dispatch")
    manifest = str(picked[0][1].relative_to(ROOT))
    subprocess.run(["gh", "workflow", "run", "youtube-direct.yml", "--repo",
                    "osminoog09-star/Shorts", "--ref", "main",
                    "-f", "manifest=" + manifest, "-f", "execute=true"], check=True)
    print("DISPATCH REQUESTED for " + manifest + " (not proof of upload).")


if __name__ == "__main__":
    main()
