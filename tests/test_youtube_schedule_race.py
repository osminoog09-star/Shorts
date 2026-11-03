import importlib.util
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

spec=importlib.util.spec_from_file_location('uploader_race',Path(__file__).resolve().parents[1]/'scripts/youtube_direct.py')
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)

class ScheduleRaceTests(unittest.TestCase):
    def test_changed_date_rejected_before_oauth(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);queue=root/'publishing/queue';queue.mkdir(parents=True)
            (queue/'one.json').write_text(json.dumps({'publish_at':'2099-01-03T15:00:00+02:00'}))
            with patch.object(u,'ROOT',root),patch.object(u,'QUEUE',queue),patch.object(u,'token_for',side_effect=AssertionError('OAuth reached')),patch.object(sys,'argv',['upload','schedule','--manifest','publishing/queue/one.json','--expected-publish-at','2099-01-04T15:00:00+02:00']):
                with self.assertRaisesRegex(ValueError,'Stale schedule request'):u.main()

    def test_changed_request_id_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);queue=root/'publishing/queue';queue.mkdir(parents=True)
            (queue/'one.json').write_text(json.dumps({'schedule_request':{'id':'new'}}))
            with patch.object(u,'ROOT',root),patch.object(u,'QUEUE',queue),patch.object(sys,'argv',['upload','schedule','--manifest','publishing/queue/one.json','--expected-request-id','old']):
                with self.assertRaisesRegex(ValueError,'Stale schedule request ID'):u.main()

    def test_reserved_slot_blocks_other_video_before_manifest_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);queue=root/'publishing/queue';queue.mkdir(parents=True)
            (root/'publishing/schedule_requests.json').write_text(json.dumps({'requests':{'other':{'at':'2099-01-03T15:00:00+02:00','kind':'short'}}}))
            current={'channel':'ru','source':{'type':'uploaded','video_id':'xRwwXYXVxSc','sha256':'a'*64},'metadata':{'title':'One','description':'','type':'short','made_for_kids':False,'contains_synthetic_media':False},'publish_at':'2099-01-03T15:00:00+02:00'}
            with patch.object(u,'ROOT',root),patch.object(u,'QUEUE',queue):
                with self.assertRaisesRegex(ValueError,'Collision'):u.validate_queue(queue/'one.json',current,{'ru':u.RU_ID})

    def test_readback_must_match_exact_date_and_private_status(self):
        when=dt.datetime(2099,1,3,13,tzinfo=dt.timezone.utc)
        data={'metadata':{'made_for_kids':False,'contains_synthetic_media':False}}
        put=Mock(ok=True);put.json.return_value={'status':{'publishAt':'2099-01-03T13:00:00Z'}}
        for status,at in [('private','2099-01-04T13:00:00Z'),('public','2099-01-03T13:00:00Z'),('private','2099-01-03T13:00:00Z')]:
            get=Mock(ok=True);get.json.return_value={'items':[{'id':'xRwwXYXVxSc','status':{'privacyStatus':status,'publishAt':at}}]}
            with self.subTest(status=status,at=at),patch.object(u.requests,'put',return_value=put),patch.object(u.requests,'get',return_value=get),patch.object(u.time,'sleep'):
                if status=='private' and at=='2099-01-03T13:00:00Z':self.assertEqual(u.youtube_schedule('xRwwXYXVxSc',data,when,'fake'),at)
                else:
                    with self.assertRaisesRegex(RuntimeError,'readback differs'):u.youtube_schedule('xRwwXYXVxSc',data,when,'fake')

    def test_stale_readback_retries_reads_without_repeating_put(self):
        data={'metadata':{'made_for_kids':False,'contains_synthetic_media':False}}
        def response(at):
            r=Mock(ok=True);r.json.return_value={'items':[{'id':'xRwwXYXVxSc','status':{'privacyStatus':'private','publishAt':at}}]};return r
        put=Mock(ok=True);put.json.return_value={'status':{'publishAt':'2099-01-03T13:00:00Z'}}
        with patch.object(u.requests,'put',return_value=put) as write,patch.object(u.requests,'get',side_effect=[response('2099-01-04T13:00:00Z'),response('2099-01-03T13:00:00Z')]) as read,patch.object(u.time,'sleep'):
            self.assertEqual(u.youtube_schedule('xRwwXYXVxSc',data,dt.datetime(2099,1,3,13,tzinfo=dt.timezone.utc),'fake'),'2099-01-03T13:00:00Z')
            self.assertEqual(write.call_count,1);self.assertEqual(read.call_count,2)

if __name__=='__main__':unittest.main()
