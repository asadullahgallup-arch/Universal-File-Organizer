# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Get the absolute path of the current directory to ensure file discovery
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC_FILE_NAME))

a = Analysis(
    ['app/main_launcher.py'],  # Target your new unified launcher entry point
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'pandas',
        'openpyxl',
        'certifi',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Universal File Organizer',  # Set the official application name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # Keeps the ugly command prompt hidden behind your GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
