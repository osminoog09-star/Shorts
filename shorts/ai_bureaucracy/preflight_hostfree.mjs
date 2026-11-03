import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const {openFilm}=await import(pathToFileURL(join(root,'skills/ext/huashu-motion/cli/lib/capture.js')).href);
const film=join(root,'shorts/ai_bureaucracy/film/index.html');
const html=readFileSync(film,'utf8').replace('<head>','<head><style>#host{display:none!important}#caps,#caps.side{left:100px!important;right:160px!important;text-align:center!important;font-size:70px!important}</style>').replace('side = !!win','side = false').replace('hostUpdate(t); outroUpdate(t);','/* host-free body, official outro assembled separately */');
const out=process.env.M1LASH_FRAMES_OUTPUT||join(root,'motion-output/ai_bureaucracy_v2');mkdirSync(out,{recursive:true});
const f=await openFilm(film,{html,shotFormat:'jpeg',chrome:process.env.OM_CHROME,chromeArgs:['--disable-dev-shm-usage']});
try{
 if(process.argv.includes('--render')||process.argv.includes('--patches')){
  const frames=join(out,'frames');mkdirSync(frames,{recursive:true});
  const ids=process.argv.includes('--patches')?[...Array(141).keys(),...Array.from({length:150},(_,i)=>1275+i)]:[...Array(1531).keys()];
  writeFileSync(join(out,'source_frame_ids.json'),JSON.stringify(ids));
  for(const [k,i] of ids.entries()){await f.seek(i/30);writeFileSync(join(frames,String(k).padStart(5,'0')+'.jpg'),await f.shot({format:'jpeg',quality:92}));if(k%50===0)console.log('RENDER_FRAME',k,'of',ids.length,'source',i);}
 }else{for(const t of [1,12,25,47]){await f.seek(t);writeFileSync(join(out,'still_'+t+'.jpg'),await f.shot({format:'jpeg',quality:92}));console.log('PREFLIGHT_FRAME',t);}}
}finally{await f.close();}
