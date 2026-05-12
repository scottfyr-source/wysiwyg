@echo off
echo Staging changes...
git add .
echo.
echo Committing changes...
git commit -m "End of day update: %date% %time%"
echo.
echo Pushing to GitHub...
git push origin main
echo.
echo Update Complete!
pause
