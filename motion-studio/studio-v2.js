'use strict';
/* M1lash Studio V2 — browser interface, no API credentials or automatic publication. */
const REPO='osminoog09-star/Shorts';
const STORE='m1lash_studio_v2';
const $=id=>document.getElementById(id);
const styleNames=[
['S1','Тушь от руки','D2','Рисунок тушью с живыми контурами'],
['S2','Бумажный коллаж','D25','Слои бумаги, тени и параллакс'],
['S3','Комикс','D2','Упругая комикс-анимация'],
['S4','Чистый вектор','D2','Чёткая объясняющая графика'],
['S5','Пиксель-арт','D2','Чёткие пиксели и покадровое движение'],
['S6','Кинетическая типографика','D2','Крупный читабельный текст'],
['S7','Неон и технологии','D25','Точная неоновая научная графика'],
['S8','Продуктовый UI','D25','Приложения с реальными взаимодействиями'],
['S9','Премиальный 3D','D3','Объёмные предметы, свет и камера'],
['X01','Документальный макро','D3','Детали механизмов и правдоподобный свет'],
['X02','Робототехника','D3','Точные узлы и разрезы роботов'],
['X03','Расследование ИИ','D25','Источники, доказательства и хронология'],
['X04','Инженерные чертежи','D25','Понятная сборка сложных устройств'],
['X05','Историческая реконструкция','D3','Музейные и документальные сцены'],
['X06','Бумажное расследование','D25','Оригинальные иллюстрации и документы'],
['X07','Космос','D3','Орбиты, масштабы и миссии'],
['X08','Мир ИИ-агентов','D25','Понятная логика действий агентов'],
['X09','Роботы: комедийный скетч','D3','Действия, жесты и эмоции'],
['X10','Мини-лаборатория','D3','Макросъёмка и опыты'],
['X11','Кибербезопасность','D25','Реальные причины и последствия'],
['X12','Научный журнал','D25','Инфографика и авторские демонстрации']
].map(x=>({id:x[0],name:x[1],depth:x[2],description:x[3],group:x[0][0]==='S'?'official':'experimental'}));
const agents=[
['research','Исследователь','Источники и дата информации',true],
['factcheck','Фактчекер','Проверка минимум двух независимых источников',true],
['script','Сценарист','Содержательный сценарий, 21+ минут для longform',true],
['director','Режиссёр','Shotlist, кадры, темп, эмоции',true],
['image','Художник','Ассеты, изображения, персонажи',false],
['animation','Аниматор','Камеры и физически понятное движение',false],
['voice','Звук','Голоса Дима/Света, тайминги, липсинк',true],
['editor','Монтажёр','Сведение звука и кадров, экспорт',true],
['quality','Аудитор','Визуальный аудит, факты и качество',true],
['youtube','Упаковка YouTube','Обложка, название, описание, теги',false]
].map(x=>({id:x[0],name:x[1],description:x[2],required:x[3]}));
const defaults={topic:'',brief:'',format:'long',duration:1500,language:'ru',voice:'dima',sources:'',style:'S9',depth:'D3',group:'official',agents:agents.map(a=>a.id)};
function safeLocal(){try{const obj=JSON.parse(localStorage.getItem(STORE)||'null');const v=Object.assign({},defaults,obj||{});if(!Array.isArray(v.agents))v.agents=defaults.agents.slice();v.agents=[...new Set([...agents.filter(a=>a.required).map(a=>a.id),...v.agents.filter(x=>agents.some(a=>a.id===x))])];return v}catch{return {...defaults,agents:defaults.agents.slice()}}}
let state=safeLocal();
function persist(){try{localStorage.setItem(STORE,JSON.stringify(state));$('saveMessage').textContent='Настройки сохранены локально'}catch{$('saveMessage').textContent='Локальное сохранение недоступно'}}
function labelTime(s){return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
function updateDurations(){const choices=state.format==='long'?[1260,1380,1500,1680,1800,2100]:[30,45,60,90,120,180];if(!choices.includes(Number(state.duration)))state.duration=state.format==='long'?1500:45; $('duration').replaceChildren(...choices.map(x=>new Option(labelTime(x),x)));$('duration').value=String(state.duration)}
function formatLabel(){return state.format==='long'?'Полный выпуск':'Shorts'}
function getStyle(id){return styleNames.find(x=>x.id===id)||styleNames[8]}
function styleButton(x){const button=document.createElement('button');button.type='button';button.className='style-pick'+(state.style===x.id?' selected':'');button.setAttribute('aria-pressed',state.style===x.id?'true':'false');const code=document.createElement('b');code.textContent=x.id+' · '+x.depth;const title=document.createElement('span');title.textContent=x.name;button.append(code,title);button.addEventListener('click',()=>chooseStyle(x));return button}
function chooseStyle(x){state.style=x.id;state.group=x.group;state.depth=x.depth;persist();renderStyles();updateSummary()}
function renderStyles(){
 $('styleChoices').replaceChildren(...styleNames.filter(x=>x.group===state.group).map(styleButton));
 document.querySelectorAll('[data-group]').forEach(b=>b.classList.toggle('selected',b.dataset.group===state.group));
 $('styleDetails').textContent=getStyle(state.style).description+' — '+getStyle(state.style).id;
 $('depth').value=state.depth;
 $('allStyles').replaceChildren(...styleNames.map((x,i)=>{const div=document.createElement('article');div.className='panel';const chip=document.createElement('div');chip.className='color-chip s'+(i%9+1);const title=document.createElement('h3');title.textContent=x.id+' · '+x.name;const p=document.createElement('p');p.textContent=x.description;const b=document.createElement('button');b.type='button';b.className='secondary';b.textContent='Выбрать';b.addEventListener('click',()=>{chooseStyle(x);setTab('create')});div.append(chip,title,p,b);return div}));
}
function renderAgents(){
 $('agentSelections').replaceChildren(...agents.map(a=>{const el=document.createElement('label');el.className='agent-choice';const ck=document.createElement('input');ck.type='checkbox';ck.checked=state.agents.includes(a.id);ck.disabled=a.required;ck.addEventListener('change',()=>{state.agents=ck.checked?[...new Set([...state.agents,a.id])]:state.agents.filter(x=>x!==a.id);persist();updateSummary()});const content=document.createElement('span');const title=document.createElement('strong');title.textContent=a.name+(a.required?' · обязательно':'');const note=document.createElement('small');note.textContent=a.description;content.append(title,note);el.append(ck,content);return el}));
 $('agentCards').replaceChildren(...agents.map((a,i)=>{const box=document.createElement('article');box.className='panel';const code=document.createElement('p');code.className='eyebrow';code.textContent='АГЕНТ '+String(i+1).padStart(2,'0');const title=document.createElement('h3');title.textContent=a.name;const info=document.createElement('p');info.textContent=a.description;box.append(code,title,info);return box}));
}
function updateSummary(){ $('sumFormat').textContent=formatLabel();$('sumDuration').textContent=labelTime(Number(state.duration));$('sumStyle').textContent=state.style+' / '+state.depth;$('sumAgents').textContent=state.agents.length; const labels={dima:'Дима',sveta:'Света','orion-ru':'Орион RU (тест)','nova-ru':'Нова RU (тест)','orion-en':'Орион EN (тест)'};$('sumVoice').textContent=labels[state.voice]||state.voice;const m=[];if(String(state.topic).trim().length<8)m.push('Заполни тему ролика.');if(state.format==='long'&&state.duration<1260)m.push('Для длинных видео требуется 21+ минута.');if(!['dima','sveta'].includes(state.voice))m.push('Голос экспериментальный: нельзя автоматически публиковать.');$('readiness').textContent=m.length?m.join(' '):'Готов к созданию задания. Видео/источники ещё не проверены.';$('submitJob').disabled=String(state.topic).trim().length<8}
function setTab(tab){document.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id==='tab-'+tab));document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));$('sectionTitle').textContent=({create:'Новый выпуск',agents:'Агенты',styles:'Стили',queue:'Производство',settings:'Настройки',news:'Радар новостей',reference:'Разбор YouTube'})[tab]||tab;if(tab==='queue')refreshJobs();if(tab==='news')refreshNews();window.scrollTo(0,0)}
function makeJob(){const topic=String(state.topic||'').trim();if(topic.length<8||topic.length>180)throw Error('Тема должна содержать 8–180 символов.');if(state.format==='long'&&(state.duration<1260||state.duration>3600))throw Error('Полный ролик 21–60 минут.');if(state.format==='short'&&(state.duration<30||state.duration>180))throw Error('Shorts 30–180 секунд.');if(state.brief.length>2200||state.sources.length>1500)throw Error('Сократи описание или ссылки перед отправкой на публичный GitHub.');return {schema:1,source:'m1lash-studio-v2',topic,brief:state.brief.trim(),format:state.format,duration_s:Number(state.duration),language:state.language,voice:state.voice,style:state.style,depth:state.depth,sources:state.sources.split(/\r?\n/).map(x=>x.trim()).filter(Boolean).slice(0,12),agents:[...new Set([...agents.filter(a=>a.required).map(a=>a.id),...state.agents])],request:'prepare_only',publish:false}}
function openGithubJob(obj){if(!confirm('Создать публичное задание через GitHub? Его текст увидят посетители репозитория. Автопубликации нет.'))return;const title='[M1LASH STUDIO] '+String(obj.topic||'Новый выпуск').slice(0,170);const body='Задание M1lash Studio. ПОДГОТОВКА, не готовый ролик.\n\nM1LASH_JOB_START\n'+JSON.stringify(obj)+'\nM1LASH_JOB_END\n\nПубликация на YouTube запрещена без одобрения.';const url='https://github.com/'+REPO+'/issues/new?title='+encodeURIComponent(title)+'&body='+encodeURIComponent(body);if(url.length>12000)throw Error('Слишком большой запрос; скачай JSON или сократи текст.');const opened=window.open(url,'_blank','noopener,noreferrer');if(!opened)location.assign(url)}
function submit(){try{openGithubJob(makeJob())}catch(e){alert(e.message)}}
function downloadJob(){try{const blob=new Blob([JSON.stringify(makeJob(),null,2)+'\n'],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.download='m1lash-project.json';a.href=url;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}catch(e){alert(e.message)}}
const stageLabels={research:'Исследователь',factcheck:'Фактчекер',script:'Сценарист',director:'Режиссёр',image:'Художник',animation:'Аниматор',voice:'Озвучка Димы',editor:'Монтаж',quality:'Аудитор',youtube:'YouTube'};
const statusLabels={ready:'Материалы созданы',needs_review:'Нужна проверка',blocked:'Ещё не сделано'};
function parseStageComment(body,issueNumber){
 if(typeof body!=='string')return null;
 const a='M1LASH_STAGE_STATUS_BEGIN\n',z='\nM1LASH_STAGE_STATUS_END';
 const start=body.indexOf(a);
 if(start<0)return null;
 const end=body.indexOf(z,start+a.length);
 if(end<0||end-start>11000)return null;
 try{
  const data=JSON.parse(body.slice(start+a.length,end));
  if(data.schema!==1||data.issue_number!==issueNumber||!Number.isSafeInteger(data.run_id)||!Array.isArray(data.stages))return null;
  if(data.stages.some(x=>!Object.hasOwn(stageLabels,x.id)||!Object.hasOwn(statusLabels,x.status)))return null;
  return data;
 }catch{return null}
}
function makeJobCard(issue){
 const card=document.createElement('article');card.className='queue-item';
 const link=document.createElement('a');link.href=issue.html_url;link.target='_blank';link.rel='noopener noreferrer';
 link.textContent=issue.title.replace('[M1LASH STUDIO] ','')+' ↗';
 const label=document.createElement('small');label.textContent='Задание №'+issue.number+' · '+issue.state+' · ожидаем подробный отчёт агентов';
 const stages=document.createElement('div');stages.className='stage-list';
 stages.textContent='Загружаем последние результаты из GitHub…';
 const info=document.createElement('p');info.className='muted';info.textContent='Новые задания автоматически стартуют в GitHub Actions. Для повтора напиши /studio run в комментарии к заданию.';
 card.append(link,label,stages,info);
 return {card,label,stages};
}
async function fetchJobStatus(issue,view){
 try{
  const response=await fetch('https://api.github.com/repos/'+REPO+'/issues/'+issue.number+'/comments?per_page=35',{headers:{Accept:'application/vnd.github+json'}});
  if(!response.ok)throw Error('API '+response.status);
  const comments=await response.json();
  let status=null;
  for(const c of comments){
   // Only bot-written summaries from our workflow, never arbitrary community comments.
   if(!c.user||c.user.type!=='Bot'||!['github-actions[bot]','github-actions'].includes(c.user.login))continue;
   const parsed=parseStageComment(c.body,issue.number);
   if(parsed)status=parsed;
  }
  if(!status){view.stages.textContent='Пока есть только GitHub Issue. Последнего отчёта агентов ещё нет.';return}
  const ready=status.stages.filter(x=>x.status==='ready').length;
  const review=status.stages.filter(x=>x.status==='needs_review').length;
  const blocked=status.stages.filter(x=>x.status==='blocked').length;
  view.label.textContent='Задание №'+issue.number+' · подготовлено этапов: '+ready+' · на проверке: '+review+' · заблокировано: '+blocked;
  view.stages.replaceChildren(...status.stages.map(x=>{
   const row=document.createElement('div');row.className='stage-row stage-'+x.status;
   const name=document.createElement('strong');name.textContent=(stageLabels[x.id]||x.id)+' · '+statusLabels[x.status];
   const reason=document.createElement('small');reason.textContent=String(x.reason||'').slice(0,250);
   row.append(name,reason);return row;
  }));
  const url='https://github.com/'+REPO+'/actions/runs/'+status.run_id;
  const artifact=document.createElement('a');artifact.href=url;artifact.className='textlink';artifact.target='_blank';artifact.rel='noopener noreferrer';
  artifact.textContent='Рабочие файлы, сценарий и отчёт запуска ↗';
  view.stages.append(artifact);
 }catch(error){view.stages.textContent='Статус не загружен ('+error.message+'). Открой GitHub Issue для подробностей.'}
}
async function refreshJobs(){
 const target=$('queueList');target.textContent='Загружаем очередь…';
 try{
  const response=await fetch('https://api.github.com/repos/'+REPO+'/issues?state=all&per_page=50&sort=created',{headers:{Accept:'application/vnd.github+json'}});
  if(!response.ok)throw Error('GitHub API '+response.status);
  const rows=(await response.json()).filter(x=>!x.pull_request&&x.title.startsWith('[M1LASH STUDIO]')).slice(0,8);
  if(!rows.length){target.textContent='Заданий пока нет. Создай первое через сайт.';return}
  const views=rows.map(issue=>({issue,view:makeJobCard(issue)}));
  target.replaceChildren(...views.map(x=>x.view.card));
  await Promise.all(views.map(x=>fetchJobStatus(x.issue,x.view)));
 }catch(e){target.textContent='Не удалось загрузить очередь: '+e.message}
}
function validNews(item){return item&&typeof item.id==='string'&&typeof item.title==='string'&&typeof item.url==='string'&&item.url.startsWith('https://')&&item.title.length<400}
function isFresh(date){const time=Date.parse(date||'');return Number.isFinite(time)&&(Date.now()-time>=0)&&(Date.now()-time<7*86400000)}
let feedCache=[];
function makeNewsCard(item){const box=document.createElement('article');box.className='panel news-card';const category=document.createElement('p');category.className='eyebrow';category.textContent=String(item.category||'Технологии')+' · '+String(item.source||'Источник');const h=document.createElement('h3');h.textContent=item.title;const date=document.createElement('p');date.className='muted';date.textContent='Дата публикации: '+(item.published_at?new Date(item.published_at).toLocaleString('ru-RU'):'неизвестна')+' · '+(isFresh(item.published_at)?'Свежая':'Требует проверки актуальности');const link=document.createElement('a');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';link.className='textlink';link.textContent='Читать первоисточник ↗';const choose=document.createElement('button');choose.type='button';choose.className='primary';choose.textContent='Взять в производство';choose.addEventListener('click',()=>{state.topic=item.title.slice(0,180);state.brief='Новость из радара; НЕ считать проверенным фактом. Найди минимум два независимых источника, уточни дату события и ключевые противоречия. Категория: '+(item.category||'технологии')+'.';state.sources=item.url;state.format='short';state.duration=45;state.style='X03';state.group='experimental';state.depth='D25';applyDraft();persist();setTab('create')});box.append(category,h,date,link,choose);return box}
async function refreshNews(){const target=$('newsList'),summary=$('newsStatus');target.textContent='Загружаем новости…';try{const r=await fetch('./data/news.json?cache='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('Нет новостного JSON');const data=await r.json();feedCache=(Array.isArray(data.items)?data.items:[]).filter(validNews);summary.textContent='Обновление: '+(data.updated_at||'ещё не выполнено')+' · источников успешно '+(data.feeds_ok||0)+' · ошибок '+(data.feeds_failed||0)+'. Новости не являются фактчекингом.';renderNews()}catch(e){summary.textContent='Радар ещё не запущен: '+e.message;target.textContent='После первого запуска GitHub Actions здесь появятся новости.'}}
function renderNews(){const category=$('newsCategory')?$('newsCategory').value:'all';const recent=feedCache.filter(x=>category==='all'||x.category===category).slice(0,48);$('newsList').replaceChildren(...recent.map(makeNewsCard));if(!recent.length)$('newsList').textContent='Нет материалов по этой категории. Попробуй другую.'}
function youtubeId(text){let u;try{u=new URL(text)}catch{return null}const host=u.hostname.toLowerCase();let id=null;if(host==='youtu.be'||host==='www.youtu.be')id=u.pathname.replace(/^\//,'').split('/')[0];else if(['youtube.com','www.youtube.com','m.youtube.com'].includes(host)){if(u.pathname==='/watch')id=u.searchParams.get('v');else{const m=u.pathname.match(/^\/(?:shorts|live|embed)\/([a-zA-Z0-9_-]{11})/);if(m)id=m[1]}}return id&&/^[a-zA-Z0-9_-]{11}$/.test(id)?id:null}
function submitReference(){const raw=$('referenceUrl').value,id=youtubeId(raw);if(!id){$('referenceStatus').textContent='Нужна настоящая ссылка на YouTube (watch, shorts, youtu.be).';return}const request={schema:1,source:'m1lash-studio-v2',request:'reference_analysis',video_url:'https://www.youtube.com/watch?v='+id,video_id:id,analysis_scope:'Only verified metadata/available authorized media; never claim frame-level audit from title alone',publish:false};$('referenceStatus').textContent='Задание для анализа: '+request.video_url+'. Покадровый разбор возможен только при доступе к самому видео.';try{openGithubJob({topic:'Разобрать ролик YouTube '+id,...request})}catch(e){alert(e.message)}}
function applyDraft(){for(const k of ['topic','brief','sources','format','language','voice','depth'])$(k).value=state[k];updateDurations();renderStyles();updateSummary()}
function init(){applyDraft();renderAgents();
 for(const k of ['topic','brief','sources'])$(k).addEventListener('input',()=>{state[k]=$(k).value;persist();updateSummary()});
 for(const k of ['format','language','voice','depth'])$(k).addEventListener('change',()=>{state[k]=$(k).value;if(k==='format'){state.duration=state.format==='long'?1500:45;updateDurations()}persist();updateSummary()});
 $('duration').addEventListener('change',()=>{state.duration=Number($('duration').value);persist();updateSummary()});
 document.querySelectorAll('.nav').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab)));
 document.querySelectorAll('[data-group]').forEach(b=>b.addEventListener('click',()=>{state.group=b.dataset.group;const x=styleNames.find(s=>s.group===state.group);state.style=x.id;state.depth=x.depth;persist();renderStyles();updateSummary()}));
 $('submitJob').addEventListener('click',submit);$('exportConfig').addEventListener('click',downloadJob);
 $('refreshJobs').addEventListener('click',refreshJobs);
 $('clearDraft').addEventListener('click',()=>{if(confirm('Сбросить локальные настройки?')){localStorage.removeItem(STORE);location.reload()}});
 if($('refreshNews'))$('refreshNews').addEventListener('click',refreshNews);
 if($('newsCategory'))$('newsCategory').addEventListener('change',renderNews);
 if($('analyzeYoutube'))$('analyzeYoutube').addEventListener('click',submitReference);
}
document.addEventListener('DOMContentLoaded',init);
