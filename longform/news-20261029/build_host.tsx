import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {Narrator2} from '../../studio/src/Narrator2';
import fs from 'node:fs';
fs.mkdirSync('assets/host',{recursive:true});
for(const pose of ['talk','point','facepalm','shock','shrug','laugh','deadpan','rest'] as const){
for(let m=0;m<8;m++){
const art=renderToStaticMarkup(<svg xmlns="http://www.w3.org/2000/svg" width="380" height="450" viewBox="0 0 1080 1280"><g transform="translate(0,-950)"><Narrator2 t={20} x={540} y={1995} pose={pose} prev={pose} k={1} mouth={m/7}/></g></svg>);
fs.writeFileSync(`assets/host/${pose}_${m}.svg`,art);
}}
