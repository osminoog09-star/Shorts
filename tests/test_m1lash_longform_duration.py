import importlib.util
import unittest
from pathlib import Path
path=Path(__file__).resolve().parents[1]/"scripts/qa/longform_duration_gate.py"
spec=importlib.util.spec_from_file_location("duration_gate",path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def metadata(seconds, w=1920, h=1080, audio=True):
    streams=[{"codec_type":"video","width":w,"height":h,"duration":str(seconds)}]
    if audio:streams.append({"codec_type":"audio","duration":str(seconds)})
    return {"format":{"duration":str(seconds)},"streams":streams}
class MinimumDuration(unittest.TestCase):
    def test_under_fails(self):self.assertFalse(m.validate(metadata(1259.9))["pass"])
    def test_exact_21min_passes(self):self.assertTrue(m.validate(metadata(1260))["pass"])
    def test_24min_passes(self):self.assertTrue(m.validate(metadata(1440))["pass"])
    def test_audio_missing_fails(self):self.assertFalse(m.validate(metadata(1440,audio=False))["pass"])
    def test_vertical_fails(self):self.assertFalse(m.validate(metadata(1440,w=1080,h=1920))["pass"])
    def test_drift_fails(self):
        x=metadata(1440);x["streams"][1]["duration"]="1410"
        self.assertFalse(m.validate(x)["pass"])
if __name__=="__main__":unittest.main()
