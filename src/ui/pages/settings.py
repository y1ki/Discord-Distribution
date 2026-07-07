from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.ui.components.toggle import ToggleSwitch
from src.core.database import Database


class SettingRow(QWidget):
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
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #ffffff;")
        text_layout.addWidget(title_label)
        
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setFont(QFont("Segoe UI", 9))
            desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)
        
        layout.addWidget(text_container)
        layout.addStretch()
        
        self.toggle = ToggleSwitch()
        layout.addWidget(self.toggle)


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_wrapper = QWidget()
        content_wrapper.setFixedSize(950, 640)
        wrapper_layout = QVBoxLayout(content_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(10)
        
        content_container = QWidget()
        content_container.setObjectName("settings_content")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(32, 28, 32, 28)
        content_layout.setSpacing(0)
        
        self.splash_row = SettingRow(
            "Показывать экран загрузки"
        )
        self.splash_row.toggle.toggled.connect(self.on_splash_toggled)
        content_layout.addWidget(self.splash_row)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")
        content_layout.addWidget(separator)
        
        self.empty_video_row = SettingRow(
            "Показывать видео в консоли"
        )
        self.empty_video_row.toggle.toggled.connect(self.on_empty_video_toggled)
        content_layout.addWidget(self.empty_video_row)
        
        separator2 = QWidget()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")
        content_layout.addWidget(separator2)

        self.tg_link_row = SettingRow(
            "Открывать Telegram при запуске приложения"
        )
        self.tg_link_row.toggle.toggled.connect(self.on_tg_link_toggled)
        content_layout.addWidget(self.tg_link_row)

        separator3 = QWidget()
        separator3.setFixedHeight(1)
        separator3.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")
        content_layout.addWidget(separator3)

        content_layout.addStretch()
        
        content_container.setStyleSheet("""
            QWidget#settings_content {
                background-color: rgba(25, 25, 28, 0.8);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        
        wrapper_layout.addWidget(content_container)
        main_layout.addWidget(content_wrapper)
    
    def load_settings(self):
        show_splash = self.db.get("show_splash", True)
        self.splash_row.toggle.set_checked(show_splash)
        
        show_empty_video = self.db.get("show_empty_video", False)
        self.empty_video_row.toggle.set_checked(show_empty_video)

        open_tg_link = self.db.get("open_tg_link", True)
        self.tg_link_row.toggle.set_checked(open_tg_link)

    def on_tg_link_toggled(self, checked):
        self.db.set("open_tg_link", checked)
    
    def on_splash_toggled(self, checked):
        self.db.set("show_splash", checked)
    
    def on_empty_video_toggled(self, checked):
        self.db.set("show_empty_video", checked)
        main_window = self.window()
        if hasattr(main_window, 'pages'):
            accounts_page = main_window.pages.widget(0)
            if hasattr(accounts_page, 'empty_state'):
                accounts_page.empty_state.set_video_enabled(checked)
            if hasattr(accounts_page, 'video_background'):
                accounts_page.video_background.set_video_enabled(checked)
        if hasattr(main_window, 'actions_page'):
            main_window.actions_page.load_settings()
