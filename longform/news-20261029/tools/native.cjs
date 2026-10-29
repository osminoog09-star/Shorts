const fs=require('fs'),vm=require('vm'),path=require('path');
const {createCanvas,loadImage,GlobalFonts,Image}=require('@napi-rs/canvas');
const root=path.resolve(__dirname,'..');process.chdir(root);GlobalFonts.registerFromPath('assets/DejaVuSans.ttf','News Sans');
const canvas=createCanvas(1920,1080),sandbox={console,Math,Image,window:null,document:{getElementById:()=>canvas,fonts:{add(){}}},FontFace:class{async load(){return this}},gsap:{timeline:()=>({addLabel(){},fromTo(){}})},OM:{clock(){},region(){}}};sandbox.window=sandbox;
let code=fs.readFileSync('film.js','utf8').replace(/a.src=`assets\/host\/\$\{p\}_\$\{i\}.svg`/,'a.src=requirePath+`/assets/host/${p}_${i}.svg`');code=code.replace("a.src='materials/'+f","a.src=requirePath+'/materials/'+f");sandbox.requirePath=root;vm.createContext(sandbox);vm.runInContext(fs.readFileSync('data.js','utf8'),sandbox);vm.runInContext(code,sandbox);
module.exports={sandbox,canvas,root,fs};
if(require.main===module){setTimeout(()=>{let times=process.argv.slice(2).map(Number);if(!times.length)times=[2,100,300,500,700,900,1100,1300];for(const t of times){sandbox.renderAt(t);fs.writeFileSync(`out/still_${t}.png`,canvas.toBuffer('image/png'));}console.log('saved',times)},1000)}
