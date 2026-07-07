from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QByteArray, QRectF, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QLinearGradient, QCursor
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path


class StatCard(QWidget):
    clicked = pyqtSignal(str)
    
    def __init__(self, icon_path, title, count, parent=None):
        super().__init__(parent)
        self.title = title
        self.count = count
        self.icon_path = icon_path
        self.setFixedSize(250, 80)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setProperty("active", False)
        self.setProperty("hovered", False)
        self.setup_ui()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        
        notch_width = 170
        notch_height = 28
        radius = 40
        
        path.moveTo(radius, 0)
        path.lineTo(self.width() - notch_width, 0)
        path.lineTo(self.width() - notch_width, notch_height)
        path.lineTo(self.width(), notch_height)
        path.lineTo(self.width(), self.height() - radius)
        path.arcTo(QRectF(self.width() - radius * 2, self.height() - radius * 2, radius * 2, radius * 2), 0, -90)
        path.lineTo(radius, self.height())
        path.arcTo(QRectF(0, self.height() - radius * 2, radius * 2, radius * 2), 270, -90)
        path.lineTo(0, radius)
        path.arcTo(QRectF(0, 0, radius * 2, radius * 2), 180, -90)
        path.closeSubpath()
        
        if self.property("active"):
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(40, 45, 52, 242))
            gradient.setColorAt(1, QColor(45, 50, 57, 242))
            painter.fillPath(path, gradient)
            pen = QPen(QColor(255, 255, 255, 25), 1)
        elif self.property("hovered"):
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(35, 35, 38, 210))
            gradient.setColorAt(1, QColor(30, 30, 33, 210))
            painter.fillPath(path, gradient)
            pen = QPen(QColor(255, 255, 255, 20), 1)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(25, 25, 28, 200))
            gradient.setColorAt(1, QColor(20, 20, 23, 200))
            painter.fillPath(path, gradient)
            pen = QPen(QColor(255, 255, 255, 20), 1)
        
        painter.setPen(pen)
        painter.drawPath(path)
        
        super().paintEvent(event)
    
    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        icon_container = QWidget()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("background-color: transparent;")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(10, 15, 10, 15)
        icon_layout.setSpacing(6)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = icon_label
        self.update_icon()
        
        icon_label.setStyleSheet("background-color: transparent; border: none;")
        icon_layout.addWidget(icon_label)
        
        count_label = QLabel(str(self.count))
        count_label.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))
        self.count_label = count_label
        self.update_count_style()
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(count_label)
        
        main_layout.addWidget(icon_container)
        
        text_container = QWidget()
        text_container.setFixedWidth(170)
        text_container.setStyleSheet("background-color: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(8, 2, 8, 0)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 8))
        self.title_label = title_label
        self.update_title_style()
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        title_label.setWordWrap(False)
        text_layout.addWidget(title_label)
        
        main_layout.addWidget(text_container)
    
    def update_count(self, count):
        self.count = count
        self.count_label.setText(str(count))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.title)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.update()
        super().leaveEvent(event)
    
    def set_active(self, active):
        self.setProperty("active", active)
        self.update()
        self.update_icon()
        self.update_count_style()
        self.update_title_style()
    
    def update_icon(self):
        svg_data = Path(self.icon_path).read_text()
        color = "#ffffff" if self.property("active") else "#606060"
        colored_svg = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
        
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pixmap = QPixmap(28, 28)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        svg_painter = QPainter(pixmap)
        renderer.render(svg_painter)
        svg_painter.end()
        
        self.icon_label.setPixmap(pixmap)
    
    def update_count_style(self):
        color = "#ffffff" if self.property("active") else "#ffffff"
        self.count_label.setStyleSheet(f"color: {color}; background-color: transparent;")
    
    def update_title_style(self):
        color = "#ffffff" if self.property("active") else "#999999"
        self.title_label.setStyleSheet(f"background-color: transparent; color: {color}; padding: 0px; border: none;")


class StatsBar(QWidget):
    card_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        icons_dir = Path(__file__).parent.parent.parent.parent / "assets" / "icons"
        
        stats_data = [
            (str(icons_dir / "stats_active.svg"), "Активные аккаунты", 0),
            (str(icons_dir / "stats_temp_block.svg"), "Недостаточно прав", 0),
            (str(icons_dir / "stats_perm_block.svg"), "Мертвые аккаунты", 0),
            (str(icons_dir / "stats_proxy.svg"), "Прокси", 0)
        ]
        
        for icon_path, title, count in stats_data:
            card = StatCard(icon_path, title, count)
            card.clicked.connect(self.card_clicked.emit)
            layout.addWidget(card)
            self.cards.append(card)
        
        layout.addStretch()
    
    def update_card_count(self, title: str, count: int):
        for card in self.cards:
            if card.title == title:
                card.update_count(count)
                break
    
    def clear_active(self):
        for card in self.cards:
            card.set_active(False)
    
    def set_active_card(self, title: str):
        for card in self.cards:
            card.set_active(card.title == title)
