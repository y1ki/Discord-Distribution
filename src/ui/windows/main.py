from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from pathlib import Path
from src.ui.styles import DARK_THEME, SIDEBAR_STYLE
from src.ui.components.sidebar import Sidebar
from src.ui.pages.accounts import AccountsPage
from src.ui.pages.actions import ActionsPage
from src.ui.pages.settings import SettingsPage
from src.ui.pages.proxy_detail import ProxyDetailPage
from src.ui.pages.accounts_detail import AccountsDetailPage
from src.ui.pages.dead_tokens import DeadTokensPage
from src.ui.pages.insufficient_rights import InsufficientRightsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anonymous&Discord")
        self.setFixedSize(1200, 700)
        self.setStyleSheet(DARK_THEME)
        
        icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "11062047e576490fbffdd85dfecb4cd9.jpg"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            icon.addFile(str(icon_path), QSize(16, 16))
            icon.addFile(str(icon_path), QSize(32, 32))
            icon.addFile(str(icon_path), QSize(48, 48))
            icon.addFile(str(icon_path), QSize(64, 64))
            icon.addFile(str(icon_path), QSize(128, 128))
            icon.addFile(str(icon_path), QSize(256, 256))
            self.setWindowIcon(icon)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.on_page_changed)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        main_layout.addWidget(self.sidebar)
        
        content_container = QWidget()
        content_container.setObjectName("content")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pages = QStackedWidget()
        self.accounts_page = AccountsPage()
        self.actions_page = ActionsPage()
        self.settings_page = SettingsPage()
        self.proxy_detail = ProxyDetailPage()
        self.accounts_detail = AccountsDetailPage()
        self.dead_tokens = DeadTokensPage()
        self.insufficient_rights = InsufficientRightsPage()
        
        self.pages.addWidget(self.accounts_page)
        self.pages.addWidget(self.actions_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.proxy_detail)
        self.pages.addWidget(self.accounts_detail)
        self.pages.addWidget(self.dead_tokens)
        self.pages.addWidget(self.insufficient_rights)
        
        self.accounts_page.stats_bar.card_clicked.connect(self.on_stat_card_clicked)
        self.proxy_detail.stats_bar.card_clicked.connect(self.on_stat_card_clicked)
        self.accounts_detail.stats_bar.card_clicked.connect(self.on_stat_card_clicked)
        self.dead_tokens.stats_bar.card_clicked.connect(self.on_stat_card_clicked)
        self.insufficient_rights.stats_bar.card_clicked.connect(self.on_stat_card_clicked)
        
        content_layout.addWidget(self.pages)
        main_layout.addWidget(content_container)
    
    def on_page_changed(self, index):
        if index < 3:
            self.pages.setCurrentIndex(index)
            if index == 0:
                self.accounts_page.stats_bar.clear_active()
                self.proxy_detail.stats_bar.clear_active()
                self.accounts_detail.stats_bar.clear_active()
                self.insufficient_rights.stats_bar.clear_active()
    
    def on_stat_card_clicked(self, card_name):
        if card_name == "Прокси":
            self.pages.setCurrentIndex(3)
            self.sidebar.set_active_button(-1)
            self.proxy_detail.stats_bar.set_active_card("Прокси")
            self.proxy_detail.load_data()
            self.accounts_page.stats_bar.clear_active()
            self.accounts_detail.stats_bar.clear_active()
            self.insufficient_rights.stats_bar.clear_active()
        elif card_name == "Активные аккаунты":
            self.pages.setCurrentIndex(4)
            self.sidebar.set_active_button(-1)
            self.accounts_detail.stats_bar.set_active_card("Активные аккаунты")
            self.accounts_detail.load_data()
            self.accounts_page.stats_bar.clear_active()
            self.proxy_detail.stats_bar.clear_active()
            self.insufficient_rights.stats_bar.clear_active()
        elif card_name == "Недостаточно прав":
            self.pages.setCurrentIndex(6)
            self.sidebar.set_active_button(-1)
            self.insufficient_rights.stats_bar.set_active_card("Недостаточно прав")
            self.insufficient_rights.load_data()
            self.accounts_page.stats_bar.clear_active()
            self.proxy_detail.stats_bar.clear_active()
            self.accounts_detail.stats_bar.clear_active()
            self.dead_tokens.stats_bar.clear_active()
        elif card_name == "Мертвые аккаунты":
            self.pages.setCurrentIndex(5)
            self.sidebar.set_active_button(-1)
            self.dead_tokens.stats_bar.set_active_card("Мертвые аккаунты")
            self.dead_tokens.load_data()
            self.accounts_page.stats_bar.clear_active()
            self.proxy_detail.stats_bar.clear_active()
            self.accounts_detail.stats_bar.clear_active()
            self.insufficient_rights.stats_bar.clear_active()
