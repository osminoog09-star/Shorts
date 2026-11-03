// Chigur V21: deterministic editorial camera and typography over authored Three.js physical sets.
// Visual reconstruction only: NO film frames, actor voice or source movie audio here.
// Run after three_stage_v7/v11/v14, v12_motion, and v15_actions. No PIL scene drawing.
(() => {
 const base=window.frame;
 const canvas=document.createElement('canvas');
 canvas.width=1280;canvas.height=720;
 const ctx=canvas.getContext('2d',{alpha:false});
 R.setSize(1280,720,false);C.aspect=1280/720;C.updateProjectionMatrix();
 R.toneMappingExposure=.85;
 S.add(new THREE.AmbientLight(0xb4c9ea,.19));
 const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
 function split(txt,limit=25){
   const words=String(txt).split(' '),out=[];let row='';
   for(const w of words){if((row+' '+w).trim().length>limit&&row){out.push(row);row=w}else row=(row+' '+w).trim()}
   if(row)out.push(row);
   return out.slice(0,2);
 }
 window.frameV21=(shot,seconds,format='image/png')=>{
   const scene=shot.scene_id,phase=Math.max(.15,Math.min(5.8,seconds));
   base(scene*6+phase);
   // The V14 hand read as a sausage/mannequin limb in the real contact sheet.
   // Hide that theatrical prop and tell refusal by a chair sliding away.
   if(scene===3){
     const hand=G[3].children.find(n=>n.isGroup&&Math.abs(n.position.z-2.1)<.01);
     if(hand)hand.visible=false;
     const chair=G[3].children.find(n=>n.isGroup&&Math.abs(n.position.z+3.4)<.15);
     if(chair){const away=Math.max(0,Math.min(1,seconds/5));chair.position.x=2.45+.65*away;chair.rotation.y=-.28-.28*away;}
   }
   const v=Number(shot.index||0);
   const dx=(v%5-2)*.26,dy=((v*7)%5-2)*.12,dz=(v%4)*.28;
   // Real 28-window coverage cannot be a rerun of the same 6 centered shots.
   // Use alternating wide/medium/detail framings and asymmetric emphasis.
   const detail=(v%3===1),macro=(v%5===2);
   if(detail){C.fov=31;C.updateProjectionMatrix()}
   else if(macro){C.fov=27;C.updateProjectionMatrix()}
   else {C.fov=36;C.updateProjectionMatrix()}
   C.position.x+=dx+.085*Math.sin(seconds*.36);
   C.position.y+=dy;C.position.z+=dz-(.055+.015*(v%3))*seconds;
   const targ=poses[scene][1];C.lookAt(targ[0]+dx*.18,targ[1],targ[2]);
   R.toneMappingExposure=scene===5?.70:scene===3?.87:(scene===2||scene===1)?1.03:.91;
   // Noir road: headlights and silhouette carry the shot; no toy-car glamour angle.
   if(scene===5){
     C.position.set((v%2?-.85:1.50)+.07*seconds,.36+(v%3)*.2,5.9-.10*seconds);
     C.lookAt(-.15,-1.18,-1.35);
     S.fog=new THREE.FogExp2(0x08101b,.065);
   }
   R.render(S,C);
   ctx.clearRect(0,0,1280,720);ctx.drawImage(R.domElement,0,0,1280,720);
   let veil=ctx.createLinearGradient(0,0,0,225);
   veil.addColorStop(0,'rgba(2,6,12,.70)');
   veil.addColorStop(.65,'rgba(2,6,12,.15)');
   veil.addColorStop(1,'rgba(2,6,12,0)');
   ctx.fillStyle=veil;ctx.fillRect(0,0,1280,225);
   let bot=ctx.createLinearGradient(0,550,0,720);
   bot.addColorStop(0,'rgba(2,6,12,0)');
   bot.addColorStop(1,'rgba(2,6,12,.52)');
   ctx.fillStyle=bot;ctx.fillRect(0,550,1280,170);
   const progress=smooth(seconds/Math.max(.2,shot.seconds));
   ctx.save();ctx.textAlign='left';ctx.textBaseline='top';
   ctx.globalAlpha=smooth(seconds/.45);
   ctx.shadowColor='rgba(0,0,0,.65)';ctx.shadowBlur=15;
   ctx.fillStyle='#f8f4ea';ctx.font='900 46px "DejaVu Sans",sans-serif';
   const head=(shot.chapter_title||shot.creative_action||'').toLocaleUpperCase('ru-RU');
   const rows=split(head);
   rows.forEach((line,k)=>{ctx.fillStyle=k===0?'#f8f3e9':'#e5aa67';ctx.fillText(line,64,46+k*54)});
   ctx.globalAlpha=.7;ctx.shadowBlur=0;ctx.fillStyle='#e1ab6f';
   ctx.fillRect(64,48+rows.length*54,330*progress,3);
   ctx.font='700 19px "DejaVu Sans",sans-serif';ctx.fillStyle='#d5cbbd';
   ctx.fillText('КИНОРАЗБОР  /  ВИЗУАЛЬНАЯ РЕКОНСТРУКЦИЯ',64,688);
   ctx.restore();
   return canvas.toDataURL(format,format==='image/jpeg'?.90:undefined);
 };
 window.chigurV21Ready=true;
})();
