from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QPixmap, QFont


class CheckBoxDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        checked = index.data(Qt.ItemDataRole.UserRole)
        
        rect = option.rect
        cb_size = 16
        cb_x = rect.x() + (rect.width() - cb_size) // 2
        cb_y = rect.y() + (rect.height() - cb_size) // 2
        cb_rect = QRect(cb_x, cb_y, cb_size, cb_size)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRoundedRect(cb_rect, 3, 3)
        
        if checked:
            painter.setBrush(QColor("#2563eb"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(cb_rect, 3, 3)
            
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawLine(cb_x + 4, cb_y + 8, cb_x + 7, cb_y + 11)
            painter.drawLine(cb_x + 7, cb_y + 11, cb_x + 12, cb_y + 5)


class AvatarDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        center_x = rect.x() + rect.width() // 2
        center_y = rect.y() + rect.height() // 2
        radius = 16
        
        avatar_data = index.data(Qt.ItemDataRole.UserRole)
        
        path = QPainterPath()
        path.addEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.setClipPath(path)
        
        if avatar_data and isinstance(avatar_data, QPixmap):
            scaled = avatar_data.scaled(
                radius * 2, radius * 2,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(center_x - radius, center_y - radius, scaled)
        else:
            gradient_colors = [
                "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"
            ]
            name = index.data(Qt.ItemDataRole.DisplayRole) or ""
            color_index = sum(ord(c) for c in name) % len(gradient_colors)
            painter.setBrush(QBrush(QColor(gradient_colors[color_index])))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            
            painter.setClipping(False)
            initials = "".join([word[0].upper() for word in name.split()[:2]]) if name else "?"
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)

    def sizeHint(self, option: QStyleOptionViewItem, index):
        return QSize(60, 56)
