// Chigur V12: deterministic 30fps prop motion, companion to stage_v11 and editorial V12 overlay.
// Animates physical objects, not the approved M1lash outro or film footage.
(() => {
  const original=A.slice();
  const coin=G[0].children.find(n=>n.type==="Group");
  const detector=G[2].children.find(n=>n.type==="Group");
  const trace=detector && detector.children.find(n=>
    n.geometry && n.geometry.type==="TubeGeometry" && n.material?.color?.getHex()===0x93ffb9);
  const car=G[5].children.find(n=>n.type==="Group");
  A[0]=t=>{
    original[0](t);
    if(coin)coin.rotation.y=-.12+t*.12;
  };
  A[1]=t=>{
    original[1](t);
    // Corridor: slow approach belongs to V11 camera, door remains slightly open.
  };
  A[2]=t=>{
    original[2](t);
    if(trace){
      trace.scale.y=1+.22*Math.sin(t*3.5);
      trace.material.color.setHex(Math.sin(t*5)>0?0x93ffb9:0x4bdd94);
    }
  };
  A[3]=t=>{original[3](t)};
  A[4]=t=>{original[4](t)};
  A[5]=t=>{
    original[5](t);
    if(car)car.position.z=-1.3+t*.19;
  };
})();