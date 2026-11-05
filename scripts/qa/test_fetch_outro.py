#!/usr/bin/env python3
"""Offline regression tests for fail-closed private Denis v7 Drive bootstrap."""
from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fetch_outro as subject


class FakeOpener:
    def __init__(self, videos: dict[str, bytes]):
        self.videos = videos
        self.calls = []

    def __call__(self, request, timeout=None):
        self.calls.append((request.full_url, dict(request.header_items())))
        if request.full_url == 'https://oauth2.googleapis.com/token':
            assert request.get_method() == 'POST'
            return BytesIO(json.dumps({'access_token': 'secret-access'}).encode())
        if 'drive/v3/files/vertical-id-123' in request.full_url:
            assert request.get_header('Authorization') == 'Bearer secret-access'
            return BytesIO(self.videos['vertical'])
        if 'drive/v3/files/horizontal-id-456' in request.full_url:
            assert request.get_header('Authorization') == 'Bearer secret-access'
            return BytesIO(self.videos['horizontal'])
        raise AssertionError('Unknown url: ' + request.full_url)


class FetchApprovedOutrosTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.videos = {'vertical': b'V' * 4096, 'horizontal': b'H' * 5000}
        self.manifest = self.root / 'approved.json'
        data = {'version': 'denis-v7-voice10', 'speaker': 'denis',
                'no_fallback_to_old_dima': True,
                'assets': {k: {'path': safe, 'drive_file_id': {'vertical': 'vertical-id-123', 'horizontal': 'horizontal-id-456'}[k],
                               'sha256': hashlib.sha256(self.videos[k]).hexdigest()}
                           for k, safe in subject.TARGETS.items()}}
        self.data = data
        self.manifest.write_text(json.dumps(data))
        self.env = {'GDRIVE_REFRESH_TOKEN': 'refresh-private', 'YOUTUBE_OAUTH_CLIENT_ID': 'client-id',
                    'YOUTUBE_OAUTH_CLIENT_SECRET': 'client-secret'}

    def test_downloads_both_with_oauth_and_sha256(self):
        opener = FakeOpener(self.videos)
        subject.fetch_all(self.manifest, self.root, self.env, opener=opener)
        subject.verify_existing(self.manifest, self.root)
        for kind, path in subject.TARGETS.items():
            self.assertEqual((self.root / path).read_bytes(), self.videos[kind])
        self.assertEqual(len(opener.calls), 3)
        self.assertNotIn('refresh-private', repr(opener.calls))
        self.assertNotIn('client-secret', repr(opener.calls))

    def test_mismatch_stops_both_and_leaves_no_partial_new_files(self):
        opener = FakeOpener({'vertical': self.videos['vertical'], 'horizontal': b'CORRUPTED' * 1000})
        with self.assertRaisesRegex(subject.OutroError, 'SHA256 несовпадение'):
            subject.fetch_all(self.manifest, self.root, self.env, opener=opener)
        for path in subject.TARGETS.values():
            self.assertFalse((self.root / path).exists())

    def test_no_refresh_secret_fail_closed(self):
        with self.assertRaisesRegex(subject.OutroError, 'GDRIVE_REFRESH_TOKEN'):
            subject.fetch_all(self.manifest, self.root, {}, opener=FakeOpener(self.videos))
        self.assertFalse((self.root / subject.TARGETS['vertical']).exists())

    def test_no_fallback_to_dima_or_wrong_approved_version(self):
        self.data['no_fallback_to_old_dima'] = False
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(subject.OutroError, 'fallback запрещён'):
            subject.read_approved(self.manifest)
        self.data['no_fallback_to_old_dima'] = True
        self.data['assets']['vertical']['path'] = 'media/outro/m1lash_outro_dima_v1.mp4'
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(subject.OutroError, 'не совпадает'):
            subject.read_approved(self.manifest)

    def test_wrong_local_hash_is_no_go(self):
        subject.fetch_all(self.manifest, self.root, self.env, opener=FakeOpener(self.videos))
        (self.root / subject.TARGETS['vertical']).write_bytes(b'DIMA' * 1000)
        with self.assertRaisesRegex(subject.OutroError, 'SHA256 не совпадает'):
            subject.verify_existing(self.manifest, self.root)

    def test_download_http_403_is_sanitized(self):
        def fail(request, timeout=None):
            if 'oauth2.googleapis.com' in request.full_url:
                return BytesIO(json.dumps({'access_token': 'secret-access'}).encode())
            raise HTTPError(request.full_url, 403, 'No permission', {}, None)
        with self.assertRaisesRegex(subject.OutroError, 'HTTP 403') as cm:
            subject.fetch_all(self.manifest, self.root, self.env, opener=fail)
        self.assertNotIn('secret-access', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
