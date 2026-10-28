"""No network, API key or FFmpeg required for these adapter guard tests."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("razgon_bridge", Path(__file__).resolve().parents[1] / "tools/razgon2d/bridge.py")
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


class RazgonBridgeTests(unittest.TestCase):
    def test_reject_archive_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bad = root / "bad.zip"
            with zipfile.ZipFile(bad, "w") as z:
                z.writestr("../escape.txt", "no")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                bridge.install(bad, root / "out")
            self.assertFalse((root / "escape.txt").exists())

    def test_reject_incomplete_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            zpath = root / "incomplete.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("skills/make-2d-video/kit/package.json", "{}")
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                bridge.install(zpath, root / "out")

    def test_cast_guard_and_missing_audio(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "dima.wav").write_bytes(b"audio-test")
            manifest = root / "voice_manifest.json"
            good = {"segments": [{"speaker": "dima", "voice_id": "ru-RU-DmitryNeural",
                                   "engine": "edge-tts", "rate": "+0%", "source_file": "dima.wav"}]}
            manifest.write_text(json.dumps(good), encoding="utf-8")
            bridge.voice_gate(manifest)
            good["segments"][0]["voice_id"] = "en-US-GuyNeural"
            manifest.write_text(json.dumps(good), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid voice"):
                bridge.voice_gate(manifest)
            good["segments"][0]["voice_id"] = "ru-RU-DmitryNeural"
            good["segments"][0]["source_file"] = "missing.wav"
            manifest.write_text(json.dumps(good), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing"):
                bridge.voice_gate(manifest)

    def test_story_timeline_guard(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "story").mkdir()
            (root / "config.json").write_text(json.dumps({"aspect": "9:16", "fps": 24, "duration": 5}))
            story = {"duration": 5, "shots": [
                {"id": "s1", "start": 0, "end": 2},
                {"id": "s2", "start": 2, "end": 5}]}
            (root / "story/shots.json").write_text(json.dumps(story))
            bridge.shots_gate(root)
            story["shots"][1]["start"] = 3
            (root / "story/shots.json").write_text(json.dumps(story))
            with self.assertRaisesRegex(ValueError, "Gap/overlap"):
                bridge.shots_gate(root)


if __name__ == "__main__":
    unittest.main()
