from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QRegion
from pathlib import Path
import av


class EmptyStateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_frame)
        self.video_enabled = True
        self.video_loaded = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(False)
        layout.addWidget(self.label)
    
    def load_video(self, video_path):
        try:
            container = av.open(str(video_path))
            stream = container.streams.video[0]
            fps = float(stream.average_rate)
            
            for frame in container.decode(video=0):
                img = frame.to_ndarray(format='rgb24')
                height, width, channels = img.shape
                bytes_per_line = 3 * width
                
                q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image.copy())
                
                scaled_pixmap = pixmap.scaled(
                    1100, 700,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                rounded_pixmap = self.round_pixmap(scaled_pixmap, 20)
                self.frames.append(rounded_pixmap)
            
            container.close()
            
            if self.frames:
                self.label.setPixmap(self.frames[0])
                interval = int(1000 / fps) if fps > 0 else 33
                self.timer.start(interval)
        except Exception:
            return
    
    def show_next_frame(self):
        if not self.frames:
            return
        
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.label.setPixmap(self.frames[self.current_frame])
    
    def stop(self):
        self.timer.stop()
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self.video_loaded and self.video_enabled:
            self.force_load()
    
    def force_load(self):
        if not self.video_loaded and self.video_enabled:
            assets_path = Path(__file__).parent.parent.parent.parent / "assets"
            video_path = assets_path / "91913-631504055.mp4"
            if video_path.exists():
                self.load_video(video_path)
                self.video_loaded = True
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_rounded_mask()
    
    def apply_rounded_mask(self):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, 18, 18)
        
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    
    def set_video_enabled(self, enabled):
        self.video_enabled = enabled
        if not enabled:
            self.timer.stop()
            self.frames.clear()
            self.label.clear()
            self.label.hide()
            self.video_loaded = False
        else:
            self.label.show()
            if not self.video_loaded:
                self.force_load()
    
    def round_pixmap(self, pixmap, radius):
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        path = QPainterPath()
        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        path.addRoundedRect(rect, 18, 18)
        
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return rounded
