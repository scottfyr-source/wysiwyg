@echo off
echo [INFO] Installing WysiChat using PsExec from C:\tools\PsExec...

:: -i: Interactive (so we can see the console output)
:: -s: Run as System (High privileges for C:\FYRTOOLS creation)
"C:\tools\PsExec\PsExec.exe" -i -s "C:\Supergirl\Tools\FYRTools\WysiChat\LocalVersion\INSTALL_WYSICHAT.exe"

pause