'use strict';
const A=require('./art.cjs');const {INK,P,path,line,rect,oval,text,paper}=A;
const PEOPLE={hero:{coat:'#c29a48',shadow:'#98783e',skin:'#e7c4a1',shade:'#c69d81',hair:'#624637',pants:'#53666b'},nora:{coat:'#527e91',shadow:'#3b596c',skin:'#e2bd9f',shade:'#be977f',hair:'#d1d5c9',pants:'#405760'},chief:{coat:'#796172',shadow:'#59465b',skin:'#d5b293',shade:'#b68e74',hair:'#686961',pants:'#565260'},worker:{coat:'#7b8972',shadow:'#5d6a58',skin:'#bb8e70',shade:'#9a7159',hair:'#544b3f',pants:'#56645d'},woman:{coat:'#9b7569',shadow:'#795b54',skin:'#e2b99a',shade:'#bd967e',hair:'#765344',pants:'#5b5d60'},child:{coat:'#b56e56',shadow:'#904f43',skin:'#e7c3a1',shade:'#c8a285',hair:'#72503b',pants:'#586d75'}};
PEOPLE.client={coat:'#d0bc91',shadow:'#a08a6f',skin:'#cba182',shade:'#ad8168',hair:'#554338',pants:'#526474'};
PEOPLE.manager={coat:'#5c7164',shadow:'#405447',skin:'#ddb795',shade:'#b58d71',hair:'#3f4240',pants:'#4c5353'};
function bone(c,x,y,X,Y,w1,w2,col){const dx=X-x,dy=Y-y,d=Math.hypot(dx,dy)||1,nx=-dy/d,ny=dx/d;path(c,`M${x+nx*w1} ${y+ny*w1} Q${(x+X)/2+nx*w1} ${(y+Y)/2+ny*w1} ${X+nx*w2} ${Y+ny*w2} Q${X+dx/d*6} ${Y+dy/d*6} ${X-nx*w2} ${Y-ny*w2} L${x-nx*w1} ${y-ny*w1} Z`,col,INK,2.4)}
function hand(c,x,y,angle=0,kind='open',skin='#e7c4a1',size=.68){c.save();c.translate(x,y);c.rotate(angle);c.scale(size,size);c.translate(0,-26);
 if(kind==='open'){
  path(c,'M-10 26 Q-15 14 -16 3 L-29 -4 Q-34 -10 -28 -13 Q-23 -16 -14 -5 L-14 -28 Q-15 -37 -9 -37 Q-4 -36 -5 -28 L-4 -13 L-2 -38 Q-1 -45 5 -43 Q10 -42 8 -34 L7 -13 L13 -34 Q15 -41 20 -38 Q25 -35 22 -29 L17 -9 L24 -22 Q28 -28 32 -24 Q36 -20 31 -14 L23 5 Q20 13 12 26 Z',skin);
  path(c,'M-12 2 Q-4 -3 3 5 M-6 15 Q4 8 16 10',null,'#9e785e',1.3);
 }else if(kind==='point'){
  path(c,'M-11 25 L-18 5 Q-23 -10 -15 -15 L-10 -13 L-9 -43 Q-8 -52 -2 -50 Q3 -50 3 -43 L3 -16 Q12 -23 18 -14 Q28 -20 31 -9 Q39 -8 33 9 L17 27 Z',skin);
  path(c,'M6 -11 L8 6 M17 -10 L18 6 M27 -5 L26 9 M-15 0 Q-3 -5 4 4',null,'#9e785e',1.6);
 }else{
  path(c,'M-12 26 L-21 5 Q-26 -10 -16 -15 Q-8 -24 1 -19 Q9 -25 17 -17 Q27 -19 29 -8 Q37 -1 29 13 L16 27 Z',skin);
  path(c,'M-14 -11 Q-7 -5 -9 7 M-4 -15 Q3 -7 1 7 M8 -16 Q16 -5 11 9 M20 -10 Q26 -1 21 10 M-18 5 Q-7 -2 4 7',null,'#9e785e',1.5);
 }
 c.restore()}
function head(c,person='hero',emotion='neutral',angle='three',look=0,t=0){const p=PEOPLE[person]||PEOPLE.hero;const female=['nora','woman'].includes(person);c.save();
 if(angle==='front'){
  path(c,'M-36 -45 Q-49 -24 -43 7 Q-39 48 0 54 Q39 48 43 7 Q49 -24 36 -45 Q0 -72 -36 -45 Z',p.skin);
  path(c,'M-36 -41 Q-42 2 -24 33 Q-15 47 0 51 Q-36 49 -43 7 Q-49 -24 -36 -41 Z',p.shade,null);
  for(const side of [-1,1]){oval(c,side*44,-2,9,16,p.skin);path(c,`M${side*44} -11 q${-side*10} 10 0 20`,null,'#a77b61',1.3)}
 }else if(angle==='profile'){
  path(c,'M-31 -45 Q-47 -12 -25 24 Q-12 53 13 51 L31 35 L30 17 L52 9 L34 -3 L32 -31 Q25 -63 -10 -60 Z',p.skin);
  path(c,'M-30 -37 Q-41 -5 -22 21 L-9 41 Q-22 26 -15 9 Q-9 -13 -10 -44 Z',p.shade,null);
  oval(c,-27,-3,12,19,p.skin);path(c,'M-28 -14 Q-14 -8 -27 7',null,'#a77b61',1.3);
 }else{
  path(c,'M-35 -45 Q-53 -22 -44 5 L-34 31 Q-18 55 6 53 Q32 52 42 25 L47 -6 Q43 -55 4 -61 Q-23 -64 -35 -45 Z',p.skin);
  path(c,'M-36 -41 Q-45 -11 -33 13 Q-24 35 -1 49 Q-28 44 -36 28 L-45 5 Q-51 -22 -36 -41 Z',p.shade,null);
  oval(c,-44,-2,11,17,p.skin);path(c,'M-47 -10 Q-35 -8 -43 7',null,'#a77b61',1.3);
 }
 if(person==='hero'||person==='child'){
  path(c,'M-47 -6 Q-57 -23 -45 -38 Q-51 -57 -30 -57 Q-29 -72 -10 -65 Q0 -78 16 -65 Q32 -71 37 -52 Q57 -47 47 -28 L39 -17 L33 -40 Q19 -29 13 -44 Q-5 -31 -10 -47 Q-18 -32 -29 -39 L-34 -13 L-40 1 Z',p.hair);
  path(c,'M-40 -40 Q-29 -54 -20 -48 M-12 -55 Q0 -66 9 -56 M14 -52 Q30 -62 35 -47',null,'#87614b',2);
 }else if(person==='nora'){
  path(c,'M-49 10 Q-63 -13 -50 -39 Q-42 -68 -8 -66 Q26 -77 44 -46 Q60 -27 48 -2 L37 -19 L30 -42 Q17 -24 2 -39 Q-13 -18 -28 -33 L-34 3 Z',p.hair);
  path(c,'M-43 -44 Q-20 -67 -3 -47 M7 -51 Q29 -67 38 -39',null,'#969e98',1.5);
 }else if(person==='chief'){
  path(c,'M-48 4 Q-55 -19 -42 -40 L-22 -51 L-27 -34 L-37 -17 L-37 7 Z',p.hair);path(c,'M25 -49 Q48 -42 49 -13 L40 -5 L36 -30 Z',p.hair);
 }else if(person==='woman'){
  path(c,'M-48 10 Q-62 -40 -28 -58 Q-1 -75 32 -53 Q59 -40 47 15 L35 -5 L31 -34 Q5 -18 -11 -40 L-30 -19 L-31 13 Z',p.hair);
 }else{
  path(c,'M-45 -4 L-51 -31 Q-41 -56 -15 -60 Q19 -68 40 -44 L44 -19 L34 -27 L25 -41 Q-1 -25 -29 -37 L-34 1 Z',p.hair);
  path(c,'M-29 21 Q5 52 35 15 Q35 53 4 58 Q-20 51 -29 21 Z',p.hair);
 }
 const blink=(t%4.9)<.105;
 let eyes=angle==='profile'?[[17,-11,12,8]]:angle==='front'?[[-19,-10,13,9],[20,-10,13,9]]:[[-12,-10,15,9],[27,-10,12,8]];
 for(const [x,y,rx,ry] of eyes){if(blink){path(c,`M${x-rx} ${y} Q${x} ${y+4} ${x+rx} ${y}`,null,INK,2.5)}else{oval(c,x,y,rx,emotion==='surprise'?ry*1.25:emotion==='focused'?ry*.72:ry,'#f4f1e3');oval(c,x+look*4+2,y+1,4.5,emotion==='focused'?5.6:6,INK,null);oval(c,x+look*4+3,y-1,1.2,1.2,'white',null)}}
 const brow=emotion==='worried'?-7:emotion==='angry'?5:emotion==='surprise'?-9:emotion==='focused'?2:0;
 path(c,emotion==='angry'?'M-29 -31 L1 -20 M16 -20 L43 -31':emotion==='focused'?'M-28 -24 L1 -21 M15 -21 L42 -25':`M-28 -27 Q-14 ${-32+brow} 1 ${-25-brow*.5} M15 ${-26-brow*.5} Q30 ${-32+brow} 42 -25`,null,p.hair,4);
 if(angle==='profile')path(c,'M28 -9 L27 8 L38 11',null,INK,1.6);else path(c,angle==='front'?'M2 -8 L-3 10 Q3 15 9 10':'M17 -10 L10 10 Q18 16 25 9',null,'#9d795f',1.6);
 if(emotion==='smile'||emotion==='relieved'){path(c,'M-7 27 Q11 39 29 24 Q11 49 -7 27 Z','#f4efe1');path(c,'M-18 12 Q-21 22 -15 24 M31 11 Q38 18 34 25',null,'#b68d71',1.3)}
 else if(emotion==='surprise')path(c,'M1 29 Q10 21 19 28 L20 37 Q8 43 1 35 Z','#785348');
 else if(emotion==='worried')path(c,'M-5 34 Q11 23 27 32',null,INK,2);
 else if(emotion==='focused')path(c,'M-6 30 L25 29',null,INK,1.8);
 else if(emotion==='angry')path(c,'M-5 31 L26 26 M0 38 L22 34',null,INK,2);
 else path(c,'M-7 29 Q11 33 27 27',null,INK,2);
 if(person==='nora'){for(let x of [-12,27])oval(c,x,-10,19,16,null,'#385765',3);line(c,7,-12,10,-12,'#385765',3);line(c,-31,-14,-42,-18,'#385765',3)}
 if(person==='chief'){path(c,'M-24 4 Q-17 8 -7 6 M21 8 Q31 10 38 6 M-20 -40 L-2 -41',null,'#9b7b64',1)}
 if(female)path(c,'M-27 -15 L-33 -20 M37 -14 L44 -18',null,INK,1.8);
 c.restore()}
function actor(c,person,x,y,s=1,pose='idle',emotion='neutral',t=0,opt={}){const p=PEOPLE[person]||PEOPLE.hero;c.save();c.translate(x,y);c.scale(s,s);if(opt.flip)c.scale(-1,1);
 const walk=pose==='walk'?Math.sin(t*7):0,lean=pose==='stamp'?-.045:pose==='lever'?0:0;
 // Individual feet and bent knees retain a stable floor.
 for(let side of [-1,1]){let hip=side*28,knee=side*35+walk*side*13,ankle=side*38+walk*side*31;bone(c,hip,-175,knee,-88,27,23,p.pants);bone(c,knee,-88,ankle,-10,24,19,p.pants);path(c,`M${ankle-22} -19 L${ankle+18} -17 Q${ankle+34} -12 ${ankle+43} -2 L${ankle+43} 12 L${ankle-23} 12 Z`,'#464d48');line(c,ankle-19,8,ankle+39,8,'#232d30',3);for(let k=0;k<3;k++)line(c,ankle+6-k*3,-13+k*5,ankle+23-k*3,-10+k*4,'#aab0a2',1.3)}
 c.save();c.rotate(lean);
 // Neck and tailored coat, seams, storm flap and readable silhouette.
 path(c,'M-24 -396 L23 -397 L29 -360 L-26 -359 Z',p.skin);
 path(c,'M-57 -369 Q-80 -352 -81 -323 L-76 -211 L-87 -164 Q-33 -143 0 -154 Q47 -145 83 -164 L72 -215 L79 -325 Q77 -354 55 -370 L26 -381 Q0 -362 -27 -381 Z',p.coat);
 path(c,'M45 -367 Q66 -340 59 -283 L55 -164 L80 -164 L71 -216 L79 -326 Q77 -355 55 -370 Z',p.shadow,null);
 path(c,'M-27 -383 L-2 -361 L-15 -338 L-43 -372 Z',P.cream);path(c,'M27 -383 L-2 -361 L12 -339 L44 -373 Z',P.cream);
 line(c,-2,-360,-2,-157,INK,2.2);for(let yy=-327;yy<-172;yy+=29)oval(c,9,yy,3.2,3.2,'#dbc9a2',INK,1);
 for(let side of [-1,1]){rect(c,side<0?-62:23,-265,40,49,p.shadow,INK,1.8);path(c,`M${side<0?-64:21} -267 l44 0 l-3 14 l-38 0 Z`,p.coat);line(c,side<0?-64:22,-196,side<0?-22:61,-196,'#746448',1)}
 path(c,'M-45 -329 Q-53 -322 -45 -317 Q-36 -317 -37 -325 Q-34 -336 -43 -336 Q-50 -336 -49 -329 Z',P.cream,INK,1.4);
 let L=[-74,-168],R=[74,-168],lk='grip',rk='grip';
 if(pose==='walk'){L=[-72+walk*29,-175+walk*17];R=[72-walk*29,-175-walk*17]}
 if(pose==='point'){R=[165,-317];rk='point';L=[-70,-210]}
 if(pose==='read'||pose==='carry'){L=[-48,-269];R=[48,-269];lk=rk='grip'}
 if(pose==='explain'){L=[-65,-235];R=[148,-325+7*Math.sin(t*1.6)];lk='grip';rk='open'}
 if(pose==='offer'){L=[-70,-210];R=[145,-265];rk='open'}
 if(pose==='inspect'){L=[-48,-269];R=[110,-335];lk='grip';rk='point'}
 if(pose==='umbrella'){L=[-70,-210];R=[35,-280];rk='grip'}
 if(pose==='box'){L=[-85,-250];R=[85,-250];lk=rk='grip'}
 if(pose==='stop'){L=[-60,-225];R=[130,-380];rk='open'}
 if(pose==='tool'){L=[-50,-260];R=[104,-325+12*Math.sin(t*2)];rk='grip'}
 if(pose==='write'){L=[-48,-269];R=[55,-275+6*Math.sin(t*3)];lk=rk='grip'}
 if(pose==='call'){R=[48,-418];rk='grip';L=[-70,-210]}
 if(pose==='stamp'){R=[90,-228-20*Math.sin(Math.min(1,t%3)*Math.PI)];L=[-45,-260];rk='grip';lk='open'}
 if(pose==='worried'){R=[26,-404];L=[-57,-230];rk='open'}
 if(pose==='lever'){L=opt.left||[120,-248];R=opt.right||[145,-250];lk=rk='grip'}
 if(pose==='umbrella')A.umbrella(c,35,-408,1,.01*Math.sin(t));
 if(pose==='box')require('./props.cjs').flowers(c,0,-250,.65);
 if(pose==='tool'){line(c,107,-354+12*Math.sin(t*2),107,-410+12*Math.sin(t*2),'#758a86',7);rect(c,99,-354+12*Math.sin(t*2),16,40,'#a66b4c')}
 if(pose==='write'){paper(c,0,-262,.78,'ЖУРНАЛ');line(c,50,-278,16,-316,'#465e64',5)}
 if(pose==='offer')paper(c,140,-271,.62,'ДОГОВОР');
 if(pose==='inspect')paper(c,-17,-260,.64,'ЗАМЕР');
 if(pose==='read')paper(c,0,-262,.78,'ЗАЯВКА');
 if(pose==='carry')A.weatherJar(c,0,-265,.55,false);
 if(pose==='call'){rect(c,35,-451,24,72,'#45585a');for(let i=0;i<3;i++)line(c,39,-435+i*7,55,-435+i*7,'#bcb59b',1.2)}
 if(opt.left)L=opt.left;if(opt.right)R=opt.right;if(opt.leftKind)lk=opt.leftKind;if(opt.rightKind)rk=opt.rightKind;
 // Two-bone IK, lowered elbows for raised gestures, stable holds for carried props.
 for(const [side,target,kind] of [[-1,L,lk],[1,R,rk]]){const sx=side*58,sy=-350,dx=target[0]-sx,dy=target[1]-sy,d=Math.min(204,Math.max(12,Math.hypot(dx,dy))),theta=Math.atan2(dy,dx),alpha=Math.acos(Math.max(-1,Math.min(1,d/210))),ea=theta+(target[1]<-300?side:-side)*alpha,ex=sx+Math.cos(ea)*105,ey=sy+Math.sin(ea)*105;
  bone(c,sx,sy,ex,ey,25,21,p.coat);bone(c,ex,ey,target[0],target[1],22,16,p.coat);const aa=Math.atan2(target[1]-ey,target[0]-ex);bone(c,target[0]-Math.cos(aa)*12,target[1]-Math.sin(aa)*12,target[0],target[1],18,18,p.shadow);hand(c,target[0],target[1],aa+Math.PI/2,kind,p.skin,.68)
 }
 if(pose==='stamp'){rect(c,76,R[1]-7,28,34,'#8f5c3d');oval(c,90,R[1]-17,13,10,P.rust);rect(c,67,R[1]+24,46,10,'#655142')}
 c.save();c.translate(0,-435);c.scale(.86,.86);head(c,person,emotion,opt.angle||'three',opt.look||0,t+1.2);c.restore();
 c.restore();c.restore();
 return {left:{x:x+L[0]*s,y:y+L[1]*s},right:{x:x+R[0]*s,y:y+R[1]*s}};
}
module.exports={PEOPLE,bone,hand,head,actor};
