from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMenu, QFileDialog,
    QMessageBox, QListWidget, QListWidgetItem, QPushButton, QStackedWidget, QFrame,
    QCheckBox, QFormLayout, QSizePolicy, QButtonGroup, QSpinBox, QSlider,
    QLineEdit, QDialog, QDialogButtonBox, QComboBox, QWidgetAction, QInputDialog, QApplication,
)
from core.engine import Engine
from core.editor import compose_layers, export_gif
from media.loader import load_animation, load_sprite_sheet
from core.window_manager import configure_desktop_window
from storage.config import load_config, save_config
from storage.library import LibraryStore
from plugins.manager import PluginManager
from ui.i18n import translate


STYLE = """
QWidget { background: #111318; color: #e8eaf0; font: 10pt 'Segoe UI'; }
QLabel#title { font-size: 19pt; font-weight: 700; }
QLabel#muted { color: #9298a7; }
QFrame#sidebar { background: #191c23; border: 0; }
QPushButton { background: #232731; border: 1px solid #303541; border-radius: 7px; padding: 9px 12px; text-align: left; }
QPushButton:hover, QPushButton:checked { background: #343b4a; }
QPushButton#primary { background: #7c5cff; border: 0; font-weight: 600; }
QListWidget { background: #191c23; border: 1px solid #2a2e38; border-radius: 8px; padding: 5px; }
QListWidget::item { padding: 10px; border-radius: 5px; }
QListWidget::item:selected { background: #343b4a; }
QLabel#preview { background: #191c23; border: 1px solid #2a2e38; border-radius: 10px; }
QSpinBox { background: #232731; padding: 6px; }
"""
LIGHT_STYLE = STYLE.replace("#111318", "#f4f5f8").replace("#e8eaf0", "#20232b").replace("#9298a7", "#626a78").replace("#191c23", "#ffffff").replace("#232731", "#eef0f4").replace("#303541", "#d5d9e2").replace("#343b4a", "#dfe3ed").replace("#2a2e38", "#d9dde6")


class DesktopWindow(QWidget):
    def __init__(self, path, geometry=None, always_on_top=True, on_close=None, loop=True, fps=24, click_through=False, sprite_sheet=None, opacity=100, language="en", on_change=None, theme="dark"):
        super().__init__()
        self.path = str(path)
        self.language = language
        self.theme = theme
        self.fps = fps
        self.always_on_top = always_on_top
        self.sprite_sheet = sprite_sheet
        self.on_close = on_close
        self.on_change = on_change
        self.drag_pos = QPoint()
        self.resize_anchor = None
        self.image = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image.setStyleSheet("background: transparent")
        self.image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image)
        self.engine = Engine(self)
        self.engine.frame_changed.connect(self.show_frame)
        self.engine.error.connect(lambda _message: QMessageBox.warning(self, translate("Unsupported or damaged animation", self.language), translate("Animora could not read this animation. The file may be damaged or its video codec may be unavailable.", self.language)))
        configure_desktop_window(self, always_on_top, click_through)
        self.setGeometry(*(geometry or [300, 150, 300, 300]))
        self.setWindowOpacity(max(20, min(100, opacity)) / 100)
        self.setAcceptDrops(True)
        self.engine.set_loop(loop)
        self.engine.set_fps(fps)
        if sprite_sheet:
            self.engine.load_sprite_sheet(self.path, *sprite_sheet, fps)
            self.engine.play()
        else:
            self.engine.load_async(self.path)

    def show_frame(self, pixmap):
        self.image.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        if self.engine.current_frame:
            self.show_frame(self.engine.current_frame)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().x() > self.width() - 18 and event.position().y() > self.height() - 18:
                self.resize_anchor = event.globalPosition().toPoint(), self.size()
            else:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.resize_anchor and event.buttons() & Qt.MouseButton.LeftButton:
            origin, size = self.resize_anchor
            delta = event.globalPosition().toPoint() - origin
            self.resize(max(80, size.width() + delta.x()), max(80, size.height() + delta.y()))
        elif event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.resize_anchor = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(LIGHT_STYLE if self.theme == "light" else STYLE)
        for key, callback in (("Pause", self.engine.pause), ("Resume", self.engine.play), ("Stop", self.engine.stop)):
            label = translate(key, self.language)
            menu.addAction(label).triggered.connect(lambda _checked=False, action=callback: action())
        menu.addSeparator()
        speed_action = QWidgetAction(menu)
        speed = QSlider(Qt.Orientation.Horizontal)
        speed.setRange(5, 60)
        speed.setValue(self.fps)
        speed.setToolTip("Tốc độ phát / FPS" if self.language == "vi" else "Playback speed / FPS")
        speed.valueChanged.connect(self.set_speed)
        speed_action.setDefaultWidget(speed)
        menu.addAction(speed_action)
        opacity_action = QWidgetAction(menu)
        opacity = QSlider(Qt.Orientation.Horizontal)
        opacity.setRange(20, 100)
        opacity.setValue(round(self.windowOpacity() * 100))
        opacity.setToolTip("Độ mờ" if self.language == "vi" else "Opacity")
        opacity.valueChanged.connect(self.set_opacity)
        opacity_action.setDefaultWidget(opacity)
        menu.addAction(opacity_action)
        menu.addAction(translate("Close animation", self.language)).triggered.connect(self.close)
        menu.exec(event.globalPos())

    def set_speed(self, fps):
        self.fps = fps
        self.engine.set_fps(fps)
        if self.on_change:
            self.on_change()

    def set_opacity(self, value):
        self.setWindowOpacity(value / 100)
        if self.on_change:
            self.on_change()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            try:
                if Path(path).suffix.lower() not in {".gif", ".png", ".apng", ".webp", ".mp4", ".m4v", ".mkv", ".mov", ".avi", ".webm"}:
                    raise ValueError("Unsupported animation format")
                self.engine.load_async(path)
                self.path = path
            except (OSError, ValueError):
                QMessageBox.warning(self, translate("Unsupported or damaged animation", self.language), translate("Unsupported or damaged animation", self.language))
        event.acceptProposedAction()

    def closeEvent(self, event):
        self.engine.unload()
        if self.on_close:
            self.on_close(self)
        super().closeEvent(event)


class MainWindow(QWidget):
    def __init__(self, tray=None):
        super().__init__()
        self.setWindowTitle("Animora")
        self.resize(1020, 680)
        self.setMinimumSize(760, 500)
        self.tray = tray
        self.config = load_config()
        self.language = self.config.get("language", "en")
        if self.config.get("main_window_geometry"):
            self.setGeometry(*self.config["main_window_geometry"])
        self._demo_added_on_start = False
        demo_path = Path(__file__).resolve().parents[1] / "assets" / "animations" / "demo.gif"
        if not self.config.get("demo_animation_added") and demo_path.is_file():
            demo_path = str(demo_path)
            self.config["items"] = list(dict.fromkeys([*self.config.get("items", []), demo_path]))
            self.config["demo_animation_added"] = True
            self._demo_added_on_start = True
        self.library_store = LibraryStore()
        for path in self.config.get("items", []):
            self.library_store.add(path)
        self.plugin_manager = PluginManager()
        for path in self.config.get("plugins", []):
            if Path(path).is_file():
                try:
                    self.plugin_manager.load(path)
                except Exception:
                    continue
        self.items = []
        self.editor_layers = []
        self.editor_frames = []
        self.desktop_windows = []
        self.preview_engine = Engine(self)
        self.preview_engine.frame_changed.connect(self.show_frame)
        self.preview_engine.error.connect(self.show_media_error)
        self.save_timer = QTimer(self)
        self.save_timer.setInterval(500)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_state)
        self._build_ui()
        self._text_widgets = []
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLabel, QPushButton, QCheckBox)) and widget.text():
                widget.setProperty("animora_text", widget.text())
                self._text_widgets.append(widget)
            if isinstance(widget, QLineEdit) and widget.placeholderText():
                widget.setProperty("animora_placeholder", widget.placeholderText())
        self.apply_theme()
        self.apply_language()
        QApplication.instance().paletteChanged.connect(self._system_theme_changed)
        self.restore_state()
        if self._demo_added_on_start:
            self.save_state()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(190)
        side = QVBoxLayout(sidebar)
        brand = QLabel("Animora")
        brand.setObjectName("title")
        side.addWidget(brand)
        self.pages = QStackedWidget()
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []
        for label, page in (("Home", self._home_page()), ("Library", self._library_page()), ("Editor", self._editor_page()), ("Settings", self._settings_page())):
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, p=page: self.pages.setCurrentWidget(p))
            side.addWidget(button)
            self.nav_group.addButton(button)
            self.nav_buttons.append((button, label))
            self.pages.addWidget(page)
            if label == "Home":
                button.setChecked(True)
        side.addStretch(1)
        side.addWidget(QLabel("Animation desktop", objectName="muted"))
        root.addWidget(sidebar)
        root.addWidget(self.pages, 1)

    def _library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QHBoxLayout()
        title = QLabel("Animation Library", objectName="title")
        header.addWidget(title)
        header.addStretch(1)
        add = QPushButton("＋  Import Animation", objectName="primary")
        add.clicked.connect(self.import_animation)
        header.addWidget(add)
        sprite_sheet = QPushButton("Import Sprite Sheet")
        sprite_sheet.clicked.connect(self.import_sprite_sheet)
        header.addWidget(sprite_sheet)
        layout.addLayout(header)
        body = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search animations…")
        self.search.textChanged.connect(self.filter_library)
        self.library = QListWidget()
        self.library.currentRowChanged.connect(self.select_animation)
        self.library.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.library.customContextMenuRequested.connect(self.show_library_menu)
        self.sort_order = QComboBox()
        for value, label in (("name", "Name"), ("recent", "Recently opened"), ("type", "Type")):
            self.sort_order.addItem(label, value)
        self.sort_order.setCurrentIndex(max(0, self.sort_order.findData(self.config.get("sort_order", "name"))))
        self.sort_order.currentIndexChanged.connect(lambda: self.refresh_library())
        library_col = QVBoxLayout()
        library_col.addWidget(self.search)
        library_col.addWidget(QLabel("Sort by"))
        library_col.addWidget(self.sort_order)
        library_col.addWidget(self.library, 1)
        body.addLayout(library_col, 1)
        preview_col = QVBoxLayout()
        self.preview = QLabel("Import an animation to preview", objectName="preview", alignment=Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(380, 340)
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        preview_col.addWidget(self.preview, 1)
        controls = QHBoxLayout()
        for label, callback in (("Play", self.preview_engine.play), ("Pause", self.preview_engine.pause), ("Stop", self.preview_engine.stop)):
            button = QPushButton(label)
            button.clicked.connect(callback)
            controls.addWidget(button)
        desktop = QPushButton("Add to Desktop", objectName="primary")
        desktop.clicked.connect(self.add_to_desktop)
        controls.addWidget(desktop)
        preview_col.addLayout(controls)
        body.addLayout(preview_col, 2)
        layout.addLayout(body, 1)
        return page

    def _home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Welcome to Animora", objectName="title"))
        layout.addWidget(QLabel("Manage and display your animated companions on the desktop.", objectName="muted"))
        button = QPushButton("Import Animation", objectName="primary")
        button.clicked.connect(self.import_animation)
        layout.addWidget(button)
        layout.addStretch(1)
        return page

    def _editor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Playback", objectName="title"))
        self.loop_check = QCheckBox("Loop animation")
        self.loop_check.setChecked(self.config.get("loop", True))
        self.loop_check.toggled.connect(self.set_loop)
        layout.addWidget(self.loop_check)
        layout.addWidget(QLabel("Frame rate"))
        self.fps = QSpinBox()
        self.fps.setRange(1, 60)
        self.fps.setSuffix(" FPS")
        self.fps.setValue(max(1, min(60, int(self.config.get("fps", 24)))))
        self.fps.valueChanged.connect(self.set_fps)
        layout.addWidget(self.fps)
        self.editor_preview = QLabel("Add an image animation as a layer to edit", objectName="preview", alignment=Qt.AlignmentFlag.AlignCenter)
        self.editor_preview.setMinimumSize(360, 220)
        layout.addWidget(self.editor_preview, 2)
        timeline_row = QHBoxLayout()
        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setRange(0, 0)
        self.timeline.setEnabled(False)
        self.timeline.valueChanged.connect(self.seek_editor_frame)
        self.timeline_label = QLabel("Frame 0 / 0")
        timeline_row.addWidget(self.timeline, 1)
        timeline_row.addWidget(self.timeline_label)
        layout.addLayout(timeline_row)
        layers_row = QHBoxLayout()
        self.editor_layers_widget = QListWidget()
        self.editor_layers_widget.itemChanged.connect(self._layer_visibility_changed)
        layers_row.addWidget(self.editor_layers_widget, 1)
        layer_buttons = QVBoxLayout()
        add_layer = QPushButton("Add selected animation as layer")
        add_layer.clicked.connect(self.add_editor_layer)
        remove_layer = QPushButton("Remove selected layer")
        remove_layer.clicked.connect(self.remove_editor_layer)
        layer_buttons.addWidget(add_layer)
        layer_buttons.addWidget(remove_layer)
        layer_buttons.addStretch(1)
        layers_row.addLayout(layer_buttons)
        layout.addLayout(layers_row, 1)
        effects = QHBoxLayout()
        self.opacity = QSpinBox()
        self.opacity.setRange(0, 100)
        self.opacity.setSuffix("% opacity")
        self.opacity.setValue(100)
        self.opacity.valueChanged.connect(self.render_editor)
        self.rotation = QSpinBox()
        self.rotation.setRange(-180, 180)
        self.rotation.setSuffix("° rotation")
        self.rotation.valueChanged.connect(self.render_editor)
        effects.addWidget(QLabel("Effects"))
        effects.addWidget(self.opacity)
        effects.addWidget(self.rotation)
        export = QPushButton("Export GIF")
        export.clicked.connect(self.export_editor_gif)
        effects.addStretch(1)
        effects.addWidget(export)
        layout.addLayout(effects)
        layout.addStretch(1)
        return page

    def add_editor_layer(self):
        row = self.library.currentRow()
        if not 0 <= row < len(getattr(self, "entries", [])):
            return
        entry = self.entries[row]
        if entry["kind"] == "video":
            QMessageBox.information(self, translate("Video layer", self.language), translate("Video preview is supported; video layers are not supported by the frame-based editor yet.", self.language))
            return
        try:
            if entry["kind"] == "sprite_sheet":
                frames, _durations, _fps = load_sprite_sheet(entry["path"], entry["columns"], entry["rows"], entry["fps"])
            else:
                frames, _durations, _fps = load_animation(entry["path"])
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, translate("Unable to add layer", self.language), str(error))
            return
        self.editor_layers.append({"entry": entry, "frames": frames, "visible": True})
        item = QListWidgetItem(entry["name"])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self.editor_layers_widget.addItem(item)
        self.render_editor()

    def remove_editor_layer(self):
        row = self.editor_layers_widget.currentRow()
        if 0 <= row < len(self.editor_layers):
            del self.editor_layers[row]
            self.editor_layers_widget.takeItem(row)
            self.render_editor()

    def _layer_visibility_changed(self, item):
        row = self.editor_layers_widget.row(item)
        if 0 <= row < len(self.editor_layers):
            self.editor_layers[row]["visible"] = item.checkState() == Qt.CheckState.Checked
            self.render_editor()

    def render_editor(self, *_args):
        self.editor_frames = compose_layers(
            [(layer["frames"], layer["visible"]) for layer in self.editor_layers],
            self.opacity.value(),
            self.rotation.value(),
        )
        self.timeline.setEnabled(bool(self.editor_frames))
        self.timeline.setRange(0, max(0, len(self.editor_frames) - 1))
        self.seek_editor_frame(min(self.timeline.value(), max(0, len(self.editor_frames) - 1)))

    def seek_editor_frame(self, index):
        if not self.editor_frames:
            self.timeline_label.setText("Khung hình 0 / 0" if self.language == "vi" else "Frame 0 / 0")
            self.editor_preview.setText(translate("Add an image animation as a layer to edit", self.language))
            self.editor_preview.setPixmap(QPixmap())
            return
        index = max(0, min(index, len(self.editor_frames) - 1))
        self.timeline_label.setText(f"Khung hình {index + 1} / {len(self.editor_frames)}" if self.language == "vi" else f"Frame {index + 1} / {len(self.editor_frames)}")
        self.editor_preview.setPixmap(self.editor_frames[index].scaled(self.editor_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def export_editor_gif(self):
        if not self.editor_frames:
            QMessageBox.information(self, translate("Nothing to export", self.language), translate("Add at least one visible image layer first.", self.language))
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export animation", "animation.gif", "GIF (*.gif)")
        if path:
            try:
                export_gif(self.editor_frames, path, self.fps.value())
            except (OSError, ValueError) as error:
            QMessageBox.critical(self, translate("Export failed", self.language), str(error))

    def _settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Settings", objectName="title"))
        form = QFormLayout()
        self.topmost = QCheckBox("Keep animation windows above other windows")
        self.topmost.setChecked(self.config.get("always_on_top", True))
        self.topmost.toggled.connect(self.apply_topmost)
        form.addRow("Desktop windows", self.topmost)
        self.click_through = QCheckBox("Click through desktop animations")
        self.click_through.setChecked(self.config.get("click_through", False))
        self.click_through.toggled.connect(self.apply_click_through)
        form.addRow("Interaction", self.click_through)
        self.theme = QComboBox()
        for value, label in (("system", "System"), ("light", "Light"), ("dark", "Dark")):
            self.theme.addItem(label, value)
        self.theme.setCurrentIndex(max(0, self.theme.findData(self.config.get("theme", "system"))))
        self.theme.currentIndexChanged.connect(self.change_theme)
        form.addRow("Theme", self.theme)
        self.language_combo = QComboBox()
        for value, label in (("en", "English"), ("vi", "Tiếng Việt")):
            self.language_combo.addItem(label, value)
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(self.language)))
        self.language_combo.currentIndexChanged.connect(self.change_language)
        form.addRow("Language", self.language_combo)
        layout.addLayout(form)
        layout.addWidget(QLabel("Plugins", objectName="title"))
        layout.addWidget(QLabel("Plugins are local Python code and run with Animora's permissions.", objectName="muted"))
        self.plugin_list = QListWidget()
        self.plugin_list.currentRowChanged.connect(self.refresh_plugin_actions)
        self.plugin_action_list = QListWidget()
        layout.addWidget(self.plugin_list)
        layout.addWidget(self.plugin_action_list)
        plugin_buttons = QHBoxLayout()
        load_plugin = QPushButton("Load Plugin…")
        load_plugin.clicked.connect(self.load_plugin)
        unload_plugin = QPushButton("Unload Selected")
        unload_plugin.clicked.connect(self.unload_plugin)
        run_action = QPushButton("Run Selected Action")
        run_action.clicked.connect(self.run_plugin_action)
        plugin_buttons.addWidget(load_plugin)
        plugin_buttons.addWidget(unload_plugin)
        plugin_buttons.addWidget(run_action)
        layout.addLayout(plugin_buttons)
        self.refresh_plugins()
        layout.addStretch(1)
        return page

    def refresh_plugins(self):
        selected = self.plugin_list.currentItem().data(Qt.ItemDataRole.UserRole) if self.plugin_list.currentItem() else None
        self.plugin_list.clear()
        for path in self.plugin_manager.plugins:
            item = QListWidgetItem(Path(path).stem)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.plugin_list.addItem(item)
            if path == selected:
                self.plugin_list.setCurrentItem(item)
        self.refresh_plugin_actions()

    def refresh_plugin_actions(self, *_args):
        self.plugin_action_list.clear()
        path = self.plugin_list.currentItem().data(Qt.ItemDataRole.UserRole) if self.plugin_list.currentItem() else None
        self.plugin_actions = [action for action in self.plugin_manager.actions() if action["path"] == path]
        for action in self.plugin_actions:
            self.plugin_action_list.addItem(action["name"])

    def load_plugin(self):
        path, _ = QFileDialog.getOpenFileName(self, translate("Load Python plugin", self.language), "", "Python files (*.py)")
        if not path:
            return
        answer = QMessageBox.question(self, translate("Run plugin code?", self.language), translate("This Python plugin can access files and run code with the same permissions as Animora. Load it only if you trust its source.", self.language))
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.plugin_manager.load(path)
            self.refresh_plugins()
            self.save_timer.start()
        except Exception as error:
            QMessageBox.warning(self, translate("Plugin load failed", self.language), str(error))

    def unload_plugin(self):
        item = self.plugin_list.currentItem()
        if item:
            self.plugin_manager.unload(item.data(Qt.ItemDataRole.UserRole))
            self.refresh_plugins()
            self.save_timer.start()

    def run_plugin_action(self):
        row = self.plugin_action_list.currentRow()
        if 0 <= row < len(getattr(self, "plugin_actions", [])):
            try:
                self.plugin_actions[row]["callback"]()
            except Exception as error:
                QMessageBox.warning(self, translate("Plugin action failed", self.language), str(error))

    def change_theme(self, *_args):
        self.config["theme"] = self.theme.currentData()
        self.apply_theme()
        self.save_timer.start()

    def apply_theme(self):
        theme = self.config.get("theme", "system")
        if hasattr(self, "theme"):
            theme = self.theme.currentData()
        if theme == "system":
            scheme = QApplication.instance().styleHints().colorScheme()
            system_light = scheme == Qt.ColorScheme.Light or (scheme == Qt.ColorScheme.Unknown and QApplication.palette().color(QApplication.palette().Window).lightness() > 128)
            theme = "light" if system_light else "dark"
        self.setStyleSheet(LIGHT_STYLE if theme == "light" else STYLE)
        self.active_theme = theme
        for window in getattr(self, "desktop_windows", []):
            window.theme = theme
        if self.tray:
            self.tray.menu.setStyleSheet(LIGHT_STYLE if theme == "light" else STYLE)

    def _system_theme_changed(self, *_args):
        if self.theme.currentData() == "system":
            self.apply_theme()

    def change_language(self, *_args):
        self.language = self.language_combo.currentData()
        self.config["language"] = self.language
        for window in self.desktop_windows:
            window.language = self.language
        self.apply_language()
        if self.tray:
            self.tray.retranslate()
        self.save_timer.start()

    def apply_language(self):
        for widget in getattr(self, "_text_widgets", []):
            original = widget.property("animora_text")
            if original:
                widget.setText(translate(original, self.language))
            placeholder = widget.property("animora_placeholder")
            if placeholder:
                widget.setPlaceholderText(translate(placeholder, self.language))
        for button, key in getattr(self, "nav_buttons", []):
            button.setText(translate(key, self.language))
        if hasattr(self, "theme"):
            for index, label in enumerate(("System", "Light", "Dark")):
                self.theme.setItemText(index, translate(label, self.language))
            for index, label in enumerate(("English", "Tiếng Việt")):
                self.language_combo.setItemText(index, translate(label, self.language))
            for index, label in enumerate(("Name", "Recently opened", "Type")):
                self.sort_order.setItemText(index, translate(label, self.language))
        if hasattr(self, "entries"):
            selected = self.entries[self.library.currentRow()]["path"] if 0 <= self.library.currentRow() < len(self.entries) else None
            self.refresh_library(selected)
        if hasattr(self, "editor_frames"):
            self.seek_editor_frame(self.timeline.value() if self.editor_frames else 0)

    def show_media_error(self, detail):
        detail = str(detail)
        if "not supported" in detail.lower() or "unsupported" in detail.lower():
            message = "This file format is not supported. Use GIF, APNG, PNG, WebP, or a Qt-supported video."
        elif "not found" in detail.lower() or "no such file" in detail.lower():
            message = "The animation file could not be found. It may have been moved or deleted."
        else:
            message = "Animora could not read this animation. The file may be damaged or its video codec may be unavailable."
        QMessageBox.warning(self, translate("Unsupported or damaged animation", self.language), translate(message, self.language))

    def set_fps(self, value):
        self.preview_engine.set_fps(value)
        for window in self.desktop_windows:
            window.engine.set_fps(value)
            if window.engine.is_playing():
                window.engine.play()
        self.save_timer.start()

    def set_loop(self, enabled):
        self.preview_engine.set_loop(enabled)
        for window in self.desktop_windows:
            window.engine.set_loop(enabled)
        self.save_timer.start()

    def apply_topmost(self, enabled):
        for window in self.desktop_windows:
            visible = window.isVisible()
            configure_desktop_window(window, enabled, self.click_through.isChecked())
            if visible:
                window.show()
        self.save_timer.start()

    def apply_click_through(self, enabled):
        for window in self.desktop_windows:
            visible = window.isVisible()
            configure_desktop_window(window, self.topmost.isChecked(), enabled)
            if visible:
                window.show()
        self.save_timer.start()

    def import_animation(self):
        paths, _ = QFileDialog.getOpenFileNames(self, translate("Import Animation", self.language), "", "Animations (*.gif *.png *.apng *.webp *.mp4 *.m4v *.mkv *.mov *.avi *.webm)")
        for path in paths:
            self.library_store.add(path)
        if paths:
            self.refresh_library(str(Path(paths[0]).resolve()))
        self.save_timer.start()

    def import_sprite_sheet(self):
        path, _ = QFileDialog.getOpenFileName(self, translate("Import Sprite Sheet", self.language), "", "Images (*.png *.apng *.webp)")
        if not path:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(translate("Sprite sheet layout", self.language))
        form = QFormLayout(dialog)
        columns, rows, fps = QSpinBox(), QSpinBox(), QSpinBox()
        columns.setRange(1, 64)
        columns.setValue(4)
        rows.setRange(1, 64)
        rows.setValue(1)
        fps.setRange(1, 60)
        fps.setValue(12)
        form.addRow(translate("Columns", self.language), columns)
        form.addRow(translate("Rows", self.language), rows)
        form.addRow(translate("Frame rate", self.language), fps)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.library_store.add(path, "sprite_sheet", columns.value(), rows.value(), fps.value())
            self.refresh_library(str(Path(path).resolve()))
            self.save_timer.start()

    def refresh_library(self, select_path=None):
        self.entries = self.library_store.sort(self.sort_order.currentData() if hasattr(self, "sort_order") else "name")
        self.items = [entry["path"] for entry in self.entries]
        self.library.clear()
        for entry in self.entries:
            label = entry["name"]
            if entry["kind"] == "sprite_sheet":
                label += f"  ({entry['columns']}×{entry['rows']} sprite sheet)"
            elif entry["kind"] == "video":
                label += "  (video)"
            item = QListWidgetItem(label)
            try:
                pixmap = QPixmap(entry["path"])
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            except (OSError, ValueError):
                pass
            self.library.addItem(item)
        if select_path:
            for row, entry in enumerate(self.entries):
                if entry["path"] == select_path:
                    self.library.setCurrentRow(row)
                    break

    def filter_library(self, query):
        query = query.casefold().strip()
        for row in range(self.library.count()):
            self.library.item(row).setHidden(query not in self.library.item(row).text().casefold())

    def show_library_menu(self, position):
        item = self.library.itemAt(position)
        if item is None:
            return
        row = self.library.row(item)
        menu = QMenu(self)
        rename = menu.addAction(translate("Rename", self.language))
        remove = menu.addAction(translate("Remove from Library", self.language))
        selected = menu.exec(self.library.mapToGlobal(position))
        if selected == rename:
            name, accepted = QInputDialog.getText(self, translate("Rename", self.language), translate("Name", self.language), text=self.entries[row]["name"])
            if accepted and name.strip():
                self.library_store.rename(self.entries[row]["id"], name)
                self.refresh_library(self.entries[row]["path"])
                self.save_timer.start()
        elif selected == remove:
            self.library_store.remove(self.entries[row]["id"])
            self.refresh_library()
            self.save_timer.start()

    def select_animation(self, row):
        if 0 <= row < len(getattr(self, "entries", [])):
            try:
                entry = self.entries[row]
                self.library_store.touch(entry["id"])
                self.preview_engine.set_loop(self.loop_check.isChecked())
                if entry["kind"] == "sprite_sheet":
                    self.preview_engine.load_sprite_sheet(entry["path"], entry["columns"], entry["rows"], entry["fps"])
                    self.fps.setValue(entry["fps"])
                    self.preview_engine.play()
                else:
                    self.preview_engine.set_fps(self.fps.value())
                    self.preview_engine.load_async(entry["path"])
            except Exception as error:
                QMessageBox.warning(self, "Unable to load animation", str(error))

    def show_frame(self, pixmap):
        self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def add_to_desktop(self):
        row = self.library.currentRow()
        if not 0 <= row < len(getattr(self, "entries", [])):
            return
        entry = self.entries[row]
        sprite_sheet = (entry["columns"], entry["rows"]) if entry["kind"] == "sprite_sheet" else None
        try:
            window = DesktopWindow(entry["path"], always_on_top=self.topmost.isChecked(), on_close=self._window_closed, loop=self.loop_check.isChecked(), fps=entry["fps"] if sprite_sheet else self.fps.value(), click_through=self.click_through.isChecked(), sprite_sheet=sprite_sheet, language=self.language, on_change=lambda: self.save_timer.start(), theme=self.active_theme)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, translate("Unable to load animation", self.language), str(error))
            return
        self.desktop_windows.append(window)
        window.show()
        self.save_timer.start()

    def _window_closed(self, window):
        if window in self.desktop_windows:
            self.desktop_windows.remove(window)
        self.save_timer.start()

    def restore_state(self):
        self.refresh_library()
        if self.items:
            self.library.setCurrentRow(0)
        for item in self.config.get("windows", []):
            if isinstance(item.get("path"), str) and Path(item["path"]).is_file():
                try:
                    sprite_sheet = (item["columns"], item["rows"]) if item.get("kind") == "sprite_sheet" else None
                    window = DesktopWindow(item["path"], item.get("geometry"), self.topmost.isChecked(), self._window_closed, self.loop_check.isChecked(), item.get("fps", self.fps.value()), self.click_through.isChecked(), sprite_sheet, item.get("opacity", 100), self.language, lambda: self.save_timer.start(), self.active_theme)
                    self.desktop_windows.append(window)
                    if self.config.get("engine_paused"):
                        window.engine.pause()
                    window.show()
                except (KeyError, OSError, TypeError, ValueError):
                    continue

    def save_state(self):
        config = {
            "items": self.items,
            "plugins": list(self.plugin_manager.plugins),
            "demo_animation_added": self.config.get("demo_animation_added", False),
            "always_on_top": self.topmost.isChecked(),
            "click_through": self.click_through.isChecked(),
            "engine_paused": bool(self.desktop_windows) and all(not window.engine.is_playing() for window in self.desktop_windows),
            "main_window_geometry": [self.x(), self.y(), self.width(), self.height()],
            "loop": self.loop_check.isChecked(),
            "fps": self.fps.value(),
            "theme": self.theme.currentData(), "language": self.language, "sort_order": self.sort_order.currentData(),
            "recent": [entry["path"] for entry in self.library_store.list_recent()],
            "windows": [{"path": window.path, "geometry": [window.x(), window.y(), window.width(), window.height()], "kind": "sprite_sheet" if window.sprite_sheet else "file", "columns": window.sprite_sheet[0] if window.sprite_sheet else 0, "rows": window.sprite_sheet[1] if window.sprite_sheet else 0, "fps": window.fps, "opacity": round(window.windowOpacity() * 100)} for window in self.desktop_windows],
        }
        try:
            save_config(config)
            self.config = config
        except OSError as error:
            QMessageBox.warning(self, "Settings not saved", str(error))

    def closeEvent(self, event):
        self.save_timer.stop()
        self.save_state()
        if self.tray and self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def shutdown(self):
        self.save_timer.stop()
        self.save_state()
        self.preview_engine.unload()
        for window in self.desktop_windows:
            window.engine.unload()
        self.library_store.close()
        self.plugin_manager.close()
