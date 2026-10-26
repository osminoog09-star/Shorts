const fs=require('fs'),path=require('path'),{createCanvas}=require('@napi-rs/canvas'),F=require('./film.cjs');
(async()=>{
 const B=__dirname;fs.mkdirSync(path.join(B,'thumbnails'),{recursive:true});
 const host=await F.hostImage(.7,'talk',1);
 const variants=[['КТО','ПЕРЕГНУЛ?','4 НОВОСТИ ОБ ИИ','#c2d4bf'],['ЛИМИТ','КОНЧИЛСЯ','KIMI · ПЕРЕСЧЁТ КВОТЫ','#e5c28b'],['КТО ДАЛ','ЕМУ КЛЮЧ?','БЕЗОПАСНОСТЬ ИИ','#b8cfcd']];
 for(let v=0;v<3;v++){
  const [a,b,strap,col]=variants[v],cv=createCanvas(1280,720),c=cv.getContext('2d');
  c.fillStyle='#eee4cc';c.fillRect(0,0,1280,720);
  for(let k=0;k<1300;k++){c.fillStyle=k%2?'#e1d5ba':'#f8efd9';c.fillRect(k*421%1280,k*173%720,2,1);}
  c.save();c.translate(450,358);c.rotate(-.027);c.shadowColor='#70664b70';c.shadowBlur=15;c.shadowOffsetY=10;c.fillStyle=col;c.beginPath();c.moveTo(-420,-280);c.lineTo(410,-291);c.lineTo(426,260);c.lineTo(-416,280);c.closePath();c.fill();c.restore();
  c.textBaseline='middle';c.fillStyle='#302c24';c.font='900 100px DejaVu Sans';c.fillText(a,74,220);c.fillText(b,74,340);
  c.fillStyle='#a34431';c.font='bold 28px DejaVu Sans';c.fillText(strap,76,458);
  c.fillStyle='#397b78';c.font='bold 29px DejaVu Sans';c.fillText('M1LASH · 26.10.2026',76,60);
  c.drawImage(host,905,192,328,388);
  if(v===0){for(let i=0;i<4;i++){c.fillStyle=['#397b78','#a34431','#3f5e7d','#b38331'][i];c.fillRect(75+i*173,550,145,72);c.fillStyle='#fff8e6';c.font='900 29px DejaVu Sans';c.fillText(['25%','ИИ?','ДОСТУП','ИСК'][i],88+i*173,586);}}
  if(v===1){c.fillStyle='#397b78';c.fillRect(75,545,680,53);c.fillStyle='#eee4cc';c.fillRect(245,552,500,39);c.fillStyle='#302c24';c.font='bold 24px DejaVu Sans';c.fillText('ОБЪЯВЛЕНИЕ КОМПАНИИ',75,644);}
  if(v===2){c.strokeStyle='#397b78';c.lineWidth=14;c.beginPath();c.arc(170,570,42,Math.PI,0);c.stroke();c.fillStyle='#d8b753';c.fillRect(119,570,102,76);c.fillStyle='#302c24';c.fillRect(164,587,12,35);c.font='bold 30px DejaVu Sans';c.fillText('ПРОСЬБА ≠ ЗАЩИТА',267,609);}
  fs.writeFileSync(path.join(B,'thumbnails',`variant_${v+1}.jpg`),cv.toBuffer('image/jpeg',93));
 }
})();
