"""Regression gates for Studio review cards vs confirmed YouTube receipts."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_studio_site import build_review_queue, add_pending_uploads


class StudioReviewStateTests(unittest.TestCase):
    def test_owner_left_deleted_is_not_review_even_with_historical_upload(self):
        q = [{"id": "gone", "status": "review"}]
        receipts = {"gone": {"status": "uploaded", "video_id": "abcdefghijk"}}
        manifests = {"gone": {"owner_decision": {"status": "leave_deleted", "reupload_allowed": False}}}
        self.assertEqual(build_review_queue(q, receipts, manifests), [])
        self.assertEqual(receipts["gone"]["status"], "uploaded", "historical receipt stays intact")

    def test_owner_left_deleted_is_not_recreated_as_pending_video(self):
        receipts = {"gone": {"status": "uploaded", "video_id": "abcdefghijk"}}
        manifests = {"gone": {"metadata": {"title": "Deleted"}, "owner_decision": {"status": "leave_deleted", "reupload_allowed": False}}}
        self.assertEqual(add_pending_uploads([], receipts, manifests), [])

    def test_scheduled_receipt_beats_stale_review_queue(self):
        q = [{"id": "kino_001", "status": "review", "title": "Kino"}]
        receipts = {"kino_001": {"status": "scheduled", "video_id": "abcdefghijk",
                                   "publish_at_utc": "2026-11-04T08:00:00Z"}}
        self.assertEqual(build_review_queue(q, receipts, {}), [])

    def test_uploaded_receipt_is_shown_only_once(self):
        q = [{"id": "a", "status": "review", "title": "A"}]
        receipts = {"a": {"status": "uploaded", "video_id": "abcdefghijk"}}
        got = build_review_queue(q, receipts, {"a": {"metadata": {"title": "A title"}}})
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["video_id"], "abcdefghijk")
        self.assertEqual(got[0]["manifest"], "publishing/queue/a.json")

    def test_unuploaded_review_never_prompts_owner(self):
        q = [{"id": "new", "status": "review", "title": "New Short"}]
        self.assertEqual(build_review_queue(q, {}, {}), [])

    def test_existing_unconfirmed_review_with_video_id_is_visible(self):
        q = [{"id": "old", "status": "review", "title": "Old Short"}]
        receipts = {"old": {"status": "review", "video_id": "abcdefghijk"}}
        self.assertEqual(build_review_queue(q, receipts, {}), [{
            "id": "old", "video_id": "abcdefghijk", "title": "Old Short"
        }])

    def test_scheduled_receipt_even_without_utc_field_never_review(self):
        q = [{"id": "a", "status": "review"}]
        self.assertEqual(build_review_queue(q, {"a": {"status": "scheduled", "video_id": "abcdefghijk"}}, {}), [])

    def test_private_receipt_with_publish_at_not_review(self):
        q = [{"id": "a", "status": "review"}]
        receipts = {"a": {"status": "uploaded", "video_id": "abcdefghijk", "publish_at_utc": "2026-11-04T08:00:00Z"}}
        self.assertEqual(build_review_queue(q, receipts, {}), [])


    def test_scheduled_video_missing_from_daily_analytics_is_visible(self):
        receipts = {"kino_007": {
            "status": "scheduled", "video_id": "3YjkmOrxDLA",
            "publish_at_utc": "2026-11-06T08:00:00Z",
            "uploaded_at": "2026-11-06T00:24:11Z",
        }}
        manifest = {"kino_007": {"metadata": {
            "type": "short", "category_id": "1",
            "title": "Он думал, что они КОМАНДА… #shorts",
        }}}
        result = add_pending_uploads([], receipts, manifest)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "3YjkmOrxDLA")
        self.assertEqual(result[0]["format"], "Кино-Shorts")
        self.assertEqual(result[0]["scheduled_at"], "2026-11-06T08:00:00Z")
        self.assertEqual(result[0]["privacy"], "private")
        self.assertIsNone(result[0]["views"], "no fabricated YouTube analytics")
        self.assertTrue(result[0]["analytics_pending"])

    def test_scheduled_video_already_in_inventory_is_not_duplicated(self):
        existing = [{"id": "3YjkmOrxDLA", "privacy": "public", "views": 50}]
        receipt = {"kino_007": {"status": "scheduled", "video_id": "3YjkmOrxDLA"}}
        manifest = {"kino_007": {"metadata": {"type": "short",
                                              "category_id": "1", "title": "Kino"}}}
        result = add_pending_uploads(existing, receipt, manifest)
        self.assertEqual(result, existing)
        self.assertEqual(result[0]["privacy"], "public")

    def test_no_ghost_placeholder_without_proven_receipt(self):
        manifest = {"ghost": {"metadata": {"type": "short", "title": "Ghost"}}}
        for state, vid in [("draft", "abcdefghijk"), ("scheduled", "bad_id")]:
            self.assertEqual(add_pending_uploads([], {"ghost": {"status": state, "video_id": vid}}, manifest), [])

    def test_all_confirmed_schedules_match_queue(self):
        queue = {q["id"]: q for q in json.loads(
            (ROOT / "publishing" / "queue.json").read_text(encoding="utf-8")
        )["items"]}
        folder = ROOT / "publishing" / "receipts"
        for receipt_path in folder.glob("*.json"):
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if receipt.get("status") != "scheduled":
                continue
            q = queue.get(receipt_path.stem)
            if not q:
                continue
            self.assertNotEqual(q.get("status"), "review", receipt_path.name)
            if q.get("status") != "scheduled":
                continue  # A confirmed public upload can be marked published.
            expected = dt.datetime.fromisoformat(
                receipt["publish_at_utc"].replace("Z", "+00:00")
            ).astimezone(ZoneInfo("Europe/Tallinn"))
            actual = dt.datetime.fromisoformat(q["slot"])
            self.assertEqual(expected, actual, receipt_path.name)


if __name__ == "__main__":
    unittest.main()
