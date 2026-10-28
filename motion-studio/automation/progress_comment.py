#!/usr/bin/env python3
"""Safely expose actual stage manifest in a bot-authored issue comment for Pages dashboard."""
import argparse
import json
import os
from pathlib import Path

ALLOWED={"ready","needs_review","blocked"}

def make_comment(data,repo,run_id):
    number=data["issue_number"]
    if not str(number).isdigit() or not str(run_id).isdigit() or repo!="osminoog09-star/Shorts":
        raise ValueError("untrusted run locator")
    safe=[]
    for st in data.get("stages",[]):
        if st["status"] not in ALLOWED:
            raise ValueError("invalid stage status")
        safe.append({"id":str(st["id"])[:25],"status":st["status"],
                     "reason":str(st["reason"])[:250]})
    stage_data={"schema":1,"issue_number":number,"run_id":int(run_id),
                "status":str(data["status"])[:100],"stages":safe,
                "output_is_final_video":False,
                "artifact_name":"m1lash-studio-production-"+str(number)}
    counts={x:sum(s["status"]==x for s in safe) for x in ALLOWED}
    link=f"https://github.com/{repo}/actions/runs/{run_id}"
    header=(f"### M1lash Studio — реальный отчёт агентов\n\n"
            f"Готовы: {counts['ready']} · требуют просмотра: {counts['needs_review']} "
            f"· заблокированы: {counts['blocked']}.\n\n"
            f"[Артефакт и логи запуска]({link})\n\n"
            "Полноценный MP4 не создан; голос и публикация не подтверждены.\n\n")
    return header+"M1LASH_STAGE_STATUS_BEGIN\n"+json.dumps(stage_data,ensure_ascii=False,separators=(",",":"))+"\nM1LASH_STAGE_STATUS_END\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    body=make_comment(data,os.environ.get("GITHUB_REPOSITORY",""),
                      os.environ.get("GITHUB_RUN_ID",""))
    Path(args.out).write_text(body,encoding="utf-8")


if __name__=="__main__":
    main()
