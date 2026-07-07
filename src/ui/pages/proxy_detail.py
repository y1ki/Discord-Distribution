from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QPushButton, QLabel, QProgressBar, QMenu
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QByteArray, QSize
from PyQt6.QtGui import QFont, QColor, QAction, QPainter, QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer
from src.ui.pages.base_detail import BaseDetailPage
from src.ui.components.pagination import CustomPaginationWidget
from src.ui.components.proxy_table import create_proxy_table
from src.ui.components.stats_bar import StatsBar
from src.ui.styles import BUTTON_SECONDARY, BUTTON_DANGER, PROGRESS_BAR
from src.ui.dialogs.confirm import ConfirmDialog
from src.ui.dialogs.text_input import TextInputDialog
from src.ui.utils.flag_loader import FlagLoader
from src.core.proxy_checker import ProxyChecker
from pathlib import Path
import asyncio
import sys

class ProxyCheckWorker(QThread):
    progress_signal = pyqtSignal(int, int)
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


class ProxyDetailPage(BaseDetailPage):
    def __init__(self, parent=None):
        super().__init__("Прокси", parent)
        self.proxy_worker = None
        self.is_checking = False
        self.actions_menu = None
        self.ping_sort_state = self.db.get_proxy_sort_state()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        self.stats_bar = StatsBar()
        self.stats_bar.card_clicked.connect(self.stat_card_clicked.emit)
        main_layout.addWidget(self.stats_bar)
        
        toolbar_layout = QHBoxLayout()
        self.check_proxy_btn = QPushButton("Проверить прокси")
        self.check_proxy_btn.setFixedHeight(36)
        self.check_proxy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_proxy_btn.setFont(QFont("Segoe UI", 9))
        self.check_proxy_btn.setStyleSheet(BUTTON_SECONDARY)
        self.check_proxy_btn.clicked.connect(self._check_selected_proxies)
        toolbar_layout.addWidget(self.check_proxy_btn)
        
        select_all_proxy_btn = QPushButton("Выделить все")
        select_all_proxy_btn.setFixedHeight(36)
        select_all_proxy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_all_proxy_btn.setFont(QFont("Segoe UI", 9))
        select_all_proxy_btn.setStyleSheet(BUTTON_SECONDARY)
        select_all_proxy_btn.clicked.connect(self._select_all_proxies)
        toolbar_layout.addWidget(select_all_proxy_btn)
        
        self.selected_proxy_count_label = QLabel("")
        self.selected_proxy_count_label.setFont(QFont("Segoe UI", 9))
        self.selected_proxy_count_label.setStyleSheet("color: rgba(255, 255, 255, 0.4);")
        toolbar_layout.addWidget(self.selected_proxy_count_label)
        
        toolbar_layout.addStretch()
        
        self.actions_btn = QPushButton("Действие")
        self.actions_btn.setFixedHeight(36)
        self.actions_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.actions_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.actions_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(25, 25, 28, 0.8);
                color: rgba(255, 255, 255, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: rgba(35, 35, 38, 0.9);
                color: rgba(255, 255, 255, 0.8);
                border-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed { background-color: rgba(20, 20, 23, 0.95); }
            QPushButton::menu-indicator { image: none; width: 0px; }
        """)
        self._create_actions_menu()
        toolbar_layout.addWidget(self.actions_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        progress_container = QWidget()
        progress_container.setStyleSheet("background: transparent; border: none;")
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(4)

        self.proxy_progress_label = QLabel("")
        self.proxy_progress_label.setFont(QFont("Segoe UI", 8))
        self.proxy_progress_label.setStyleSheet("color: rgba(255, 255, 255, 0.3); background: transparent; border: none;")
        progress_layout.addWidget(self.proxy_progress_label)

        self.proxy_progress_bar = QProgressBar()
        self.proxy_progress_bar.setFixedHeight(6)
        self.proxy_progress_bar.setTextVisible(False)
        self.proxy_progress_bar.setStyleSheet(PROGRESS_BAR)
        progress_layout.addWidget(self.proxy_progress_bar)
        
        self.proxy_progress_container = progress_container
        self.proxy_progress_container.setVisible(False)
        main_layout.addWidget(self.proxy_progress_container)
        
        self.proxy_table = create_proxy_table()
        self.proxy_table.itemChanged.connect(self._update_proxy_count)
        self.proxy_table.itemChanged.connect(self._on_proxy_item_changed)
        self.proxy_table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        main_layout.addWidget(self.proxy_table)
        
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(0)
        
        pagination_widget = CustomPaginationWidget()
        
        pagination_inner = QHBoxLayout(pagination_widget)
        pagination_inner.setContentsMargins(0, 10, 0, 10)
        pagination_inner.setSpacing(12)
        
        pagination_inner.addStretch()
        
        icons_dir = Path(__file__).parent.parent.parent.parent / "assets" / "icons"
        
        self.prev_page_btn = QPushButton()
        self.prev_page_btn.setFixedSize(28, 28)
        self.prev_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_page_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(25, 25, 28, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(35, 35, 38, 0.9);
                border-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed { background-color: rgba(20, 20, 23, 0.95); }
            QPushButton:disabled {
                background-color: rgba(15, 15, 17, 0.6);
                border-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self._set_svg_icon(self.prev_page_btn, str(icons_dir / "arrow_up.svg"))
        self.prev_page_btn.clicked.connect(self._prev_page)
        pagination_inner.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("1/1")
        self.page_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.page_label.setStyleSheet("color: #3b82f6; background: transparent; border: none;")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setFixedWidth(40)
        pagination_inner.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton()
        self.next_page_btn.setFixedSize(28, 28)
        self.next_page_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_page_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(25, 25, 28, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(35, 35, 38, 0.9);
                border-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed { background-color: rgba(20, 20, 23, 0.95); }
            QPushButton:disabled {
                background-color: rgba(15, 15, 17, 0.6);
                border-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self._set_svg_icon(self.next_page_btn, str(icons_dir / "arrow_down.svg"))
        self.next_page_btn.clicked.connect(self._next_page)
        pagination_inner.addWidget(self.next_page_btn)
        
        pagination_inner.addStretch()
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(pagination_widget)
        main_layout.addLayout(pagination_layout)
        
        self._update_proxy_count()
    
    def _set_svg_icon(self, button, svg_path):
        svg_data = Path(svg_path).read_text()
        colored_svg = svg_data.replace('stroke="currentColor"', 'stroke="#ffffff"')
        
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(18, 18))
    
    def _select_all_proxies(self):
        self._save_current_page_state()
        
        all_selected = all(proxy["checked"] for proxy in self.all_accounts)
        target_state = not all_selected
        
        for proxy in self.all_accounts:
            proxy["checked"] = target_state
        
        for row in range(self.proxy_table.rowCount()):
            checkbox_item = self.proxy_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setData(Qt.ItemDataRole.UserRole, target_state)
        
        self.proxy_table.viewport().update()
        self._update_proxy_count()
    
    def _update_proxy_count(self):
        self._save_current_page_state()
        
        selected = sum(1 for proxy in self.all_accounts if proxy["checked"])
        if selected > 0:
            self.selected_proxy_count_label.setText(f"Выбрано: {selected}")
            self.selected_proxy_count_label.setStyleSheet("color: #3b82f6; font-weight: 600;")
        else:
            self.selected_proxy_count_label.setText("")
    
    def _on_proxy_item_changed(self, item):
        if not item:
            return
        
        col = item.column()
        if col != 8:
            return
        
        full_text = item.text().strip()
        if not full_text:
            full_text = "---"
        
        if len(full_text) > 15:
            self.proxy_table.blockSignals(True)
            item.setText(full_text[:15])
            item.setToolTip(full_text)
            self.proxy_table.blockSignals(False)
        else:
            item.setToolTip(full_text)
        
        row = item.row()
        start_idx = self.current_page * self.accounts_per_page
        proxy_idx = start_idx + row
        
        if proxy_idx < len(self.all_accounts):
            proxy = self.all_accounts[proxy_idx]
            proxy["tag"] = full_text[:15]
            self.db.update_proxy_tags([proxy["id"]], full_text[:15])
    
    def _load_page(self):
        start_idx = self.current_page * self.accounts_per_page
        end_idx = min(start_idx + self.accounts_per_page, len(self.all_accounts))
        page_proxies = self.all_accounts[start_idx:end_idx]
        
        self.proxy_table.blockSignals(True)
        self.proxy_table.setRowCount(len(page_proxies))
        
        for row, proxy in enumerate(page_proxies):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setData(Qt.ItemDataRole.UserRole, proxy["checked"])
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.proxy_table.setItem(row, 0, checkbox_item)
            
            country = proxy.get('country', 'UN')
            
            ip_widget = QWidget()
            ip_layout = QHBoxLayout(ip_widget)
            ip_layout.setContentsMargins(4, 0, 4, 0)
            ip_layout.setSpacing(6)
            
            flag_label = FlagLoader.get_flag_label(country)
            ip_layout.addWidget(flag_label)
            
            ip_text_label = QLabel(proxy['ip'])
            ip_text_label.setStyleSheet("color: #ffffff; font-size: 9pt; font-family: 'Segoe UI';")
            ip_layout.addWidget(ip_text_label)
            ip_layout.addStretch()
            
            self.proxy_table.setCellWidget(row, 1, ip_widget)
            
            port_item = QTableWidgetItem(proxy["port"])
            port_item.setForeground(QColor("#666666"))
            port_font = QFont("Segoe UI", 8)
            port_item.setFont(port_font)
            port_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            port_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 2, port_item)
            
            response_time = proxy.get("response_time")
            if response_time and proxy["status"] == "alive":
                ping_text = f"{int(response_time * 1000)}ms"
                ping_color = "#10b981" if response_time < 0.5 else "#f59e0b" if response_time < 1.0 else "#ef4444"
            else:
                ping_text = "-"
                ping_color = "#666666"
            
            ping_item = QTableWidgetItem(ping_text)
            ping_item.setForeground(QColor(ping_color))
            ping_font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
            ping_item.setFont(ping_font)
            ping_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            ping_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 3, ping_item)
            
            login_item = QTableWidgetItem(proxy["login"] if proxy["login"] else "-")
            login_item.setForeground(QColor("#999999"))
            login_font = QFont("Segoe UI", 8)
            login_item.setFont(login_font)
            login_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            login_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 4, login_item)
            
            password_item = QTableWidgetItem(proxy["password"] if proxy["password"] else "-")
            password_item.setForeground(QColor("#999999"))
            password_font = QFont("Segoe UI", 8)
            password_item.setFont(password_font)
            password_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            password_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 5, password_item)
            
            protocol_item = QTableWidgetItem(proxy["protocol"])
            protocol_item.setForeground(QColor("#3b82f6"))
            protocol_font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
            protocol_item.setFont(protocol_font)
            protocol_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            protocol_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 6, protocol_item)
            
            status_item = QTableWidgetItem(proxy["status"])
            status_font = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
            status_item.setFont(status_font)
            status_item.setForeground(QColor("#10b981") if proxy["status"] == "alive" else QColor("#ef4444"))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.proxy_table.setItem(row, 7, status_item)
            
            tag_text = proxy.get("tag", "---") or "---"
            tag_item = QTableWidgetItem(tag_text[:15])
            tag_item.setForeground(QColor("#888888"))
            tag_item.setToolTip(tag_text)
            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            tag_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.proxy_table.setItem(row, 8, tag_item)
        
        self.proxy_table.blockSignals(False)
        self._update_pagination()
        self._update_proxy_count()
    
    def _check_selected_proxies(self):
        if self.is_checking:
            self._stop_proxy_check()
            return
        
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери прокси")
            return
        
        self.is_checking = True
        self.check_proxy_btn.setText("Остановить")
        self.check_proxy_btn.setStyleSheet(BUTTON_DANGER)
        
        proxy_tuples = []
        for proxy in selected:
            proxy_tuples.append((
                proxy["ip"],
                int(proxy["port"]),
                proxy["protocol"],
                proxy.get("login"),
                proxy.get("password")
            ))
        
        self.proxy_progress_container.setVisible(True)
        self.proxy_worker = ProxyCheckWorker(proxy_tuples, parent=self)
        self.proxy_worker.progress_signal.connect(self._on_check_progress)
        self.proxy_worker.finished_signal.connect(self._on_check_finished)
        self.proxy_worker.start()
    
    def _stop_proxy_check(self):
        if self.proxy_worker and self.proxy_worker.isRunning():
            self.proxy_worker.stop()
    
    def _on_check_progress(self, current, total):
        progress = int((current / total) * 100)
        self.proxy_progress_bar.setValue(progress)
        self.proxy_progress_label.setText(f"Проверено: {current}/{total}")
    
    def _on_check_finished(self, results):
        self.is_checking = False
        self.check_proxy_btn.setText("Проверить прокси")
        self.check_proxy_btn.setStyleSheet(BUTTON_SECONDARY)
        self.proxy_progress_container.setVisible(False)
        
        alive_count = sum(1 for r in results if r.status == "alive")
        dead_count = len(results) - alive_count
        
        for result in results:
            for acc in self.all_accounts:
                if acc["ip"] == result.ip and int(acc["port"]) == result.port:
                    acc["status"] = result.status
                    acc["response_time"] = result.response_time
                    acc["country"] = result.country
                    if result.status == "alive":
                        acc["protocol"] = result.protocol
                    self.db.update_proxy_status(
                        acc["id"],
                        result.status,
                        result.response_time,
                        result.country,
                        result.protocol if result.status == "alive" else acc["protocol"]
                    )
                    break
        
        self.load_data()
        
        if self.notification:
            self.notification.show_notification(f"Проверка завершена: {alive_count} живых, {dead_count} мёртвых")
    
    def _delete_selected_proxies(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери прокси")
            return
        
        dialog = ConfirmDialog(
            f"Удалить {len(selected)} прокси?",
            "Это действие нельзя отменить",
            self
        )
        if dialog.exec():
            proxy_ids = [acc["id"] for acc in selected]
            self.db.delete_proxies(proxy_ids)
            self.load_data()
            self._update_accounts_stats()
            if self.notification:
                self.notification.show_notification(f"Удалено {len(selected)} прокси")
    
    def _delete_dead_proxies(self):
        dead = [acc for acc in self.all_accounts if acc.get("status") == "dead"]
        if not dead:
            if self.notification:
                self.notification.show_notification("Нет мертвых прокси")
            return
        
        dialog = ConfirmDialog(
            f"Удалить {len(dead)} мертвых прокси?",
            "Это действие нельзя отменить",
            self
        )
        if dialog.exec():
            proxy_ids = [acc["id"] for acc in dead]
            self.db.delete_proxies(proxy_ids)
            self.load_data()
            self._update_accounts_stats()
            if self.notification:
                self.notification.show_notification(f"Удалено {len(dead)} мертвых прокси")
    
    def _create_actions_menu(self):
        self.actions_menu = QMenu(self)
        self.actions_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(20, 20, 23, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                color: rgba(255, 255, 255, 0.6);
                padding: 10px 24px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: rgba(35, 35, 38, 0.9);
                color: rgba(255, 255, 255, 0.95);
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.06);
                margin: 6px 0;
            }
        """)
        
        delete_selected_action = QAction("Удалить прокси", self)
        delete_selected_action.triggered.connect(self._delete_selected_proxies)
        self.actions_menu.addAction(delete_selected_action)
        
        delete_dead_action = QAction("Удалить плохие прокси", self)
        delete_dead_action.triggered.connect(self._delete_dead_proxies)
        self.actions_menu.addAction(delete_dead_action)
        
        self.actions_menu.addSeparator()
        
        set_tag_action = QAction("Поставить тег", self)
        set_tag_action.triggered.connect(self._set_tag_for_selected)
        self.actions_menu.addAction(set_tag_action)
        
        self.actions_btn.setMenu(self.actions_menu)
    
    def _set_tag_for_selected(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери прокси")
            return
        
        dialog = TextInputDialog(
            "Введи тег",
            "Тег для выбранных прокси",
            "Например: 123321",
            self
        )
        if dialog.exec():
            tag = dialog.get_text()
            if tag:
                proxy_ids = [acc["id"] for acc in selected]
                self.db.update_proxy_tags(proxy_ids, tag)
                self.load_data()
                if self.notification:
                    self.notification.show_notification(f"Тег '{tag}' установлен для {len(selected)} прокси")
    
    def _on_header_clicked(self, logical_index):
        if logical_index == 3:
            self._save_current_page_state()
            
            if self.ping_sort_state == 0:
                self.ping_sort_state = 1
                self.all_accounts.sort(key=lambda x: (
                    x.get('response_time') is None or x.get('status') != 'alive',
                    x.get('response_time') if x.get('response_time') is not None else float('inf')
                ))
            else:
                self.ping_sort_state = 0
                proxies = self.db.load_proxies()
                self.all_accounts = []
                for proxy in proxies:
                    self.all_accounts.append({
                        "id": proxy.get("id"),
                        "ip": proxy.get("ip", ""),
                        "port": str(proxy.get("port", "")),
                        "protocol": proxy.get("protocol", "HTTP"),
                        "login": proxy.get("login"),
                        "password": proxy.get("password"),
                        "status": proxy.get("status", "alive"),
                        "response_time": proxy.get("response_time"),
                        "tag": proxy.get("tag", "---"),
                        "country": proxy.get("country", "UN"),
                        "checked": False
                    })
            
            self.db.set_proxy_sort_state(self.ping_sort_state)
            self.current_page = 0
            self._load_page()
    
    def _update_accounts_stats(self):
        main_window = self.window()
        if hasattr(main_window, 'accounts_page'):
            main_window.accounts_page._update_stats()
    
    def load_data(self):
        proxies = self.db.load_proxies()
        self.all_accounts = []
        self.ping_sort_state = self.db.get_proxy_sort_state()
        
        for proxy in proxies:
            status = proxy.get("status", "alive")
            
            self.all_accounts.append({
                "id": proxy.get("id"),
                "ip": proxy.get("ip", ""),
                "port": str(proxy.get("port", "")),
                "protocol": proxy.get("protocol", "HTTP"),
                "login": proxy.get("login"),
                "password": proxy.get("password"),
                "status": status,
                "response_time": proxy.get("response_time"),
                "tag": proxy.get("tag", "---"),
                "country": proxy.get("country", "UN"),
                "checked": False
            })
        
        if self.ping_sort_state == 1:
            self.all_accounts.sort(key=lambda x: (
                x.get('response_time') is None or x.get('status') != 'alive',
                x.get('response_time') if x.get('response_time') is not None else float('inf')
            ))
        
        self.stats_bar.update_card_count("Прокси", len(self.all_accounts))
        main_window = self.window()
        if hasattr(main_window, 'accounts_page'):
            account_count = main_window.accounts_page.db.get_account_count()
            self.stats_bar.update_card_count("Активные аккаунты", account_count)
            self.stats_bar.update_card_count("Недостаточно прав", self.db.get_insufficient_rights_count())
            self.stats_bar.update_card_count("Мертвые аккаунты", self.db.get_dead_tokens_count())
        
        self.current_page = 0
        self._load_page()
