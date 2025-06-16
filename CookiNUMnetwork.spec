# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import glob
import os
from pathlib import Path

# Collecte les fichiers de données du package vosk (exemple)
vosk_datas = collect_data_files('vosk')

# Inclure tous les fichiers sous src/resources en conservant l'arborescence src/resources
resources_datas = [
    (str(f), os.path.dirname(os.path.join('src', os.path.relpath(str(f), 'src'))))
    for f in Path('src/resources').rglob('*')
    if f.is_file()
]


# Exemple modèle vosk (optionnel, si nécessaire)
model_datas = [
    (f, os.path.join('src', os.path.relpath(f, 'src')))
    for f in glob.glob('src/resources/binaries/audio_model/vosk-model-small-fr-0.22/**/*', recursive=True)
    if os.path.isfile(f)
]

a = Analysis(
    ['src\\core\\main.py'],  # chemin vers ton script principal
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
    icon=os.path.join('src', 'resources', 'images', 'Logo-CookiNUM-v.ico'),
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
