import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import fs from 'node:fs';
import {Narrator2} from '../../studio/src/Narrator2';
fs.mkdirSync('build/host',{recursive:true});
const levels={A:0,B:.3,C:.55,D:.95,E:.65,F:.35,G:.25,H:.55,X:0};
for(const pose of ['talk','point','shock','shrug','rest'])for(const [v,mouth] of Object.entries(levels)){
 const body=renderToStaticMarkup(<svg xmlns="http://www.w3.org/2000/svg" width="380" height="450" viewBox="0 0 380 450">
 <defs><radialGradient id="bg"><stop stopColor="#2a3a7a"/><stop offset="1" stopColor="#10142c"/></radialGradient><linearGradient id="rim"><stop stopColor="#58c8ff"/><stop offset="1" stopColor="#ff5fb0"/></linearGradient><linearGradient id="desk" x2="0" y2="1"><stop stopColor="#7a4a2c"/><stop offset="1" stopColor="#3d2214"/></linearGradient></defs>
 <rect x="3" y="3" width="374" height="444" rx="26" fill="url(#bg)" stroke="url(#rim)" strokeWidth="6"/>
 <circle cx="40" cy="60" r="13" fill="#58c8ff" opacity=".25"/><circle cx="320" cy="90" r="13" fill="#ff5fb0" opacity=".25"/>
 <rect x="250" y="210" width="110" height="80" rx="8" fill="#0d1330" stroke="#384467" strokeWidth="3"/>
 <path d="M260 230h70m-70 15h50" stroke="#58c8ff" strokeWidth="5"/>
 <svg x="0" y="-250" width="380" height="675.56" viewBox="0 0 1080 1920"><g transform="translate(540,1300) scale(1.05) translate(-540,-1300)"><Narrator2 t={0} x={540} y={1995} pose={pose as any} mouth={mouth}/></g></svg>
 <rect x="7" y="358" width="366" height="85" fill="url(#desk)"/>
 <path d="M7 358h366" stroke="#a8714a" strokeWidth="5"/>
 <path d="M63 380l35-115" stroke="#30303b" strokeWidth="8"/>
 <rect x="74" y="205" width="44" height="72" rx="22" fill="#282832" stroke="#777" strokeWidth="3" transform="rotate(18 96 241)"/>
 <path d="M82 224h24m-24 12h24m-24 12h24" stroke="#777" strokeWidth="3"/>
 <rect x="295" y="340" width="43" height="50" rx="8" fill="#e9e3da"/><path d="M337 350q25 0 15 24h-15" fill="none" stroke="#e9e3da" strokeWidth="6"/>
 <text x="303" y="371" fill="#e43c40" fontFamily="DejaVu Sans" fontWeight="bold" fontSize="18">M1</text>
 </svg>);
 let ink=body.replace(/#[0-9a-fA-F]{6}/g,(c)=>({
 '#f3c9a9':'#f5d9bd','#fde3cf':'#fff3df','#d99f80':'#d5b99e','#b97b5f':'#5b4b45',
 '#58c8ff':'#2c82aa','#ff5fb0':'#cc5c87','#4fd1ff':'#2c82aa','#ff5ad1':'#cc5c87',
 '#e9e3da':'#fff8ec','#e43c40':'#ae4d62'
 }[c.toLowerCase()]||(/#(?:1|2|3)/.test(c)?'#30363d':'#6a7275')));
 ink=ink.replace(/url\(#bg\)/g,'#f6edda').replace(/url\(#desk\)/g,'#e5cda5').replace(/url\(#rim\)/g,'#30363d');
 ink=ink.replace('<defs>','<defs><pattern id="pencil" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 8L8 0" stroke="#343b42" stroke-width="0.5" opacity="0.12"/></pattern>');
 ink=ink.replace(/<\/svg>$/, '<rect x="8" y="365" width="360" height="70" fill="url(#pencil)" pointer-events="none"/></svg>');
 fs.writeFileSync(`build/host/${pose}_${v}.svg`,ink);
}
