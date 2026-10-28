#!/usr/bin/env python3
"""Generate original visual contact sheet for an actual design review before rendering."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from render_visuals import drawframe
OUT=Path("film54-output");OUT.mkdir(exist_ok=True)
tags=["plant","map","ship","engine","neurons","archival","timeline","lungs","chart","molecular"]
sheet=Image.new("RGB",(960*2,540*5),(13,22,31))
for idx,tag in enumerate(tags):
    im=drawframe(23+idx,1500,idx%7+1,
       ["До Колумба","По обе стороны океана","Атлантический мир",
        "Механизация","Никотиновая зависимость","Доклад 1964",
        "Историческая линия","Воздействие дыма","Данные ВОЗ",
        "Как работает вещество"][idx],tag,0)
    im.save(OUT/("preview-"+tag+".png"))
    sheet.paste(im,((idx%2)*960,(idx//2)*540))
sheet.resize((960,1350)).save(OUT/"M1lash_Tobacco_54_Storyboard.png")
print("10 unique procedural visual styles rendered; contact sheet is not an MP4.")
