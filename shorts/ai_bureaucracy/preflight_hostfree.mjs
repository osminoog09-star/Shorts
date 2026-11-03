import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const {openFilm}=await import(pathToFileURL(join(root,'skills/ext/huashu-motion/cli/lib/capture.js')).href);
const film=join(root,'shorts/ai_bureaucracy/film/index.html');
const html=readFileSync(film,'utf8').replace('<head>','<head><style>#host{display:none!important}</style>').replace('hostUpdate(t); outroUpdate(t);','/* host-free body, official outro assembled separately */');
const out=join(root,'motion-output/ai_bureaucracy_v2');mkdirSync(out,{recursive:true});
const f=await openFilm(film,{html,shotFormat:'jpeg',chrome:process.env.OM_CHROME,chromeArgs:['--disable-dev-shm-usage']});
try{for(const t of [1,12,25,47]){await f.seek(t);writeFileSync(join(out,'still_'+t+'.jpg'),await f.shot({format:'jpeg',quality:92}));console.log('PREFLIGHT_FRAME',t);}}finally{await f.close();}
