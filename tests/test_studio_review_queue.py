"""Regression gates for Studio review cards vs confirmed YouTube receipts."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_studio_site import build_review_queue


class StudioReviewStateTests(unittest.TestCase):
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
