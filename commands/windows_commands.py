"""
commands/windows_commands.py — Automação Windows
"""
import os
import subprocess
import time
from datetime import datetime

try:
    from PIL import ImageGrab
    _SCREENSHOT_OK = True
except ImportError:
    _SCREENSHOT_OK = False


class WindowsCommands:
    def __init__(self, tts):
        self.tts = tts

    def shutdown(self, seconds: int = 30):
        self.tts.speak(
            f"Desligando o computador em {seconds} segundos. "
            "Diga cancelar desligamento para abortar."
        )
        subprocess.Popen(f'shutdown /s /t {seconds}', shell=True)

    def restart(self, seconds: int = 30):
        self.tts.speak(f"Reiniciando em {seconds} segundos.")
        subprocess.Popen(f'shutdown /r /t {seconds}', shell=True)

    def cancel_shutdown(self):
        subprocess.Popen('shutdown /a', shell=True)
        self.tts.speak("Desligamento cancelado.")

    def lock(self):
        self.tts.speak("Bloqueando o computador.")
        time.sleep(0.6)
        subprocess.Popen('rundll32.exe user32.dll,LockWorkStation', shell=True)

    def sleep(self):
        self.tts.speak("Entrando em modo de suspensão.")
        time.sleep(0.6)
        subprocess.Popen('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True)

    def screenshot(self):
        if not _SCREENSHOT_OK:
            self.tts.speak("Screenshot indisponível.")
            return
        try:
            folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
            os.makedirs(folder, exist_ok=True)
            filename = datetime.now().strftime("jarvis_%Y%m%d_%H%M%S.png")
            path = os.path.join(folder, filename)
            ImageGrab.grab().save(path)
            self.tts.speak(f"Screenshot salvo.")
        except Exception as e:
            self.tts.speak("Erro ao capturar a tela.")
            print(f"  Screenshot erro: {e}")