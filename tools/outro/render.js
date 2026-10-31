const {chromium}=require('playwright');const fs=require('fs');(async()=>{
const [w,h,dur,dir]=[+process.argv[2],+process.argv[3],+process.argv[4],process.argv[5]];fs.mkdirSync(dir,{recursive:true});
const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl']});const p=await b.newPage({viewport:{width:w,height:h}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:8790/outro.html?w=${w}&h=${h}`);await p.evaluate(()=>window.ready);
const n=Math.round(dur*30);for(let i=0;i<n;i++){const d=await p.evaluate(t=>frame(t),i/30);fs.writeFileSync(`${dir}/f${String(i).padStart(4,'0')}.png`,Buffer.from(d.split(',')[1],'base64'));}
console.log('frames',n,errs.join('|')||'ok');await b.close()})();
