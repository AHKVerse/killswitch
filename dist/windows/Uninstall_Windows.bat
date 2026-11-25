@echo off
chcp 65001 >nul
title VPN Kill Switch Uninstaller

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Please run as administrator.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\VPNKillSwitch"

echo Removing shortcuts...
del "%Public%\Desktop\VPN Kill Switch.lnk" >nul 2>&1
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\VPN Kill Switch.lnk" >nul 2>&1

echo Cleaning up directory...
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

echo.
echo [OK] VPN Kill Switch was uninstalled successfully.
pause
