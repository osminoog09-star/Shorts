// Full audit of the live M1lash Studio site (Claude, 07.11.2026): every tab opens and renders, no JS errors,
// no failed requests/broken images, every link answers, desktop + phone layout without horizontal overflow.
// usage: node scripts/qa/studio_site_audit.mjs [url]   (needs playwright-core; PLAYWRIGHT_CHROME = headless shell)
import { chromium } from '../../longform/smart-strike/node_modules/playwright-core/index.mjs';
const URL = process.argv[2] || 'https://osminoog09-star.github.io/Shorts/studio/';
const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROME });
const report = { url: URL, at: new Date().toISOString(), viewports: {}, links: [] };
const links = new Set();
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 412, height: 915 }]]) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1 });
  const page = await ctx.newPage(); const errs = [], failed = [];
  page.on('pageerror', e => errs.push(String(e.message).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
  page.on('requestfailed', r => failed.push(r.url().slice(0, 140) + ' ' + (r.failure()?.errorText || '')));
  page.on('response', r => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url().slice(0, 140)); });
  const t0 = Date.now(); await page.goto(URL + '?audit=' + Date.now(), { waitUntil: 'networkidle', timeout: 60000 }); const load = Date.now() - t0;
  await page.waitForTimeout(1500);
  const tabs = await page.$$eval('[data-tab]', b => [...new Set(b.map(x => x.dataset.tab))]);
  const res = { load_ms: load, tabs: {}, errors: errs, failed };
  for (const k of tabs) {
    await page.evaluate(k => { const b = [...document.querySelectorAll(`[data-tab="${k}"]`)].find(x => x.offsetParent); (b || document.querySelector(`[data-tab="${k}"]`)).click(); }, k);
    await page.waitForTimeout(900);
    res.tabs[k] = await page.evaluate(() => {
      const m = document.querySelector('main'); const txt = m?.innerText || '';
      return { chars: txt.length, buttons: m?.querySelectorAll('button').length || 0,
        brokenImg: [...(m?.querySelectorAll('img') || [])].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.slice(0, 100)),
        bad: (txt.match(/.{0,40}\b(undefined|NaN|null|\[object Object\])\b.{0,40}/g) || []).slice(0, 4),
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 2,
        hrefs: [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith('http')) };
    });
    res.tabs[k].hrefs.forEach(h => links.add(h)); delete res.tabs[k].hrefs;
  }
  // settings dialog opens
  res.settings = await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Настройки|⚙/.test(x.innerText + x.title + (x.getAttribute('aria-label') || ''))); if (!b) return 'no settings button'; b.click(); return 'clicked'; });
  await page.waitForTimeout(600); res.settingsOpen = await page.evaluate(() => /Обновить сейчас|Токены/.test(document.body.innerText));
  await page.screenshot({ path: process.env.AUDIT_SHOTS ? `${process.env.AUDIT_SHOTS}/${name}.png` : `studio_${name}.png`, fullPage: false });
  report.viewports[name] = res; await ctx.close();
}
for (const h of links) {
  if (/youtube\.com|youtu\.be|studio\.youtube/.test(h)) { report.links.push([h.slice(0, 120), 'skip (YouTube needs login)']); continue; }
  try { const r = await fetch(h, { method: 'GET', redirect: 'follow' }); report.links.push([h.slice(0, 120), r.status]); } catch (e) { report.links.push([h.slice(0, 120), 'ERR ' + e.message]); }
}
await browser.close();
console.log(JSON.stringify(report, null, 1));
