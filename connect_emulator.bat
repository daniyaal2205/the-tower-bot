@echo off
echo Attempting to connect to emulators...
:: BlueStacks / LDPlayer
platform-tools\adb.exe connect 127.0.0.1:5555
echo connected to 127.0.0.1:5555
.\platform-tools\adb.exe connect 127.0.0.1:5556
echo connected to 127.0.0.1:5556
:: LDPlayer / MuMu
.\platform-tools\adb.exe connect 127.0.0.1:7555
:: Nox
platform-tools\adb.exe connect 127.0.0.1:62001

echo.
echo Checking for connected devices...
platform-tools\adb.exe devices
echo.
echo If you see a device listed above, you are ready!
echo If not, ensure your emulator is running and USB Debugging is enabled.
pause
