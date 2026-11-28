#!/usr/bin/env python3
"""M1lash S3-D25: three shopping tricks. Original comic SVG animation, Denis voice only.
Usage: python render.py --voice-dir DIR --out DIR ; --preview renders a silent animatic.
No outro, no publishing. All media stays local/private.
"""
import argparse, hashlib, html, json, math, pathlib, subprocess, textwrap
import cairosvg
P=pathlib.Path
INK="#171528"; PAPER="#fff7dc"; RED="#f34459"; GOLD="#ffc83d"; BLUE="#42d6e8"; GREEN="#86e4a9"
LINES=[
("v01","Три уловки магазинов, на которые легко попасться.", "hook"),
("v02","Первая. Товар стоил пятьсот евро. Цену подняли до тысячи.", "price1"),
("v03","Потом скидка в пятьдесят процентов. А платишь всё те же пятьсот.", "price2"),
("v04","Вторая. Таймер обещает конец скидки. Обновляешь страницу, и он начинается снова.", "timer"),
("v05","Третья. Остался последний товар. Но иногда это просто надпись, а не реальный остаток.", "stock"),
("v06","В Евросоюзе при объявлении скидки обычно указывают самую низкую цену за последние тридцать дней.", "rule"),
("v07","Проверяй цены. Не спеши платить только потому, что тебя торопят.", "end")]
def sh(*a):
    return subprocess.run(list(map(str,a)),check=True,capture_output=True)
def tx(x,y,s,size=62,fill=INK,weight=900,anchor="middle"):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans" font-weight="{weight}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(s))}</text>'
def rr(x,y,w,h,f,rad=30,stroke=INK,sw=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rad}" fill="{f}" stroke="{stroke}" stroke-width="{sw}"/>'
def circ(x,y,r,f,sw=8):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}" stroke="{INK}" stroke-width="{sw}"/>'
def path(d,f="none",s=INK,w=12):
    return f'<path d="{d}" fill="{f}" stroke="{s}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'
def group(s,x=0,y=0,scale=1,angle=0):
    return f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})">{s}</g>'
def sticker(x,y,w,h,color,label,sz=86):
    return group(rr(13,17,w,h,INK,30,INK,0)+rr(0,0,w,h,color,30,"white",18)+rr(0,0,w,h,color,30,INK,7)+tx(w/2,h/2+sz*.34,label,sz),x,y)
def tv(x,y,s):
    obj=rr(0,0,640,390,INK,35, "white",15)+rr(19,19,602,352,"#292f55",22,INK,5)
    obj+=path("M 30 325 Q 170 145 320 205 T 620 65 L 620 365 L 30 365 Z","#6a57cb","none",0)
    obj+=path("M 30 265 Q 125 180 230 255 T 430 195 T 620 165 L 620 365 L 30 365 Z","#38bfd0","none",0)
    obj+=path("M 245 390 L 395 390 L 425 444 L 215 444 Z",INK)+rr(180,440,280,23,INK,8,INK,0)
    return group(obj,x,y,s)
def burst(x,y,r,color):
    pts=[]
    for i in range(24):
        a=i*math.pi/12; q=r*(1 if i%2==0 else .76)
        pts.append(f"{x+math.cos(a)*q:.1f},{y+math.sin(a)*q:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
def phone(x,y):
    return group(rr(14,18,640,820,INK,48,INK,0)+rr(0,0,640,820,INK,48,"white",14)+rr(23,24,594,772,"#fffdfa",35,INK,4)+rr(232,39,176,18,INK,9,INK,0),x,y)
def package(x,y,s=1,fade=1):
    obj=path("M 0 65 L 135 0 L 270 65 L 135 135 Z","#ffd174")+path("M 0 65 L 135 135 L 135 280 L 0 210 Z","#cf8749")+path("M 135 135 L 270 65 L 270 210 L 135 280 Z","#f3af59")+path("M 65 34 L 201 99 L 201 150","#fff3bf",INK,5)
    return f'<g opacity="{fade}">'+group(obj,x,y,s)+"</g>"
def caption(text):
    words=textwrap.wrap(text, width=27,break_long_words=False,break_on_hyphens=False)
    n=len(words); size=53 if n<=3 else 46
    y=1410-(n-1)*size*.63
    h=n*size*1.27+36
    return rr(65,y-size-17,880,h,INK,25,"white",5)+''.join(tx(505,y+i*size*1.27,w,size,"white") for i,w in enumerate(words))
def frame(key,u,t,sub):
    u=max(0,min(1,u)); pulse=1+.018*math.sin(t*5); bg={"hook":GOLD,"price1":"#f8d783","price2":"#f8d783","timer":"#89e3ef","stock":"#b4e9b8","rule":"#dcd1ff","end":GOLD}[key]
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><defs><pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="3" fill="{INK}" opacity=".15"/></pattern></defs><rect width="1080" height="1920" fill="{bg}"/><rect width="1080" height="1920" fill="url(#dots)"/>']
    out.append(path("M -50 1120 L 1120 610 L 1120 970 L -50 1510 Z",PAPER,"none",0))
    out.append(tx(500,183,"M1LASH  /  ДЕНЬГИ",34,INK,700))
    if key=="hook":
        out += [tx(500,335,"3 УЛОВКИ",105),tx(500,442,"МАГАЗИНОВ",91),group(burst(0,0,265,RED)+tx(0,34,"−50%",100,"white"),500,830,pulse,-8),sticker(102,1100,790,114,"white","НЕ ПОПАДИСЬ!",61)]
    elif key in ("price1","price2"):
        out += [tx(500,335,"01 / ЦЕНА",80),tv(174,448,.99)]
        if key=="price1":
            jump= min(1,max(0,(u-.30)*3))
            price="500 €" if u<.53 else "1 000 €"
            out.append(sticker(150,950-52*math.sin(math.pi*jump),700,180,GOLD if u<.53 else RED,price,111))
            out.append(tx(500,1220,"БЫЛО" if u<.53 else "ПОДНЯЛИ ЦЕНУ",59))
        else:
            out += [sticker(142,928,710,160,GREEN,"500 €",110),group(burst(0,0,145,RED)+tx(0,23,"−50%",57,"white"),826,610,pulse,-12),tx(500,1183,"ЭКОНОМИЯ: 0 €",65)]
    elif key=="timer":
        out += [tx(500,335,"02 / ТАЙМЕР",77),phone(180,390),tx(500,570,"СКИДКА СГОРИТ!",46)]
        reset=u>.65
        remain=max(0,10-int((u/(.65 if not reset else 1))*10)) if not reset else max(1,10-int((u-.65)*12))
        out += [rr(270,650,460,165,RED,24,INK,8),tx(500,761,f"00:{remain:02d}",96,"white"),rr(279,862,442,105,GOLD,21),tx(500,930,"КУПИТЬ",56),tx(500,1060,"↻",95),tx(500,1165,"СНОВА 10 СЕКУНД" if reset else "ОБНОВИ СТРАНИЦУ",42)]
    elif key=="stock":
        out += [tx(500,335,"03 / ДЕФИЦИТ",77),sticker(100,420,800,140,RED,"ОСТАЛСЯ 1!",72)]
        for k in range(6):
            x=110+(k%3)*260; y=675+(k//3)*250
            if k==0 or u>.48:
                p=max(0,min(1,(u-.48)*7-(k-1)*.13)) if k else 1
                if p>0: out.append(package(x,y,.85,p))
        out.append(tx(500,1210,"А ТОЧНО ЛИ?" if u>.48 else "СРОЧНО ПОКУПАЙ?",54))
    elif key=="rule":
        out += [tx(500,335,"ПРОВЕРЬ ЦЕНУ",77),rr(112,480,780,674,PAPER,40),tx(500,605,"30 ДНЕЙ",95)]
        for i,v in enumerate([.65,.65,.65,.70,.67,.65,1,.65]):
            x=185+i*89; h=300*v; out.append(rr(x,1000-h,54,h,RED if i==6 else BLUE,8,INK,4))
        out += [path("M 155 1010 L 838 1010", "none",INK,8),tx(500,1110,"СМОТРИ МИНИМУМ",48)]
    else:
        out += [tx(500,335,"НЕ ТОРОПИСЬ!",85),group(burst(0,0,240,GREEN)+tx(0,29,"СТОП",91),500,770,pulse,-8),sticker(100,1080,800,120,"white","СРАВНИ ЦЕНЫ",63)]
    out.append(caption(sub));out.append("</svg>")
    return "".join(out)
def dur(p):
    return float(sh("ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p).stdout)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--voice-dir",type=P);ap.add_argument("--out",type=P,required=True);ap.add_argument("--preview",action="store_true");a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True); fps=15 if not a.preview else 10; scale=1 if not a.preview else .5
    starts=[]; audio=[]; total=0; manifest=None
    if not a.preview:
        manifest=json.loads((a.voice_dir/"manifest.json").read_text())
        assert manifest["speaker"]=="denis" and manifest["voice_id"]=="denis-qwen3tts-reference-v1"
        items={x["id"]:x for x in manifest["utterances"]}
    for lid,text,key in LINES:
        if a.preview: seconds=max(2.5,len(text.split())/2.8)
        else:
            item=items[lid];assert item["asr_pass"] is True and item["text"]==text
            p=a.voice_dir/item["source_file"];assert hashlib.sha256(p.read_bytes()).hexdigest()==item["sha256"]
            seconds=dur(p); audio.append(p)
        n=math.ceil((seconds+.15)*fps);starts.append((lid,text,key,n,seconds,total/fps));total+=n
    assert total/fps<59.5
    w,h=int(1080*scale),int(1920*scale); silent=a.out/"picture.mp4"
    cmd=["ffmpeg","-y","-v","error","-f","image2pipe","-vcodec","png","-r",str(fps),"-i","-","-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","fast","-crf","19",str(silent)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for lid,text,key,n,seconds,start in starts:
            words=text.split(); chunks=[];i=0
            while i<len(words):
                chunks.append(" ".join(words[i:i+6]));i+=6
            for f in range(n):
                u=f/max(1,n-1);idx=min(len(chunks)-1,int(u*len(chunks)))
                svg=frame(key,u,start+f/fps,chunks[idx])
                png=cairosvg.svg2png(bytestring=svg.encode(),output_width=w,output_height=h)
                proc.stdin.write(png)
        proc.stdin.close()
        if proc.wait():raise RuntimeError("video encode failed")
    except BaseException:
        proc.kill();raise
    final=a.out/("M1lash_3_tricks_preview.mp4" if a.preview else "M1lash_3_tricks_ru.mp4")
    if a.preview:silent.replace(final)
    else:
        for i,((lid,text,key,n,seconds,start),p) in enumerate(zip(starts,audio)):
            sh("ffmpeg","-v","error","-y","-i",p,"-af",f"apad,atrim=duration={n/fps:.6f}","-ar","48000","-ac","1",a.out/f"clip{i}.wav")
        (a.out/"concat.txt").write_text("\n".join(f"file 'clip{i}.wav'" for i in range(len(audio)))+"\n")
        sh("ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",a.out/"concat.txt","-af","loudnorm=I=-15:TP=-1.5:LRA=7","-ar","48000",a.out/"voice.wav")
        sh("ffmpeg","-v","error","-y","-i",silent,"-i",a.out/"voice.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",final)
    sh("ffmpeg","-v","error","-xerror","-i",final,"-f","null","-")
    probe=json.loads(sh("ffprobe","-v","error","-show_streams","-show_format","-of","json",final).stdout)
    vs=next(x for x in probe["streams"] if x["codec_type"]=="video")
    assert int(vs["width"])==w and int(vs["height"])==h
    if not a.preview:
        au=next(x for x in probe["streams"] if x["codec_type"]=="audio")
        assert abs(float(vs["duration"])-float(au["duration"]))<.25
    report={"status":"DRAFT_OWNER_REVIEW","decode":"PASS","preview":a.preview,"seconds":dur(final),"resolution":[w,h],"sha256":hashlib.sha256(final.read_bytes()).hexdigest(),"voice":"none" if a.preview else "Denis Qwen3-TTS / all ASR PASS","caption_timing":"phrase estimates, manual AV review pending","outro":False,"sources":["https://commission.europa.eu/news-and-media/news/eu-check-reveals-misleading-sales-practices-online-2026-03-26_en","https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A52023SC0335"],"illustrative_examples":True}
    (a.out/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
