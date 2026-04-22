"""
tts_engine.py — Edge-TTS Microsoft (com pyttsx3 fallback)
"""
import asyncio
import os
import tempfile
import threading
import time

import config

try:
    import pygame
    pygame.mixer.init()
    _PYGAME_OK = True
except Exception:
    _PYGAME_OK = False

try:
    import edge_tts
    _EDGE_OK = True
except ImportError:
    _EDGE_OK = False

try:
    import pyttsx3
    _PYTTSX3_OK = True
except ImportError:
    pyttsx3 = None
    _PYTTSX3_OK = False


class TTSEngine:
    def __init__(self, shared_state: dict):
        self.shared_state = shared_state
        self._lock = threading.Lock()
        self._use_edge = _EDGE_OK and _PYGAME_OK
        self._use_pyttsx3 = _PYTTSX3_OK

        self._pyttsx3 = None
        if self._use_pyttsx3:
            try:
                self._pyttsx3 = pyttsx3.init()
                self._pyttsx3.setProperty('rate', config.TTS_RATE)
                self._pyttsx3.setProperty('volume', config.TTS_VOLUME)
                for v in self._pyttsx3.getProperty('voices'):
                    vid = (v.id + v.name).lower()
                    if any(k in vid for k in ('pt', 'portuguese', 'brasil', 'brazil')):
                        self._pyttsx3.setProperty('voice', v.id)
                        break
            except Exception as e:
                self._pyttsx3 = None
                self._use_pyttsx3 = False
                print(f"⚠️  pyttsx3 indisponível: {e}")

        if self._use_edge:
            print(f"🗣️  Voz: Edge-TTS ({config.TTS_VOICE})")
        elif self._use_pyttsx3:
            print("🗣️  Voz: pyttsx3 (fallback)")
        else:
            print("🗣️  Voz: texto apenas (sem sintetizador instalado)")

    def speak(self, text: str):
        with self._lock:
            self.shared_state['is_speaking'] = True
            print(f"🤖 Jarvis: {text}")
            try:
                if self._use_edge: self._speak_edge(text)
                else: self._speak_pyttsx3(text)
            finally:
                self.shared_state['is_speaking'] = False

    def speak_async(self, text: str):
        threading.Thread(target=self.speak, args=(text,), daemon=True).start()

    def _speak_edge(self, text: str):
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                tmp = f.name
            async def _synth():
                await edge_tts.Communicate(text, config.TTS_VOICE).save(tmp)
            asyncio.run(_synth())
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"  Edge-TTS erro: {e}")
            self._use_edge = False
            self._speak_pyttsx3(text)
        finally:
            if tmp and os.path.exists(tmp):
                try: os.unlink(tmp)
                except Exception: pass

    def _speak_pyttsx3(self, text: str):
        if not self._pyttsx3:
            return
        try:
            self._pyttsx3.say(text)
            self._pyttsx3.runAndWait()
        except RuntimeError: pass