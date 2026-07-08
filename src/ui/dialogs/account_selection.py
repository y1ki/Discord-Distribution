from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.core.database import Database
from src.ui.components.combobox import AnimatedComboBox
from src.ui.dialogs._widgets import (
    DIALOG_FRAME_STYLE,
    make_dialog_header,
    make_separator,
    make_dialog_button,
)


LABEL_STYLE = "color: rgba(255, 255, 255, 0.7); background: transparent; border: none;"
BASE_HEIGHT = 286
EXTRA_HEIGHT = 74


class AccountSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.selected_proxies = []
        self.selected_accounts = []
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }" + DIALOG_FRAME_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        frame = QWidget()
        frame.setObjectName("dialogFrame")
        frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        frame.setMinimumWidth(520)
        layout.addWidget(frame)

        content = QVBoxLayout(frame)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        content.addWidget(make_dialog_header("Выбор аккаунтов", self.reject))
        content.addWidget(make_separator())

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 18)
        body_layout.setSpacing(0)

        body_layout.addWidget(self._field_label("Источник прокси"))
        body_layout.addSpacing(4)
        self.proxy_combo = AnimatedComboBox()
        self.proxy_combo.addItems(["Все прокси", "По тегу", "По стране"])
        self.proxy_combo.currentIndexChanged.connect(self._on_proxy_source_changed)
        body_layout.addWidget(self.proxy_combo)

        self.proxy_detail_container, self.proxy_detail_label, self.proxy_detail_combo = self._build_detail()
        body_layout.addWidget(self.proxy_detail_container)
        self.proxy_detail_container.setVisible(False)

        body_layout.addSpacing(12)
        body_layout.addWidget(self._field_label("Аккаунты"))
        body_layout.addSpacing(4)
        self.accounts_combo = AnimatedComboBox()
        self.accounts_combo.addItems(["Все аккаунты", "По тегу"])
        self.accounts_combo.currentIndexChanged.connect(self._on_accounts_filter_changed)
        body_layout.addWidget(self.accounts_combo)

        self.accounts_detail_container, self.accounts_detail_label, self.accounts_detail_combo = self._build_detail("Выбери тег")
        body_layout.addWidget(self.accounts_detail_container)
        self.accounts_detail_container.setVisible(False)

        body_layout.addSpacing(8)
        body_layout.addWidget(self._build_buttons())
        content.addWidget(body)
        self._recalc_size()

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setFixedHeight(16)
        label.setStyleSheet(LABEL_STYLE)
        return label

    def _build_detail(self, initial_text: str = ""):
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(6)

        label = QLabel(initial_text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(label)

        combo = AnimatedComboBox()
        layout.addWidget(combo)
        return container, label, combo

    def _build_buttons(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        cancel = make_dialog_button("Отмена")
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

        ok = make_dialog_button("Продолжить", primary=True, width=100)
        ok.clicked.connect(self._on_accept)
        layout.addWidget(ok)
        self.ok_btn = ok
        return container

    def _recalc_size(self):
        extra = 0
        if self.proxy_detail_container.isVisible():
            extra += EXTRA_HEIGHT
        if self.accounts_detail_container.isVisible():
            extra += EXTRA_HEIGHT
        self.setFixedSize(540, BASE_HEIGHT + extra)

    def _on_proxy_source_changed(self, index: int):
        self.proxy_detail_combo.clear()
        if index == 1:
            self.proxy_detail_label.setText("Выбери тег")
            tags = self.db.get_proxy_tags()
            self.proxy_detail_combo.addItems(tags or ["Нет тегов"])
            self.proxy_detail_container.setVisible(True)
        elif index == 2:
            self.proxy_detail_label.setText("Выбери страну")
            countries = self.db.get_proxy_countries()
            self.proxy_detail_combo.addItems(countries or ["Нет стран"])
            self.proxy_detail_container.setVisible(True)
        else:
            self.proxy_detail_container.setVisible(False)
        self._recalc_size()

    def _on_accounts_filter_changed(self, index: int):
        if index == 1:
            self.accounts_detail_combo.clear()
            tags = self.db.get_account_tags()
            self.accounts_detail_combo.addItems(tags or ["Нет тегов"])
            self.accounts_detail_container.setVisible(True)
        else:
            self.accounts_detail_container.setVisible(False)
        self._recalc_size()

    def _on_accept(self):
        proxy_index = self.proxy_combo.currentIndex()
        if proxy_index == 0:
            proxies = self.db.get_proxies_for_rotation("all")
        elif proxy_index == 1:
            proxies = self.db.get_proxies_for_rotation("tag", self.proxy_detail_combo.currentText())
        else:
            proxies = self.db.get_proxies_for_rotation("country", self.proxy_detail_combo.currentText())

        if self.accounts_combo.currentIndex() == 0:
            accounts = self.db.get_accounts_with_proxy()
        else:
            accounts = self.db.get_accounts_by_tag(self.accounts_detail_combo.currentText())

        self.selected_proxies = [
            p if isinstance(p, dict) else {
                "id": p[0], "ip": p[1], "port": p[2], "protocol": p[3],
                "login": p[4], "password": p[5],
            }
            for p in proxies
        ]
        self.selected_accounts = accounts
        self.accept()

    def get_result(self):
        return self.selected_proxies, self.selected_accounts
