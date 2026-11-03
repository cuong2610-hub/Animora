# Changelog

## Unreleased

- **Audit:** recorded the verified source baseline and clarified which requested features are still missing in README.
- **Tests:** baseline included four passing unit/integration checks before this development run.
- **Fix bugs / desktop engine:** added click-through using Qt's input-transparency flag, exposed a recovery toggle in Settings and tray, and made JSON configuration saves atomic. Offscreen integration verifies playback and click-through on desktop windows; 4/4 tests pass.
- **Media engine:** added APNG and animated WebP/Pillow decoding, sprite-sheet slicing API, and Qt Multimedia video playback with muted audio and playback-rate control. Video sources are unloaded when windows close to release file handles. Local MP4 decoder check plus suite: 6/6 tests pass.
- **Library:** added a stdlib SQLite store, idempotent import of existing JSON paths, search, remove-from-library without deleting source files, and sprite-sheet row/column/FPS metadata. Added tests for store idempotency and metadata; suite: 8/8 tests pass.
- **UI, tray, settings:** exposed sprite-sheet import and Library search/removal; added click-through recovery in tray, persistent main-window geometry and explicit SQLite connection shutdown. Full tests: 8/8 pass.
- **Editor:** added frame timeline scrubbing, add/remove and visibility controls for image layers, opacity/rotation composition, and transparent GIF export. The exporter test covers multiple frames and alpha; full suite: 9/9 pass. Video preview remains supported, but video tracks are not part of this frame-based editor.
- **Plugins:** added a Python `register(api)` contract, action registration, plugin load/unload, persistence, and Settings manager. The UI warns that plugins execute with the app's permissions. Plugin lifecycle tests pass; suite: 11/11.
- **Performance:** image files decode to QImage off the UI thread using a two-worker shared pool; stale requests are discarded, closing an animation unloads its frames/video source, and video decoding stays in Qt Multimedia. Added race-cancellation test; suite: 12/12. Editor composition remains in-memory.
- **Release:** added MIT License, PyInstaller spec, Inno Setup installer script, and build/codec notes in README.
- **Portable build fix:** changed PyInstaller output to one-file and added `build_release.py` to verify embedded `python312.dll` and smoke-test with Python paths removed. PyInstaller 6.22.3 build succeeded; `dist\Animora.exe` is about 65 MB and started without Python on `PATH`. Installer compilation remains unverified because Inno Setup is unavailable.
