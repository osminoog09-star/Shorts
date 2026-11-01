#!/usr/bin/env python3
"""Verify approved 6.6s outro AAC priming after an MP4 concat.
Byte-identical AAC payloads alone are insufficient for identical playback.
"""
import argparse
import json
import subprocess

def packets(path):
    raw=subprocess.check_output([
        "ffprobe","-v","error","-select_streams","a:0",
        "-show_packets","-show_entries","packet=pts_time,data_hash,side_data_list",
        "-show_data_hash","sha256","-of","json",str(path)])
    return json.loads(raw)["packets"]

def skip_count(packet):
    return max([int(row.get("skip_samples",0)) for row in
                packet.get("side_data_list",[])] or [0])

def verify(outro,final):
    reference=packets(outro)
    joined=packets(final)
    first=reference[0]
    expected=skip_count(first)
    matched=[x for x in joined if x.get("data_hash")==first.get("data_hash")]
    observed=skip_count(matched[0]) if len(matched)==1 else 0
    return {"status":"PASS" if expected and observed==expected else "FAIL",
            "required_skip_samples":expected,"found_skip_samples":observed}

if __name__=='__main__':
    import sys
    value=verify(sys.argv[1],sys.argv[2])
    print(json.dumps(value))
    sys.exit(0 if value['status']=='PASS' else 1)
