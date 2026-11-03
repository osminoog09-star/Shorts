// Chigur V22: deterministic, story-specific physical action preflight.
// Load AFTER three_stage_v21_editorial.js. Existing shots preserved; no film footage.
// Only original Three.js geometry and camera effects, no PIL draw scene.
(() => {
  const smooth = (x) => {
    x = Math.max(0, Math.min(1, x));
    return x*x*(3-2*x);
  };
  const ramp = (t,a,b) => smooth((t-a)/(b-a));
  const original=A.slice();

  // COIN: a visibly spinning/settling physical object, not a title card.
  const coin=G[0].children.find(n=>n.isGroup && n.position.y < 0 && n.position.y > -3);
  A[0]=(t)=>{
    original[0](t);
    if(coin){
      const settle=ramp(t,2.1,4.9);
      coin.position.set(-.65,-1.28+.19*(1-settle)*Math.abs(Math.sin(t*4.2)),.54);
      coin.rotation.set(.05+.60*(1-settle)*Math.abs(Math.sin(t*5.1)), -.28+3.0*t*(1-settle), .06+.15*(1-settle)*Math.sin(t*8));
    }
  };

  // MOTEL DOOR: swing into a growing real amber pool of light.
  const door=G[1].children.find(n=>n.isMesh && n.geometry?.type==="ExtrudeGeometry" &&
    Math.abs(n.position.x+4.22)<.04 && Math.abs(n.position.z+2.6)<.04);
  const poolLight=new THREE.PointLight(0xffb46c,1.1,7,2);
  poolLight.position.set(-4.1,.1,-2.3);
  G[1].add(poolLight);
  A[1]=(t)=>{
    original[1](t);
    const open=ramp(t,.55,4.2);
    if(door)door.rotation.y=Math.PI/2+.10+.94*open;
    poolLight.intensity=.6+2.8*open;
  };

  // DETECTOR: physical LED streak racing toward the right edge of the display.
  const unit=G[2].children.find(n=>n.isGroup);
  const leds=[];
  if(unit){
    for(let i=0;i<12;i++){
      const dot=new THREE.Mesh(
        new THREE.SphereGeometry(.039,10,8),
        new THREE.MeshBasicMaterial({color:0x0f3d30,transparent:true,opacity:.4})
      );
      dot.position.set(-1.73+i*.174,.18,1.765);
      unit.add(dot);leds.push(dot);
    }
    const ledglow=new THREE.PointLight(0x35ff9c,1.1,2);
    ledglow.position.set(-.8,.2,2.01);unit.add(ledglow);
  }
  A[2]=(t)=>{
    original[2](t);
    const head=(Math.floor(t*4.0)%12);
    leds.forEach((dot,i)=>{
      const on=Math.abs(i-head)<=1;
      dot.material.color.setHex(on?0x76ffb7:0x184431);
      dot.material.opacity=on?1:.31;
      dot.scale.setScalar(on?1.65:1);
    });
  };

  // REFUSAL: withdraw the chair into shadow; coin left untouched.
  const chair=G[3].children.find(n=>n.isGroup && n.position.z < -2.4 && n.position.z > -3.7);
  A[3]=(t)=>{
    original[3](t);
    if(chair){
      const retreat=ramp(t,.7,4.8);
      chair.position.set(1.5+1.05*retreat,-1.17,-3.0-.12*retreat);
      chair.rotation.y=-.28-.30*retreat;
    }
  };

  // BRIEFCASE: the offer snaps shut; use real existing hinge.
  const caseBox=G[4].children.find(n=>n.isGroup);
  const caseLid=caseBox?.children.find(n=>n.isGroup);
  A[4]=(t)=>{
    original[4](t);
    if(caseLid){
      const shut=ramp(t,1.0,3.35);
      caseLid.rotation.x=-1.15+.90*shut;
    }
  };

  // ROAD: car actually approaches into a growing headlamp-lit area.
  const car=G[5].children.find(n=>n.isGroup);
  const edgeLight=new THREE.PointLight(0xe1b782,.4,7,2);
  edgeLight.position.set(0,.3,1.7);G[5].add(edgeLight);
  A[5]=(t)=>{
    original[5](t);
    const approach=ramp(t,.4,5.5);
    if(car){
      car.position.set(-.2+.27*approach,-1,-1.65+1.55*approach);
      car.rotation.y=-.17+.1*approach;
    }
    edgeLight.intensity=.4+2.3*approach;
  };
  window.chigurV22ActionReady=true;
})();


// V22 preflight-only camera override. Scoped to frameV22; V21 remains untouched.
(() => {
  const original=R.render.bind(R);
  R.render=(scene,camera)=>{
    const shot=window.__chigurV22ActiveShot;
    if(shot && scene===S && camera===C){
      const id=Number(shot.scene_id);
      const t=Number(window.__chigurV22ActiveTime)||0;
      if(id===1){ // make the open door a subject, not a blank distant hallway
        C.position.set(-.45,.9,6.1-.035*t);
        C.fov=41;C.updateProjectionMatrix();
        C.lookAt(-3.35,-.35,-2.85);
      } else if(id===3){ // show chair retreating and untouched coin together
        C.position.set(1.6,2.0,6.6-.02*t);
        C.fov=40;C.updateProjectionMatrix();
        C.lookAt(.55,-.83,-.65);
      } else if(id===4){ // keep cash, hinge, lid and handle inside frame
        C.position.set(2.0,2.45,7.75-.04*t);
        C.fov=42;C.updateProjectionMatrix();
        C.lookAt(0,-.25,.25);
      } else if(id===5){ // NO cropped toy bumper, show road, side and whole car
        C.position.set(2.95,1.7,8.5-.04*t);
        C.fov=42;C.updateProjectionMatrix();
        C.lookAt(0,-.48,-.45);
      }
    }
    return original(scene,camera);
  };
  window.frameV22=(shot,t,format="image/png")=>{
    window.__chigurV22ActiveShot=shot;
    window.__chigurV22ActiveTime=t;
    try{return window.frameV21(shot,t,format)}
    finally{window.__chigurV22ActiveShot=null;window.__chigurV22ActiveTime=null}
  };
  window.chigurV22CameraReady=true;
})();
