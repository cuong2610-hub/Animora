import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image, ImageSequence
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication
from core.editor import compose_layers, export_gif


class EditorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_layers_visibility_timeline_frames_and_transparent_export(self):
        red, red2, blue = QPixmap(16, 16), QPixmap(16, 16), QPixmap(16, 16)
        red.fill(Qt.GlobalColor.transparent)
        red2.fill(Qt.GlobalColor.transparent)
        blue.fill(Qt.GlobalColor.transparent)
        for pixmap, color, x in ((red, QColor("red"), 4), (red2, QColor("red"), 6), (blue, QColor("blue"), 4)):
            painter = QPainter(pixmap)
            painter.fillRect(x, 4, 6, 8, color)
            painter.end()
        frames = compose_layers([([red, red2], True), ([blue], True)], opacity=50)
        self.assertEqual(len(frames), 2)
        hidden = compose_layers([([red, red2], True), ([blue], False)])
        self.assertEqual(hidden[0].toImage().pixelColor(8, 8), QColor("red"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "edited.gif"
            export_gif(frames, output, fps=12)
            with Image.open(output) as image:
                self.assertEqual(image.format, "GIF")
                self.assertEqual(image.n_frames, 2)
                self.assertIn("transparency", image.info)
                self.assertEqual(list(ImageSequence.Iterator(image))[0].convert("RGBA").getpixel((0, 0))[3], 0)


if __name__ == "__main__":
    unittest.main()
