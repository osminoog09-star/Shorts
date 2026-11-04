#!/usr/bin/env python3
"""One-time owner-approved schedule migration, never uploads or deletes videos.

Only the exact existing YouTube IDs and November 2026 Tallinn times below are allowed.
Each action must pass a live YouTube read, private-state and original-date check.
After verified YouTube readback, mirror that single change to GitHub and push.
Retries are read-only unless the exact old state still exists; never retry a PUT
after an ambiguous API failure. Manual inspection is required in that case.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youtube_direct as yt  # noqa: E402

TICKET = {
    "ticket": "m1lash-20261104-cadence-v1",
    "approved_by": "owner",
    "execute_existing_schedules_only": True,
}
PLAN = [
    # Existing scheduled off-format Shorts: keep the same video PRIVATE with NO release date.
    ("ai_news_2026_11_03", "oMhef8NQg1s", "2026-11-05T10:00:00+02:00", None),
    ("science_mirror_202611", "6KgLv_omqao", "2026-11-05T20:00:00+02:00", None),
    ("science_orbit_202611", "9XeZBiX7Pr8", "2026-11-06T20:00:00+02:00", None),
    # Reuse approved uploads, no new uploads and no new publishing approval.
    ("kino_006", "sCThiwmigy0", "2026-11-06T10:00:00+02:00", "2026-11-05T10:00:00+02:00"),
    ("ai_fridge_202611", "QS66i62EgJk", "2026-11-05T15:00:00+02:00", "2026-11-05T20:00:00+02:00"),
    ("ai_vacation_202611", "R0y8D9MZanc", "2026-11-06T15:00:00+02:00", "2026-11-06T20:00:00+02:00"),
    ("coffee_v8_20261104", "bEdC0uFDvl4", "2026-11-07T10:00:00+02:00", "2026-11-07T20:00:00+02:00"),
]


def utc(value):
    if value is None:
        return None
    value = value.replace("Z", "+00:00")
    return dt.datetime.fromisoformat(value).astimezone(dt.timezone.utc)


def iso_utc(value):
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z") if value else None


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save_json(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_status(token, video_id):
    resp = requests.get(
        yt.API + "/videos",
        params={"part": "status", "id": video_id},
        headers={"Authorization": "Bearer " + token, "Cache-Control": "no-cache"},
        timeout=40,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if len(items) != 1 or items[0].get("id") != video_id:
        raise RuntimeError(f"{video_id}: video is missing or inaccessible; stop")
    return items[0].get("status") or {}


def verified_status(token, video_id, expected):
    for i in range(4):
        if i:
            time.sleep(2 ** (i - 1))
        got = get_status(token, video_id)
        if got.get("privacyStatus") == "private" and utc(got.get("publishAt")) == expected:
            return got
    raise RuntimeError(f"{video_id}: YouTube readback differs (DO NOT repeat the write)")


def push_checkpoint(paths, slug, target):
    subprocess.run(["git", "config", "user.name", "m1lash-schedule-bot"], check=True)
    subprocess.run(["git", "config", "user.email", "m1lash-schedule-bot@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", *paths], check=True)
    subprocess.run(["git", "commit", "-m", f"schedule: verify {slug} -> {target or 'PRIVATE/no date'}"], check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)


def migrate_one(token, slug, video_id, old_iso, new_iso):
    manifest_path = f"publishing/queue/{slug}.json"
    receipt_path = f"publishing/receipts/{slug}.json"
    queue_path = "publishing/queue.json"
    request_path = "publishing/schedule_requests.json"
    manifest, receipt = read_json(manifest_path), read_json(receipt_path)
    q, ledger = read_json(queue_path), read_json(request_path)
    entries = [x for x in q["items"] if x.get("id") == slug]
    if len(entries) != 1 or entries[0].get("youtube_id") != video_id:
        raise RuntimeError(f"{slug}: queue ID mismatch; no change")
    if receipt.get("video_id") != video_id:
        raise RuntimeError(f"{slug}: receipt video ID mismatch; no change")
    source_id = (manifest.get("source") or {}).get("video_id")
    if source_id and source_id != video_id:
        raise RuntimeError(f"{slug}: manifest source ID mismatch; no change")
    old_at, new_at = utc(old_iso), utc(new_iso)
    local_at = utc(manifest.get("publish_at"))
    # File may reflect a prior successful checkpoint; otherwise must match the old date.
    if local_at not in (old_at, new_at):
        raise RuntimeError(f"{slug}: manifest date was independently modified; no change")
    state = get_status(token, video_id)
    if state.get("privacyStatus") != "private":
        raise RuntimeError(f"{slug}: is no longer PRIVATE; leave untouched")
    live_at = utc(state.get("publishAt"))
    if live_at not in (old_at, new_at):
        raise RuntimeError(f"{slug}: live date differs from original and target; leave untouched")
    if new_at is not None and new_at < dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=45):
        raise RuntimeError(f"{slug}: destination is too close/in the past; leave untouched")
    if live_at == old_at and new_at != old_at:
        if new_at:
            # The existing helper performs a single PUT and multiple GET readbacks.
            yt.youtube_schedule(video_id, manifest, new_at, token)
        else:
            # Explicitly clear the scheduled date, keep the same video PRIVATE.
            status = {"privacyStatus": "private",
                      "selfDeclaredMadeForKids": manifest["metadata"].get("made_for_kids", False),
                      "containsSyntheticMedia": manifest["metadata"].get("contains_synthetic_media", False)}
            resp = requests.put(yt.API + "/videos",
                                params={"part": "status"},
                                headers={"Authorization": "Bearer " + token},
                                json={"id": video_id, "status": status}, timeout=60)
            if not resp.ok:
                raise RuntimeError(f"{slug}: cancel-date HTTP {resp.status_code}; do not retry blindly")
        verified_status(token, video_id, new_at)
    else:
        verified_status(token, video_id, new_at)
    # ONLY after a YouTube verified read, mirror the exact platform state in GitHub.
    if new_at is None:
        manifest.pop("publish_at", None)
        manifest.pop("schedule_request", None)
        ledger.get("requests", {}).pop(slug, None)
        entries[0]["slot"] = None
        entries[0]["status"] = "review"
        entries[0]["note"] = (entries[0].get("note", "") + "\n04.11 owner: снята будущая дата; не соответствует новому основному формату, остаётся PRIVATE.").strip()
        receipt["status"] = "uploaded"
        receipt["publish_at_utc"] = None
        receipt.pop("schedule_confirmed_at", None)
        receipt.pop("schedule_request_id", None)
    else:
        request_id = f"owner-migration-20261104-{slug}"
        at = new_iso
        stamp = dt.datetime.now(dt.timezone.utc).isoformat()
        manifest["publish_at"] = at
        manifest["schedule_request"] = {"id": request_id, "requested_at": stamp, "publish_at": at}
        ledger.setdefault("requests", {})[slug] = {
            "at": at, "kind": "short", "title": manifest["metadata"]["title"],
            "video_id": video_id, "request_id": request_id, "requested_at": stamp,
            "owner_migration": "2026-11-04",
        }
        entries[0]["slot"] = at
        entries[0]["status"] = "scheduled"
        receipt["status"] = "scheduled"
        receipt["publish_at_utc"] = iso_utc(new_at)
        receipt["schedule_confirmed_at"] = stamp
        receipt["schedule_request_id"] = request_id
    receipt["privacy_status"] = "private"
    receipt["owner_migration_20261104"] = "YouTube GET verified; no re-upload"
    for p, data in [(manifest_path, manifest), (receipt_path, receipt),
                    (queue_path, q), (request_path, ledger)]:
        save_json(p, data)
    push_checkpoint([manifest_path, receipt_path, queue_path, request_path], slug, new_iso)
    print(f"VERIFIED {slug}: {video_id} -> {new_iso or 'PRIVATE with no publishAt'}", flush=True)


def main():
    if read_json("publishing/migrations/20261104_execute.json") != TICKET:
        raise RuntimeError("Not the exact owner-approved migration ticket; nothing changed")
    token = yt.token_for("ru")
    yt.verify_channel(token, yt.RU_ID)
    failures = []
    for slug, video_id, old, new in PLAN:
        try:
            migrate_one(token, slug, video_id, old, new)
        except Exception as exc:
            print(f"BLOCKED {slug}: {type(exc).__name__}: {exc}", flush=True)
            failures.append(slug)
            # A failed PUT may have reached YouTube; NEVER reattempt automatically.
    if failures:
        print("MANUAL_RECONCILIATION_REQUIRED:", ", ".join(failures), flush=True)
        raise SystemExit(1)
    print("All seven existing schedules verified; no new media uploaded.", flush=True)


if __name__ == "__main__":
    main()
