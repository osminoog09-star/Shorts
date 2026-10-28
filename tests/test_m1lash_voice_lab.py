import importlib.util,math,struct,tempfile,unittest,wave
from pathlib import Path
path=Path(__file__).resolve().parents[1]/"tools/voice_lab/wav_audit.py"
spec=importlib.util.spec_from_file_location("voice_lab",path)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class VoiceLab(unittest.TestCase):
 def test_measures_actual_pcm(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"sample.wav"
   with wave.open(str(f),"wb") as out:
    out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000)
    out.writeframes(struct.pack("<"+"h"*2400,*[int(1600*math.sin(i/10)) for i in range(2400)]))
   r=mod.inspect(f)
   self.assertAlmostEqual(r["duration_s"],0.1,places=2)
   self.assertEqual(len(r["sha256"]),64)
   self.assertLess(r["sample_peak_dbfs"],0)
 def test_rejects_non_audio(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"fake.wav";f.write_text("not wav")
   with self.assertRaises((ValueError,EOFError,wave.Error)):mod.inspect(f)
if __name__=="__main__":unittest.main()
