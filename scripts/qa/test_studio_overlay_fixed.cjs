// Регресс 07.11.2026: glass.css делал .sheet/#scrim/#toast position:relative —
// окно «Выбрать время» и сообщения уезжали в низ страницы, кнопка «ничего не делала».
// glass.css подключается после стилей index.html, поэтому его правила сильнее.
const fs=require('fs'),path=require('path');
const css=fs.readFileSync(path.resolve(__dirname,'../../site/studio/glass.css'),'utf8').replace(/\/\*[\s\S]*?\*\//g,'');
const fail=[];
for(const [sel,re] of [['.sheet',/(^|[,}\s])\.sheet(?=[\s,{])/],['#scrim',/#scrim(?=[\s,{])/],['#toast',/#toast(?=[\s,{])/]]){
  const rules=[...css.matchAll(/([^{}]+)\{([^}]*)\}/g)].filter(m=>re.test(' '+m[1].trim()+' ')&&/position\s*:/.test(m[2]));
  const last=rules.at(-1);
  if(last&&!/position\s*:\s*fixed\s*!important/.test(last[2]))fail.push(sel+' → '+last[2].trim());
}
if(fail.length){console.error('FAIL: оверлеи сайта не fixed:\n'+fail.join('\n'));process.exit(1)}
console.log('Studio overlays (sheet/scrim/toast) stay fixed PASS');
