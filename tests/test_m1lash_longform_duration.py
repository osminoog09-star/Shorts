"""Offline regressions for >=21m release. No long video needs to be rendered in CI."""
import importlib.util
import math
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts/qa/longform_duration_gate.py"
spec = importlib.util.spec_from_file_location("duration_gate", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def metadata(seconds, w=1920, h=1080, audio=True):
    streams = [{"codec_type": "video", "codec_name": "h264", "width": w, "height": h,
                "duration": str(seconds)}]
    if audio:
        streams.append({"codec_type": "audio", "codec_name": "aac", "duration": str(seconds)})
    return {"format": {"duration": str(seconds)}, "streams": streams}


class MinimumDuration(unittest.TestCase):
    def test_under_fails(self):
        self.assertFalse(m.validate(metadata(1259.999))["pass"])

    def test_exact_21min_passes(self):
        self.assertTrue(m.validate(metadata(1260))["pass"])

    def test_24min_passes(self):
        self.assertTrue(m.validate(metadata(1440))["pass"])

    def test_audio_missing_fails(self):
        self.assertFalse(m.validate(metadata(1440, audio=False))["pass"])

    def test_vertical_fails(self):
        self.assertFalse(m.validate(metadata(1440, w=1080, h=1920))["pass"])

    def test_stream_drift_fails(self):
        x = metadata(1440)
        x["streams"][1]["duration"] = "1438"
        self.assertFalse(m.validate(x)["pass"])

    def test_fake_container_21m_with_90sec_video_fails(self):
        x = metadata(1260)
        x["streams"][0]["duration"] = "90"
        self.assertFalse(m.validate(x)["pass"])

    def test_fake_container_21m_with_short_audio_fails(self):
        x = metadata(1260)
        x["streams"][1]["duration"] = "42"
        self.assertFalse(m.validate(x)["pass"])

    def test_stream_duration_missing_fails(self):
        x = metadata(1460)
        del x["streams"][0]["duration"]
        self.assertFalse(m.validate(x)["pass"])

    def test_nan_inf_and_negative_durations_fail(self):
        for v in ("NaN", "Infinity", "-1", "0"):
            with self.subTest(v=v):
                self.assertFalse(m.validate(metadata(v))["pass"])

    def test_absurd_duration_fail(self):
        self.assertFalse(m.validate(metadata(864000))["pass"])

    def test_mp4_codec_required(self):
        x = metadata(1330)
        x["streams"][0]["codec_name"] = "mpeg2video"
        self.assertFalse(m.validate(x)["pass"])

    def test_missing_container_duration(self):
        x = metadata(1400)
        del x["format"]["duration"]
        self.assertFalse(m.validate(x)["pass"])


if __name__ == "__main__":
    unittest.main()
