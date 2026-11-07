/* Раздел «Агенты» студии M1lash (Claude, 06.11.2026): визуально (карточки агентов), технически (запуски GitHub Actions)
   и чат (сообщение агенту → agents/inbox/*.json в репо; ответы агенты кладут в agents/outbox/*.json — на ПК их пишет scripts/pc/agent_bridge.py). */
(() => {
  const AG = {
    'm1lash-studio-director': { t: 'Директор студии', c: '#ffffff', wf: [], boss: 1 },
    'm1lash-scout': { t: 'Скаут материала', c: '#9be15d', wf: ['material-scout.yml'] },
    'm1lash-editor': { t: 'Монтажёр кино-Shorts', c: '#ff5f7a', wf: ['movie-short.yml'] },
    'm1lash-cartoon-shorts': { t: 'Мульт-Shorts', c: '#ff9de2', wf: ['mini-strike.yml'] },
    'm1lash-film-mult': { t: 'Длинные мультфильмы', c: '#8fd3ff', wf: ['render-long.yml', 'join-long.yml'] },
    'm1lash-writer': { t: 'Сценарист скетчей', c: '#c6ff6b', wf: [] },
    'm1lash-packaging': { t: 'Обложки и SEO', c: '#ffd36b', wf: [] },
    'm1lash-community': { t: 'Подписчики и комментарии', c: '#6bffe1', wf: ['youtube-pulse.yml'] },
    'm1lash-gaming-lead': { t: 'Игры · руководитель', c: '#7cff6b', wf: [], dep: 'Игровой отдел' },
    'm1lash-game-editor': { t: 'Игры · монтаж серий', c: '#5fd36b', wf: [], dep: 'Игровой отдел' },
    'm1lash-game-clipper': { t: 'Игры · Shorts', c: '#b6ff6b', wf: [], dep: 'Игровой отдел' },
    'm1lash-stream-producer': { t: 'Игры · стримы', c: '#6bffb0', wf: [], dep: 'Игровой отдел' },
    'm1lash-director': { t: 'Режиссёр', c: '#b195ff', wf: [] },
    'm1lash-animator': { t: 'Аниматор', c: '#6aa0ff', wf: ['mini-strike.yml', 'motion-render.yml'] },
    'm1lash-voice': { t: 'Голос и звук', c: '#ff6bb0', wf: ['denis-voice-tts.yml', 'female-voice-design.yml'] },
    'm1lash-qa': { t: 'Контроль качества', c: '#5ee6a0', wf: ['mini-strike.yml', 'movie-short.yml'] },
    'm1lash-publisher': { t: 'Публикация', c: '#ffc65c', wf: ['youtube-direct.yml', 'playlists.yml'] },
    'm1lash-analyst': { t: 'Аналитик', c: '#7fe3ff', wf: ['youtube-analytics.yml', 'youtube-pulse.yml'] },
    'm1lash-researcher': { t: 'Ресёрчер', c: '#ff9f6b', wf: ['m1lash-news-radar.yml', 'motion-trends.yml'] },
  };
  const KEY_WF = ['youtube-pulse.yml', 'youtube-analytics.yml', 'm1lash-news-radar.yml', 'playlists.yml', 'denis-voice-tts.yml', 'female-voice-design.yml', 'mini-strike.yml', 'movie-short.yml', 'motion-pages.yml', 'youtube-direct.yml'];
  // Решение Дениса 06.11 18:23: агенты на ПК отменены — чат/режимы/циклы никто не читает (аудит 07.11).
  const AGENTS_OFF = true;
  const NEEDS_INPUT = new Set(['denis-voice-tts.yml', 'female-voice-design.yml', 'movie-short.yml', 'youtube-direct.yml']);
  let PC = null, pcAt = 0;
  async function loadPC() {
    if (Date.now() - pcAt < 120000) return; pcAt = Date.now();
    try { const r = await fetch('https://raw.githubusercontent.com/' + REPO + '/pc-status/status.json?t=' + Date.now(), { cache: 'no-store' }); PC = r.ok ? await r.json() : { none: 1 }; } catch (err) { PC = { none: 1 }; }
    if (tab === 'agents') render();
  }
  let RUNS = null, runsAt = 0, chatTo = 'm1lash-studio-director';
  const e = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const since = iso => { if (!iso) return '—'; const m = Math.round((Date.now() - new Date(iso)) / 60000); return m < 60 ? m + ' мин' : m < 1440 ? Math.round(m / 60) + ' ч' : Math.round(m / 1440) + ' д'; };

  async function loadRuns() {
    if (RUNS && Date.now() - runsAt < 60000) return;
    try {
      const r = await fetch('https://api.github.com/repos/' + REPO + '/actions/runs?per_page=60', { cache: 'no-store', headers: tok() ? { Authorization: 'Bearer ' + tok() } : {} });
      const j = await r.json(); RUNS = (j.workflow_runs || []).map(x => ({ wf: x.path.split('/').pop(), st: x.status, c: x.conclusion, at: x.created_at, url: x.html_url, ev: x.event }));
      runsAt = Date.now(); if (tab === 'agents') render();
    } catch (err) { RUNS = RUNS || []; }
  }
  const lastRun = wf => (RUNS || []).find(r => r.wf === wf);
  const dotCls = r => !r ? '' : r.st !== 'completed' ? 'run' : r.c === 'success' ? '' : 'fail';

  function view() {
    loadRuns(); loadPC();
    const S = D.studio_agents || { agents: [], chat: [] };
    const DEP = { 'm1lash-studio-director': 'Руководство', 'm1lash-scout': 'Кино-Shorts', 'm1lash-editor': 'Кино-Shorts',
      'm1lash-cartoon-shorts': 'Мультфильмы и скетчи', 'm1lash-film-mult': 'Мультфильмы и скетчи', 'm1lash-writer': 'Мультфильмы и скетчи', 'm1lash-director': 'Мультфильмы и скетчи', 'm1lash-animator': 'Мультфильмы и скетчи' };
    const depOf = id => (AG[id] || {}).dep || DEP[id] || 'Общие службы';
    const DORDER = ['Руководство', 'Кино-Shorts', 'Мультфильмы и скетчи', 'Игровой отдел', 'Общие службы'];
    const ORDER = Object.keys(AG);
    const list = S.agents.slice().sort((x, y) => (DORDER.indexOf(depOf(x.id)) - DORDER.indexOf(depOf(y.id))) || ((ORDER.indexOf(x.id) + 1 || 99) - (ORDER.indexOf(y.id) + 1 || 99)));
    let lastDep = '';
    const cards = list.map(a => {
      const dp = depOf(a.id), head = dp !== lastDep && dp !== 'Руководство' ? `<h3 class="dep">${e(dp)}</h3>` : ''; lastDep = dp;
      const m = AG[a.id] || { t: a.id, c: '#b195ff', wf: [] };
      const busy = m.wf.some(w => { const r = lastRun(w); return r && r.st !== 'completed'; });
      const last = m.wf.map(lastRun).filter(Boolean).sort((x, y) => y.at.localeCompare(x.at))[0];
      return head + `<div class="card ag${m.boss ? ' boss' : ''}" style="--c:${m.c}">${m.boss ? '<span class="lead">главный · сам раздаёт задачи · 08:30 · 13:30 · 19:30</span>' : ''}<span class="st ${busy ? 'on' : ''}">${busy ? '● работает' : 'ждёт'}</span>
        <div class="orb ${busy ? 'busy' : ''}"></div><h4>${e(m.t)}</h4><p>${e(((a.description.split('—')[1] || a.description).split('. ')[0]).trim())}</p>
        <div class="row2"><span class="chip">${last ? 'последний запуск ' + since(last.at) + ' назад' : 'запусков нет'}</span>
        <button class="btn" data-agchat="${e(a.id)}">Написать</button></div></div>`;
    }).join('');
    const wf = KEY_WF.map(w => { const r = lastRun(w); return `<div class="wf"><i class="${dotCls(r)}"></i><span>${e(w.replace('.yml', ''))}<br><code>${r ? (r.st !== 'completed' ? 'идёт' : r.c) + ' · ' + since(r.at) + ' назад · ' + r.ev : RUNS ? 'нет свежих запусков' : 'загрузка…'}</code></span>
      ${r ? `<a class="btn" href="${e(r.url)}" target="_blank" rel="noopener">Лог</a>` : '<span></span>'}${NEEDS_INPUT.has(w) ? '<small class="muted">запуск — из задачи</small>' : `<button class="btn" data-run="${e(w)}">Запуск</button>`}</div>`; }).join('');
    const msgs = (S.chat || []).map(m => `<div class="msg ${m.box === 'inbox' ? 'me' : ''}"><small>${m.box === 'inbox' ? 'Ты → ' + e((AG[m.to] || {}).t || m.to) : e((AG[m.from] || {}).t || m.from || 'агент')} · ${e((m.t || '').replace('T', ' ').slice(5, 16))}</small>${e(m.text)}</div>`).join('') || '<p class="muted">Здесь будет переписка с агентами. Напиши задачу — агент на ПК возьмёт её в работу и ответит сюда.</p>';
    const opts = list.map(a => `<option value="${e(a.id)}" ${a.id === chatTo ? 'selected' : ''}>${e((AG[a.id] || {}).t || a.id)}</option>`).join('');
    const ST = D.studio_settings || {}, BF = D.studio_buffer || { grid: [], covered_days: 0, days: 7, ready_unscheduled: 0 };
    const dot = ok => `<i class="bd ${ok ? 'ok' : ''}"></i>`;
    const wd = d => ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'][new Date(d + 'T12:00:00').getDay()];
    const ctl = `<div class="card ctl" style="padding:16px">
      <div class="sec-row"><b>Управление студией</b><span class="chip ${ST.paused ? 'warn' : 'on'}">${ST.paused ? '⏸ публикация на паузе' : (ST.autonomy === 'full' ? '● полный автопилот' : '● до приватной заливки')}</span></div>
      <div class="mode">${[['on', '▶ Студия работает'], ['game', '🎮 Игровой режим'], ['off', '■ Выключена']].map(([k, t]) => `<button class="btn ${(ST.mode || 'on') === k ? 'cur m-' + k : ''}" data-mode="${k}">${t}</button>`).join('')}</div>
      <small class="mhint">${(ST.mode || 'on') === 'game' ? 'Агенты стоят, видеокарта свободна для игры. Записи из папки игр обработаются после включения.' : (ST.mode || 'on') === 'off' ? 'Всё стоит: агенты, циклы директора, подготовка записей. Опубликованное по расписанию выйдет само.' : 'Агенты работают по циклам. Перед игрой включи игровой режим — тут или ярлыком «Панель M1lash» на ПК.'}</small>
      <div class="pc">${!PC ? 'ПК: проверяю…' : PC.none ? '<i class="bd"></i> ПК ещё не подключён — после установки <code>setup.ps1</code> здесь будет его статус' : (() => { const age = (Date.now() - new Date(PC.t)) / 60000; const on = age < 25; return `<i class="bd ${on ? 'ok' : ''}"></i> ПК ${on ? 'онлайн' + (PC.mode && PC.mode !== 'on' ? (PC.mode === 'game' ? ' · 🎮 игровой режим' : ' · студия выключена') : '') : 'офлайн ' + since(PC.t) + ' назад'} · модель ${e(PC.local_model)} ${PC.ollama ? '' : '(Ollama выкл.)'} · Claude осталось ${e(PC.claude_left)}/${e(PC.claude_cap)} · цикл ${PC.last_cycle ? since(PC.last_cycle) + ' назад' : '—'}`; })()}</div>
      <div class="buf"><div class="bufh">Запас на ${BF.days} дн.: <b>${BF.covered_days}</b> дн. закрыто подряд · готово без даты: ${BF.ready_unscheduled}</div>
        <div class="bufg">${BF.grid.map(g => `<div><small>${wd(g.day)} ${g.day.slice(8)}</small>${dot(g.kino)}${dot(g.sketch)}</div>`).join('')}</div>
        <div class="bufl"><span>${dot(1)} кино ${e((ST.slots || {}).kino || '10:00')}</span><span>${dot(1)} скетч ${e((ST.slots || {}).sketch || '20:00')}</span></div></div>
      <div class="sets">
        <label>Режим<select id="s_aut"><option value="full" ${ST.autonomy === 'full' ? 'selected' : ''}>Полностью сам (и дату ставит)</option><option value="review" ${ST.autonomy !== 'full' ? 'selected' : ''}>До приватной заливки, дату ставлю я</option></select></label>
        <label>Запас вперёд<select id="s_buf">${[3, 5, 7, 10, 14].map(n => `<option ${+ST.buffer_days === n ? 'selected' : ''}>${n}</option>`).join('')}</select></label>
        <label>Кино-Shorts<input id="s_kino" value="${e((ST.slots || {}).kino || '10:00')}"></label>
        <label>Скетч<input id="s_sk" value="${e((ST.slots || {}).sketch || '20:00')}"></label>
        <label>Циклы директора<input id="s_cyc" value="${e((ST.director_cycles || []).join(', '))}"></label>
        <label>Claude в сутки (макс.)<input id="s_cap" type="number" min="0" max="20" value="${e(ST.claude_daily_cap ?? 4)}"></label>
        <label>Где рендер и голос<select id="s_cmp"><option value="auto" ${(ST.compute || 'auto') === 'auto' ? 'selected' : ''}>Авто: ПК, в игре — GitHub</option><option value="pc" ${ST.compute === 'pc' ? 'selected' : ''}>Только ПК</option><option value="actions" ${ST.compute === 'actions' ? 'selected' : ''}>Только GitHub Actions</option></select></label>
        <label>Локальная модель<input id="s_llm" value="${e(ST.local_model || 'auto')}"></label>
        <label>Серии игр<input id="s_game" value="${e((ST.gaming || {}).series_slot || 'вс 15:00')}"></label>
        <label class="tg"><input id="s_gon" type="checkbox" ${(ST.gaming || {}).enabled !== false ? 'checked' : ''}> Игровой отдел включён</label>
        <label class="tg"><input id="s_rep" type="checkbox" ${ST.auto_replies ? 'checked' : ''}> Сам отвечает подписчикам</label>
      </div>
      ${(() => { const C = D.clip_sources || { sources: [] }; return `<div class="clips"><b>Запись фрагментов фильмов</b> <small>агент записывает кусок фильма в браузере ПК только с сайтов из этого списка</small>
        <div class="sets">
          <label class="tg"><input id="c_on" type="checkbox" ${C.enabled !== false ? 'checked' : ''}> Запись включена</label>
          <label>Длина фрагмента, с<input id="c_len" type="number" min="10" max="${e(C.max_fragment_sec || 60)}" value="${e(C.default_fragment_sec || 45)}"></label>
          <label>Фрагментов с фильма<input id="c_per" type="number" min="1" max="10" value="${e(C.max_per_film || 3)}"></label>
        </div>
        <div class="srcs">${(C.sources || []).map((x, i) => `<label class="tg src"><input type="checkbox" data-src="${i}" ${x.enabled !== false ? 'checked' : ''}> <span><b>${e(x.name || x.domain)}</b> · ${e(x.domain)} ${x.legal ? '' : '<em class="wait">выключен</em>'}</span><button class="btn del" data-srcdel="${e(x.domain)}" title="Удалить сайт">✕</button></label>`).join('') || '<small>Сайтов нет — предложи ниже</small>'}</div>
        <div class="chatin"><input id="c_new" placeholder="Добавить сайт: адрес (например, kino.example.ru)"><button class="btn" id="c_add">Добавить</button></div>
        <label class="tg"><input id="c_ok" type="checkbox"> Подтверждаю, что запись и использование выбранных материалов разрешены правообладателем либо другими имеющимися правами</label></div>`; })()}
      <div class="row2"><button class="btn pri" id="s_save">Сохранить</button><button class="btn" id="s_pause">${ST.paused ? '▶ Вернуть публикацию' : '⏸ Не публиковать'}</button><button class="btn" id="s_cycle">Цикл директора сейчас</button></div></div>`;
    if (AGENTS_OFF) {
      const buf = `<div class="card ctl" style="padding:16px"><div class="sec-row"><b>Студия</b><span class="chip warn">агенты на ПК отключены</span></div>
        <small class="mhint">06.11 ты отменил автономных агентов. Всё производство теперь идёт через Claude в чате, а даты ставишь ты: «Ролики → Очередь и план → Выбрать время». Здесь остались запас по сетке и техпанель GitHub Actions.</small>
        <div class="buf"><div class="bufh">Запас на ${BF.days} дн.: <b>${BF.covered_days}</b> дн. закрыто подряд · готово без даты: ${BF.ready_unscheduled}</div>
        <div class="bufg">${BF.grid.map(g => `<div><small>${wd(g.day)} ${g.day.slice(8)}</small>${dot(g.kino)}${dot(g.sketch)}</div>`).join('')}</div>
        <div class="bufl"><span>${dot(1)} кино ${e((ST.slots || {}).kino || '10:00')}</span><span>${dot(1)} скетч ${e((ST.slots || {}).sketch || '20:00')}</span></div></div></div>`;
      return `${buf}<div class="card" style="padding:16px"><div class="sec-row"><b>Техническая панель · GitHub Actions</b><span class="chip">${RUNS ? 'обновлено ' + since(new Date(runsAt).toISOString()) + ' назад' : '…'}</span></div>${wf}</div>`;
    }
    return `${ctl}<section class="sec-row"><h2 style="margin:0;font:800 22px var(--f-d)">Агенты студии</h2><span class="chip">${S.agents.length} агентов · директор + отделы</span></section>
      <div class="ag-grid">${cards}</div>
      <div class="card" style="padding:16px"><div class="sec-row"><b>Техническая панель · GitHub Actions</b><span class="chip">${RUNS ? 'обновлено ' + since(new Date(runsAt).toISOString()) + ' назад' : '…'}</span></div>${wf}</div>
      <div class="card" style="padding:16px"><div class="sec-row"><b>Чат с агентами</b><span class="chip">ответы приходят с ПК</span></div>
        <div class="chat" id="chatbox">${msgs}</div>
        <div class="chatin"><select id="chatTo">${opts}</select><input id="chatIn" placeholder="Например: сделай скетч про робота-курьера" autocomplete="off"><button class="btn pri" id="chatSend">Отправить</button></div></div>`;
  }

  async function saveSettings(btn, patch) {
    if (!needTok()) return;
    const cyc = ($('#s_cyc')?.value || '').split(/[ ,;]+/).filter(x => /^\d{1,2}:\d{2}$/.test(x));
    await act(btn, async () => {
      const d = await editJSON('publishing/studio_settings.json', s => {
        Object.assign(s, patch || {
          autonomy: $('#s_aut').value, buffer_days: +$('#s_buf').value,
          slots: Object.assign(s.slots || {}, { kino: $('#s_kino').value.trim(), sketch: $('#s_sk').value.trim() }),
          director_cycles: cyc.length ? cyc : s.director_cycles, claude_daily_cap: Math.max(0, Math.min(20, +$('#s_cap').value || 0)),
          local_model: $('#s_llm').value.trim() || 'auto', auto_replies: $('#s_rep').checked, compute: $('#s_cmp').value,
          gaming: Object.assign(s.gaming || {}, { series_slot: $('#s_game').value.trim(), enabled: $('#s_gon').checked }),
        });
        s.updated = new Date().toISOString(); s.updated_by = 'Денис (сайт)';
      }, 'studio: настройки автономии (Денис, с сайта)');
      D.studio_settings = Object.fromEntries(Object.entries(d).filter(([k]) => !k.startsWith('_')));
      if (!patch && $('#c_on')) {
        const c = await editJSON('publishing/clip_sources.json', c => {
          c.enabled = $('#c_on').checked;
          c.default_fragment_sec = Math.max(10, Math.min(c.max_fragment_sec || 60, +$('#c_len').value || 45));
          c.max_per_film = Math.max(1, Math.min(10, +$('#c_per').value || 3));
          document.querySelectorAll('[data-src]').forEach(el => { const s = c.sources[+el.dataset.src]; if (s) s.enabled = el.checked; });
        }, 'studio: настройки записи фрагментов (Денис, с сайта)');
        D.clip_sources = Object.fromEntries(Object.entries(c).filter(([k]) => !k.startsWith('_')));
      }
      render(); toast('Сохранено — агенты возьмут при следующем цикле ✓'); btn.disabled = false;
    });
  }

  async function proposeSite(btn) {
    const raw = ($('#c_new').value || '').trim(); if (!raw || !needTok()) return;
    if (!$('#c_ok').checked) return toast('Подтверди право на запись и использование материалов');
    let host = ''; try { host = new URL(/^https?:/.test(raw) ? raw : 'https://' + raw).hostname.replace(/^www\./, ''); } catch (err) { return toast('Не похоже на адрес сайта'); }
    await act(btn, async () => {
      const c = await editJSON('publishing/clip_sources.json', c => {
        if (!c.sources.some(s => s.domain === host)) c.sources.push({ domain: host, name: host, legal: true, enabled: true, added: new Date().toISOString().slice(0, 10), added_by: 'Денис (сайт): подтвердил права на запись и использование выбранных материалов' });
      }, 'studio: добавлен сайт записи фрагментов ' + host + ' (Денис, с сайта)');
      D.clip_sources = Object.fromEntries(Object.entries(c).filter(([k]) => !k.startsWith('_')));
      render(); toast('Сайт добавлен ✓ агент может брать с него'); btn.disabled = false;
    });
  }

  async function delSite(btn) {
    const host = btn.dataset.srcdel; if (!needTok()) return;
    await act(btn, async () => {
      const c = await editJSON('publishing/clip_sources.json', c => { c.sources = c.sources.filter(s => s.domain !== host); }, 'studio: удалён сайт записи фрагментов ' + host + ' (Денис, с сайта)');
      D.clip_sources = Object.fromEntries(Object.entries(c).filter(([k]) => !k.startsWith('_')));
      render(); toast('Сайт удалён ✓');
    });
  }

  async function send(btn) {
    const text = ($('#chatIn').value || '').trim(); if (!text) return;
    if (!needTok()) return;
    chatTo = $('#chatTo').value;
    const t = new Date().toISOString().replace(/\.\d+Z$/, 'Z'), id = t.replace(/[-:TZ]/g, '') + '-' + chatTo;
    const msg = { id, t, from: 'denis', to: chatTo, text, status: 'new' };
    await act(btn, async () => {
      await gh('/contents/agents/inbox/' + id + '.json', { method: 'PUT', body: JSON.stringify({ message: 'agents: сообщение Дениса → ' + chatTo + ' (с сайта)', content: b64e(JSON.stringify(msg, null, 2) + '\n'), branch: 'main' }) });
      (D.studio_agents = D.studio_agents || { agents: [], chat: [] }).chat.push({ ...msg, box: 'inbox' });
      $('#chatIn').value = ''; render(); toast('Отправлено агенту ✓'); btn.disabled = false;
    });
  }

  // 07.11.2026: агенты студии отменены (AGENTS §2, решение Дениса) — вкладку «Агенты» больше не показываем.
  // Код раздела оставлен как история; чтобы вернуть, раскомментировать две строки ниже.
  // TABS.push(['agents', 'Агенты', 'idea']);
  // VIEWS.agents = view;
  if (tab === 'agents' || store.get('m1-tab2', '') === 'agents') { tab = TABS[0][0]; try { store.set('m1-tab2', tab); } catch (e) {} }
  document.addEventListener('click', ev => {
    const b = ev.target.closest('#chatSend'); if (b) return send(b);
    const sv = ev.target.closest('#s_save'); if (sv) return saveSettings(sv);
    const ca = ev.target.closest('#c_add'); if (ca) return proposeSite(ca);
    const cd = ev.target.closest('[data-srcdel]'); if (cd) { ev.preventDefault(); return delSite(cd); }
    const ps = ev.target.closest('#s_pause'); if (ps) return saveSettings(ps, { paused: !(D.studio_settings || {}).paused });
    const md = ev.target.closest('[data-mode]'); if (md) return saveSettings(md, { mode: md.dataset.mode });
    const cy = ev.target.closest('#s_cycle'); if (cy) { $('#chatTo').value = 'm1lash-studio-director'; $('#chatIn').value = 'Выполни цикл студии сейчас'; return send($('#chatSend')); }
    const a = ev.target.closest('[data-agchat]'); if (a) { chatTo = a.dataset.agchat; render(); setTimeout(() => $('#chatIn')?.focus(), 50); }
  });
  document.addEventListener('keydown', ev => { if (ev.key === 'Enter' && ev.target.id === 'chatIn') send($('#chatSend')); });
  // верхняя «таблетка» вкладок на компьютере
  const top = document.querySelector('.top'); const tt = document.createElement('nav'); tt.id = 'toptabs'; tt.setAttribute('aria-label', 'Разделы');
  top.querySelector('.t').after(tt);
  const _render = render;
  render = function () { _render(); tt.innerHTML = TABS.map(([k, t]) => `<button data-tab="${k}" ${tab === k ? 'aria-current="page"' : ''}>${t}</button>`).join(''); const c = $('#chatbox'); if (c) c.scrollTop = c.scrollHeight; };
  if (D) render();
})();
