import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from transcription_engine import TranscriptionEngine

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
        self.engine = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("即時語音轉錄")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.text_display = TranscriptionDisplay()
        layout.addWidget(self.text_display)

        self.toggle_button = QPushButton("開始轉錄")
        self.toggle_button.clicked.connect(self.toggle_transcription)
        layout.addWidget(self.toggle_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def toggle_transcription(self):
        if self.engine is None or not self.engine.is_running:
            try:
                if self.engine is None:
                    self.init_transcription_engine()
                self.engine.start()
                self.toggle_button.setText("停止轉錄")
            except Exception as e:
                self.text_display.update_text(f"錯誤：無法初始化音頻設備。{str(e)}")
        else:
            self.engine.stop()
            self.toggle_button.setText("開始轉錄")

    def init_transcription_engine(self):
        self.engine = TranscriptionEngine()
        self.engine.textUpdated.connect(self.text_display.update_text)

    def closeEvent(self, event):
        if self.engine:
            self.engine.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranscriptionWindow()
    window.show()
    sys.exit(app.exec())