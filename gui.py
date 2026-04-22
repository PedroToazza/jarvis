"""
gui.py — Interface cyberpunk roxa neon
"""
import math
import os
import random
import tkinter as tk
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


BG_DEEP       = "#0a0318"
BG_MID        = "#14092a"
BG_LIGHT      = "#1f1340"
ACCENT        = "#b445ff"
ACCENT_BRIGHT = "#d97eff"
ACCENT_GLOW   = "#9d38ff"
ACCENT_DIM    = "#5b2a94"
ACCENT_DARK   = "#2e1452"
CORE          = "#e7b8ff"
MAGENTA       = "#ff44e8"
TEXT_MUTED    = "#4a3a66"
TEXT_DIM      = "#8067a8"
TEXT_LIGHT    = "#d8c4f0"
TEXT_WHITE    = "#ffffff"
SUCCESS       = "#5df7b8"
DANGER        = "#ff3d6e"
WARNING       = "#ffb347"


class StarField(tk.Canvas):
    def __init__(self, parent, width, height, n_stars=140, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=BG_DEEP, highlightthickness=0, **kwargs)
        self.w = width; self.h = height
        self.stars = []
        for _ in range(n_stars):
            hp = random.random()
            if hp < 0.5:   base = (180, 69, 255)
            elif hp < 0.8: base = (217, 126, 255)
            else:          base = (255, 68, 232)
            self.stars.append({
                'x': random.uniform(0, width), 'y': random.uniform(0, height),
                'r': random.uniform(0.4, 2.4),
                'alpha': random.uniform(0.3, 1.0),
                'speed': random.uniform(0.003, 0.018),
                'phase': random.uniform(0, 6.28),
                'color': base, 'vy': random.uniform(-0.08, 0.08),
            })
        self._animate()

    def _animate(self):
        self.delete('star')
        for s in self.stars:
            s['phase'] += s['speed']
            s['y'] += s['vy']
            if s['y'] < 0: s['y'] = self.h
            elif s['y'] > self.h: s['y'] = 0
            a = max(0.15, min(1.0, s['alpha'] * (0.5 + 0.5 * math.sin(s['phase']))))
            r, g, b = s['color']
            r = int(r*a + 10*(1-a)); g = int(g*a*0.3); b = int(b*a)
            color = f'#{r:02x}{g:02x}{b:02x}'
            rad = s['r']
            self.create_oval(s['x']-rad, s['y']-rad, s['x']+rad, s['y']+rad,
                             fill=color, outline='', tags='star')
        self.after(50, self._animate)


class CoreOrb(tk.Canvas):
    def __init__(self, parent, size=300, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=BG_DEEP, highlightthickness=0, **kwargs)
        self.size = size; self.cx = size//2; self.cy = size//2
        self.phase = 0.0; self.amp = 0.2; self.target = 0.2
        self.status = 'idle'
        self.particles = []
        for _ in range(70):
            self.particles.append({
                'angle': random.uniform(0, 6.28),
                'tilt': random.uniform(-1, 1),
                'radius': random.uniform(0.35, 0.88),
                'speed': random.uniform(0.008, 0.030),
                'size': random.uniform(1.5, 3.8),
                'phase': random.uniform(0, 6.28),
                'color_pick': random.random(),
            })
        self._animate()

    def set_status(self, status):
        if status == self.status: return
        self.status = status
        self.target = {'off': 0.05, 'idle': 0.22, 'listening': 0.5,
                        'processing': 0.38, 'speaking': 0.78}.get(status, 0.2)

    def _animate(self):
        self.amp += (self.target - self.amp) * 0.1
        vk = 0.0
        if self.status == 'speaking': vk = random.uniform(-0.18, 0.28)
        elif self.status == 'processing': vk = math.sin(self.phase * 3) * 0.12
        elif self.status == 'listening': vk = math.sin(self.phase * 2) * 0.15

        self.phase += 0.06
        self.delete('all')
        max_r = self.size * 0.42

        for i, (shade, factor) in enumerate([(ACCENT_DARK, 1.05),
                                              (ACCENT_DIM, 0.95),
                                              (ACCENT, 0.85)]):
            hr = max_r * (factor + vk * 0.1)
            self.create_oval(self.cx-hr, self.cy-hr, self.cx+hr, self.cy+hr,
                             outline=shade, width=1 + i)

        pulse = self.amp * (0.9 + 0.1 * math.sin(self.phase * 1.5))
        ring_r = max_r * (0.78 + pulse * 0.22)
        self.create_oval(self.cx-ring_r, self.cy-ring_r, self.cx+ring_r, self.cy+ring_r,
                         outline=ACCENT_BRIGHT, width=2)

        inner_r = max_r * (0.55 + pulse * 0.15)
        self.create_oval(self.cx-inner_r, self.cy-inner_r, self.cx+inner_r, self.cy+inner_r,
                         outline=ACCENT_GLOW, width=1)

        for p in self.particles:
            p['angle'] += p['speed'] * (1 + self.amp * 2.5)
            p['phase'] += 0.05
            r = max_r * p['radius'] * (0.85 + 0.15 * math.sin(p['phase']))
            x = self.cx + math.cos(p['angle']) * r
            y = self.cy + math.sin(p['angle']) * r * (0.3 + abs(p['tilt']) * 0.5)
            depth = (math.sin(p['angle']) + 1) / 2
            s = p['size'] * (0.6 + depth * 0.8)
            if p['color_pick'] > 0.9:
                color = MAGENTA if depth > 0.7 else ACCENT_DIM
            else:
                if depth > 0.7: color = CORE
                elif depth > 0.4: color = ACCENT_BRIGHT
                elif depth > 0.2: color = ACCENT
                else: color = ACCENT_DIM
            self.create_oval(x-s, y-s, x+s, y+s, fill=color, outline='')

        core_r = self.size * 0.045
        if self.status != 'off':
            core_r *= 1 + self.amp * 0.9 + vk * 0.3
        self.create_oval(self.cx-core_r, self.cy-core_r, self.cx+core_r, self.cy+core_r,
                         fill=CORE if self.status != 'off' else TEXT_MUTED,
                         outline=MAGENTA, width=2)
        if self.status != 'off':
            tiny = core_r * 0.35
            self.create_oval(self.cx-tiny, self.cy-tiny, self.cx+tiny, self.cy+tiny,
                             fill=TEXT_WHITE, outline='')
        self.after(33, self._animate)


class JarvisApp(ctk.CTk):
    WIDTH = 1080; HEIGHT = 640

    def __init__(self, shared_state, on_toggle=None):
        super().__init__()
        self.shared_state = shared_state
        self.on_toggle = on_toggle
        self.is_on = True
        self.log_entries = []

        self.title("J.A.R.V.I.S.")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.configure(fg_color=BG_DEEP)
        self.minsize(900, 560)

        try:
            icon = os.path.join(os.path.dirname(__file__), "jarvis.ico")
            if os.path.exists(icon): self.iconbitmap(icon)
        except Exception: pass

        self.starfield = StarField(self, self.WIDTH, self.HEIGHT, n_stars=160)
        self.starfield.place(x=0, y=0, relwidth=1, relheight=1)

        topbar = ctk.CTkFrame(self, fg_color="transparent", height=44)
        topbar.place(x=0, y=0, relwidth=1)
        ctk.CTkLabel(topbar, text="◈  J A R V I S",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=ACCENT_BRIGHT).pack(side="left", padx=22, pady=10)
        self.header_status = ctk.CTkLabel(topbar, text="Aguardando comando",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_DIM)
        self.header_status.pack(side="left", padx=14, pady=12)
        for label, color in [("MIC", SUCCESS), ("NET", ACCENT_BRIGHT),
                              ("CPU", MAGENTA), ("AI", WARNING)]:
            ctk.CTkLabel(topbar, text=f"● {label}",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=color).pack(side="right", padx=6, pady=12)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        self.orb = CoreOrb(center, size=300)
        self.orb.pack()
        self.status_label = ctk.CTkLabel(center, text="READY",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=ACCENT_BRIGHT)
        self.status_label.pack(pady=(14, 2))
        self.sub_status = ctk.CTkLabel(center, text='diga "jarvis"',
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_DIM)
        self.sub_status.pack()
        self.power_btn = ctk.CTkButton(center, text="⏻",
            width=52, height=52, corner_radius=26,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=BG_LIGHT, hover_color=ACCENT_DARK,
            text_color=SUCCESS, border_width=2, border_color=ACCENT,
            command=self._toggle_power)
        self.power_btn.pack(pady=(18, 0))

        log_panel = ctk.CTkFrame(self, fg_color=BG_MID, corner_radius=8,
            border_width=1, border_color=ACCENT_DIM, width=340, height=240)
        log_panel.place(x=20, y=self.HEIGHT - 260)
        log_panel.pack_propagate(False)
        log_header = ctk.CTkFrame(log_panel, fg_color="transparent", height=34)
        log_header.pack(fill="x", padx=12, pady=(10, 4))
        log_header.pack_propagate(False)
        ctk.CTkLabel(log_header, text="● J.A.R.V.I.S. REALTIME",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=SUCCESS).pack(side="left")
        ctk.CTkLabel(log_header, text="▣",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=TEXT_DIM).pack(side="right")

        btn_row = ctk.CTkFrame(log_panel, fg_color="transparent", height=28)
        btn_row.pack(fill="x", padx=12, pady=2)
        for label, color in [("ONLINE", SUCCESS), ("OFFLINE", DANGER),
                              ("INTERROMPER", WARNING)]:
            ctk.CTkLabel(btn_row, text=label,
                font=ctk.CTkFont(family="Consolas", size=8, weight="bold"),
                text_color=color, fg_color=BG_LIGHT,
                corner_radius=3, padx=8, pady=2).pack(side="left", padx=2)

        self.log_box = ctk.CTkTextbox(log_panel,
            fg_color=BG_DEEP, text_color=TEXT_LIGHT,
            font=ctk.CTkFont(family="Consolas", size=10),
            border_width=0, corner_radius=4, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(4, 10))
        self.log_box.configure(state="disabled")

        stats_panel = ctk.CTkFrame(self, fg_color=BG_MID, corner_radius=8,
            border_width=1, border_color=ACCENT_DIM, width=260, height=140)
        stats_panel.place(x=self.WIDTH - 280, y=self.HEIGHT - 160)
        stats_panel.pack_propagate(False)
        ctk.CTkLabel(stats_panel, text="● STATUS",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=ACCENT_BRIGHT).pack(anchor="w", padx=12, pady=(8, 4))
        self.stats_power = ctk.CTkLabel(stats_panel, text="POWER     :  LIGADO",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=SUCCESS, anchor="w")
        self.stats_power.pack(anchor="w", padx=14, pady=1)
        self.stats_voice = ctk.CTkLabel(stats_panel, text="VOICE     :  COQUI XTTS",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=ACCENT_BRIGHT, anchor="w")
        self.stats_voice.pack(anchor="w", padx=14, pady=1)
        self.stats_model = ctk.CTkLabel(stats_panel, text="MODEL     :  LLAMA 3.1",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=ACCENT_BRIGHT, anchor="w")
        self.stats_model.pack(anchor="w", padx=14, pady=1)
        self.stats_memory = ctk.CTkLabel(stats_panel, text="MEMORY    :  0 TURNS",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_LIGHT, anchor="w")
        self.stats_memory.pack(anchor="w", padx=14, pady=1)
        self.stats_state = ctk.CTkLabel(stats_panel, text="STATE     :  IDLE",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=ACCENT_BRIGHT, anchor="w")
        self.stats_state.pack(anchor="w", padx=14, pady=1)

        corner = ctk.CTkFrame(self, fg_color="transparent")
        corner.place(x=20, y=60)
        ctk.CTkLabel(corner, text="█▓▒░",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=ACCENT_DIM).pack(anchor="w")
        self.mode_label = ctk.CTkLabel(corner, text="MODO\nREADY",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=ACCENT_BRIGHT, justify="left")
        self.mode_label.pack(anchor="w", pady=(4, 0))

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._add_log("SISTEMA", "Jarvis inicializado", SUCCESS)
        self._update_ui()

    def _add_log(self, source, message, color=TEXT_LIGHT):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_entries.append((ts, source, message, color))
        self.log_entries = self.log_entries[-100:]
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {source:<8} {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _update_ui(self):
        if not self.is_on: status = 'off'
        elif self.shared_state.get('is_speaking'): status = 'speaking'
        elif self.shared_state.get('is_busy'): status = 'processing'
        elif self.shared_state.get('status') == 'listening': status = 'listening'
        else: status = 'idle'
        self.orb.set_status(status)
        labels = {
            'off': ('OFFLINE', 'desligado', TEXT_DIM),
            'idle': ('READY', 'diga "jarvis"', ACCENT_BRIGHT),
            'listening': ('OUVINDO', 'fale seu comando', SUCCESS),
            'processing': ('PROCESSANDO', 'analisando...', WARNING),
            'speaking': ('RESPONDENDO', 'jarvis está falando', MAGENTA),
        }
        main, sub, color = labels.get(status, ('—', '', TEXT_DIM))
        self.status_label.configure(text=main, text_color=color)
        self.sub_status.configure(text=sub)
        self.header_status.configure(text=sub)
        self.stats_state.configure(text=f"STATE     :  {status.upper()}", text_color=color)
        self.mode_label.configure(text=f"MODO\n{main}", text_color=color)
        mem = self.shared_state.get('memory_turns', 0)
        self.stats_memory.configure(text=f"MEMORY    :  {mem} TURNS")

        last = self.shared_state.get('last_command', '')
        if last and (not self.log_entries or self.log_entries[-1][2] != f"> {last}"):
            self._add_log("VOCÊ", f"> {last}", TEXT_LIGHT)
        last_reply = self.shared_state.get('last_reply', '')
        if last_reply:
            already = any(e[2] == last_reply and e[1] == "JARVIS"
                          for e in self.log_entries[-3:])
            if not already:
                self._add_log("JARVIS", last_reply, ACCENT_BRIGHT)
        self.after(100, self._update_ui)

    def _toggle_power(self):
        self.is_on = not self.is_on
        self.shared_state['is_active'] = self.is_on
        if self.is_on:
            self.power_btn.configure(text_color=SUCCESS, border_color=ACCENT)
            self.stats_power.configure(text="POWER     :  LIGADO", text_color=SUCCESS)
            self._add_log("SISTEMA", "ligado", SUCCESS)
        else:
            self.power_btn.configure(text_color=DANGER, border_color=DANGER)
            self.stats_power.configure(text="POWER     :  DESLIGADO", text_color=DANGER)
            self._add_log("SISTEMA", "desligado", DANGER)
        if callable(self.on_toggle): self.on_toggle(self.is_on)

    def _on_close(self):
        self.shared_state['is_active'] = False
        self.destroy()
        os._exit(0)