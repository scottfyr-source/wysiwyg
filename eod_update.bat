@echo off
SETLOCAL

:: Set the repository path
set REPO_DIR=C:\Git\WysiWyg
cd /d "%REPO_DIR%"

echo ========================================
echo   WysiWyg End-of-Day Sync
echo ========================================

:: 1. Clear stale git locks to prevent the "index.lock" error
if exist ".git\index.lock" (
    echo [INFO] Removing stale git index lock...
    del ".git\index.lock" /f /q
)

:: 2. Stage all changes
echo [INFO] Staging changes...
git add .

:: 3. Check for changes and commit with a timestamp
set TIMESTAMP=%DATE% %TIME%
git diff-index --quiet HEAD --
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Committing changes at %TIMESTAMP%...
    git commit -m "End of day update: %TIMESTAMP%"
    
    echo [INFO] Pushing changes to https://github.com/scottfyr-source/wysiwyg.git...
    git push -u origin master
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Push failed! Check your connection or permissions.
    ) else (
        echo [SUCCESS] Repository updated and pushed successfully.
    )
) else (
    echo [INFO] No changes to update.
)
pause
