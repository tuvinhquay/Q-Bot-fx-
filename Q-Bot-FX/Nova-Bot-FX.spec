# -*- mode: python ; coding: utf-8 -*-
"""
Nova-Bot-FX Production Build Spec
Portable Distribution (OneDir mode)
"""

import sys
from pathlib import Path

a = Analysis(
    [str(Path("backend/main.py"))],
    pathex=[str(Path.cwd())],
    binaries=[],
    datas=[
        (str(Path("config")), "config"),
        (str(Path(".env")), "."),
        (str(Path(".env.example")), "."),
    ],
    hiddenimports=[
        "MetaTrader5",
        "psutil",
        "requests",
        "sqlite3",
        "numpy",
        "pandas",
        "telegram",
        "dotenv",
        "pytz",
        "aiohttp",
        "asyncio",
        "google",
        "google.generativeai",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Nova-Bot-FX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Nova-Bot-FX",
)
