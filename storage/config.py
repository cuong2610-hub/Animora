import json
import os
from pathlib import Path
import tempfile

CONFIG_PATH = Path.home() / ".animora" / "config.json"
DEFAULT_CONFIG = {"items": [], "windows": [], "plugins": [], "always_on_top": True, "click_through": False, "engine_paused": False, "loop": True, "fps": 24, "theme": "system", "language": "en", "recent": []}


def load_config():
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(config, dict):
            merged = {**DEFAULT_CONFIG, **config}
            merged["items"] = [path for path in merged["items"] if isinstance(path, str)] if isinstance(merged["items"], list) else []
            merged["windows"] = [window for window in merged["windows"] if isinstance(window, dict)] if isinstance(merged["windows"], list) else []
            merged["plugins"] = [path for path in merged["plugins"] if isinstance(path, str)] if isinstance(merged["plugins"], list) else []
            merged["theme"] = merged["theme"] if isinstance(merged["theme"], str) and merged["theme"] in {"system", "light", "dark"} else "system"
            merged["language"] = merged["language"] if isinstance(merged["language"], str) and merged["language"] in {"en", "vi"} else "en"
            merged["recent"] = [path for path in merged["recent"] if isinstance(path, str)] if isinstance(merged["recent"], list) else []
            geometry = merged.get("main_window_geometry")
            if isinstance(geometry, list) and len(geometry) == 4:
                try:
                    x, y, width, height = map(int, geometry)
                    merged["main_window_geometry"] = [x, y, max(760, width), max(500, height)]
                except (TypeError, ValueError):
                    merged["main_window_geometry"] = None
            else:
                merged["main_window_geometry"] = None
            for key in ("always_on_top", "click_through", "engine_paused", "loop"):
                merged[key] = bool(merged[key])
            try:
                merged["fps"] = max(1, min(60, int(merged["fps"])))
            except (TypeError, ValueError):
                merged["fps"] = DEFAULT_CONFIG["fps"]
            return merged
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=CONFIG_PATH.parent, delete=False) as file:
            temporary_path = Path(file.name)
            json.dump(config, file, indent=2, ensure_ascii=False)
        os.replace(temporary_path, CONFIG_PATH)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
