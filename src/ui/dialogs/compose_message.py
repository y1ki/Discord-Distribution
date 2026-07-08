from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QWidget,
    QScrollArea, QFileDialog, QGridLayout,
)

from src.ui.dialogs._widgets import (
    DIALOG_FRAME_STYLE,
    render_svg_icon,
    make_dialog_header,
    make_separator,
    make_dialog_button,
)


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃",
    "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙",
    "🥲", "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫",
    "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄", "😬",
    "🤥", "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕", "🤢",
    "🤮", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳", "🥸", "😎",
    "🤓", "🧐", "😕", "😟", "🙁", "😮", "😯", "😲", "😳", "🥺",
    "😦", "😧", "😨", "😰", "😥", "😢", "😭", "😱", "😖", "😣",
    "😞", "😓", "😩", "😫", "🥱", "😤", "😡", "😠", "🤬", "😈",
    "👿", "💀", "☠️", "💩", "🤡", "👹", "👺", "👻", "👽", "👾",
    "🤖", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾",
    "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞",
    "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍",
    "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝",
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
    "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "🔥",
    "⭐", "🌟", "✨", "💫", "🎉", "🎊", "🎈", "🎁", "🏆", "🥇",
    "💰", "💵", "💎", "🔔", "📢", "📣", "💬", "💭", "🗯️", "✅",
    "❌", "⚠️", "🔒", "🔓", "📌", "📎", "🔗", "💡", "🔍", "🚀",
]


def rounded_thumbnail(filepath: str, size: int, radius: int = 8) -> QPixmap:
    src = QPixmap(filepath)
    if src.isNull():
        return QPixmap()
    scaled = src.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (scaled.width() - size) // 2
    y = (scaled.height() - size) // 2
    cropped = scaled.copy(x, y, size, size)

    rounded = QPixmap(size, size)
    rounded.fill(Qt.GlobalColor.transparent)
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, cropped)
    painter.end()
    return rounded


class AttachmentCard(QWidget):
    SIZE = 72

    def __init__(self, filepath: str, on_remove):
        super().__init__()
        self.filepath = filepath
        self._on_remove = on_remove
        self.setFixedSize(self.SIZE, self.SIZE)
        self._build()

    def _build(self):
        self.setStyleSheet(
            "AttachmentCard { background-color: rgba(255,255,255,0.05);"
            " border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; }"
        )

        thumb = QLabel(self)
        thumb.setGeometry(4, 4, self.SIZE - 8, self.SIZE - 8)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("background: transparent; border: none;")

        ext = Path(self.filepath).suffix.lower()
        if ext in IMAGE_EXTS:
            thumb.setPixmap(rounded_thumbnail(self.filepath, self.SIZE - 8))
        else:
            thumb.setText(ext.lstrip(".").upper() or "FILE")
            thumb.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            thumb.setStyleSheet(
                "background-color: rgba(88,101,242,0.15); border-radius: 8px;"
                " color: rgba(255,255,255,0.7);"
            )

        remove = QPushButton("\u00d7", self)
        remove.setFixedSize(18, 18)
        remove.setGeometry(self.SIZE - 22, 4, 18, 18)
        remove.setCursor(Qt.CursorShape.PointingHandCursor)
        remove.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        remove.setStyleSheet(
            "QPushButton { background-color: rgba(20,20,23,0.85);"
            " color: rgba(255,255,255,0.85); border: none; border-radius: 9px; }"
            "QPushButton:hover { background-color: #ed4245; color: white; }"
        )
        remove.clicked.connect(lambda: self._on_remove(self))


class EmojiPicker(QWidget):
    COLUMNS = 10

    def __init__(self, on_select, parent=None):
        super().__init__(parent)
        self._on_select = on_select
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(340, 300)
        self._build()

    def _build(self):
        container = QWidget(self)
        container.setGeometry(0, 0, self.width(), self.height())
        container.setStyleSheet(
            "QWidget { background-color: rgba(25,25,28,0.98);"
            " border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; }"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Эмодзи")
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        title.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent; border: none;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: transparent; width: 5px; }"
            "QScrollBar::handle:vertical { background: rgba(255,255,255,0.15);"
            " border-radius: 2px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent; border: none;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)

        for i, emoji in enumerate(EMOJIS):
            btn = QPushButton(emoji)
            btn.setFixedSize(28, 28)
            btn.setFont(QFont("Segoe UI Emoji", 13))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-radius: 4px; }"
                "QPushButton:hover { background: rgba(255,255,255,0.1); }"
            )
            btn.clicked.connect(lambda _, em=emoji: self._pick(em))
            grid.addWidget(btn, i // self.COLUMNS, i % self.COLUMNS)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

    def _pick(self, emoji: str):
        self._on_select(emoji)
        self.close()


class ComposeMessageDialog(QDialog):
    DIALOG_WIDTH = 600
    BASE_HEIGHT = 360
    ATTACHMENTS_HEIGHT = AttachmentCard.SIZE + 18

    def __init__(self, parent=None):
        super().__init__(parent)
        self.attachments: list[str] = []
        self._cards: list[AttachmentCard] = []
        self._emoji_picker: EmojiPicker | None = None

        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }" + DIALOG_FRAME_STYLE)
        self._build()
        self._apply_size()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        self._frame = QWidget()
        self._frame.setObjectName("dialogFrame")
        self._frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        outer.addWidget(self._frame)

        root = QVBoxLayout(self._frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(make_dialog_header("Составить сообщение", self.reject))
        root.addWidget(make_separator())
        root.addWidget(self._build_body(), 1)

    def _build_body(self) -> QWidget:
        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 12, 20, 14)
        layout.setSpacing(8)

        layout.addWidget(self._field_label("Сообщение"))
        layout.addWidget(self._build_text_edit())
        layout.addLayout(self._build_toolbar())
        layout.addWidget(self._build_attachments())
        layout.addStretch()
        layout.addWidget(self._build_actions())
        return body

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent; border: none;")
        return label

    def _build_text_edit(self) -> QTextEdit:
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введи текст сообщения...")
        self.text_edit.setFixedHeight(130)
        self.text_edit.setFont(QFont("Segoe UI", 10))
        self.text_edit.setStyleSheet(
            "QTextEdit { background-color: rgba(255,255,255,0.06);"
            " border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;"
            " color: rgba(255,255,255,0.9); padding: 10px 12px; }"
            "QTextEdit:focus { border: 1px solid rgba(88,101,242,0.6);"
            " background-color: rgba(255,255,255,0.08); }"
            "QScrollBar:vertical { background-color: transparent; width: 6px; }"
            "QScrollBar::handle:vertical { background-color: rgba(255,255,255,0.15);"
            " border-radius: 3px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        return self.text_edit

    def _build_toolbar(self) -> QHBoxLayout:
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(6)
        self.emoji_btn = self._icon_button("emoji.svg", self._toggle_emoji_picker)
        toolbar.addWidget(self.emoji_btn)
        toolbar.addWidget(self._icon_button("plus.svg", self._add_attachments))
        toolbar.addStretch()
        return toolbar

    def _icon_button(self, icon: str, on_click) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(34, 34)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setIcon(render_svg_icon(icon, "#b5b5b5", 18))
        btn.setIconSize(QSize(18, 18))
        btn.setStyleSheet(
            "QPushButton { background-color: transparent; border: none; border-radius: 8px; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.08); }"
            "QPushButton:pressed { background-color: rgba(255,255,255,0.12); }"
        )
        btn.clicked.connect(on_click)
        return btn

    def _build_attachments(self) -> QScrollArea:
        self.attach_scroll = QScrollArea()
        self.attach_scroll.setFixedHeight(AttachmentCard.SIZE + 14)
        self.attach_scroll.setWidgetResizable(True)
        self.attach_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.attach_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.attach_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:horizontal { background: transparent; height: 5px; }"
            "QScrollBar::handle:horizontal { background: rgba(255,255,255,0.15);"
            " border-radius: 2px; min-width: 20px; }"
            "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
        )
        self.attach_scroll.setVisible(False)

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        self.attach_layout = QHBoxLayout(container)
        self.attach_layout.setContentsMargins(2, 6, 2, 6)
        self.attach_layout.setSpacing(8)
        self.attach_layout.addStretch()

        self.attach_scroll.setWidget(container)
        return self.attach_scroll

    def _build_actions(self) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        cancel = make_dialog_button("Отмена", width=96)
        cancel.setFixedHeight(36)
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

        send = make_dialog_button("Готово", primary=True, width=110)
        send.setFixedHeight(36)
        send.clicked.connect(self._on_accept)
        layout.addWidget(send)
        return row

    def _toggle_emoji_picker(self):
        if self._emoji_picker and self._emoji_picker.isVisible():
            self._emoji_picker.close()
            return
        picker = EmojiPicker(self._insert_emoji, self)
        anchor = self.emoji_btn.mapToGlobal(self.emoji_btn.rect().bottomLeft())
        picker.move(anchor.x(), anchor.y() + 4)
        picker.show()
        self._emoji_picker = picker

    def _insert_emoji(self, emoji: str):
        self.text_edit.insertPlainText(emoji)
        self.text_edit.setFocus()

    def _add_attachments(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выбрать файлы", "",
            "Изображения (*.png *.jpg *.jpeg *.gif *.webp);;Все файлы (*)",
        )
        if not files:
            return
        self.attachments.extend(files)
        for filepath in files:
            self._add_card(filepath)
        self.attach_scroll.setVisible(bool(self.attachments))

    def _add_card(self, filepath: str):
        card = AttachmentCard(filepath, on_remove=self._remove_card)
        self._cards.append(card)
        self.attach_layout.insertWidget(self.attach_layout.count() - 1, card)
        self._apply_size()

    def _remove_card(self, card: AttachmentCard):
        if card not in self._cards:
            return
        index = self._cards.index(card)
        self._cards.pop(index)
        if 0 <= index < len(self.attachments):
            self.attachments.pop(index)
        card.setParent(None)
        card.deleteLater()
        self.attach_scroll.setVisible(bool(self.attachments))
        self._apply_size()

    def _on_accept(self):
        if not self.text_edit.toPlainText().strip() and not self.attachments:
            self.text_edit.setFocus()
            return
        self.accept()

    def get_result(self) -> tuple[str, list[str]]:
        return self.text_edit.toPlainText().strip(), list(self.attachments)

    def _apply_size(self):
        height = self.BASE_HEIGHT + (self.ATTACHMENTS_HEIGHT if self.attachments else 0)
        self.setFixedSize(self.DIALOG_WIDTH, height)
        self._frame.setFixedSize(self.DIALOG_WIDTH - 20, height - 20)
