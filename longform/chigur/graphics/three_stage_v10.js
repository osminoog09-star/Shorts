// Chigur V10 — cinematic prop miniatures, 6 physical sets, no movie footage.
// Loaded AFTER three_stage_v7.js, replaces all visible V7 stage geometry.
// Three.js r128, deterministic t -> frame, filmic light, 3D forms over diagrams.
(() => {
  const pi=Math.PI;
  const mat=(color,rough=.62,metal=.06,more={})=>
    new THREE.MeshPhysicalMaterial({color,roughness:rough,metalness:metal,clearcoat:metal>.2?.5:.1,...more});
  const dark=mat(0x10131a,.72,.25),iron=mat(0x333840,.52,.7),black=mat(0x090c11,.55,.4),
    leather=mat(0x211813,.78,.06),linen=mat(0xcfbd95,.84),warm=mat(0xa76a3e,.53,.4),
    copper=mat(0xc68e4a,.35,.85),silver=mat(0xaab2b9,.22,.92),glass=mat(0x0c2632,.14,.25,{transparent:true,opacity:.74}),
    olive=mat(0x303729,.59,.11);
  const seed=(x)=>{const v=Math.sin(x*127.1+78.3)*43758.5453;return v-Math.floor(v)};
  function rounded(g,w,h,d,r,material,x=0,y=0,z=0){
    const r0=Math.min(w,h,r);
    const q=new THREE.Shape();q.moveTo(-w/2+r0,-h/2);
    q.lineTo(w/2-r0,-h/2);q.quadraticCurveTo(w/2,-h/2,w/2,-h/2+r0);
    q.lineTo(w/2,h/2-r0);q.quadraticCurveTo(w/2,h/2,w/2-r0,h/2);
    q.lineTo(-w/2+r0,h/2);q.quadraticCurveTo(-w/2,h/2,-w/2,h/2-r0);
    q.lineTo(-w/2,-h/2+r0);q.quadraticCurveTo(-w/2,-h/2,-w/2+r0,-h/2);
    const geom=new THREE.ExtrudeGeometry(q,{depth:Math.max(.012,d-2*r*.35),bevelEnabled:true,bevelSegments:3,steps:1,bevelThickness:r*.35,bevelSize:r*.35,curveSegments:6});
    geom.translate(0,0,-d/2+r*.35);
    return add(g,geom,material,x,y,z);
  }
  function beam(g,x,y,z,w,h,d,m){return box(g,x,y,z,w,h,d,m)}
  function light(g,col,energy,range,x,y,z){const l=new THREE.PointLight(col,energy,range,2);l.position.set(x,y,z);g.add(l);return l}
  function wire(g,points,r=.019,material=iron){const path=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));return add(g,new THREE.TubeGeometry(path,72,r,8,false),material)}
  function typography(g,str,w,h,x,y,z,color=0xf6e7bc){
    const can=document.createElement('canvas');can.width=512;can.height=128;
    const ctx=can.getContext('2d');ctx.clearRect(0,0,512,128);
    ctx.font='bold 75px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.shadowColor='rgba(255,190,90,.5)';ctx.shadowBlur=9;ctx.fillStyle='#'+color.toString(16).padStart(6,'0');
    ctx.fillText(str,256,64);
    const tex=new THREE.CanvasTexture(can);tex.encoding=THREE.sRGBEncoding;
    const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false}));
    p.position.set(x,y,z);g.add(p);return p;
  }
  function planks(g,y=-1.45,size=12){
    beam(g,0,y-.13,-.25,size,.25,size,mat(0x1e1715,.93));
    for(let i=0;i<12;i++){
      let z=-size/2+i*size/12;
      beam(g,0,y,z,size,.018,.008,mat(i%3?0x402e28:0x53372c,.8));
      for(let j=0;j<12;j++){
        const x=-size/2+j*1.04;
        const k=beam(g,x,y+.011,z+seed(i*27+j)*.4,.5,.001,.008,mat(0x5c4237,.95));
        k.rotation.y=seed(j*35+i)*.11;
      }
    }
  }
  function realisticCoin(g,x,y,z,r=.71){
    const group=new THREE.Group();group.position.set(x,y,z);g.add(group);
    cy(group,0,0,0,r,.11,copper);
    for(const sign of [-1,1]){
      const l=ring(group,0,sign*.062,0,r*.78,.019,silver);l.rotation.x=pi/2;
      const a=ring(group,0,sign*.063,0,r*.55,.016,copper);a.rotation.x=pi/2;
    }
    for(let n=0;n<92;n++){const a=n*2*pi/92;const bar=beam(group,Math.cos(a)*r*.985,0,Math.sin(a)*r*.985,.018,.115,.026,silver);bar.rotation.y=a}
    const relief=ball(group,0,.063,0,r*.22,copper);relief.scale.set(1,.09,.7);
    for(let n=0;n<10;n++){
      const a=n*2*pi/10;
      ball(group,Math.cos(a)*r*.40,.069,Math.sin(a)*r*.40,.025,silver).scale.set(1,.28,1);
    }
    return group;
  }
  function scene(i){const g=G[i];for(const child of [...g.children])g.remove(child);return g}
  S.background=new THREE.Color(0x070b12);S.fog=new THREE.FogExp2(0x0a0e16,.022);
  R.toneMappingExposure=.70;K.intensity=2.9;K.position.set(-2.5,5,5);B.intensity=1.7;B.position.set(4,2,1);
  // 1 — tight macro, coin on a scarred counter; its worn edge dominates the story.
  {
    const g=scene(0);planks(g,-1.45,13);
    const c=realisticCoin(g,-.65,-1.28,.54,.97);c.rotation.set(.01,-.28,.075);
    const check=rounded(g,2.8,.045,3.7,.08,linen,2.1,-1.37,-1.2);check.rotation.x=-pi/2;check.rotation.z=.15;
    for(let j=0;j<17;j++){const inkline=beam(g,2.2,-1.336,-2.72+j*.185,1.3,.002,.012,mat(0x676055,.8));inkline.rotation.y=.13}
    const cup=cy(g,-3.1,-1.14,-2.8,.38,.62,iron);
    ring(g,-3.1,-.80,-2.8,.38,.035,silver).rotation.x=pi/2;
    const curl=wire(g,[[-2.8,-.81,-2.8],[-2.57,-.74,-2.65],[-2.64,-1,-2.38]],.060,iron);
    light(g,0xffc282,2.6,7,-1.8,1,1.2);light(g,0x467bb9,1.9,8,3,1,-3);
    const nick=rounded(g,.66,.045,.25,.04,mat(0xd3c3aa,.91),-2.65,-1.37,1.6);nick.rotation.y=.35;
    A[0]=t=>{c.rotation.z=.075+.015*Math.sin(t*.7);C.fov=35;C.updateProjectionMatrix()};
  }
  // 2 — actual motel corridor, open door with light spill, ceiling fixtures and carpet.
  {
    const g=scene(1);
    beam(g,0,-1.62,-4,14,.12,23,mat(0x23242a,.97));
    beam(g,0,3.32,-4,14,.16,23,mat(0x151a22,.92));
    beam(g,0,.9,-12.2,14,6,.3,mat(0x232c35,.93));
    beam(g,-4.68,.9,-4,.23,6,23,mat(0x43505c,.91));
    beam(g,4.68,.9,-4,.23,6,23,mat(0x43505c,.91));
    beam(g,0,-1.49,-2.4,2.2,.03,17,mat(0x3c2625,.9));
    for(let i=0;i<5;i++){
      const z=-10+i*3.6;
      for(const x of [-4.48,4.48]){
        const panel=rounded(g,1.9,3.35,.11,.06,mat(0x3f2920,.8),x,-.18,z);
        panel.rotation.y=x>0?-pi/2:pi/2;
        for(let j=0;j<2;j++){let trim=rounded(g,1.38,1.08,.025,.03,mat(0x64422b,.72),x+(x>0?-.10:.10),-.31+j*1.28,z);trim.rotation.y=panel.rotation.y}
        const knob=ball(g,x+(x>0?-.15:.15),-.36,z+.63,.085,copper);
        beam(g,x,-.2,z-.95,.10,3.5,.11,silver);
      }
      const top=rounded(g,.49,.11,.37,.05,linen,-4.47,1.75,z);
      typography(g,String(100+i),.43,.16,-4.27,1.75,z,0xf4d4a0).rotation.y=pi/2;
    }
    const gdoor=rounded(g,1.85,3.33,.11,.05,mat(0x8a4d30,.74),-4.22,-.2,-2.6);
    gdoor.rotation.y=pi/2+.33;
    const bulb=light(g,0xffad57,5,10,-3.78,.8,-2.6);
    beam(g,-4.1,-1.47,-2.5,1.1,.008,2.65,mat(0xc99451,.24));
    for(let j=0;j<5;j++){const z=-10+j*3.6;light(g,0xf3d7a2,.75,4,0,2.9,z);rounded(g,1.0,.08,.34,.09,linen,0,3.1,z);}
    typography(g,"EXIT",.9,.4,0,2.47,-11.7,0xea4433);
    A[1]=t=>{gdoor.rotation.y=pi/2+.33+.02*Math.sin(t*.28);bulb.intensity=4.8+.15*Math.sin(t*.7)};
  }
  // 3 — close control box with proper sloped upper cover, knobs, screwheads, glowing trace.
  {
    const g=scene(2);planks(g,-1.5,12);
    const unit=new THREE.Group();unit.position.set(0,-.8,-.2);unit.rotation.y=-.13;g.add(unit);
    rounded(unit,4.5,1.48,2.8,.13,iron,0,0,0);
    rounded(unit,4.15,.09,2.5,.04,dark,0,.76,0);
    const dial=rounded(unit,2.64,.96,.12,.07,black,-.69,.19,1.47);
    const display=rounded(unit,2.39,.76,.02,.05,mat(0x163d2e,.15,.25,{emissive:0x0b3121,emissiveIntensity:.6}),-.69,.19,1.549);
    const linePts=[];
    for(let n=0;n<89;n++){const x=-1.76+n*2.12/88;linePts.push(new THREE.Vector3(x,.19+.16*Math.sin(n*.39)*Math.exp(-Math.abs(n-45)/45),1.565))}
    const trace=add(unit,new THREE.TubeGeometry(new THREE.CatmullRomCurve3(linePts),116,.010,6,false),new THREE.MeshBasicMaterial({color:0x91facc}));
    for(let n=0;n<7;n++)beam(unit,-1.73+n*.33,-.24,1.56,.009,.74,.004,mat(0x356b50,.3));
    for(let n=0;n<7;n++)beam(unit,-1.89,.55-n*.12,1.56,2.38,.006,.003,mat(0x295741,.4));
    for(let n=0;n<6;n++){
      const xx=.85+(n%2)*.63,yy=.49-Math.floor(n/2)*.36;
      let knob=cy(unit,xx,yy,1.5,.17,.16,dark);knob.rotation.x=pi/2;
      ring(unit,xx,yy,1.585,.146,.014,silver);
      beam(unit,xx+.07,yy+.06,1.60,.045,.02,.025,copper);
    }
    typography(unit,"SIGNAL",.7,.18,-1.0,.68,1.54,0xc5dcbd);
    for(let n=0;n<6;n++)ball(unit,-2.0+n*.8,.68,1.33,.037,silver);
    wire(g,[[1.92,-.61,1.4],[3,-.85,1.9],[3.3,-1.4,2.3],[4.4,-1.48,1]],.072,black);
    light(g,0x31c891,2.0,5,-1,.3,2);light(g,0xffbd75,2.8,8,-3,3,3);
    A[2]=t=>{unit.rotation.y=-.13+.018*Math.sin(t*.25)};
  }
  // 4 — absence, refusal: the untouched coin stays on counter while chair recedes.
  {
    const g=scene(3);planks(g,-1.45,13);
    const c=realisticCoin(g,-.55,-1.28,.9,.61);
    c.rotation.z=.025;
    const envelope=rounded(g,2.22,.025,1.55,.04,linen,1.1,-1.32,-.6);envelope.rotation.x=-pi/2;envelope.rotation.z=.24;
    const flap=wire(g,[[.25,-1.298,-.17],[1.3,-1.294,-1.05],[2.0,-1.298,-.13]],.012,mat(0x887961,.8));
    beam(g,0,.6,-5.0,12,5,.25,mat(0x262d37,.93));
    // Empty chair is the real subject; not a repeated macro of the coin.
    const chair=new THREE.Group();chair.position.set(2.45,-1.17,-3.4);chair.rotation.y=-.28;g.add(chair);
    rounded(chair,1.3,.18,1.35,.08,leather,0,.33,0);
    rounded(chair,1.42,1.68,.17,.12,leather,0,1.14,-.52);
    for(let x of [-.55,.55])beam(chair,x,-.29,0,.10,1.11,.1,iron);
    wire(chair,[[-.67,.1,0],[-.85,.65,-.13],[-.75,1.2,-.52]],.075,iron);
    wire(chair,[[.67,.1,0],[.85,.65,-.13],[.75,1.2,-.52]],.075,iron);
    light(g,0x79abd6,2.8,10,3,3,-3);light(g,0xffbd85,1.2,5,-3,2,3);
    A[3]=t=>{chair.rotation.y=-.28+.02*Math.sin(t*.25)};
  }
  // 5 — case, believable hardware: bevels, metal hinges, handles, tied stacks.
  {
    const g=scene(4);planks(g,-1.5,12);
    const caseG=new THREE.Group();caseG.position.set(0,-.9,.3);caseG.rotation.y=.12;g.add(caseG);
    rounded(caseG,4.52,.68,2.93,.20,leather,0,0,0);
    rounded(caseG,4.19,.53,2.61,.10,mat(0x101319,.8),0,.15,0);
    const lid=new THREE.Group();lid.position.set(0,.38,-1.43);caseG.add(lid);lid.rotation.x=-1.12;
    rounded(lid,4.53,.24,2.93,.15,leather,0,0,1.44);
    rounded(lid,4.1,.08,2.56,.09,mat(0x7c633f,.82),0,-.125,1.38);
    for(let j=0;j<3;j++)for(let k=0;k<2;k++){
      const x=-1.25+j*1.25,z=-.62+k*1.15;
      for(let n=0;n<15;n++){
        const bill=rounded(caseG,1.04,.008,.79,.025,linen,x,.43+n*.011,z);
        bill.rotation.y=(n%5-2)*.004;
      }
      beam(caseG,x,.61,z,.13,.043,.8,mat(0x788c65,.83));
    }
    for(let x of [-1.3,1.3]){
      rounded(caseG,.47,.32,.12,.04,copper,x,.0,1.52);
      rounded(caseG,.25,.08,.11,.02,black,x,.04,1.60);
      cy(caseG,x,.39,-1.44,.09,.10,silver);
    }
    wire(caseG,[[-.51,-.08,1.54],[-.49,-.22,1.83],[.49,-.22,1.83],[.51,-.08,1.54]],.078,black);
    for(let x of [-2.03,2.03])for(let z of [-1.21,1.21])ball(caseG,x,.04,z,.058,silver);
    light(g,0xf4b77a,3.2,8,-3,3,2);light(g,0x5ba0b4,1.9,10,3,1,-3);
    A[4]=t=>{lid.rotation.x=-1.12-.04*Math.cos(t*.35)};
  }
  // 6 — sculpted sedan shell, glazing, grill, proper wheels; wet asphalt at night.
  {
    const g=scene(5);
    beam(g,0,-1.56,-2,25,.12,32,mat(0x161b21,.24,.18));
    for(let z=-15;z<14;z+=3.0)beam(g,0,-1.49,z,.11,.01,1.32,linen);
    for(let x of [-5,5])for(let z=-15;z<14;z+=1.3){
      beam(g,x,-1.48,z,.08,.008,.49,mat(0x33404b,.9));
    }
    const car=new THREE.Group();car.position.set(-.2,-1,-1.3);car.rotation.y=-.17;g.add(car);
    const carpaint=mat(0x242d37,.22,.7,{clearcoat:1,clearcoatRoughness:.1});
    rounded(car,2.5,.55,4.33,.23,carpaint,0,0,0);
    rounded(car,2.54,.24,3.4,.12,carpaint,0,.14,.10);
    rounded(car,2.14,.73,2.30,.22,carpaint,0,.58,-.33);
    for(let side of [-1,1]){
      const w=rounded(car,.94,.42,.04,.06,glass,side*.63,.59,.59);
      w.rotation.y=side*.2;
      rounded(car,.09,.62,2.2,.06,carpaint,side*1.07,.48,-.4);
      for(let z of [-1.42,1.35]){
        const wheel=cy(car,side*1.27,-.27,z,.42,.23,black);wheel.rotation.z=pi/2;
        const hub=cy(car,side*1.396,-.27,z,.25,.018,silver);hub.rotation.z=pi/2;
        for(let a=0;a<5;a++){const ang=a*2*pi/5;ball(car,side*1.41,-.27+Math.sin(ang)*.14,z+Math.cos(ang)*.14,.04,dark);}
      }
      rounded(car,.39,.16,.11,.05,mat(0xffdc94,.2,.3,{emissive:0xf5bc72,emissiveIntensity:1.3}),side*.88,.02,2.18);
      rounded(car,.34,.18,.075,.04,mat(0xa02014,.4,.3,{emissive:0x600e09,emissiveIntensity:.4}),side*.86,.02,-2.19);
      rounded(car,.39,.04,.13,.04,silver,side*.62,-.08,2.22);
    }
    rounded(car,1.18,.28,.10,.06,black,0,-.14,2.26);
    for(let n=0;n<7;n++)beam(car,-.45+n*.15,-.13,2.33,.04,.19,.04,silver);
    rounded(car,1.65,.035,.23,.04,silver,0,.26,1.25);
    rounded(car,.89,.035,.28,.04,silver,0,.25,-1.8);
    wire(car,[[-1.1,.40,.55],[-.95,.9,.3],[.95,.9,.3],[1.1,.4,.55]],.018,silver);
    const street=light(g,0xffb35d,5.1,13,3.5,4.3,-1.2);
    const pole=cy(g,4.2,1.4,-1,.095,5.6,iron);
    beam(g,3.5,4.15,-1,1.6,.13,.17,iron);
    rounded(g,.52,.11,.48,.03,linen,2.8,4.06,-1);
    light(g,0x2e78b9,2.2,13,-4,2,-5);
    for(let i=0;i<7;i++){const z=-9+i*2.7;beam(g,7,-1.18,z,1,.62,.12,iron)}
    A[5]=t=>{car.position.z=-1.3+t*.06;street.intensity=5+.1*Math.sin(t*.7)};
  }
  // Camera: six distinct angles, not six equally lit mockup diagrams.
  const q=[
    [[1.65,1.3,4.7],[-.43,-1.12,.25]],
    [[-1.4,.3,5.0],[-1,-.4,-5.1]],
    [[1.1,1.2,4.35],[-.45,-.2,.75]],
    [[-.6,1.32,4.4],[1.0,-.25,-1.75]],
    [[1.6,1.24,5.2],[0,-.55,.35]],
    [[2.4,.82,6.55],[-.2,-.66,-1.3]],
  ];
  q.forEach((p,i)=>poses[i]=p);
  const baseFrame=window.frame;
  window.frame=(T)=>{
    const i=Math.min(5,Math.floor(Math.max(0,T)/6)),t=T-i*6;
    baseFrame(T); // visibility, lighting, camera easing in canonical timeline
    C.position.x += (i===0?-.045:.025)*t;
    C.position.z -= t*.025;
    C.lookAt(...poses[i][1]);
    S.fog=new THREE.FogExp2(i===1?0x171b23:i===5?0x0b111a:0x080b12,i===1?.052:i===5?.036:.014);
    R.render(S,C);
    return R.domElement.toDataURL('image/png');
  };
  window.ready=true;window.frame(0);
})();