/* M1lash studio clip-requests UI. Save only links into repo JSON.
   Automated media fetch/assembly is a separate gated workflow: never claim upload.
*/
function clips(){
  const req=(D.clip_requests||{}).items||[];
  const missing=req.filter(r=>r.status==="нужен").length;
  let html='<section class="card reveal"><h2>Киноисходники <span class="cnt">'+missing+' нужно</span></h2>'+
    '<p class="muted">Русская актёрская дорожка обязательна. Нажми «Сохранить ссылку» — она попадёт в GitHub. Автоматическое скачивание пока не подключено.</p></section>';
  html+='<div class="grid">'+req.map(r=>{
    const id=esc(r.id), status=esc(r.status||"нужен");
    return '<section class="idea reveal"><div class="row"><span class="chip">'+status+
      '</span><span class="muted">'+esc(r.minute||"")+'</span></div><b>'+esc(r.film||"")+
      '</b><p>'+esc(r.scene||"")+'</p><p class="muted">'+esc(r.why||"")+
      '</p><label class="muted" for="clip-'+id+'">Ссылка на фильм или клип (Google Drive)</label>'+
      '<input class="t" id="clip-'+id+'" type="url" inputmode="url" autocomplete="off" '+
      'placeholder="https://drive.google.com/file/d/…" value="'+esc(r.link||"")+'">'+
      '<div class="row"><button class="btn sm pri" data-clip-save="'+id+'">Сохранить ссылку</button>'+
      '<span class="muted">'+esc(r.note||"")+'</span></div></section>';
  }).join('')+'</div>';
  html+='<section class="card reveal"><h2>Свой клип</h2>'+
      '<label class="muted" for="newclip-link">Ссылка</label><input id="newclip-link" class="t" type="url" placeholder="https://drive.google.com/file/d/…">'+
      '<label class="muted" for="newclip-note">Какая сцена?</label><input id="newclip-note" class="t" type="text" maxlength="200" placeholder="Опиши сцену">'+
      '<button class="btn pri" data-clip-add>Сохранить свой клип</button></section>';
  return html;
}
function clipUrl(raw){
  let u;try{u=new URL(raw)}catch(e){throw new Error("Нужна полная ссылка https://")}
  if(u.protocol!=="https:"||!u.hostname||u.username||u.password||raw.length>2048)throw new Error("Нужна безопасная ссылка https://");
  return u.href;
}
document.addEventListener("click",e=>{
  let b=e.target.closest("[data-clip-save]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      const id=b.dataset.clipSave;
      const input=document.getElementById("clip-"+id);
      const url=clipUrl((input?.value||"").trim());
      const data=await editJSON("publishing/clip_requests.json",d=>{
        const row=(d.items||[]).find(x=>x.id===id);
        if(!row)throw new Error("Заявка не найдена");
        row.link=url;row.status="ссылка есть";row.updated=new Date().toISOString().slice(0,10);
        d.updated=row.updated;
      },"studio: clip link provided "+id);
      D.clip_requests=data;render();toast("Ссылка сохранена. Автоимпорт ещё не подключён.");
    });
  }
  b=e.target.closest("[data-clip-add]");
  if(b){
    if(!needTok())return;
    return act(b,async()=>{
      const url=clipUrl((document.getElementById("newclip-link")?.value||"").trim());
      const note=(document.getElementById("newclip-note")?.value||"").trim();
      if(note.length<4)throw new Error("Опиши сцену хотя бы в четырёх символах");
      const id="custom-"+Date.now().toString(36);
      const data=await editJSON("publishing/clip_requests.json",d=>{
        d.items=d.items||[];
        d.items.push({id,film:"Свой клип",scene:note,minute:"—",why:"Заявка владельца",
          for:"Новый кино-Shorts",status:"ссылка есть",link:url,note:"Требуется настоящий русский дубляж",
          updated:new Date().toISOString().slice(0,10)});
        d.updated=new Date().toISOString().slice(0,10);
      },"studio: custom clip request "+id);
      D.clip_requests=data;render();toast("Заявка сохранена в GitHub.");
    });
  }
});
