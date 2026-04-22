"""
clap_detector.py — Detector de dupla palma por duração

Calibrado com o teste do seu microfone:
  - Palma: pico alto que dura 1-3 chunks e volta ao silêncio
  - Voz:   pico alto que sustenta por 4+ chunks consecutivos
"""
import time
import threading
import pyaudio
import numpy as np


class ClapDetector:
    CHUNK    = 2048
    RATE     = 16000
    FORMAT   = pyaudio.paInt16
    CHANNELS = 1

    MAX_CLAP_CHUNKS = 3   # palma ≤3 chunks; voz dura 4+

    def __init__(self, callback, shared_state,
                 peak_threshold=0.06,
                 sustain_threshold=0.012,
                 max_interval=0.9,
                 cooldown=2.5):
        self.callback          = callback
        self.shared_state      = shared_state
        self.peak_threshold    = peak_threshold
        self.sustain_threshold = sustain_threshold
        self.max_interval      = max_interval
        self.cooldown          = cooldown

    def start(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.FORMAT, channels=self.CHANNELS,
            rate=self.RATE, input=True,
            frames_per_buffer=self.CHUNK
        )
        print("👏 Detector de palmas ativo")

        in_sound        = False
        sound_chunks    = 0
        sound_peak      = 0.0

        first_clap_time = 0.0
        clap_count      = 0
        last_trigger    = 0.0

        while True:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)

                if self.shared_state.get('is_speaking') or \
                   self.shared_state.get('is_busy'):
                    in_sound     = False
                    sound_chunks = 0
                    sound_peak   = 0.0
                    continue

                audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                rms   = float(np.sqrt(np.mean(audio ** 2)))
                now   = time.time()

                if rms > self.sustain_threshold:
                    if not in_sound:
                        in_sound     = True
                        sound_chunks = 1
                        sound_peak   = rms
                    else:
                        sound_chunks += 1
                        sound_peak    = max(sound_peak, rms)
                else:
                    if in_sound:
                        # Evento terminou — avaliar se foi palma
                        if (sound_chunks <= self.MAX_CLAP_CHUNKS
                                and sound_peak >= self.peak_threshold):

                            if now - last_trigger >= self.cooldown:
                                if now - first_clap_time > self.max_interval:
                                    first_clap_time = now
                                    clap_count      = 1
                                    print("👏 Palma 1")
                                else:
                                    clap_count += 1
                                    print(f"👏 Palma {clap_count}")

                                if clap_count >= 2:
                                    clap_count   = 0
                                    last_trigger = now
                                    print("✅ Duas palmas!")
                                    threading.Thread(
                                        target=self.callback, daemon=True
                                    ).start()

                        in_sound     = False
                        sound_chunks = 0
                        sound_peak   = 0.0

            except Exception as e:
                print(f"⚠️  Erro no detector de palmas: {e}")
                time.sleep(0.5)