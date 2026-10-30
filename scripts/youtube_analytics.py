#!/usr/bin/env python3
"""Read-only YouTube collection. Secrets stay in the Actions environment."""
import argparse
import csv
import io
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.youtube_direct import token_for, verify_channel

METRICS = ['views', 'engagedViews', 'averageViewPercentage', 'averageViewDuration',
           'subscribersGained', 'subscribersLost', 'likes', 'comments', 'shares', 'estimatedMinutesWatched']
ANALYTICS = 'https://youtubeanalytics.googleapis.com/v2/reports'
DATA = 'https://www.googleapis.com/youtube/v3/'


class ApiError(RuntimeError):
    def __init__(self, status, endpoint):
        self.status = status
        super().__init__(f'YouTube {endpoint}: HTTP {status} (credentials/body omitted)')


class Client:
    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer ' + token

    def get(self, url, params):
        for attempt in range(4):
            r = self.session.get(url, params=params, timeout=60)
            if r.status_code not in (429, 500, 502, 503, 504):
                break
            if attempt < 3:
                time.sleep(2 ** attempt)
        if not r.ok:
            raise ApiError(r.status_code, 'Analytics' if url == ANALYTICS else 'Data API')
        return r.json()

    def query(self, start, end, dimensions, metrics, filters=None):
        params = dict(ids='channel==MINE', startDate=str(start), endDate=str(end),
                      dimensions=dimensions, metrics=','.join(metrics), maxResults=200,
                      sort=dimensions)
        if filters:
            params['filters'] = filters
        rows = []
        while True:
            params['startIndex'] = len(rows) + 1
            result = self.get(ANALYTICS, params)
            names = [x['name'] for x in result.get('columnHeaders', [])]
            page = [dict(zip(names, row)) for row in result.get('rows', [])]
            rows.extend(page)
            if len(page) < params['maxResults']:
                return rows

    def metrics(self, start, end, dimensions, filters=None, metrics=METRICS):
        """Keep unsupported metrics null; permission/auth failures abort the run."""
        merged, missing = {}, []
        for metric in metrics:
            try:
                rows = self.query(start, end, dimensions, [metric], filters)
            except ApiError as exc:
                if exc.status != 400:
                    raise
                missing.append(metric)
                continue
            for row in rows:
                key = row[dimensions]
                merged.setdefault(key, {dimensions: key, **dict.fromkeys(metrics)}).update(row)
        return list(merged.values()), missing


def inventory(client, channel_id):
    channel = client.get(DATA + 'channels', dict(part='contentDetails,statistics', id=channel_id))['items'][0]
    playlist = channel['contentDetails']['relatedPlaylists']['uploads']
    ids, page = [], None
    while True:
        params = dict(part='contentDetails', playlistId=playlist, maxResults=50)
        if page:
            params['pageToken'] = page
        result = client.get(DATA + 'playlistItems', params)
        ids.extend(x['contentDetails']['videoId'] for x in result.get('items', []))
        page = result.get('nextPageToken')
        if not page:
            break
    videos = []
    for offset in range(0, len(ids), 50):
        result = client.get(DATA + 'videos', dict(part='snippet,contentDetails,statistics,status', id=','.join(ids[offset:offset+50])))
        for item in result.get('items', []):
            snippet = item['snippet']
            videos.append(dict(video_id=item['id'], title=snippet['title'], published_at=snippet['publishedAt'],
                               duration=item['contentDetails']['duration'], privacy=item['status']['privacyStatus'],
                               statistics=item.get('statistics', {})))
    return videos, channel.get('statistics', {})


def duration_seconds(value):
    match = re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', value)
    return sum(int(x or 0) * factor for x, factor in zip(match.groups(), (3600, 60, 1))) if match else None


def atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    tmp.replace(path)


def save_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def update_journal(path, videos, metrics, fetched_at):
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = list(reader.fieldnames), list(reader)
    extras = ['analytics_as_of', 'analytics_start', 'analytics_end'] + ['yt_' + x for x in METRICS]
    fields += [x for x in extras if x not in fields]
    indexed = {r['video_id']: r for r in rows if r.get('video_id')}
    for video in videos:
        vid = video['video_id']
        row = indexed.get(vid)
        if row is None:
            # Never fuzzy-match titles to scheduled entries or guess a Shorts classification.
            row = dict.fromkeys(fields, '')
            row.update(video_id=vid, title=video['title'], kind='unknown',
                       notes='Обнаружен API; формат/стиль/автор требуют сверки')
            if video['privacy'] == 'public':
                published = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).astimezone(ZoneInfo('Europe/Tallinn'))
                row.update(date=published.date().isoformat(), time=published.strftime('%H:%M'))
            rows.append(row)
        if not row.get('length_s'):
            row['length_s'] = duration_seconds(video['duration']) or ''
        row.update(analytics_as_of=fetched_at, analytics_start=metrics['start'], analytics_end=metrics['end'])
        values = metrics['videos'].get(vid, {})
        for key in METRICS:
            value = values.get(key)
            row['yt_' + key] = '' if value is None else value
        # Exact rolling 48h/7d cannot be reconstructed from day-granularity Analytics.
        # Keep editorial fields and existing exact-age observations untouched.
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    atomic(path, output.getvalue())


def period_bounds(today):
    """Latest completed Mon-Sun week and calendar month; refresh lagged data daily."""
    sunday = today if today.weekday() == 6 else today - timedelta(days=today.weekday() + 1)
    month_end = today.replace(day=1) - timedelta(days=1)
    return [('weekly', sunday - timedelta(days=6), sunday, f'{sunday.isocalendar().year}-W{sunday.isocalendar().week:02d}'),
            ('monthly', month_end.replace(day=1), month_end, month_end.strftime('%Y-%m'))]


def period_data(client, start, end):
    rows, missing = client.metrics(start, end, 'video')
    return dict(start=str(start), end=str(end), videos={r['video']: r for r in rows}, unsupported_metrics=missing)


def summary(data, videos):
    labels = {v['video_id']: v for v in videos}
    lines = [f"Период API: {data['start']} — {data['end']} (America/Los_Angeles).",
             'Данные предварительные: задержка YouTube, пустое значение ≠ ноль.', '',
             '| ID | Название | Просмотры | Engaged | Средний просмотр, с | Средний % | Подписки + | Лайки | Комментарии |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for vid, row in sorted(data['videos'].items(), key=lambda x: x[1].get('views') or 0, reverse=True):
        title = labels.get(vid, {}).get('title', vid).replace('|', ' / ').replace('\n', ' ')
        # Explicit order: views, engaged, duration, percentage, subscribers.
        values = ['—' if row.get(k) is None else str(row[k]) for k in ['views','engagedViews','averageViewDuration','averageViewPercentage','subscribersGained','likes','comments']]
        lines.append(f"| {vid} | {title} | " + ' | '.join(values) + ' |')
    if data['unsupported_metrics']:
        lines.append('\nНедоступные метрики API: ' + ', '.join(data['unsupported_metrics']))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=date.fromisoformat, help='Дата снимка Europe/Tallinn')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    today = args.date or now.astimezone(ZoneInfo('Europe/Tallinn')).date()
    # Request only past Pacific calendar days, never an incomplete current day.
    end = min(today - timedelta(days=1), now.astimezone(ZoneInfo('America/Los_Angeles')).date() - timedelta(days=1))
    channel_id = json.loads((ROOT / 'publishing/channels.json').read_text())['ru']
    token = token_for('ru')
    verify_channel(token, channel_id)
    client = Client(token)
    videos, statistics = inventory(client, channel_id)
    start = min([date.fromisoformat(v['published_at'][:10]) - timedelta(days=1) for v in videos] + [end])
    data = period_data(client, start, end)
    history, missing = client.metrics(max(start, end - timedelta(days=34)), end, 'day', metrics=['views'])
    traffic, traffic_missing = {}, {}
    for video in videos:
        vid = video['video_id']
        rows, gaps = client.metrics(max(start, end - timedelta(days=27)), end, 'insightTrafficSourceType',
                                   filters='video==' + vid, metrics=['views'])
        traffic[vid], traffic_missing[vid] = rows, gaps
    data.update(schema_version=1, channel_id=channel_id, snapshot_date=str(today), fetched_at=now.isoformat(),
                inventory=videos, channel_statistics=statistics, recent_daily_views=history,
                last_observed_view_day=max([r['day'] for r in history], default=None),
                traffic=dict(start=str(max(start, end - timedelta(days=27))), end=str(end), videos=traffic,
                             unsupported_metrics=traffic_missing),
                limitations=['Analytics days use Pacific time; data may lag and be revised.',
                             'Missing rows are null, not zero; empty API response is not evidence of zero activity.',
                             'Exact rolling 48h/7d unavailable: journal age-specific fields are not overwritten.',
                             'Data API counters are lifetime snapshots; Analytics metrics use the stated window.',
                             'Shorts type is editorial metadata, never inferred from duration alone.'])
    daily = ROOT / 'reports/youtube/daily'
    save_json(daily / f'{today}.json', data)
    # Include every inventory video even when Analytics has no rows.
    for video in videos:
        data['videos'].setdefault(video['video_id'], dict.fromkeys(METRICS))
    save_json(daily / f'{today}.json', data)
    atomic(daily / f'{today}.md', '# M1lash — ежедневный снимок\n\n' + summary(data, videos))
    save_json(ROOT / 'reports/youtube/latest.json', data)
    update_journal(ROOT / 'reports/videos.csv', videos, data, now.isoformat())
    for kind, first, last, label in period_bounds(today):
        # A Sunday/1st report may initially lack recent data. Refresh until API catches up.
        period = period_data(client, first, min(last, end))
        period.update(requested_end=str(last), fetched_at=now.isoformat(), provisional=True)
        save_json(ROOT / f'reports/youtube/{kind}/{label}.json', period)
        atomic(ROOT / f'reports/youtube/{kind}/{label}.md', '# M1lash — цифры периода\n\n' + summary(period, videos))
    print(f'Analytics snapshot saved: {today}; inventory={len(videos)}; API end={end}')


if __name__ == '__main__':
    try:
        main()
    except (ApiError, ValueError, KeyError, requests.RequestException):
        # Request exceptions can contain URLs/params; never print their repr or token.
        sys.exit('Analytics collection failed; check API authorization/availability (no secrets logged).')
