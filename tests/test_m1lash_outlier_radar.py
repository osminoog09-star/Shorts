import datetime as dt
import importlib.util
import tempfile
import unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"motion-studio/automation/outlier_radar.py"
spec=importlib.util.spec_from_file_location("outlier_radar",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW=dt.datetime(2026,10,28,12,0,tzinfo=dt.timezone.utc)
VIDEO_ID="AbCdEF01234"
CHANNEL_ID="UCchannel123"
PUBLISHED="2026-10-25T10:00:00Z"
BASE_IDS=["oldvideo%03d"%i for i in range(10)]


def response(method,params):
    if method=="search":
        return {"items":[{"id":{"videoId":VIDEO_ID}}]}
    if method=="channels":
        return {"items":[{
            "id":CHANNEL_ID,
            "statistics":{"subscriberCount":"10900","hiddenSubscriberCount":False},
            "contentDetails":{"relatedPlaylists":{"uploads":"UUupload"}}}]}
    if method=="playlistItems":
        return {"items":[{"snippet":{"resourceId":{"videoId":vid},"publishedAt":"2026-10-26T10:00:00Z"},
                          "contentDetails":{"videoPublishedAt":"2026-09-01T10:00:00Z"}}
                         for vid in BASE_IDS]}
    if method=="videos":
        if "maxResults" in params:
            raise AssertionError("videos.list(id=...) must NOT include maxResults")
        ids=params["id"].split(",")
        rows=[]
        for vid in ids:
            if vid==VIDEO_ID:
                rows.append({"id":VIDEO_ID,
                   "snippet":{"title":"Original small channel technology documentary",
                              "channelId":CHANNEL_ID,"channelTitle":"Example Channel","publishedAt":PUBLISHED},
                   "statistics":{"viewCount":"250000"},
                   "contentDetails":{"duration":"PT24M00S"}})
            elif vid in BASE_IDS:
                rows.append({"id":vid,
                   "snippet":{"publishedAt":"2026-09-01T10:00:00Z"},
                   "statistics":{"viewCount":"10000"},
                   "contentDetails":{"duration":"PT25M00S"}})
        return {"items":rows}
    raise AssertionError("unexpected method "+method)


class OutlierTests(unittest.TestCase):
    def test_duration_buckets(self):
        self.assertEqual(m.group_of(1260),"long")
        self.assertIsNone(m.group_of(1259))
        self.assertEqual(m.group_of(45),"short")
        self.assertEqual(m.seconds_iso8601("PT1H02M04S"),3724)
        self.assertIsNone(m.seconds_iso8601("invalid"))
    def test_baseline_not_with_too_few_uploads(self):
        self.assertIsNone(m.median_outlier(30000,[1000,1000,1000,1000]))
        self.assertEqual(m.median_outlier(250000,[10000]*10),25)
    def test_not_false_current_velocity(self):
        self.assertIsNone(m.growth_velocity(VIDEO_ID,300,{},NOW))
        old={VIDEO_ID:{"views":200,"measured_at":"2026-10-28T06:00:00Z"}}
        self.assertEqual(m.growth_velocity(VIDEO_ID,300,old,NOW),16.67)
    def test_decreasing_views_no_negative_growth(self):
        self.assertIsNone(m.growth_velocity(VIDEO_ID,80,{VIDEO_ID:{"views":150,"measured_at":"2026-10-28T06:00:00Z"}},NOW))
    def test_quota_is_bounded(self):
        api=m.YouTubeAPI("fake-key",request=lambda method,params:{"items":[]})
        for i in range(m.MAX_SEARCH_CALLS):
            api.get("search",part="snippet")
        with self.assertRaises(ValueError):
            api.get("search",part="snippet")
    def test_realistic_fake_scan(self):
        api=m.YouTubeAPI("fake-key",request=response)
        output=m.scan(api,now=NOW)
        self.assertEqual(output["status"],"success")
        self.assertEqual(len(output["items"]),1)
        record=output["items"][0]
        self.assertEqual(record["outlier_ratio"],25)
        self.assertEqual(record["baseline_sample_count"],10)
        self.assertEqual(record["duration_s"],1440)
        self.assertIsNone(record["recent_views_per_hour"])
        self.assertEqual(record["faceless_status"],"NOT_ASSESSED_API_CANNOT_CONFIRM")
        self.assertEqual(api.calls["search"],12)
    def test_second_scan_growth(self):
        baseline=m.scan(m.YouTubeAPI("demo",request=response),now=NOW)
        api=m.YouTubeAPI("demo",request=lambda method,params:(
          {"items":[{"id":VIDEO_ID,"snippet":{"title":"Documentary","channelId":CHANNEL_ID,"channelTitle":"Channel","publishedAt":PUBLISHED},"statistics":{"viewCount":"280000"},"contentDetails":{"duration":"PT24M"}}]} if method=="videos" and VIDEO_ID in params.get("id","") and not any(x in params.get("id","") for x in BASE_IDS)
          else response(method,params)))
        # Ensure measured difference if second observation is at a newer time.
        next_time=NOW+dt.timedelta(hours=12)
        result=m.scan(api,old=baseline,now=next_time)
        self.assertEqual(result["items"][0]["recent_views_per_hour"],2500)
    def test_batch_uses_only_supported_id_params(self):
        seen=[]
        def strict(method, params):
            if method=="videos" and "maxResults" in params:
                raise ValueError("YouTube API would reject id+maxResults")
            seen.append((method, params))
            return {"items":[]}
        api=m.YouTubeAPI("fake",request=strict)
        api.batched("videos",["abc123"]*80,part="statistics")
        self.assertEqual(len(seen),1)
        self.assertEqual(seen[0][1]["id"],"abc123")
        self.assertNotIn("maxResults",seen[0][1])

    def test_other_channel_playlist_failure_isolated(self):
        def flaky(method,params):
            if method=="playlistItems":
                raise RuntimeError("403 inaccessible channel")
            return response(method,params)
        output=m.scan(m.YouTubeAPI("fake",request=flaky),now=NOW)
        self.assertEqual(len(output["items"]),1)
        self.assertEqual(output["items"][0]["baseline_status"],"UNAVAILABLE_NO_RATIO")
        self.assertIsNone(output["items"][0]["outlier_ratio"])

    def test_video_publication_date_over_playlist_insertion_date(self):
        output=m.scan(m.YouTubeAPI("fake",request=response),now=NOW)
        self.assertEqual(output["items"][0]["baseline_sample_count"],10)

    def test_no_api_key_in_errors(self):
        key="private-key"
        api=m.YouTubeAPI(key,request=lambda method,params:{"items":[]})
        self.assertNotIn(key,str(m.scan(api,now=NOW)))
    def test_published_age(self):
        r={"video_id":VIDEO_ID,"published_at":"2026-10-25T10:00:00Z","views":4,"duration_s":1259}
        self.assertFalse(m.validate_row(r,NOW))
if __name__=="__main__":unittest.main()
