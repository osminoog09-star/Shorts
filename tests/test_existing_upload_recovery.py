import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("youtube_direct", Path(__file__).resolve().parents[1] / "scripts" / "youtube_direct.py")
yt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yt)

class ExistingUploadRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.queue = self.root / "publishing/queue"
        self.receipts = self.root / "publishing/receipts"
        self.queue.mkdir(parents=True)
        self.receipts.mkdir(parents=True)
        self.channels = self.root / "channels.json"
        self.channels.write_text(json.dumps({"ru": yt.RU_ID}))
        self.data = {"channel":"ru", "source":{"type":"uploaded", "video_id":"xRwwXYXVxSc", "sha256":"a"*64},
                     "metadata":{"title":"Reviewed", "description":"", "type":"short", "made_for_kids":False,
                                 "contains_synthetic_media":False, "category_id":"1", "tags":[]}}
        self.file = self.queue / "reviewed.json"
        self.receipt = self.receipts / self.file.name
        self.prior = {"status":"uploaded", "channel":"ru", "video_id":"xRwwXYXVxSc", "source_sha256":"a"*64}
        self.patches = [patch.object(yt, k, v) for k,v in {
            "ROOT":self.root, "QUEUE":self.queue, "RECEIPTS":self.receipts, "CHANNELS":self.channels}.items()]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.tmp.cleanup()

    def run_main(self, operation):
        self.file.write_text(json.dumps(self.data))
        self.receipt.write_text(json.dumps(self.prior))
        with patch.object(sys, "argv", ["uploader", operation, "--manifest", "publishing/queue/reviewed.json"]):
            yt.main()

    def test_existing_source_metadata_valid_without_local_mp4(self):
        self.assertEqual(yt.validate(self.data, {"ru":yt.RU_ID})[2], None)

    def test_reupload_operations_all_blocked_before_oauth(self):
        for operation in ("check","preflight","reserve","send"):
            with self.subTest(operation=operation), patch.object(yt, "token_for", side_effect=AssertionError("OAuth reached")):
                with self.assertRaisesRegex(ValueError, "NEVER re-upload"):
                    self.run_main(operation)

    def test_missing_id_or_sha_blocked(self):
        for field in ("video_id","sha256"):
            with self.subTest(field=field):
                bad = json.loads(json.dumps(self.data)); del bad["source"][field]
                with self.assertRaises(ValueError): yt.validate(bad, {"ru":yt.RU_ID})

    def test_existing_upload_cannot_schedule_without_date(self):
        with self.assertRaisesRegex(ValueError, "Add publish_at"): self.run_main("schedule")

    def test_schedule_receipt_mismatches_blocked_before_oauth(self):
        self.data["publish_at"]="2099-01-03T15:00:00+02:00"
        for field,value in (("video_id","qYSbQisqEpc"),("source_sha256","b"*64),("channel","en")):
            with self.subTest(field=field):
                original=self.prior[field]; self.prior[field]=value
                with patch.object(yt, "token_for", side_effect=AssertionError("OAuth reached")):
                    with self.assertRaisesRegex(ValueError, "receipt/source mismatch"): self.run_main("schedule")
                self.prior[field]=original

    def test_schedule_uses_existing_id_and_never_uploads(self):
        self.data["publish_at"]="2099-01-03T15:00:00+02:00"
        with patch.object(yt,"token_for",return_value="fake"), patch.object(yt,"verify_channel") as verify, \
             patch.object(yt,"youtube_schedule",return_value="2099-01-03T13:00:00Z") as schedule, \
             patch.object(yt,"youtube_upload",side_effect=AssertionError("New upload attempted")):
            self.run_main("schedule")
            self.assertEqual(schedule.call_args.args[0],"xRwwXYXVxSc")
            verify.assert_called_once_with("fake",yt.RU_ID)
            self.assertEqual(json.loads(self.receipt.read_text())["status"],"scheduled")

if __name__ == "__main__": unittest.main()
