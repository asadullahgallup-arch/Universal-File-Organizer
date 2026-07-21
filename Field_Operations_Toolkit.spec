# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# FIXED: Replaced SPEC_FILE_NAME with a universally compatible absolute path definition
SPEC_DIR = os.path.dirname(os.path.abspath(__file__))

a = Analysis(
    ['app/main_launcher.py'],  # Entry point pointing to your UI hub launcher
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
        'organizer',            
        'common',               
        'separator'             
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
    console=False,                    # Hides the console window behind your modern GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
