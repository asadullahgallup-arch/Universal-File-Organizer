# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

SPEC_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = SPEC_DIR   # the spec is in the project root

a = Analysis(
    ['app/main_launcher.py'],         # entry point
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        ('app/assets/*', 'app/assets'),    # icon(s) and any other resources
    ],
    hiddenimports=[
        'customtkinter',
        'pandas',
        'openpyxl',
        'certifi',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # Packages – PyInstaller will crawl them if they contain __init__.py
        'organizer',
        'common',
        'separator',
        # Explicit app.* modules (not auto‑detected due to dynamic loading)
        'app.excel_handler',
        'app.config',
        'app.indexer',
        'app.matcher',
        'app.worker',
        'app.profile_manager',
        'app.version',
        'app.updater',
        'app.report',
        'app.organizer',               # the file‑ops engine used by Worker
        'app.compare',                 # if you later add the Compare tool
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
    ...
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Field Operations Toolkit',
)