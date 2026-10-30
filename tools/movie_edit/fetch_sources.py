"""Fetch declared source clips with their original audio; never publish a video."""
import argparse
import json
import pathlib
import re
import subprocess
from urllib.parse import urlparse


def fetch(manifest_path, output_dir):
    manifest_path = pathlib.Path(manifest_path)
    if manifest_path.parent.as_posix() != 'tools/movie_edit/source_jobs':
        raise ValueError('Expected tools/movie_edit/source_jobs/<job>.json')
    job = json.loads(manifest_path.read_text(encoding='utf-8'))
    sources = job['sources']
    if not isinstance(sources, list) or not 1 <= len(sources) <= 8:
        raise ValueError('Expected 1–8 sources')
    output = pathlib.Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    receipts = []
    seen = set()
    for source in sources:
        sid, url = source['id'], source['url']
        if not re.fullmatch(r'[a-z0-9_-]{1,64}', sid) or sid in seen:
            raise ValueError('Invalid or duplicate source ID')
        seen.add(sid)
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Expected public HTTPS source without credentials')
        dest = output / (sid + '.%(ext)s')
        subprocess.run([
            'python3', '-m', 'yt_dlp', '--no-playlist', '--retries', '1',
            '--extractor-retries', '0', '--max-filesize', '250M',
            '--match-filters', 'duration <= 900', '--write-info-json',
            '--format', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '--merge-output-format', 'mp4', '--output', str(dest), '--', url,
        ], check=True)
        video = output / (sid + '.mp4')
        if not video.is_file():
            raise RuntimeError('Expected source MP4 missing; no silent substitute')
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-show_format',
            '-of', 'json', str(video),
        ]))
        streams = probe['streams']
        if not any(s['codec_type'] == 'audio' for s in streams):
            raise RuntimeError('Original audio missing; source cannot serve RU film editing')
        receipts.append({
            'id': sid, 'url': url, 'path': video.name,
            'duration': float(probe['format']['duration']),
            'original_audio_preserved': True,
            'language_verification': 'pending actual listening; captions metadata is insufficient',
            'publication': 'source only; no upload or scheduling',
        })
    (output / 'source_receipt.json').write_text(
        json.dumps({'manifest': str(manifest_path), 'sources': receipts}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest')
    parser.add_argument('output')
    args = parser.parse_args()
    fetch(args.manifest, args.output)
