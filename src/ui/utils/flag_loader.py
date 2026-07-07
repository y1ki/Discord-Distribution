from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
import urllib.request
from pathlib import Path


def country_code_to_flag(country_code: str) -> str:
    if not country_code or len(country_code) != 2:
        return "🏳️"
    
    country_code = country_code.upper()
    if country_code == "UN":
        return "🏳️"
    
    offset = 127397
    flag = chr(ord(country_code[0]) + offset) + chr(ord(country_code[1]) + offset)
    return flag


class FlagLoader:
    _cache = {}
    _flags_dir = Path(__file__).parent.parent.parent / "resources" / "icons" / "flags"
    
    @classmethod
    def get_flag_label(cls, country_code: str) -> QLabel:
        label = QLabel()
        label.setFixedSize(20, 15)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if not country_code or len(country_code) != 2 or country_code == "UN":
            label.setText("🏳️")
            label.setStyleSheet("font-size: 12pt;")
            label.setToolTip("Unknown")
            return label
        
        country_code = country_code.upper()
        
        if country_code in cls._cache:
            label.setPixmap(cls._cache[country_code])
            label.setToolTip(country_code)
            return label
        
        cls._flags_dir.mkdir(parents=True, exist_ok=True)
        flag_path = cls._flags_dir / f"{country_code.lower()}.png"
        
        if not flag_path.exists():
            try:
                urllib.request.urlretrieve(
                    f"https://flagcdn.com/20x15/{country_code.lower()}.png",
                    flag_path
                )
            except:
                label.setText("🏳️")
                label.setStyleSheet("font-size: 12pt;")
                label.setToolTip("Unknown")
                return label
        
        pixmap = QPixmap(str(flag_path))
        if not pixmap.isNull():
            cls._cache[country_code] = pixmap
            label.setPixmap(pixmap)
            label.setToolTip(country_code)
        else:
            label.setText("🏳️")
            label.setStyleSheet("font-size: 12pt;")
            label.setToolTip("Unknown")
        
        return label


