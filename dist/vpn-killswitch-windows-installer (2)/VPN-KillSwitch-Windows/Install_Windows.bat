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
    echo [!] In barname baraye ghad-e dastresi shabake niaz be dastresi Administrator darad.
    echo [!] Lotfan rooye file "Install_Windows.bat" راست کلیک konid va "Run as administrator" ra entekhab konid.
    echo.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [X] Python rooye system shoma yaft nashod!
    echo Lotfan ebtedaa Python ra az https://www.python.org nasb konid va gozineye "Add python.exe to PATH" ra bezanid.
    echo.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\VPNKillSwitch"
echo [*] Dar hal-e sakht-e pooshe-ye nasb dar %INSTALL_DIR% ...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [*] Dar hal-e kopy kardan-e file-ha...
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
echo [OK] Nasb ba movafaghiat anjam shod!
echo Icon-e "VPN Kill Switch" dar Desktop va Start Menu ezafe shod.
echo ========================================================
echo.
pause
