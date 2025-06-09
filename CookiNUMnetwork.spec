# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import glob
import os
from pathlib import Path

# Collecte les fichiers de données du package vosk
vosk_datas = collect_data_files('vosk')

# Inclure tous les fichiers sous src/resources en conservant l'arborescence src/resources
resources_datas = [
    (str(f), os.path.dirname(os.path.join('src', os.path.relpath(str(f), 'src'))))
    for f in Path('src/resources').rglob('*')
    if f.is_file()
]

a = Analysis(
    ['src/core/main.py'],  # chemin vers le script principal (utilisant forward slashes)
    pathex=[],
    binaries=[],
    datas=[
        *vosk_datas,
        *resources_datas,
    ],
    hiddenimports=[],
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
    name='CookiNUMnetwork',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Activé pour macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Configuration spécifique pour macOS
app = BUNDLE(
    exe,
    name='CookiNUMnetwork.app',
    bundle_identifier='com.cookinum.network',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'NSRequiresAquaSystemAppearance': 'False',  # Support du mode sombre
    },
)
