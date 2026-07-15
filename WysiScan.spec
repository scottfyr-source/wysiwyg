# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Git\\WysiWyg\\WysiScan\\scanner_server.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Git\\WysiWyg\\WysiScan\\scanner_test.html', 'WysiScan'), ('C:\\Git\\WysiWyg\\WysiScan\\WysiScan.ico', 'WysiScan'), ('C:\\Git\\WysiWyg\\WysiScan\\WysiScan.png', 'WysiScan')],
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
    name='WysiScan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Git\\WysiWyg\\WysiScan\\WysiScan.ico'],
)
