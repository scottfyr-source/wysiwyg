@echo off
echo [1/3] Verifying files...
echo.
echo [2/3] Cleaning old builds...
rmdir /s /q build dist 2>nul

echo [3/3] Building WysichatLocal.exe...
pyinstaller --noconfirm --onefile --windowed --name "WysichatLocal" --icon "fyr-logo.ico" --add-data "wysiwyglogo.png;." --add-data "fyrlogo_alert.png;." localmain.py

echo Syncing to local root...
copy /y "dist\WysichatLocal.exe" "WysichatLocal.exe"

echo DONE!
pause