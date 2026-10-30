#!/usr/bin/env python3
"""Render a precise 2560x1440 M1lash banner using Pillow (all text in central safe area)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

W, H = 2560, 1440
OUT = Path(__file__).resolve().parents[1] / "publishing" / "branding" / "banner.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
im = Image.new("RGB", (W, H), "#0b1024")
px = im.load()
for y in range(H):
    for x in range(W):
        q = math.hypot((x-W*0.50)/(W*.85), (y-H*.47)/(H*.8))
        pulse = max(0, 1-q)
        r = int(10+18*pulse+7*(x/W))
        g = int(14+16*pulse+6*(y/H))
        b = int(31+48*pulse+11*(x/W))
        px[x, y] = (r,g,b)
d = ImageDraw.Draw(im,"RGBA")
for x in range(90,W+300,180):
    d.line([(x,0),(x-440,H)],fill=(90,110,235,20),width=2)
for y in range(80,H,150):
    d.line([(0,y),(W,y)],fill=(128,141,234,12),width=2)
for i in range(28):
    x=(167*i*i+211*i+123)%W
    y=(109*i*i+277*i+39)%H
    rr=3+i%4
    d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(173,150,255,88))
for radius,rgba,weight in [(590,(98,82,250,110),4),(780,(215,62,206,80),2),(990,(62,132,241,60),2)]:
    d.arc((W//2-radius,H//2-radius,W//2+radius,H//2+radius),15,165,fill=rgba,width=weight)
    d.arc((W//2-radius,H//2-radius,W//2+radius,H//2+radius),205,345,fill=rgba,width=weight)
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
main=ImageFont.truetype(fontfile,215)
tag=ImageFont.truetype(fontfile,55)
sub=ImageFont.truetype(regular,34)
title="M1LASH"
x,y=W//2,670
glow=Image.new("RGBA",(W,H))
g=ImageDraw.Draw(glow)
g.text((x,y),title,font=main,anchor="mm",fill=(100,103,255,255),stroke_width=12,stroke_fill=(99,78,255,255))
im=Image.alpha_composite(im.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(32)))
d=ImageDraw.Draw(im,"RGBA")
for n in range(12,0,-3):
    d.text((x+n,y+n),title,font=main,anchor="mm",fill=(46,29,118,150),stroke_width=0)
d.text((x,y),title,font=main,anchor="mm",fill=(255,255,255,255),stroke_width=3,stroke_fill=(172,150,255,220))
d.line((800,785,1760,785),fill=(236,88,211,170),width=5)
d.text((x,838),"КИНО. ИИ. СМЕХ.",font=tag,anchor="mm",fill=(226,224,253,255))
d.text((x,909),"НОВЫЕ SHORTS КАЖДЫЙ ДЕНЬ",font=sub,anchor="mm",fill=(184,189,234,255))
# YouTube safe text zone: central 1546x423 = x[507,2053], y[508,931].
for font,txt,cy in [(main,title,670),(tag,"КИНО. ИИ. СМЕХ.",838),(sub,"НОВЫЕ SHORTS КАЖДЫЙ ДЕНЬ",909)]:
    bb=d.textbbox((x,cy),txt,font=font,anchor="mm")
    assert bb[0]>=507 and bb[2]<=2053 and bb[1]>=508 and bb[3]<=931, (txt,bb)
im.convert("RGB").save(OUT,optimize=True)
print("BANNER_OK",OUT,im.size,OUT.stat().st_size)
