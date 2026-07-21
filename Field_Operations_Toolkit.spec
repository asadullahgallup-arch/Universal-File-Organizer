# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# FIXED: Uses the current working directory to completely bypass PyInstaller sandbox restrictions
SPEC_DIR = os.getcwd()

a = Analysis(
    ['app/main_launcher.py'],  # Target your true UI hub launcher entry point
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
        'tkinter.messagebox',
        'organizer',            # Bundles your original toolset package
        'common',               # Bundles common updaters/handlers
        'separator'             # Bundles your spreadsheet categorizer engine
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
    name='Field Operations Toolkit',  # Sets your official application name with spaces
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # Keeps the command window hidden behind your GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
