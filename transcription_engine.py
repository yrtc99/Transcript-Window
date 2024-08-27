import threading
import numpy as np
import sounddevice as sd
import whisper
from PyQt5.QtCore import QObject, pyqtSignal

class AudioRecorder:
    def __init__(self, sample_rate=16000, duration=5):
        self.sample_rate = sample_rate
        self.duration = duration

    def record(self):
        recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
        sd.wait()
        return recording.flatten().astype(np.float32)

class WhisperTranscriber:
    def __init__(self, model_name="small", language="zh"):
        self.model = whisper.load_model(model_name)
        self.language = language

    def transcribe(self, audio):
        result = self.model.transcribe(audio, language=self.language)
        return result["text"]

class TranscriptionEngine(QObject):
    textUpdated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber()
        self.is_running = False

    def start(self):
        self.is_running = True
        threading.Thread(target=self._transcribe_loop, daemon=True).start()

    def stop(self):
        self.is_running = False

    def _transcribe_loop(self):
        while self.is_running:
            audio = self.recorder.record()
            text = self.transcriber.transcribe(audio)
            if text:
                self.textUpdated.emit(text)