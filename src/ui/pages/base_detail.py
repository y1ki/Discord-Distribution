from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from src.ui.components.notification import NotificationWidget
from src.core.database import Database


class BaseDetailPage(QWidget):
    stat_card_clicked = pyqtSignal(str)
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.all_accounts = []
        self.current_page = 0
        self.accounts_per_page = 7
        self.db = Database()
        self.notification = None
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self.notification:
            self.notification = NotificationWidget(self.window())
    
    def setup_ui(self):
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def load_data(self):
        raise NotImplementedError("Subclasses must implement load_data()")
    
    def _truncate_text(self, text, max_length=25):
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def _update_pagination(self):
        total_pages = (len(self.all_accounts) + self.accounts_per_page - 1) // self.accounts_per_page
        self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
        self.prev_page_btn.setEnabled(self.current_page > 0)
        self.next_page_btn.setEnabled(self.current_page < total_pages - 1)
    
    def _prev_page(self):
        if self.current_page > 0:
            self._save_current_page_state()
            self.current_page -= 1
            self._load_page()
    
    def _next_page(self):
        total_pages = (len(self.all_accounts) + self.accounts_per_page - 1) // self.accounts_per_page
        if self.current_page < total_pages - 1:
            self._save_current_page_state()
            self.current_page += 1
            self._load_page()
    
    def _save_current_page_state(self):
        table = getattr(self, "accounts_table", None) or getattr(self, "proxy_table", None)
        if not table:
            return

        start_idx = self.current_page * self.accounts_per_page
        for row in range(table.rowCount()):
            item_idx = start_idx + row
            if item_idx < len(self.all_accounts):
                checkbox_item = table.item(row, 0)
                if checkbox_item:
                    self.all_accounts[item_idx]["checked"] = checkbox_item.data(Qt.ItemDataRole.UserRole)
    
    def _load_page(self):
        raise NotImplementedError("Subclasses must implement _load_page()")
