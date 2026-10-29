import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent.parent;(R/'lipsync').mkdir(exist_ok=True)
for ident in json.loads((R/'out/host_targets.json').read_text()):
 out=R/'lipsync'/(ident+'.json')
 if not out.exists():subprocess.run(['bash',str(R.parents[1]/'tools/lipsync.sh'),str(R/'audio_verified'/(ident+'.mp3')),str(out)],check=True)
 print('LIPSYNC',ident,flush=True)
