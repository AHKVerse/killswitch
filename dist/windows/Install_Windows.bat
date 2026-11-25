@echo off
chcp 65001 >nul
title VPN Kill Switch Installer (Windows)

echo ========================================================
echo        VPN Kill Switch - Windows Setup ^& Installer
echo ========================================================
echo.

:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Administrator privileges required.
    echo [!] Please right-click "Install_Windows.bat" and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [X] Python was not found on your system!
    echo Please install Python from https://www.python.org and check "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\VPNKillSwitch"
echo [*] Creating installation directory at %INSTALL_DIR% ...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [*] Copying application files...
copy /Y "%~dp0killswitch_win.py" "%INSTALL_DIR%\killswitch_win.py" >nul
copy /Y "%~dp0vpn-killswitch.ico" "%INSTALL_DIR%\vpn-killswitch.ico" >nul

:: Create Start Menu and Desktop shortcuts using VBScript
set "VBS_SCRIPT=%TEMP%\create_shortcuts.vbs"
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sDesktop = oWS.SpecialFolders^("AllUsersDesktop"^)
echo Set oLink = oWS.CreateShortcut^(sDesktop ^& "\VPN Kill Switch.lnk"^)
echo oLink.TargetPath = "pythonw.exe"
echo oLink.Arguments = """" ^& "%INSTALL_DIR%\killswitch_win.py" ^& """"
echo oLink.IconLocation = "%INSTALL_DIR%\vpn-killswitch.ico, 0"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "VPN Kill Switch - Instant IP Leak Protection"
echo oLink.Save
echo sPrograms = oWS.SpecialFolders^("AllUsersPrograms"^)
echo Set oLink2 = oWS.CreateShortcut^(sPrograms ^& "\VPN Kill Switch.lnk"^)
echo oLink2.TargetPath = "pythonw.exe"
echo oLink2.Arguments = """" ^& "%INSTALL_DIR%\killswitch_win.py" ^& """"
echo oLink2.IconLocation = "%INSTALL_DIR%\vpn-killswitch.ico, 0"
echo oLink2.WorkingDirectory = "%INSTALL_DIR%"
echo oLink2.Description = "VPN Kill Switch"
echo oLink2.Save
) > "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%" >nul 2>&1

echo.
echo ========================================================
echo [OK] Installation completed successfully!
echo "VPN Kill Switch" shortcut added to Desktop and Start Menu.
echo ========================================================
echo.
pause
