# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['app/main_launcher.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'customtkinter',
        'pandas',
        'openpyxl',
        'certifi',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'organizer',
        'app.common',
        'app.common.config',
        'app.common.excel_handler',
        'app.common.profile_manager',
        'app.common.updater',
        'app.common.version',
        'app.organizer',
        'app.organizer.gui',
        'app.organizer.indexer',
        'app.organizer.matcher',
        'app.organizer.organizer',
        'app.organizer.report',
        'app.organizer.worker',
        'app.separator',
        'app.separator.separator',
        'app.compare_excel',
        'app.compare_excel.compare',
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
    exclude_binaries=True,
    name='Field Operations Toolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Field Operations Toolkit',
)