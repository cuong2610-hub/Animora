import importlib.util
import sys
from pathlib import Path

from plugins.api import PluginAPI


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load(self, path):
        path = Path(path).resolve()
        if path.suffix.lower() != ".py" or not path.is_file():
            raise ValueError("Plugin phải là file Python tồn tại (.py).")
        key = str(path)
        if key in self.plugins:
            return self.plugins[key]["api"]
        module_name = f"animora_plugin_{abs(hash(key))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Không thể nạp plugin: {path.name}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            register = getattr(module, "register", None)
            if not callable(register):
                raise ValueError("Plugin phải định nghĩa register(api).")
            api = PluginAPI(path.stem)
            register(api)
        except Exception:
            sys.modules.pop(module_name, None)
            raise
        self.plugins[key] = {"module_name": module_name, "module": module, "api": api}
        return api

    def unload(self, path):
        key = str(Path(path).resolve())
        plugin = self.plugins.pop(key, None)
        if plugin:
            sys.modules.pop(plugin["module_name"], None)

    def actions(self):
        return [
            {"path": path, "plugin": Path(path).stem, **action}
            for path, plugin in self.plugins.items()
            for action in plugin["api"].actions
        ]

    def close(self):
        for path in list(self.plugins):
            self.unload(path)
