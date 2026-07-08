from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QByteArray, QPoint
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont, QPainter
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path


class SidebarButton(QPushButton):
    def __init__(self, icon_path, tooltip_text, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.tooltip_text = tooltip_text
        self.setFixedSize(38, 38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("active", False)
        
        self.svg_data = Path(icon_path).read_text()
        self._update_icon(False)
        self.setIconSize(QSize(20, 20))
        
        self.tooltip_label = None
    
    def _create_colored_icon(self, color):
        colored_svg = self.svg_data.replace('stroke="#606060"', f'stroke="{color}"')
        colored_svg = colored_svg.replace('stroke="#8E8E93"', f'stroke="{color}"')
        
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pixmap = QPixmap(QSize(20, 20))
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def _update_icon(self, active):
        color = "#ffffff" if active else "#8E8E93"
        self.setIcon(self._create_colored_icon(color))
    
    def set_active(self, active):
        self.setProperty("active", active)
        self._update_icon(active)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def enterEvent(self, event):
        super().enterEvent(event)
        self.show_tooltip()
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hide_tooltip()
    
    def show_tooltip(self):
        if not self.tooltip_label:
            self.tooltip_label = QLabel(self.tooltip_text, self.window())
            self.tooltip_label.setObjectName("sidebar_tooltip")
            self.tooltip_label.setFont(QFont("Segoe UI", 10))
            self.tooltip_label.setStyleSheet("""
                QLabel#sidebar_tooltip {
                    background-color: rgba(20, 20, 25, 0.95);
                    color: #ffffff;
                    padding: 9px 16px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            self.tooltip_label.adjustSize()
        
        btn_pos = self.mapTo(self.window(), QPoint(0, 0))
        tooltip_x = btn_pos.x() + self.width() + 12
        tooltip_y = btn_pos.y() + (self.height() - self.tooltip_label.height()) // 2
        
        self.tooltip_label.move(tooltip_x, tooltip_y)
        self.tooltip_label.show()
    
    def hide_tooltip(self):
        if self.tooltip_label:
            self.tooltip_label.hide()


class Sidebar(QWidget):
    page_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.current_index = 0
        self.buttons = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedWidth(68)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        container = QWidget()
        container.setObjectName("sidebar_container")
        container.setFixedWidth(54)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 120))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 9, 8, 9)
        container_layout.setSpacing(5)
        
        icons_dir = Path(__file__).parent.parent.parent.parent / "assets" / "icons"
        icon_data = [
            ("accounts.svg", "Аккаунты"),
            ("actions.svg", "Действие"),
            ("settings.svg", "Настройки")
        ]
        
        for icon_file, tooltip in icon_data:
            icon_path = icons_dir / icon_file
            btn = SidebarButton(icon_path, tooltip)
            btn.clicked.connect(lambda checked, idx=len(self.buttons): self.on_button_clicked(idx))
            self.buttons.append(btn)
            container_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.buttons[0].set_active(True)
    
    def on_button_clicked(self, index):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index)
        
        self.current_index = index
        self.page_changed.emit(index)
    
    def set_active_button(self, index):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index if index >= 0 else False)
        if index >= 0:
            self.current_index = index
