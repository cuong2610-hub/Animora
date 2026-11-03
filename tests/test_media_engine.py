import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication
from core.engine import Engine
from core.video_animation import VideoAnimation
from media.loader import load_animation, load_sprite_sheet


class MediaEngineChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_apng_frames_and_sprite_sheet_slices(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            frames = [Image.new("RGBA", (16, 16), color) for color in ("red", "blue")]
            apng = directory / "moving.apng"
            frames[0].save(apng, save_all=True, append_images=frames[1:], duration=[100, 150], loop=0, format="PNG")
            loaded, durations, fps = load_animation(apng)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(durations, [100, 150])
            self.assertGreater(fps, 0)

            sheet = Image.new("RGBA", (20, 10))
            sheet.paste("red", (0, 0, 10, 10))
            sheet.paste("blue", (10, 0, 20, 10))
            sheet_path = directory / "sheet.png"
            sheet.save(sheet_path)
            slices, delays, _ = load_sprite_sheet(sheet_path, 2, 1, fps=10)
            self.assertEqual([frame.size().width() for frame in slices], [10, 10])
            self.assertEqual(delays, [100, 100])
            with self.assertRaises(ValueError):
                load_sprite_sheet(sheet_path, 3, 1)

    def test_newer_load_cancels_stale_async_result(self):
        with tempfile.TemporaryDirectory() as directory:
            replacement = Path(directory) / "replacement.png"
            Image.new("RGBA", (2, 2), "green").save(replacement)
            engine = Engine()
            engine.load_async(Path(__file__).resolve().parents[1] / "assets" / "animations" / "demo.gif")
            engine.load(replacement)
            loop = QEventLoop()
            QTimer.singleShot(200, loop.quit)
            loop.exec()
            self.assertEqual(engine.path, str(replacement.resolve()))
            self.assertEqual(len(engine.animation.frames), 1)
            engine.unload()

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is needed to create a local video fixture")
    def test_qt_multimedia_decodes_video_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "sample.mp4"
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=purple:s=64x64:d=2:r=12", "-an", "-c:v", "mpeg4", "-pix_fmt", "yuv420p", str(video)],
                check=True,
                capture_output=True,
            )
            engine = Engine()
            engine.load(video)
            self.assertIsInstance(engine.animation, VideoAnimation)
            loop = QEventLoop()
            engine.frame_changed.connect(loop.quit)
            QTimer.singleShot(5000, loop.quit)
            engine.play()
            loop.exec()
            self.assertIsNotNone(engine.current_frame)
            self.assertFalse(engine.current_frame.isNull())
            engine.unload()


if __name__ == "__main__":
    unittest.main()
