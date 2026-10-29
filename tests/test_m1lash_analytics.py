import importlib.util,unittest
from pathlib import Path
src=Path(__file__).resolve().parents[1]/"tools/analytics/coverage.py"
spec=importlib.util.spec_from_file_location("analytics_coverage",src)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class CoverageTests(unittest.TestCase):
 def test_unknown_metrics_remain_unknown(self):
  r=c.summarize([{"video_id":"A","views_48h":"","views_7d":""},{"video_id":"","views_48h":"900"}])
  self.assertEqual(r["published_with_id"],1)
  self.assertEqual(r["known_counts"]["views_48h"],0)
  self.assertEqual(r["missing_counts"]["views_7d"],1)
if __name__=="__main__":unittest.main()
