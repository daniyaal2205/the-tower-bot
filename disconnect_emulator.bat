@echo off
cd /d "%~dp0"
set PATH=%~dp0platform-tools;%PATH%

echo Disconnecting all devices...
adb disconnect
echo Done.
pause
