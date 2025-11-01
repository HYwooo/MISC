#!/bin/bash

echo "============================================"
echo " Rust可执行文件大小比较工具"
echo "============================================"
echo

echo "构建Debug版本..."
cargo build
if [ $? -ne 0 ]; then
    echo "构建失败!"
    exit 1
fi

echo "构建Release版本..."
cargo build --release
if [ $? -ne 0 ]; then
    echo "构建失败!"
    exit 1
fi

echo "构建最小体积版本..."
cargo build --profile min-size
if [ $? -ne 0 ]; then
    echo "构建失败!"
    exit 1
fi

echo
echo "============================================"
echo "文件大小比较结果:"
echo "============================================"
echo

debug_size=$(stat -c%s "target/debug/homework0_rs.exe" 2>/dev/null || stat -f%z "target/debug/homework0_rs.exe")
release_size=$(stat -c%s "target/release/homework0_rs.exe" 2>/dev/null || stat -f%z "target/release/homework0_rs.exe")
minsize_size=$(stat -c%s "target/min-size/homework0_rs.exe" 2>/dev/null || stat -f%z "target/min-size/homework0_rs.exe")

debug_kb=$((debug_size / 1024))
release_kb=$((release_size / 1024))
minsize_kb=$((minsize_size / 1024))

echo "Debug版本:    ${debug_kb} KB"
echo "Release版本:  ${release_kb} KB"
echo "最小体积版本: ${minsize_kb} KB"
echo

release_saving=$((debug_kb - release_kb))
minsize_saving=$((debug_kb - minsize_kb))

echo "Release版本比Debug版本节省: ${release_saving} KB"
echo "最小体积版本比Debug版本节省: ${minsize_saving} KB"
echo

echo "各版本文件路径:"
echo "Debug:    target/debug/homework0_rs.exe"
echo "Release:  target/release/homework0_rs.exe"
echo "Min-Size: target/min-size/homework0_rs.exe"
echo

echo "运行测试:"
echo "Debug版本:    target/debug/homework0_rs.exe"
echo "Release版本:  target/release/homework0_rs.exe"
echo "最小体积版本: target/min-size/homework0_rs.exe"
echo

read -p "按任意键继续..."
