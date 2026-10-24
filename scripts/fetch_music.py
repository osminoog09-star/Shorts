#!/usr/bin/env python3
"""Качает разрешённую музыку (CC BY 4.0, incompetech.com — Kevin MacLeod) в media/music/ + файл атрибуции.
Вход: jobs/music/*.json  {"tracks": [{"title": "Investigations", "file": "Investigations.mp3"}]}
"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path
out = Path("media/music"); out.mkdir(parents=True, exist_ok=True)
log = []
for p in sys.argv[1:]:
    for tr in json.load(open(p))["tracks"]:
        dst = out / tr["file"]
        if dst.exists() and dst.stat().st_size > 50000:
            continue
        url = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/" + urllib.parse.quote(tr["file"])
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) < 50000:
                raise RuntimeError(f"too small: {len(data)}")
            dst.write_bytes(data)
            (out / (dst.stem + ".license.txt")).write_text(
                f'"{tr["title"]}" Kevin MacLeod (incompetech.com)\n'
                "Licensed under Creative Commons: By Attribution 4.0 License\n"
                "http://creativecommons.org/licenses/by/4.0/\n", encoding="utf-8")
            log.append(f"ok {tr['file']} {len(data)}")
        except Exception as ex:  # noqa: BLE001
            log.append(f"FAIL {tr['file']} {url} {ex!r}")
(out / "_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
print("\n".join(log))
