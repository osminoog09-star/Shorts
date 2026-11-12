import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.youtube_analytics import load_backfill

mod = load_backfill()


def snapshot(folder, day, fetched_at, items):
    (folder / f'{day}.json').write_text(json.dumps(dict(fetched_at=fetched_at, inventory=items)), encoding='utf-8')


def item(vid, views, privacy='public', published='2026-11-01T08:00:00Z', title='Ролик #shorts'):
    return dict(video_id=vid, title=title, published_at=published, duration='PT40S', privacy=privacy,
                statistics=dict(viewCount=str(views)))


class BackfillTests(unittest.TestCase):
    def run_backfill(self, rows, snapshots):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            daily = root / 'daily'
            daily.mkdir()
            for day, fetched_at, items in snapshots:
                snapshot(daily, day, fetched_at, items)
            fields = ['date', 'time', 'kind', 'video_id', 'title', 'format', 'length_s', 'views_48h', 'views_7d']
            path = root / 'videos.csv'
            with path.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            filled = mod.backfill(path, daily, root)
            with path.open(encoding='utf-8', newline='') as f:
                return filled, list(csv.DictReader(f))

    def test_fills_nearest_snapshot_and_records_real_age(self):
        filled, rows = self.run_backfill(
            [dict(video_id='a', title='Ролик #shorts', kind='unknown')],
            [('2026-11-01', '2026-11-01T15:00:00+00:00', [item('a', 100)]),
             ('2026-11-03', '2026-11-03T15:00:00+00:00', [item('a', 500)]),
             ('2026-11-08', '2026-11-08T15:00:00+00:00', [item('a', 700)])])
        row = rows[0]
        self.assertEqual((row['views_48h'], row['views_48h_age_h']), ('500', '55.0'))
        self.assertEqual((row['views_7d'], row['views_7d_age_h']), ('700', '175.0'))
        self.assertEqual((row['date'], row['time'], row['kind']), ('2026-11-01', '10:00', 'short'))
        self.assertEqual(filled['views_48h'], 1)

    def test_no_snapshot_near_age_stays_empty_not_zero(self):
        _, rows = self.run_backfill(
            [dict(video_id='a', title='Ролик #shorts', kind='unknown')],
            [('2026-11-01', '2026-11-01T15:00:00+00:00', [item('a', 100)]),
             ('2026-11-05', '2026-11-05T15:00:00+00:00', [item('a', 600)])])
        self.assertEqual((rows[0]['views_48h'], rows[0]['views_7d']), ('', ''))

    def test_existing_value_and_private_video_untouched(self):
        _, rows = self.run_backfill(
            [dict(video_id='a', title='Ролик #shorts', kind='short', views_48h='42'),
             dict(video_id='b', title='Закрытый #shorts', kind='unknown')],
            [('2026-11-03', '2026-11-03T08:00:00+00:00', [item('a', 500), item('b', 9, privacy='private')])])
        self.assertEqual(rows[0]['views_48h'], '42')
        self.assertEqual((rows[1]['views_48h'], rows[1]['date']), ('', ''))

    def test_video_opened_long_after_published_at_is_unknown(self):
        _, rows = self.run_backfill(
            [dict(video_id='a', title='Ролик #shorts', kind='unknown')],
            [('2026-11-01', '2026-11-01T15:00:00+00:00', [item('a', 0, privacy='private')]),
             ('2026-11-08', '2026-11-08T08:00:00+00:00', [item('a', 300)])])
        self.assertEqual((rows[0]['views_7d'], rows[0]['date']), ('', ''))

    def test_kind_is_not_guessed_from_duration_alone(self):
        self.assertIsNone(mod.classify_kind('Без хештега', 40, None))
        self.assertEqual(mod.classify_kind('Без хештега', 1400, None), 'long')
        self.assertEqual(mod.classify_kind('Без хештега', 40, {'type': 'short'}), 'short')


if __name__ == '__main__':
    unittest.main()
