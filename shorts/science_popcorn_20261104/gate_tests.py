#!/usr/bin/env python3
"""Offline regression tests: only popcorn master, Denis voice, true timestamps."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
target=ROOT/"shorts/science_popcorn_20261104/build_private_master.py"
spec=importlib.util.spec_from_file_location("popcorn_master",str(target))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def bogus_timeline(**changes):
    data={
      "id":"science_popcorn_20261104","theme":"popcorn",
      "actual_audio":False,"voice_id":"denis-qwen3tts-reference-v1",
      "engine":"qwen3-tts-local",
      "segments":[],"caps":[],"cuts":[],
      "total":37,
    }
    data.update(changes)
    return data

class PopcornVoiceGates(unittest.TestCase):
    def test_single_episode_isolation(self):
        m.gate_basics()
        self.assertEqual(m.SPEC["id"],"science_popcorn_20261104")
        self.assertEqual(len(m.SPEC["scenes"]),6)
        self.assertEqual(sum(len(s["voice"]) for s in m.SPEC["scenes"]),12)
        self.assertNotIn("vacuum",(m.HERE/"film.html").read_text(encoding="utf8").lower())
    def test_denies_fabricated_caption_timing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError,"provisional"):
                m.validate_actual(bogus_timeline(),Path(d)/"absent.wav",Path(d))
    def test_denies_other_channel_or_theme(self):
        for changes in [{"id":"ai_vacuum_20261104"},{"theme":"vacuum"}]:
            with self.subTest(changes=changes),tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(RuntimeError,"wrong film"):
                    m.validate_actual(bogus_timeline(**changes),Path(d)/"absent.wav",Path(d))
    def test_denies_dima_and_wrong_engine(self):
        for changes in [{"voice_id":"ru-RU-DmitryNeural","actual_audio":True},
                        {"engine":"edge-tts","actual_audio":True}]:
            with self.subTest(changes=changes),tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(RuntimeError,"voice identity mismatch"):
                    m.validate_actual(bogus_timeline(**changes),Path(d)/"absent.wav",Path(d))
    def test_denies_owner_voice_inside_public_repo(self):
        with self.assertRaisesRegex(RuntimeError,"inside public"):
            m.protect_private(ROOT/"videos"/"owner_voice.wav")
    def test_denies_unapproved_outro(self):
        with tempfile.TemporaryDirectory() as d:
            sample=Path(d)/"fake-outro.mp4"
            sample.write_bytes(b"not approved")
            with self.assertRaisesRegex(RuntimeError,"SHA"):
                m.install_verified_outro(sample)
    def test_no_dima_or_youtube_write_in_source(self):
        src=target.read_text(encoding="utf8")
        self.assertNotIn("edge_tts",src)
        self.assertNotIn("youtube_direct",src)
        self.assertNotIn("m1lash_outro_v1",src)
        self.assertIn("approved.json",src)
        self.assertIn("actual_audio",src)

if __name__=="__main__":
    unittest.main(verbosity=2)
