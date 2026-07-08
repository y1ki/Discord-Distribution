from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QWidget
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QFont, QPixmap, QPainter, QIcon
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path
from src.ui.components.toggle import ToggleSwitch
from src.core.database import Database


class SettingRowWithToggle(QWidget):
    def __init__(self, title, description=""):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")
        text_layout.addWidget(title_label)
        
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setFont(QFont("Segoe UI", 8))
            desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); background: transparent; border: none;")
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)
        
        layout.addWidget(text_container)
        layout.addStretch()
        
        self.toggle = ToggleSwitch()
        layout.addWidget(self.toggle)


class SettingRowWithSpinBox(QWidget):
    def __init__(self, title, description="", min_val=1, max_val=100, default_val=10):
        super().__init__()
        self.title = title
        self.description = description
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = default_val
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")
        text_layout.addWidget(title_label)
        
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setFont(QFont("Segoe UI", 8))
            desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); background: transparent; border: none;")
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)
        
        layout.addWidget(text_container)
        layout.addStretch()
        
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_val)
        self.spinbox.setMaximum(self.max_val)
        self.spinbox.setValue(self.default_val)
        self.spinbox.setFixedWidth(90)
        self.spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spinbox.setStyleSheet("""
            QSpinBox {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.9);
                padding: 6px 10px;
                font-size: 10pt;
                font-family: "Segoe UI";
            }
            QSpinBox:hover {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            QSpinBox:focus {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(88, 101, 242, 0.8);
            }
        """)
        layout.addWidget(self.spinbox)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }")
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        container = QLabel()
        container.setFixedSize(580, 480)
        container.setStyleSheet("""
            QLabel {
                background-color: rgba(20, 20, 23, 252);
                border-radius: 28px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        layout.addWidget(container)

        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header_container = QLabel()
        header_container.setFixedHeight(60)
        header_container.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(24, 18, 18, 0)
        header_layout.setSpacing(0)

        title_label = QLabel("Настройки")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton()
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        
        close_icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icons" / "close.svg"
        svg_data = close_icon_path.read_text()
        colored_svg = svg_data.replace('stroke="currentColor"', 'stroke="#999999"')
        
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        close_btn.setIcon(QIcon(pixmap))
        close_btn.setIconSize(pixmap.size())
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        content_layout.addWidget(header_container)

        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); border: none;")
        content_layout.addWidget(separator)

        self.body_container = QLabel()
        self.body_container.setStyleSheet("background: transparent; border: none;")
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(24, 20, 24, 24)
        self.body_layout.setSpacing(0)
        
        self.threads_row = SettingRowWithSpinBox(
            "Количество потоков",
            "",
            min_val=1,
            max_val=250,
            default_val=100
        )
        self.threads_row.spinbox.valueChanged.connect(self._on_threads_changed)
        self.body_layout.addWidget(self.threads_row)
        
        separator1 = QLabel()
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); border: none;")
        self.body_layout.addWidget(separator1)
        
        self.use_proxy_row = SettingRowWithToggle(
            "Использовать прокси",
            ""
        )
        self.use_proxy_row.toggle.toggled.connect(self._on_use_proxy_toggled)
        self.body_layout.addWidget(self.use_proxy_row)
        
        separator2 = QLabel()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); border: none;")
        self.body_layout.addWidget(separator2)
        
        self.detailed_check_row = SettingRowWithToggle(
            "Проверять кол-во чатов/серверов",
            ""
        )
        self.detailed_check_row.toggle.toggled.connect(self._on_detailed_check_toggled)
        self.body_layout.addWidget(self.detailed_check_row)
        
        self.body_layout.addStretch()
        
        content_layout.addWidget(self.body_container)
    
    def _load_settings(self):
        threads = int(self.db.get("account_check_threads", 100))
        use_proxy = self.db.get("account_use_proxy", True)
        detailed_check = self.db.get("account_detailed_check", False)
        
        self.threads_row.spinbox.setValue(threads)
        self.use_proxy_row.toggle.set_checked(use_proxy)
        self.detailed_check_row.toggle.set_checked(detailed_check)
    
    def _on_threads_changed(self, value):
        self.db.set("account_check_threads", value)
    
    def _on_use_proxy_toggled(self, checked):
        self.db.set("account_use_proxy", checked)
    
    def _on_detailed_check_toggled(self, checked):
        self.db.set("account_detailed_check", checked)
