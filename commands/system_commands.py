"""
commands/system_commands.py — Apps (foca se já aberto), volume, brilho
"""
import os
import re
import subprocess
import glob

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _VOLUME_OK = True
except Exception:
    _VOLUME_OK = False

try:
    import screen_brightness_control as sbc
    _BRIGHTNESS_OK = True
except Exception:
    _BRIGHTNESS_OK = False

from .window_commands import find_window_by_keyword, focus_window, open_url_in_browser


EXPLICIT_APPS = {
    "chrome":                 ("path", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    "google chrome":          ("path", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    "firefox":                ("path", r"C:\Program Files\Mozilla Firefox\firefox.exe"),
    "edge":                   ("path", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    "google":                 ("url",  "https://www.google.com"),
    "calculadora":            ("cmd",  "calc.exe"),
    "notepad":                ("cmd",  "notepad.exe"),
    "bloco de notas":         ("cmd",  "notepad.exe"),
    "paint":                  ("cmd",  "mspaint.exe"),
    "explorador":             ("cmd",  "explorer.exe"),
    "explorador de arquivos": ("cmd",  "explorer.exe"),
    "terminal":               ("cmd",  "wt.exe"),
    "cmd":                    ("cmd",  "cmd.exe"),
    "powershell":             ("cmd",  "powershell.exe"),
    "gerenciador de tarefas": ("cmd",  "taskmgr.exe"),
    "painel de controle":     ("cmd",  "control.exe"),
    "spotify":                ("uri",  "spotify:"),
    "discord":                ("cmd",  r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe"),
    "steam":                  ("path", r"C:\Program Files (x86)\Steam\steam.exe"),
    "vscode":                 ("cmd",  "code"),
    "code":                   ("cmd",  "code"),
    "visual studio code":     ("cmd",  "code"),
    "word":                   ("path", r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"),
    "excel":                  ("path", r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"),
    "whatsapp":               ("path", r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
    "configurações":          ("uri",  "ms-settings:"),
    "configuracoes":          ("uri",  "ms-settings:"),
    "wifi":                   ("uri",  "ms-settings:network-wifi"),
    "bluetooth":              ("uri",  "ms-settings:bluetooth"),
    "tela":                   ("uri",  "ms-settings:display"),
    "som":                    ("uri",  "ms-settings:sound"),
}


def _normalize(s):
    import unicodedata
    s = unicodedata.normalize('NFD', s or "")
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().strip()


def find_shortcut(query):
    q = _normalize(query)
    if not q: return None
    matches = []
    bases = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    for base in bases:
        if not os.path.isdir(base): continue
        for root, _, files in os.walk(base):
            for fname in files:
                if not fname.lower().endswith('.lnk'): continue
                name = _normalize(os.path.splitext(fname)[0])
                path = os.path.join(root, fname)
                if name == q: return path
                if name.startswith(q): matches.append((1, path, name))
                elif q in name: matches.append((2, path, name))
    if matches:
        matches.sort(key=lambda x: (x[0], len(x[2])))
        return matches[0][1]
    return None


class SystemCommands:
    def __init__(self, tts):
        self.tts = tts
        self._vol_interface = None
        if _VOLUME_OK:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._vol_interface = cast(interface, POINTER(IAudioEndpointVolume))
            except Exception: pass

    def open_app(self, query):
        q = (query or "").strip()
        if not q: self.tts.speak("O que abrir?"); return
        qnorm = _normalize(q)

        if qnorm in EXPLICIT_APPS:
            return self._launch_explicit(qnorm, EXPLICIT_APPS[qnorm])

        best = None; best_score = 0
        for key, payload in EXPLICIT_APPS.items():
            key_norm = _normalize(key)
            if key_norm == qnorm: best = (key, payload); break
            if key_norm in qnorm:
                s = len(key_norm)
                if s > best_score: best = (key, payload); best_score = s
            elif qnorm in key_norm and len(qnorm) >= 4:
                s = len(qnorm)
                if s > best_score: best = (key, payload); best_score = s
        if best: return self._launch_explicit(best[0], best[1])

        shortcut = find_shortcut(q)
        if shortcut:
            try:
                existing = find_window_by_keyword(q)
                if existing and focus_window(existing):
                    self.tts.speak(f"Focando {q}."); return
                os.startfile(shortcut)
                self.tts.speak(f"Abrindo {os.path.splitext(os.path.basename(shortcut))[0]}.")
                return
            except Exception as e: print(f"  atalho: {e}")

        try:
            subprocess.Popen(q, shell=True)
            self.tts.speak(f"Tentando abrir {q}.")
        except Exception:
            self.tts.speak(f"Não encontrei '{q}'.")

    def _launch_explicit(self, name, payload):
        kind, target = payload
        try:
            if kind == "url":
                open_url_in_browser(target)
                self.tts.speak(f"Abrindo {name}.")
            elif kind == "uri":
                os.startfile(target)
                self.tts.speak(f"Abrindo {name}.")
            elif kind == "path":
                existing = find_window_by_keyword(name)
                if existing and focus_window(existing):
                    self.tts.speak(f"Focando {name}."); return
                path = os.path.expandvars(target)
                if '*' in path:
                    m = glob.glob(path); path = m[0] if m else path
                if os.path.exists(path):
                    subprocess.Popen([path])
                else:
                    subprocess.Popen(os.path.basename(path), shell=True)
                self.tts.speak(f"Abrindo {name}.")
            elif kind == "cmd":
                existing = find_window_by_keyword(name)
                if existing and focus_window(existing):
                    self.tts.speak(f"Focando {name}."); return
                subprocess.Popen(os.path.expandvars(target), shell=True)
                self.tts.speak(f"Abrindo {name}.")
        except Exception as e:
            print(f"  _launch_explicit: {e}")
            self.tts.speak(f"Não consegui abrir {name}.")

    def handle_volume(self, text):
        if not self._vol_interface:
            self.tts.speak("Volume indisponível."); return
        if any(w in text for w in ('mudo','silêncio','silencio','mutar','mute')):
            self._vol_interface.SetMute(1, None); self.tts.speak("Silenciado."); return
        if any(w in text for w in ('desmutar','tirar mudo','unmute')):
            self._vol_interface.SetMute(0, None); self.tts.speak("Volume restaurado."); return
        m = re.search(r'(\d+)', text)
        if m:
            level = max(0, min(100, int(m.group(1))))
            self._vol_interface.SetMasterVolumeLevelScalar(level/100.0, None)
            self.tts.speak(f"Volume em {level} por cento."); return
        current = int(self._vol_interface.GetMasterVolumeLevelScalar() * 100)
        if 'up' in text or any(w in text for w in ('aumentar','subir')):
            new = min(100, current + 10)
            self._vol_interface.SetMasterVolumeLevelScalar(new/100.0, None)
            self.tts.speak(f"Volume em {new} por cento.")
        elif 'down' in text or any(w in text for w in ('diminuir','baixar')):
            new = max(0, current - 10)
            self._vol_interface.SetMasterVolumeLevelScalar(new/100.0, None)
            self.tts.speak(f"Volume em {new} por cento.")
        else:
            self.tts.speak(f"Volume em {current} por cento.")

    def handle_brightness(self, text):
        if not _BRIGHTNESS_OK:
            self.tts.speak("Brilho indisponível."); return
        def _get():
            try: return sbc.get_brightness(display=0)[0]
            except Exception: return 50
        def _set(v):
            try: sbc.set_brightness(v, display=0)
            except Exception as e: print(f"  brilho: {e}")
        m = re.search(r'(\d+)', text)
        if m:
            level = max(0, min(100, int(m.group(1))))
            _set(level); self.tts.speak(f"Brilho em {level} por cento."); return
        cur = _get()
        if 'up' in text or any(w in text for w in ('aumentar','subir')):
            _set(min(100, cur+10)); self.tts.speak(f"Brilho em {min(100,cur+10)} por cento.")
        elif 'down' in text or any(w in text for w in ('diminuir','baixar')):
            _set(max(0, cur-10)); self.tts.speak(f"Brilho em {max(0,cur-10)} por cento.")
        else:
            self.tts.speak(f"Brilho em {cur} por cento.")