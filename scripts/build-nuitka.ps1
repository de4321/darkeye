
# 清理旧的构建目录
Write-Host "Cleaning old build and dist folders..."

if (Test-Path build) {
    Remove-Item build -Recurse -Force
}

if (Test-Path dist) {
    Remove-Item dist -Recurse -Force
}

# 如果存在 __pycache__，也清掉
if (Test-Path __pycache__) {
    Remove-Item __pycache__ -Recurse -Force
}

# 1. 记录开始时间
$startTime = Get-Date

# 运行 pyinstaller 打包
Write-Host "Building with Nutika..."
    #   --onefile `--msvc=latest  --mingw64
nuitka `
    --msvc=latest --standalone --show-progress --show-memory `
    --windows-console-mode=disable `
    --windows-icon-from-ico="resources/icons/logo.ico" `
    --include-data-dir="resources/icons=resources/icons" `
    --include-data-dir="resources/data=resources/data" `
    --include-data-dir="resources/actressimages=resources/actressimages" `
    --include-data-dir="resources/workcovers=resources/workcovers" `
    --include-data-dir="styles=styles" `
    --enable-plugin=pyside6 `
    --enable-plugin=upx `
    --upx-binary="C:/upx-5.0.2-win64" `
    --include-module=sqlite3 `
    --nofollow-import-to="PySide6.QtWebEngine" `
    --nofollow-import-to="PySide6.QtNetwork" `
    --nofollow-import-to="PySide6.QtMultimedia" `
    --nofollow-import-to="PySide6.QtQml" `
    --nofollow-import-to="PySide6.QtQuick" `
    --nofollow-import-to="PySide6.QtOpenGL" `
    --nofollow-import-to="PySide6.QtBluetooth" `
    --nofollow-import-to="PySide6.QtNfc" `
    --nofollow-import-to="PySide6.QtPositioning" `
    --nofollow-import-to="PySide6.QtRemoteObjects" `
    --nofollow-import-to="PySide6.QtSensors" `
    --nofollow-import-to="PySide6.QtSerialPort" `
    --nofollow-import-to="PySide6.QtWebChannel" `
    --nofollow-import-to="PySide6.QtWebSockets" `
    --nofollow-import-to="PySide6.Qt3D" `
    --nofollow-import-to="PySide6.Qt3DAnimation" `
    --nofollow-import-to="PySide6.Qt3DCore" `
    --nofollow-import-to="PySide6.Qt3DExtras" `
    --nofollow-import-to="PySide6.Qt3DInput" `
    --nofollow-import-to="PySide6.Qt3DLogic" `
    --nofollow-import-to="PySide6.Qt3DRender" `
    --nofollow-import-to="PySide6.QtQml" `
    --nofollow-import-to="PySide6.QtQuick" `
    --nofollow-import-to="PySide6.QtPdf" `
    --nofollow-import-to="PySide6.QtPdfWidgets" `
    --nofollow-import-to="PySide6.QtQuickControls2" `
    --nofollow-import-to="PySide6.QtQuickWidgets" `
    --nofollow-import-to="PySide6.QtQuick3D" `
    --nofollow-import-to="PySide6.QtQmlModels" `
    --nofollow-import-to="PySide6.QtQmlWorkerScript" `
    --nofollow-import-to="matplotlib.tests" `
    --nofollow-import-to="matplotlib.examples" `
    --nofollow-import-to="matplotlib.backends.backend_gtk3agg" `
    --nofollow-import-to="matplotlib.backends.backend_macosx" `
    --nofollow-import-to="matplotlib.backends.backend_wxagg" `
    --nofollow-import-to="matplotlib.backends.backend_webagg" `
    --nofollow-import-to="matplotlib.backends.backend_tkagg" `
    --nofollow-import-to="matplotlib.backends.backend_gtk" `
    --nofollow-import-to="matplotlib.backends.backend_wx" `
    --nofollow-import-to="matplotlib.backends.backend_pdf" `
    --nofollow-import-to="matplotlib.backends.backend_ps" `
    --nofollow-import-to="matplotlib.backends.backend_svg" `
    --nofollow-import-to="matplotlib.backends.backend_cairo" `
    --nofollow-import-to="numpy.testing" `
    --nofollow-import-to="numpy.f2py" `
    --nofollow-import-to="numpy.distutils" `
    --nofollow-import-to="numpy.doc" `
    --nofollow-import-to="numpy.random" `
    --nofollow-import-to="numpy.fft" `
    --nofollow-import-to="PIL.ImageShow" `
    --nofollow-import-to="PIL.ImageTk" `
    --nofollow-import-to="PIL.SpiderImagePlugin" `
    --nofollow-import-to="PIL._tkinter_finder" `
    --nofollow-import-to="PIL.BmpImagePlugin" `
    --nofollow-import-to="PIL.IcoImagePlugin" `
    --nofollow-import-to="PIL.CurImagePlugin" `
    --nofollow-import-to="PIL.PcxImagePlugin" `
    --nofollow-import-to="PIL.TgaImagePlugin" `
    --nofollow-import-to="PIL.XbmImagePlugin" `
    --nofollow-import-to="PIL.XpmImagePlugin" `
    --nofollow-import-to="PIL.MspImagePlugin" `
    --nofollow-import-to="PIL.WalImagePlugin" `
    --nofollow-import-to="PIL.FliImagePlugin" `
    --nofollow-import-to="PIL.GbrImagePlugin" `
    --nofollow-import-to="PIL.SunImagePlugin" `
    --nofollow-import-to="PIL.SgiImagePlugin" `
    --nofollow-import-to="pandas.tests" `
    --nofollow-import-to="seaborn.tests" `
    --nofollow-import-to="scipy" `
    --nofollow-import-to="sklearn" `
    --nofollow-import-to="sqlalchemy.tests" `
    --nofollow-import-to="sqlite3.test" `
    --nofollow-import-to="tkinter" `
    --nofollow-import-to="pytest" `
    --nofollow-import-to="test" `
    --nofollow-import-to="pydoc" `
    --nofollow-import-to="pkg_resources" `
    --nofollow-import-to="setuptools" `
    --nofollow-import-to="pip" `
    --nofollow-import-to="wheel" `
    --nofollow-import-to="virtualenv" `
    --nofollow-import-to="doctest" `
    --nofollow-import-to="unittest" `
    --nofollow-import-to="pdb" `
    --nofollow-import-to="trace" `
    --nofollow-import-to="distutils" `
    --nofollow-import-to="setuptools" `
    --nofollow-import-to="venv" `
    --nofollow-import-to="lib2to3" `
    --nofollow-import-to="uu" `
    --nofollow-import-to="lzma" `
    --nofollow-import-to="bz2" `
    --nofollow-import-to="wsgiref" `
    --nofollow-import-to="xml.etree.cElementTree" `
    --nofollow-import-to="msvcrt" `
    --nofollow-import-to="_osx_support" `
    --nofollow-import-to="ossaudiodev" `
    --output-dir=dist `
    main.py


Write-Host "Build complete."
# 3. 记录结束时间
$endTime = Get-Date

# 4. 计算耗时
$timeElapsed = $endTime - $startTime

# 5. 输出结果
Write-Host "耗时: $($timeElapsed.TotalSeconds) 秒"
