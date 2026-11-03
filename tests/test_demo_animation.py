import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image, ImageSequence
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from ui.main_window import DesktopWindow, MainWindow
from storage.library import LibraryStore


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "assets" / "animations" / "demo.gif"


class DemoAnimationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_demo_is_transparent_and_animates(self):
        with Image.open(DEMO) as image:
            self.assertEqual(image.format, "GIF")
            self.assertEqual(image.info.get("loop"), 0)
            self.assertIn("transparency", image.info)
            frames = list(ImageSequence.Iterator(image))
            self.assertGreaterEqual(len(frames), 10)
            self.assertTrue(all(frame.info.get("duration", 0) >= 80 for frame in frames))
            self.assertEqual(frames[0].convert("RGBA").getpixel((0, 0))[3], 0)
        with Image.open(ROOT / "assets" / "animations" / "preview.png") as preview:
            self.assertEqual(preview.format, "PNG")

        window = DesktopWindow(DEMO, fps=24)
        window.show()
        loaded = QEventLoop()
        window.engine.animation_loaded.connect(loaded.quit)
        QTimer.singleShot(3000, loaded.quit)
        loaded.exec()
        first_frame = window.engine.animation.index
        loop = QEventLoop()
        QTimer.singleShot(180, loop.quit)
        loop.exec()
        self.assertTrue(window.engine.animation.timer.isActive())
        self.assertNotEqual(window.engine.animation.index, first_frame)
        window.close()

        click_through = DesktopWindow(DEMO, click_through=True)
        self.assertTrue(click_through.windowFlags() & Qt.WindowType.WindowTransparentForInput)
        click_through.close()

    def test_first_launch_adds_demo_and_preserves_imported_animation(self):
        with tempfile.TemporaryDirectory() as directory:
            imported = Path(directory) / "my-animation.png"
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(imported)
            initial = {
                "items": [str(imported)], "windows": [], "always_on_top": True,
                "engine_paused": False, "loop": True, "fps": 24,
            }
            store = LibraryStore(Path(directory) / "test-library.sqlite3")
            with patch("ui.main_window.load_config", return_value=initial), patch("ui.main_window.save_config"), patch("ui.main_window.LibraryStore", return_value=store):
                window = MainWindow()
                self.assertIn(str(imported), window.items)
                self.assertIn(str(DEMO), window.items)
                self.assertEqual(window.library.count(), 2)
                window.close()
            store.close()


if __name__ == "__main__":
    unittest.main()
