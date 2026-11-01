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
