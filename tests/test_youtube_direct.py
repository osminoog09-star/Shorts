"""Offline tests: no Google OAuth calls, no uploads."""
import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "youtube_direct.py"
spec = importlib.util.spec_from_file_location("youtube_direct", SCRIPT)
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)


class DirectUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        (root / "publishing/queue").mkdir(parents=True)
        (root / "publishing/receipts").mkdir(parents=True)
        (root / "videos").mkdir()
        (root / "videos/test.mp4").write_bytes(b"0" * 1500)
        self.patchers = [
            mock.patch.object(uploader, "ROOT", root),
            mock.patch.object(uploader, "QUEUE", root / "publishing/queue"),
            mock.patch.object(uploader, "RECEIPTS", root / "publishing/receipts"),
            mock.patch.object(uploader, "CHANNELS", root / "publishing/channels.json"),
        ]
        for patch in self.patchers:
            patch.start()
            self.addCleanup(patch.stop)
        self.channels = {"ru": uploader.RU_ID, "en": ""}
        self.future = (dt.datetime.now(ZoneInfo("Europe/Tallinn")) +
                       dt.timedelta(days=10)).replace(hour=10, minute=0, second=0, microsecond=0)

    def manifest(self, time=None, kind="short", channel="ru"):
        return {
            "channel": channel,
            "source": {"type": "repo", "path": "videos/test.mp4"},
            "metadata": {"title": "Safe video", "description": "Checked", "type": kind,
                         "made_for_kids": False, "contains_synthetic_media": True,
                         "tags": ["AI"], "category_id": "24"},
            "publish_at": (time or self.future).isoformat()
        }

    def test_russian_channel_and_tallinn_time(self):
        lang, channel_id, instant = uploader.validate(self.manifest(), self.channels)
        self.assertEqual((lang, channel_id), ("ru", uploader.RU_ID))
        self.assertEqual(instant.tzinfo, dt.timezone.utc)

    def test_en_requires_its_own_channel(self):
        with self.assertRaisesRegex(ValueError, "not configured"):
            uploader.validate(self.manifest(channel="en"), self.channels)
        self.channels["en"] = uploader.RU_ID
        with self.assertRaisesRegex(ValueError, "different"):
            uploader.validate(self.manifest(channel="en"), self.channels)

    def test_rejects_wrong_summer_offset(self):
        data = self.manifest()
        data["publish_at"] = "2027-07-05T10:00:00+02:00"
        with self.assertRaisesRegex(ValueError, "Tallinn"):
            uploader.validate(data, self.channels, check_future=False)

    def test_rejects_missing_mp4(self):
        data = self.manifest()
        data["source"]["path"] = "videos/missing.mp4"
        with self.assertRaisesRegex(ValueError, "absent"):
            uploader.validate(data, self.channels)

    def test_colliding_slot(self):
        other = self.manifest()
        path = uploader.QUEUE / "other.json"
        path.write_text(json.dumps(other), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Collision"):
            uploader.validate_queue(uploader.QUEUE / "new.json", self.manifest(), self.channels)

    def test_two_shorts_maximum(self):
        d = self.future
        for index, hour in enumerate([10, 16]):
            other = self.manifest(time=d.replace(hour=hour))
            (uploader.QUEUE / f"old-{index}.json").write_text(json.dumps(other), encoding="utf-8")
        third = self.manifest(time=d.replace(hour=22))
        with self.assertRaisesRegex(ValueError, "two Shorts"):
            uploader.validate_queue(uploader.QUEUE / "new.json", third, self.channels)

    def test_short_spacing(self):
        d = self.future
        other = self.manifest(time=d.replace(hour=10))
        (uploader.QUEUE / "old.json").write_text(json.dumps(other), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "six hours"):
            uploader.validate_queue(
                uploader.QUEUE / "new.json", self.manifest(time=d.replace(hour=15)), self.channels)

    def test_receipt_roundtrip(self):
        receipt = uploader.RECEIPTS / "test.json"
        uploader.atomic_json(receipt, {"status": "reserved", "channel": "ru"})
        self.assertEqual(uploader.load_json(receipt)["status"], "reserved")
        uploader.atomic_json(receipt, {"status": "uploaded", "video_id": "abcdefghijkl"})
        self.assertEqual(uploader.load_json(receipt)["status"], "uploaded")

    def test_oauth_not_needed_for_validation(self):
        with mock.patch.object(uploader, "token_for", side_effect=AssertionError("OAuth accessed")):
            uploader.validate(self.manifest(), self.channels)


if __name__ == "__main__":
    unittest.main()
