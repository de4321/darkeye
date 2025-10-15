# main.spec
# 适用于 project 结构的 PyInstaller 打包配置

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# 如果需要支持路径兼容
project_path = os.path.abspath(".")
sys.path.insert(0, project_path)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        # 静态资源（icons、封面、演员图、数据库）
        ('resources/icons', 'resources/icons'),
        ('resources/public/workcovers', 'resources/public/workcovers'),
        ('resources/public/actressimages', 'resources/public/actressimages'),
        ('resources/public/actorimages', 'resources/public/actorimages'),
        ('resources/public/public.db', 'resources/public/'),
        ('resources/config', 'resources/config'),
        ('resources/sql/', 'resources/sql/'),
        ('styles', 'styles'),
    ],
    hiddenimports=[
        *collect_submodules('core'),
        *collect_submodules('ui'),
        *collect_submodules('controller'),
        'matplotlib.backends.backend_agg',#只打包agg后端
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngine',                                    #精简pyside6
        'PySide6.QtNetwork',
        'PySide6.QtMultimedia',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtOpenGL',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtPositioning',
        'PySide6.QtRemoteObjects',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtWebChannel',
        'PySide6.QtWebSockets',
        'PySide6.Qt3D',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.QtQml', 
        'PySide6.QtQuick', 
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtQuickControls2',
        'PySide6.QtQuickWidgets',
        'PySide6.QtQuick3D*',
        'PySide6.QtQmlModels',
        'PySide6.QtQmlWorkerScript',
        'matplotlib.tests',                                           #精简numpy
        'matplotlib.examples',
        'matplotlib.backends.backend_gtk3agg',
        'matplotlib.backends.backend_macosx',
        'matplotlib.backends.backend_wxagg',
        'matplotlib.backends.backend_webagg',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_gtk',
        'matplotlib.backends.backend_wx',
        'matplotlib.backends.backend_pdf',
        'matplotlib.backends.backend_ps',
        'matplotlib.backends.backend_svg',
        'matplotlib.backends.backend_cairo',
        'numpy.testing',                                            #精简numpy
        'numpy.f2py',
        'numpy.distutils',
        'numpy.doc',
        'numpy.random',
        'numpy.fft',
        'PIL.ImageShow',                                           #精简PIL
        'PIL.ImageTk',
        'PIL.SpiderImagePlugin',
        'PIL._tkinter_finder',
        'PIL.BmpImagePlugin',       # 支持 BMP 格式
        'PIL.IcoImagePlugin',       # 支持 ICO 格式
        'PIL.CurImagePlugin',       # 支持 CUR 格式
        'PIL.PcxImagePlugin',       # 支持 PCX 格式
        'PIL.TgaImagePlugin',       # 支持 TGA 格式
        'PIL.XbmImagePlugin',       # 支持 XBM 格式
        'PIL.XpmImagePlugin',       # 支持 XPM 格式
        'PIL.MspImagePlugin',       # 支持 MSP 格式
        'PIL.WalImagePlugin',       # 支持 WAL 格式
        'PIL.FliImagePlugin',       # 支持 FLI/FLC 格式
        'PIL.GbrImagePlugin',       # 支持 GBR 格式
        'PIL.SunImagePlugin',       # 支持 Sun Raster 格式
        'PIL.SgiImagePlugin',       # 支持 SGI 格式
        'pandas.tests',
        'seaborn.tests',
        'scipy',  
        'sklearn',  
        'sqlalchemy.tests', 
        'sqlite3.test',                                       #一些python自带的
        'tkinter',
        'pytest',
        'test',
        'pydoc',
        'pkg_resources',
        'setuptools',
        'pip',
        'wheel',
        'virtualenv',
        # 调试和测试模块
        'doctest',
        'unittest',
        'pdb',
        'trace',
        # 构建和部署模块
        'distutils',
        'setuptools',
        'venv',
        'lib2to3',
        # 不常用的数据格式和工具
        'uu',
        'lzma',
        'bz2',
        'wsgiref',
        'xml.etree.cElementTree',
        # 特定环境的模块
        'msvcrt',
        '_osx_support',
        'ossaudiodev',
    ],
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
    name='DarkEye',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['Qt6Core.dll', 'Qt6Gui.dll','Qt6Widgets.dll','Qt6Qml.dll','Qt6Quick.dll','Qt6Pdf.dll'],
    console=False,  # 改为 True 可显示终端日志窗口
    icon='resources/icons/logo.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['Qt6Core.dll', 'Qt6Gui.dll','Qt6Widgets.dll','Qt6Qml.dll','Qt6Quick.dll','Qt6Pdf.dll'],
    name='DarkEye'
)
