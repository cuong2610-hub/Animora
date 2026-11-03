import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from core.animation import Animation
from storage import config


class CoreChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_non_looping_animation_stops_on_last_frame(self):
        animation = Animation()
        animation.load_frames([QPixmap(1, 1), QPixmap(1, 1)], loop=False)
        animation.next_frame()
        self.assertEqual(animation.index, 1)
        animation.next_frame()
        self.assertEqual(animation.index, 1)
        self.assertFalse(animation.timer.isActive())

    def test_config_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            state = {"items": ["pet.gif"], "engine_paused": True}
            with patch.object(config, "CONFIG_PATH", path):
                config.save_config(state)
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), state)
                self.assertEqual(config.load_config()["items"], ["pet.gif"])
                self.assertTrue(config.load_config()["always_on_top"])
                self.assertFalse(config.load_config()["click_through"])
                self.assertEqual(config.load_config()["theme"], "system")
                self.assertEqual(config.load_config()["language"], "en")


if __name__ == "__main__":
    unittest.main()
