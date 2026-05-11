@echo off
echo [1/3] Verifying files...
echo.
echo [2/3] Cleaning old builds...
rmdir /s /q build dist 2>nul

echo [3/3] Building Wysichat.exe...
pyinstaller --noconfirm --onefile --windowed --name "Wysichat" --icon "fyr-logo.ico" --add-data "fyrlogo.png;." --add-data "fyrlogo_alert.png;." main.py


echo Syncing to local root...
copy /y "dist\Wysichat.exe" "Wysichat.exe"

echo Syncing to Z Drive...
copy /y "dist\Wysichat.exe" "Z:\Tools\FYRTools\Wysichat\Wysichat.exe"
copy /y "fyrlogo.png" "Z:\Tools\FYRTools\Wysichat\fyrlogo.png"
copy /y "fyrlogo.ico" "Z:\Tools\FYRTools\Wysichat\fyr-logo.ico"
copy /y "fyrlogo_alert.png" "Z:\Tools\FYRTools\Wysichat\fyrlogo_alert.png"

echo DONE!
pause