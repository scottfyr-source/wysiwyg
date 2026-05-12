ECHO.
ECHO [1.75/6] Cleaning up previous build folders...
IF EXIST "build" RMDIR /S /Q "build"
IF EXIST "dist" RMDIR /S /Q "dist"

SET "SERVER_SHARE=\\192.168.0.108\FYRShare\Tools\FYRTools\WYSIWYG\temp"

ECHO.
ECHO [2/6] Building Main Application (WYSIWYG.exe)...
:: Combined into single line to prevent batch file syntax errors
python -m PyInstaller --noconfirm --onefile --windowed --icon="fyr-logo.ico" --add-data "app.js;." --add-data "fyrlogo.png;." --add-data "index.html;." --add-data "editor.html;." --add-data "admin.html;." --add-data "search.html;." --add-data "style_guide.html;." --add-data "data.json;." --add-data "media_formats.json;." --add-data "version.json;." --add-data "changelog.txt;." --add-data "styles.css;." --add-data "walmart.html;." --add-data "fyr-logo.ico;." --add-data "Uberpaste;Uberpaste" --add-data "WysiScan;WysiScan" --add-data "WalmartSheet;WalmartSheet" --name "WYSIWYG" --hidden-import=psutil --hidden-import=win32timezone main.py

IF EXIST ""%SERVER_SHARE%\WYSIWYG.exe" DEL /Q""
copy /Y "dist\WYSIWYG.exe" "%SERVER_SHARE%\"