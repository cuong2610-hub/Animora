class PluginAPI:
    def __init__(self, plugin_name):
        self.plugin_name = plugin_name
        self.actions = []

    def add_action(self, name, callback):
        if not isinstance(name, str) or not name.strip() or not callable(callback):
            raise ValueError("Plugin action cần tên và callback hợp lệ.")
        self.actions.append({"name": name.strip(), "callback": callback})
