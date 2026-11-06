"""Панель M1lash — ярлык на рабочем столе ПК (решение Дениса 06.11.2026).

Включить / выключить студию / игровой режим одной кнопкой. То же самое переключается на сайте студии
(Агенты → Управление студией): обе стороны пишут режим в publishing/studio_settings.json → git.
Игровой режим: агенты и подготовка записей встают, модель выгружается из видеокарты сразу.
"""
import json, os, subprocess, threading, tkinter as tk, urllib.request, webbrowser
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


if __name__ == "__main__":
    Panel().mainloop()
