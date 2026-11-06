import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clip_lifecycle import resolve, needed_requests, film_key
import drive_scene_probe as probe

class LifecycleTests(unittest.TestCase):
    def test_live_repo(self):
        root=Path(__file__).resolve().parents[2]
        rows=json.loads((root/'publishing/clip_requests.json').read_text())['items']
        needed={r['id'] for r in needed_requests(rows,root)}
        self.assertNotIn('w45-oppenheimer-trinity', needed,
                         'Kino008 already has a verified PRIVATE video, never ask to upload movie again')
        f={f['film']:f for f in resolve(root)['items']}
        self.assertEqual(f['Одержимость (2014)']['state'],'published')
        self.assertEqual(f['Старикам тут не место (2007)']['state'],'in_progress')
        self.assertIn(f['Оппенгеймер (2023)']['state'], ('in_progress','published'))
        self.assertTrue(any(p.get('youtube_id')=='G4IMzvrv1Zw' for p in f['Оппенгеймер (2023)']['projects']))

    def test_lifecycle_and_stale_asr(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            def save(path, value):
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
            req=[{'id':'req','film':'Whiplash (2014)','status':'нужен'}]
            save('publishing/film_projects.json',{'items':[]})
            self.assertEqual(len(needed_requests(req,root)),1)
            save('publishing/queue.json',{'items':[{'id':'new','film':'Одержимость (2014)','status':'draft'}]})
            self.assertEqual(resolve(root)['items'][0]['state'],'in_progress')
            self.assertEqual(needed_requests(req,root),[])
            save('publishing/receipts/new.json',{'video_id':'abc','status':'scheduled','publish_at_utc':'2000-01-01T00:00:00Z','privacy_status':'private'})
            self.assertEqual(resolve(root)['items'][0]['state'],'in_progress')  # date passed != public
            save('publishing/clip_requests.json',{'items':req})
            save('publishing/drive_scan.json',{'status':'ok','items':[{'id':'req','status':'фильм найден','file_url':'stale'}]})
            with patch.object(probe,'ROOT',root),patch.object(probe,'REQUESTS',root/'publishing/clip_requests.json'),patch.object(probe,'SCAN',root/'publishing/drive_scan.json'),patch.object(probe,'STATE',root/'state.json'):
                self.assertEqual(probe.pending()[0],[])
            save('reports/youtube/pulse.json',{'recent':[{'id':'abc'}]})
            self.assertEqual(resolve(root)['items'][0]['state'],'published')
            save('publishing/queue.json',{'items':[{'id':'new','film':'Одержимость (2014)'},{'id':'next','film':'Одержимость (2014)'}]})
            self.assertEqual(resolve(root)['items'][0]['state'],'in_progress')

    def test_year_and_aliases(self):
        self.assertEqual(film_key('Whiplash (2014)'),film_key('Одержимость (2014)'))
        self.assertNotEqual(film_key('Бэтмен (2022)'),film_key('Бэтмен (1989)'))

if __name__=='__main__': unittest.main()
