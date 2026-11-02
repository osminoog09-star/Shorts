const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const html=fs.readFileSync(path.resolve(__dirname,"../../site/studio/index.html"),"utf8");
const rules=[
  /\.sheet\{min-width:0;overflow-x:hidden;overflow-wrap:anywhere\}/,
  /\.sheet \.idea\{grid-template-columns:minmax\(0,1fr\)\}/,
  /\.sheet code,\.sheet \.chip\{white-space:normal;overflow-wrap:anywhere;/,
  /\.sheet \.row \.btn,\.sheet \.row button,\.sheet \.row a\.btn\{white-space:normal;/,
  /@media \(max-width:959px\)\{[\s\S]*?\.sheet\{width:100%;max-width:100vw;/,
  /<details class="drive-legacy"/,
  /id="driveGoogleStart"/,
  /id="driveGoogleFinish"/
];
for(const rule of rules) assert.match(html,rule,"mobile settings regression");
assert.equal((html.match(/id="driveTok"/g)||[]).length,1);
assert.equal((html.match(/id="driveSave"/g)||[]).length,1);
console.log("Mobile settings layout regression PASS");
