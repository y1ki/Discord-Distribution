from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QProgressBar, QStackedWidget, QFileDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QGraphicsBlurEffect
import sys
from src.ui.components.stats_bar import StatsBar
from src.ui.components.empty_state import EmptyStateWidget
from src.ui.styles import BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_DANGER, PROGRESS_BAR, LOG_TERMINAL, LOG_COLORS
from src.ui.dialogs.settings import SettingsDialog
from src.ui.dialogs.proxy_selection import ProxySelectionDialog
from src.core.database import Database
from src.core.proxy_checker import ProxyChecker
from src.workers.account_check import AccountCheckWorker
from datetime import datetime
import asyncio


class ProxyCheckWorker(QThread):
    progress_signal = pyqtSignal(int, int)
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal(list)

    def __init__(self, proxies, parent=None):
        super().__init__(parent)
        self.proxies = proxies
        self.checker = ProxyChecker(timeout=10, max_workers=100)
        self.should_stop = False

    def run(self):
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                self.checker.check_proxies(
                    self.proxies,
                    progress_callback=self._on_progress,
                    log_callback=self._on_log,
                    should_stop_callback=lambda: self.should_stop,
                    force_protocol="autodetect"
                )
            )
            self.finished_signal.emit(results)
        except Exception:
            return
        finally:
            loop.close()

    def stop(self):
        self.should_stop = True

    def _on_progress(self, current, total):
        self.progress_signal.emit(current, total)

    def _on_log(self, message, color):
        self.log_signal.emit(message, color)


class AccountsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.has_logs = False
        self.loaded_proxies = []
        self.proxy_worker = None
        self.account_worker = None
        self.is_checking = False
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        self.stats_bar = StatsBar()
        main_layout.addWidget(self.stats_bar)
        self._update_stats()
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        
        self.btn_load_accounts = self._make_button("Загрузить аккаунты")
        self.btn_load_proxy = self._make_button("Загрузить прокси")
        btn_settings = self._make_button("Настройки")
        btn_settings.clicked.connect(self._open_settings)
        self.btn_load_accounts.clicked.connect(self._load_accounts_file)
        self.btn_load_proxy.clicked.connect(self._load_proxy_file)

        controls_layout.addWidget(self.btn_load_accounts)
        controls_layout.addWidget(self.btn_load_proxy)
        controls_layout.addWidget(btn_settings)
        controls_layout.addStretch()

        self.launch_btn = self._make_button("Запуск", primary=True)
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self._toggle_proxy_check)
        controls_layout.addWidget(self.launch_btn)
        
        content_layout.addLayout(controls_layout)
        
        progress_container = QWidget()
        progress_container.setStyleSheet("background: transparent; border: none;")
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(4)

        self.progress_label = QLabel("")
        self.progress_label.setFont(QFont("Segoe UI", 8))
        self.progress_label.setStyleSheet("color: #555555; background: transparent; border: none;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(PROGRESS_BAR)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_container = progress_container
        self.progress_container.setVisible(False)
        content_layout.addWidget(self.progress_container)
        
        terminal_container = QWidget()
        terminal_container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 28, 0.8);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        terminal_layout = QVBoxLayout(terminal_container)
        terminal_layout.setContentsMargins(24, 18, 24, 18)
        terminal_layout.setSpacing(12)

        terminal_header = QLabel("Консоль логов")
        terminal_header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        terminal_header.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")
        terminal_layout.addWidget(terminal_header)

        self.terminal_stack = QStackedWidget()
        self.terminal_stack.setStyleSheet("background: transparent; border: none;")
        
        self.empty_state = EmptyStateWidget()
        self.terminal_stack.addWidget(self.empty_state)
        
        overlay_container = QWidget()
        overlay_container.setStyleSheet("background: transparent; border: none;")
        overlay_layout = QVBoxLayout(overlay_container)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)
        
        self.video_background = EmptyStateWidget()
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.video_background.setGraphicsEffect(self.blur_effect)
        overlay_layout.addWidget(self.video_background)
        
        self.overlay_log_terminal = QTextEdit(overlay_container)
        self.overlay_log_terminal.setReadOnly(True)
        self.overlay_log_terminal.setFont(QFont("Consolas", 9))
        self.overlay_log_terminal.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #3d9970;
                border: none;
                padding: 0;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background-color: rgba(255, 255, 255, 0.25); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        self.overlay_log_terminal.raise_()
        
        def position_overlay_log(event):
            size = overlay_container.size()
            self.overlay_log_terminal.setGeometry(0, 0, size.width(), size.height())
        
        overlay_container.resizeEvent = position_overlay_log
        self.terminal_stack.addWidget(overlay_container)

        self.log_terminal = QTextEdit()
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setFont(QFont("Consolas", 9))
        self.log_terminal.setStyleSheet(LOG_TERMINAL)
        self.terminal_stack.addWidget(self.log_terminal)
        
        terminal_layout.addWidget(self.terminal_stack)
        content_layout.addWidget(terminal_container)
        main_layout.addLayout(content_layout)
    
    def add_log(self, message, color="#3d9970"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        hex_color = LOG_COLORS.get(color, color)
        log_text = f'<span style="color: {hex_color};">[{timestamp}] {message}</span>'
        
        if not self.has_logs:
            self.has_logs = True
            show_video = self.db.get("show_empty_video", True)
            
            if show_video:
                self.terminal_stack.setCurrentIndex(1)
                self.overlay_log_terminal.append(log_text)
            else:
                self.terminal_stack.setCurrentIndex(2)
                self.log_terminal.append(log_text)
        else:
            current_index = self.terminal_stack.currentIndex()
            if current_index == 1:
                self.overlay_log_terminal.append(log_text)
                self.overlay_log_terminal.moveCursor(QTextCursor.MoveOperation.End)
            else:
                self.log_terminal.append(log_text)
                self.log_terminal.moveCursor(QTextCursor.MoveOperation.End)

    def _make_button(self, text: str, primary: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setMinimumWidth(140)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold if primary else QFont.Weight.Normal))
        btn.setStyleSheet(BUTTON_PRIMARY if primary else BUTTON_SECONDARY)
        return btn
    
    def _update_stats(self):
        account_count = self.db.get_account_count()
        proxy_count = self.db.get_proxy_count()
        
        self.stats_bar.update_card_count("Активные аккаунты", account_count)
        self.stats_bar.update_card_count("Прокси", proxy_count)
        self.stats_bar.update_card_count("Недостаточно прав", self.db.get_insufficient_rights_count())
        self.stats_bar.update_card_count("Мертвые аккаунты", self.db.get_dead_tokens_count())
    
    def load_settings(self):
        show_empty_video = self.db.get("show_empty_video", True)
        self.empty_state.set_video_enabled(show_empty_video)
        self.video_background.set_video_enabled(show_empty_video)
    
    def _open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _load_accounts_file(self):
        if self.is_checking:
            self.add_log("Невозможно загрузить аккаунты во время проверки", "red")
            return
        
        use_proxy = self.db.get("account_use_proxy", True)
        selected_proxies = []
        
        if use_proxy:
            proxy_dialog = ProxySelectionDialog(self)
            if proxy_dialog.exec() == ProxySelectionDialog.DialogCode.Accepted:
                mode, value = proxy_dialog.get_selection()
                selected_proxies = self.db.get_proxies_for_rotation(mode, value)
                
                if not selected_proxies:
                    self.add_log("Нет доступных прокси для выбранного режима", "red")
                    return
                
                self.add_log(f"Загружено {len(selected_proxies)} прокси (режим: {mode})", "blue")
            else:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать файл с токенами",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tokens = [line.strip() for line in f if line.strip()]
            
            if not tokens:
                self.add_log("Файл не содержит токенов", "red")
                return
            
            self.add_log(f"Загружено {len(tokens)} токенов", "blue")
            self._start_token_check(tokens, selected_proxies)
            
        except Exception as e:
            self.add_log(f"Ошибка загрузки файла: {str(e)}", "red")
    
    def _start_token_check(self, tokens: list, proxies: list):
        self.is_checking = True
        self.btn_load_accounts.setEnabled(False)
        self.btn_load_proxy.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Проверка токенов...")
        self.progress_container.setVisible(True)
        
        self.launch_btn.setEnabled(True)
        self.launch_btn.setText("Остановить")
        self.launch_btn.setStyleSheet(BUTTON_DANGER)
        self.launch_btn.clicked.disconnect()
        self.launch_btn.clicked.connect(self._stop_token_check)
        
        max_workers = int(self.db.get("account_check_threads", 100))
        detailed = self.db.get("account_detailed_check", False)
        
        self.account_worker = AccountCheckWorker(tokens, proxies, max_workers, detailed, parent=self)
        self.account_worker.progress_signal.connect(self._on_token_check_progress)
        self.account_worker.log_signal.connect(self._on_token_check_log)
        self.account_worker.finished_signal.connect(self._on_token_check_finished)
        self.account_worker.start()
        
        self.add_log(f"Запущена проверка {len(tokens)} токенов (потоков: {max_workers})", "blue")
    
    def _stop_token_check(self):
        if self.account_worker:
            self.account_worker.stop()
            self.add_log("Остановка проверки...", "yellow")
    
    def _on_token_check_progress(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Проверка токенов: {current}/{total}")
    
    def _on_token_check_log(self, message, color):
        self.add_log(message, color)
    
    def _on_token_check_finished(self, stats):
        self.is_checking = False
        self.btn_load_accounts.setEnabled(True)
        self.btn_load_proxy.setEnabled(True)
        self.progress_container.setVisible(False)
        
        self.launch_btn.setEnabled(False)
        self.launch_btn.setText("Запуск")
        self.launch_btn.setStyleSheet(BUTTON_PRIMARY)
        self.launch_btn.clicked.disconnect()
        self.launch_btn.clicked.connect(self._toggle_proxy_check)
        
        summary = f"Проверка завершена: Валидных: {stats['valid']}, Невалидных: {stats['invalid']}"
        self.add_log(summary, "blue")
        
        self._update_stats()
    
    def _load_proxy_file(self):
        if self.is_checking:
            self.add_log("Невозможно загрузить прокси во время проверки", "red")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать файл с прокси",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.loaded_proxies, duplicates = ProxyChecker.load_proxies_from_file(file_path)
            if self.loaded_proxies:
                msg = f"Загружено {len(self.loaded_proxies)} прокси"
                if duplicates > 0:
                    msg += f" (удалено {duplicates} дублей)"
                self.add_log(msg, "blue")
                self.launch_btn.setEnabled(True)
            else:
                self.add_log("Файл не содержит валидных прокси", "red")
    
    def _toggle_proxy_check(self):
        if self.is_checking:
            self._stop_proxy_check()
        else:
            self._start_proxy_check()
    
    def _start_proxy_check(self):
        if not self.loaded_proxies:
            self.add_log("Прокси не загружены", "red")
            return

        self.is_checking = True
        self.add_log(f"Начата проверка {len(self.loaded_proxies)} прокси (Auto)...", "blue")
        self.btn_load_proxy.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Проверка прокси...")
        self.progress_container.setVisible(True)
        
        self.launch_btn.setText("Остановить")
        self.launch_btn.setStyleSheet(BUTTON_DANGER)

        self.proxy_worker = ProxyCheckWorker(self.loaded_proxies, parent=self)
        self.proxy_worker.progress_signal.connect(self._on_check_progress)
        self.proxy_worker.log_signal.connect(self._on_check_log)
        self.proxy_worker.finished_signal.connect(self._on_check_finished)
        self.proxy_worker.start()

    def _stop_proxy_check(self):
        if self.proxy_worker and self.proxy_worker.isRunning():
            self.add_log("Остановка проверки...", "yellow")
            self.proxy_worker.stop()

    def _on_check_progress(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Проверено: {current}/{total}")

    def _on_check_log(self, message, color):
        self.add_log(message, color)

    def _reload_proxy_page(self):
        main_window = self.window()
        if hasattr(main_window, 'proxy_detail'):
            proxy_page = main_window.proxy_detail
            if hasattr(proxy_page, 'load_data'):
                proxy_page.load_data()

    def _on_check_finished(self, results):
        self.is_checking = False
        alive_count = sum(1 for r in results if r.status == "alive")
        dead_count = len(results) - alive_count

        alive_proxies = [r for r in results if r.status == "alive"]
        if alive_proxies:
            self.db.remove_duplicate_proxies()
            saved_count, duplicates_count = self.db.save_proxies(alive_proxies)
            if duplicates_count > 0:
                self.add_log(f"Сохранено {saved_count} прокси ({duplicates_count} дублей)", "green")
            else:
                self.add_log(f"Сохранено {saved_count} прокси", "green")

        self._reload_proxy_page()
        self._update_stats()
        
        self.add_log(f"Проверка завершена: {alive_count} живых, {dead_count} мёртвых", "blue")
        self.btn_load_proxy.setEnabled(True)
        self.progress_container.setVisible(False)
        
        self.launch_btn.setText("Запуск")
        self.launch_btn.setStyleSheet(BUTTON_PRIMARY)
