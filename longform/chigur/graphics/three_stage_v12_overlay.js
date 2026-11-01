// Chigur V12 editorial 2.5D lens OVER actual Three.js V11 scenes.
// Three.js renders all physical props; overlay adds cinematic compositing,
// safe kinetic captions and deterministic film grain — NOT flat title cards.
(() => {
  const base=window.frame;
  const canvas=document.createElement('canvas');
  canvas.width=960;canvas.height=540;
  const ctx=canvas.getContext('2d',{alpha:false});
  const titles=[
    {a:"КТО",b:"ВЫБИРАЕТ?",side:"right",accent:"#e4af70",chapter:"МОНЕТА",unit:"01"},
    {a:"СЛЫШНО",b:"ТИШИНУ",side:"right",accent:"#d4ae7c",chapter:"ГОСТИНИЦА",unit:"02"},
    {a:"ЗВУК",b:"ВЫДАЁТ",side:"right",accent:"#77e2b3",chapter:"СИГНАЛ",unit:"03"},
    {a:"ОНА",b:"ОТКАЗАЛАСЬ",side:"left",accent:"#e4af70",chapter:"ВЫБОР",unit:"04"},
    {a:"ЦЕНА",b:"МОЛЧАНИЯ",side:"right",accent:"#e7bc88",chapter:"ПОСЛЕДСТВИЯ",unit:"05"},
    {a:"УГРОЗА",b:"БЛИЖЕ",side:"right",accent:"#88c7e8",chapter:"ПОГОНЯ",unit:"06"},
  ];
  function line(x,y,w,h,color,alpha=1){
    ctx.globalAlpha=alpha;ctx.fillStyle=color;ctx.fillRect(x,y,w,h);ctx.globalAlpha=1;
  }
  function grain(t) {
    // Low-value, seeded lightweight overlay. No non-determinism in output frames.
    const n=Math.floor(t*30+1);
    ctx.globalAlpha=.085;
    ctx.fillStyle='#d9d5c8';
    for(let j=0;j<220;j++){
      const x=((j*97+n*29)%953),y=((j*193+n*11)%537);
      ctx.fillRect(x,y,1,1);
    }
    ctx.globalAlpha=1;
  }
  function caption(t){
    const i=Math.max(0,Math.min(5,Math.floor(t/6)));
    const info=titles[i],local=t-i*6;
    const right=info.side==="right";
    const x=right?918:48;
    const align=right?'right':'left';
    ctx.textAlign=align;ctx.textBaseline='alphabetic';
    const reveal=Math.min(1,Math.max(0,local/.50)),slide=(1-reveal)*22;
    const a=Math.min(1,Math.max(0,local/.4));
    ctx.globalAlpha=a;
    ctx.shadowBlur=14;ctx.shadowColor='rgba(0,0,0,.86)';
    ctx.font='900 48px "DejaVu Sans",sans-serif';
    ctx.fillStyle='#faf6ee';
    ctx.fillText(info.a,x+(right?slide:-slide),108);
    ctx.fillStyle=info.accent;
    ctx.fillText(info.b,x+(right?slide:-slide),165);
    ctx.shadowBlur=0;
    const w=right?356:348;
    line(right?x-w:x,188,w,2,'#f6e4bd',.45);
    ctx.globalAlpha=1;
    // Dedicated production slate is small, not the main composition.
    ctx.textAlign='left';ctx.font='700 17px "DejaVu Sans",sans-serif';
    ctx.fillStyle='#e3d2b4';ctx.fillText(info.unit+'  /  '+info.chapter,46,482);
    line(46,501,128,3,info.accent,.75);
    line(46,501,128*Math.max(0,Math.min(1,local/6)),3,'#ffffff',.84);
  }
  function lens(t){
    const dark=ctx.createRadialGradient(480,254,85,480,265,582);
    dark.addColorStop(0,'rgba(4,7,12,0)');
    dark.addColorStop(.65,'rgba(3,6,11,.16)');
    dark.addColorStop(1,'rgba(2,3,7,.75)');
    ctx.fillStyle=dark;ctx.fillRect(0,0,960,540);
    const top=ctx.createLinearGradient(0,0,0,208);
    top.addColorStop(0,'rgba(4,6,11,.65)');
    top.addColorStop(1,'rgba(4,6,11,0)');
    ctx.fillStyle=top;ctx.fillRect(0,0,960,208);
  }
  window.frame=(t)=>{
    base(t);
    ctx.clearRect(0,0,960,540);
    ctx.drawImage(R.domElement,0,0,960,540);
    lens(t);caption(t);grain(t);
    return canvas.toDataURL('image/png');
  };
  window.ready=true;window.frame(0);
})();