from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #0a0a0a;")

        layout = QVBoxLayout(self)

        label = QLabel("Anonymous&Discord")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #e0e0e0; font-size: 48px; font-weight: bold;")
        layout.addWidget(label)
