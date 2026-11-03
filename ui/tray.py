from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class SystemTray(QSystemTrayIcon):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setToolTip("Animora")
        self.menu = QMenu()
        self.menu.setStyleSheet(parent.styleSheet())
        self.show_action = QAction("Show Main Window", self.menu)
        show = self.show_action
        show.triggered.connect(self.show_main)
        self.menu.addAction(show)
        self.hide_main_action = QAction("Hide Main Window", self.menu)
        self.hide_main_action.triggered.connect(parent.hide)
        self.menu.addAction(self.hide_main_action)
        self.menu.addSeparator()
        self.hide_animations_action = QAction("Hide Animations", self.menu)
        self.hide_animations_action.triggered.connect(self.toggle_animations)
        self.menu.addAction(self.hide_animations_action)
        self.pause_action = QAction("Pause All", self.menu)
        self.pause_action.triggered.connect(self.pause_all)
        self.menu.addAction(self.pause_action)
        self.resume_action = QAction("Resume All", self.menu)
        self.resume_action.triggered.connect(self.resume_all)
        self.menu.addAction(self.resume_action)
        self.click_action = QAction("Click-through animations", self.menu, checkable=True)
        self.click_action.toggled.connect(self.set_click_through)
        self.click_action.setChecked(parent.click_through.isChecked())
        self.menu.addAction(self.click_action)
        self.menu.addSeparator()
        self.exit_action = QAction("Exit", self.menu)
        exit_action = self.exit_action
        exit_action.triggered.connect(app.quit)
        self.menu.addAction(exit_action)
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.show_main() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.retranslate()

    def retranslate(self):
        from ui.i18n import translate
        language = self.parent().language
        self.show_action.setText(translate("Show Main Window", language))
        self.hide_main_action.setText(translate("Hide Main Window", language))
        self.hide_animations_action.setText(translate("Show Animations" if any(w.isHidden() for w in self.parent().desktop_windows) else "Hide Animations", language))
        self.pause_action.setText(translate("Pause All", language))
        self.resume_action.setText(translate("Resume All", language))
        self.click_action.setText(translate("Click-through animations", language))
        self.exit_action.setText(translate("Exit", language))

    def toggle_animations(self):
        windows = self.parent().desktop_windows
        hide = any(window.isVisible() for window in windows)
        for window in windows:
            window.setVisible(not hide)
        self.retranslate()

    def show_main(self):
        self.parent().showNormal()
        self.parent().raise_()
        self.parent().activateWindow()

    def pause_all(self):
        for window in self.parent().desktop_windows:
            window.engine.pause()
        self.parent().config["engine_paused"] = True
        self.parent().save_state()

    def resume_all(self):
        for window in self.parent().desktop_windows:
            window.engine.play()
        self.parent().config["engine_paused"] = False
        self.parent().save_state()

    def set_click_through(self, enabled):
        checkbox = self.parent().click_through
        if checkbox.isChecked() != enabled:
            checkbox.setChecked(enabled)
