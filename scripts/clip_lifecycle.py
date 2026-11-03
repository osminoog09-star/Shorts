"""Film-level intake lifecycle. Upload/date alone never proves publication."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    'no country for old men': 'старикам тут не место', 'whiplash': 'одержимость',
    'ex machina': 'из машины', 'nightcrawler': 'стрингер', 'interstellar': 'интерстеллар',
    'the batman': 'бэтмен', 'oppenheimer': 'оппенгеймер', 'the menu': 'меню',
}


def film_key(name):
    title = re.sub(r'\s*\(\d{4}\)\s*$', '', name or '').strip().lower().replace('ё', 'е')
    title = ALIASES.get(title, title)
    year = re.search(r'\((\d{4})\)\s*$', name or '')
    return re.sub(r'[^а-яa-z0-9]', '', title) + (year.group(1) if year else '')


def read(root, path, default):
    try:
        return json.loads((root / path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def resolve(root=ROOT):
    """Use explicit film links, queue, receipts and public API inventory/pulse."""
    catalog = read(root, 'publishing/film_projects.json', {'items': []})
    queue = {r['id']: r for r in read(root, 'publishing/queue.json', {}).get('items', [])}
    inventory = read(root, 'reports/youtube/latest.json', {}).get('inventory', [])
    public = {r.get('video_id') for r in inventory if r.get('privacy') == 'public' or
              r.get('status', {}).get('privacyStatus') == 'public'}
    pulse = read(root, 'reports/youtube/pulse.json', {})
    # youtube_pulse.py emits only public videos in recent.
    public.update(r.get('id') for r in pulse.get('recent', []))
    # New projects carry film on queue rows; no new hand-maintained status needed.
    by_key = {film_key(f['film']): f for f in catalog.get('items', [])}
    for q in queue.values():
        if not q.get('film'):
            continue
        key = film_key(q['film'])
        f = by_key.setdefault(key, {'film': q['film'], 'projects': []})
        if not any(p['id'] == q['id'] for p in f['projects']):
            f['projects'].append({'id': q['id']})
    catalog['items'] = list(by_key.values())
    films = []
    for film in catalog.get('items', []):
        projects = []
        for linked in film.get('projects', []):
            q = queue.get(linked['id'], {})
            receipt = read(root, 'publishing/receipts/' + linked['id'] + '.json', {})
            vid = receipt.get('video_id') or q.get('youtube_id') or linked.get('youtube_id')
            published = bool(vid) and (vid in public or q.get('status') == 'published' or
                        receipt.get('privacy_status') == 'public' or linked.get('status') == 'published')
            state = 'published' if published else 'scheduled' if receipt.get('status') == 'scheduled' else 'private' if vid else 'production'
            projects.append({**linked, 'title': q.get('title') or linked.get('title', linked['id']),
                             'youtube_id': vid, 'state': state,
                             'publish_at': receipt.get('publish_at_utc'),
                             'blocker': q.get('blocked_reason') or linked.get('blocker')})
        active = [p for p in projects if p['state'] != 'published']
        state = 'in_progress' if active else 'published' if projects else 'needed'
        films.append({**film, 'key': film_key(film['film']), 'state': state, 'projects': projects})
    return {'items': films}


def classify_requests(requests, lifecycle):
    films = {f['key']: f for f in lifecycle['items']}
    result = []
    for r in requests:
        film = films.get(film_key(r.get('film')))
        result.append({**r, 'lifecycle': film['state'] if film else 'needed',
                       'projects': film['projects'] if film else []})
    return result


def needed_requests(requests, root=ROOT):
    return [r for r in classify_requests(requests, resolve(root))
            if r['lifecycle'] == 'needed' and r.get('status') not in ('собран', 'опубликован', 'архив')]
