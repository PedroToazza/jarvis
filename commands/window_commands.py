"""
commands/window_commands.py — Minimize + reutilização de navegador
"""
import time
import unicodedata
import webbrowser

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


BROWSER_KEYWORDS = ('chrome', 'firefox', 'edge', 'opera', 'brave')


def _norm(s: str) -> str:
    s = unicodedata.normalize('NFD', s or "")
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().strip()


def find_browser_window():
    if not _GW_OK: return None
    try:
        for w in gw.getAllWindows():
            if w.title and any(b in w.title.lower() for b in BROWSER_KEYWORDS):
                return w
    except Exception: pass
    return None


def find_window_by_keyword(keyword: str):
    if not _GW_OK: return None
    kw = _norm(keyword)
    try:
        for w in gw.getAllWindows():
            if w.title and kw in _norm(w.title):
                return w
    except Exception: pass
    return None


def focus_window(w) -> bool:
    if not w: return False
    try:
        if w.isMinimized: w.restore()
        w.activate()
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"  focus: {e}"); return False


def open_url_in_browser(url: str) -> bool:
    """Se navegador já aberto, abre em nova aba. Senão abre navegador padrão."""
    browser = find_browser_window()
    if browser and _PYAUTO_OK:
        try:
            if focus_window(browser):
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.4)
                pyautogui.typewrite(url, interval=0.01)
                time.sleep(0.2)
                pyautogui.press('enter')
                return True
        except Exception as e:
            print(f"  open_url: {e}")
    webbrowser.open(url)
    return False


class WindowCommands:
    def __init__(self, tts):
        self.tts = tts

    def minimize(self, target: str = ""):
        if not _GW_OK:
            self.tts.speak("Controle de janelas indisponível."); return
        target = (target or "").strip().lower()
        if not target or target in ("todas", "tudo", "all"):
            count = 0
            try:
                for w in gw.getAllWindows():
                    if w.title and w.visible and not w.isMinimized:
                        try: w.minimize(); count += 1
                        except Exception: continue
                self.tts.speak(f"Minimizei {count} janelas.")
            except Exception as e:
                self.tts.speak("Erro ao minimizar.")
                print(f"  minimize: {e}")
            return
        kw = _norm(target)
        found = 0
        try:
            for w in gw.getAllWindows():
                if w.title and kw in _norm(w.title) and not w.isMinimized:
                    try: w.minimize(); found += 1
                    except Exception: continue
        except Exception as e:
            print(f"  minimize: {e}")
        if found > 0: self.tts.speak(f"Minimizei {target}.")
        else: self.tts.speak(f"Não achei {target} aberto.")