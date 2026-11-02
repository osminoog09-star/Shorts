/* M1lash Studio: background refresh without page reload (all tabs, source statuses, hourly pulse).
   YouTube counters are as fresh as the API/Actions snapshots, NOT per-second realtime.
   No token, entered URL, or source media is uploaded by this module. */
(() => {
  "use strict";
  const PAGE_MS = 15000;
  const PULSE_MS = 30000;
  const STATUS_MS = 12000;
  const STATUS_BASE = "https://raw.githubusercontent.com/osminoog09-star/Shorts/main/publishing/";
  const PULSE_URL = "https://raw.githubusercontent.com/osminoog09-star/Shorts/pulse-data/pulse.json";
  let pageKey = null, pulseKey = null, pulseData = null;
  let pageBusy = false, pulseBusy = false, statusBusy = false, needsRender = false, lastError = false;
  const latestStatuses = {};
  let pendingData = null;

  const isVisible = () => !document.hidden && navigator.onLine !== false;
  const pageFingerprint = d => JSON.stringify({
    ...d, live:null, comments:null, comments_status:null, channel:null
  });
  const currentPulse = p => Array.isArray(p?.snapshots) && p.snapshots.length
    ? p.snapshots[p.snapshots.length - 1] : null;
  const timeMs = s => {
    const ms = Date.parse(s || "");
    return Number.isFinite(ms) ? ms : 0;
  };
  function hourlyValue(snaps, last, hours, key) {
    const target = timeMs(last.t) - hours * 3600000;
    if (!snaps.length || target < timeMs(snaps[0].t)) return null;
    for (let i = 1; i < snaps.length; i++) {
      const a = snaps[i - 1], b = snaps[i], ta = timeMs(a.t), tb = timeMs(b.t);
      if (ta <= target && target <= tb && tb > ta) {
        const fraction = (target - ta) / (tb - ta);
        return Math.round((a[key] || 0) + ((b[key] || 0) - (a[key] || 0)) * fraction);
      }
    }
    return last[key] ?? null;
  }
  function updateHeader() {
    if (!D) return;
    const stamp = D.live?.t, ageMin = stamp ? (Date.now() - timeMs(stamp)) / 60000 : Infinity;
    const marker = ageMin > 35 ? " · данные устарели" : " · автообновление каждые 15 с";
    const display = stamp ? "счётчики " + ago(stamp) + " назад" :
      "аналитика по " + dshort(D.analytics_as_of);
    const elem = document.getElementById("asof");
    if (elem) elem.textContent = (lastError ? "Сеть недоступна · " : "") + display + marker;
  }
  function preserveClipFormsAndRender() {
    const controls = tab === "clips"
      ? [...document.querySelectorAll("#view input[id],#view select[id],#view textarea[id]")]
        .filter(el => el.id.startsWith("hd-") || el.id === "media-url" ||
                        el.id === "drive-folder-url" || el.id.startsWith("newclip-"))
        .map(el => ({id:el.id,value:el.value}))
      : [];
    render();
    for (const field of controls) {
      const el = document.getElementById(field.id);
      if (el) el.value = field.value;
    }
  }
  function patchClipStatus() {
    if (tab !== "clips") return;
    const s = D?.hdrezka_intake || {};
    const text = document.getElementById("hd-status");
    if (text) text.textContent = s.status === "ok"
      ? (s.drive_uploaded ? "Файл загружен в Drive" : "Качества проверены")
      : s.status === "error" ? "Не удалось: " + (s.message || s.error_code || "см. Actions")
      : "Проверка ещё не запускалась";
    const qualities = document.getElementById("hd-qualities");
    if (qualities) qualities.textContent = Object.entries(s.available || {})
      .map(([k,v]) => k + " — " + (v === "available" ? "доступно" : "только Premium"))
      .join(" · ") || "Ещё не определены";
    const checked = document.getElementById("hd-checked");
    if (checked) checked.textContent = s.checked_at ? "Проверено " + s.checked_at : "";
    const drive = D?.drive_auth || {};
    const driveState = document.getElementById("drive-oauth-state");
    if (driveState) driveState.textContent = drive.connected ? "Подключён ✓" : drive.message || "Требуется OAuth";
    const settingsLabel = document.getElementById("driveAuthLabel");
    if (settingsLabel) settingsLabel.textContent = drive.connected ? "Подключён ✓" : drive.message || "Требуется OAuth";
    const download = document.querySelector("[data-hd-download]");
    if (download && !drive.connected) download.disabled = true;
  }
  function safeToRender() {
    if (document.getElementById("sheet")?.classList.contains("open")) return false;
    const active = document.activeElement;
    return !(active?.closest?.("#view") &&
      active.matches?.("input,textarea,select,[contenteditable=true]"));
  }
  function refreshView() {
    updateHeader();
    if (!D) return;
    if (!safeToRender()) {
      needsRender = true;
      patchClipStatus();
      return;
    }
    needsRender = false;
    preserveClipFormsAndRender();
    patchClipStatus();
  }
  function normalize(d) {
    d.comments = d.comments || [];
    d.experiments = d.experiments || [];
    d.review = d.review || [];
    d.plan = d.plan || [];
    return d;
  }
  function mergePulse(data, force = false) {
    if (!D) return false;
    const snaps = data?.snapshots || [], last = currentPulse(data);
    if (!last || !timeMs(last.t)) return false;
    if (!force && timeMs(last.t) <= timeMs(D.live?.t)) return false;
    const at = (hours, key) => {
      const value = hourlyValue(snaps, last, hours, key);
      return value == null ? null : last[key] - value;
    };
    const recent = (data.recent || []).map(item => ({
      ...item,
      views: last.videos?.[item.id] ?? 0,
      views_1h: (() => {
        const target = timeMs(last.t) - 3600000;
        let prev = null;
        for (const s of snaps) if (timeMs(s.t) <= target) prev = s;
        return prev ? (last.videos?.[item.id] || 0) - (prev.videos?.[item.id] || 0) : null;
      })()
    }));
    const fresh = recent[0];
    const span = snaps.length > 1 ? Math.min(24, (timeMs(last.t) - timeMs(snaps[0].t)) / 3600000) : 0;
    D.live = {
      ...(D.live || {}),
      t:last.t, subs:last.subs, views:last.views,
      views_1h:at(1,"views"), views_12h:at(12,"views"),
      views_24h:at(24,"views"), subs_12h:at(12,"subs"),
      subs_24h:at(24,"subs"), span_h:span,
      recent,
      fresh_short:fresh ? {
        id:fresh.id,title:fresh.title,published:fresh.published,
        views:fresh.views,views_1h:fresh.views_1h
      } : null
    };
    D.channel = {...(D.channel || {}),subs:last.subs,views:last.views};
    if (Array.isArray(data.comments)) D.comments = data.comments;
    if (data.status?.comments) D.comments_status = data.status.comments;
    if (Array.isArray(D.videos)) {
      for (const v of D.videos) if (v.privacy === "public" && last.videos?.[v.id] != null) {
        v.views = last.videos[v.id];
      }
    }
    return true;
  }
  async function getData() {
    if (pageBusy || !isVisible() || !D) return;
    pageBusy = true;
    try {
      const response = await fetch("data.json?t=" + Date.now(), {cache:"no-store"});
      if (!response.ok) throw new Error("Studio data HTTP " + response.status);
      const next = normalize(await response.json()), key = pageFingerprint(next);
      if (pageKey === null) {
        pageKey = key;
        if (pageFingerprint(D) === key) return;
      } else if (key === pageKey) return;
      pageKey = key;
      D = next;
      mergeStatuses();
      if (pulseData) mergePulse(pulseData);
      lastError = false;
      refreshView();
    } catch (e) {
      lastError = true;
      updateHeader();
    } finally { pageBusy = false; }
  }
  async function getPulse() {
    if (pulseBusy || !isVisible() || !D) return;
    pulseBusy = true;
    try {
      const response = await fetch(PULSE_URL + "?t=" + Date.now(), {cache:"no-store"});
      if (!response.ok) throw new Error("Pulse HTTP " + response.status);
      const body = await response.json(), latest = currentPulse(body);
      if (!latest) return;
      const key = [latest.t,body.comments?.length,body.status?.comments,
        latest.subs,latest.views].join("|");
      if (key !== pulseKey) {
        pulseKey = key;
        pulseData = body;
        if (mergePulse(body)) refreshView();
      }
      lastError = false;
      updateHeader();
    } catch (e) {
      // Pages data.json remains a complete fallback if raw pulse is inaccessible.
      updateHeader();
    } finally { pulseBusy = false; }
  }
  function mergeStatuses() {
    if (!D) return false;
    let changed = false;
    for (const [key, status] of Object.entries(latestStatuses)) {
      const old = D[key] || {};
      // Never regress a newer status to cached data from an older deployment.
      const newer = timeMs(status?.checked_at) >= timeMs(old?.checked_at);
      if (!newer || JSON.stringify(old) === JSON.stringify(status)) continue;
      D[key] = status;
      changed = true;
    }
    return changed;
  }
  async function getStatuses() {
    if (statusBusy || !isVisible() || !D) return;
    statusBusy = true;
    try {
      const pairs = [["drive_auth","drive_auth_status.json"],
                     ["hdrezka_intake","hdrezka_status.json"]];
      let changed = false;
      const results = await Promise.allSettled(pairs.map(async ([key, name]) => {
        const response = await fetch(STATUS_BASE + name + "?t=" + Date.now(), {cache:"no-store"});
        if (!response.ok) throw new Error("Status HTTP " + response.status);
        const data = await response.json();
        if (!data || typeof data !== "object" || !("status" in data)) throw new Error("Invalid status");
        return [key, data];
      }));
      for (const result of results) if (result.status === "fulfilled") {
        const [key,data] = result.value;
        if (timeMs(data.checked_at) >= timeMs(latestStatuses[key]?.checked_at)) latestStatuses[key] = data;
      }
      changed = mergeStatuses();
      if (changed) refreshView();
    } catch (_) {
      // Keep the last verified status; a transient CDN failure must not claim success.
    } finally { statusBusy = false; }
  }
  function tick() {
    if (!D || !isVisible()) return;
    if (needsRender && safeToRender()) refreshView();
    updateHeader();
  }
  function wake() {
    if (!isVisible()) return;
    void getData();
    void getPulse();
    void getStatuses();
    tick();
  }
  setInterval(() => { void getData(); }, PAGE_MS);
  setInterval(() => { void getPulse(); }, PULSE_MS);
  setInterval(() => { void getStatuses(); }, STATUS_MS);
  setInterval(tick, 10000);
  document.addEventListener("visibilitychange", wake);
  window.addEventListener("online", wake);
  window.addEventListener("focus", wake);
  // Initial load() in the main Studio script remains the source of first render.
  setTimeout(wake, 2000);
})();