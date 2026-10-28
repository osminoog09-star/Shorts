#!/usr/bin/env python3
"""M1lash free source-linked news radar: twice daily RSS/Atom acquisition.

No AI-generated claims, no rehosting full articles, no unfounded verification flags.
Sources are hard-coded, not selected from untrusted user input. Feed XML is capped
and DTD/entity declarations are rejected. A source failure cannot erase prior data.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "news.json"
UTC = dt.timezone.utc
MAX_BYTES = 1_250_000
AGE_LIMIT_DAYS = 7
MAX_ITEMS = 80
USER_AGENT = "M1lashStudioNewsRadar/1.0 (RSS; published titles/URLs only)"
FEEDS = [
    ("TechCrunch AI", "ai", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "ai", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("MIT AI", "ai", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
    ("NASA News", "space", "https://www.nasa.gov/news-release/feed/"),
    ("NASA Technology", "space", "https://www.nasa.gov/technology/feed/"),
    ("IEEE Spectrum Robotics", "robotics", "https://spectrum.ieee.org/feeds/topic/robotics.rss"),
    ("Ars Technica", "technology", "https://feeds.arstechnica.com/arstechnica/index"),
]
SOURCES = {s for s, _, _ in FEEDS}
CATEGORIES = {"ai", "space", "robotics", "technology"}


def clean_text(raw: str, limit: int) -> str:
    without_tags = re.sub(r"<[^>]{0,1000}>", " ", raw or "")
    return " ".join(html.unescape(without_tags).split())[:limit]


def item_date(raw):
    if not raw:
        return None
    try:
        when = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            when = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return when.astimezone(UTC)


def valid_link(url, now=None):
    if not url or len(url) > 1500 or any(c in url for c in "\n\r\t"):
        return False
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    hostname = parsed.hostname.lower()
    return hostname in (
        "techcrunch.com", "www.theverge.com", "news.mit.edu",
        "www.nasa.gov", "nasa.gov", "spectrum.ieee.org",
        "arstechnica.com", "www.arstechnica.com",
    )


def elem_value(item, names):
    for name in names:
        child = item.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def parse_feed(blob, source, category, now=None):
    if source not in SOURCES or category not in CATEGORIES:
        raise ValueError("unknown feed identity")
    if len(blob) > MAX_BYTES or b"<!DOCTYPE" in blob.upper() or b"<!ENTITY" in blob.upper():
        raise ValueError("unsafe or oversized XML feed")
    now = now or dt.datetime.now(UTC)
    root = ET.fromstring(blob)
    entries = root.findall(".//item")
    atom = False
    if not entries:
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        atom = True
    rows = []
    for entry in entries[:60]:
        title = clean_text(elem_value(entry, ["title", "{http://www.w3.org/2005/Atom}title"]), 220)
        if not title:
            continue
        if atom:
            link = ""
            for el in entry.findall("{http://www.w3.org/2005/Atom}link"):
                if el.attrib.get("rel", "alternate") == "alternate":
                    link = el.attrib.get("href", "")
                    break
            raw_date = elem_value(entry, ["{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated"])
        else:
            link = elem_value(entry, ["link"])
            raw_date = elem_value(entry, ["pubDate", "{http://purl.org/dc/elements/1.1/}date"])
        if not valid_link(link):
            continue
        when = item_date(raw_date)
        if not when:
            continue  # never claim freshness with no trusted timestamp
        age = (now - when).total_seconds()
        if age < -3600 or age > AGE_LIMIT_DAYS * 86400:
            continue
        # Dedupe by stable canonical URL, strip trackers
        parsed = urllib.parse.urlsplit(link)
        normalized_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path, "", ""))
        rows.append({
            "id": hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:18],
            "title": title,
            "url": normalized_url,
            "category": category,
            "source": source,
            "published_at": when.isoformat().replace("+00:00", "Z"),
            "status": "SOURCE_TITLE_NOT_FACT_CHECKED",
        })
    return rows


def fetch_one(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=18) as response:
        if not response.url.startswith("https://"):
            raise ValueError("unexpected unencrypted redirect")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("too large")
    return data


def merge(previous, current, now=None):
    now = now or dt.datetime.now(UTC)
    unique = {}
    for entry in [*current, *previous]:
        if not isinstance(entry, dict) or not valid_link(entry.get("url")):
            continue
        date = item_date(entry.get("published_at"))
        if not date or not 0 <= (now - date).total_seconds() <= AGE_LIMIT_DAYS * 86400:
            continue
        if entry.get("id") not in unique and entry.get("source") in SOURCES:
            unique[entry["id"]] = entry
    return sorted(unique.values(), key=lambda x: x["published_at"], reverse=True)[:MAX_ITEMS]


def collect(old=None, fetch=fetch_one, now=None):
    now = now or dt.datetime.now(UTC)
    data = []
    errors = []
    successful = 0
    for name, category, address in FEEDS:
        try:
            data.extend(parse_feed(fetch(address), name, category, now))
            successful += 1
        except Exception as exc:
            errors.append({"source": name, "error_type": type(exc).__name__})
    kept = merge((old or {}).get("items", []), data, now)
    # Avoid poisoning the site with fake freshness when every provider fails.
    status = "success" if successful == len(FEEDS) else ("partial" if successful else "unavailable")
    return {
        "status": status,
        "updated_at": now.isoformat().replace("+00:00", "Z") if successful else (old or {}).get("updated_at"),
        "last_attempt_at": now.isoformat().replace("+00:00", "Z"),
        "feeds_ok": successful,
        "feeds_failed": len(errors),
        "errors": errors,
        "scope": "source headlines only; articles, primary statements and claims need independent verification",
        "items": kept,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()
    target = Path(args.output)
    try:
        old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
    except json.JSONDecodeError:
        old = {}
    result = collect(old)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"status={result['status']} live_sources={result['feeds_ok']} items={len(result['items'])} errors={result['feeds_failed']}")


if __name__ == "__main__":
    main()
