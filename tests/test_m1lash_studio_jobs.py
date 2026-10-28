"""Issue-to-research regression tests: owner-only, no fake YouTube observation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

src=Path(__file__).resolve().parents[1]/"motion-studio/automation/prepare_job.py"
spec=importlib.util.spec_from_file_location("studio_job",src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def job_issue(data, owner="osminoog09-star"):
    return {"user":{"login":owner},"body":"M1LASH_JOB_START\n"+json.dumps(data)+"\nM1LASH_JOB_END"}


def sample():
    return {"schema":1,"source":"m1lash-studio-v2",
      "topic":"Как роботы изменят жизнь","format":"long","duration_s":1500,
      "language":"ru","voice":"dima","style":"S9","depth":"D3",
      "agents":["research","factcheck","script","director","voice","editor","quality"],
      "sources":["https://www.nasa.gov/news-release/test"],
      "request":"prepare_only","publish":False}


class StudioJobs(unittest.TestCase):
 def test_owner_longform(self):
  j=m.parse_issue(job_issue(sample()))
  self.assertEqual(j["duration_s"],1500)
 def test_non_owner_rejected(self):
  with self.assertRaises(ValueError):m.parse_issue(job_issue(sample(),owner="stranger"))
 def test_20_minutes_rejected(self):
  d=sample();d["duration_s"]=1200
  with self.assertRaises(ValueError):m.parse_issue(job_issue(d))
 def test_publishing_rejected(self):
  d=sample();d["publish"]=True
  with self.assertRaises(ValueError):m.parse_issue(job_issue(d))
 def test_invalid_styles_rejected(self):
  d=sample();d["style"]="X99"
  with self.assertRaises(ValueError):m.parse_issue(job_issue(d))
 def test_reference_metadata_no_fake_video(self):
  ref={"schema":1,"source":"m1lash-studio-v2","request":"reference_analysis",
       "video_id":"9hE5-98ZeCg","video_url":"https://www.youtube.com/watch?v=9hE5-98ZeCg",
       "topic":"Разбор видео","publish":False}
  with tempfile.TemporaryDirectory() as td:
   report=m.prepare(m.parse_issue(job_issue(ref)),td,key="",get=lambda _:{"title":"My Title","author_name":"Demo Channel"})
   self.assertEqual(report,"NOT_RUN_NO_GEMINI_KEY")
   data=json.loads((Path(td)/"source.json").read_text())
   self.assertEqual(data["metadata"]["title"],"My Title")
   self.assertNotIn("VIDEO_RESEARCH",data["status"])
   self.assertIn("ещё не просмотрено",(Path(td)/"reference_analysis.md").read_text())
 def test_video_analysis_with_mock(self):
  ref={"schema":1,"source":"m1lash-studio-v2","request":"reference_analysis",
       "video_id":"9hE5-98ZeCg","video_url":"https://www.youtube.com/watch?v=9hE5-98ZeCg",
       "publish":False}
  with tempfile.TemporaryDirectory() as td:
   result=m.prepare(m.parse_issue(job_issue(ref)),td,key="fake-key",
        get=lambda _:{"title":"Demo","author_name":"Channel"},
        analyze=lambda i,k:"timestamp 00:00:10: наблюдаем движение камеры. "*10)
   self.assertEqual(result,"MODEL_VIDEO_RESEARCH_NEEDS_HUMAN_REVIEW")
   self.assertIn("наблюдаем",(Path(td)/"reference_analysis.md").read_text())
 def test_job_artifact_content_honest(self):
  with tempfile.TemporaryDirectory() as td:
   result=m.prepare(sample(),td)
   self.assertEqual(result,"PRODUCTION_BRIEF_ONLY_NO_VIDEO_RENDERED")
   info=json.loads((Path(td)/"production_brief.json").read_text())
   self.assertEqual(len(info["acts"]),5)
   self.assertFalse(info["publish"])
   self.assertEqual(info["acts"][-1]["end_s"],1500)
if __name__=="__main__":unittest.main()
