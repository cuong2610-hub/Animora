from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap


class Animation(QObject):
    frame_changed = Signal(QPixmap)
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.durations = []
        self.base_durations = []
        self.index = 0
        self.loop = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def load_frames(self, frames, fps=24, loop=True, durations=None):
        self.stop()
        self.frames = list(frames)
        self.loop = bool(loop)
        default_duration = max(1, round(1000 / max(1, fps)))
        self.durations = list(durations or [default_duration] * len(self.frames))
        self.durations = [max(1, int(value)) for value in self.durations]
        self.base_durations = self.durations.copy()
        self.index = 0
        if self.frames:
            self.frame_changed.emit(self.frames[0])

    def play(self):
        if self.frames:
            self.timer.start(self.durations[self.index])

    def pause(self):
        self.timer.stop()

    def stop(self):
        self.timer.stop()
        self.index = 0
        if self.frames:
            self.frame_changed.emit(self.frames[0])

    def next_frame(self):
        if not self.frames:
            return
        if self.index + 1 >= len(self.frames):
            if not self.loop:
                self.timer.stop()
                self.index = len(self.frames) - 1
                self.finished.emit()
                return
            self.index = 0
        else:
            self.index += 1
        self.frame_changed.emit(self.frames[self.index])
        self.timer.start(self.durations[self.index])
