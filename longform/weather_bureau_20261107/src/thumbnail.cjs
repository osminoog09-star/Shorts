'use strict';
const fs=require('node:fs'),path=require('node:path');
const A=require('./art.cjs'),{actor}=require('./actors.cjs'),{OUT,makeCanvas}=require('./render.cjs');
const {rect,path:drawPath,text,line,weatherJar,P,INK}=A;
(async()=>{
 const {cv,c}=makeCanvas();c.drawImage(A.background('street'),0,0,1280,720);
 rect(c,0,0,1280,720,'rgba(27,49,56,.32)',null);
 actor(c,'hero',330,1100,2.15,'point','surprise',2,{look:1});
 weatherJar(c,970,452,1.65,true);
 c.save();c.translate(1010,620);c.rotate(-.12);rect(c,-163,-37,326,74,P.cream,INK,4);text(c,'ПРОДАНО',0,16,49,'#a64e41','Arial','center');c.restore();
 c.save();c.font='bold 72px Arial';c.textAlign='left';c.lineJoin='round';c.lineWidth=14;c.strokeStyle=INK;c.fillStyle=P.cream;
 for(const [s,x,y] of [['ТВОЙ ДОЖДЬ',580,105],['ПРОДАЛИ',580,190]]){c.strokeText(s,x,y);c.fillText(s,x,y)}c.restore();
 drawPath(c,'M780 380 Q685 410 625 520 L655 515 L620 560 L610 508 L629 520 Q675 405 774 364 Z','#a4d0cf',INK,3);
 const dest=path.join(OUT,'thumbnail.png');fs.writeFileSync(dest,await cv.encode('png'));console.log(dest);
})().catch(e=>{console.error(e);process.exit(1)});
