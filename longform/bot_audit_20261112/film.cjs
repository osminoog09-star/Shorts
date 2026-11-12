const {shot,makeCanvas,type,background}=require('./art.cjs');
const fs=require('node:fs'), path=require('node:path'), {spawn}=require('node:child_process'), {once}=require('node:events');
const HERE=__dirname, OUT=process.env.BOT_AUDIT_WORK || 'C:/M1lash/Работа/bot_audit_20261112';
const staging=JSON.parse(fs.readFileSync(path.join(HERE,'staging.json'),'utf8').replace(/^\uFEFF/,''));
const envelopePath=path.join(OUT,'voice_envelope.u8');
const envelope=fs.existsSync(envelopePath)?fs.readFileSync(envelopePath):null;
const mouthPath=path.join(OUT,'mouth_poses.u8');
const mouth=fs.existsSync(mouthPath)?fs.readFileSync(mouthPath):null;
const ease=x=>(x=Math.max(0,Math.min(1,x)),x*x*(3-2*x));
function rect(c,x,y,w,h,color,r=0){c.beginPath();c.roundRect(x,y,w,h,r);c.fillStyle=color;c.fill()}
function ellipse(c,x,y,w,h,color){c.beginPath();c.ellipse(x,y,w,h,0,0,Math.PI*2);c.fillStyle=color;c.fill()}
function poly(c,color,...p){c.beginPath();c.moveTo(...p[0]);for(const a of p.slice(1))c.lineTo(...a);c.closePath();c.fillStyle=color;c.fill()}
function unlock(c,s,t,d,scale){
 const pr=t/d, reach=ease((pr-.12)/.28), ok=pr>.42, open=ease((pr-.48)/.37);
 c.drawImage(background('entry',scale,true),0,0,1280,720);
 rect(c,0,0,1280,720,'#1728399a');
 rect(c,545,64,470,590,'#293d4d',8);
 rect(c,568,83,425,548,'#718a90',4);
 const edge=977-open*300;
 poly(c,'#526e80',[579,96],[edge,111+open*53],[edge,604-open*19],[579,618]);
 poly(c,'#9db6b4',[596,119],[edge-20,135+open*45],[edge-20,389-open*23],[596,388]);
 rect(c,edge-43,432,11,54,'#caaa77',3);
 rect(c,1008,287,106,156,'#273c4b',13);rect(c,1021,328,78,72,'#526977',8);
 ellipse(c,1060,310,10,10,ok?'#91f7ae':'#f88465');
 if(ok){c.globalAlpha=.30;ellipse(c,1060,310,19+Math.sin(t*11)*4,19,'#91f7ae');c.globalAlpha=1}
 const x=1167-reach*108+(ok?ease((pr-.64)/.3)*88:0), y=462-reach*115;
 poly(c,'#346951',[1280,499],[x+135,y+68],[x+36,y+13],[x+18,y+62],[x+104,y+112],[1280,657]);
 poly(c,'#4e7b62',[1280,513],[x+139,y+74],[x+41,y+20],[x+34,y+42],[1280,557]);
 ellipse(c,x+28,y+20,37,28,'#deae92');rect(c,x-9,y-4,44,50,'#345667',13);
 ellipse(c,x+10,y+20,6,7,'#a2b7ad');rect(c,x+21,y-2,42,12,'#e5b59b',5);
 if(open>.2){poly(c,'#d4d2ac22',[edge,181],[994,90],[994,631],[edge,591])}
}
function draw(c,s,t,d,scale){
 if(s.mode==='pilot')unlock(c,s,t,d,scale);
 else shot(c,s,t,d,scale);
}
function frame(cv,c,s,t,d,scale){c.save();c.scale(scale,scale);draw(c,s,t,d,scale);c.restore()}
async function encode(op,shots,start,end,fps,scale,out){
 const {cv,c}=makeCanvas(scale);
 const log=fs.openSync(path.join(OUT,op+'_encode.log'),'w');
 const ff=spawn('ffmpeg',['-v','error','-y','-filter_threads','2','-f','rawvideo','-pixel_format','rgba','-video_size',cv.width+'x'+cv.height,'-framerate',String(fps),'-i','pipe:0','-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'+(fps===2?',fps=30':''),'-c:v','h264_nvenc','-preset','p4','-cq',fps===2?'24':'18','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',out],{stdio:['pipe','ignore',log]});
 let error;ff.on('error',e=>error=e);ff.stdin.on('error',e=>error=e);
 const closed=once(ff,'close');let i=0;
 for(let n=start;n<end;n++){
  if(error)throw error;
  const t=n/fps;while(i+1<shots.length&&t>=shots[i].end)i++;
  const s=shots[i];
  s.voiceOpen=(envelope?.[Math.round(t*30)]||0)/255;
  s.mouthPose=mouth?.[Math.round(t*30)]??255;
  frame(cv,c,s,Math.max(0,t-s.start),s.end-s.start,scale);
  if(n%(fps*30)===0)console.log(op,n/fps,'shot',s.id);
  if(!ff.stdin.write(cv.data())) await once(ff.stdin,'drain');
 }
 ff.stdin.end();const [code]=await closed;fs.closeSync(log);
 if(code!==0)throw Error('FFmpeg exit '+code);
 console.log('RENDERED',op,out);
}
function sample(ch,p,mode){
 const [location,other,prop,action]=staging.chapters[ch-1][p-1].split('/');
 return {id:'sample',location,other,prop,action,mode,serial:ch*4+p,start:0,end:10};
}
async function main(){
 fs.mkdirSync(OUT,{recursive:true});
 const op=process.argv[2]||'stills';
 if(op==='stills'){
  const selections=[[1,1,'insert'],[1,2,'medium'],[3,3,'wide'],[5,3,'insert'],[6,4,'reaction'],[6,6,'pilot']];
  for(let i=0;i<selections.length;i++){
   const scale=1.5,{cv,c}=makeCanvas(scale),s=sample(...selections[i]);
   frame(cv,c,s,i===5?5.4:2.8,10,scale);
   fs.writeFileSync(path.join(OUT,'still_'+(i+1)+'.jpg'),await cv.encode('jpeg',88));
  }
 }else if(op==='pilot'){
  const s=sample(6,6,'pilot');await encode(op,[s],0,300,30,1.5,path.join(OUT,'motion_pilot.mp4'));
 }else if(op==='thumbnail'){
  const scale=1.5,{cv,c}=makeCanvas(scale);frame(cv,c,sample(1,2,'wide'),1.6,10,scale);
  c.save();c.scale(scale,scale);
  const g=c.createLinearGradient(0,0,870,0);g.addColorStop(0,'#10192af2');g.addColorStop(1,'#10192a00');c.fillStyle=g;c.fillRect(0,0,950,720);
  type(c,'ПРОВЕРКА',60,209,99,'#ffdc91','left');type(c,'НА ЧЕЛОВЕКА',60,308,76,'#f6f2e0','left');
  rect(c,64,362,297,53,'#ad694c',7);type(c,'ПРИТВОРИСЬ БОТОМ',213,396,24,'#f7e6ba');
  c.restore();fs.writeFileSync(path.join(OUT,'thumbnail.png'),await cv.encode('png'));
 }else{
  const tl=JSON.parse(fs.readFileSync(path.join(OUT,'timeline.json'),'utf8')), ch=op.startsWith('chapter-')?Number(op.split('-')[1]):null;
  const frames=Math.ceil(tl.duration_s*30);
  if(op==='review'){
   for(const [i,start,stop] of [[1,38,53],[2,223,240],[3,376,400],[4,850,872],[5,1017,1041],[6,1273,1297.44]]){
    await encode('review-'+i,tl.scenes,Math.round(start*30),Math.round(stop*30),30,1,path.join(OUT,'review_'+i+'.mp4'));
   }
  }else if(op==='opening'){
   await encode(op,tl.scenes,0,720,30,1.5,path.join(OUT,'opening_silent.mp4'));
  }else if(ch){
   const s=tl.scenes.filter(x=>x.chapter===ch);const start=Math.round(s[0].start*30),end=ch===8?frames:Math.round(s.at(-1).end*30);
   await encode(op,tl.scenes,start,end,30,1.5,path.join(OUT,'chapter_'+String(ch).padStart(2,'0')+'_silent.mp4'));
  }else{
   await encode(op,tl.scenes,0,Math.ceil(tl.duration_s*2),2,.75,path.join(OUT,'animatic_silent.mp4'));
  }
 }
}
main().catch(e=>{console.error(e);process.exitCode=1});
