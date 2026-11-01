// Chigur V14: physical story accents for three weakest V12 frames.
// No downloaded models, no generated movie frames, deterministic Three.js only.
(() => {
  const pm=(c,rough=.7,metal=.08)=>new THREE.MeshPhysicalMaterial({color:c,roughness:rough,metalness:metal});
  const silk=pm(0x11151b,.76),skin=pm(0x1e1f21,.80),stone=pm(0x24282b,.9),
        amber=pm(0xb87e4b,.4,.32),wet=pm(0x25313d,.26,.3);
  function block(g,x,y,z,w,h,d,m){const n=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);n.position.set(x,y,z);n.castShadow=true;n.receiveShadow=true;g.add(n);return n}
  function sphere(g,x,y,z,r,m){const n=new THREE.Mesh(new THREE.SphereGeometry(r,18,14),m);n.position.set(x,y,z);n.castShadow=true;g.add(n);return n}
  function rod(g,xyz,rad,len,m,dir){const n=new THREE.Mesh(new THREE.CylinderGeometry(rad*.72,rad,len,16),m);
    n.position.set(...xyz);if(dir)n.rotation.set(...dir);n.castShadow=true;g.add(n);return n;}
  function point(g,c,power,r,x,y,z){const n=new THREE.PointLight(c,power,r,2);n.position.set(x,y,z);g.add(n);}
  // 2 — improve hotel corridor: trim, carpet seams, practical wall-lamps,
  // a distant silhouette in doorway (no explicit film actor/face).
  {
    const g=G[1];
    for(let k=0;k<18;k++){
      const z=-13+k*1.2;
      block(g,0,-1.455,z,2.08,.013,.014,pm(0x70514e,.9));
      block(g,-1.11,-1.455,z,0.025,.014,1.18,pm(0x65514b,.8));
      block(g,1.11,-1.455,z,.025,.014,1.18,pm(0x65514b,.8));
    }
    for(let x of [-4.38,4.38])for(let z of [-8.8,-3.9,1.0]){
      block(g,x,1.67,z,.15,.34,.25,amber);
      sphere(g,x+(x<0?.15:-.15),1.67,z,.10,pm(0xffcc82,.2));
      point(g,0xe6a365,.52,4,x+(x<0?.22:-.22),1.64,z);
    }

    // No mannequin. A suggestive, soft shadow moves from the partly open door.
    // Projection is a 3D floor plane with a radial soft shadow, not a flat title card.
    const can=document.createElement('canvas');can.width=256;can.height=256;
    const cx=can.getContext('2d');
    const grd=cx.createRadialGradient(128,128,16,128,128,126);
    grd.addColorStop(0,'rgba(1,2,4,.57)');grd.addColorStop(.58,'rgba(1,2,4,.27)');
    grd.addColorStop(1,'rgba(1,2,4,0)');
    cx.fillStyle=grd;cx.fillRect(0,0,256,256);
    const tex=new THREE.CanvasTexture(can);
    const shadow=new THREE.Mesh(new THREE.PlaneGeometry(1.45,4.6),
      new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2}));
    shadow.rotation.x=-Math.PI/2;shadow.rotation.z=.28;shadow.position.set(-3.50,-1.424,-2.5);
    g.add(shadow);
    point(g,0xedb76f,.95,4,-4.05,.35,-3.15);
    const base=A[1];A[1]=t=>{base(t);shadow.scale.y=1+.18*Math.min(t/6,1);
      shadow.material.opacity=.92+.08*Math.sin(t*.3)};
  }
  // 4 — a gloved arm retreats from the coin: actual action of *refusing*.
  // Keep the person out of shot; no uncanny faces or mannequin closeups.
  {
    const g=G[3];const hand=new THREE.Group();hand.position.set(1.06,-.90,2.1);g.add(hand);
    const arm=rod(hand,[-.55,.22,.22],.18,1.15,silk,[0,0,1.03]);
    const wrist=sphere(hand,.03,-.11,0,.22,skin);wrist.scale.set(1.35,.42,.85);
    for(let i=0;i<4;i++){
      const f=rod(hand,[.25+i*.10,-.22,.03+i*.032],.044,.43-(i===3?.11:0),skin,[.18,.16,1.1]);
      sphere(hand,.39+i*.1,-.34,.03+i*.032,.06,skin);
    }
    rod(hand,[.05,-.33,-.14],.063,.35,skin,[.3,.7,-.6]);
    point(g,0x9bb7d0,1.3,5,2.1,.75,2.7);
    poses[3]=[[2.25,1.3,5.15],[.25,-.92,.45]];
    const base=A[3];A[3]=t=>{base(t);
      const retreat=Math.min(1,Math.max(0,(t-.45)/4.3));hand.position.x=1.06+1.05*retreat;hand.position.y=-.90+.31*retreat;
      hand.rotation.y=-.08-.3*retreat;};
  }
  // 6 — wet road and street atmosphere, headlight beam and distant motel windows.
  {
    const g=G[5];
    for(let i=0;i<38;i++){
      const z=-12+(i%19)*1.5,x=((i*37)%17-8)*.48;
      block(g,x,-1.488,z,.10,.005,.4,wet).rotation.y=(i%5-2)*.08;
    }
    for(let side of [-1,1])for(let i=0;i<4;i++){
      const z=-14+i*5.5;
      block(g,side*8,1.0,z,2.4,4.6,.3,stone);
      for(let y=0;y<2;y++){
        const pane=block(g,side*7.86,.15+y*1.45,z+(i%2?.6:-.5),.035,.67,.43,pm(0x6b5733,.27,.22));
        pane.rotation.y=side*1.57;
        point(g,0xffab52,.28,4,side*7.45,.6+y*1.45,z);
      }
    }
    const haze=new THREE.Points(
      new THREE.BufferGeometry(),
      new THREE.PointsMaterial({color:0xaac6d6,size:.035,transparent:true,opacity:.22,depthWrite:false})
    );
    const count=240,pos=new Float32Array(count*3);
    for(let i=0;i<count;i++){const u=(Math.sin(i*91.73)*45371.1)%1;const v=(Math.sin(i*42.21)*19577.9)%1;
      pos[i*3]=((i*47)%31-15)*.50;pos[i*3+1]=.1+((i*29)%37)*.11;pos[i*3+2]=-9+((i*59)%47)*.37;}
    haze.geometry.setAttribute('position',new THREE.BufferAttribute(pos,3));g.add(haze);
    const base=A[5];A[5]=t=>{base(t);haze.position.z=-.12*t};
  }
})();