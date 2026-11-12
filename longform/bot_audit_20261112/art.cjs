'use strict';
const {createCanvas,GlobalFonts}=require(process.env.M1LASH_CANVAS_MODULE || 'C:/M1lash/Работа/weather_bureau_runtime/node_modules/@napi-rs/canvas');
const W=1280,H=720;
const palette={
 coffee:['#36565c','#87a4a1','#bd824f'],office:['#415862','#93a6a0','#a37c51'],
 meeting:['#263c4c','#788889','#956752'],lobby:['#4f6868','#b9b7a2','#a78058'],
 street:['#879fb0','#bfccd0','#687b84'],court:['#607d8a','#a8b9b7','#82907c'],
 entry:['#42545c','#7f9391','#957e66'],shop:['#45505b','#899491','#98643d'],
 dark:['#171d30','#374c59','#51433b'],dusk:['#44496f','#8e83a1','#5b554d']
};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), ease=x=>(x=clamp(x),x*x*(3-2*x));
const rng=n=>((Math.sin(n*72.173+6.41)*43758.5453)%1+1)%1;
function poly(c,fill,pts,stroke){c.beginPath();c.moveTo(...pts[0]);for(const p of pts.slice(1))c.lineTo(...p);c.closePath();c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=2;c.stroke()}}
function line(c,stroke,width,...p){c.beginPath();c.moveTo(...p[0]);for(const x of p.slice(1))c.lineTo(...x);c.strokeStyle=stroke;c.lineWidth=width;c.lineJoin='round';c.lineCap='round';c.stroke()}
function rr(c,x,y,w,h,r,fill,stroke){c.beginPath();c.roundRect(x,y,w,h,r);c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=2;c.stroke()}}
function oval(c,x,y,w,h,fill){c.beginPath();c.ellipse(x,y,w,h,0,0,Math.PI*2);c.fillStyle=fill;c.fill()}
function gradient(c,x,y,a,b){const g=c.createLinearGradient(x,y,x,y+360);g.addColorStop(0,a);g.addColorStop(1,b);return g}
function type(c,s,x,y,n,color='#f5ddad',align='center'){c.font=`700 ${n}px Arial`;c.textAlign=align;c.fillStyle=color;c.fillText(s,x,y)}
function box(c,x,y,w,h,d,front,top,side){poly(c,top,[[x,y],[x+d,y-d*.56],[x+w+d,y-d*.56],[x+w,y]],'#202b34');poly(c,side,[[x+w,y],[x+w+d,y-d*.56],[x+w+d,y+h-d*.56],[x+w,y+h]],'#202b34');rr(c,x,y,w,h,3,front,'#202b34')}
function windowFrame(c,x,y,w,h,blind=false){rr(c,x-7,y-7,w+14,h+14,5,'#263744');rr(c,x,y,w,h,0,gradient(c,x,y,'#b4cdd0','#536e89'));for(let i=0;i<9;i++){const hh=24+rng(i+x)*78;c.fillStyle=i%2?'#688597':'#78919d';c.fillRect(x+i*w/9,y+h-hh,w/10,hh)}for(let i=1;i<3;i++)line(c,'#405764',5,[x+w*i/3,y],[x+w*i/3,y+h]);line(c,'#476173',4,[x,y+h*.57],[x+w,y+h*.57]);if(blind)for(let j=0;j<18;j++)line(c,'#455b63b8',3,[x,y+j*h/18],[x+w,y+j*h/18]);poly(c,'#e9f4e52f',[[x+12,y],[x+w*.7,y],[x+w*.33,y+h],[x,y+h]])}
function plant(c,x,y,sz=1){c.save();c.translate(x,y);c.scale(sz,sz);box(c,-19,-24,40,28,9,'#aa7652','#c79760','#724e3a');for(let k=0;k<7;k++){let ax=(k-3)*15,ay=-57-rng(k)*44;line(c,'#537455',3,[2,-24],[ax,ay]);c.save();c.translate(ax,ay);c.rotate((k-3)*.32);oval(c,0,0,10,25,k%2?'#72906a':'#537d70');c.restore()}c.restore()}
function desk(c,x,y,w=220){box(c,x,y,w,24,31,'#926647','#c9a16f','#614a3f');for(const j of [12,w-23])rr(c,x+j,y+24,10,68,2,'#384453');box(c,x+w*.35,y-62,78,49,8,'#394c55','#61747b','#293742');rr(c,x+w*.35+7,y-56,65,35,2,'#7e9b94');line(c,'#b9c7a3',2,[x+w*.35+17,y-37],[x+w*.35+55,y-38]);rr(c,x+w*.49,y-14,9,16,0,'#323d47')}
const bgCache=new Map();
function background(loc,scale,customDoor=false){
 const key=loc+scale+customDoor;if(bgCache.has(key))return bgCache.get(key);
 const cv=createCanvas(Math.round(W*scale),Math.round(H*scale)),c=cv.getContext('2d');c.scale(scale,scale);
 const [wall,light,floor]=palette[loc];c.fillStyle=gradient(c,0,0,wall,light);c.fillRect(0,0,W,H);
 const outside=['street','court','dusk'].includes(loc);
 poly(c,floor,[[0,470],[1280,450],[1280,720],[0,720]]);
 if(outside){
  for(let i=0;i<13;i++){const x=i*112-52,h=82+rng(i)*135;box(c,x,427-h,96,h,23,i%2?'#637b89':'#74919c','#acb9b8','#526877');for(let j=0;j<3;j++)for(let k=0;k<4;k++)rr(c,x+14+k*18,442-h+j*20,9,12,1,(k+j+i)%5?'#415b70':'#d5b479')}
  if(loc!=='street'){box(c,795,155,443,319,40,loc==='dusk'?'#5e637a':'#9f9c8c','#abb3ad','#596878');windowFrame(c,835,192,130,100);windowFrame(c,1025,192,128,100);rr(c,953,312,136,166,4,'#354c56','#bec3aa');rr(c,970,325,100,91,2,'#78949b','#263f4a');rr(c,1063,411,10,27,2,'#edbd76');for(let i=0;i<4;i++)line(c,'#6b7270',3,[800,337+i*25],[935,337+i*25])}
  poly(c,'#b9bfb4',[[0,560],[340,498],[890,499],[1280,573],[1280,640],[0,610]]);
  for(let i=0;i<6;i++){const x=i*229+30;line(c,'#56635f',6,[x,414],[x+6,485]);line(c,'#56635f',4,[x,425],[x-25,402]);oval(c,x,395,31,23,'#627b75')}
  if(loc==='dusk')oval(c,108,112,23,23,'#f3ce91');
 }else{
  poly(c,'#304554',[[0,0],[162,76],[162,479],[0,558]]);poly(c,'#263a4d',[[1280,0],[1120,71],[1120,457],[1280,549]]);line(c,'#a5a7a16b',3,[0,558],[163,477],[1117,454],[1280,549]);
  for(let i=0;i<8;i++){line(c,'#24333b34',2,[640+(i-3.5)*79,469],[(i-.8)*244,720]);line(c,'#ccd4b325',2,[0,500+i*i*4],[1280,500+i*i*4])}
  if(['office','meeting','coffee'].includes(loc)){
   windowFrame(c,185,100,360,211,loc==='meeting');windowFrame(c,741,97,356,218);
   if(loc==='office'){desk(c,255,433,196);desk(c,605,414,150);desk(c,886,449,175)}
   if(loc==='meeting'){box(c,324,484,585,19,73,'#8f623d','#c89862','#735339')}
   if(loc==='coffee'){box(c,808,449,278,42,26,'#5a6262','#c49866','#33474d');for(let i=0;i<3;i++)line(c,'#2c424a',2,[842+i*70,452],[842+i*70,490]);rr(c,851,334,186,48,4,'#325058');type(c,'КОФЕ',944,367,25,'#f4d28c')}
  }
  if(loc==='lobby'||loc==='entry'){
   if(!customDoor){rr(c,729,111,269,362,8,'#293c4d','#bc9b66');rr(c,745,125,238,330,4,gradient(c,745,125,'#91aeb0','#537084'));line(c,'#304b5a',10,[868,125],[868,455]);line(c,'#4a6672',5,[749,319],[983,319]);rr(c,904,321,11,42,2,'#efb46b');}
   if(loc==='lobby')for(let i=0;i<3;i++){box(c,219+i*129,438,34,92,12,'#526e79','#a0adb0','#314858');line(c,'#c3c5ad',5,[237+i*129,440],[289+i*129,414])}
   else{for(let i=0;i<5;i++)box(c,188+i*90,455-i*20,113,27+i*12,15,'#536672','#a1a8a1','#3e5160')}
  }
  if(loc==='shop'||loc==='dark'){
   for(const x of [166,859]){rr(c,x,123,233,350,4,'#2f424c','#80716a');for(let j=0;j<4;j++){for(let i=0;i<4;i++){const h=25+rng(i+j*4)*25;box(c,x+13+i*50,190+j*75-h,38,h,8,i%2?'#b58a5e':'#537988','#bda289','#394e55')}line(c,'#8e7966',9,[x+5,193+j*75],[x+227,193+j*75])}}
   box(c,408,459,410,39,39,'#725a48','#bb9268','#4f4f46');
  }
  if(loc!=='dark')for(const x of [232,581,915]){poly(c,'#d6d5b8',[[x,49],[x+151,48],[x+138,64],[x+10,64]]);line(c,'#fff6d1',4,[x+15,59],[x+130,59])}
  plant(c,1060,489,.85);
 }
 for(let i=0;i<4400;i++){const x=rng(i*2+1)*W,y=rng(i*2+2)*H;c.fillStyle=i%2?'#f5edcb08':'#1726390a';c.fillRect(x,y,1+rng(i)*2,1)}
 const practical=c.createRadialGradient(outside?980:790,outside?115:189,38,outside?980:790,outside?115:189,560);
 practical.addColorStop(0,loc==='dark'?'#6b8abc14':loc==='dusk'?'#efab8d27':'#ffe5a431');
 practical.addColorStop(1,'#ffffff00');c.fillStyle=practical;c.fillRect(0,0,W,H);
 if(!outside&&loc!=='dark'){
  poly(c,'#ffe6ad17',[[737,448],[952,448],[1138,642],[683,656]]);
  for(let i=0;i<4;i++)line(c,'#201b2029',2,[174,500+i*33],[1100,478+i*43]);
 }
 const vg=c.createRadialGradient(W*.53,H*.43,180,W*.5,H*.45,740);vg.addColorStop(0,'#10203000');vg.addColorStop(1,'#10152173');c.fillStyle=vg;c.fillRect(0,0,W,H);
 bgCache.set(key,cv);return cv;
}
const cast={
 vika:['#9a635a','#c98c70','#f0b890','#ead097'],
 sasha:['#426572','#b68362','#e6ae89','#b9d6b2'],
 oleg:['#745b46','#a57455','#d4aa7c','#e2b779'],
 hero:['#344b61','#c99a5e','#ffd8a0','#67a4c7'],
 lida:['#513e65','#b38254','#efb77c','#da8395'],
 kolya:['#2f6d69','#b37b49','#e5b17c','#e1ba67'],
 tamara:['#3b6654','#d9a180','#f0c1a1','#ddc88c'],
 auditor:['#bdc6bb','#43576a','#d4d6c1','#81d3cf'],
 neighbor:['#8b594e','#bd8768','#e0b08f','#dec687']
};
function face(c,who,x,y,blink,phase,emotion,look=1){
 const [coat,base,top,trim]=cast[who];
 if(['vika','sasha','oleg'].includes(who)){
  oval(c,x,y-8,47,51,who==='vika'?'#6a403d':'#42373c');oval(c,x,y+4,39,43,base);
  if(who==='vika'){rr(c,x-37,y-14,30,19,5,'#d8bd9e','#4a4a50');rr(c,x+6,y-14,30,19,5,'#d8bd9e','#4a4a50');line(c,'#4a4a50',3,[x-7,y-7],[x+6,y-7]);}
  if(who==='oleg')rr(c,x-45,y-42,90,21,7,'#758358','#344742');
 }else if(who==='neighbor'){
  oval(c,x,y-6,47,53,'#e2d2bc');oval(c,x,y+7,38,43,base);
  poly(c,'#e2d2bc',[[x-41,y-27],[x-19,y-51],[x+19,y-55],[x+41,y-32],[x+17,y-17],[x-2,y-27],[x-31,y-11]]);
 }else if(who==='tamara'){
  oval(c,x,y,52,59,'#574b53');oval(c,x,y+5,43,48,base);oval(c,x-39,y+8,7,12,base);oval(c,x+39,y+8,7,12,base);rr(c,x-52,y-53,104,33,11,'#326451','#182f34');oval(c,x,y-60,34,22,'#477e62');line(c,'#83a480',3,[x-43,y-35],[x+45,y-35]);line(c,'#855d58',2,[x-30,y+16],[x-18,y+18]);line(c,'#855d58',2,[x+28,y+16],[x+35,y+19]);
 }else if(who==='auditor'){
  box(c,x-55,y-45,110,92,20,'#c4cebd','#e2dcc5','#8699a1');rr(c,x-39,y-27,76,50,10,'#213643');line(c,'#718f94',4,[x+11,y-56],[x+11,y-71]);oval(c,x+11,y-72,5,5,'#f4b370');
 }else{
  box(c,x-53,y-49,106,94,20,base,top,'#805c49');
  poly(c,top,[[x-54,y-48],[x-69,y-70],[x-20,y-66],[x+4,y-49]],'#725949');
  poly(c,top,[[x+4,y-49],[x+23,y-71],[x+71,y-71],[x+53,y-49]],'#725949');
  line(c,'#f4d0a358',4,[x-48,y+37],[x+45,y+37]);
  for(let i=0;i<8;i++){
   const yy=y-40+i*10;
   line(c,i%2?'#6f4f3d21':'#fff0bb21',1,[x+57,yy],[x+70,yy-7]);
  }
  line(c,'#ffdfaf5c',1.5,[x-48,y-42],[x+45,y-42]);rr(c,x+54,y-3,15,12,1,trim);
  if(who==='lida')line(c,'#6a4a4a',4,[x-51,y-11],[x-27,y-19],[x-5,y-13],[x+22,y-13],[x+48,y-20]);
 }
 const ink=who==='auditor'?'#96e0d6':'#2d2834';const hh=blink?1.8:6.9;
 oval(c,x-17+look*3,y-4,4.8,hh,ink);oval(c,x+19+look*3,y-4,4.8,hh,ink);
 if(who!=='auditor'){let sl=emotion==='tension'?5:emotion==='relief'?-4:0;line(c,ink,3,[x-26,y-17-sl],[x-8,y-18]);line(c,ink,3,[x+10,y-18],[x+27,y-17-sl])}
 const speech=phase>0?2+phase*5:2;
 if(emotion==='relief'&&phase===0){c.beginPath();c.arc(x+2,y+15,12,.18,Math.PI-.18);c.lineWidth=3;c.strokeStyle=ink;c.stroke()}else oval(c,x+2,y+20,9,speech,ink);
}
function hand(c,x,y,side,skin,shadow,grip){
 c.save();c.translate(x,y);c.scale(side,1);c.rotate(grip?-.46:.18);
 rr(c,-9,-8,17,17,6,skin,shadow);
 for(let i=0;i<4;i++)rr(c,2-i*.6,-7+i*4,grip?8:12-i,4,2,skin,shadow);
 oval(c,-2,-9,4,6,skin);c.restore();
}
function actor(c,who,x,y,s,t,action,emotion,side,spoken=false,propType=null,sceneTime=t,voiceOpen=0,boxMotion=null){
 c.save();c.translate(x,y);c.scale(s,s);
 const [coat,base,top,trim]=cast[who];const walk=action==='walk', unboxed=who==='hero'&&action==='unboxed';
 const removing=who==='hero'&&boxMotion;
 const bob=Math.sin(t*(walk?8:2))*(walk?5:1.2);
 oval(c,5,3,76,15,'#101c3260');c.translate(0,bob);
 if(who==='auditor'){rr(c,-57,-69,115,62,18,'#7e9196','#263a4b');for(const x of [-38,42]){oval(c,x,-6,18,18,'#26313d');oval(c,x,-6,7,7,'#a3af9e')}}
 else{
  let z=walk?Math.sin(t*7)*16:0;line(c,'#25333e',24,[-25,-104],[-28+z,-63],[-30+z,-12]);line(c,'#354956',23,[24,-105],[28-z,-58],[31-z,-12]);rr(c,-46+z,-17,40,16,6,'#1c2734');rr(c,18-z,-17,44,16,6,'#1c2734');
 }
 poly(c,coat,[[-46,-195],[35,-197],[57,-166],[51,-82],[-47,-82],[-60,-158]],'#1e2938');
 poly(c,'#ffffff19',[[-43,-190],[-11,-198],[-4,-102],[-37,-85],[-49,-156]]);
 poly(c,'#c9c7b3',[[-17,-194],[20,-195],[11,-169],[-1,-157]]);
 poly(c,trim,[[1,-182],[10,-181],[14,-129],[2,-119],[-4,-133]]);
 rr(c,24,-163,19,12,3,'#d6bc82','#2b3545');
 const reaching=['read','greet','test','call','unlock','open','restore','confirm','inspect','lift','discover','decide','brake','carry','compare','listen','argue','search','reveal','heat','blackout'].includes(action);
 const gesture=['argue','decide','search'].includes(action)?1.2:['call','read','carry'].includes(action)?.72:.94;
 const f=reaching?gesture*(.22+.78*ease((sceneTime-.16)/1.08))*(.7+.3*(1-ease((sceneTime-2.6)/2.4))):0;
 const handX=side*(65+31*f+(walk?12*Math.sin(t*7):0));let handY=-114-42*f+(walk?9*Math.cos(t*7):0);
 if(action==='call')handY=-171-38*f;if(action==='test'||action==='unlock')handY=-137-33*f;
 const elbowX=side*(59+13*f),elbowY=-136+11*f;
 line(c,'#242f3d',23,[side*40,-167],[elbowX,elbowY],[handX,handY]);line(c,coat,18,[side*40,-167],[elbowX,elbowY],[handX,handY]);
 line(c,'#242f3d',22,[-side*40,-164],[-side*60,-136],[-side*48,-109]);line(c,coat,17,[-side*40,-164],[-side*60,-136],[-side*48,-109]);
 hand(c,handX,handY,side,top,base,Boolean(propType)||unboxed);hand(c,-side*48,-109,-side,top,base,false);
 if(propType){c.save();c.translate(handX+side*5,handY-7);c.scale(.26,.26);prop(c,propType,t,action,emotion);c.restore()}
 const blink=(t+.42)%4.1<.13;
 const attention=emotion==='tension'?.06:emotion==='relief'?-.035:.013;
 const beat=spoken?Math.min(1,voiceOpen)*.025:0;
 c.translate(0,-205);c.rotate(side*(attention+beat)*ease(sceneTime/.55));c.translate(0,205);
 if(unboxed||removing){
  const hx=side*68;
  if(!removing){
  box(c,hx-37,-157,72,62,15,base,top,'#805c49');
  poly(c,top,[[hx-37,-157],[hx-49,-174],[hx-12,-170],[hx,-157]],'#725949');
  poly(c,top,[[hx,-157],[hx+14,-172],[hx+50,-172],[hx+35,-157]],'#725949');
  hand(c,hx+side*12,-112,-side,top,base,true);}
  oval(c,0,-244,40,48,'#5c3e37');oval(c,0,-237,37,42,'#e0aa85');
  poly(c,'#593b36',[[-37,-250],[-34,-275],[-9,-290],[31,-278],[39,-250],[24,-261],[10,-254],[-7,-264],[-24,-253]]);
  oval(c,-13,-240,4,blink?1:5,'#302935');oval(c,15,-240,4,blink?1:5,'#302935');
  line(c,'#ad745f',2,[3,-237],[6,-222],[0,-222]);
  oval(c,2,-211,8,spoken?2+5*voiceOpen:2,'#6d423c');
  if(removing){
   const {lift,lower}=boxMotion;
   const xx=side*68*lower,yy=-243-82*lift+198*lower;
   c.save();c.translate(xx,yy);c.scale(1-.33*lower,1-.33*lower);
   face(c,who,0,0,blink,0,emotion,side);c.restore();
   line(c,coat,17,[side*39,-161],[side*(61+36*lift),-194-57*lift+91*lower],[xx+side*47,yy+36]);
   hand(c,xx+side*47,yy+36,-side,top,base,true);
  }
 }else face(c,who,Math.sin(t*1.5)*3,-243,blink,spoken?voiceOpen:0,emotion,side);
 c.restore();
}
function prop(c,name,t,action,emotion){
 const b='#263945',gold='#f3b972',paper='#f5dfb2',lit=emotion==='relief'||action==='unlock'||action==='restore'||action==='confirm';
 if(name==='coffee'){box(c,-84,-105,155,182,30,'#45576b','#b3bbc0','#2e4155');rr(c,-64,-86,115,63,10,'#202d3e');oval(c,-29,-57,7,11,'#b8d8e8');oval(c,16,-57,7,11,'#b8d8e8');oval(c,-7,-38,11,3+Math.sin(t*8)**2*3,'#b8d8e8');rr(c,-62,-3,104,53,4,'#283745');rr(c,-33,16,42,35,7,paper);line(c,'#e3b489',3,[-16,-5],[-16,16]);if(action==='receipt'||action==='confirm'){const h=20+ease(t/1.4)*90;rr(c,50,-13,37,h,2,paper);for(let i=0;i<7;i++)if(i*10<h-10)line(c,'#80705c',2,[55,-5+i*10],[80,-5+i*10]);if(h>52&&action==='receipt'){type(c,'09:00',68,22,10,'#694b48');type(c,'ПРОВЕРКА',68,32,6,'#a45141')}}}
 else if(name==='key'){rr(c,-66,-27,60,58,13,'#2b5363','#22323e');oval(c,-46,0,8,9,'#d3b17f');poly(c,gold,[[-10,-8],[65,-8],[65,8],[55,8],[55,18],[43,18],[43,8],[26,8],[26,15],[-10,15]],b)}
 else if(name==='reader'){box(c,-46,-74,96,133,17,'#42565d','#879da0','#273d48');rr(c,-25,-34,56,50,5,'#293c50');oval(c,2,-48,9,9,lit?'#7be4a0':'#f37261');for(let i=0;i<3;i++)line(c,'#aac0b1',2,[-14,-23+i*10],[23,-23+i*10])}
 else if(name==='phone'||name==='screen'){const w=name==='phone'?73:185,h=name==='phone'?130:108;rr(c,-w/2,-h/2,w,h,10,b,'#809297');rr(c,-w/2+7,-h/2+8,w-14,h-20,6,'#66898c');for(let i=0;i<5;i++)line(c,i===0?(lit?'#b8e6a8':gold):'#b8c9be',3,[-w/2+15,-h/2+23+i*12],[w/2-13-(i%3)*10,-h/2+23+i*12]);oval(c,0,h/2-6,4,2,'#d7ccab')}
 else if(name==='receipt'||name==='papers'||name==='cards'){const count=name==='receipt'?1:4;for(let j=count-1;j>=0;j--)rr(c,-73+j*8,-56-j*8,146,108,4,paper,'#9d805d');rr(c,-59,-45,36,14,2,'#ac6e56');for(let i=0;i<5;i++)line(c,'#8f806a',2,[-57,-20+i*12],[53-i%3*12,-20+i*12]);if(lit)type(c,'✓',52,40,37,'#417861')}
 else if(name==='helmet'){box(c,-64,-55,128,111,24,'#b4c0bd','#e0dccc','#7c9298');rr(c,-46,-30,92,59,14,'#21394a');oval(c,-20,-2,6,9,'#ace0db');oval(c,22,-2,6,9,'#ace0db');if(action==='lift')plant(c,1,-42,.6)}
 else if(name==='cup'){poly(c,'#d9a36e',[[-46,-53],[48,-53],[32,50],[-32,50]],b);oval(c,0,-53,50,13,paper);oval(c,0,-53,41,8,'#5b3c39');rr(c,-30,-10,58,24,2,'#ead0a0');if(action==='heat')for(let i=0;i<3;i++)line(c,'#e5eadab0',4,[-26+i*23,-62],[-31+i*23+Math.sin(t*4+i)*6,-85],[-23+i*23,-102])}
 else if(name==='cart'){box(c,-88,-48,155,52,22,'#a56e52','#dbb47e','#765b57');line(c,'#d6cba5',7,[70,-56],[88,-95],[107,-95]);for(const x of [-60,54]){oval(c,x,17,19,20,'#233440');oval(c,x,17,7,8,'#8d9d95')}}
 else if(name==='tools'){box(c,-81,-36,161,76,23,'#386177','#6798a2','#31515d');rr(c,-25,-55,50,18,5,'#223b4d');rr(c,-15,-6,30,21,4,gold);line(c,'#b7b4a0',5,[-62,5],[62,5])}
 else if(name==='board'){box(c,-127,-69,254,140,16,'#9b785c','#c29e72','#6a544c');for(let i=0;i<5;i++)rr(c,-110+i*43,-41+(i%2)*11,31,62,2,i%2?'#edc48c':'#b8d0bc');for(let i=0;i<4;i++)line(c,'#695b5c',2,[-107+i*43,-18],[ -85+i*43,-18])}
 else if(name==='door'){rr(c,-96,-126,183,250,4,'#263e51','#cbb486');const s=action==='open'||action==='unlock' ? 1-.55*ease((t-.85)/1.6):1;poly(c,'#5c8289',[[-86,-112],[-86+164*s,-112+30*(1-s)],[-86+164*s,112],[-86,112]],b);rr(c,-76,-101,Math.max(12,144*s),100,2,'#9bb6b4','#42616f');rr(c,-86+143*s,22,11,38,2,gold);oval(c,103,-28,9,9,lit?'#84d9a1':'#dc7862')}
 else if(name==='flash'){box(c,-55,-18,103,38,13,'#79644f','#ad9670','#514b4d');oval(c,46,0,16,23,'#eed8a3');poly(c,'#ffe6a04c',[[52,-20],[191,-67],[191,64],[52,20]])}
}
function editorialInsert(c,sc,tm,dur,scale){
 const id=sc.id;
 if(!['s001','s030','s035','s082','s089','s104','s116','s120','s126','s135','s196','s205'].includes(id))return false;
 c.drawImage(background(sc.location,scale,id==='s104'),0,0,W,H);
 c.fillStyle='#101a2c9c';c.fillRect(0,0,W,H);
 const e=ease(tm/.65);
 if(id==='s001'||id==='s205'){
  c.save();c.translate(326,384);c.scale(2.34,2.34);prop(c,'coffee',tm,'wait','focus');c.restore();
  const h=375*(id==='s001'?ease((tm-.1)/1.05):e);
  c.save();c.beginPath();c.rect(591,127,550,h);c.clip();
  rr(c,610,135,480,346,7,'#151b2b');rr(c,590,127,480,346,5,'#f8e3b7');
  for(let i=0;i<24;i++)poly(c,'#353340',[[590+i*20,474],[600+i*20,465],[610+i*20,474]]);
  type(c,'КОФЕ / СЛУЖЕБНЫЙ ЧЕК',830,184,22,'#705643');
  line(c,'#b69871',2,[630,205],[1030,205]);
  type(c,id==='s001'?'ПРОВЕРКА ОФИСА':'РЕЗУЛЬТАТ ПРОВЕРКИ',830,254,38,'#352b2a');
  type(c,id==='s001'?'09:00':'ПОДТВЕРЖДЕНО',830,333,id==='s001'?63:44,id==='s001'?'#a63d2f':'#246349');
  type(c,id==='s001'?'СПИСАНИЕ СОТРУДНИКОВ':'ЧЕЛОВЕКОМ',830,398,id==='s001'?27:50,id==='s001'?'#a63d2f':'#246349');
  c.restore();return true;
 }
 if(id==='s104'){
  rr(c,382,75,514,573,12,'#192d39','#ac986d');
  rr(c,399,88,480,542,6,'#7a6751');
  c.save();c.beginPath();c.rect(399,88,480,542);c.clip();
  const swing=ease((tm-.75)/1.45);
  const x=830-swing*303;
  c.globalAlpha=ease((swing-.2)/.6);actor(c,'neighbor',768,633,1.16,tm,'open','focus',-1,false);c.globalAlpha=1;
  poly(c,'#4d6f80',[[403,94],[x,105+swing*46],[x,607-swing*23],[403,625]],'#2d4857');
  poly(c,'#a3bcba',[[425,121],[x-24,130+swing*46],[x-24,347],[425,366]],'#537887');
  rr(c,x-40,411,15,52,3,'#dfb77c');c.restore();
  rr(c,925,290,66,96,9,'#2e4858');oval(c,958,314,7,7,'#f29770');
  return true;
 }
 if(id==='s135'){
  rr(c,377,175,528,408,22,'#202e3d','#729398');rr(c,413,206,455,304,13,'#476878');
  const push=ease((tm-1.05)/.8),release=ease((tm-2.5)/.65);
  const press=push*(1-release);
  rr(c,493,340+press*7,290,81-press*7,8,'#2f7b69');
  type(c,'ПОДТВЕРДИТЬ',640,393+press*3,28,'#eff1d1');
  oval(c,639,262,15,15,tm>1.85?'#ff945f':'#88dcb1');
  const x=1010-press*275,y=510-press*128;
  line(c,'#24574d',67,[1260,609],[x+151,y+66],[x+51,y+14]);
  c.save();c.translate(x+45,y);c.scale(4,4);hand(c,0,0,-1,'#e8ba8e','#996949',false);c.restore();
  return true;
 }
 const largePhone=id==='s196'||id==='s120';
 const x=largePhone?350:240,w=largePhone?580:800;
 c.save();c.translate(0,(1-e)*24);
 rr(c,x+12,129,w,486,28,'#121827');rr(c,x,110,w,485,25,'#182e3d','#729094');
 rr(c,x+20,130,w-40,437,16,'#e1e8d8');
 rr(c,x+20,130,w-40,83,15,'#284a54');
 const left=x+60;
 if(['s082','s089'].includes(id)){
  type(c,'ПАНЕЛЬ ДОСТУПА',left,184,28,'#f6efcf','left');
  for(let i=0;i<2;i++){
   const y=255+i*140;
   rr(c,left+3,y+12,w-120,96,14,i?'#173c37':'#aec6ae');
   rr(c,left,y,w-120,96,14,i?'#388061':'#518b71');
   type(c,'Восстановить',640,y+62,45,'#f4f0ce');
  }
 }else{
  const data={
   s030:['УЧЁТНАЯ СИСТЕМА','3 209 задач закрыто','Создать задачу'],
   s035:['УЧЁТНАЯ СИСТЕМА','Создать задачу','Проверить создание'],
   s116:['КАРТОЧКИ ДОСТУПА','Брелоки и ключи','Сверка списка'],
   s120:['ЛИДА · СВЯЗЬ','Список ключей','Проверяем вручную'],
   s126:['ПРОВЕРКА СПИСКА','Записи в журнале','Сверка с карточками'],
   s196:['ТАМАРА','Зашла домой.','Ключ работает.']
  }[id];
  type(c,data[0],left,183,28,'#f5ebc8','left');
  const y=259;
  rr(c,left,y,w-120,95,14,'#c1d8c3');
  type(c,data[1],left+22,y+60,largePhone?37:42,'#28464a','left');
  const y2=y+127;
  if(ease((tm-.8)/.65)>.01){
   c.globalAlpha=ease((tm-.8)/.65);rr(c,left,y2,w-120,95,14,'#accbbc');
   type(c,data[2],left+22,y2+60,largePhone?37:42,'#254a43','left');c.globalAlpha=1;
  }
 }
 c.restore();return true;
}
const workShots = new Set(['s115','s117','s118','s121','s122','s123','s124','s125','s129','s131']);
function workshop(c,s,tm,dur,scale){
 const t=s.start+tm;
 const drawCard=(x,y,label,index,passed)=>{
  c.save();c.translate(x,y);c.rotate(index%2?.034:-.048);
  rr(c,-94,-60,188,120,10,'#342c36');
  rr(c,-98,-67,188,120,8,'#f1d7a7','#7b5a45');
  type(c,label,-4,-19,19,'#422f37');
  line(c,'#b19675',2,[-71,-3],[63,-3]);type(c,passed?'СОВПАЛО':'КЛЮЧ '+(index+1),-4,28,18,passed?'#2d6d52':'#5c4a49');
  c.restore();
 };
 const tabletop=()=>{
  c.fillStyle=gradient(c,0,0,'#493d4a','#b78758');c.fillRect(0,0,W,H);
  for(let i=0;i<8;i++)line(c,'#805d4a',2,[0,i*99],[W,i*99+19]);
  const g=c.createRadialGradient(623,322,140,623,322,740);
  g.addColorStop(0,'#ffe3ab38');g.addColorStop(1,'#222333a6');c.fillStyle=g;c.fillRect(0,0,W,H);
 };
 if(t<737.97){
  tabletop();
  const index=Math.min(4,Math.floor(Math.max(0,t-724.7)/2.25));
  const phase=Math.max(0,(t-724.7)/2.25)%1;
  rr(c,411,143,477,427,15,'#342c38');
  rr(c,403,131,477,427,15,'#f0d5a8','#9c7b56');
  type(c,'ЖУРНАЛ ВЫДАЧИ',642,194,38,'#423440');
  for(let i=0;i<5;i++){
   rr(c,453,221+55*i,378,45,6,i===index?'#f6e4b9':'#dbbf96');
   type(c,i===4?'ТАМАРА':('БРЕЛОК 0'+(i+1)),479,251+55*i,21,'#513f41','left');
   if(i<index||i===index&&phase>.69)type(c,i===4?'НЕ СОВПАЛО':'✓',807,251+55*i,19,i===4?'#9e3d36':'#306f50','right');
  }
  const reach=ease(phase/.55),x=218+140*reach,y=323+index*28;
  line(c,'#224f49',66,[-20,601],[x-131,y+128],[x-40,y+37]);
  hand(c,x-55,y+37,1,'#eac08e','#9e7551',true);
  drawCard(x,y,index===4?'ТАМАРА':'КАРТОЧКА',index,index!==4&&phase>.7);
  if(index===4&&phase>.32){line(c,'#a33f38',5,[x+8,y+19],[x+65,y+7]);line(c,'#a33f38',4,[x+15,y+5],[x+67,y+22]);}
  return;
 }
 if(t<767.65){
  const stage=t<753.65?0:t<759.6?1:2;
  const who=['vika','sasha','oleg'][stage];
  c.drawImage(background(stage===0?'office':stage===1?'meeting':'lobby',scale),0,0,W,H);
  const e=ease(tm/.65),x=825+72*(1-e);
  actor(c,who,x,607,1.55,tm,'read','focus',-1,true,['cards','phone','key'][stage],tm,s.voiceOpen);
  rr(c,94,142,484,335,23,'#233644','#91a6a4');
  rr(c,112,160,448,298,16,'#e3ebd6');
  type(c,['ВИКА','САША','ОЛЕГ'][stage],336,251,59,'#254e4d');
  type(c,['Читает карточки','Проверяет историю','Ищет владельцев'][stage],336,319,30,'#345657');
  const status=ease((tm-.6)/.45);
  c.globalAlpha=status;rr(c,192,366,288,54,26,'#b6d1a8');type(c,'НА СВЯЗИ',336,402,22,'#255541');c.globalAlpha=1;
  return;
 }
 if(t<783.29){
  tabletop();
  rr(c,154,82,972,552,30,'#233742','#829c9d');
  rr(c,177,107,926,500,15,'#dce5d5');
  type(c,'ОТВЕТСТВЕННЫЙ',411,195,32,'#335454');
  rr(c,246,232,327,78,9,'#b9d1bf');type(c,'Лида',409,283,35,'#214b48');
  const e=ease((t-774)/1.2);
  c.globalAlpha=e;
  rr(c,644,139,394,401,14,'#f1dcaf');
  type(c,'ЖУРНАЛ УЧАСТНИКОВ',841,197,24,'#4f4342');
  for(let i=0;i<3;i++){
   const yy=241+85*i;line(c,'#b19470',2,[679,yy+50],[998,yy+50]);
   type(c,['Вика','Саша','Олег'][i],695,yy+31,29,'#415653','left');
   type(c,'✓',974,yy+31,27,'#3c754d');
  }
  c.globalAlpha=1;return;
 }
 tabletop();
 if(s.id==='s131'){
  rr(c,390,84,500,550,37,'#203544','#a0b4ab');
  rr(c,411,112,458,492,23,'#dce8d6');
  type(c,'ВОДИТЕЛЬ',640,206,34,'#28484c');
  rr(c,448,250,384,160,16,'#b9d3c4');
  type(c,'Я у соседнего',640,317,31,'#2b5150');
  type(c,'дома.',640,366,31,'#2b5150');
  return;
 }
 const pour=ease((t-796.4)/1.55);
 const kettleY=442-146*pour;
 line(c,'#345e50',63,[0,664],[165,535],[340,kettleY-5]);
 hand(c,331,kettleY-5,1,'#e5b39a','#a67865',true);
 c.save();c.translate(504,442-146*pour);c.rotate(pour*.55);box(c,-128,-98,226,187,40,'#758f8c','#a5b9ac','#3e606a');
 rr(c,-184,-76,79,93,23,'#233e50','#789791');poly(c,'#779897',[[90,-39],[166,-61],[185,-40],[100,18]]);
 c.restore();
 if(pour>.8){line(c,'#bde4e3a6',6,[685,362],[710,428],[725,490]);oval(c,727,495,26,6,'#badac3');}
 oval(c,722,547,139,16,'#211d2a77');rr(c,636,467,176,74,14,'#554e51','#a59281');
 type(c,'МЕСТО ДЛЯ ЧАЙНИКА',724,514,16,'#e7cfab');
}
function actionV3(c,s,tm,dur,scale){
 if(workShots.has(s.id)){workshop(c,s,tm,dur,scale);return true;}
 if(!['s066','s072','s170','s204'].includes(s.id))return false;
 c.drawImage(background(s.location,scale,s.id==='s066'||s.id==='s072'),0,0,W,H);
 if(s.id==='s066'||s.id==='s072'){
  rr(c,710,108,290,462,8,'#273c4d','#af9a78');
  rr(c,727,127,254,420,6,'#58778a');
  rr(c,748,152,211,177,5,'#abc3bf');
  rr(c,934,389,13,65,4,'#e1b376');
  c.save();c.translate(1046,352);c.scale(.73,.73);prop(c,'reader',tm,'wait','focus');c.restore();
  actor(c,s.id==='s066'?'kolya':'tamara',550,623,1.28,tm,'inspect','tension',1,true,s.id==='s072'?'key':null,tm,s.voiceOpen);
  return true;
 }
 if(s.id==='s170'){
  const e=ease(tm/2.4),x=711+139*e;
  actor(c,'kolya',570+139*e,608,1.19,tm,'walk','focus',1,false);
  c.save();c.translate(x,570);c.scale(1.08,1.08);prop(c,'cart',tm,'roll','focus');c.restore();
  return true;
 }
 const lift=ease((tm-.42)/1.2),lower=ease((tm-1.65)/1.45);
 actor(c,'hero',599,628,1.32,tm,lower>.76?'unboxed':'lifting','focus',1,true,null,tm,s.voiceOpen,{lift,lower});
 actor(c,'lida',873,599,1.02,tm,'listen','relief',-1,false);
 return true;
}

function shot(c,sc,t,dur,scale){
 const tm=clamp(t,0,dur),bg=background(sc.location,scale,sc.action==='unlock'||sc.id==='s111');
 if(actionV3(c,sc,tm,dur,scale))return;
 const special=editorialInsert(c,sc,tm,dur,scale);
 if(!special)c.drawImage(bg,0,0,W,H);
 const pr=tm/Math.max(.1,dur), phase=(sc.serial||0)*.73;
 const tension=['blackout','argue','search','decide','inspect'].includes(sc.action), relief=['unlock','restore','confirm','heat','open'].includes(sc.action);
 const mood=relief?'relief':tension?'tension':'focus';
 const loc=sc.location;const walk=sc.action==='walk',motion=walk?(pr-.5)*143:0;
 if(['street','court','dusk'].includes(loc)){
  c.save();c.fillStyle=loc==='dusk'?'#ffdcb058':'#f6f6e361';
  for(let j=0;j<37;j++){
   const x=(rng(j+18)*W+tm*(8+rng(j)*9))%W, y=(rng(j*7+2)*H+tm*(14+rng(j+9)*21))%H;
   const r=1+rng(j)*1.1;c.beginPath();c.ellipse(x,y,r,r,0,0,Math.PI*2);c.fill();
  }
  c.restore()
 }
 const own=sc.other==='hero', main=sc.other, secondary=own?'lida':'hero';
 const blinkTime=tm+phase;
 const lastScene=sc.chapter===8&&sc.paragraph===6;
 const heroAction=lastScene?'unboxed':sc.action;
 if(!special){
 if(sc.mode==='portrait'){
  c.save();c.translate(648,385);c.scale(2.25+pr*.18,2.25+pr*.18);actor(c,main,0,224,1.16,blinkTime,main==='hero'?heroAction:sc.action,mood,1,true,null,tm,sc.voiceOpen);c.restore();
 }else if(sc.mode==='insert'){
  c.save();c.fillStyle='#101c2d88';c.fillRect(0,0,W,H);
  poly(c,loc==='dark'?'#455464':'#735641',[[0,563],[1280,512],[1280,720],[0,720]]);
  oval(c,655,sc.prop==='cart'?562:546,sc.prop==='cart'?210:275,sc.prop==='cart'?16:55,'#16213758');
  const enter=ease(tm/1.3);
  const ax=626+Math.sin(tm*.7+phase)*13,ay=sc.prop==='cart'?480:361+(1-enter)*60;
  c.translate(ax,ay);c.scale(2.18+pr*.14,2.18+pr*.14);
  if(['key','phone','receipt','cards','cup','tools'].includes(sc.prop)){
   c.save();c.translate(-84-(1-enter)*39,43);c.rotate(-.28);rr(c,-89,-14,102,38,10,cast[main][0],'#263947');oval(c,15,4,25,19,cast[main][2]);for(let i=0;i<3;i++)line(c,cast[main][1],2,[11+i*4,-4],[26+i*3,-6]);c.restore()
  }
  prop(c,sc.prop,tm,sc.action,mood);c.restore();
 }else{
  c.save();
  let z=sc.mode==='wide'?1.03+pr*.03:sc.mode==='reaction'?1.46+pr*.08:1.37+pr*.07;
  let focus=sc.mode==='reaction'?820:sc.mode==='medium'?487:640;
  const bx=W*.5-focus*z+Math.sin(pr*1.2+phase)*10,by=H*.54-H*.54*z+(z-1)*48;
  c.save();c.translate(Math.min(0,bx*.42),by*.42);const bz=1+(z-1)*.43;c.scale(bz,bz);c.drawImage(bg,0,0,W,H);c.restore();
  c.translate(bx,by);
  c.scale(z,z);
  if(['coffee','shop','meeting'].includes(loc)){box(c,852,548,175,22,20,'#716653','#b49873','#3e4d52');c.save();c.translate(925,498);c.scale(.51,.51);prop(c,loc==='coffee'?'coffee':loc==='shop'?'tools':'papers',tm,sc.action,mood);c.restore()}
  if(sc.action==='unlock'){c.save();c.translate(867,341);c.scale(1.13,1.34);prop(c,'door',tm,'wait','focus');c.restore()}
  if(sc.prop==='cart'||(sc.prop==='coffee'&&walk)){
   c.save();c.translate(1028+motion,562);c.scale(.65,.65);prop(c,'cart',tm,sc.action,mood);
   if(sc.prop==='coffee'){c.translate(-5,-117);c.scale(.57,.57);prop(c,'coffee',tm,sc.action,mood)}
   c.restore()
  }
  const obj=['key','phone','receipt','cards','cup','tools','flash','helmet'].includes(sc.prop)?sc.prop:null;
  const offset=(rng(sc.paragraph*13+sc.chapter*25)-.5)*103;
  const actorX=462+motion+offset,otherX=803+motion-offset*.5;
  if(sc.prop==='reader'||sc.action==='test'){
   c.save();c.translate((sc.mode==='reaction'?otherX-133:actorX+132),430);c.scale(.43,.43);prop(c,'reader',tm,sc.action,mood);c.restore()
  }
  if(sc.location==='court'&&sc.chapter>=3&&sc.mode==='wide'&&['test','greet','confirm'].includes(sc.action)){
   actor(c,'kolya',967,488,.59,blinkTime+.9,'wait','focus',-1,false);
  }
  if(sc.mode==='reaction'){
   actor(c,main,otherX,611+(sc.action==='inspect'?16:0),1.10,blinkTime,main==='hero'?heroAction:sc.action,mood,-1,true,obj,tm,sc.voiceOpen);
   actor(c,secondary,actorX,634,1.15,blinkTime+.6,lastScene&&secondary==='hero'?'unboxed':'wait',mood,1,false);
  }else{
   actor(c,main,actorX,605+(sc.action==='inspect'?18:0),1.08,blinkTime,main==='hero'?heroAction:sc.action,mood,1,true,obj,tm,sc.voiceOpen);
   actor(c,secondary,otherX,602,.97,blinkTime+.65,lastScene&&secondary==='hero'?'unboxed':walk?'walk':sc.action==='argue'?'argue':'wait',mood,-1,false);
  }
  c.restore();
 }
 }
 if(loc==='dark'){const gl=c.createRadialGradient(670,375,60,670,375,640);gl.addColorStop(0,'#10152000');gl.addColorStop(1,'#101527a0');c.fillStyle=gl;c.fillRect(0,0,W,H)}
 if(sc.action==='blackout'){c.fillStyle=`rgba(10,15,26,${.66*ease((sc.start+tm-837.32)/.39)})`;c.fillRect(0,0,W,H)}
}
function makeCanvas(scale){const cv=createCanvas(Math.round(W*scale),Math.round(H*scale));return {cv,c:cv.getContext('2d')}}
module.exports={shot,makeCanvas,type,background};
