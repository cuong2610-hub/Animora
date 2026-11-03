# Animora

Animora is a Python desktop animation player for Windows, built with PySide6 and Pillow. This repository is under active development; see [CHANGELOG.md](CHANGELOG.md) for completed stages and remaining work.

## Current status

The app includes Light, Dark, and System themes, English and Vietnamese UI, JSON settings, a SQLite animation library, animation preview, independent desktop windows, a system tray, a frame-based editor, a local Python plugin API, and a bundled transparent demo GIF. The library supports multi-file import, search, sorting, thumbnails, rename, removal, and recently opened items. Desktop animations can be moved and resized, accept dropped media files, and expose speed and opacity controls from their context menu. Pillow loads GIF, APNG, PNG, WebP, and sprite sheets; Qt Multimedia decodes video. Image decoding runs in a bounded background pool. Video layers are not supported in the editor.

## Requirements

- Python 3.12+
- Windows 10 or 11 (initial target)

## Run from source

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Run checks with:

```powershell
python -m unittest discover -s tests -v
```

The included sample generator uses Pillow and requires no network access:

```powershell
python assets\animations\generate_demo.py
```

## Current controls

- Import GIF, APNG, PNG, WebP, and Qt-supported video files in Library; a demo GIF is added on first launch.
- Import sprite sheets by specifying rows, columns, and frame rate.
- Search, sort, rename, or remove Library entries without deleting their source files. Recently opened items are tracked in SQLite.
- Editor supports frame scrubbing, visible/hidden image layers, opacity, rotation, and transparent GIF export.
- Select a library item to preview it. Use Play, Pause, Stop, and Add to Desktop.
- Drag a desktop animation to move it; drag its bottom-right corner to resize it. Drop a supported media file onto it to replace its animation.
- Right-click a desktop animation for playback, speed, opacity, and close controls.
- Toggle click-through mode from Settings or the tray menu; it can be switched off from either place.
- Close the main window to keep the process in the system tray. Use the tray menu to show the window, pause/resume desktop animations, or exit.
- Settings store theme, language, library paths, desktop window geometry, playback state, loop, frame rate, sort order, opacity, and always-on-top in `%USERPROFILE%\.animora\config.json`.
- Plugins are local Python code and run with Animora's permissions; load only plugins from sources you trust.

Video formats depend on codecs available to the Qt Multimedia backend on the target machine. The frame-based editor exports GIF; video layers are not supported there.

## Build a Windows release

Build the portable single-file application and run its startup check:

```powershell
.\.venv\Scripts\python.exe build_release.py
```

The distributable is `dist\Animora.exe` (one-file, roughly 65 MB on the current build). It includes the Python runtime, Qt, Pillow, and Qt Multimedia; the build script checks for the embedded `python312.dll` and smoke-tests it with Python paths removed. Files under `build\` are PyInstaller work files; run the executable from `dist\`, not from `build\`. To create the installer, install Inno Setup 6 and compile `installer.iss` with `ISCC.exe`.

Animora is distributed under the MIT License; see [LICENSE](LICENSE).

## Development stages

| Stage | Status |
|---|---|
| Audit and baseline | Complete |
| Bug fixes and desktop engine | Complete (click-through, drag/resize, independent windows) |
| Media engine | Complete (GIF/APNG/PNG/WebP, Qt video playback, sprite-sheet loader API) |
| SQLite library | Complete (search, import, sprite-sheet metadata, remove, JSON-path migration) |
| UI and tray | Complete (searchable Library, sprite-sheet import, system-tray controls) |
| Settings | Complete (JSON playback and window geometry, click-through, atomic writes) |
| Editor | Basic image-frame editing complete (timeline, layers, opacity/rotation, GIF export); video layers planned |
| Plugin API | Basic `register(api)` actions and load/unload manager complete |
| Performance | Baseline complete (background image decode, 2-worker cap, unload/cancel stale loads); editor composition still keeps frames in memory |
| Release packaging and documentation | One-file portable EXE built and verified without Python on PATH; installer build remains unverified |
"# Animora" 
