from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QPushButton, QLabel, QMenu, QApplication
from PyQt6.QtCore import Qt, QByteArray, QSize
from PyQt6.QtGui import QFont, QColor, QAction, QPainter, QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer
from src.ui.pages.base_detail import BaseDetailPage
from src.ui.components.accounts_table import create_accounts_table
from src.ui.components.pagination import CustomPaginationWidget
from src.ui.components.stats_bar import StatsBar
from src.ui.styles import BUTTON_SECONDARY
from src.ui.dialogs.confirm import ConfirmDialog
from src.ui.dialogs.text_input import TextInputDialog
from pathlib import Path

class AccountsDetailPage(BaseDetailPage):
    def __init__(self, parent=None):
        super().__init__("Активные аккаунты", parent)
        self.actions_menu = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        self.stats_bar = StatsBar()
        self.stats_bar.card_clicked.connect(self.stat_card_clicked.emit)
        main_layout.addWidget(self.stats_bar)
        
        toolbar_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Выделить все")
        select_all_btn.setFixedHeight(36)
        select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_all_btn.setFont(QFont("Segoe UI", 9))
        select_all_btn.setStyleSheet(BUTTON_SECONDARY)
        select_all_btn.clicked.connect(self._select_all_accounts)
        toolbar_layout.addWidget(select_all_btn)
        
        self.selected_count_label = QLabel("")
        self.selected_count_label.setFont(QFont("Segoe UI", 9))
        self.selected_count_label.setStyleSheet("color: rgba(255, 255, 255, 0.4);")
        toolbar_layout.addWidget(self.selected_count_label)
        
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
        
        self.accounts_table = create_accounts_table()
        self.accounts_table.itemChanged.connect(self._update_selected_count)
        self.accounts_table.itemChanged.connect(self._on_item_changed)
        self.accounts_table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        main_layout.addWidget(self.accounts_table)
        
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
        
        self._update_selected_count()
    
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
    
    def _select_all_accounts(self):
        self._save_current_page_state()
        
        all_selected = all(acc["checked"] for acc in self.all_accounts)
        target_state = not all_selected
        
        for acc in self.all_accounts:
            acc["checked"] = target_state
        
        for row in range(self.accounts_table.rowCount()):
            checkbox_item = self.accounts_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setData(Qt.ItemDataRole.UserRole, target_state)
        
        self.accounts_table.viewport().update()
        self._update_selected_count()
    
    def _update_selected_count(self):
        self._save_current_page_state()
        
        selected = sum(1 for acc in self.all_accounts if acc["checked"])
        if selected > 0:
            self.selected_count_label.setText(f"Выбрано: {selected}")
            self.selected_count_label.setStyleSheet("color: #3b82f6; font-weight: 600;")
        else:
            self.selected_count_label.setText("")
    
    def _on_item_changed(self, item):
        if not item:
            return
        
        col = item.column()
        if col != 4:
            return
        
        full_text = item.text().strip()
        if not full_text:
            full_text = "---"
        
        if len(full_text) > 15:
            self.accounts_table.blockSignals(True)
            item.setText(full_text[:15])
            item.setToolTip(full_text)
            self.accounts_table.blockSignals(False)
        else:
            item.setToolTip(full_text)
        
        row = item.row()
        start_idx = self.current_page * self.accounts_per_page
        acc_idx = start_idx + row
        
        if acc_idx < len(self.all_accounts):
            account = self.all_accounts[acc_idx]
            account["tag"] = full_text[:15]
            self.db.update_account_tag(account["id"], full_text[:15])
    
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
        
        delete_selected_action = QAction("Удалить аккаунты", self)
        delete_selected_action.triggered.connect(self._delete_selected_accounts)
        self.actions_menu.addAction(delete_selected_action)

        move_dead_action = QAction("Переместить в мертвые", self)
        move_dead_action.triggered.connect(self._move_to_dead)
        self.actions_menu.addAction(move_dead_action)
        
        self.actions_menu.addSeparator()
        
        set_tag_action = QAction("Поставить тег", self)
        set_tag_action.triggered.connect(self._set_tag_for_selected)
        self.actions_menu.addAction(set_tag_action)
        
        self.actions_btn.setMenu(self.actions_menu)
    
    def _delete_selected_accounts(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери аккаунты")
            return
        
        dialog = ConfirmDialog(
            f"Удалить {len(selected)} аккаунтов?",
            "Это действие нельзя отменить",
            self
        )
        if dialog.exec():
            account_ids = [acc["id"] for acc in selected]
            self.db.delete_accounts(account_ids)
            self.load_data()
            main_window = self.window()
            if hasattr(main_window, 'accounts_page'):
                main_window.accounts_page._update_stats()
            if self.notification:
                self.notification.show_notification(f"Удалено {len(selected)} аккаунтов")
    
    def _move_to_dead(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери аккаунты")
            return
        dialog = ConfirmDialog(
            f"Переместить {len(selected)} аккаунтов в мертвые?",
            "Их можно будет восстановить позже",
            self,
            confirm_text="Переместить"
        )
        if dialog.exec():
            account_ids = [acc["id"] for acc in selected]
            self.db.move_to_dead(account_ids)
            self.load_data()
            main_window = self.window()
            if hasattr(main_window, 'accounts_page'):
                main_window.accounts_page._update_stats()
            if self.notification:
                self.notification.show_notification(f"Перемещено {len(selected)} аккаунтов")

    def _set_tag_for_selected(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери аккаунты")
            return
        
        dialog = TextInputDialog(
            "Введи тег",
            "Тег для выбранных аккаунтов",
            "Например: 123321",
            self
        )
        if dialog.exec():
            tag = dialog.get_text().strip()
            if not tag:
                tag = "---"
            
            if len(tag) > 15:
                tag = tag[:15]
            
            account_ids = [acc["id"] for acc in selected]
            self.db.update_account_tags(account_ids, tag)
            
            for acc in selected:
                acc["tag"] = tag
            
            self._load_page()
            
            if self.notification:
                self.notification.show_notification(f"Тег '{tag}' установлен для {len(selected)} аккаунтов")
    
    def load_data(self):
        accounts_data = self.db.get_accounts()
        self.all_accounts = []
        
        for acc in accounts_data:
            proxy_ip = acc[11] if len(acc) > 11 else None
            proxy_port = acc[12] if len(acc) > 12 else None
            proxy_str = f"{proxy_ip}:{proxy_port}" if proxy_ip and proxy_port else "---"
            
            nitro_str = self._get_nitro_string(acc[7])
            added_date = acc[10] if len(acc) > 10 else ""
            
            if added_date and isinstance(added_date, str):
                added_date = added_date.replace('T', ' ').split('.')[0]
            else:
                added_date = str(added_date) if added_date else ""
            
            self.all_accounts.append({
                "id": acc[0],
                "token": acc[1],
                "username": acc[2] or "Unknown",
                "user_id": acc[3],
                "email": acc[4],
                "phone": acc[5] or "---",
                "discriminator": acc[6],
                "nitro": nitro_str,
                "proxy": proxy_str,
                "tag": acc[9] or "---",
                "added_date": added_date,
                "checked": False
            })
        
        self.stats_bar.update_card_count("Прокси", self.db.get_proxy_count())
        self.stats_bar.update_card_count("Активные аккаунты", len(self.all_accounts))
        self.stats_bar.update_card_count("Недостаточно прав", self.db.get_insufficient_rights_count())
        self.stats_bar.update_card_count("Мертвые аккаунты", self.db.get_dead_tokens_count())
        self.current_page = 0
        self._load_page()
    
    def _get_nitro_string(self, nitro_value):
        nitro_map = {
            0: "None",
            1: "Classic",
            2: "Full",
            3: "Basic"
        }
        return nitro_map.get(nitro_value, "None")
    
    def _on_cell_double_clicked(self, row, column):
        if column == 3:
            item = self.accounts_table.item(row, column)
            if item:
                token = item.data(Qt.ItemDataRole.UserRole)
                if token:
                    clipboard = QApplication.clipboard()
                    clipboard.setText(token)
                    if self.notification:
                        self.notification.show_notification("Токен скопирован")
        
        elif column == 5:
            start_idx = self.current_page * self.accounts_per_page
            acc_idx = start_idx + row
            
            if acc_idx < len(self.all_accounts):
                account = self.all_accounts[acc_idx]
                
                item = self.accounts_table.item(row, column)
                if item:
                    rect = self.accounts_table.visualItemRect(item)
                    global_pos = self.accounts_table.viewport().mapToGlobal(rect.bottomLeft())
                    self._show_proxy_menu(global_pos, account)
    
    def _show_proxy_menu(self, pos, account):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        
        all_proxies_menu = QMenu("Все прокси", self)
        all_proxies_menu.setStyleSheet(self._get_menu_style())
        self._populate_protocol_menu(all_proxies_menu, "all", None, account)
        menu.addMenu(all_proxies_menu)
        
        tags = self.db.get_proxy_tags()
        if tags:
            by_tag_menu = QMenu("По тегу", self)
            by_tag_menu.setStyleSheet(self._get_menu_style())
            
            for tag in tags:
                tag_menu = QMenu(tag, self)
                tag_menu.setStyleSheet(self._get_menu_style())
                self._populate_protocol_menu(tag_menu, "tag", tag, account)
                by_tag_menu.addMenu(tag_menu)
            
            menu.addMenu(by_tag_menu)
        
        countries = self.db.get_proxy_countries()
        if countries:
            by_country_menu = QMenu("По стране", self)
            by_country_menu.setStyleSheet(self._get_menu_style())
            
            for country in countries:
                country_menu = QMenu(country, self)
                country_menu.setStyleSheet(self._get_menu_style())
                self._populate_protocol_menu(country_menu, "country", country, account)
                by_country_menu.addMenu(country_menu)
            
            menu.addMenu(by_country_menu)
        
        unused_menu = QMenu("Неиспользуемые", self)
        unused_menu.setStyleSheet(self._get_menu_style())
        self._populate_protocol_menu(unused_menu, "unused", None, account)
        menu.addMenu(unused_menu)
        
        menu.exec(pos)
    
    def _populate_protocol_menu(self, parent_menu, mode, value, account):
        protocols = ["Все протоколы", "SOCKS5", "SOCKS4", "HTTP", "HTTPS"]
        
        for protocol in protocols:
            proxies = self.db.get_proxies_for_rotation(mode, value)
            
            if protocol != "Все протоколы":
                proxies = [p for p in proxies if p[3] == protocol]
            
            if proxies:
                protocol_menu = QMenu(protocol, self)
                protocol_menu.setStyleSheet(self._get_menu_style())
                
                total_count = len(proxies)
                limit = 15
                
                for proxy in proxies[:limit]:
                    proxy_id = proxy[0]
                    ip = proxy[1]
                    port = proxy[2]
                    proto = proxy[3]
                    display_text = f"{ip}:{port} ({proto})"
                    
                    action = QAction(display_text, self)
                    action.triggered.connect(lambda checked, pid=proxy_id, acc=account: self._assign_proxy(pid, acc))
                    protocol_menu.addAction(action)
                
                if total_count > limit:
                    protocol_menu.addSeparator()
                    info_action = QAction(f"Всего: {total_count} прокси", self)
                    info_action.setEnabled(False)
                    protocol_menu.addAction(info_action)
                
                parent_menu.addMenu(protocol_menu)
            else:
                if protocol == "Все протоколы":
                    action = QAction("Нет доступных прокси", self)
                    action.setEnabled(False)
                    parent_menu.addAction(action)
    
    def _assign_proxy(self, proxy_id, account):
        self.db.update_account_proxy(account["id"], proxy_id)
        
        self.load_data()
        
        if self.notification:
            self.notification.show_notification("Прокси обновлен")
    
    def _get_menu_style(self):
        return """
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
            QMenu::right-arrow {
                image: none;
                width: 0px;
            }
            QMenu QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
                border-radius: 5px;
                margin: 6px 2px 6px 2px;
            }
            QMenu QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                min-height: 30px;
            }
            QMenu QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QMenu QScrollBar::add-line:vertical,
            QMenu QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMenu QScrollBar::add-page:vertical,
            QMenu QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """
    
    def _load_page(self):
        start_idx = self.current_page * self.accounts_per_page
        end_idx = min(start_idx + self.accounts_per_page, len(self.all_accounts))
        page_accounts = self.all_accounts[start_idx:end_idx]
        
        self.accounts_table.blockSignals(True)
        self.accounts_table.setRowCount(len(page_accounts))
        
        for row, account in enumerate(page_accounts):            
            checkbox_item = QTableWidgetItem()
            checkbox_item.setData(Qt.ItemDataRole.UserRole, account["checked"])
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.accounts_table.setItem(row, 0, checkbox_item)
            
            phone_item = QTableWidgetItem(account["phone"])
            phone_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            phone_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.accounts_table.setItem(row, 1, phone_item)
            
            username_item = QTableWidgetItem(account["username"])
            username_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            username_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.accounts_table.setItem(row, 2, username_item)
            
            token_item = QTableWidgetItem(account["token"])
            token_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            token_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            token_item.setData(Qt.ItemDataRole.UserRole, account["token"])
            self.accounts_table.setItem(row, 3, token_item)
            
            tag_item = QTableWidgetItem(account["tag"])
            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tag_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.accounts_table.setItem(row, 4, tag_item)
            
            proxy_item = QTableWidgetItem(account["proxy"])
            proxy_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            proxy_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.accounts_table.setItem(row, 5, proxy_item)
            
            nitro_item = QTableWidgetItem(account["nitro"])
            nitro_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            nitro_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.accounts_table.setItem(row, 6, nitro_item)
            
            date_item = QTableWidgetItem(account.get("added_date", ""))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.accounts_table.setItem(row, 7, date_item)
        
        self.accounts_table.blockSignals(False)
        self._update_pagination()
        self._update_selected_count()
