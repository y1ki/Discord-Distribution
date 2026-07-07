from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TextInputDialog(QDialog):
    def __init__(self, title: str, message: str, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(360, 200)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }")
        self._build_ui(title, message, placeholder)

    def _build_ui(self, title: str, message: str, placeholder: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QLabel()
        container.setFixedSize(340, 180)
        container.setStyleSheet("""
            QLabel {
                background-color: rgba(20, 20, 20, 250);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
        """)
        layout.addWidget(container)

        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(20, 18, 20, 18)
        content_layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setFont(QFont("Segoe UI", 9))
        msg_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent; border: none;")
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(msg_label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setMaxLength(15)
        self.input_field.setFont(QFont("Segoe UI", 9))
        self.input_field.setFixedHeight(32)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 0 12px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        content_layout.addWidget(self.input_field)

        content_layout.addSpacing(4)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setMinimumWidth(140)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFont(QFont("Segoe UI", 9))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.12); }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.06); }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Применить")
        ok_btn.setFixedHeight(32)
        ok_btn.setMinimumWidth(140)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:pressed { background-color: #1d4ed8; }
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        content_layout.addLayout(btn_layout)

    def get_text(self):
        return self.input_field.text().strip()
