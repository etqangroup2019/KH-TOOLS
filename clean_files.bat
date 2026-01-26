@echo off
echo Cleaning temporary files...

echo Deleting .blend1 files...
del /s /q /f "*.blend1"

echo Deleting .pyc files...
del /s /q /f "*.pyc"

echo Deleting __pycache__ directories...
for /d /r . %%d in (__pycache__) do @(
    if exist "%%d" (
        echo Removing: %%d
        rd /s /q "%%d"
    )
)

echo.
echo Clean up complete!
pause
