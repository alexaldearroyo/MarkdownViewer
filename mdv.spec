# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['mdv.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('./themes/dark_theme.css', 'themes'),
        ('./themes/light_theme.css', 'themes'),
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
    name='Markdown Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Markdown Viewer',
)
app = BUNDLE(
    coll,
    name='Markdown Viewer.app',
    icon='icon.icns',
    bundle_identifier=None,
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': 'Markdown File',
            'CFBundleTypeRole': 'Editor',
            'LSHandlerRank': 'Owner',
            'LSItemContentTypes': ['public.plain-text'],
            'CFBundleTypeExtensions': ['md']
        }]
    }
)
