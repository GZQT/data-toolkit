#!/bin/bash

set -e

# 安装 server 依赖
cd server
poetry lock --no-update
poetry install

# 构建 server 下的 application.py
pyinstaller --onefile application.py

# 将生成的 application.exe 复制到 client/src-electron 目录
cp dist/application /app/client/src-electron/application

# 安装 client 依赖并构建
cd ../client
rm -rf node_modules
npm config set registry https://registry.npmmirror.com
npm install
npm run build:electron

echo "CI build and tests completed successfully."
