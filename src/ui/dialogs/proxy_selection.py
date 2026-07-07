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
BASE_HEIGHT = 234
EXTRA_HEIGHT = 74


class ProxySelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }" + DIALOG_FRAME_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self._frame = QLabel()
        self._frame.setObjectName("dialogFrame")
        layout.addWidget(self._frame)

        content = QVBoxLayout(self._frame)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        content.addWidget(make_dialog_header("Выбор прокси", self.reject))
        content.addWidget(make_separator())

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 18)
        body_layout.setSpacing(0)

        body_layout.addWidget(self._make_field_label("Источник прокси"))
        body_layout.addSpacing(4)

        self.source_combo = AnimatedComboBox()
        self.source_combo.addItems(["Все прокси", "По тегу", "По стране"])
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        body_layout.addWidget(self.source_combo)

        self.detail_container = QWidget()
        self.detail_container.setStyleSheet("background: transparent; border: none;")
        detail_layout = QVBoxLayout(self.detail_container)
        detail_layout.setContentsMargins(0, 12, 0, 0)
        detail_layout.setSpacing(6)

        self.detail_label = QLabel()
        self.detail_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.detail_label.setStyleSheet(LABEL_STYLE)
        detail_layout.addWidget(self.detail_label)

        self.detail_combo = AnimatedComboBox()
        detail_layout.addWidget(self.detail_combo)

        body_layout.addWidget(self.detail_container)
        self.detail_container.setVisible(False)

        body_layout.addSpacing(8)
        body_layout.addWidget(self._build_buttons())

        content.addWidget(body)
        self._recalc_size()

    def _make_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setFixedHeight(16)
        label.setStyleSheet(LABEL_STYLE)
        return label

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

        ok = make_dialog_button("Продолжить", primary=True)
        ok.clicked.connect(self.accept)
        layout.addWidget(ok)
        return container

    def _recalc_size(self):
        extra = EXTRA_HEIGHT if self.detail_container.isVisible() else 0
        height = BASE_HEIGHT + extra
        self._frame.setFixedSize(500, height - 20)
        self.setFixedSize(520, height)

    def _on_source_changed(self, index: int):
        self.detail_combo.clear()
        if index == 1:
            self.detail_label.setText("Выбери тег")
            tags = self.db.get_proxy_tags()
            self.detail_combo.addItems(tags or ["Нет тегов"])
            self.detail_container.setVisible(True)
        elif index == 2:
            self.detail_label.setText("Выбери страну")
            countries = self.db.get_proxy_countries()
            self.detail_combo.addItems(countries or ["Нет стран"])
            self.detail_container.setVisible(True)
        else:
            self.detail_container.setVisible(False)
        self._recalc_size()

    def get_selection(self):
        index = self.source_combo.currentIndex()
        if index == 1:
            return ("tag", self.detail_combo.currentText())
        if index == 2:
            return ("country", self.detail_combo.currentText())
        return ("all", None)
