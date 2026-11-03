#!/usr/bin/env python3
"""Require byte-identical compressed AAC actor/outro audio between private V20 and V21.

Read-only verification: FFmpeg's hash muxer receives copied AAC packets.
PASS does not establish audible language, sync, copyright or artistic quality.
"""
import argparse,subprocess,re,sys
def audio_packet_hash(path):
    process=subprocess.run(["ffmpeg","-hide_banner","-nostdin","-v","error","-i",path,
      "-map","0:a:0","-c:a","copy","-f","hash","-hash","sha256","-"],
       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
    m=re.search(r"SHA256=([a-fA-F0-9]{64})",process.stdout)
    if not m:raise RuntimeError("Cannot read encoded AAC SHA-256")
    return m.group(1).lower()
p=argparse.ArgumentParser()
p.add_argument("baseline");p.add_argument("revised")
a=p.parse_args()
before=audio_packet_hash(a.baseline);after=audio_packet_hash(a.revised)
ok=before==after
print("AAC_PACKETS_SHA256_BASE",before)
print("AAC_PACKETS_SHA256_NEW ",after)
print("BIT_EXACT_ACTOR_AND_OUTRO_AAC", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
