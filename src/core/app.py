import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from src.ui.splash import SplashScreen
from src.ui.windows.main import MainWindow
from src.core.database import Database


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.splash = None
        self.main_window = None
        self.db = Database()

    def run(self):
        if self.db.get("open_tg_link", True):
            QDesktopServices.openUrl(QUrl("https://t.me/Ab3stPublic"))

        if self.db.get("show_splash", True):
            self.splash = SplashScreen()
            self.splash.finished.connect(self.show_main_window)
            self.splash.show()
        else:
            self.show_main_window()

        return self.app.exec()

    def show_main_window(self):
        if self.main_window is None:
            self.main_window = MainWindow()
        self.main_window.show()
