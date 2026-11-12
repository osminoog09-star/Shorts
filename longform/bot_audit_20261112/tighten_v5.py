"""Remove three complete, redundant beats on frame-aligned pauses."""
from pathlib import Path
import argparse, json, subprocess

CUTS = ((7004, 7209), (20877, 21257), (35528, 35709))
REMOVED = {"c02_p03_u02", "c05_p02_u01", "c08_p02_u02"}
FPS = 30
SAMPLES_PER_FRAME = 1600

def remap(seconds):
    return seconds - sum(max(0, min(seconds, b/FPS)-a/FPS) for a,b in CUTS)

def cut_body(source, output):
    kept = list(zip([0, *(b for _,b in CUTS)], [*(a for a,_ in CUTS), None]))
    filters = []
    for i,(a,b) in enumerate(kept):
        v = f"trim=start_frame={a}"
        sound = f"atrim=start_sample={a*SAMPLES_PER_FRAME}"
        if b is not None:
            v += f":end_frame={b}"
            sound += f":end_sample={b*SAMPLES_PER_FRAME}"
        filters.extend([f"[0:v]{v},setpts=PTS-STARTPTS[v{i}]",
                        f"[0:a]{sound},asetpts=PTS-STARTPTS[a{i}]"])
    filters.append("".join(f"[v{i}][a{i}]" for i in range(len(kept)))+
                   f"concat=n={len(kept)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg","-v","error","-xerror","-y","-i",str(source),
                    "-filter_complex",";".join(filters),"-map","[v]","-map","[a]",
                    "-c:v","h264_nvenc","-preset","p5","-cq","16","-pix_fmt","yuv420p",
                    "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
                    "-c:a","pcm_s24le",str(output)],check=True)

def cut_timeline(source, output):
    t=json.loads(source.read_text("utf-8"))
    t["duration_s"]=remap(t["duration_s"])
    for scene in t["scenes"]:
        scene["start"]=remap(scene["start"])
        scene["end"]=remap(scene["end"])
    t["scenes"]=[s for s in t["scenes"] if s["end"]-s["start"]>=.5/FPS]
    for c in t["chapters"]:
        c["start"]=remap(c["start"])
    output.write_text(json.dumps(t,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("work",type=Path)
    args=p.parse_args()
    cut_timeline(args.work/"timeline.json",args.work/"timeline_final.json")
    cut_body(args.work/"body.mp4",args.work/"body_cut.mkv")
    print("Removed",sum(b-a for a,b in CUTS)/FPS,"seconds at 3 pauses")

if __name__=="__main__":
    main()
