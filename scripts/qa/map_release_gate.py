#!/usr/bin/env python3
"""Pre-render release gate for a narrated country map. No mutation.
Example: pip install countryinfo
python scripts/qa/map_release_gate.py --facts /project/facts_v3.csv --route /project/route_159.json --renderer /project/render_v3.py --output /project/map_qa.json
A 0 exit only passes preflight; human full playback remains mandatory.
"""
import argparse,collections,csv,json,re
from pathlib import Path
from urllib.parse import urlparse


def geometry(codes):
    try:
        from countryinfo import CountryInfo
    except ImportError as e:
        raise RuntimeError("pip install countryinfo (or provide a tested geometry provider)") from e
    records=CountryInfo().all()
    lookup={v.get("ISO",{}).get("alpha2"):v for v in records.values() if v.get("ISO",{}).get("alpha2")}
    for code,key in (("GB","united kingdom"),("ME","montenegro"),("MM","myanmar")):
        if code not in lookup and key in records:lookup[code]=records[key]
    missing=[]
    for code in codes:
        features=lookup.get(code,{}).get("geoJSON",{}).get("features",[])
        ok=any(f.get("geometry",{}).get("type") in ("Polygon","MultiPolygon") and f.get("geometry",{}).get("coordinates") for f in features)
        if not ok:missing.append(code)
    return missing


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--facts",required=True)
    p.add_argument("--route",required=True)
    p.add_argument("--renderer",required=True)
    p.add_argument("--cues",help="CSV with iso2,cue_time,cue_word for EVERY country")
    p.add_argument("--output")
    a=p.parse_args()
    facts=list(csv.DictReader(Path(a.facts).open(encoding="utf-8-sig")))
    itinerary=json.loads(Path(a.route).read_text(encoding="utf-8"))
    route=[v["iso2"] if isinstance(v,dict) else v for v in itinerary]
    codes=[x["iso2"] for x in facts]
    script=Path(a.renderer).read_text(encoding="utf-8")
    errors=[];warnings=[]
    def fail(tag,reason):errors.append({"tag":tag,"detail":reason})
    def warn(tag,reason):warnings.append({"tag":tag,"detail":reason})
    if len(set(route))!=len(route):fail("DUPLICATE_ROUTE","Country counted twice")
    if len(set(codes))!=len(codes):fail("DUPLICATE_FACTS","Duplicate ISO2 in facts")
    if set(route)!=set(codes):fail("ROUTE_FACT_MISMATCH",{"missing":sorted(set(route)-set(codes)),"extra":sorted(set(codes)-set(route))})
    if len(route)<100:fail("UNDER_100",len(route))
    regions=collections.Counter(x.get("region","") for x in facts)
    for region,n in regions.items():
        if n<10:fail("REGION_UNDER_10",{"region":region,"count":n})
    try:
        missing=geometry(codes)
        if missing:fail("MISSING_POLYGON",missing)
    except Exception as e:
        fail("UNVERIFIED_GEOMETRY",str(e))
        missing=[]
    # An inset may be supplied only by an explicit separate geo review;
    # never infer presence from centroid/pin alone.
    verified=[x for x in facts if x.get("map_binary")=="official_retail_confirmed"]
    weak=[]
    for f in verified:
        u=f.get("source_url","")
        if not u or not (urlparse(u).hostname or "").endswith("samsung.com"):
            weak.append(f["iso2"])
    if weak:fail("WEAK_RETAIL_SOURCE",weak)
    if re.search(r"cdur\s*\*\s*k\s*/\s*len\(xs\)",script):
        fail("EQUAL_DURATION_COUNTRY_TIMING","Map stop times must follow spoken country word cues")
    if re.search(r"range\(0,\s*len\(entries\),\s*7\)",script):
        fail("FIXED_SEVEN_WORD_SUBTITLES","Split by sentence/voice timing, not token count")
    if "alpha_over(frame,sprite,sx+ox,sy+oy)" in script:
        fail("UNLINKED_OFFSET_FLAG","Countryball may be 100+ px away from its geographic anchor")
    if "cv2.line(frame,(px,py),m" in script:
        warn("PERSISTENT_PREVIOUS_ROUTE","Old-country path can look like incorrect target pointer")
    if re.search(r"(?m)^W\s*,\s*H\s*=\s*960\s*,\s*540",script):
        warn("LOW_INTERNAL_RESOLUTION","Output 1920x1080 scaled from only 960x540")
    if not a.cues:
        fail("MISSING_COUNTRY_CUE_SHEET","No verified per-country word timing")
    else:
        cues=list(csv.DictReader(Path(a.cues).open(encoding="utf-8-sig")))
        if len(cues)!=len(route) or set(x.get("iso2") for x in cues)!=set(route):
            fail("INCOMPLETE_CUES","Every first-pass ISO needs exact spoken cue")
        for x in cues:
            try:float(x["cue_time"])
            except (KeyError,ValueError):fail("BAD_CUE_TIME",x)
            if not x.get("cue_word"):fail("MISSING_CUE_WORD",x)
    report={"status":"BLOCKED" if errors else "PREFLIGHT_PASS_NEEDS_MANUAL_QA",
            "route_count":len(route),"unique":len(set(route)),"regions":dict(regions),
            "retail_confirmed":len(verified),"missing_geometry":missing,
            "errors":errors,"warnings":warnings,
            "manual_gates":["Country+flag correct at each entry and camera zoom","No overlap with story panels","Subtitles and country names synced to audible speech","All export frames and full audio watched/heard","Dates and country-specific direct sales sources checked"]}
    if a.output:Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 2 if errors else 0


if __name__=="__main__":raise SystemExit(main())
