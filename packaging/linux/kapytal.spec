# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ["../../main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("../../resources/images", "resources/images"),
        ("../../resources/icons", "resources/icons"),
        ("../../logs/README.md", "logs/."),
        ("../../saved_data/README.md", "saved_data/."),
        ("../../saved_data/demo_basic.json", "saved_data/."),
        ("../../saved_data/demo_mortgage.json", "saved_data/."),
        ("../../saved_data/template_category_en.json", "saved_data/."),
        ("../../saved_data/template_category_cz.json", "saved_data/."),
        ("../../saved_data/backups/README.md", "saved_data/backups/."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Kapytal",
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
    icon="../../resources/icons/icons-custom/kapytal.png",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Kapytal",
)
