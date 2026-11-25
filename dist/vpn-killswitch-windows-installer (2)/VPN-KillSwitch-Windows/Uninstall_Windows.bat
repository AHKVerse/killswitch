@echo off
chcp 65001 >nul
title VPN Kill Switch Uninstaller

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Lotfan ba Run as administrator ejra konid.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\VPNKillSwitch"

echo Dar hal-e hazf-e shortcut-ha...
del "%Public%\Desktop\VPN Kill Switch.lnk" >nul 2>&1
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\VPN Kill Switch.lnk" >nul 2>&1

echo Dar hal-e pak sazi pooshe-ye barname...
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

echo.
echo [OK] Barname ba movafaghiat hazf shod.
pause
