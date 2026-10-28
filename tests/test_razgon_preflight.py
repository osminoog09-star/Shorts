import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "tools/razgon/preflight.py"
spec = importlib.util.spec_from_file_location("preflight", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class VoiceGateTests(unittest.TestCase):
    def test_author_voices(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "voice.json"
            p.write_text(json.dumps({"segments": [
                {"speaker":"dima","voice_id":"ru-RU-DmitryNeural","engine":"edge-tts","source_file":"d.wav","rate":"-5%","role":"narration"},
                {"speaker":"sveta","voice_id":"ru-RU-SvetlanaNeural","engine":"edge-tts","source_file":"s.wav","rate":"-5%","role":"dialogue"},
                {"speaker":"dima","voice_id":"ru-RU-DmitryNeural","engine":"edge-tts","source_file":"end.wav","rate":"-5%","role":"cta"}
            ]}))
            self.assertEqual(module.check_voice(p)["voice_gate"], "PASS")
            bad = json.loads(p.read_text())
            bad["segments"][-1]["voice_id"] = "en-US-LiamNeural"
            p.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                module.check_voice(p)

    def test_missing_cta(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "voice.json"
            p.write_text(json.dumps({"segments":[
                {"speaker":"dima","voice_id":"ru-RU-DmitryNeural","engine":"edge-tts","source_file":"d.wav","rate":"-5%","role":"narration"}]}))
            with self.assertRaisesRegex(ValueError, "CTA"):
                module.check_voice(p)

if __name__ == "__main__":
    unittest.main()
