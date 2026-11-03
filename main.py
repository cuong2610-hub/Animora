import sys

from PySide6.QtWidgets import QApplication, QStyle
from ui.main_window import MainWindow
from ui.tray import SystemTray


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Animora")
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    tray = SystemTray(app, window)
    tray.setIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
    tray.show()
    window.tray = tray
    app.aboutToQuit.connect(window.shutdown)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
