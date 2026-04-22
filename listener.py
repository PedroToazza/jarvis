"""
listener.py — Wake word "Jarvis" com variantes PT-BR
"""
import os
import re
import time
import speech_recognition as sr

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import config

try:
    from faster_whisper import WhisperModel
    import numpy as np
    _WHISPER_OK = True
except ImportError:
    _WHISPER_OK = False


WAKE_VARIANTS = [
    "jarvis", "jarves", "jarvys", "jarviz", "jarbes", "jarbis",
    "jar vis", "jar bis", "giravis",
    "já vi", "ja vi", "jardinz", "jardins",
    "jordes", "jornes", "jorbes",
    "travis", "trevis",
    "aves", "javes", "arvis",
]


def contains_wake_word(text):
    text = (text or "").lower()
    return any(v in text for v in WAKE_VARIANTS)


def extract_command(text):
    text = (text or "").lower().strip()
    vs = sorted(WAKE_VARIANTS, key=len, reverse=True)
    for v in vs:
        pat = rf'^\s*{re.escape(v)}[\s,\.\-]*'
        new = re.sub(pat, '', text)
        if new != text: return new.strip()
    for v in vs:
        pat = rf'\b{re.escape(v)}\b[\s,\.\-]*'
        text = re.sub(pat, ' ', text)
    return text.strip()


class VoiceListener:
    def __init__(self, on_command, tts, shared_state):
        self.on_command = on_command
        self.tts = tts
        self.shared_state = shared_state
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.whisper = None
        if _WHISPER_OK:
            print("⏳ Carregando Whisper base...")
            try:
                self.whisper = WhisperModel("base", device="cpu", compute_type="int8")
                print("✅ Whisper carregado.")
            except Exception as e:
                print(f"⚠️  Whisper: {e}")

    def start(self):
        with sr.Microphone(sample_rate=16000) as source:
            print("⏳ Calibrando...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print(f"🎤 Aguardando '{config.WAKE_WORD}'...")
            while True:
                if not self.shared_state.get('is_active', True):
                    self.shared_state['status'] = 'idle'
                    time.sleep(0.3); continue
                if self.shared_state.get('is_speaking') or self.shared_state.get('is_busy'):
                    time.sleep(0.1); continue
                self.shared_state['status'] = 'idle'
                try:
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"⚠️  {e}"); time.sleep(0.3); continue
                if self.shared_state.get('is_speaking'): continue
                self.shared_state['status'] = 'processing'
                text = self._transcribe(audio)
                if not text:
                    self.shared_state['status'] = 'idle'; continue
                print(f"  Você disse: '{text}'")
                if contains_wake_word(text):
                    command = extract_command(text)
                    if command: self._run(command)
                    else: self._prompt_and_capture(source)

    def _run(self, command):
        self.shared_state['is_busy'] = True
        try: self.on_command(command)
        finally: self.shared_state['is_busy'] = False

    def _prompt_and_capture(self, source):
        self.shared_state['is_busy'] = True
        try:
            self.tts.speak("Sim?")
            self.shared_state['status'] = 'listening'
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                self.tts.speak("Não ouvi nada."); return
            self.shared_state['status'] = 'processing'
            text = self._transcribe(audio)
            if text: self.on_command(text)
            else: self.tts.speak("Não entendi.")
        finally: self.shared_state['is_busy'] = False

    def _transcribe(self, audio):
        try:
            return self.recognizer.recognize_google(audio, language="pt-BR").strip()
        except sr.UnknownValueError: return ""
        except sr.RequestError: print("  Google indisponível")
        if self.whisper:
            try:
                raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
                a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                segments, _ = self.whisper.transcribe(a, language="pt", beam_size=1, vad_filter=True)
                return " ".join(s.text.strip() for s in segments).strip()
            except Exception as e: print(f"  Whisper erro: {e}")
        return ""