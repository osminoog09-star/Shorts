import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"tools/studio/prompt_compose.py"
s=importlib.util.spec_from_file_location("composer",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PromptLab(unittest.TestCase):
 def test_short_original_style(self):
  x=m.build("X09","Робот проверяет пропуск","short",44)
  self.assertIn("physical prop contact",x["director_prompt"])
  self.assertIn("ru-RU-DmitryNeural",x["voice_prompt"])
 def test_long_21_min(self):
  x=m.build("X07","Что на самом деле известно о Марсе","long",1260)
  self.assertEqual(x["duration_s"],1260)
  self.assertIn("4-5 acts",x["script_prompt"])
 def test_short_long_rejected(self):
  with self.assertRaises(ValueError):m.build("X01","Марс","long",899)
 def test_missing_style_rejected(self):
  with self.assertRaises(ValueError):m.build("X99","Марс","short",40)
 def test_catalog_all_have_key_fields(self):
  import json
  styles=json.loads(m.REGISTRY.read_text(encoding="utf-8"))["styles"]
  self.assertEqual(len(styles),12)
  self.assertEqual(len({x["id"] for x in styles}),12)
  self.assertTrue(all(x["visual"] and x["motion"] and x["negative"] for x in styles))
if __name__=="__main__":unittest.main()
