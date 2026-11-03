#!/usr/bin/env python3
"""Индекс проверенных производственных уроков; не оценщик качества видео."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(data):
    if data.get('schema_version')!=1: raise ValueError('schema_version must be 1')
    ids=set()
    for row in data['entries']:
        for k in ['id','project','issue','cause','fix','status','evidence','acceptance','owner_review','audience_effect','regression']:
            if k not in row: raise ValueError('Missing '+k)
        if row['id'] in ids: raise ValueError('Duplicate '+row['id'])
        ids.add(row['id'])
        if row['status'] not in ['observed','fixed','verified','hypothesis','pending']: raise ValueError('Bad status')
        if row['owner_review'] not in ['pending','accepted','rejected']: raise ValueError('Bad review')
        if row['audience_effect'] not in ['unknown','positive','negative','inconclusive']: raise ValueError('Bad audience effect')
        path=(ROOT/row['evidence']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file(): raise ValueError('Missing/local evidence '+row['id'])
        if row['status']=='verified' and not row['acceptance'].strip(): raise ValueError('No acceptance test')
    return len(ids)
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','preflight']);a=p.parse_args()
    d=json.loads((ROOT/'reports/learning/journal.json').read_text());n=validate(d)
    print(f'Journal structure/evidence links: {n} entries valid. This does not verify media quality.')
    if a.action=='preflight':
        print('Also read AGENTS.md, skills/m1lash-studio/SKILL.md and reports/learnings.md.')
        for x in d['entries']:print(f"{x['id']} [{x['status']}, owner={x['owner_review']}]: {x['issue']} -> {x['fix']}; test: {x['acceptance']}")
if __name__=='__main__':main()
