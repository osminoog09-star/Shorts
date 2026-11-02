/* M1lash Google Drive OAuth handoff: no client secret or refresh token in browser.
 * Authorization code is briefly encrypted as a GitHub Secret, then exchanged
 * by Actions. Only GitHub-public-key-encrypted refresh token is published.
 */
(() => {
  "use strict";
  const NONCE_KEY = "m1-drive-oauth-nonce";
  // The nonce is a non-secret request identifier: persist across mobile tabs/reloads.
  function getNonce() {
    return sessionStorage.getItem(NONCE_KEY) || localStorage.getItem(NONCE_KEY) || "";
  }
  function setNonce(value) {
    sessionStorage.setItem(NONCE_KEY, value);
    localStorage.setItem(NONCE_KEY, value);
  }
  function clearNonce() {
    sessionStorage.removeItem(NONCE_KEY);
    localStorage.removeItem(NONCE_KEY);
  }
  const RESULT_URL = "https://raw.githubusercontent.com/osminoog09-star/Shorts/main/publishing/drive_oauth_exchange.json";
  let working = false;
  let checking = false;
  const notice = m => {
    const elem = document.getElementById("driveConnectStatus");
    if (elem) elem.textContent = m;
  };
  async function clientId() {
    const r = await fetch("google_client.json?t=" + Date.now(), {cache:"no-store"});
    if (!r.ok) throw new Error("Не получен публичный Google Client ID с сайта.");
    const data = await r.json();
    if (!/^[0-9]+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$/.test(data.client_id || ""))
      throw new Error("Google Client ID ещё не настроен для Студии.");
    return data.client_id;
  }
  function randomNonce() {
    const bits = crypto.getRandomValues(new Uint8Array(16));
    return Array.from(bits, b=>b.toString(16).padStart(2,"0")).join("");
  }
  async function begin(evt) {
    if (working) return;
    if (!tok()) { notice("Сначала сохрани GitHub-токен в этом разделе."); return; }
    const button = evt.target.closest("#driveGoogleStart");
    if (!button) return;
    // Open synchronously from click so mobile browsers will not block popup.
    const popup = window.open("about:blank", "_blank");
    button.disabled = true;
    try {
      const id = await clientId();
      const u = new URL("https://accounts.google.com/o/oauth2/v2/auth");
      u.searchParams.set("client_id",id);
      u.searchParams.set("redirect_uri","https://developers.google.com/oauthplayground");
      u.searchParams.set("response_type","code");
      u.searchParams.set("scope","https://www.googleapis.com/auth/drive");
      u.searchParams.set("access_type","offline");
      u.searchParams.set("prompt","consent select_account");
      u.searchParams.set("state",randomNonce());
      // The full OAuth Client Secret remains inside GitHub Actions, never in the page.
      if (popup) popup.location.href = u.href;
      else {
        const a=document.getElementById("driveGoogleLink");
        if (a) {a.href=u.href;a.hidden=false;}
      }
      notice("В Google выбери свой аккаунт и разреши доступ. В открывшемся OAuth Playground скопируй Authorization code из шага 2, не нажимая Exchange. Вставь код ниже.");
    } catch (error) {
      if (popup) popup.close();
      notice("Не получилось открыть Google: " + error.message);
    } finally {button.disabled=false;}
  }
  async function finish(button) {
    if (working) return;
    if (!tok()) {notice("Нужен GitHub-токен в этом браузере.");return;}
    const field=document.getElementById("driveAuthCode");
    const code=(field?.value||"").trim();
    if (code.length<16||code.length>2000||/[\r\n]/.test(code)) {
      notice("Вставь свежий Authorization code из OAuth Playground, не Refresh token.");
      return;
    }
    working=true;button.disabled=true;
    try {
      const id=await clientId();
      const pub=await gh("/actions/secrets/public-key");
      if (!pub.key || !pub.key_id) throw new Error("GitHub не выдал открытый ключ секретов.");
      const nonce=randomNonce();
      await setSecret("GDRIVE_AUTH_CODE",code);
      if (field) field.value="";
      setNonce(nonce);
      await dispatch("drive-oauth-exchange.yml",{
        nonce,client_id:id,public_key:pub.key,key_id:pub.key_id
      });
      notice("Код передан в защищённое задание GitHub. Проверяю разрешение Google и сохраняю доступ в GitHub Secrets…");
    } catch (error) {
      notice("Ошибка подключения: " + error.message);
    } finally { working=false;button.disabled=false; }
  }
  async function check() {
    if (checking || working || !getNonce() || !tok()) return;
    checking=true;
    try {
      const response=await fetch(RESULT_URL+"?t="+Date.now(),{cache:"no-store"});
      if (!response.ok) return;
      const status=await response.json();
      const nonce=getNonce();
      if (!nonce || status.nonce!==nonce) return;
      if (status.status==="error") {
        clearNonce();
        notice("Google: " + (status.message||status.error_code||"ошибка подключения"));
        try {await gh("/actions/secrets/GDRIVE_AUTH_CODE",{method:"DELETE"});} catch(_) {}
        return;
      }
      if (status.status!=="ready" || !status.encrypted_value || !status.key_id) return;
      // The encrypted_value has never been decrypted or exposed by a public website.
      await gh("/actions/secrets/GDRIVE_REFRESH_TOKEN", {
        method:"PUT",body:JSON.stringify({
          encrypted_value:status.encrypted_value,key_id:status.key_id
        })
      });
      clearNonce();
      try {await gh("/actions/secrets/GDRIVE_AUTH_CODE",{method:"DELETE"});} catch(_) {}
      await dispatch("hdrezka-intake.yml",{
        url:"",quality:"1080p",mode:"drive_check",translation:""
      });
      notice("Новый Google Drive токен сохранён в GitHub Secrets. Запущена проверка доступа к папке — результат появится автоматически.");
    } catch(error) {
      notice("Не удалось завершить подключение: "+error.message+" (можно повторить, код не утрачен).");
    } finally { checking=false; }
  }
  document.addEventListener("click",evt=>{
    if (evt.target.closest("#driveGoogleStart")) {void begin(evt);}
    else if (evt.target.closest("#driveGoogleFinish")) {
      const button=evt.target.closest("#driveGoogleFinish");
      void finish(button);
    }
  });
  setInterval(()=>{void check();},10000);
  window.addEventListener("focus",()=>{void check();});
  setTimeout(()=>{void check();},1500);
})();
