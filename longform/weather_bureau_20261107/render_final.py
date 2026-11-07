"""Render approved actual-timed animatic in four independent local workers."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess
HERE=Path(__file__).parent.resolve();ROOT=HERE.parents[1]
OUT=Path(r'C:\M1lash\Работа\weather_bureau_20261107')

def main():
    review=json.loads((OUT/'animatic_review.json').read_text('utf8'))
    assert review['decision']=='GO' and review['actual_frames_viewed']
    assert hashlib.sha256((OUT/'animatic.mp4').read_bytes()).hexdigest()==review['animatic_sha256']
    # Do not start video rendering while a capture process is running anywhere on this PC.
    ps="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ffmpeg|python|obs' } | Select-Object Name,CommandLine | ConvertTo-Json -Compress"
    result=subprocess.run(['powershell','-NoProfile','-Command',ps],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
    processes=json.loads(result.stdout or '[]');processes=[processes] if isinstance(processes,dict) else processes
    for p in processes:
        cmd=(p.get('CommandLine') or '').lower()
        if any(x in cmd for x in ['gdigrab','ddagrab','record_chrome','capture_window','wgc_record']):raise RuntimeError('Capture active: wait for recording to finish')
    tl=json.loads((HERE/'timeline.json').read_text('utf8'));fps=tl['fps']
    def render(ch):
        dest=OUT/f'chapter_{ch:02d}_silent.mp4'
        ss=[s for s in tl['scenes'] if s['chapter']==ch]
        expected=(round(ss[-1]['end']*fps) if ch!=8 else __import__('math').ceil(tl['duration_s']*fps))-round(ss[0]['start']*fps)
        with (OUT/f'chapter_{ch:02d}_render.log').open('w',encoding='utf8') as log:
            subprocess.run(['node',str(HERE/'src/film.cjs'),f'chapter-{ch}'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        count=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(dest)],text=True).strip()
        assert int(count)==expected,(ch,count,expected)
        print('CHAPTER_RENDERED',ch,expected,'frames',flush=True)
        return dest
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(render,range(1,9)))
    lst=OUT/'chapters_concat.txt';lst.write_text(''.join("file '"+f.as_posix()+"'\n" for f in files),'utf8')
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(OUT/'film_silent.mp4')],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'film_silent.mp4'),'-i',str(OUT/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-shortest','-movflags','+faststart',str(OUT/'body.mp4')],check=True)
    print('FULL_BODY_RENDERED',OUT/'body.mp4',flush=True)

if __name__=='__main__':main()
