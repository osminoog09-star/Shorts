#!/usr/bin/env python3
"""M1lash NEUROOFFICE V4 -- fully code-rendered animation, narration-aligned subtitles.
Script depends on its neighboring V3 render module. Video and audio are rendered
without third-party artwork, music, or video clips; no publishing to platforms.
"""
import argparse, hashlib, importlib.util, json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('neurooffice_v3', HERE/'render_v3.py')
base=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)
OUT=HERE/'output'; OUT.mkdir(exist_ok=True)
FPS=base.FPS; CUT=base.CUT; W=base.W; H=base.H
# Word positions are from the actual seven Microsoft voice .json metadata segments.
WORD_TIMINGS=[
[["Попросил",.1,.67],["ИИ",.67,.84],["составить",.84,1.33],["справедливый",1.33,1.93],["график",1.93,2.28],["смен",2.28,2.67],["Он",3.51,3.77],["сказал",3.77,4.16],["учту",4.47,4.8],["пожелания",4.8,5.37],["абсолютно",5.37,5.96],["каждого",5.96,6.51]],
[["Начальник",.1,.75],["хочет",.75,1.13],["все",1.13,1.4],["выходные",1.4,1.85],["дома",1.85,2.24],["ИИ",3.08,3.38],["готово",3.61,4.12],["пожелание",4.24,4.82],["учтено",4.82,5.42]],
[["Коллеги",.1,.61],["просят",.61,.99],["убрать",.99,1.34],["ночные",1.34,1.93],["ИИ",2.74,3.02],["без",3.13,3.42],["проблем",3.42,3.86],["пожелания",4.05,4.6],["тоже",4.6,4.92],["учтены",4.92,5.48]],
[["Я",.1,.42],["открываю",.42,.91],["свой",.91,1.18],["график",1.18,1.69],["Понедельник",2.47,3.19],["ночь",3.37,3.81],["Вторник",4.59,5.29],["ночь",5.48,5.93],["Среда",6.71,7.26],["угадай",7.48,8.02],["блин",8.27,8.71]],
[["Спрашиваю",.1,.84],["а",1.08,1.26],["где",1.26,1.48],["справедливость",1.48,2.28],["Он",3.05,3.28],["отвечает",3.28,3.83],["недовольный",4.07,4.62],["всего",4.62,4.93],["один",4.93,5.32],["Раньше",6.17,6.73],["недовольны",6.73,7.28],["были",7.28,7.46],["все",7.46,7.83]],
[["Говорю",.1,.63],["тогда",.91,1.23],["сам",1.23,1.55],["выходи",1.55,1.88],["на",1.88,1.99],["смену",1.99,2.44],["Он",3.27,3.55],["пишет",3.55,3.94],["к",4.14,4.18],["сожалению",4.18,4.78],["ваша",5.06,5.33],["подписка",5.33,5.78],["не",5.78,5.87],["включает",5.87,6.38],["физический",6.38,6.93],["труд",6.93,7.27]],
[["Подпишись",.1,.88],["И",1.66,1.83],["спасибо",1.83,2.26],["всем",2.26,2.63],["кто",2.83,3.01],["досмотрел",3.01,3.61],["и",3.61,3.74],["поставил",3.74,4.24],["лайк",4.24,4.64]]]
# Each card appears with its first spoken word and stays stable for an entire phrase.
# Punctuation comes from original TTS script, not from guessed ASR.
CAPTIONS=[
 [(0,5,'Попросил ИИ составить|справедливый график смен.'),(6,11,'Он сказал: учту пожелания|абсолютно каждого.')],
 [(0,4,'Начальник хочет все|выходные дома.'),(5,8,'ИИ: готово, пожелание учтено.')],
 [(0,3,'Коллеги просят убрать ночные.'),(4,9,'ИИ: без проблем,|пожелания тоже учтены.')],
 [(0,3,'Я открываю свой график.'),(4,5,'Понедельник — ночь.'),(6,7,'Вторник — ночь.'),(8,10,'Среда — угадай, блин.')],
 [(0,3,'Спрашиваю: а где справедливость?'),(4,8,'Он отвечает: недовольный|всего один.'),(9,12,'Раньше недовольны были все.')],
 [(0,5,'Говорю: тогда сам|выходи на смену.'),(6,9,'Он пишет: к сожалению,'),(10,15,'ваша подписка не включает|физический труд.')],
 [(0,0,'Подпишись!'),(1,4,'И спасибо всем, кто'),(5,8,'досмотрел и поставил лайк.')]
]
# Prevent old fast-scrolling subtitle from drawing inside the V3 scene.
base.subtitle=lambda *a,**kw: None
_V3_HUMAN=base.draw_human
_V3_ROBOT=base.draw_robot

def human_v4(*args,**kwargs):
    sprite,xy=_V3_HUMAN(*args,**kwargs)
    # Screen-space clothing material: stitched lapels, catchlights and animated cuff accent.
    # New details are additional code strokes, not imported still images.
    scale=kwargs.get('scale',1)
    if not isinstance(scale,(int,float)) or scale<=0:return sprite,xy
    who=kwargs.get('identity', args[4] if len(args)>4 else 'hero')
    t=args[3] if len(args)>3 else 0
    q=ImageDraw.Draw(sprite,'RGBA')
    sc=lambda x,y:(round(x*scale),round(y*scale))
    s=lambda u:max(1,round(u*scale))
    # Suit pocket stitch at the upper chest, low intensity compared to main silhouette.
    q.line([sc(184,351),sc(194,353),sc(203,348)], fill=(223,237,226,175),width=s(2))
    q.line([sc(106,353),sc(118,360)], fill=(208,231,224,160),width=s(2))
    # Tuned per-shot belt / brass buttons; very small features to reduce plastic appearance.
    for y in (370,405):
        xx=177+1.1*math.sin(t*.8+y)
        x0,y0=sc(xx,y)
        q.ellipse((x0-s(2),y0-s(2),x0+s(2),y0+s(2)),fill=(239,208,155,215))
    if who=='hero':
        q.line([sc(88,422),sc(210,422)],fill=(75,144,159,110),width=s(2))
    return sprite,xy

def robot_v4(*args,**kwargs):
    sprite,xy=_V3_ROBOT(*args,**kwargs)
    scale=kwargs.get('scale',1)
    t=args[2] if len(args)>2 else 0
    q=ImageDraw.Draw(sprite,'RGBA');sc=lambda x,y:(round(x*scale),round(y*scale))
    thick=lambda v:max(1,round(v*scale))
    # Visor sweep and physically motivated thin reflections.
    glint=math.sin(t*1.35)*9
    q.line([sc(128+glint,150),sc(143+glint,162)],fill=(187,252,246,90),width=thick(2))
    q.line([sc(219,140),sc(228,144)],fill=(244,252,244,175),width=thick(2))
    # Ribbed joint and front chassis additional seam to break up the bland geometry.
    for y in (347,361,375):
        q.line([sc(116,y),sc(124,y+1)],fill=(169,209,205,100),width=thick(2))
    r=4+2*max(0,math.sin(t*2.3))
    x0,y0=sc(173,368)
    q.ellipse((x0-thick(r),y0-thick(r),x0+thick(r),y0+thick(r)),fill=(236,255,239,180))
    return sprite,xy

base.draw_human=human_v4
base.draw_robot=robot_v4

# Softer photographic lens vignetting, fixed across frames to avoid flashing.
def make_vignette():
    layer=Image.new('RGBA',(W,H));q=ImageDraw.Draw(layer)
    for k in range(18):
        pad=2+k*4
        alpha=max(0,15-int(k*.4))
        q.rounded_rectangle((pad,pad,W-pad,H-pad),radius=32,outline=(7,12,30,alpha),width=5)
    return layer
VIGNETTE=make_vignette()

def story_fx(im,scene,t,span):
    # Code-driven props reacting to specific speech, not random overlays or UI labels.
    overlay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(overlay)
    if scene==0:
        # Ambient AI computer power light; background-only near desk.
        radius=4+3*(math.sin(t*2.8)**2)
        d.ellipse((438-radius,570-radius,438+radius,570+radius),fill=(74,234,210,195))
    elif scene==1 and t>3.05:
        # Approval pulse around the accepted leave request.
        pulse=(t-3.05)%1.5/1.5
        radius=44+10*pulse
        d.ellipse((288-radius,366-radius*.43,288+radius,366+radius*.43),outline=(92,234,196,round(140*(1-pulse))),width=2)
    elif scene==2:
        # Night moon icon fades as request gets approved (dark blue icon, no new text).
        if t<2.1:
            cx,cy=465,308
            d.ellipse((cx-11,cy-11,cx+11,cy+11),fill=(230,235,209,175))
            d.ellipse((cx-6,cy-13,cx+16,cy+8),fill=(26,56,72,255))
    elif scene==3:
        # Selected night-shift row highlights appear on the voice cue, not merely shot time.
        for a,yy in [(3.36,278),(5.47,381),(7.45,484)]:
            if t>=a:
                fade=min(130,int((t-a)*210))
                d.rounded_rectangle((251,yy,502,yy+54),radius=10,outline=(252,139,151,fade),width=3)
    elif scene==4:
        # Counter 1 lights at "всего один"; underscores arithmetic punchline.
        if t>=4.88:
            pulse=math.sin((t-4.88)*3.5)**2
            d.ellipse((449-8-pulse*4,244-8-pulse*4,449+8+pulse*4,244+8+pulse*4),outline=(87,224,201,int(90+130*pulse)),width=2)
    elif scene==5:
        # Subscription denial signal flashes near main upper card.
        if t>5.35:
            xx=485;yy=154
            d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=(245,122,138,140+round(90*math.sin(t*3)**2)))
    elif scene==6:
        # Very restrained original procedural outro confetti.
        if t<2.5:
            for n in range(12):
                x=34+(n*61+t*(7+n%3)*4)%486;y=283+(n*23+int(t*53))%160
                if 25<x<512:
                    col=(101,223,204,140) if n%2 else (232,193,138,145)
                    d.ellipse((x,y,x+3,y+7),fill=col)
    im=Image.alpha_composite(im.convert('RGBA'),overlay)
    im=Image.alpha_composite(im,VIGNETTE)
    return im.convert('RGB')

def caption_at(scene,t):
    meta=WORD_TIMINGS[scene]
    for index,(first,last,label) in enumerate(CAPTIONS[scene]):
        st=meta[first][1]
        en=meta[last][2]
        next_start=meta[CAPTIONS[scene][index+1][0]][1] if index+1<len(CAPTIONS[scene]) else CUT[scene+1]-CUT[scene]
        # The card stays stable while an entire sentence is spoken; never flickers word by word.
        until=min(next_start-.09,en+.70)
        if st-.10<=t<until:
            return (label,st,en,first,last)
    return None

def caption_v4(im,scene,t):
    selected=caption_at(scene,t)
    if selected is None:return im
    label,start,end,first,last=selected
    rows=label.split('|')
    d=ImageDraw.Draw(im)
    box_height=117 if len(rows)==2 else 88
    top=814 if len(rows)==1 else 790
    # Consistent frame-safe position and clean visual hierarchy; title/scene panels remain.
    base.rect(d,(23,top,517,top+box_height),'#071829',18,'#416373',2)
    for i,row in enumerate(rows):
        font=22
        while d.textbbox((0,0),row,font=base.TTF[font])[2]>454 and font>17:
            font-=1
        d.text((270,top+43+i*39),row,font=base.TTF[font],anchor='mm',fill=base.WHITE)
    # Show progress subtly along bottom edge, based on true first/last word times.
    p=base.f((t-start)/max(.2,end-start))
    base.rect(d,(75,top+box_height-17,465,top+box_height-13),'#243a48',2)
    if p>0:base.rect(d,(75,top+box_height-17,75+390*p,top+box_height-13),base.CYAN if scene not in (3,5) else base.HOT,2)
    return im

def frame(scene,t,span):
    im=base.scene_frame(scene,t,span)
    im=story_fx(im,scene,t,span)
    return caption_v4(im,scene,t)

def validate_cues():
    for si,groups in enumerate(CAPTIONS):
        assert groups[0][0]==0
        assert groups[-1][1]==len(WORD_TIMINGS[si])-1
        for gi,(a,b,label) in enumerate(groups):
            assert a<=b and label
            if gi:assert groups[gi-1][1]+1==a
            assert WORD_TIMINGS[si][b][2]<=CUT[si+1]-CUT[si]+.02

def preview():
    base.load_voice_energy()
    images=[]
    for si in range(7):
        span=CUT[si+1]-CUT[si]
        for frac in (.26,.78):
            im=frame(si,span*frac,span)
            images.append(im.resize((216,384),Image.Resampling.LANCZOS))
    sheet=Image.new('RGB',(7*216,2*384),'#0c1c30')
    for si in range(7):
        for pi in range(2):sheet.paste(images[si*2+pi],(si*216,pi*384))
    path=OUT/'V4_STORYBOARD.jpg';sheet.save(path,quality=92)
    print('Preview',path,flush=True)

def run(preview_only=False):
    validate_cues()
    if not base.PREVIOUS.exists():raise RuntimeError('Missing original Dmitry narration')
    dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(base.PREVIOUS)]))['format']['duration'])
    assert abs(dur-CUT[-1])<.12,(dur,CUT[-1])
    base.load_voice_energy()
    preview()
    if preview_only:return
    frames=HERE/'frames';frames.mkdir(exist_ok=True)
    count=round(CUT[-1]*FPS)
    for k in range(count):
        if (frames/f'{k:05d}.jpg').exists():
            continue
        t=k/FPS
        scene=next((i for i in range(7) if CUT[i]<=t<CUT[i+1]),6)
        im=frame(scene,t-CUT[scene],CUT[scene+1]-CUT[scene])
        im.save(frames/f'{k:05d}.jpg',format='JPEG',quality=88,subsampling=0)
        if k%120==0: print('V4 rendered',k,'/',count,flush=True)
    out=OUT/'NEUROOFFICE_V4_SYNC_RU.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-framerate',str(FPS),'-i',str(frames/'%05d.jpg'),
                    '-i',str(base.PREVIOUS),'-map','0:v','-map','1:a:0','-vf','scale=1080:1920:flags=lanczos,format=yuv420p',
                    '-c:v','libx264','-preset','veryfast','-crf','20','-c:a','copy','-movflags','+faststart',str(out)],check=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
    actual=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(out)]))['format']['duration'])
    assert abs(actual-CUT[-1])<.12
    # Audio stream integrity: decoded PCM SHA256 of source and output must match.
    def pcm_hash(p):
        x=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-vn','-ac','1','-ar','48000','-f','s16le','-'])
        return hashlib.sha256(x).hexdigest()
    same=pcm_hash(base.PREVIOUS)==pcm_hash(out)
    if not same:raise RuntimeError('NO-GO: narration stream modified')
    qa={'status':'TECHNICAL_PASS_ART_REVIEW_REQUIRED','video':str(out),'duration':actual,
        'frames':count,'fps':FPS,'size_bytes':out.stat().st_size,
        'caption_method':'original TTS word-start/word-end timestamps, stable grouped phrase cards',
        'caption_groups':sum(map(len,CAPTIONS)),'caption_words':sum(map(len,WORD_TIMINGS)),
        'voice_pcm_identical':same,'h264_full_decode':'PASS','video_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'posted_to_youtube':False}
    (OUT/'QA_V4.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    run(preview_only=args.preview)