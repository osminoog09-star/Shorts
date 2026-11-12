#!/usr/bin/env python3
"""Дозаполняет журнал reports/videos.csv из уже сохранённых ежедневных снимков (без сети).

python3 tools/analytics/backfill_ages.py [--dry]

Что заполняет и только там, где поле пустое (ручные значения не трогает):
- views_48h / views_7d — счётчик просмотров из ежедневного снимка, ближайшего к возрасту
  ролика 48 ч / 7 дней. Фактический возраст снимка в часах пишется рядом
  (views_48h_age_h / views_7d_age_h): это «около 48 ч», а не точное скользящее окно.
- date / time — время выхода по Таллину для открытых роликов.
- kind — short/long: по типу в паспорте публикации или хештегу #shorts; длинное — от 3 минут
  без хештега. Одной длиной Shorts не определяется.
- format — та же классификация, что на сайте студии (scripts/build_studio_site.py).

Нет подходящего снимка — поле остаётся пустым (unknown), ноль не подставляется.
"""
import argparse
import csv
import io
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
TALLINN = ZoneInfo('Europe/Tallinn')
# (поле, целевой возраст в часах, допуск в часах)
AGES = (('views_48h', 48, 12), ('views_7d', 168, 18))
NEW_FIELDS = ['views_48h_age_h', 'views_7d_age_h']
# Ролик считаем вышедшим в published_at, только если уже в первом «открытом» снимке
# он не старше этого порога; иначе его открыли позже и возраст неизвестен.
MAX_FIRST_PUBLIC_LAG_H = 36


def parse_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def duration_seconds(value):
    match = re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', value or '')
    return sum(int(x or 0) * f for x, f in zip(match.groups(), (3600, 60, 1))) if match else None


def load_snapshots(daily_dir):
    """[(fetched_at, {video_id: inventory_item})] по возрастанию времени."""
    snapshots = []
    for path in sorted(Path(daily_dir).glob('*.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            fetched = parse_time(data['fetched_at'])
        except (OSError, ValueError, KeyError):
            continue
        items = {i['video_id']: i for i in data.get('inventory') or [] if i.get('video_id')}
        if items:
            snapshots.append((fetched, items))
    return sorted(snapshots, key=lambda s: s[0])


def load_manifest_meta(root):
    """{video_id: metadata паспорта} через квитанции заливки."""
    meta = {}
    for receipt_path in (Path(root) / 'publishing/receipts').glob('*.json'):
        try:
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            vid, manifest = receipt.get('video_id'), receipt.get('manifest')
            if not vid or not manifest:
                continue
            data = json.loads((Path(root) / manifest).read_text(encoding='utf-8'))
            meta[vid] = data.get('metadata') or {}
        except (OSError, ValueError):
            continue
    return meta


def classify_kind(title, seconds, meta):
    kind = (meta or {}).get('type')
    if kind in ('short', 'long'):
        return kind
    if re.search(r'#shorts?\b', title.lower()):
        return 'short'
    if seconds and seconds > 180:
        return 'long'
    return None


def classify_format(title, seconds, meta):
    t = title.lower()
    if seconds and seconds > 180:
        return 'Длинное'
    if str((meta or {}).get('category_id')) == '1' or re.search(
            r'сцена|фильм|\| во все|волк с уолл|стыковка|назвать сво', t):
        return 'Кино-Shorts'
    if 'притворись ботом' in t:
        return 'Притворись ботом'
    if 'новост' in t:
        return 'Новости ИИ'
    if re.search(r'\bии\b|робот|нейросет|chatgpt|claude|бот|умн\w+ дом|кофемашин|пылесос|холодильник|колонк|чайник', t):
        return 'ИИ-скетчи'
    if re.search(r'компьютер|древн|луну|самол|венер|батаре|заряд|бросил её|зеркал|мкс|гравитац|орбит', t):
        return 'Наука'
    return 'Юмор/прочее'


def public_history(vid, snapshots):
    """Снимки, где ролик открыт: [(fetched_at, views)], и его published_at."""
    history, published = [], None
    for fetched, items in snapshots:
        item = items.get(vid)
        if not item or item.get('privacy') != 'public':
            continue
        count = (item.get('statistics') or {}).get('viewCount')
        if count is None:
            continue
        published = parse_time(item['published_at'])
        history.append((fetched, int(count)))
    return history, published


def views_at_age(history, published, hours, tolerance):
    """(просмотры, фактический возраст в часах) или None, если снимка рядом нет."""
    if not history or published is None:
        return None
    target = published + timedelta(hours=hours)
    fetched, count = min(history, key=lambda h: abs(h[0] - target))
    age = (fetched - published).total_seconds() / 3600
    if abs(age - hours) > tolerance:
        return None
    return count, round(age, 1)


def backfill_rows(rows, snapshots, manifest_meta):
    """Меняет строки на месте; возвращает счётчики заполненного."""
    filled = dict.fromkeys(['views_48h', 'views_7d', 'date', 'kind', 'format'], 0)
    latest = snapshots[-1][1] if snapshots else {}
    for row in rows:
        vid = row.get('video_id')
        if not vid:
            continue
        history, published = public_history(vid, snapshots)
        first_public_ok = bool(history) and \
            history[0][0] - published <= timedelta(hours=MAX_FIRST_PUBLIC_LAG_H)
        for field, hours, tolerance in AGES:
            if row.get(field) or not first_public_ok:
                continue
            found = views_at_age(history, published, hours, tolerance)
            if found:
                row[field], row[field + '_age_h'] = found
                filled[field] += 1
        if published and first_public_ok and not row.get('date'):
            local = published.astimezone(TALLINN)
            row['date'], row['time'] = local.date().isoformat(), local.strftime('%H:%M')
            filled['date'] += 1
        item = latest.get(vid) or {}
        title = row.get('title') or item.get('title') or ''
        try:
            seconds = float(row['length_s']) if row.get('length_s') else None
        except ValueError:
            seconds = None
        seconds = seconds or duration_seconds(item.get('duration'))
        meta = manifest_meta.get(vid)
        if row.get('kind') in ('', None, 'unknown'):
            kind = classify_kind(title, seconds, meta)
            if kind:
                row['kind'] = kind
                filled['kind'] += 1
        if not row.get('format') and title:
            row['format'] = classify_format(title, seconds, meta)
            filled['format'] += 1
    return filled


def backfill(csv_path, daily_dir, root=ROOT, dry=False):
    csv_path = Path(csv_path)
    with csv_path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = list(reader.fieldnames), list(reader)
    fields += [x for x in NEW_FIELDS if x not in fields]
    for row in rows:
        for name in NEW_FIELDS:
            row.setdefault(name, '')
    filled = backfill_rows(rows, load_snapshots(daily_dir), load_manifest_meta(root))
    if not dry:
        output = io.StringIO(newline='')
        # Журнал с урезанной шапкой (тесты) не должен ломаться из-за дозаполняемых полей.
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
        tmp = csv_path.with_suffix(csv_path.suffix + '.tmp')
        tmp.write_text(output.getvalue(), encoding='utf-8', newline='')
        tmp.replace(csv_path)
    return filled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', action='store_true', help='только показать, что заполнится')
    args = parser.parse_args()
    filled = backfill(ROOT / 'reports/videos.csv', ROOT / 'reports/youtube/daily', dry=args.dry)
    print('Заполнено:', ', '.join(f'{k}={v}' for k, v in filled.items()))


if __name__ == '__main__':
    main()
