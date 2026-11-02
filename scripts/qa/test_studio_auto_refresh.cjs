// Node-only regression guard for M1lash Studio auto-refresh. No network, no browser, no credentials.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const page = fs.readFileSync(path.join(root, "site/studio/index.html"), "utf8");
const worker = fs.readFileSync(path.join(root, "site/studio/auto_refresh.js"), "utf8");
const deploy = fs.readFileSync(path.join(root, ".github/workflows/motion-pages.yml"), "utf8");
assert.match(page, /<script src="auto_refresh\.js"><\/script>/);
const inline = page.match(/<script>\s*("use strict";[\s\S]*?)<\/script>/);
assert.ok(inline, "main Studio inline script missing");
new vm.Script(inline[1], {filename:"studio/index.html:inline"});
assert.match(page, /id="driveTok"/);
assert.match(page, /setSecret\("GDRIVE_REFRESH_TOKEN",v\)/);

assert.match(deploy, /node --check site\/studio\/auto_refresh\.js/);
assert.match(deploy, /cp site\/studio\/index\.html site\/studio\/clips_ui\.js site\/studio\/auto_refresh\.js/);
new vm.Script(worker, {filename: "auto_refresh.js"});

let renders = 0;
const elements = {
  asof: {textContent:""},
  sheet: {classList:{contains:()=>false}},
  "hd-status": {textContent:""},
  "hd-qualities": {textContent:""},
  "hd-checked": {textContent:""},
  "drive-oauth-state": {textContent:""},
  "hd-workflow-state": {textContent:""},
  "download-action": {disabled:false},
  "hd-url": {id:"hd-url",value:"https://rezka.ag/films/drama/test.html"},
  "hd-quality": {id:"hd-quality",value:"1080p"}
};
const timers = [];
const next = {
  built:"new build",analytics_as_of:"2026-11-01",
  channel:{subs:10,views:100,videos:2},live:{t:"2026-11-02T20:00:00Z",subs:10,views:100},
  hdrezka_intake:{status:"ok",drive_uploaded:false,available:{"1080p":"available"}},
  drive_auth:{connected:false,status:"not_connected",message:"Требуется OAuth"},
  videos:[],comments:[],review:[],plan:[],experiments:[]
};
const pulse = {
  snapshots:[
    {t:"2026-11-02T20:00:00Z",subs:10,views:100,videos:{}},
    {t:"2026-11-02T21:00:00Z",subs:11,views:140,videos:{}}
  ], recent:[], comments:[{id:"test-comment"}], status:{comments:"ok"}
};
const context = {
  D: {...next, built:"old build", hdrezka_intake:{status:"not_started"}},
  tab:"clips",document:{
    hidden:false, activeElement:{closest:()=>true,matches:()=>true},
    getElementById:id=>elements[id]||null,
    querySelectorAll:()=>[elements["hd-url"],elements["hd-quality"]],
    querySelector:selector=>selector==="[data-hd-download]"?elements["download-action"]:null,
    addEventListener:()=>{}
  },
  navigator:{onLine:true},window:{addEventListener:()=>{}},
  tok:()=> "fake-local-test-pat",
  gh:async path=>({workflow_runs:[{id:12345,status:"in_progress",conclusion:null,head_branch:"main"}]}),
  render:()=>{renders++},
  ago:()=>"1 мин",dshort:()=>"вчера",
  fetch:async url=>({ok:true,json:async()=>url.startsWith("data.json")?next:url.includes("/main/publishing/")?(url.includes("drive_auth_status.json")?{connected:false,checked_at:"2026-11-02T21:30:00Z",status:"error",message:"Drive OAuth denied"}:{status:"error",checked_at:"2026-11-02T21:30:00Z",message:"Source failed"}):pulse}),
  setInterval:(fn,delay)=>{timers.push({fn,delay});return timers.length},
  setTimeout:(fn,delay)=>{timers.push({fn,delay});return timers.length},
  Date,JSON,Object,Array,Number,Math,Promise,console
};
vm.runInNewContext(worker,context,{timeout:1000});
const run = async delay => {
  const tick = timers.find(t=>t.delay===delay);
  assert.ok(tick, "missing timer "+delay);
  tick.fn();
  // Let async response parsing and effects settle.
  for(let i=0;i<8;i++) await new Promise(resolve=>setImmediate(resolve));
};
(async()=>{
  await run(15000);
  assert.equal(context.D.built,"new build");
  assert.equal(renders,0,"must not wipe focused form while refreshing");
  assert.match(elements["hd-status"].textContent,/Качества проверены/);
  assert.match(elements["hd-qualities"].textContent,/1080p/);
  assert.equal(elements["download-action"].disabled,true,"OAuth not connected must disable download");
  context.document.activeElement=null;
  await run(10000);
  assert.equal(renders,1,"render pending update on blur");
  assert.equal(elements["hd-url"].value,"https://rezka.ag/films/drama/test.html");
  await run(30000);
  assert.equal(context.D.channel.subs,11);
  assert.equal(context.D.channel.views,140);
  assert.equal(context.D.live.views_1h,40);
  assert.equal(context.D.comments[0].id,"test-comment");
  const now=renders;
  await run(15000);
  assert.equal(renders,now,"same snapshot must not trigger redundant re-render");
  await run(12000);
  assert.match(elements["drive-oauth-state"].textContent,/Drive OAuth denied/);
  assert.match(elements["hd-status"].textContent,/Source failed/);
  assert.equal(context.D.drive_auth.connected,false);
  assert.equal(elements["download-action"].disabled,true);
  await run(25000);
  assert.match(elements["hd-workflow-state"].textContent,/GitHub Actions #12345: выполняется/);
  console.log("studio auto-refresh smoke PASS (15s page, 30s pulse, 12s raw status, form preserved)");
})().catch(e=>{console.error(e);process.exitCode=1});