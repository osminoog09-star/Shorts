const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../..'),S=require(path.join(root,'site/studio/scheduling.js'));
const page=fs.readFileSync(path.join(root,'site/studio/index.html'),'utf8');
new vm.Script(page.match(/<script>\s*("use strict";[\s\S]*?)<\/script>/)[1]);
assert.equal(S.localTime('2099-01-03T15:00'),Date.parse('2099-01-03T13:00:00Z'));
assert.equal(S.localTime('2099-07-03T15:00'),Date.parse('2099-07-03T12:00:00Z'));
const at='2099-01-03T15:00:00+02:00';
assert.equal(S.occupied({taken:[{id:'one',at},{id:'one',at}],plan:[{id:'one',date:'2099-01-03',time:'15:00',title:'one'}]}).length,1,'taken+plan must not double count');
assert.throws(()=>S.assertFree({taken:[{id:'one',at}]},'two',Date.parse(at)),/занято/);
assert.equal(S.assertFree({taken:[{id:'one',at}]},'one',Date.parse(at)),true,'rescheduling excludes the same video');
assert.throws(()=>S.assertFree({taken:[{id:'one',at}]},'two',Date.parse('2099-01-03T18:59:00+02:00')),/занято/);
assert.equal(S.assertFree({taken:[{id:'one',at}]},'two',Date.parse('2099-01-03T19:00:00+02:00')),true);
assert.throws(()=>S.assertFree({taken:[],best_times:{rules:{max_shorts_per_day:2}}},'film',Date.parse('2099-01-03T20:00:00+02:00'),'short',45,'movie'),/Кино-Shorts/);
assert.equal(S.assertFree({taken:[],best_times:{rules:{max_shorts_per_day:2}}},'film',Date.parse('2099-01-03T10:00:00+02:00'),'short',45,'movie'),true);
assert.throws(()=>S.assertFree({taken:[]},'cartoon',Date.parse('2099-01-04T15:00:00+02:00'),'long',45,'cartoon'),/мультфильмы/);
function context(shared){
 const cache=new Map(),events=[];
 const c={D:{best_times:{rules:{min_gap_hours:4}},taken:[],plan:[],review:[{id:'one',kind:'short',title:'One',video_id:'aaaaaaaaaaa'},{id:'two',kind:'short',title:'Two',video_id:'bbbbbbbbbbb'}],videos:[]},
   store:{get:(k,d)=>cache.get(k)||d,set:(k,v)=>cache.set(k,v)},window:{},M1Schedule:S,
   Date,Intl,Object,JSON,Map,Set,Math,Promise,crypto:require('node:crypto').webcrypto,
   render:()=>{},closeSheet:()=>{},toast:m=>events.push(m),
   editJSON:async(p,fn)=>{if(p.endsWith('schedule_requests.json')){fn(shared);return shared;}const m=shared.manifests[p]||{};fn(m);shared.manifests[p]=m;return m;},
   dispatch:async(w,input)=>events.push(input)};
 vm.createContext(c);
 const controller=page.slice(page.indexOf('let scheduleState='),page.indexOf('function bestSlots('));
 const iso=page.slice(page.indexOf('function tallinnISO('),page.indexOf('async function doSchedule('));
 const action=page.slice(page.indexOf('async function doSchedule('),page.indexOf('/* ---------- 3D',page.indexOf('async function doSchedule(')));
 vm.runInContext(controller+iso+action,c);
 vm.runInContext('refreshSchedulingState=async()=>({requests:{}})',c);
 return {c,events};
}
(async()=>{
 const shared={requests:{},manifests:{}},a=context(shared),b=context(shared);
 const results=await Promise.allSettled([vm.runInContext(`doSchedule('one','${at}')`,a.c),vm.runInContext(`doSchedule('two','${at}')`,b.c)]);
 assert.equal(results.filter(x=>x.status==='fulfilled').length,1,'two tabs cannot reserve the same slot');
 assert.equal(Object.keys(shared.requests).length,1);
 const input=a.events.find(x=>typeof x==='object')||b.events.find(x=>typeof x==='object');
 assert.equal(input.expected_publish_at,at,'dispatch freezes the exact owner-selected time');
 assert.ok(input.request_id);
 const owner=a.c.D.taken.length?a:b;
 owner.c.D={taken:[],plan:[],review:[{id:'one'}],videos:[{id:'aaaaaaaaaaa',privacy:'private'}]};
 vm.runInContext('applySchedulingState(D)',owner.c);
 assert.equal(owner.c.D.taken.length,1,'stale Pages refresh must not release a reserved slot');
 assert.ok(owner.events.some(x=>typeof x==='string'&&x.includes('Ожидаем подтверждения')));
 assert.ok(!owner.events.some(x=>typeof x==='string'&&x.includes('Дата назначена')));
 const chooser=context({requests:{},manifests:{}});
 chooser.c.D.best_times={rules:{short_hours:[10,15,20],long_hours:[19],max_shorts_per_day:3,min_gap_hours:4,min_lead_hours:2,horizon_days:3,near_best_ratio:.85}};
 chooser.c.avg=a=>a.reduce((a,b)=>a+b,0)/a.length;chooser.c.fmtAvg=()=>({});
 vm.runInContext(page.slice(page.indexOf('function bestSlots('),page.indexOf('const DW=')),chooser.c);
 const first=vm.runInContext('bestSlots("short").best.t',chooser.c),part=S.parts(first);
 chooser.c.D.taken.push({id:'first',at:new Date(first).toISOString()});
 chooser.c.D.plan.push({id:'first',date:part.date,time:String(part.hour).padStart(2,'0')+':00',title:'One'});
 const next=vm.runInContext('bestSlots("short").best.t',chooser.c);
 assert.notEqual(first,next,'successive Auto picks must use different slots');
 assert.ok(Math.abs(next-first)>=4*3600000);
 console.log('Studio scheduling PASS: timezone, deduplication, minimum gap, simultaneous tabs, immutable dispatch, stale refresh');
})().catch(e=>{console.error(e);process.exitCode=1});
