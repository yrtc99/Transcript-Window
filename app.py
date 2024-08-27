import sys
import threading
import numpy as np
import sounddevice as sd
import whisper
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal


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

class TranscriptionDisplay(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def update_text(self, new_text):
        current_text = self.toPlainText()
        updated_text = current_text + " " + new_text if current_text else new_text
        self.setPlainText(updated_text)
        self.moveCursor(self.textCursor().End)

class TranscriptionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_transcription_engine()

    def init_ui(self):
        self.setWindowTitle("即時語音轉錄")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.text_display = TranscriptionDisplay()
        layout.addWidget(self.text_display)

        self.toggle_button = QPushButton("停止轉錄")
        self.toggle_button.clicked.connect(self.toggle_transcription)
        layout.addWidget(self.toggle_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def init_transcription_engine(self):
        self.engine = TranscriptionEngine()
        self.engine.textUpdated.connect(self.text_display.update_text)
        self.engine.start()

    def toggle_transcription(self):
        if self.engine.is_running:
            self.engine.stop()
            self.toggle_button.setText("開始轉錄")
        else:
            self.engine.start()
            self.toggle_button.setText("停止轉錄")

    def closeEvent(self, event):
        self.engine.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranscriptionWindow()
    window.show()
    sys.exit(app.exec())