@echo off
echo [1/3] Cleaning old installer builds...
rmdir /s /q build dist 2>nul

echo [2/3] Building WysiChat Installer.exe...
:: Using --console so users can see the text output (progress/errors)
pyinstaller --noconfirm --onefile --console --icon="fyr-logo.ico" --name="WysiChat_Local_Installer" install.py

echo [3/3] Syncing Installer to C drive...
copy /y "dist\WysiChat_Local_Installer.exe" "C:\Supergirl\Tools\FYRTools\WysiChat\LocalVersion\INSTALL_WYSICHAT.exe"

echo DONE!
pause