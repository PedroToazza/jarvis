"""
commands/close_commands.py — Fechar apps (processo) ou abas (site)
"""
import subprocess
import time
import unicodedata

try:
    import psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False

try:
    import pygetwindow as gw
    _GW_OK = True
except ImportError:
    _GW_OK = False

try:
    import pyautogui
    _PYAUTO_OK = True
except ImportError:
    _PYAUTO_OK = False


WEB_SITES = {
    "youtube", "facebook", "instagram", "twitter", "x",
    "gmail", "outlook", "netflix", "github", "reddit",
    "linkedin", "twitch", "disney", "prime", "whatsapp web",
    "globo", "uol", "g1", "google", "chatgpt", "bing",
}


APP_PROCESS_MAP = {
    "chrome":                  ["chrome.exe"],
    "google chrome":           ["chrome.exe"],
    "firefox":                 ["firefox.exe"],
    "edge":                    ["msedge.exe"],
    "spotify":                 ["Spotify.exe"],
    "discord":                 ["Discord.exe", "DiscordPTB.exe"],
    "steam":                   ["steam.exe"],
    "notepad":                 ["notepad.exe"],
    "bloco de notas":          ["notepad.exe"],
    "calculadora":             ["CalculatorApp.exe", "Calculator.exe"],
    "vscode":                  ["Code.exe"],
    "code":                    ["Code.exe"],
    "visual studio code":      ["Code.exe"],
    "paint":                   ["mspaint.exe"],
    "whatsapp":                ["WhatsApp.exe"],
    "word":                    ["WINWORD.EXE"],
    "excel":                   ["EXCEL.EXE"],
    "powerpoint":              ["POWERPNT.EXE"],
    "obs":                     ["obs64.exe", "obs32.exe"],
    "terminal":                ["WindowsTerminal.exe", "wt.exe"],
    "cmd":                     ["cmd.exe"],
    "powershell":              ["powershell.exe", "pwsh.exe"],
    "explorer":                ["explorer.exe"],
    "explorador":              ["explorer.exe"],
    "explorador de arquivos":  ["explorer.exe"],
}


def _normalize(s: str) -> str:
    s = unicodedata.normalize('NFD', s or "")
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().strip()


class CloseCommands:
    def __init__(self, tts):
        self.tts = tts

    def close(self, target: str):
        target = (target or "").strip()
        if not target:
            self.tts.speak("O que você quer fechar?")
            return

        norm = _normalize(target)

        if self._is_website(norm):
            self._close_current_tab(norm)
            return

        for key, procs in APP_PROCESS_MAP.items():
            if _normalize(key) in norm or norm in _normalize(key):
                self._kill_processes(procs, key)
                return

        if norm.endswith(".exe"):
            self._kill_processes([norm], norm)
            return

        if self._close_window_by_title(target):
            return

        self.tts.speak(f"Não encontrei {target} aberto.")

    def _is_website(self, norm: str) -> bool:
        for site in WEB_SITES:
            if site in norm:
                return True
        return False

    def _kill_processes(self, proc_names: list, friendly_name: str):
        if not _PSUTIL_OK:
            killed = False
            for name in proc_names:
                result = subprocess.run(
                    f'taskkill /F /IM "{name}"',
                    shell=True, capture_output=True
                )
                if result.returncode == 0:
                    killed = True
            if killed: self.tts.speak(f"Fechei {friendly_name}.")
            else: self.tts.speak(f"{friendly_name} não está aberto.")
            return

        killed_count = 0
        target_set   = {n.lower() for n in proc_names}
        for p in psutil.process_iter(['name']):
            try:
                if (p.info['name'] or '').lower() in target_set:
                    p.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_count > 0:
            self.tts.speak(f"Fechei {friendly_name}.")
        else:
            self.tts.speak(f"{friendly_name} não está aberto.")

    def _close_current_tab(self, site_name: str):
        if not _PYAUTO_OK:
            self.tts.speak("Preciso do pyautogui para fechar abas.")
            return

        if _GW_OK:
            try:
                for w in gw.getAllWindows():
                    title = (w.title or "").lower()
                    if any(b in title for b in ("chrome", "firefox", "edge",
                                                  "opera", "brave")):
                        try:
                            w.activate()
                            time.sleep(0.3)
                            break
                        except Exception:
                            continue
            except Exception:
                pass

        try:
            pyautogui.hotkey('ctrl', 'w')
            shown = site_name
            for s in WEB_SITES:
                if s in site_name:
                    shown = s
                    break
            self.tts.speak(f"Aba do {shown} fechada.")
        except Exception as e:
            self.tts.speak("Não consegui fechar a aba.")
            print(f"  close_tab: {e}")

    def _close_window_by_title(self, query: str) -> bool:
        if not _GW_OK:
            return False
        try:
            qnorm = _normalize(query)
            for w in gw.getAllWindows():
                if w.title and qnorm in _normalize(w.title):
                    try:
                        w.close()
                        self.tts.speak("Janela fechada.")
                        return True
                    except Exception:
                        continue
        except Exception as e:
            print(f"  close_window: {e}")
        return False