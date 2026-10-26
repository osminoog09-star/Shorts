import subprocess,json,sys,os,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
B=Path(__file__).resolve().parent;R=B.parents[1];j=json.load(open(B/'script.json'))
env=os.environ.copy();env['NODE_PATH']='/workspace/scratch/45719f0e4ec5/renderdeps/node_modules';env['NODE_ENV']='production'
def one(s,short=False):
 sid=s['id'];subprocess.run([sys.executable,str(B/'prepare.py'),sid],cwd=R,check=True,env=env)
 subprocess.run(['node',str(B/'render.cjs'),sid]+(['--short'] if short else []),cwd=R,check=True,env=env)
 return sid
if __name__=='__main__':
 chosen=sys.argv[1:];rows=[(s,False) for s in j['scenes']]+[(s,True) for s in j['short']]
 if chosen:rows=[r for r in rows if r[0]['id'] in chosen]
 results=[]
 with ThreadPoolExecutor(max_workers=3) as pool:
  futures={pool.submit(one,s,sh):s['id'] for s,sh in rows}
  for f in as_completed(futures):
   try:results.append({'id':f.result(),'ok':True})
   except Exception as ex:results.append({'id':futures[f],'ok':False,'error':str(ex)})
 (B/'PRODUCE_STATUS.json').write_text(json.dumps(results,indent=2));assert all(r['ok'] for r in results),results
