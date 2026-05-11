@echo off
echo [1/3] Cleaning old installer builds...
rmdir /s /q build dist 2>nul

echo [2/3] Building WysiChat Installer.exe...
:: Using --console so users can see the text output (progress/errors)
pyinstaller --noconfirm --onefile --console --icon="fyr-logo.ico" --name="WysiChatInstaller" install.py

echo [3/3] Syncing Installer to Z drive...
copy /y "dist\WysiChatInstaller.exe" "Z:\Tools\FYRTools\Wysichat\WysiChatInstaller.exe"

echo DONE!
pause