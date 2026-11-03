import tempfile
import unittest
from pathlib import Path

from plugins.manager import PluginManager


class PluginManagerChecks(unittest.TestCase):
    def test_plugin_action_load_run_unload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample_plugin.py"
            path.write_text("def register(api):\n    api.add_action('Say hello', lambda: 'hello')\n", encoding="utf-8")
            manager = PluginManager()
            manager.load(path)
            actions = manager.actions()
            self.assertEqual(actions[0]["name"], "Say hello")
            self.assertEqual(actions[0]["callback"](), "hello")
            manager.unload(path)
            self.assertEqual(manager.actions(), [])

    def test_invalid_plugin_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.py"
            path.write_text("value = 1\n", encoding="utf-8")
            manager = PluginManager()
            with self.assertRaisesRegex(ValueError, r"register\(api\)"):
                manager.load(path)
            self.assertEqual(manager.plugins, {})


if __name__ == "__main__":
    unittest.main()
