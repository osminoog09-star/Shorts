from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,math,os
HERE=Path(__file__).parent.resolve()
OUT=Path(os.environ.get('BOT_AUDIT_WORK',r'C:\M1lash\Работа\bot_audit_20261112'))
def guard():
    ps="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|obs' } | Select-Object Name,CommandLine | ConvertTo-Json -Compress"
    out=subprocess.check_output(['powershell','-NoProfile','-Command',ps],encoding='utf-8',errors='replace')
    items=json.loads(out or '[]')
    if isinstance(items,dict):items=[items]
    for p in items:
        cmd=(p.get('CommandLine') or '').lower()
        if any(x in cmd for x in ('capture_chrome_window','clip_recorder','gdigrab','ddagrab','wgc_record')):
            raise RuntimeError('Active recording; wait before rendering')
def main():
    review=json.loads((OUT/'animatic_review.json').read_text('utf-8'))
    assert review['decision']=='GO' and review['actual_frames_viewed']
    assert hashlib.file_digest((OUT/'animatic.mp4').open('rb'),'sha256').hexdigest()==review['sha256']
    guard()
    tl=json.loads((OUT/'timeline.json').read_text('utf-8'))
    def render(ch):
        dest=OUT/f'chapter_{ch:02d}_silent.mp4'
        ss=[s for s in tl['scenes'] if s['chapter']==ch]
        expected=(round(ss[-1]['end']*30) if ch!=8 else math.ceil(tl['duration_s']*30))-round(ss[0]['start']*30)
        with (OUT/f'chapter_{ch:02d}_render.log').open('w',encoding='utf-8') as log:
            subprocess.run(['node',str(HERE/'film.cjs'),f'chapter-{ch}'],stdout=log,stderr=subprocess.STDOUT,check=True)
        count=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(dest)],text=True).strip()
        assert int(count)==expected,(ch,count,expected)
        print('CHAPTER_RENDERED',ch,expected,flush=True)
        return dest
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(render,range(1,9)))
    lst=OUT/'chapters_concat.txt'
    lst.write_text(''.join("file '"+f.as_posix()+"'\n" for f in files),'utf-8')
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(lst),'-i',str(OUT/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-shortest','-movflags','+faststart',str(OUT/'body.mp4')],check=True)
    print('FULL_BODY_RENDERED',OUT/'body.mp4',flush=True)
if __name__=='__main__':main()
