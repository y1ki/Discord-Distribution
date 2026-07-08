from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath


class CustomPaginationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setFixedSize(160, 50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        w = self.width()
        h = self.height()

        notch_width = 80
        notch_height = 6
        corner_radius = 14

        start_x = (w - notch_width) / 2

        path.moveTo(corner_radius, 0)
        path.lineTo(start_x - 10, 0)
        path.lineTo(start_x, notch_height)
        path.lineTo(start_x + notch_width, notch_height)
        path.lineTo(start_x + notch_width + 10, 0)
        path.lineTo(w - corner_radius, 0)
        path.arcTo(QRectF(w - corner_radius * 2, 0, corner_radius * 2, corner_radius * 2), 90, -90)
        path.lineTo(w, h - corner_radius)
        path.arcTo(QRectF(w - corner_radius * 2, h - corner_radius * 2, corner_radius * 2, corner_radius * 2), 0, -90)
        path.lineTo(corner_radius, h)
        path.arcTo(QRectF(0, h - corner_radius * 2, corner_radius * 2, corner_radius * 2), 270, -90)
        path.lineTo(0, corner_radius)
        path.arcTo(QRectF(0, 0, corner_radius * 2, corner_radius * 2), 180, -90)
        path.closeSubpath()

        painter.fillPath(path, QColor(15, 15, 17, 242))
        painter.setPen(QColor(255, 255, 255, 20))
        painter.drawPath(path)
