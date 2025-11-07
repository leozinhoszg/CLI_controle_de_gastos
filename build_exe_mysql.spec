# -*- mode: python ; coding: utf-8 -*-
"""
Spec file para criar executável do Sistema de Controle de Gastos com MySQL
PyInstaller configuração avançada
"""

block_cipher = None

# Dados adicionais (arquivos que precisam ser incluídos)
added_files = [
    ('src', 'src'),  # Incluir toda a pasta src
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

a = Analysis(
    ['main_avancado.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'mysql.connector',
        'mysql.connector.pooling',
        'mysql.connector.cursor',
        'src.db.db_config',
        'src.db.db_connection',
        'src.controllers.controle_avancado_mysql',
        'src.controllers.controle_gastos',
        'src.utils.exportador',
        'matplotlib',
        'pandas',
        'numpy',
        'openpyxl',
        'reportlab',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],  # Não precisamos de tkinter
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaControleGastosMySQL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Manter console para CLI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione um ícone se tiver
)




