'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const {shot,pilot,makeCanvas,OUT}=require('./render.cjs');
const A=require('./art.cjs');
const HERE=path.dirname(__dirname);
function draw(c,sc,t,duration){if(sc.mode==='pilot')pilot(c,t,duration);else shot(c,sc,t,duration)}
async function render(op='animatic'){
 const tl=JSON.parse(fs.readFileSync(path.join(HERE,'timeline.json'),'utf8'));
 const draft=op==='animatic',fps=draft?2:30,scale=draft?.75:1.5;
 const {cv,c}=makeCanvas(scale),dest=path.join(OUT,draft?'animatic_silent.mp4':'film_silent.mp4');
 const log=fs.openSync(path.join(OUT,op+'_encode.log'),'w');
 const ff=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size',`${cv.width}x${cv.height}`,'-framerate',String(fps),'-i','pipe:0','-an','-vf',`scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p${draft?',fps=30':''}`,'-c:v','h264_nvenc','-preset','p4','-cq',draft?'24':'18','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',dest],{stdio:['pipe','ignore',log]});
 let failure=null;ff.on('error',e=>failure=e);ff.stdin.on('error',e=>failure=e);
 const frames=Math.ceil(tl.duration_s*fps);let si=0;
 for(let n=0;n<frames;n++){
  if(failure)throw failure;
  const tm=n/fps;while(si<tl.scenes.length-1&&tm>=tl.scenes[si].end)si++;
  const sc=tl.scenes[si];c.save();draw(c,sc,tm-sc.start,sc.end-sc.start);c.restore();
  if(n%(fps*30)===0)console.log('RENDER',op,Math.round(tm),'/',Math.round(tl.duration_s),'shot',sc.id);
  if(!ff.stdin.write(cv.data()))await require('node:events').once(ff.stdin,'drain');
 }
 ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));fs.closeSync(log);if(code)throw Error('encode '+code);console.log('FILM_RENDERED',dest);
}
async function storyboard(){
 const bp=JSON.parse(fs.readFileSync(path.join(HERE,'blueprint.json'),'utf8')).chapters;
 fs.mkdirSync(path.join(OUT,'storyboard'),{recursive:true});
 const modes=['wide','insert','medium','reaction'];
 for(let ci=0;ci<bp.length;ci++)for(let pi=0;pi<bp[ci].rows.length;pi++){
  const [location,other,prop,action,emotion]=bp[ci].rows[pi].split('/');
  for(let mi=0;mi<modes.length;mi++){
   const sc={location,other,prop,action,emotion,mode:modes[mi],variant:ci>=6?1:0,otherAction:other==='nora'?'inspect':other==='woman'&&prop==='flowers'?'box':'read'};
   if(prop==='umbrella')sc.prop='board';if(prop==='gauge')sc.prop='gauge';
   const {cv,c}=makeCanvas(.75);if(ci===6&&pi===6)pilot(c,7,12);else shot(c,sc,2,6);
   const name=`c${ci+1}_p${String(pi+1).padStart(2,'0')}_${modes[mi]}.png`;
   fs.writeFileSync(path.join(OUT,'storyboard',name),await cv.encode('png'));
  }
 }
 console.log('STORYBOARD_RENDERED');
}
const op=process.argv[2]||'animatic';(op==='storyboard'?storyboard():render(op)).catch(e=>{console.error(e);process.exit(1)});
