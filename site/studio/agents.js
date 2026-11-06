/* Раздел «Агенты» студии M1lash (Claude, 06.11.2026): визуально (карточки агентов), технически (запуски GitHub Actions)
   и чат (сообщение агенту → agents/inbox/*.json в репо; ответы агенты кладут в agents/outbox/*.json — на ПК их пишет scripts/pc/agent_bridge.py). */
(() => {
  const AG = {
    'm1lash-director': { t: 'Режиссёр', c: '#b195ff', wf: [] },
    'm1lash-animator': { t: 'Аниматор', c: '#6aa0ff', wf: ['mini-strike.yml', 'motion-render.yml'] },
    'm1lash-voice': { t: 'Голос и звук', c: '#ff6bb0', wf: ['denis-voice-tts.yml', 'female-voice-design.yml'] },
    'm1lash-qa': { t: 'Контроль качества', c: '#5ee6a0', wf: ['mini-strike.yml', 'movie-short.yml'] },
    'm1lash-publisher': { t: 'Публикация', c: '#ffc65c', wf: ['youtube-direct.yml', 'playlists.yml'] },
    'm1lash-analyst': { t: 'Аналитик', c: '#7fe3ff', wf: ['youtube-analytics.yml', 'youtube-pulse.yml'] },
    'm1lash-researcher': { t: 'Ресёрчер', c: '#ff9f6b', wf: ['m1lash-news-radar.yml', 'motion-trends.yml'] },
  };
  const KEY_WF = ['youtube-pulse.yml', 'youtube-analytics.yml', 'm1lash-news-radar.yml', 'playlists.yml', 'denis-voice-tts.yml', 'female-voice-design.yml', 'mini-strike.yml', 'movie-short.yml', 'motion-pages.yml', 'youtube-direct.yml'];
  let RUNS = null, runsAt = 0, chatTo = 'm1lash-director';
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
    loadRuns();
    const S = D.studio_agents || { agents: [], chat: [] };
    const cards = S.agents.map(a => {
      const m = AG[a.id] || { t: a.id, c: '#b195ff', wf: [] };
      const busy = m.wf.some(w => { const r = lastRun(w); return r && r.st !== 'completed'; });
      const last = m.wf.map(lastRun).filter(Boolean).sort((x, y) => y.at.localeCompare(x.at))[0];
      return `<div class="card ag" style="--c:${m.c}"><span class="st ${busy ? 'on' : ''}">${busy ? '● работает' : 'ждёт'}</span>
        <div class="orb ${busy ? 'busy' : ''}"></div><h4>${e(m.t)}</h4><p>${e(((a.description.split('—')[1] || a.description).split('. ')[0]).trim())}</p>
        <div class="row2"><span class="chip">${last ? 'последний запуск ' + since(last.at) + ' назад' : 'запусков нет'}</span>
        <button class="btn" data-agchat="${e(a.id)}">Написать</button></div></div>`;
    }).join('');
    const wf = KEY_WF.map(w => { const r = lastRun(w); return `<div class="wf"><i class="${dotCls(r)}"></i><span>${e(w.replace('.yml', ''))}<br><code>${r ? (r.st !== 'completed' ? 'идёт' : r.c) + ' · ' + since(r.at) + ' назад · ' + r.ev : RUNS ? 'нет свежих запусков' : 'загрузка…'}</code></span>
      ${r ? `<a class="btn" href="${e(r.url)}" target="_blank" rel="noopener">Лог</a>` : '<span></span>'}<button class="btn" data-run="${e(w)}">Запуск</button></div>`; }).join('');
    const msgs = (S.chat || []).map(m => `<div class="msg ${m.box === 'inbox' ? 'me' : ''}"><small>${m.box === 'inbox' ? 'Ты → ' + e((AG[m.to] || {}).t || m.to) : e((AG[m.from] || {}).t || m.from || 'агент')} · ${e((m.t || '').replace('T', ' ').slice(5, 16))}</small>${e(m.text)}</div>`).join('') || '<p class="muted">Здесь будет переписка с агентами. Напиши задачу — агент на ПК возьмёт её в работу и ответит сюда.</p>';
    const opts = S.agents.map(a => `<option value="${e(a.id)}" ${a.id === chatTo ? 'selected' : ''}>${e((AG[a.id] || {}).t || a.id)}</option>`).join('');
    return `<section class="sec-row"><h2 style="margin:0;font:800 22px var(--f-d)">Агенты студии</h2><span class="chip">${S.agents.length} агентов · Claude + GPT</span></section>
      <div class="ag-grid">${cards}</div>
      <div class="card" style="padding:16px"><div class="sec-row"><b>Техническая панель · GitHub Actions</b><span class="chip">${RUNS ? 'обновлено ' + since(new Date(runsAt).toISOString()) + ' назад' : '…'}</span></div>${wf}</div>
      <div class="card" style="padding:16px"><div class="sec-row"><b>Чат с агентами</b><span class="chip">ответы приходят с ПК</span></div>
        <div class="chat" id="chatbox">${msgs}</div>
        <div class="chatin"><select id="chatTo">${opts}</select><input id="chatIn" placeholder="Например: сделай скетч про робота-курьера" autocomplete="off"><button class="btn pri" id="chatSend">Отправить</button></div></div>`;
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

  TABS.push(['agents', 'Агенты', 'idea']);
  VIEWS.agents = view;
  if (store.get('m1-tab2', '') === 'agents') tab = 'agents';
  document.addEventListener('click', ev => {
    const b = ev.target.closest('#chatSend'); if (b) return send(b);
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
