"""Model-free end-to-end checks: sourced pack, all stages, optional real draft via mock API."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"motion-studio/automation"

def import_file(name):
    spec=importlib.util.spec_from_file_location(name,BASE/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

p=import_file("run_agents")
c=import_file("progress_comment")

def issue(number=54,owner="osminoog09-star",fmt="long",duration=1500):
    job={"schema":1,"source":"m1lash-studio-v2","topic":"Как появился табак",
         "brief":"Взглянуть на историю, зависимость и последствия","format":fmt,
         "duration_s":duration,"language":"ru","voice":"dima","style":"X05",
         "depth":"D25","sources":[],
         "agents":["research","factcheck","script","director","image","animation","voice","editor","quality","youtube"],
         "request":"prepare_only","publish":False}
    return {"number":number,"title":"[M1LASH STUDIO] Как появился табак",
            "user":{"login":owner},
            "body":"M1LASH_JOB_START\n"+json.dumps(job)+"\nM1LASH_JOB_END"}

class ProductionPipeline(unittest.TestCase):
    def test_curated_pack_has_independent_sources_per_claim(self):
        pack=p.load_pack(54)
        self.assertEqual(len(pack["chapters"]),7)
        self.assertGreaterEqual(len(pack["sources"]),8)
        self.assertTrue(p.valid_sources(pack))
        for claim in pack["claims"]:
            self.assertGreaterEqual(len(set(claim["sources"])),2)

    def test_real_source_files_without_any_ai_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            status=p.run(issue(),tmp)
            self.assertEqual(status["status"],"EDITORIAL_PACKAGE_NEEDS_REVIEW")
            rows={x["id"]:x for x in status["stages"]}
            self.assertEqual(rows["research"]["status"],"ready")
            self.assertEqual(rows["script"]["status"],"blocked")
            self.assertEqual(rows["voice"]["status"],"blocked")
            self.assertEqual(rows["editor"]["status"],"blocked")
            self.assertFalse(status["output_is_final_video"])
            self.assertTrue((Path(tmp)/"facts.json").is_file())
            self.assertTrue((Path(tmp)/"research.md").is_file())
            self.assertTrue((Path(tmp)/"director_and_art_prompts.md").is_file())
            self.assertFalse((Path(tmp)/"script_draft_ru.md").exists())
            facts=json.loads((Path(tmp)/"facts.json").read_text())
            self.assertTrue(all(x["release_status"]=="REQUIRES_FACT_CHECK" for x in facts["claims"]))
            self.assertFalse(json.loads((Path(tmp)/"scene_cues_provisional.json").read_text())["renderable"])

    def test_optionally_generate_real_length_text_in_chunks(self):
        def mock(prompt,key):
            self.assertEqual(key,"mock-private-key")
            self.assertIn("Главный голос Дима",prompt)
            return ("Важная оригинальная историческая мысль подтверждается источниками [F01]. " * 80).strip()
        with tempfile.TemporaryDirectory() as tmp:
            report=p.run(issue(),tmp,key="mock-private-key",text_ai_enabled=True,generate=mock)
            self.assertEqual(next(x for x in report["stages"] if x["id"]=="script")["status"],"needs_review")
            self.assertEqual(len(list(Path(tmp).glob("script_chapter_*.md"))),7)
            metrics=json.loads((Path(tmp)/"script_metrics.json").read_text())
            self.assertEqual(metrics["status"],"DRAFT_NEEDS_EDITOR_AND_SOURCE_REVIEW")
            self.assertGreater(metrics["draft_words"],2600)
            self.assertEqual(next(x for x in report["stages"] if x["id"]=="voice")["status"],"blocked")

    def test_model_exception_keeps_accurate_status_not_fake_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=p.run(issue(),tmp,key="test",text_ai_enabled=True,
                    generate=lambda x,y:(_ for _ in ()).throw(RuntimeError("API not available")))
            self.assertEqual(next(x for x in r["stages"] if x["id"]=="script")["status"],"blocked")
            self.assertFalse((Path(tmp)/"script_draft_ru.md").exists())

    def test_unknown_issue_honest_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=p.run(issue(number=950),tmp)
            self.assertEqual(r["status"],"BLOCKED_NEEDS_SOURCE_RESEARCH")
            self.assertFalse((Path(tmp)/"facts.json").exists())

    def test_only_owner_can_start(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            p.run(issue(owner="bad-user"),tmp)

    def test_status_comment_parses_as_safe_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=p.run(issue(),tmp)
            comment=c.make_comment(r,"osminoog09-star/Shorts","123456789")
            self.assertIn("M1LASH_STAGE_STATUS_BEGIN",comment)
            raw=comment.split("M1LASH_STAGE_STATUS_BEGIN\n")[1].split("\nM1LASH_STAGE_STATUS_END")[0]
            summary=json.loads(raw)
            self.assertEqual(summary["run_id"],123456789)
            self.assertFalse(summary["output_is_final_video"])
            self.assertEqual(len(summary["stages"]),10)
            self.assertNotIn("GEMINI_API_KEY",comment)

    def test_unsafe_source_rejected(self):
        pack=p.load_pack(54)
        pack["sources"][0]["url"]="http://127.0.0.1/internal"
        self.assertFalse(p.valid_sources(pack))

if __name__=="__main__":
    unittest.main()
