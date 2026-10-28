import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
f=Path(__file__).resolve().parents[1]/"tools/m1lash_qa/preflight.py"
s=importlib.util.spec_from_file_location("qa_preflight",f)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class TestProfiles(unittest.TestCase):
 def check(self,w,h,profile):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"test.mp4";file.write_bytes(b"dummy")
   data={"format":{"duration":"40"},"streams":[
    {"codec_type":"video","codec_name":"h264","width":w,"height":h,"duration":"40"},
    {"codec_type":"audio","codec_name":"aac","duration":"40"}]}
   with patch.object(m,"probe",return_value=data),patch.object(m,"call",return_value=(0,"","")):
    return m.analyze(file,profile=profile)
 def test_valid_short(self):
  q=self.check(1080,1920,"short")
  self.assertTrue(q["technical_pass"])
  self.assertFalse(any("below" in x["issue"] for x in q["issues"]))
 def test_invalid_orientation(self):
  self.assertFalse(self.check(1920,1080,"short")["technical_pass"])
 def test_valid_long(self):
  self.assertTrue(self.check(1920,1080,"long")["technical_pass"])
 def test_low_resolution(self):
  self.assertTrue(any(x["severity"]=="P1" for x in self.check(720,1280,"short")["issues"]))
if __name__=="__main__":unittest.main()
