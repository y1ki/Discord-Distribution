from pathlib import Path
from PyQt6.QtWidgets import QPushButton, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QFont, QPixmap, QPainter, QIcon
from PyQt6.QtSvg import QSvgRenderer


ICONS_DIR = Path(__file__).resolve().parents[3] / "assets" / "icons"

DIALOG_FRAME_STYLE = """
QLabel#dialogFrame, QWidget#dialogFrame {
    background-color: rgba(20, 20, 23, 252);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.9);
}
QPushButton:hover { background-color: rgba(255, 255, 255, 0.12); }
QPushButton:pressed { background-color: rgba(255, 255, 255, 0.06); }
"""

PRIMARY_BUTTON_STYLE = """
QPushButton {
    background-color: rgba(88, 101, 242, 0.9);
    border: none;
    border-radius: 8px;
    color: #ffffff;
}
QPushButton:hover { background-color: rgba(88, 101, 242, 1.0); }
QPushButton:pressed { background-color: rgba(88, 101, 242, 0.8); }
"""

CLOSE_BUTTON_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
QPushButton:hover { background-color: rgba(255, 255, 255, 0.08); }
QPushButton:pressed { background-color: rgba(255, 255, 255, 0.12); }
"""


def render_svg_icon(name: str, color: str = "#999999", size: int = 16) -> QIcon:
    svg = (ICONS_DIR / name).read_text()
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def make_close_button(on_click) -> QPushButton:
    btn = QPushButton()
    btn.setFixedSize(28, 28)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(CLOSE_BUTTON_STYLE)
    icon = render_svg_icon("close.svg")
    btn.setIcon(icon)
    btn.setIconSize(icon.actualSize(btn.size()))
    btn.clicked.connect(on_click)
    return btn


def make_dialog_button(text: str, primary: bool = False, width: int = 90) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(34)
    btn.setFixedWidth(width)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
    btn.setStyleSheet(PRIMARY_BUTTON_STYLE if primary else SECONDARY_BUTTON_STYLE)
    return btn


def make_dialog_header(title: str, on_close) -> QWidget:
    header = QWidget()
    header.setFixedHeight(50)
    header.setStyleSheet("background: transparent; border: none;")
    layout = QHBoxLayout(header)
    layout.setContentsMargins(20, 14, 14, 0)
    layout.setSpacing(0)

    title_label = QLabel(title)
    title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
    title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent; border: none;")
    layout.addWidget(title_label)
    layout.addStretch()
    layout.addWidget(make_close_button(on_close))
    return header


def make_separator() -> QLabel:
    sep = QLabel()
    sep.setFixedHeight(1)
    sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); border: none;")
    return sep
