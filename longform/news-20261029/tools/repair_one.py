import asyncio,json,sys
from pathlib import Path
from tts_local import synth,ROOT
line=next(x for x in json.loads((ROOT/'tts_job.json').read_text())['lines'] if x['id']==sys.argv[1]);d=ROOT/'audio';(d/(line['id']+'.json')).rename(d/(line['id']+'_rejected.json'));(d/(line['id']+'.mp3')).rename(d/(line['id']+'_rejected.mp3'));asyncio.run(synth(line))
