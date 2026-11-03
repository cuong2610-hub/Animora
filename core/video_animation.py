from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink


class VideoAnimation(QObject):
    frame_changed = Signal(QPixmap)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.durations = []
        self.base_durations = []
        self.index = 0
        self._loop = True
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.audio.setMuted(True)
        self.player.setAudioOutput(self.audio)
        self.video_sink = QVideoSink(self)
        self.player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self._show_frame)
        self.player.errorOccurred.connect(self._report_error)
        self.loop = True

    def load(self, path):
        path = Path(path).resolve()
        self.player.setSource(QUrl.fromLocalFile(str(path)))

    def _show_frame(self, frame):
        image = frame.toImage()
        if not image.isNull():
            self.frame_changed.emit(QPixmap.fromImage(image))

    def _report_error(self, _error, message):
        if message:
            self.error.emit(message)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, enabled):
        self._loop = bool(enabled)
        self.player.setLoops(QMediaPlayer.Loops.Infinite if self._loop else QMediaPlayer.Loops.Once)

    def set_fps(self, fps):
        # Qt's video API accepts playback rate, so use 24 FPS as the speed baseline.
        self.player.setPlaybackRate(max(0.25, min(2.5, fps / 24)))

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def unload(self):
        self.player.stop()
        self.player.setSource(QUrl())

    def is_playing(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
