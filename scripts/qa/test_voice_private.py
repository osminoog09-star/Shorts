#!/usr/bin/env python3
"""Offline fail-closed regression tests. No real Google OAuth or voice bytes."""
from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from denis_voice_tts import VoiceError, job_config
from voice_private_io import VoicePrivateError, fetch_refs, approved, verify_refs, upload_result


class FakeGoogle:
    def __init__(self, files, corrupt=""):
        self.files = files
        self.corrupt = corrupt
        self.urls = []

    def __call__(self, request, timeout=None):
        self.urls.append(request.full_url)
        if "oauth2.googleapis.com" in request.full_url:
            return BytesIO(b'{"access_token":"fake-token"}')
        if "/drive/v3/files/" in request.full_url:
            file_id = request.full_url.split("/drive/v3/files/")[-1].split("?")[0]
            data = self.files[file_id]
            return BytesIO(b"CORRUPT" if self.corrupt == file_id else data)
        if "uploadType=multipart" in request.full_url:
            # Fake a server-verified result from the multipart request body.
            raw = request.data
            import re
            name = re.search(rb'"name":\s*"([^"]+)"', raw).group(1).decode()
            return BytesIO(json.dumps({"id":"uploaded12345", "name":name}).encode())
        if request.full_url.startswith("https://www.googleapis.com/drive/v3/files?"):
            return BytesIO(b'{"id":"foldernew123456","name":"test_claude"}')
        raise AssertionError(request.full_url)


class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file_ids = {
            "reference_wav":"voicewav123456",
            "reference_text":"voicetext123456",
            "params":"voiceparams123456",
        }
        self.files = {
            "voicewav123456": b"\x01\x02" * 160000,
            "voicetext123456": b"Denis reference text sample longer than 20 bytes",
            "voiceparams123456": b'{"voice_id":"denis-qwen3tts-reference-v1","no_fallback":true,"model_id":"Qwen/Qwen3-TTS-12Hz-1.7B-Base"}'
        }
        a = {
            "reference_wav":("reference_clean.wav","voicewav123456"),
            "reference_text":("ref_text.txt","voicetext123456"),
            "params":("params.json","voiceparams123456"),
        }
        self.data = {
            "version":"denis-qwen3tts-reference-v1",
            "speaker":"denis","voice_id":"denis-qwen3tts-reference-v1",
            "engine":"qwen3-tts-local","no_fallback":True,
            "voice_folder_id":"voicefolder123456",
            "voice_out_folder_id":"voiceout123456",
            "assets":{k:{"name":name, "drive_file_id":id_,
                         "sha256":hashlib.sha256(self.files[id_]).hexdigest()}
                      for k,(name,id_) in a.items()}
        }
        self.manifest = self.root/"approved.json"
        self.manifest.write_text(json.dumps(self.data))
        self.env = {"GDRIVE_REFRESH_TOKEN":"private-refresh",
                    "YOUTUBE_OAUTH_CLIENT_ID":"client","YOUTUBE_OAUTH_CLIENT_SECRET":"secret"}

    def test_fetch_all_three_private_assets_and_verify_hash(self):
        opener=FakeGoogle(self.files)
        dest=self.root/"private"
        fetch_refs(self.manifest,dest,self.env,opener=opener)
        verify_refs(self.manifest,dest)
        self.assertEqual((dest/"reference_clean.wav").read_bytes(),self.files["voicewav123456"])
        self.assertEqual(len(opener.urls),4)
        self.assertNotIn("private-refresh",str(opener.urls))

    def test_tampered_reference_stops_all(self):
        dest=self.root/"private"
        with self.assertRaisesRegex(VoicePrivateError,"SHA256 mismatch"):
            fetch_refs(self.manifest,dest,self.env,opener=FakeGoogle(self.files,corrupt="voicetext123456"))
        self.assertFalse((dest/"reference_clean.wav").exists())

    def test_no_secret_fails_before_downloading_voice(self):
        with self.assertRaisesRegex(Exception,"GDRIVE_REFRESH_TOKEN"):
            fetch_refs(self.manifest,self.root/"private",{},opener=FakeGoogle(self.files))

    def test_approved_wrong_voice_is_rejected(self):
        self.data["voice_id"]="other-male"
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(VoicePrivateError,"чужой голос"):
            approved(self.manifest)

    def test_job_schema_rate_and_duplicate(self):
        path=self.root/"job.json"
        obj={"job_id":"test_claude","speaker":"denis","voice_id":"denis-qwen3tts-reference-v1",
             "utterances":[{"id":"intro","text":"Это проверка моего голоса","rate":1.0}]}
        path.write_text(json.dumps(obj))
        self.assertEqual(job_config(path)[0],"test_claude")
        obj["utterances"][0]["rate"]=2.0
        path.write_text(json.dumps(obj))
        with self.assertRaisesRegex(VoiceError,"rate"):
            job_config(path)

    def test_private_drive_upload_never_uploads_reference(self):
        out=self.root/"result";(out/"audio").mkdir(parents=True)
        wav=out/"audio/intro.wav";wav.write_bytes(b"FAKE_LOCAL_TTS_WAVE"*100)
        obj={"job_id":"test_claude","voice_id":"denis-qwen3tts-reference-v1",
             "utterances":[{"id":"intro","source_file":"audio/intro.wav",
                            "sha256":hashlib.sha256(wav.read_bytes()).hexdigest()}]}
        (out/"manifest.json").write_text(json.dumps(obj))
        opener=FakeGoogle(self.files)
        receipt=upload_result(self.manifest,out,"test_claude",self.env,opener=opener)
        self.assertEqual(len(receipt["files"]),2)
        self.assertTrue(receipt["folder_url"].endswith("foldernew123456"))
        self.assertTrue(all("reference" not in a["name"] for a in receipt["files"]))


if __name__ == "__main__":
    unittest.main()
