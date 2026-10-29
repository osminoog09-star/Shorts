import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/m1lash_calendar_audit.py"
spec=importlib.util.spec_from_file_location("m1calendar",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CalendarTests(unittest.TestCase):
 def test_collision(self):
  rows=[{"date":"2026-11-02","time":h,"kind":"short","title":h} for h in ("10:00","12:00","16:00")]
  issues=m.audit(rows)["issues"]
  self.assertTrue(any("two" in i["issue"] for i in issues))
  self.assertTrue(any("six hours" in i["issue"] for i in issues))
 def test_no_fake_publication(self):
  r=m.audit([{"date":"2026-11-02","time":"10:00","kind":"short","title":"A","notes":"scheduled","video_id":""}])
  self.assertEqual(len(r["scheduled_without_youtube_id"]),1)
  self.assertIn("no live",r["scope"])
if __name__=="__main__":unittest.main()
