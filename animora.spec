# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


root = Path(SPECPATH)
pil_datas, pil_binaries, pil_hidden = collect_all("PIL")

analysis = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=pil_binaries,
    datas=pil_datas + [(str(root / "assets" / "animations" / "demo.gif"), "assets/animations")],
    hiddenimports=pil_hidden + ["PySide6.QtMultimedia"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "unittest"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(analysis.pure)

# One-file bundles Python and all native dependencies into the distributable EXE.
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="Animora",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
