# CARpetrosani.spec — build Windows (onedir, fara consola DOS)
# -*- mode: python ; coding: utf-8 -*-
#
# Model app: resursele de date (baze .db, config JSON) sunt citite din
# os.path.dirname(sys.executable) = folderul exe-ului. De aceea folosim
# contents_directory='.' -> PyInstaller pune TOT langa exe (nu in _internal),
# astfel incat dirname(sys.executable), sys._MEIPASS si caile relative
# ('icons/...') sa arate toate spre acelasi folder.
#
# Bazele de date RON GOALE + configurarile se copiaza langa exe DUPA build
# (nu sunt bundle-uite ca sa nu ajunga read-only). Vezi pasul de asamblare.

datas = [
    ('icons', 'icons'),
    ('fonts', 'fonts'),
    ('config_dobanda.json', '.'),
    ('conversie_config.json', '.'),
    ('dual_currency.json', '.'),
    ('theme_settings.json', '.'),
    ('imprumuturi_noi_config.json', '.'),
    ('imprumuturi_noi_prima_rata.json', '.'),
    ('car_settings.json', '.'),
    # fonturi din radacina (reportlab le foloseste pentru PDF)
    ('Arial.ttf', '.'),
    ('DejaVuSans.ttf', '.'),
    ('DejaVuSans-Bold.ttf', '.'),
    ('DejaVuBoldSans.ttf', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'xlsxwriter',
        'reportlab', 'reportlab.lib', 'reportlab.pdfgen', 'reportlab.pdfbase',
        'PIL', 'PIL.Image',
        'dbf',
        'pyzipper',
        'security_manager', 'dialog_styles', 'permisiuni',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['AppKit', 'Foundation'],  # module macOS — irelevante pe Windows
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CARpetrosani',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX off -> mai putine false-positive antivirus
    console=False,             # FARA fereastra DOS
    disable_windowed_traceback=False,
    icon='icons/pol.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CARpetrosani',
    contents_directory='.',    # tot langa exe (nu in _internal)
)
