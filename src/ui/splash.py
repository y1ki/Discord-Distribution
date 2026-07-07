from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QObject, QElapsedTimer
from PyQt6.QtGui import QPixmap, QImage
from pathlib import Path
import av
import numpy as np


class VideoLoader(QObject):
    metadata_ready = pyqtSignal(float)
    frame_ready = pyqtSignal(QImage)
    finished = pyqtSignal(float)
    failed = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            container = av.open(str(self.video_path))
            stream = container.streams.video[0]
            fps = float(stream.average_rate) if stream.average_rate else 60.0
            self.metadata_ready.emit(fps)

            for frame in container.decode(video=0):
                rgb = frame.to_ndarray(format='rgb24')
                rgb = np.ascontiguousarray(rgb)
                h, w = rgb.shape[:2]

                r = rgb[:, :, 0].astype(np.uint16)
                g = rgb[:, :, 1].astype(np.uint16)
                b = rgb[:, :, 2].astype(np.uint16)
                brightness = (r + g + b) // 3

                alpha = np.zeros((h, w), dtype=np.uint8)
                mask = brightness > 25
                alpha[mask] = 255
                edge = (brightness > 25) & (brightness <= 40)
                alpha[edge] = ((brightness[edge] - 25) * 17).astype(np.uint8)

                rgba = np.dstack([rgb, alpha])
                rgba = np.ascontiguousarray(rgba)
                q_image = QImage(rgba.data, w, h, 4 * w, QImage.Format.Format_RGBA8888)
                self.frame_ready.emit(q_image.copy())

            container.close()
            self.finished.emit(fps)
        except Exception as e:
            self.failed.emit(str(e))


class SplashScreen(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.frames = []
        self.current_frame = 0
        self.video_fps = 60.0
        self.frame_interval_ms = 16
        self.video_duration_ms = 0
        self.loading_finished = False
        self.video_started = False
        self.displayed_frame = -1
        self.elapsed_timer = QElapsedTimer()
        self.loader_thread = None
        self.loader = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_frame)
        
        self.setup_ui()
        
    def setup_ui(self):
        assets_path = Path(__file__).parent.parent.parent / "assets"
        
        mov_path = assets_path / "Comp 1_2.mp4"
        
        if mov_path.exists():
            self.setup_video_frames(mov_path)
        else:
            self.setup_fallback()
            
    def setup_video_frames(self, video_path):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.loader_thread = QThread(self)
        self.loader = VideoLoader(video_path)
        self.loader.moveToThread(self.loader_thread)

        self.loader_thread.started.connect(self.loader.run)
        self.loader.metadata_ready.connect(self.on_video_metadata)
        self.loader.frame_ready.connect(self.on_frame_ready)
        self.loader.finished.connect(self.on_video_loaded)
        self.loader.failed.connect(self.on_video_failed)
        self.loader.finished.connect(self.loader_thread.quit)
        self.loader.failed.connect(self.loader_thread.quit)
        self.loader_thread.finished.connect(self.loader.deleteLater)
        self.loader_thread.start()

    def on_video_metadata(self, fps):
        self.video_fps = fps if fps > 0 else 60.0
        self.frame_interval_ms = max(1, int(1000 / self.video_fps))

    def on_frame_ready(self, q_image):
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            max(1, int(pixmap.width() / 2.5)),
            max(1, int(pixmap.height() / 2.5)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.frames.append(scaled_pixmap)

        if not self.video_started:
            self.video_started = True
            self.setFixedSize(self.frames[0].size())
            self.label.setFixedSize(self.frames[0].size())
            self.label.setPixmap(self.frames[0])
            self.displayed_frame = 0

            screen = self.screen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)

            self.elapsed_timer.start()
            self.timer.start(max(1, self.frame_interval_ms // 2))

    def on_video_loaded(self, fps):
        self.video_fps = fps
        self.frame_interval_ms = max(1, int(1000 / self.video_fps))
        self.loading_finished = True
        self.video_duration_ms = max(self.video_duration_ms, len(self.frames) * self.frame_interval_ms)

    def on_video_failed(self, error):
        self.setup_fallback()
            
    def show_next_frame(self):
        if not self.video_started or not self.frames:
            return

        target_frame = self.elapsed_timer.elapsed() // self.frame_interval_ms
        if target_frame >= len(self.frames):
            target_frame = len(self.frames) - 1

        if target_frame != self.displayed_frame:
            self.label.setPixmap(self.frames[target_frame])
            self.displayed_frame = target_frame

        if self.loading_finished and self.displayed_frame >= len(self.frames) - 1:
            self.timer.stop()
            QTimer.singleShot(100, self.on_finished)
    
    def on_finished(self):
        self.finished.emit()
        self.close()
            
    def setup_fallback(self):
        self.loading_finished = True
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #0a0a0a;")
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Anonymous&Discord")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #e0e0e0; font-size: 48px; font-weight: bold;")
        layout.addWidget(label)
