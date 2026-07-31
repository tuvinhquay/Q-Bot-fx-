# -*- mode: python ; coding: utf-8 -*-

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
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="QBotFX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
