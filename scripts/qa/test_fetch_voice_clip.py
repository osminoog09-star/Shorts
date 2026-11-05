#!/usr/bin/env python3
"""Drive owner-only spoken-title fetch guard. No real voice or OAuth in tests."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fetch_voice_clip import download_clip, VoiceClipError
from voice_private_io import approved


def test_wav():
    bio=BytesIO()
    with wave.open(bio,"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000)
        w.writeframes(struct.pack("<h",1234)*36000)
    return bio.getvalue()


class MockDrive:
    def __init__(self,wav,parent_ok=True):
        self.wav=wav
        self.parent_ok=parent_ok
        self.sha=hashlib.sha256(wav).hexdigest()
        self.conf=approved()
        self.urls=[]

    def __call__(self,request,timeout=None):
        u=request.full_url
        self.urls.append(u)
        if "oauth2.googleapis.com/token" in u:
            return BytesIO(b'{"access_token":"mock-private-access"}')
        if "/drive/v3/files/voiceclip12345?fields" in u:
            return BytesIO(json.dumps({"id":"voiceclip12345","mimeType":"audio/wav",
                                        "name":"intro.wav","parents":["jobfolder12345"]}).encode())
        if "/drive/v3/files/jobfolder12345?fields" in u:
            return BytesIO(json.dumps({"id":"jobfolder12345","name":"test_claude",
                                        "mimeType":"application/vnd.google-apps.folder",
                                        "parents":[self.conf["voice_out_folder_id"] if self.parent_ok else "wrongroot123456"]}).encode())
        if "/drive/v3/files?" in u and "pageSize=10" in u:
            return BytesIO(b'{"files":[{"id":"manifest12345","name":"manifest.json"}]}')
        if "/drive/v3/files/manifest12345?alt=media" in u:
            meta={"speaker":"denis","voice_id":"denis-qwen3tts-reference-v1",
                  "engine":"qwen3-tts-local",
                  "utterances":[{"source_file":"audio/intro.wav","sha256":self.sha,"asr_similarity":0.95}]}
            return BytesIO(json.dumps(meta).encode())
        if "/drive/v3/files/voiceclip12345?alt=media" in u:
            return BytesIO(self.wav)
        raise AssertionError("unexpected URL: "+u)


class FetchPrivateTitleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.wav=test_wav()
        self.fake=MockDrive(self.wav)
        self.env={"GDRIVE_REFRESH_TOKEN":"secret-refresh",
                  "YOUTUBE_OAUTH_CLIENT_ID":"client",
                  "YOUTUBE_OAUTH_CLIENT_SECRET":"secret"}

    def test_only_manifest_verified_denis_wav_is_accepted(self):
        target=self.root/"title.wav"
        download_clip("voiceclip12345",self.fake.sha,target,self.env,opener=self.fake)
        self.assertEqual(target.read_bytes(),self.wav)
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),self.fake.sha)
        self.assertNotIn("secret-refresh",str(self.fake.urls))

    def test_wrong_sha_fails_closed_without_output(self):
        target=self.root/"title.wav"
        with self.assertRaisesRegex(VoiceClipError,"manifest"):
            download_clip("voiceclip12345","0"*64,target,self.env,opener=self.fake)
        self.assertFalse(target.exists())

    def test_wrong_parent_is_refused(self):
        target=self.root/"title.wav"
        self.fake.parent_ok=False
        with self.assertRaisesRegex(VoiceClipError,"outside M1lash"):
            download_clip("voiceclip12345",self.fake.sha,target,self.env,opener=self.fake)
        self.assertFalse(target.exists())

    def test_missing_oauth_is_refused(self):
        with self.assertRaisesRegex(Exception,"GDRIVE_REFRESH_TOKEN"):
            download_clip("voiceclip12345",self.fake.sha,self.root/"title.wav",{},opener=self.fake)


if __name__=="__main__":
    unittest.main()
