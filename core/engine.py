from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QPixmap

from core.animation import Animation
from core.video_animation import VideoAnimation
from media.loader import load_animation, load_animation_images, load_sprite_sheet


VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}
IMAGE_EXTENSIONS = {".apng", ".gif", ".png", ".webp"}
IMAGE_POOL = QThreadPool()
IMAGE_POOL.setMaxThreadCount(2)  # ponytail: two decoders limit peak RAM; increase only if bulk imports need throughput.


class _LoadSignals(QObject):
    completed = Signal(int, str, object, object, str)


class _ImageLoadTask(QRunnable):
    def __init__(self, token, path):
        super().__init__()
        self.token = token
        self.path = path
        self.signals = _LoadSignals()

    def run(self):
        try:
            frames, durations, fps = load_animation_images(self.path)
            self.signals.completed.emit(self.token, self.path, frames, durations, "")
        except Exception as error:
            self.signals.completed.emit(self.token, self.path, None, None, str(error))


class Engine(QObject):
    animation_loaded = Signal(str)
    frame_changed = Signal(QPixmap)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        self.current_frame = None
        self.path = None
        self._loop = True
        self._fps = None
        self._load_generation = 0
        self.is_loading = False
        self._load_tasks = {}

    def _replace_animation(self, animation, path):
        if self.animation:
            if isinstance(self.animation, VideoAnimation):
                self.animation.unload()
            else:
                self.animation.stop()
            self.animation.deleteLater()
        self.animation = animation
        self.path = str(path)
        self.is_loading = False
        self.current_frame = None
        animation.loop = self._loop
        if isinstance(animation, VideoAnimation):
            animation.set_fps(self._fps or 24)
        elif self._fps:
            animation.durations = [max(1, round(1000 / self._fps))] * len(animation.base_durations)
        animation.frame_changed.connect(self._on_frame)
        if isinstance(animation, VideoAnimation):
            animation.error.connect(self.error)
        elif animation.frames:
            self._on_frame(animation.frames[0])
        self.animation_loaded.emit(self.path)

    def _on_frame(self, frame):
        self.current_frame = frame
        self.frame_changed.emit(frame)

    def load(self, path):
        self._load_generation += 1
        self.is_loading = False
        path = Path(path).resolve()
        suffix = path.suffix.lower()
        if suffix in VIDEO_EXTENSIONS:
            if not path.is_file():
                raise FileNotFoundError(path)
            animation = VideoAnimation(self)
            animation.load(path)
        elif suffix in IMAGE_EXTENSIONS:
            frames, durations, _fps = load_animation(path)
            if not frames:
                raise ValueError("Không tìm thấy frame animation.")
            animation = Animation(self)
            animation.load_frames(frames, loop=True, durations=durations)
        else:
            raise ValueError(f"Định dạng không được hỗ trợ: {suffix or path.name}")
        self._replace_animation(animation, path)

    def load_async(self, path):
        path = Path(path).resolve()
        suffix = path.suffix.lower()
        self._load_generation += 1
        token = self._load_generation
        self.is_loading = False
        self.pause()
        if suffix in VIDEO_EXTENSIONS:
            self.load(path)
            self.play()
            return
        if suffix not in IMAGE_EXTENSIONS:
            self.error.emit(f"Định dạng không được hỗ trợ: {suffix or path.name}")
            return
        self.is_loading = True
        task = _ImageLoadTask(token, str(path))
        self._load_tasks[token] = task
        task.signals.completed.connect(self._finish_image_load)
        IMAGE_POOL.start(task)

    def _finish_image_load(self, token, path, images, durations, error):
        self._load_tasks.pop(token, None)
        if token != self._load_generation:
            return
        self.is_loading = False
        if error:
            self.error.emit(error)
            return
        frames = [QPixmap.fromImage(image) for image in images]
        images.clear()
        if not frames:
            self.error.emit("Không tìm thấy frame animation.")
            return
        animation = Animation(self)
        animation.load_frames(frames, durations=durations)
        self._replace_animation(animation, path)
        self.play()

    def load_sprite_sheet(self, path, columns, rows, fps=12):
        self._load_generation += 1
        self.is_loading = False
        frames, durations, _fps = load_sprite_sheet(path, columns, rows, fps)
        animation = Animation(self)
        animation.load_frames(frames, loop=True, durations=durations)
        self._fps = fps
        self._replace_animation(animation, path)

    def play(self):
        if self.animation:
            self.animation.play()

    def pause(self):
        if self.animation:
            self.animation.pause()

    def stop(self):
        if self.animation:
            self.animation.stop()

    def unload(self):
        self._load_generation += 1
        self.is_loading = False
        if not self.animation:
            return
        if isinstance(self.animation, VideoAnimation):
            self.animation.unload()
        else:
            self.animation.stop()
        self.animation.deleteLater()
        self.animation = None
        self.current_frame = None

    def set_loop(self, enabled):
        self._loop = bool(enabled)
        if self.animation:
            self.animation.loop = self._loop

    def set_fps(self, fps):
        self._fps = max(1, min(60, int(fps)))
        if isinstance(self.animation, VideoAnimation):
            self.animation.set_fps(self._fps)
        elif self.animation and self.animation.base_durations:
            duration = max(1, round(1000 / self._fps))
            self.animation.durations = [duration] * len(self.animation.base_durations)
            if self.animation.timer.isActive():
                self.animation.play()

    def is_playing(self):
        if isinstance(self.animation, VideoAnimation):
            return self.animation.is_playing()
        return bool(self.animation and self.animation.timer.isActive())
