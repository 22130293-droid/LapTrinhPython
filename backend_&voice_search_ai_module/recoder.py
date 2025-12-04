import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import queue
import threading
import time
from pathlib import Path

def record_seconds_to_wav(filename: str, duration: float = 5.0, samplerate: int = 16000, channels: int = 1):
    """
    Ghi âm trong `duration` giây và lưu file WAV.
    Trả về path của file đã lưu.
    """
    filename = Path(filename)
    q = queue.Queue()

    def callback(indata, frames, time_, status):
        if status:
            print("Recording status:", status)
        q.put(indata.copy())

    print(f"Recording for {duration} seconds...")
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        frames = []
        start = time.time()
        while True:
            try:
                data = q.get(timeout=duration + 1)
                frames.append(data)
            except Exception:
                pass
            if time.time() - start >= duration:
                break

    audio = np.concatenate(frames, axis=0)
    audio_int16 = np.int16(audio / np.max(np.abs(audio)) * 32767)
    wavfile.write(str(filename), samplerate, audio_int16)
    print(f"Saved recording to {filename}")
    return str(filename)
