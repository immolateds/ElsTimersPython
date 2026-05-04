import tkinter as tk
import time
import threading
import winsound
from pynput import keyboard
 
# ─── Timer Model ────────────────────────────────────────────────────────────────
 
# Distinct beep signatures per timer: (frequency_hz, duration_ms)
BEEP_SIGNATURES = {
    "FS":  (880, 400),  # high pitch
    "NP":  (520, 400),  # mid pitch
    "TSS": (300, 400),  # low pitch
}
 
class Timer:
    def __init__(self, title):
        self.title = title
        self.duration = -1
        self.start_time = -1
        self.active = False
        self._expired_notified = False
        self._beep_freq, self._beep_dur = BEEP_SIGNATURES.get(title, (1000, 300))
 
    def start(self, duration):
        if not self.active:
            self.duration = duration
            self.start_time = time.time()
            self.active = True
            self._expired_notified = False
 
    def get_remaining(self):
        if not self.active:
            return 0
        elapsed = int(time.time() - self.start_time)
        remaining = self.duration - elapsed
        if remaining <= 0:
            self.active = False
            return 0
        return remaining
 
    def check_and_notify(self):
        """Plays a beep the moment the timer expires."""
        if not self.active and self.start_time != -1 and not self._expired_notified:
            self._expired_notified = True
            freq, dur = self._beep_freq, self._beep_dur
            threading.Thread(
                target=lambda: winsound.Beep(freq, dur),
                daemon=True
            ).start()
 
    def reset(self):
        self.active = False
        self.start_time = -1
        self._expired_notified = False
 
    def get_display_text(self):
        if self.active:
            return f"{self.title}: {self.get_remaining()}s"
        else:
            return f"{self.title}  \u2726 READY"
 
 
# ─── Main App ───────────────────────────────────────────────────────────────────
 
class ElswordTimerApp:
 
    NP_KEYS = {'f', 't', 'r', 'e', 'q', 'a', 's', 'd'}
 
    # Colours
    BG          = "#0d0d0f"
    CARD_BG     = "#17171f"
    CARD_IDLE   = "#2a2a3a"
    CARD_ACTIVE = "#3a3a5a"
    FG_READY    = "#00e676"
    FG_NORMAL   = "#e8e8f0"
    FG_WARN     = "#ffd740"
    FG_DANGER   = "#ff5252"
 
    BADGE_COLORS = {
        "Neutral":      ("#1a1a2a", "#4a4a6a", "\u25cf NEUTRAL"),
        "Changing":     ("#1a1800", "#c8b400", "\u25c8 CHANGING"),
        "Freed Shadow": ("#001a10", "#00c87a", "\u25b2 FREED SHADOW"),
        "Night Parade": ("#1a0010", "#c800a0", "\u25c6 NIGHT PARADE"),
        "TSS":          ("#00101a", "#0096c8", "\u25a0 TSS"),
    }
 
    def __init__(self, root):
        self.root = root
        self.root.title("Elsword Timers")
        self.root.configure(bg=self.BG)
        self.root.geometry("280x360")
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)
 
        self.timers = {
            "FS":  Timer("FS"),
            "NP":  Timer("NP"),
            "TSS": Timer("TSS"),
        }
        self.title_state = "Neutral"
        self._ctrl_held  = False
        self._pulse_on   = True
 
        # ── Load images ──────────────────────────────────────────────────────────
        IMAGE_PATHS = {
            "FS":  "Title_2050.png",
            "NP":  "TITLE_2320.png",
            "TSS": "TITLE_1840.png",
        }
        IMAGE_SIZE = (42, 42)
        self._images = {}
        for key, path in IMAGE_PATHS.items():
            try:
                from PIL import Image, ImageTk
                img = Image.open(path).resize(IMAGE_SIZE, Image.LANCZOS)
                self._images[key] = ImageTk.PhotoImage(img)
            except Exception:
                self._images[key] = None
 
        # ── State badge ───────────────────────────────────────────────────────────
        badge_wrap = tk.Frame(root, bg=self.BG)
        badge_wrap.pack(fill="x", padx=12, pady=(10, 6))
        self._badge_inner = tk.Frame(badge_wrap, bg="#1a1a2a",
                                     highlightbackground="#4a4a6a",
                                     highlightthickness=1)
        self._badge_inner.pack(fill="x")
        self._badge_lbl = tk.Label(
            self._badge_inner, text="\u25cf NEUTRAL",
            bg="#1a1a2a", fg="#6a6a9a",
            font=("Consolas", 10, "bold"), pady=5
        )
        self._badge_lbl.pack()
 
        # ── Timer cards ───────────────────────────────────────────────────────────
        self._timer_labels = {}
        self._card_borders = {}
 
        for key in ("FS", "NP", "TSS"):
            border = tk.Frame(root, bg=self.CARD_IDLE, pady=1, padx=1)
            border.pack(fill="x", padx=12, pady=5)
            inner = tk.Frame(border, bg=self.CARD_BG)
            inner.pack(fill="x")
 
            icon = self._images.get(key)
            if icon:
                tk.Label(inner, image=icon, bg=self.CARD_BG).pack(
                    side="left", padx=(10, 6), pady=8)
            else:
                tk.Frame(inner, bg=self.CARD_BG, width=8).pack(side="left")
 
            lbl = tk.Label(
                inner, text=f"{key}  \u2726 READY",
                bg=self.CARD_BG, fg=self.FG_READY,
                font=("Consolas", 15, "bold"), anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True, padx=(0, 12))
 
            self._timer_labels[key] = lbl
            self._card_borders[key] = border
 
        # ── Reset button ──────────────────────────────────────────────────────────
        tk.Button(
            root, text="\u27f3   Hard Reset All Timers",
            command=self.reset_all,
            bg="#13131e", fg="#55557a",
            activebackground="#1e1e30", activeforeground="#aaaacc",
            font=("Consolas", 9, "bold"), relief="flat", pady=7,
            cursor="hand2", bd=0
        ).pack(side="bottom", fill="x", padx=12, pady=(4, 10))
 
        # ── Start loops ───────────────────────────────────────────────────────────
        self._update_ui()
 
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
 
    # ── UI update ──────────────────────────────────────────────────────────────
 
    def _timer_color(self, key):
        t = self.timers[key]
        if not t.active:
            if t.start_time != -1:
                return self.FG_READY if self._pulse_on else "#007a40"
            return self.FG_READY
        r = t.get_remaining()
        if r <= 8:
            return self.FG_DANGER
        if r <= 15:
            return self.FG_WARN
        return self.FG_NORMAL
 
    def _update_ui(self):
        self._pulse_on = not self._pulse_on
 
        for key, lbl in self._timer_labels.items():
            t = self.timers[key]
            t.check_and_notify()
            lbl.config(text=t.get_display_text(), fg=self._timer_color(key))
            self._card_borders[key].config(
                bg=self.CARD_ACTIVE if t.active else self.CARD_IDLE
            )
 
        bg, fg, text = self.BADGE_COLORS.get(
            self.title_state,
            ("#1a1a2a", "#4a4a6a", f"\u25cf {self.title_state.upper()}")
        )
        self._badge_inner.config(bg=bg, highlightbackground=fg)
        self._badge_lbl.config(text=text, bg=bg, fg=fg)
 
        self.root.after(500, self._update_ui)
 
    # ── Key handling ───────────────────────────────────────────────────────────
 
    def _on_press(self, key):
        try:
            ch = key.char.lower() if hasattr(key, 'char') and key.char else None
        except AttributeError:
            ch = None
 
        if key == keyboard.Key.ctrl_r:
            self.title_state = "Changing"
            return
 
        if key == keyboard.Key.ctrl_l:
            self._ctrl_held = True
            if self.title_state == "Freed Shadow":
                if not self.timers["FS"].active:
                    print("Freed Shadow Activated")
                    self.timers["FS"].start(60)
                self.title_state = "Neutral"
            return
 
        if key == keyboard.Key.up and self.title_state == "Changing":
            self.title_state = "Freed Shadow"
            return
        if key == keyboard.Key.down and self.title_state == "Changing":
            self.title_state = "Night Parade"
            return
        if key == keyboard.Key.left and self.title_state == "Changing":
            self.title_state = "TSS"
            return
        if key == keyboard.Key.right and self.title_state == "Changing":
            print("Right arrow pressed — no state yet.")
            return
 
        if ch is None:
            return
 
        if ch in self.NP_KEYS and self.title_state == "Night Parade":
            if not self.timers["NP"].active:
                print("Night Parade Activated")
                self.timers["NP"].start(30)
            self.title_state = "Neutral"
 
        elif ch == '5' and self.title_state == "TSS":
            if not self.timers["TSS"].active:
                print("TSS Activated")
                self.timers["TSS"].start(30)
            self.title_state = "Neutral"
 
    def _on_release(self, key):
        if key == keyboard.Key.ctrl_l:
            self._ctrl_held = False
 
    # ── Reset & cleanup ────────────────────────────────────────────────────────
 
    def reset_all(self):
        for t in self.timers.values():
            t.reset()
 
    def _on_close(self):
        self._listener.stop()
        self.root.destroy()
 
 
# ─── Entry point ────────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    root = tk.Tk()
    app = ElswordTimerApp(root)
    root.mainloop()
