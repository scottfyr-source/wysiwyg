@echo off
ECHO --- LOCAL BUILD SCRIPT ---
SETLOCAL

ECHO.
ECHO [0/3] Installing Dependencies...
pip install -r requirements.txt

ECHO.
ECHO [1/3] Building Main Application (WYSIWYG.exe) for local testing...
:: Combined into single line to prevent batch file syntax errors
pyinstaller --noconfirm --onefile --windowed --icon="fyr-logo.ico" --add-data "fyrlogo.png;." --add-data "index.html;." --add-data "editor.html;." --add-data "admin.html;." --add-data "search.html;." --add-data "style_guide.html;." --add-data "data.json;." --add-data "media_formats.json;." --add-data "version.json;." --add-data "changelog.txt;." --add-data "styles.css;." --add-data "Uberpaste;Uberpaste" --add-data "WysiScan;WysiScan" --name "WYSIWYG" --hidden-import=psutil --hidden-import=win32timezone main.py

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ECHO ERROR: Main Application build failed!
    ECHO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    PAUSE
    EXIT /B %ERRORLEVEL%
)

ECHO.
ECHO [2/3] Building Context Menu Helper (send_to_wysiwyg.exe)...
pyinstaller --noconfirm --onefile --windowed --name "send_to_wysiwyg" send_to_wysiwyg.py

ECHO.
ECHO [3/3] --- LOCAL BUILD COMPLETE ---
ECHO The executable can be found in the 'dist' folder.
PAUSE
ENDLOCAL