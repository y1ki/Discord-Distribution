from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None, confirm_text: str = "Удалить", confirm_color: str = "#ff453a"):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(360, 160)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }")
        self._build_ui(title, message, confirm_text, confirm_color)

    def _build_ui(self, title: str, message: str, confirm_text: str = "Удалить", confirm_color: str = "#ff453a"):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QLabel()
        container.setFixedSize(340, 140)
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

        content_layout.addSpacing(4)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        no_btn = QPushButton("Отмена")
        no_btn.setFixedHeight(32)
        no_btn.setMinimumWidth(140)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setFont(QFont("Segoe UI", 9))
        no_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.12); }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.06); }
        """)
        no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(no_btn)

        yes_btn = QPushButton(confirm_text)
        yes_btn.setFixedHeight(32)
        yes_btn.setMinimumWidth(140)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {confirm_color};
                color: #ffffff;
                border: 1px solid transparent;
                border-radius: 8px;
            }}
            QPushButton:hover {{ border: 1px solid rgba(255, 255, 255, 0.25); }}
            QPushButton:pressed {{ border: 1px solid rgba(255, 255, 255, 0.1); }}
        """)
        yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(yes_btn)

        content_layout.addLayout(btn_layout)
