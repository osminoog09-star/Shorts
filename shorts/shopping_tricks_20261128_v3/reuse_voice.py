"""Reassemble verified Denis WAVs from the owner's private Drive.
Never writes voice data into the repo. New lines must independently pass ASR.
"""
import hashlib,json,os,sys
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import voice_private_io as vp
OLD="shopping_tricks_20261128"
NEW="shopping_tricks_20261128_v3"
FILES={"manifest.json":"1AyZUmpZLCs8oeYNefWpsVdWTjSPmbNck","v02.wav":"1yTdyDTGTTenG50guJHroGgvpSI70UX_-","v03.wav":"1M0-N_ZyBolAolMJuqKmlcrImgVV_Dzd8","v04.wav":"1CtyuyCwf278f5EXRAmixMAYz9Jj_vf_X","v05.wav":"1Du0rrYyjx-OoMhSscfbwgH-cve8hixi_","v07.wav":"1ERjUi7116iBydy6s_NVe0IGFy81Mpeh6"}
def fetch(name,token):
    req=Request("https://www.googleapis.com/drive/v3/files/"+FILES[name]+"?alt=media",headers={"Authorization":"Bearer "+token})
    with urlopen(req,timeout=60) as res:
        data=res.read(20*1024*1024+1)
    assert 0<len(data)<=20*1024*1024
    return data
def main():
    out=Path(sys.argv[1]); manifest=out/"manifest.json"
    fresh=json.loads(manifest.read_text())
    assert fresh["job_id"]==NEW and fresh["voice_id"]=="denis-qwen3tts-reference-v1" and fresh["speaker"]=="denis"
    token=vp.refresh_access_token(dict(os.environ))
    previous=json.loads(fetch("manifest.json",token))
    assert previous["job_id"]==OLD and previous["speaker"]==fresh["speaker"] and previous["voice_id"]==fresh["voice_id"]
    old={u["id"]:u for u in previous["utterances"]}
    new={u["id"]:u for u in fresh["utterances"]}
    assert set(new)=={"v01","v06","v07"}
    for dest,source in {"v02":"v02","v03":"v03","v04":"v04","v05":"v05","v08":"v07"}.items():
        u=dict(old[source]); assert u["asr_pass"] is True and u["voice_id"]==fresh["voice_id"]
        data=fetch(source+".wav",token)
        assert hashlib.sha256(data).hexdigest()==u["sha256"]
        u["id"]=dest;u["source_file"]="audio/"+dest+".wav"
        (out/u["source_file"]).write_bytes(data)
        new[dest]=u
    assert set(new)=={f"v{i:02d}" for i in range(1,9)}
    assert all(u["asr_pass"] is True and hashlib.sha256((out/u["source_file"]).read_bytes()).hexdigest()==u["sha256"] for u in new.values())
    fresh["utterances"]=[new[f"v{i:02d}"] for i in range(1,9)]
    fresh["reused_verified_voice_job"]=OLD
    manifest.write_text(json.dumps(fresh,ensure_ascii=False,indent=2),encoding="utf-8")
    print("MERGE PASS: 5 reused SHA-verified WAVs; 3 new ASR-verified WAVs")
if __name__=="__main__":main()
