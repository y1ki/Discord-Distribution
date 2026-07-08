from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = False
        self._circle_position = 3
        
        self.animation = QPropertyAnimation(self, b"circle_position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(200)
    
    def is_checked(self):
        return self._checked
    
    def set_checked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self._animate()
    
    def _animate(self):
        if self._checked:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(25)
        else:
            self.animation.setStartValue(self._circle_position)
            self.animation.setEndValue(3)
        self.animation.start()
    
    def get_circle_position(self):
        return self._circle_position
    
    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()
    
    circle_position = pyqtProperty(int, get_circle_position, set_circle_position)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self._animate()
            self.toggled.emit(self._checked)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._checked:
            painter.setBrush(QColor(40, 45, 52, int(0.95 * 255)))
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.setBrush(QColor(60, 60, 65))
            painter.setPen(Qt.PenStyle.NoPen)
        
        painter.drawRoundedRect(0, 0, 48, 26, 13, 13)
        
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(int(self._circle_position), 3, 20, 20)
