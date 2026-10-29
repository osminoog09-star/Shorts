from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).resolve().parent.parent
v=r/'out/M1lash_News_V2_Quality_26m50.mp4'
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
subprocess.run(['python3',str(r/'tools/longform_duration_gate.py'),str(v),'--report',str(r/'out/qa/DURATION_GATE.json')],check=True)
subprocess.run(['python3',str(r/'tools/audit_metrics.py'),str(v),str(r/'out/qa/v2_metrics.json')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels','-of','json',str(v)]))
(r/'out/qa/FINAL_PROBE.json').write_text(json.dumps(probe,indent=2))
hashv=subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-map','0:a:0','-c:a','copy','-f','hash','-'],text=True).strip()
hasho=(r/'out/qa/ORIGINAL_AUDIO_HASH.txt').read_text().strip()
assert hashv==hasho,(hashv,hasho)
result={'full_decode':'PASS','audio_packet_hash_identical':True,'audio_hash':hashv,'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'status':'OWNER_REVIEW','voices_unchanged':['ru-RU-DmitryNeural','ru-RU-SvetlanaNeural'],'duration_seconds':float(probe['format']['duration']),'size_bytes':int(probe['format']['size'])}
(r/'out/qa/FINAL_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))

(r/'out/CURRENT_EXPORT_PENDING').unlink(missing_ok=True)
