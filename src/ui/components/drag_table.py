from PyQt6.QtWidgets import QTableWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMouseEvent


class DragSelectTableBase(QTableWidget):
    def __init__(self, enable_copy_columns=None, parent=None):
        super().__init__(parent)
        self.drag_start_row = -1
        self.drag_start_col = -1
        self.last_drag_row = -1
        self.drag_target_state = False
        self.has_moved = False
        self.enable_copy_columns = enable_copy_columns or []
        self.non_drag_columns = []
        self.setMouseTracking(True)
        
        if self.enable_copy_columns:
            self.copy_tooltip = QLabel(self)
            self.copy_tooltip.setText("Скопировано!")
            self.copy_tooltip.setStyleSheet("""
                QLabel {
                    background-color: #2563eb;
                    color: #ffffff;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
            self.copy_tooltip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.copy_tooltip.hide()
            self.copy_tooltip.setFixedSize(100, 30)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            row = self.rowAt(event.pos().y())
            col = self.columnAt(event.pos().x())
            
            if col in self.enable_copy_columns and row >= 0:
                item = self.item(row, col)
                if item:
                    text = item.toolTip() or item.text()
                    clipboard = QApplication.clipboard()
                    clipboard.setText(text)
                    
                    item_rect = self.visualItemRect(item)
                    tooltip_x = item_rect.center().x() - self.copy_tooltip.width() // 2
                    tooltip_y = item_rect.center().y() - self.copy_tooltip.height() // 2
                    self.copy_tooltip.move(tooltip_x, tooltip_y)
                    self.copy_tooltip.show()
                    self.copy_tooltip.raise_()
                    
                    QTimer.singleShot(1000, self.copy_tooltip.hide)
                    
                event.accept()
                return
            
            if col in self.non_drag_columns:
                super().mousePressEvent(event)
                return
            
            if row >= 0:
                self.drag_start_row = row
                self.drag_start_col = col
                self.last_drag_row = row
                self.has_moved = False
                checkbox_item = self.item(row, 0)
                if checkbox_item:
                    current = checkbox_item.data(Qt.ItemDataRole.UserRole)
                    self.drag_target_state = not current
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        col = self.columnAt(event.pos().x())
        if col in self.enable_copy_columns:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_row >= 0 and self.drag_start_col not in self.non_drag_columns:
            row = self.rowAt(event.pos().y())
            if row >= 0:
                if not self.has_moved:
                    self.has_moved = True
                    checkbox_item = self.item(self.drag_start_row, 0)
                    if checkbox_item:
                        checkbox_item.setData(Qt.ItemDataRole.UserRole, self.drag_target_state)
                        self.viewport().update()
                
                if row != self.last_drag_row:
                    self.last_drag_row = row
                    checkbox_item = self.item(row, 0)
                    if checkbox_item:
                        checkbox_item.setData(Qt.ItemDataRole.UserRole, self.drag_target_state)
                        self.viewport().update()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.has_moved and self.drag_start_row >= 0 and self.drag_start_col not in self.non_drag_columns:
                checkbox_item = self.item(self.drag_start_row, 0)
                if checkbox_item:
                    checkbox_item.setData(Qt.ItemDataRole.UserRole, self.drag_target_state)
                    self.viewport().update()
            
            self.drag_start_row = -1
            self.drag_start_col = -1
            self.last_drag_row = -1
            self.has_moved = False
        super().mouseReleaseEvent(event)
