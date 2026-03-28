#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MoodTracker v3 — Compacto, Windows & Linux"""

import tkinter as tk
from tkinter import messagebox
import json, os, sys, datetime, platform

IS_WIN   = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"


def app_path():
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(__file__)

if IS_WIN:
    DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "MoodTracker")
else:
    DATA_DIR = os.path.expanduser("~/.moodtracker")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
APP_PATH  = app_path()

# Fonts
if IS_WIN:
    FN = "Segoe UI"
else:
    FN = "DejaVu Sans"

# Palette
BG     = "#0f0f18"
CARD   = "#16161f"
CARD2  = "#1c1c28"
BORDER = "#28283a"
ACCENT = "#6c63ff"
ACCT2  = "#9088ff"
TEXT   = "#eeeefc"
MUTED  = "#55556a"
MUTED2 = "#35354a"

# ── Color ─────────────────────────────────────────────────────────────────────
def lerp(a, b, t): return int(a + (b-a)*t)

def mood_color(val):
    t = (val + 10) / 20.0
    stops = [
        (0.00, (190, 20, 20)),
        (0.30, (210, 90, 20)),
        (0.48, (140,110, 50)),
        (0.50, ( 70, 70, 85)),
        (0.52, ( 50,120, 55)),
        (0.70, ( 30,185, 75)),
        (1.00, ( 15,150, 55)),
    ]
    for i in range(len(stops)-1):
        t0,c0 = stops[i]; t1,c1 = stops[i+1]
        if t0 <= t <= t1:
            f = (t-t0)/(t1-t0)
            return "#{:02x}{:02x}{:02x}".format(
                lerp(c0[0],c1[0],f), lerp(c0[1],c1[1],f), lerp(c0[2],c1[2],f))
    return "#505060"

def mood_emoji(val):
    if val<=-9: return "😭"
    if val<=-7: return "😢"
    if val<=-5: return "😔"
    if val<=-3: return "😕"
    if val<=-1: return "😶"
    if val== 0: return "😐"
    if val<= 2: return "🙂"
    if val<= 4: return "😌"
    if val<= 6: return "😊"
    if val<= 8: return "😁"
    return "🌟"

DESCS = [
    "Malestar extremo","Malestar severo","Muy mal","Bastante mal",
    "Mal","Algo mal","Bajo","Un poco bajo","Levemente bajo",
    "Casi neutral","Neutral","Levemente bien","Algo bien",
    "Un poco bien","Bien","Bastante bien","Muy bien",
    "Genial","Excelente","Extraordinario","Bienestar total",
]

# ── Data ──────────────────────────────────────────────────────────────────────
def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f:
                d = json.load(f)
                for k in ("entries","daily","weekly","monthly"):
                    d.setdefault(k, [] if k=="entries" else {})
                return d
        except (json.JSONDecodeError, OSError):
            broken = f"{DATA_FILE}.broken"
            try:
                if os.path.exists(broken):
                    os.remove(broken)
                os.replace(DATA_FILE, broken)
            except OSError:
                pass
    return {"entries":[],"daily":{},"weekly":{},"monthly":{}}

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def recalculate(data):
    today = datetime.date.today().isoformat()
    by_date = {}
    for e in data["entries"]:
        by_date.setdefault(e["date"],[]).append(e["value"])
    for d,vals in by_date.items():
        if d != today:
            data["daily"][d] = round(sum(vals)/len(vals), 2)
    by_week = {}
    for d,avg in data["daily"].items():
        dt = datetime.date.fromisoformat(d)
        wk = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
        by_week.setdefault(wk,[]).append(avg)
    for wk,vals in by_week.items():
        data["weekly"][wk] = round(sum(vals)/len(vals), 2)
    by_month = {}
    for d,avg in data["daily"].items():
        mo = d[:7]
        by_month.setdefault(mo,[]).append(avg)
    for mo,vals in by_month.items():
        data["monthly"][mo] = round(sum(vals)/len(vals), 2)
    save_data(data)

def today_stats(data):
    today = datetime.date.today().isoformat()
    vals = [e["value"] for e in data["entries"] if e["date"]==today]
    if not vals: return None, 0
    return round(sum(vals)/len(vals), 2), len(vals)

# ── Compact gradient slider (pure canvas) ─────────────────────────────────────
class Slider(tk.Canvas):
    TH = 6   # track height
    KR = 9   # knob radius

    def __init__(self, parent, command=None, **kw):
        self._cw = int(kw.pop("width", 240))
        super().__init__(parent, width=self._cw, height=28,
                         bg=CARD, highlightthickness=0, **kw)
        self._val = 0
        self._cmd = command
        self.bind("<ButtonPress-1>",   self._press)
        self.bind("<B1-Motion>",       self._motion)
        self.bind("<ButtonRelease-1>", lambda e: None)
        self._redraw()

    def get(self): return self._val

    def _px(self, v):
        pad = self.KR + 2
        return pad + (v + 10) / 20 * (self._cw - 2*pad)

    def _val_from(self, x):
        pad = self.KR + 2
        span = self._cw - 2*pad
        raw = (x - pad) / span * 20 - 10
        return max(-10, min(10, int(round(raw))))

    def _redraw(self):
        self.delete("all")
        pad = self.KR + 2
        ty  = 14
        span = self._cw - 2*pad
        # gradient track
        for i in range(int(span)):
            v = -10 + 20*i/span
            self.create_line(pad+i, ty-self.TH//2,
                             pad+i, ty+self.TH//2, fill=mood_color(v))
        # track border
        self.create_rectangle(pad, ty-self.TH//2,
                               pad+span, ty+self.TH//2,
                               outline=MUTED2, fill="", width=1)
        # knob
        kx  = self._px(self._val)
        col = mood_color(self._val)
        self.create_oval(kx-self.KR, ty-self.KR,
                         kx+self.KR, ty+self.KR,
                         fill=CARD, outline=col, width=2)
        self.create_oval(kx-3, ty-3, kx+3, ty+3, fill=col, outline="")

    def _press(self, e):   self._update(e.x)
    def _motion(self, e):  self._update(e.x)

    def _update(self, x):
        n = self._val_from(x)
        if n != self._val:
            self._val = n
            self._redraw()
            if self._cmd: self._cmd(n)


# ── Timeline ──────────────────────────────────────────────────────────────────
class TimelineWindow(tk.Toplevel):
    TABS = [("Registros","entries"),("Diario","daily"),
            ("Semanal","weekly"),("Mensual","monthly")]

    def __init__(self, parent, data):
        super().__init__(parent)
        self.title("MoodTracker — Historial")
        self.configure(bg=BG)
        self.geometry("900x580")
        self.minsize(600, 400)
        self.data = data
        self._btns = {}
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=CARD2, pady=0)
        bar.pack(fill="x")
        for lbl, val in self.TABS:
            b = tk.Button(bar, text=lbl,
                          command=lambda v=val: self._switch(v),
                          bg=CARD2, fg=MUTED, font=(FN,9),
                          relief="flat", padx=18, pady=8,
                          cursor="hand2", bd=0,
                          activebackground=CARD, activeforeground=TEXT)
            b.pack(side="left")
            self._btns[val] = b
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self._fr = tk.Frame(self, bg=BG)
        self._fr.pack(fill="both", expand=True)
        self._switch("entries")

    def _switch(self, tab):
        for v,b in self._btns.items():
            b.config(bg=CARD if v==tab else CARD2,
                     fg=TEXT if v==tab else MUTED)
        for w in self._fr.winfo_children(): w.destroy()
        self._draw(tab)

    def _draw(self, tab):
        try:
            import matplotlib; matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt, matplotlib.dates as mdates
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.colors import LinearSegmentedColormap
            self._mpl(tab, plt, mdates, FigureCanvasTkAgg, LinearSegmentedColormap)
        except ImportError:
            self._tkdraw(tab)

    def _mpl(self, tab, plt, mdates, FCA, LSC):
        cmap = LSC.from_list("mood",
            ["#be1414","#d25a14","#8c6e32","#464650","#286e30","#1eb84b","#0f9637"])
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
        fig.patch.set_facecolor(BG); ax.set_facecolor(CARD)
        for sp in ax.spines.values(): sp.set_color(BORDER)
        ax.tick_params(colors=MUTED, labelsize=8)
        ax.grid(True, color=CARD2, linewidth=0.6, linestyle="--", alpha=0.9)
        ax.set_ylim(-12, 12)
        ax.axhline(0, color=BORDER, linewidth=1.2)
        today = datetime.date.today().isoformat()
        bc = lambda vals: [cmap((v+10)/20) for v in vals]
        no = lambda msg: ax.text(0.5,0.5,msg,transform=ax.transAxes,
                                  ha="center",va="center",color=MUTED,fontsize=12,linespacing=1.9)

        if tab == "entries":
            es = self.data["entries"]
            if not es:
                no("Sin registros aún.\nEmpezá registrando tu estado de ánimo.")
            else:
                dts  = [datetime.datetime.fromisoformat(e["timestamp"]) for e in es]
                vals = [e["value"] for e in es]
                ax.scatter(dts, vals, c=vals, cmap=cmap, vmin=-10, vmax=10,
                           s=50, zorder=5, edgecolors=BG, linewidths=0.8)
                ax.plot(dts, vals, color=BORDER, linewidth=0.9, zorder=3, alpha=0.7)
                ax.fill_between(dts, [v if v>=0 else 0 for v in vals], alpha=0.10, color="#1eb84b")
                ax.fill_between(dts, [v if v<0  else 0 for v in vals], alpha=0.10, color="#d25a14")
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
                ax.set_title("Todos los registros", color=TEXT, pad=12, fontsize=10, fontweight="bold")

        elif tab == "daily":
            d = dict(self.data["daily"]); avg,_ = today_stats(self.data)
            if avg is not None: d[today] = avg
            if not d:
                no("Sin datos diarios aún.\nSe calculan al día siguiente.")
            else:
                dates = sorted(d.keys()); vals = [d[x] for x in dates]
                xs = [datetime.date.fromisoformat(x) for x in dates]
                bars = ax.bar(xs, vals, color=bc(vals), alpha=0.9, width=0.7,
                              edgecolor=BG, linewidth=0.4)
                for bar,v in zip(bars,vals):
                    ax.text(bar.get_x()+bar.get_width()/2,
                            v+(0.4 if v>=0 else -0.8),
                            f"{v:+.1f}", ha="center",
                            va="bottom" if v>=0 else "top",
                            color=TEXT, fontsize=7, alpha=0.85)
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", color=MUTED)
                ax.set_title("Promedio Diario", color=TEXT, pad=12, fontsize=10, fontweight="bold")

        elif tab == "weekly":
            w = self.data["weekly"]
            if not w:
                no("Sin datos semanales aún.\nSe calculan cuando hay días completos registrados.")
            else:
                wks = sorted(w.keys()); vals = [w[x] for x in wks]; ys = list(range(len(wks)))
                ax.barh(ys, vals, color=bc(vals), alpha=0.9, edgecolor=BG)
                ax.set_yticks(ys); ax.set_yticklabels(wks, color=MUTED, fontsize=8)
                ax.set_xlim(-12,12); ax.axvline(0, color=BORDER, linewidth=1.2)
                ax.set_ylim(-0.8, len(wks)-0.2)
                ax.set_title("Promedio Semanal", color=TEXT, pad=12, fontsize=10, fontweight="bold")

        else:
            m = self.data["monthly"]
            if not m:
                no("Sin datos mensuales aún.")
            else:
                mos = sorted(m.keys()); vals = [m[x] for x in mos]; ys = list(range(len(mos)))
                ax.barh(ys, vals, color=bc(vals), alpha=0.9, edgecolor=BG)
                ax.set_yticks(ys); ax.set_yticklabels(mos, color=MUTED, fontsize=9)
                ax.set_xlim(-12,12); ax.axvline(0, color=BORDER, linewidth=1.2)
                ax.set_ylim(-0.8, len(mos)-0.2)
                ax.set_title("Promedio Mensual", color=TEXT, pad=12, fontsize=10, fontweight="bold")

        plt.tight_layout(pad=1.5)
        c = FCA(fig, master=self._fr); c.draw()
        c.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _tkdraw(self, tab):
        today = datetime.date.today().isoformat()
        if tab == "entries":
            items = [(datetime.datetime.fromisoformat(e["timestamp"]).strftime("%d/%m %H:%M"),
                      e["value"]) for e in self.data["entries"]]
            title = "Todos los registros"
        elif tab == "daily":
            d = dict(self.data["daily"]); avg,_ = today_stats(self.data)
            if avg is not None: d[today] = avg
            items = sorted(d.items()); title = "Promedio Diario"
        elif tab == "weekly":
            items = sorted(self.data["weekly"].items()); title = "Promedio Semanal"
        else:
            items = sorted(self.data["monthly"].items()); title = "Promedio Mensual"
        if not items:
            tk.Label(self._fr, text="Sin datos aún.", bg=BG, fg=MUTED,
                     font=(FN,11)).pack(expand=True)
            return
        c = tk.Canvas(self._fr, bg=BG, highlightthickness=0)
        c.pack(fill="both", expand=True)
        self._fr.update_idletasks()
        W = self._fr.winfo_width() or 860
        H = self._fr.winfo_height() or 540
        PL,PR,PT,PB = 52,16,44,64
        pw = W-PL-PR; ph = H-PT-PB; cy0 = PT+ph//2
        c.create_text(W//2, 20, text=title, fill=TEXT, font=(FN,10,"bold"))
        c.create_line(PL,PT,PL,H-PB, fill=BORDER)
        c.create_line(PL,cy0,W-PR,cy0, fill=BORDER, dash=(4,4))
        for v in range(-10,11,5):
            y = cy0 - v*(ph//2)//10
            c.create_text(PL-5,y, text=str(v), fill=MUTED, anchor="e", font=(FN,7))
        n = len(items); bw = max(5,min(32,(pw-8)//n-2))
        for i,(lbl,val) in enumerate(items):
            x   = PL+8 + i*(pw-8)//n + bw//2
            yv  = cy0 - int(val*(ph//2)/10)
            col = mood_color(val)
            c.create_rectangle(x-bw//2, min(yv,cy0), x+bw//2, max(yv,cy0),
                                fill=col, outline="")
            c.create_text(x, yv+(-10 if val>=0 else 10),
                          text=f"{val:.1f}" if isinstance(val,float) else str(val),
                          fill=TEXT, font=(FN,7))
            if i % max(1,n//12) == 0:
                c.create_text(x, H-PB+12, text=str(lbl)[:7],
                              fill=MUTED, font=(FN,7))


# ── Autostart ─────────────────────────────────────────────────────────────────
def setup_autostart():
    if IS_WIN:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0, winreg.KEY_SET_VALUE)
            if getattr(sys, "frozen", False):
                command = f'"{APP_PATH}"'
            else:
                pw = sys.executable.replace("python.exe","pythonw.exe")
                if not os.path.exists(pw):
                    pw = sys.executable
                command = f'"{pw}" "{APP_PATH}"'
            winreg.SetValueEx(key, "MoodTracker", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            messagebox.showinfo("Inicio Automático",
                "✅ Listo!\n\nMoodTracker se iniciará automáticamente\ncada vez que inicies Windows.")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo configurar:\n{ex}")
    else:
        p = os.path.expanduser("~/.config/autostart/moodtracker.desktop")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if getattr(sys, "frozen", False):
            exec_cmd = APP_PATH
        else:
            exec_cmd = f"python3 {APP_PATH}"
        with open(p,"w") as f:
            f.write(f"[Desktop Entry]\nType=Application\nName=MoodTracker\n"
                    f"Exec={exec_cmd}\nX-GNOME-Autostart-enabled=true\n")
        messagebox.showinfo("Inicio Automático",
            "✅ Listo!\n\nMoodTracker se iniciará automáticamente.")


# ── Main Widget ───────────────────────────────────────────────────────────────
class MoodWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MoodTracker")
        self.root.resizable(False, False)
        self.root.configure(bg=BORDER)
        self.root.attributes("-topmost", True)
        if IS_WIN:
            self.root.attributes("-toolwindow", True)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"+{sw-296}+14")

        self.data = load_data()
        recalculate(self.data)
        self._after = None
        self._build()
        self._refresh()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _lbl(self, parent, text, fg=None, font_size=9, bold=False, anchor="center"):
        style = "bold" if bold else ""
        f = (FN, font_size, style) if style else (FN, font_size)
        return tk.Label(parent, text=text, bg=CARD,
                        fg=fg or MUTED, font=f, anchor=anchor)

    def _build(self):
        # Outer frame = 1px border
        outer = tk.Frame(self.root, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)
        self._main = tk.Frame(outer, bg=CARD)
        self._main.pack(fill="both", expand=True)
        m = self._main

        # ── Header ──────────────────────────────────────────────────────
        hdr = tk.Frame(m, bg=CARD2, padx=12, pady=5)
        hdr.pack(fill="x")
        tk.Label(hdr, text="MOOD", bg=CARD2, fg=ACCENT,
                 font=(FN, 8, "bold")).pack(side="left")
        tk.Label(hdr, text="TRACKER", bg=CARD2, fg=MUTED,
                 font=(FN, 8)).pack(side="left", padx=(3,0))
        self._date_lbl = tk.Label(hdr, bg=CARD2, fg=MUTED, font=(FN,8))
        self._date_lbl.pack(side="right")

        tk.Frame(m, bg=BORDER, height=1).pack(fill="x")

        # ── Emoji + Number + Desc ────────────────────────────────────────
        mid = tk.Frame(m, bg=CARD, pady=10)
        mid.pack(fill="x")
        row = tk.Frame(mid, bg=CARD)
        row.pack()
        self._emoji_lbl = tk.Label(row, text="😐", bg=CARD, font=("Arial",20))
        self._emoji_lbl.pack(side="left", padx=(0,6))
        self._num_lbl   = tk.Label(row, text=" 0", bg=CARD, fg=TEXT,
                                    font=(FN,34,"bold"), width=3, anchor="e")
        self._num_lbl.pack(side="left")
        self._desc_lbl  = tk.Label(mid, text="Neutral", bg=CARD,
                                    fg=MUTED, font=(FN,8))
        self._desc_lbl.pack(pady=(2,0))

        # ── Slider ───────────────────────────────────────────────────────
        sf = tk.Frame(m, bg=CARD, padx=12, pady=4)
        sf.pack(fill="x")
        lr = tk.Frame(sf, bg=CARD); lr.pack(fill="x")
        tk.Label(lr, text="−10", bg=CARD, fg="#be1414",
                 font=(FN,7)).pack(side="left")
        tk.Label(lr, text="+10", bg=CARD, fg="#0f9637",
                 font=(FN,7)).pack(side="right")
        self._sl = Slider(sf, command=self._slide, width=256)
        self._sl.pack(pady=(2,0))

        # ── Register button ──────────────────────────────────────────────
        bf = tk.Frame(m, bg=CARD, padx=12, pady=8)
        bf.pack(fill="x")
        self._rbtn = tk.Button(
            bf, text="▶  REGISTRAR",
            command=self._reg,
            bg=ACCENT, fg="white", font=(FN,9,"bold"),
            relief="flat", pady=7, cursor="hand2",
            activebackground=ACCT2, activeforeground="white"
        )
        self._rbtn.pack(fill="x")

        # ── Stats ────────────────────────────────────────────────────────
        tk.Frame(m, bg=BORDER, height=1).pack(fill="x")
        st = tk.Frame(m, bg=CARD, padx=12, pady=8)
        st.pack(fill="x")
        self._avg_lbl = tk.Label(st, text="Promedio hoy:  —",
                                  bg=CARD, fg=TEXT, font=(FN,9,"bold"), anchor="w")
        self._avg_lbl.pack(fill="x")
        self._cnt_lbl = tk.Label(st, text="Sin registros aún",
                                  bg=CARD, fg=MUTED, font=(FN,8), anchor="w")
        self._cnt_lbl.pack(fill="x", pady=(1,6))
        self._hist_fr = tk.Frame(st, bg=CARD)
        self._hist_fr.pack(fill="x")

        # ── Bottom buttons ───────────────────────────────────────────────
        tk.Frame(m, bg=BORDER, height=1).pack(fill="x")
        bot = tk.Frame(m, bg=CARD2, padx=8, pady=6)
        bot.pack(fill="x")
        for txt,cmd in [("📊 Historial", self._timeline),
                         ("⚙ Inicio auto", setup_autostart)]:
            tk.Button(bot, text=txt, command=cmd,
                      bg=CARD2, fg=MUTED, font=(FN,8),
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      activebackground=CARD, activeforeground=TEXT
                      ).pack(side="left", padx=2)

    def _slide(self, val=None):
        if val is None: val = self._sl.get()
        col = mood_color(val)
        self._num_lbl.config(text=f"{val:+d}" if val!=0 else " 0", fg=col)
        self._emoji_lbl.config(text=mood_emoji(val))
        self._desc_lbl.config(text=DESCS[val+10], fg=col)

    def _reg(self):
        val  = self._sl.get()
        now  = datetime.datetime.now().isoformat(timespec="seconds")
        today= datetime.date.today().isoformat()
        self.data["entries"].append({"timestamp":now,"date":today,"value":val})
        save_data(self.data)
        self._refresh()
        col = mood_color(val)
        self._rbtn.config(bg=col, text="  ✓  GUARDADO  ")
        if self._after: self.root.after_cancel(self._after)
        self._after = self.root.after(1100,
            lambda: self._rbtn.config(bg=ACCENT, text="▶  REGISTRAR"))

    def _refresh(self):
        today = datetime.date.today().isoformat()
        self._date_lbl.config(text=today)
        avg, cnt = today_stats(self.data)
        if avg is None:
            self._avg_lbl.config(text="Promedio hoy:  —", fg=TEXT)
            self._cnt_lbl.config(text="Sin registros aún")
        else:
            self._avg_lbl.config(text=f"Promedio hoy:  {avg:+.1f}", fg=mood_color(avg))
            self._cnt_lbl.config(text=f"{cnt} registro{'s' if cnt>1 else ''} hoy")
        # Last 5 entries today
        for w in self._hist_fr.winfo_children(): w.destroy()
        entries = [e for e in self.data["entries"] if e["date"]==today]
        last = entries[-5:]
        if not last: return
        tk.Label(self._hist_fr, text="Últimos:", bg=CARD,
                 fg=MUTED2, font=(FN,7)).pack(anchor="w")
        row = tk.Frame(self._hist_fr, bg=CARD); row.pack(anchor="w", pady=(2,0))
        for e in last:
            col = mood_color(e["value"])
            t   = datetime.datetime.fromisoformat(e["timestamp"]).strftime("%H:%M")
            pill= tk.Frame(row, bg=CARD2, padx=5, pady=2)
            pill.pack(side="left", padx=(0,4))
            tk.Label(pill, text=f"{e['value']:+d}", bg=CARD2,
                     fg=col, font=(FN,8,"bold")).pack()
            tk.Label(pill, text=t, bg=CARD2,
                     fg=MUTED, font=(FN,7)).pack()

    def _timeline(self):
        recalculate(self.data)
        TimelineWindow(self.root, self.data)

    def _close(self):
        recalculate(self.data)
        self.root.destroy()

    def run(self):
        self._slide(0)
        self.root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if IS_LINUX and "--detached" not in sys.argv:
        try:
            if sys.stdin and os.isatty(sys.stdin.fileno()):
                import subprocess
                cmd = [APP_PATH, "--detached"] if getattr(sys, "frozen", False) \
                    else [sys.executable, APP_PATH, "--detached"]
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL, start_new_session=True)
                print("MoodTracker iniciado ✓")
                sys.exit(0)
        except Exception:
            pass
    MoodWidget().run()
