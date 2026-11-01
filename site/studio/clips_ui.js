/* M1lash Drive intake UI: ONE public folder for future clips, not re-requests for existing 7.
   Browser writes JSON with owner's GitHub token; read-only scheduled scanner handles matching.
   No fake ready status: ASR, licensing and media QA are separate gates.
*/
function clips(){
  const req=(D.clip_requests||{}).items||[];
  const scan=D.drive_scan||{};
  const folder=D.drive_folder||{};
  const found=new Map((scan.items||[]).map(x=>[x.id,x]));
  const missing=req.filter(r=>!["собран","сцена найдена"].includes((found.get(r.id)||{}).status||r.status)).length;
  const active=!!folder.scan_enabled&&!!folder.url;
  const stat=scan.status==="ok"
    ? 'В папке '+num(scan.file_count)+' файлов, из них видео '+num(scan.video_files)+
      ' · нужно фильмов '+num(scan.required_film_count)+
      ' · найдено '+num(scan.matched_film_count)
    : scan.status==="error"?'Ошибка сканирования: '+esc(scan.message||"доступ закрыт")
    : 'Папка ещё не подключена. Уже собранные 7 видео повторно скачивать не нужно.';
  let html='<section class="card reveal"><h2>Одна папка Google Drive</h2>'+
    '<p class="muted">Для новых кино-сцен. Фильмы целиком, русская актёрская дорожка. Доступ: «Все, у кого есть ссылка». Не загружай сюда исходники для уже собранных 7 роликов повторно.</p>'+
    '<label class="muted" for="drive-folder-url">Папка Google Drive</label>'+
    '<input class="t" id="drive-folder-url" type="url" inputmode="url" autocomplete="off" placeholder="https://drive.google.com/drive/folders/…" value="'+esc(folder.url||"")+'">'+
    '<div class="row"><button class="btn pri" data-folder-save>Сохранить папку</button>'+
    '<button class="btn" data-folder-scan '+(!active?'disabled':'')+'>Проверить папку</button></div>'+
    '<p class="muted">'+stat+'</p>'+
    ((scan.missing||[]).length?'<p class="muted">Не хватает: '+(scan.missing||[]).map(esc).join(' · ')+'</p>':'')+
    '<p class="muted">Последняя проверка: '+esc(scan.scanned_at||"ещё не было")+
    '. Сканер пока определяет файлы, но не скачивает фильмы и не заявляет о готовом монтаже.</p></section>';
  html+='<section class="card reveal"><h2>Заявки <span class="cnt">'+missing+' ожидают исходники/сцены</span></h2>'+
    '<p class="muted">Без ссылок на каждую сцену: сканер сопоставляет фильмы автоматически. При неоднозначности — подтверждение ниже.</p></section>';
  html+='<div class="grid">'+req.map(r=>{
    const id=esc(r.id);
    const m=found.get(r.id)||{};
    const state=r.status==="собран"?"собран":(m.status||"нет фильма в папке");
    const choices=(m.candidates||[]);
    const chosen=!!choices.length?
      '<label class="muted" for="match-'+id+'">Это тот фильм?</label>'+
      '<select class="t" id="match-'+id+'">'+choices.map((p,i)=>'<option value="'+i+'">'+esc(p)+'</option>').join('')+'</select>'+
      '<button class="btn sm" data-clip-confirm="'+id+'">Подтвердить соответствие</button>':'';
    return '<section class="idea reveal"><div class="row"><span class="chip">'+esc(state)+
      '</span><span class="muted">'+esc(r.minute||"")+'</span></div><b>'+esc(r.film||"")+
      '</b><p>'+esc(r.scene||"")+'</p><p class="muted">'+esc(r.why||"")+
      '</p>'+(m.filename?'<p class="muted">В папке: '+esc(m.filename)+'</p>':'')+
      (m.scene_start!=null?'<p class="muted">Найдено с '+Math.floor(m.scene_start/60)+':'+String(Math.floor(m.scene_start%60)).padStart(2,"0")+'</p>':'')+
      chosen+'<p class="muted">'+esc(r.note||"")+'</p></section>';
  }).join('')+'</div>';
  html+='<section class="card reveal"><h2>Своя заявка</h2>'+
      '<label class="muted" for="newclip-film">Фильм и год</label><input id="newclip-film" class="t" maxlength="120" placeholder="Название фильма (2022)">'+
      '<label class="muted" for="newclip-note">Какая сцена?</label><input id="newclip-note" class="t" maxlength="200" placeholder="Опиши сцену">'+
      '<button class="btn pri" data-clip-add>Добавить заявку</button></section>';
  return html;
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