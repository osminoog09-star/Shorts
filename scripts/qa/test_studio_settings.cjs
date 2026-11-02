// Regression: settings categories isolate credential controls and retain existing IDs/actions.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const path=require("node:path");
const root=path.resolve(__dirname,"../..");
const html=fs.readFileSync(path.join(root,"site/studio/index.html"),"utf8");
const clips=fs.readFileSync(path.join(root,"site/studio/clips_ui.js"),"utf8");
const inline=html.match(/<script>\s*("use strict";[\s\S]*?)<\/script>/);
assert.ok(inline,"Studio inline script was not found");
new vm.Script(inline[1],{filename:"studio/index.html:inline"});
const start=inline[1].indexOf('let settingsSection="general";');
const end=inline[1].indexOf('/* ---------- «Авто»',start);
assert.ok(start>=0&&end>start,"Settings code missing");
let sheetHTML="";
const ctx=vm.createContext({
  D:{drive_auth:{connected:false,message:"Требуется OAuth"},app:{name:"test",apk:"#"}},
  tok:()=>null,
  esc:val=>String(val??""),
  openSheet:html=>{sheetHTML=html;},
});
vm.runInContext(inline[1].slice(start,end)+"\nopenSettings('general');",ctx);
assert.match(sheetHTML, /data-settings-panel="general"[^>]*>/);
assert.match(sheetHTML, /data-settings-panel="tokens" hidden/);
assert.match(sheetHTML, /data-run="youtube-pulse.yml"/);
assert.match(sheetHTML, /data-run="youtube-analytics.yml"/);
assert.match(sheetHTML, /id="tokIn"/);
assert.match(sheetHTML, /id="ytTok"/);
assert.match(sheetHTML, /id="driveTok"/);
assert.match(sheetHTML, /id="mkKey"/);
vm.runInContext("openSettings('tokens')",ctx);
assert.match(sheetHTML,/data-settings-panel="tokens"[^>]*>/);
assert.doesNotMatch(sheetHTML,/data-settings-panel="tokens" hidden/);
assert.match(sheetHTML,/data-settings-panel="general" hidden/);
for(const id of ["tokIn","tokSave","tokDel","ytTok","ytSave","driveTok","driveSave","driveCheck","mkKey"]){
  if(id==="tokDel")continue; // Shown only if GitHub auth exists
  assert.ok(sheetHTML.includes('id="'+id+'"'),id+" missing from tokens section");
}
assert.match(inline[1],/if\(el=q\("\[data-settings-section\]"\)\)return openSettings\(el\.dataset\.settingsSection\)/);
assert.match(clips,/data-settings-section="tokens">🔐 Токены и доступы/);
assert.match(html,/\[hidden\]\{display:none!important\}/);
console.log("settings categories PASS: general, tokens, actions, Drive shortcut");
