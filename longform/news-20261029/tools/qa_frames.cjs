process.env.NEWS_DATA_FILE='full_data.js';
const {sandbox,canvas,fs,root}=require('./native.cjs');
(async()=>{while(!sandbox.READY)await new Promise(r=>setTimeout(r,20));const P=sandbox.SHOT_PLAN;fs.mkdirSync('out/qa',{recursive:true});const {createCanvas}=require('@napi-rs/canvas');let contacts=[];
for(let page=0;page<Math.ceil(P.length/20);page++){if(process.env.ONLY_PAGE!==undefined&&page!==Number(process.env.ONLY_PAGE))continue;let c=createCanvas(1600,1200),g=c.getContext('2d');g.fillStyle='#e2e5dc';g.fillRect(0,0,1600,1200);for(let j=0;j<20&&page*20+j<P.length;j++){let q=P[page*20+j],t=q.start+Math.min(2,(q.end-q.start)/2);sandbox.renderAt(t);let x=j%4*400,y=Math.floor(j/4)*240;g.drawImage(canvas,x,y,400,225);g.fillStyle='#102235';g.font='12px sans-serif';g.fillText(q.id+' '+t.toFixed(2),x+5,y+237)}let path=`out/qa/contact_${page}.jpg`;fs.writeFileSync(path,c.toBuffer('image/jpeg',90));contacts.push(path)}
if(process.env.ONLY_PAGE!==undefined){console.log('updated',contacts);return}
// Every real transition: deterministic pixels, no history-dependent state.
let fail=[];for(const q of P.slice(1)){let t=q.start+.2;sandbox.renderAt(t);const a=canvas.toBuffer('image/png');sandbox.renderAt(t-2);sandbox.renderAt(t);const b=canvas.toBuffer('image/png');if(!a.equals(b))fail.push(q.id)}fs.writeFileSync('out/qa/DETERMINISM.json',JSON.stringify({transitions:P.length-1,failed:fail},null,2));console.log('contacts',contacts,'determinism failures',fail.length);
})();
