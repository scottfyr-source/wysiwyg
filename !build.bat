@echo off
ECHO --- WYSIWYG BUILD SCRIPT ---
SETLOCAL

:: Configure the destination network share
SET "SERVER_SHARE=\\192.168.0.108\FYRShare\Tools\FYRTools\WYSIWYG"

ECHO.
ECHO [0/6] Installing Dependencies...
python -m pip install -r requirements.txt

ECHO.
ECHO [1/6] Checking local version against server...
python check_version.py
PAUSE

ECHO.
ECHO [1.5/6] Terminating any running instances of the application...
taskkill /F /IM WYSIWYG.exe /T > nul 2>&1

ECHO.
ECHO [1.75/6] Cleaning up previous build folders...
IF EXIST "build" RMDIR /S /Q "build"
IF EXIST "dist" RMDIR /S /Q "dist"

ECHO.
ECHO [2/6] Building Main Application (WYSIWYG.exe)...
:: Combined into single line to prevent batch file syntax errors
python -m PyInstaller --noconfirm WYSIWYG.spec

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ECHO ERROR: Main Application build failed!
    ECHO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    PAUSE
    EXIT /B %ERRORLEVEL%
)

ECHO.
ECHO [4/6] Copying executables to server share...
ECHO   Source:      dist\
ECHO   Destination: %SERVER_SHARE%
copy /Y "dist\WYSIWYG.exe" "%SERVER_SHARE%\"
IF EXIST "dist\send_to_wysiwyg.exe" copy /Y "dist\send_to_wysiwyg.exe" "%SERVER_SHARE%\"

ECHO.
ECHO [4.5/6] Cleaning up stale web assets from server share...
:: We remove these to ensure the EXE uses its internal bundled versions
IF EXIST "%SERVER_SHARE%\index.html" DEL /Q "%SERVER_SHARE%\index.html"
IF EXIST "%SERVER_SHARE%\styles.css" DEL /Q "%SERVER_SHARE%\styles.css"
IF EXIST "%SERVER_SHARE%\app.js" DEL /Q "%SERVER_SHARE%\app.js"
IF EXIST "%SERVER_SHARE%\admin.html" DEL /Q "%SERVER_SHARE%\admin.html"
IF EXIST "%SERVER_SHARE%\editor.html" DEL /Q "%SERVER_SHARE%\editor.html"
IF EXIST "%SERVER_SHARE%\search.html" DEL /Q "%SERVER_SHARE%\search.html"
IF EXIST "%SERVER_SHARE%\style_guide.html" DEL /Q "%SERVER_SHARE%\style_guide.html"
IF EXIST "%SERVER_SHARE%\fyrlogo.png" DEL /Q "%SERVER_SHARE%\fyrlogo.png"
IF EXIST "%SERVER_SHARE%\Uberpaste" RMDIR /S /Q "%SERVER_SHARE%\Uberpaste"
IF EXIST "%SERVER_SHARE%\WysiScan" RMDIR /S /Q "%SERVER_SHARE%\WysiScan"

ECHO.
ECHO [5/6] Copying core configuration and update files to server share...

copy /Y "version.json" "%SERVER_SHARE%\"
copy /Y "changelog.txt" "%SERVER_SHARE%\"
copy /Y "Conditions.json" "%SERVER_SHARE%\"
IF EXIST "WYSIWYG.lnk" copy /Y "WYSIWYG.lnk" "%SERVER_SHARE%\"

ECHO.
ECHO [6/6] --- BUILD AND DEPLOYMENT COMPLETE ---
ECHO All necessary files have been copied to %SERVER_SHARE%
ECHO The application is ready for users to install.
PAUSE
ENDLOCAL
