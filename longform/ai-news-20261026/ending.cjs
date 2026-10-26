const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),{once}=require('events');
const F=require('./film.cjs');
(async()=>{
 const B=__dirname,R=path.resolve(B,'../..'),vis=JSON.parse(fs.readFileSync(path.join(R,'shorts/laeko_host_demo/liam_lipsync_source.json'))).visemes;
 const canvas=F.createCanvas(1920,1080),o=path.join(B,'work','ending_landscape.mp4');
 const enc=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size','1920x1080','-framerate','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','22','-pix_fmt','yuv420p',o],{stdio:['pipe','inherit','inherit']});
 const closed=once(enc,'close');
 for(let f=0;f<180;f++){await F.ending(canvas,f/30,vis);if(f===70)fs.writeFileSync(path.join(B,'qa','ending_landscape.jpg'),canvas.toBuffer('image/jpeg',90));const a=canvas.getContext('2d').getImageData(0,0,1920,1080).data;if(!enc.stdin.write(Buffer.from(a.buffer,a.byteOffset,a.byteLength)))await once(enc.stdin,'drain');}
 enc.stdin.end();const [code]=await closed;if(code)throw Error('ending encode failed');
})();
