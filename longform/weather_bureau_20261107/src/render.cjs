'use strict';
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const A=require('./art.cjs'),{actor,head,hand,PEOPLE,actorBack}=require('./actors.cjs');
const {createCanvas,W,H,P,INK,ease,clamp,line,rect,oval,text,cloud,gauge,paper,weatherJar,umbrella,panel}=A;
const OUT='C:/M1lash/Работа/weather_bureau_20261107';fs.mkdirSync(OUT,{recursive:true});
const BG=new Map();function bg(type,v=0){const k=type+v;if(!BG.has(k))BG.set(k,A.background(type,v));return BG.get(k)}
function drizzle(c,t,count=80){c.save();c.strokeStyle='rgba(211,231,220,.40)';c.lineWidth=1.2;for(let i=0;i<count;i++){let x=(i*131+t*43)%1320-20,y=(i*73+t*310)%780-40;line(c,x,y,x-6,y+19,'rgba(211,231,220,.42)',1.2)}c.restore()}
function steam(c,t,x,y){for(let i=0;i<5;i++){let phase=(t*.35+i*.2)%1;c.globalAlpha=(1-phase)*.13;oval(c,x+Math.sin(t+i)*14,y-phase*100,12+phase*35,12+phase*25,'#d6e3d4',null)}c.globalAlpha=1}
function gripWrist(side,knob){let v=[...knob];for(let i=0;i<5;i++){const sx=side*58,sy=-350,dx=v[0]-sx,dy=v[1]-sy,d=Math.min(204,Math.hypot(dx,dy)),theta=Math.atan2(dy,dx),ea=theta-side*Math.acos(clamp(d/210,-1,1)),ex=sx+Math.cos(ea)*105,ey=sy+Math.sin(ea)*105,dd=Math.hypot(v[0]-ex,v[1]-ey);v=[knob[0]-(v[0]-ex)/dd*14.28,knob[1]-(v[1]-ey)/dd*14.28]}return v}
function leverState(t,dur){const p=clamp(t/dur),reach=ease((p-.14)/.16),pull=ease((p-.36)/.34),theta=-1.9+pull*.8,knob=[990+Math.cos(theta)*105,550+Math.sin(theta)*105],x=880+60*ease(p/.18),y=680;
 const local=[knob[0]-x,knob[1]-y],L=gripWrist(-1,[local[0]-6,local[1]]),R=gripWrist(1,[local[0]+6,local[1]]);return {p,reach,pull,theta,knob,x,y,L,R}}
function drawLever(c,S){panel(c,955,550,95,115,'#6c7d70');line(c,990,550,S.knob[0],S.knob[1],INK,17);line(c,990,550,S.knob[0],S.knob[1],P.gold,11);oval(c,S.knob[0],S.knob[1],15,15,P.rust,INK,3);oval(c,990,550,20,20,'#8a9b87',INK,3);oval(c,990,550,6,6,INK);for(let i=0;i<8;i++)line(c,1030+i*11,615,1030+i*11,630,INK,2);text(c,'ПОДАЧА',1001,653,15,INK,'Arial','center')}
function pilot(c,t,dur=15,hold=false){const S=leverState(hold?dur*.88:t,dur);c.drawImage(bg('pump'),0,0,W,H);gauge(c,620,205,1.35,.83-S.pull*.37,'ДАВЛЕНИЕ');
 oval(c,800,190,20,20,S.pull>.8?'#9ebd7a':((t*2)%1<.5?'#c5724a':'#8c493b'));rect(c,880,575,330,30,'#52777b',INK,3);rect(c,887,581,317*S.pull,16,'#9cc3c3',null);for(let i=0;i<8;i++){let xx=892+(t*110+i*44)%304;line(c,xx,584,xx+12,592,'#cee0d1',1.5)}
 actor(c,'nora',400,670,.95,S.pull>.65?'point':'read',S.pull>.85?'relieved':'focused',t,{look:1});
 drawLever(c,S);
 let pose=S.p<.18?'walk':'lever';let L=S.L.map((v,i)=>[-74,-168][i]+(v-[-74,-168][i])*S.reach),R=S.R.map((v,i)=>[74,-168][i]+(v-[74,-168][i])*S.reach);
 actor(c,'hero',S.x,S.y,1,pose,S.p<.7?'focused':'relieved',t,{left:L,right:R,walkFactor:1-ease((S.p-.10)/.08),look:S.p>.82?-1:1});
 steam(c,t,1150,530);text(c,'',0,0);
 return S;
}
function propInsert(c,type,t,theme='desk'){
 c.drawImage(bg(theme),0,0,W,H);rect(c,0,0,W,H,'rgba(34,51,54,.36)',null);pathTable(c);
 if(type==='jar'){weatherJar(c,650,335,2.05,t%4<1);hand(c,458,481,-.45,'grip',PEOPLE.hero.skin,1.6)}
 else if(type==='gauge'){gauge(c,680,340,3,.25+.2*ease((t%6)/6),'ФАКТИЧЕСКИ');hand(c,460,480,.9,'point',PEOPLE.nora.skin,1.4)}
 else if(type==='umbrella'){umbrella(c,660,330,2,.08*Math.sin(t));}
 else if(type==='map'){panel(c,330,150,650,410,'#b5c3aa');for(let i=0;i<7;i++)line(c,380+i*75,185,370+i*75,520,'#657b71',10);for(let i=0;i<5;i++)line(c,360,215+i*64,940,205+i*64,'#657b71',10);cloud(c,545,300,.9);for(let i=0;i<3;i++)pathDrop(c,510+i*35,365);hand(c,900,500,-.9,'point',PEOPLE.hero.skin,1.5)}
 else {paper(c,640,340,2.55,type==='stamp'?'ПОГОДА':type==='wire'?'НЕТ ДАННЫХ':'ЗАЯВЛЕНИЕ',type==='stamp');hand(c,457,470,.05,'grip',PEOPLE.hero.skin,1.5);if(type==='stamp'){const yy=210+ease((t%3)/1.8)*130;rect(c,780,yy,55,90,'#936847');oval(c,808,yy-14,35,25,P.rust);rect(c,755,yy+88,105,20,'#665246');hand(c,816,yy-3,Math.PI,'grip',PEOPLE.hero.skin,1.7)}else hand(c,890,480,-.5,'point',PEOPLE.nora.skin,1.5)}
}
function pathTable(c){A.path(c,'M160 100 L1100 100 L1270 690 L10 690 Z','#ad875a');for(let i=0;i<20;i++)line(c,200+i*43,120,50+i*58,670,'rgba(77,56,40,.2)',1)}
function pathDrop(c,x,y){A.path(c,`M${x} ${y} q-18 25 0 33 q18-8 0-33`,P.water)}
function hook(c,t){c.drawImage(bg('desk'),0,0,W,H);rect(c,0,0,W,H,'rgba(30,49,53,.16)',null);actor(c,'hero',1040,1210,2.1,'read','worried',t,{look:-1});c.save();c.translate(585,390+5*Math.sin(t));c.rotate(-.10);paper(c,0,0,2.75,'РАБОЧИЙ ДОГОВОР');rect(c,-145,5,290,70,P.cream,null);text(c,'ДОЖДЯ НЕТ',0,30,28,INK,'Georgia','center');text(c,'* в помещении',0,60,15,INK,'Arial','center');c.restore();drizzle(c,t,35)}
function shot(c,scene,t=0,dur=6){const loc=scene.location||'desk',mode=scene.mode||'wide',pose=scene.action||'read',emotion=scene.emotion||'neutral';c.save();
 const z=1.01+.018*ease(t/Math.max(.1,dur));c.translate(640,360);c.scale(z,z);c.translate(-640-5*ease(t/dur),-360);c.drawImage(bg(loc,scene.variant||0),0,0,W,H);if(scene.rainOnGlass){c.save();c.beginPath();c.rect(0,50,W,460);c.clip();drizzle(c,t,55);c.restore()}
 if(mode==='hook'){hook(c,t)}
 else if(mode==='insert'){require('./props.cjs').narrativeInsert(c,scene.prop||'paper',t,scene.propVariant??scene.variant??0)}
 else if(mode==='environment'){actor(c,scene.person||'hero',760+70*ease(t/dur),679,.65,'walk',emotion,t,{look:-1});if(loc==='vault')gauge(c,1060,200,1.2,.4,'РЕЗЕРВ')}
 else if(mode==='reverse'){actor(c,scene.other||'nora',505,1050,1.85,scene.otherAction||'explain',scene.otherEmotion||(scene.other==='child'?'smile':'focused'),t,{look:1});actorBack(c,'hero',1120,1200,2.1)}
 else if(mode==='reaction'){actor(c,scene.person||'hero',700,1415,2.55,pose,emotion,t,{look:scene.look||0,angle:scene.angle||'three'});}
 else if(mode==='medium'){actor(c,scene.person||'hero',710,1000,1.65,pose,emotion,t,{phase:t/dur,look:-.7});actor(c,scene.other||'nora',210,835,scene.other==='guest'?.90:scene.other==='child'?.75:1.15,scene.otherAction||'explain',scene.otherEmotion||'neutral',t,{phase:t/dur,look:1,angle:scene.otherAngle||'three'});}
 else {const family=loc==='roof'&&scene.other==='child';
  if(!family)actor(c,scene.other||'nora',325,675,scene.other==='guest'?.76:scene.other==='child'?.62:.94,scene.otherAction||'read',scene.otherEmotion||(scene.other==='child'?'smile':'focused'),t,{phase:t/dur,look:1});
  actor(c,scene.person||'hero',pose==='walk'?760+120*ease(t/dur):820,684,1,pose,emotion,t,{phase:t/dur,look:-.5,umbrellaWide:family});
  if(family)actor(c,'child',700,690,.62,scene.otherAction||'telescope','smile',t,{look:1});
  if((loc==='street'||loc==='bureau_front')&&scene.other!=='woman')actor(c,'woman',1130,660,.72,'walk','worried',t,{look:-1})}

 if(['street','bureau_front','canal','roof','city'].includes(loc))drizzle(c,t,scene.rainCount??55);if(['pump','vault','laundry'].includes(loc))steam(c,t,1150,570);
 c.restore();
 if(scene.chapterTitle&&t<1.8){c.globalAlpha=clamp((1.8-t)/.3);rect(c,45,42,Math.min(1100,scene.chapterTitle.length*16+55),55,'#2b4148',P.paper,1.5);text(c,scene.chapterTitle,66,79,29,P.cream,'Georgia');c.globalAlpha=1}
}
function makeCanvas(scale=1.5){const cv=createCanvas(Math.round(W*scale),Math.round(H*scale));const c=cv.getContext('2d');c.scale(scale,scale);return {cv,c}}
async function stills(){const samples=[['street','wide','walk','worried','Первый рабочий день'],['desk','medium','stamp','focused','Мокрое заявление'],['vault','wide','carry','surprise','Хранилище осадков'],['orangery','medium','explain','worried','Сухой вечер'],['pump','pilot','lever','focused','Подача воды'],['roof','wide','explain','relieved','Завтра']];
 for(let i=0;i<samples.length;i++){const [location,mode,action,emotion,title]=samples[i],{cv,c}=makeCanvas();if(mode==='pilot')pilot(c,9,15);else shot(c,{location,mode,action,emotion,other:location==='orangery'?'client':location==='roof'?'child':'nora',otherAction:location==='roof'?'telescope':'read',variant:location==='roof'?2:0},2.5,6);fs.writeFileSync(path.join(OUT,`still_${i+1}.png`),await cv.encode('png'));console.log('STILL',i+1,title)}
 const {cv,c}=makeCanvas();rect(c,0,0,W,H,P.cream,null);const em=['neutral','focused','worried','smile','angry','surprise'];for(let i=0;i<6;i++){c.save();c.translate(190+(i%3)*430,180+Math.floor(i/3)*330);c.scale(1.9,1.9);head(c,'hero',em[i],i===2?'profile':i===0?'front':'three',0,1);c.restore();text(c,em[i],190+(i%3)*430,315+Math.floor(i/3)*330,22,INK,'Arial','center')}fs.writeFileSync(path.join(OUT,'hero_model.png'),await cv.encode('png'));
}
async function renderPilot(seconds=15){const {cv,c}=makeCanvas();const dest=path.join(OUT,'motion_pilot_silent.mp4');const log=fs.openSync(path.join(OUT,'pilot_encode.log'),'w');const ff=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size',`${cv.width}x${cv.height}`,'-framerate','30','-i','pipe:0','-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','h264_nvenc','-preset','p4','-cq','18','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',dest],{stdio:['pipe','ignore',log]});let audit=[];
 for(let i=0;i<Math.round(seconds*30);i++){c.save();const S=pilot(c,i/30,seconds);c.restore();if(i%15===0)audit.push({time:i/30,phase:S.p,pull:S.pull,knob:S.knob,root:[S.x,S.y],left_wrist:S.L,right_wrist:S.R});if(!ff.stdin.write(cv.data()))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));fs.closeSync(log);if(code)throw Error('Pilot encode failed '+code);fs.writeFileSync(path.join(OUT,'pilot_geometry.json'),JSON.stringify(audit,null,2));console.log('PILOT_RENDERED',dest,seconds)
}
if(require.main===module){const op=process.argv[2]||'stills';(op==='pilot'?renderPilot(Number(process.argv[3]||15)):stills()).catch(e=>{console.error(e);process.exit(1)})}
module.exports={OUT,BG,shot,pilot,makeCanvas,renderPilot,stills,drizzle,gripWrist,leverState};
