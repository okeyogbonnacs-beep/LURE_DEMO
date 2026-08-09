# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('../ASSETS', 'ASSETS'), ('data', 'data')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='LURE',
    console=False,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='LURE',
)