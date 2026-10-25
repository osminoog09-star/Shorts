// Native Canvas2D export: no browser service, no remotely running workflow.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),{once}=require('events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const B=__dirname,canvas=createCanvas(1080,1920),host={style:{}};
global.window={};global.document={getElementById:id=>id==='film'?canvas:host};
require('./native-bundle.cjs');
(async()=>{
 const id=process.argv[2],e=JSON.parse(fs.readFileSync(path.join(B,'episodes.json'))).find(e=>e.id===id),O=path.join(B,'work',id);
 const timeline=JSON.parse(fs.readFileSync(path.join(O,'timeline.json')));const visPath=path.join(O,'visemes.json');const vis=fs.existsSync(visPath)?JSON.parse(fs.readFileSync(visPath)).visemes:'';
 window.configure(e,timeline,vis);const frames=Math.ceil(timeline.at(-1).end*30);
 if(process.env.PREVIEW_ONLY){const sc=Number(process.env.PREVIEW_SCENE||0),tt=timeline[sc];window.renderFrame(Math.floor((tt.start+(tt.end-tt.start)*.5)*30));fs.writeFileSync(path.join(O,`preview_${sc}.png`),canvas.toBuffer('image/png'));return;}
 const enc=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size','1080x1920','-framerate','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p',path.join(O,'silent.mp4')],{stdio:['pipe','inherit','inherit']});const closed=once(enc,'close');
 const starts=timeline.map(s=>Math.floor((s.start+(s.end-s.start)*.5)*30));
 for(let f=0;f<frames;f++){
  window.renderFrame(f);
  if(process.env.PREVIEW_ONLY){if(f===starts[Number(process.env.PREVIEW_SCENE||0)]){fs.writeFileSync(path.join(O,'native_preview.png'),canvas.toBuffer('image/png'));enc.stdin.end();enc.kill();return;}continue;}
  const rgba=canvas.getContext('2d').getImageData(0,0,1080,1920).data;
  if(!enc.stdin.write(Buffer.from(rgba.buffer,rgba.byteOffset,rgba.byteLength)))await once(enc.stdin,'drain');
  if(f%180===0)console.log(id,f,'/',frames);
 }
 enc.stdin.end();const [code]=await closed;if(code!==0)throw Error('ffmpeg '+code);
 fs.writeFileSync(path.join(O,'render.json'),JSON.stringify({frames,fps:30,width:1080,height:1920,renderer:'native Canvas2D',bodyHost:false,outroHost:'unchanged approved video with original visemes',style:e.style},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
