@echo off
echo Building local WYSIWYG.exe...

echo.
echo Deleting previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Previous build folders removed.

echo.
echo Running PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --icon="fyr-logo.ico" ^
    --add-data "fyrlogo.png;." ^
    --add-data "index.html;." ^
    --add-data "editor.html;." ^
    --add-data "admin.html;." ^
    --add-data "search.html;." ^
    --add-data "style_guide.html;." ^
    --add-data "data.json;." ^
    --add-data "media_formats.json;." ^
    --add-data "version.json;." ^
    --add-data "changelog.txt;." ^
    --add-data "styles.css;." ^
    --add-data "app.js;." ^
    --add-data "Uberpaste;Uberpaste" ^
    --add-data "WysiScan;WysiScan" ^
    --add-data "WalmartSheet;WalmartSheet" ^
    --name "WYSIWYG" ^
    --hidden-import=psutil ^
    --hidden-import=win32timezone ^
    main.py

echo Build process finished.
pause
