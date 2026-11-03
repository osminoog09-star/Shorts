/* M1lash Drive intake UI: ONE public folder for future clips, not re-requests for existing 7.
   Browser writes JSON with owner's GitHub token; read-only scheduled scanner handles matching.
   No fake ready status: ASR, licensing and media QA are separate gates.
*/
function clips(){
  const req=(D.clip_requests||{}).items||[];
  const scan=D.drive_scan||{};
  const folder=D.drive_folder||{};
  const found=new Map((scan.items||[]).map(x=>[x.id,x]));
  const probes=(D.scene_candidates||{}).items||{};
  const missing=req.filter(r=>!["собран","сцена найдена"].includes((found.get(r.id)||{}).status||r.status)).length;
  const active=!!folder.scan_enabled&&!!folder.url;
  const stat=scan.status==="ok"
    ? 'В папке '+num(scan.file_count)+' файлов, из них видео '+num(scan.video_files)+
      ' · нужно фильмов '+num(scan.required_film_count)+
      ' · найдено '+num(scan.matched_film_count)
    : scan.status==="error"?'Ошибка сканирования: '+esc(scan.message||"доступ закрыт")
    : folder.url?'Папка подключена для приватной проверки через Google OAuth. Публичный доступ НЕ требуется. Семь старых фильмов повторно не нужны.':'Папка ещё не подключена. Уже собранные 7 видео повторно скачивать не нужно.';
  let html='<section class="card reveal"><h2>Одна папка Google Drive</h2>'+
    '<p class="muted">Для новых кино-сцен. Фильмы целиком, русская актёрская дорожка. Сканирование через твой закрытый Google Drive OAuth — открывать доступ всем по ссылке не надо. Не загружай сюда исходники для уже собранных 7 роликов повторно.</p>'+
    '<label class="muted" for="drive-folder-url">Папка Google Drive</label>'+
    '<input class="t" id="drive-folder-url" type="url" inputmode="url" autocomplete="off" placeholder="https://drive.google.com/drive/folders/…" value="'+esc(folder.url||"")+'">'+
    '<div class="row"><button class="btn pri" data-folder-save>'+(folder.url&&!active?'Включить проверку папки':'Сохранить папку')+'</button>'+
    '<button class="btn" data-folder-scan '+(!active?'disabled':'')+'>Проверить папку</button>'+
    (folder.url?'<a class="btn" target="_blank" rel="noopener noreferrer" href="'+esc(folder.url)+'">Открыть Drive</a>':'')+'</div>'+
    '<p class="muted">'+stat+'</p>'+
    ((scan.missing||[]).length?'<p class="muted">Не хватает: '+(scan.missing||[]).map(esc).join(' · ')+'</p>':'')+
    '<p class="muted">Последняя проверка: '+esc(scan.scanned_at||"ещё не было")+
    '. Сканер пока определяет файлы, но не скачивает фильмы и не заявляет о готовом монтаже.</p></section>';
  html+='<section class="card reveal"><h2>Заявки <span class="cnt">'+missing+' ожидают исходники/сцены</span></h2>'+
    '<p class="muted">Без ссылок на каждую сцену: сканер сопоставляет фильмы автоматически. При неоднозначности — подтверждение ниже.</p></section>';
  html+='<div class="grid">'+req.map(r=>{
    const id=esc(r.id);
    const m=found.get(r.id)||{};
    const probe=probes[r.id]||{};
    const matchingProbe=m.file_url&&m.file_url===probe.file_url;
    const state=r.status==="собран"?"собран":
      (matchingProbe&&probe.status==="candidate"?"кандидаты ASR (не проверены)":
       matchingProbe&&probe.status==="error"?"ошибка поиска сцены":(m.status||"нет фильма в папке"));
    const choices=(m.candidates||[]);
    const chosen=!!choices.length?
      '<label class="muted" for="match-'+id+'">Это тот фильм?</label>'+
      '<select class="t" id="match-'+id+'">'+choices.map((p,i)=>'<option value="'+i+'">'+esc(p)+'</option>').join('')+'</select>'+
      '<button class="btn sm" data-clip-confirm="'+id+'">Подтвердить соответствие</button>':'';
    return '<section class="idea reveal"><div class="row"><span class="chip">'+esc(state)+
      '</span><span class="muted">'+esc(r.minute||"")+'</span></div><b>'+esc(r.film||"")+
      '</b><p>'+esc(r.scene||"")+'</p><p class="muted">'+esc(r.why||"")+
      '</p>'+(m.filename?'<p class="muted">В папке: '+esc(m.filename)+'</p>':'')+
      (matchingProbe&&probe.status==="candidate"&&probe.candidates?.length?
       '<p class="muted">ASR предложил примерно '+Math.floor(probe.candidates[0].start/60)+':'+
         String(Math.floor(probe.candidates[0].start%60)).padStart(2,"0")+
         '. Это НЕ проверенная по кадрам сцена и не готовый Short.</p>':'')+
      (matchingProbe&&probe.status==="error"?'<p class="muted">'+esc(probe.error||"Нужна проверка исходника")+'</p>':'')+
      (m.scene_start!=null?'<p class="muted">Сцена проверена с '+Math.floor(m.scene_start/60)+':'+String(Math.floor(m.scene_start%60)).padStart(2,"0")+'</p>':'')+
      chosen+'<p class="muted">'+esc(r.note||"")+'</p></section>';
  }).join('')+'</div>';
  html+='<section class="card reveal"><h2>Своя заявка</h2>'+
      '<label class="muted" for="newclip-film">Фильм и год</label><input id="newclip-film" class="t" maxlength="120" placeholder="Название фильма (2022)">'+
      '<label class="muted" for="newclip-note">Какая сцена?</label><input id="newclip-note" class="t" maxlength="200" placeholder="Опиши сцену">'+
      '<button class="btn pri" data-clip-add>Добавить заявку</button></section>';
  return rezkaIntakePanel()+mediaLinkPanel()+html;
}
function clipFolderUrl(raw){
  let u;try{u=new URL(raw)}catch(e){throw new Error("Нужна ссылка на папку Google Drive")}
  if(u.protocol!=="https:"||u.hostname!=="drive.google.com"||u.username||u.password||raw.length>500)
    throw new Error("Нужна безопасная ссылка на Google Drive");
  const m=u.pathname.match(/^\/drive\/(?:u\/\d+\/)?folders\/([A-Za-z0-9_-]{10,})\/?$/);
  if(!m)throw new Error("Нужна ссылка на ПАПКУ, не на отдельный фильм");
  return "https://drive.google.com/drive/folders/"+m[1];
}
document.addEventListener("click",e=>{
  let b=e.target.closest("[data-folder-save]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      const url=clipFolderUrl((document.getElementById("drive-folder-url")?.value||"").trim());
      const saved=await editJSON("publishing/drive_folder.json",d=>{
        d.url=url;d.scan_enabled=true;d.updated=new Date().toISOString().slice(0,10);
      },"studio: set ONE Drive folder for future film intake");
      D.drive_folder=saved;
      // Updating drive_folder.json automatically triggers the scan workflow on push.
      render();toast("Папка сохранена. Автосканирование запустится через GitHub Actions.");
    });
  }
  b=e.target.closest("[data-folder-scan]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      if(!(D.drive_folder||{}).scan_enabled)throw new Error("Сначала сохрани папку");
      await dispatch("drive-folder-intake.yml");
      toast("Проверка папки запущена. Обнови страницу после завершения сканирования.");
      b.disabled=false;
    });
  }
  b=e.target.closest("[data-clip-confirm]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      const id=b.dataset.clipConfirm;
      const m=((D.drive_scan||{}).items||[]).find(x=>x.id===id);
      const index=Number(document.getElementById("match-"+id)?.value);
      const candidate=m?.candidates?.[index];
      if(!candidate)throw new Error("Не найден файл для подтверждения");
      const saved=await editJSON("publishing/clip_requests.json",d=>{
        const row=(d.items||[]).find(x=>x.id===id);
        if(!row)throw new Error("Заявка не найдена");
        row.match_confirmed_filename=candidate;
        row.updated=new Date().toISOString().slice(0,10);
        d.updated=row.updated;
      },"studio: confirm Drive movie match "+id);
      D.clip_requests=saved;await dispatch("drive-folder-intake.yml");
      render();toast("Выбран файл. Сканер повторно проверит соответствие.");
    });
  }
  b=e.target.closest("[data-clip-add]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      const film=(document.getElementById("newclip-film")?.value||"").trim();
      const scene=(document.getElementById("newclip-note")?.value||"").trim();
      if(film.length<3||scene.length<4)throw new Error("Нужны фильм и описание сцены");
      const id="custom-"+Date.now().toString(36);
      const saved=await editJSON("publishing/clip_requests.json",d=>{
        d.items=d.items||[];
        d.items.push({id,film,scene,minute:"—",why:"Заявка владельца",
          for:"Новый кино-Shorts",status:"нужен",
          note:"Русский актёрский дубляж, проверка ASR и кадров до монтажа",
          updated:new Date().toISOString().slice(0,10)});
        d.updated=new Date().toISOString().slice(0,10);
      },"studio: add future scene request "+id);
      D.clip_requests=saved;render();toast("Новая сцена добавлена в очередь.");
    });
  }
});

/* Browser-only direct-file helper. It does not extract video from site/player pages. */
function mediaLinkPanel(){
  let driveUrl="";
  try{if(D?.drive_folder?.url)driveUrl=clipFolderUrl(D.drive_folder.url)}catch(e){}
  const imported=D?.direct_movie_status||{};
  const run=window.__m1LatestDirectRun;
  const requestTime=Date.parse(window.__m1DirectRequestedAt||run?.created_at||"")||0;
  const resultTime=Date.parse(imported.checked_at||"")||0;
  const pending=requestTime>resultTime&&Date.now()-requestTime<2*3600000;
  const status=pending&&run&&["queued","pending","in_progress"].includes(run.status)
    ? "GitHub Actions #"+run.id+": "+(run.status==="in_progress"?"скачивает или проверяет":"в очереди")
    : pending?"Задача принята GitHub Actions. Ожидаем результат"
    : imported.status==="ok"?(imported.drive_uploaded?"MP4 проверен и загружен в Drive":"Прямая ссылка отвечает; качество не проверено")
    : imported.status==="error"?"Ошибка: "+(imported.message||imported.error_code||"см. Actions")
    :"Серверный импорт ещё не запускался";
  const driveCta=driveUrl?
    '<p class="muted">Папка Drive подключена. Готовые разрешённые MP4 можно загружать и анализировать автоматически, без телефона.</p>'+
    '<a class="btn" href="'+esc(driveUrl)+'" target="_blank" rel="noopener noreferrer">Открыть папку Drive</a>':
    '<p class="muted">Для сохранения фильма нужна подключённая папка Google Drive.</p>';
  return '<section class="card reveal" aria-label="Серверная загрузка MP4 по ссылке">'+
    '<h2>⬇️ Прямой MP4 → Google Drive (сервер)</h2>'+
    '<p class="muted">Без телефона. Поддерживаются публичные HTTPS-ссылки на разрешённые к использованию полные MP4 с Archive.org, Blender и GitHub Releases. '+
    'Ссылки на страницы HDRezka, другие плееры, DRM и антибот не подходят. Не путай прямой MP4 с адресом страницы фильма.</p>'+
    '<label class="f" for="media-url">Прямая ссылка на видео'+
    '<input class="t" type="url" id="media-url" inputmode="url" autocomplete="off" '+
    'maxlength="2048" placeholder="https://archive.org/download/Example/movie.mp4"></label>'+
    '<div class="row"><button type="button" class="btn" data-media-server-check>Проверить на сервере</button>'+
    '<button type="button" class="btn pri" data-media-server-upload '+(!D?.drive_auth?.connected?'disabled':'')+'>Проверить MP4 и отправить в Drive</button></div>'+
    '<p class="muted" id="direct-movie-state" role="status" aria-live="polite">'+esc(status)+'</p>'+
    '<p class="muted">Проверка качества и длительности выполняется по фактическому скачанному файлу. Отправка только полнометражного MP4 от 20 минут, минимум выбранное разрешение 1080p. '+
    'GitHub Actions не публикует фильм в репозитории или на YouTube.</p>'+
    '<a class="btn sm" target="_blank" rel="noopener noreferrer" href="https://github.com/osminoog09-star/Shorts/actions/workflows/direct-movie-intake.yml">Журнал серверного импорта</a>'+
    '<details><summary>Открыть прямую ссылку в браузере</summary>'+
    '<div class="row"><button type="button" class="btn" data-media-check>Проверить формат ссылки</button>'+
    '<button type="button" class="btn" data-media-clear>Очистить</button></div>'+
    '<p class="muted" id="media-status" role="status">Без загрузки в GitHub.</p>'+
    '<div id="media-actions" hidden><p class="muted" id="media-meta"></p>'+
    '<a class="btn" id="media-download" rel="noopener noreferrer" target="_blank">Открыть файл</a></div></details>'+
    driveCta+'</section>';
}

function serverMovieSource(raw){
  const result=classifyMediaLink(raw);
  if(!result.ok)throw new Error(result.message);
  const u=new URL(result.url),host=u.hostname.toLowerCase();
  if(!u.pathname.toLowerCase().endsWith(".mp4")||u.search||u.hash||result.url.length>800||
     !(["archive.org","download.blender.org","github.com","release-assets.githubusercontent.com"].includes(host)||
       host.endsWith(".archive.org")))
    throw new Error("Сервер принимает только прямые публичные MP4 с Archive.org, Blender или GitHub Releases без ключей в ссылке.");
  return result.url;
}

document.addEventListener("click",e=>{
  const button=e.target.closest("[data-media-server-check],[data-media-server-upload]");
  if(!button)return;
  if(!needTok())return;
  return act(button,async()=>{
    const url=serverMovieSource(document.getElementById("media-url")?.value||"");
    const mode=button.hasAttribute("data-media-server-upload")?"download":"inspect";
    if(mode==="download"&&!D?.drive_auth?.connected)
      throw new Error("Google Drive пока не подключён.");
    await dispatch("direct-movie-intake.yml",{url,mode,quality:"1080p"});
    window.__m1DirectRequestedAt=new Date().toISOString();
    const label=document.getElementById("direct-movie-state");
    if(label)label.textContent="GitHub Actions принял задачу. Результат обновится автоматически.";
    toast(mode==="download"?"Серверная загрузка запрошена; проверим MP4 и Drive.":"Проверка прямой ссылки запущена.");
    button.disabled=false;
  });
});

function classifyMediaLink(raw){
  if(typeof raw!=="string"||raw.length>2048)return {ok:false,message:"Ссылка слишком длинная или некорректная."};
  let u;try{u=new URL(raw.trim())}catch(e){return {ok:false,message:"Вставь полную ссылку HTTPS."}}
  if(u.protocol!=="https:"||u.username||u.password||(u.port&&u.port!=="443"))
    return {ok:false,message:"Поддерживаются только безопасные HTTPS-ссылки без пароля и нестандартного порта."};
  const host=u.hostname.toLowerCase();
  if(host==="localhost"||host.endsWith(".localhost")||host.endsWith(".local"))
    return {ok:false,message:"Локальные адреса здесь не поддерживаются."};
  if(/(^|\.)(?:hdrezka|rezka)\./i.test(host))
    return {ok:false,message:"Это страница HDRezka, а не прямая ссылка на видеофайл. GitHub Pages не умеет извлекать из неё MP4 или выбирать 1080p. Скачивание с HDRezka не поддерживается."};
  const ext=u.pathname.toLowerCase().match(/\.(mp4|m4v|webm)$/);
  if(!ext)return {ok:false,message:"Не обнаружен прямой файл MP4, M4V или WebM. Ссылки на страницы плееров, HLS (.m3u8) и DRM не поддерживаются."};
  let name;try{name=decodeURIComponent(u.pathname.split("/").pop())}catch(e){name=u.pathname.split("/").pop()}
  return {ok:true,url:u.href,filename:name.replace(/[\\/<>:"|?*\x00-\x1f]/g,"_").slice(0,140)};
}
document.addEventListener("click",e=>{
  if(e.target.closest("[data-media-clear]")){
    const input=document.getElementById("media-url"),status=document.getElementById("media-status");
    if(input)input.value="";
    if(status)status.textContent="Ссылка обрабатывается только в браузере, без отправки в GitHub.";
    const actions=document.getElementById("media-actions");if(actions)actions.hidden=true;
    return;
  }
  if(!e.target.closest("[data-media-check]"))return;
  const status=document.getElementById("media-status"),actions=document.getElementById("media-actions");
  if(!status||!actions)return;
  const result=classifyMediaLink(document.getElementById("media-url")?.value||"");
  actions.hidden=true;
  if(!result.ok){status.textContent=result.message;return}
  const link=document.getElementById("media-download");
  link.href=result.url;link.download=result.filename||"video.mp4";
  document.getElementById("media-meta").textContent="Файл: "+result.filename+" · разрешение и доступность 1080p не проверены. Браузер скачает исходное качество.";
  actions.hidden=false;
  status.textContent="Прямая ссылка на видеофайл распознана. Скачивание зависит от доступа к файлу и настроек браузера.";
});


function rezkaIntakePanel(){
  const s=D?.hdrezka_intake||{};
  const connected=!!D?.drive_auth?.connected;
  const driveMessage=connected?"Подключён ✓":D?.drive_auth?.message||"Требуется OAuth";
  const run=window.__m1LatestIntakeRun;
  const requestTime=Date.parse(window.__m1IntakeRequestedAt||run?.created_at||"")||0;
  const resultTime=Date.parse(s.checked_at||"")||0;
  const isRecent=requestTime>resultTime&&Date.now()-requestTime<2*3600000;
  const running=run&&["queued","pending","in_progress"].includes(run.status);
  const state=isRecent&&running
    ? "Задание GitHub Actions #"+run.id+": "+(run.status==="in_progress"?"выполняется":"в очереди")
    : isRecent&&!run ? "Запрос отправлен в GitHub Actions. Ожидаем запуска"
    : s.status==="ok"?(s.drive_uploaded?"Загружено в Drive":"Качества проверены"):
      s.status==="error"?"Не удалось: "+(s.message||s.error_code||"см. Actions"):"Проверка ещё не запускалась";
  const avail=s.available||{};
  const qualities=Object.keys(avail).length
    ? Object.entries(avail).map(([k,v])=>k+" — "+(v==="available"?"доступно":"только Premium")).join(" · ")
    : "Ещё не определены";
  return '<section class="card reveal" aria-label="HDRezka private intake">'+
    '<h2>🎞️ HDRezka → Google Drive</h2>'+
    '<p class="muted">Экспериментальный серверный загрузчик для личного хранения. Выбери качество и озвучку. Сначала проверь источник: сайт может блокировать GitHub Actions, а 1080p иногда доступно только Premium. Без DRM/капчи.</p>'+
    '<label class="f" for="hd-url">Ссылка на фильм'+
    '<input class="t" id="hd-url" type="url" inputmode="url" autocomplete="off" maxlength="600" '+
    'placeholder="https://rezka.ag/films/drama/54016-oppengeymer-2023-latest.html"></label>'+
    '<label class="f" for="hd-quality">Качество'+
    '<select class="t" id="hd-quality"><option value="1080p">1080p · для Shorts и обзоров</option><option value="720p">720p · черновик</option></select></label>'+
    '<label class="f" for="hd-translation">Озвучка (необязательно)'+
    '<input class="t" id="hd-translation" maxlength="80" placeholder="Пусто = озвучка по умолчанию"></label>'+
    '<div class="row"><button class="btn" data-hd-inspect>Проверить качество</button>'+
    '<button class="btn pri" data-hd-download '+(!connected||s.status!=="ok"?'disabled':'')+'>Скачать в Drive</button></div>'+
    '<p class="muted" role="status">Последнее действие: <span id="hd-status">'+esc(state)+'</span>'+ 
    '. Доступно: <span id="hd-qualities">'+esc(qualities)+'</span>. <span id="hd-checked">'+(s.checked_at?"Проверено "+esc(s.checked_at):"")+'</span></p>'+
    '<p class="muted">Google Drive: <span id="drive-oauth-state">'+esc(driveMessage)+'</span>. Качество проверяется отдельно. Скачивание доступно только после успешной проверки OAuth. <button class="btn sm" type="button" data-settings-section="tokens">🔐 Токены и доступы</button></p>'+
    '<p class="muted" id="hd-workflow-state" role="status">GitHub Actions: статусы проверяются автоматически, когда открыт раздел «Клипы».</p>'+
    '<a class="btn sm" id="hd-run-link" target="_blank" rel="noopener noreferrer" hidden>Открыть текущую проверку</a> '+
    '<a class="btn sm" target="_blank" rel="noopener noreferrer" href="https://github.com/osminoog09-star/Shorts/actions/workflows/hdrezka-intake.yml">Все проверки GitHub Actions</a>'+
    '</section>';
}
function rezkaInput(){
  const raw=(document.getElementById("hd-url")?.value||"").trim();
  let u;try{u=new URL(raw)}catch(e){throw new Error("Вставь полную HTTPS-ссылку на фильм")}
  const hostname=u.hostname.toLowerCase();
  if(u.protocol!=="https:"||!["rezka.ag","hdrezka.ag"].includes(hostname)||u.username||u.password||
     (u.port&&u.port!=="443")||raw.length>600||
     !/^\/films\/[a-zA-Z0-9_/-]+\.html\/?$/.test(u.pathname)||u.search||u.hash)
     throw new Error("Нужна HTTPS-страница полнометражного фильма (/films/) на rezka.ag или hdrezka.ag");
  return {url:u.href,quality:document.getElementById("hd-quality")?.value||"1080p",
          translation:(document.getElementById("hd-translation")?.value||"").trim()};
}
document.addEventListener("click",e=>{
  const button=e.target.closest("[data-hd-inspect],[data-hd-download]");
  if(!button)return;
  if(!needTok())return;
  return act(button,async()=>{
    const params=rezkaInput();
    const mode=button.hasAttribute("data-hd-download")?"download":"inspect";
    await dispatch("hdrezka-intake.yml",{...params,mode});
    window.__m1IntakeRequestedAt=new Date().toISOString();
    window.__m1IntakeMode=mode;
    const status=document.getElementById("hd-status");
    if(status)status.textContent=mode==="inspect"
      ?"Проверка отправлена в GitHub Actions. Ожидаем запуска"
      :"Загрузка запрошена в GitHub Actions. Ожидаем запуска";
    const workflow=document.getElementById("hd-workflow-state");
    if(workflow)workflow.textContent="GitHub Actions: запрос принят, отслеживаю выполнение";
    toast(mode==="inspect"?"Проверка отправлена. Смотри статус под кнопками — он обновится автоматически.":"Загрузка отправлена. Смотри статус под кнопками.");
    button.disabled=false;
  });
});
