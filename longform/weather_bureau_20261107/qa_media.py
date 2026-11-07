"""Extract actual rendered shot coverage; PIL only arranges QA thumbnails."""
from pathlib import Path
import argparse,json,subprocess,io
from PIL import Image,ImageDraw
HERE=Path(__file__).parent;OUT=Path(r'C:\M1lash\Работа\weather_bureau_20261107')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('movie');ap.add_argument('--label',default='final');a=ap.parse_args()
    tl=json.loads((HERE/'timeline.json').read_text('utf8'))
    target=OUT/('qa_'+a.label);target.mkdir(exist_ok=True)
    manifest=[]
    for i,s in enumerate(tl['scenes']):
        tm=(s['start']+s['end'])/2
        dest=target/(s['id']+'.jpg')
        p=subprocess.run(['ffmpeg','-v','error','-y','-ss',str(tm),'-i',a.movie,'-frames:v','1','-vf','scale=480:270','-q:v','3',str(dest)],capture_output=True)
        if p.returncode or not dest.is_file():raise RuntimeError('Missing decoded shot '+s['id'])
        manifest.append(dict(shot=s['id'],time_s=tm,frame=dest.name,spoken_words=s['spoken_words'],mode=s['mode'],location=s['location']))
    for n,start in enumerate(range(0,len(manifest),24)):
        sheet=Image.new('RGB',(1600,1500),'#20252b');draw=ImageDraw.Draw(sheet)
        for j,item in enumerate(manifest[start:start+24]):
            x=(j%4)*400;y=(j//4)*250
            image=Image.open(target/item['frame']).convert('RGB').resize((400,225))
            sheet.paste(image,(x,y));draw.text((x+5,y+227),f"{item['shot']} {item['time_s']:.1f}s {item['mode']}",fill='white')
        sheet.save(target/f'coverage_{n:02}.jpg',quality=91)
    (target/'coverage_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('ACTUAL_SHOT_COVERAGE',len(manifest),'shots',len(list(target.glob('coverage_*.jpg'))),'sheets',target)

if __name__=='__main__':main()
