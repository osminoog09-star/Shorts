// Chigur V15 · physical blocking and semantic motion on the six existing Three.js sets.
// Revision is QA-only, not a film replacement. Loaded after V14 atmosphere and V12 overlay.
// No actors, movie frames, soundtracks, paid services or PIL drawing.
(() => {
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
  const easing=(t,start,end)=>smooth((t-start)/(end-start));
  const original=A.slice();

  // 01: a hand releases the physical coin and the metal rotates/settles.
  const coinScene=G[0];
  const looseCoin=coinScene.children.find(o=>o.type==='Group'&&o.position.y<0&&o.position.y>-3);
  A[0]=t=>{
    original[0](t);
    if(looseCoin){
      const fall=easing(t,1.5,4.5);
      looseCoin.rotation.z=.20*(1-fall)*Math.sin(11*t)+.08;
      looseCoin.rotation.y+=.18*Math.sin(t*1.5);
    }
  };

  // 02: real door moves, light changes. No mannequin or a fake actor's words.
  const hotel=G[1];
  let hotelDoor=null;
  hotel.traverse(n=>{
    if(n.isMesh&&n.geometry&&n.geometry.type==='ExtrudeGeometry'&&
       Math.abs(n.position.x+4.22)<.04&&Math.abs(n.position.z+2.6)<.04){
      hotelDoor=n;
    }
  });
  A[1]=t=>{
    original[1](t);
    const open=easing(t,1.0,4.6);
    if(hotelDoor)hotelDoor.rotation.y=Math.PI/2+.08+open*.66;
  };

  // 03: signal is a *moving* electronic trace; this is a stylized illustration,
  // not evidence that the identical device/beeps occur in the source movie.
  const instrument=G[2].children.find(o=>o.type==='Group');
  const tubes=[];
  if(instrument)instrument.traverse(n=>{
    if(n.isMesh&&n.geometry?.type==='TubeGeometry')tubes.push(n);
  });
  A[2]=t=>{
    original[2](t);
    for(const [i,n] of tubes.entries()){
      n.scale.y=1+.18*Math.sin(t*7+i*.7);
      if(n.material?.color)n.material.color.setHSL(.40,.42+.1*Math.sin(t*2),.65+.12*Math.sin(t*3));
    }
  };

  // 04: after the refusal, the glove visibly retreats and the coin stays put.
  // Only a symbolic bodyless arm: no invented film footage.
  const refusal=G[3],arm=refusal.children.find(n=>n.isGroup&&Math.abs(n.position.z-2.1)<.01);
  A[3]=t=>{
    original[3](t);
    if(arm){
      const p=easing(t,.8,5.0);
      arm.position.x=1.06+.92*p;
      arm.position.y=-.90+.35*p;
      arm.position.z=2.10+.1*p;
      arm.rotation.z=-.16*p;
    }
  };

  // 05: briefcase actually opens, then holds. Money is *not* presented as
  // footage of Carson offering this exact cash case.
  const caseGroup=G[4].children.find(n=>n.isGroup);
  const caseLid=caseGroup?.children.find(n=>n.isGroup);
  A[4]=t=>{
    original[4](t);
    if(caseLid)caseLid.rotation.x=-.22-.92*easing(t,.6,3.5);
  };

  // 06: traffic moves across the wet road. Symbolic epilogue only.
  const road=G[5],car=road.children.find(n=>n.isGroup);
  A[5]=t=>{
    original[5](t);
    if(car){
      car.position.z=-1.65+.36*t;
      car.position.x=-.2+.025*t;
    }
  };
  window.chigurV15Info={
    "kind":"editorial_preview_only",
    "frames":["coin_action","hotel_door_opens","device_trace","refusal_hand","case_lid","moving_car"],
    "contains_movie_footage":false,"contains_movie_audio":false,
    "requires_author_audio_proof":true
  };
})();
