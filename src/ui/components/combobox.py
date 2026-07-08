from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QPoint, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPolygon, QColor


COMBO_STYLE = """
QComboBox {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    padding-right: 35px;
    font-size: 10pt;
    font-family: "Segoe UI";
}
QComboBox:hover {
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
}
QComboBox::drop-down { border: none; width: 0px; }
QComboBox::down-arrow { image: none; }
QComboBox QAbstractItemView {
    background-color: rgba(30, 30, 35, 0.98);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    selection-background-color: rgba(88, 101, 242, 0.3);
    color: rgba(255, 255, 255, 0.9);
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item { padding: 6px 10px; border-radius: 4px; }
QComboBox QAbstractItemView::item:hover { background-color: rgba(255, 255, 255, 0.08); }
"""


class AnimatedComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rotation = 0
        self._animation = QPropertyAnimation(self, b"rotation")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setStyleSheet(COMBO_STYLE)
        self.setFixedHeight(38)

    def showPopup(self):
        super().showPopup()
        self._animate(180)

    def hidePopup(self):
        super().hidePopup()
        self._animate(0)

    def _animate(self, end_value: int):
        self._animation.stop()
        self._animation.setStartValue(self._rotation)
        self._animation.setEndValue(end_value)
        self._animation.start()

    def get_rotation(self) -> int:
        return self._rotation

    def set_rotation(self, value: int):
        self._rotation = value
        self.update()

    rotation = pyqtProperty(int, get_rotation, set_rotation)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        arrow_x = self.width() - 25
        arrow_y = self.height() // 2

        painter.translate(arrow_x, arrow_y)
        painter.rotate(self._rotation)
        painter.translate(-arrow_x, -arrow_y)

        painter.setBrush(QColor(255, 255, 255, 178))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygon([
            QPoint(arrow_x - 4, arrow_y - 2),
            QPoint(arrow_x + 4, arrow_y - 2),
            QPoint(arrow_x, arrow_y + 3),
        ]))
        painter.end()
