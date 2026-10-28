import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "tools/studio/production_inputs.py"
spec = importlib.util.spec_from_file_location("render_params", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProductionArgs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        project = self.root / "longform" / "test"
        (project / "audio").mkdir(parents=True)
        (project / "audio" / "mix.m4a").write_bytes(b"fake audio for argument tests")
        (project / "audio" / "cues.json").write_text('{"duration": 1380}', encoding="utf-8")
        self.data = {"project": "test", "short": "", "audio": "audio/mix.m4a",
                     "chunks": "20", "fps": "30", "base_run": "", "only": ""}

    def tearDown(self):
        self.temp.cleanup()

    def check(self, **changes):
        return module.validate_input({**self.data, **changes}, self.root, require_timeline=True)

    def test_valid_full_render(self):
        self.assertEqual(len(self.check()["idx"]), 20)

    def test_valid_partial_render(self):
        self.assertEqual(self.check(base_run="123456", only="1,7,13")["idx"], [1, 7, 13])

    def test_script_injection_rejected(self):
        for payload in ("test'; echo hacked; '", "../test", "$(id)", "test/path", "test\nbad"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.check(project=payload)

    def test_missing_audio_rejected(self):
        with self.assertRaises(ValueError):
            self.check(audio="audio/other.m4a")

    def test_unsafe_audio_path_rejected(self):
        with self.assertRaises(ValueError):
            self.check(audio="../secret.wav")

    def test_no_base_run_for_partial_rejected(self):
        with self.assertRaises(ValueError):
            self.check(only="0,1")

    def test_invalid_only_and_duplicates_rejected(self):
        for chunk in ("1,1", "1,21", "1; echo hacked", "-1"):
            with self.subTest(chunk=chunk), self.assertRaises(ValueError):
                self.check(base_run="100", only=chunk)

    def test_invalid_fps_and_chunk_count_rejected(self):
        for value in ("0", "33", "1; echo x", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(chunks=value)
        with self.assertRaises(ValueError):
            self.check(fps="120")

    def test_20_minute_cues_rejected(self):
        cue = self.root / "longform" / "test" / "audio" / "cues.json"
        cue.write_text('{"duration": 1200}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.check()

    def test_nonfinite_cues_rejected(self):
        cue = self.root / "longform" / "test" / "audio" / "cues.json"
        cue.write_text('{"duration": NaN}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.check()


if __name__ == "__main__":
    unittest.main()
