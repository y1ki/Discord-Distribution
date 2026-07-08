DARK_THEME = """
QMainWindow {
    background-color: #0B0B0D;
}

QWidget#content {
    background-color: #0B0B0D;
}

QLabel {
    color: #ffffff;
}
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: transparent;
}

QWidget#sidebar_container {
    background-color: rgba(25, 25, 28, 0.8);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QWidget#sidebar QPushButton {
    background-color: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    border-radius: 12px;
}

QWidget#sidebar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

QWidget#sidebar QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.1);
}

QWidget#sidebar QPushButton[active="true"] {
    background-color: rgba(40, 45, 52, 0.95);
}

QWidget#sidebar QPushButton[active="true"]:hover {
    background-color: rgba(45, 50, 57, 0.95);
}
"""

BUTTON_PRIMARY = """
QPushButton {
    background-color: rgba(59, 130, 246, 0.9);
    color: #ffffff;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 10px;
    padding: 0 22px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(37, 99, 235, 0.95);
    border-color: rgba(37, 99, 235, 0.5);
}
QPushButton:pressed {
    background-color: rgba(29, 78, 216, 1);
}
"""

BUTTON_DANGER = """
QPushButton {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 0 22px;
}
QPushButton:hover   { background-color: #b91c1c; }
QPushButton:pressed { background-color: #991b1b; }
"""

BUTTON_SECONDARY = """
QPushButton {
    background-color: rgba(25, 25, 28, 0.8);
    color: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 0 18px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(35, 35, 38, 0.9);
    color: rgba(255, 255, 255, 0.95);
    border-color: rgba(255, 255, 255, 0.15);
}
QPushButton:pressed {
    background-color: rgba(20, 20, 23, 0.95);
}
"""

PROGRESS_BAR = """
QProgressBar {
    background-color: rgba(15, 15, 17, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}
QProgressBar::chunk {
    background-color: rgba(59, 130, 246, 0.9);
    border-radius: 4px;
}
"""

LOG_TERMINAL = """
QTextEdit {
    background-color: transparent;
    color: #3d9970;
    border: none;
    padding: 0;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
}
QScrollBar::handle:vertical {
    background-color: #222222;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #2e2e2e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

LOG_COLORS = {
    "green": "#2ecc71",
    "red": "#e74c3c",
    "blue": "#3498db",
    "yellow": "#f39c12"
}

TABLE_STYLE = """
QTableWidget {
    background-color: rgba(25, 25, 28, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    gridline-color: transparent;
}
QTableWidget::item {
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}
QTableWidget::item:selected {
    background-color: transparent;
}
QHeaderView::section {
    background-color: rgba(25, 25, 28, 0.8);
    color: rgba(255, 255, 255, 0.4);
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-weight: 600;
    font-size: 9px;
    text-transform: uppercase;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: rgba(255, 255, 255, 0.15);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""
