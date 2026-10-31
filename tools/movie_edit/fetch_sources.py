"""Fetch declared source clips with their original audio; never publish a video."""
import argparse
import json
import pathlib
import re
import subprocess
from urllib.parse import urlparse
from urllib.request import Request, urlopen


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
        clip_args = []
        has_range = 'start_seconds' in source or 'end_seconds' in source
        if has_range:
            start = float(source['start_seconds'])
            end = float(source['end_seconds'])
            if not 0 <= start < end or end - start > 900:
                raise ValueError('Expected a positive clip range of at most 900 seconds')
            # Fetch only the requested interval using FFmpeg input seeking.
            clip_args = ['--download-sections', f'*{start}-{end}',
                         '--downloader', 'ffmpeg']
        if parsed.path.lower().endswith('.mp4') and not has_range:
            # Direct downloadable movie promo: yt-dlp often has no pre-download
            # height/duration metadata, so its format filters reject a valid MP4.
            # Stream plain HTTPS only (no authentication, cookies, or DRM bypass).
            video = output / (sid + '.mp4')
            cap = 250 * 1024 * 1024
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0 M1lash-QA/1.0'})
            try:
                with urlopen(request, timeout=45) as response, video.open('wb') as file:
                    content_type = (response.headers.get('Content-Type') or '').split(';')[0].lower().strip()
                    if content_type not in ('video/mp4', 'application/octet-stream', 'video/quicktime'):
                        raise RuntimeError(f'Not a downloadable video/mp4 response: {content_type}')
                    length = int(response.headers.get('Content-Length') or 0)
                    if length > cap:
                        raise RuntimeError(f'File declares {length} bytes, above the 250MB limit')
                    size = 0
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > cap:
                            raise RuntimeError('File exceeded the 250MB limit during transfer')
                        file.write(chunk)
                if video.stat().st_size < 10240:
                    raise RuntimeError('Downloaded source MP4 suspiciously short')
            except Exception:
                video.unlink(missing_ok=True)
                raise
        else:
            dest = output / (sid + '.%(ext)s')
            subprocess.run([
                'python3', '-m', 'yt_dlp', '--no-playlist', '--retries', '1',
                '--extractor-retries', '0', '--max-filesize', '250M',
                '--write-info-json',
                '--format', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                '--merge-output-format', 'mp4', '--output', str(dest), *clip_args, '--', url,
            ], check=True)
            video = output / (sid + '.mp4')
        if not video.is_file():
            raise RuntimeError('Expected source MP4 missing; no silent substitute')
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-show_format',
            '-of', 'json', str(video),
        ]))
        # Direct MP4 links usually have unknown duration before download;
        # yt-dlp --match-filters 'duration <= 900' silently discarded them.
        # Enforce the hard cap on the actual decoded file instead.
        duration = float(probe['format']['duration'])
        if not 0 < duration <= 900:
            video.unlink(missing_ok=True)
            raise RuntimeError(f"Source duration {duration:.2f}s exceeds the 15-minute promo limit")
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
