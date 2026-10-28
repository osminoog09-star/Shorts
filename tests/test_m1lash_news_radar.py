"""No-network regressions for source attribution, freshness and untrusted XML."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"motion-studio/automation/news_radar.py"
spec=importlib.util.spec_from_file_location("radar",path)
radar=importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)
NOW=dt.datetime(2026,10,28,12,tzinfo=dt.timezone.utc)
RSS=b"""<?xml version="1.0"?><rss><channel><item><title>Robots: a new test</title><link>https://www.nasa.gov/news-release/robot-test/?utm_source=x</link><pubDate>Wed, 28 Oct 2026 10:00:00 GMT</pubDate></item><item><title>Old story</title><link>https://www.nasa.gov/news-release/old</link><pubDate>Sun, 12 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"""
ATOM=b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>AI study released</title><link href="https://news.mit.edu/2026/study-ai"/><updated>2026-10-27T10:00:00Z</updated></entry></feed>"""
class Radar(unittest.TestCase):
 def test_rss_timestamp_url_strip_and_age(self):
  a=radar.parse_feed(RSS,"NASA News","space",NOW)
  self.assertEqual(len(a),1)
  self.assertEqual(a[0]["url"],"https://www.nasa.gov/news-release/robot-test/")
  self.assertEqual(a[0]["status"],"SOURCE_TITLE_NOT_FACT_CHECKED")
 def test_atom(self):
  a=radar.parse_feed(ATOM,"MIT AI","ai",NOW)
  self.assertEqual(len(a),1)
 def test_untrusted_xml_disallowed(self):
  with self.assertRaises(ValueError):radar.parse_feed(b'<!DOCTYPE lol [<!ENTITY x "abc">]><rss/>',"NASA News","space",NOW)
 def test_unknown_source_disallowed(self):
  with self.assertRaises(ValueError):radar.parse_feed(RSS,"Hacker website","space",NOW)
 def test_invalid_urls(self):
  for url in ("javascript:alert(1)","http://www.nasa.gov/test","https://example.net/","https://nasa.gov.evil.net/test"):
   self.assertFalse(radar.valid_link(url))
 def test_preserve_when_offline(self):
  old=radar.parse_feed(RSS,"NASA News","space",NOW)
  result=radar.collect({"items":old,"updated_at":"2026-10-28T06:00:00Z"},fetch=lambda url:(_ for _ in ()).throw(OSError("offline")),now=NOW)
  self.assertEqual(result["status"],"unavailable")
  self.assertEqual(len(result["items"]),1)
  self.assertEqual(result["updated_at"],"2026-10-28T06:00:00Z")
 def test_deduplication(self):
  x=radar.parse_feed(RSS,"NASA News","space",NOW)[0]
  merged=radar.merge([x],[x],NOW)
  self.assertEqual(len(merged),1)
if __name__=="__main__":unittest.main()
