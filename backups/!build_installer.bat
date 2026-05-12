@echo off
if not exist install.py echo ERROR: install.py missing! && pause && exit
echo [1/3] Cleaning old installer builds...
rmdir /s /q build dist 2>nul

echo [2/3] Building INSTALL_WYSIWYG.exe...
:: Using --console so users can see the text output (progress/errors)
pyinstaller --onefile --uac-admin --icon=fyr-logo.ico --name="INSTALL_WYSIWYG" install.py

echo [3/3] Syncing Installer to Z drive...
if not exist "Z:\" (
    echo ERROR: Z: drive is not connected! Cannot sync.
    pause
    exit /b
)
copy /y "dist\INSTALL_WYSIWYG.exe" "Z:\Tools\FYRTools\WYSIWYG\INSTALL_WYSIWYG.exe"

echo DONE!
pause