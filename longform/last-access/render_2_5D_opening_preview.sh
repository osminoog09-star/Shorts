#!/usr/bin/env bash
set -euo pipefail
# A reproducible illustrated motion-comic preview. No YouTube/Metricool publication.
cd "$(dirname "$0")"
mkdir -p _preview_render
cd _preview_render
curl -fsSL --retry 3 --connect-timeout 10 --max-time 90 'https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225616_beb822ca-f5fe-4391-aaa2-393f6f92c7ec.png' -o shot01.png
curl -fsSL --retry 3 --connect-timeout 10 --max-time 90 'https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_db8d015c-dd86-4f9a-bb22-42036d094d94.png' -o shot02.png
curl -fsSL --retry 3 --connect-timeout 10 --max-time 90 'https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_818926b1-09be-4b72-859d-8d6a91d3a703.png' -o shot03.png
curl -fsSL --retry 3 --connect-timeout 10 --max-time 90 'https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_acbaa80a-4ca7-43c4-99d1-28a2f6527155.png' -o shot04.png
curl -fsSL --retry 3 --connect-timeout 10 --max-time 120 'https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/1c018130-74ee-47d9-bcf3-65917c6371e3.mp4' -o original_draft_audio.mp4
cp ../preview_2_5D_opening.srt opening.srt
python3 - <<'PY'
from PIL import Image, ImageDraw
import random
im=Image.new('RGBA',(1310,750),(0,0,0,0));d=ImageDraw.Draw(im);r=random.Random(20261027)
for _ in range(220):
 x=r.randrange(1310);y=r.randrange(750);s=r.randrange(1,4)
 d.ellipse((x,y,x+s,y+s),fill=(134,205,232,r.randrange(12,65)))
for _ in range(9):
 x=r.randrange(1310);d.line((x,0,x+10,750),fill=(130,177,197,r.randrange(3,13)),width=1)
im.save('atmosphere.png')
PY
# One still illustration per source and two motivated camera configurations per source.
# Atmospheric dust runs as a separate independently drifting foreground plane.
F="[0:v]scale=1496:840,split=2[s01a][s01b];[1:v]scale=1496:840,split=2[s02a][s02b];[2:v]scale=1496:840,split=2[s03a][s03b];[3:v]scale=1496:840,split=2[s04a][s04b];"
F+="[s01a]zoompan=z='min(zoom+0.0003,1.16)':x='iw/2-iw/zoom/2+16*sin(on/35)':y='ih/2-ih/zoom/2+10*cos(on/49)':d=240:s=1280x720:fps=24,setsar=1,format=yuv420p[v0];"
F+="[s02a]zoompan=z='min(zoom+0.00038,1.15)':x='iw/2-iw/zoom/2-14*sin(on/36)':y='ih/2-ih/zoom/2+5*sin(on/36)':d=240:s=1280x720:fps=24,setsar=1,format=yuv420p[v1];"
F+="[s03a]zoompan=z='1.06+0.00022*on':x='iw/2-iw/zoom/2+24*sin(on/45)':y='ih/2-ih/zoom/2+8*cos(on/39)':d=192:s=1280x720:fps=24,setsar=1,format=yuv420p[v2];"
F+="[s01b]zoompan=z='1.13-0.00015*on':x='iw/2-iw/zoom/2+9*sin(on/25)':y='ih/2-ih/zoom/2+11*cos(on/25)':d=192:s=1280x720:fps=24,setsar=1,format=yuv420p[v3];"
F+="[s03b]zoompan=z='1.08+0.0002*on':x='iw/2-iw/zoom/2+7*sin(on/42)':y='ih/2-ih/zoom/2+11*cos(on/42)':d=192:s=1280x720:fps=24,setsar=1,format=yuv420p[v4];"
F+="[s04a]zoompan=z='1.045+0.00022*on':x='iw/2-iw/zoom/2+12*sin(on/36)':y='ih/2-ih/zoom/2+11*cos(on/33)':d=192:s=1280x720:fps=24,setsar=1,format=yuv420p[v5];"
F+="[s04b]zoompan=z='1.13-0.0002*on':x='iw/2-iw/zoom/2+4*sin(on/31)':y='ih/2-ih/zoom/2+8*cos(on/52)':d=192:s=1280x720:fps=24,setsar=1,format=yuv420p[v6];"
F+="[s02b]zoompan=z='1.07+0.00025*on':x='iw/2-iw/zoom/2+7*sin(on/30)':y='ih/2-ih/zoom/2+14*cos(on/43)':d=240:s=1280x720:fps=24,setsar=1,format=yuv420p[v7];"
F+="[v0][v1][v2][v3][v4][v5][v6][v7]concat=n=8:v=1:a=0,format=yuv420p[base];"
F+="[4:v]scale=1310:750,format=rgba[foreground];[base][foreground]overlay=x='-18+13*sin(t/2)':y='-11+12*cos(t/3)':eval=frame:shortest=1,format=yuv420p,"
F+="subtitles=opening.srt:force_style='FontName=DejaVu Sans,FontSize=14,Outline=1,BorderStyle=3,PrimaryColour=&H00FFFFFF,BackColour=&H8A07121C,MarginV=32',"
F+="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='ПОСЛЕДНИЙ ДОПУСК':fontcolor=white:fontsize=24:x=34:y=25:box=1:boxcolor=0x061522@0.64:boxborderw=12,"
F+="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='ПРОБА 2.5D':fontcolor=0x9cd6df:fontsize=21:x=w-tw-35:y=28:box=1:boxcolor=0x061522@0.60:boxborderw=10,"
F+="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='311 В РЕЕСТРЕ  /  312 ЖИВЫХ':fontcolor=0x8eeedb:fontsize=29:x=w-tw-42:y=117:box=1:boxcolor=0x061522@0.80:boxborderw=12:enable='between(t,45,60)',"
F+="fade=t=out:st=69:d=1,format=yuv420p[out];[5:a]atrim=0:70,afade=t=out:st=69:d=1,asetpts=PTS-STARTPTS[aout]"
mkdir -p output
ffmpeg -hide_banner -y -loglevel warning \
 -i shot01.png -i shot02.png -i shot03.png -i shot04.png \
 -loop 1 -framerate 24 -t 70 -i atmosphere.png \
 -i original_draft_audio.mp4 \
 -filter_complex "$F" -map '[out]' -map '[aout]' \
 -metadata title='Последний допуск — 2.5D проба первых сцен' \
 -c:v libx264 -preset veryfast -crf 23 -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -r 24 \
 -c:a aac -b:a 160k -movflags +faststart -t 70 output/Last_Access_EP01_2_5D_OPENING_PREVIEW.mp4
ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height -of json output/Last_Access_EP01_2_5D_OPENING_PREVIEW.mp4 | tee output/probe.json
ffmpeg -hide_banner -v error -i output/Last_Access_EP01_2_5D_OPENING_PREVIEW.mp4 -f null -
for sec in 3 14 35 53 67; do
 ffmpeg -hide_banner -loglevel error -y -ss "$sec" -i output/Last_Access_EP01_2_5D_OPENING_PREVIEW.mp4 -frames:v 1 -q:v 4 "output/qa_$sec.jpg"
done
echo "PASS: four original 2.5D reference-conditioned illustrated frames, 70s cinematic pan/atmosphere test, existing Russian dialogue. Not published."
