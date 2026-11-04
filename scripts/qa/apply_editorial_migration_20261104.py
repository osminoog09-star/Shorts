#!/usr/bin/env python3
"""One-time, fail-closed YouTube rescheduling for the owner's 04.11.2026 M1lash policy.

Changes only seven existing owner-reviewed RU videos, never uploads, deletes or makes public.
YouTube status is read BEFORE every mutation and AGAIN AFTER it. No request is retried.
Idempotent after partial failure: future runs may reconcile only known old/new times.
"""
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from youtube_direct import API, RU_ID, event_time, token_for, verify_channel  # noqa: E402

REQUEST = ROOT / "publishing/schedule_migrations/2026-11-04_editorial.json"
Q = ROOT / "publishing/queue"
RECEIPTS = ROOT / "publishing/receipts"

# Exact approval scope; even a malicious/mistaken change to the JSON cannot expand it.
EXPECTED = {
    "ai_news_2026_11_03": ("oMhef8NQg1s", "2026-11-05T10:00:00+02:00", None),
    "science_mirror_202611": ("6KgLv_omqao", "2026-11-05T20:00:00+02:00", None),
    "science_orbit_202611": ("9XeZBiX7Pr8", "2026-11-06T20:00:00+02:00", None),
    "kino_006": ("sCThiwmigy0", "2026-11-06T10:00:00+02:00", "2026-11-05T10:00:00+02:00"),
    "ai_fridge_202611": ("QS66i62EgJk", "2026-11-05T15:00:00+02:00", "2026-11-05T20:00:00+02:00"),
    "ai_vacation_202611": ("R0y8D9MZanc", "2026-11-06T15:00:00+02:00", "2026-11-06T20:00:00+02:00"),
    "coffee_v8_20261104": ("bEdC0uFDvl4", "2026-11-07T10:00:00+02:00", "2026-11-07T20:00:00+02:00"),
}

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    return event_time(a) == event_time(b)

def status(token, vid):
    response = requests.get(
        API + "/videos",
        params={"part": "status", "id": vid},
        headers={"Authorization": "Bearer " + token, "Cache-Control": "no-cache"},
        timeout=45)
    response.raise_for_status()
    items = response.json().get("items", [])
    if len(items) != 1 or items[0].get("id") != vid:
        raise RuntimeError("Cannot read exact video status: " + vid)
    return items[0].get("status", {})

def main():
    migration = read(REQUEST)
    if migration.get("migration_id") != "owner-2026-11-04-2shorts-2cartoons":
        raise RuntimeError("Wrong migration ID")
    items = migration.get("changes", [])
    if len(items) != len(EXPECTED) or {x.get("id") for x in items} != set(EXPECTED):
        raise RuntimeError("Unexpected migration scope")
    if migration.get("channel_id") != RU_ID:
        raise RuntimeError("Wrong YouTube channel")
    by_id = {x["id"]: x for x in items}
    manifests = {}
    receipts = {}
    for vid_slug, (video_id, old_at, new_at) in EXPECTED.items():
        item = by_id[vid_slug]
        if (item.get("video_id"), item.get("old"), item.get("new")) != (video_id, old_at, new_at):
            raise RuntimeError("The owner-approved old/new date has changed: " + vid_slug)
        manifest = read(Q / (vid_slug + ".json"))
        receipt = read(RECEIPTS / (vid_slug + ".json"))
        if manifest.get("channel") != "ru" or receipt.get("channel") != "ru":
            raise RuntimeError("Wrong channel in manifest/receipt " + vid_slug)
        if receipt.get("video_id") != video_id or receipt.get("source_sha256") != manifest.get("source", {}).get("sha256"):
            raise RuntimeError("Video ID/SHA mismatch: " + vid_slug)
        if not same(manifest.get("publish_at"), new_at):
            raise RuntimeError("Manifest not updated to new editorial policy: " + vid_slug)
        if new_at:
            request = (manifest.get("schedule_request") or {})
            if request.get("id") != "migration-20261104-" + vid_slug or not same(request.get("publish_at"), new_at):
                raise RuntimeError("Missing immutable migration request: " + vid_slug)
            if event_time(new_at) <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=45):
                raise RuntimeError("Requested time too close or past: " + vid_slug)
        manifests[vid_slug], receipts[vid_slug] = manifest, receipt
    token = token_for("ru")
    verify_channel(token, RU_ID)
    # Fail closed for ALL entries before changing ANY.
    live = {}
    for slug, (video_id, old_at, new_at) in EXPECTED.items():
        s = status(token, video_id)
        if s.get("privacyStatus") != "private":
            raise RuntimeError("Video is not PRIVATE; no mutation: " + slug)
        p = s.get("publishAt")
        if not (same(p, old_at) or same(p, new_at) or p is None):
            raise RuntimeError("Unexpected existing YouTube schedule: " + slug + " (" + str(p) + ")")
        live[slug] = p
        print("PREFLIGHT", slug, "current=", p or "PRIVATE-unscheduled", "desired=", new_at or "PRIVATE-unscheduled", flush=True)
    # Cancel old off-grid reservations first; then rebook exact two-per-day roles.
    order = [x for x in EXPECTED if EXPECTED[x][2] is None] + [x for x in EXPECTED if EXPECTED[x][2] is not None]
    for slug in order:
        video_id, old_at, new_at = EXPECTED[slug]
        m = manifests[slug]
        if not same(live[slug], new_at):
            new_status = {
                "privacyStatus": "private",
                "selfDeclaredMadeForKids": m["metadata"]["made_for_kids"],
                "containsSyntheticMedia": m["metadata"]["contains_synthetic_media"]
            }
            if new_at:
                new_status["publishAt"] = event_time(new_at).isoformat().replace("+00:00", "Z")
            response = requests.put(
                API + "/videos", params={"part": "status"},
                headers={"Authorization": "Bearer " + token},
                json={"id": video_id, "status": new_status}, timeout=60)
            if not response.ok:
                raise RuntimeError("YouTube update uncertain or refused, no retry: " + slug + " HTTP " + str(response.status_code))
        # Verify real YouTube state, not the local manifest or HTTP response alone.
        confirmed = None
        for attempt in range(4):
            if attempt:
                time.sleep(2 ** (attempt - 1))
            actual = status(token, video_id)
            if actual.get("privacyStatus") == "private" and same(actual.get("publishAt"), new_at):
                confirmed = actual.get("publishAt")
                break
        if confirmed is None and new_at is not None:
            raise RuntimeError("YouTube schedule not confirmed: " + slug)
        if new_at is None and actual.get("publishAt") is not None:
            raise RuntimeError("YouTube private unschedule not confirmed: " + slug)
        if actual.get("privacyStatus") != "private":
            raise RuntimeError("YouTube privacy changed unexpectedly: " + slug)
        r = receipts[slug]
        r.update({
            "status": "scheduled" if new_at else "uploaded",
            "publish_at_utc": confirmed,
            "privacy_status": "private",
            "schedule_confirmed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "schedule_request_id": ("migration-20261104-" + slug) if new_at else None,
            "editorial_migration": migration["migration_id"]
        })
        (RECEIPTS / (slug + ".json")).write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("YOUTUBE_READBACK_OK", slug, video_id, confirmed or "PRIVATE-unscheduled", flush=True)
    print("ALL_7_YOUTUBE_READBACK_OK", flush=True)

if __name__ == "__main__":
    main()
