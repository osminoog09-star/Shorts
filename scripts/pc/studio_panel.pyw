"""Панель M1lash — ярлык на рабочем столе ПК (решение Дениса 06.11.2026).

UI (решение Дениса 06.11, grill-me): стеклянное 3D-окно как сайт студии — site/studio/pc_panel.html в pywebview
(Edge WebView2), без рамки Windows; данные/кнопки через локальный API 127.0.0.1. Нет pywebview → ставим его в фоне
и показываем прежнюю панель Tkinter (управление студией не пропадает).

Включить / выключить студию / игровой режим одной кнопкой. То же самое переключается на сайте студии
(Агенты → Управление студией): обе стороны пишут режим в publishing/studio_settings.json → git.
Игровой режим: агенты и подготовка записей встают, модель выгружается из видеокарты сразу.
"""
import json, os, socket, subprocess, sys, threading, time, urllib.request, webbrowser
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SETTINGS = REPO / "publishing" / "studio_settings.json"
SITE = "https://osminoog09-star.github.io/Shorts/studio/"
OLLAMA = os.environ.get("M1_OLLAMA_URL", "http://localhost:11434")
NO_WIN = 0x08000000 if os.name == "nt" else 0  # без чёрных окон консоли
MODES = {"on": ("СТУДИЯ РАБОТАЕТ", "#5ee6a0"), "off": ("СТУДИЯ ВЫКЛЮЧЕНА", "#ff6b7a"), "game": ("ИГРОВОЙ РЕЖИМ", "#ffc65c")}


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, creationflags=NO_WIN)


def read():
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def unload_ollama():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=3) as r:
            for m in json.loads(r.read()).get("models", []):
                req = urllib.request.Request(OLLAMA + "/api/generate", data=json.dumps({"model": m["name"], "keep_alive": 0}).encode(),
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass


def set_mode(mode, done):
    def work():
        msg = ""
        git("pull", "-q", "--rebase")
        st = read()
        st["mode"] = mode
        st["updated"] = datetime.now().astimezone().isoformat(timespec="seconds")
        st["updated_by"] = "Денис (панель ПК)"
        SETTINGS.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if mode != "on":
            unload_ollama()
        git("add", str(SETTINGS))
        git("commit", "-q", "-m", f"studio: режим {mode} (Денис, панель ПК)")
        for _ in range(3):
            if git("pull", "-q", "--rebase").returncode == 0 and git("push", "-q").returncode == 0:
                break
        else:
            msg = "Режим включён на ПК, но не отправлен на сайт (нет сети?) — отправится позже"
        done(msg)
    threading.Thread(target=work, daemon=True).start()


def tk_panel():
  import tkinter as tk

  class Panel(tk.Tk):
      def __init__(self):
          super().__init__()
          self.title("Панель M1lash")
          self.configure(bg="#0b0818")
          self.resizable(False, False)
          f = ("Segoe UI", 11)
          self.state_lbl = tk.Label(self, font=("Segoe UI Semibold", 18), bg="#0b0818", fg="#fff", pady=14)
          self.state_lbl.pack(fill="x", padx=20)
          self.info = tk.Label(self, font=("Segoe UI", 10), bg="#0b0818", fg="#b9b3d6", justify="left")
          self.info.pack(fill="x", padx=20)
          row = tk.Frame(self, bg="#0b0818"); row.pack(padx=16, pady=14)
          for mode, text, color in (("on", "▶  Включить", "#2e8f63"), ("game", "🎮  Игровой режим", "#9a7420"), ("off", "■  Выключить", "#8f2e3b")):
              tk.Button(row, text=text, font=f, width=16, pady=10, bg=color, fg="#fff", activebackground=color, bd=0,
                        command=lambda m=mode: self.switch(m)).pack(side="left", padx=4)
          row2 = tk.Frame(self, bg="#0b0818"); row2.pack(padx=16, pady=(0, 14))
          tk.Button(row2, text="🌐  Сайт студии", font=f, width=16, bg="#2a2147", fg="#fff", bd=0, pady=6,
                    command=lambda: webbrowser.open(SITE + "#agents")).pack(side="left", padx=4)
          tk.Button(row2, text="📂  Папка игр", font=f, width=16, bg="#2a2147", fg="#fff", bd=0, pady=6,
                    command=lambda: os.startfile(os.environ.get("M1LASH_GAMES", r"C:\M1lash\Игры")) if os.name == "nt" else None).pack(side="left", padx=4)
          self.msg = tk.Label(self, font=("Segoe UI", 9), bg="#0b0818", fg="#ffc65c"); self.msg.pack(pady=(0, 10))
          self.refresh()

      def switch(self, mode):
          self.msg.config(text="Переключаю…")
          set_mode(mode, lambda m: self.after(0, lambda: (self.msg.config(text=m or "Готово ✓ (сайт обновится за 1–2 мин)"), self.refresh())))

      def refresh(self):
          st = read()
          mode = st.get("mode", "on")
          t, c = MODES.get(mode, (mode, "#fff"))
          self.state_lbl.config(text=t, fg=c)
          try:
              urllib.request.urlopen(OLLAMA + "/api/tags", timeout=2); oll = "запущена"
          except Exception:
              oll = "не отвечает"
          self.info.config(text=f"Режим публикации: {'сам ставит даты' if st.get('autonomy') == 'full' else 'дату ставит Денис'}"
                                f"   ·   Запас: {st.get('buffer_days', 7)} дн.\nЛокальная модель (Ollama): {oll}"
                                f"   ·   Claude в сутки: {st.get('claude_daily_cap', 4)}")
          self.after(30000, self.refresh)


  Panel().mainloop()


# ---------- новое окно: стекло + 3D (pc_panel.html) ----------
WEB = REPO / "site" / "studio"
LOG = REPO / "agents" / "bridge.log"
WIN = []


def gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=4, creationflags=NO_WIN).stdout
        u, used, total, t = [int(float(x)) for x in out.splitlines()[0].split(",")]
        return {"util": u, "used": used, "total": total, "temp": t}
    except Exception:
        return None


def ollama_state():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=2) as r:
            return True, [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return False, []


def agents_state():
    try:
        fresh = time.time() - LOG.stat().st_mtime < 180
        lines = [l for l in LOG.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
        last = lines[-1][11:] if lines else ""
        return fresh, last[:90]
    except Exception:
        return False, "журнал агентов пуст"


def obs_up():
    try:
        socket.create_connection(("127.0.0.1", 4455), timeout=0.5).close(); return True
    except Exception:
        return False


def state():
    st = read()
    up, loaded = ollama_state()
    f = REPO / "agents" / "local_model.txt"
    model = st.get("local_model", "auto")
    if model in ("", "auto"):
        model = f.read_text(encoding="utf-8").strip() if f.exists() else "gemma4:12b"
    ag, last = agents_state()
    return {"mode": st.get("mode", "on"), "autonomy": st.get("autonomy"), "buffer_days": st.get("buffer_days", 7),
            "claude_cap": st.get("claude_daily_cap", 4), "host": socket.gethostname(), "gpu": gpu(), "ollama": up,
            "model": model, "loaded": any(n.startswith(model) for n in loaded), "agents": ag, "last": last, "obs": obs_up()}


def serve():
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(WEB), **k)

        def log_message(self, *a):
            pass

        def send_json(self, obj):
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            if self.path.startswith("/api/state"):
                return self.send_json(state())
            return super().do_GET()

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            if self.path == "/api/mode" and body.get("mode") in MODES:
                ev, res = threading.Event(), {}
                set_mode(body["mode"], lambda m: (res.update(msg=m), ev.set()))
                ev.wait(90)
                return self.send_json({"msg": res.get("msg", "")})
            if self.path == "/api/open":
                if body.get("what") == "site":
                    webbrowser.open(SITE + "#agents")
                elif os.name == "nt":
                    os.startfile(os.environ.get("M1LASH_GAMES", r"C:\M1lash\Игры"))
                return self.send_json({})
            if self.path == "/api/win" and WIN:
                (WIN[0].minimize if body.get("act") == "min" else WIN[0].destroy)()
                return self.send_json({})
            self.send_json({"error": "?"})

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


def install_webview():
    """Первый запуск без pywebview: ставим в фоне, со следующего запуска — новое окно."""
    py = Path(sys.executable).with_name("python.exe")
    subprocess.Popen([str(py if py.exists() else sys.executable), "-m", "pip", "install", "-q", "pywebview"], creationflags=NO_WIN)


if __name__ == "__main__":
    try:
        import webview
    except Exception:
        install_webview()
        tk_panel()
        sys.exit()
    port = serve()
    WIN.append(webview.create_window("Панель M1lash", f"http://127.0.0.1:{port}/pc_panel.html", width=580, height=600,
                                     resizable=False, frameless=True, easy_drag=False, background_color="#05040D"))
    webview.start()
