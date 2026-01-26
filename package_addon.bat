@echo off
setlocal enabledelayedexpansion

:: 1. Extract version from __init__.py
for /f "tokens=2 delims=()" %%a in ('findstr /r "\"version\":.*(" "__init__.py"') do (
    set "v=%%a"
    set "v=!v: =!"
    set "v=!v:,=.!"
    set "VERSION=!v!"
)

set "ADDON_NAME=KH-Tools"
set "ZIP_NAME=%ADDON_NAME%V!VERSION!.zip"
set "BUILD=TEMP_BUILD"

echo [KH-Tools] Packaging v!VERSION!...

:: 2. Cleanup old zips and temp build folder
if exist "%ADDON_NAME%V*.zip" del "%ADDON_NAME%V*.zip"
if exist "%BUILD%" rd /s /q "%BUILD%"

:: 3. Create initial folder structure so it exists inside the ZIP
mkdir "%BUILD%\%ADDON_NAME%"

:: 4. Copy files (excluding unwanted ones) to the temp folder
robocopy "." "%BUILD%\%ADDON_NAME%" /E /XD .git __pycache__ temp .vscode "%BUILD%" /XF .gitignore deploy.bat package_addon.bat *.blend1* *.pyc .DS_Store Thumbs.db *.log *.zip > nul

:: 5. Create the ZIP from the temp folder
powershell -Command "Compress-Archive -Path '%BUILD%\%ADDON_NAME%' -DestinationPath '%ZIP_NAME%' -Force"

:: 6. Final cleanup
rd /s /q "%BUILD%"

echo.
echo ===========================================
echo Done! !ZIP_NAME! created successfully.
echo Files are contained within '%ADDON_NAME%' folder.
echo ===========================================
pause
