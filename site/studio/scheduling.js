/* Pure scheduling rules shared by the Studio UI and offline regression tests. */
(function (root) {
  'use strict';
  const zone='Europe/Tallinn';
  function parts(ms){
    const p=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date(ms)).map(x=>[x.type,x.value]));
    return {date:`${p.year}-${p.month}-${p.day}`,hour:+p.hour,minute:+p.minute};
  }
  function localTime(value){
    if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value||''))throw new Error('Выбери дату и время');
    const target=Date.parse(value+'Z');let t=target;
    for(let i=0;i<3;i++){const p=parts(t);const wall=Date.parse(p.date+'T'+String(p.hour).padStart(2,'0')+':'+String(p.minute).padStart(2,'0')+'Z');t+=target-wall;}
    const p=parts(t);if(p.date+'T'+String(p.hour).padStart(2,'0')+':'+String(p.minute).padStart(2,'0')!==value)throw new Error('Это время не существует при переводе часов');
    return t;
  }
  function occupied(data,exclude){
    const slots=new Map();
    for(const x of data.taken||[]){const t=Date.parse(x.at);if(x.id===exclude||x.id===exclude+"/previous"||!Number.isFinite(t))continue;slots.set((x.id||'slot')+'|'+t,{...x,t,kind:x.kind||'short'});}
    for(const x of data.plan||[]){if(!x.title||x.id===exclude)continue;const t=localTime(x.date+'T'+x.time.slice(0,5));if([...slots.values()].some(s=>s.t===t))continue;slots.set((x.id||'slot')+'|'+t,{...x,t,kind:x.kind||(x.what==='Рисованный мультфильм'||x.what==='кино-разбор'?'long':'short')});}
    return [...slots.values()];
  }
  function assertFree(data,id,t,kind='short',leadMinutes=45,role=null){
    if(!Number.isFinite(t)||t<Date.now()+leadMinutes*60000)throw new Error('Нужно минимум '+leadMinutes+' минут до публикации');
    const r=data.best_times?.rules||{},gap=(r.min_gap_hours||4)*3600000,all=occupied(data,id);
    if(all.some(x=>Math.abs(x.t-t)<gap))throw new Error('Время занято: между роликами нужно минимум '+(r.min_gap_hours||4)+' часа. Выбери другой слот');
        if(kind!=='long'&&all.filter(x=>x.kind!=='long'&&parts(x.t).date===parts(t).date).length>=(r.max_shorts_per_day||2))throw new Error('На этот день уже назначены два Shorts');
    if(role){
      const p=parts(t),day=new Date(p.date+'T12:00:00Z').getUTCDay();
      if(kind==='long'&&!(role==='cartoon'&&p.hour===15&&(day===3||day===6)))throw new Error('Длинные разрешены только как оригинальные рисованные мультфильмы в ср/сб 15:00');
      if(kind!=='long'&&!(role==='movie'&&p.hour===10||role==='sketch'&&p.hour===20))throw new Error('Кино-Shorts только 10:00, скетчи только 20:00');
    }
    return true;
  }
  const api={parts,localTime,occupied,assertFree};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.M1Schedule=api;
})(typeof window!=='undefined'?window:globalThis);
