"""Offline safeguards for opt-in YouTube queue; no OAuth, network or uploads."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youtube_direct as direct
import youtube_autoqueue as queue


class AutoQueueTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for name in ["publishing/queue", "publishing/receipts", "videos"]:
            (root / name).mkdir(parents=True, exist_ok=True)
        (root / "videos/approved.mp4").write_bytes(b"0" * 2048)
        (root / "publishing/channels.json").write_text(
            json.dumps({"ru": direct.RU_ID, "en": ""}), encoding="utf-8")
        for obj, field, value in [
            (direct, "ROOT", root), (direct, "QUEUE", root / "publishing/queue"),
            (direct, "RECEIPTS", root / "publishing/receipts"),
            (direct, "CHANNELS", root / "publishing/channels.json"),
            (queue, "ROOT", root)
        ]:
            patch = mock.patch.object(obj, field, value)
            patch.start()
            self.addCleanup(patch.stop)
        self.root = root
        self.current = dt.datetime.now(dt.timezone.utc)
        self.when = (self.current + dt.timedelta(days=2)).astimezone(
            ZoneInfo("Europe/Tallinn")).replace(hour=19, minute=0, second=0, microsecond=0)
        self.config = {
            "migration_hold_until": (self.current - dt.timedelta(days=1)).astimezone(ZoneInfo("Europe/Tallinn")).isoformat(),
            "min_lead_hours": 8, "max_days_ahead": 14,
            "require_sha256": True, "max_dispatch_per_run": 1,
        }

    def manifest(self, **changes):
        data = {
            "channel": "ru", "source": {"type": "repo", "path": "videos/approved.mp4",
                                         "sha256": "a"*64},
            "metadata": {
                "type": "long", "title": "Reviewed", "description": "Original material",
                "made_for_kids": False, "contains_synthetic_media": True,
            },
            "publish_at": self.when.isoformat(),
            "auto_publish": True, "approved": True, "quality_checked": True,
            "rights_checked": True, "metricool_clear": True,
        }
        data.update(changes)
        return data

    def save(self, name="approved.json", **changes):
        file = self.root / "publishing/queue" / name
        file.write_text(json.dumps(self.manifest(**changes)), encoding="utf-8")
        return file

    def test_approved_can_queue_without_network(self):
        f = self.save()
        with mock.patch.object(direct, "token_for", side_effect=AssertionError("No OAuth")):
            selected, skipped = queue.select(self.config, self.current)
        self.assertEqual(selected[0][1], f)
        self.assertFalse(skipped)

    def test_unapproved_is_never_dispatched(self):
        self.save(approved=False)
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_requires_rights_and_metricool_clear(self):
        self.save(rights_checked=False)
        self.assertFalse(queue.select(self.config, self.current)[0])
        self.save(metricool_clear=False)
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_rejects_missing_digest(self):
        f = self.save()
        data = json.loads(f.read_text())
        del data["source"]["sha256"]
        f.write_text(json.dumps(data))
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_stops_during_migration(self):
        self.save()
        self.config["migration_hold_until"] = (
            self.current + dt.timedelta(days=4)).isoformat()
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_receipt_prevents_duplicate(self):
        self.save()
        (self.root / "publishing/receipts/approved.json").write_text('{"status":"reserved"}')
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_dispatch_lead_time(self):
        self.save(publish_at=(self.current + dt.timedelta(hours=2)).astimezone(
            ZoneInfo("Europe/Tallinn")).isoformat())
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_invalid_en_channel(self):
        self.save(channel="en")
        self.assertFalse(queue.select(self.config, self.current)[0])

    def test_max_one_per_pass(self):
        f = self.save("first.json")
        self.save("second.json", publish_at=(self.when +
                  dt.timedelta(days=1)).isoformat())
        selected, _ = queue.select(self.config, self.current)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][1], f)

    def test_minimum_guards(self):
        f = self.root / "publishing/autopilot.json"
        f.write_text(json.dumps({"max_dispatch_per_run": 2, "max_days_ahead": 14,
                                  "min_lead_hours": 8}))
        with mock.patch.object(queue, "SETTINGS", f):
            with self.assertRaises(ValueError):
                queue.load_settings()


if __name__ == "__main__":
    unittest.main()
