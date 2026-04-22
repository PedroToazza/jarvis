"""
commands/screenshot.py — Só screenshot
"""
import os
from datetime import datetime

try:
    from PIL import ImageGrab
    _OK = True
except ImportError:
    _OK = False


class ScreenshotCommand:
    def __init__(self, tts):
        self.tts = tts

    def take(self):
        if not _OK:
            self.tts.speak("Screenshot indisponível."); return
        try:
            folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
            os.makedirs(folder, exist_ok=True)
            filename = datetime.now().strftime("jarvis_%Y%m%d_%H%M%S.png")
            path = os.path.join(folder, filename)
            ImageGrab.grab().save(path)
            self.tts.speak(f"Screenshot salvo.")
        except Exception as e:
            self.tts.speak("Erro ao capturar a tela.")
            print(f"  screenshot: {e}")