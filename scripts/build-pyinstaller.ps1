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
Write-Host "Building with PyInstaller..."
pyinstaller --clean --noconfirm .\main.spec


#手动删除一些不用的包
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\opengl32sw.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6OpenGL.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6Pdf.dll" -Force
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6QmlMeta.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6Qml.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6QmlModels.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6QmlWorkerScript.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6Quick.dll" -Force 
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6Network.dll" -Force
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\Qt6VirtualKeyboard.dll" -Force
Remove-Item -Path ".\dist\DarkEye\_internal\PySide6\translations" -Force -Recurse
Remove-Item -Path ".\dist\DarkEye\_internal\cv2" -Force -Recurse
Write-Host "Build complete."
# 3. 记录结束时间
$endTime = Get-Date

# 4. 计算耗时
$timeElapsed = $endTime - $startTime

# 5. 输出结果
Write-Host "耗时: $($timeElapsed.TotalSeconds) 秒"