"""M1lash Voice Studio: CPU-only mock inference, privacy/consistency regressions."""
import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/voice_studio/m1lash_voice.py"
spec = importlib.util.spec_from_file_location("m1lash_voice", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class MockDesign:
    def generate_voice_design(self, **kwargs):
        assert kwargs["language"] in ("Russian", "English")
        assert kwargs["instruct"]
        return [[0.0] * 32000], 16000


class MockBase:
    def create_voice_clone_prompt(self, **kwargs):
        assert kwargs["ref_text"]
        assert kwargs["x_vector_only_mode"] is False
        return "reusable_original_voice_prompt"

    def generate_voice_clone(self, **kwargs):
        assert kwargs["voice_clone_prompt"] == "reusable_original_voice_prompt"
        assert kwargs["text"]
        return [[0.0] * 32000], 16000


def fake_save(destination, audio, rate):
    with wave.open(str(destination), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\0\0" * len(audio[0]))
    return {
        "audio_sha256": mod.sha256(destination), "sample_rate": rate,
        "duration_s": len(audio[0]) / rate, "bytes": destination.stat().st_size,
    }


class VoiceLabTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.voice = mod.read_voices()["orion-ru"]
        self.design_model = MockDesign()
        self.base_model = MockBase()

    def tearDown(self):
        self.temp.cleanup()

    def design(self):
        return mod.create_reference(
            self.voice, self.root / "ref", Path("/dummy"),
            infer=lambda _p, _cpu: self.design_model, save=fake_save)

    def test_original_personas(self):
        profiles = mod.read_voices()
        self.assertTrue({"orion-ru", "nova-ru", "orion-en"} <= profiles.keys())
        self.assertNotIn("Dima", [x["name"] for x in profiles.values()])

    def test_sentence_split_and_no_truncation(self):
        sample = ("Здесь проверили данные космического аппарата. " * 100).strip()
        result = mod.segments(sample)
        self.assertEqual(" ".join(result), " ".join(sample.split()))
        self.assertTrue(all(len(s) <= 240 for s in result))

    def test_empty_text_and_giant_token_rejected(self):
        with self.assertRaises(ValueError):
            mod.segments(" ")
        with self.assertRaises(ValueError):
            mod.segments("x" * 80001)
        with self.assertRaises(ValueError):
            mod.segments("x" * 241)

    def test_references_not_approved(self):
        result = self.design()
        self.assertFalse(result["approved_for_channel"])
        self.assertEqual(result["provenance"], "original_qwen_voice_design")
        self.assertEqual(mod.ref_manifest(self.root / "ref", self.voice)[1]["audio_sha256"],
                         result["audio_sha256"])

    def test_cannot_overwrite_voice(self):
        self.design()
        with self.assertRaises(FileExistsError):
            self.design()

    def test_tampering_reference_blocks_narration(self):
        self.design()
        with (self.root / "ref" / "reference.wav").open("ab") as f:
            f.write(b"tampered")
        with self.assertRaises(ValueError):
            mod.ref_manifest(self.root / "ref", self.voice)

    def test_other_profile_cannot_reuse_voice_without_design(self):
        self.design()
        with self.assertRaises(ValueError):
            mod.ref_manifest(self.root / "ref", mod.read_voices()["nova-ru"])

    def test_narration_and_per_line_manifest(self):
        self.design()
        script = "Эксперимент прошёл успешно. " * 55
        report = mod.synthesize(
            self.voice, self.root / "ref", script, self.root / "takes", Path("/dummy"),
            infer=lambda _p, _cpu: self.base_model, save=fake_save)
        self.assertGreater(report["total_lines"], 1)
        self.assertFalse(report["approved_for_channel"])
        self.assertEqual(report["status"], "EXPERIMENTAL_NOT_APPROVED_FOR_PUBLICATION")
        self.assertEqual(" ".join(x["text"] for x in report["lines"]), " ".join(script.split()))
        self.assertTrue((self.root / "takes" / "manifest.json").is_file())
        self.assertTrue((self.root / "takes" / "narration.wav").is_file())
        self.assertGreater(report["full_wav_duration_s"], report["estimated_total_audio_s"])
        self.assertEqual(report["full_wav_sha256"], mod.sha256(self.root / "takes" / "narration.wav"))

    def test_missing_local_model_rejected(self):
        with self.assertRaises(ValueError):
            mod.check_model(self.root, "design")

    def test_real_local_named_model_preflight(self):
        d = self.root / mod.MODELS["design"]
        d.mkdir()
        (d / "config.json").write_text("{}", encoding="utf-8")
        self.assertEqual(mod.check_model(d, "design"), d.resolve())


if __name__ == "__main__":
    unittest.main()
