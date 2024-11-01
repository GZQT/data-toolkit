@echo off

REM 切换到 server 目录
cd server

REM 使用 PyInstaller 打包 application.py
poetry.exe install
poetry.exe run pyinstaller.exe --onefile application.py -p . >nul 2>&1

cd ..

REM 复制 application.exe 到 client/src-electron 目录
copy server\dist\application.exe client\src-electron
copy server\alembic.ini client\src-electron\alembic.ini
xcopy "server\alembic" "client\src-electron\alembic" /E /I /Y

REM 切换到 client 目录
cd client

REM 运行 bun
bun install
bun run build:electron

echo 脚本执行完毕
pause
