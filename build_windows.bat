@echo off
setlocal

cd /d "%~dp0"

py -3 -m pip install --upgrade pip
py -3 -m pip install pyinstaller matplotlib

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

py -3 -m PyInstaller --noconfirm moodtracker.spec

echo.
echo Build listo. Ejecutable generado en:
echo %cd%\dist\MoodTracker.exe
echo.

endlocal
