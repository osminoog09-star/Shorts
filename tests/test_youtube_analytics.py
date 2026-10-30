import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from scripts.youtube_analytics import Client, ApiError, inventory, period_bounds, update_journal


class AnalyticsTests(unittest.TestCase):
    def test_paginated_reports(self):
        client = Client('fake')
        calls = []
        def get(url, params):
            calls.append(dict(params))
            n = 200 if params['startIndex'] == 1 else 1
            return dict(columnHeaders=[{'name':'video'}, {'name':'views'}], rows=[[str(i), 0] for i in range(n)])
        client.get = get
        rows = client.query(date(2026,1,1), date(2026,1,2), 'video', ['views'])
        self.assertEqual(len(rows), 201)
        self.assertEqual(calls[1]['startIndex'], 201)

    def test_unsupported_and_zero(self):
        client = Client('fake')
        def query(a,b,c,metrics,filters):
            if metrics == ['engagedViews']:
                raise ApiError(400, 'test')
            return [{'video':'id', 'views':0}]
        client.query = query
        rows, missing = client.metrics(1,2,'video', metrics=['views','engagedViews'])
        self.assertEqual(rows[0]['views'], 0)
        self.assertIsNone(rows[0]['engagedViews'])
        self.assertEqual(missing, ['engagedViews'])

    def test_auth_failure_not_hidden(self):
        client = Client('fake')
        client.query = lambda *a: (_ for _ in ()).throw(ApiError(403, 'test'))
        with self.assertRaises(ApiError):
            client.metrics(1,2,'video')

    def test_calendar_year_boundary(self):
        periods = period_bounds(date(2027,1,1))
        self.assertEqual(periods[1][1:4], (date(2026,12,1),date(2026,12,31),'2026-12'))
        self.assertEqual(periods[0][1:3], (date(2026,12,21),date(2026,12,27)))

    def test_sunday_includes_current_week_provisionally(self):
        self.assertEqual(period_bounds(date(2026,11,1))[0][1:3], (date(2026,10,26),date(2026,11,1)))

    def test_journal_preserves_editorial_and_age_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'videos.csv'
            path.write_text('date,time,video_id,title,kind,style,length_s,notes,views_48h,views_7d\n2026-01-01,10:00,a,Title,short,S5,45,editorial,0,99\n2026-01-02,10:00,,Draft,short,S3,40,pending,,\n')
            videos = [dict(video_id='a',title='Title changed',duration='PT45S',privacy='public',published_at='2026-01-01T08:00:00Z'),
                      dict(video_id='b',title='Draft',duration='PT1M2S',privacy='private',published_at='2026-01-02T08:00:00Z')]
            update_journal(path, videos, dict(start='2026-01-01',end='2026-01-04',videos={'a':{'views':0}}), 'now')
            with path.open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]['style'], 'S5')
            self.assertEqual(rows[0]['views_48h'], '0')
            self.assertEqual(rows[0]['views_7d'], '99')
            self.assertEqual(rows[0]['yt_views'], '0')
            self.assertEqual(rows[2]['date'], '')
            self.assertEqual(rows[2]['yt_views'], '')
            self.assertEqual(rows[2]['kind'], 'unknown')
            self.assertEqual(rows[2]['length_s'], '62')

    def test_inventory_pagination(self):
        client = Client('fake')
        def get(url, params):
            if url.endswith('channels'):
                return {'items':[{'contentDetails':{'relatedPlaylists':{'uploads':'pl'}},'statistics':{'viewCount':'5'}}]}
            if url.endswith('playlistItems'):
                return {'items':[{'contentDetails':{'videoId':'b' if params.get('pageToken') else 'a'}}], **({} if params.get('pageToken') else {'nextPageToken':'next'})}
            return {'items':[{'id':v,'snippet':{'title':v,'publishedAt':'2026-01-01T00:00:00Z'},'contentDetails':{'duration':'PT2S'},'status':{'privacyStatus':'public'}} for v in params['id'].split(',')]}
        client.get = get
        videos, stats = inventory(client,'channel')
        self.assertEqual([v['video_id'] for v in videos], ['a','b'])
        self.assertEqual(stats['viewCount'], '5')

    def test_main_writes_snapshot_and_periods(self):
        from scripts import youtube_analytics as module
        class FakeClient:
            def __init__(self, token):
                pass
            def metrics(self, start, end, dim, **kwargs):
                if dim == 'video':
                    return ([dict(video='a', views=0, likes=0)], ['engagedViews'])
                if dim == 'day':
                    return ([dict(day=str(end), views=0)], [])
                return ([], [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'publishing').mkdir()
            (root/'publishing/channels.json').write_text('{"ru":"expected"}')
            (root/'reports').mkdir()
            (root/'reports/videos.csv').write_text('date,time,video_id,title,kind,notes,length_s\n')
            video = dict(video_id='a',title='Title',duration='PT5S',privacy='public',published_at='2026-10-22T10:00:00Z')
            with patch.object(module,'ROOT',root), patch.object(module,'Client',FakeClient), patch.object(module,'token_for',return_value='fake'), patch.object(module,'verify_channel') as verify, patch.object(module,'inventory',return_value=([video],{})), patch('sys.argv',['collector','--date','2026-10-30']):
                module.main()
            verify.assert_called_once_with('fake','expected')
            data = json.loads((root/'reports/youtube/daily/2026-10-30.json').read_text())
            self.assertEqual(data['videos']['a']['views'],0)
            self.assertEqual(data['traffic']['videos']['a'],[])
            self.assertEqual(data['snapshot_date'],'2026-10-30')
            self.assertEqual(len(list((root/'reports/youtube/weekly').glob('*.json'))),1)
            self.assertEqual(len(list((root/'reports/youtube/monthly').glob('*.json'))),1)


if __name__ == '__main__':
    unittest.main()
