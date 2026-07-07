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
from pathlib import Path

class DeadTokensPage(BaseDetailPage):
    def __init__(self, parent=None):
        super().__init__("Мертвые аккаунты", parent)
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
                border-radius: 6px; padding: 4px;
            }
            QPushButton:hover { background-color: rgba(35, 35, 38, 0.9); border-color: rgba(255, 255, 255, 0.15); }
            QPushButton:pressed { background-color: rgba(20, 20, 23, 0.95); }
            QPushButton:disabled { background-color: rgba(15, 15, 17, 0.6); border-color: rgba(255, 255, 255, 0.05); }
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
                border-radius: 6px; padding: 4px;
            }
            QPushButton:hover { background-color: rgba(35, 35, 38, 0.9); border-color: rgba(255, 255, 255, 0.15); }
            QPushButton:pressed { background-color: rgba(20, 20, 23, 0.95); }
            QPushButton:disabled { background-color: rgba(15, 15, 17, 0.6); border-color: rgba(255, 255, 255, 0.05); }
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

    def _create_actions_menu(self):
        self.actions_menu = QMenu(self)
        self.actions_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(20, 20, 23, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px; padding: 6px;
            }
            QMenu::item { color: rgba(255, 255, 255, 0.6); padding: 10px 24px; border-radius: 6px; }
            QMenu::item:selected { background-color: rgba(35, 35, 38, 0.9); color: rgba(255, 255, 255, 0.95); }
            QMenu::separator { height: 1px; background-color: rgba(255, 255, 255, 0.06); margin: 6px 0; }
        """)

        restore_action = QAction("Восстановить", self)
        restore_action.triggered.connect(self._restore_selected)
        self.actions_menu.addAction(restore_action)

        self.actions_menu.addSeparator()

        delete_action = QAction("Удалить навсегда", self)
        delete_action.triggered.connect(self._delete_selected)
        self.actions_menu.addAction(delete_action)

        self.actions_btn.setMenu(self.actions_menu)

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

    def _restore_selected(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери аккаунты")
            return
        dialog = ConfirmDialog(
            f"Восстановить {len(selected)} аккаунтов?",
            "Они вернутся в Активные аккаунты",
            self,
            confirm_text="Восстановить",
            confirm_color="#3b82f6"
        )
        if dialog.exec():
            ids = [acc["id"] for acc in selected]
            self.db.restore_dead_tokens(ids)
            self.load_data()
            main_window = self.window()
            if hasattr(main_window, 'accounts_page'):
                main_window.accounts_page._update_stats()
            if self.notification:
                self.notification.show_notification(f"Восстановлено {len(selected)} аккаунтов")

    def _delete_selected(self):
        selected = [acc for acc in self.all_accounts if acc.get("checked")]
        if not selected:
            if self.notification:
                self.notification.show_notification("Выбери аккаунты")
            return
        dialog = ConfirmDialog(
            f"Удалить {len(selected)} аккаунтов навсегда?",
            "Это действие нельзя отменить",
            self
        )
        if dialog.exec():
            ids = [acc["id"] for acc in selected]
            self.db.delete_dead_tokens(ids)
            self.load_data()
            main_window = self.window()
            if hasattr(main_window, 'accounts_page'):
                main_window.accounts_page._update_stats()
            if self.notification:
                self.notification.show_notification(f"Удалено {len(selected)} аккаунтов")

    def _on_cell_double_clicked(self, row, column):
        if column == 3:
            item = self.accounts_table.item(row, column)
            if item:
                token = item.data(Qt.ItemDataRole.UserRole)
                if token:
                    QApplication.clipboard().setText(token)
                    if self.notification:
                        self.notification.show_notification("Токен скопирован")

    def load_data(self):
        rows = self.db.get_dead_tokens()
        self.all_accounts = []
        for acc in rows:
            proxy_ip = acc[11] if len(acc) > 11 else None
            proxy_port = acc[12] if len(acc) > 12 else None
            proxy_str = f"{proxy_ip}:{proxy_port}" if proxy_ip and proxy_port else "---"
            nitro_map = {0: "None", 1: "Classic", 2: "Full", 3: "Basic"}
            nitro_str = nitro_map.get(acc[7], "None")
            moved_date = acc[10] if len(acc) > 10 else ""
            if moved_date and isinstance(moved_date, str):
                moved_date = moved_date.replace('T', ' ').split('.')[0]
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
                "added_date": moved_date,
                "checked": False
            })

        self.stats_bar.update_card_count("Активные аккаунты", self.db.get_account_count())
        self.stats_bar.update_card_count("Недостаточно прав", self.db.get_insufficient_rights_count())
        self.stats_bar.update_card_count("Мертвые аккаунты", len(self.all_accounts))
        self.stats_bar.update_card_count("Прокси", self.db.get_proxy_count())
        self.current_page = 0
        self._load_page()

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
            tag_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
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
