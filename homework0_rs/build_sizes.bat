@echo off
chcp 65001 >nul
echo ============================================
echo  Rust可执行文件大小比较工具
echo ============================================
echo.

echo 构建Debug版本...
cargo build
if %errorlevel% neq 0 (
    echo 构建失败!
    exit /b 1
)

echo 构建Release版本...
cargo build --release
if %errorlevel% neq 0 (
    echo 构建失败!
    exit /b 1
)

echo 构建最小体积版本...
cargo build --profile min-size
if %errorlevel% neq 0 (
    echo 构建失败!
    exit /b 1
)

echo.
echo ============================================
echo 文件大小比较结果:
echo ============================================
echo.

for %%f in (target\debug\homework0_rs.exe) do set debug_size=%%~zf
for %%f in (target\release\homework0_rs.exe) do set release_size=%%~zf
for %%f in (target\min-size\homework0_rs.exe) do set minsize_size=%%~zf

set /a debug_kb=%debug_size%/1024
set /a release_kb=%release_size%/1024
set /a minsize_kb=%minsize_size%/1024

echo Debug版本:    %debug_kb% KB
echo Release版本:  %release_kb% KB
echo 最小体积版本: %minsize_kb% KB
echo.

set /a release_saving=%debug_kb%-%release_kb%
set /a minsize_saving=%debug_kb%-%minsize_kb%

echo Release版本比Debug版本节省: %release_saving% KB
echo 最小体积版本比Debug版本节省: %minsize_saving% KB
echo.

echo 各版本文件路径:
echo Debug:    target\debug\homework0_rs.exe
echo Release:  target\release\homework0_rs.exe
echo Min-Size: target\min-size\homework0_rs.exe
echo.

echo 运行测试:
echo Debug版本:    target\debug\homework0_rs.exe
echo Release版本:  target\release\homework0_rs.exe
echo 最小体积版本: target\min-size\homework0_rs.exe
echo.

pause
