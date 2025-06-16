# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
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

# Ajouter le répertoire src au PYTHONPATH
src_path = os.path.abspath('src')
os.environ['PYTHONPATH'] = src_path + os.pathsep + os.environ.get('PYTHONPATH', '')

a = Analysis(
    ['src\\core\\main.py'],  # chemin vers ton script principal
    pathex=[src_path],
    binaries=[],
    datas=[
        *vosk_datas,
        *resources_datas,
    ],
    hiddenimports=['src.core'],  # Ajouter explicitement le module src.core
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
    [],
    exclude_binaries=True,
    name='CookiNUMnetwork',
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
    icon=os.path.join('src', 'resources', 'images', 'cookiNUM.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CookiNUMnetwork',
)
