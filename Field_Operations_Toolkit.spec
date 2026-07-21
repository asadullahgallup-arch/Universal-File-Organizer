# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Uses the current working directory to completely bypass PyInstaller sandbox restrictions
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
    exclude_binaries=True,           # FIXED: Exclude binaries from the exe to generate a folder structure
    name='Field Operations Toolkit',  
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                   # Hides the command window behind your GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# FIXED: Added the COLLECT block. This explicitly tells PyInstaller 
# to group all DLLs, Python libraries, and files into a folder named "Field Operations Toolkit"
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Field Operations Toolkit',
)
