import pyaudio
import numpy as np

CHUNK = 2048
RATE  = 16000
p     = pyaudio.PyAudio()

print("Testando microfone por 5 segundos... fale e bata palmas!")
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

import time
start = time.time()
while time.time() - start < 5:
    data  = stream.read(CHUNK, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    rms   = np.sqrt(np.mean(audio**2))
    bar   = "█" * int(rms * 200)
    print(f"  RMS: {rms:.4f}  {bar}")

stream.stop_stream()
stream.close()
p.terminate()
print("Fim do teste.")