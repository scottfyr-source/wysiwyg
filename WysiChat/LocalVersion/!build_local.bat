@echo off
echo [1/3] Verifying files...
echo.
echo [2/3] Cleaning old builds...
rmdir /s /q build dist 2>nul

echo [3/3] Building WysichatLocal.exe...
pyinstaller --noconfirm --onefile --windowed --name "WysichatLocal" --icon "fyr-logo.ico" --add-data "fyrlogo.png;." --add-data "fyrlogo_alert.png;." main.py

echo Syncing to local root...
copy /y "dist\WysichatLocal.exe" "WysichatLocal.exe"

echo Syncing to Supergirl Tools...
copy /y "dist\WysichatLocal.exe" "C:\Supergirl\Tools\FYRTools\Wysichat\LocalVersion\WysichatLocal.exe"

echo DONE!
pause