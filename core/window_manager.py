from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

def configure_desktop_window(window: QWidget, always_on_top=True, click_through=False):
    flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
    if always_on_top:
        flags |= Qt.WindowType.WindowStaysOnTopHint
    if click_through:
        flags |= Qt.WindowType.WindowTransparentForInput
    window.setWindowFlags(flags)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
